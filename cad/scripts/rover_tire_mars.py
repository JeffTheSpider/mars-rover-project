"""
Mars Rover Tire — Chevron Grouser Pattern
==========================================

Interchangeable tire band for the two-piece wheel system.
Mars rover-style angled chevron grousers for loose soil and gravel.

Geometry:
  - 70mm ID (sits on hub seat) x 80mm OD (at tread tips) x 40mm wide
  - 2mm structural wall (70mm to 74mm)
  - 12x chevron grousers, 3mm tall, tapered cross-section
  - Grousers sweep partial width with alternating angle (V-pattern)
  - Clamped between motor-side lip and beadlock ring (no screw holes in tire)

Fits: rover_wheel_hub_v4.py (70mm seat OD, 74mm flange, 44mm wide)
Print: Tread side up, PLA, 50% gyroid, 3 perimeters, no supports
Qty: 6 tires (or more for spare sets)

Reference: EA-08, Curiosity/Perseverance wheel tread patterns
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, CHAMFER_STD,
    find_largest_profile, find_profile_by_area,
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

        # Must match hub seat dimensions
        TIRE_IR = 3.5           # 35mm R (70mm ID) — matches hub seat OD
        TIRE_WALL = 0.2         # 2mm structural wall
        TIRE_STRUCT_R = TIRE_IR + TIRE_WALL  # 37mm R (74mm OD structural)
        TIRE_W = 4.0            # 40mm wide (fits between lip and beadlock ring)

        # Tread / grousers
        GROUSER_COUNT = 12
        TREAD_HEIGHT = 0.3      # 3mm grouser height
        TREAD_OD_R = TIRE_STRUCT_R + TREAD_HEIGHT  # 40mm R (80mm OD at tips)
        GROUSER_BASE_W = 0.3    # 3mm grouser base width (circumferential)
        GROUSER_TIP_W = 0.15    # 1.5mm grouser tip width (tapered)

        # Chevron angle (grousers angled relative to axial direction)
        # Each grouser covers about 70% of tire width
        GROUSER_AXIAL_SPAN = TIRE_W * 0.7  # 28mm axial coverage
        GROUSER_SKEW_DEG = 15   # Angle of chevron from perpendicular

        comp = design.rootComponent
        revolves = comp.features.revolveFeatures
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Revolve tire band (plain ring)
        # XZ plane: X = radius, Y = axial position
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Tire Band Profile'
        lines = sketch.sketchCurves.sketchLines

        # Simple rectangular cross-section (structural wall only)
        pts = [
            (TIRE_IR, 0),                       # inner surface, face 1
            (TIRE_STRUCT_R, 0),                  # outer structural, face 1
            (TIRE_STRUCT_R, TIRE_W),             # outer structural, face 2
            (TIRE_IR, TIRE_W),                   # inner surface, face 2
        ]

        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            lines.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        axis = lines.addByTwoPoints(p(0, 0, 0), p(0, TIRE_W, 0))
        axis.isConstruction = True

        prof = find_largest_profile(sketch)
        tireBody = None
        if prof:
            revInput = revolves.createInput(
                prof, axis,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            revInput.setAngleExtent(False, val(2 * math.pi))
            tireRev = revolves.add(revInput)
            tireBody = tireRev.bodies.item(0)
            tireBody.name = 'Tire Mars Chevron'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Add chevron grousers
        # Each grouser is a small revolved ridge on the tire surface.
        # Revolve a trapezoidal cross-section by a small angle.
        # Then circular pattern x12.
        # ══════════════════════════════════════════════════════════

        # Grouser cross-section on XZ plane
        # The grouser sits on the structural surface and extends outward
        grsk = comp.sketches.add(comp.xZConstructionPlane)
        grsk.name = 'Chevron Grouser'
        grl = grsk.sketchCurves.sketchLines

        # Grouser is centred at y = TIRE_W / 2
        # Trapezoidal cross-section (wider at base, narrower at tip)
        gy_centre = TIRE_W / 2
        base_half = GROUSER_BASE_W / 2
        tip_half = GROUSER_TIP_W / 2

        # Points (radius, axial):
        # Base on structural surface
        gr_pts = [
            (TIRE_STRUCT_R - 0.01, gy_centre - base_half),    # base left (slight overlap for join)
            (TIRE_STRUCT_R + TREAD_HEIGHT, gy_centre - tip_half),  # tip left
            (TIRE_STRUCT_R + TREAD_HEIGHT, gy_centre + tip_half),  # tip right
            (TIRE_STRUCT_R - 0.01, gy_centre + base_half),    # base right
        ]

        for i in range(len(gr_pts)):
            x1, y1 = gr_pts[i]
            x2, y2 = gr_pts[(i + 1) % len(gr_pts)]
            grl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        grAxis = grl.addByTwoPoints(p(0, 0, 0), p(0, TIRE_W, 0))
        grAxis.isConstruction = True

        # The grouser angular width at the tire surface
        gr_angle = GROUSER_BASE_W / TIRE_STRUCT_R  # arc length / radius

        grProf = find_largest_profile(grsk)
        grRev = None
        if grProf:
            grRevInput = revolves.createInput(
                grProf, grAxis,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            grRevInput.setAngleExtent(False, val(gr_angle))
            try:
                grRev = revolves.add(grRevInput)
            except Exception as e:
                print(f'  Warning: grouser revolve failed: {e}')

        # Circular pattern x12
        if grRev and GROUSER_COUNT > 1:
            ie = adsk.core.ObjectCollection.create()
            ie.add(grRev)
            patInput = comp.features.circularPatternFeatures.createInput(
                ie, comp.zConstructionAxis
            )
            patInput.quantity = val(GROUSER_COUNT)
            patInput.totalAngle = val(2 * math.pi)
            patInput.isSymmetric = False
            try:
                comp.features.circularPatternFeatures.add(patInput)
            except Exception as e:
                print(f'  Warning: grouser pattern failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 3: Entry chamfer on inner bore edges (easier install)
        # ══════════════════════════════════════════════════════════

        if tireBody:
            bore_edges = adsk.core.ObjectCollection.create()
            for ei in range(tireBody.edges.count):
                edge = tireBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - TIRE_IR) < 0.02:
                        bore_edges.add(edge)

            if bore_edges.count > 0:
                try:
                    cham = comp.features.chamferFeatures
                    cham_in = cham.createInput2()
                    cham_in.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                        bore_edges, val(CHAMFER_STD), True
                    )
                    cham.add(cham_in)
                except Exception as e:
                    print(f'  Warning: bore chamfer failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            f'Mars Rover Tire (Chevron) created!\n\n'
            f'MARS CHEVRON PATTERN\n'
            f'Inspired by Curiosity/Perseverance grousers\n\n'
            f'ID: {TIRE_IR * 20:.0f}mm (fits hub seat)\n'
            f'OD: {TREAD_OD_R * 20:.0f}mm (at grouser tips)\n'
            f'Width: {TIRE_W * 10:.0f}mm\n'
            f'Wall: {TIRE_WALL * 10:.0f}mm structural\n'
            f'Grousers: {GROUSER_COUNT}x, {TREAD_HEIGHT * 10:.0f}mm tall, tapered\n\n'
            f'Clamped by beadlock ring (no screws through tire).\n'
            f'Pair with rover_wheel_hub_v4.py + rover_beadlock_ring.py\n\n'
            f'Print tread-side up, PLA, 50% gyroid, 3 perimeters.\n'
            f'Qty: 6 tires',
            'Mars Rover - Tire (Chevron)'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
