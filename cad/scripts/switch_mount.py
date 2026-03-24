"""
Mars Rover Switch Mount Plate — Phase 1 (0.4 Scale)
=====================================================

Reinforcing plate for the panel-mount toggle switch on the
RR body quadrant rear wall. Glued/bolted to the inside of the
body wall to strengthen the 3mm PLA around the 15mm switch bore.

Dimensions: 30 × 30 × 5mm
  - 15mm centre bore (switch barrel)
  - 2× M3 bolt holes for body wall attachment (diagonal)
  - 5mm thick (reinforces 3mm wall from inside)
  - 2.85mm wall from bolt holes to plate edge (safe for PLA)

Qty: 1

Print orientation: Flat (face down)
Supports: None
Perimeters: 4 (solid for strength)
Infill: 60%

Reference: EA-15 (safety), EA-08 (body spec)
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
        PLATE_L = 3.0       # 30mm (X) — increased from 25mm for bolt-hole clearance
        PLATE_W = 3.0       # 30mm (Y)
        PLATE_H = 0.5       # 5mm thickness (Z)
        BORE_R = 0.75       # 15mm diameter / 2
        HOLE_R = 0.165      # M3 clearance (3.3mm dia)
        HOLE_OFFSET = 1.05  # 10.5mm from centre (wall to edge: 15-12.15 = 2.85mm)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════════
        # Step 1: Base plate
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Switch Plate'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-PLATE_L / 2, -PLATE_W / 2, 0),
            p(PLATE_L / 2, PLATE_W / 2, 0)
        )

        # Find the outer profile
        outerProf = None
        maxArea = 0
        for pi in range(sketch1.profiles.count):
            pr = sketch1.profiles.item(pi)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                outerProf = pr

        extInput = extrudes.createInput(
            outerProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(PLATE_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'Switch Mount Plate'

        # ══════════════════════════════════════════════════════════════
        # Step 2: Centre bore (15mm for toggle switch barrel)
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(PLATE_H)
        )
        topP = topPlane.add(tpInput)

        boreSketch = comp.sketches.add(topP)
        boreSketch.name = 'Switch Bore'
        boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BORE_R
        )

        boreProf = None
        minArea = float('inf')
        for pi in range(boreSketch.profiles.count):
            pr = boreSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                boreProf = pr

        if boreProf:
            boreInput = extrudes.createInput(
                boreProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            boreInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(PLATE_H + 0.1)
            )
            extrudes.add(boreInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: M3 mounting holes (diagonal corners)
        # ══════════════════════════════════════════════════════════════

        holeSketch = comp.sketches.add(topP)
        holeSketch.name = 'Mount Holes'
        holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(-HOLE_OFFSET, -HOLE_OFFSET, 0), HOLE_R
        )
        holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(HOLE_OFFSET, HOLE_OFFSET, 0), HOLE_R
        )

        for pi in range(holeSketch.profiles.count):
            pr = holeSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.2:
                hInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                hInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(PLATE_H + 0.1)
                )
                try:
                    extrudes.add(hInput)
                except:
                    pass

        # ── Report ──
        app.activeViewport.fit()
        ui.messageBox(
            'Switch Mount Plate created!\n\n'
            f'Size: {PLATE_L * 10:.0f} × {PLATE_W * 10:.0f} × '
            f'{PLATE_H * 10:.0f}mm\n'
            f'Centre bore: {BORE_R * 20:.0f}mm diameter\n'
            f'Mounting: 2× M3 holes (diagonal, 2.85mm edge wall)\n\n'
            'Glue + bolt to inside of RR body rear wall,\n'
            'aligned with the 15mm kill switch hole.\n\n'
            'Qty needed: 1\n'
            'Print flat, 60% infill, 4 perimeters.',
            'Mars Rover - Switch Mount Plate'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
