"""
*** DEPRECATED — See EA-25 ***
Replaced by tube+connector approach: 8mm steel rods + rocker_hub_connector.py
+ front_wheel_connector.py. This script retained for dimension reference only.

Mars Rover Rocker Arm — Phase 1 (0.4 Scale) — TWO-PIECE SPLIT
===============================================================

Main suspension arm connecting the body (via differential bar) to the
front wheel and bogie pivot. Each rocker spans from the bogie pivot
(rear) through the body pivot to the front wheel.

Full span: ~270mm (bogie pivot Y=-90mm to front wheel Y=+180mm)
Cross-section: 20mm wide × 15mm tall (hollow rectangular tube)

** SPLIT INTO 2 PIECES ** because 270mm exceeds CTC Bizer bed (225mm).
  - Front half: body pivot (Y=0) to front wheel (Y=+180mm) = ~195mm with joint
  - Rear half: bogie pivot (Y=-90mm) to body pivot (Y=0) = ~105mm with joint
  - Half-lap joint at Y=0 with 2× M3 bolts
  - Both halves share the M8 body pivot bolt

Features:
  - Body pivot boss (608ZZ bearing seat, at Y=0) — on both halves
  - Bogie pivot boss (608ZZ bearing seat, at Y=-90mm) — rear half
  - Front motor mount face (at Y=+180mm) — front half
  - Servo mount tab (near front, for SG90 steering servo) — front half
  - Half-lap joint with 2× M3 bolt holes at Y=0

Qty: 4 total (2 front halves + 2 rear halves, left/right mirrors)

Print orientation: Flat (20mm face down)
Supports: Minimal (joint step may need support)
Perimeters: 4
Infill: 50% gyroid

Reference: EA-01, EA-08 s4.3, EA-20
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
        # Rocker spans from bogie pivot to front wheel
        # Body pivot at Y=0, bogie pivot at Y=-9cm, front wheel at Y=+18cm
        REAR_Y = -9.0           # bogie pivot position
        FRONT_Y = 18.0          # front wheel position
        TOTAL_LEN = FRONT_Y - REAR_Y  # 27cm = 270mm
        ARM_W = 2.0             # 20mm width
        ARM_H = 1.5             # 15mm height
        WALL = 0.3              # 3mm wall thickness

        # Body pivot boss (at Y=0, shared by both halves)
        BODY_PIVOT_BOSS_R = 1.5   # 15mm radius (30mm OD)
        BEARING_SEAT_R = 1.1075   # 22.15mm dia
        BEARING_SEAT_DEPTH = 0.72 # 7.2mm
        PIVOT_BORE_R = 0.4        # 8mm dia

        # Bogie pivot boss (at Y=-9cm, rear half only)
        BOGIE_PIVOT_BOSS_R = 1.5  # 15mm radius (30mm OD, matches body pivot boss wall thickness)

        # Half-lap joint at Y=0
        LAP_LEN = 1.5            # 15mm overlap each direction
        LAP_HALF_H = ARM_H / 2   # Half arm height for lap step
        M3_HOLE_R = 0.165        # 3.3mm dia (M3 clearance)
        M3_HOLE_SPACING = 1.0    # 10mm between M3 bolt holes

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════════
        # FRONT HALF: Y = -LAP_LEN (joint overlap) to Y = +FRONT_Y
        # ══════════════════════════════════════════════════════════════

        # Step 1a: Front half main arm body
        frontSketch = comp.sketches.add(comp.xYConstructionPlane)
        frontSketch.name = 'Front Half Outer'
        fl = frontSketch.sketchCurves.sketchLines
        fl.addTwoPointRectangle(
            p(-ARM_W / 2, -LAP_LEN, 0),
            p(ARM_W / 2, FRONT_Y, 0)
        )

        outerProf = None
        maxArea = 0
        for pi in range(frontSketch.profiles.count):
            pr = frontSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                outerProf = pr

        frontBody = None
        if outerProf:
            extInput = extrudes.createInput(
                outerProf,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(ARM_H)
            )
            ext = extrudes.add(extInput)
            frontBody = ext.bodies.item(0)
            frontBody.name = 'Rocker Front Half'

        # Step 2a: Hollow out front half interior
        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(ARM_H)
        )
        topP = topPlane.add(tpInput)

        fHollowSketch = comp.sketches.add(topP)
        fHollowSketch.name = 'Front Hollow'
        fhl = fHollowSketch.sketchCurves.sketchLines
        inner_w_half = ARM_W / 2 - WALL
        fhl.addTwoPointRectangle(
            p(-inner_w_half, -LAP_LEN + WALL, 0),
            p(inner_w_half, FRONT_Y - WALL, 0)
        )

        hProf = None
        minArea = float('inf')
        for pi in range(fHollowSketch.profiles.count):
            pr = fHollowSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                hProf = pr

        if hProf:
            hollowInput = extrudes.createInput(
                hProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            hollowInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(ARM_H - WALL)
            )
            extrudes.add(hollowInput)

        # Step 3a: Body pivot boss on front half (at Y=0)
        fBossSketch = comp.sketches.add(comp.xYConstructionPlane)
        fBossSketch.name = 'Front Body Pivot Boss'
        fBossSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BODY_PIVOT_BOSS_R
        )

        bProf = None
        minArea = float('inf')
        for pi in range(fBossSketch.profiles.count):
            pr = fBossSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                bProf = pr

        if bProf:
            bossInput = extrudes.createInput(
                bProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            bossInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(ARM_H)
            )
            extrudes.add(bossInput)

        # Step 4a: Half-lap step on front half (cut upper half for Y < 0)
        # The front half keeps the LOWER half in the joint zone (Y = -LAP_LEN to 0)
        # Cut away the upper half from Y=-LAP_LEN to Y=0
        halfPlane = comp.constructionPlanes
        hpInput = halfPlane.createInput()
        hpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(LAP_HALF_H)
        )
        halfP = halfPlane.add(hpInput)

        lapCutSketch = comp.sketches.add(topP)
        lapCutSketch.name = 'Front Lap Cut'
        lcl = lapCutSketch.sketchCurves.sketchLines
        # Cut rectangle covers the joint overlap zone
        cut_w = ARM_W / 2 + 0.5  # Wider than arm to ensure full cut
        lcl.addTwoPointRectangle(
            p(-cut_w, -LAP_LEN - 0.1, 0),
            p(cut_w, 0, 0)
        )

        lcProf = None
        maxArea = 0
        for pi in range(lapCutSketch.profiles.count):
            pr = lapCutSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                lcProf = pr

        if lcProf:
            lcInput = extrudes.createInput(
                lcProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            lcInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(LAP_HALF_H)
            )
            extrudes.add(lcInput)

        # Step 5a: Bearing seat on front half (from top at Y=0)
        fSeatSketch = comp.sketches.add(topP)
        fSeatSketch.name = 'Front Bearing Seat'
        fSeatSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BEARING_SEAT_R
        )

        sProf = None
        minArea = float('inf')
        for pi in range(fSeatSketch.profiles.count):
            pr = fSeatSketch.profiles.item(pi)
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

        # Step 6a: 8mm pivot bore through front half at Y=0
        fBoreSketch = comp.sketches.add(topP)
        fBoreSketch.name = 'Front Pivot Bore'
        fBoreSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), PIVOT_BORE_R
        )

        boreProf = None
        minArea = float('inf')
        for pi in range(fBoreSketch.profiles.count):
            pr = fBoreSketch.profiles.item(pi)
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

        # Step 7a: M3 bolt holes in front half joint zone
        for hole_y in [-M3_HOLE_SPACING / 2, M3_HOLE_SPACING / 2]:
            hSketch = comp.sketches.add(topP)
            hSketch.name = f'Front M3 Hole'
            hSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(0, hole_y, 0), M3_HOLE_R
            )

            mProf = None
            minArea = float('inf')
            for pi in range(hSketch.profiles.count):
                pr = hSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    mProf = pr

            if mProf:
                mInput = extrudes.createInput(
                    mProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                mInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(ARM_H + 0.1)
                )
                try:
                    extrudes.add(mInput)
                except:
                    pass

        # Step 8a: Servo mount tab on front half (near front end)
        SERVO_Y = FRONT_Y - 3.0  # 30mm from front end
        SERVO_TAB_L = 3.5        # 35mm long
        SERVO_TAB_W = 0.5        # 5mm extension outward
        SERVO_TAB_H = ARM_H      # same height as arm

        tabSketch = comp.sketches.add(comp.xYConstructionPlane)
        tabSketch.name = 'Servo Mount Tab'
        tl = tabSketch.sketchCurves.sketchLines
        tl.addTwoPointRectangle(
            p(ARM_W / 2, SERVO_Y - SERVO_TAB_L / 2, 0),
            p(ARM_W / 2 + SERVO_TAB_W, SERVO_Y + SERVO_TAB_L / 2, 0)
        )

        tProf = None
        minArea = float('inf')
        for pi in range(tabSketch.profiles.count):
            pr = tabSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                tProf = pr

        if tProf:
            tabInput = extrudes.createInput(
                tProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            tabInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(SERVO_TAB_H)
            )
            try:
                extrudes.add(tabInput)
            except:
                pass

        # Step 8b: M3 bolt holes in servo tab for servo mount attachment
        SERVO_BOLT_SPACING = 2.0  # 20mm between holes
        for sby in [SERVO_Y - SERVO_BOLT_SPACING / 2,
                     SERVO_Y + SERVO_BOLT_SPACING / 2]:
            stbSketch = comp.sketches.add(topP)
            stbSketch.name = 'Servo Tab Bolt'
            stbSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(ARM_W / 2 + SERVO_TAB_W / 2, sby, 0), M3_HOLE_R
            )

            stbProf = None
            minArea = float('inf')
            for pi in range(stbSketch.profiles.count):
                pr = stbSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    stbProf = pr

            if stbProf:
                stbInput = extrudes.createInput(
                    stbProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                stbInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(SERVO_TAB_H + 0.1)
                )
                try:
                    extrudes.add(stbInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # REAR HALF: Y = REAR_Y to Y = +LAP_LEN (joint overlap)
        # Offset in X by 5cm so both halves are visible side-by-side
        # ══════════════════════════════════════════════════════════════

        OFFSET_X = 5.0  # 50mm gap between the two pieces in the design

        # Step 1b: Rear half main arm body
        rearSketch = comp.sketches.add(comp.xYConstructionPlane)
        rearSketch.name = 'Rear Half Outer'
        rl = rearSketch.sketchCurves.sketchLines
        rl.addTwoPointRectangle(
            p(OFFSET_X - ARM_W / 2, REAR_Y, 0),
            p(OFFSET_X + ARM_W / 2, LAP_LEN, 0)
        )

        rOuterProf = None
        maxArea = 0
        for pi in range(rearSketch.profiles.count):
            pr = rearSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                rOuterProf = pr

        rearBody = None
        if rOuterProf:
            extInput = extrudes.createInput(
                rOuterProf,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(ARM_H)
            )
            ext = extrudes.add(extInput)
            rearBody = ext.bodies.item(0)
            rearBody.name = 'Rocker Rear Half'

        # Step 2b: Hollow out rear half
        rHollowSketch = comp.sketches.add(topP)
        rHollowSketch.name = 'Rear Hollow'
        rhl = rHollowSketch.sketchCurves.sketchLines
        rhl.addTwoPointRectangle(
            p(OFFSET_X - inner_w_half, REAR_Y + WALL, 0),
            p(OFFSET_X + inner_w_half, LAP_LEN - WALL, 0)
        )

        rhProf = None
        minArea = float('inf')
        for pi in range(rHollowSketch.profiles.count):
            pr = rHollowSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                rhProf = pr

        if rhProf:
            rhInput = extrudes.createInput(
                rhProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            rhInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(ARM_H - WALL)
            )
            extrudes.add(rhInput)

        # Step 3b: Bogie pivot boss on rear half (at Y=-9cm)
        rBossSketch = comp.sketches.add(comp.xYConstructionPlane)
        rBossSketch.name = 'Rear Bogie Pivot Boss'
        rBossSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(OFFSET_X, REAR_Y, 0), BOGIE_PIVOT_BOSS_R
        )

        rbProf = None
        minArea = float('inf')
        for pi in range(rBossSketch.profiles.count):
            pr = rBossSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                rbProf = pr

        if rbProf:
            rbInput = extrudes.createInput(
                rbProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            rbInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(ARM_H)
            )
            extrudes.add(rbInput)

        # Step 3b2: Body pivot boss on rear half (at Y=0)
        rBodyBossSketch = comp.sketches.add(comp.xYConstructionPlane)
        rBodyBossSketch.name = 'Rear Body Pivot Boss'
        rBodyBossSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(OFFSET_X, 0, 0), BODY_PIVOT_BOSS_R
        )

        rb2Prof = None
        minArea = float('inf')
        for pi in range(rBodyBossSketch.profiles.count):
            pr = rBodyBossSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                rb2Prof = pr

        if rb2Prof:
            rb2Input = extrudes.createInput(
                rb2Prof, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            rb2Input.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(ARM_H)
            )
            extrudes.add(rb2Input)

        # Step 4b: Half-lap step on rear half (cut LOWER half for Y > 0)
        # The rear half keeps the UPPER half in the joint zone (Y = 0 to LAP_LEN)
        # Cut away the lower half from Y=0 to Y=+LAP_LEN
        rLapSketch = comp.sketches.add(comp.xYConstructionPlane)
        rLapSketch.name = 'Rear Lap Cut'
        rll = rLapSketch.sketchCurves.sketchLines
        rll.addTwoPointRectangle(
            p(OFFSET_X - cut_w, 0, 0),
            p(OFFSET_X + cut_w, LAP_LEN + 0.1, 0)
        )

        rlProf = None
        maxArea = 0
        for pi in range(rLapSketch.profiles.count):
            pr = rLapSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                rlProf = pr

        if rlProf:
            rlInput = extrudes.createInput(
                rlProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            rlInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(LAP_HALF_H)
            )
            extrudes.add(rlInput)

        # Step 5b: Bearing seats on rear half (bogie pivot + body pivot)
        for pivot_y, seat_name in [(REAR_Y, 'Rear Bogie Bearing Seat'),
                                    (0, 'Rear Body Bearing Seat')]:
            seatSketch = comp.sketches.add(topP)
            seatSketch.name = seat_name
            seatSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(OFFSET_X, pivot_y, 0), BEARING_SEAT_R
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
                try:
                    extrudes.add(seatInput)
                except:
                    pass

        # Step 6b: 8mm pivot bores through rear half (both pivots)
        for pivot_y, bore_name in [(REAR_Y, 'Rear Bogie Bore'),
                                    (0, 'Rear Body Bore')]:
            boreSketch = comp.sketches.add(topP)
            boreSketch.name = bore_name
            boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(OFFSET_X, pivot_y, 0), PIVOT_BORE_R
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
                try:
                    extrudes.add(boreInput)
                except:
                    pass

        # Step 7b: M3 bolt holes in rear half joint zone
        for hole_y in [-M3_HOLE_SPACING / 2, M3_HOLE_SPACING / 2]:
            hSketch = comp.sketches.add(topP)
            hSketch.name = f'Rear M3 Hole'
            hSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(OFFSET_X, hole_y, 0), M3_HOLE_R
            )

            mProf = None
            minArea = float('inf')
            for pi in range(hSketch.profiles.count):
                pr = hSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    mProf = pr

            if mProf:
                mInput = extrudes.createInput(
                    mProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                mInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(ARM_H + 0.1)
                )
                try:
                    extrudes.add(mInput)
                except:
                    pass

        # ── Zoom and report ──
        app.activeViewport.fit()

        front_len = (FRONT_Y + LAP_LEN) * 10
        rear_len = (-REAR_Y + LAP_LEN) * 10

        ui.messageBox(
            'Rocker Arm (TWO-PIECE) created!\n\n'
            f'Total span: {TOTAL_LEN * 10:.0f}mm '
            f'(rear Y={REAR_Y * 10:.0f}mm to front Y={FRONT_Y * 10:.0f}mm)\n\n'
            f'FRONT HALF: {front_len:.0f}mm '
            f'(Y={-LAP_LEN * 10:.0f}mm to Y={FRONT_Y * 10:.0f}mm)\n'
            f'REAR HALF: {rear_len:.0f}mm '
            f'(Y={REAR_Y * 10:.0f}mm to Y={LAP_LEN * 10:.0f}mm)\n\n'
            f'Half-lap joint: {LAP_LEN * 20:.0f}mm overlap at Y=0\n'
            f'Joint bolts: 2× M3 (spacing {M3_HOLE_SPACING * 10:.0f}mm)\n\n'
            f'Cross-section: {ARM_W * 10:.0f} × {ARM_H * 10:.0f}mm\n'
            f'Wall thickness: {WALL * 10:.1f}mm\n'
            f'Body pivot boss: {BODY_PIVOT_BOSS_R * 20:.0f}mm OD (on both halves)\n'
            f'Bogie pivot boss: {BOGIE_PIVOT_BOSS_R * 20:.0f}mm OD (rear half, wall={BOGIE_PIVOT_BOSS_R * 10 - BEARING_SEAT_R * 10:.1f}mm)\n'
            f'Bearing seats: {BEARING_SEAT_R * 20:.2f}mm × '
            f'{BEARING_SEAT_DEPTH * 10:.1f}mm deep\n'
            f'Pivot bores: {PIVOT_BORE_R * 20:.0f}mm through\n\n'
            f'Both halves fit CTC Bizer bed (225mm): '
            f'front={front_len:.0f}mm, rear={rear_len:.0f}mm\n\n'
            'Qty needed: 4 pieces (2 front + 2 rear)\n'
            'Assembly: slide halves onto M8 body pivot bolt, '
            'align lap joint, secure with 2× M3 bolts.',
            'Mars Rover - Rocker Arm (Split)'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
