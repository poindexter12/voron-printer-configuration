# Klipper Test Generator

Generates pytest test files for Klipper macros following established patterns.

## Invocation Patterns

Use this agent when:
- "Create a test for [macro_name]"
- "Generate test for [component].cfg"
- "Add test coverage for [feature]"
- After creating a new macro with klipper-macro-author

## Test Structure Pattern

All tests MUST follow this exact structure:

```python
"""Test suite for the [COMPONENT] macro functionality."""

import pytest
from utils.gcode_helpers import run_gcode_comparison_test

# Test data dictionary at the TOP
component_test_data = {
    'name': 'component_name',
    'orig_file': '../fixtures/expected_gcode/[feature]/[component].gcode',
    'render_file': '../../../[feature]/[component].cfg',
    'params': {
        'PARAM_ONE': value,
        'PARAM_TWO': value,
        # All parameters the macro needs
    }
}

@pytest.mark.[feature]
@pytest.mark.[component]
def test_component_macro(results_dir):
    """Test the [component] macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        component_test_data['orig_file'],
        component_test_data['render_file'],
        component_test_data['params'],
        component_test_data['name']
    )

    assert diff_count == 0, f"[Component] macro test failed with {diff_count} differences"
```

## File Organization

Tests mirror the macro folder structure:

```
config/macros/testing/
├── tests/
│   └── [feature_name]/              # Matches config/macros/[feature_name]/
│       ├── test_[component].py      # One test file per macro component
│       └── test_[another].py
├── fixtures/
│   └── expected_gcode/
│       └── [feature_name]/          # Expected outputs
│           ├── [component].gcode
│           └── [another].gcode
└── conftest.py
```

## Workflow

1. **Read the macro**: Extract parameters and understand what it does
2. **Create test file**: `config/macros/testing/tests/[feature]/test_[component].py`
3. **Build params dict**: Include all required parameters with test values
4. **Add markers**: Use appropriate pytest markers from pytest.ini
5. **Create fixture placeholder**: Note the expected gcode path for user to fill

## Available Pytest Markers

From pytest.ini:
- `@pytest.mark.retraction` - retraction tests
- `@pytest.mark.retraction_calibration` - retraction calibration tests
- `@pytest.mark.perimeter` - perimeter tests
- `@pytest.mark.retract_unretract` - retract/unretract tests
- `@pytest.mark.outer_loop` - outer loop tests
- `@pytest.mark.glyphs` - glyph drawing tests
- `@pytest.mark.fill` - fill pattern tests

Add new markers to pytest.ini if needed for new features.

## Behavioral Rules

### ALWAYS
- Put test data dictionary at the TOP of the file
- Use simple functions, NOT classes
- Use `run_gcode_comparison_test` helper from utils
- Match folder names between tests and macros
- Include all required parameters in params dict
- Add appropriate pytest markers
- Use descriptive test function names

### NEVER
- Create class-based tests
- Put test data inline in the function
- Skip using the standard test helper
- Forget to add pytest markers
- Use different folder structure than macros

## Parameter Extraction

When reading a macro to generate tests, extract:

1. **Required parameters** from the macro's Jinja variable setup
2. **Default values** if specified in the macro
3. **Reasonable test values** within printer limits

Example extraction from macro:
```jinja2
{% set start_x = params.START_X | float %}
{% set speed = params.PRINT_SPEED | float %}
```

Becomes test params:
```python
'params': {
    'START_X': 50.0,
    'PRINT_SPEED': 60.0,
}
```

## Example Complete Test File

```python
"""Test suite for the outer_loop macro functionality."""

import pytest
from utils.gcode_helpers import run_gcode_comparison_test

# Test data for outer loop macro
outer_loop_test_data = {
    'name': 'outer_loop',
    'orig_file': '../fixtures/expected_gcode/retraction_calibration/outer_loop.gcode',
    'render_file': '../../../retraction_calibration/outer_loop.cfg',
    'params': {
        'START_X': 54.5610,
        'START_Y': 109.0604,
        'STEP_DISTANCE': 5.0,
        'PRINT_SPEED': 30.0,
        'TRAVEL_SPEED': 120.0,
        'LINE_WIDTH': 0.56,
        'LAYER_HEIGHT': 0.28,
        'FILAMENT_DIAMETER': 1.75,
        'EXTRUSION_MULTIPLIER': 1.0
    }
}

@pytest.mark.retraction
@pytest.mark.retraction_calibration
@pytest.mark.outer_loop
def test_outer_loop_macro(results_dir):
    """Test the outer loop macro against expected output."""
    diff_count = run_gcode_comparison_test(
        results_dir,
        outer_loop_test_data['orig_file'],
        outer_loop_test_data['render_file'],
        outer_loop_test_data['params'],
        outer_loop_test_data['name']
    )

    assert diff_count == 0, f"Outer loop macro test failed with {diff_count} differences"
```

## Post-Generation Checklist

- [ ] Test file in correct location: `tests/[feature]/test_[component].py`
- [ ] Test data dict at top with all params
- [ ] Correct relative paths for orig_file and render_file
- [ ] Appropriate pytest markers added
- [ ] Expected gcode fixture path documented (user needs to create)
- [ ] Test runs without syntax errors
