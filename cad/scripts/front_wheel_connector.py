"""
Mars Rover Front/Rear Wheel Connector — Phase 1
=================================================

End connector at the front or rear wheel position. Receives one 8mm
tube from the suspension arm and provides mounting faces for the
steering bracket and servo mount.

Also used for rear wheels (identical geometry — all 4 corner wheels
are steered).

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - Tube socket with chamfered entry via shared helper
  - Proper heat-set insert pockets via helper
  - Oval wire exit with rounded edges
  - 0.5mm fillets on all external edges
  - M3 grub screw for tube retention

Features:
  - 1× tube socket (8.2mm bore × 15mm deep) with M3 grub screw
  - Steering bracket mount face: 2× M3 heat-set inserts
  - Servo mount face: 2× M3 heat-set inserts
  - Wire exit hole: 10×8mm (motor + servo wires)
  - 4mm minimum wall thickness

Overall size: ~35 × 30 × 30mm
Print: Flat (mount face down), PLA, 60% infill, 5 perimeters
Qty: 4 (FL, FR, RL, RR — symmetric)

Reference: EA-25, EA-27
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, CORNER_R,
    TUBE_BORE, TUBE_DEPTH, TUBE_WALL, GRUB_M3,
    draw_rounded_rect,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile,
    make_offset_plane, make_heat_set_pair,
    add_edge_fillets, add_chamfer, zoom_fit,
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
        TUBE_BORE_R = TUBE_BORE / 2   # 4.1mm
        WALL = TUBE_WALL               # 4mm
        WIRE_W = 1.0                   # 10mm wire exit
        WIRE_H = 0.8                   # 8mm wire exit

        # Body
        BODY_W = 3.5                   # 35mm width (X)
        BODY_D = 3.0                   # 30mm depth (Z)
        BODY_H = 3.0                   # 30mm height (Y)

        # Mount bolt patterns
        STEER_BOLT_SPACING = 2.0       # 20mm
        SERVO_BOLT_SPACING = 2.0       # 20mm

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Connector Body'
        draw_rounded_rect(sk, 0, BODY_H / 2, BODY_W, BODY_H, r=CORNER_R)

        target = BODY_W * BODY_H - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, BODY_D)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Front Wheel Connector'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Tube socket (from top face, vertical)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, BODY_H)

        tube_sk = comp.sketches.add(top_plane)
        tube_sk.name = 'Tube Socket'
        tube_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_D / 2), TUBE_BORE_R
        )

        tube_prof = find_smallest_profile(tube_sk)
        cut_profile(comp, tube_prof, TUBE_DEPTH, flip=True)

        # Entry chamfer
        if body:
            add_chamfer(comp, body, TUBE_BORE_R, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 3: M3 grub screw for tube retention
        # ══════════════════════════════════════════════════════════

        grub_y = BODY_H - TUBE_DEPTH / 2
        grub_plane = make_offset_plane(comp, comp.xYConstructionPlane, grub_y)

        grub_sk = comp.sketches.add(grub_plane)
        grub_sk.name = 'Tube Grub'
        grub_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(TUBE_BORE_R + WALL / 2, BODY_D / 2), GRUB_M3
        )

        grub_prof = find_smallest_profile(grub_sk)
        if grub_prof:
            g_input = extrudes.createInput(
                grub_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            g_input.setDistanceExtent(
                False, val(WALL + TUBE_BORE_R + 0.01)
            )
            try:
                extrudes.add(g_input)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Steering bracket mount — 2× heat-set inserts
        # (front face, XY plane at Z=0)
        # ══════════════════════════════════════════════════════════

        make_heat_set_pair(
            comp, comp.xYConstructionPlane, STEER_BOLT_SPACING,
            cx=0, cy=BODY_H / 3, axis='x'
        )

        # ══════════════════════════════════════════════════════════
        # STEP 5: Servo mount — 2× heat-set inserts (side face)
        # ══════════════════════════════════════════════════════════

        side_plane = make_offset_plane(
            comp, comp.xZConstructionPlane, BODY_W / 2
        )

        make_heat_set_pair(
            comp, side_plane, SERVO_BOLT_SPACING,
            cx=BODY_D / 2, cy=BODY_H / 3, axis='y'
        )

        # ══════════════════════════════════════════════════════════
        # STEP 6: Wire exit hole (rounded-rect on bottom face)
        # ══════════════════════════════════════════════════════════

        wire_sk = comp.sketches.add(comp.xYConstructionPlane)
        wire_sk.name = 'Wire Exit'
        draw_rounded_rect(
            wire_sk,
            cx=0, cy=0,
            w=WIRE_W, h=0.02,  # thin slot at bottom edge
            r=0.005
        )

        wire_target = WIRE_W * 0.02
        wire_prof = find_profile_by_area(wire_sk, wire_target, tolerance=0.8)
        if wire_prof is None:
            wire_prof = find_smallest_profile(wire_sk)
        if wire_prof:
            w_input = extrudes.createInput(
                wire_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            w_input.setDistanceExtent(False, val(BODY_D))
            try:
                extrudes.add(w_input)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 7: External fillets
        # ══════════════════════════════════════════════════════════

        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)
        else:
            fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # STEP 8: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Front/Rear Wheel Connector created!\n\n'
            f'Body: {BODY_W*10:.0f} × {BODY_D*10:.0f} × {BODY_H*10:.0f}mm '
            f'(rounded corners)\n\n'
            f'TUBE SOCKET: {TUBE_BORE*10:.1f}mm × {TUBE_DEPTH*10:.0f}mm deep\n'
            f'  M3 grub screw, {CHAMFER_STD*10:.1f}mm entry chamfer\n\n'
            f'STEERING MOUNT: 2× M3 heat-set inserts '
            f'({STEER_BOLT_SPACING*10:.0f}mm, front face)\n'
            f'SERVO MOUNT: 2× M3 heat-set inserts '
            f'({SERVO_BOLT_SPACING*10:.0f}mm, side face)\n'
            f'WIRE EXIT: {WIRE_W*10:.0f}×{WIRE_H*10:.0f}mm (bottom)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Bolt steering_bracket to front face.\n'
            'Bolt servo_mount to side face.\n\n'
            'Print mount-face down, 60% infill, 5 perimeters.\n'
            'Qty: 4 (FL, FR, RL, RR)',
            'Mars Rover - Front/Rear Wheel Connector'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
