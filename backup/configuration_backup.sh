#!/bin/bash
# -----------------------------------------------------------------------------
# Script: configuration_backup.sh
# Purpose: Backup Voron printer configuration and related data to Git and optional archives.
#
# Features:
#   - Pushes printer_data/config to Git (auto-commits when changes detected)
#   - Optionally creates a timestamped .tar.gz archive of config, database, and backup folders
#   - Supports extra files/folders via CLI or .env file
#   - Dry-run and verbose modes for safe testing
#
# Usage:
#   ./configuration_backup.sh [--printer-root ROOT] [--extra-folders F1,F2] [--extra-files F1,F2]
#                            [--enable-archive] [--dry-run] [--verbose]
#
# Configuration:
#   - Place a .env file in the same folder with variables: PRINTER_ROOT, EXTRA_FOLDERS, EXTRA_FILES,
#     ENABLE_ARCHIVE, DRY_RUN, VERBOSE
#
# -----------------------------------------------------------------------------

set -euo pipefail
IFS=$'\n\t'

log() { echo "[$(date +'%F %T')] $*"; }
vlog() { [ "${VERBOSE:-false}" = "true" ] && log "$@"; }

# Load environment vars from .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
  log "Loading environment from .env"
  # shellcheck source=/dev/null  # operator-supplied .env, resolved at runtime
  source "$ENV_FILE"
fi

# Defaults
PRINTER_ROOT="${PRINTER_ROOT:-$SCRIPT_DIR/../}"
BRANCH="${BRANCH:-main}"
DRY_RUN="${DRY_RUN:-false}"
VERBOSE="${VERBOSE:-false}"

# CLI overrides
while [[ $# -gt 0 ]]; do
  case $1 in
    --printer-root) PRINTER_ROOT="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --dry-run) DRY_RUN="true"; shift ;;
    --verbose) VERBOSE="true"; shift ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

cd "$PRINTER_ROOT" || { log "Failed to cd to $PRINTER_ROOT"; exit 1; }

# A rejected push used to abort the script into backup.log, which nothing
# reads - promtail ships klippy.log and the journal, not this file. That is how
# a non-fast-forward rejection went unnoticed from 2026-09-08 to 2026-09-22 and
# cost two weeks of off-Pi backups. Failures now go to the journal, which is
# already scraped into Loki, and leave a sentinel on disk.
#
# Deliberately NOT sent to the Klipper console: posting M118 through the gcode
# endpoint queues it behind whatever is printing.
FAIL_SENTINEL="${FAIL_SENTINEL:-$SCRIPT_DIR/.push-failed}"

alert() {
  log "ALERT: $*"
  if command -v logger >/dev/null 2>&1; then
    logger -t voron-backup -p user.err "$*" || true
  fi
  printf '%s\t%s\n' "$(date +'%F %T')" "$*" >> "$FAIL_SENTINEL" || true
}

log "Checking for Git changes..."
if [ -n "$(git status --porcelain)" ]; then
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  log "Committing and pushing changes..."
  if [ "$DRY_RUN" = "false" ]; then
    git add .
    git commit -m "Autocommit from $timestamp by configuration_backup.sh"

    # set -e would abort here before anything could report why.
    if git push origin "$BRANCH"; then
      if [ -f "$FAIL_SENTINEL" ]; then
        log "Push recovered; clearing $FAIL_SENTINEL"
        rm -f "$FAIL_SENTINEL"
      fi
    else
      # Without this the counts come from a stale remote-tracking ref and
      # report "0 behind" during the exact divergence they are meant to explain.
      git fetch --quiet origin "$BRANCH" 2>/dev/null || true
      ahead=$(git rev-list --count "origin/$BRANCH..$BRANCH" 2>/dev/null || echo "?")
      behind=$(git rev-list --count "$BRANCH..origin/$BRANCH" 2>/dev/null || echo "?")
      alert "push to origin/$BRANCH FAILED - $ahead commit(s) ahead, $behind behind. Backups are NOT leaving the Pi until this is resolved."
      exit 1
    fi
  else
    log "Dry run: would commit and push to $BRANCH"
  fi
else
  log "No changes to commit."
fi
