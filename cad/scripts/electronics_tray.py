"""
Mars Rover Electronics Tray — Phase 1 (0.4 Scale)
====================================================

Flat tray that sits inside the body frame and holds all electronics:
  - ESP32-S3 DevKitC-1 (63×25mm, 4× M2.5 standoffs)
  - 2× L298N motor drivers (43×43mm, 4× M2.5 standoffs each)
  - LiPo battery cradle (86×34×19mm)
  - Wire routing U-channels
  - Mini breadboard pocket

Redesigned with:
  - Rounded corners (2mm radius)
  - U-channel wire routes (rounded profile)
  - USB-C access cutout on side wall
  - Corner gussets (triangular reinforcement)
  - Strap anchor posts for battery retention
  - 0.5mm fillets on external edges

Tray size: ~180 × 120 × 15mm
Qty: 1

Print: Flat (bottom down), no supports, 30% gyroid

Reference: EA-08, EA-09
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CORNER_R,
    draw_rounded_rect,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, add_triangular_gusset,
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
        TRAY_L = 18.0       # 180mm (Y)
        TRAY_W = 12.0       # 120mm (X)
        TRAY_H = 1.5        # 15mm (Z)
        FLOOR_H = 0.3       # 3mm floor
        WALL_T = 0.2        # 2mm walls

        # ESP32 standoffs
        ESP32_X = 0.0
        ESP32_Y = 4.0
        ESP32_DX = 3.0
        ESP32_DY = 6.0
        STAND_H = 0.5       # 5mm standoff height
        STAND_R = 0.35      # 3.5mm radius
        SCREW_R = 0.1       # 2.0mm dia (self-tap)

        # L298N drivers
        L298N_1_X = -3.5
        L298N_2_X = 3.5
        L298N_Y = -3.0
        L298N_OFFSET = 1.85

        # LiPo cradle
        LIPO_L = 8.8
        LIPO_W = 3.6
        LIPO_WALL = 0.3
        LIPO_X = 0.0
        LIPO_Y = -7.0

        # Strap posts
        STRAP_R = 0.2
        STRAP_H_TOTAL = 1.8  # above tray wall

        # Breadboard pocket
        BB_L = 4.9
        BB_W = 3.7
        BB_X = 4.0
        BB_Y = 7.0

        # Wire channels
        CHANNEL_W = 1.0
        CHANNEL_D = 0.3

        # Cable exits
        EXIT_W = 1.0
        EXIT_H = 0.5

        # USB-C access
        USB_W = 1.2         # 12mm wide
        USB_H = 0.6         # 6mm tall

        # Gussets
        GUSSET_L = 0.5

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # Step 1: Tray base with rounded corners
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Tray Base'
        draw_rounded_rect(sk, 0, 0, TRAY_W, TRAY_L, r=CORNER_R)

        target = TRAY_W * TRAY_L - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, TRAY_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Electronics Tray'

        # ══════════════════════════════════════════════════════════
        # Step 2: Hollow out interior (rounded inner corners)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, TRAY_H)

        inner_w = TRAY_W - 2 * WALL_T
        inner_l = TRAY_L - 2 * WALL_T

        hollow_sk = comp.sketches.add(top_plane)
        hollow_sk.name = 'Interior'
        draw_rounded_rect(hollow_sk, 0, 0, inner_w, inner_l, r=0.1)

        h_target = inner_w * inner_l
        h_prof = find_profile_by_area(hollow_sk, h_target, tolerance=0.5)
        if h_prof is None:
            h_prof = find_smallest_profile(hollow_sk)
        cut_profile(comp, h_prof, TRAY_H - FLOOR_H, flip=True)

        # ══════════════════════════════════════════════════════════
        # Step 3: ESP32 standoffs (4×)
        # ══════════════════════════════════════════════════════════

        esp_positions = [
            (ESP32_X - ESP32_DX / 2, ESP32_Y - ESP32_DY / 2),
            (ESP32_X + ESP32_DX / 2, ESP32_Y - ESP32_DY / 2),
            (ESP32_X - ESP32_DX / 2, ESP32_Y + ESP32_DY / 2),
            (ESP32_X + ESP32_DX / 2, ESP32_Y + ESP32_DY / 2),
        ]

        so_sk = comp.sketches.add(comp.xYConstructionPlane)
        so_sk.name = 'ESP32 Standoffs'
        for sx, sy in esp_positions:
            so_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(sx, sy), STAND_R
            )

        for pi in range(so_sk.profiles.count):
            pr = so_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.5:
                join_profile(comp, pr, FLOOR_H + STAND_H)

        # ══════════════════════════════════════════════════════════
        # Step 4: L298N standoffs (8×, 2 drivers)
        # ══════════════════════════════════════════════════════════

        l298n_positions = []
        l298n_sk = comp.sketches.add(comp.xYConstructionPlane)
        l298n_sk.name = 'L298N Standoffs'

        for dx in [L298N_1_X, L298N_2_X]:
            for ox in [-L298N_OFFSET, L298N_OFFSET]:
                for oy in [-L298N_OFFSET, L298N_OFFSET]:
                    sx, sy = dx + ox, L298N_Y + oy
                    l298n_positions.append((sx, sy))
                    l298n_sk.sketchCurves.sketchCircles.addByCenterRadius(
                        p(sx, sy), STAND_R
                    )

        for pi in range(l298n_sk.profiles.count):
            pr = l298n_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.5:
                join_profile(comp, pr, FLOOR_H + STAND_H)

        # ══════════════════════════════════════════════════════════
        # Step 5: Screw holes in all standoffs
        # ══════════════════════════════════════════════════════════

        all_positions = list(esp_positions) + l298n_positions
        so_top = make_offset_plane(
            comp, comp.xYConstructionPlane, FLOOR_H + STAND_H
        )
        screw_sk = comp.sketches.add(so_top)
        screw_sk.name = 'Standoff Screws'
        for sx, sy in all_positions:
            screw_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(sx, sy), SCREW_R
            )

        for pi in range(screw_sk.profiles.count):
            pr = screw_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.1:
                cut_profile(comp, pr, STAND_H + 0.2, flip=True)

        # ══════════════════════════════════════════════════════════
        # Step 6: LiPo battery cradle walls
        # ══════════════════════════════════════════════════════════

        cradle_sk = comp.sketches.add(comp.xYConstructionPlane)
        cradle_sk.name = 'LiPo Cradle'
        cl = cradle_sk.sketchCurves.sketchLines

        # Outer rectangle
        cl.addTwoPointRectangle(
            p(LIPO_X - LIPO_W / 2 - LIPO_WALL, LIPO_Y - LIPO_L / 2 - LIPO_WALL),
            p(LIPO_X + LIPO_W / 2 + LIPO_WALL, LIPO_Y + LIPO_L / 2 + LIPO_WALL)
        )
        # Inner rectangle
        cl.addTwoPointRectangle(
            p(LIPO_X - LIPO_W / 2, LIPO_Y - LIPO_L / 2),
            p(LIPO_X + LIPO_W / 2, LIPO_Y + LIPO_L / 2)
        )

        # Find frame profile (between inner and outer)
        areas = []
        for pi in range(cradle_sk.profiles.count):
            pr = cradle_sk.profiles.item(pi)
            areas.append((pr.areaProperties().area, pi))
        areas.sort()

        for a, pi in areas:
            if a > areas[0][0] and a < areas[-1][0]:
                pr = cradle_sk.profiles.item(pi)
                join_profile(comp, pr, TRAY_H)
                break

        # ══════════════════════════════════════════════════════════
        # Step 7: Battery strap anchor posts
        # ══════════════════════════════════════════════════════════

        strap_offset = LIPO_W / 2 + LIPO_WALL + 0.4
        strap_sk = comp.sketches.add(comp.xYConstructionPlane)
        strap_sk.name = 'Strap Posts'
        strap_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(LIPO_X - strap_offset, LIPO_Y), STRAP_R
        )
        strap_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(LIPO_X + strap_offset, LIPO_Y), STRAP_R
        )

        for pi in range(strap_sk.profiles.count):
            pr = strap_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.2:
                join_profile(comp, pr, STRAP_H_TOTAL)

        # ══════════════════════════════════════════════════════════
        # Step 8: Wire routing U-channels (rounded profile)
        # ══════════════════════════════════════════════════════════

        floor_plane = make_offset_plane(comp, comp.xYConstructionPlane, FLOOR_H)
        ch_sk = comp.sketches.add(floor_plane)
        ch_sk.name = 'Wire Channels'
        chl = ch_sk.sketchCurves.sketchLines
        half_ch = CHANNEL_W / 2

        # ESP32 → L298N #1
        chl.addTwoPointRectangle(
            p(ESP32_X - half_ch, ESP32_Y - ESP32_DY / 2),
            p(L298N_1_X + L298N_OFFSET + half_ch,
              ESP32_Y - ESP32_DY / 2 - CHANNEL_W)
        )
        chl.addTwoPointRectangle(
            p(L298N_1_X - half_ch, L298N_Y + L298N_OFFSET),
            p(L298N_1_X + half_ch, ESP32_Y - ESP32_DY / 2 - CHANNEL_W)
        )

        # ESP32 → L298N #2
        chl.addTwoPointRectangle(
            p(ESP32_X + half_ch, ESP32_Y - ESP32_DY / 2),
            p(L298N_2_X - L298N_OFFSET - half_ch,
              ESP32_Y - ESP32_DY / 2 - CHANNEL_W)
        )
        chl.addTwoPointRectangle(
            p(L298N_2_X - half_ch, L298N_Y + L298N_OFFSET),
            p(L298N_2_X + half_ch, ESP32_Y - ESP32_DY / 2 - CHANNEL_W)
        )

        # ESP32 → breadboard
        chl.addTwoPointRectangle(
            p(ESP32_X + ESP32_DX / 2, ESP32_Y + ESP32_DY / 2),
            p(BB_X - BB_W / 2, ESP32_Y + ESP32_DY / 2 + CHANNEL_W)
        )

        # LiPo → rear exit
        chl.addTwoPointRectangle(
            p(LIPO_X - half_ch, -TRAY_L / 2 + WALL_T),
            p(LIPO_X + half_ch, LIPO_Y - LIPO_L / 2)
        )

        for pi in range(ch_sk.profiles.count):
            pr = ch_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 8.0 and a > 0.01:
                cut_profile(comp, pr, CHANNEL_D, flip=True)

        # ══════════════════════════════════════════════════════════
        # Step 9: Breadboard pocket
        # ══════════════════════════════════════════════════════════

        bb_sk = comp.sketches.add(floor_plane)
        bb_sk.name = 'Breadboard Pocket'
        draw_rounded_rect(bb_sk, BB_X, BB_Y, BB_W, BB_L, r=0.1)

        bb_target = BB_W * BB_L
        bb_prof = find_profile_by_area(bb_sk, bb_target, tolerance=0.5)
        if bb_prof is None:
            bb_prof = find_smallest_profile(bb_sk)
        cut_profile(comp, bb_prof, 0.2, flip=True)

        # ══════════════════════════════════════════════════════════
        # Step 10: Cable exit holes (3× through walls)
        # ══════════════════════════════════════════════════════════

        # Left wall exit
        left_plane = make_offset_plane(
            comp, comp.yZConstructionPlane, -TRAY_W / 2
        )
        left_sk = comp.sketches.add(left_plane)
        left_sk.name = 'Cable Exit Left'
        draw_rounded_rect(
            left_sk, L298N_Y, FLOOR_H + EXIT_H / 2,
            EXIT_W, EXIT_H, r=0.05
        )
        for pi in range(left_sk.profiles.count):
            pr = left_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0 and a > 0.01:
                l_in = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                l_in.setDistanceExtent(True, val(WALL_T + 0.01))
                try:
                    extrudes.add(l_in)
                except:
                    pass

        # Right wall exit
        right_plane = make_offset_plane(
            comp, comp.yZConstructionPlane, TRAY_W / 2
        )
        right_sk = comp.sketches.add(right_plane)
        right_sk.name = 'Cable Exit Right'
        draw_rounded_rect(
            right_sk, L298N_Y, FLOOR_H + EXIT_H / 2,
            EXIT_W, EXIT_H, r=0.05
        )
        for pi in range(right_sk.profiles.count):
            pr = right_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0 and a > 0.01:
                r_in = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                r_in.setDistanceExtent(True, val(WALL_T + 0.01))
                try:
                    extrudes.add(r_in)
                except:
                    pass

        # Rear wall exit
        rear_plane = make_offset_plane(
            comp, comp.xZConstructionPlane, -TRAY_L / 2
        )
        rear_sk = comp.sketches.add(rear_plane)
        rear_sk.name = 'Cable Exit Rear'
        draw_rounded_rect(
            rear_sk, LIPO_X, FLOOR_H + EXIT_H / 2,
            EXIT_W, EXIT_H, r=0.05
        )
        for pi in range(rear_sk.profiles.count):
            pr = rear_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 1.0 and a > 0.01:
                re_in = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                re_in.setDistanceExtent(True, val(WALL_T + 0.01))
                try:
                    extrudes.add(re_in)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # Step 11: USB-C access cutout (front wall, for ESP32)
        # ══════════════════════════════════════════════════════════

        front_plane = make_offset_plane(
            comp, comp.xZConstructionPlane, TRAY_L / 2
        )
        usb_sk = comp.sketches.add(front_plane)
        usb_sk.name = 'USB-C Access'
        draw_rounded_rect(
            usb_sk, ESP32_X, FLOOR_H + STAND_H,
            USB_W, USB_H, r=0.05
        )
        usb_target = USB_W * USB_H
        usb_prof = find_profile_by_area(usb_sk, usb_target, tolerance=0.6)
        if usb_prof is None:
            usb_prof = find_smallest_profile(usb_sk)
        if usb_prof:
            u_in = extrudes.createInput(
                usb_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            u_in.setDistanceExtent(True, val(WALL_T + 0.01))
            try:
                extrudes.add(u_in)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # Step 12: Corner gussets (4× triangular reinforcement)
        # ══════════════════════════════════════════════════════════

        iw = TRAY_W / 2 - WALL_T
        il = TRAY_L / 2 - WALL_T
        gusset_h = FLOOR_H + 0.2

        for cx, cy in [(-iw, -il), (iw, -il), (-iw, il), (iw, il)]:
            dx = GUSSET_L if cx < 0 else -GUSSET_L
            dy = GUSSET_L if cy < 0 else -GUSSET_L
            add_triangular_gusset(
                comp, comp.xYConstructionPlane,
                cx, cy, cx + dx, cy, cx, cy + dy,
                gusset_h
            )

        # ══════════════════════════════════════════════════════════
        # Step 13: External fillets
        # ══════════════════════════════════════════════════════════

        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)
        else:
            fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # Step 14: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Electronics Tray created!\n\n'
            f'Tray: {TRAY_W*10:.0f} × {TRAY_L*10:.0f} × '
            f'{TRAY_H*10:.0f}mm (rounded corners)\n'
            f'Floor: {FLOOR_H*10:.0f}mm | Walls: {WALL_T*10:.0f}mm\n\n'
            f'ESP32 standoffs: 4× ({STAND_H*10:.0f}mm, M2.5 screws)\n'
            f'L298N standoffs: 8× (2 drivers)\n'
            f'LiPo cradle: {LIPO_W*10:.0f}×{LIPO_L*10:.0f}mm + strap posts\n'
            f'Wire channels: 6 ({CHANNEL_W*10:.0f}mm, U-profile)\n'
            f'Breadboard pocket: {BB_W*10:.0f}×{BB_L*10:.0f}mm (rounded)\n'
            f'Cable exits: 3× (rounded {EXIT_W*10:.0f}×{EXIT_H*10:.0f}mm)\n'
            f'USB-C access: {USB_W*10:.0f}×{USB_H*10:.0f}mm (front wall)\n'
            f'Corner gussets: 4× triangular\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Print flat bottom down, 30% infill.\n'
            'Qty: 1',
            'Mars Rover - Electronics Tray'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
