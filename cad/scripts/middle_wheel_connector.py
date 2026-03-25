"""
Mars Rover Middle Wheel Connector — Phase 1
=============================================

End connector at the middle wheel position. Receives one 8mm tube
from the bogie arm. Middle wheels are NOT steered — only a fixed
motor mount is needed.

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - Tube socket with chamfered entry
  - Heat-set insert pockets via shared helper
  - Rounded wire exit
  - 0.5mm fillets on all external edges
  - M3 grub screw for tube retention

Features:
  - 1× tube socket (8.2mm bore × 15mm deep) with M3 grub screw
  - Fixed wheel mount face: 2× M3 heat-set inserts
  - Wire exit hole: 8×6mm (motor wires only — no servo)
  - 4mm minimum wall thickness

Overall size: ~30 × 25 × 25mm (smallest connector)
Print: Flat (mount face down), PLA, 60% infill, 5 perimeters
Qty: 2 (ML, MR — symmetric)

Reference: EA-25
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
        WIRE_W = 0.8                   # 8mm
        WIRE_H = 0.6                   # 6mm

        # Body (smallest connector)
        BODY_W = 3.0                   # 30mm (X)
        BODY_D = 2.5                   # 25mm (Z)
        BODY_H = 2.5                   # 25mm (Y)

        MOUNT_BOLT_SPACING = 1.6       # 16mm (matches fixed_wheel_mount)

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
            body.name = 'Middle Wheel Connector'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Tube socket (from side face, horizontal entry)
        # ══════════════════════════════════════════════════════════

        # Tube socket on side face — rod enters horizontally from bogie arm.
        # Socket bore faces +Y direction (arm rod arrives from +Y side).
        # XZ plane normal is +Y. Offset to mid-height of the body.
        side_plane = make_offset_plane(comp, comp.xZConstructionPlane, BODY_H / 2)

        tube_sk = comp.sketches.add(side_plane)
        tube_sk.name = 'Tube Socket'
        tube_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(BODY_D / 2, 0), TUBE_BORE_R
        )

        tube_prof = find_smallest_profile(tube_sk)
        # flip=True on XZ-offset plane → extrude in -Y direction (into body)
        cut_profile(comp, tube_prof, TUBE_DEPTH, flip=True)

        # Entry chamfer
        if body:
            add_chamfer(comp, body, TUBE_BORE_R, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 3: M3 grub screw for tube retention
        # ══════════════════════════════════════════════════════════

        # Grub screw approaches from the top face, perpendicular to the
        # horizontal tube bore axis. Positioned at mid-depth of tube engagement.
        grub_plane_y = BODY_H / 2 - TUBE_DEPTH / 2
        grub_plane = make_offset_plane(comp, comp.xZConstructionPlane, grub_plane_y)

        grub_sk = comp.sketches.add(grub_plane)
        grub_sk.name = 'Tube Grub'
        grub_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(BODY_D / 2, TUBE_BORE_R + WALL / 2), GRUB_M3
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
            except Exception as e:
                print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: Fixed mount — 2× heat-set inserts (bottom face)
        # ══════════════════════════════════════════════════════════

        # NOTE: Heat-set insert faces (fixed wheel mount on bottom)
        # must be re-verified once tube socket is reoriented to horizontal entry.

        make_heat_set_pair(
            comp, comp.xYConstructionPlane, MOUNT_BOLT_SPACING,
            cx=0, cy=BODY_D / 2, axis='x'
        )

        # ══════════════════════════════════════════════════════════
        # STEP 5: Wire exit (rounded-rect on bottom edge)
        # ══════════════════════════════════════════════════════════

        wire_sk = comp.sketches.add(comp.xYConstructionPlane)
        wire_sk.name = 'Wire Exit'
        draw_rounded_rect(
            wire_sk,
            cx=0, cy=WIRE_H / 2,
            w=WIRE_W, h=WIRE_H,
            r=0.05
        )

        wire_target = WIRE_W * WIRE_H
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
            except Exception as e:
                print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 6: External fillets
        # ══════════════════════════════════════════════════════════

        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)
        else:
            fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # STEP 7: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Middle Wheel Connector created!\n\n'
            f'Body: {BODY_W*10:.0f} × {BODY_D*10:.0f} × {BODY_H*10:.0f}mm '
            f'(rounded corners)\n\n'
            f'TUBE SOCKET: {TUBE_BORE*10:.1f}mm × {TUBE_DEPTH*10:.0f}mm deep\n'
            f'  M3 grub screw, {CHAMFER_STD*10:.1f}mm entry chamfer\n\n'
            f'FIXED MOUNT: 2× M3 heat-set inserts '
            f'({MOUNT_BOLT_SPACING*10:.0f}mm, bottom face)\n'
            f'WIRE EXIT: {WIRE_W*10:.0f}×{WIRE_H*10:.0f}mm (rounded)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Bolt fixed_wheel_mount to bottom face.\n'
            'No steering — middle wheels are fixed.\n\n'
            'Print mount-face down, 60% infill, 5 perimeters.\n'
            'Qty: 2 (ML, MR)',
            'Mars Rover - Middle Wheel Connector'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
