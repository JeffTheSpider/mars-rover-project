"""
Mars Rover Bogie Pivot Connector — Phase 1
============================================

Central pivot hub for the bogie arm. Connects to the rocker (via one
tube from above) and splits to two wheels (front/rear tubes going down).

Redesigned with:
  - Revolve body (cylinder with bearing boss)
  - 608ZZ bearing seat via shared helper
  - Tube socket bosses with chamfered entries
  - Wire channel with rounded entries
  - 0.5mm fillets on all external edges
  - M3 grub screws in each tube socket

Features:
  - 608ZZ bearing seat (bogie rotation on rocker shaft)
  - 3× tube sockets (8.2mm bore × 15mm deep):
    * UP: from rocker rear arm (60mm tube)
    * FRONT-DOWN: to middle wheel (60mm tube)
    * REAR-DOWN: to rear wheel (60mm tube)
  - M3 grub screws in each tube socket
  - Wire channel: 8×6mm Y-split
  - 4mm minimum wall thickness

Overall size: ~45 × 35 × 30mm
Print: Flat (bearing face down), PLA, 60% infill, 5 perimeters
Qty: 2 (left + right — symmetric)

Reference: EA-25, EA-26, Sawppy Bogie-Body
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD,
    BEARING_OD, BEARING_DEPTH, BEARING_BORE,
    TUBE_BORE, TUBE_DEPTH, TUBE_WALL, GRUB_M3,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_bearing_seat,
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
        TUBE_BORE_R = TUBE_BORE / 2    # 4.1mm
        WALL = TUBE_WALL               # 4mm
        WIRE_W = 0.8                   # 8mm
        WIRE_H = 0.6                   # 6mm

        # Body
        BODY_R = BEARING_OD / 2 + WALL  # ~15mm radius
        BODY_H = 3.0                    # 30mm height

        # Socket boss
        SOCKET_OUTER_R = TUBE_BORE_R + WALL   # ~8.1mm outer

        comp = design.rootComponent
        revolves = comp.features.revolveFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Revolve body — cylinder with through bore
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Connector Body'
        sl = sketch.sketchCurves.sketchLines

        bore_r = BEARING_BORE / 2  # 4.05mm

        # Cross-section (rectangle for revolve, excluding bore)
        pts = [
            (bore_r, 0),
            (BODY_R, 0),
            (BODY_R, BODY_H),
            (bore_r, BODY_H),
        ]
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            sl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        axis = sl.addByTwoPoints(p(0, 0, 0), p(0, BODY_H, 0))
        axis.isConstruction = True

        prof = find_largest_profile(sketch)
        body = None
        if prof:
            rev_input = revolves.createInput(
                prof, axis,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            rev_input.setAngleExtent(False, val(2 * math.pi))
            rev = revolves.add(rev_input)
            body = rev.bodies.item(0)
            body.name = 'Bogie Pivot Connector'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Bearing seat (from bottom face) via helper
        # ══════════════════════════════════════════════════════════

        # TODO: Verify bearing seat cut direction in Fusion 360. If pocket is missing,
        # change sketch plane to offset at BODY_H and use flip=True to cut inward.
        # XZ plane normal is +Y. Body extends Y=0 to Y=BODY_H. Bearing seat should
        # cut into the bottom face (Y=0) in the +Y direction (flip=False on XZ plane).

        make_bearing_seat(
            comp, comp.xZConstructionPlane,
            cx=0, cy=0,
            bore_through=BODY_H + 0.01,
            chamfer=True,
        )

        # ══════════════════════════════════════════════════════════
        # STEP 3: UP tube socket boss (from top, vertical)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xZConstructionPlane, BODY_H)

        # Boss cylinder
        boss_sk = comp.sketches.add(top_plane)
        boss_sk.name = 'Rocker Socket Boss'
        boss_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0), SOCKET_OUTER_R
        )
        boss_prof = find_smallest_profile(boss_sk)
        join_profile(comp, boss_prof, TUBE_DEPTH)

        # Bore
        bore_sk = comp.sketches.add(top_plane)
        bore_sk.name = 'Rocker Socket Bore'
        bore_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0), TUBE_BORE_R
        )
        bore_prof = find_smallest_profile(bore_sk)
        cut_profile(comp, bore_prof, TUBE_DEPTH + BODY_H / 2, flip=False)

        # Bore entry chamfer
        if body:
            add_chamfer(comp, body, TUBE_BORE_R, CHAMFER_STD)

        # M3 grub screw for top socket
        grub_z = BODY_H + TUBE_DEPTH / 2
        grub_plane = make_offset_plane(comp, comp.xZConstructionPlane, grub_z)
        grub_sk = comp.sketches.add(grub_plane)
        grub_sk.name = 'Rocker Grub'
        grub_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(TUBE_BORE_R + WALL / 2, 0), GRUB_M3
        )
        grub_prof = find_smallest_profile(grub_sk)
        if grub_prof:
            cut_profile(comp, grub_prof, WALL + TUBE_BORE_R + 0.01, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Front-down tube socket boss (to middle wheel)
        # ══════════════════════════════════════════════════════════

        socket_y = BODY_H / 2  # Mid-height
        spread_half = math.radians(70)  # 140° spread / 2

        # TODO: Verify socket angles in assembled rover context. 70-degree spread
        # from vertical = 20 degrees below horizontal. May need adjustment based
        # on actual arm geometry and wheel positions.

        # Front boss: project outward from body at mid-height
        front_cx = math.sin(spread_half) * BODY_R
        front_cz = math.cos(spread_half) * BODY_R

        mid_plane = make_offset_plane(comp, comp.xZConstructionPlane, socket_y)

        fb_sk = comp.sketches.add(mid_plane)
        fb_sk.name = 'Front Socket Boss'
        fb_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(front_cx, front_cz), SOCKET_OUTER_R
        )
        fb_prof = find_smallest_profile(fb_sk)
        if fb_prof:
            extrude_profile(
                comp, fb_prof, TUBE_DEPTH * 2 + BODY_R,
                adsk.fusion.FeatureOperations.JoinFeatureOperation,
                symmetric=True
            )

        # Front bore — TUBE_DEPTH engagement from each entry face
        fb_bore_sk = comp.sketches.add(mid_plane)
        fb_bore_sk.name = 'Front Socket Bore'
        fb_bore_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(front_cx, front_cz), TUBE_BORE_R
        )
        fb_bore_prof = find_smallest_profile(fb_bore_sk)
        if fb_bore_prof:
            extrude_profile(
                comp, fb_bore_prof, TUBE_DEPTH * 2 + BODY_R + 0.01,
                adsk.fusion.FeatureOperations.CutFeatureOperation,
                symmetric=True
            )

        # ══════════════════════════════════════════════════════════
        # STEP 5: Rear-down tube socket boss (to rear wheel)
        # ══════════════════════════════════════════════════════════

        rear_cx = -math.sin(spread_half) * BODY_R
        rear_cz = math.cos(spread_half) * BODY_R

        rb_sk = comp.sketches.add(mid_plane)
        rb_sk.name = 'Rear Socket Boss'
        rb_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(rear_cx, rear_cz), SOCKET_OUTER_R
        )
        rb_prof = find_smallest_profile(rb_sk)
        if rb_prof:
            extrude_profile(
                comp, rb_prof, TUBE_DEPTH * 2 + BODY_R,
                adsk.fusion.FeatureOperations.JoinFeatureOperation,
                symmetric=True
            )

        # Rear bore — TUBE_DEPTH engagement from each entry face
        rb_bore_sk = comp.sketches.add(mid_plane)
        rb_bore_sk.name = 'Rear Socket Bore'
        rb_bore_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(rear_cx, rear_cz), TUBE_BORE_R
        )
        rb_bore_prof = find_smallest_profile(rb_bore_sk)
        if rb_bore_prof:
            extrude_profile(
                comp, rb_bore_prof, TUBE_DEPTH * 2 + BODY_R + 0.01,
                adsk.fusion.FeatureOperations.CutFeatureOperation,
                symmetric=True
            )

        # ══════════════════════════════════════════════════════════
        # STEP 5b: M3 grub screws for front/rear sockets
        # ══════════════════════════════════════════════════════════

        # Grub screws approach radially (perpendicular to socket bore axis).
        # Socket bores radiate from the body centre on the mid_plane (XZ).
        # Grub holes are placed on the same mid_plane, offset perpendicular
        # to the bore axis (rotated 90 degrees around Y).

        for (scx, scz, sname) in [(front_cx, front_cz, 'Front'), (rear_cx, rear_cz, 'Rear')]:
            # Normalise direction from body centre to socket centre
            dist = math.sqrt(scx**2 + scz**2)
            if dist < 0.001:
                continue
            dx, dz = scx / dist, scz / dist
            # Grub position: along bore axis, TUBE_DEPTH/2 from body surface
            grub_cx = scx + dx * TUBE_DEPTH / 2
            grub_cz = scz + dz * TUBE_DEPTH / 2
            # Perpendicular direction (90 deg CCW in XZ plane)
            perp_x, perp_z = -dz, dx
            # Grub hole centre offset perpendicular for the approach
            grub_off_x = grub_cx + perp_x * (TUBE_BORE_R + WALL / 2)
            grub_off_z = grub_cz + perp_z * (TUBE_BORE_R + WALL / 2)

            lg_sk = comp.sketches.add(mid_plane)
            lg_sk.name = f'{sname} Socket Grub'
            lg_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(grub_off_x, grub_off_z), GRUB_M3
            )
            lg_prof = find_smallest_profile(lg_sk)
            if lg_prof:
                cut_profile(comp, lg_prof, WALL + TUBE_BORE_R + 0.01, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 6: Wire channel (vertical through body centre)
        # ══════════════════════════════════════════════════════════

        from rover_cad_helpers import draw_rounded_rect

        wire_sk = comp.sketches.add(comp.xYConstructionPlane)
        wire_sk.name = 'Wire Channel'
        # Wire channel is a modest slot, not a body-splitting cut.
        # Height = WIRE_H (6mm), centred at mid-body height.
        draw_rounded_rect(
            wire_sk,
            cx=0, cy=BODY_H / 2,
            w=WIRE_W, h=WIRE_H,
            r=0.1
        )

        wire_target = WIRE_W * WIRE_H
        wire_prof = find_profile_by_area(wire_sk, wire_target, tolerance=0.6)
        if wire_prof is None:
            wire_prof = find_largest_profile(wire_sk)
        if wire_prof:
            extrude_profile(
                comp, wire_prof, WIRE_H,
                adsk.fusion.FeatureOperations.CutFeatureOperation,
                symmetric=True
            )

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
            'Bogie Pivot Connector created!\n\n'
            f'Body: {BODY_R*20:.0f}mm OD × {BODY_H*10:.0f}mm tall '
            f'(revolve, cylindrical)\n\n'
            f'BEARING SEAT (608ZZ):\n'
            f'  Bore: {BEARING_OD*10:.2f}mm × {BEARING_DEPTH*10:.1f}mm deep\n'
            f'  Pivot bore: {BEARING_BORE*10:.1f}mm through\n'
            f'  Entry chamfer: {CHAMFER_STD*10:.1f}mm\n\n'
            f'TUBE SOCKETS: 3× (up, front-down, rear-down)\n'
            f'  Bore: {TUBE_BORE*10:.1f}mm × {TUBE_DEPTH*10:.0f}mm deep\n'
            f'  Wall: {WALL*10:.0f}mm minimum\n\n'
            f'WIRE CHANNEL: {WIRE_W*10:.0f}×{WIRE_H*10:.0f}mm (rounded)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Print bearing-face down, 60% infill, 5 perimeters.\n'
            'Qty: 2 (symmetric, left = right)',
            'Mars Rover - Bogie Pivot Connector'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
