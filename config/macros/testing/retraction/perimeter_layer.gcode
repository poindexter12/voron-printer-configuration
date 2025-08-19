; Advanced Mode: true
;
; Printer:
;  - Firmware: klipper
;  - Bed Shape: Rect
;  - Bed Size X: 350 mm
;  - Bed Size Y: 350 mm
;  - Origin Bed Center: false
;  - Extruder Name: Disabled
;  - Travel Speed: 120 mm/s
;  - Nozzle Diameter: 0.4 mm
;  - Filament Diameter: 1.7 mm
;  - Extrusion Multiplier: 1
;
; Retraction / Z Hop:
;  - Firmware Retraction: false
;  - Retraction Distance: 0.5 mm
;  - Retract Speed: 35 mm/s
;  - Unretract Speed: 35 mm/s
;  - Z Hop Enable: true
;  - Z Hop Height: 0.1mm
;
; First Layer Settings:
;  - First Layer Height: 0.25 mm
;  - First Layer Printing Speed: 30 mm/s
;  - First Layer Fan Speed: 0%
;  - Anchor Option: anchor_frame
;  - Anchor Frame Perimeters: 4
;  - Anchor Line Width: 140 %
;
; Print Settings:
;  - Line Width: 112.5 %
;  - Layer Count: 4
;  - Layer Height: 0.2 mm
;  - Print Speed: 100 mm/s
;  - Acceleration: Disabled
;  - Fan Speed: 100%
;
; Pattern Settings `(Customized)`:
;  - Wall Count: 3
;  - Side Length: 30 mm
;  - Spacing: 2 mm
;  - Corner Angle: 90 degrees 
;  - Printing Direction: 0 degree
;
; Pressure Advance Stepping:
;  - PA Start Value: 0
;  - PA End Value: 0.08
;  - PA Increment: 0.005
;  - Increment Smooth Time Instead: false
;  - Show on LCD: true
;  - Number Tab: true
;  - No Leading Zeroes: false
;
; Start / End G-code:
;  - Hotend Temp: 200C
;  - Bed Temp: 60C
;  - Don't Add G28: false
;  - Don't Add Heating G-Codes: false
;  - Entered Start G-code: 
;       G28 ; Home all axes
;       M190 S60 ; Set & wait for bed temp
;       M109 S200 ; Set & wait for hotend temp
;       PRINT_START ; Start macro
;       ; START_PRINT ; Start macro (alternate / official start macro name)
;  - Entered End G-code: 
;       PRINT_END ; End macro. Change name to match yours
;
; Calculated Values:
;  - Print Size X: 84.72 mm
;  - Print Size Y: 53.99 mm
;  - Number of Patterns to Print: 17
;  - PA Values: 0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08
;

G1 X132.6417 Y190.4332 E2.36613 F1800 ; Draw perimeter (up)
G1 X217.3583 Y190.4332 E4.72467 F1800 ; Draw perimeter (right)
G1 X217.3583 Y148.0068 E2.36613 F1800 ; Draw perimeter (down)
G1 X132.6417 Y148.0068 E4.72467 F1800 ; Draw perimeter (left)
G0 X133.148 Y148.5131 F7200 ; Step inwards to print next perimeter
G1 X133.148 Y189.9269 E2.30965 F1800 ; Draw perimeter (up)
G1 X216.852 Y189.9269 E4.66819 F1800 ; Draw perimeter (right)
G1 X216.852 Y148.5131 E2.30965 F1800 ; Draw perimeter (down)
G1 X133.148 Y148.5131 E4.66819 F1800 ; Draw perimeter (left)
G0 X133.6544 Y149.0195 F7200 ; Step inwards to print next perimeter
G1 X133.6544 Y189.4205 E2.25317 F1800 ; Draw perimeter (up)
G1 X216.3456 Y189.4205 E4.61171 F1800 ; Draw perimeter (right)
G1 X216.3456 Y149.0195 E2.25317 F1800 ; Draw perimeter (down)
G1 X133.6544 Y149.0195 E4.61171 F1800 ; Draw perimeter (left)
G0 X134.1607 Y149.5258 F7200 ; Step inwards to print next perimeter
G1 X134.1607 Y188.9142 E2.1967 F1800 ; Draw perimeter (up)
G1 X215.8393 Y188.9142 E4.55523 F1800 ; Draw perimeter (right)
G1 X215.8393 Y149.5258 E2.1967 F1800 ; Draw perimeter (down)
G1 X134.1607 Y149.5258 E4.55523 F1800 ; Draw perimeter (left)
