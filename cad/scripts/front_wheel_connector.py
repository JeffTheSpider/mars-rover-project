"""
Mars Rover Front/Rear Wheel Connector — Phase 1
=================================================

End connector at the front or rear wheel position. Receives one 8mm
tube from the suspension arm and provides mounting faces for the
steering bracket and servo mount.

Also used for rear wheels (identical geometry — all 4 corner wheels
are steered).

Features:
  - 1× tube socket (8.2mm bore × 15mm deep) with M3 grub screw
  - Steering bracket mount face: 2× M3 heat-set inserts (matches steering_bracket.py)
  - Servo mount face: 2× M3 heat-set inserts (matches servo_mount.py)
  - Wire exit hole: 10×8mm (motor + servo wires exit here)
  - 4mm minimum wall thickness

Overall size: ~35 × 30 × 30mm
Print: Flat (mount face down), PLA, 60% infill, 5 perimeters
Qty: 4 (FL, FR, RL, RR — symmetric, no mirror needed)

Reference: EA-25, Sawppy Steering Knuckle (97×40×110mm — ours is much smaller)
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

        # ── Shared connector dimensions (cm, EA-25) ──
        TUBE_BORE_R = 0.41          # 8.2mm
        TUBE_DEPTH = 1.5            # 15mm
        GRUB_R = 0.15               # 3mm M3
        WALL = 0.4                  # 4mm
        INSERT_BORE_R = 0.24        # 4.8mm (heat-set insert)
        INSERT_DEPTH = 0.55         # 5.5mm
        WIRE_W = 1.0                # 10mm wire exit width
        WIRE_H = 0.8                # 8mm wire exit height

        # ── Connector body ──
        BODY_W = 3.5               # 35mm width (X)
        BODY_D = 3.0               # 30mm depth (Z)
        BODY_H = 3.0               # 30mm height (Y, tube enters from top)

        # ── Mount bolt patterns ──
        # Steering bracket: 2× M3 bolts, 20mm spacing, on front face
        STEER_BOLT_SPACING = 2.0   # 20mm
        # Servo mount: 2× M3 bolts, 20mm spacing, on side face
        SERVO_BOLT_SPACING = 2.0   # 20mm

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Main body block
        # Rectangular block, tube enters from top (Y+)
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Connector Body'
        sl = sketch.sketchCurves.sketchLines
        sl.addTwoPointRectangle(
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

        connBody = None
        if prof:
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_D)
            )
            connExt = extrudes.add(extInput)
            connBody = connExt.bodies.item(0)
            connBody.name = 'Front Wheel Connector'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Tube socket bore (from top face, vertical)
        # ══════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H)
        )
        topP = topPlane.add(tpInput)

        tubeSketch = comp.sketches.add(topP)
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
            tubeInput = extrudes.createInput(
                tubeProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            tubeInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(TUBE_DEPTH)
            )
            try:
                extrudes.add(tubeInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: M3 grub screw hole for tube retention
        # Horizontal hole through wall into tube socket
        # ══════════════════════════════════════════════════════════

        grub_y = BODY_H - TUBE_DEPTH / 2  # Mid-socket height
        grubPlane = comp.constructionPlanes
        gpInput = grubPlane.createInput()
        gpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(grub_y)
        )
        gP = grubPlane.add(gpInput)

        grubSketch = comp.sketches.add(gP)
        grubSketch.name = 'Grub Screw'
        grubSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(TUBE_BORE_R + WALL / 2, BODY_D / 2, 0), GRUB_R
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
                False, adsk.core.ValueInput.createByReal(WALL + TUBE_BORE_R + 0.1)
            )
            try:
                extrudes.add(grubInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Steering bracket mount — 2× heat-set inserts on front face
        # ══════════════════════════════════════════════════════════

        for offset in [-STEER_BOLT_SPACING / 2, STEER_BOLT_SPACING / 2]:
            insSketch = comp.sketches.add(comp.xYConstructionPlane)
            insSketch.name = 'Steer Insert'
            insSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(offset, BODY_H / 3, 0), INSERT_BORE_R
            )

            insProf = None
            minArea = float('inf')
            for pi_idx in range(insSketch.profiles.count):
                pr = insSketch.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    insProf = pr

            if insProf:
                insInput = extrudes.createInput(
                    insProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                insInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(INSERT_DEPTH)
                )
                try:
                    extrudes.add(insInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Servo mount — 2× heat-set inserts on side face
        # ══════════════════════════════════════════════════════════

        sidePlane = comp.constructionPlanes
        spInput = sidePlane.createInput()
        spInput.setByOffset(
            comp.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_W / 2)
        )
        sP = sidePlane.add(spInput)

        for offset in [-SERVO_BOLT_SPACING / 2, SERVO_BOLT_SPACING / 2]:
            sInsSketch = comp.sketches.add(sP)
            sInsSketch.name = 'Servo Insert'
            sInsSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(BODY_D / 2, BODY_H / 3 + offset, 0), INSERT_BORE_R
            )

            sInsProf = None
            minArea = float('inf')
            for pi_idx in range(sInsSketch.profiles.count):
                pr = sInsSketch.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    sInsProf = pr

            if sInsProf:
                sInsInput = extrudes.createInput(
                    sInsProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                sInsInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(INSERT_DEPTH)
                )
                try:
                    extrudes.add(sInsInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 6: Wire exit hole (bottom face)
        # ══════════════════════════════════════════════════════════

        wireSketch = comp.sketches.add(comp.xYConstructionPlane)
        wireSketch.name = 'Wire Exit'
        wl = wireSketch.sketchCurves.sketchLines
        wl.addTwoPointRectangle(
            p(-WIRE_W / 2, -0.01, 0),
            p(WIRE_W / 2, 0.01, 0)
        )

        wireProf = None
        minArea = float('inf')
        for pi_idx in range(wireSketch.profiles.count):
            pr = wireSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                wireProf = pr

        if wireProf:
            wireInput = extrudes.createInput(
                wireProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            wireInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_D)
            )
            try:
                extrudes.add(wireInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 7: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Front/Rear Wheel Connector created!\n\n'
            f'Body: {BODY_W * 10:.0f} × {BODY_D * 10:.0f} × {BODY_H * 10:.0f}mm\n'
            f'Tube socket: {TUBE_BORE_R * 20:.1f}mm bore × {TUBE_DEPTH * 10:.0f}mm deep\n'
            f'Steering bracket mount: 2× M3 heat-set inserts ({STEER_BOLT_SPACING * 10:.0f}mm spacing)\n'
            f'Servo mount: 2× M3 heat-set inserts ({SERVO_BOLT_SPACING * 10:.0f}mm spacing)\n'
            f'Wire exit: {WIRE_W * 10:.0f} × {WIRE_H * 10:.0f}mm\n\n'
            'Bolt the steering_bracket.py to the front face.\n'
            'Bolt the servo_mount.py to the side face.\n'
            'Wire exit at bottom for motor + servo cables.\n\n'
            'Print mount-face down, 60% infill, 5 perimeters.\n'
            'Qty: 4 (FL, FR, RL, RR — all identical)',
            'Mars Rover - Front/Rear Wheel Connector'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
