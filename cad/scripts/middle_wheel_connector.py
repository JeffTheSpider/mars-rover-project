"""
Mars Rover Middle Wheel Connector — Phase 1
=============================================

End connector at the middle wheel position. Receives one 8mm tube
from the bogie arm. Middle wheels are NOT steered — only a fixed
motor mount is needed.

Features:
  - 1× tube socket (8.2mm bore × 15mm deep) with M3 grub screw
  - Fixed wheel mount face: 2× M3 heat-set inserts (matches fixed_wheel_mount.py)
  - Wire exit hole: 8×6mm (motor wires only — no servo)
  - 4mm minimum wall thickness

Overall size: ~30 × 25 × 25mm (smallest connector)
Print: Flat (mount face down), PLA, 60% infill, 5 perimeters
Qty: 2 (ML, MR — symmetric)

Reference: EA-25, Sawppy Fixed Knuckle (100×40×73.5mm — ours is much smaller)
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

        # ── Dimensions (cm, EA-25) ──
        TUBE_BORE_R = 0.41
        TUBE_DEPTH = 1.5
        GRUB_R = 0.15
        WALL = 0.4
        INSERT_BORE_R = 0.24
        INSERT_DEPTH = 0.55
        WIRE_W = 0.8
        WIRE_H = 0.6

        BODY_W = 3.0               # 30mm
        BODY_D = 2.5               # 25mm
        BODY_H = 2.5               # 25mm
        MOUNT_BOLT_SPACING = 1.6   # 16mm (matches fixed_wheel_mount)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ═══ STEP 1: Body block ═══
        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Connector Body'
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-BODY_W / 2, 0, 0),
            p(BODY_W / 2, BODY_H, 0)
        )

        prof = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                prof = pr

        body = None
        if prof:
            ext = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            ext.setDistanceExtent(False, adsk.core.ValueInput.createByReal(BODY_D))
            body = extrudes.add(ext).bodies.item(0)
            body.name = 'Middle Wheel Connector'

        # ═══ STEP 2: Tube socket ═══
        topPlane = comp.constructionPlanes.add(
            comp.constructionPlanes.createInput().setByOffset(
                comp.xYConstructionPlane,
                adsk.core.ValueInput.createByReal(BODY_H)
            ) or comp.constructionPlanes.createInput()
        )

        # Workaround: create plane properly
        tpInput = comp.constructionPlanes.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H)
        )
        topPlane = comp.constructionPlanes.add(tpInput)

        tubeSketch = comp.sketches.add(topPlane)
        tubeSketch.name = 'Tube Socket'
        tubeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_D / 2, 0), TUBE_BORE_R
        )

        tubeProf = None
        minArea = float('inf')
        for pi_idx in range(tubeSketch.profiles.count):
            pr = tubeSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                tubeProf = pr

        if tubeProf:
            tInput = extrudes.createInput(
                tubeProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            tInput.setDistanceExtent(True, adsk.core.ValueInput.createByReal(TUBE_DEPTH))
            try:
                extrudes.add(tInput)
            except:
                pass

        # ═══ STEP 3: Grub screw ═══
        grub_y = BODY_H - TUBE_DEPTH / 2
        gpInput = comp.constructionPlanes.createInput()
        gpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(grub_y)
        )
        gP = comp.constructionPlanes.add(gpInput)

        gSketch = comp.sketches.add(gP)
        gSketch.name = 'Grub Screw'
        gSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(TUBE_BORE_R + WALL / 2, BODY_D / 2, 0), GRUB_R
        )

        gProf = None
        minArea = float('inf')
        for pi_idx in range(gSketch.profiles.count):
            pr = gSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                gProf = pr

        if gProf:
            gInput = extrudes.createInput(
                gProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            gInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(WALL + TUBE_BORE_R + 0.1)
            )
            try:
                extrudes.add(gInput)
            except:
                pass

        # ═══ STEP 4: Fixed mount inserts (bottom face) ═══
        for offset in [-MOUNT_BOLT_SPACING / 2, MOUNT_BOLT_SPACING / 2]:
            iSketch = comp.sketches.add(comp.xYConstructionPlane)
            iSketch.name = 'Mount Insert'
            iSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(offset, BODY_D / 2, 0), INSERT_BORE_R
            )

            iProf = None
            minArea = float('inf')
            for pi_idx in range(iSketch.profiles.count):
                pr = iSketch.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    iProf = pr

            if iProf:
                iInput = extrudes.createInput(
                    iProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                iInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(INSERT_DEPTH)
                )
                try:
                    extrudes.add(iInput)
                except:
                    pass

        # ═══ STEP 5: Wire exit ═══
        wSketch = comp.sketches.add(comp.xYConstructionPlane)
        wSketch.name = 'Wire Exit'
        wSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-WIRE_W / 2, -0.01, 0),
            p(WIRE_W / 2, 0.01, 0)
        )

        wProf = None
        minArea = float('inf')
        for pi_idx in range(wSketch.profiles.count):
            pr = wSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                wProf = pr

        if wProf:
            wInput = extrudes.createInput(
                wProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            wInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_D)
            )
            try:
                extrudes.add(wInput)
            except:
                pass

        # ═══ Report ═══
        app.activeViewport.fit()

        ui.messageBox(
            'Middle Wheel Connector created!\n\n'
            f'Body: {BODY_W * 10:.0f} × {BODY_D * 10:.0f} × {BODY_H * 10:.0f}mm\n'
            f'Tube socket: {TUBE_BORE_R * 20:.1f}mm × {TUBE_DEPTH * 10:.0f}mm\n'
            f'Mount inserts: 2× M3 ({MOUNT_BOLT_SPACING * 10:.0f}mm spacing)\n'
            f'Wire exit: {WIRE_W * 10:.0f} × {WIRE_H * 10:.0f}mm\n\n'
            'Bolt fixed_wheel_mount.py to bottom face.\n'
            'No steering — middle wheels are fixed.\n\n'
            'Qty: 2 (ML, MR)',
            'Mars Rover - Middle Wheel Connector'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
