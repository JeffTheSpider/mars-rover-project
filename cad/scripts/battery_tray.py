"""
Mars Rover Battery Tray — Phase 1
===================================

Standalone cradle for 2S LiPo 2200mAh battery pack.
Sits inside the electronics tray or bolts directly to body floor.

Designed for:
  - 2S LiPo: 86 × 34 × 19mm (varies by brand, +1mm clearance each side)
  - XT60 connector access on one end
  - JST-XH balance lead exit on same end
  - Strap slots for zip-tie or Velcro retention
  - 4× M3 bolt holes for mounting

Features:
  - Rounded-rect body (2mm corner radius)
  - Rounded interior pocket (1mm corner radius)
  - Strap slots through side walls (2 per side)
  - XT60 access cutout on front end wall
  - JST-XH cable exit slot on front end wall
  - Corner gussets for rigidity
  - 0.5mm fillets on external edges

Dimensions:
  - Interior: 88 × 36 × 20mm (battery + clearance)
  - Wall: 3mm, Floor: 3mm
  - External: 94 × 42 × 23mm
  - Strap slots: 3mm wide × 10mm long (2 per side)

Print: Flat (open top up), 30% infill, 3 perimeters
Qty: 1

Reference: EA-03 (power), EA-08 (body spec)
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
    make_offset_plane, add_edge_fillets, add_triangular_gusset,
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

        # ── Dimensions (cm) ──
        # Battery: 86 × 34 × 19mm
        BATT_L = 8.8        # 88mm interior length (X) — 86mm + 2mm clearance
        BATT_W = 3.6        # 36mm interior width (Y) — 34mm + 2mm clearance
        BATT_H = 2.0        # 20mm interior depth — 19mm + 1mm clearance
        WALL = 0.3           # 3mm walls
        FLOOR = 0.3          # 3mm floor
        OUTER_L = BATT_L + 2 * WALL  # 94mm
        OUTER_W = BATT_W + 2 * WALL  # 42mm
        TOTAL_H = BATT_H + FLOOR     # 23mm

        # Strap slots
        STRAP_W = 0.3       # 3mm wide
        STRAP_L = 1.0       # 10mm long
        STRAP_Z = FLOOR + 0.5  # 5mm above base (mid-height of battery)
        STRAP_SPACING = 2.5  # 25mm between strap pairs

        # XT60 connector cutout
        XT60_W = 1.6        # 16mm wide (XT60 housing)
        XT60_H = 1.0        # 10mm tall
        XT60_Z = FLOOR       # starts at floor level

        # JST-XH cable exit
        JST_W = 0.8         # 8mm wide
        JST_H = 0.5         # 5mm tall
        JST_Z = FLOOR + XT60_H + 0.2  # above XT60 cutout

        # Mounting holes
        HOLE_R = 0.165       # M3 clearance
        HOLE_X = OUTER_L / 2 - 0.5  # 5mm from ends
        HOLE_Y = OUTER_W / 2 - 0.5

        # Corner gussets
        GUSSET = 0.5         # 5mm gusset size

        CR = CORNER_R        # 2mm external corner radius
        CR_INT = 0.1         # 1mm internal corner radius

        comp = design.rootComponent

        # ══════════════════════════════════════════════════════════
        # STEP 1: Outer body — rounded-rect block
        # ══════════════════════════════════════════════════════════

        sk1 = comp.sketches.add(comp.xYConstructionPlane)
        sk1.name = 'Battery Tray Outer'
        draw_rounded_rect(sk1, 0, 0, OUTER_L, OUTER_W, r=CR)

        body_prof = find_largest_profile(sk1)
        ext = extrude_profile(comp, body_prof, TOTAL_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Battery Tray'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Interior pocket (cut from top)
        # ══════════════════════════════════════════════════════════

        topP = make_offset_plane(comp, comp.xYConstructionPlane, TOTAL_H)
        int_sk = comp.sketches.add(topP)
        int_sk.name = 'Battery Pocket'
        draw_rounded_rect(int_sk, 0, 0, BATT_L, BATT_W, r=CR_INT)

        int_target = BATT_L * BATT_W
        int_prof = find_profile_by_area(int_sk, int_target, tolerance=0.5)
        if int_prof is None:
            int_prof = find_smallest_profile(int_sk)

        if int_prof:
            cut_profile(comp, int_prof, BATT_H, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Strap slots through side walls (Y-facing)
        # ══════════════════════════════════════════════════════════
        # Sketch on XZ plane (offset to wall Y position), cut through
        # wall in Y direction so velcro/zip-tie can thread through.

        for y_sign in [1, -1]:
            y_wall = y_sign * OUTER_W / 2
            strap_wall_plane = make_offset_plane(
                comp, comp.xZConstructionPlane, y_wall
            )
            strap_sk = comp.sketches.add(strap_wall_plane)
            strap_sk.name = f'Strap Slots {"+" if y_sign > 0 else "-"}Y'
            sl = strap_sk.sketchCurves.sketchLines

            for x_off in [-STRAP_SPACING / 2, STRAP_SPACING / 2]:
                # On XZ plane: X stays X, Z becomes the vertical axis
                # Slot is STRAP_L wide (X) × STRAP_W tall (Z)
                sl.addTwoPointRectangle(
                    p(x_off - STRAP_L / 2, STRAP_Z, 0),
                    p(x_off + STRAP_L / 2, STRAP_Z + STRAP_W, 0)
                )

            strap_target = STRAP_L * STRAP_W
            for pi_idx in range(strap_sk.profiles.count):
                pr = strap_sk.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if abs(a - strap_target) < strap_target * 0.6:
                    try:
                        cut_profile(comp, pr, WALL + 0.01, flip=(y_sign > 0))
                    except Exception as e:
                        print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: XT60 connector access cutout (front end wall)
        # ══════════════════════════════════════════════════════════

        xt60_plane = make_offset_plane(comp, comp.xYConstructionPlane, XT60_Z)
        xt60_sk = comp.sketches.add(xt60_plane)
        xt60_sk.name = 'XT60 Access'
        xt_lines = xt60_sk.sketchCurves.sketchLines

        # Cutout through front wall (+X end)
        x_outer = OUTER_L / 2
        x_inner = OUTER_L / 2 - WALL - 0.01
        xt_lines.addTwoPointRectangle(
            p(x_inner, -XT60_W / 2, 0),
            p(x_outer, XT60_W / 2, 0)
        )

        xt_target = (WALL + 0.01) * XT60_W
        xt_prof = find_profile_by_area(xt60_sk, xt_target, tolerance=0.6)
        if xt_prof is None:
            xt_prof = find_smallest_profile(xt60_sk)

        if xt_prof:
            try:
                cut_profile(comp, xt_prof, XT60_H, flip=False)
            except Exception as e:
                print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5: JST-XH balance lead exit (above XT60)
        # ══════════════════════════════════════════════════════════

        jst_plane = make_offset_plane(comp, comp.xYConstructionPlane, JST_Z)
        jst_sk = comp.sketches.add(jst_plane)
        jst_sk.name = 'JST-XH Exit'
        jst_lines = jst_sk.sketchCurves.sketchLines

        jst_lines.addTwoPointRectangle(
            p(x_inner, -JST_W / 2, 0),
            p(x_outer, JST_W / 2, 0)
        )

        jst_target = (WALL + 0.01) * JST_W
        jst_prof = find_profile_by_area(jst_sk, jst_target, tolerance=0.6)
        if jst_prof is None:
            jst_prof = find_smallest_profile(jst_sk)

        if jst_prof:
            try:
                cut_profile(comp, jst_prof, JST_H, flip=False)
            except Exception as e:
                print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 6: M3 mounting holes through floor (4 corners)
        # ══════════════════════════════════════════════════════════

        hole_sk = comp.sketches.add(topP)
        hole_sk.name = 'Mount Holes'
        circles = hole_sk.sketchCurves.sketchCircles

        for hx in [-HOLE_X, HOLE_X]:
            for hy in [-HOLE_Y, HOLE_Y]:
                circles.addByCenterRadius(p(hx, hy, 0), HOLE_R)

        hole_area = math.pi * HOLE_R**2
        for pi_idx in range(hole_sk.profiles.count):
            pr = hole_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < hole_area * 1.5:
                try:
                    cut_profile(comp, pr, TOTAL_H + 0.02, flip=True)
                except Exception as e:
                    print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 7: Corner gussets (interior corners, floor to wall)
        # ══════════════════════════════════════════════════════════

        if body:
            gusset_sk = comp.sketches.add(comp.xYConstructionPlane)
            gusset_sk.name = 'Corner Gussets'
            gl = gusset_sk.sketchCurves.sketchLines

            # 4 corner gusset triangles (inside corners of pocket)
            for x_sign in [-1, 1]:
                for y_sign in [-1, 1]:
                    cx = x_sign * (BATT_L / 2 - 0.01)
                    cy = y_sign * (BATT_W / 2 - 0.01)
                    gx = cx - x_sign * GUSSET
                    gy = cy - y_sign * GUSSET

                    gl.addByTwoPoints(p(cx, cy, 0), p(gx, cy, 0))
                    gl.addByTwoPoints(p(gx, cy, 0), p(cx, gy, 0))
                    gl.addByTwoPoints(p(cx, gy, 0), p(cx, cy, 0))

            gusset_target = 0.5 * GUSSET * GUSSET
            for pi_idx in range(gusset_sk.profiles.count):
                pr = gusset_sk.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if abs(a - gusset_target) < gusset_target * 0.6:
                    try:
                        join_profile(comp, pr, BATT_H)
                    except Exception as e:
                        print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 8: Fillets
        # ══════════════════════════════════════════════════════════

        fillet_count = 0
        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 9: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Battery Tray created!\n\n'
            f'External: {OUTER_L*10:.0f} × {OUTER_W*10:.0f} × '
            f'{TOTAL_H*10:.0f}mm\n'
            f'Interior: {BATT_L*10:.0f} × {BATT_W*10:.0f} × '
            f'{BATT_H*10:.0f}mm\n'
            f'Wall: {WALL*10:.0f}mm  Floor: {FLOOR*10:.0f}mm\n'
            f'Corner radius: {CR*10:.1f}mm ext, {CR_INT*10:.0f}mm int\n\n'
            f'Strap slots: 4× ({STRAP_L*10:.0f}×{STRAP_W*10:.0f}mm)\n'
            f'XT60 access: {XT60_W*10:.0f}×{XT60_H*10:.0f}mm cutout\n'
            f'JST-XH exit: {JST_W*10:.0f}×{JST_H*10:.0f}mm slot\n\n'
            f'Mounting: 4× M3 holes (corners)\n'
            f'Corner gussets: {GUSSET*10:.0f}mm\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Fits 2S LiPo 2200mAh (86×34×19mm).\n'
            'Strap through slots with zip-tie or Velcro.\n'
            'Print open-top up, 30% infill.\nQty: 1',
            'Mars Rover - Battery Tray'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
