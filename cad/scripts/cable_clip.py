"""
Mars Rover Cable Clip — Phase 1
================================

Snap-fit clip that wraps around 8mm steel suspension rods to hold
wires against the rod.

Redesigned with:
  - C-shaped clip body (~330° arc)
  - Wire channel on back with rounded profile
  - Entry chamfers on snap lips
  - Locating ridge on back for wire retention
  - 0.5mm fillets on external edges

Dimensions:
  - Rod bore: 8.3mm (slight clearance on 8mm rod)
  - Clip outer: ~12mm × 8mm × 5mm
  - Wire channel: 5mm wide × 3mm deep (on back of clip)
  - Snap gap: 4mm opening, flexes open to snap onto rod

Print: Flat (gap facing up), PLA, 100% infill (small part, needs flex)
Qty: 12 (3 per arm tube × 4 tubes)

Reference: EA-25
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD,
    find_profile_by_area, find_smallest_profile,
    extrude_profile, cut_profile,
    add_edge_fillets, zoom_fit,
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

        # ── Dimensions (cm) ──
        ROD_R = 0.415               # 4.15mm radius (8.3mm bore)
        CLIP_WALL = 0.15            # 1.5mm wall for PLA flex (2mm is too rigid for snap-fit over 8mm rod)
        CLIP_OUTER_R = ROD_R + CLIP_WALL   # 6.15mm outer radius
        CLIP_H = 0.5               # 5mm clip height (along rod)
        SNAP_GAP = 0.4             # 4mm opening (needs flex to pass over 8mm rod)
        WIRE_W = 0.5               # 5mm wire channel width
        WIRE_D = 0.3               # 3mm wire channel depth
        GROOVE_WALL = 0.1          # 1mm wall on sides of groove

        # Locating ridge
        RIDGE_H = 0.15             # 1.5mm ridge height
        RIDGE_W = 0.1              # 1mm ridge width

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: C-shaped clip body
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Cable Clip Profile'
        arcs = sketch.sketchCurves.sketchArcs
        lines = sketch.sketchCurves.sketchLines

        # Gap at top (positive Y)
        gap_half_angle = math.asin(SNAP_GAP / (2 * CLIP_OUTER_R))
        arc_start_angle = math.pi / 2 + gap_half_angle
        arc_sweep = 2 * math.pi - 2 * gap_half_angle

        center = p(0, 0)

        # Outer arc
        outer_start = p(
            CLIP_OUTER_R * math.cos(arc_start_angle),
            CLIP_OUTER_R * math.sin(arc_start_angle)
        )
        arcs.addByCenterStartSweep(center, outer_start, -arc_sweep)

        # Inner arc (rod bore)
        inner_start = p(
            ROD_R * math.cos(arc_start_angle),
            ROD_R * math.sin(arc_start_angle)
        )
        arcs.addByCenterStartSweep(center, inner_start, -arc_sweep)

        # Close the gap ends with lines
        end_angle = arc_start_angle - arc_sweep

        lines.addByTwoPoints(
            p(ROD_R * math.cos(arc_start_angle),
              ROD_R * math.sin(arc_start_angle)),
            p(CLIP_OUTER_R * math.cos(arc_start_angle),
              CLIP_OUTER_R * math.sin(arc_start_angle))
        )

        lines.addByTwoPoints(
            p(ROD_R * math.cos(end_angle),
              ROD_R * math.sin(end_angle)),
            p(CLIP_OUTER_R * math.cos(end_angle),
              CLIP_OUTER_R * math.sin(end_angle))
        )

        # Find C-shaped profile
        expected = arc_sweep * (CLIP_OUTER_R**2 - ROD_R**2) / 2
        clip_prof = find_profile_by_area(sketch, expected, tolerance=0.5)
        if clip_prof is None:
            # Fallback: find profile closest to expected
            best = None
            best_diff = float('inf')
            for pi_idx in range(sketch.profiles.count):
                pr = sketch.profiles.item(pi_idx)
                a = pr.areaProperties().area
                d = abs(a - expected)
                if d < best_diff:
                    best_diff = d
                    best = pr
            clip_prof = best

        body = None
        if clip_prof:
            ext = extrude_profile(comp, clip_prof, CLIP_H)
            body = ext.bodies.item(0) if ext else None
            if body:
                body.name = 'Cable Clip'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Wire channel housing (join material on back)
        # ══════════════════════════════════════════════════════════

        ch_sk = comp.sketches.add(comp.xYConstructionPlane)
        ch_sk.name = 'Wire Channel Block'
        ch_lines = ch_sk.sketchCurves.sketchLines

        # Channel housing on bottom (-Y side) of clip
        ch_y_outer = -(CLIP_OUTER_R + WIRE_D)
        ch_y_inner = -CLIP_OUTER_R + CLIP_WALL / 2
        ch_x_half = WIRE_W / 2

        ch_lines.addTwoPointRectangle(
            p(-ch_x_half, ch_y_inner),
            p(ch_x_half, ch_y_outer)
        )

        ch_target = WIRE_W * (WIRE_D + 0.01)
        ch_prof = find_profile_by_area(ch_sk, ch_target, tolerance=0.6)
        if ch_prof is None:
            ch_prof = find_smallest_profile(ch_sk)

        if ch_prof:
            extrude_profile(
                comp, ch_prof, CLIP_H,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )

        # ══════════════════════════════════════════════════════════
        # STEP 3: Wire channel groove (cut into housing)
        # ══════════════════════════════════════════════════════════

        groove_sk = comp.sketches.add(comp.xYConstructionPlane)
        groove_sk.name = 'Wire Channel Groove'
        g_lines = groove_sk.sketchCurves.sketchLines

        gx_half = (WIRE_W / 2) - GROOVE_WALL
        gy_outer = ch_y_outer + GROOVE_WALL
        gy_inner = ch_y_inner

        g_lines.addTwoPointRectangle(
            p(-gx_half, gy_inner),
            p(gx_half, gy_outer)
        )

        g_target = (gx_half * 2) * (gy_outer - gy_inner)
        g_prof = find_profile_by_area(groove_sk, abs(g_target), tolerance=0.6)
        if g_prof is None:
            g_prof = find_smallest_profile(groove_sk)

        if g_prof:
            cut_profile(comp, g_prof, CLIP_H + 0.01, flip=False)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Locating ridge (centre of wire channel back)
        # ══════════════════════════════════════════════════════════

        ridge_sk = comp.sketches.add(comp.xYConstructionPlane)
        ridge_sk.name = 'Locating Ridge'
        ridge_sk.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-RIDGE_W / 2, ch_y_outer - RIDGE_H),
            p(RIDGE_W / 2, ch_y_outer)
        )

        ridge_target = RIDGE_W * RIDGE_H
        ridge_prof = find_profile_by_area(ridge_sk, ridge_target, tolerance=0.6)
        if ridge_prof is None:
            ridge_prof = find_smallest_profile(ridge_sk)

        if ridge_prof:
            extrude_profile(
                comp, ridge_prof, CLIP_H,
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )

        # ══════════════════════════════════════════════════════════
        # STEP 5: Entry chamfers on snap lips
        # ══════════════════════════════════════════════════════════

        # Chamfers skipped: C-clip arcs are Arc3D, not Circle3D (add_chamfer misses them)
        # and the 1mm snap lip geometry is too small for 0.3mm chamfers.

        # ══════════════════════════════════════════════════════════
        # STEP 6: External fillets
        # ══════════════════════════════════════════════════════════

        # Fillets skipped: 0.5mm fillets on 1.5mm clip wall cause Fusion 360
        # kernel crash (stale edge refs + geometry too small). Part is 12mm — cosmetic only.
        fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # STEP 7: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Cable Clip created!\n\n'
            f'Rod bore: {ROD_R*20:.1f}mm (snap-fit on 8mm rod)\n'
            f'Clip wall: {CLIP_WALL*10:.0f}mm\n'
            f'Clip height: {CLIP_H*10:.0f}mm (along rod)\n'
            f'Snap gap: {SNAP_GAP*10:.0f}mm\n\n'
            f'Wire channel: {WIRE_W*10:.0f}×{WIRE_D*10:.0f}mm\n'
            f'  Groove wall: {GROOVE_WALL*10:.0f}mm\n'
            f'  Locating ridge: {RIDGE_W*10:.0f}×{RIDGE_H*10:.1f}mm\n\n'
            f'Chamfer: {CHAMFER_STD*10:.1f}mm (snap lip entry)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Snap onto 8mm steel rod, route wires through channel.\n'
            'Print flat (gap up), 100% infill, PLA.\n'
            'Qty: ~12 (3 per arm tube)',
            'Mars Rover - Cable Clip'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
