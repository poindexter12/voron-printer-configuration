# G-Code Testing Conventions

## Test Structure Convention

### Test Organization

- **Test folders**: Use descriptive names like `retraction_calibration/` instead of generic `retraction/`
- **Test grouping**: Group related test files under feature-specific folders
- **File naming**: `test_[component_name].py` for individual test files

### Test Location

``` markdown
config/macros/testing/
├── tests/
│   └── [feature_name]/           # e.g., retraction_calibration/
│       ├── test_[component].py   # e.g., test_outer_loop.py
│       ├── test_[component].py   # e.g., test_perimeter.py
│       └── test_[component].py   # e.g., test_glyphs.py
├── fixtures/
│   ├── expected_gcode/
│   │   └── [feature_name]/       # e.g., retraction_calibration/
│   └── macro_templates/
└── conftest.py
```

## Macro Organization Convention

### Macro Structure

- **Macro folders**: Match test folder names (e.g., `retraction_calibration/`)
- **Reference file**: Always include `original.gcode` in the macro function folder as the target output to mimic
- **Component files**: Split functionality into focused `.cfg` files (e.g., `glyphs.cfg`, `outer_loop.cfg`)

### Macro Location

``` markdown
config/macros/[feature_name]/      # e.g., retraction_calibration/
├── original.gcode                 # Reference output to mimic
├── [component].cfg               # e.g., outer_loop.cfg
├── [component].cfg               # e.g., perimeter.cfg
├── [component].cfg               # e.g., glyphs.cfg
└── [main_macro].cfg              # e.g., retraction_test.cfg
```

## Test-Macro Relationship

### Consistency Rules

- **Test location**: `config/macros/testing/tests/[feature_name]/`
- **Macro location**: `config/macros/[feature_name]/`
- **Fixtures location**: `config/macros/testing/fixtures/expected_gcode/[feature_name]/`

### Naming Convention

- Keep test and macro folder names consistent
- Use descriptive, specific names (e.g., `retraction_calibration` not just `retraction`)
- Component names should clearly indicate their function

## Key Principles

1. **Reference First**: Always examine `original.gcode` to understand the target output
2. **Modular Design**: Split complex macros into focused, testable components
3. **Consistent Structure**: Maintain parallel organization between tests and macros
4. **Descriptive Names**: Use names that clearly indicate purpose and scope
