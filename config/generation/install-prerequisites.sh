#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# install_prerequisites.sh — Ensure Python & dependencies for Klipper config gen
#
# Usage:
#   1. Place this script in your printer_config folder alongside:
#        • steppers.yaml
#        • stepper_settings.cfg.j2
#        • requirements.txt
#   2. chmod +x install_prerequisites.sh
#   3. ./install_prerequisites.sh
#
# What it does:
#   • Installs system packages: python3, venv support, pip
#   • Creates a Python virtual environment in ./venv
#   • Upgrades pip, setuptools, wheel in the venv
#   • Installs PyYAML & Jinja2 from requirements.txt into the venv
# -----------------------------------------------------------------------------

# Change to script’s directory
cd "$(dirname "$0")"

# Paths
PROJECT_DIR="$(pwd)"
REQUIREMENTS_FILE="${PROJECT_DIR}/requirements.txt"
VENV_DIR="${PROJECT_DIR}/venv"

echo "Updating apt repositories…"
sudo apt update

echo "Installing system Python packages…"
sudo apt install -y python3 python3-venv python3-full python3-pip

# Check requirements file
if [ ! -f "$REQUIREMENTS_FILE" ]; then
  echo "Error: requirements.txt not found in ${PROJECT_DIR}"
  exit 1
fi

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating Python virtual environment…"
  python3 -m venv "$VENV_DIR"
fi

# Upgrade pip, setuptools, wheel inside venv
echo "Upgrading pip, setuptools, wheel in venv…"
"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel

# Install Python deps into venv
echo "Installing Python dependencies from requirements.txt…"
"$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"

echo
echo "Setup complete!"
echo "To activate the virtualenv, run:"
echo "  source ${VENV_DIR}/bin/activate"