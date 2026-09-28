# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Voron 2.4 350mm printer configuration repository. Contains Klipper configs, custom G-code macros, and a testing framework for validating macro output.

## Commands

### Running Tests

```bash
cd config/macros/testing
make install  # First time setup: creates venv and installs dependencies
make test     # Run all tests
```

Or directly with pytest:

```bash
cd config/macros/testing
. .venv/bin/activate
python -m pytest tests/ -v
python -m pytest tests/retraction_calibration/test_outer_loop.py -v  # Single file
python -m pytest -m "glyphs" -v  # By marker
```

Available markers (authoritative list is `config/macros/testing/pytest.ini`):
`retraction`, `retraction_calibration`, `perimeter`, `retract_unretract`,
`outer_loop`, `glyphs`, `fill`, `layers`, `combined`, `temperature_tower`,
`stringing`, `pressure_advance`, `config`

### Linting

CI runs these on every push and pull request (`.github/workflows/ci.yml`), so
run them before pushing. Settings live in `ruff.toml` at the repo root.

```bash
ruff check .                 # or: uvx ruff check .
ruff check . --fix           # apply the safe fixes
shellcheck backup/*.sh observability/*.sh
```

`trunk fmt` / `trunk check` also work if you have trunk installed, but the repo
carries no `.trunk` config and CI does not use it.

### CI

`.github/workflows/ci.yml` has three jobs: the macro test suite,
ruff, and shellcheck. Note `.gitignore` denies everything at the repo root by
default — a new top-level file needs an explicit `!/name` exception or git will
not see it.

### Config structure checks

`config/macros/testing/tests/test_config_structure.py` guards the wiring rather
than the rendered G-code: every `[include]` in `printer.cfg` resolves, no
Klipper section is declared in two files, every `macros/<feature>/` has a
matching `tests/<feature>/`, and every marker used in a test is registered in
`pytest.ini`. Add a genuinely external include to `EXTERNAL_INCLUDES` in that
file rather than loosening the check.

## Architecture

### Directory Structure

- `config/` - Klipper printer configuration (mirrors printer's `printer_data`)
- `config/macros/[feature_name]/` - Custom macros organized by feature
- `config/macros/testing/` - pytest-based G-code testing framework
- `config/klipper-macros/` - Third-party Klipper macros (git submodule)

### Testing Framework Structure

```
config/macros/testing/
├── tests/[feature_name]/test_[component].py  # Test files
├── fixtures/expected_gcode/[feature_name]/   # Expected G-code output
├── utils/gcode_helpers.py                    # G-code comparison utilities
└── conftest.py                               # Shared pytest fixtures
```

### Macro-Test Relationship

Macros and tests use parallel folder structures. The `[feature_name]` segment
must match exactly across all three — a test directory named for the macro
rather than its folder is a bug, not a style choice.

- Macro: `config/macros/[feature_name]/[component].cfg`
- Test: `config/macros/testing/tests/[feature_name]/test_[component].py`
- Expected output: `config/macros/testing/fixtures/expected_gcode/[feature_name]/[component].gcode`

Each macro folder should include `original.gcode` as reference output to mimic.

## Klipper Macro Conventions

### Parameter Rules (Critical)

- **ALWAYS use UPPERCASE for macro parameters** (e.g., `START_X`, `PRINT_SPEED`)
- **ALWAYS access via `params.PARAM_NAME`** when setting Jinja variables
- **ALWAYS type Jinja variables**: `| float`, `| int`, `| string`

```jinja2
[gcode_macro _MACRO_NAME]
description: What the macro does
gcode:
    {% set start_x = params.START_X | float %}
    {% set count = params.COUNT | int %}
    G1 X{{ start_x }}
```

Common parameter names: `START_X`, `START_Y`, `STEP_DISTANCE`, `PRINT_SPEED`, `TRAVEL_SPEED`, `Z_HOP_DISTANCE`, `RETRACT_DISTANCE`, `LINE_WIDTH`, `LAYER_HEIGHT`

### Macro Structure

1. Parameters section with UPPERCASE names and descriptions
2. Jinja variable setup at beginning (extract from params with typing)
3. Use Jinja variables throughout, not parameters directly
4. Macros cannot access parameters from other macros

## Test File Pattern

```python
"""Test suite for the [COMPONENT] macro."""

import pytest
from utils.gcode_helpers import run_gcode_comparison_test

component_test_data = {
    'name': 'component_name',
    'orig_file': '../fixtures/expected_gcode/feature/component.gcode',
    'render_file': '../../../feature/component.cfg',
    'params': { /* parameters */ }
}

@pytest.mark.feature
def test_component_macro(results_dir):
    """Test the component macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        component_test_data['orig_file'],
        component_test_data['render_file'],
        component_test_data['params'],
        component_test_data['name']
    )
    assert diff_count == 0, f"Macro test failed with {diff_count} differences"
```

Use simple functions, not classes. Test data dictionary at top, clean function below.

## Operating the live printer

- Host is `voron-printer.home.arpa`, never `.local`. Moonraker listens on `:7125`.
- `tools/moonraker.py` wraps the Moonraker calls (`status`, `gcode`, `upload`,
  `start`, `cancel`, `log`, `restart`) and works when SSH to the Pi does not.
  Deploy a config edit with `upload FILE --config`, then `restart`.
- Never home, move, heat or start a print without an explicit "hands clear"
  from the user. Nothing in the tooling checks the bed is clear.
- klipper-macros wraps `SET_GCODE_OFFSET` and saves every Z offset into the
  active bed surface in `variables.cfg`, even when the print is cancelled. Test
  G-code that shifts Z must use `_KM_SET_GCODE_OFFSET_BASE`. After editing
  `[probe] z_offset`, run `ADJUST_SURFACE_OFFSETS IGNORE=1`.
- On the printer this repo is `printer_data`, and `backup/configuration_backup.sh`
  commits and pushes config changes straight to `main` every few hours. A hand
  commit of an edit already deployed to the printer may be dropped as a
  duplicate when rebased onto `origin/main`.
