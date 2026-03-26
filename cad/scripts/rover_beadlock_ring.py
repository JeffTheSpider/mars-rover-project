"""
Mars Rover Beadlock Ring — Tire Retention
=========================================

Simple annular ring that bolts to the hub open face,
clamping the tire band against the motor-side lip.

Geometry:
  - 66mm ID x 74mm OD x 2mm thick
  - 4x M2 through-holes at 33.75mm radius (matches hub pattern)
  - Chamfered edges for clean appearance

Assembly:
  1. Tire slides onto hub seat from open side
  2. Ring placed over hub face
  3. 4x M2x8mm screws through ring into hub pilot holes
  4. Tire is clamped between ring and motor-side lip

Print: Flat, PLA, 100% infill (thin part), 3 perimeters
Qty: 6 rings

Reference: EA-08, beadlock wheel retention mechanism
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, CHAMFER_STD,
    find_largest_profile, find_smallest_profile,
    zoom_fit,
)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('No active design.')
            return

        # ══════════════════════════════════════════════════════════
        # DIMENSIONS (cm — Fusion API unit)
        # ══════════════════════════════════════════════════════════

        RING_IR = 3.3           # 33mm R (66mm ID) — clears spoke area
        RING_OR = 3.7           # 37mm R (74mm OD) — matches hub flange
        RING_T = 0.2            # 2mm thickness

        # Screw holes — must match hub beadlock pattern
        HOLE_COUNT = 4
        HOLE_R = 0.11           # M2 clearance (2.2mm dia)
        HOLE_POS_R = 3.375      # 33.75mm from centre (mid rim wall)

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Create ring body
        # Sketch on XY plane: two concentric circles, extrude
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Ring Profile'
        circles = sketch.sketchCurves.sketchCircles

        center = p(0, 0, 0)
        circles.addByCenterRadius(center, RING_OR)
        circles.addByCenterRadius(center, RING_IR)

        # Find the annular profile (between the two circles)
        target_area = math.pi * (RING_OR**2 - RING_IR**2)
        ringProf = None
        for i in range(sketch.profiles.count):
            prof = sketch.profiles.item(i)
            if abs(prof.areaProperties().area - target_area) < target_area * 0.2:
                ringProf = prof
                break

        ringBody = None
        if ringProf:
            extInput = extrudes.createInput(
                ringProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(False, val(RING_T))
            ringExt = extrudes.add(extInput)
            ringBody = ringExt.bodies.item(0)
            ringBody.name = 'Beadlock Ring'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Cut M2 through-holes (1 + circular pattern x4)
        # ══════════════════════════════════════════════════════════

        holeSketch = comp.sketches.add(comp.xYConstructionPlane)
        holeSketch.name = 'Screw Holes'
        holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(HOLE_POS_R, 0, 0), HOLE_R
        )

        holeProf = find_smallest_profile(holeSketch)
        holeCut = None
        if holeProf:
            holeInput = extrudes.createInput(
                holeProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            # Through all (ring thickness + extra)
            holeInput.setDistanceExtent(False, val(RING_T + 0.05))
            try:
                holeCut = extrudes.add(holeInput)
            except Exception as e:
                print(f'  Warning: hole cut failed: {e}')

        if holeCut and HOLE_COUNT > 1:
            ie = adsk.core.ObjectCollection.create()
            ie.add(holeCut)
            patInput = comp.features.circularPatternFeatures.createInput(
                ie, comp.zConstructionAxis
            )
            patInput.quantity = val(HOLE_COUNT)
            patInput.totalAngle = val(2 * math.pi)
            patInput.isSymmetric = False
            try:
                comp.features.circularPatternFeatures.add(patInput)
            except Exception as e:
                print(f'  Warning: hole pattern failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 3: Chamfer edges
        # ══════════════════════════════════════════════════════════

        if ringBody:
            all_edges = adsk.core.ObjectCollection.create()
            for ei in range(ringBody.edges.count):
                edge = ringBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - RING_OR) < 0.02 or abs(geom.radius - RING_IR) < 0.02:
                        all_edges.add(edge)

            if all_edges.count > 0:
                try:
                    cham = comp.features.chamferFeatures
                    cham_in = cham.createInput2()
                    cham_in.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                        all_edges, val(CHAMFER_STD), True
                    )
                    cham.add(cham_in)
                except Exception as e:
                    print(f'  Warning: edge chamfer failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            f'Beadlock Ring created!\n\n'
            f'ID: {RING_IR * 20:.0f}mm | OD: {RING_OR * 20:.0f}mm\n'
            f'Thickness: {RING_T * 10:.0f}mm\n'
            f'Holes: {HOLE_COUNT}x M2 clearance at {HOLE_POS_R * 10:.1f}mm R\n\n'
            f'Print flat, PLA, 100% infill, 3 perimeters.\n'
            f'Qty: 6 rings\n\n'
            f'Assembly: 4x M2x8mm screws, hex key.',
            'Mars Rover - Beadlock Ring'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
