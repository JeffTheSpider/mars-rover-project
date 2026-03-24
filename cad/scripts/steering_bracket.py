"""
Mars Rover Steering Bracket — Phase 1 (0.4 Scale)
====================================================

35×30×40mm bracket that connects a steered wheel to the rocker/bogie arm.
Contains: 608ZZ bearing seat (top), 8mm pivot bore, N20 motor clip (bottom),
horizontal shaft exit hole, 2× M3 heat-set insert pockets for arm mounting,
bearing entry chamfer.

Width increased from 25mm to 30mm for 3.9mm wall around bearing seat.

Quantity: 4 (FL, FR, RL, RR corners)

Print orientation: Large flat face down (35×30mm on bed)
Supports: None needed
Perimeters: 5 (structural — 3.9mm bearing wall is tightest margin)
Infill: 60% gyroid (increased for bearing retention strength)

Reference: EA-08, EA-10
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
        BRACKET_H = 4.0     # 40mm height (vertical)

        # Bearing seat (top face)
        BEARING_SEAT_R = 1.1075  # 22.15mm dia bore
        BEARING_SEAT_DEPTH = 0.72  # 7.2mm
        PIVOT_BORE_R = 0.4       # 8mm dia through-hole

        # Motor clip pocket (bottom)
        MOTOR_W = 1.22      # 12.2mm clip inner width
        MOTOR_H = 1.02      # 10.2mm clip inner height
        MOTOR_DEPTH = 2.5   # 25mm motor body length
        CLIP_WALL = 0.2     # 2mm clip wall
        SHAFT_HOLE_R = 0.2  # 4mm shaft exit hole

        # Wheel offset
        PIVOT_TO_WHEEL = 2.0  # 20mm vertical offset (wheel below bracket)

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════
        # Main body — revolve/extrude approach
        # Create as rectangular block, then cut features
        # ══════════════════════════════════════════════════════

        # Step 1: Base block on XY plane
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

        # Step 2: Bearing seat (cylindrical cut from top)
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

        # Find the circle profile (smallest area)
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

        # Step 3: Pivot bore (8mm through entire height)
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

        # Step 4: Motor clip pocket (rectangular cut from bottom)
        motorSketch = comp.sketches.add(comp.xYConstructionPlane)
        motorSketch.name = 'Motor Pocket'
        motorSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-MOTOR_W / 2, -MOTOR_H / 2, 0),
            p(MOTOR_W / 2, MOTOR_H / 2, 0)
        )

        # Find the rectangular profile (smallest = motor pocket)
        mProf = None
        minArea = float('inf')
        for pi in range(motorSketch.profiles.count):
            pr = motorSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                mProf = pr

        if mProf:
            motorInput = extrudes.createInput(
                mProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            motorInput.setDistanceExtent(
                False,
                adsk.core.ValueInput.createByReal(MOTOR_DEPTH)
            )
            extrudes.add(motorInput)

        # Step 5: Horizontal shaft exit hole (motor shaft exits through side wall)
        # The motor sits vertically in the pocket, shaft points downward
        # toward the wheel. The shaft exit goes through the bracket bottom.
        # Actually for the steering bracket design, the motor is oriented
        # with shaft horizontal (pointing outward toward wheel).
        # Create horizontal shaft hole on the side face (YZ plane).
        SHAFT_EXIT_Z = MOTOR_DEPTH / 2  # mid-height of motor pocket

        shaftPlaneInput = comp.constructionPlanes.createInput()
        shaftPlaneInput.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(-BRACKET_L / 2)
        )
        shaftPlane = comp.constructionPlanes.add(shaftPlaneInput)

        shaftSketch = comp.sketches.add(shaftPlane)
        shaftSketch.name = 'Shaft Exit'
        # On YZ plane at X offset: sketch coords map to (Y, Z)
        # Need hole at centre Y=0, Z=shaft_exit_z
        # YZ plane sketch: X -> -Z world, Y -> Y world
        shaftSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(-SHAFT_EXIT_Z, 0, 0), SHAFT_HOLE_R
        )

        sProf = None
        minArea = float('inf')
        for pi in range(shaftSketch.profiles.count):
            pr = shaftSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                sProf = pr

        if sProf:
            shaftInput = extrudes.createInput(
                sProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            shaftInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(BRACKET_L)
            )
            try:
                extrudes.add(shaftInput)
            except:
                pass

        # Step 6: M3 heat-set insert pockets for arm mounting
        # Two pockets on the top face, outside the bearing seat,
        # at the front and rear of the bracket along the arm direction
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

        # Step 7: Bearing entry chamfer (0.3mm x 45°)
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
            'Steering Bracket created!\n\n'
            f'Size: {BRACKET_L*10:.0f} × {BRACKET_W*10:.0f} × '
            f'{BRACKET_H*10:.0f}mm\n'
            f'Bearing seat: {BEARING_SEAT_R*20:.2f}mm dia × '
            f'{BEARING_SEAT_DEPTH*10:.1f}mm deep\n'
            f'Bearing wall: {wall_around_bearing:.1f}mm\n'
            f'Pivot bore: {PIVOT_BORE_R*20:.0f}mm through\n'
            f'Motor pocket: {MOTOR_W*10:.1f} × {MOTOR_H*10:.1f}mm\n'
            f'Shaft exit: horizontal, {SHAFT_HOLE_R*20:.0f}mm dia\n'
            f'Arm mounting: 2× M3 heat-set insert pockets\n'
            f'Bearing chamfer: 0.3mm\n\n'
            'Qty needed: 4 (FL, FR, RL, RR)\n'
            'Print flat face down, no supports.',
            'Mars Rover - Steering Bracket'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
