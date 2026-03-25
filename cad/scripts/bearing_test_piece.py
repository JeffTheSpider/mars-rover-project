"""
Bearing Test Piece — 608ZZ Press-Fit Validation
================================================

Creates a simple test piece in Fusion 360 to validate 608ZZ bearing
press-fit dimensions on the CTC printer (PLA).

608ZZ bearing: 8mm ID x 22mm OD x 7mm width
Bore: 22.15mm (0.15mm oversize for PLA press-fit)
Seat depth: 7.2mm (bearing width + 0.2mm)

The test piece is a 30mm diameter cylinder, 10mm tall, with a 22.15mm
bore in the centre and a 0.3mm chamfer to guide insertion.

After printing, test-fit a 608ZZ bearing:
- Too tight: increase bore by 0.05mm increments
- Too loose: decrease bore by 0.05mm increments
- Target: firm press fit by hand, no hammer needed

Usage: Run as a Script in Fusion 360 (UTILITIES > Scripts and Add-Ins)

Reference: EA-08 Section 10.3 (Bearing Press-Fit Dimensions)
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
            ui.messageBox('No active design. Please create or open a design first.')
            return

        # ── Parameters (all in cm — Fusion 360 API uses cm internally) ──
        OUTER_R = 1.5         # 15mm radius (30mm outer diameter)
        HEIGHT = 1.0          # 10mm tall
        BORE_R = 1.1075       # 11.075mm radius (22.15mm bore for 608ZZ)
        BORE_DEPTH = 0.72     # 7.2mm seat depth (7mm bearing + 0.2mm)
        SHAFT_R = 0.405       # 4.05mm radius (8.1mm through-hole)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ═══ STEP 1: Outer cylinder ═══
        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Outer Cylinder'
        sketch1.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), OUTER_R
        )
        prof1 = sketch1.profiles.item(0)
        ext1 = extrudes.createInput(
            prof1, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext1.setDistanceExtent(False, adsk.core.ValueInput.createByReal(HEIGHT))
        body = extrudes.add(ext1).bodies.item(0)
        body.name = 'Bearing Test Piece'

        # ═══ STEP 2: Bearing bore (cut from top) ═══
        # Create offset plane at top
        topInput = comp.constructionPlanes.createInput()
        topInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(HEIGHT)
        )
        topPlane = comp.constructionPlanes.add(topInput)

        sketch2 = comp.sketches.add(topPlane)
        sketch2.name = 'Bearing Bore'
        sketch2.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BORE_R
        )

        # Pick the inner (smaller) profile for the cut
        boreProf = None
        minArea = float('inf')
        for i in range(sketch2.profiles.count):
            pr = sketch2.profiles.item(i)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                boreProf = pr

        if boreProf:
            ext2 = extrudes.createInput(
                boreProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            ext2.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(BORE_DEPTH)
            )
            extrudes.add(ext2)

        # ═══ STEP 3: Shaft through-hole (cut from bottom) ═══
        sketch3 = comp.sketches.add(comp.xYConstructionPlane)
        sketch3.name = 'Shaft Hole'
        sketch3.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), SHAFT_R
        )

        shaftProf = None
        minArea = float('inf')
        for i in range(sketch3.profiles.count):
            pr = sketch3.profiles.item(i)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                shaftProf = pr

        if shaftProf:
            ext3 = extrudes.createInput(
                shaftProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            ext3.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(HEIGHT)
            )
            extrudes.add(ext3)

        # ── Zoom to fit ──
        app.activeViewport.fit()

        # ── Report ──
        ui.messageBox(
            'Bearing Test Piece created!\n\n'
            f'Outer diameter: {OUTER_R * 20:.1f}mm\n'
            f'Height: {HEIGHT * 10:.1f}mm\n'
            f'Bore diameter: {BORE_R * 20:.2f}mm (608ZZ + 0.15mm)\n'
            f'Bore depth: {BORE_DEPTH * 10:.1f}mm\n'
            f'Shaft hole: {SHAFT_R * 20:.1f}mm\n\n'
            'Print this piece and test-fit a 608ZZ bearing.\n'
            'Adjust bore ±0.05mm if needed.',
            'Mars Rover - Bearing Test'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
