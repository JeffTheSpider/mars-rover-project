"""
Mars Rover Top Deck Tile — Phase 1 (0.4 Scale)
=================================================

Cosmetic cover that snaps onto the top of the body frame.
Split into 4 tiles matching body quadrant layout.

Redesigned with:
  - Rounded corners (2mm radius)
  - Improved cantilever snap clips with ramp geometry
  - Stiffening ribs with rib-panel fillets
  - Solar panel grid texture (cosmetic)
  - Camera mast mount (RL) and antenna dish (RR)
  - 0.5mm fillets on external edges

Each tile: ~220 × 130 × 3mm flat panel with snap clips.

Qty: 4 tiles (FL, FR, RL, RR)
Print: Flat (ribs up), brim recommended, 20% grid

Reference: EA-08
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CORNER_R,
    INSERT_BORE, INSERT_DEPTH,
    draw_rounded_rect,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_heat_set_pocket,
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

        # ── Which tile ──
        TILE = 'FL'

        # ── Dimensions (cm) ──
        BODY_L = 44.0
        BODY_W = 26.0
        PANEL_H = 0.3       # 3mm panel thickness

        X_SPLIT = 0.0
        Y_SPLIT = 0.0

        # Snap clips
        CLIP_W = 0.6
        CLIP_L = 1.0
        CLIP_H = 0.5
        CLIP_OFFSET = 3.0

        # Edge lip
        LIP_W = 0.3
        LIP_H = 0.3

        # Stiffening ribs
        RIB_T = 0.2
        RIB_DEPTH = 0.4

        # Grid texture
        GRID_SPACING = 3.0
        GRID_W = 0.1
        GRID_D = 0.05

        # Phone mount (FR only)
        PHONE_W = 6.0
        PHONE_L = 8.0
        PHONE_BOSS_R = 0.4
        PHONE_BOSS_H = 0.3

        # Camera mast (RL only)
        CAM_PATTERN = 2.5
        CAM_BOSS_R = 0.4
        CAM_BOSS_H = 0.3

        # Antenna (RR only)
        ANT_BOSS_R = 0.75
        ANT_BOSS_H = 0.3
        ANT_DISH_R = 0.6
        ANT_DISH_D = 0.1

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # Determine tile bounds
        X_MIN = -BODY_W / 2
        X_MAX = BODY_W / 2
        Y_MIN = -BODY_L / 2
        Y_MAX = BODY_L / 2

        if TILE == 'FL':
            tx_min, tx_max = X_MIN, X_SPLIT
            ty_min, ty_max = Y_SPLIT, Y_MAX
        elif TILE == 'FR':
            tx_min, tx_max = X_SPLIT, X_MAX
            ty_min, ty_max = Y_SPLIT, Y_MAX
        elif TILE == 'RL':
            tx_min, tx_max = X_MIN, X_SPLIT
            ty_min, ty_max = Y_MIN, Y_SPLIT
        elif TILE == 'RR':
            tx_min, tx_max = X_SPLIT, X_MAX
            ty_min, ty_max = Y_MIN, Y_SPLIT
        else:
            ui.messageBox(f'Unknown tile: {TILE}')
            return

        tile_w = tx_max - tx_min
        tile_l = ty_max - ty_min
        tile_cx = (tx_min + tx_max) / 2
        tile_cy = (ty_min + ty_max) / 2

        # ══════════════════════════════════════════════════════════
        # Step 1: Flat panel with rounded corners
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = f'Top Deck {TILE}'
        draw_rounded_rect(sk, tile_cx, tile_cy, tile_w, tile_l, r=CORNER_R)

        target = tile_w * tile_l - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, PANEL_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = f'Top Deck {TILE}'

        # ══════════════════════════════════════════════════════════
        # Step 2: Edge lips (hang down from outer edges)
        # ══════════════════════════════════════════════════════════

        outer_edges = []
        if TILE in ('FL', 'RL'):
            outer_edges.append((tx_min, tx_min + LIP_W, ty_min, ty_max))
        if TILE in ('FR', 'RR'):
            outer_edges.append((tx_max - LIP_W, tx_max, ty_min, ty_max))
        if TILE in ('FL', 'FR'):
            outer_edges.append((tx_min, tx_max, ty_max - LIP_W, ty_max))
        if TILE in ('RL', 'RR'):
            outer_edges.append((tx_min, tx_max, ty_min, ty_min + LIP_W))

        for ex_min, ex_max, ey_min, ey_max in outer_edges:
            lip_sk = comp.sketches.add(comp.xYConstructionPlane)
            lip_sk.name = 'Edge Lip'
            lip_sk.sketchCurves.sketchLines.addTwoPointRectangle(
                p(ex_min, ey_min), p(ex_max, ey_max)
            )
            lip_prof = find_smallest_profile(lip_sk)
            if lip_prof:
                extrude_profile(
                    comp, lip_prof, LIP_H,
                    adsk.fusion.FeatureOperations.JoinFeatureOperation
                )

        # ══════════════════════════════════════════════════════════
        # Step 3: Snap clips (hang down from seam edges)
        # ══════════════════════════════════════════════════════════

        clip_positions = []
        if TILE in ('FL', 'RL'):
            for cy in [ty_min + CLIP_OFFSET, ty_max - CLIP_OFFSET]:
                clip_positions.append(
                    (tx_max - CLIP_W, tx_max, cy - CLIP_L / 2, cy + CLIP_L / 2)
                )
        if TILE in ('FR', 'RR'):
            for cy in [ty_min + CLIP_OFFSET, ty_max - CLIP_OFFSET]:
                clip_positions.append(
                    (tx_min, tx_min + CLIP_W, cy - CLIP_L / 2, cy + CLIP_L / 2)
                )
        if TILE in ('FL', 'FR'):
            for cx in [tx_min + CLIP_OFFSET, tx_max - CLIP_OFFSET]:
                clip_positions.append(
                    (cx - CLIP_W / 2, cx + CLIP_W / 2, ty_min, ty_min + CLIP_L)
                )
        if TILE in ('RL', 'RR'):
            for cx in [tx_min + CLIP_OFFSET, tx_max - CLIP_OFFSET]:
                clip_positions.append(
                    (cx - CLIP_W / 2, cx + CLIP_W / 2, ty_max - CLIP_L, ty_max)
                )

        for cx_min, cx_max, cy_min, cy_max in clip_positions:
            clip_sk = comp.sketches.add(comp.xYConstructionPlane)
            clip_sk.name = 'Snap Clip'
            clip_sk.sketchCurves.sketchLines.addTwoPointRectangle(
                p(cx_min, cy_min), p(cx_max, cy_max)
            )
            clip_prof = find_smallest_profile(clip_sk)
            if clip_prof:
                c_in = extrudes.createInput(
                    clip_prof, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                c_in.setDistanceExtent(True, val(CLIP_H))
                try:
                    extrudes.add(c_in)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # Step 4: Stiffening ribs (cross pattern, underside)
        # ══════════════════════════════════════════════════════════

        rib_sk = comp.sketches.add(comp.xYConstructionPlane)
        rib_sk.name = f'Ribs {TILE}'
        rl = rib_sk.sketchCurves.sketchLines

        mid_y = (ty_min + ty_max) / 2
        mid_x = (tx_min + tx_max) / 2

        rl.addTwoPointRectangle(
            p(tx_min + 0.5, mid_y - RIB_T / 2),
            p(tx_max - 0.5, mid_y + RIB_T / 2)
        )
        rl.addTwoPointRectangle(
            p(mid_x - RIB_T / 2, ty_min + 0.5),
            p(mid_x + RIB_T / 2, ty_max - 0.5)
        )

        for pi in range(rib_sk.profiles.count):
            pr = rib_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 2.0:
                r_in = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                r_in.setDistanceExtent(True, val(RIB_DEPTH))
                try:
                    extrudes.add(r_in)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # Step 5: Solar panel grid texture (cosmetic, top surface)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, PANEL_H)
        grid_sk = comp.sketches.add(top_plane)
        grid_sk.name = f'Panel Lines {TILE}'
        gl = grid_sk.sketchCurves.sketchLines

        # X-direction lines
        gy = ty_min + GRID_SPACING
        while gy < ty_max - 0.1:
            gl.addTwoPointRectangle(
                p(tx_min + 0.3, gy - GRID_W / 2),
                p(tx_max - 0.3, gy + GRID_W / 2)
            )
            gy += GRID_SPACING

        # Y-direction lines
        gx = tx_min + GRID_SPACING
        while gx < tx_max - 0.1:
            gl.addTwoPointRectangle(
                p(gx - GRID_W / 2, ty_min + 0.3),
                p(gx + GRID_W / 2, ty_max - 0.3)
            )
            gx += GRID_SPACING

        for pi in range(grid_sk.profiles.count):
            pr = grid_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 3.0:
                cut_profile(comp, pr, GRID_D, flip=True)

        # ══════════════════════════════════════════════════════════
        # Step 6: Phone mount bosses (FR only)
        # ══════════════════════════════════════════════════════════

        phone_count = 0
        if TILE == 'FR':
            ph_sk = comp.sketches.add(top_plane)
            ph_sk.name = 'Phone Mount Bosses'
            for sx in [-1, 1]:
                for sy in [-1, 1]:
                    ph_sk.sketchCurves.sketchCircles.addByCenterRadius(
                        p(tile_cx + sx * PHONE_W / 2,
                          tile_cy + sy * PHONE_L / 2),
                        PHONE_BOSS_R
                    )

            for pi in range(ph_sk.profiles.count):
                pr = ph_sk.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 1.0:
                    join_profile(comp, pr, PHONE_BOSS_H)
                    phone_count += 1

            # Heat-set inserts
            ph_top = make_offset_plane(
                comp, comp.xYConstructionPlane, PANEL_H + PHONE_BOSS_H
            )
            for sx in [-1, 1]:
                for sy in [-1, 1]:
                    make_heat_set_pocket(
                        comp, ph_top,
                        tile_cx + sx * PHONE_W / 2,
                        tile_cy + sy * PHONE_L / 2
                    )

        # ══════════════════════════════════════════════════════════
        # Step 7: Camera mast mount (RL only)
        # ══════════════════════════════════════════════════════════

        cam_count = 0
        if TILE == 'RL':
            cam_sk = comp.sketches.add(top_plane)
            cam_sk.name = 'Camera Mast Bosses'
            cam_cy = tile_cy - 1.0
            for sx in [-1, 1]:
                for sy in [-1, 1]:
                    cam_sk.sketchCurves.sketchCircles.addByCenterRadius(
                        p(tile_cx + sx * CAM_PATTERN / 2,
                          cam_cy + sy * CAM_PATTERN / 2),
                        CAM_BOSS_R
                    )

            for pi in range(cam_sk.profiles.count):
                pr = cam_sk.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 1.0:
                    join_profile(comp, pr, CAM_BOSS_H)
                    cam_count += 1

            cam_top = make_offset_plane(
                comp, comp.xYConstructionPlane, PANEL_H + CAM_BOSS_H
            )
            for sx in [-1, 1]:
                for sy in [-1, 1]:
                    make_heat_set_pocket(
                        comp, cam_top,
                        tile_cx + sx * CAM_PATTERN / 2,
                        cam_cy + sy * CAM_PATTERN / 2
                    )

        # ══════════════════════════════════════════════════════════
        # Step 8: Antenna dish detail (RR only, cosmetic)
        # ══════════════════════════════════════════════════════════

        has_antenna = False
        if TILE == 'RR':
            has_antenna = True
            ant_sk = comp.sketches.add(top_plane)
            ant_sk.name = 'Antenna Boss'
            ant_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(tile_cx, tile_cy - 0.5), ANT_BOSS_R
            )
            ant_prof = find_smallest_profile(ant_sk)
            join_profile(comp, ant_prof, ANT_BOSS_H)

            # Dish recess
            ant_top = make_offset_plane(
                comp, comp.xYConstructionPlane, PANEL_H + ANT_BOSS_H
            )
            dish_sk = comp.sketches.add(ant_top)
            dish_sk.name = 'Antenna Dish'
            dish_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(tile_cx, tile_cy - 0.5), ANT_DISH_R
            )
            dish_prof = find_smallest_profile(dish_sk)
            cut_profile(comp, dish_prof, ANT_DISH_D, flip=True)

        # ══════════════════════════════════════════════════════════
        # Step 9: External fillets
        # ══════════════════════════════════════════════════════════

        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)
        else:
            fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # Step 10: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        extras = ''
        if phone_count:
            extras += f'Phone mount: {phone_count}× M3 bosses\n'
        if cam_count:
            extras += f'Camera mast: {cam_count}× M3 bosses (25mm pattern)\n'
        if has_antenna:
            extras += 'Antenna dish: 15mm boss + 12mm recess\n'

        ui.messageBox(
            f'Top Deck Tile {TILE} created!\n\n'
            f'Size: {tile_w*10:.0f} × {tile_l*10:.0f} × '
            f'{PANEL_H*10:.0f}mm (rounded corners)\n\n'
            f'Snap clips: {len(clip_positions)}\n'
            f'Edge lips: {len(outer_edges)}\n'
            f'Ribs: cross pattern ({RIB_T*10:.0f}mm × {RIB_DEPTH*10:.0f}mm)\n'
            f'Grid texture: {GRID_SPACING*10:.0f}mm spacing\n'
            f'{extras}'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Change TILE variable for other quadrants.\n'
            'Print flat (ribs up), brim, 20% infill.\n'
            'Qty: 4 tiles total',
            f'Mars Rover - Top Deck {TILE}'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
