"""
Mars Rover Top Deck Tile — Phase 1 (0.4 Scale)
=================================================

Cosmetic cover that snaps onto the top of the body frame.
Split into 4 tiles matching body quadrant layout.

Each tile: ~220 × 130 × 3mm flat panel with cantilever snap clips
and stiffening ribs.

This script creates one tile. Modify TILE variable for each quadrant.

Features:
  - 3mm flat panel (increased from 2mm for rigidity)
  - Cantilever snap clips on seam edges
  - Stiffening ribs on underside (cross pattern)
  - Edge lips on outer edges (overlap body wall)
  - Camera mast mount (RL tile, 4× M3 heat-set, 25mm pattern)
  - Antenna dish detail (RR tile, cosmetic high-gain antenna)

Qty: 4 tiles (FL, FR, RL, RR)

Print orientation: Flat (2mm panel down)
Supports: None
Perimeters: 3
Infill: 20% grid (thin, cosmetic)

Reference: EA-08
"""

import adsk.core
import adsk.fusion
import traceback
import math


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
        BODY_L = 44.0       # 440mm total
        BODY_W = 26.0       # 260mm total
        PANEL_H = 0.3       # 3mm panel thickness (increased for rigidity)

        # Split positions (same as body quadrants)
        X_SPLIT = 0.0
        Y_SPLIT = 0.0       # centre — matches body quadrant split

        X_MIN = -BODY_W / 2
        X_MAX = BODY_W / 2
        Y_MIN = -BODY_L / 2
        Y_MAX = BODY_L / 2

        # Snap clip dimensions
        CLIP_W = 0.6        # 6mm wide
        CLIP_L = 1.0        # 10mm long
        CLIP_H = 0.5        # 5mm tall (hangs down from panel)
        CLIP_TAB = 0.1      # 1mm snap tab protrusion
        CLIP_OFFSET = 3.0   # 30mm inset from edge

        # Edge lip (overlaps body wall)
        LIP_W = 0.3         # 3mm overlap
        LIP_H = 0.3         # 3mm hang-down depth

        # Phone holder mount (FR tile only) — 4× M3 heat-set insert bosses
        # Rectangle pattern for a universal phone cradle bracket
        PHONE_MOUNT_W = 6.0   # 60mm wide (phone width axis)
        PHONE_MOUNT_L = 8.0   # 80mm long (phone length axis)
        PHONE_BOSS_OD_R = 0.4 # 8mm OD boss / 2 = 4mm radius
        PHONE_HSERT_R = 0.24  # 4.8mm / 2 = 2.4mm radius (M3 heat-set)
        PHONE_HSERT_DEPTH = 0.55  # 5.5mm

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # Determine tile bounds
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

        # ══════════════════════════════════════════════════════════════
        # Step 1: Flat panel
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = f'Top Deck {TILE}'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(tx_min, ty_min, 0),
            p(tx_max, ty_max, 0)
        )

        prof = sketch1.profiles.item(0)
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(PANEL_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = f'Top Deck {TILE}'

        # ══════════════════════════════════════════════════════════════
        # Step 2: Edge lips (hang down from outer edges only)
        # Lips are extruded downward from the bottom of the panel.
        # The panel sits at Z=0 (bottom) to Z=PANEL_H (top).
        # Lips extrude from Z=0 downward (negative Z) as separate
        # sketches on a plane offset below the panel bottom.
        # ══════════════════════════════════════════════════════════════

        outer_edges = []
        if TILE in ('FL', 'RL'):
            outer_edges.append(('left', tx_min, tx_min + LIP_W, ty_min, ty_max))
        if TILE in ('FR', 'RR'):
            outer_edges.append(('right', tx_max - LIP_W, tx_max, ty_min, ty_max))
        if TILE in ('FL', 'FR'):
            outer_edges.append(('front', tx_min, tx_max, ty_max - LIP_W, ty_max))
        if TILE in ('RL', 'RR'):
            outer_edges.append(('rear', tx_min, tx_max, ty_min, ty_min + LIP_W))

        # Create offset plane at bottom of panel (Z=0) for downward extrusions
        # We sketch on topP (at Z=PANEL_H) and extrude upward through panel+lip
        # OR sketch on XY (Z=0) and use symmetric/two-side extent.
        # Simplest: sketch on XY, extrude with negative direction (True = flip).
        for edge_name, ex_min, ex_max, ey_min, ey_max in outer_edges:
            lipSketch = comp.sketches.add(comp.xYConstructionPlane)
            lipSketch.name = f'Lip {edge_name}'
            lipSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                p(ex_min, ey_min, 0),
                p(ex_max, ey_max, 0)
            )

            lProf = None
            minArea = float('inf')
            for pi in range(lipSketch.profiles.count):
                pr = lipSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    lProf = pr

            if lProf:
                lipInput = extrudes.createInput(
                    lProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                # Extrude downward (flip direction) by LIP_H
                lipInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(LIP_H)
                )
                try:
                    extrudes.add(lipInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 3: Snap clips (small tabs hanging down from panel)
        # 2 clips per seam edge, extruded downward from panel bottom
        # ══════════════════════════════════════════════════════════════

        clip_positions = []
        if TILE in ('FL', 'RL'):
            for cy in [ty_min + CLIP_OFFSET, ty_max - CLIP_OFFSET]:
                clip_positions.append((tx_max - CLIP_W, tx_max, cy - CLIP_L / 2, cy + CLIP_L / 2))
        if TILE in ('FR', 'RR'):
            for cy in [ty_min + CLIP_OFFSET, ty_max - CLIP_OFFSET]:
                clip_positions.append((tx_min, tx_min + CLIP_W, cy - CLIP_L / 2, cy + CLIP_L / 2))
        if TILE in ('FL', 'FR'):
            for cx in [tx_min + CLIP_OFFSET, tx_max - CLIP_OFFSET]:
                clip_positions.append((cx - CLIP_W / 2, cx + CLIP_W / 2, ty_min, ty_min + CLIP_L))
        if TILE in ('RL', 'RR'):
            for cx in [tx_min + CLIP_OFFSET, tx_max - CLIP_OFFSET]:
                clip_positions.append((cx - CLIP_W / 2, cx + CLIP_W / 2, ty_max - CLIP_L, ty_max))

        for cx_min, cx_max, cy_min, cy_max in clip_positions:
            clipSketch = comp.sketches.add(comp.xYConstructionPlane)
            clipSketch.name = 'Snap Clip'
            clipSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                p(cx_min, cy_min, 0),
                p(cx_max, cy_max, 0)
            )

            cProf = None
            minArea = float('inf')
            for pi in range(clipSketch.profiles.count):
                pr = clipSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    cProf = pr

            if cProf:
                clipInput = extrudes.createInput(
                    cProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                # Extrude downward from panel bottom
                clipInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(CLIP_H)
                )
                try:
                    extrudes.add(clipInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 4: Stiffening ribs on underside (cross pattern)
        # 2mm wide × 4mm deep ribs to prevent flex
        # Extruded downward from panel bottom
        # ══════════════════════════════════════════════════════════════

        RIB_T = 0.2        # 2mm rib thickness
        RIB_DEPTH = 0.4    # 4mm rib hang-down depth

        ribSketch = comp.sketches.add(comp.xYConstructionPlane)
        ribSketch.name = f'Stiffener Ribs {TILE}'
        rl = ribSketch.sketchCurves.sketchLines

        # Cross rib along X midline
        mid_y = (ty_min + ty_max) / 2
        rl.addTwoPointRectangle(
            p(tx_min + 0.5, mid_y - RIB_T / 2, 0),
            p(tx_max - 0.5, mid_y + RIB_T / 2, 0)
        )

        # Cross rib along Y midline
        mid_x = (tx_min + tx_max) / 2
        rl.addTwoPointRectangle(
            p(mid_x - RIB_T / 2, ty_min + 0.5, 0),
            p(mid_x + RIB_T / 2, ty_max - 0.5, 0)
        )

        for pi in range(ribSketch.profiles.count):
            pr = ribSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 2.0:  # thin rib profiles
                ribInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                # Extrude downward from panel bottom
                ribInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(RIB_DEPTH)
                )
                try:
                    extrudes.add(ribInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 5: Phone holder mount bosses (FR tile only)
        # 4× cylindrical bosses on top surface with M3 heat-set insert
        # holes. Provides mounting points for a phone cradle bracket
        # that acts as a dashboard display during testing.
        # ══════════════════════════════════════════════════════════════

        phone_mount_count = 0
        if TILE == 'FR':
            # Centre the mount pattern on the tile
            pmx = (tx_min + tx_max) / 2
            pmy = (ty_min + ty_max) / 2

            phone_mounts = [
                (pmx - PHONE_MOUNT_W / 2, pmy - PHONE_MOUNT_L / 2),
                (pmx + PHONE_MOUNT_W / 2, pmy - PHONE_MOUNT_L / 2),
                (pmx - PHONE_MOUNT_W / 2, pmy + PHONE_MOUNT_L / 2),
                (pmx + PHONE_MOUNT_W / 2, pmy + PHONE_MOUNT_L / 2),
            ]

            # Create offset plane at top of panel (Z=PANEL_H)
            phonePlaneInput = comp.constructionPlanes.createInput()
            phonePlaneInput.setByOffset(
                comp.xYConstructionPlane,
                adsk.core.ValueInput.createByReal(PANEL_H)
            )
            phoneTopPlane = comp.constructionPlanes.add(phonePlaneInput)

            # Boss cylinders (join upward from panel top)
            BOSS_HEIGHT = 0.3  # 3mm tall bosses above panel
            bossSketch = comp.sketches.add(phoneTopPlane)
            bossSketch.name = 'Phone Mount Bosses'
            for bx, by in phone_mounts:
                bossSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(bx, by, 0), PHONE_BOSS_OD_R
                )

            for pi in range(bossSketch.profiles.count):
                pr = bossSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 1.0:  # boss circle profiles
                    bossInput = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    bossInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(BOSS_HEIGHT)
                    )
                    try:
                        extrudes.add(bossInput)
                    except:
                        pass

            # Heat-set insert holes (cut down into bosses + panel)
            hsertPlaneInput = comp.constructionPlanes.createInput()
            hsertPlaneInput.setByOffset(
                comp.xYConstructionPlane,
                adsk.core.ValueInput.createByReal(PANEL_H + BOSS_HEIGHT)
            )
            hsertPlane = comp.constructionPlanes.add(hsertPlaneInput)

            hsertSketch = comp.sketches.add(hsertPlane)
            hsertSketch.name = 'Phone Mount Inserts'
            for bx, by in phone_mounts:
                hsertSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(bx, by, 0), PHONE_HSERT_R
                )

            for pi in range(hsertSketch.profiles.count):
                pr = hsertSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 0.5:
                    hsertCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    hsertCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(PHONE_HSERT_DEPTH)
                    )
                    try:
                        extrudes.add(hsertCut)
                    except:
                        pass

            phone_mount_count = len(phone_mounts)

        # ══════════════════════════════════════════════════════════════
        # Step 6: Panel line grid on top surface (cosmetic)
        # Shallow grooves (0.5mm deep × 1mm wide) every 30mm
        # Creates "solar panel" texture — very Mars rover
        # ══════════════════════════════════════════════════════════════

        GRID_SPACING = 3.0    # 30mm between grid lines
        GRID_W = 0.1          # 1mm wide groove
        GRID_D = 0.05         # 0.5mm deep

        # Create offset plane at top of panel
        gridPlaneInput = comp.constructionPlanes.createInput()
        gridPlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(PANEL_H)
        )
        gridTopPlane = comp.constructionPlanes.add(gridPlaneInput)

        gridSketch = comp.sketches.add(gridTopPlane)
        gridSketch.name = f'Panel Lines {TILE}'
        grl = gridSketch.sketchCurves.sketchLines

        # X-direction lines (running along X, spaced along Y)
        gy = ty_min + GRID_SPACING
        while gy < ty_max - 0.1:
            grl.addTwoPointRectangle(
                p(tx_min + 0.3, gy - GRID_W / 2, 0),
                p(tx_max - 0.3, gy + GRID_W / 2, 0)
            )
            gy += GRID_SPACING

        # Y-direction lines (running along Y, spaced along X)
        gx = tx_min + GRID_SPACING
        while gx < tx_max - 0.1:
            grl.addTwoPointRectangle(
                p(gx - GRID_W / 2, ty_min + 0.3, 0),
                p(gx + GRID_W / 2, ty_max - 0.3, 0)
            )
            gx += GRID_SPACING

        # Cut all grid line profiles
        for pi in range(gridSketch.profiles.count):
            pr = gridSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 3.0:  # thin groove profiles only
                gridCut = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                gridCut.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(GRID_D)
                )
                try:
                    extrudes.add(gridCut)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 6a: Camera mast mount (RL tile only)
        # 4× M3 heat-set insert bosses in a 25mm square pattern.
        # Camera mast mount point for Phase 2.
        # ══════════════════════════════════════════════════════════════

        CAM_MOUNT_PATTERN = 2.5     # 25mm square pattern (2.5cm)
        CAM_BOSS_OD_R = 0.4        # 8mm OD / 2 = 4mm radius
        CAM_BOSS_H = 0.3           # 3mm tall boss above panel
        CAM_HSERT_R = 0.24         # 4.8mm / 2 = 2.4mm (M3 heat-set)
        CAM_HSERT_DEPTH = 0.55     # 5.5mm deep

        cam_mount_count = 0
        if TILE == 'RL':
            # Centre on tile, offset slightly toward rear (lower Y)
            cam_cx = (tx_min + tx_max) / 2
            cam_cy = (ty_min + ty_max) / 2 - 1.0  # 10mm toward rear

            cam_mounts = [
                (cam_cx - CAM_MOUNT_PATTERN / 2, cam_cy - CAM_MOUNT_PATTERN / 2),
                (cam_cx + CAM_MOUNT_PATTERN / 2, cam_cy - CAM_MOUNT_PATTERN / 2),
                (cam_cx - CAM_MOUNT_PATTERN / 2, cam_cy + CAM_MOUNT_PATTERN / 2),
                (cam_cx + CAM_MOUNT_PATTERN / 2, cam_cy + CAM_MOUNT_PATTERN / 2),
            ]

            # Offset plane at top of panel (Z = PANEL_H)
            camPlaneInput = comp.constructionPlanes.createInput()
            camPlaneInput.setByOffset(
                comp.xYConstructionPlane,
                adsk.core.ValueInput.createByReal(PANEL_H)
            )
            camTopPlane = comp.constructionPlanes.add(camPlaneInput)

            # Boss cylinders (join upward from panel top)
            camBossSketch = comp.sketches.add(camTopPlane)
            camBossSketch.name = 'Camera Mast Bosses RL'
            for bx, by in cam_mounts:
                camBossSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(bx, by, 0), CAM_BOSS_OD_R
                )

            for pi in range(camBossSketch.profiles.count):
                pr = camBossSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 1.0:  # boss circle profiles
                    camBossInput = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    camBossInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(CAM_BOSS_H)
                    )
                    try:
                        extrudes.add(camBossInput)
                    except:
                        pass

            # Heat-set insert holes (cut down into bosses + panel)
            camHsertPlaneInput = comp.constructionPlanes.createInput()
            camHsertPlaneInput.setByOffset(
                comp.xYConstructionPlane,
                adsk.core.ValueInput.createByReal(PANEL_H + CAM_BOSS_H)
            )
            camHsertPlane = comp.constructionPlanes.add(camHsertPlaneInput)

            camHsertSketch = comp.sketches.add(camHsertPlane)
            camHsertSketch.name = 'Camera Mast Inserts RL'
            for bx, by in cam_mounts:
                camHsertSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(bx, by, 0), CAM_HSERT_R
                )

            for pi in range(camHsertSketch.profiles.count):
                pr = camHsertSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 0.5:
                    camHsertCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    camHsertCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(CAM_HSERT_DEPTH)
                    )
                    try:
                        extrudes.add(camHsertCut)
                    except:
                        pass

            cam_mount_count = len(cam_mounts)

        # ══════════════════════════════════════════════════════════════
        # Step 6b: Antenna dish detail (RR tile only, cosmetic)
        # 15mm diameter × 3mm tall circular boss with a 12mm × 1mm
        # deep circular recess on top (dish shape).
        # Cosmetic high-gain antenna detail.
        # ══════════════════════════════════════════════════════════════

        ANTENNA_BOSS_R = 0.75      # 15mm diameter / 2 = 7.5mm radius
        ANTENNA_BOSS_H = 0.3       # 3mm tall
        ANTENNA_DISH_R = 0.6       # 12mm diameter / 2 = 6mm radius
        ANTENNA_DISH_D = 0.1       # 1mm deep recess

        has_antenna = False
        if TILE == 'RR':
            has_antenna = True
            # Centre on tile, offset slightly toward rear
            ant_cx = (tx_min + tx_max) / 2
            ant_cy = (ty_min + ty_max) / 2 - 0.5  # 5mm toward rear

            # Offset plane at top of panel (Z = PANEL_H)
            antPlaneInput = comp.constructionPlanes.createInput()
            antPlaneInput.setByOffset(
                comp.xYConstructionPlane,
                adsk.core.ValueInput.createByReal(PANEL_H)
            )
            antTopPlane = comp.constructionPlanes.add(antPlaneInput)

            # Boss cylinder (join upward from panel top)
            antBossSketch = comp.sketches.add(antTopPlane)
            antBossSketch.name = 'Antenna Boss RR'
            antBossSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(ant_cx, ant_cy, 0), ANTENNA_BOSS_R
            )

            antBossProf = None
            minArea = float('inf')
            for pi in range(antBossSketch.profiles.count):
                pr = antBossSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    antBossProf = pr

            if antBossProf:
                antBossInput = extrudes.createInput(
                    antBossProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                antBossInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(ANTENNA_BOSS_H)
                )
                try:
                    extrudes.add(antBossInput)
                except:
                    pass

            # Dish recess (cut from top of boss)
            antDishPlaneInput = comp.constructionPlanes.createInput()
            antDishPlaneInput.setByOffset(
                comp.xYConstructionPlane,
                adsk.core.ValueInput.createByReal(PANEL_H + ANTENNA_BOSS_H)
            )
            antDishPlane = comp.constructionPlanes.add(antDishPlaneInput)

            antDishSketch = comp.sketches.add(antDishPlane)
            antDishSketch.name = 'Antenna Dish Recess RR'
            antDishSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(ant_cx, ant_cy, 0), ANTENNA_DISH_R
            )

            antDishProf = None
            minArea = float('inf')
            for pi in range(antDishSketch.profiles.count):
                pr = antDishSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    antDishProf = pr

            if antDishProf:
                antDishCut = extrudes.createInput(
                    antDishProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                antDishCut.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(ANTENNA_DISH_D)
                )
                try:
                    extrudes.add(antDishCut)
                except:
                    pass

        # ── Zoom and report ──
        app.activeViewport.fit()

        phone_msg = ''
        if phone_mount_count > 0:
            phone_msg = f'Phone mount bosses: {phone_mount_count} (M3 heat-set inserts)\n'

        cam_msg = ''
        if cam_mount_count > 0:
            cam_msg = f'Camera mast bosses: {cam_mount_count} (M3 heat-set, 25mm pattern)\n'

        antenna_msg = ''
        if has_antenna:
            antenna_msg = f'Antenna dish: 15mm boss + 12mm recess (cosmetic)\n'

        ui.messageBox(
            f'Top Deck Tile {TILE} created!\n\n'
            f'Size: {tile_w * 10:.0f} × {tile_l * 10:.0f} × '
            f'{PANEL_H * 10:.0f}mm\n'
            f'Snap clips: {len(clip_positions)}\n'
            f'Edge lips: {len(outer_edges)}\n'
            f'Stiffening ribs: cross pattern (2mm wide x 4mm deep, underside)\n'
            f'Panel line grid: 30mm spacing (0.5mm deep, solar panel look)\n'
            f'{phone_msg}'
            f'{cam_msg}'
            f'{antenna_msg}\n'
            'Change TILE variable for other quadrants.\n\n'
            'Qty needed: 4 tiles total\n'
            'Print flat (ribs up), brim recommended, 20% infill.',
            f'Mars Rover - Top Deck {TILE}'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
