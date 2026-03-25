"""
Mars Rover Fixed Wheel Mount — Phase 1 (0.4 Scale)
=====================================================

Simple bracket that bolts to the bogie arm and holds an N20 motor
for the non-steered middle wheels. No steering pivot needed.

25 × 25 × 30mm rectangular block with:
  - N20 motor clip pocket (from bottom, motor hangs below)
  - 4mm horizontal shaft exit hole (through side wall toward wheel)
  - 2× M3 heat-set insert pockets (top, for arm bolting from one side)
  - Zip-tie slot across motor pocket opening for motor retention

Qty: 2 (ML, MR — middle left, middle right)

Print orientation: Large flat face down (25×25mm face)
Supports: None
Perimeters: 4
Infill: 50% gyroid

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

        # ── Dimensions (cm) ──
        MOUNT_L = 2.5       # 25mm (along arm direction, Y)
        MOUNT_W = 2.5       # 25mm (across arm, X)
        MOUNT_H = 3.0       # 30mm (vertical, Z)

        # N20 motor clip pocket
        MOTOR_W = 1.22      # 12.2mm clip inner width
        MOTOR_H = 1.02      # 10.2mm clip inner height
        MOTOR_DEPTH = 2.5   # 25mm clip depth (holds 24mm motor+gearbox + 1mm clearance)
        SHAFT_HOLE_R = 0.2  # 4mm shaft exit

        # M3 bolt holes for arm mounting
        BOLT_SPACING = 1.5  # 15mm between bolt centres
        BOLT_R = 0.165      # 3.3mm clearance hole for M3

        # Heat-set insert holes
        INSERT_HOLE_R = 0.24  # 4.8mm dia for M3 heat-set insert

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════════════
        # Step 1: Main body block
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Mount Body'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-MOUNT_W / 2, -MOUNT_L / 2, 0),
            p(MOUNT_W / 2, MOUNT_L / 2, 0)
        )

        prof = sketch1.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(MOUNT_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'Fixed Wheel Mount'

        # ══════════════════════════════════════════════════════════════
        # Step 2: Motor clip pocket (from bottom, motor hangs below)
        # Cut rectangular pocket from bottom face upward
        # ══════════════════════════════════════════════════════════════

        motorSketch = comp.sketches.add(comp.xYConstructionPlane)
        motorSketch.name = 'Motor Pocket'
        motorSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-MOTOR_W / 2, -MOTOR_H / 2, 0),
            p(MOTOR_W / 2, MOTOR_H / 2, 0)
        )

        mProf = None
        minArea = float('inf')
        for pi in range(motorSketch.profiles.count):
            pr = motorSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                mProf = pr

        if mProf:
            motorInput = extrudes.createInput(
                mProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            motorInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(MOTOR_DEPTH)
            )
            extrudes.add(motorInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: Horizontal shaft exit hole through side wall
        # Motor shaft exits laterally toward the wheel
        # Cut from side face (YZ plane) through to motor pocket
        # ══════════════════════════════════════════════════════════════

        SHAFT_EXIT_Z = MOTOR_DEPTH / 2  # mid-height of motor pocket

        shaftPlaneInput = comp.constructionPlanes.createInput()
        shaftPlaneInput.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(-MOUNT_W / 2)
        )
        shaftPlane = comp.constructionPlanes.add(shaftPlaneInput)

        shaftSketch = comp.sketches.add(shaftPlane)
        shaftSketch.name = 'Shaft Exit'
        # On YZ plane: sketch X -> -Z world, sketch Y -> Y world
        shaftSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(-SHAFT_EXIT_Z, 0, 0), SHAFT_HOLE_R
        )

        sProf = None
        minArea = float('inf')
        for pi in range(shaftSketch.profiles.count):
            pr = shaftSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                sProf = pr

        if sProf:
            shaftInput = extrudes.createInput(
                sProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            shaftInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(MOUNT_W)
            )
            try:
                extrudes.add(shaftInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════════
        # Step 4: M3 heat-set insert pockets (from top, for arm bolting)
        # 4.8mm dia, 5.5mm deep — bolt from one side only
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(MOUNT_H)
        )
        topP = topPlane.add(tpInput)

        boltSketch = comp.sketches.add(topP)
        boltSketch.name = 'Arm Mount Holes'

        for by in [-BOLT_SPACING / 2, BOLT_SPACING / 2]:
            boltSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(0, by, 0), INSERT_HOLE_R
            )

        for pi in range(boltSketch.profiles.count):
            pr = boltSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.3:
                bInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                bInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(0.55)  # 5.5mm
                )
                try:
                    extrudes.add(bInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 5: Zip-tie slot across motor pocket opening for retention
        # 3mm wide × 2mm deep slot on each side of pocket
        # ══════════════════════════════════════════════════════════════

        ZIPTIE_W = 0.35      # 3.5mm slot width
        ZIPTIE_DEPTH = 0.2   # 2mm deep into wall
        ZIPTIE_Z = MOTOR_DEPTH * 0.3  # 30% up from bottom

        ztPlaneInput = comp.constructionPlanes.createInput()
        ztPlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(ZIPTIE_Z)
        )
        ztPlane = comp.constructionPlanes.add(ztPlaneInput)

        ztSketch = comp.sketches.add(ztPlane)
        ztSketch.name = 'Zip Tie Slot'
        # Slot runs across the Y-axis at the motor pocket walls
        ztSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-MOUNT_W / 2, -ZIPTIE_W / 2, 0),
            p(MOUNT_W / 2, ZIPTIE_W / 2, 0)
        )

        for pi in range(ztSketch.profiles.count):
            pr = ztSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0:
                ztInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                ztInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(ZIPTIE_DEPTH)
                )
                try:
                    extrudes.add(ztInput)
                except:
                    pass

        # ── Zoom and report ──
        app.activeViewport.fit()

        ui.messageBox(
            'Fixed Wheel Mount created!\n\n'
            f'Size: {MOUNT_W * 10:.0f} × {MOUNT_L * 10:.0f} × '
            f'{MOUNT_H * 10:.0f}mm\n'
            f'Motor pocket: {MOTOR_W * 10:.1f} × {MOTOR_H * 10:.1f}mm, '
            f'{MOTOR_DEPTH * 10:.0f}mm deep\n'
            f'Shaft hole: {SHAFT_HOLE_R * 20:.0f}mm horizontal\n'
            f'Arm mount: 2× M3 heat-set insert pockets\n'
            f'Motor retention: zip-tie slot\n\n'
            'Qty needed: 2 (ML, MR)\n'
            'Print 25×25mm face down, no supports.',
            'Mars Rover - Fixed Wheel Mount'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
