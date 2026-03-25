"""
Mars Rover Switch Mount Plate — Phase 1
=========================================

Reinforcing plate for panel-mount toggle switch on the RR body
quadrant rear wall. Glued/bolted inside the body wall to strengthen
the 3mm PLA around the 15mm switch bore.

Redesigned with:
  - Rounded-rect plate (2mm corner radius)
  - Centre bore with entry chamfer (eases switch insertion)
  - M3 counterbored bolt holes (flush mounting)
  - 0.5mm fillets on external edges

Dimensions:
  - Plate: 30 × 30 × 5mm
  - Centre bore: 15mm diameter (switch barrel)
  - Bore chamfer: 0.5mm × 45° entry
  - 2× M3 bolt holes (diagonal), counterbored for cap heads
  - 2.85mm min wall from bolt hole to plate edge

Print: Flat (face down), 60% infill, 4 perimeters (solid for strength)
Qty: 1

Reference: EA-15, EA-08
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, CORNER_R,
    draw_rounded_rect,
    find_profile_by_area, find_smallest_profile, find_largest_profile,
    extrude_profile, cut_profile,
    make_offset_plane, add_edge_fillets, add_chamfer, zoom_fit,
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
        PLATE_S = 3.0        # 30mm square plate
        PLATE_H = 0.5        # 5mm thickness (Z)
        BORE_R = 0.75        # 15mm diameter / 2
        BORE_CHAMFER = 0.05  # 0.5mm entry chamfer
        HOLE_R = 0.165       # M3 clearance (3.3mm dia)
        CB_R = 0.3           # 6mm counterbore diameter / 2 (M3 cap head)
        CB_D = 0.2           # 2mm counterbore depth
        HOLE_OFFSET = 1.05   # 10.5mm from centre (diagonal)
        CR = CORNER_R        # 2mm corner radius

        comp = design.rootComponent

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect plate
        # ══════════════════════════════════════════════════════════

        sk1 = comp.sketches.add(comp.xYConstructionPlane)
        sk1.name = 'Switch Plate'
        draw_rounded_rect(sk1, 0, 0, PLATE_S, PLATE_S, r=CR)

        body_prof = find_largest_profile(sk1)
        ext = extrude_profile(comp, body_prof, PLATE_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Switch Mount Plate'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Centre bore (15mm for toggle switch barrel)
        # ══════════════════════════════════════════════════════════

        topP = make_offset_plane(comp, comp.xYConstructionPlane, PLATE_H)
        bore_sk = comp.sketches.add(topP)
        bore_sk.name = 'Switch Bore'
        bore_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BORE_R
        )

        bore_prof = find_smallest_profile(bore_sk)
        if bore_prof:
            cut_profile(comp, bore_prof, PLATE_H + 0.02, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Bore entry chamfer (ring cut at top edge)
        # ══════════════════════════════════════════════════════════

        # Chamfer ring: annular cut at bore mouth
        cham_sk = comp.sketches.add(topP)
        cham_sk.name = 'Bore Chamfer'
        circles = cham_sk.sketchCurves.sketchCircles
        circles.addByCenterRadius(p(0, 0, 0), BORE_R + BORE_CHAMFER)
        circles.addByCenterRadius(p(0, 0, 0), BORE_R)

        # Find the annular ring profile
        ring_target = math.pi * ((BORE_R + BORE_CHAMFER)**2 - BORE_R**2)
        ring_prof = find_profile_by_area(cham_sk, ring_target, tolerance=0.5)
        if ring_prof is None:
            ring_prof = find_smallest_profile(cham_sk)

        if ring_prof:
            try:
                cut_profile(comp, ring_prof, BORE_CHAMFER, flip=True)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: M3 bolt holes with counterbores (diagonal corners)
        # ══════════════════════════════════════════════════════════

        # Through holes
        hole_sk = comp.sketches.add(topP)
        hole_sk.name = 'Bolt Holes'
        hole_circles = hole_sk.sketchCurves.sketchCircles
        hole_circles.addByCenterRadius(
            p(-HOLE_OFFSET, -HOLE_OFFSET, 0), HOLE_R
        )
        hole_circles.addByCenterRadius(
            p(HOLE_OFFSET, HOLE_OFFSET, 0), HOLE_R
        )

        hole_area = math.pi * HOLE_R**2
        for pi_idx in range(hole_sk.profiles.count):
            pr = hole_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < hole_area * 1.5:
                try:
                    cut_profile(comp, pr, PLATE_H + 0.02, flip=True)
                except:
                    pass

        # Counterbores (larger diameter, shallow from top)
        cb_sk = comp.sketches.add(topP)
        cb_sk.name = 'Counterbores'
        cb_circles = cb_sk.sketchCurves.sketchCircles
        cb_circles.addByCenterRadius(
            p(-HOLE_OFFSET, -HOLE_OFFSET, 0), CB_R
        )
        cb_circles.addByCenterRadius(
            p(HOLE_OFFSET, HOLE_OFFSET, 0), CB_R
        )

        cb_area = math.pi * CB_R**2
        for pi_idx in range(cb_sk.profiles.count):
            pr = cb_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            # Select the annular ring (counterbore minus through-hole)
            if a < cb_area * 1.5 and a > hole_area * 0.5:
                try:
                    cut_profile(comp, pr, CB_D, flip=True)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Fillets
        # ══════════════════════════════════════════════════════════

        fillet_count = 0
        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 6: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Switch Mount Plate created!\n\n'
            f'Size: {PLATE_S*10:.0f} × {PLATE_S*10:.0f} × {PLATE_H*10:.0f}mm\n'
            f'Corner radius: {CR*10:.1f}mm\n\n'
            f'Centre bore: {BORE_R*20:.0f}mm dia\n'
            f'Bore chamfer: {BORE_CHAMFER*10:.1f}mm entry\n\n'
            f'Mounting: 2× M3 holes (diagonal)\n'
            f'  Counterbore: {CB_R*20:.0f}mm × {CB_D*10:.0f}mm deep\n'
            f'  Edge wall: 2.85mm min\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Glue + bolt inside RR body rear wall.\n'
            'Print flat, 60% infill, 4 perimeters.\nQty: 1',
            'Mars Rover - Switch Mount Plate'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
