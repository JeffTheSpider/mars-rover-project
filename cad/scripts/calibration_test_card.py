"""
Calibration Test Card — CTC Bizer Printer Tolerance Check
==========================================================

A small flat card with test holes at key sizes used throughout
the Mars Rover build. Print this FIRST to measure your printer's
dimensional accuracy, then update printer_calibration.py.

Test holes (through):
  2.0mm - M2 bolt
  2.2mm - M2 clearance / servo mount
  3.0mm - N20 D-shaft
  3.4mm - M3 clearance
  4.8mm - M3 heat-set insert
  8.0mm - 608ZZ bore / M8 shaft
  8.4mm - M8 clearance

Also includes:
  - 22.15mm x 3.6mm counterbore (half-depth 608ZZ seat test)
  - Outer dimensions 80x30mm for measuring XY accuracy

Instructions:
  1. Print at 0.2mm layer height, 4 perimeters, 50% infill
  2. Measure each hole with calipers
  3. Measure outer dimensions (should be 80.0 x 30.0mm)
  4. Update cad/scripts/printer_calibration.py with results
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
            ui.messageBox('No active design. Create or open a design first.')
            return

        # ── Dimensions (cm — Fusion API unit) ──
        CARD_W = 8.0        # 80mm width (X)
        CARD_D = 3.0        # 30mm depth (Y)
        CARD_H = 0.5        # 5mm height (Z)

        # Test hole diameters (mm → cm radii)
        HOLES = [
            {"dia_mm": 2.0,  "label": "M2"},
            {"dia_mm": 2.2,  "label": "M2clr"},
            {"dia_mm": 3.0,  "label": "N20shaft"},
            {"dia_mm": 3.4,  "label": "M3clr"},
            {"dia_mm": 4.8,  "label": "M3hsi"},
            {"dia_mm": 8.0,  "label": "M8/608"},
            {"dia_mm": 8.4,  "label": "M8clr"},
        ]

        # Bearing counterbore test
        BEARING_BORE_R = 1.1075   # 22.15mm dia → 11.075mm radius → 1.1075cm
        BEARING_DEPTH = 0.36      # 3.6mm (half depth test) → 0.36cm

        comp = design.rootComponent

        # ── Step 1: Create base plate ──
        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Card Base'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-CARD_W / 2, -CARD_D / 2, 0),
            adsk.core.Point3D.create(CARD_W / 2, CARD_D / 2, 0)
        )
        prof = sketch1.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(CARD_H)
        )
        baseExtrude = extrudes.add(extInput)
        baseBody = baseExtrude.bodies.item(0)
        baseBody.name = 'Calibration Card'

        # ── Step 2: Create offset plane at top of card ──
        planes = comp.constructionPlanes
        planeInput = planes.createInput()
        planeInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(CARD_H)
        )
        topPlane = planes.add(planeInput)

        # ── Step 3: Cut through-holes ──
        hole_spacing_cm = 1.0  # 10mm between hole centres
        start_x = -(len(HOLES) - 1) * hole_spacing_cm / 2  # centre the row

        for i, hole in enumerate(HOLES):
            r_cm = hole["dia_mm"] / 20.0  # mm diameter → cm radius
            cx = start_x + i * hole_spacing_cm
            cy = 0.5  # offset toward top edge (5mm from centre)

            holeSketch = comp.sketches.add(topPlane)
            holeSketch.name = f'Hole {hole["dia_mm"]}mm'
            holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(cx, cy, 0), r_cm
            )

            # Find the circle profile (inner profile = the circle itself)
            # With one circle on a plane intersecting a body, we get 2 profiles:
            # the circle and the ring around it. We want the circle (smaller area).
            holeProf = None
            minArea = float('inf')
            for pi in range(holeSketch.profiles.count):
                p = holeSketch.profiles.item(pi)
                if p.areaProperties().area < minArea:
                    minArea = p.areaProperties().area
                    holeProf = p

            if holeProf:
                cutInput = extrudes.createInput(
                    holeProf,
                    adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                cutInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(CARD_H)
                )
                extrudes.add(cutInput)

        # ── Step 4: Bearing counterbore (half-depth test) ──
        bearingSketch = comp.sketches.add(topPlane)
        bearingSketch.name = 'Bearing Seat Test'
        bearingSketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, -0.7, 0),  # offset toward bottom edge
            BEARING_BORE_R
        )

        # Find smallest profile (the circle)
        boreProf = None
        minArea = float('inf')
        for pi in range(bearingSketch.profiles.count):
            p = bearingSketch.profiles.item(pi)
            if p.areaProperties().area < minArea:
                minArea = p.areaProperties().area
                boreProf = p

        if boreProf:
            boreInput = extrudes.createInput(
                boreProf,
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            boreInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(BEARING_DEPTH)
            )
            extrudes.add(boreInput)

        # ── Step 5: Add identification dots next to each hole ──
        # Small raised bumps (count = hole position 1-7) for identification
        # without needing text labels
        dotPlane = topPlane  # build on top surface
        for i, hole in enumerate(HOLES):
            cx = start_x + i * hole_spacing_cm
            dotSketch = comp.sketches.add(dotPlane)
            dotSketch.name = f'Dots {i + 1}'

            # Place dots above the hole
            dot_y = 0.5 + hole["dia_mm"] / 20.0 + 0.15  # above hole edge + gap
            for d in range(i + 1):
                dot_x = cx - (i * 0.08) + d * 0.16  # space dots 1.6mm apart
                dotSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    adsk.core.Point3D.create(dot_x, dot_y, 0), 0.05  # 1mm dia dots
                )

            # Extrude dots up 0.4mm as identification bumps
            for pi in range(dotSketch.profiles.count):
                p = dotSketch.profiles.item(pi)
                area = p.areaProperties().area
                if area < 0.01:  # small circles only (dots, not background)
                    dotInput = extrudes.createInput(
                        p, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    dotInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(0.04)  # 0.4mm
                    )
                    try:
                        extrudes.add(dotInput)
                    except:
                        pass  # dots are cosmetic, skip if they fail

        # ── Zoom to fit ──
        app.activeViewport.fit()

        # ── Success message ──
        hole_list = '\n'.join(
            f'  Hole {i+1} ({i+1} dot{"s" if i > 0 else ""}): '
            f'{h["dia_mm"]:.1f}mm ({h["label"]})'
            for i, h in enumerate(HOLES)
        )
        ui.messageBox(
            'Calibration Test Card created!\n\n'
            f'Card size: {CARD_W * 10:.0f} x {CARD_D * 10:.0f} x '
            f'{CARD_H * 10:.0f}mm\n\n'
            'Through-holes (identify by dot count):\n'
            f'{hole_list}\n\n'
            f'Bearing counterbore: {BEARING_BORE_R * 20:.2f}mm dia x '
            f'{BEARING_DEPTH * 10:.1f}mm deep\n\n'
            'PRINT SETTINGS:\n'
            '  Layer height: 0.2mm\n'
            '  Perimeters: 4\n'
            '  Infill: 50% gyroid\n'
            '  No supports needed\n\n'
            'After printing, measure ALL holes and outer\n'
            'dimensions with calipers.',
            'Mars Rover - Calibration'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
