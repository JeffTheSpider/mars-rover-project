"""
Mars Rover Wheel Hub V4 — Two-Piece Design with Spiral Spokes
=============================================================

Structural hub/rim with 6 curved spiral spokes (Mars rover aesthetic).
Designed as part of a two-piece wheel system:
  - THIS SCRIPT: Hub/rim (PLA, structural)
  - rover_tire_*.py: Interchangeable tire bands (PLA or TPU)
  - rover_beadlock_ring.py: Retention ring (PLA)

Geometry:
  - 70mm OD tire seat (35mm R) with 74mm motor-side lip
  - 6 spiral spokes with 25deg twist from hub to rim (Perseverance-style)
  - 65mm rim inner diameter (32.5mm R), 2.5mm rim wall
  - 14mm OD hub boss with 3.1mm D-shaft bore (N20 motor)
  - M2 grub screw through hub for shaft retention
  - 4x M2 screw holes on open face for beadlock ring
  - 44mm total width (2mm motor lip + 40mm tire channel + 2mm ring face)

Assembly:
  1. Motor-side lip (permanent, 74mm OD) retains tire on one side
  2. Tire band (70mm ID) slides onto seat from open side
  3. Beadlock ring bolts to open face, clamping tire against lip

Print: Hub face down, PLA, 50% gyroid, 4 perimeters, no supports
Qty: 6 hubs

Reference: EA-08, EA-29, jakkra/Mars-Rover, Sawppy
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

        # ══════════════════════════════════════════════════════════
        # DIMENSIONS (cm — Fusion API unit)
        # ══════════════════════════════════════════════════════════

        # Rim / tire interface
        SEAT_R = 3.5            # 35mm R (70mm OD) — tire band sits here
        FLANGE_R = 3.7          # 37mm R (74mm OD) — motor-side lip height
        RIM_WALL = 0.25         # 2.5mm — rim wall thickness
        RIM_INNER_R = SEAT_R - RIM_WALL  # 32.5mm R (65mm ID)

        # Width
        WHEEL_W = 4.4           # 44mm total width
        LIP_W = 0.2             # 2mm motor-side lip width
        RING_FACE_W = 0.2       # 2mm open-side face for beadlock ring

        # Hub
        HUB_R = 0.7             # 7mm R (14mm OD)
        HUB_BOSS_L = 0.8        # 8mm boss protrusion (extends from motor face)
        SHAFT_R = 0.155         # 1.55mm R (3.1mm bore for N20 D-shaft)
        D_FLAT_DEPTH = 0.05     # 0.5mm D-flat depth

        # Spokes
        SPOKE_COUNT = 6
        SPOKE_FRACTION = 0.40   # Spokes occupy 40% of arc, voids 60%
        TWIST_DEG = 25          # Spoke twist angle from hub to rim
        TWIST_RAD = math.radians(TWIST_DEG)
        HUB_CLEAR_R = HUB_R + 0.1  # 8mm R clearance (void doesn't cut into hub)

        # Grub screw
        GRUB_R = 0.1            # M2 (2mm dia)
        GRUB_DEPTH = 0.5        # 5mm deep

        # Beadlock screw holes
        BEADLOCK_COUNT = 4
        BEADLOCK_HOLE_R = 0.11  # M2 clearance (2.2mm dia)
        BEADLOCK_POS_R = 3.375  # 33.75mm from centre (mid rim wall)
        BEADLOCK_DEPTH = 0.5    # 5mm pilot hole depth

        # Fillets
        SPOKE_FILLET = 0.1      # 1mm fillet at spoke-rim intersections
        HUB_FILLET = 0.08       # 0.8mm fillet at hub-disc junction
        LIP_FILLET = 0.05       # 0.5mm fillet on lip edge

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures
        revolves = comp.features.revolveFeatures
        fillets = comp.features.filletFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Revolve hub body — stepped profile for tire channel
        # XZ plane: sketch X = radius, sketch Y → -world Z
        # Revolve axis along Y → wheel axle along -Z
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Hub Profile'
        lines = sketch.sketchCurves.sketchLines

        # Profile points: (radius, axial position)
        # Y=0 = motor face, Y=WHEEL_W = open face
        pts = [
            (SHAFT_R, 0),                      # 1: bore, motor face
            (FLANGE_R, 0),                     # 2: motor lip outer edge
            (FLANGE_R, LIP_W),                 # 3: motor lip inner step
            (SEAT_R, LIP_W),                   # 4: seat start (after lip)
            (SEAT_R, WHEEL_W),                 # 5: seat end (open face)
            (SHAFT_R, WHEEL_W),                # 6: bore, open face
        ]

        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            lines.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        # Revolve axis along Y
        axis = lines.addByTwoPoints(p(0, 0, 0), p(0, WHEEL_W, 0))
        axis.isConstruction = True

        prof = find_largest_profile(sketch)
        hubBody = None
        if prof:
            revInput = revolves.createInput(
                prof, axis,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            revInput.setAngleExtent(False, val(2 * math.pi))
            hubRev = revolves.add(revInput)
            hubBody = hubRev.bodies.item(0)
            hubBody.name = 'Wheel Hub V4'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Cut 6 spiral spoke voids
        # Each void is bounded by 4 curves:
        #   - Inner arc at hub clearance radius
        #   - Outer arc at rim inner radius
        #   - Two spiral arcs (3-point) connecting hub to rim
        # ══════════════════════════════════════════════════════════

        sector = 2 * math.pi / SPOKE_COUNT
        spoke_half = sector * SPOKE_FRACTION / 2
        void_angle = sector * (1 - SPOKE_FRACTION)

        # First void: between spoke 0 and spoke 1
        void_start_hub = spoke_half
        void_end_hub = void_start_hub + void_angle
        void_start_rim = void_start_hub + TWIST_RAD
        void_end_rim = void_end_hub + TWIST_RAD

        def polar_xy(r, angle):
            """Convert polar to cartesian (x, y)."""
            return (r * math.cos(angle), r * math.sin(angle))

        # Four corner points of the void
        pA = polar_xy(HUB_CLEAR_R, void_start_hub)   # hub, left spoke edge
        pB = polar_xy(HUB_CLEAR_R, void_end_hub)     # hub, right spoke edge
        pC = polar_xy(RIM_INNER_R, void_end_rim)      # rim, right spoke edge
        pD = polar_xy(RIM_INNER_R, void_start_rim)    # rim, left spoke edge

        # Midpoints for spiral arcs (at middle radius, middle angle)
        mid_r = (HUB_CLEAR_R + RIM_INNER_R) / 2
        pAD_mid = polar_xy(mid_r, (void_start_hub + void_start_rim) / 2)
        pBC_mid = polar_xy(mid_r, (void_end_hub + void_end_rim) / 2)

        voidSketch = comp.sketches.add(comp.xYConstructionPlane)
        voidSketch.name = 'Spoke Void'
        arcs = voidSketch.sketchCurves.sketchArcs

        center = p(0, 0, 0)

        # 1. Hub arc: A → B (counterclockwise, void_angle sweep)
        arcs.addByCenterStartSweep(center, p(pA[0], pA[1], 0), void_angle)

        # 2. Right spiral edge: B → C (outward from hub to rim)
        arcs.addByThreePoints(
            p(pB[0], pB[1], 0),
            p(pBC_mid[0], pBC_mid[1], 0),
            p(pC[0], pC[1], 0)
        )

        # 3. Rim arc: C → D (clockwise, -void_angle sweep)
        arcs.addByCenterStartSweep(center, p(pC[0], pC[1], 0), -void_angle)

        # 4. Left spiral edge: D → A (inward from rim to hub)
        arcs.addByThreePoints(
            p(pD[0], pD[1], 0),
            p(pAD_mid[0], pAD_mid[1], 0),
            p(pA[0], pA[1], 0)
        )

        # Find the void profile (approximate sector area)
        target_area = 0.5 * void_angle * (RIM_INNER_R**2 - HUB_CLEAR_R**2)
        voidProf = find_profile_by_area(voidSketch, target_area)

        voidCut = None
        if voidProf:
            cutInput = extrudes.createInput(
                voidProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            # Cut through full wheel width (into -Z = body direction)
            cutInput.setDistanceExtent(True, val(WHEEL_W + 0.05))
            try:
                voidCut = extrudes.add(cutInput)
            except Exception as e:
                print(f'  Warning: spoke void cut failed: {e}')

        # Circular pattern the void × 6
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
        # STEP 3: Hub boss protrusion (extends from motor face)
        # ══════════════════════════════════════════════════════════

        hubSketch = comp.sketches.add(comp.xZConstructionPlane)
        hubSketch.name = 'Hub Boss'
        hl = hubSketch.sketchCurves.sketchLines

        hub_pts = [
            (SHAFT_R, -HUB_BOSS_L),    # bore at boss tip (+Z in world)
            (HUB_R, -HUB_BOSS_L),      # boss OD at tip
            (HUB_R, 0),                 # boss OD at motor face
            (SHAFT_R, 0),               # bore at motor face
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
        boss_start = -HUB_BOSS_L - 0.01
        open_end = WHEEL_W + 0.01

        dfl.addByTwoPoints(p(flat_x, boss_start, 0), p(SHAFT_R + 0.01, boss_start, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, boss_start, 0), p(SHAFT_R + 0.01, open_end, 0))
        dfl.addByTwoPoints(p(SHAFT_R + 0.01, open_end, 0), p(flat_x, open_end, 0))
        dfl.addByTwoPoints(p(flat_x, open_end, 0), p(flat_x, boss_start, 0))

        dflatAxis = dfl.addByTwoPoints(p(0, boss_start, 0), p(0, open_end, 0))
        dflatAxis.isConstruction = True

        dflatProf = find_smallest_profile(dflatSketch)
        if dflatProf:
            dflat_angle = 1.05  # ~60deg angular sweep for D-flat
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
        # Radial hole on XZ plane at axial midpoint (Z-negation: Y = WHEEL_W/2)
        # Extrude along Y (radial through hub wall)
        # ══════════════════════════════════════════════════════════

        grubSketch = comp.sketches.add(comp.xZConstructionPlane)
        grubSketch.name = 'Grub Screw'
        # XZ plane: sketch Y = -world Z. Axial midpoint Z = -WHEEL_W/2 → Y = WHEEL_W/2
        grubSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(HUB_R, WHEEL_W / 2, 0), GRUB_R
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

        if hubBody:
            grub_edges = adsk.core.ObjectCollection.create()
            for ei in range(hubBody.edges.count):
                edge = hubBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - GRUB_R) < 0.02:
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
        # STEP 6: Beadlock screw holes — through-holes in rim wall
        # Sketch on XY plane (perpendicular to wheel axis Z),
        # extrude symmetric to cut through full wheel width.
        # M2 through-holes at BEADLOCK_POS_R, screw self-taps into PLA.
        # ══════════════════════════════════════════════════════════

        blSketch = comp.sketches.add(comp.xYConstructionPlane)
        blSketch.name = 'Beadlock Holes'

        # First hole at 0deg on XY plane
        blSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(BEADLOCK_POS_R, 0, 0), BEADLOCK_HOLE_R
        )

        blProf = find_smallest_profile(blSketch)
        blCut = None
        if blProf:
            blInput = extrudes.createInput(
                blProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            # Symmetric through full wheel width (through-holes)
            blInput.setDistanceExtent(True, val(WHEEL_W + 0.1))
            try:
                blCut = extrudes.add(blInput)
            except Exception as e:
                print(f'  Warning: beadlock hole cut failed: {e}')

        # Circular pattern x4
        if blCut and BEADLOCK_COUNT > 1:
            blEntities = adsk.core.ObjectCollection.create()
            blEntities.add(blCut)
            blPatterns = comp.features.circularPatternFeatures
            blPatInput = blPatterns.createInput(blEntities, comp.zConstructionAxis)
            blPatInput.quantity = val(BEADLOCK_COUNT)
            blPatInput.totalAngle = val(2 * math.pi)
            blPatInput.isSymmetric = False
            try:
                blPatterns.add(blPatInput)
            except Exception as e:
                print(f'  Warning: beadlock pattern failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 7: Fillets
        # ══════════════════════════════════════════════════════════

        if hubBody:
            # Fillet on motor-side lip edge (outer circular edge at Z=0)
            lip_edges = adsk.core.ObjectCollection.create()
            for ei in range(hubBody.edges.count):
                edge = hubBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - FLANGE_R) < 0.02:
                        lip_edges.add(edge)

            if lip_edges.count > 0:
                try:
                    fillet_in = fillets.createInput()
                    fillet_in.addConstantRadiusEdgeSet(
                        lip_edges, val(LIP_FILLET), True
                    )
                    fillets.add(fillet_in)
                except Exception as e:
                    print(f'  Warning: lip fillet failed: {e}')

            # Hub boss fillet (blend into disc face)
            hub_edges = adsk.core.ObjectCollection.create()
            for ei in range(hubBody.edges.count):
                edge = hubBody.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - HUB_R) < 0.02:
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

        ui.messageBox(
            f'Mars Rover Wheel Hub V4 created!\n\n'
            f'TWO-PIECE DESIGN (hub + tire + beadlock ring)\n\n'
            f'Seat OD: {SEAT_R * 20:.0f}mm (tire bore = {SEAT_R * 20:.0f}mm)\n'
            f'Flange OD: {FLANGE_R * 20:.0f}mm (motor-side lip)\n'
            f'Rim inner: {RIM_INNER_R * 20:.0f}mm (spoke outer end)\n'
            f'Width: {WHEEL_W * 10:.0f}mm total\n'
            f'Spokes: {SPOKE_COUNT} spiral ({TWIST_DEG}deg twist)\n'
            f'Hub: {HUB_R * 20:.0f}mm OD, {SHAFT_R * 20:.1f}mm D-shaft bore\n'
            f'Grub screw: M2 x {GRUB_DEPTH * 10:.0f}mm\n'
            f'Beadlock: {BEADLOCK_COUNT}x M2 holes at {BEADLOCK_POS_R * 10:.1f}mm R\n\n'
            f'Pair with:\n'
            f'  rover_tire_mars.py (chevron grousers)\n'
            f'  rover_tire_smooth.py (indoor/pavement)\n'
            f'  rover_beadlock_ring.py (retention ring)\n\n'
            f'Print hub-side down, PLA, 50% gyroid, 4 perimeters.\n'
            f'Qty: 6 hubs',
            'Mars Rover - Wheel Hub V4'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
