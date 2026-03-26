"""
Mars Rover Tire — Paddle (Sand/Loose Substrate)
================================================

Interchangeable tire band with full-width paddle scoops.
Designed for sand, snow, and very loose substrates.

Geometry:
  - 70mm ID x 84mm OD x 40mm wide
  - 2mm structural wall (70mm to 74mm)
  - 6x full-width paddles, 5mm tall, 4mm wide (circumferential)
  - Paddles span 100% of tire width for maximum scooping

Fits: rover_wheel_hub_v4.py (70mm seat OD, 74mm flange, 44mm wide)
Print: Tread side up, PLA, 50% gyroid, 4 perimeters, no supports
Qty: 6 tires

Reference: EA-08, paddle wheel design for loose terrain
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, CHAMFER_STD,
    find_largest_profile,
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
        # DIMENSIONS (cm)
        # ══════════════════════════════════════════════════════════

        TIRE_IR = 3.5           # 35mm R (70mm ID)
        TIRE_WALL = 0.2         # 2mm structural wall
        TIRE_STRUCT_R = TIRE_IR + TIRE_WALL  # 37mm R (74mm)

        TIRE_W = 4.0            # 40mm wide

        PADDLE_COUNT = 6
        PADDLE_HEIGHT = 0.5     # 5mm paddle height (tallest tread type)
        TREAD_OD_R = TIRE_STRUCT_R + PADDLE_HEIGHT  # 42mm R (84mm OD)
        PADDLE_CIRC_W = 0.4     # 4mm circumferential width

        comp = design.rootComponent
        revolves = comp.features.revolveFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Revolve tire band
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Paddle Tire Profile'
        lines = sketch.sketchCurves.sketchLines

        pts = [
            (TIRE_IR, 0),
            (TIRE_STRUCT_R, 0),
            (TIRE_STRUCT_R, TIRE_W),
            (TIRE_IR, TIRE_W),
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
            tireBody.name = 'Tire Paddle'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Add paddle scoops (full-width)
        # Each paddle spans the entire tire width
        # ══════════════════════════════════════════════════════════

        psk = comp.sketches.add(comp.xZConstructionPlane)
        psk.name = 'Paddle'
        pl = psk.sketchCurves.sketchLines

        paddle_pts = [
            (TIRE_STRUCT_R - 0.01, 0),
            (TIRE_STRUCT_R + PADDLE_HEIGHT, 0),
            (TIRE_STRUCT_R + PADDLE_HEIGHT, TIRE_W),
            (TIRE_STRUCT_R - 0.01, TIRE_W),
        ]

        for i in range(len(paddle_pts)):
            x1, y1 = paddle_pts[i]
            x2, y2 = paddle_pts[(i + 1) % len(paddle_pts)]
            pl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        pAxis = pl.addByTwoPoints(p(0, 0, 0), p(0, TIRE_W, 0))
        pAxis.isConstruction = True

        paddle_angle = PADDLE_CIRC_W / TIRE_STRUCT_R

        pProf = find_largest_profile(psk)
        pRev = None
        if pProf:
            pRevInput = revolves.createInput(
                pProf, pAxis,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            pRevInput.setAngleExtent(False, val(paddle_angle))
            try:
                pRev = revolves.add(pRevInput)
            except Exception as e:
                print(f'  Warning: paddle revolve failed: {e}')

        if pRev and PADDLE_COUNT > 1:
            ie = adsk.core.ObjectCollection.create()
            ie.add(pRev)
            patInput = comp.features.circularPatternFeatures.createInput(
                ie, comp.zConstructionAxis
            )
            patInput.quantity = val(PADDLE_COUNT)
            patInput.totalAngle = val(2 * math.pi)
            patInput.isSymmetric = False
            try:
                comp.features.circularPatternFeatures.add(patInput)
            except Exception as e:
                print(f'  Warning: paddle pattern failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 3: Bore chamfer
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

        zoom_fit(app)

        ui.messageBox(
            f'Paddle Tire created!\n\n'
            f'PADDLE PATTERN — Sand/Snow/Loose Substrate\n\n'
            f'ID: {TIRE_IR * 20:.0f}mm | OD: {TREAD_OD_R * 20:.0f}mm\n'
            f'Width: {TIRE_W * 10:.0f}mm\n'
            f'Paddles: {PADDLE_COUNT}x, {PADDLE_HEIGHT * 10:.0f}mm tall, full-width\n\n'
            f'Maximum scooping action for loose terrain.\n'
            f'Print tread-side up, PLA, 50% gyroid, 4 perimeters.\n'
            f'Qty: 6 tires',
            'Mars Rover - Tire (Paddle)'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
