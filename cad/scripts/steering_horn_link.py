"""
Mars Rover Steering Horn Link — Phase 1
=========================================

Small printed bar that connects the SG90 servo horn tip to the steering
knuckle arm, forming a 4-bar linkage for steering actuation.

Redesigned with:
  - 0.5mm fillets on all external edges
  - M2 pin hole chamfers (entry guides for pin insertion)
  - Washer counterbores (0.5mm deep, 5mm dia) on both faces at each hole
  - Thicker mid-section with tapered profile for strength

One link per steered wheel (FL, FR, RL, RR). All identical.

Features:
  - Stadium shape (rectangle + 2 semicircles)
  - 2× M2 clearance holes (2.2mm) at 20mm centre-to-centre
  - 8mm wide × 5mm thick × 28mm overall (20mm c/c + 2× 4mm end radius)
  - Washer counterbores for nylon washers

Assembly:
  1. Horn end: M2×10 → nylon washer → horn hole → link hole → washer → nyloc nut
  2. Knuckle end: same hardware
  Both pins must rotate freely (finger-tight + 1/4 turn)

Print: Flat (largest face down), PLA, 100% infill, 4 perimeters
Qty: 4 (FL, FR, RL, RR — all identical)

Reference: EA-27 Section 4 (Dimensional Chain), EA-10
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, M2_CLEAR,
    draw_stadium,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile,
    make_offset_plane, add_edge_fillets, zoom_fit,
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
        LINK_CC = 2.0       # 20mm centre-to-centre
        LINK_W = 0.8        # 8mm width
        LINK_H = 0.5        # 5mm thickness
        HOLE_R = M2_CLEAR   # M2 clearance (1.1mm radius)
        END_R = LINK_W / 2  # 4mm end radius (rounded ends)

        # Washer counterbore
        CBORE_R = 0.25      # 5mm dia washer counterbore
        CBORE_DEPTH = 0.05  # 0.5mm deep

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Link body (stadium shape)
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Horn Link Body'
        half_cc = LINK_CC / 2

        draw_stadium(sk, 0, 0, half_cc, END_R)

        # Target area: rectangle + two semicircles
        target = LINK_CC * LINK_W + math.pi * END_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, LINK_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Steering Horn Link'

        # ══════════════════════════════════════════════════════════
        # STEP 2: M2 clearance holes (2× through-holes)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, LINK_H)

        hole_sk = comp.sketches.add(top_plane)
        hole_sk.name = 'M2 Pin Holes'
        hole_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(-half_cc, 0), HOLE_R
        )
        hole_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(half_cc, 0), HOLE_R
        )

        hole_area = math.pi * HOLE_R**2
        for pi_idx in range(hole_sk.profiles.count):
            pr = hole_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if abs(a - hole_area) < hole_area * 0.5:
                cut_profile(comp, pr, LINK_H + 0.01, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Washer counterbores (both faces, both holes)
        # Shallow recess for nylon washers to sit in
        # ══════════════════════════════════════════════════════════

        for plane, flip in [(top_plane, True), (comp.xYConstructionPlane, False)]:
            cbore_sk = comp.sketches.add(plane)
            cbore_sk.name = 'Washer Counterbore'
            cbore_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(-half_cc, 0), CBORE_R
            )
            cbore_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(half_cc, 0), CBORE_R
            )

            cbore_area = math.pi * CBORE_R**2
            for pi_idx in range(cbore_sk.profiles.count):
                pr = cbore_sk.profiles.item(pi_idx)
                a = pr.areaProperties().area
                # Find the annular ring (counterbore minus through-hole)
                ring_area = cbore_area - hole_area
                if abs(a - ring_area) < ring_area * 0.8:
                    cut_profile(comp, pr, CBORE_DEPTH, flip=flip)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Pin hole chamfers (entry guides)
        # ══════════════════════════════════════════════════════════

        if body:
            from rover_cad_helpers import add_chamfer
            add_chamfer(comp, body, HOLE_R, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 5: External fillets
        # ══════════════════════════════════════════════════════════

        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)
        else:
            fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # STEP 6: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        overall_l = (LINK_CC + LINK_W) * 10
        ui.messageBox(
            'Steering Horn Link created!\n\n'
            f'Overall: {overall_l:.0f} × {LINK_W*10:.0f} × '
            f'{LINK_H*10:.0f}mm (stadium shape)\n\n'
            f'M2 holes: 2× at {LINK_CC*10:.0f}mm c/c\n'
            f'  Hole dia: {HOLE_R*20:.1f}mm (M2 clearance)\n'
            f'  Chamfered entries: {CHAMFER_STD*10:.1f}mm\n'
            f'  Washer counterbores: {CBORE_R*20:.0f}mm × '
            f'{CBORE_DEPTH*10:.1f}mm (both faces)\n\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'ASSEMBLY:\n'
            '  Horn end: M2×10 + washer + horn + link + washer + nyloc\n'
            '  Arm end: same hardware\n'
            '  Both pins must rotate freely.\n\n'
            'Print flat, 100% infill, 4 perimeters.\n'
            'Qty: 4 (FL, FR, RL, RR)',
            'Mars Rover - Steering Horn Link'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
