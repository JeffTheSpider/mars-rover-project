"""
Mars Rover Electronics Tray — Phase 1 (0.4 Scale)
====================================================

Flat tray that sits inside the body frame and holds all electronics:
  - ESP32-S3 DevKitC-1 (69×25mm, 4× M3 standoffs)
  - 2× L298N motor drivers (43×43mm, 4× M3 standoffs each)
  - LiPo battery cradle (70×35×18mm)
  - Wiring channels between components
  - Mini breadboard area (47×35mm)

Tray size: ~180 × 120 × 15mm (fits inside 440×260mm body)

Qty: 1

Print orientation: Flat (bottom down)
Supports: None (all features are pockets from top)
Perimeters: 3
Infill: 30% gyroid

Reference: EA-08, EA-09
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

        # ── Dimensions (cm) ──
        TRAY_L = 18.0       # 180mm (Y-axis, along body)
        TRAY_W = 12.0       # 120mm (X-axis, across body)
        TRAY_H = 1.5        # 15mm (Z-axis, total height)
        FLOOR_H = 0.3       # 3mm floor thickness
        WALL_H = 1.5        # 15mm (full height for walls)
        WALL_T = 0.2        # 2mm wall thickness

        # ESP32-S3 DevKitC-1 pocket
        ESP32_L = 7.1        # 71mm (69mm + 2mm clearance)
        ESP32_W = 2.7        # 27mm (25mm + 2mm clearance)
        ESP32_Y = 4.0        # offset toward front
        ESP32_X = 0.0        # centred

        # Standoff positions (M3, 4 corners of ESP32)
        ESP32_STAND_H = 0.5  # 5mm standoff height
        ESP32_STAND_R = 0.35 # 3.5mm radius standoff
        ESP32_HOLE_R = 0.165 # 3.3mm clearance for M3
        ESP32_MOUNT_DX = 3.0 # 30mm X spacing (est)
        ESP32_MOUNT_DY = 6.0 # 60mm Y spacing (est)

        # L298N driver pockets (×2)
        L298N_L = 4.5        # 45mm (43mm + 2mm)
        L298N_W = 4.5        # 45mm
        L298N_H = 2.9        # 29mm (27mm + 2mm clearance)
        L298N_1_X = -3.5     # left driver X
        L298N_2_X = 3.5      # right driver X
        L298N_Y = -3.0       # rear of tray

        # LiPo battery cradle
        LIPO_L = 7.2         # 72mm (70mm + 2mm)
        LIPO_W = 3.7         # 37mm (35mm + 2mm)
        LIPO_WALL = 0.3      # 3mm cradle walls
        LIPO_Y = -7.0        # rear of tray
        LIPO_X = 0.0         # centred

        # Breadboard pocket
        BB_L = 4.9           # 49mm (47mm + 2mm)
        BB_W = 3.7           # 37mm (35mm + 2mm)
        BB_Y = 7.0           # front of tray
        BB_X = 4.0           # offset right

        # Wire channels (grooves cut into floor)
        CHANNEL_W = 1.0      # 10mm wide
        CHANNEL_D = 0.3      # 3mm deep (through 3mm floor = exit slots)

        # Cable exit holes on tray walls
        EXIT_W = 1.0         # 10mm wide
        EXIT_H = 0.5         # 5mm tall

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════════════
        # Step 1: Tray base plate
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Tray Base'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-TRAY_W / 2, -TRAY_L / 2, 0),
            p(TRAY_W / 2, TRAY_L / 2, 0)
        )

        prof = sketch1.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(TRAY_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'Electronics Tray'

        # ══════════════════════════════════════════════════════════════
        # Step 2: Hollow out interior (leave floor + perimeter walls)
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(TRAY_H)
        )
        topP = topPlane.add(tpInput)

        hollowSketch = comp.sketches.add(topP)
        hollowSketch.name = 'Interior Hollow'
        hollowSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-TRAY_W / 2 + WALL_T, -TRAY_L / 2 + WALL_T, 0),
            p(TRAY_W / 2 - WALL_T, TRAY_L / 2 - WALL_T, 0)
        )

        hProf = None
        minArea = float('inf')
        for pi in range(hollowSketch.profiles.count):
            pr = hollowSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                hProf = pr

        if hProf:
            hollowInput = extrudes.createInput(
                hProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            hollowInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(TRAY_H - FLOOR_H)
            )
            extrudes.add(hollowInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: ESP32 standoffs (4× cylindrical bosses from floor)
        # ══════════════════════════════════════════════════════════════

        standoffSketch = comp.sketches.add(comp.xYConstructionPlane)
        standoffSketch.name = 'ESP32 Standoffs'

        esp32_positions = [
            (ESP32_X - ESP32_MOUNT_DX / 2, ESP32_Y - ESP32_MOUNT_DY / 2),
            (ESP32_X + ESP32_MOUNT_DX / 2, ESP32_Y - ESP32_MOUNT_DY / 2),
            (ESP32_X - ESP32_MOUNT_DX / 2, ESP32_Y + ESP32_MOUNT_DY / 2),
            (ESP32_X + ESP32_MOUNT_DX / 2, ESP32_Y + ESP32_MOUNT_DY / 2),
        ]

        for sx, sy in esp32_positions:
            standoffSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(sx, sy, 0), ESP32_STAND_R
            )

        # Extrude all standoffs (join to tray)
        for pi in range(standoffSketch.profiles.count):
            pr = standoffSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.5:  # small circles only
                soInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                soInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(
                        FLOOR_H + ESP32_STAND_H)
                )
                try:
                    extrudes.add(soInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 4: L298N standoffs (4× each, 2 drivers)
        # ══════════════════════════════════════════════════════════════

        l298nSketch = comp.sketches.add(comp.xYConstructionPlane)
        l298nSketch.name = 'L298N Standoffs'

        L298N_MOUNT_OFFSET = 1.85  # 18.5mm from centre (37mm PCD)

        for driver_x in [L298N_1_X, L298N_2_X]:
            for dx in [-L298N_MOUNT_OFFSET, L298N_MOUNT_OFFSET]:
                for dy in [-L298N_MOUNT_OFFSET, L298N_MOUNT_OFFSET]:
                    l298nSketch.sketchCurves.sketchCircles.addByCenterRadius(
                        p(driver_x + dx, L298N_Y + dy, 0), ESP32_STAND_R
                    )

        for pi in range(l298nSketch.profiles.count):
            pr = l298nSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.5:
                lInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                lInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(
                        FLOOR_H + ESP32_STAND_H)
                )
                try:
                    extrudes.add(lInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 3b: Screw holes in ALL standoffs (M2.5 self-tap, 2.0mm dia)
        # Cut from top down into each standoff for PCB mounting screws
        # ══════════════════════════════════════════════════════════════

        SCREW_R = 0.1        # 2.0mm dia (self-tapping into PLA for M2.5)
        SCREW_DEPTH = ESP32_STAND_H + 0.2  # through standoff + into floor

        # Combine all standoff positions
        all_standoff_positions = list(esp32_positions)

        for driver_x in [L298N_1_X, L298N_2_X]:
            for dx in [-L298N_MOUNT_OFFSET, L298N_MOUNT_OFFSET]:
                for dy in [-L298N_MOUNT_OFFSET, L298N_MOUNT_OFFSET]:
                    all_standoff_positions.append((driver_x + dx, L298N_Y + dy))

        # Create screw holes from top of standoffs
        standoffTopPlane = comp.constructionPlanes
        stpInput = standoffTopPlane.createInput()
        stpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(FLOOR_H + ESP32_STAND_H)
        )
        standoffTopP = standoffTopPlane.add(stpInput)

        screwSketch = comp.sketches.add(standoffTopP)
        screwSketch.name = 'Standoff Screws'

        for sx, sy in all_standoff_positions:
            screwSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(sx, sy, 0), SCREW_R
            )

        for pi in range(screwSketch.profiles.count):
            pr = screwSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.1:
                scInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                scInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(SCREW_DEPTH)
                )
                try:
                    extrudes.add(scInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 5: LiPo battery cradle walls (raised ridges)
        # Just the outline walls, battery sits inside
        # ══════════════════════════════════════════════════════════════

        # Create raised cradle walls as a frame
        cradleSketch = comp.sketches.add(comp.xYConstructionPlane)
        cradleSketch.name = 'LiPo Cradle'
        cl = cradleSketch.sketchCurves.sketchLines

        # Outer rectangle of cradle
        cl.addTwoPointRectangle(
            p(LIPO_X - LIPO_W / 2 - LIPO_WALL, LIPO_Y - LIPO_L / 2 - LIPO_WALL, 0),
            p(LIPO_X + LIPO_W / 2 + LIPO_WALL, LIPO_Y + LIPO_L / 2 + LIPO_WALL, 0)
        )
        # Inner rectangle (battery space)
        cl.addTwoPointRectangle(
            p(LIPO_X - LIPO_W / 2, LIPO_Y - LIPO_L / 2, 0),
            p(LIPO_X + LIPO_W / 2, LIPO_Y + LIPO_L / 2, 0)
        )

        # Find the frame profile (annular/ring-shaped region)
        # This is the profile that's NOT the smallest and NOT the largest
        areas = []
        for pi in range(cradleSketch.profiles.count):
            pr = cradleSketch.profiles.item(pi)
            a = pr.areaProperties().area
            areas.append((a, pi))
        areas.sort()

        # The frame is typically the middle-sized area, or we can pick
        # profiles that represent the wall region
        if len(areas) >= 2:
            # Try the second profile (frame region)
            for a, pi in areas:
                pr = cradleSketch.profiles.item(pi)
                area = pr.areaProperties().area
                # Frame area should be between inner and outer
                if area > areas[0][0] and area < areas[-1][0]:
                    cInput = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    cInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(TRAY_H)
                    )
                    try:
                        extrudes.add(cInput)
                    except:
                        pass
                    break

        # ══════════════════════════════════════════════════════════════
        # Step 5b: Battery strap anchor posts (for velcro or rubber band)
        # Two small posts on opposite sides of the battery cradle
        # ══════════════════════════════════════════════════════════════

        STRAP_POST_R = 0.2   # 4mm dia post
        STRAP_POST_H = TRAY_H + 0.3  # 3mm above tray wall
        STRAP_OFFSET = LIPO_W / 2 + LIPO_WALL + 0.4  # 4mm outside cradle

        strapSketch = comp.sketches.add(comp.xYConstructionPlane)
        strapSketch.name = 'Strap Posts'
        strapSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(LIPO_X - STRAP_OFFSET, LIPO_Y, 0), STRAP_POST_R
        )
        strapSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(LIPO_X + STRAP_OFFSET, LIPO_Y, 0), STRAP_POST_R
        )

        for pi in range(strapSketch.profiles.count):
            pr = strapSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.2:
                spInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                spInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(STRAP_POST_H)
                )
                try:
                    extrudes.add(spInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 6: Wire routing grooves (cut into tray floor from top)
        # Connects: ESP32↔L298N #1, ESP32↔L298N #2,
        #           ESP32↔breadboard area, battery cradle→rear edge
        # ══════════════════════════════════════════════════════════════

        # Create a plane at floor top surface to sketch channels
        floorPlane = comp.constructionPlanes
        fpInput = floorPlane.createInput()
        fpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(FLOOR_H)
        )
        floorP = floorPlane.add(fpInput)

        channelSketch = comp.sketches.add(floorP)
        channelSketch.name = 'Wire Channels'
        chl = channelSketch.sketchCurves.sketchLines

        half_ch = CHANNEL_W / 2

        # Channel 1: ESP32 (centre, Y=4) → L298N #1 (X=-3.5, Y=-3)
        chl.addTwoPointRectangle(
            p(ESP32_X - half_ch, ESP32_Y - ESP32_MOUNT_DY / 2, 0),
            p(L298N_1_X + L298N_MOUNT_OFFSET + half_ch, ESP32_Y - ESP32_MOUNT_DY / 2 - CHANNEL_W, 0)
        )
        # Vertical run down to L298N #1
        chl.addTwoPointRectangle(
            p(L298N_1_X - half_ch, L298N_Y + L298N_MOUNT_OFFSET, 0),
            p(L298N_1_X + half_ch, ESP32_Y - ESP32_MOUNT_DY / 2 - CHANNEL_W, 0)
        )

        # Channel 2: ESP32 (centre) → L298N #2 (X=+3.5, Y=-3)
        chl.addTwoPointRectangle(
            p(ESP32_X + half_ch, ESP32_Y - ESP32_MOUNT_DY / 2, 0),
            p(L298N_2_X - L298N_MOUNT_OFFSET - half_ch, ESP32_Y - ESP32_MOUNT_DY / 2 - CHANNEL_W, 0)
        )
        # Vertical run down to L298N #2
        chl.addTwoPointRectangle(
            p(L298N_2_X - half_ch, L298N_Y + L298N_MOUNT_OFFSET, 0),
            p(L298N_2_X + half_ch, ESP32_Y - ESP32_MOUNT_DY / 2 - CHANNEL_W, 0)
        )

        # Channel 3: ESP32 → breadboard area (X=+4, Y=+7)
        chl.addTwoPointRectangle(
            p(ESP32_X + ESP32_MOUNT_DX / 2, ESP32_Y + ESP32_MOUNT_DY / 2, 0),
            p(BB_X - BB_W / 2, ESP32_Y + ESP32_MOUNT_DY / 2 + CHANNEL_W, 0)
        )

        # Channel 4: LiPo cradle → rear edge (cable exit)
        chl.addTwoPointRectangle(
            p(LIPO_X - half_ch, -TRAY_L / 2 + WALL_T, 0),
            p(LIPO_X + half_ch, LIPO_Y - LIPO_L / 2, 0)
        )

        # Cut all channel profiles into floor
        for pi in range(channelSketch.profiles.count):
            pr = channelSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 8.0:  # channel-sized profiles only
                chInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                chInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(CHANNEL_D)
                )
                try:
                    extrudes.add(chInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 7: Breadboard locating pocket (49×37mm, 2mm deep)
        # ══════════════════════════════════════════════════════════════

        bbSketch = comp.sketches.add(floorP)
        bbSketch.name = 'Breadboard Pocket'
        bbSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(BB_X - BB_W / 2, BB_Y - BB_L / 2, 0),
            p(BB_X + BB_W / 2, BB_Y + BB_L / 2, 0)
        )

        bbProf = None
        minArea = float('inf')
        for pi in range(bbSketch.profiles.count):
            pr = bbSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                bbProf = pr

        if bbProf:
            bbInput = extrudes.createInput(
                bbProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            bbInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(0.2)  # 2mm pocket
            )
            try:
                extrudes.add(bbInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════════
        # Step 8: Cable exit holes on tray walls (10×5mm rectangular slots)
        # One on each side wall + one on rear wall for battery/motor cables
        # ══════════════════════════════════════════════════════════════

        # Left wall exit (for L298N #1 motor cables)
        leftWallInput = comp.constructionPlanes.createInput()
        leftWallInput.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(-TRAY_W / 2)
        )
        leftWallP = comp.constructionPlanes.add(leftWallInput)

        exitSketchL = comp.sketches.add(leftWallP)
        exitSketchL.name = 'Cable Exit Left'
        exitSketchL.sketchCurves.sketchLines.addTwoPointRectangle(
            p(L298N_Y - EXIT_W / 2, FLOOR_H, 0),
            p(L298N_Y + EXIT_W / 2, FLOOR_H + EXIT_H, 0)
        )

        for pi in range(exitSketchL.profiles.count):
            pr = exitSketchL.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0:
                eInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                eInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(WALL_T + 0.01)
                )
                try:
                    extrudes.add(eInput)
                except:
                    pass

        # Right wall exit (for L298N #2 motor cables)
        rightWallInput = comp.constructionPlanes.createInput()
        rightWallInput.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(TRAY_W / 2)
        )
        rightWallP = comp.constructionPlanes.add(rightWallInput)

        exitSketchR = comp.sketches.add(rightWallP)
        exitSketchR.name = 'Cable Exit Right'
        exitSketchR.sketchCurves.sketchLines.addTwoPointRectangle(
            p(L298N_Y - EXIT_W / 2, FLOOR_H, 0),
            p(L298N_Y + EXIT_W / 2, FLOOR_H + EXIT_H, 0)
        )

        for pi in range(exitSketchR.profiles.count):
            pr = exitSketchR.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0:
                eInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                eInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(WALL_T + 0.01)
                )
                try:
                    extrudes.add(eInput)
                except:
                    pass

        # Rear wall exit (for battery/power cables)
        rearWallInput = comp.constructionPlanes.createInput()
        rearWallInput.setByOffset(
            comp.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(-TRAY_L / 2)
        )
        rearWallP = comp.constructionPlanes.add(rearWallInput)

        exitSketchRear = comp.sketches.add(rearWallP)
        exitSketchRear.name = 'Cable Exit Rear'
        exitSketchRear.sketchCurves.sketchLines.addTwoPointRectangle(
            p(LIPO_X - EXIT_W / 2, FLOOR_H, 0),
            p(LIPO_X + EXIT_W / 2, FLOOR_H + EXIT_H, 0)
        )

        for pi in range(exitSketchRear.profiles.count):
            pr = exitSketchRear.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0:
                eInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                eInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(WALL_T + 0.01)
                )
                try:
                    extrudes.add(eInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 9: Corner gussets (triangular reinforcement at wall-floor)
        # 5×5×2mm triangular gussets at all 4 interior corners
        # Prevents wall flex under vibration
        # ══════════════════════════════════════════════════════════════

        GUSSET_L = 0.5     # 5mm leg length
        GUSSET_T = 0.2     # 2mm thickness

        # Gusset positions: 4 interior corners of the tray
        corners = [
            (-TRAY_W / 2 + WALL_T, -TRAY_L / 2 + WALL_T, 'BL'),
            ( TRAY_W / 2 - WALL_T, -TRAY_L / 2 + WALL_T, 'BR'),
            (-TRAY_W / 2 + WALL_T,  TRAY_L / 2 - WALL_T, 'FL'),
            ( TRAY_W / 2 - WALL_T,  TRAY_L / 2 - WALL_T, 'FR'),
        ]

        for cx, cy, cname in corners:
            gSketch = comp.sketches.add(comp.xYConstructionPlane)
            gSketch.name = f'Gusset {cname}'
            gl = gSketch.sketchCurves.sketchLines

            # Determine which direction the gusset extends (into interior)
            dx = GUSSET_L if cx < 0 else -GUSSET_L
            dy = GUSSET_L if cy < 0 else -GUSSET_L

            # Triangle: corner, corner+dx, corner+dy
            p1 = p(cx, cy, 0)
            p2 = p(cx + dx, cy, 0)
            p3 = p(cx, cy + dy, 0)
            gl.addByTwoPoints(p1, p2)
            gl.addByTwoPoints(p2, p3)
            gl.addByTwoPoints(p3, p1)

            # Find triangular profile
            gProf = None
            minArea = float('inf')
            for pi in range(gSketch.profiles.count):
                pr = gSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    gProf = pr

            if gProf:
                gInput = extrudes.createInput(
                    gProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                gInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(FLOOR_H + GUSSET_T)
                )
                try:
                    extrudes.add(gInput)
                except:
                    pass

        # ── Zoom and report ──
        app.activeViewport.fit()

        ui.messageBox(
            'Electronics Tray created!\n\n'
            f'Tray: {TRAY_W * 10:.0f} × {TRAY_L * 10:.0f} × '
            f'{TRAY_H * 10:.0f}mm\n'
            f'Floor: {FLOOR_H * 10:.0f}mm thick\n'
            f'Walls: {WALL_T * 10:.0f}mm thick\n\n'
            f'ESP32 standoffs: 4× (M2.5 screw holes)\n'
            f'L298N standoffs: 8× (M2.5 screw holes)\n'
            f'LiPo cradle: {LIPO_W * 10:.0f}×{LIPO_L * 10:.0f}mm + strap posts\n'
            f'Wire channels: 4 ({CHANNEL_W * 10:.0f}mm wide × '
            f'{CHANNEL_D * 10:.0f}mm deep)\n'
            f'Breadboard pocket: {BB_W * 10:.0f}×{BB_L * 10:.0f}mm × 2mm\n'
            f'Cable exits: 3 ({EXIT_W * 10:.0f}×{EXIT_H * 10:.0f}mm)\n'
            f'Corner gussets: 4× (5×5×2mm triangular reinforcements)\n\n'
            'Qty needed: 1\n'
            'Print flat bottom down, 30% infill.',
            'Mars Rover - Electronics Tray'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
