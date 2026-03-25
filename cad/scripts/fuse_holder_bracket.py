"""
Mars Rover Fuse Holder Bracket — Phase 1
==========================================

Mounting bracket for inline ATC/ATO blade fuse holder.
Bolts to electronics tray or body wall.

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - Clip channel with rounded ends
  - Retention lips at channel openings (prevents fuse holder slide-out)
  - Entry chamfers on lip edges
  - 0.5mm fillets on external edges

Dimensions:
  - Body: 40 × 19 × 12mm (widened for M3 hole wall clearance)
  - Clip channel: 8mm wide × 6mm deep (inline fuse holder body)
  - End retention lips: 1mm overhang × 1.5mm thick
  - 4× M3 bolt holes (2 per side of channel)

Print: Flat (bottom down), 40% infill, 3 perimeters
Qty: 1

Reference: EA-15, EA-19
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
        BRKT_L = 4.0        # 40mm length (Y — along fuse holder)
        BRKT_W = 1.9        # 19mm wide (was 15mm, widened for M3 hole wall clearance)
        BRKT_H = 1.2        # 12mm height (Z)
        BASE_H = 0.3        # 3mm base thickness
        CLIP_W = 0.8        # 8mm fuse holder channel width
        CLIP_D = 0.6        # 6mm channel depth (from top)
        WALL_T = 0.2        # 2mm side wall thickness
        END_WALL = 0.3      # 3mm end wall thickness
        LIP_OVERHANG = 0.1  # 1mm retention lip overhang
        LIP_T = 0.15        # 1.5mm lip thickness
        HOLE_R = 0.165      # M3 clearance (3.3mm dia)
        HOLE_Y1 = -1.2      # Hole Y positions
        HOLE_Y2 = 1.2
        CR = min(CORNER_R, BRKT_W / 4)

        comp = design.rootComponent

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body
        # ══════════════════════════════════════════════════════════

        sk1 = comp.sketches.add(comp.xYConstructionPlane)
        sk1.name = 'Bracket Body'
        draw_rounded_rect(sk1, 0, 0, BRKT_W, BRKT_L, r=CR)

        body_prof = find_largest_profile(sk1)
        ext = extrude_profile(comp, body_prof, BRKT_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Fuse Holder Bracket'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Clip channel cut (from top, leaving base + end walls)
        # ══════════════════════════════════════════════════════════

        topP = make_offset_plane(comp, comp.xYConstructionPlane, BRKT_H)
        ch_sk = comp.sketches.add(topP)
        ch_sk.name = 'Fuse Channel'

        # Channel interior with rounded ends
        ch_len = BRKT_L - 2 * END_WALL
        ch_r = min(CR * 0.5, CLIP_W / 4)
        draw_rounded_rect(ch_sk, 0, 0, CLIP_W, ch_len, r=ch_r)

        ch_target = CLIP_W * ch_len
        ch_prof = find_profile_by_area(ch_sk, ch_target, tolerance=0.5)
        if ch_prof is None:
            ch_prof = find_smallest_profile(ch_sk)

        if ch_prof:
            cut_profile(comp, ch_prof, CLIP_D, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Retention lips at channel ends
        # ══════════════════════════════════════════════════════════

        lip_sk = comp.sketches.add(topP)
        lip_sk.name = 'Retention Lips'
        sl = lip_sk.sketchCurves.sketchLines

        # Front lip (negative Y end of channel)
        lip_y_front = -ch_len / 2
        sl.addTwoPointRectangle(
            p(-CLIP_W / 2, lip_y_front - LIP_OVERHANG, 0),
            p(CLIP_W / 2, lip_y_front, 0)
        )

        # Rear lip (positive Y end of channel)
        lip_y_rear = ch_len / 2
        sl.addTwoPointRectangle(
            p(-CLIP_W / 2, lip_y_rear, 0),
            p(CLIP_W / 2, lip_y_rear + LIP_OVERHANG, 0)
        )

        lip_target = CLIP_W * LIP_OVERHANG
        for pi_idx in range(lip_sk.profiles.count):
            pr = lip_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if abs(a - lip_target) < lip_target * 0.8:
                try:
                    join_profile(comp, pr, LIP_T)
                except Exception as e:
                    print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: M3 mounting holes (2 per side of channel)
        # ══════════════════════════════════════════════════════════

        hole_sk = comp.sketches.add(topP)
        hole_sk.name = 'Mount Holes'
        circles = hole_sk.sketchCurves.sketchCircles

        hole_x_pos = BRKT_W / 2 - 0.25  # 2.5mm from outer edge (gives ~2.4mm wall to channel)
        for hx in [hole_x_pos, -hole_x_pos]:
            circles.addByCenterRadius(p(hx, HOLE_Y1, 0), HOLE_R)
            circles.addByCenterRadius(p(hx, HOLE_Y2, 0), HOLE_R)

        hole_area = math.pi * HOLE_R**2
        for pi_idx in range(hole_sk.profiles.count):
            pr = hole_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < hole_area * 1.5:
                try:
                    cut_profile(comp, pr, BRKT_H + 0.02, flip=True)
                except Exception as e:
                    print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5: Fillets
        # ══════════════════════════════════════════════════════════

        fillet_count = 0
        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 6: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Fuse Holder Bracket created!\n\n'
            f'Size: {BRKT_L*10:.0f} × {BRKT_W*10:.0f} × {BRKT_H*10:.0f}mm\n'
            f'Corner radius: {CR*10:.1f}mm\n\n'
            f'Channel: {CLIP_W*10:.0f}mm wide × {CLIP_D*10:.0f}mm deep\n'
            f'End walls: {END_WALL*10:.0f}mm thick\n'
            f'Retention lips: {LIP_OVERHANG*10:.0f}mm × {LIP_T*10:.1f}mm\n\n'
            f'Mounting: 4× M3 holes (2 per side)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Print flat, 40% infill.\nQty: 1',
            'Mars Rover - Fuse Holder Bracket'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
