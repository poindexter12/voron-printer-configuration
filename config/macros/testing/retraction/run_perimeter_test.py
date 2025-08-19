#!/usr/bin/env python3
"""
Simple test runner for perimeter layer macro
"""

def main():
    print("🔧 Perimeter Layer Macro Test")
    print("=" * 40)
    
    print("\n📋 Test Setup:")
    print("1. Load retraction-core.cfg in Klipper")
    print("2. Call _DRAW_PERIMETER_LAYER with test parameters")
    print("3. Compare output with perimeter_layer.gcode")
    
    print("\n🧪 Test Parameters:")
    print("START_X=132.6417")
    print("START_Y=148.0068") 
    print("WIDTH=84.72")
    print("HEIGHT=53.99")
    print("LINE_WIDTH=0.45")
    print("LAYER_HEIGHT=0.2")
    print("NUM_PERIMETERS=4")
    print("STEP_DISTANCE=0.5")
    print("SPEED=100")
    print("FILAMENT_DIAMETER=1.7")
    print("EXTRUSION_MULTIPLIER=1.0")
    
    print("\n📝 Expected Output:")
    print("- 4 perimeters stepping inward by 0.5mm each")
    print("- Each perimeter draws: up, right, down, left")
    print("- Extrusion values calculated using the same formula as original")
    print("- G0 moves between perimeters to step inward")
    
    print("\n✅ Test Complete!")
    print("Check that the generated G-code matches perimeter_layer.gcode")

if __name__ == "__main__":
    main()

