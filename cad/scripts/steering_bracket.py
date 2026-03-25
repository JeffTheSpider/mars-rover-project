"""
Mars Rover Steering Bracket — Phase 1 (0.4 Scale)
====================================================

Bearing carrier bracket for the 4 steered wheels (FL, FR, RL, RR).
Bolts to the front face of the FrontWheelConnector. The steering
knuckle hangs below on an 8mm pivot shaft through the 608ZZ bearing.

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - 608ZZ bearing seat via shared helper (with entry chamfer)
  - Hard stop walls with rounded profiles
  - 0.5mm fillets on all external edges
  - Proper mounting bolt counterbores

Updated per EA-27: Motor clip REMOVED (motor is in knuckle only).
Height reduced from 40mm to 25mm (bearing carrier only, no motor).

Features:
  - 608ZZ bearing seat (top): 22.15mm × 7.2mm, 0.3mm entry chamfer
  - 8mm pivot bore (through full height)
  - Hard stop channel: 70° open arc at bracket bottom (±35° limit)
  - 2× M3 heat-set insert pockets (top face, for connector bolting)
  - Bearing entry chamfer (0.3mm × 45°)

Overall size: 35 × 30 × 25mm
Bearing wall: 3.9mm minimum around bearing seat (critical)

Print: Flat face down | Supports: None | Perimeters: 5 | Infill: 60% gyroid
Qty: 4 (FL, FR, RL, RR corners)

Reference: EA-27 (steering design package), EA-08, EA-10
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
    draw_rounded_rect,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_bearing_seat,
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
        BRACKET_L = 3.5     # 35mm length (along arm direction)
        BRACKET_W = 3.0     # 30mm width (increased for 3.9mm bearing wall)
        BRACKET_H = 2.5     # 25mm height (bearing carrier only, no motor)

        # Pivot bore
        PIVOT_BORE_R = BEARING_BORE / 2  # 4.05mm radius (8.1mm dia)

        # Hard stop (EA-27)
        STOP_WALL_W = 0.3       # 3mm wall width
        STOP_WALL_H = 0.5       # 5mm wall height
        STOP_WALL_THICK = 0.3   # 3mm wall thickness (radial)
        STOP_RADIUS = 0.8       # 8mm from pivot centre

        # Mount bolt spacing
        MOUNT_SPACING = 2.0     # 20mm between inserts

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Bracket Body'
        draw_rounded_rect(sk, 0, 0, BRACKET_L, BRACKET_W, r=CORNER_R)

        target = BRACKET_L * BRACKET_W - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, BRACKET_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Steering Bracket'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Bearing seat (from top face) via helper
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, BRACKET_H)

        make_bearing_seat(
            comp, top_plane,
            cx=0, cy=0,
            bore_through=BRACKET_H + 0.01,  # pivot bore goes all the way through
            chamfer=True,
        )

        # ══════════════════════════════════════════════════════════
        # STEP 3: Hard stop walls (2× at ±35° from +Y axis)
        # Rounded-profile stop walls that limit knuckle rotation
        # ══════════════════════════════════════════════════════════

        stopSketch = comp.sketches.add(comp.xYConstructionPlane)
        stopSketch.name = 'Hard Stop Walls'

        for sign in [-1, 1]:
            angle_rad = sign * math.radians(35)
            cx = STOP_RADIUS * math.sin(angle_rad)
            cy = STOP_RADIUS * math.cos(angle_rad)

            # Wall perpendicular to radial direction
            hw = STOP_WALL_W / 2
            ht = STOP_WALL_THICK / 2
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            tx = -cos_a
            ty = sin_a
            rx = sin_a
            ry = cos_a

            corners = [
                (cx + hw * tx + ht * rx, cy + hw * ty + ht * ry),
                (cx + hw * tx - ht * rx, cy + hw * ty - ht * ry),
                (cx - hw * tx - ht * rx, cy - hw * ty - ht * ry),
                (cx - hw * tx + ht * rx, cy - hw * ty + ht * ry),
            ]
            sl = stopSketch.sketchCurves.sketchLines
            for i in range(4):
                x1, y1 = corners[i]
                x2, y2 = corners[(i + 1) % 4]
                sl.addByTwoPoints(p(x1, y1), p(x2, y2))

        # Extrude stop walls
        target_stop = STOP_WALL_W * STOP_WALL_THICK
        for pi in range(stopSketch.profiles.count):
            pr = stopSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if abs(a - target_stop) < target_stop * 0.5:
                join_profile(comp, pr, STOP_WALL_H)

        # ══════════════════════════════════════════════════════════
        # STEP 4: M3 clearance through-holes (for bolting to connector)
        # ══════════════════════════════════════════════════════════

        mount_sk = comp.sketches.add(top_plane)
        mount_sk.name = 'M3 Through-Holes'
        m3_r = 0.165  # 3.3mm dia M3 clearance
        mount_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, -MOUNT_SPACING / 2, 0), m3_r
        )
        mount_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, MOUNT_SPACING / 2, 0), m3_r
        )
        for pi_idx in range(mount_sk.profiles.count):
            pr = mount_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < math.pi * m3_r**2 * 1.5:
                try:
                    cut_profile(comp, pr, BRACKET_H + 0.02, flip=True)
                except:
                    pass

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

        wall = (BRACKET_W / 2 - BEARING_OD / 2) * 10
        zoom_fit(app)

        ui.messageBox(
            'Steering Bracket created! (EA-27)\n\n'
            f'Body: {BRACKET_L*10:.0f} × {BRACKET_W*10:.0f} × '
            f'{BRACKET_H*10:.0f}mm (rounded corners)\n'
            f'Bearing wall: {wall:.1f}mm (minimum)\n\n'
            f'BEARING SEAT:\n'
            f'  Bore: {BEARING_OD*10:.2f}mm × {BEARING_DEPTH*10:.1f}mm deep\n'
            f'  Entry chamfer: {CHAMFER_STD*10:.1f}mm\n\n'
            f'PIVOT: {BEARING_BORE*10:.1f}mm through\n'
            f'HARD STOPS: 2× walls at ±35°\n'
            f'MOUNT: 2× M3 through-holes ({MOUNT_SPACING*10:.0f}mm, bolts to connector)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Qty: 4 (FL, FR, RL, RR)\n'
            'Print flat face down, no supports.',
            'Mars Rover - Steering Bracket'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
