"""
*** DEPRECATED — See EA-25 ***
Replaced by tube+connector approach: 8mm steel rods + bogie_pivot_connector.py
+ middle/rear_wheel_connector.py. This script retained for dimension reference only.

Mars Rover Bogie Arm — Phase 1 (0.4 Scale)
=============================================

Structural arm connecting middle and rear wheels on each side.
Pivots on the rocker arm via a 608ZZ bearing.

Length: 180mm total (90mm each side of pivot, corrected from original 120mm)
Cross-section: 15mm wide × 12mm tall (hollow rectangular tube, 3mm walls)

GEOMETRY:
  Full scale bogie = 450mm. At 0.4 scale = 180mm.
  Bogie pivot is at Y=-90mm on the rocker. Each bogie arm extends
  90mm from pivot, so total span = 180mm. We build each arm as 90mm.
  The two arms are joined at the pivot boss.

Qty: 2 (left, right — mirror of each other)

Print orientation: Flat (15mm face down)
Supports: None
Perimeters: 4
Infill: 50% gyroid

Reference: EA-01, EA-08, EA-20
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
        # Full arm span: pivot to each wheel = 90mm = 9.0cm
        ARM_HALF_LEN = 9.0      # 90mm each side of pivot
        ARM_W = 1.5             # 15mm width
        ARM_H = 1.2             # 12mm height
        WALL = 0.3              # 3mm wall thickness (increased from 2.5mm, matches rocker arm)

        # Pivot boss (centre, 608ZZ bearing seat)
        PIVOT_BOSS_OD_R = 1.5   # 15mm radius (30mm OD boss around bearing)
        PIVOT_BOSS_H = 1.2      # 12mm (matches arm height)
        BEARING_SEAT_R = 1.1075 # 22.15mm dia
        BEARING_SEAT_DEPTH = 0.72  # 7.2mm
        PIVOT_BORE_R = 0.4      # 8mm dia through-hole

        # Motor mount faces at each end
        MOTOR_MOUNT_W = 1.6     # 16mm motor mount face width
        MOTOR_MOUNT_H = 1.4     # 14mm motor mount face height
        MOTOR_CLIP_W = 0.61     # 6.1mm half (12.2mm clip inner)
        MOTOR_CLIP_H = 0.51     # 5.1mm half (10.2mm clip inner)
        MOTOR_CLIP_DEPTH = 2.5  # 25mm motor body length pocket

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════════════
        # Step 1: Main arm body (rectangular tube along Y-axis)
        # Oriented: X=width, Y=length, Z=height
        # ══════════════════════════════════════════════════════════════

        TOTAL_LEN = ARM_HALF_LEN * 2  # 180mm total span

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Bogie Arm Outer'
        lines = sketch1.sketchCurves.sketchLines

        # Outer rectangle
        lines.addTwoPointRectangle(
            p(-ARM_W / 2, -ARM_HALF_LEN, 0),
            p(ARM_W / 2, ARM_HALF_LEN, 0)
        )

        # Get outer profile (largest area)
        outerProf = None
        maxArea = 0
        for pi in range(sketch1.profiles.count):
            pr = sketch1.profiles.item(pi)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                outerProf = pr

        extrudes = comp.features.extrudeFeatures

        if outerProf:
            extInput = extrudes.createInput(
                outerProf,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(ARM_H)
            )
            ext = extrudes.add(extInput)
            body = ext.bodies.item(0)
            body.name = 'Bogie Arm'

        # ══════════════════════════════════════════════════════════════
        # Step 2: Hollow out interior (cut pocket from top)
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(ARM_H)
        )
        topP = topPlane.add(tpInput)

        hollowSketch = comp.sketches.add(topP)
        hollowSketch.name = 'Hollow Interior'
        hl = hollowSketch.sketchCurves.sketchLines

        # Inner rectangle (wall thickness inset)
        inner_w_half = ARM_W / 2 - WALL
        inner_len_half = ARM_HALF_LEN - WALL
        hl.addTwoPointRectangle(
            p(-inner_w_half, -inner_len_half, 0),
            p(inner_w_half, inner_len_half, 0)
        )

        # Find smallest profile
        hProf = None
        minArea = float('inf')
        for pi in range(hollowSketch.profiles.count):
            pr = hollowSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                hProf = pr

        if hProf:
            hollowInput = extrudes.createInput(
                hProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            # Cut through most of the height, leaving bottom wall
            hollowInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(ARM_H - WALL)
            )
            extrudes.add(hollowInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: Pivot boss at centre (cylindrical thickening)
        # The boss is wider than the arm to provide bearing seat
        # ══════════════════════════════════════════════════════════════

        bossSketch = comp.sketches.add(comp.xYConstructionPlane)
        bossSketch.name = 'Pivot Boss'
        bossSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), PIVOT_BOSS_OD_R
        )

        # Find circle profile (smallest area)
        bProf = None
        minArea = float('inf')
        for pi in range(bossSketch.profiles.count):
            pr = bossSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                bProf = pr

        if bProf:
            bossInput = extrudes.createInput(
                bProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            bossInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(PIVOT_BOSS_H)
            )
            extrudes.add(bossInput)

        # ══════════════════════════════════════════════════════════════
        # Step 4: Bearing seat cut into boss (from top)
        # ══════════════════════════════════════════════════════════════

        seatSketch = comp.sketches.add(topP)
        seatSketch.name = 'Bearing Seat'
        seatSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BEARING_SEAT_R
        )

        sProf = None
        minArea = float('inf')
        for pi in range(seatSketch.profiles.count):
            pr = seatSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                sProf = pr

        if sProf:
            seatInput = extrudes.createInput(
                sProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            seatInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(BEARING_SEAT_DEPTH)
            )
            extrudes.add(seatInput)

        # ══════════════════════════════════════════════════════════════
        # Step 5: 8mm pivot bore through entire height
        # ══════════════════════════════════════════════════════════════

        boreSketch = comp.sketches.add(topP)
        boreSketch.name = 'Pivot Bore'
        boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), PIVOT_BORE_R
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
                True, adsk.core.ValueInput.createByReal(ARM_H + 0.1)
            )
            extrudes.add(boreInput)

        # ══════════════════════════════════════════════════════════════
        # Step 6: Motor clip pockets at each end (Y=+90mm and Y=-90mm)
        # Rectangular pockets for N20 motor snap-fit
        # Cut from top of arm, motor sits transverse (shaft along X)
        # ══════════════════════════════════════════════════════════════

        for end_y, suffix in [(ARM_HALF_LEN - MOTOR_CLIP_DEPTH / 2 - WALL,
                               'Front'),
                              (-ARM_HALF_LEN + MOTOR_CLIP_DEPTH / 2 + WALL,
                               'Rear')]:
            mSketch = comp.sketches.add(topP)
            mSketch.name = f'Motor Pocket {suffix}'
            ml = mSketch.sketchCurves.sketchLines
            ml.addTwoPointRectangle(
                p(-MOTOR_CLIP_W, end_y - MOTOR_CLIP_DEPTH / 2, 0),
                p(MOTOR_CLIP_W, end_y + MOTOR_CLIP_DEPTH / 2, 0)
            )

            mProf = None
            minArea = float('inf')
            for pi in range(mSketch.profiles.count):
                pr = mSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    mProf = pr

            if mProf:
                mInput = extrudes.createInput(
                    mProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                mInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(ARM_H - WALL)
                )
                try:
                    extrudes.add(mInput)
                except:
                    pass  # May fail if overlapping hollow

        # ══════════════════════════════════════════════════════════════
        # Step 7: Wire routing slot alongside pivot boss
        # 5mm wide channel through boss wall for motor/sensor cables
        # ══════════════════════════════════════════════════════════════

        WIRE_SLOT_W = 0.5    # 5mm wide
        WIRE_SLOT_H = 0.4    # 4mm tall

        wireSketch = comp.sketches.add(topP)
        wireSketch.name = 'Wire Slot'
        # Slot adjacent to the boss, along the arm axis
        wireSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-ARM_W / 2 - 0.01, -WIRE_SLOT_W / 2, 0),
            p(-ARM_W / 2 + WIRE_SLOT_H, WIRE_SLOT_W / 2, 0)
        )

        for pi in range(wireSketch.profiles.count):
            pr = wireSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.5:
                wsInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                wsInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(ARM_H * 0.6)
                )
                try:
                    extrudes.add(wsInput)
                except:
                    pass

        # ── Zoom and report ──
        app.activeViewport.fit()

        ui.messageBox(
            'Bogie Arm created!\n\n'
            f'Total span: {ARM_HALF_LEN * 20:.0f}mm '
            f'(pivot to wheel: {ARM_HALF_LEN * 10:.0f}mm each side)\n'
            f'Cross-section: {ARM_W * 10:.0f} × {ARM_H * 10:.0f}mm\n'
            f'Wall thickness: {WALL * 10:.1f}mm\n'
            f'Pivot boss: {PIVOT_BOSS_OD_R * 20:.0f}mm OD\n'
            f'Bearing seat: {BEARING_SEAT_R * 20:.2f}mm × '
            f'{BEARING_SEAT_DEPTH * 10:.1f}mm deep\n'
            f'Pivot bore: {PIVOT_BORE_R * 20:.0f}mm through\n'
            f'Wire slot: {WIRE_SLOT_W * 10:.0f} × {WIRE_SLOT_H * 10:.0f}mm\n\n'
            'Qty needed: 2 (left, right)\n'
            'Print flat (15mm face down), 50% infill.',
            'Mars Rover - Bogie Arm'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
