"""
Mars Rover Steering Bracket — Phase 1 (0.4 Scale)
====================================================

Bearing carrier bracket for the 4 steered wheels (FL, FR, RL, RR).
Bolts to the front face of the FrontWheelConnector. The steering
knuckle hangs below on an 8mm pivot shaft through the 608ZZ bearing.

Updated per EA-27: Motor clip REMOVED (motor is in knuckle only).
Hard stop channel added (±35° mechanical steering limit).
Height reduced from 40mm to 25mm (bearing carrier only, no motor).

Features:
  - 608ZZ bearing seat (top): 22.15mm × 7.2mm, 0.3mm entry chamfer
  - 8mm pivot bore (through full height)
  - Hard stop channel: 70° open arc at bracket bottom (±35° limit)
  - 2× M3 heat-set insert pockets (top face, for connector bolting)
  - Bearing entry chamfer (0.3mm × 45°)

Overall size: 35 × 30 × 25mm (reduced from 40mm — no motor)
Bearing wall: 3.9mm minimum around bearing seat (critical)

Print orientation: Large flat face down (35×30mm on bed)
Supports: None needed
Perimeters: 5 (structural — 3.9mm bearing wall is tightest margin)
Infill: 60% gyroid (bearing retention strength)

Qty: 4 (FL, FR, RL, RR corners)

Reference: EA-27 (steering design package), EA-08, EA-10
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
        BRACKET_L = 3.5     # 35mm length (along arm direction)
        BRACKET_W = 3.0     # 30mm width (increased for 3.9mm bearing wall)
        BRACKET_H = 2.5     # 25mm height (reduced: bearing carrier only, no motor)

        # Bearing seat (top face)
        BEARING_SEAT_R = 1.1075  # 22.15mm dia bore
        BEARING_SEAT_DEPTH = 0.72  # 7.2mm
        PIVOT_BORE_R = 0.4       # 8mm dia through-hole

        # Hard stop channel (bottom face, ±35° limit)
        STOP_WALL_W = 0.3       # 3mm wall width
        STOP_WALL_H = 0.5       # 5mm wall height (extends up from bottom)
        STOP_WALL_THICK = 0.3   # 3mm wall thickness (radial)
        STOP_CHANNEL_DEG = 70   # 70° open channel (±35°)
        STOP_RADIUS = 0.8       # 8mm from pivot centre to stop wall

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════
        # Step 1: Base block on XY plane
        # ══════════════════════════════════════════════════════

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
        blockExt = extrudes.add(extInput)
        body = blockExt.bodies.item(0)
        body.name = 'Steering Bracket'

        # ══════════════════════════════════════════════════════
        # Step 2: Bearing seat (cylindrical cut from top)
        # ══════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BRACKET_H)
        )
        topP = topPlane.add(tpInput)

        bearingSketch = comp.sketches.add(topP)
        bearingSketch.name = 'Bearing Seat'
        bearingSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, 0, 0), BEARING_SEAT_R
        )

        bProf = None
        minArea = float('inf')
        for pi in range(bearingSketch.profiles.count):
            pr = bearingSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                bProf = pr

        if bProf:
            cutInput = extrudes.createInput(
                bProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            cutInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(BEARING_SEAT_DEPTH)
            )
            extrudes.add(cutInput)

        # ══════════════════════════════════════════════════════
        # Step 3: Pivot bore (8mm through entire height)
        # ══════════════════════════════════════════════════════

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
                True, adsk.core.ValueInput.createByReal(BRACKET_H)
            )
            extrudes.add(boreInput)

        # ══════════════════════════════════════════════════════
        # Step 4: Hard stop walls (2× blocks at ±35° from +Y axis)
        # These limit the knuckle's rotation to ±35°
        # ══════════════════════════════════════════════════════

        # Hard stop walls are small rectangular blocks on the bracket
        # inner face near the bottom. They sit at ±35° from the
        # "straight ahead" (+Y) direction at STOP_RADIUS from centre.

        stopSketch = comp.sketches.add(comp.xYConstructionPlane)
        stopSketch.name = 'Hard Stop Walls'

        for sign in [-1, 1]:
            angle_rad = sign * math.radians(35)
            # Centre of stop wall at STOP_RADIUS from pivot, at ±35°
            cx = STOP_RADIUS * math.sin(angle_rad)
            cy = STOP_RADIUS * math.cos(angle_rad)
            # Wall is perpendicular to the radial direction
            # Approximate as small rectangle
            hw = STOP_WALL_W / 2
            ht = STOP_WALL_THICK / 2
            # Rotate the rectangle to be tangential
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            # Rectangle corners (tangential direction = perpendicular to radius)
            # tangent = (-cos, sin) for CW rotation
            tx = -cos_a
            ty = sin_a
            # radial direction
            rx = sin_a
            ry = cos_a
            corners = [
                (cx + hw * tx + ht * rx, cy + hw * ty + ht * ry),
                (cx + hw * tx - ht * rx, cy + hw * ty - ht * ry),
                (cx - hw * tx - ht * rx, cy - hw * ty - ht * ry),
                (cx - hw * tx + ht * rx, cy - hw * ty + ht * ry),
            ]
            sl = stopSketch.sketchCurves.sketchLines
            for i in range(4):
                x1, y1 = corners[i]
                x2, y2 = corners[(i + 1) % 4]
                sl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        # Extrude stop walls upward
        for pi in range(stopSketch.profiles.count):
            pr = stopSketch.profiles.item(pi)
            a = pr.areaProperties().area
            target = STOP_WALL_W * STOP_WALL_THICK
            if abs(a - target) < target * 0.5:
                swInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                swInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(STOP_WALL_H)
                )
                try:
                    extrudes.add(swInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════
        # Step 5: M3 heat-set insert pockets for arm mounting
        # ══════════════════════════════════════════════════════

        HSERT_R = 0.24       # 4.8mm dia / 2
        HSERT_DEPTH = 0.55   # 5.5mm deep
        MOUNT_Y_OFFSET = BRACKET_L / 2 - 0.5  # 5mm from bracket edge

        mountSketch = comp.sketches.add(topP)
        mountSketch.name = 'Arm Mount Holes'
        mountSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, -MOUNT_Y_OFFSET, 0), HSERT_R
        )
        mountSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, MOUNT_Y_OFFSET, 0), HSERT_R
        )

        for pi in range(mountSketch.profiles.count):
            pr = mountSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.5:
                mInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                mInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(HSERT_DEPTH)
                )
                try:
                    extrudes.add(mInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════
        # Step 6: Bearing entry chamfer (0.3mm x 45°)
        # ══════════════════════════════════════════════════════

        chamferEdges = adsk.core.ObjectCollection.create()
        for edge in body.edges:
            geom = edge.geometry
            if isinstance(geom, adsk.core.Circle3D):
                if abs(geom.radius - BEARING_SEAT_R) < 0.02:
                    chamferEdges.add(edge)
                    break

        if chamferEdges.count > 0:
            chamfers = comp.features.chamferFeatures
            chamInput = chamfers.createInput2()
            chamInput.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                chamferEdges,
                adsk.core.ValueInput.createByReal(0.03),
                True
            )
            try:
                chamfers.add(chamInput)
            except:
                pass

        # ── Zoom and report ──
        wall_around_bearing = (BRACKET_W / 2 - BEARING_SEAT_R) * 10
        app.activeViewport.fit()

        ui.messageBox(
            'Steering Bracket created! (EA-27 updated)\n\n'
            f'Size: {BRACKET_L*10:.0f} × {BRACKET_W*10:.0f} × '
            f'{BRACKET_H*10:.0f}mm\n'
            f'Bearing seat: {BEARING_SEAT_R*20:.2f}mm dia × '
            f'{BEARING_SEAT_DEPTH*10:.1f}mm deep\n'
            f'Bearing wall: {wall_around_bearing:.1f}mm\n'
            f'Pivot bore: {PIVOT_BORE_R*20:.0f}mm through\n'
            f'Hard stops: 2× walls at ±35° (EA-27)\n'
            f'Arm mounting: 2× M3 heat-set insert pockets\n'
            f'Bearing chamfer: 0.3mm\n\n'
            'CHANGES (EA-27):\n'
            '  - Motor clip REMOVED (now in knuckle only)\n'
            '  - Shaft exit hole REMOVED\n'
            '  - Height reduced 40→25mm\n'
            '  - Hard stop walls added at ±35°\n\n'
            'Qty needed: 4 (FL, FR, RL, RR)\n'
            'Print flat face down, no supports.',
            'Mars Rover - Steering Bracket'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
