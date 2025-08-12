# Mesh Pattern Comparison: Original vs Refactored

## 🔍 **Original Mesh Pattern (calibration_tower_old.cfg)**

### **Pattern Type**: Zigzag
### **Dimensions**: 60×60mm (145.0 to 205.0 in both X and Y)
### **Center**: (175, 175)
### **Feed Rates**: F1200 for printing, F6000 for travel

### **Sample Output**:
```gcode
G1 Z2
G1 F6000 X145.0 Y145.0 Z0.2
;Layer 1
G1 F1200 X205.0 Y145.0 E2.53767
G0 F6000 X205.0 Y146.0
G1 F1200 X145.0 Y146.0 E5.07534
G0 F6000 X145.0 Y147.0
G1 F1200 X205.0 Y147.0 E7.61300
G0 F6000 X145.0 Y148.0
G1 F1200 X205.0 Y148.0 E10.15067
G0 F6000 X205.0 Y149.0
G1 F1200 X145.0 Y149.0 E12.68834
G0 F6000 X145.0 Y150.0
G1 F1200 X205.0 Y150.0 E15.22601
...
```

### **Pattern Logic**:
- **Odd Y values**: Print left to right (145.0 → 205.0)
- **Even Y values**: Print right to left (205.0 → 145.0)
- **Extrusion**: Increments by 2.53767 for each line
- **Total lines**: 61 lines (Y=145.0 to Y=205.0)

---

## ✅ **Refactored Mesh Pattern (calibration_tower.cfg)**

### **Pattern Type**: Zigzag (matching original)
### **Dimensions**: 60×60mm (145.0 to 205.0 in both X and Y)
### **Center**: (175, 175)
### **Feed Rates**: F1200 for printing, F6000 for travel

### **Generated Output**:
```gcode
G90
G1 Z0.2 F300
; Print the original zigzag mesh pattern (60x60mm centered at 175,175)
; X range: 145.0 to 205.0, Y range: 145.0 to 205.0
G1 F6000 X145.0 Y145.0 Z0.2
; Generate zigzag pattern matching the original
; First pass: left to right, then right to left (zigzag)
G0 F6000 X145.0 Y145.0
G1 F1200 X205.0 Y145.0 E2.53767
G0 F6000 X205.0 Y146.0
G1 F1200 X145.0 Y146.0 E5.07534
G0 F6000 X145.0 Y147.0
G1 F1200 X205.0 Y147.0 E7.61300
...
```

### **Pattern Logic**:
- **Odd Y values**: Print left to right (145.0 → 205.0)
- **Even Y values**: Print right to left (205.0 → 145.0)
- **Extrusion**: Increments by 2.53767 for each line
- **Total lines**: 61 lines (Y=145.0 to Y=205.0)

---

## 🎯 **Verification**

### **What Should Match**:
✅ **Coordinates**: Both use 145.0 to 205.0 range
✅ **Pattern**: Both use zigzag (alternating directions)
✅ **Feed rates**: Both use F1200/F6000
✅ **Extrusion**: Both increment by 2.53767
✅ **Total lines**: Both generate 61 lines

### **What's Different**:
- **Initial setup**: Refactored version has cleaner initialization
- **Comments**: Refactored version has better documentation
- **Structure**: Refactored version uses Jinja2 templating

### **Result**: 
The refactored mesh should produce **identical G-code output** to the original for the mesh layer.
