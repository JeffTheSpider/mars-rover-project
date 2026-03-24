"""
*** DEPRECATED — See EA-25 ***
Diff bar now passes directly through 608ZZ bearings in body pivot bosses.
Rocker hub connectors clamp rigidly to diff bar ends (no separate adapters).
This script retained for dimension reference only.

Mars Rover Differential Bar Adapter — Phase 1
===============================================

Cylindrical adapter that press-fits onto the 8mm steel rod and
provides a 608ZZ bearing seat for pivoting.

3 needed: Left end, Centre (body mount), Right end

20mm tall × 12mm body OD, with 30mm bearing boss OD, 8mm bore
and 22.15mm bearing seat. Boss wall 3.9mm around bearing.

Print orientation: Flat end down
Supports: None
Perimeters: 4 (structural)
Infill: 60% (bearing seat needs rigidity)

Reference: EA-08 differential bar section
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

        # ── Dimensions (cm) ──
        ADAPTER_H = 2.0         # 20mm total height
        OUTER_R = 0.6           # 6mm radius (12mm OD)
        ROD_BORE_R = 0.4        # 4mm radius (8mm bore for steel rod)
        BEARING_SEAT_R = 1.1075 # 22.15mm dia → 11.075mm radius
        BEARING_SEAT_DEPTH = 0.72  # 7.2mm
        BEARING_BOSS_R = 1.5    # 15mm radius (30mm OD boss) — 3.9mm wall around bearing
        BOSS_H = BEARING_SEAT_DEPTH + 0.1  # boss is slightly taller than seat

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════
        # Create via revolve cross-section on XZ plane
        # X = radial distance, Y = height
        # ══════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Adapter Cross Section'
        lines = sketch.sketchCurves.sketchLines

        # Profile: cylindrical body with wider bearing boss at top
        #
        #     boss_r ──┐
        #              │  bearing seat wall
        #   outer_r ───┤──────────────── outer_r
        #              │   body tube    │
        #   rod_bore_r ┤───────────────┤ rod_bore_r
        #              │    (bore)     │
        #            Y=0            Y=ADAPTER_H

        # Main tube cross-section
        p1 = p(ROD_BORE_R, 0, 0)            # bore, bottom
        p2 = p(OUTER_R, 0, 0)               # outer, bottom
        p3 = p(OUTER_R, ADAPTER_H - BOSS_H, 0)  # outer, below boss
        p4 = p(BEARING_BOSS_R, ADAPTER_H - BOSS_H, 0)  # boss outer, step
        p5 = p(BEARING_BOSS_R, ADAPTER_H, 0)    # boss outer, top
        p6 = p(ROD_BORE_R, ADAPTER_H, 0)        # bore, top

        lines.addByTwoPoints(p1, p2)
        lines.addByTwoPoints(p2, p3)
        lines.addByTwoPoints(p3, p4)
        lines.addByTwoPoints(p4, p5)
        lines.addByTwoPoints(p5, p6)
        lines.addByTwoPoints(p6, p1)

        # Revolve axis
        axis = lines.addByTwoPoints(p(0, 0, 0), p(0, ADAPTER_H, 0))
        axis.isConstruction = True

        # Revolve 360°
        profile = sketch.profiles.item(0)
        revolves = comp.features.revolveFeatures
        revInput = revolves.createInput(
            profile, axis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        revInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        rev = revolves.add(revInput)

        body = rev.bodies.item(0)
        body.name = 'Diff Bar Adapter'

        # ══════════════════════════════════════════════════════
        # Cut bearing seat into the boss (from top)
        # ══════════════════════════════════════════════════════

        # Create bearing seat cross-section (annular cut)
        seatSketch = comp.sketches.add(comp.xZConstructionPlane)
        seatSketch.name = 'Bearing Seat Cut'
        sl = seatSketch.sketchCurves.sketchLines

        # Cut from inner radius of bearing to boss outer, at top
        seat_bottom = ADAPTER_H - BEARING_SEAT_DEPTH
        sp1 = p(ROD_BORE_R, seat_bottom, 0)  # inner, at seat bottom
        sp2 = p(BEARING_SEAT_R, seat_bottom, 0)  # bearing OD, at seat bottom
        sp3 = p(BEARING_SEAT_R, ADAPTER_H, 0)    # bearing OD, at top
        sp4 = p(ROD_BORE_R, ADAPTER_H, 0)        # inner, at top

        sl.addByTwoPoints(sp1, sp2)
        sl.addByTwoPoints(sp2, sp3)
        sl.addByTwoPoints(sp3, sp4)
        sl.addByTwoPoints(sp4, sp1)

        seatAxis = sl.addByTwoPoints(p(0, 0, 0), p(0, ADAPTER_H, 0))
        seatAxis.isConstruction = True

        seatProfile = seatSketch.profiles.item(0)
        seatRevInput = revolves.createInput(
            seatProfile, seatAxis,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        seatRevInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        revolves.add(seatRevInput)

        # ── Chamfer bearing entry ──
        # Find the top edge of the bearing seat bore
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
                adsk.core.ValueInput.createByReal(0.03),  # 0.3mm chamfer
                True
            )
            try:
                chamfers.add(chamInput)
            except:
                pass  # cosmetic, skip if fails

        # ── Zoom and report ──
        app.activeViewport.fit()

        ui.messageBox(
            'Differential Bar Adapter created!\n\n'
            f'Body: {OUTER_R*20:.0f}mm OD × {ADAPTER_H*10:.0f}mm tall\n'
            f'Boss: {BEARING_BOSS_R*20:.0f}mm OD × {BOSS_H*10:.1f}mm '
            f'(wall: {(BEARING_BOSS_R - BEARING_SEAT_R)*10:.1f}mm)\n'
            f'Rod bore: {ROD_BORE_R*20:.0f}mm (press-fit on 8mm rod)\n'
            f'Bearing seat: {BEARING_SEAT_R*20:.2f}mm × '
            f'{BEARING_SEAT_DEPTH*10:.1f}mm deep\n\n'
            'Qty needed: 3 (left, centre, right)\n'
            'Print flat end down, 60% infill.',
            'Mars Rover - Diff Bar Adapter'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
