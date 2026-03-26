"""
Mars Rover Fixed Wheel Mount — Phase 1 (0.4 Scale)
=====================================================

Simple bracket that bolts to the middle wheel connector and holds an
N20 motor for the non-steered middle wheels. No steering pivot needed.

Redesigned with:
  - Rounded-rect body (2mm corner radius)
  - N20 motor clip via shared helper (rounded pocket)
  - Reinforcement ribs between mount face and motor pocket
  - 0.5mm fillets on all external edges
  - Chamfered shaft exit hole
  - Improved zip-tie retention slot geometry

25 × 25 × 30mm body
Qty: 2 (ML, MR — middle left, middle right)

Print orientation: Large flat face down (25×25mm face)
Supports: None | Perimeters: 4 | Infill: 50% gyroid

Reference: EA-08
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, FILLET_STD, CHAMFER_STD, CORNER_R,
    N20_W, N20_H, N20_D, N20_SHAFT_EXIT,
    draw_rounded_rect,
    find_largest_profile, find_smallest_profile, find_profile_by_area,
    extrude_profile, cut_profile, join_profile,
    make_offset_plane, make_n20_clip,
    add_edge_fillets, add_triangular_gusset, zoom_fit,
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
        MOUNT_L = 2.5       # 25mm (along arm direction, Y)
        MOUNT_W = 2.5       # 25mm (across arm, X)
        MOUNT_H = 3.0       # 30mm (vertical, Z)

        # Shaft exit
        SHAFT_HOLE_R = N20_SHAFT_EXIT  # 2mm radius (4mm hole)

        # M3 heat-set insert spacing
        BOLT_SPACING = 1.6  # 16mm between bolt centres (matches middle_wheel_connector)

        # Zip-tie slot
        ZIPTIE_W = 0.35     # 3.5mm slot width
        ZIPTIE_DEPTH = 0.2  # 2mm deep
        ZIPTIE_Z = N20_D * 0.3  # 30% up from bottom

        # Ribs
        RIB_THICK = 0.15    # 1.5mm rib thickness

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect body
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Mount Body'
        draw_rounded_rect(sk, 0, 0, MOUNT_W, MOUNT_L, r=CORNER_R)

        target = MOUNT_W * MOUNT_L - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        ext = extrude_profile(comp, prof, MOUNT_H)
        body = ext.bodies.item(0) if ext else None
        if body:
            body.name = 'Fixed Wheel Mount'

        # ══════════════════════════════════════════════════════════
        # STEP 2: N20 motor clip pocket (horizontal — shaft toward wheel)
        # FIX C2: Motor pocket cut from side face (YZ plane) so motor
        # sits horizontally with shaft pointing out in -X toward wheel.
        # ══════════════════════════════════════════════════════════

        motor_entry_plane = make_offset_plane(
            comp, comp.yZConstructionPlane, MOUNT_W / 2
        )
        motor_result = make_n20_clip(
            comp, motor_entry_plane,
            cx=0, cy=MOUNT_H / 2,  # centred on Y=0, mid-height Z
        )

        # ══════════════════════════════════════════════════════════
        # STEP 3: Shaft exit hole (through opposite side wall)
        # Motor shaft exits through the -X face toward the wheel.
        # ══════════════════════════════════════════════════════════

        shaft_plane = make_offset_plane(
            comp, comp.yZConstructionPlane, -(MOUNT_W / 2 - 0.001)
        )
        shaft_sk = comp.sketches.add(shaft_plane)
        shaft_sk.name = 'Shaft Exit'
        shaft_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, MOUNT_H / 2, 0), SHAFT_HOLE_R
        )

        shaft_prof = find_smallest_profile(shaft_sk)
        if shaft_prof:
            shaft_input = extrudes.createInput(
                shaft_prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            shaft_input.setDistanceExtent(False, val(MOUNT_W))
            try:
                extrudes.add(shaft_input)
            except Exception as e:
                print(f'  Warning: shaft exit cut failed: {e}')

        # Shaft exit chamfer (entry guide)
        if body:
            shaft_edges = adsk.core.ObjectCollection.create()
            for ei in range(body.edges.count):
                edge = body.edges.item(ei)
                geom = edge.geometry
                if isinstance(geom, adsk.core.Circle3D):
                    if abs(geom.radius - SHAFT_HOLE_R) < 0.02:
                        shaft_edges.add(edge)

            if shaft_edges.count > 0:
                try:
                    cham = comp.features.chamferFeatures
                    cham_in = cham.createInput2()
                    cham_in.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                        shaft_edges, val(CHAMFER_STD), True
                    )
                    cham.add(cham_in)
                except Exception as e:
                    print(f'  Warning: shaft exit chamfer failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 4: M3 clearance through-holes (for bolting to connector)
        # ══════════════════════════════════════════════════════════

        # FIX C1: Bolt holes along X to match middle_wheel_connector's
        # heat-set inserts (axis='x' in make_heat_set_pair)
        top_plane = make_offset_plane(comp, comp.xYConstructionPlane, MOUNT_H)
        mount_sk = comp.sketches.add(top_plane)
        mount_sk.name = 'M3 Through-Holes'
        m3_r = 0.165  # 3.3mm dia M3 clearance
        mount_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(-BOLT_SPACING / 2, 0, 0), m3_r
        )
        mount_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(BOLT_SPACING / 2, 0, 0), m3_r
        )
        for pi_idx in range(mount_sk.profiles.count):
            pr = mount_sk.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < math.pi * m3_r**2 * 1.5:
                try:
                    cut_profile(comp, pr, MOUNT_H + 0.02, flip=True)
                except Exception as e:
                    print(f'  Warning: M3 through-hole cut failed: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5: Zip-tie slot across motor pocket for retention
        # ══════════════════════════════════════════════════════════

        zt_plane = make_offset_plane(comp, comp.xYConstructionPlane, ZIPTIE_Z)
        zt_sk = comp.sketches.add(zt_plane)
        zt_sk.name = 'Zip Tie Slot'

        # Rounded slot running across the body in X direction
        draw_rounded_rect(zt_sk, 0, 0, MOUNT_W + 0.02, ZIPTIE_W, r=0.05)

        zt_target = (MOUNT_W + 0.02) * ZIPTIE_W
        zt_prof = find_profile_by_area(zt_sk, zt_target, tolerance=0.6)
        if zt_prof is None:
            zt_prof = find_largest_profile(zt_sk)
        cut_profile(comp, zt_prof, ZIPTIE_DEPTH, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 6: Reinforcement ribs (2x diagonal gussets)
        # Connect top mount face to motor pocket walls
        # ══════════════════════════════════════════════════════════

        # Side gussets on XZ midplane (sketch Y = -world Z on XZ plane)
        mid_plane = make_offset_plane(comp, comp.xZConstructionPlane, 0)
        for sign in [-1, 1]:
            x_base = sign * (MOUNT_W / 2 - RIB_THICK)
            add_triangular_gusset(
                comp, mid_plane,
                x_base, -N20_D,              # motor pocket top, near wall
                x_base, -MOUNT_H,            # mount face top
                sign * N20_W / 2, -N20_D,    # motor pocket corner
                MOUNT_L * 0.6,
                symmetric=True,
                target_body=body,
            )

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
            'Fixed Wheel Mount created!\n\n'
            f'Body: {MOUNT_W*10:.0f} × {MOUNT_L*10:.0f} × {MOUNT_H*10:.0f}mm '
            f'(rounded corners, {CORNER_R*10:.0f}mm radius)\n\n'
            f'N20 motor pocket: {N20_W*10:.1f} × {N20_H*10:.1f}mm, '
            f'{N20_D*10:.0f}mm deep (rounded corners)\n'
            f'Shaft hole: {SHAFT_HOLE_R*20:.0f}mm horizontal (chamfered)\n'
            f'Arm mount: 2× M3 through-holes '
            f'({BOLT_SPACING*10:.0f}mm, bolts to connector)\n'
            f'Motor retention: zip-tie slot\n'
            f'Reinforcement: 2× diagonal gussets\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'Qty needed: 2 (ML, MR)\n'
            'Print 25×25mm face down, no supports.',
            'Mars Rover - Fixed Wheel Mount'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
