"""
Mars Rover Differential Pivot Housing — Phase 1
=================================================

Central pivot mount for the differential bar. Bolts onto the body top
cross-member. Contains a 608ZZ bearing so the diff bar can rotate freely
about the X-axis (longitudinal).

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - 608ZZ bearing seat via shared helper (chamfered entry)
  - 4× M3 heat-set insert mounting holes via helper
  - Rotation hard stops at ±25°
  - 0.5mm fillets on all external edges

Features:
  - 608ZZ bearing seat: 22.15mm OD × 7.2mm depth
  - Through bore: 8.1mm (diff bar rod passes through)
  - 4× M3 heat-set insert holes on 32mm PCD
  - Hard stop slots at ±25°
  - Flat bottom for bolting to cross-member

Overall size: ~30 × 30 × 20mm
Print: Flat (bottom face down), PLA, 60% infill, 4 perimeters
Qty: 1

Reference: EA-26 Section 9
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, CORNER_R,
    BEARING_OD, BEARING_DEPTH, BEARING_BORE,
    INSERT_BORE, INSERT_DEPTH,
    draw_rounded_rect,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_bearing_seat, make_heat_set_pocket,
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
        BODY_W = 3.0               # 30mm (X)
        BODY_L = 3.0               # 30mm (Y)
        BODY_H = 2.0               # 20mm (Z)
        WALL = 0.4                 # 4mm minimum wall

        # Mounting
        BOLT_PCD = 3.2             # 32mm bolt circle diameter
        BOLT_R_PCD = BOLT_PCD / 2

        # Hard stop
        STOP_W = 0.3               # 3mm stop feature width
        STOP_D = 0.2               # 2mm stop depth
        STOP_RADIUS = 0.8          # 8mm from centre

        comp = design.rootComponent

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Housing Body'
        draw_rounded_rect(sk, 0, 0, BODY_W, BODY_L, r=CORNER_R)

        target = BODY_W * BODY_L - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, BODY_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Diff Pivot Housing'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Bearing seat (from top face) via helper
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, BODY_H)

        make_bearing_seat(
            comp, top_plane,
            cx=0, cy=0,
            bore_through=BODY_H + 0.01,
            chamfer=True,
        )

        # ══════════════════════════════════════════════════════════
        # STEP 3: 4× M3 heat-set insert mounting holes
        # At 45° intervals on bolt PCD
        # ══════════════════════════════════════════════════════════

        # NOTE: Minimum wall between bearing seat OD and insert pocket is 2.5mm.
        # This is above the 2.4mm minimum but leaves no margin. Use 4+ perimeters
        # and 60%+ infill. Insert heat-set inserts BEFORE bearing to avoid thermal
        # distortion near the bearing seat.

        for angle_deg in [45, 135, 225, 315]:
            angle = math.radians(angle_deg)
            cx = BOLT_R_PCD * math.cos(angle)
            cy = BOLT_R_PCD * math.sin(angle)
            make_heat_set_pocket(comp, comp.xYConstructionPlane, cx, cy)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Hard stop slots at ±25° (rotation limiters)
        # ══════════════════════════════════════════════════════════

        # Hard stop walls limit diff bar rotation to ±25 degrees.
        # REQUIRES: A radial tab on rocker_hub_connector.py that sweeps between
        # these walls. Currently the rocker hub has no such tab — add one as a
        # small arm protruding radially from the hub body, positioned to engage
        # these stop walls at the ±25 degree limits.
        # TODO: Add matching hard stop tab to rocker_hub_connector.py

        stop_sk = comp.sketches.add(top_plane)
        stop_sk.name = 'Hard Stop Slots'

        for sign in [-1, 1]:
            angle_rad = sign * math.radians(25)
            cx = STOP_RADIUS * math.sin(angle_rad)
            cy = STOP_RADIUS * math.cos(angle_rad)

            # Rotated rectangle for stop wall
            hw = STOP_W / 2
            ht = STOP_D / 2
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            corners = [
                (cx + hw * (-cos_a) + ht * sin_a,
                 cy + hw * sin_a + ht * cos_a),
                (cx + hw * (-cos_a) - ht * sin_a,
                 cy + hw * sin_a - ht * cos_a),
                (cx - hw * (-cos_a) - ht * sin_a,
                 cy - hw * sin_a - ht * cos_a),
                (cx - hw * (-cos_a) + ht * sin_a,
                 cy - hw * sin_a + ht * cos_a),
            ]

            sl = stop_sk.sketchCurves.sketchLines
            for i in range(4):
                x1, y1 = corners[i]
                x2, y2 = corners[(i + 1) % 4]
                sl.addByTwoPoints(p(x1, y1), p(x2, y2))

        # Extrude stop walls upward
        stop_target = STOP_W * STOP_D
        for pi_idx in range(stop_sk.profiles.count):
            pr = stop_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if abs(a - stop_target) < stop_target * 0.5:
                join_profile(comp, pr, 0.3)  # 3mm tall stop walls

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

        wall = (BODY_W / 2 - BEARING_OD / 2) * 10
        zoom_fit(app)

        ui.messageBox(
            'Differential Pivot Housing created!\n\n'
            f'Body: {BODY_W*10:.0f} × {BODY_L*10:.0f} × '
            f'{BODY_H*10:.0f}mm (rounded corners)\n'
            f'Bearing wall: {wall:.1f}mm\n\n'
            f'BEARING SEAT:\n'
            f'  608ZZ: {BEARING_OD*10:.2f}mm × {BEARING_DEPTH*10:.1f}mm deep\n'
            f'  Through bore: {BEARING_BORE*10:.1f}mm\n'
            f'  Entry chamfer: {CHAMFER_STD*10:.1f}mm\n\n'
            f'MOUNTING: 4× M3 heat-set inserts on {BOLT_PCD*10:.0f}mm PCD\n'
            f'HARD STOPS: 2× walls at ±25° rotation limit\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Mounts on body top cross-member.\n'
            'Diff bar passes through 608ZZ bearing.\n\n'
            'Print bottom-face down, 60% infill, 4 perimeters.\n'
            'Qty: 1',
            'Mars Rover - Diff Pivot Housing'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
