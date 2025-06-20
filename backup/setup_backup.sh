#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# setup_backup.sh
# Purpose: Bootstrap the backup script:
#   - Copy .env.example → .env (if missing)
#   - Make configuration_backup.sh executable
#   - Install an hourly cron job
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_EXAMPLE="$SCRIPT_DIR/.env.example"
ENV_FILE="$SCRIPT_DIR/.env"
BACKUP_SCRIPT="$SCRIPT_DIR/configuration_backup.sh"
LOG_FILE="$SCRIPT_DIR/backup.log"

# 1) Ensure .env exists
if [ ! -f "$ENV_FILE" ]; then
  if [ -f "$ENV_EXAMPLE" ]; then
    echo "Creating .env from .env.example..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
  else
    echo "Warning: .env.example not found; create .env by hand."
  fi
else
  echo ".env already exists; skipping creation."
fi

# 2) Make sure the backup script is executable
if [ -f "$BACKUP_SCRIPT" ]; then
  chmod +x "$BACKUP_SCRIPT"
  echo "Made configuration_backup.sh executable."
else
  echo "Error: Backup script not found at $BACKUP_SCRIPT"
  exit 1
fi

# 3) Install cron job (hourly at minute 0)
CRON_SCHEDULE="${CRON_SCHEDULE:-0 * * * *}"
CRON_CMD="cd \"$SCRIPT_DIR\" && \"$BACKUP_SCRIPT\" >> \"$LOG_FILE\" 2>&1"
TMP_CRON="$(mktemp)"

# Remove any existing lines for our script
crontab -l 2>/dev/null | grep -v -F "$BACKUP_SCRIPT" > "$TMP_CRON" || true
# Add our job
echo "$CRON_SCHEDULE $CRON_CMD" >> "$TMP_CRON"
crontab "$TMP_CRON"
rm "$TMP_CRON"

echo "Installed cron job:"
echo "  $CRON_SCHEDULE $CRON_CMD"
echo "Logs will be appended to: $LOG_FILE"