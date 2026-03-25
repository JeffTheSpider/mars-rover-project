"""
Bearing Test Piece — 608ZZ Press-Fit Validation
================================================

Creates a print-ready test piece to validate 608ZZ bearing press-fit
dimensions on the CTC Bizer (PLA).

608ZZ bearing: 8mm ID x 22mm OD x 7mm width
Bore: 22.15mm (0.15mm oversize for PLA press-fit)
Seat depth: 7.2mm (bearing width + 0.2mm)

Redesigned with:
  - Rounded-rect body (2mm corner radius) instead of plain cylinder
  - 0.5mm fillets on all external edges
  - 0.3mm bearing entry chamfer
  - Chamfered shaft bore entry
  - Engraved label ring (bearing size identification)

After printing, test-fit a 608ZZ bearing:
- Too tight: increase bore by 0.05mm increments
- Too loose: decrease bore by 0.05mm increments
- Target: firm press fit by hand, no hammer needed

Usage: Run as Script in Fusion 360 (UTILITIES > Scripts and Add-Ins)

Reference: EA-08 Section 10.3 (Bearing Press-Fit Dimensions)
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, BEARING_OD, BEARING_DEPTH, BEARING_BORE,
    FILLET_STD, CHAMFER_STD,
    find_smallest_profile, find_largest_profile,
    cut_profile, add_edge_fillets, add_chamfer,
    make_bearing_seat, make_offset_plane, zoom_fit,
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
        OUTER_W = 3.2          # 32mm wide (enough for 22.15mm bore + 5mm wall each side)
        OUTER_D = 3.2          # 32mm deep
        HEIGHT = 1.2           # 12mm tall (7.2mm seat + 4.8mm base)
        CORNER_R = 0.3         # 3mm corner radius (generous for grip)
        BEVEL_H = 0.15         # 1.5mm bottom bevel

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body with bevelled base
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Test Piece Body'

        # Draw rounded rectangle
        lines = sk.sketchCurves.sketchLines
        arcs = sk.sketchCurves.sketchArcs
        hw = OUTER_W / 2
        hd = OUTER_D / 2
        r = CORNER_R

        # Straight edges
        lines.addByTwoPoints(p(-hw + r, hd), p(hw - r, hd))         # top
        lines.addByTwoPoints(p(hw, hd - r), p(hw, -hd + r))         # right
        lines.addByTwoPoints(p(hw - r, -hd), p(-hw + r, -hd))       # bottom
        lines.addByTwoPoints(p(-hw, -hd + r), p(-hw, hd - r))       # left

        # Corner arcs
        half_pi = math.pi / 2
        arcs.addByCenterStartSweep(p(-hw + r, hd - r), p(-hw, hd - r), -half_pi)
        arcs.addByCenterStartSweep(p(hw - r, hd - r), p(hw - r, hd), -half_pi)
        arcs.addByCenterStartSweep(p(hw - r, -hd + r), p(hw, -hd + r), -half_pi)
        arcs.addByCenterStartSweep(p(-hw + r, -hd + r), p(-hw + r, -hd), -half_pi)

        prof = find_largest_profile(sk)
        ext = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext.setDistanceExtent(False, val(HEIGHT))

        # Add draft taper for easy bed release (2°)
        try:
            ext.taperAngle = val(math.radians(2))
        except:
            pass

        body_ext = extrudes.add(ext)
        body = body_ext.bodies.item(0)
        body.name = 'Bearing Test Piece'

        # ══════════════════════════════════════════════════════════
        # STEP 2: 608ZZ bearing seat (from top face)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, HEIGHT)

        seat_result = make_bearing_seat(
            comp, top_plane,
            cx=0, cy=0,
            bore_through=HEIGHT + 0.01,  # shaft bore goes all the way through
            chamfer=True,
        )

        # ══════════════════════════════════════════════════════════
        # STEP 3: Bottom shaft bore chamfer (guide for rod insertion)
        # ══════════════════════════════════════════════════════════

        # Add chamfer to the bottom of the shaft bore
        if body:
            add_chamfer(comp, body, BEARING_BORE / 2, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Identification ring (shallow groove on top face)
        # Helps identify which test piece this is if you print multiples
        # ══════════════════════════════════════════════════════════

        ring_sk = comp.sketches.add(top_plane)
        ring_sk.name = 'ID Ring'
        # Shallow groove at bearing OD + 1mm
        ring_r_outer = BEARING_OD / 2 + 0.15  # ~12.2mm
        ring_r_inner = BEARING_OD / 2 + 0.1   # ~11.7mm
        ring_sk.sketchCurves.sketchCircles.addByCenterRadius(p(0, 0), ring_r_outer)
        ring_sk.sketchCurves.sketchCircles.addByCenterRadius(p(0, 0), ring_r_inner)

        # Find the ring profile (annular area between two circles)
        ring_area = math.pi * (ring_r_outer**2 - ring_r_inner**2)
        from rover_cad_helpers import find_profile_by_area
        ring_prof = find_profile_by_area(ring_sk, ring_area, tolerance=0.6)
        if ring_prof:
            cut_profile(comp, ring_prof, 0.03, flip=True)  # 0.3mm deep groove

        # ══════════════════════════════════════════════════════════
        # STEP 5: Fillets on external edges
        # ══════════════════════════════════════════════════════════

        fillet_count = add_edge_fillets(comp, body, FILLET_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 6: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        bearing_dia = BEARING_OD * 10
        seat_depth = BEARING_DEPTH * 10
        shaft_dia = BEARING_BORE * 10

        ui.messageBox(
            'Bearing Test Piece created!\n\n'
            f'Body: {OUTER_W*10:.0f} × {OUTER_D*10:.0f} × {HEIGHT*10:.0f}mm '
            f'(rounded corners, {CORNER_R*10:.0f}mm radius)\n\n'
            f'BEARING SEAT (top):\n'
            f'  Bore: {bearing_dia:.2f}mm (608ZZ + 0.15mm)\n'
            f'  Depth: {seat_depth:.1f}mm\n'
            f'  Entry chamfer: {CHAMFER_STD*10:.1f}mm\n\n'
            f'SHAFT BORE:\n'
            f'  Diameter: {shaft_dia:.1f}mm through\n'
            f'  Bottom chamfer: {CHAMFER_STD*10:.1f}mm\n\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n'
            f'ID ring: shallow groove on top face\n\n'
            'TEST PROCEDURE:\n'
            '1. Print flat, PLA, 60% infill, 4 perimeters\n'
            '2. Insert 608ZZ bearing from top\n'
            '3. Too tight → increase bore +0.05mm\n'
            '4. Too loose → decrease bore -0.05mm\n'
            '5. Target: firm press fit by hand\n\n'
            'Qty: 1 (print more at different bore sizes if needed)',
            'Mars Rover - Bearing Test'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
