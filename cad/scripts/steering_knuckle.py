"""
Mars Rover Steering Knuckle — Phase 1
=======================================

Steering upright/knuckle for the 4 steered wheels (FL, FR, RL, RR).
Rotates about a vertical (Z-axis) steering pivot and carries the
wheel axle + motor mount below.

Redesigned with:
  - Tapered organic body (wider at pivot, narrower at axle) via revolve
  - Rounded steering arm ends (stadium shape)
  - 0.5mm fillets on external edges
  - Tube socket with grub screw via shared helper
  - Rounded N20 motor pocket via helper
  - Chamfered axle bore entries
  - Hard stop tab with rounded profile

The knuckle connects:
  - TOP: Steering pivot shaft (into bearing in bracket)
  - SIDE: Steering arm extension (M2 hole for horn link pin joint)
  - TOP: Hard stop tab (contacts bracket ±35° walls)
  - MIDDLE: Motor mount recess (N20 gearmotor clip)
  - BOTTOM: Wheel axle through-bore

Overall size: ~25 × 30 × 40mm body + 15mm arm extension
Print: Upright (pivot socket up), PLA, 60% infill, 4 perimeters
Qty: 4 (FL, FR, RL, RR — all identical, symmetric design)

Reference: EA-27 (steering design package), EA-26 Section 12, EA-10
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, CORNER_R,
    TUBE_BORE, TUBE_DEPTH, GRUB_M3, M2_CLEAR,
    N20_W, N20_H, N20_D,
    draw_rounded_rect, draw_stadium,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_n20_clip, make_m3_grub_hole,
    add_edge_fillets, zoom_fit,
)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('No active design.')
            return

        # ── Dimensions (cm) ──
        # Pivot (top)
        PIV_BORE_R = TUBE_BORE / 2    # 4.1mm (8.2mm bore)
        PIV_DEPTH = 1.5                # 15mm socket depth
        PIV_WALL = 0.4                 # 4mm wall around pivot

        # Body
        BODY_W = 2.5       # 25mm width (X)
        BODY_L = 3.0       # 30mm length (Y)
        BODY_H = 4.0       # 40mm height (Z)

        # Taper: body narrows from top (pivot) to bottom (axle)
        BODY_W_BOT = 2.0   # 20mm at bottom (narrower)
        BODY_L_BOT = 2.5   # 25mm at bottom

        # Motor mount (N20)
        AXLE_R = 0.2       # 4mm bore for N20 D-shaft
        AXLE_Z = 0.8       # 8mm up from bottom (axle centre height)

        # Steering arm (EA-27)
        ARM_LENGTH = 1.5   # 15mm from pivot centre
        ARM_WIDTH = 0.8    # 8mm arm width
        ARM_HEIGHT = 0.5   # 5mm arm thickness
        ARM_HOLE_R = M2_CLEAR  # M2 clearance

        # Hard stop tab (EA-27)
        STOP_TAB_W = 0.5   # 5mm tab width
        STOP_TAB_R = 0.8   # 8mm radial extent
        STOP_TAB_H = 0.3   # 3mm tab thickness

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Main body — tapered rounded-rect (wider at top)
        # Use a straight extrude with draft angle for organic taper
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Knuckle Body'
        draw_rounded_rect(sk, 0, 0, BODY_W, BODY_L, r=CORNER_R)

        target = BODY_W * BODY_L - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext_input = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_input.setDistanceExtent(False, val(BODY_H))

        # Add slight draft taper for organic look (2°)
        try:
            ext_input.taperAngle = val(math.radians(-2))
        except Exception as e:
            print(f'  Warning: {e}')

        ext = extrudes.add(ext_input)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Steering Knuckle'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Pivot shaft socket (from top, down)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, BODY_H)

        piv_sk = comp.sketches.add(top_plane)
        piv_sk.name = 'Pivot Socket'
        piv_sk.sketchCurves.sketchCircles.addByCenterRadius(p(0, 0), PIV_BORE_R)

        piv_prof = find_smallest_profile(piv_sk)
        cut_profile(comp, piv_prof, PIV_DEPTH, flip=True)

        # Entry chamfer on pivot socket
        if body:
            from rover_cad_helpers import add_chamfer
            add_chamfer(comp, body, PIV_BORE_R, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 3: M3 grub screw for pivot shaft retention
        # ══════════════════════════════════════════════════════════

        grub_z = BODY_H - PIV_DEPTH / 2
        grub_plane = make_offset_plane(comp, comp.xYConstructionPlane, grub_z)

        grub_sk = comp.sketches.add(grub_plane)
        grub_sk.name = 'Pivot Grub Screw'
        grub_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_L / 2 - 0.1), GRUB_M3
        )

        grub_prof = find_smallest_profile(grub_sk)
        if grub_prof:
            grub_input = extrudes.createInput(
                grub_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            grub_input.setDistanceExtent(
                True, val(BODY_L / 2 + PIV_BORE_R + 0.01)
            )
            try:
                extrudes.add(grub_input)
            except Exception as e:
                print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: Motor mount pocket (N20 entering from -Y face, horizontal)
        # Sketch on XZ offset plane at Y = -BODY_L/2 (the -Y face),
        # coordinates are (X, Z), extrusion goes in +Y into body.
        # ══════════════════════════════════════════════════════════

        motor_plane = make_offset_plane(
            comp, comp.xZConstructionPlane, -BODY_L / 2
        )

        motor_sk = comp.sketches.add(motor_plane)
        motor_sk.name = 'Motor Pocket'
        # Sketch on XZ plane: coords are (X, Z)
        # Motor pocket centred at X=0, Z=AXLE_Z (motor centre height)
        draw_rounded_rect(
            motor_sk,
            cx=0, cy=AXLE_Z,
            w=N20_W, h=N20_H,
            r=0.05
        )

        motor_target = N20_W * N20_H
        motor_prof = find_profile_by_area(motor_sk, motor_target, tolerance=0.4)
        if motor_prof is None:
            motor_prof = find_largest_profile(motor_sk)
        if motor_prof:
            # XZ plane normal = +Y; flip=False → +Y (into body from -Y face)
            m_input = extrudes.createInput(
                motor_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            m_input.setDistanceExtent(False, val(N20_D))
            try:
                extrudes.add(m_input)
            except Exception as e:
                print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5: Wheel axle bore (horizontal, through body along X)
        # Sketch on YZ offset plane at X = -BODY_W/2 (the -X face),
        # coordinates are (Y, Z), extrusion goes in +X through body.
        # ══════════════════════════════════════════════════════════

        axle_plane = make_offset_plane(
            comp, comp.yZConstructionPlane, -BODY_W / 2
        )
        axle_sk = comp.sketches.add(axle_plane)
        axle_sk.name = 'Axle Bore'
        # Sketch on YZ plane: coords are (Y, Z)
        # Bore centred at Y=0, Z=AXLE_Z
        axle_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, AXLE_Z), AXLE_R
        )

        axle_prof = find_smallest_profile(axle_sk)
        if axle_prof:
            # YZ plane normal = +X; flip=False → +X (through body)
            ax_input = extrudes.createInput(
                axle_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            ax_input.setDistanceExtent(False, val(BODY_W + 0.1))
            try:
                extrudes.add(ax_input)
            except Exception as e:
                print(f'  Warning: {e}')

        # Axle bore chamfers
        if body:
            from rover_cad_helpers import add_chamfer
            add_chamfer(comp, body, AXLE_R, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 6: Steering arm extension (EA-27 — stadium shape)
        # ══════════════════════════════════════════════════════════

        arm_z = BODY_H - PIV_DEPTH / 2
        arm_plane = make_offset_plane(
            comp, comp.xYConstructionPlane, arm_z - ARM_HEIGHT / 2
        )

        arm_sk = comp.sketches.add(arm_plane)
        arm_sk.name = 'Steering Arm'

        # Stadium shape for the arm (wider at body, rounded at tip)
        arm_tip_x = BODY_W / 2 - 0.2 + ARM_LENGTH
        arm_mid_x = (BODY_W / 2 - 0.2 + arm_tip_x) / 2
        arm_half_len = (arm_tip_x - (BODY_W / 2 - 0.2)) / 2

        draw_stadium(
            arm_sk,
            cx=BODY_W / 2 - 0.2 + arm_half_len,
            cy=0,
            half_length=arm_half_len,
            radius=ARM_WIDTH / 2
        )

        arm_target = (arm_half_len * 2) * ARM_WIDTH + math.pi * (ARM_WIDTH / 2)**2
        arm_prof = find_profile_by_area(arm_sk, arm_target, tolerance=0.5)
        if arm_prof is None:
            arm_prof = find_largest_profile(arm_sk)
        join_profile(comp, arm_prof, ARM_HEIGHT)

        # M2 hole at arm tip
        arm_hole_plane = make_offset_plane(
            comp, comp.xYConstructionPlane, arm_z + ARM_HEIGHT / 2
        )
        arm_hole_sk = comp.sketches.add(arm_hole_plane)
        arm_hole_sk.name = 'Arm Link Hole'
        arm_hole_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(arm_tip_x - ARM_WIDTH / 2, 0), ARM_HOLE_R
        )

        arm_hole_prof = find_smallest_profile(arm_hole_sk)
        cut_profile(comp, arm_hole_prof, ARM_HEIGHT + 0.01, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 7: Hard stop tab (EA-27 — rounded profile)
        # ══════════════════════════════════════════════════════════

        stop_plane = make_offset_plane(comp, comp.xYConstructionPlane, BODY_H)
        stop_sk = comp.sketches.add(stop_plane)
        stop_sk.name = 'Hard Stop Tab'

        # Stadium-shaped tab extending in +Y direction
        tab_cy = BODY_L / 2 - 0.1 + STOP_TAB_R / 2
        draw_stadium(
            stop_sk,
            cx=0, cy=tab_cy,
            half_length=STOP_TAB_W / 2,
            radius=STOP_TAB_R / 2
        )

        tab_target = STOP_TAB_W * STOP_TAB_R + math.pi * (STOP_TAB_R / 2)**2
        stop_prof = find_profile_by_area(stop_sk, tab_target, tolerance=0.6)
        if stop_prof is None:
            stop_prof = find_largest_profile(stop_sk)
        join_profile(comp, stop_prof, STOP_TAB_H)

        # ══════════════════════════════════════════════════════════
        # STEP 8: External fillets
        # ══════════════════════════════════════════════════════════

        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)
        else:
            fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # STEP 9: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Steering Knuckle created! (EA-27)\n\n'
            f'Body: {BODY_W*10:.0f} × {BODY_L*10:.0f} × {BODY_H*10:.0f}mm '
            f'(tapered, rounded corners)\n\n'
            f'PIVOT SOCKET: {PIV_BORE_R*20:.1f}mm × {PIV_DEPTH*10:.0f}mm deep '
            f'(chamfered entry, M3 grub)\n\n'
            f'STEERING ARM (EA-27): {ARM_LENGTH*10:.0f}mm, stadium shape\n'
            f'  M2 hole at tip for horn link\n\n'
            f'HARD STOP TAB: {STOP_TAB_W*10:.0f}×{STOP_TAB_R*10:.0f}×'
            f'{STOP_TAB_H*10:.0f}mm (rounded)\n\n'
            f'MOTOR: N20 pocket {N20_W*10:.1f}×{N20_H*10:.1f}mm\n'
            f'AXLE: {AXLE_R*20:.0f}mm through (chamfered)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Print upright (pivot socket up), 60% infill.\n'
            'Qty: 4 (all steered wheels)',
            'Mars Rover - Steering Knuckle'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
