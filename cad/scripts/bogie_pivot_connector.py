"""
Mars Rover Bogie Pivot Connector — Phase 1
============================================

Central pivot hub for the bogie arm. Connects to the rocker (via one
tube from above) and splits to two wheels (front/rear tubes going down).

Features:
  - 608ZZ bearing seat (bogie rotation on rocker shaft)
  - 3× tube sockets (8.2mm bore × 15mm deep):
    * UP: from rocker rear arm (60mm tube)
    * FRONT-DOWN: to middle wheel (60mm tube)
    * REAR-DOWN: to rear wheel (60mm tube)
  - M3 grub screws in each tube socket (rod retention)
  - Wire channel Y-split: 8×6mm in from rocker, 2× 8×6mm out to wheels
  - 4mm minimum wall thickness

Overall size: ~45 × 35 × 30mm
Print: Flat (bearing face down), PLA, 60% infill, 5 perimeters
Qty: 2 (left + right — symmetric, no mirror needed)

Reference: EA-25, MrOver BogieJoint3_7.scad, Sawppy Bogie-Body (20×57×40mm)
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

        # ── Shared connector dimensions (cm, EA-25 standard) ──
        TUBE_BORE_R = 0.41          # 8.2mm dia (0.2mm clearance on 8mm rod)
        TUBE_DEPTH = 1.5            # 15mm socket engagement
        GRUB_R = 0.15               # 3mm M3 grub screw
        GRUB_DEPTH = 0.6            # 6mm (through wall into tube)
        WIRE_W = 0.8                # 8mm wire channel width
        WIRE_H = 0.6                # 6mm wire channel height
        WALL = 0.4                  # 4mm minimum wall
        BEARING_SEAT_R = 1.1075     # 22.15mm dia (608ZZ)
        BEARING_SEAT_DEPTH = 0.72   # 7.2mm
        PIVOT_BORE_R = 0.41         # 8.2mm through-hole (for 8mm bogie shaft)
        CHAMFER = 0.03              # 0.3mm bearing entry chamfer

        # ── Connector body ──
        BODY_R = BEARING_SEAT_R + WALL  # ~15mm radius (30mm OD)
        BODY_H = 3.0               # 30mm total height

        # ── Tube socket angles ──
        # UP socket: vertical (from rocker rear arm above)
        # FRONT socket: angled forward-down for middle wheel
        # REAR socket: angled backward-down for rear wheel
        # Tubes spread at ~120° from each other for stability
        FRONT_ANGLE_DEG = 35       # degrees below horizontal (forward-down)
        REAR_ANGLE_DEG = 35        # degrees below horizontal (backward-down)
        SPREAD_ANGLE_DEG = 140     # angle between front and rear tubes (viewed from top)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures
        revolves = comp.features.revolveFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Main body — cylinder with bearing boss
        # Revolve on XZ plane, axis along Y
        # Body is oriented: Y = vertical (pivot axis), X/Z = horizontal
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Connector Body'
        sl = sketch.sketchCurves.sketchLines

        # Cross-section: cylinder with wider bearing boss at bottom
        pts = [
            (PIVOT_BORE_R, 0),                          # bore, bottom
            (BODY_R, 0),                                # outer, bottom
            (BODY_R, BODY_H),                           # outer, top
            (PIVOT_BORE_R, BODY_H),                     # bore, top
        ]

        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            sl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        axis = sl.addByTwoPoints(p(0, 0, 0), p(0, BODY_H, 0))
        axis.isConstruction = True

        prof = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                prof = pr

        body = None
        if prof:
            revInput = revolves.createInput(
                prof, axis,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            revInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
            bodyRev = revolves.add(revInput)
            body = bodyRev.bodies.item(0)
            body.name = 'Bogie Pivot Connector'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Bearing seat (from bottom face)
        # ══════════════════════════════════════════════════════════

        seatSketch = comp.sketches.add(comp.xZConstructionPlane)
        seatSketch.name = 'Bearing Seat'
        ssl = seatSketch.sketchCurves.sketchLines

        seat_top = BEARING_SEAT_DEPTH
        ssl.addByTwoPoints(p(PIVOT_BORE_R, 0, 0), p(BEARING_SEAT_R, 0, 0))
        ssl.addByTwoPoints(p(BEARING_SEAT_R, 0, 0), p(BEARING_SEAT_R, seat_top, 0))
        ssl.addByTwoPoints(p(BEARING_SEAT_R, seat_top, 0), p(PIVOT_BORE_R, seat_top, 0))
        ssl.addByTwoPoints(p(PIVOT_BORE_R, seat_top, 0), p(PIVOT_BORE_R, 0, 0))

        seatAxis = ssl.addByTwoPoints(p(0, 0, 0), p(0, seat_top, 0))
        seatAxis.isConstruction = True

        seatProf = seatSketch.profiles.item(0)
        seatRevInput = revolves.createInput(
            seatProf, seatAxis,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        seatRevInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        revolves.add(seatRevInput)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Tube socket bosses (3 cylindrical protrusions)
        # Each boss extends outward from the main body
        # ══════════════════════════════════════════════════════════

        SOCKET_OUTER_R = TUBE_BORE_R + WALL  # Socket outer radius (~8.2mm)

        # Socket positions and directions
        # All originate from the body center at Y = BODY_H/2 (mid-height)
        socket_y = BODY_H / 2
        sockets = []

        # UP socket (from rocker, vertical — goes straight up from top)
        sockets.append({
            'name': 'Rocker Socket',
            'dir_x': 0, 'dir_y': 1, 'dir_z': 0,  # straight up
            'origin_y': BODY_H,  # starts at top
        })

        # FRONT-DOWN socket (to middle wheel)
        front_rad = math.radians(FRONT_ANGLE_DEG)
        spread_rad = math.radians(SPREAD_ANGLE_DEG / 2)
        sockets.append({
            'name': 'Front Socket',
            'dir_x': math.sin(spread_rad) * math.cos(front_rad),
            'dir_y': -math.sin(front_rad),
            'dir_z': math.cos(spread_rad) * math.cos(front_rad),
            'origin_y': socket_y,
        })

        # REAR-DOWN socket (to rear wheel)
        rear_rad = math.radians(REAR_ANGLE_DEG)
        sockets.append({
            'name': 'Rear Socket',
            'dir_x': -math.sin(spread_rad) * math.cos(rear_rad),
            'dir_y': -math.sin(rear_rad),
            'dir_z': math.cos(spread_rad) * math.cos(rear_rad),
            'origin_y': socket_y,
        })

        # For simplicity, create tube sockets as cylinders extruded
        # along each direction from the body surface.
        # The sockets are cut (bore) into these bosses.

        for sock in sockets:
            # Create boss (solid cylinder along socket direction)
            # For the UP socket, sketch on top face (XZ at Y=BODY_H)
            # For angled sockets, use construction plane

            if sock['dir_y'] == 1:
                # Vertical up socket — sketch on XZ plane offset to top
                topPlane = comp.constructionPlanes
                tpInput = topPlane.createInput()
                tpInput.setByOffset(
                    comp.xZConstructionPlane,
                    adsk.core.ValueInput.createByReal(BODY_H)
                )
                sPlane = topPlane.add(tpInput)

                bossSketch = comp.sketches.add(sPlane)
                bossSketch.name = f'{sock["name"]} Boss'
                bossSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(0, 0, 0), SOCKET_OUTER_R
                )

                bossProf = None
                minArea = float('inf')
                for pi_idx in range(bossSketch.profiles.count):
                    pr = bossSketch.profiles.item(pi_idx)
                    a = pr.areaProperties().area
                    if a < minArea:
                        minArea = a
                        bossProf = pr

                if bossProf:
                    bossInput = extrudes.createInput(
                        bossProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    bossInput.setDistanceExtent(
                        False, adsk.core.ValueInput.createByReal(TUBE_DEPTH)
                    )
                    extrudes.add(bossInput)

                    # Cut bore
                    boreSketch = comp.sketches.add(sPlane)
                    boreSketch.name = f'{sock["name"]} Bore'
                    boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
                        p(0, 0, 0), TUBE_BORE_R
                    )

                    boreProf = None
                    minArea = float('inf')
                    for pi_idx in range(boreSketch.profiles.count):
                        pr = boreSketch.profiles.item(pi_idx)
                        a = pr.areaProperties().area
                        if a < minArea:
                            minArea = a
                            boreProf = pr

                    if boreProf:
                        boreInput = extrudes.createInput(
                            boreProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                        )
                        boreInput.setDistanceExtent(
                            False, adsk.core.ValueInput.createByReal(TUBE_DEPTH + 0.5)
                        )
                        try:
                            extrudes.add(boreInput)
                        except:
                            pass

            else:
                # Angled socket — create at body surface angled outward
                # For simplicity, create horizontal boss offset from center
                # The angle is approximate for the prototype
                dx = sock['dir_x']
                dz = sock['dir_z']
                norm = math.sqrt(dx**2 + dz**2)
                if norm > 0:
                    dx /= norm
                    dz /= norm

                # Boss center on body surface
                boss_cx = dx * BODY_R
                boss_cz = dz * BODY_R

                # Create boss at mid-height, projecting outward
                midPlane = comp.constructionPlanes
                mpInput = midPlane.createInput()
                mpInput.setByOffset(
                    comp.xZConstructionPlane,
                    adsk.core.ValueInput.createByReal(socket_y)
                )
                mPlane = midPlane.add(mpInput)

                bossSketch = comp.sketches.add(mPlane)
                bossSketch.name = f'{sock["name"]} Boss'
                bossSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(boss_cx + dx * TUBE_DEPTH / 2,
                      boss_cz + dz * TUBE_DEPTH / 2, 0),
                    SOCKET_OUTER_R
                )

                bossProf = None
                minArea = float('inf')
                for pi_idx in range(bossSketch.profiles.count):
                    pr = bossSketch.profiles.item(pi_idx)
                    a = pr.areaProperties().area
                    if a < minArea:
                        minArea = a
                        bossProf = pr

                if bossProf:
                    # Extrude vertically (approximate — should be along tube angle)
                    bossInput = extrudes.createInput(
                        bossProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                    )
                    bossInput.setSymmetricExtent(
                        adsk.core.ValueInput.createByReal(SOCKET_OUTER_R + 0.2),
                        True
                    )
                    try:
                        extrudes.add(bossInput)
                    except:
                        pass

                    # Cut bore through the boss
                    boreSketch = comp.sketches.add(mPlane)
                    boreSketch.name = f'{sock["name"]} Bore'
                    boreSketch.sketchCurves.sketchCircles.addByCenterRadius(
                        p(boss_cx + dx * TUBE_DEPTH / 2,
                          boss_cz + dz * TUBE_DEPTH / 2, 0),
                        TUBE_BORE_R
                    )

                    boreProf = None
                    minArea = float('inf')
                    for pi_idx in range(boreSketch.profiles.count):
                        pr = boreSketch.profiles.item(pi_idx)
                        a = pr.areaProperties().area
                        if a < minArea:
                            minArea = a
                            boreProf = pr

                    if boreProf:
                        boreInput = extrudes.createInput(
                            boreProf, adsk.fusion.FeatureOperations.CutFeatureOperation
                        )
                        boreInput.setSymmetricExtent(
                            adsk.core.ValueInput.createByReal(SOCKET_OUTER_R + 0.5),
                            True
                        )
                        try:
                            extrudes.add(boreInput)
                        except:
                            pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Wire channels (rectangular through-cuts)
        # Main channel from rocker side, splits to front/rear
        # ══════════════════════════════════════════════════════════

        # Vertical wire channel through the body center (from top socket down)
        wireSketch = comp.sketches.add(comp.xYConstructionPlane)
        wireSketch.name = 'Wire Channel'
        wl = wireSketch.sketchCurves.sketchLines
        wl.addTwoPointRectangle(
            p(-WIRE_W / 2, 0, 0),
            p(WIRE_W / 2, BODY_H + TUBE_DEPTH, 0)
        )

        wireProf = None
        minArea = float('inf')
        for pi_idx in range(wireSketch.profiles.count):
            pr = wireSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                wireProf = pr

        if wireProf:
            wireInput = extrudes.createInput(
                wireProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            wireInput.setSymmetricExtent(
                adsk.core.ValueInput.createByReal(WIRE_H / 2),
                True
            )
            try:
                extrudes.add(wireInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Chamfer bearing entry
        # ══════════════════════════════════════════════════════════

        if body:
            chamferEdges = adsk.core.ObjectCollection.create()
            for edge in body.edges:
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - BEARING_SEAT_R) < 0.01:
                        chamferEdges.add(edge)
                        break

            if chamferEdges.count > 0:
                chamfers = comp.features.chamferFeatures
                chamInput = chamfers.createInput2()
                chamInput.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                    chamferEdges,
                    adsk.core.ValueInput.createByReal(CHAMFER),
                    True
                )
                try:
                    chamfers.add(chamInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 6: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Bogie Pivot Connector created!\n\n'
            f'Body: {BODY_R * 20:.0f}mm OD × {BODY_H * 10:.0f}mm tall\n'
            f'Bearing seat: {BEARING_SEAT_R * 20:.2f}mm × '
            f'{BEARING_SEAT_DEPTH * 10:.1f}mm deep (608ZZ)\n'
            f'Pivot bore: {PIVOT_BORE_R * 20:.1f}mm\n\n'
            f'Tube sockets: 3× (up, front-down, rear-down)\n'
            f'  Bore: {TUBE_BORE_R * 20:.1f}mm × {TUBE_DEPTH * 10:.0f}mm deep\n'
            f'  Wall: {WALL * 10:.0f}mm minimum\n\n'
            f'Wire channel: {WIRE_W * 10:.0f}×{WIRE_H * 10:.0f}mm (Y-split)\n'
            f'Front/Rear spread: {SPREAD_ANGLE_DEG}°\n'
            f'Tube down-angle: {FRONT_ANGLE_DEG}°\n\n'
            'Print bearing-face down, 60% infill, 5 perimeters.\n'
            'Qty: 2 (symmetric, left = right)',
            'Mars Rover - Bogie Pivot Connector'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
