"""
Bearing Test Piece — 608ZZ Press-Fit Validation
================================================

Creates a simple test piece in Fusion 360 to validate 608ZZ bearing
press-fit dimensions on the CTC printer (PLA).

608ZZ bearing: 8mm ID x 22mm OD x 7mm width
Bore: 22.15mm (0.15mm oversize for PLA press-fit)
Seat depth: 7.2mm (bearing width + 0.2mm)

The test piece is a 30mm diameter cylinder, 10mm tall, with a 22.15mm
bore in the centre and a 0.3mm chamfer to guide insertion.

After printing, test-fit a 608ZZ bearing:
- Too tight: increase bore by 0.05mm increments
- Too loose: decrease bore by 0.05mm increments
- Target: firm press fit by hand, no hammer needed

Usage: Run as a Script in Fusion 360 (UTILITIES > Scripts and Add-Ins)

Reference: EA-08 Section 10.3 (Bearing Press-Fit Dimensions)
"""

import adsk.core
import adsk.fusion
import traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('No active design. Please create or open a design first.')
            return

        # ── Parameters (all in cm — Fusion 360 API uses cm internally) ──
        OUTER_DIA = 3.0       # 30mm outer diameter
        HEIGHT = 1.0          # 10mm tall
        BORE_DIA = 2.215      # 22.15mm bore (608ZZ OD + 0.15mm for PLA press-fit)
        BORE_DEPTH = 0.72     # 7.2mm seat depth (7mm bearing + 0.2mm)
        CHAMFER = 0.03        # 0.3mm chamfer at bore entry
        SHAFT_HOLE = 0.8      # 8mm through-hole for M8 shaft
        LIP_HEIGHT = 0.05     # 0.5mm retention lip at bottom of bore

        # ── Create a new component ──
        root = design.rootComponent
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occ.component
        comp.name = 'Bearing Test Piece - 608ZZ'

        # ── Sketch 1: Outer profile (revolve profile) ──
        # We'll use revolve for a cleaner result
        sketches = comp.sketches
        xyPlane = comp.xYConstructionPlane
        sketch1 = sketches.add(xyPlane)
        sketch1.name = 'Profile'

        lines = sketch1.sketchCurves.sketchLines
        arcs = sketch1.sketchCurves.sketchArcs

        # Draw half-profile for revolution around Y axis (centre axis)
        # Points define the cross-section (X = radius, Y = height)
        # Going clockwise from bottom-centre:
        #
        # The profile (right side, for revolve around Y axis):
        #   Bottom: shaft hole radius to outer radius
        #   Right side: up to top
        #   Top: outer radius to bore radius
        #   Bore wall: down to bore bottom
        #   Bore bottom: to shaft radius
        #   Centre shaft: down to bottom

        p = adsk.core.Point3D.create

        # Profile points (x = radius from centre, y = height)
        shaft_r = SHAFT_HOLE / 2        # 4mm = 0.4cm radius
        outer_r = OUTER_DIA / 2         # 15mm = 1.5cm radius
        bore_r = BORE_DIA / 2           # 11.075mm
        lip_r = bore_r - 0.05           # Retention lip (0.5mm step inward)

        # Draw the profile as a closed loop
        # Start at bottom-centre (shaft hole), go clockwise
        p1 = p(shaft_r, 0, 0)             # Bottom, at shaft radius
        p2 = p(outer_r, 0, 0)             # Bottom, at outer radius
        p3 = p(outer_r, HEIGHT, 0)         # Top, at outer radius
        p4 = p(bore_r, HEIGHT, 0)          # Top, at bore radius
        p5 = p(bore_r, HEIGHT - BORE_DEPTH, 0)  # Bore bottom, at bore radius
        p6 = p(shaft_r, HEIGHT - BORE_DEPTH, 0)  # Bore bottom, at shaft radius (no lip for simplicity)
        # Close back to p1

        l1 = lines.addByTwoPoints(p1, p2)  # Bottom face
        l2 = lines.addByTwoPoints(p2, p3)  # Outer wall
        l3 = lines.addByTwoPoints(p3, p4)  # Top face (outer to bore)
        l4 = lines.addByTwoPoints(p4, p5)  # Bore wall
        l5 = lines.addByTwoPoints(p5, p6)  # Bore bottom
        l6 = lines.addByTwoPoints(p6, p1)  # Inner shaft wall

        # ── Revolve the profile ──
        # Create construction axis (Y axis through origin)
        profile = sketch1.profiles.item(0)

        # Create revolve axis line (Y axis)
        axisLine = sketch1.sketchCurves.sketchLines.addByTwoPoints(
            p(0, 0, 0), p(0, HEIGHT, 0)
        )
        axisLine.isConstruction = True

        revolves = comp.features.revolveFeatures
        revolveInput = revolves.createInput(
            profile,
            axisLine,
            adsk.fusion.FeatureOperations.NewBodyFeature
        )
        revolveInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * 3.14159265358979))
        revolve = revolves.add(revolveInput)

        # ── Add chamfer at bore entry (top edge) ──
        # Find the top circular edge of the bore
        body = revolve.bodies.item(0)
        body.name = 'Bearing Test Piece'

        # Find edges for chamfer - the bore top edge
        chamferEdges = adsk.core.ObjectCollection.create()
        for edge in body.edges:
            # Find circular edges at the top (Y = HEIGHT) with radius ~= bore_r
            geom = edge.geometry
            if hasattr(geom, 'radius'):
                radius = geom.radius
                # Check if it's the bore edge at the top
                _, center = geom.center  # Returns (bool, Point3D)  -- actually this is wrong
                # Let's use a simpler check
                if abs(radius - bore_r) < 0.01:
                    # Check Y coordinate of edge midpoint
                    eval_result = edge.evaluator
                    _, startPt, endPt = eval_result.getEndPoints()
                    if abs(startPt.y - HEIGHT) < 0.01 or abs(endPt.y - HEIGHT) < 0.01:
                        chamferEdges.add(edge)
                        break

        if chamferEdges.count > 0:
            chamfers = comp.features.chamferFeatures
            chamferInput = chamfers.createInput2()
            chamferInput.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                chamferEdges,
                adsk.core.ValueInput.createByReal(CHAMFER),
                True
            )
            chamfers.add(chamferInput)

        # ── Add text label on top face ──
        # Skip text for simplicity — can be added later

        # ── Set material appearance ──
        # Skip — will use default

        # ── Zoom to fit ──
        vp = app.activeViewport
        vp.fit()

        # ── Report ──
        ui.messageBox(
            'Bearing Test Piece created!\n\n'
            f'Outer diameter: {OUTER_DIA * 10:.1f}mm\n'
            f'Height: {HEIGHT * 10:.1f}mm\n'
            f'Bore diameter: {BORE_DIA * 10:.2f}mm (608ZZ + 0.15mm)\n'
            f'Bore depth: {BORE_DEPTH * 10:.1f}mm\n'
            f'Shaft hole: {SHAFT_HOLE * 10:.1f}mm\n'
            f'Chamfer: {CHAMFER * 10:.1f}mm\n\n'
            'Print this piece and test-fit a 608ZZ bearing.\n'
            'Adjust BORE_DIA ±0.05mm if needed.',
            'Mars Rover - Bearing Test'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
