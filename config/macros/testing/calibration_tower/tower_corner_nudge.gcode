;Calibration Generator 1.3.4
;
;
;Retraction Distance from the top looking down
;
;       3.25    3.00    2.75    2.50
;		|		|		|		|
;
;3.50-                               -2.25
;
;
;3.75-                               -2.00
;
;
;4.00-                               -1.75
;
;
;4.25-                               -1.50
;
;		|		|		|		|
;       0.50    0.75    1.00    1.25
;
;
;Variables by Height
;
;Height         Retraction  Nozzle      Fan
;               Speed       Temp        Speed
;
;25 layers      150.00      215.00      40.00
;25 layers      140.00      215.00      40.00
;25 layers      130.00      215.00      40.00
;25 layers      120.00      215.00      40.00
;25 layers      110.00      215.00      40.00
;25 layers      100.00      215.00      40.00
;25 layers      90.00      215.00      40.00
;25 layers      80.00      215.00      40.00
;25 layers      70.00      215.00      40.00
;25 layers      60.00      215.00      40.00
;25 layers      50.00      215.00      40.00
;25 layers      40.00      215.00      40.00
;25 layers      30.00      215.00      40.00
;25 layers      20.00      215.00      40.00
;25 layers      10.00      215.00      40.00
;
;
;All inputs
;
;Dimension X 					350
;Dimension Y 					350
;Starting Retraction Distance	0.5
;Increment Retraction 			0.25
;Start Retraction Speed 		10.0
;Retraction Speed Increment 	10.0
;Print Speed 					40.0
;Starting Temp 					215
;Increment Temp 				0
;Bed Temp 						75
;Fan Speed 						40
;Fan Speed Increment 			0
;Nozzle Diameter 				0.4
;Layer Height 					0.2
;Filament Diameter 				1.7
;Extrusion Multiplier 			1.0
;Layers Per Test                25.0
;Number of Tests                15.0

; These are the four nudge commands for the tower corner from the original file

; # first nudge, 0 degrees of rotation
; G1 F2400 X-2 E0.03384
; G1 F2400 Y-2 E0.03384
; G1 F2400 X2 E0.03384
; G1 F2400 Y2 E0.03384

; # second nudge, 90 degrees of rotation
; G1 F2400 X1 E0.03384
; G1 F2400 Y-1 E0.03384
; G1 F2400 X-1 E0.03384
; G1 F2400 Y1 E0.03384

; # third nudge, 180 degrees of rotation
; G1 F2400 X1 E0.03384
; G1 F2400 Y1 E0.03384
; G1 F2400 X-1 E0.03384
; G1 F2400 Y-1 E0.03384

# fourth nudge, 270 degrees of rotation
G1 F2400 X-1 E0.03384
G1 F2400 Y1 E0.03384
G1 F2400 X1 E0.03384
G1 F2400 Y-1 E0.03384