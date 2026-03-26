"""
Mars Rover Tire — Off-Road Deep Lugs
=====================================

Interchangeable tire band with deep rectangular lugs.
Self-cleaning gaps between lugs for mud and wet grass.

Geometry:
  - 70mm ID x 82mm OD x 40mm wide
  - 2mm structural wall (70mm to 74mm)
  - 8x deep rectangular lugs, 4mm tall, 6mm wide (circumferential)
  - 2mm lateral channels between lugs for self-cleaning

Fits: rover_wheel_hub_v4.py (70mm seat OD, 74mm flange, 44mm wide)
Print: Tread side up, PLA, 50% gyroid, 4 perimeters, no supports
Qty: 6 tires

Reference: EA-08, off-road tire design principles
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
        # DIMENSIONS (cm)
        # ══════════════════════════════════════════════════════════

        TIRE_IR = 3.5           # 35mm R (70mm ID)
        TIRE_WALL = 0.2         # 2mm structural wall
        TIRE_STRUCT_R = TIRE_IR + TIRE_WALL  # 37mm R (74mm)

        TIRE_W = 4.0            # 40mm wide

        LUG_COUNT = 8
        LUG_HEIGHT = 0.4        # 4mm lug height (taller than chevron)
        TREAD_OD_R = TIRE_STRUCT_R + LUG_HEIGHT  # 41mm R (82mm OD)
        LUG_CIRC_W = 0.6        # 6mm circumferential width
        LUG_AXIAL_W = TIRE_W * 0.85  # 34mm — lugs span 85% of width

        comp = design.rootComponent
        revolves = comp.features.revolveFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Revolve tire band
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Offroad Tire Profile'
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
            tireBody.name = 'Tire Offroad'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Add deep rectangular lugs
        # Each lug is a revolved block spanning most of tire width
        # ══════════════════════════════════════════════════════════

        lsk = comp.sketches.add(comp.xZConstructionPlane)
        lsk.name = 'Lug'
        ll = lsk.sketchCurves.sketchLines

        lug_y_start = (TIRE_W - LUG_AXIAL_W) / 2  # centred on tire
        lug_y_end = lug_y_start + LUG_AXIAL_W

        lug_pts = [
            (TIRE_STRUCT_R - 0.01, lug_y_start),
            (TIRE_STRUCT_R + LUG_HEIGHT, lug_y_start),
            (TIRE_STRUCT_R + LUG_HEIGHT, lug_y_end),
            (TIRE_STRUCT_R - 0.01, lug_y_end),
        ]

        for i in range(len(lug_pts)):
            x1, y1 = lug_pts[i]
            x2, y2 = lug_pts[(i + 1) % len(lug_pts)]
            ll.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        lugAxis = ll.addByTwoPoints(p(0, 0, 0), p(0, TIRE_W, 0))
        lugAxis.isConstruction = True

        lug_angle = LUG_CIRC_W / TIRE_STRUCT_R

        lugProf = find_largest_profile(lsk)
        lugRev = None
        if lugProf:
            lugRevInput = revolves.createInput(
                lugProf, lugAxis,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            lugRevInput.setAngleExtent(False, val(lug_angle))
            try:
                lugRev = revolves.add(lugRevInput)
            except Exception as e:
                print(f'  Warning: lug revolve failed: {e}')

        if lugRev and LUG_COUNT > 1:
            ie = adsk.core.ObjectCollection.create()
            ie.add(lugRev)
            patInput = comp.features.circularPatternFeatures.createInput(
                ie, comp.zConstructionAxis
            )
            patInput.quantity = val(LUG_COUNT)
            patInput.totalAngle = val(2 * math.pi)
            patInput.isSymmetric = False
            try:
                comp.features.circularPatternFeatures.add(patInput)
            except Exception as e:
                print(f'  Warning: lug pattern failed: {e}')

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
            f'Off-Road Tire created!\n\n'
            f'DEEP LUG PATTERN — Mud/Wet Grass\n\n'
            f'ID: {TIRE_IR * 20:.0f}mm | OD: {TREAD_OD_R * 20:.0f}mm\n'
            f'Width: {TIRE_W * 10:.0f}mm\n'
            f'Lugs: {LUG_COUNT}x, {LUG_HEIGHT * 10:.0f}mm tall, '
            f'{LUG_CIRC_W * 10:.0f}mm wide\n\n'
            f'Self-cleaning gaps between lugs.\n'
            f'Print tread-side up, PLA, 50% gyroid, 4 perimeters.\n'
            f'Qty: 6 tires',
            'Mars Rover - Tire (Off-Road)'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
