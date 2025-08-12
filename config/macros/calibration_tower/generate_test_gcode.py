#!/usr/bin/env python3
"""
Test script to generate G-code output from the calibration tower macro.
This helps validate that the refactored version produces the same output as the original.
"""

def generate_test_commands():
    """Generate test commands for different scenarios."""
    
    print("# ===== Test Commands for Calibration Tower =====\n")
    
    # Test 1: Mesh only
    print("# Test 1: Mesh Only")
    print("CONFIGURATION_TOWER CALIBRATION_BLOCKS=0")
    print("# Expected: Should print mesh, then exit early\n")
    
    # Test 2: Single block
    print("# Test 2: Single Configuration Block")
    print("CONFIGURATION_TOWER CALIBRATION_BLOCKS=1")
    print("# Expected: Should print mesh + 1 calibration block\n")
    
    # Test 3: Full tower
    print("# Test 3: Full Calibration Tower")
    print("CONFIGURATION_TOWER")
    print("# Expected: Should print mesh + 10 calibration blocks\n")
    
    # Test 4: Custom parameters
    print("# Test 4: Custom Parameters")
    print("CONFIGURATION_TOWER CALIBRATION_BLOCKS=3 LAYERS_PER_TEST=10")
    print("# Expected: Should print mesh + 3 blocks of 10 layers each\n")

def generate_comparison_commands():
    """Generate commands to help compare with original."""
    
    print("# ===== Comparison Commands =====\n")
    
    print("# To compare with original, you can:")
    print("# 1. Run the new version and capture output:")
    print("#    CONFIGURATION_TOWER CALIBRATION_BLOCKS=1 > new_output.txt")
    print("#")
    print("# 2. Run the old version and capture output:")
    print("#    CONFIGURATION_TOWER_OLD > old_output.txt")
    print("#")
    print("# 3. Compare the files:")
    print("#    diff old_output.txt new_output.txt")
    print("#")
    print("# Note: The old version might need to be renamed back temporarily")
    print("#       or you might need to copy it to a new macro name")

if __name__ == "__main__":
    print("Calibration Tower Test Generator\n")
    generate_test_commands()
    print("\n" + "="*50 + "\n")
    generate_comparison_commands()
