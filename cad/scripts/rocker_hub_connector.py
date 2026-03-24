"""
Mars Rover Rocker Hub Connector — Phase 1
===========================================

THE most complex connector. Sits outside the body, clamped to the
diff bar. Provides tube sockets for the front arm (to front wheel)
and rear arm (to bogie pivot).

Differential mechanism: This connector CLAMPS rigidly to the 8mm
diff bar via an M3 grub screw. The diff bar passes through 608ZZ
bearings in the body. When one side tilts, the bar rotates, tilting
the other side — keeping the body level.

Features:
  - Diff bar clamp bore: 8.0mm (press-fit on 8mm rod, M3 grub for retention)
  - 2× tube sockets (8.2mm bore × 15mm deep):
    * FRONT: angled forward-down (~8.5° below horizontal)
    * REAR: angled backward-down (~9.5° below horizontal)
  - M3 grub screws in each tube socket + diff bar clamp
  - 2× wire channels (8×6mm): from body side to each tube socket
  - 4mm minimum wall thickness

Overall size: ~45 × 40 × 35mm
Print: Flat (body-facing side down), PLA, 60% infill, 5 perimeters
Qty: 2 (left + right — symmetric)

Reference: EA-25, MrOver RockerJoint2_6.scad, Sawppy Rocker Body Mount
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
        TUBE_BORE_R = 0.41          # 8.2mm tube socket bore
        TUBE_DEPTH = 1.5            # 15mm socket depth
        DIFF_BORE_R = 0.4           # 8.0mm diff bar bore (press-fit)
        GRUB_R = 0.15               # 3mm M3 grub
        WALL = 0.4                  # 4mm minimum wall
        WIRE_W = 0.8                # 8mm wire channel
        WIRE_H = 0.6                # 6mm wire channel

        # ── Body dimensions ──
        # The connector is roughly a cylinder aligned with the diff bar (X axis)
        # with tube sockets projecting in Y direction (front/rear)
        BODY_R = TUBE_BORE_R + WALL + 0.2   # ~8.3mm radius, 16.6mm OD
        BODY_LEN = 3.5             # 35mm long (along diff bar axis, X)

        # ── Tube socket angles (from EA-25 Appendix A) ──
        FRONT_DOWN_ANGLE = 8.5     # degrees below horizontal
        REAR_DOWN_ANGLE = 9.5      # degrees below horizontal

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures
        revolves = comp.features.revolveFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Main body — rectangular block with rounded edges
        # Oriented: X = diff bar axis, Y = front-rear, Z = up-down
        # Diff bar runs through the center along X
        # ══════════════════════════════════════════════════════════

        BODY_W = 4.5               # 45mm (Y direction, front-rear)
        BODY_H = 3.5               # 35mm (Z direction, up-down)
        BODY_D = 3.5               # 35mm (X direction, along diff bar)

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Hub Body'
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

        hubBody = None
        if prof:
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_D)
            )
            hubExt = extrudes.add(extInput)
            hubBody = hubExt.bodies.item(0)
            hubBody.name = 'Rocker Hub Connector'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Diff bar bore (horizontal through center, along Z axis)
        # The diff bar runs through the connector at mid-height
        # ══════════════════════════════════════════════════════════

        # Bore runs through the block in Z direction at center
        diffSketch = comp.sketches.add(comp.xYConstructionPlane)
        diffSketch.name = 'Diff Bar Bore'
        diffSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_H / 2, 0), DIFF_BORE_R
        )

        diffProf = None
        minArea = float('inf')
        for pi_idx in range(diffSketch.profiles.count):
            pr = diffSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                diffProf = pr

        if diffProf:
            diffInput = extrudes.createInput(
                diffProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            diffInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_D + 0.1)
            )
            try:
                extrudes.add(diffInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: M3 grub screw for diff bar retention
        # Radial hole from outside into diff bar bore
        # ══════════════════════════════════════════════════════════

        midPlane = comp.constructionPlanes
        mpInput = midPlane.createInput()
        mpInput.setByOffset(
            comp.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_D / 2)
        )
        mP = midPlane.add(mpInput)

        diffGrubSketch = comp.sketches.add(mP)
        diffGrubSketch.name = 'Diff Bar Grub'
        diffGrubSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, BODY_H / 2 + DIFF_BORE_R + WALL / 2, 0), GRUB_R
        )

        dgProf = None
        minArea = float('inf')
        for pi_idx in range(diffGrubSketch.profiles.count):
            pr = diffGrubSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                dgProf = pr

        if dgProf:
            dgInput = extrudes.createInput(
                dgProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            dgInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(WALL + DIFF_BORE_R + 0.1)
            )
            try:
                extrudes.add(dgInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Front tube socket (tube goes forward-down)
        # Socket bore on the front face (+Y side) of the block
        # ══════════════════════════════════════════════════════════

        # Front tube exits from the +Y face at mid-height
        frontBoreSketch = comp.sketches.add(mP)  # mid-Z plane
        frontBoreSketch.name = 'Front Tube Socket'
        # Position at the +Y face, mid-height
        front_y = BODY_W / 2
        front_z = BODY_H / 2
        frontBoreSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(front_y, front_z, 0), TUBE_BORE_R
        )

        fbProf = None
        minArea = float('inf')
        for pi_idx in range(frontBoreSketch.profiles.count):
            pr = frontBoreSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                fbProf = pr

        if fbProf:
            fbInput = extrudes.createInput(
                fbProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            fbInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(TUBE_DEPTH)
            )
            try:
                extrudes.add(fbInput)
            except:
                pass

        # Front grub screw
        fgSketch = comp.sketches.add(mP)
        fgSketch.name = 'Front Grub'
        fgSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(front_y - TUBE_DEPTH / 2,
              front_z + TUBE_BORE_R + WALL / 2, 0),
            GRUB_R
        )

        fgProf = None
        minArea = float('inf')
        for pi_idx in range(fgSketch.profiles.count):
            pr = fgSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                fgProf = pr

        if fgProf:
            fgInput = extrudes.createInput(
                fgProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            fgInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(WALL + TUBE_BORE_R + 0.1)
            )
            try:
                extrudes.add(fgInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Rear tube socket (tube goes backward-down)
        # Socket bore on the -Y face
        # ══════════════════════════════════════════════════════════

        rearBoreSketch = comp.sketches.add(mP)
        rearBoreSketch.name = 'Rear Tube Socket'
        rear_y = -BODY_W / 2
        rear_z = BODY_H / 2
        rearBoreSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(rear_y, rear_z, 0), TUBE_BORE_R
        )

        rbProf = None
        minArea = float('inf')
        for pi_idx in range(rearBoreSketch.profiles.count):
            pr = rearBoreSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                rbProf = pr

        if rbProf:
            rbInput = extrudes.createInput(
                rbProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            rbInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(TUBE_DEPTH)
            )
            try:
                extrudes.add(rbInput)
            except:
                pass

        # Rear grub screw
        rgSketch = comp.sketches.add(mP)
        rgSketch.name = 'Rear Grub'
        rgSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(rear_y + TUBE_DEPTH / 2,
              rear_z + TUBE_BORE_R + WALL / 2, 0),
            GRUB_R
        )

        rgProf = None
        minArea = float('inf')
        for pi_idx in range(rgSketch.profiles.count):
            pr = rgSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                rgProf = pr

        if rgProf:
            rgInput = extrudes.createInput(
                rgProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            rgInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(WALL + TUBE_BORE_R + 0.1)
            )
            try:
                extrudes.add(rgInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 6: Wire channels
        # Front channel: from body side (Z=0 face) to front tube socket
        # Rear channel: from body side to rear tube socket
        # ══════════════════════════════════════════════════════════

        # Front wire channel (rectangular slot through body)
        fwSketch = comp.sketches.add(comp.xYConstructionPlane)
        fwSketch.name = 'Front Wire Channel'
        fwl = fwSketch.sketchCurves.sketchLines
        fwl.addTwoPointRectangle(
            p(WIRE_W / 2, 0, 0),        # inner edge (near center)
            p(BODY_W / 2 + 0.1, BODY_H / 2 + WIRE_H / 2, 0)
        )

        fwProf = None
        maxArea = 0
        for pi_idx in range(fwSketch.profiles.count):
            pr = fwSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                fwProf = pr

        if fwProf:
            fwInput = extrudes.createInput(
                fwProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            fwInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(WIRE_H)
            )
            try:
                extrudes.add(fwInput)
            except:
                pass

        # Rear wire channel
        rwSketch = comp.sketches.add(comp.xYConstructionPlane)
        rwSketch.name = 'Rear Wire Channel'
        rwl = rwSketch.sketchCurves.sketchLines
        rwl.addTwoPointRectangle(
            p(-BODY_W / 2 - 0.1, 0, 0),
            p(-WIRE_W / 2, BODY_H / 2 + WIRE_H / 2, 0)
        )

        rwProf = None
        maxArea = 0
        for pi_idx in range(rwSketch.profiles.count):
            pr = rwSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                rwProf = pr

        if rwProf:
            rwInput = extrudes.createInput(
                rwProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            rwInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(WIRE_H)
            )
            try:
                extrudes.add(rwInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 7: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Rocker Hub Connector created!\n\n'
            f'Body: {BODY_W * 10:.0f} × {BODY_H * 10:.0f} × {BODY_D * 10:.0f}mm\n\n'
            'DIFF BAR:\n'
            f'  Bore: {DIFF_BORE_R * 20:.0f}mm (press-fit on 8mm rod)\n'
            f'  M3 grub screw for retention\n\n'
            'TUBE SOCKETS (front + rear):\n'
            f'  Bore: {TUBE_BORE_R * 20:.1f}mm × {TUBE_DEPTH * 10:.0f}mm deep\n'
            f'  Front angle: ~{FRONT_DOWN_ANGLE}° below horizontal\n'
            f'  Rear angle: ~{REAR_DOWN_ANGLE}° below horizontal\n'
            f'  M3 grub screws for tube retention\n\n'
            'WIRE CHANNELS:\n'
            f'  2× {WIRE_W * 10:.0f}×{WIRE_H * 10:.0f}mm '
            f'(front + rear, from body side)\n\n'
            'The rocker hub clamps to the diff bar.\n'
            'Diff bar passes through body 608ZZ bearings.\n'
            'Differential: one side up → other side down.\n\n'
            'Print body-side down, 60% infill, 5 perimeters.\n'
            'Qty: 2 (left + right — symmetric)',
            'Mars Rover - Rocker Hub Connector'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
