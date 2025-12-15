# Create Test Fixture

Create expected G-code fixture files for macro tests.

## When to Use

Use this skill when:
- "Create fixture for [component]"
- "Add expected gcode for test"
- Setting up a new test
- After creating test file with klipper-test-generator

## Fixture Location

Fixtures go in the expected_gcode directory matching the feature:

```
config/macros/testing/fixtures/expected_gcode/[feature_name]/[component].gcode
```

Example:
```
config/macros/testing/fixtures/expected_gcode/retraction_calibration/outer_loop.gcode
```

## Creating a Fixture

### Option 1: From Reference File
If `original.gcode` exists in the macro folder, extract the relevant section:

1. Read `config/macros/[feature]/original.gcode`
2. Identify the section that matches the component
3. Copy to fixture location
4. Clean up (remove irrelevant parts)

### Option 2: Manual Generation
If no reference exists:

1. Understand what the macro should output
2. Calculate expected G-code manually or run macro
3. Save to fixture location
4. Verify correctness

### Option 3: From Macro Render
Run the macro template with test parameters:

1. Use Jinja2 to render the macro with params from test
2. Capture output
3. Save to fixture location
4. Verify output is correct

## Fixture Format

Expected G-code files should:
- Contain only the G-code the macro produces
- Not include startup/shutdown sequences (unless macro does)
- Use consistent formatting
- Include comments if helpful for understanding

Example fixture content:
```gcode
G0 X54.561 Y109.060 F7200
G1 X54.561 Y190.940 E2.43567 F1800
G1 X59.561 Y190.940 E0.14876 F1800
G1 X59.561 Y109.060 E2.43567 F1800
```

## Workflow

1. **Identify test**: Find the test file that needs a fixture
2. **Check params**: Note the parameters used in test_data
3. **Generate output**: Create expected G-code for those params
4. **Save fixture**: Place in correct location
5. **Run test**: Verify test passes with new fixture

## File Organization

```
config/macros/testing/fixtures/expected_gcode/
├── retraction_calibration/
│   ├── outer_loop.gcode
│   ├── perimeter.gcode
│   ├── glyphs.gcode
│   └── fill.gcode
├── temperature_test/
│   ├── tower_layer.gcode
│   └── temperature_tower.gcode
└── calibration_tower/
    └── tower_block.gcode
```

## Validation

After creating fixture:

1. Run the specific test:
   ```bash
   cd config/macros/testing
   python -m pytest tests/[feature]/test_[component].py -v
   ```

2. If test fails, check the diff output in `test_results/`

3. Adjust fixture or macro until test passes

## Common Issues

- **Path mismatch**: Fixture path must match `orig_file` in test data
- **Trailing whitespace**: Can cause diff failures
- **Floating point precision**: Use consistent decimal places
- **Line endings**: Use Unix line endings (LF)
