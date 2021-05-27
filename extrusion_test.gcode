; Extrusion test g-code by cnc Kitchen (https://www.cnckitchen.com)
; reused here with permission under MIT license
; Extrusion test speed table:
; 1 mm³/s = 25 mm/min
; 2 mm³/s = 50 mm/min
; 3 mm³/s = 75 mm/min
; 5 mm³/s = 125 mm/min
; 7.5 mm³/s = 187 mm/min
; 10 mm³/s = 249 mm/min
; 12.5 mm³/s = 312 mm/min
; 15 mm³/s = 374 mm/min
; 17.5 mm³/s = 437 mm/min
; 20 mm³/s = 499 mm/min

M104 S200				; Set Nozzle Temperature
M109
G1 X150 Y80 Z60 F10000	; Go to extrusion position
M83						; Relative Extrusions
G1 F200 				; Prime
G1 E20
G4 S2

G1 F25 					; Set Extrusion Speed in mm/min HERE

G1 E100					; Extrude 100 mm
G1 E100					; Extrude 100 mm
G4 S0
G1 E-5 F1000			; Retract 5 mm