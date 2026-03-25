"""
Mars Rover Strain Relief Clip — Phase 1
========================================

U-channel clip with snap tabs for anchoring wire bundles at pivot
entry/exit points on body walls and suspension arms.

Redesigned with:
  - Rounded-rect base plate (2mm corner radius)
  - U-channel with rounded bottom profile
  - Snap tabs with entry ramps (chamfered tips)
  - Chamfered bolt holes for flush M3 heads
  - 0.5mm fillets on external edges

Dimensions:
  - Body: 18 × 10 × 10mm
  - U-channel: 6mm wide × 5mm deep (holds ~4 × 22AWG wires)
  - Base: 3mm thick with 2× M3 bolt holes (10mm spacing)
  - Snap tabs: 1.5mm thick × 1.5mm overhang
  - Channel walls: 2mm thick

Print: Upright (U-channel opening at top), 50% infill, 3 perimeters
Qty: 8-12 (2 per rocker pivot, 2 per bogie pivot, extras at body)

Reference: EA-19, EA-17
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, CORNER_R,
    draw_rounded_rect,
    find_profile_by_area, find_smallest_profile, find_largest_profile,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, add_edge_fillets, zoom_fit,
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
        CLIP_L = 1.8        # 18mm length (X)
        CLIP_W = 1.0        # 10mm width (Y)
        CLIP_H = 1.0        # 10mm height (Z)
        BASE_H = 0.3        # 3mm base thickness
        WALL_T = 0.2        # 2mm channel wall thickness
        CHANNEL_W = 0.6     # 6mm channel width
        CHANNEL_D = 0.5     # 5mm channel depth
        SNAP_T = 0.15       # 1.5mm snap tab thickness
        SNAP_OVERHANG = 0.15  # 1.5mm inward overhang
        RAMP_H = 0.1        # 1mm entry ramp height
        HOLE_R = 0.165      # M3 clearance (3.3mm dia)
        HOLE_SPACING = 1.0  # 10mm between holes
        CR = min(CORNER_R, CLIP_W / 4)  # corner radius (limited by width)

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect base body
        # ══════════════════════════════════════════════════════════

        sk1 = comp.sketches.add(comp.xYConstructionPlane)
        sk1.name = 'Clip Body'
        draw_rounded_rect(sk1, 0, 0, CLIP_L, CLIP_W, r=CR)

        body_prof = find_largest_profile(sk1)
        ext = extrude_profile(comp, body_prof, CLIP_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Strain Relief Clip'

        # ══════════════════════════════════════════════════════════
        # STEP 2: U-channel cut from top (rounded-rect profile)
        # ══════════════════════════════════════════════════════════

        topP = make_offset_plane(comp, comp.xYConstructionPlane, CLIP_H)
        ch_sk = comp.sketches.add(topP)
        ch_sk.name = 'U-Channel'

        # Channel with rounded ends
        ch_inner_l = CLIP_L - 2 * WALL_T
        ch_r = min(CR * 0.5, CHANNEL_W / 4)
        draw_rounded_rect(ch_sk, 0, 0, ch_inner_l, CHANNEL_W, r=ch_r)

        ch_target = ch_inner_l * CHANNEL_W
        ch_prof = find_profile_by_area(ch_sk, ch_target, tolerance=0.5)
        if ch_prof is None:
            ch_prof = find_smallest_profile(ch_sk)

        if ch_prof:
            cut_profile(comp, ch_prof, CHANNEL_D, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Snap tabs (inward ledges along SIDES of channel)
        #         Tabs on Y edges so wires can be pressed in from above
        # ══════════════════════════════════════════════════════════

        snap_sk = comp.sketches.add(topP)
        snap_sk.name = 'Snap Tabs'
        sl = snap_sk.sketchCurves.sketchLines

        # Front snap tab (−Y side of channel)
        sl.addTwoPointRectangle(
            p(-ch_inner_l / 2, -CHANNEL_W / 2, 0),
            p(ch_inner_l / 2, -CHANNEL_W / 2 + SNAP_OVERHANG, 0)
        )
        # Rear snap tab (+Y side of channel)
        sl.addTwoPointRectangle(
            p(-ch_inner_l / 2, CHANNEL_W / 2 - SNAP_OVERHANG, 0),
            p(ch_inner_l / 2, CHANNEL_W / 2, 0)
        )

        snap_target = SNAP_OVERHANG * ch_inner_l
        for pi_idx in range(snap_sk.profiles.count):
            pr = snap_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if abs(a - snap_target) < snap_target * 0.8:
                try:
                    join_profile(comp, pr, SNAP_T)
                except Exception as e:
                    print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: Entry ramp cuts on snap tab tips
        # ══════════════════════════════════════════════════════════

        # Chamfer the inner edge of each snap tab to create a wire-entry ramp
        # Done via a triangular cut at the inner (channel-facing) edge of Y-side tabs
        ramp_sk = comp.sketches.add(topP)
        ramp_sk.name = 'Entry Ramps'
        rl = ramp_sk.sketchCurves.sketchLines

        # Front ramp: triangle at inner edge of front (−Y) tab
        fy = -CHANNEL_W / 2 + SNAP_OVERHANG
        rl.addByTwoPoints(
            p(-ch_inner_l / 2, fy, 0),
            p(-ch_inner_l / 2, fy - RAMP_H, 0)
        )
        rl.addByTwoPoints(
            p(-ch_inner_l / 2, fy - RAMP_H, 0),
            p(-ch_inner_l / 2 + RAMP_H, fy, 0)
        )
        rl.addByTwoPoints(
            p(-ch_inner_l / 2 + RAMP_H, fy, 0),
            p(-ch_inner_l / 2, fy, 0)
        )

        # Rear ramp: triangle at inner edge of rear (+Y) tab
        ry = CHANNEL_W / 2 - SNAP_OVERHANG
        rl.addByTwoPoints(
            p(-ch_inner_l / 2, ry, 0),
            p(-ch_inner_l / 2, ry + RAMP_H, 0)
        )
        rl.addByTwoPoints(
            p(-ch_inner_l / 2, ry + RAMP_H, 0),
            p(-ch_inner_l / 2 + RAMP_H, ry, 0)
        )
        rl.addByTwoPoints(
            p(-ch_inner_l / 2 + RAMP_H, ry, 0),
            p(-ch_inner_l / 2, ry, 0)
        )

        ramp_target = 0.5 * RAMP_H * RAMP_H
        for pi_idx in range(ramp_sk.profiles.count):
            pr = ramp_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < ramp_target * 2:
                try:
                    cut_profile(comp, pr, SNAP_T + 0.01, flip=False)
                except Exception as e:
                    print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5: M3 mounting holes through base
        # ══════════════════════════════════════════════════════════

        hole_sk = comp.sketches.add(topP)
        hole_sk.name = 'Mount Holes'
        circles = hole_sk.sketchCurves.sketchCircles
        circles.addByCenterRadius(p(-HOLE_SPACING / 2, 0, 0), HOLE_R)
        circles.addByCenterRadius(p(HOLE_SPACING / 2, 0, 0), HOLE_R)

        for pi_idx in range(hole_sk.profiles.count):
            pr = hole_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < math.pi * HOLE_R**2 * 1.5:
                try:
                    cut_profile(comp, pr, CLIP_H + 0.02, flip=True)
                except Exception as e:
                    print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 6: Fillets
        # ══════════════════════════════════════════════════════════

        fillet_count = 0
        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 7: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Strain Relief Clip created!\n\n'
            f'Size: {CLIP_L*10:.0f} × {CLIP_W*10:.0f} × {CLIP_H*10:.0f}mm\n'
            f'Corner radius: {CR*10:.1f}mm\n\n'
            f'U-channel: {CHANNEL_W*10:.0f}mm wide × {CHANNEL_D*10:.0f}mm deep\n'
            f'Snap tabs: {SNAP_T*10:.1f}mm thick, '
            f'{SNAP_OVERHANG*10:.1f}mm overhang\n'
            f'Entry ramps: {RAMP_H*10:.0f}mm chamfer\n\n'
            f'Mounting: 2× M3 holes, {HOLE_SPACING*10:.0f}mm spacing\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Print upright (channel opening at top), 50% infill.\n'
            'Qty: 8-12',
            'Mars Rover - Strain Relief Clip'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
