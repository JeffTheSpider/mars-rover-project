"""
Mars Rover Differential Link — Phase 1
========================================

*** DEPRECATED — Through-bar differential mechanism no longer uses links. ***
*** Kept for reference only. See generate_rover_params.py mechanism_type. ***

Rigid link connecting the differential bar end to a rocker arm.
Each end has a ball joint (M3 rod-end bearing / Heim joint) for
multi-axis rotation accommodation.

The diff bar rotates about X, rockers rotate about Y — these axes
are perpendicular, so pin joints would bind. Ball joints allow the
angular misalignment.

NOTE: With the NASA-proportioned through-bar design, the diff bar
passes directly through the rocker hub connectors. No external links
are needed. This script is only relevant if mechanism_type == "bar+links".

Features:
  - Printed flat bar: ~85mm long × 15mm wide × 6mm thick
  - 2× M3 through-holes at each end for rod-end bearing bolts
  - Reinforced ends (wider pads around bolt holes)
  - Lightening cutout in centre (optional, reduces mass)

Assembly:
  - M3 rod-end bearing (Heim joint) threads onto M3 bolt at each end
  - Top bolt → connects to diff bar end bracket
  - Bottom bolt → connects to rocker arm bracket (near rocker pivot)

Link length: ~85mm (Phase 1, 0.4x scale) / ~212mm (full scale)
  Calculated from: bar_half_span, rocker_pivot_x, pivot heights, offsets
  See generate_rover_params.py differential_computed.link_length

Print: Flat, PLA, 80% infill, 5 perimeters (structural link)
Qty: 2 (left + right — identical, not mirrored) — ONLY if using bar+links mode

Reference: EA-26 Section 9.4, generate_rover_params.py
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

        # ── Dimensions (cm for Fusion API) ──
        # Link geometry (Phase 1 values from generate_rover_params.py)
        LINK_LEN  = 8.5        # 85mm link length (centre-to-centre of bolt holes)
        LINK_W    = 1.5        # 15mm link width
        LINK_T    = 0.6        # 6mm link thickness
        PAD_W     = 2.0        # 20mm end pad width (wider for bolt reinforcement)
        PAD_LEN   = 1.2        # 12mm end pad length
        BOLT_R    = 0.165      # M3 clearance hole (3.3mm / 2)
        FILLET_R  = 0.2        # 2mm fillets on transitions

        # The link is oriented along Y axis for this script
        # Bolt hole 1 at Y = +LINK_LEN/2, Bolt hole 2 at Y = -LINK_LEN/2

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures
        fillets = comp.features.filletFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Link body — dog-bone shape (narrow centre, wide ends)
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Link Profile'
        sl = sketch.sketchCurves.sketchLines
        sa = sketch.sketchCurves.sketchArcs

        # Build the outline as a series of points
        # Top end pad (Y = +LINK_LEN/2 region)
        top_y = LINK_LEN / 2
        bot_y = -LINK_LEN / 2
        neck_top = top_y - PAD_LEN  # where pad transitions to narrow neck
        neck_bot = bot_y + PAD_LEN

        # Top pad rectangle
        p1 = p(-PAD_W / 2, top_y, 0)
        p2 = p(PAD_W / 2, top_y, 0)
        p3 = p(PAD_W / 2, neck_top, 0)
        p4 = p(LINK_W / 2, neck_top, 0)
        p5 = p(LINK_W / 2, neck_bot, 0)
        p6 = p(PAD_W / 2, neck_bot, 0)
        p7 = p(PAD_W / 2, bot_y, 0)
        p8 = p(-PAD_W / 2, bot_y, 0)
        p9 = p(-PAD_W / 2, neck_bot, 0)
        p10 = p(-LINK_W / 2, neck_bot, 0)
        p11 = p(-LINK_W / 2, neck_top, 0)
        p12 = p(-PAD_W / 2, neck_top, 0)

        # Draw closed profile
        sl.addByTwoPoints(p1, p2)
        sl.addByTwoPoints(p2, p3)
        sl.addByTwoPoints(p3, p4)
        sl.addByTwoPoints(p4, p5)
        sl.addByTwoPoints(p5, p6)
        sl.addByTwoPoints(p6, p7)
        sl.addByTwoPoints(p7, p8)
        sl.addByTwoPoints(p8, p9)
        sl.addByTwoPoints(p9, p10)
        sl.addByTwoPoints(p10, p11)
        sl.addByTwoPoints(p11, p12)
        sl.addByTwoPoints(p12, p1)

        prof = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                prof = pr

        linkBody = None
        if prof:
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(LINK_T)
            )
            ext = extrudes.add(extInput)
            linkBody = ext.bodies.item(0)
            linkBody.name = 'Differential Link'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Bolt holes (M3 through-holes at each end)
        # ══════════════════════════════════════════════════════════

        boltSketch = comp.sketches.add(comp.xYConstructionPlane)
        boltSketch.name = 'Bolt Holes'

        # Top hole
        boltSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, top_y - PAD_LEN / 2, 0), BOLT_R
        )
        # Bottom hole
        boltSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, bot_y + PAD_LEN / 2, 0), BOLT_R
        )

        target_area = math.pi * BOLT_R * BOLT_R
        for pi_idx in range(boltSketch.profiles.count):
            pr = boltSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if abs(a - target_area) < target_area * 0.3:
                holeInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                holeInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(LINK_T + 0.1)
                )
                try:
                    extrudes.add(holeInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Differential Link created!\n\n'
            f'Link length: {LINK_LEN * 10:.0f}mm (centre-to-centre)\n'
            f'Width: {LINK_W * 10:.0f}mm body / '
            f'{PAD_W * 10:.0f}mm end pads\n'
            f'Thickness: {LINK_T * 10:.0f}mm\n\n'
            'BOLT HOLES:\n'
            f'  2× M3 through-holes ({BOLT_R * 20:.1f}mm dia)\n'
            f'  Located at end pad centres\n\n'
            'ASSEMBLY:\n'
            '  M3 rod-end bearing (Heim joint) at each end\n'
            '  Top → diff bar end bracket\n'
            '  Bottom → rocker arm bracket\n'
            '  Ball joints accommodate X/Y axis misalignment\n\n'
            'Print flat, 80% infill, 5 perimeters (structural).\n'
            'Qty: 2 (identical, one per side)',
            'Mars Rover - Differential Link'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
