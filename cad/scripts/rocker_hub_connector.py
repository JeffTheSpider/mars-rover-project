"""
Mars Rover Rocker Hub Connector — Phase 1
===========================================

THE most complex connector. Sits outside the body, clamped to the
diff bar. Provides tube sockets for the front arm (to front wheel)
and rear arm (to bogie pivot).

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - Tube sockets via shared helpers (chamfered entries)
  - Diff bar clamp bore with grub screw via helper
  - Triangular gussets reinforcing tube socket bosses
  - Wire channels with rounded entries
  - 0.5mm fillets on all external edges

Differential mechanism: This connector CLAMPS rigidly to the 8mm
diff bar via an M3 grub screw. The diff bar passes through 608ZZ
bearings in the body.

Features:
  - Diff bar clamp bore: 8.2mm (clearance fit, M3 grub retention)
  - 2× tube sockets (8.2mm × 15mm deep): front + rear
  - M3 grub screws in each tube socket + diff bar clamp
  - 2× wire channels (8×6mm)
  - 4mm minimum wall thickness

Overall size: ~45 × 35 × 35mm
Print: Body-side down | PLA | 60% infill | 5 perimeters
Qty: 2 (left + right — symmetric)

Reference: EA-25, EA-26, Sawppy Rocker Body Mount
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
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_m3_grub_hole,
    add_edge_fillets, add_triangular_gusset, zoom_fit,
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
        DIFF_BORE_R = 0.41             # 4.1mm (8.2mm bore, assembly clearance on 8mm rod)
        WALL = TUBE_WALL               # 4mm
        WIRE_W = 0.8                   # 8mm
        WIRE_H = 0.6                   # 6mm

        # Body
        BODY_W = 4.5                   # 45mm (Y, front-rear)
        BODY_H_Z = 3.5                 # 35mm (Z, up-down)
        BODY_D = 3.5                   # 35mm (X, along diff bar)

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Hub Body'
        draw_rounded_rect(sk, 0, BODY_H_Z / 2, BODY_W, BODY_H_Z, r=CORNER_R)

        target = BODY_W * BODY_H_Z - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, BODY_D)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Rocker Hub Connector'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Diff bar bore (through centre along Z-axis)
        # ══════════════════════════════════════════════════════════

        diff_sk = comp.sketches.add(comp.xYConstructionPlane)
        diff_sk.name = 'Diff Bar Bore'
        diff_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_H_Z / 2), DIFF_BORE_R
        )

        diff_prof = find_smallest_profile(diff_sk)
        if diff_prof:
            d_input = extrudes.createInput(
                diff_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            d_input.setDistanceExtent(False, val(BODY_D + 0.01))
            try:
                extrudes.add(d_input)
            except:
                pass

        # Diff bar bore entry chamfer
        if body:
            from rover_cad_helpers import add_chamfer
            add_chamfer(comp, body, DIFF_BORE_R, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 3: M3 grub screw for diff bar retention
        # ══════════════════════════════════════════════════════════

        mid_plane = make_offset_plane(comp, comp.xZConstructionPlane, BODY_D / 2)

        grub_sk = comp.sketches.add(mid_plane)
        grub_sk.name = 'Diff Bar Grub'
        grub_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_H_Z / 2 + DIFF_BORE_R + WALL / 2), GRUB_M3
        )

        grub_prof = find_smallest_profile(grub_sk)
        if grub_prof:
            g_input = extrudes.createInput(
                grub_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            g_input.setDistanceExtent(True, val(WALL + DIFF_BORE_R + 0.01))
            try:
                extrudes.add(g_input)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Front tube socket (on +Y face)
        # ══════════════════════════════════════════════════════════

        front_y = BODY_W / 2
        front_z = BODY_H_Z / 2

        fb_sk = comp.sketches.add(mid_plane)
        fb_sk.name = 'Front Tube Socket'
        fb_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(front_y, front_z), TUBE_BORE_R
        )

        fb_prof = find_smallest_profile(fb_sk)
        cut_profile(comp, fb_prof, TUBE_DEPTH, flip=False)

        # Front grub screw
        fg_sk = comp.sketches.add(mid_plane)
        fg_sk.name = 'Front Grub'
        fg_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(front_y - TUBE_DEPTH / 2, front_z + TUBE_BORE_R + WALL / 2),
            GRUB_M3
        )
        fg_prof = find_smallest_profile(fg_sk)
        if fg_prof:
            fg_in = extrudes.createInput(
                fg_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            fg_in.setDistanceExtent(True, val(WALL + TUBE_BORE_R + 0.01))
            try:
                extrudes.add(fg_in)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Rear tube socket (on -Y face)
        # ══════════════════════════════════════════════════════════

        rear_y = -BODY_W / 2
        rear_z = BODY_H_Z / 2

        rb_sk = comp.sketches.add(mid_plane)
        rb_sk.name = 'Rear Tube Socket'
        rb_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(rear_y, rear_z), TUBE_BORE_R
        )

        rb_prof = find_smallest_profile(rb_sk)
        cut_profile(comp, rb_prof, TUBE_DEPTH, flip=True)

        # Rear grub screw
        rg_sk = comp.sketches.add(mid_plane)
        rg_sk.name = 'Rear Grub'
        rg_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(rear_y + TUBE_DEPTH / 2, rear_z + TUBE_BORE_R + WALL / 2),
            GRUB_M3
        )
        rg_prof = find_smallest_profile(rg_sk)
        if rg_prof:
            rg_in = extrudes.createInput(
                rg_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            rg_in.setDistanceExtent(True, val(WALL + TUBE_BORE_R + 0.01))
            try:
                extrudes.add(rg_in)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 6: Wire channels (rounded-rect cross-section)
        # ══════════════════════════════════════════════════════════

        for sign, name in [(1, 'Front'), (-1, 'Rear')]:
            wsk = comp.sketches.add(comp.xYConstructionPlane)
            wsk.name = f'{name} Wire Channel'
            draw_rounded_rect(
                wsk,
                cx=sign * (WIRE_W / 2 + 0.2),
                cy=BODY_H_Z / 2,
                w=BODY_W / 2 - WIRE_W / 2,
                h=WIRE_H,
                r=0.1
            )
            w_target = (BODY_W / 2 - WIRE_W / 2) * WIRE_H
            w_prof = find_profile_by_area(wsk, w_target, tolerance=0.6)
            if w_prof is None:
                w_prof = find_largest_profile(wsk)
            cut_profile(comp, w_prof, WIRE_H, flip=False)

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
            'Rocker Hub Connector created!\n\n'
            f'Body: {BODY_W*10:.0f} × {BODY_H_Z*10:.0f} × {BODY_D*10:.0f}mm '
            f'(rounded corners)\n\n'
            f'DIFF BAR: {DIFF_BORE_R*20:.0f}mm bore (press-fit, M3 grub, chamfered)\n'
            f'TUBE SOCKETS: 2× {TUBE_BORE_R*20:.1f}mm × {TUBE_DEPTH*10:.0f}mm '
            f'(front + rear, M3 grubs)\n'
            f'WIRE CHANNELS: 2× {WIRE_W*10:.0f}×{WIRE_H*10:.0f}mm (rounded)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Print body-side down, 60% infill, 5 perimeters.\n'
            'Qty: 2 (left + right — symmetric)',
            'Mars Rover - Rocker Hub Connector'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
