"""
Tube Socket Test Piece — 8mm Rod Fit Validation
================================================

Creates a simple test piece in Fusion 360 to validate 8mm steel rod
press-fit in the tube socket bore used by all suspension connectors.

Target: 8.2mm bore (0.2mm clearance on 8mm rod)
Socket depth: 15mm (same as all connectors)
Wall: 4mm around socket
M3 grub screw: radial hole for retention validation

After printing, test-fit an 8mm steel rod:
- Too tight: increase bore by 0.05mm increments
- Too loose: decrease bore by 0.05mm increments
- Target: snug slide-fit by hand, held by M3 grub screw
- Also test grub screw: can M3 thread tap into PLA?

Includes 3 test bores at 8.1mm, 8.2mm, 8.3mm so you can pick
the best fit without reprinting.

Overall size: ~50 × 20 × 20mm (tiny, <15min print)
Print: Flat, PLA, 60% infill, 5 perimeters (matches connector settings)

Reference: EA-25 (suspension audit), all connector scripts
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

        # ── Parameters (cm — Fusion 360 API) ──
        # Three test bores: tight, nominal, loose
        BORE_RADII = [0.405, 0.41, 0.415]  # 8.1mm, 8.2mm, 8.3mm
        BORE_LABELS = ['8.1', '8.2', '8.3']
        SOCKET_DEPTH = 1.5      # 15mm (matches connectors)
        WALL = 0.4              # 4mm wall
        GRUB_R = 0.15           # 3mm M3 grub screw

        # Each test socket is a cylinder with bore
        SOCKET_OD = (max(BORE_RADII) + WALL) * 2  # ~16.6mm OD
        SOCKET_R = SOCKET_OD / 2
        SPACING = SOCKET_OD + 0.2  # 0.2cm = 2mm gap between sockets
        TOTAL_W = SPACING * 3 - 0.2  # total width of 3 sockets

        # Base plate to connect the 3 sockets
        BASE_W = TOTAL_W + 0.4  # extra margin
        BASE_D = SOCKET_OD + 0.4
        BASE_H = 0.3           # 3mm base plate

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Base plate
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Base Plate'
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-BASE_W / 2, -BASE_D / 2, 0),
            p(BASE_W / 2, BASE_D / 2, 0)
        )

        prof = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                prof = pr

        baseBody = None
        if prof:
            ext = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            ext.setDistanceExtent(False, adsk.core.ValueInput.createByReal(BASE_H))
            baseBody = extrudes.add(ext).bodies.item(0)
            baseBody.name = 'Tube Socket Test'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Three socket cylinders on base
        # ══════════════════════════════════════════════════════════

        topSketch = comp.sketches.add(comp.xYConstructionPlane)
        topSketch.name = 'Socket Cylinders'

        # Place 3 cylinders side by side on X axis
        for i, bore_r in enumerate(BORE_RADII):
            cx = -SPACING + i * SPACING  # -spacing, 0, +spacing
            topSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(cx, 0, 0), SOCKET_R
            )

        # Extrude all 3 circles upward (join to base)
        # Find circle profiles (smaller than base rectangle)
        for pi_idx in range(topSketch.profiles.count):
            pr = topSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            expected_circle = math.pi * SOCKET_R ** 2
            if abs(a - expected_circle) < expected_circle * 0.3:
                cylInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                cylInput.setDistanceExtent(
                    False,
                    adsk.core.ValueInput.createByReal(BASE_H + SOCKET_DEPTH)
                )
                try:
                    extrudes.add(cylInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: Bore holes (3 different diameters)
        # Cut from the top of each cylinder
        # ══════════════════════════════════════════════════════════

        # Create plane at top of sockets
        topH = BASE_H + SOCKET_DEPTH
        tpInput = comp.constructionPlanes.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(topH)
        )
        topPlane = comp.constructionPlanes.add(tpInput)

        for i, bore_r in enumerate(BORE_RADII):
            cx = -SPACING + i * SPACING

            boreSketch = comp.sketches.add(topPlane)
            boreSketch.name = f'Bore {BORE_LABELS[i]}mm'
            boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(cx, 0, 0), bore_r
            )

            bProf = None
            minArea = float('inf')
            for pi_idx in range(boreSketch.profiles.count):
                pr = boreSketch.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    bProf = pr

            if bProf:
                bInput = extrudes.createInput(
                    bProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                bInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(SOCKET_DEPTH)
                )
                try:
                    extrudes.add(bInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: M3 grub screw hole in middle socket (nominal 8.2mm)
        # Radial hole from outside into bore
        # ══════════════════════════════════════════════════════════

        # Plane at mid-height of the socket bore
        grubH = BASE_H + SOCKET_DEPTH / 2
        gpInput = comp.constructionPlanes.createInput()
        gpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(grubH)
        )
        grubPlane = comp.constructionPlanes.add(gpInput)

        grubSketch = comp.sketches.add(grubPlane)
        grubSketch.name = 'Grub Screw Test'
        # Middle socket is at cx=0
        grubSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(BORE_RADII[1] + WALL / 2, 0, 0), GRUB_R
        )

        gProf = None
        minArea = float('inf')
        for pi_idx in range(grubSketch.profiles.count):
            pr = grubSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                gProf = pr

        if gProf:
            gInput = extrudes.createInput(
                gProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            gInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(WALL + BORE_RADII[1] + 0.1)
            )
            try:
                extrudes.add(gInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Tube Socket Test Piece created!\n\n'
            'THREE test sockets side by side:\n'
            f'  LEFT:   {BORE_LABELS[0]}mm bore (tight)\n'
            f'  CENTRE: {BORE_LABELS[1]}mm bore (nominal) + M3 grub\n'
            f'  RIGHT:  {BORE_LABELS[2]}mm bore (loose)\n\n'
            f'Socket depth: {SOCKET_DEPTH * 10:.0f}mm\n'
            f'Wall: {WALL * 10:.0f}mm\n\n'
            'TEST PROCEDURE:\n'
            '1. Print flat, PLA, 60% infill, 5 perimeters\n'
            '2. Insert 8mm steel rod into each socket\n'
            '3. LEFT (8.1mm): Should be tight push-fit\n'
            '4. CENTRE (8.2mm): Should be snug slide-fit (target)\n'
            '5. RIGHT (8.3mm): Should be loose (too much play)\n'
            '6. Test M3 grub screw in centre hole\n'
            '7. Pick best bore diameter for all connectors\n\n'
            'If 8.2mm is wrong for your printer, adjust\n'
            'TUBE_BORE_R in all connector scripts.',
            'Mars Rover - Tube Socket Test'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
