"""
Mars Rover Wheel V3 — Phase 1 (0.4 Scale) — 5-Spoke Jakkra-Style
==================================================================

80mm OD × 44mm wide PLA wheel rim with 5 chunky spokes.
Designed for PLA strength at 0.4 scale — inspired by jakkra/Mars-Rover.

Redesigned with:
  - Fillets at spoke-rim and spoke-hub intersections
  - Hub boss fillet (blend into disc face)
  - Grub screw entry chamfer
  - Smoother spoke void profile (avoids sharp stress risers)

Geometry:
  - 80mm OD at lip peaks, 75mm seat OD (tire channel between lips), 44mm wide
  - 5 solid spokes from hub to rim inner wall (70mm ID)
  - 2.5mm rim wall, 2mm lip width each side, 2.5mm lip height
  - 14mm OD hub boss with 3.1mm D-shaft bore (N20 motor)
  - M2 grub screw through hub for shaft retention

Two modes (USE_TPU_TIRE toggle):
  True  → Stepped rim with tire channel (75mm seat + 80mm lips)
  False → 80mm OD flat rim with O-ring grooves + grousers (fallback)

Print: Hub face down, PLA, 50% gyroid, 4 perimeters, no supports
Qty: 6 wheels

Reference: EA-08, EA-25 (suspension audit), jakkra/Mars-Rover
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD,
    find_largest_profile, find_profile_by_area, find_smallest_profile,
    make_offset_plane, zoom_fit,
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

        # ── Mode Toggle ──
        # False = PLA wheel with O-ring grooves (Phase 1 CTC Bizer). True = TPU tire version.
        USE_TPU_TIRE = False

        # ── Dimensions (cm — Fusion API unit) ──
        WHEEL_R = 4.0           # 40mm radius (80mm OD at lip peaks)
        SEAT_R = 3.75           # 37.5mm radius (75mm seat OD for tire)
        WHEEL_W = 4.4           # 44mm width (NASA-proportioned)
        LIP_W = 0.2             # 2mm lip width (axial)
        RIM_WALL = 0.25         # 2.5mm rim wall thickness
        RIM_INNER_R = SEAT_R - RIM_WALL  # 35mm radius (70mm inner dia)

        # Hub
        HUB_R = 0.7             # 7mm radius (14mm OD)
        HUB_BOSS_L = 0.8        # 8mm boss protrusion
        SHAFT_R = 0.155         # 1.55mm radius (3.1mm bore for N20 D-shaft)
        D_FLAT_DEPTH = 0.05     # 0.5mm D-flat depth

        # Spokes
        SPOKE_COUNT = 5
        SPOKE_FRACTION = 0.45   # Spokes occupy 45% of arc, voids 55%
        SPOKE_ANGLE = (2 * math.pi / SPOKE_COUNT) * SPOKE_FRACTION
        VOID_ANGLE = (2 * math.pi / SPOKE_COUNT) * (1 - SPOKE_FRACTION)

        # Grub screw
        GRUB_R = 0.1            # M2 (2mm dia)
        GRUB_DEPTH = 0.5        # 5mm deep

        # O-ring grooves (fallback mode only)
        ORING_GROOVE_W = 0.35   # 3.5mm width
        ORING_GROOVE_D = 0.2    # 2mm depth
        ORING_COUNT = 3
        GROUSER_DEPTH = 0.3     # 3mm
        GROUSER_WIDTH = 0.3     # 3mm
        GROUSER_COUNT = 12

        # Fillets
        SPOKE_FILLET = 0.1      # 1mm fillet at spoke intersections
        HUB_FILLET = 0.08       # 0.8mm fillet at hub-disc junction

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures
        revolves = comp.features.revolveFeatures
        fillets = comp.features.filletFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Revolve full solid wheel body
        # Profile on XZ plane: closed polygon from bore to OD
        # X = radius, Y = axial position (height of revolve)
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Wheel Profile'
        lines = sketch.sketchCurves.sketchLines

        if USE_TPU_TIRE:
            # Stepped profile: lips at 80mm, seat at 75mm
            pts = [
                (SHAFT_R, 0),                    # p1: bore, face 1
                (WHEEL_R, 0),                    # p2: lip 1 outer
                (WHEEL_R, LIP_W),                # p3: lip 1 end
                (SEAT_R, LIP_W),                 # p4: seat start
                (SEAT_R, WHEEL_W - LIP_W),       # p5: seat end
                (WHEEL_R, WHEEL_W - LIP_W),      # p6: lip 2 start
                (WHEEL_R, WHEEL_W),              # p7: lip 2 outer
                (SHAFT_R, WHEEL_W),              # p8: bore, face 2
            ]
        else:
            # Flat profile: full 80mm OD (no lips)
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

        # Revolve axis along Y (axial direction)
        axis = lines.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
        axis.isConstruction = True

        prof = find_largest_profile(sketch)
        wheelBody = None
        if prof:
            revInput = revolves.createInput(
                prof, axis,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            revInput.setAngleExtent(False, val(2 * math.pi))
            wheelRev = revolves.add(revInput)
            wheelBody = wheelRev.bodies.item(0)
            wheelBody.name = 'Wheel V3'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Cut 5 spoke voids
        # Each void is a sector from HUB_R to RIM_INNER_R
        # Sketch on XY plane (face 1), extrude through full width
        # ══════════════════════════════════════════════════════════

        void_start = SPOKE_ANGLE / 2

        voidSketch = comp.sketches.add(comp.xYConstructionPlane)
        voidSketch.name = 'Spoke Void'
        vl = voidSketch.sketchCurves.sketchLines
        va = voidSketch.sketchCurves.sketchArcs

        a1 = void_start
        a2 = void_start + VOID_ANGLE

        # Four corners of the sector void
        hi1 = p(HUB_R * math.cos(a1), HUB_R * math.sin(a1), 0)
        hi2 = p(HUB_R * math.cos(a2), HUB_R * math.sin(a2), 0)
        ro1 = p(RIM_INNER_R * math.cos(a1), RIM_INNER_R * math.sin(a1), 0)
        ro2 = p(RIM_INNER_R * math.cos(a2), RIM_INNER_R * math.sin(a2), 0)

        # Radial lines (spoke edges)
        vl.addByTwoPoints(hi1, ro1)
        vl.addByTwoPoints(hi2, ro2)

        # Arcs
        center = p(0, 0, 0)
        va.addByCenterStartSweep(center, hi1, VOID_ANGLE)
        va.addByCenterStartSweep(center, ro2, -VOID_ANGLE)

        # Find the void profile
        targetArea = 0.5 * VOID_ANGLE * (RIM_INNER_R**2 - HUB_R**2)
        voidProf = find_profile_by_area(voidSketch, targetArea)

        voidCut = None
        if voidProf:
            cutInput = extrudes.createInput(
                voidProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            cutInput.setDistanceExtent(True, val(WHEEL_W + 0.05))  # -Z direction into wheel body
            try:
                voidCut = extrudes.add(cutInput)
            except Exception as e:
                print(f'  Warning: spoke void cut failed: {e}')

        # Circular pattern the void cut × 5
        if voidCut and SPOKE_COUNT > 1:
            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(voidCut)
            patterns = comp.features.circularPatternFeatures
            patInput = patterns.createInput(inputEntities, comp.zConstructionAxis)
            patInput.quantity = val(SPOKE_COUNT)
            patInput.totalAngle = val(2 * math.pi)
            patInput.isSymmetric = False
            try:
                patterns.add(patInput)
            except Exception as e:
                print(f'  Warning: circular pattern failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 3: Hub boss protrusion (extends inward from face 1)
        # ══════════════════════════════════════════════════════════

        hubSketch = comp.sketches.add(comp.xZConstructionPlane)
        hubSketch.name = 'Hub Boss'
        hl = hubSketch.sketchCurves.sketchLines

        hub_pts = [
            (SHAFT_R, -HUB_BOSS_L),
            (HUB_R, -HUB_BOSS_L),
            (HUB_R, 0),
            (SHAFT_R, 0),
        ]
        for i in range(len(hub_pts)):
            x1, y1 = hub_pts[i]
            x2, y2 = hub_pts[(i + 1) % len(hub_pts)]
            hl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        hubAxis = hl.addByTwoPoints(p(0, -HUB_BOSS_L, 0), p(0, 0, 0))
        hubAxis.isConstruction = True

        hubProf = find_largest_profile(hubSketch)
        if hubProf:
            hubRevInput = revolves.createInput(
                hubProf, hubAxis,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            hubRevInput.setAngleExtent(False, val(2 * math.pi))
            try:
                revolves.add(hubRevInput)
            except Exception as e:
                print(f'  Warning: hub boss revolve failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: D-flat cut on shaft bore
        # ══════════════════════════════════════════════════════════

        dflatSketch = comp.sketches.add(comp.xZConstructionPlane)
        dflatSketch.name = 'D-Flat'
        dfl = dflatSketch.sketchCurves.sketchLines

        flat_x = SHAFT_R - D_FLAT_DEPTH
        dfl.addByTwoPoints(p(flat_x, -HUB_BOSS_L - 0.01, 0),
                           p(SHAFT_R + 0.01, -HUB_BOSS_L - 0.01, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, -HUB_BOSS_L - 0.01, 0),
                           p(SHAFT_R + 0.01, WHEEL_W + 0.01, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, WHEEL_W + 0.01, 0),
                           p(flat_x, WHEEL_W + 0.01, 0))
        dfl.addByTwoPoints(p(flat_x, WHEEL_W + 0.01, 0),
                           p(flat_x, -HUB_BOSS_L - 0.01, 0))

        dflatAxis = dfl.addByTwoPoints(p(0, -HUB_BOSS_L - 0.01, 0),
                                       p(0, WHEEL_W + 0.01, 0))
        dflatAxis.isConstruction = True

        dflatProf = find_smallest_profile(dflatSketch)
        if dflatProf:
            dflat_angle = 1.05  # ~60° angular sweep for D-flat
            dflatRevInput = revolves.createInput(
                dflatProf, dflatAxis,
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            dflatRevInput.setAngleExtent(False, val(dflat_angle))
            try:
                revolves.add(dflatRevInput)
            except Exception as e:
                print(f'  Warning: D-flat revolve failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5: M2 grub screw hole through hub wall
        # ══════════════════════════════════════════════════════════

        grub_y = WHEEL_W / 2
        grubPlane = make_offset_plane(comp, comp.xZConstructionPlane, grub_y)

        grubSketch = comp.sketches.add(grubPlane)
        grubSketch.name = 'Grub Screw'
        grubSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(HUB_R, 0, 0), GRUB_R
        )

        grubProf = find_smallest_profile(grubSketch)
        if grubProf:
            grubInput = extrudes.createInput(
                grubProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            grubInput.setDistanceExtent(True, val(GRUB_DEPTH))
            try:
                extrudes.add(grubInput)
            except Exception as e:
                print(f'  Warning: grub screw cut failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5b: Grub screw entry chamfer
        # ══════════════════════════════════════════════════════════

        if wheelBody:
            grub_edges = adsk.core.ObjectCollection.create()
            for ei in range(wheelBody.edges.count):
                edge = wheelBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - GRUB_R) < 0.02:
                        # Only the outer entry edge
                        bb = edge.boundingBox
                        mid_x = (bb.minPoint.x + bb.maxPoint.x) / 2
                        if abs(mid_x - HUB_R) < 0.05:
                            grub_edges.add(edge)

            if grub_edges.count > 0:
                try:
                    cham = comp.features.chamferFeatures
                    cham_in = cham.createInput2()
                    cham_in.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                        grub_edges, val(CHAMFER_STD), True
                    )
                    cham.add(cham_in)
                except Exception as e:
                    print(f'  Warning: grub chamfer failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 6: O-ring grooves + grousers (fallback mode only)
        # ══════════════════════════════════════════════════════════

        if not USE_TPU_TIRE:
            # O-ring grooves
            groove_spacing = WHEEL_W / (ORING_COUNT + 1)
            for gi in range(ORING_COUNT):
                gy = groove_spacing * (gi + 1)
                gsk = comp.sketches.add(comp.xZConstructionPlane)
                gsk.name = f'O-Ring Groove {gi + 1}'
                gl = gsk.sketchCurves.sketchLines

                g_y1 = gy - ORING_GROOVE_W / 2
                g_y2 = gy + ORING_GROOVE_W / 2

                gl.addByTwoPoints(p(WHEEL_R - ORING_GROOVE_D, g_y1, 0),
                                  p(WHEEL_R, g_y1, 0))
                gl.addByTwoPoints(p(WHEEL_R, g_y1, 0), p(WHEEL_R, g_y2, 0))
                gl.addByTwoPoints(p(WHEEL_R, g_y2, 0),
                                  p(WHEEL_R - ORING_GROOVE_D, g_y2, 0))
                gl.addByTwoPoints(p(WHEEL_R - ORING_GROOVE_D, g_y2, 0),
                                  p(WHEEL_R - ORING_GROOVE_D, g_y1, 0))

                gAxis = gl.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
                gAxis.isConstruction = True

                gProf = gsk.profiles.item(0)
                gRevInput = revolves.createInput(
                    gProf, gAxis,
                    adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                gRevInput.setAngleExtent(False, val(2 * math.pi))
                revolves.add(gRevInput)

            # Grousers (one + circular pattern)
            grsk = comp.sketches.add(comp.xZConstructionPlane)
            grsk.name = 'Grouser'
            grl = grsk.sketchCurves.sketchLines

            grl.addByTwoPoints(p(WHEEL_R - 0.01, 0, 0),
                              p(WHEEL_R + GROUSER_DEPTH, 0, 0))
            grl.addByTwoPoints(p(WHEEL_R + GROUSER_DEPTH, 0, 0),
                              p(WHEEL_R + GROUSER_DEPTH, WHEEL_W, 0))
            grl.addByTwoPoints(p(WHEEL_R + GROUSER_DEPTH, WHEEL_W, 0),
                              p(WHEEL_R - 0.01, WHEEL_W, 0))
            grl.addByTwoPoints(p(WHEEL_R - 0.01, WHEEL_W, 0),
                              p(WHEEL_R - 0.01, 0, 0))

            grAxis = grl.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
            grAxis.isConstruction = True

            grProf = grsk.profiles.item(0)
            gr_angle = GROUSER_WIDTH / WHEEL_R
            grRevInput = revolves.createInput(
                grProf, grAxis,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            grRevInput.setAngleExtent(False, val(gr_angle))
            grRev = revolves.add(grRevInput)

            if GROUSER_COUNT > 1:
                ie = adsk.core.ObjectCollection.create()
                ie.add(grRev)
                patInput = comp.features.circularPatternFeatures.createInput(
                    ie, comp.zConstructionAxis
                )
                patInput.quantity = val(GROUSER_COUNT)
                patInput.totalAngle = val(2 * math.pi)
                patInput.isSymmetric = False
                comp.features.circularPatternFeatures.add(patInput)

        # ══════════════════════════════════════════════════════════
        # STEP 7: Fillets — spoke edges and hub boss
        # ══════════════════════════════════════════════════════════

        if wheelBody:
            # Fillet linear (spoke) edges
            spoke_edges = adsk.core.ObjectCollection.create()
            for ei in range(wheelBody.edges.count):
                edge = wheelBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Line3D):
                    # Skip very short edges
                    if edge.length > 0.3:  # > 3mm
                        spoke_edges.add(edge)

            if spoke_edges.count > 0:
                try:
                    fillet_in = fillets.createInput()
                    fillet_in.addConstantRadiusEdgeSet(
                        spoke_edges, val(SPOKE_FILLET), True
                    )
                    fillets.add(fillet_in)
                except Exception as e:
                    print(f'  Warning: spoke fillet failed: {e}')

            # Hub boss fillet (blend into disc face)
            hub_edges = adsk.core.ObjectCollection.create()
            for ei in range(wheelBody.edges.count):
                edge = wheelBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - HUB_R) < 0.02:
                        # Hub outer edge at disc face
                        bb = edge.boundingBox
                        if abs(bb.minPoint.z) < 0.05:
                            hub_edges.add(edge)

            if hub_edges.count > 0:
                try:
                    hf_in = fillets.createInput()
                    hf_in.addConstantRadiusEdgeSet(
                        hub_edges, val(HUB_FILLET), True
                    )
                    fillets.add(hf_in)
                except Exception as e:
                    print(f'  Warning: hub fillet failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 8: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        if USE_TPU_TIRE:
            mode = 'TPU TIRE (75mm seat, 80mm lips — press-fit tire channel)'
            extra = (
                f'Seat OD: {SEAT_R * 20:.0f}mm (tire bore = 75mm)\n'
                f'Lip OD: {WHEEL_R * 20:.0f}mm (retention)\n'
                f'Lip width: {LIP_W * 10:.0f}mm each side\n'
                f'Lip height: {(WHEEL_R - SEAT_R) * 10:.1f}mm\n'
                f'Rim wall: {RIM_WALL * 10:.1f}mm\n\n'
                'Pair with rover_tire.py (75mm bore TPU tire).\n'
                'Tire stretches over lips into channel.\n'
                'Set USE_TPU_TIRE=False for O-ring fallback.'
            )
        else:
            mode = 'STANDALONE (O-rings + grousers, no tire)'
            extra = (
                f'O-ring grooves: {ORING_COUNT}× '
                f'({ORING_GROOVE_W * 10:.1f}mm × {ORING_GROOVE_D * 10:.0f}mm)\n'
                f'Grousers: {GROUSER_COUNT}× radial, '
                f'{GROUSER_DEPTH * 10:.0f}mm deep\n\n'
                'Fit 80mm ID × 3mm O-rings for traction.\n'
                'Set USE_TPU_TIRE=True for two-piece wheel.'
            )

        ui.messageBox(
            f'Mars Rover Wheel V3 created!\n\n'
            f'Mode: {mode}\n\n'
            f'OD: {WHEEL_R * 20:.0f}mm | Width: {WHEEL_W * 10:.0f}mm\n'
            f'Spokes: {SPOKE_COUNT} chunky (jakkra-style)\n'
            f'Hub: {HUB_R * 20:.0f}mm OD, {SHAFT_R * 20:.1f}mm D-shaft bore\n'
            f'Grub screw: M2 × {GRUB_DEPTH * 10:.0f}mm (chamfered entry)\n\n'
            f'FILLETS:\n'
            f'  Spoke edges: {SPOKE_FILLET*10:.0f}mm\n'
            f'  Hub boss: {HUB_FILLET*10:.1f}mm\n\n'
            f'{extra}\n\n'
            f'Print hub-side down, PLA, 50% gyroid, 4 perimeters.\n'
            f'Qty needed: 6 wheels',
            'Mars Rover - Wheel V3'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
