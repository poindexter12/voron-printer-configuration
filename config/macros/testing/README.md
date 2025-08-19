# Klipper Macro Testing

This directory contains the testing infrastructure for Klipper macros, specifically focused on G-code generation and comparison.

## Folder Structure

```
config/macros/testing/
├── tests/                          # Main test directory
│   ├── __init__.py                # Makes tests a Python package
│   └── test_compare_gcode.py      # G-code comparison tests
├── fixtures/                       # Test data and fixtures
│   ├── expected_gcode/            # Expected G-code output files
│   │   ├── perimeter_first_layer.gcode
│   │   └── perimeter_other_layers.gcode
│   └── macro_templates/           # Jinja2 macro templates
│       └── draw_perimeter_layer.cfg
├── utils/                          # Utility functions
│   ├── __init__.py
│   └── gcode_helpers.py           # G-code processing utilities
├── conftest.py                     # Pytest configuration and shared fixtures
├── requirements.txt                # Python dependencies
├── Makefile                        # Build and test commands
└── README.md                       # This file
```

## Running Tests

### Using Make

```bash
make tests
```

### Using pytest directly

```bash
# Activate virtual environment first
. .venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_compare_gcode.py::test_first_layer_perimeter -v
```

## Test Structure

### Test Files

- **`test_compare_gcode.py`**: Tests that compare generated G-code with expected output
  - `test_first_layer_perimeter`: Tests first layer perimeter generation (140% line width)
  - `test_other_layers_perimeter`: Tests subsequent layer perimeter generation (112.5% line width)

### Fixtures

- **`conftest.py`**: Provides shared pytest fixtures
  - `results_dir`: Creates timestamped test result directories
  - `fixtures_dir`: Path to test fixtures
  - `expected_gcode_dir`: Path to expected G-code files
  - `macro_templates_dir`: Path to macro templates

### Utilities

- **`gcode_helpers.py`**: Common functions for G-code processing
  - `clean_gcode_file()`: Clean and optionally render Jinja2 templates
  - `save_cleaned_files()`: Save processed files for debugging
  - `diff_with_html()`: Generate HTML diffs for easy comparison

## Test Results

Test results are saved in `test_results/` with timestamped directories:

- **Log files**: Summary of test results
- **HTML diffs**: Beautiful, easy-to-read diffs when tests fail
- **Cleaned files**: Both expected and generated G-code for manual inspection

## Adding New Tests

1. **Create test file** in `tests/` directory
2. **Add test data** to appropriate `fixtures/` subdirectory
3. **Import utilities** from `utils.gcode_helpers`
4. **Use shared fixtures** from `conftest.py`

## Dependencies

- `pytest`: Testing framework
- `jinja2`: Template rendering
- `difflib`: HTML diff generation (built-in)

## Example Test

```python
def test_my_macro(results_dir, expected_gcode_dir, macro_templates_dir):
    """Test that my macro generates expected G-code."""
    # Test implementation here
    pass
```
