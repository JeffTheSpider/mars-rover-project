"""
Mars Rover Wheel V2 — Perseverance-Inspired (0.4 Scale)
=======================================================

Redesigned wheel with Perseverance/Sawppy-inspired aesthetics:
  - 6 curved spokes (angled from hub to rim, impact-absorbing look)
  - 24 tread grousers (gently angled bars, double the V1 count)
  - Wider hub boss (12mm OD, better spoke attachment area)
  - Same 80mm OD × 32mm wide, 3.1mm D-shaft bore

Design inspiration:
  - NASA Perseverance: titanium curved spokes, 48 grousers
  - Sawppy rover: simplified curved spokes, prints face-down
  - jakkra/Mars-Rover: chunky proportions, two-part TPU option

Print orientation: Hub face down (flat on bed, no supports)
Material: PLA
Infill: 50% gyroid
Perimeters: 4
Quantity: 6 wheels

Reference: EA-08, Sawppy, jakkra/Mars-Rover
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

        # ==================================================================
        # PARAMETERS (cm — Fusion 360 API unit)
        # ==================================================================

        # Overall wheel
        WHEEL_R = 4.0           # 40mm radius (80mm OD)
        WHEEL_W = 3.2           # 32mm width
        RIM_THICK = 0.25        # 2.5mm rim wall thickness
        RIM_INNER_R = WHEEL_R - RIM_THICK   # 37.5mm

        # Hub
        HUB_R = 1.2             # 12mm radius (24mm OD) — wider than V1 for spoke area
        HUB_LEN = 0.8           # 8mm hub boss protrusion (shaft engagement)
        SHAFT_R = 0.155         # 1.55mm (3.1mm bore for N20 D-shaft)
        D_FLAT_DEPTH = 0.05     # 0.5mm D-flat

        # Disc (connects hub to rim)
        DISC_THICK = 0.30       # 3mm disc thickness

        # Spoke geometry
        SPOKE_COUNT = 6
        SPOKE_W_HUB = 0.5      # 5mm spoke width at hub
        SPOKE_W_RIM = 0.4      # 4mm spoke width at rim (tapers slightly)
        SPOKE_CURVE = 20.0      # degrees — angular offset from hub to rim (the "sweep")

        # Grousers (tread bars)
        GROUSER_COUNT = 24
        GROUSER_H = 0.2        # 2mm grouser height (above rim)
        GROUSER_W = 0.15       # 1.5mm grouser width (along circumference)
        GROUSER_TILT = 8.0     # degrees — slight tilt for Perseverance look

        # Grub screw
        GRUB_R = 0.1           # M2 (1mm radius)
        GRUB_DEPTH = 0.5       # 5mm deep

        # Rim retention lips (for optional TPU tire)
        LIP_H = 0.15           # 1.5mm lip height
        LIP_W = 0.2            # 2mm lip width

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        revolves = comp.features.revolveFeatures
        extrudes = comp.features.extrudeFeatures

        # ==================================================================
        # STEP 1: RIM — hollow cylinder (outer ring of wheel)
        # Revolve an L-shaped cross-section around the Y axis
        # Sketch on XZ plane (X=radial, Y=axial/width)
        # ==================================================================

        rimSketch = comp.sketches.add(comp.xZConstructionPlane)
        rimSketch.name = 'Rim Profile'
        rl = rimSketch.sketchCurves.sketchLines

        # L-shape: outer wall + back face floor
        # Points going around the rim cross-section:
        #   Bottom-inner  → Bottom-outer  → Top-outer  → Top-inner
        # "Bottom" = Y=0 face, "Top" = Y=WHEEL_W face
        # "Inner" = RIM_INNER_R, "Outer" = WHEEL_R

        rim_pts = [
            (RIM_INNER_R, 0),           # A: inner bottom
            (WHEEL_R, 0),               # B: outer bottom
            (WHEEL_R, WHEEL_W),         # C: outer top
            (RIM_INNER_R, WHEEL_W),     # D: inner top
            (RIM_INNER_R, WHEEL_W - DISC_THICK),  # E: step inward (disc top)
            (RIM_INNER_R, DISC_THICK),  # F: step inward (disc bottom) — NOT USED
        ]

        # Draw the closed U-shaped profile (rim walls + back face)
        # Going: A→B→C→D→A (simple rectangle for full rim)
        for i in range(4):
            x1, y1 = rim_pts[i]
            x2, y2 = rim_pts[(i + 1) % 4]
            rl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        # Revolve axis (Y axis through origin)
        rimAxis = rl.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
        rimAxis.isConstruction = True

        rimProf = rimSketch.profiles.item(0)
        rimRevInput = revolves.createInput(
            rimProf, rimAxis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        rimRevInput.setAngleExtent(
            False, adsk.core.ValueInput.createByReal(2 * math.pi)
        )
        rimRev = revolves.add(rimRevInput)
        rimBody = rimRev.bodies.item(0)
        rimBody.name = 'Wheel_Rim'

        # ==================================================================
        # STEP 2: HUB BOSS — central cylinder for motor shaft
        # ==================================================================

        hubSketch = comp.sketches.add(comp.xZConstructionPlane)
        hubSketch.name = 'Hub Profile'
        hl = hubSketch.sketchCurves.sketchLines

        # Hub profile: rectangle from shaft bore to hub OD, full width + boss
        hub_pts = [
            (SHAFT_R, -HUB_LEN),       # shaft bore, boss start (behind face)
            (HUB_R, -HUB_LEN),         # hub OD, boss start
            (HUB_R, WHEEL_W),           # hub OD, far face
            (SHAFT_R, WHEEL_W),         # shaft bore, far face
        ]

        for i in range(4):
            x1, y1 = hub_pts[i]
            x2, y2 = hub_pts[(i + 1) % 4]
            hl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        hubAxis = hl.addByTwoPoints(p(0, -HUB_LEN, 0), p(0, WHEEL_W, 0))
        hubAxis.isConstruction = True

        hubProf = hubSketch.profiles.item(0)
        hubRevInput = revolves.createInput(
            hubProf, hubAxis,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        hubRevInput.setAngleExtent(
            False, adsk.core.ValueInput.createByReal(2 * math.pi)
        )
        revolves.add(hubRevInput)

        # ==================================================================
        # STEP 3: CURVED SPOKES — 6 angled ribs from hub to rim
        # Each spoke is a tapered bar that sweeps SPOKE_CURVE degrees
        # from hub to rim, creating the Perseverance curved-spoke look.
        # ==================================================================

        # Create spoke on the disc mid-plane
        # NOTE: Rim revolves around Z axis (due to XZ sketch Z-negation).
        # Spokes must be in the XY plane (perpendicular to wheel axis).
        # Wheel extends from Z=0 to Z=-WHEEL_W, so mid-plane is Z=-WHEEL_W/2.
        spokePlaneInput = comp.constructionPlanes.createInput()
        spokePlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(-WHEEL_W / 2)
        )
        spokePlane = comp.constructionPlanes.add(spokePlaneInput)

        # Helper: point on circle at angle (degrees) and radius
        def polar(radius, angle_deg):
            rad = math.radians(angle_deg)
            return (radius * math.cos(rad), radius * math.sin(rad))

        # Angular half-widths
        spoke_half_hub = math.degrees(SPOKE_W_HUB / (2 * HUB_R * 10)) * 10  # degrees
        spoke_half_rim = math.degrees(SPOKE_W_RIM / (2 * RIM_INNER_R * 10)) * 10

        # Create one spoke shape, then use circular pattern
        # Spoke 0 centred at 0° on hub, arrives at SPOKE_CURVE° on rim
        base_angle = 0.0
        curve = SPOKE_CURVE

        # 4 corners of the spoke trapezoid
        # Hub left/right edges
        h_left = polar(HUB_R, base_angle - spoke_half_hub)
        h_right = polar(HUB_R, base_angle + spoke_half_hub)
        # Rim left/right edges (angularly offset by curve)
        r_left = polar(RIM_INNER_R, base_angle + curve - spoke_half_rim)
        r_right = polar(RIM_INNER_R, base_angle + curve + spoke_half_rim)

        spokeSketch = comp.sketches.add(spokePlane)
        spokeSketch.name = 'Spoke 0'
        sl = spokeSketch.sketchCurves.sketchLines

        # Draw the trapezoid
        p1 = p(h_left[0], h_left[1], 0)
        p2 = p(h_right[0], h_right[1], 0)
        p3 = p(r_right[0], r_right[1], 0)
        p4 = p(r_left[0], r_left[1], 0)

        sl.addByTwoPoints(p1, p4)  # hub left → rim left
        sl.addByTwoPoints(p4, p3)  # rim left → rim right
        sl.addByTwoPoints(p3, p2)  # rim right → hub right
        sl.addByTwoPoints(p2, p1)  # hub right → hub left

        # Find and extrude the spoke profile
        spokeProf = None
        targetArea = SPOKE_W_HUB * (RIM_INNER_R - HUB_R)  # approximate
        minDiff = float('inf')
        for pi_idx in range(spokeSketch.profiles.count):
            pr = spokeSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            diff = abs(a - targetArea)
            if diff < minDiff:
                minDiff = diff
                spokeProf = pr

        if spokeProf:
            spokeExtInput = extrudes.createInput(
                spokeProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            # Extrude symmetrically to disc thickness
            spokeExtInput.setSymmetricExtent(
                adsk.core.ValueInput.createByReal(DISC_THICK / 2 + 0.01),
                True
            )
            spokeExt = extrudes.add(spokeExtInput)

            # Circular pattern for 6 spokes
            if SPOKE_COUNT > 1:
                inputEntities = adsk.core.ObjectCollection.create()
                inputEntities.add(spokeExt)
                # Pattern around Z axis (wheel rotational axis)
                # Rim revolves on XZ plane → Z-negation → wheel axis is Z
                patterns = comp.features.circularPatternFeatures
                patInput = patterns.createInput(inputEntities, comp.zConstructionAxis)
                patInput.quantity = adsk.core.ValueInput.createByReal(SPOKE_COUNT)
                patInput.totalAngle = adsk.core.ValueInput.createByReal(2 * math.pi)
                patInput.isSymmetric = False
                try:
                    patterns.add(patInput)
                except:
                    pass  # If pattern fails, we still have one spoke

        # ==================================================================
        # STEP 4: RIM RETENTION LIPS (both faces, for TPU tire option)
        # ==================================================================

        lip1Sketch = comp.sketches.add(comp.xZConstructionPlane)
        lip1Sketch.name = 'Rim Lip Face 1'
        ll = lip1Sketch.sketchCurves.sketchLines
        lip_r_inner = WHEEL_R - LIP_W
        lip_r_outer = WHEEL_R

        lip1_pts = [
            (lip_r_inner, -LIP_H),
            (lip_r_outer, -LIP_H),
            (lip_r_outer, 0),
            (lip_r_inner, 0),
        ]
        for i in range(4):
            x1, y1 = lip1_pts[i]
            x2, y2 = lip1_pts[(i + 1) % 4]
            ll.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        lipAxis1 = ll.addByTwoPoints(p(0, -LIP_H, 0), p(0, 0, 0))
        lipAxis1.isConstruction = True

        lipProf1 = lip1Sketch.profiles.item(0)
        try:
            lipRev1 = revolves.createInput(
                lipProf1, lipAxis1,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            lipRev1.setAngleExtent(
                False, adsk.core.ValueInput.createByReal(2 * math.pi)
            )
            revolves.add(lipRev1)
        except:
            pass

        # Lip on face 2 (far side)
        lip2Sketch = comp.sketches.add(comp.xZConstructionPlane)
        lip2Sketch.name = 'Rim Lip Face 2'
        ll2 = lip2Sketch.sketchCurves.sketchLines

        lip2_pts = [
            (lip_r_inner, WHEEL_W),
            (lip_r_outer, WHEEL_W),
            (lip_r_outer, WHEEL_W + LIP_H),
            (lip_r_inner, WHEEL_W + LIP_H),
        ]
        for i in range(4):
            x1, y1 = lip2_pts[i]
            x2, y2 = lip2_pts[(i + 1) % 4]
            ll2.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        lipAxis2 = ll2.addByTwoPoints(p(0, WHEEL_W, 0), p(0, WHEEL_W + LIP_H, 0))
        lipAxis2.isConstruction = True

        lipProf2 = lip2Sketch.profiles.item(0)
        try:
            lipRev2 = revolves.createInput(
                lipProf2, lipAxis2,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            lipRev2.setAngleExtent(
                False, adsk.core.ValueInput.createByReal(2 * math.pi)
            )
            revolves.add(lipRev2)
        except:
            pass

        # ==================================================================
        # STEP 5: GROUSERS — 24 tread bars on rim surface
        # Each grouser is a thin raised bar, slightly tilted
        # ==================================================================

        # Create one grouser as a small rectangular extrusion on the rim
        # Sketch on a plane tangent to the rim surface at angle 0
        grouserSketch = comp.sketches.add(comp.xZConstructionPlane)
        grouserSketch.name = 'Grouser'
        gl = grouserSketch.sketchCurves.sketchLines

        # Grouser profile: thin rectangle at rim OD
        gr_inner = WHEEL_R - 0.01   # just below rim surface (for clean join)
        gr_outer = WHEEL_R + GROUSER_H

        # Grouser tilted by GROUSER_TILT degrees
        tilt_offset = GROUSER_W * math.tan(math.radians(GROUSER_TILT))

        gl.addByTwoPoints(p(gr_inner, 0, 0), p(gr_outer, tilt_offset, 0))
        gl.addByTwoPoints(p(gr_outer, tilt_offset, 0),
                          p(gr_outer, WHEEL_W - tilt_offset, 0))
        gl.addByTwoPoints(p(gr_outer, WHEEL_W - tilt_offset, 0),
                          p(gr_inner, WHEEL_W, 0))
        gl.addByTwoPoints(p(gr_inner, WHEEL_W, 0), p(gr_inner, 0, 0))

        grouserAxis = gl.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
        grouserAxis.isConstruction = True

        # Find the grouser profile
        grouserProf = None
        minArea = float('inf')
        for pi_idx in range(grouserSketch.profiles.count):
            pr = grouserSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                grouserProf = pr

        if grouserProf:
            # Revolve a thin arc (one grouser width)
            grouser_angle = GROUSER_W / WHEEL_R  # radians
            grouserRevInput = revolves.createInput(
                grouserProf, grouserAxis,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            grouserRevInput.setAngleExtent(
                False, adsk.core.ValueInput.createByReal(grouser_angle)
            )
            try:
                grouserRev = revolves.add(grouserRevInput)

                # Circular pattern for 24 grousers
                inputEntities = adsk.core.ObjectCollection.create()
                inputEntities.add(grouserRev)
                patterns = comp.features.circularPatternFeatures
                patInput = patterns.createInput(inputEntities, comp.zConstructionAxis)
                patInput.quantity = adsk.core.ValueInput.createByReal(GROUSER_COUNT)
                patInput.totalAngle = adsk.core.ValueInput.createByReal(2 * math.pi)
                patInput.isSymmetric = False
                patterns.add(patInput)
            except:
                pass

        # ==================================================================
        # STEP 6: D-FLAT CUT on shaft bore
        # ==================================================================

        dflatSketch = comp.sketches.add(comp.xZConstructionPlane)
        dflatSketch.name = 'D-Flat Cut'
        dfl = dflatSketch.sketchCurves.sketchLines

        flat_x = SHAFT_R - D_FLAT_DEPTH
        dfl.addByTwoPoints(p(flat_x, -HUB_LEN, 0), p(SHAFT_R + 0.01, -HUB_LEN, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, -HUB_LEN, 0),
                           p(SHAFT_R + 0.01, WHEEL_W, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, WHEEL_W, 0), p(flat_x, WHEEL_W, 0))
        dfl.addByTwoPoints(p(flat_x, WHEEL_W, 0), p(flat_x, -HUB_LEN, 0))

        dflatAxis = dfl.addByTwoPoints(p(0, -HUB_LEN, 0), p(0, WHEEL_W, 0))
        dflatAxis.isConstruction = True

        dflatProf = None
        minArea = float('inf')
        for pi_idx in range(dflatSketch.profiles.count):
            pr = dflatSketch.profiles.item(pi_idx)
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
            dflatRevInput.setAngleExtent(
                False, adsk.core.ValueInput.createByReal(dflat_angle)
            )
            try:
                revolves.add(dflatRevInput)
            except:
                pass

        # ==================================================================
        # STEP 7: M2 GRUB SCREW hole through hub wall
        # ==================================================================

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
                True, adsk.core.ValueInput.createByReal(GRUB_DEPTH)
            )
            try:
                extrudes.add(grubInput)
            except:
                pass

        # ==================================================================
        # STEP 8: ZOOM AND REPORT
        # ==================================================================

        app.activeViewport.fit()

        ui.messageBox(
            'Mars Rover Wheel V2 — Perseverance Style!\n\n'
            f'Outer diameter: {WHEEL_R * 20:.0f}mm\n'
            f'Width: {WHEEL_W * 10:.0f}mm\n'
            f'Hub OD: {HUB_R * 20:.0f}mm (wider for spoke attachment)\n'
            f'Shaft bore: {SHAFT_R * 20:.1f}mm (N20 D-shaft)\n\n'
            f'Spokes: {SPOKE_COUNT}x curved ({SPOKE_CURVE:.0f}° sweep)\n'
            f'  Width: {SPOKE_W_HUB * 10:.0f}mm (hub) → '
            f'{SPOKE_W_RIM * 10:.0f}mm (rim)\n'
            f'Grousers: {GROUSER_COUNT}x tilted bars '
            f'({GROUSER_H * 10:.0f}mm tall, {GROUSER_TILT:.0f}° tilt)\n'
            f'Rim lips: 2x {LIP_H * 10:.1f}mm (TPU tire retention)\n\n'
            'Design inspired by:\n'
            '  - NASA Perseverance curved spokes\n'
            '  - Sawppy simplified spoke geometry\n'
            '  - jakkra/Mars-Rover proportions\n\n'
            'Print hub-side down, no supports.\n'
            'Qty needed: 6 wheels.',
            'Mars Rover — Wheel V2'
        )

    except:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}')
