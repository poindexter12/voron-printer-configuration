#!/usr/bin/env python3
"""
Test script for the calibration tower G-code generator.
This demonstrates how to use the generate_gcode_output.py script.
"""

import subprocess
import sys
import os

def run_gcode_generator(macro_file, output_file=None, params=None):
    """Run the G-code generator with the given parameters."""
    cmd = ["python3", "generate_gcode_output.py", macro_file]
    
    if output_file:
        cmd.append(output_file)
    
    if params:
        for key, value in params.items():
            cmd.append(f"{key}={value}")
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Failed to run command: {e}")

def main():
    """Main test function."""
    print("Calibration Tower G-code Generator Test")
    print("=" * 50)
    
    # Path to the calibration tower macro
    macro_file = "../config/macros/calibration_tower/calibration_tower.cfg"
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Mesh Only (CALIBRATION_BLOCKS=0)",
            "params": {"CALIBRATION_BLOCKS": 0},
            "output": "mesh_only.gcode"
        },
        {
            "name": "Single Block (CALIBRATION_BLOCKS=1)",
            "params": {"CALIBRATION_BLOCKS": 1},
            "output": "single_block.gcode"
        },
        {
            "name": "Full Tower (CALIBRATION_BLOCKS=15)",
            "params": {"CALIBRATION_BLOCKS": 15},
            "output": "full_tower.gcode"
        },
        {
            "name": "Custom Parameters",
            "params": {"CALIBRATION_BLOCKS": 3, "LAYERS_PER_TEST": 10},
            "output": "custom_params.gcode"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 40)
        run_gcode_generator(macro_file, scenario['output'], scenario['params'])
        print()

if __name__ == "__main__":
    main()
