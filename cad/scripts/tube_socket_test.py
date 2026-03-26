"""
Tube Socket Test Piece — 8mm Rod Fit Validation
================================================

Creates a print-ready test piece to validate 8mm steel rod fit in the
tube socket bore used by all suspension connectors.

Redesigned with:
  - Rounded-rect base with 2mm corner radii
  - Cylindrical bosses with entry chamfers on each socket
  - 0.5mm fillets on all external edges
  - Three test bores: 8.1mm, 8.2mm, 8.3mm
  - M3 grub screw hole in centre socket
  - Raised boss rings for socket identification

Target: 8.2mm bore (0.2mm clearance on 8mm rod)
Socket depth: 15mm (same as all connectors)
Wall: 4mm around socket

Overall size: ~55 × 22 × 22mm (~15min print)
Print: Flat, PLA, 60% infill, 5 perimeters (matches connector settings)

Reference: EA-25 (suspension audit), all connector scripts
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys

sys.path.insert(0, r"D:\Mars Rover Project\cad\scripts")
from rover_cad_helpers import (
    p, val, TUBE_BORE, TUBE_DEPTH, TUBE_WALL, GRUB_M3,
    FILLET_STD, CHAMFER_STD, CORNER_R,
    draw_rounded_rect,
    find_smallest_profile, find_largest_profile, find_profile_by_area,
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

        # ── Parameters (cm) ──
        BORE_RADII = [0.405, 0.41, 0.415]   # 8.1mm, 8.2mm, 8.3mm
        BORE_LABELS = ['8.1', '8.2', '8.3']
        SOCKET_DEPTH = 1.5                    # 15mm
        WALL = 0.4                            # 4mm wall
        GRUB_R = GRUB_M3                      # 1.5mm (M3)

        # Socket boss geometry
        BOSS_R = max(BORE_RADII) + WALL       # ~8.15mm radius (16.3mm OD)
        BOSS_H = SOCKET_DEPTH                 # 15mm boss height above base

        # Base plate
        SPACING = BOSS_R * 2 + 0.3            # ~16.9mm centre-to-centre
        BASE_W = SPACING * 2 + BOSS_R * 2 + 0.4  # total width
        BASE_D = BOSS_R * 2 + 0.4            # depth
        BASE_H = 0.4                          # 4mm base plate (thicker for stability)

        # Entry chamfer on socket bores
        ENTRY_CHAM = 0.05                     # 0.5mm 45° chamfer

        comp = design.rootComponent
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Rounded-rect base plate
        # ══════════════════════════════════════════════════════════

        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Base Plate'
        draw_rounded_rect(sk, 0, 0, BASE_W, BASE_D, r=CORNER_R)

        target_area = BASE_W * BASE_D - (4 - math.pi) * CORNER_R**2
        prof = find_profile_by_area(sk, target_area, tolerance=0.5)
        if prof is None:
            prof = find_largest_profile(sk)

        base_ext = extrude_profile(comp, prof, BASE_H)
        body = base_ext.bodies.item(0) if base_ext else None
        if body:
            body.name = 'Tube Socket Test'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Three socket boss cylinders on base
        # Each boss has a slight taper at the base (gusset fillet)
        # ══════════════════════════════════════════════════════════

        base_top = make_offset_plane(comp, comp.xYConstructionPlane, BASE_H)

        for i in range(3):
            cx = (i - 1) * SPACING  # -SPACING, 0, +SPACING

            boss_sk = comp.sketches.add(base_top)
            boss_sk.name = f'Socket Boss {BORE_LABELS[i]}mm'
            boss_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(cx, 0), BOSS_R
            )

            boss_area = math.pi * BOSS_R**2
            boss_prof = find_profile_by_area(boss_sk, boss_area, tolerance=0.4)
            if boss_prof is None:
                boss_prof = find_smallest_profile(boss_sk)

            join_profile(comp, boss_prof, BOSS_H)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Bore holes (3 different diameters, from top)
        # ══════════════════════════════════════════════════════════

        top_plane = make_offset_plane(
            comp, comp.xYConstructionPlane, BASE_H + BOSS_H
        )

        for i, bore_r in enumerate(BORE_RADII):
            cx = (i - 1) * SPACING

            bore_sk = comp.sketches.add(top_plane)
            bore_sk.name = f'Bore {BORE_LABELS[i]}mm'
            bore_sk.sketchCurves.sketchCircles.addByCenterRadius(
                p(cx, 0), bore_r
            )

            bore_prof = find_smallest_profile(bore_sk)
            cut_profile(comp, bore_prof, SOCKET_DEPTH, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Entry chamfers on each bore (guides rod insertion)
        # ══════════════════════════════════════════════════════════

        if body:
            for bore_r in BORE_RADII:
                edges = adsk.core.ObjectCollection.create()
                for ei in range(body.edges.count):
                    edge = body.edges.item(ei)
                    geom = edge.geometry
                    if isinstance(geom, adsk.core.Circle3D):
                        if abs(geom.radius - bore_r) < 0.01:
                            # Only chamfer the top edge (highest Z)
                            bb = edge.boundingBox
                            if bb.maxPoint.z > (BASE_H + BOSS_H - 0.05):
                                edges.add(edge)

                if edges.count > 0:
                    chamfers = comp.features.chamferFeatures
                    try:
                        cham_in = chamfers.createInput2()
                        cham_in.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                            edges, val(ENTRY_CHAM), True
                        )
                        chamfers.add(cham_in)
                    except Exception as e:
                        print(f'  Warning: chamfer {bore_r*20:.1f}mm bore: {e}')

        # ══════════════════════════════════════════════════════════
        # STEP 5: M3 grub screw hole in centre socket (nominal 8.2mm)
        # FIX C19: Grub hole must cut radially (from outside toward bore
        # centre), not vertically. Sketch on YZ offset plane at socket
        # height, extrude in +X to cut through the wall.
        # ══════════════════════════════════════════════════════════

        grub_z = BASE_H + SOCKET_DEPTH / 2  # mid-socket height (Z)

        # Offset the XZ plane along Y to the boss centre (Y=0 for centre boss)
        # Sketch circle on that plane at (boss_outer_edge, grub_z)
        grub_plane = make_offset_plane(comp, comp.xZConstructionPlane, 0)

        grub_sk = comp.sketches.add(grub_plane)
        grub_sk.name = 'Grub Screw Test'
        # On XZ plane: X = radial position, Y = height (Z in model space)
        # Position the hole at the outer edge of the boss wall
        grub_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p(BOSS_R, -grub_z), GRUB_R
        )

        grub_prof = find_smallest_profile(grub_sk)
        # Cut radially inward through the wall only (not through opposite wall)
        cut_profile(comp, grub_prof, WALL + 0.01, flip=True)

        # ══════════════════════════════════════════════════════════
        # STEP 6: Identification rings on boss tops
        # One ring = 8.1mm, two rings = 8.2mm, three rings = 8.3mm
        # ══════════════════════════════════════════════════════════

        for i in range(3):
            cx = (i - 1) * SPACING
            ring_count = i + 1
            for ri in range(ring_count):
                ring_r = BOSS_R - 0.05 - ri * 0.1  # concentric grooves
                if ring_r > BORE_RADII[i] + 0.1:
                    ring_sk = comp.sketches.add(top_plane)
                    ring_sk.name = f'ID Ring {BORE_LABELS[i]}mm #{ri+1}'
                    ring_sk.sketchCurves.sketchCircles.addByCenterRadius(
                        p(cx, 0), ring_r
                    )
                    ring_sk.sketchCurves.sketchCircles.addByCenterRadius(
                        p(cx, 0), ring_r - 0.04  # 0.4mm wide groove
                    )
                    ring_area = math.pi * (ring_r**2 - (ring_r - 0.04)**2)
                    ring_prof = find_profile_by_area(ring_sk, ring_area, tolerance=0.8)
                    if ring_prof:
                        cut_profile(comp, ring_prof, 0.03, flip=True)  # 0.3mm deep

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
            'Tube Socket Test Piece created!\n\n'
            f'Base: {BASE_W*10:.0f} × {BASE_D*10:.0f} × {BASE_H*10:.0f}mm '
            f'(rounded corners)\n'
            f'Socket bosses: {BOSS_R*20:.1f}mm OD × '
            f'{(BASE_H + BOSS_H)*10:.0f}mm tall\n'
            f'Fillets: {fillet_count} edges @ {FILLET_STD*10:.1f}mm\n\n'
            'THREE test sockets with ID rings:\n'
            f'  LEFT (1 ring):   {BORE_LABELS[0]}mm bore (tight)\n'
            f'  CENTRE (2 rings): {BORE_LABELS[1]}mm bore (nominal) + M3 grub\n'
            f'  RIGHT (3 rings):  {BORE_LABELS[2]}mm bore (loose)\n\n'
            f'Socket depth: {SOCKET_DEPTH*10:.0f}mm | Wall: {WALL*10:.0f}mm\n'
            f'Entry chamfer: {ENTRY_CHAM*10:.1f}mm on each bore\n\n'
            'TEST PROCEDURE:\n'
            '1. Print flat, PLA, 60% infill, 5 perimeters\n'
            '2. Insert 8mm steel rod into each socket\n'
            '3. LEFT (8.1mm): Should be tight push-fit\n'
            '4. CENTRE (8.2mm): Should be snug slide-fit (target)\n'
            '5. RIGHT (8.3mm): Should be loose (too much play)\n'
            '6. Test M3 grub screw in centre hole\n'
            '7. Pick best bore diameter for all connectors',
            'Mars Rover - Tube Socket Test'
        )

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
