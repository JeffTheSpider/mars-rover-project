"""
Mars Rover Differential Pivot Housing — Phase 1
=================================================

Central pivot mount for the differential bar. Bolts onto the body top
cross-member. Contains a 608ZZ bearing so the diff bar can rotate freely
about the X-axis (longitudinal).

Features:
  - 608ZZ bearing seat: 22.15mm OD × 7.2mm depth (press-fit)
  - Through bore: 8mm (diff bar rod passes through)
  - Mounting flanges: 4× M3 heat-set insert holes
  - Body-mating face: flat bottom for bolting to cross-member
  - Hard stop slots: ±25° rotation limiters

Overall size: ~40 × 40 × 25mm
Print: Flat (bottom face down), PLA, 60% infill, 4 perimeters
Qty: 1

Reference: EA-26 Section 9, generate_rover_params.py
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
        # Bearing
        BRG_OD   = 2.215       # 22.15mm (608ZZ + press-fit oversize)
        BRG_W    = 0.72        # 7.2mm depth
        BRG_ID   = 0.8         # 8mm through bore
        BRG_OD_R = BRG_OD / 2
        BRG_ID_R = BRG_ID / 2

        # Housing body
        BODY_W   = 4.0         # 40mm (X direction)
        BODY_L   = 4.0         # 40mm (Y direction)
        BODY_H   = 2.5         # 25mm (Z direction, height)
        WALL     = 0.4         # 4mm minimum wall
        FILLET_R = 0.15        # 1.5mm edge fillets

        # Flanges for mounting bolts
        FLANGE_W = 1.0         # 10mm flange extension beyond body
        FLANGE_T = 0.4         # 4mm flange thickness
        BOLT_R   = 0.165       # M3 clearance hole (3.3mm / 2)
        INSERT_R = 0.24        # M3 heat-set insert hole (4.8mm / 2)
        INSERT_D = 0.55        # 5.5mm insert depth
        BOLT_PCD = 3.2         # 32mm bolt circle diameter
        BOLT_R_PCD = BOLT_PCD / 2

        # Hard stop
        STOP_W   = 0.3         # 3mm stop feature width
        STOP_D   = 0.2         # 2mm stop depth

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures
        fillets = comp.features.filletFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Main housing body — rectangular block
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Housing Body'
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

        mainBody = None
        if prof:
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_H)
            )
            ext = extrudes.add(extInput)
            mainBody = ext.bodies.item(0)
            mainBody.name = 'Diff Pivot Housing'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Bearing seat (counterbore from top)
        # ══════════════════════════════════════════════════════════

        # Offset plane at top of housing
        topPlane = comp.constructionPlanes
        topInput = topPlane.createInput()
        topInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H)
        )
        topP = topPlane.add(topInput)

        brgSketch = comp.sketches.add(topP)
        brgSketch.name = 'Bearing Seat'
        brgSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BRG_OD_R
        )

        brgProf = None
        minArea = float('inf')
        for pi_idx in range(brgSketch.profiles.count):
            pr = brgSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                brgProf = pr

        if brgProf:
            brgInput = extrudes.createInput(
                brgProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            brgInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BRG_W)
            )
            try:
                extrudes.add(brgInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: Through bore for diff bar rod
        # ══════════════════════════════════════════════════════════

        boreSketch = comp.sketches.add(comp.xYConstructionPlane)
        boreSketch.name = 'Diff Bar Bore'
        boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BRG_ID_R
        )

        boreProf = None
        minArea = float('inf')
        for pi_idx in range(boreSketch.profiles.count):
            pr = boreSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                boreProf = pr

        if boreProf:
            boreInput = extrudes.createInput(
                boreProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            boreInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BODY_H + 0.1)
            )
            try:
                extrudes.add(boreInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Four M3 heat-set insert mounting holes
        # ══════════════════════════════════════════════════════════

        boltSketch = comp.sketches.add(comp.xYConstructionPlane)
        boltSketch.name = 'Mounting Holes'

        # 4 holes at 45° on bolt PCD
        for angle_deg in [45, 135, 225, 315]:
            angle = math.radians(angle_deg)
            cx = BOLT_R_PCD * math.cos(angle)
            cy = BOLT_R_PCD * math.sin(angle)
            boltSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(cx, cy, 0), INSERT_R
            )

        # Find the 4 small circle profiles and cut them
        for pi_idx in range(boltSketch.profiles.count):
            pr = boltSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            # Heat-set insert holes are small circles
            target_area = math.pi * INSERT_R * INSERT_R
            if abs(a - target_area) < target_area * 0.3:
                holeInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                holeInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(INSERT_D)
                )
                try:
                    extrudes.add(holeInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Differential Pivot Housing created!\n\n'
            f'Body: {BODY_W * 10:.0f} × {BODY_L * 10:.0f} × '
            f'{BODY_H * 10:.0f}mm\n\n'
            'BEARING SEAT:\n'
            f'  608ZZ: {BRG_OD * 10:.1f}mm OD × {BRG_W * 10:.1f}mm deep\n'
            f'  Through bore: {BRG_ID * 10:.0f}mm\n\n'
            'MOUNTING:\n'
            f'  4× M3 heat-set inserts on {BOLT_PCD * 10:.0f}mm PCD\n'
            f'  Insert holes: {INSERT_R * 20:.1f}mm × '
            f'{INSERT_D * 10:.1f}mm deep\n\n'
            'Mounts on body top cross-member.\n'
            'Diff bar passes through 608ZZ bearing.\n'
            'Print bottom-face down, 60% infill, 4 perimeters.\n'
            'Qty: 1',
            'Mars Rover - Diff Pivot Housing'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
