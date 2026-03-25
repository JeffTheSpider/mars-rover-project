"""
Mars Rover Servo Mount Bracket — Phase 1 (0.4 Scale)
======================================================

Small bracket that mounts an SG90 micro servo to the suspension connector.
The servo's horn connects to the steering horn link to rotate the wheel.

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - SG90 pocket via shared helper (rounded corners)
  - Cable routing slot (3mm wide channel for servo wires)
  - 0.5mm fillets on all external edges
  - Improved horn slot with chamfered entry
  - Proper M2 mounting holes with counterbores

40 × 18 × 25mm bracket
Qty: 4 (FL, FR, RL, RR — one per steered wheel)

Print: Pocket opening up | Supports: None | Perimeters: 4 | Infill: 50%

Reference: EA-08, EA-27
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, CORNER_R,
    SG90_W, SG90_D, SG90_POCKET_DEPTH, SG90_TAB_W, SG90_TAB_H,
    M2_CLEAR,
    draw_rounded_rect,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_sg90_pocket,
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

        # NOTE: For the steering 4-bar linkage to work, the servo output shaft height
        # must match the steering knuckle arm height. Verify at assembly time that
        # both the servo mount and steering bracket position these features at the
        # same Z-level on the front_wheel_connector.

        # ── Dimensions (cm) ──
        BRACKET_L = 4.0     # 40mm (along arm, Y)
        BRACKET_W = 1.8     # 18mm (across arm, X)
        BRACKET_H = 2.5     # 25mm (vertical, Z)

        # M2 mounting holes for servo tabs
        M2_SPACING = 2.75   # 27.5mm centre-to-centre

        # Horn slot
        HORN_SLOT_R = 0.6   # 6mm radius (12mm dia)
        # SG90 shaft is 6mm from edge, not centred on body
        SHAFT_OFFSET = SG90_W / 2 - 0.6  # offset from body centre (cm)

        # M3 arm mounting
        ARM_MOUNT_SPACING = 2.0  # 20mm

        # Cable routing slot
        CABLE_W = 0.3       # 3mm wide
        CABLE_D = 0.4       # 4mm deep

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Bracket Body'
        draw_rounded_rect(sk, 0, 0, BRACKET_L, BRACKET_W, r=CORNER_R)

        target = BRACKET_L * BRACKET_W - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, BRACKET_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Servo Mount'

        # ══════════════════════════════════════════════════════════
        # STEP 2: SG90 servo pocket (from top) via helper
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, BRACKET_H)
        make_sg90_pocket(comp, top_plane, cx=0, cy=0, tab_slots=True)

        # ══════════════════════════════════════════════════════════
        # STEP 3: M2 mounting holes (through bracket for servo tabs)
        # ══════════════════════════════════════════════════════════

        m2_sk = comp.sketches.add(top_plane)
        m2_sk.name = 'M2 Holes'

        for hx in [-M2_SPACING / 2, M2_SPACING / 2]:
            m2_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(hx, 0), M2_CLEAR
            )

        for pi in range(m2_sk.profiles.count):
            pr = m2_sk.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.1:
                cut_profile(comp, pr, BRACKET_H + 0.01, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Horn slot (circular cut for horn clearance)
        # ══════════════════════════════════════════════════════════

        horn_sk = comp.sketches.add(top_plane)
        horn_sk.name = 'Horn Slot'
        # SG90 shaft is NOT centred — offset by SHAFT_OFFSET in -X
        horn_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(-SHAFT_OFFSET, 0), HORN_SLOT_R
        )

        horn_prof = find_smallest_profile(horn_sk)
        if horn_prof:
            horn_input = extrudes.createInput(
                horn_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            horn_input.setDistanceExtent(True, val(BRACKET_H + 0.01))
            try:
                extrudes.add(horn_input)
            except Exception as e:
                print(f'  Warning: {e}')

        # Horn slot chamfer (entry guide for horn)
        if body:
            from rover_cad_helpers import add_chamfer
            add_chamfer(comp, body, HORN_SLOT_R, CHAMFER_STD)

        # ══════════════════════════════════════════════════════════
        # STEP 5: Cable routing slot
        # A channel on the side wall for servo wires to exit
        # ══════════════════════════════════════════════════════════

        cable_plane = make_offset_plane(
            comp, comp.yZConstructionPlane, BRACKET_L / 2
        )
        cable_sk = comp.sketches.add(cable_plane)
        cable_sk.name = 'Cable Slot'
        # Slot on the +Y face, at servo pocket level
        cable_z = BRACKET_H - SG90_POCKET_DEPTH / 2
        draw_rounded_rect(
            cable_sk,
            -cable_z, 0,
            CABLE_D, CABLE_W,
            r=0.05
        )
        cable_target = CABLE_D * CABLE_W
        cable_prof = find_profile_by_area(cable_sk, cable_target, tolerance=0.6)
        if cable_prof:
            cable_input = extrudes.createInput(
                cable_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            cable_input.setDistanceExtent(True, val(0.5))  # 5mm into wall
            try:
                extrudes.add(cable_input)
            except Exception as e:
                print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 6: M3 clearance through-holes (for bolting to connector)
        # ══════════════════════════════════════════════════════════

        mount_sk = comp.sketches.add(comp.xYConstructionPlane)
        mount_sk.name = 'M3 Through-Holes'
        m3_r = 0.165  # 3.3mm dia M3 clearance
        mount_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, -ARM_MOUNT_SPACING / 2, 0), m3_r
        )
        mount_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, ARM_MOUNT_SPACING / 2, 0), m3_r
        )
        for pi_idx in range(mount_sk.profiles.count):
            pr = mount_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < math.pi * m3_r**2 * 1.5:
                try:
                    cut_profile(comp, pr, BRACKET_H + 0.02, flip=False)
                except Exception as e:
                    print(f'  Warning: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 7: External fillets
        # ══════════════════════════════════════════════════════════

        if body:
            fillet_count = add_edge_fillets(comp, body, FILLET_STD)
        else:
            fillet_count = 0

        # ══════════════════════════════════════════════════════════
        # STEP 8: Zoom and report
        # ══════════════════════════════════════════════════════════

        zoom_fit(app)

        ui.messageBox(
            'Servo Mount Bracket created!\n\n'
            f'Body: {BRACKET_L*10:.0f} × {BRACKET_W*10:.0f} × '
            f'{BRACKET_H*10:.0f}mm (rounded corners)\n\n'
            f'SG90 pocket: {SG90_W*10:.1f} × {SG90_D*10:.1f}mm, '
            f'{SG90_POCKET_DEPTH*10:.0f}mm deep (with tab slots)\n'
            f'M2 holes: {M2_SPACING*10:.1f}mm spacing (through)\n'
            f'Horn slot: {HORN_SLOT_R*20:.0f}mm dia (chamfered)\n'
            f'Cable slot: {CABLE_W*10:.0f}×{CABLE_D*10:.0f}mm routing channel\n'
            f'Arm mount: 2× M3 through-holes ({ARM_MOUNT_SPACING*10:.0f}mm, bolts to connector)\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Qty: 4 (FL, FR, RL, RR)\n'
            'Print pocket-up, no supports.',
            'Mars Rover - Servo Mount'
        )

    except Exception as e:
        print(f'  Warning: {e}')
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
