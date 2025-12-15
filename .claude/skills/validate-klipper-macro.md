# Validate Klipper Macro

Quick validation of macro files against repository conventions.

## When to Use

Use this skill when:
- "Validate this macro"
- "Check macro conventions"
- "Is this macro correct?"
- After editing a .cfg file
- Before committing macro changes

## Validation Checks

### 1. Parameter Naming (CRITICAL)
All parameters MUST be UPPERCASE:
```jinja2
; PASS
{% set speed = params.PRINT_SPEED | float %}

; FAIL - lowercase parameter
{% set speed = params.print_speed | float %}
```

### 2. Parameter Access (CRITICAL)
Must use `params.` prefix:
```jinja2
; PASS
{% set x = params.START_X | float %}

; FAIL - missing params prefix
{% set x = START_X | float %}
```

### 3. Jinja Variable Typing (CRITICAL)
All variables must be typed:
```jinja2
; PASS
{% set speed = params.SPEED | float %}
{% set count = params.COUNT | int %}

; FAIL - untyped variable
{% set speed = params.SPEED %}
```

### 4. Variable Usage in G-code
Use Jinja variables, not params:
```jinja2
; PASS
G1 X{{ start_x }} F{{ speed * 60 }}

; FAIL - using params directly
G1 X{{ params.START_X }} F{{ params.SPEED * 60 }}
```

### 5. Description Field
Macro should have description:
```jinja2
; PASS
[gcode_macro _MY_MACRO]
description: Does something useful
gcode:
    ...

; FAIL - missing description
[gcode_macro _MY_MACRO]
gcode:
    ...
```

### 6. Speed Conversion
F parameter should be mm/min (speed * 60):
```jinja2
; PASS - speed in mm/s converted to mm/min
G1 X100 F{{ speed * 60 }}

; QUESTIONABLE - might be wrong if speed is mm/s
G1 X100 F{{ speed }}
```

## Validation Output Format

```
VALIDATING: config/macros/feature/component.cfg

CRITICAL ISSUES:
[X] Line 5: Parameter 'start_x' should be UPPERCASE 'START_X'
[X] Line 8: Missing params prefix: 'SPEED' should be 'params.SPEED'

WARNINGS:
[!] Line 12: Untyped variable 'count' - add '| int' or '| float'
[!] No description field found

PASSED:
[✓] All G-code uses Jinja variables (not params directly)
[✓] Speed values use * 60 conversion

RESULT: FAILED - 2 critical issues, 2 warnings
```

## Quick Fix Suggestions

For each issue, provide the fix:

```
ISSUE: Line 5: Parameter 'start_x' should be UPPERCASE
FIX: Change '{% set x = params.start_x | float %}'
  to '{% set x = params.START_X | float %}'
```

## Validation Command

To validate a macro file:
1. Read the file
2. Check each rule
3. Report issues with line numbers
4. Suggest fixes

## Common Issues by Frequency

1. **Lowercase parameters** - Most common mistake
2. **Missing `params.` prefix** - Easy to forget
3. **Untyped variables** - Causes Jinja rendering issues
4. **Direct params in G-code** - Works but violates convention
5. **Missing description** - Documentation gap
