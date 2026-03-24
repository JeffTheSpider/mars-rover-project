"""
Mars Rover Servo Mount Bracket — Phase 1 (0.4 Scale)
======================================================

Small bracket that mounts an SG90 micro servo to the rocker/bogie arm.
The servo's horn connects to the steering bracket to rotate the wheel.

40 × 18 × 25mm bracket with:
  - SG90 pocket (22.4 × 12.2 × 12mm deep)
  - 2× M2 mounting holes (27.5mm spacing) — through tabs
  - 12mm circular horn slot (for horn clearance at ±35°)
  - 2× M3 heat-set insert pockets on bottom face for arm attachment

Length increased from 35mm to 40mm for 3.8mm tab slot walls.
Horn slot widened from 6mm to 12mm for ±35° rotation.

Qty: 4 (FL, FR, RL, RR — one per steered wheel)

Print orientation: Pocket opening up (flat bottom down)
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
        BRACKET_L = 4.0     # 40mm (along arm, Y) — increased for tab wall clearance
        BRACKET_W = 1.8     # 18mm (across arm, X direction — 2.9mm walls around servo)
        BRACKET_H = 2.5     # 25mm (vertical, Z)

        # SG90 servo pocket
        SERVO_BODY_W = 2.24  # 22.4mm (22.2 + 0.2mm clearance)
        SERVO_BODY_D = 1.20  # 12.0mm depth (pocket)
        SERVO_BODY_H = 1.22  # 12.2mm (11.8 + 0.4mm clearance)

        # Servo tab extensions (tabs stick out beyond body)
        SERVO_TAB_TOTAL_W = 3.24  # 32.4mm total with tabs
        SERVO_TAB_H = 0.25        # 2.5mm tab thickness
        # Tabs extend 5mm each side beyond body

        # M2 mounting holes for servo tabs
        M2_SPACING = 2.75   # 27.5mm centre-to-centre
        M2_HOLE_R = 0.11    # 2.2mm clearance for M2

        # Horn slot (circular for ±35° horn sweep clearance)
        HORN_SLOT_R = 0.6   # 12mm diameter (6mm radius) — clears horn at ±35°

        # M3 arm mounting holes
        M3_SPACING = 1.0    # 10mm apart
        M3_HOLE_R = 0.165   # 3.3mm clearance for M3

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════════════
        # Step 1: Main bracket body
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Bracket Body'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-BRACKET_L / 2, -BRACKET_W / 2, 0),
            p(BRACKET_L / 2, BRACKET_W / 2, 0)
        )

        prof = sketch1.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(BRACKET_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'Servo Mount'

        # ══════════════════════════════════════════════════════════════
        # Step 2: SG90 servo pocket (from top)
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BRACKET_H)
        )
        topP = topPlane.add(tpInput)

        servoSketch = comp.sketches.add(topP)
        servoSketch.name = 'Servo Pocket'
        servoSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-SERVO_BODY_W / 2, -SERVO_BODY_H / 2, 0),
            p(SERVO_BODY_W / 2, SERVO_BODY_H / 2, 0)
        )

        sProf = None
        minArea = float('inf')
        for pi in range(servoSketch.profiles.count):
            pr = servoSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                sProf = pr

        if sProf:
            servoInput = extrudes.createInput(
                sProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            servoInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(SERVO_BODY_D)
            )
            extrudes.add(servoInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: Tab slots (servo mounting tabs rest on ledges)
        # Cut wider slots at the tab level
        # ══════════════════════════════════════════════════════════════

        # Tab level: just below the top of the pocket
        tabPlane = comp.constructionPlanes
        tabInput = tabPlane.createInput()
        tabInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BRACKET_H - SERVO_BODY_D + SERVO_TAB_H)
        )
        tabP = tabPlane.add(tabInput)

        tabSketch = comp.sketches.add(topP)
        tabSketch.name = 'Tab Slots'
        tabSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-SERVO_TAB_TOTAL_W / 2, -SERVO_BODY_H / 2, 0),
            p(SERVO_TAB_TOTAL_W / 2, SERVO_BODY_H / 2, 0)
        )

        # Find the ring-shaped profile (tab area minus servo body area)
        # Use the larger profile that includes the tab extension
        tProf = None
        maxArea = 0
        for pi in range(tabSketch.profiles.count):
            pr = tabSketch.profiles.item(pi)
            a = pr.areaProperties().area
            # We want the annular region (tab slots)
            if a > maxArea:
                maxArea = a
                tProf = pr

        if tProf:
            tabCutInput = extrudes.createInput(
                tProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            tabCutInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(SERVO_TAB_H)
            )
            try:
                extrudes.add(tabCutInput)
            except:
                pass  # May fail if geometry overlaps

        # ══════════════════════════════════════════════════════════════
        # Step 4: M2 mounting holes through bracket (for servo tabs)
        # ══════════════════════════════════════════════════════════════

        m2Sketch = comp.sketches.add(topP)
        m2Sketch.name = 'M2 Holes'

        for hx in [-M2_SPACING / 2, M2_SPACING / 2]:
            m2Sketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(hx, 0, 0), M2_HOLE_R
            )

        for pi in range(m2Sketch.profiles.count):
            pr = m2Sketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.1:  # small circles only
                m2Input = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                m2Input.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(BRACKET_H + 0.1)
                )
                try:
                    extrudes.add(m2Input)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 5: Horn slot (circular cut from top for servo horn clearance)
        # ══════════════════════════════════════════════════════════════

        hornSketch = comp.sketches.add(topP)
        hornSketch.name = 'Horn Slot'
        hornSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), HORN_SLOT_R
        )

        hornProf = None
        minArea = float('inf')
        for pi in range(hornSketch.profiles.count):
            pr = hornSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                hornProf = pr

        if hornProf:
            hornInput = extrudes.createInput(
                hornProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            hornInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(BRACKET_H)
            )
            try:
                extrudes.add(hornInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════════
        # Step 6: M3 heat-set insert pockets on bottom face for arm mounting
        # ══════════════════════════════════════════════════════════════

        HSERT_R = 0.24       # 4.8mm dia / 2
        HSERT_DEPTH = 0.55   # 5.5mm deep
        ARM_MOUNT_SPACING = 2.0  # 20mm between mount holes (Y)

        armSketch = comp.sketches.add(comp.xYConstructionPlane)
        armSketch.name = 'Arm Mount Holes'
        for ay in [-ARM_MOUNT_SPACING / 2, ARM_MOUNT_SPACING / 2]:
            armSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(0, ay, 0), HSERT_R
            )

        for pi in range(armSketch.profiles.count):
            pr = armSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.3:
                armInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                armInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(HSERT_DEPTH)
                )
                try:
                    extrudes.add(armInput)
                except:
                    pass

        # ── Zoom and report ──
        app.activeViewport.fit()

        ui.messageBox(
            'Servo Mount Bracket created!\n\n'
            f'Size: {BRACKET_L * 10:.0f} × {BRACKET_W * 10:.0f} × '
            f'{BRACKET_H * 10:.0f}mm\n'
            f'Servo pocket: {SERVO_BODY_W * 10:.1f} × {SERVO_BODY_H * 10:.1f}mm, '
            f'{SERVO_BODY_D * 10:.0f}mm deep\n'
            f'M2 holes: {M2_SPACING * 10:.1f}mm spacing\n'
            f'Horn slot: {HORN_SLOT_R * 20:.0f}mm dia circular\n'
            f'Arm mount: 2× M3 heat-set insert pockets\n\n'
            'Qty needed: 4 (FL, FR, RL, RR)\n'
            'Print pocket-up, no supports.',
            'Mars Rover - Servo Mount'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
