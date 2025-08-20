# Voron Printer Configuration

This repository contains the configuration for my Voron 2.4 350mm printer

## Repository Structure & Purpose

- **`backup/`** - Automated backup scripts that run on the printer itself
  - `configuration_backup.sh` - Backs up printer configuration
  - `setup_backup.sh` - Backs up system setup

- **`config/`** - Mirror of the printer's `printer_data` folder
  - Contains all Klipper, Moonraker, and other configuration files
  - This is the "source of truth" for printer settings

- **`database/`** - Moonraker database from the printer
  - Contains print history, settings, and other operational data

- **`simulator/`** - Docker compose setup for testing configurations locally

## Development Workflow

1. **Local Development** - Edit macros and configs in the `config/` folder
2. **Testing** - Use the testing framework to validate G-code generation
3. **Deployment** - Copy changes to the printer (or use git pull on the printer)
4. **Backup** - Printer automatically backs up to this repository
5. **Validation** - Test actual prints to ensure changes work as expected

## Key Components

- **Klipper** - 3D printer firmware (installed via KIAUH)
- **Moonraker** - API server for printer communication
- **KlipperScreen** - Touchscreen interface
- **Custom Macros** - Specialized G-code for calibration and testing

## Printer Setup

- **Model**: Voron 2.4 350mm
- **Installation**: KIAUH (Klipper Installation And Update Helper)
- **Components**: Klipper, Moonraker, KlipperScreen, etc.
- **Backup**: Automated scripts run on the printer itself

## Testing Framework

- **Purpose**: Validate G-code generation before deploying to printer
- **Framework**: pytest with custom G-code comparison utilities
- **Location**: `config/macros/testing/`
- **Workflow**: Generate expected G-code, compare with macro output
