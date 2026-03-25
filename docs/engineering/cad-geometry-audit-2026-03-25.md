# CAD Geometry Audit — 2026-03-25

## Context

A rigorous geometry-level audit of all 23 active CAD scripts, going beyond constant-checking to verify extrusion directions, sketch plane selections, assembly fit, kinematic chains, and print orientation.

Previous audits (constant-value level) reported 23/23 PASS. This deep audit found 19 CRITICAL + 23 MAJOR issues.

## Methodology

Four parallel audit agents read every line of every script, checking:
1. **Geometry Logic** — sketch planes, extrusion directions, profile selection, boolean operations
2. **Print Orientation & DFM** — overhangs, bed fit, minimum features, layer line direction
3. **Assembly Fit** — bolt pattern alignment, kinematic chain verification, clearances
4. **Code Quality** — silent error handling, magic numbers, unused imports

## Critical Findings (19)

| # | Script | Issue | Fix Applied |
|---|--------|-------|-------------|
| C1 | fixed_wheel_mount.py | Bolt holes on Y axis; connector inserts on X axis | Swapped bolt axis to X |
| C2 | fixed_wheel_mount.py | Motor pocket vertical; should be horizontal | Rewritten to YZ offset plane |
| C3 | steering_knuckle.py | Motor pocket sketched on XY, cuts in Z (vertical) | Rewritten to XZ offset plane, cuts in Y |
| C4 | steering_knuckle.py | Axle bore on XY plane, extrudes in Z (vertical) | Rewritten to YZ offset plane, cuts in X |
| C5 | steering_bracket.py | Hard stop walls join into existing body (no new geometry) | Changed to flip=True, walls protrude downward |
| C6 | servo_mount.py | Horn slot at (0,0) but SG90 shaft offset 5.1mm | Added SHAFT_OFFSET, slot at (-0.51, 0) |
| C7 | servo_mount.py + steering | Servo horn and knuckle arm at different Z heights | NOTE added for assembly-time verification |
| C8 | rocker_hub_connector.py | Tube sockets horizontal; EA-25 says -15°/-20° angled | TODO for angled construction planes |
| C9 | rocker_hub_connector.py | Diff bar bore 8.2mm (slide-fit); EA-25 says 8.0mm (press) | Changed to 0.40cm (8.0mm) |
| C10 | bogie_pivot_connector.py | Bearing seat cut direction ambiguous on XZ plane | TODO with verification guidance |
| C11 | bogie_pivot_connector.py | Tube socket depth ~8mm; needs 15mm | Changed to TUBE_DEPTH-based calculation |
| C12 | front_wheel_connector.py | Tube socket vertical; arm rod is horizontal | Rewritten to XZ offset plane, horizontal entry |
| C13 | middle_wheel_connector.py | Tube socket vertical; same issue as C12 | Same fix pattern |
| C14 | differential_pivot_housing.py | Hard stops non-functional (no matching tab) | TODO for rocker_hub tab feature |
| C15 | body_quadrant.py | 8mm brim on 220mm part exceeds 225mm bed | Changed to 2-3mm brim recommendation |
| C16 | electronics_tray.py | ESP32-S3 DevKitC-1 has NO mounting holes | Redesigned as edge-clip cradle |
| C17 | body_quadrant.py | No clip receiver slots for top deck | TODO with exact dimensions |
| C18 | rover_wheel_v3.py | USE_TPU_TIRE=True default; CTC Bizer can't print TPU | Changed to False |
| C19 | tube_socket_test.py | Grub screw hole vertical instead of radial | Rewritten to XZ plane, radial cut |

## Major Findings (23)

