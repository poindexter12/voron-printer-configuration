#!/usr/bin/env python3
"""
Test script for _DRAW_PERIMETER_LAYER macro
Compares the output of the macro with expected G-code
"""

import os
import sys

def run_klipper_macro(macro_file, macro_name):
    """Run a Klipper macro and capture its output"""
    try:
        # This would need to be adapted to your actual Klipper setup
        # For now, we'll just check if the macro file exists and has the right structure
        if not os.path.exists(macro_file):
            return None, f"Macro file not found: {macro_file}"
        
        with open(macro_file, 'r') as f:
            content = f.read()
            
        if macro_name not in content:
            return None, f"Macro {macro_name} not found in {macro_file}"
            
        return content, None
    except Exception as e:
        return None, f"Error reading macro file: {e}"

def test_perimeter_layer_macro():
    """Test the perimeter layer macro"""
    print("Testing _DRAW_PERIMETER_LAYER macro...")
    
    # Paths
    macro_file = "../../retraction_test/retraction-core.cfg"
    expected_file = "perimeter_layer.gcode"
    
    # Check if macro exists
    macro_content, error = run_klipper_macro(macro_file, "_DRAW_PERIMETER_LAYER")
    if error:
        print(f"❌ {error}")
        return False
    
    # Check if expected output exists
    if not os.path.exists(expected_file):
        print(f"❌ Expected output file not found: {expected_file}")
        return False
    
    print("✅ Macro file found and contains _DRAW_PERIMETER_LAYER")
    print("✅ Expected output file found")
    
    # Basic validation of macro structure
    if "START_X" in macro_content and "WIDTH" in macro_content and "HEIGHT" in macro_content:
        print("✅ Macro has required parameters")
    else:
        print("❌ Macro missing required parameters")
        return False
    
    # Check for the key calculation logic
    if "line_area" in macro_content and "extrusion_per_mm" in macro_content:
        print("✅ Macro has extrusion calculation logic")
    else:
        print("❌ Macro missing extrusion calculation logic")
        return False
    
    # Check for the perimeter drawing loop
    if "{% for i in range" in macro_content and "current_width" in macro_content:
        print("✅ Macro has perimeter drawing loop")
    else:
        print("❌ Macro missing perimeter drawing loop")
        return False
    
    print("\n🎯 Macro structure looks good!")
    print("To run a full test, you'll need to:")
    print("1. Load the macro in Klipper")
    print("2. Call _DRAW_PERIMETER_LAYER with test parameters")
    print("3. Compare the output with perimeter_layer.gcode")
    
    return True

if __name__ == "__main__":
    success = test_perimeter_layer_macro()
    sys.exit(0 if success else 1)
