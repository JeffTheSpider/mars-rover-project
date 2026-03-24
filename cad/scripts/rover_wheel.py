"""
Mars Rover Wheel — Phase 1 (0.4 Scale)
=======================================

80mm OD × 32mm wide PLA wheel rim with:
- Hub with 3.1mm D-shaft bore for N20 motor
- M2 grub screw hole for shaft retention
- 6 spoke lightening holes (Curiosity-style, saves ~15g per wheel)
- 1.5mm rim retention lips on both faces (holds TPU tire)

Two operating modes controlled by USE_TPU_TIRE flag:
  True  → Rim only (smooth OD, lips for TPU tire press-fit)
  False → Standalone wheel with 3× O-ring grooves + 12 grousers

Print orientation: Hub face down (flat on bed)
Material: PLA
Supports: None needed
Infill: 50% gyroid (structural)
Perimeters: 4

Quantity needed: 6 wheels

Reference: EA-08 Section 7, generate_rover_params.py
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
            ui.messageBox('No active design. Create or open a design first.')
            return

        # ── Mode Toggle ──
        USE_TPU_TIRE = True  # True = rim only (for TPU tire), False = O-rings + grousers

        # ── Parameters (cm — Fusion API unit) ──
        WHEEL_R = 4.0           # 40mm radius (80mm OD)
        WHEEL_W = 3.2           # 32mm width
        HUB_R = 0.5             # 5mm radius (10mm OD hub boss)
        HUB_LEN = 0.8           # 8mm hub boss length (shaft engagement)
        SHAFT_R = 0.155         # 1.55mm radius (3.1mm bore)
        D_FLAT_DEPTH = 0.05     # 0.5mm D-flat depth
        DISC_THICK = 0.3        # 3mm disc thickness (solid web)
        RIM_THICK = 0.25        # 2.5mm rim wall thickness
        RIM_INNER_R = WHEEL_R - RIM_THICK

        # Rim retention lips (TPU tire mode)
        LIP_H = 0.15           # 1.5mm lip height above rim face
        LIP_W = 0.2            # 2mm lip width (radial)

        # Spoke lightening holes
        SPOKE_COUNT = 6         # 6 holes (Curiosity-style)
        SPOKE_HOLE_R_POS = 2.5  # 25mm from axis (radial position of hole centre)
        SPOKE_HOLE_LONG = 0.6   # 12mm semi-major (along circumference)
        SPOKE_HOLE_SHORT = 0.3  # 6mm semi-minor (radial direction)

        # O-ring grooves (fallback mode)
        GROUSER_DEPTH = 0.3     # 3mm grouser height
        GROUSER_WIDTH = 0.3     # 3mm grouser width
        GROUSER_COUNT = 12
        ORING_GROOVE_W = 0.35   # 3.5mm groove width
        ORING_GROOVE_D = 0.2    # 2mm groove depth
        ORING_COUNT = 3

        # Grub screw
        GRUB_R = 0.1            # M2 (2mm dia)
        GRUB_DEPTH = 0.5        # 5mm deep

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════════
        # STEP 1: Create main wheel body via revolve
        # Sketch on XZ plane, revolve around Y axis
        # ══════════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Wheel Cross Section'
        lines = sketch.sketchCurves.sketchLines

        pts = [
            (SHAFT_R, 0),
            (WHEEL_R, 0),
            (WHEEL_R, WHEEL_W),
            (SHAFT_R, WHEEL_W),
        ]

        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            lines.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        axis = lines.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
        axis.isConstruction = True

        profile = sketch.profiles.item(0)
        revolves = comp.features.revolveFeatures
        revInput = revolves.createInput(
            profile, axis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        revInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        wheelRev = revolves.add(revInput)

        wheelBody = wheelRev.bodies.item(0)
        wheelBody.name = 'Wheel'

        # ══════════════════════════════════════════════════════════════
        # STEP 2: Rim retention lips (both faces) — TPU tire mode
        # 1.5mm raised lip on each face at the outer rim edge
        # ══════════════════════════════════════════════════════════════

        if USE_TPU_TIRE:
            # Lip on face 1 (Y=0 side)
            lip1Sketch = comp.sketches.add(comp.xZConstructionPlane)
            lip1Sketch.name = 'Rim Lip Face 1'
            ll = lip1Sketch.sketchCurves.sketchLines
            lip_r_inner = WHEEL_R - LIP_W
            lip_r_outer = WHEEL_R
            ll.addByTwoPoints(p(lip_r_inner, -LIP_H, 0), p(lip_r_outer, -LIP_H, 0))
            ll.addByTwoPoints(p(lip_r_outer, -LIP_H, 0), p(lip_r_outer, 0, 0))
            ll.addByTwoPoints(p(lip_r_outer, 0, 0), p(lip_r_inner, 0, 0))
            ll.addByTwoPoints(p(lip_r_inner, 0, 0), p(lip_r_inner, -LIP_H, 0))

            lipAxis1 = ll.addByTwoPoints(p(0, -LIP_H, 0), p(0, 0, 0))
            lipAxis1.isConstruction = True

            lipProf1 = lip1Sketch.profiles.item(0)
            lipRev1 = revolves.createInput(
                lipProf1, lipAxis1,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            lipRev1.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
            try:
                revolves.add(lipRev1)
            except:
                pass

            # Lip on face 2 (Y=WHEEL_W side)
            lip2Sketch = comp.sketches.add(comp.xZConstructionPlane)
            lip2Sketch.name = 'Rim Lip Face 2'
            ll2 = lip2Sketch.sketchCurves.sketchLines
            ll2.addByTwoPoints(p(lip_r_inner, WHEEL_W, 0), p(lip_r_outer, WHEEL_W, 0))
            ll2.addByTwoPoints(p(lip_r_outer, WHEEL_W, 0), p(lip_r_outer, WHEEL_W + LIP_H, 0))
            ll2.addByTwoPoints(p(lip_r_outer, WHEEL_W + LIP_H, 0), p(lip_r_inner, WHEEL_W + LIP_H, 0))
            ll2.addByTwoPoints(p(lip_r_inner, WHEEL_W + LIP_H, 0), p(lip_r_inner, WHEEL_W, 0))

            lipAxis2 = ll2.addByTwoPoints(p(0, WHEEL_W, 0), p(0, WHEEL_W + LIP_H, 0))
            lipAxis2.isConstruction = True

            lipProf2 = lip2Sketch.profiles.item(0)
            lipRev2 = revolves.createInput(
                lipProf2, lipAxis2,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            lipRev2.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
            try:
                revolves.add(lipRev2)
            except:
                pass

        # ══════════════════════════════════════════════════════════════
        # STEP 2b: O-ring grooves (fallback mode only)
        # ══════════════════════════════════════════════════════════════

        if not USE_TPU_TIRE:
            groove_spacing = WHEEL_W / (ORING_COUNT + 1)
            for gi in range(ORING_COUNT):
                gy = groove_spacing * (gi + 1)
                grooveSketch = comp.sketches.add(comp.xZConstructionPlane)
                grooveSketch.name = f'O-Ring Groove {gi + 1}'
                gl = grooveSketch.sketchCurves.sketchLines

                g_y1 = gy - ORING_GROOVE_W / 2
                g_y2 = gy + ORING_GROOVE_W / 2
                g_r_outer = WHEEL_R
                g_r_inner = WHEEL_R - ORING_GROOVE_D

                gl.addByTwoPoints(p(g_r_inner, g_y1, 0), p(g_r_outer, g_y1, 0))
                gl.addByTwoPoints(p(g_r_outer, g_y1, 0), p(g_r_outer, g_y2, 0))
                gl.addByTwoPoints(p(g_r_outer, g_y2, 0), p(g_r_inner, g_y2, 0))
                gl.addByTwoPoints(p(g_r_inner, g_y2, 0), p(g_r_inner, g_y1, 0))

                gAxis = gl.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
                gAxis.isConstruction = True

                gProfile = grooveSketch.profiles.item(0)
                gRevInput = revolves.createInput(
                    gProfile, gAxis,
                    adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                gRevInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
                revolves.add(gRevInput)

        # ══════════════════════════════════════════════════════════════
        # STEP 3: Grousers (fallback mode only)
        # ══════════════════════════════════════════════════════════════

        if not USE_TPU_TIRE:
            grouserSketch = comp.sketches.add(comp.xZConstructionPlane)
            grouserSketch.name = 'Grouser'
            grl = grouserSketch.sketchCurves.sketchLines

            gr_inner = WHEEL_R - 0.01
            gr_outer = WHEEL_R + GROUSER_DEPTH

            grl.addByTwoPoints(p(gr_inner, 0, 0), p(gr_outer, 0, 0))
            grl.addByTwoPoints(p(gr_outer, 0, 0), p(gr_outer, WHEEL_W, 0))
            grl.addByTwoPoints(p(gr_outer, WHEEL_W, 0), p(gr_inner, WHEEL_W, 0))
            grl.addByTwoPoints(p(gr_inner, WHEEL_W, 0), p(gr_inner, 0, 0))

            grAxis = grl.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
            grAxis.isConstruction = True

            grProfile = grouserSketch.profiles.item(0)
            grouser_angle = GROUSER_WIDTH / WHEEL_R
            grRevInput = revolves.createInput(
                grProfile, grAxis,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            grRevInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(grouser_angle))
            revolves.add(grRevInput)

            if GROUSER_COUNT > 1:
                lastFeature = revolves.item(revolves.count - 1)
                inputEntities = adsk.core.ObjectCollection.create()
                inputEntities.add(lastFeature)
                zAxis = comp.zConstructionAxis
                patterns = comp.features.circularPatternFeatures
                patInput = patterns.createInput(inputEntities, zAxis)
                patInput.quantity = adsk.core.ValueInput.createByReal(GROUSER_COUNT)
                patInput.totalAngle = adsk.core.ValueInput.createByReal(2 * math.pi)
                patInput.isSymmetric = False
                patterns.add(patInput)

        # ══════════════════════════════════════════════════════════════
        # STEP 4: D-flat cut on shaft bore
        # ══════════════════════════════════════════════════════════════

        dflatSketch = comp.sketches.add(comp.xZConstructionPlane)
        dflatSketch.name = 'D-Flat Cut'
        dfl = dflatSketch.sketchCurves.sketchLines

        flat_x = SHAFT_R - D_FLAT_DEPTH
        dfl.addByTwoPoints(p(flat_x, 0, 0), p(SHAFT_R + 0.01, 0, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, 0, 0), p(SHAFT_R + 0.01, WHEEL_W, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, WHEEL_W, 0), p(flat_x, WHEEL_W, 0))
        dfl.addByTwoPoints(p(flat_x, WHEEL_W, 0), p(flat_x, 0, 0))

        dflatAxis = dfl.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
        dflatAxis.isConstruction = True

        dflatProf = None
        minArea = float('inf')
        for pi in range(dflatSketch.profiles.count):
            pr = dflatSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                dflatProf = pr

        if dflatProf:
            dflat_angle = 1.05  # ~60 degrees
            dflatRevInput = revolves.createInput(
                dflatProf, dflatAxis,
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            dflatRevInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(dflat_angle))
            try:
                revolves.add(dflatRevInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════════
        # STEP 5: M2 grub screw hole through hub wall
        # ══════════════════════════════════════════════════════════════

        grub_y = WHEEL_W / 2
        grubPlaneInput = comp.constructionPlanes.createInput()
        grubPlaneInput.setByOffset(
            comp.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(grub_y)
        )
        grubPlane = comp.constructionPlanes.add(grubPlaneInput)

        grubSketch = comp.sketches.add(grubPlane)
        grubSketch.name = 'Grub Screw'
        grubSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(HUB_R, 0, 0), GRUB_R
        )

        grubProf = None
        minArea = float('inf')
        for pi in range(grubSketch.profiles.count):
            pr = grubSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                grubProf = pr

        if grubProf:
            grubInput = extrudes.createInput(
                grubProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            grubInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(GRUB_DEPTH)
            )
            try:
                extrudes.add(grubInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════════
        # STEP 6: Spoke lightening holes (6× elliptical cutouts)
        # Through-cuts between hub and rim, circular pattern
        # ══════════════════════════════════════════════════════════════

        # Create one elliptical hole on the wheel face, then pattern it
        # Sketch on an offset XZ plane at mid-width
        spokePlaneInput = comp.constructionPlanes.createInput()
        spokePlaneInput.setByOffset(
            comp.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(WHEEL_W / 2)
        )
        spokePlane = comp.constructionPlanes.add(spokePlaneInput)

        spokeSketch = comp.sketches.add(spokePlane)
        spokeSketch.name = 'Spoke Hole'

        # Draw an ellipse centred at (SPOKE_HOLE_R_POS, 0) on the sketch
        # Semi-major along Y (circumferential), semi-minor along X (radial)
        centre = p(SPOKE_HOLE_R_POS, 0, 0)
        majorPt = p(SPOKE_HOLE_R_POS, SPOKE_HOLE_LONG, 0)  # semi-major endpoint
        spokeSketch.sketchCurves.sketchEllipses.add(
            centre, majorPt, SPOKE_HOLE_SHORT
        )

        # Find the ellipse profile (smallest area)
        spokeProf = None
        minArea = float('inf')
        for pi in range(spokeSketch.profiles.count):
            pr = spokeSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                spokeProf = pr

        if spokeProf:
            # Extrude cut symmetrically through the full wheel width
            spokeCutInput = extrudes.createInput(
                spokeProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            # Symmetric extent: half-width each direction from mid-plane
            spokeCutInput.setSymmetricExtent(
                adsk.core.ValueInput.createByReal(WHEEL_W / 2 + 0.05),  # slight overcut
                True  # full extent = 2× this value
            )
            try:
                spokeCut = extrudes.add(spokeCutInput)

                # Circular pattern the spoke hole
                if SPOKE_COUNT > 1:
                    inputEntities = adsk.core.ObjectCollection.create()
                    inputEntities.add(spokeCut)
                    zAxis = comp.zConstructionAxis
                    patterns = comp.features.circularPatternFeatures
                    patInput = patterns.createInput(inputEntities, zAxis)
                    patInput.quantity = adsk.core.ValueInput.createByReal(SPOKE_COUNT)
                    patInput.totalAngle = adsk.core.ValueInput.createByReal(2 * math.pi)
                    patInput.isSymmetric = False
                    patterns.add(patInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════════
        # STEP 7: Zoom and report
        # ══════════════════════════════════════════════════════════════

        app.activeViewport.fit()

        mode_str = 'TPU TIRE (rim only, lips for press-fit tire)' if USE_TPU_TIRE else 'STANDALONE (O-rings + grousers)'

        msg = (
            f'Mars Rover Wheel created!\n\n'
            f'Mode: {mode_str}\n'
            f'Outer diameter: {WHEEL_R * 20:.0f}mm\n'
            f'Width: {WHEEL_W * 10:.0f}mm\n'
            f'Shaft bore: {SHAFT_R * 20:.1f}mm (D-shaft with flat)\n'
            f'Grub screw: M2 x {GRUB_DEPTH * 10:.0f}mm deep (radial)\n'
            f'Spoke holes: {SPOKE_COUNT}x elliptical lightening cutouts\n'
        )

        if USE_TPU_TIRE:
            msg += (
                f'Rim lips: 2x {LIP_H * 10:.1f}mm (tire retention)\n'
                f'Tire seat OD: {WHEEL_R * 20:.0f}mm (TPU bore = 70mm)\n\n'
                'Pair with rover_tire.py TPU tire (friend\'s printer).\n'
                'Set USE_TPU_TIRE=False for O-ring fallback mode.'
            )
        else:
            msg += (
                f'Grousers: {GROUSER_COUNT}x radial, {GROUSER_DEPTH * 10:.0f}mm deep\n'
                f'O-ring grooves: {ORING_COUNT}x '
                f'({ORING_GROOVE_W * 10:.1f}mm x {ORING_GROOVE_D * 10:.0f}mm)\n\n'
                'Fit 70mm ID x 3mm O-rings for traction.\n'
                'Set USE_TPU_TIRE=True for two-piece wheel mode.'
            )

        msg += (
            '\n\nPrint hub-side down, no supports.\n'
            'Thread M2 grub screw into radial hole after printing.'
        )

        ui.messageBox(msg, 'Mars Rover - Wheel')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
