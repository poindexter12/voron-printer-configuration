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

log "Checking for Git changes..."
if [ -n "$(git status --porcelain)" ]; then
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  log "Committing and pushing changes..."
  if [ "$DRY_RUN" = "false" ]; then
    git add .
    git commit -m "Autocommit from $timestamp by configuration_backup.sh"
    git push origin "$BRANCH"
  else
    log "Dry run: would commit and push to $BRANCH"
  fi
else
  log "No changes to commit."
fi