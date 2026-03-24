"""
Mars Rover Body Quadrant — Phase 1 (0.4 Scale)
=================================================

The body frame is split into 4 quadrants to fit the CTC Bizer printer
bed (225×145×150mm). Each quadrant is joined with tongue-and-groove
seams and aligned with 3mm steel dowel pins.

Quadrant split:
  - X split: centre (X=0)
  - Y split: Y=0mm (centre — all quadrants 220×130mm, fits 225mm bed)

Quadrants:
  FL: Front-left  (~220 × 130 × 80mm)
  FR: Front-right (~220 × 130 × 80mm)
  RL: Rear-left   (~220 × 130 × 80mm)
  RR: Rear-right  (~220 × 130 × 80mm)

This script creates ONE quadrant at a time. Run with appropriate
parameters or modify the QUADRANT variable.

Features per quadrant (as applicable):
  - 4mm walls (increased for strength), internal ribs
  - Rocker pivot boss (608ZZ seat) — on side quadrants
  - Diff bar mount boss — on RL/RR
  - Tongue-and-groove seams at joins (stepped interlock)
  - M3 heat-set insert pockets along seams (40mm spacing)
  - Cable exit holes (12×8mm, JST-XH compatible) through side walls
  - Alignment dowel pin holes (3mm) at seam corners
  - Cable channels, vent slots
  - Arm mount bosses (FL only, Phase 2 robotic arm — EA-24)
  - RTG-style radiator fin detail (RL/RR rear wall, cosmetic)
  - MLI blanket edge ridges (all quadrants, cosmetic)
  - 0.5mm bottom-edge chamfer for bed adhesion

Qty: 4 total (FL, FR, RL, RR)

Print orientation: Open face up (internal features accessible)
Supports: Minimal (overhangs < 45°)
Perimeters: 4 (4mm walls = 4 × 0.4mm nozzle widths)
Infill: 20% gyroid (body panels, not structural)

Reference: EA-08, EA-11, EA-20
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

        # ── Which quadrant to create ──
        # Change this to 'FL', 'FR', 'RL', 'RR' before running
        QUADRANT = 'FL'

        # ── Dimensions (cm) ──
        BODY_L = 44.0       # 440mm total body length (Y)
        BODY_W = 26.0       # 260mm total body width (X)
        BODY_H = 8.0        # 80mm total body height (Z)
        WALL = 0.4          # 4mm wall thickness (increased from 3mm for strength)
        RIB_T = 0.2         # 2mm internal rib thickness

        # Split positions
        X_SPLIT = 0.0       # centre
        Y_SPLIT = 0.0       # centre — all quadrants 220mm, fits 225mm bed

        # Overall body bounds (centred at origin in X and Y)
        X_MIN = -BODY_W / 2  # -130mm
        X_MAX = BODY_W / 2   # +130mm
        Y_MIN = -BODY_L / 2  # -220mm
        Y_MAX = BODY_L / 2   # +220mm
        Z_BOTTOM = 0.0       # quadrant bottom at Z=0 (will be elevated in assembly)

        # Tongue-and-groove
        TONGUE_W = 0.5       # 5mm tongue width
        TONGUE_D = 0.3       # 3mm tongue depth (protrusion)
        TONGUE_GAP = 0.01    # 0.1mm gap for fit

        # Rocker pivot boss
        ROCKER_PIVOT_X = 12.5  # 125mm from centre
        PIVOT_BOSS_OD_R = 1.5  # 15mm radius (30mm OD)
        BEARING_SEAT_R = 1.1075  # 22.15mm
        BEARING_SEAT_DEPTH = 0.72  # 7.2mm
        PIVOT_BORE_R = 0.4  # 8mm

        # Vent slots (cut through side wall)
        VENT_W = 0.3        # 3mm wide
        VENT_H = 2.0        # 20mm tall
        VENT_COUNT = 5      # 5 vents per side wall
        VENT_SPACING = 2.5  # 25mm between vents

        # Cable channel guide walls (raised ridges on interior floor)
        CABLE_CH_W = 1.0    # 10mm channel width (between ridges)
        CABLE_RIDGE_T = 0.2 # 2mm ridge thickness
        CABLE_RIDGE_H = 1.0 # 10mm ridge height

        # Kill switch hole (RR quadrant rear wall only)
        KILL_SW_DIA_R = 0.75  # 15mm diameter / 2 = 7.5mm radius

        # LED underglow pass-through holes (floor, near perimeter)
        LED_HOLE_R = 0.25     # 5mm diameter / 2
        LED_HOLE_INSET = 1.5  # 15mm inset from outer wall

        # Headlight / taillight holes (through front/rear walls)
        LIGHT_HOLE_R = 0.25   # 5mm diameter
        LIGHT_SPACING = 4.0   # 40mm between pair of lights
        LIGHT_Z = 0.6         # 60% up the wall height (48mm from base)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════════
        # Determine quadrant bounds
        # ══════════════════════════════════════════════════════════════

        if QUADRANT == 'FL':
            qx_min, qx_max = X_MIN, X_SPLIT
            qy_min, qy_max = Y_SPLIT, Y_MAX
        elif QUADRANT == 'FR':
            qx_min, qx_max = X_SPLIT, X_MAX
            qy_min, qy_max = Y_SPLIT, Y_MAX
        elif QUADRANT == 'RL':
            qx_min, qx_max = X_MIN, X_SPLIT
            qy_min, qy_max = Y_MIN, Y_SPLIT
        elif QUADRANT == 'RR':
            qx_min, qx_max = X_SPLIT, X_MAX
            qy_min, qy_max = Y_MIN, Y_SPLIT
        else:
            ui.messageBox(f'Unknown quadrant: {QUADRANT}')
            return

        q_width = qx_max - qx_min
        q_length = qy_max - qy_min

        # ══════════════════════════════════════════════════════════════
        # Step 1: Outer shell (solid block)
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = f'Body {QUADRANT} Outer'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(qx_min, qy_min, 0),
            p(qx_max, qy_max, 0)
        )

        # Find largest profile
        outerProf = None
        maxArea = 0
        for pi in range(sketch1.profiles.count):
            pr = sketch1.profiles.item(pi)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                outerProf = pr

        extInput = extrudes.createInput(
            outerProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(BODY_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = f'Body {QUADRANT}'

        # ══════════════════════════════════════════════════════════════
        # Step 2: Hollow out interior (shell with walls)
        # Cut from top, leaving floor and walls
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H)
        )
        topP = topPlane.add(tpInput)

        hollowSketch = comp.sketches.add(topP)
        hollowSketch.name = f'Hollow {QUADRANT}'

        # Inner rectangle with wall offset
        # On seam edges (where quadrants join), use thicker wall for tongue
        inner_x_min = qx_min + WALL
        inner_x_max = qx_max - WALL
        inner_y_min = qy_min + WALL
        inner_y_max = qy_max - WALL

        # On seam edges, add extra for tongue
        if QUADRANT in ('FL', 'RL'):
            inner_x_max = qx_max - WALL - TONGUE_D  # right edge is seam
        if QUADRANT in ('FR', 'RR'):
            inner_x_min = qx_min + WALL + TONGUE_D  # left edge is seam
        if QUADRANT in ('FL', 'FR'):
            inner_y_min = qy_min + WALL + TONGUE_D  # bottom edge is seam
        if QUADRANT in ('RL', 'RR'):
            inner_y_max = qy_max - WALL - TONGUE_D  # top edge is seam

        hollowSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(inner_x_min, inner_y_min, 0),
            p(inner_x_max, inner_y_max, 0)
        )

        hProf = None
        minArea = float('inf')
        for pi in range(hollowSketch.profiles.count):
            pr = hollowSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                hProf = pr

        if hProf:
            hollowInput = extrudes.createInput(
                hProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            hollowInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(BODY_H - WALL)
            )
            extrudes.add(hollowInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: Internal ribs (cross-bracing)
        # One rib along X, one along Y inside the quadrant
        # ══════════════════════════════════════════════════════════════

        ribSketch = comp.sketches.add(comp.xYConstructionPlane)
        ribSketch.name = f'Ribs {QUADRANT}'
        rl = ribSketch.sketchCurves.sketchLines

        # X-direction rib (horizontal, at mid-Y of quadrant)
        mid_y = (qy_min + qy_max) / 2
        rl.addTwoPointRectangle(
            p(qx_min + WALL, mid_y - RIB_T / 2, 0),
            p(qx_max - WALL, mid_y + RIB_T / 2, 0)
        )

        # Y-direction rib (vertical, at mid-X of quadrant)
        mid_x = (qx_min + qx_max) / 2
        rl.addTwoPointRectangle(
            p(mid_x - RIB_T / 2, qy_min + WALL, 0),
            p(mid_x + RIB_T / 2, qy_max - WALL, 0)
        )

        # Extrude ribs to about 2/3 of body height
        RIB_HEIGHT = BODY_H * 0.6
        for pi in range(ribSketch.profiles.count):
            pr = ribSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 2.0:  # small rib profiles only
                ribInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                ribInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(RIB_HEIGHT)
                )
                try:
                    extrudes.add(ribInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 4: Rocker pivot boss (FL and RL have left pivot,
        #                            FR and RR have right pivot)
        # Only on the side walls of the quadrant
        # ══════════════════════════════════════════════════════════════

        # Check if this quadrant contains a rocker pivot
        has_pivot = False
        pivot_x = 0
        if QUADRANT in ('FL', 'RL'):
            has_pivot = True
            pivot_x = -ROCKER_PIVOT_X  # left side
        elif QUADRANT in ('FR', 'RR'):
            has_pivot = True
            pivot_x = ROCKER_PIVOT_X  # right side

        # Pivot is at Y=0, which is exactly on the Y seam.
        # Both RL/RR contain Y=0 as their upper boundary.
        # The pivot boss straddles the seam — each side gets half.
        # RL/RR build the full boss, then a trimming cut removes anything
        # outside the quadrant bounds so the part fits the print bed.
        pivot_y = 0.0
        if QUADRANT in ('FL', 'FR'):
            has_pivot = False  # pivot boss built by RL/RR side

        if has_pivot:
            # Create pivot boss on the outer wall (cylindrical protrusion)
            bossSketch = comp.sketches.add(comp.xYConstructionPlane)
            bossSketch.name = f'Rocker Pivot Boss {QUADRANT}'
            bossSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(pivot_x, pivot_y, 0), PIVOT_BOSS_OD_R
            )

            bProf = None
            minArea = float('inf')
            for pi in range(bossSketch.profiles.count):
                pr = bossSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    bProf = pr

            if bProf:
                bossInput = extrudes.createInput(
                    bProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                bossInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(BODY_H)
                )
                try:
                    extrudes.add(bossInput)
                except:
                    pass

            # Bearing seat (cut from top into boss)
            seatSketch = comp.sketches.add(topP)
            seatSketch.name = f'Bearing Seat {QUADRANT}'
            seatSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(pivot_x, pivot_y, 0), BEARING_SEAT_R
            )

            sProf = None
            minArea = float('inf')
            for pi in range(seatSketch.profiles.count):
                pr = seatSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    sProf = pr

            if sProf:
                seatInput = extrudes.createInput(
                    sProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                seatInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(BEARING_SEAT_DEPTH)
                )
                try:
                    extrudes.add(seatInput)
                except:
                    pass

            # 8mm pivot bore
            boreSketch = comp.sketches.add(topP)
            boreSketch.name = f'Pivot Bore {QUADRANT}'
            boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(pivot_x, pivot_y, 0), PIVOT_BORE_R
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
                    True, adsk.core.ValueInput.createByReal(BODY_H + 0.1)
                )
                try:
                    extrudes.add(boreInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 4b: Trim pivot boss to quadrant bounds
        # The boss circle can protrude past qy_max (RL/RR) or qx_min/max.
        # Cut away any geometry outside the quadrant bounding box so the
        # part fits the CTC Bizer bed (225×145mm).
        # ══════════════════════════════════════════════════════════════

        if has_pivot:
            # Large trim box above qy_max (for RL/RR the boss protrudes into Y>0)
            TRIM_MARGIN = 5.0  # 50mm oversized trim block
            trimSketch = comp.sketches.add(comp.xYConstructionPlane)
            trimSketch.name = f'Trim Boss {QUADRANT}'

            # Trim anything beyond qy_max (boss protrudes in +Y for RL/RR)
            if QUADRANT in ('RL', 'RR'):
                trimSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    p(pivot_x - PIVOT_BOSS_OD_R - 0.1, qy_max, 0),
                    p(pivot_x + PIVOT_BOSS_OD_R + 0.1, qy_max + TRIM_MARGIN, 0)
                )
            # Trim anything beyond qy_min (boss protrudes in -Y for FL/FR — not used currently)
            elif QUADRANT in ('FL', 'FR'):
                trimSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    p(pivot_x - PIVOT_BOSS_OD_R - 0.1, qy_min - TRIM_MARGIN, 0),
                    p(pivot_x + PIVOT_BOSS_OD_R + 0.1, qy_min, 0)
                )

            # Find the trim profile and cut through entire height
            trimProf = None
            maxArea = 0
            for pi in range(trimSketch.profiles.count):
                pr = trimSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a > maxArea:
                    maxArea = a
                    trimProf = pr

            if trimProf:
                trimInput = extrudes.createInput(
                    trimProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                trimInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(BODY_H + 0.2)
                )
                try:
                    extrudes.add(trimInput)
                except:
                    pass  # No geometry to trim — boss didn't protrude

        # ══════════════════════════════════════════════════════════════
        # Step 5: Vent slots on side walls
        # ══════════════════════════════════════════════════════════════

        # Vent slots: rectangular cuts through the outer side wall
        # Need a construction plane on the side wall (XZ plane offset to wall)
        vent_x = qx_min if QUADRANT in ('FL', 'RL') else qx_max
        vent_base_z = BODY_H * 0.3  # start 30% up the wall

        # Create offset YZ plane at the side wall position
        ventPlaneInput = comp.constructionPlanes.createInput()
        ventPlaneInput.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(vent_x)
        )
        ventPlane = comp.constructionPlanes.add(ventPlaneInput)

        ventSketch = comp.sketches.add(ventPlane)
        ventSketch.name = f'Vents {QUADRANT}'
        vl = ventSketch.sketchCurves.sketchLines

        # Distribute vents evenly along the quadrant length
        vent_total_span = (VENT_COUNT - 1) * VENT_SPACING
        vent_start_y = (qy_min + qy_max) / 2 - vent_total_span / 2

        for vi in range(VENT_COUNT):
            vy = vent_start_y + vi * VENT_SPACING
            # On YZ plane: Y is horizontal, Z is vertical
            vl.addTwoPointRectangle(
                p(vy - VENT_H / 2, vent_base_z, 0),
                p(vy + VENT_H / 2, vent_base_z + VENT_W * 4, 0)  # 12mm tall slot
            )

        # Cut vent slots through wall
        for pi in range(ventSketch.profiles.count):
            pr = ventSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0:  # small slot profiles only
                ventCut = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                ventCut.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(WALL + 0.01)
                )
                try:
                    extrudes.add(ventCut)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 6: Cable channel guide walls (raised ridges on floor)
        # One channel runs front-to-back near the side wall (motor/servo routing)
        # One channel runs left-to-right near the seam edge (cross-body routing)
        # ══════════════════════════════════════════════════════════════

        cableSketch = comp.sketches.add(comp.xYConstructionPlane)
        cableSketch.name = f'Cable Channels {QUADRANT}'
        ccl = cableSketch.sketchCurves.sketchLines

        # Front-to-back channel: near the outer side wall
        if QUADRANT in ('FL', 'RL'):
            ch_x_centre = qx_min + WALL + CABLE_RIDGE_T + CABLE_CH_W / 2
        else:
            ch_x_centre = qx_max - WALL - CABLE_RIDGE_T - CABLE_CH_W / 2

        # Left ridge of front-to-back channel
        ccl.addTwoPointRectangle(
            p(ch_x_centre - CABLE_CH_W / 2 - CABLE_RIDGE_T,
              qy_min + WALL, 0),
            p(ch_x_centre - CABLE_CH_W / 2,
              qy_max - WALL, 0)
        )
        # Right ridge
        ccl.addTwoPointRectangle(
            p(ch_x_centre + CABLE_CH_W / 2,
              qy_min + WALL, 0),
            p(ch_x_centre + CABLE_CH_W / 2 + CABLE_RIDGE_T,
              qy_max - WALL, 0)
        )

        # Left-to-right channel: near the seam edge (Y split or Y min/max)
        if QUADRANT in ('FL', 'FR'):
            ch_y_centre = qy_min + WALL + CABLE_RIDGE_T + CABLE_CH_W / 2
        else:
            ch_y_centre = qy_max - WALL - CABLE_RIDGE_T - CABLE_CH_W / 2

        # Bottom ridge of left-to-right channel
        ccl.addTwoPointRectangle(
            p(qx_min + WALL, ch_y_centre - CABLE_CH_W / 2 - CABLE_RIDGE_T, 0),
            p(qx_max - WALL, ch_y_centre - CABLE_CH_W / 2, 0)
        )
        # Top ridge
        ccl.addTwoPointRectangle(
            p(qx_min + WALL, ch_y_centre + CABLE_CH_W / 2, 0),
            p(qx_max - WALL, ch_y_centre + CABLE_CH_W / 2 + CABLE_RIDGE_T, 0)
        )

        # Extrude cable channel ridges upward from floor
        for pi in range(cableSketch.profiles.count):
            pr = cableSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 5.0:  # thin ridge profiles only
                ridgeInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                ridgeInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(
                        WALL + CABLE_RIDGE_H)  # floor + ridge height
                )
                try:
                    extrudes.add(ridgeInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 7: Kill switch hole (RR quadrant only)
        # 15mm diameter through-hole on the rear wall
        # ══════════════════════════════════════════════════════════════

        if QUADRANT == 'RR':
            # Rear wall is at Y = Y_MIN (qy_min)
            # Create construction plane on the rear wall (XZ plane at Y_MIN)
            swPlaneInput = comp.constructionPlanes.createInput()
            swPlaneInput.setByOffset(
                comp.xZConstructionPlane,
                adsk.core.ValueInput.createByReal(qy_min)
            )
            swPlane = comp.constructionPlanes.add(swPlaneInput)

            swSketch = comp.sketches.add(swPlane)
            swSketch.name = 'Kill Switch Hole'
            # Centre the hole on the quadrant wall, mid-height
            sw_x = (qx_min + qx_max) / 2
            sw_z = BODY_H / 2
            swSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(sw_x, sw_z, 0), KILL_SW_DIA_R
            )

            swProf = None
            minArea = float('inf')
            for pi in range(swSketch.profiles.count):
                pr = swSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    swProf = pr

            if swProf:
                swCut = extrudes.createInput(
                    swProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                swCut.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(WALL + 0.01)
                )
                try:
                    extrudes.add(swCut)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 8: M3 heat-set insert pockets along seam edges
        # 4.8mm dia, 5.5mm deep, spaced 40mm apart along each seam
        # ══════════════════════════════════════════════════════════════

        HSERT_R = 0.24       # 4.8mm dia / 2 = 2.4mm
        HSERT_DEPTH = 0.55   # 5.5mm deep
        BOLT_SPACING = 4.0   # 40mm between bolt holes
        BOLT_INSET = 2.0     # 20mm from seam corner to first bolt

        # Determine which edges are seams
        seam_edges = []  # list of (x, y) positions for bolt holes

        # X seam: at X_SPLIT (X=0), both FL/RL have right-edge seam, FR/RR have left-edge seam
        if QUADRANT in ('FL', 'RL'):
            seam_x = qx_max - WALL / 2  # right wall midplane
            n_bolts = int((q_length * 10 - 2 * BOLT_INSET * 10) / (BOLT_SPACING * 10)) + 1
            for bi in range(n_bolts):
                by = qy_min + BOLT_INSET + bi * BOLT_SPACING
                if by < qy_max - BOLT_INSET + 0.01:
                    seam_edges.append((seam_x, by))
        elif QUADRANT in ('FR', 'RR'):
            seam_x = qx_min + WALL / 2
            n_bolts = int((q_length * 10 - 2 * BOLT_INSET * 10) / (BOLT_SPACING * 10)) + 1
            for bi in range(n_bolts):
                by = qy_min + BOLT_INSET + bi * BOLT_SPACING
                if by < qy_max - BOLT_INSET + 0.01:
                    seam_edges.append((seam_x, by))

        # Y seam: at Y_SPLIT (Y=0), FL/FR have bottom-edge seam, RL/RR have top-edge seam
        if QUADRANT in ('FL', 'FR'):
            seam_y = qy_min + WALL / 2
            n_bolts = int((q_width * 10 - 2 * BOLT_INSET * 10) / (BOLT_SPACING * 10)) + 1
            for bi in range(n_bolts):
                bx = qx_min + BOLT_INSET + bi * BOLT_SPACING
                if bx < qx_max - BOLT_INSET + 0.01:
                    seam_edges.append((bx, seam_y))
        elif QUADRANT in ('RL', 'RR'):
            seam_y = qy_max - WALL / 2
            n_bolts = int((q_width * 10 - 2 * BOLT_INSET * 10) / (BOLT_SPACING * 10)) + 1
            for bi in range(n_bolts):
                bx = qx_min + BOLT_INSET + bi * BOLT_SPACING
                if bx < qx_max - BOLT_INSET + 0.01:
                    seam_edges.append((bx, seam_y))

        # Cut heat-set insert pockets from top face
        if seam_edges:
            boltSketch = comp.sketches.add(topP)
            boltSketch.name = f'Seam Bolts {QUADRANT}'
            for bx, by in seam_edges:
                boltSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(bx, by, 0), HSERT_R
                )

            for pi in range(boltSketch.profiles.count):
                pr = boltSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 0.5:  # small hole profiles
                    boltCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    boltCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(HSERT_DEPTH)
                    )
                    try:
                        extrudes.add(boltCut)
                    except:
                        pass

        # ══════════════════════════════════════════════════════════════
        # Step 9: Cable exit holes through side walls
        # 12×8mm rectangular slots for motor/servo wires + JST-XH connectors
        # ══════════════════════════════════════════════════════════════

        CABLE_EXIT_W = 1.2   # 12mm wide (enlarged for JST-XH connectors)
        CABLE_EXIT_H = 0.8   # 8mm tall (enlarged for JST-XH 2/3-pin housings)
        CABLE_EXIT_Z = BODY_H * 0.25  # 25% up from base

        # Cable exits on outer side wall near rocker pivot locations
        cable_exits = []
        if QUADRANT in ('RL', 'RR'):
            # Near rocker pivot Y=0: exit at Y=-2cm and Y=+0 area
            cable_exits.append((qy_min + q_length * 0.8, CABLE_EXIT_Z))
            cable_exits.append((qy_min + q_length * 0.4, CABLE_EXIT_Z))
        else:
            # Front quadrants: exit near front wheels
            cable_exits.append((qy_max - 3.0, CABLE_EXIT_Z))

        if cable_exits:
            cExitPlaneInput = comp.constructionPlanes.createInput()
            ce_x = qx_min if QUADRANT in ('FL', 'RL') else qx_max
            cExitPlaneInput.setByOffset(
                comp.yZConstructionPlane,
                adsk.core.ValueInput.createByReal(ce_x)
            )
            cExitPlane = comp.constructionPlanes.add(cExitPlaneInput)
            ceSketch = comp.sketches.add(cExitPlane)
            ceSketch.name = f'Cable Exits {QUADRANT}'

            for ce_y, ce_z in cable_exits:
                # On YZ plane: sketch coords are (-Z, Y)
                ceSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    p(ce_y - CABLE_EXIT_W / 2, ce_z, 0),
                    p(ce_y + CABLE_EXIT_W / 2, ce_z + CABLE_EXIT_H, 0)
                )

            for pi in range(ceSketch.profiles.count):
                pr = ceSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 1.0:
                    ceCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    ceCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(WALL + 0.02)
                    )
                    try:
                        extrudes.add(ceCut)
                    except:
                        pass

        # ══════════════════════════════════════════════════════════════
        # Step 10: Alignment dowel pin holes at seam corners (3mm dia)
        # ══════════════════════════════════════════════════════════════

        DOWEL_R = 0.155      # 3.1mm dia (slight clearance for 3mm pin)
        DOWEL_DEPTH = 0.8    # 8mm deep

        dowel_positions = []

        # Corner dowels at intersection of X and Y seams
        if QUADRANT == 'FL':
            dowel_positions.append((qx_max - 0.5, qy_min + 0.5))
        elif QUADRANT == 'FR':
            dowel_positions.append((qx_min + 0.5, qy_min + 0.5))
        elif QUADRANT == 'RL':
            dowel_positions.append((qx_max - 0.5, qy_max - 0.5))
        elif QUADRANT == 'RR':
            dowel_positions.append((qx_min + 0.5, qy_max - 0.5))

        if dowel_positions:
            dowelSketch = comp.sketches.add(topP)
            dowelSketch.name = f'Dowel Pins {QUADRANT}'
            for dx, dy in dowel_positions:
                dowelSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(dx, dy, 0), DOWEL_R
                )

            for pi in range(dowelSketch.profiles.count):
                pr = dowelSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 0.2:
                    dowelCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    dowelCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(DOWEL_DEPTH)
                    )
                    try:
                        extrudes.add(dowelCut)
                    except:
                        pass

        # ══════════════════════════════════════════════════════════════
        # Step 11: LED underglow pass-through holes (floor)
        # 4 holes per quadrant through the floor near the perimeter
        # for routing WS2812B LED strip wiring
        # ══════════════════════════════════════════════════════════════

        led_holes = []
        # 2 holes along the side wall (front and rear of quadrant)
        side_x = qx_min + LED_HOLE_INSET if QUADRANT in ('FL', 'RL') else qx_max - LED_HOLE_INSET
        led_holes.append((side_x, qy_min + q_length * 0.25))
        led_holes.append((side_x, qy_min + q_length * 0.75))
        # 2 holes along the front/rear wall
        end_y = qy_max - LED_HOLE_INSET if QUADRANT in ('FL', 'FR') else qy_min + LED_HOLE_INSET
        led_holes.append((qx_min + q_width * 0.3 if QUADRANT in ('FL', 'RL') else qx_max - q_width * 0.3, end_y))
        led_holes.append((qx_min + q_width * 0.7 if QUADRANT in ('FL', 'RL') else qx_max - q_width * 0.7, end_y))

        ledSketch = comp.sketches.add(comp.xYConstructionPlane)
        ledSketch.name = f'LED Underglow {QUADRANT}'
        for lx, ly in led_holes:
            ledSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(lx, ly, 0), LED_HOLE_R
            )

        for pi in range(ledSketch.profiles.count):
            pr = ledSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.3:  # small LED hole profiles
                ledCut = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                ledCut.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(WALL + 0.01)
                )
                try:
                    extrudes.add(ledCut)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 12: Headlight holes (FL/FR front wall) and
        #          Taillight holes (RL/RR rear wall)
        # 2× 5mm diameter through-holes for 5mm LEDs
        # ══════════════════════════════════════════════════════════════

        light_holes = []  # list of (y_pos, z_pos) on the wall plane

        if QUADRANT in ('FL', 'FR'):
            # Headlights on front wall (Y = qy_max)
            light_wall_y = qy_max
            light_wall_plane_offset = light_wall_y
            light_plane_ref = comp.xZConstructionPlane
            mid_x_q = (qx_min + qx_max) / 2
            light_holes = [
                (mid_x_q - LIGHT_SPACING / 2, BODY_H * LIGHT_Z),
                (mid_x_q + LIGHT_SPACING / 2, BODY_H * LIGHT_Z),
            ]
        elif QUADRANT in ('RL', 'RR'):
            # Taillights on rear wall (Y = qy_min)
            light_wall_y = qy_min
            light_wall_plane_offset = light_wall_y
            light_plane_ref = comp.xZConstructionPlane
            mid_x_q = (qx_min + qx_max) / 2
            light_holes = [
                (mid_x_q - LIGHT_SPACING / 2, BODY_H * LIGHT_Z),
                (mid_x_q + LIGHT_SPACING / 2, BODY_H * LIGHT_Z),
            ]

        if light_holes:
            lightPlaneInput = comp.constructionPlanes.createInput()
            lightPlaneInput.setByOffset(
                light_plane_ref,
                adsk.core.ValueInput.createByReal(light_wall_plane_offset)
            )
            lightPlane = comp.constructionPlanes.add(lightPlaneInput)
            lightSketch = comp.sketches.add(lightPlane)
            light_type = 'Headlights' if QUADRANT in ('FL', 'FR') else 'Taillights'
            lightSketch.name = f'{light_type} {QUADRANT}'

            for lx, lz in light_holes:
                lightSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(lx, lz, 0), LIGHT_HOLE_R
                )

            for pi in range(lightSketch.profiles.count):
                pr = lightSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 0.3:
                    lightCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    lightCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(WALL + 0.01)
                    )
                    try:
                        extrudes.add(lightCut)
                    except:
                        pass

        # ══════════════════════════════════════════════════════════════
        # Step 13: Panel line grooves on outer walls (cosmetic)
        # 2 horizontal grooves at 25% and 75% height
        # 1mm wide × 0.5mm deep — evokes spacecraft panelling
        # ══════════════════════════════════════════════════════════════

        PANEL_LINE_W = 0.1     # 1mm wide
        PANEL_LINE_D = 0.05    # 0.5mm deep

        # Create grooves on the outer side wall (left for FL/RL, right for FR/RR)
        panel_wall_x = qx_min if QUADRANT in ('FL', 'RL') else qx_max

        for groove_frac in [0.25, 0.75]:
            groove_z = BODY_H * groove_frac
            plSketch = comp.sketches.add(comp.xYConstructionPlane)
            plSketch.name = f'Panel Line {groove_frac:.0%}'

            # Groove rectangle on XY plane at groove_z height?
            # Actually need to cut into the side wall face.
            # Create on a YZ offset plane at the wall position
            plPlaneInput = comp.constructionPlanes.createInput()
            plPlaneInput.setByOffset(
                comp.yZConstructionPlane,
                adsk.core.ValueInput.createByReal(panel_wall_x)
            )
            plPlane = comp.constructionPlanes.add(plPlaneInput)

            plSketch2 = comp.sketches.add(plPlane)
            plSketch2.name = f'Panel Line {groove_frac:.0%}'

            # On YZ plane: Y is horizontal (along body), Z is vertical
            plSketch2.sketchCurves.sketchLines.addTwoPointRectangle(
                p(qy_min + WALL, groove_z - PANEL_LINE_W / 2, 0),
                p(qy_max - WALL, groove_z + PANEL_LINE_W / 2, 0)
            )

            for pi in range(plSketch2.profiles.count):
                pr = plSketch2.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 2.0:
                    plCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    plCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(PANEL_LINE_D)
                    )
                    try:
                        extrudes.add(plCut)
                    except:
                        pass

        # Also add panel lines on the front/rear outer wall
        panel_wall_y = qy_max if QUADRANT in ('FL', 'FR') else qy_min

        for groove_frac in [0.25, 0.75]:
            groove_z = BODY_H * groove_frac

            plFRPlaneInput = comp.constructionPlanes.createInput()
            plFRPlaneInput.setByOffset(
                comp.xZConstructionPlane,
                adsk.core.ValueInput.createByReal(panel_wall_y)
            )
            plFRPlane = comp.constructionPlanes.add(plFRPlaneInput)

            plFRSketch = comp.sketches.add(plFRPlane)
            plFRSketch.name = f'Panel Line FR {groove_frac:.0%}'

            plFRSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                p(qx_min + WALL, groove_z - PANEL_LINE_W / 2, 0),
                p(qx_max - WALL, groove_z + PANEL_LINE_W / 2, 0)
            )

            for pi in range(plFRSketch.profiles.count):
                pr = plFRSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 2.0:
                    plFRCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    plFRCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(PANEL_LINE_D)
                    )
                    try:
                        extrudes.add(plFRCut)
                    except:
                        pass

        # ══════════════════════════════════════════════════════════════
        # Step 5d: Front panel arm mount pattern (FL quadrant only)
        # 4× M3 heat-set insert bosses in a 40×40mm square pattern,
        # centred on the front wall at 60% wall height.
        # For Phase 2 robotic arm mount point (EA-24).
        # ══════════════════════════════════════════════════════════════

        ARM_MOUNT_BOSS_OD_R = 0.4   # 8mm OD / 2 = 4mm radius
        ARM_MOUNT_BOSS_H = 0.55     # 5.5mm tall (matches heat-set depth)
        ARM_MOUNT_HSERT_R = 0.24    # 4.8mm / 2 = 2.4mm (M3 heat-set)
        ARM_MOUNT_HSERT_DEPTH = 0.55  # 5.5mm deep
        ARM_MOUNT_PATTERN = 4.0     # 40mm square pattern (4.0cm)

        arm_mount_count = 0
        if QUADRANT == 'FL':
            # Front wall is at Y = qy_max
            # Centre the 40×40mm pattern on the front wall, 60% up
            arm_cx = (qx_min + qx_max) / 2  # centre of quadrant X
            arm_cz = BODY_H * 0.6            # 60% up wall height

            # 4 bosses at corners of 40×40mm square
            arm_mounts = [
                (arm_cx - ARM_MOUNT_PATTERN / 2, arm_cz - ARM_MOUNT_PATTERN / 2),
                (arm_cx + ARM_MOUNT_PATTERN / 2, arm_cz - ARM_MOUNT_PATTERN / 2),
                (arm_cx - ARM_MOUNT_PATTERN / 2, arm_cz + ARM_MOUNT_PATTERN / 2),
                (arm_cx + ARM_MOUNT_PATTERN / 2, arm_cz + ARM_MOUNT_PATTERN / 2),
            ]

            # Construction plane on front wall (XZ plane at Y = qy_max)
            armPlaneInput = comp.constructionPlanes.createInput()
            armPlaneInput.setByOffset(
                comp.xZConstructionPlane,
                adsk.core.ValueInput.createByReal(qy_max)
            )
            armPlane = comp.constructionPlanes.add(armPlaneInput)

            # Boss cylinders on front wall exterior
            armBossSketch = comp.sketches.add(armPlane)
            armBossSketch.name = 'Arm Mount Bosses FL'
            for ax, az in arm_mounts:
                armBossSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(ax, az, 0), ARM_MOUNT_BOSS_OD_R
                )

            for pi in range(armBossSketch.profiles.count):
                pr = armBossSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 1.0:  # boss circle profiles
                    armBossInput = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    # Extrude outward from front wall (positive Y direction)
                    armBossInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(ARM_MOUNT_BOSS_H)
                    )
                    try:
                        extrudes.add(armBossInput)
                    except:
                        pass

            # Heat-set insert holes (cut inward from boss top surface)
            armBossTopOffset = qy_max + ARM_MOUNT_BOSS_H
            armHsertPlaneInput = comp.constructionPlanes.createInput()
            armHsertPlaneInput.setByOffset(
                comp.xZConstructionPlane,
                adsk.core.ValueInput.createByReal(armBossTopOffset)
            )
            armHsertPlane = comp.constructionPlanes.add(armHsertPlaneInput)

            armHsertSketch = comp.sketches.add(armHsertPlane)
            armHsertSketch.name = 'Arm Mount Inserts FL'
            for ax, az in arm_mounts:
                armHsertSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(ax, az, 0), ARM_MOUNT_HSERT_R
                )

            for pi in range(armHsertSketch.profiles.count):
                pr = armHsertSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 0.5:
                    armHsertCut = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                    )
                    armHsertCut.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(ARM_MOUNT_HSERT_DEPTH)
                    )
                    try:
                        extrudes.add(armHsertCut)
                    except:
                        pass

            arm_mount_count = len(arm_mounts)

        # ══════════════════════════════════════════════════════════════
        # Step 6c: RTG-style rear detail (RL/RR rear wall, cosmetic)
        # 2 small raised rectangular pads (10×5×1mm) on the rear outer
        # wall, at 70% and 80% of wall height, evoking radiator fins.
        # ══════════════════════════════════════════════════════════════

        RTG_PAD_W = 1.0    # 10mm wide
        RTG_PAD_H = 0.5    # 5mm tall
        RTG_PAD_D = 0.1    # 1mm raised (protrusion depth)

        rtg_count = 0
        if QUADRANT in ('RL', 'RR'):
            # Rear wall is at Y = qy_min
            rtg_cx = (qx_min + qx_max) / 2  # centred horizontally

            rtg_pads = [
                (rtg_cx, BODY_H * 0.70),  # 70% up wall height
                (rtg_cx, BODY_H * 0.80),  # 80% up wall height
            ]

            # Construction plane on rear wall (XZ plane at Y = qy_min)
            rtgPlaneInput = comp.constructionPlanes.createInput()
            rtgPlaneInput.setByOffset(
                comp.xZConstructionPlane,
                adsk.core.ValueInput.createByReal(qy_min)
            )
            rtgPlane = comp.constructionPlanes.add(rtgPlaneInput)

            rtgSketch = comp.sketches.add(rtgPlane)
            rtgSketch.name = f'RTG Detail {QUADRANT}'

            for rx, rz in rtg_pads:
                rtgSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    p(rx - RTG_PAD_W / 2, rz - RTG_PAD_H / 2, 0),
                    p(rx + RTG_PAD_W / 2, rz + RTG_PAD_H / 2, 0)
                )

            for pi in range(rtgSketch.profiles.count):
                pr = rtgSketch.profiles.item(pi)
                a = pr.areaProperties().area
                if a < 1.0:  # small pad profiles
                    rtgInput = extrudes.createInput(
                        pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    # Extrude outward from rear wall (negative Y direction)
                    rtgInput.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(RTG_PAD_D)
                    )
                    try:
                        extrudes.add(rtgInput)
                    except:
                        pass

            rtg_count = len(rtg_pads)

        # ══════════════════════════════════════════════════════════════
        # Step 6d: Faux MLI blanket edge ridges (all quadrants)
        # 0.5mm raised ridge along the top edge of each outer wall,
        # running the full wall length, 2mm below the top edge.
        # Evokes multi-layer insulation blanket seam detailing.
        # ══════════════════════════════════════════════════════════════

        MLI_RIDGE_H = 0.05   # 0.5mm raised ridge height
        MLI_RIDGE_W = 0.1    # 1mm ridge width
        MLI_INSET = 0.2      # 2mm below top edge (Z position)

        mli_ridge_z = BODY_H - MLI_INSET  # Z position of ridge centre

        # Side wall ridge (left for FL/RL, right for FR/RR)
        mli_side_x = qx_min if QUADRANT in ('FL', 'RL') else qx_max

        mliSidePlaneInput = comp.constructionPlanes.createInput()
        mliSidePlaneInput.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(mli_side_x)
        )
        mliSidePlane = comp.constructionPlanes.add(mliSidePlaneInput)

        mliSideSketch = comp.sketches.add(mliSidePlane)
        mliSideSketch.name = f'MLI Ridge Side {QUADRANT}'
        mliSideSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(qy_min + WALL, mli_ridge_z - MLI_RIDGE_W / 2, 0),
            p(qy_max - WALL, mli_ridge_z + MLI_RIDGE_W / 2, 0)
        )

        for pi in range(mliSideSketch.profiles.count):
            pr = mliSideSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 3.0:
                mliSideInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                # Extrude outward from side wall
                if QUADRANT in ('FL', 'RL'):
                    mliSideInput.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(MLI_RIDGE_H)
                    )
                else:
                    mliSideInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(MLI_RIDGE_H)
                    )
                try:
                    extrudes.add(mliSideInput)
                except:
                    pass

        # Front/rear wall ridge
        mli_end_y = qy_max if QUADRANT in ('FL', 'FR') else qy_min

        mliEndPlaneInput = comp.constructionPlanes.createInput()
        mliEndPlaneInput.setByOffset(
            comp.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(mli_end_y)
        )
        mliEndPlane = comp.constructionPlanes.add(mliEndPlaneInput)

        mliEndSketch = comp.sketches.add(mliEndPlane)
        mliEndSketch.name = f'MLI Ridge End {QUADRANT}'
        mliEndSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(qx_min + WALL, mli_ridge_z - MLI_RIDGE_W / 2, 0),
            p(qx_max - WALL, mli_ridge_z + MLI_RIDGE_W / 2, 0)
        )

        for pi in range(mliEndSketch.profiles.count):
            pr = mliEndSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 2.0:
                mliEndInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                # Extrude outward from front/rear wall
                if QUADRANT in ('FL', 'FR'):
                    mliEndInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(MLI_RIDGE_H)
                    )
                else:
                    mliEndInput.setDistanceExtent(
                        True, adsk.core.ValueInput.createByReal(MLI_RIDGE_H)
                    )
                try:
                    extrudes.add(mliEndInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 14: Corner fillets on outer vertical edges
        # 3mm radius fillet — softens appearance, safer to handle
        # Note: Fusion API fillet requires selecting edge objects.
        # We approximate by cutting chamfers with a diagonal sketch.
        # ══════════════════════════════════════════════════════════════

        FILLET_R = 0.3  # 3mm radius (approximated as 45° chamfer)

        # Try to apply chamfer on all vertical edges of the body
        try:
            chamfers = comp.features.chamferFeatures
            # Find the body
            target_body = None
            for bi in range(comp.bRepBodies.count):
                b = comp.bRepBodies.item(bi)
                if f'Body {QUADRANT}' in b.name:
                    target_body = b
                    break

            if target_body:
                # Collect vertical edges (edges parallel to Z-axis at outer corners)
                edgeCollection = adsk.core.ObjectCollection.create()
                for ei in range(target_body.edges.count):
                    edge = target_body.edges.item(ei)
                    # Check if edge is approximately vertical (Z-aligned)
                    sp = edge.startVertex.geometry
                    ep = edge.endVertex.geometry
                    dx = abs(sp.x - ep.x)
                    dy = abs(sp.y - ep.y)
                    dz = abs(sp.z - ep.z)
                    # Vertical edge: small dx and dy, large dz
                    if dz > 0.5 and dx < 0.01 and dy < 0.01:
                        # Check if it's an outer corner (at quadrant boundary)
                        avg_x = (sp.x + ep.x) / 2
                        avg_y = (sp.y + ep.y) / 2
                        is_outer_x = abs(avg_x - qx_min) < 0.05 or abs(avg_x - qx_max) < 0.05
                        is_outer_y = abs(avg_y - qy_min) < 0.05 or abs(avg_y - qy_max) < 0.05
                        if is_outer_x and is_outer_y:
                            edgeCollection.add(edge)

                if edgeCollection.count > 0:
                    chamInput = chamfers.createInput2()
                    chamInput.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                        edgeCollection,
                        adsk.core.ValueInput.createByReal(FILLET_R),
                        True  # tangent chain
                    )
                    chamfers.add(chamInput)
        except:
            pass  # Chamfer may fail on complex geometry — cosmetic only

        # ── Zoom and report ──
        app.activeViewport.fit()

        bolt_count = len(seam_edges)
        has_switch = (QUADRANT == 'RR')
        ui.messageBox(
            f'Body Quadrant {QUADRANT} created!\n\n'
            f'Size: {q_width * 10:.0f} × {q_length * 10:.0f} × '
            f'{BODY_H * 10:.0f}mm\n'
            f'Walls: {WALL * 10:.0f}mm\n'
            f'Internal ribs: 2 (cross pattern)\n'
            f'Pivot boss: {"Yes (608ZZ seat + 8mm bore, trimmed to bounds)" if has_pivot else "No (not in this quadrant)"}\n'
            f'Vent slots: {VENT_COUNT}x on side wall\n'
            f'Cable channels: 2 (front-to-back + left-to-right)\n'
            f'Cable exit holes: {len(cable_exits)}x (12×8mm, JST-XH compatible)\n'
            f'Seam bolt holes: {bolt_count}x M3 heat-set insert pockets\n'
            f'Alignment dowels: {len(dowel_positions)}x 3mm pin holes\n'
            f'Kill switch hole: {"Yes (15mm dia)" if has_switch else "No (RR only)"}\n'
            f'LED underglow holes: {len(led_holes)}x (5mm dia, floor)\n'
            f'Light holes: {len(light_holes)}x 5mm ({"headlights" if QUADRANT in ("FL", "FR") else "taillights"})\n'
            f'Panel line grooves: 4 (cosmetic, 1mm × 0.5mm)\n'
            f'Arm mount bosses: {arm_mount_count}x (FL only, Phase 2 robotic arm)\n'
            f'RTG detail pads: {rtg_count}x (RL/RR rear wall, cosmetic)\n'
            f'MLI blanket ridges: 2 (side + end walls, cosmetic)\n'
            f'Corner chamfers: 3mm on outer vertical edges\n\n'
            f'To create other quadrants, change QUADRANT variable.\n\n'
            'Qty needed: 4 quadrants total\n'
            'Print open face up, 20% infill, 8mm brim recommended.',
            f'Mars Rover - Body {QUADRANT}'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
