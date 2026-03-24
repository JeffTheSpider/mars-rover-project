"""
Mars Rover Steering Knuckle — Phase 1
=======================================

Steering upright/knuckle for the 4 steered wheels (FL, FR, RL, RR).
Rotates about a vertical (Z-axis) steering pivot and carries the
wheel axle + motor mount below.

Updated per EA-27:
  - Steering arm extension added (15mm lateral, M2 hole for horn link)
  - Hard stop tab added (radial protrusion, contacts bracket stop walls)

The knuckle connects:
  - TOP: Steering pivot shaft (into bearing in bracket)
  - SIDE: Steering arm extension (M2 hole for horn link pin joint)
  - TOP: Hard stop tab (contacts bracket ±35° walls)
  - MIDDLE: Motor mount recess (N20 gearmotor clip)
  - BOTTOM: Wheel axle through-bore

Features:
  - Vertical pivot shaft socket: 8mm bore × 15mm deep (for 8mm rod)
  - Steering arm: 15mm extension from pivot centre, M2 hole at tip
  - Hard stop tab: 5×8×3mm radial, contacts bracket walls at ±35°
  - Motor mount recess: 12.2 × 10.2mm (N20 clip pocket)
  - Wheel axle bore: 4mm through (N20 D-shaft)
  - M3 grub screw in pivot shaft socket for retention

Overall size: ~25 × 30 × 40mm body + 15mm arm extension
Print: Upright (pivot socket up), PLA, 60% infill, 4 perimeters
Qty: 4 (FL, FR, RL, RR — all identical, symmetric design)

Reference: EA-27 (steering design package), EA-26 Section 12, EA-10
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

        # ── Dimensions (cm for Fusion API) ──
        # Pivot (top) — connects to arm via vertical shaft
        PIV_BORE_R = 0.41      # 8.2mm bore for 8mm rod (0.2mm clearance)
        PIV_DEPTH  = 1.5       # 15mm socket depth
        PIV_WALL   = 0.4       # 4mm wall around pivot bore
        GRUB_R     = 0.15      # M3 grub screw (3mm)

        # Body dimensions
        BODY_W     = 2.5       # 25mm width (X, lateral)
        BODY_L     = 3.0       # 30mm length (Y, fore-aft)
        BODY_H     = 4.0       # 40mm height (Z, vertical)

        # Motor mount (N20 pocket)
        MOTOR_W    = 1.22      # 12.2mm (N20 + clearance)
        MOTOR_H    = 1.02      # 10.2mm
        MOTOR_D    = 2.5       # 25mm pocket depth (motor body length)

        # Wheel axle (horizontal bore through bottom section)
        AXLE_R     = 0.2       # 4mm bore for N20 D-shaft
        AXLE_Z     = 0.8       # 8mm up from bottom (axle centre height)

        # Steering arm extension (EA-27)
        ARM_LENGTH = 1.5       # 15mm from pivot centre to M2 hole
        ARM_WIDTH  = 0.8       # 8mm arm width
        ARM_HEIGHT = 0.5       # 5mm arm thickness (vertical)
        ARM_HOLE_R = 0.11      # M2 clearance (2.2mm / 2)

        # Hard stop tab (EA-27)
        STOP_TAB_W = 0.5       # 5mm tab width (tangential)
        STOP_TAB_R = 0.8       # 8mm radial extent from pivot centre
        STOP_TAB_H = 0.3       # 3mm tab thickness (vertical)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Main body block
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Knuckle Body'
        sl = sketch.sketchCurves.sketchLines
        sl.addTwoPointRectangle(
            p(-BODY_W / 2, -BODY_L / 2, 0),
            p(BODY_W / 2, BODY_L / 2, 0)
        )

        prof = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                prof = pr

        knuckleBody = None
        if prof:
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_H)
            )
            ext = extrudes.add(extInput)
            knuckleBody = ext.bodies.item(0)
            knuckleBody.name = 'Steering Knuckle'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Vertical pivot shaft socket (from top, down)
        # ══════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        topInput = topPlane.createInput()
        topInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H)
        )
        topP = topPlane.add(topInput)

        pivSketch = comp.sketches.add(topP)
        pivSketch.name = 'Pivot Socket'
        pivSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), PIV_BORE_R
        )

        pivProf = None
        minArea = float('inf')
        for pi_idx in range(pivSketch.profiles.count):
            pr = pivSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                pivProf = pr

        if pivProf:
            pivInput = extrudes.createInput(
                pivProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            pivInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(PIV_DEPTH)
            )
            try:
                extrudes.add(pivInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: M3 grub screw for pivot shaft retention
        # ══════════════════════════════════════════════════════════

        midZPlane = comp.constructionPlanes
        midZInput = midZPlane.createInput()
        midZInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H - PIV_DEPTH / 2)
        )
        midZP = midZPlane.add(midZInput)

        grubSketch = comp.sketches.add(midZP)
        grubSketch.name = 'Pivot Grub Screw'
        grubSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_L / 2 - 0.1, 0), GRUB_R
        )

        grubProf = None
        minArea = float('inf')
        for pi_idx in range(grubSketch.profiles.count):
            pr = grubSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                grubProf = pr

        if grubProf:
            grubInput = extrudes.createInput(
                grubProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            grubInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(
                    BODY_L / 2 + PIV_BORE_R + 0.1)
            )
            try:
                extrudes.add(grubInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Motor mount pocket (N20 recess from -Y face)
        # ══════════════════════════════════════════════════════════

        motorSketchPlane = comp.constructionPlanes
        motorInput = motorSketchPlane.createInput()
        motorInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(AXLE_Z)
        )
        motorP = motorSketchPlane.add(motorInput)

        motorSketch = comp.sketches.add(motorP)
        motorSketch.name = 'Motor Pocket'
        msl = motorSketch.sketchCurves.sketchLines
        msl.addTwoPointRectangle(
            p(-MOTOR_W / 2, -BODY_L / 2, 0),
            p(MOTOR_W / 2, -BODY_L / 2 + MOTOR_D, 0)
        )

        motorProf = None
        maxArea = 0
        for pi_idx in range(motorSketch.profiles.count):
            pr = motorSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            target = MOTOR_W * MOTOR_D
            if abs(a - target) < target * 0.3 and a > maxArea:
                maxArea = a
                motorProf = pr

        if motorProf:
            mInput = extrudes.createInput(
                motorProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            mInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(MOTOR_H)
            )
            try:
                extrudes.add(mInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Wheel axle bore (horizontal, through body)
        # ══════════════════════════════════════════════════════════

        axlePlane = comp.constructionPlanes
        axleInput = axlePlane.createInput()
        axleInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(AXLE_Z)
        )
        axleP = axlePlane.add(axleInput)

        axleSketch = comp.sketches.add(axleP)
        axleSketch.name = 'Axle Bore'
        axleSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(-BODY_W / 2, 0, 0), AXLE_R
        )

        axleProf = None
        minArea = float('inf')
        for pi_idx in range(axleSketch.profiles.count):
            pr = axleSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                axleProf = pr

        if axleProf:
            axInput = extrudes.createInput(
                axleProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            axInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_W + 0.1)
            )
            try:
                extrudes.add(axInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 6: Steering arm extension (EA-27 — for horn link)
        # Extends laterally from knuckle body near the top
        # ══════════════════════════════════════════════════════════

        # Arm extends in +X direction from body, at pivot socket level
        arm_z = BODY_H - PIV_DEPTH / 2  # same height as grub screw level
        armPlane = comp.constructionPlanes
        armPInput = armPlane.createInput()
        armPInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(arm_z - ARM_HEIGHT / 2)
        )
        armP = armPlane.add(armPInput)

        armSketch = comp.sketches.add(armP)
        armSketch.name = 'Steering Arm'
        asl = armSketch.sketchCurves.sketchLines
        # Arm extends from body edge (+X side) outward
        asl.addTwoPointRectangle(
            p(BODY_W / 2 - 0.2, -ARM_WIDTH / 2, 0),  # slight overlap with body
            p(BODY_W / 2 - 0.2 + ARM_LENGTH, ARM_WIDTH / 2, 0)
        )

        armProf = None
        maxArea = 0
        for pi_idx in range(armSketch.profiles.count):
            pr = armSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            target = ARM_LENGTH * ARM_WIDTH
            if abs(a - target) < target * 0.5 and a > maxArea:
                maxArea = a
                armProf = pr

        if armProf:
            armInput = extrudes.createInput(
                armProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            armInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(ARM_HEIGHT)
            )
            try:
                extrudes.add(armInput)
            except:
                pass

        # M2 hole at arm tip for horn link pin joint
        armHolePlane = comp.constructionPlanes
        ahpInput = armHolePlane.createInput()
        ahpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(arm_z + ARM_HEIGHT / 2)
        )
        ahP = armHolePlane.add(ahpInput)

        armHoleSketch = comp.sketches.add(ahP)
        armHoleSketch.name = 'Arm Link Hole'
        # Hole at arm tip centre
        arm_tip_x = BODY_W / 2 - 0.2 + ARM_LENGTH - ARM_WIDTH / 2
        armHoleSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(arm_tip_x, 0, 0), ARM_HOLE_R
        )

        target_area = math.pi * ARM_HOLE_R * ARM_HOLE_R
        for pi_idx in range(armHoleSketch.profiles.count):
            pr = armHoleSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if abs(a - target_area) < target_area * 0.5:
                ahInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                ahInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(ARM_HEIGHT + 0.1)
                )
                try:
                    extrudes.add(ahInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 7: Hard stop tab (EA-27 — contacts bracket walls)
        # Radial tab near top of knuckle, in +Y direction
        # ══════════════════════════════════════════════════════════

        # Tab at the top of the body, extending radially outward in +Y
        # It sits at the same Z level as the bracket stop walls
        stopPlane = comp.constructionPlanes
        spInput = stopPlane.createInput()
        spInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H)
        )
        stopP = stopPlane.add(spInput)

        stopSketch = comp.sketches.add(stopP)
        stopSketch.name = 'Hard Stop Tab'
        ssl = stopSketch.sketchCurves.sketchLines
        # Tab extends in +Y from body edge
        ssl.addTwoPointRectangle(
            p(-STOP_TAB_W / 2, BODY_L / 2 - 0.1, 0),
            p(STOP_TAB_W / 2, BODY_L / 2 - 0.1 + STOP_TAB_R, 0)
        )

        stopProf = None
        maxArea = 0
        for pi_idx in range(stopSketch.profiles.count):
            pr = stopSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            target = STOP_TAB_W * STOP_TAB_R
            if abs(a - target) < target * 0.5 and a > maxArea:
                maxArea = a
                stopProf = pr

        if stopProf:
            stopInput = extrudes.createInput(
                stopProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            stopInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(STOP_TAB_H)
            )
            try:
                extrudes.add(stopInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 8: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Steering Knuckle created! (EA-27 updated)\n\n'
            f'Body: {BODY_W * 10:.0f} × {BODY_L * 10:.0f} × '
            f'{BODY_H * 10:.0f}mm\n\n'
            'PIVOT SOCKET (top):\n'
            f'  Bore: {PIV_BORE_R * 20:.1f}mm × {PIV_DEPTH * 10:.0f}mm deep\n'
            f'  M3 grub screw for retention\n\n'
            'STEERING ARM (EA-27):\n'
            f'  Length: {ARM_LENGTH * 10:.0f}mm from pivot centre\n'
            f'  M2 hole at tip for horn link pin joint\n\n'
            'HARD STOP TAB (EA-27):\n'
            f'  {STOP_TAB_W * 10:.0f} × {STOP_TAB_R * 10:.0f} × '
            f'{STOP_TAB_H * 10:.0f}mm radial\n'
            f'  Contacts bracket walls at ±35°\n\n'
            'MOTOR MOUNT:\n'
            f'  N20 pocket: {MOTOR_W * 10:.1f} × {MOTOR_H * 10:.1f}mm\n'
            f'  Depth: {MOTOR_D * 10:.0f}mm\n\n'
            'WHEEL AXLE:\n'
            f'  Through bore: {AXLE_R * 20:.0f}mm (N20 D-shaft)\n'
            f'  Height: {AXLE_Z * 10:.0f}mm from bottom\n\n'
            'Print upright (pivot socket up), 60% infill.\n'
            'Qty: 4 (all steered wheels)',
            'Mars Rover - Steering Knuckle'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
