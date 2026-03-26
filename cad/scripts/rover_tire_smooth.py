"""
Mars Rover Tire — Smooth (Indoor/Pavement)
===========================================

Interchangeable tire band with no tread pattern.
Maximum contact patch for hard, flat surfaces.

Geometry:
  - 70mm ID x 80mm OD x 40mm wide
  - 5mm solid wall (no grousers — full material to 80mm OD)
  - Chamfered bore edges for easy installation

Fits: rover_wheel_hub_v4.py (70mm seat OD, 74mm flange, 44mm wide)
Print: Flat, PLA, 50% gyroid, 3 perimeters, no supports
Qty: 6 tires

Reference: EA-08
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
        TIRE_OR = 4.0           # 40mm R (80mm OD) — full wall, no tread
        TIRE_W = 4.0            # 40mm wide

        comp = design.rootComponent
        revolves = comp.features.revolveFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Revolve smooth tire band
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Smooth Tire Profile'
        lines = sketch.sketchCurves.sketchLines

        pts = [
            (TIRE_IR, 0),
            (TIRE_OR, 0),
            (TIRE_OR, TIRE_W),
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
            tireBody.name = 'Tire Smooth'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Chamfer bore edges
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
            f'Smooth Tire created!\n\n'
            f'SMOOTH (no tread) — Indoor/Pavement\n\n'
            f'ID: {TIRE_IR * 20:.0f}mm | OD: {TIRE_OR * 20:.0f}mm\n'
            f'Width: {TIRE_W * 10:.0f}mm | Wall: {(TIRE_OR - TIRE_IR) * 10:.0f}mm\n\n'
            f'Print flat, PLA, 50% gyroid, 3 perimeters.\n'
            f'Qty: 6 tires',
            'Mars Rover - Tire (Smooth)'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
