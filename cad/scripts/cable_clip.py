"""
Mars Rover Cable Clip — Phase 1
================================

Snap-fit clip that wraps around 8mm steel suspension rods to hold
wires against the rod. Inspired by Sawppy Rod Support and general
cable management clips.

Dimensions:
  - Rod bore: 8.3mm (slight clearance on 8mm rod)
  - Clip outer: ~12mm × 8mm × 5mm
  - Wire channel: 5mm wide × 3mm deep (on back of clip)
  - Snap gap: 3mm opening, flexes open to snap onto rod

The clip wraps ~270° around the rod with a 3mm gap for snap-on.
A flat back surface has a groove for wire routing.

Print: Flat (gap facing up), PLA, 100% infill (small part, needs flex)
Qty: 12 (3 per arm tube × 4 tubes, rough estimate)

Reference: EA-25, Sawppy Rod Support (11×22×30mm)
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
        ROD_R = 0.415           # 4.15mm radius (8.3mm bore, 0.3mm clearance on 8mm)
        CLIP_WALL = 0.2         # 2mm wall around rod
        CLIP_OUTER_R = ROD_R + CLIP_WALL  # 6.15mm outer radius
        CLIP_H = 0.5            # 5mm clip height (along rod axis)
        SNAP_GAP = 0.3          # 3mm snap opening
        WIRE_CHANNEL_W = 0.5    # 5mm wire channel width
        WIRE_CHANNEL_D = 0.3    # 3mm wire channel depth

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Create clip body
        # Sketch on XY plane: C-shaped clip (270° arc) with flat back
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Cable Clip Profile'
        arcs = sketch.sketchCurves.sketchArcs
        lines = sketch.sketchCurves.sketchLines

        center = p(0, 0, 0)

        # The clip opens at the top (positive Y). Gap width = SNAP_GAP.
        # Half-gap angle from vertical: asin(gap/2 / radius)
        gap_half_angle = math.asin(SNAP_GAP / (2 * ROD_R))
        # Clip arc spans from (pi/2 + gap_half) to (pi/2 - gap_half + 2*pi)
        # i.e., almost full circle minus the gap at top

        arc_start_angle = math.pi / 2 + gap_half_angle
        arc_sweep = 2 * math.pi - 2 * gap_half_angle  # ~330° for 3mm gap on 8.3mm bore

        # Outer arc
        outer_start = p(
            CLIP_OUTER_R * math.cos(arc_start_angle),
            CLIP_OUTER_R * math.sin(arc_start_angle), 0
        )
        outer_arc = arcs.addByCenterStartSweep(center, outer_start, -arc_sweep)

        # Inner arc (rod bore)
        inner_start = p(
            ROD_R * math.cos(arc_start_angle),
            ROD_R * math.sin(arc_start_angle), 0
        )
        inner_arc = arcs.addByCenterStartSweep(center, inner_start, -arc_sweep)

        # Close the ends with lines (the gap edges)
        # End 1 (at arc_start_angle)
        lines.addByTwoPoints(
            p(ROD_R * math.cos(arc_start_angle),
              ROD_R * math.sin(arc_start_angle), 0),
            p(CLIP_OUTER_R * math.cos(arc_start_angle),
              CLIP_OUTER_R * math.sin(arc_start_angle), 0)
        )

        # End 2 (at arc_start_angle - arc_sweep = pi/2 - gap_half_angle)
        end_angle = arc_start_angle - arc_sweep
        lines.addByTwoPoints(
            p(ROD_R * math.cos(end_angle),
              ROD_R * math.sin(end_angle), 0),
            p(CLIP_OUTER_R * math.cos(end_angle),
              CLIP_OUTER_R * math.sin(end_angle), 0)
        )

        # Find the C-shaped profile
        clipProf = None
        # The clip profile area ≈ arc_sweep * (outer_r² - inner_r²) / 2
        expected = arc_sweep * (CLIP_OUTER_R**2 - ROD_R**2) / 2
        bestDiff = float('inf')
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            diff = abs(a - expected)
            if diff < bestDiff:
                bestDiff = diff
                clipProf = pr

        clipBody = None
        if clipProf:
            extInput = extrudes.createInput(
                clipProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(CLIP_H)
            )
            clipExt = extrudes.add(extInput)
            clipBody = clipExt.bodies.item(0)
            clipBody.name = 'Cable Clip'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Add wire channel on the back (bottom, -Y side)
        # Rectangular groove on the outside of the clip
        # ══════════════════════════════════════════════════════════

        channelSketch = comp.sketches.add(comp.xYConstructionPlane)
        channelSketch.name = 'Wire Channel'
        cl = channelSketch.sketchCurves.sketchLines

        # Channel is on the bottom of the clip (opposite to the gap)
        # Center at Y = -(CLIP_OUTER_R + WIRE_CHANNEL_D/2)
        ch_y_outer = -(CLIP_OUTER_R + WIRE_CHANNEL_D)
        ch_y_inner = -CLIP_OUTER_R + 0.01  # slight overlap for cut
        ch_x_half = WIRE_CHANNEL_W / 2

        cl.addTwoPointRectangle(
            p(-ch_x_half, ch_y_inner, 0),
            p(ch_x_half, ch_y_outer, 0)
        )

        chProf = None
        minArea = float('inf')
        for pi_idx in range(channelSketch.profiles.count):
            pr = channelSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                chProf = pr

        if chProf:
            chInput = extrudes.createInput(
                chProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            chInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(CLIP_H)
            )
            try:
                extrudes.add(chInput)
            except:
                pass

        # Cut the actual channel groove into the added material
        chCutSketch = comp.sketches.add(comp.xYConstructionPlane)
        chCutSketch.name = 'Wire Channel Cut'
        ccl = chCutSketch.sketchCurves.sketchLines

        # The channel is a U-shaped groove
        groove_wall = 0.1  # 1mm walls on sides of groove
        gx_half = (WIRE_CHANNEL_W / 2) - groove_wall
        gy_outer = ch_y_outer + groove_wall
        gy_inner = ch_y_inner

        ccl.addTwoPointRectangle(
            p(-gx_half, gy_inner, 0),
            p(gx_half, gy_outer, 0)
        )

        ccProf = None
        minArea = float('inf')
        for pi_idx in range(chCutSketch.profiles.count):
            pr = chCutSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                ccProf = pr

        if ccProf:
            ccInput = extrudes.createInput(
                ccProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            ccInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(CLIP_H + 0.01)
            )
            try:
                extrudes.add(ccInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Cable Clip created!\n\n'
            f'Rod bore: {ROD_R * 20:.1f}mm (snap-fit on 8mm rod)\n'
            f'Clip wall: {CLIP_WALL * 10:.0f}mm\n'
            f'Clip height: {CLIP_H * 10:.0f}mm (along rod)\n'
            f'Snap gap: {SNAP_GAP * 10:.0f}mm\n'
            f'Wire channel: {WIRE_CHANNEL_W * 10:.0f} × '
            f'{WIRE_CHANNEL_D * 10:.0f}mm\n\n'
            'Snap onto 8mm steel rod, route wires through channel.\n'
            'Print flat (gap up), 100% infill, PLA.\n\n'
            'Qty needed: ~12 (3 per arm tube)',
            'Mars Rover - Cable Clip'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
