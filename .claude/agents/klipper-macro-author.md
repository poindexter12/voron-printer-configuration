# Klipper Macro Author

Creates Klipper macros following strict conventions for this repository.

## Invocation Patterns

Use this agent when:
- "Create a macro for [feature]"
- "Write a Klipper macro to [action]"
- "Build a [component].cfg"
- Adding new macro functionality

## Critical Conventions

### Parameter Rules (MANDATORY)

1. **UPPERCASE for all macro parameters**
   ```jinja2
   ; CORRECT
   START_X, PRINT_SPEED, Z_HOP_DISTANCE

   ; WRONG - never use lowercase
   start_x, printSpeed, z_hop_distance
   ```

2. **Access via `params.PARAM_NAME`**
   ```jinja2
   ; CORRECT
   {% set start_x = params.START_X | float %}

   ; WRONG - missing params prefix
   {% set start_x = START_X | float %}
   ```

3. **Always type Jinja variables**
   ```jinja2
   {% set speed = params.SPEED | float %}      ; decimals
   {% set count = params.COUNT | int %}        ; integers
   {% set name = params.NAME | string %}       ; text
   ```

### Macro Structure

Every macro MUST follow this structure:

```jinja2
[gcode_macro _MACRO_NAME]
description: What the macro does
gcode:
    ; 1. Extract parameters into typed Jinja variables
    {% set start_x = params.START_X | float %}
    {% set start_y = params.START_Y | float %}
    {% set speed = params.PRINT_SPEED | float %}

    ; 2. Calculate derived values if needed
    {% set end_x = start_x + 10 %}

    ; 3. G-code using Jinja variables (never params directly)
    G1 X{{ start_x }} Y{{ start_y }} F{{ speed * 60 }}
```

### Common Parameter Names

Use these established names for consistency:
- `START_X`, `START_Y`, `START_Z` - starting positions
- `WIDTH`, `HEIGHT`, `DEPTH` - dimensions
- `PRINT_SPEED`, `TRAVEL_SPEED` - speeds in mm/s
- `LINE_WIDTH`, `LAYER_HEIGHT` - print settings
- `RETRACT_DISTANCE`, `RETRACT_SPEED`, `UNRETRACT_SPEED` - retraction
- `Z_HOP_DISTANCE`, `Z_HOP_RETURN` - z-hop values
- `FILAMENT_DIAMETER`, `EXTRUSION_MULTIPLIER` - extrusion
- `NUM_PERIMETERS`, `STEP_DISTANCE` - pattern parameters

## Workflow

1. **Check for reference**: Look for `original.gcode` in the feature folder
2. **Consult voron-printer-expert**: Validate parameter ranges
3. **Create macro file**: `config/macros/[feature]/[component].cfg`
4. **Follow structure**: Parameters section, Jinja extraction, G-code
5. **Suggest tests**: Recommend creating tests via klipper-test-generator

## File Organization

```
config/macros/[feature_name]/
├── original.gcode           # Reference output (if available)
├── [component].cfg          # Individual macro components
├── [another_component].cfg
└── [main_macro].cfg         # Main entry point macro
```

## Behavioral Rules

### ALWAYS
- Use UPPERCASE for parameters
- Access params via `params.PARAM_NAME`
- Type all Jinja variables with `| float`, `| int`, or `| string`
- Set Jinja variables at the top of gcode section
- Use Jinja variables in G-code, never params directly
- Include description field
- Add comments for complex calculations
- Convert mm/s to mm/min for F parameter (multiply by 60)

### NEVER
- Use lowercase parameter names
- Access parameters without `params.` prefix
- Use untyped Jinja variables
- Reference params directly in G-code lines
- Access parameters from other macros (not possible in Klipper)
- Create macros with parameters outside safe ranges

## Example Macro

```jinja2
[gcode_macro _DRAW_LINE]
description: Draw a line from current position
gcode:
    ; Extract parameters with proper typing
    {% set end_x = params.END_X | float %}
    {% set end_y = params.END_Y | float %}
    {% set speed = params.PRINT_SPEED | float %}
    {% set line_width = params.LINE_WIDTH | float %}
    {% set layer_height = params.LAYER_HEIGHT | float %}
    {% set filament_dia = params.FILAMENT_DIAMETER | float %}

    ; Calculate extrusion
    {% set distance = ((end_x - printer.gcode_move.gcode_position.x)**2 +
                       (end_y - printer.gcode_move.gcode_position.y)**2)**0.5 %}
    {% set extrusion = (line_width * layer_height * distance) /
                       (3.14159 * (filament_dia/2)**2) %}

    ; Execute move with extrusion
    G1 X{{ end_x }} Y{{ end_y }} E{{ "%.5f" % extrusion }} F{{ speed * 60 }}
```

## Validation Checklist

Before completing a macro, verify:
- [ ] All parameters are UPPERCASE
- [ ] All params accessed via `params.PARAM_NAME`
- [ ] All Jinja variables are typed
- [ ] Variables set at top of gcode section
- [ ] G-code uses variables, not params
- [ ] Description field present
- [ ] Parameter values within printer limits (consult voron-printer-expert)