| # | Script | Issue | Fix Applied |
|---|--------|-------|-------------|
| M1 | rocker_hub_connector.py | Wire channels are shallow pockets, not through-paths | NOTE: wires route externally per EA-26 |
| M2 | rocker_hub_connector.py | Docstring promises gussets but none created | TODO for add_triangular_gusset() |
| M3 | rocker_hub_connector.py | Body height 35mm; EA-25 says 40mm | Changed BODY_H_Z to 4.0cm |
| M4 | bogie_pivot_connector.py | 140° spread places sockets nearly horizontal | TODO for angle verification |
| M5 | bogie_pivot_connector.py | No grub screws on front/rear sockets | Added new Step 5b with grub holes |
| M6 | bogie_pivot_connector.py | Wire channel 45mm tall would split body | Changed to WIRE_H (6mm) |
| M7 | front_wheel_connector.py | Wire exit h=0.02 (0.2mm!) magic number | Changed to h=WIRE_H (8mm) |
| M8 | middle_wheel_connector.py | Same 0.2mm wire exit bug | Changed to h=WIRE_H (6mm) |
| M9 | front_wheel_connector.py | Heat-set insert face assignment confused | NOTE for re-verification |
| M10 | middle_wheel_connector.py | Same face assignment issue | NOTE for re-verification |
| M11 | differential_pivot_housing.py | 2.5mm wall between bearing and inserts | NOTE on print settings |
| M12 | body_quadrant.py | Rounded corners on seam edges create gap | NOTE with mitigation options |
| M13 | body_quadrant.py | Tongue-and-groove is just thicker walls | TODO for proper interlock |
| M14 | electronics_tray.py | USB-C cutout 6.7mm off from connector | Added USB_OFFSET_X = 0.67 |
| M15 | electronics_tray.py | Comment says M2.5 but code uses M2 | Corrected comments |
| M16 | electronics_tray.py | No body mounting holes | Added 4x M3 holes at corners |
| M17 | top_deck.py | Edge lips on inner side (jams against wall) | Lip coordinates inverted to extend outward |
| M18 | strain_relief_clip.py | Snap tabs at ends, not sides | Rewritten to Y-axis sides |
| M19 | fuse_holder_bracket.py | M3 holes 0.1mm from channel wall | Widened bracket 15→19mm |
| M20 | battery_tray.py | Strap slots cut in Z instead of through Y wall | Rewritten to XZ offset planes |
| M21 | cable_clip.py | 2mm PLA too rigid for snap-fit | Wall 2.0→1.5mm, gap 3→4mm |
| M22 | rover_wheel_v3.py | O-ring groove depth marginal | Noted (functional but tight) |
| M23 | rover_cad_helpers.py | Grub drill depth WALL+bore_r (overdrills) | Changed to WALL only |

## Systemic Fix: Error Handling

~87 bare `except: pass` blocks replaced with `except Exception as e: print(f'  Warning: {e}')` across all 23 active scripts. Failed geometry operations are now visible in Fusion 360's Text Commands panel.

## Items Requiring Fusion 360 Verification

| Item | Script | Risk if Wrong |
|------|--------|--------------|
| Angled tube sockets (-15°/-20°) | rocker_hub_connector.py | ~6mm arm position error at 0.4 scale |
| Bearing seat cut direction | bogie_pivot_connector.py | Missing bearing pocket |
| Clip receiver slot geometry | body_quadrant.py | Top deck sits loose |
| Tongue-and-groove interlock | body_quadrant.py | Quadrants rely only on dowels+bolts |
| Hard stop tab on diff assembly | differential_pivot_housing.py | No rotation limit on diff bar |
| Servo/knuckle height alignment | servo_mount + steering_bracket | 4-bar linkage may bind |

## Lessons Learned

1. **Constant-checking audits are insufficient.** Verifying that `BEARING_OD = 2.215` is consistent tells you nothing about whether the bearing seat cut goes in the right direction.

2. **Sketch plane selection is the #1 source of geometry bugs.** 8 of 19 critical issues were features sketched on the wrong plane (XY instead of YZ/XZ), causing features to extrude in the wrong direction.

3. **Silent error handling masks geometry failures.** With bare `except: pass`, a script can produce a part that looks complete but is missing the bearing seat, motor pocket, or bolt holes.

4. **Wire routing assumes hollow tubes but rods are solid.** All wire channels should be external routing guides, not internal tunnels.

5. **The SG90 servo shaft is NOT centred on the body.** It's offset 5.1mm from centre (6mm from one edge). Any servo mount must account for this.

6. **ESP32-S3 DevKitC-1 has NO mounting holes.** Cannot use standoff+screw approach; must use edge-clip cradle.

7. **CTC Bizer bed margins are tight.** Body quadrants at 220mm leave only 2.5mm per side. Brim must be minimal or omitted on long edges.

8. **Cross-script assembly verification requires checking actual 3D coordinates**, not just parameter values. Two parts can have matching bolt spacing but on perpendicular axes.
