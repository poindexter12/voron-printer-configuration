#!/usr/bin/env python3
"""
G-code Generator for Klipper Macros
This script simulates the Jinja2 template processing to generate actual G-code output
without needing to run it on the printer.

Usage:
    python3 generate_gcode_output.py <macro_file> [output_file] [parameters...]

Examples:
    python3 generate_gcode_output.py ../config/macros/calibration_tower/calibration_tower.cfg
    python3 generate_gcode_output.py ../config/macros/calibration_tower/calibration_tower.cfg output.gcode CALIBRATION_BLOCKS=0
    python3 generate_gcode_output.py ../config/macros/calibration_tower/calibration_tower.cfg output.gcode CALIBRATION_BLOCKS=1 LAYERS_PER_TEST=20
"""

import re
import sys
import os
from pathlib import Path

def extract_jinja_variables(template_content):
    """Extract Jinja2 variables from template content."""
    variables = {}
    
    # Find {% set variable = value %} patterns
    set_pattern = r'{%\s*set\s+(\w+)\s*=\s*([^%]+)%}'
    matches = re.findall(set_pattern, template_content)
    
    for var_name, var_value in matches:
        # Clean up the value and evaluate it
        var_value = var_value.strip()
        try:
            # Handle simple expressions
            if '|default(' in var_value:
                # Extract default value
                default_match = re.search(r'\|default\(([^)]+)\)', var_value)
                if default_match:
                    default_val = default_match.group(1)
                    if default_val.isdigit():
                        variables[var_name] = int(default_val)
                    elif '.' in default_val:
                        variables[var_name] = float(default_val)
                    else:
                        variables[var_name] = default_val.strip('"\'')
            else:
                # Simple value
                if var_value.isdigit():
                    variables[var_name] = int(var_value)
                elif '.' in var_value:
                    variables[var_name] = float(var_value)
                else:
                    variables[var_name] = var_value.strip('"\'')
        except (ValueError, SyntaxError):
            variables[var_name] = var_value
    
    return variables

def process_jinja_loops(template_content, variables):
    """Process Jinja2 loops and conditionals."""
    output = template_content
    
    # Process {% for %} loops
    for_pattern = r'{%\s*for\s+(\w+)\s+in\s+range\(([^)]+)\)\s*%}(.*?){%\s*endfor\s*%}'
    
    def replace_loop(match):
        var_name = match.group(1)
        range_expr = match.group(2)
        loop_body = match.group(3)
        
        # Parse range expression
        if ',' in range_expr:
            parts = [p.strip() for p in range_expr.split(',')]
            if len(parts) == 2:
                start = eval(parts[0], variables)
                end = eval(parts[1], variables)
                step = 1
            elif len(parts) == 3:
                start = eval(parts[0], variables)
                end = eval(parts[1], variables)
                step = eval(parts[2], variables)
            else:
                return match.group(0)
        else:
            end = eval(range_expr, variables)
            start = 0
            step = 1
        
        # Generate loop iterations
        result = []
        for i in range(start, end, step):
            loop_vars = variables.copy()
            loop_vars[var_name] = i
            
            # Replace variables in loop body
            body = loop_body
            for var, val in loop_vars.items():
                body = body.replace(f'{{{var}}}', str(val))
            
            result.append(body)
        
        return '\n'.join(result)
    
    output = re.sub(for_pattern, replace_loop, output, flags=re.DOTALL)
    
    # Process {% if %} statements
    if_pattern = r'{%\s*if\s+([^%]+)%}(.*?){%\s*endif\s*%}'
    
    def replace_if(match):
        condition = match.group(1)
        if_body = match.group(2)
        
        try:
            # Evaluate condition
            if eval(condition, variables):
                return if_body
            else:
                return ''
        except (ValueError, SyntaxError, NameError):
            return match.group(0)
    
    output = re.sub(if_pattern, replace_if, output, flags=re.DOTALL)
    
    return output

def generate_gcode_output(macro_file, params=None):
    """Generate G-code output from a macro file."""
    if params is None:
        params = {}
    
    # Read the macro file
    with open(macro_file, 'r') as f:
        content = f.read()
    
    # Extract variables
    variables = extract_jinja_variables(content)
    
    # Override with provided parameters
    variables.update(params)
    
    # Process Jinja2 templates
    output = process_jinja_loops(content, variables)
    
    # Replace remaining variables
    for var, val in variables.items():
        output = output.replace(f'{{{var}}}', str(val))
    
    # Clean up Jinja2 syntax
    output = re.sub(r'{%[^%]*%}', '', output)
    output = re.sub(r'{[^}]*}', '', output)
    
    # Extract only G-code lines
    gcode_lines = []
    for line in output.split('\n'):
        line = line.strip()
        if line and (line.startswith('G') or line.startswith('M') or line.startswith(';')):
            gcode_lines.append(line)
    
    return '\n'.join(gcode_lines)

def parse_parameters(param_strings):
    """Parse parameter strings like 'CALIBRATION_BLOCKS=0' into a dictionary."""
    params = {}
    for param_str in param_strings:
        if '=' in param_str:
            key, value = param_str.split('=', 1)
            try:
                if value.isdigit():
                    params[key] = int(value)
                elif '.' in value:
                    params[key] = float(value)
                else:
                    params[key] = value.strip('"\'')
            except ValueError:
                params[key] = value
    return params

def main():
    """Main function to generate G-code output."""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    macro_file = sys.argv[1]
    
    # Check if macro file exists
    if not os.path.exists(macro_file):
        print(f"Error: Macro file '{macro_file}' not found.")
        return
    
    # Parse output file (optional)
    output_file = None
    if len(sys.argv) > 2 and not '=' in sys.argv[2]:
        output_file = sys.argv[2]
        params_start = 3
    else:
        params_start = 2
    
    # Parse parameters
    param_strings = sys.argv[params_start:] if len(sys.argv) > params_start else []
    params = parse_parameters(param_strings)
    
    print(f"Generating G-code from: {macro_file}")
    if params:
        print(f"Parameters: {params}")
    if output_file:
        print(f"Output file: {output_file}")
    print("-" * 50)
    
    try:
        gcode = generate_gcode_output(macro_file, params)
        gcode_lines = gcode.split('\n')
        
        print(f"Generated {len(gcode_lines)} G-code commands")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(gcode)
            print(f"G-code saved to: {output_file}")
        else:
            print("\nFirst 20 lines of generated G-code:")
            print("-" * 30)
            for i, line in enumerate(gcode_lines[:20]):
                print(f"{i+1:3d}: {line}")
            
            if len(gcode_lines) > 20:
                print(f"... and {len(gcode_lines) - 20} more lines")
        
    except Exception as e:
        print(f"Error generating G-code: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
