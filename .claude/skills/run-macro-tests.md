# Run Macro Tests

Run pytest tests with appropriate filters and markers.

## When to Use

Use this skill when:
- "Run tests"
- "Test the [feature] macros"
- "Check if tests pass"
- After making macro changes
- Validating macro output

## Test Commands

### Run All Tests
```bash
cd config/macros/testing
make test
```

Or directly:
```bash
cd config/macros/testing
. .venv/bin/activate
python -m pytest tests/ -v
```

### Run by Feature Folder
```bash
python -m pytest tests/retraction_calibration/ -v
python -m pytest tests/temperature_test/ -v
```

### Run Single Test File
```bash
python -m pytest tests/retraction_calibration/test_outer_loop.py -v
```

### Run by Marker
```bash
python -m pytest -m "glyphs" -v
python -m pytest -m "retraction_calibration" -v
python -m pytest -m "fill" -v
```

### Exclude Markers
```bash
python -m pytest -m "not glyphs" -v
```

### Combine Markers
```bash
python -m pytest -m "retraction and not fill" -v
```

## Available Markers

From `config/macros/testing/pytest.ini`:

| Marker | Description |
|--------|-------------|
| `retraction` | All retraction tests |
| `retraction_calibration` | Retraction calibration tests |
| `perimeter` | Perimeter drawing tests |
| `retract_unretract` | Retract/unretract operation tests |
| `outer_loop` | Outer loop pattern tests |
| `glyphs` | Glyph drawing tests |
| `fill` | Fill pattern tests |

## Natural Language Mapping

| User Says | Command |
|-----------|---------|
| "test everything" | `python -m pytest tests/ -v` |
| "test retraction" | `python -m pytest -m "retraction" -v` |
| "test the glyphs" | `python -m pytest -m "glyphs" -v` |
| "test outer loop only" | `python -m pytest tests/retraction_calibration/test_outer_loop.py -v` |
| "test fill patterns" | `python -m pytest -m "fill" -v` |

## Understanding Test Output

### Success
```
tests/retraction_calibration/test_outer_loop.py::test_outer_loop_macro PASSED
```

### Failure
```
tests/retraction_calibration/test_outer_loop.py::test_outer_loop_macro FAILED

AssertionError: Outer loop macro test failed with 3 differences
```

### Finding Diffs
When tests fail, HTML diffs are saved in:
```
config/macros/testing/test_results/[timestamp]/
```

Open the HTML file to see exactly what differs.

## Troubleshooting

### Test Not Found
```bash
# Make sure you're in the right directory
cd config/macros/testing

# Check test file exists
ls tests/[feature]/test_[component].py
```

### Import Errors
```bash
# Ensure venv is activated
. .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Fixture Not Found
Check that the expected gcode file exists:
```bash
ls fixtures/expected_gcode/[feature]/[component].gcode
```

### Path Issues
Test data paths are relative to the test file location:
- `orig_file`: `../fixtures/expected_gcode/...`
- `render_file`: `../../../[feature]/[component].cfg`

## Quick Reference

```bash
# Setup (first time)
cd config/macros/testing
make install

# Run all
make test

# Run specific marker
. .venv/bin/activate
python -m pytest -m "glyphs" -v

# Run specific file
python -m pytest tests/retraction_calibration/test_glyphs.py -v

# Run with output on failure
python -m pytest tests/ -v --tb=short
```
