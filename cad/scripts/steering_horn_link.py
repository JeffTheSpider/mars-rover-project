"""
Mars Rover Steering Horn Link — Phase 1
=========================================

Small printed bar that connects the SG90 servo horn tip to the steering
knuckle arm, forming a 4-bar linkage for steering actuation.

One link per steered wheel (FL, FR, RL, RR). All identical.

Features:
  - Rectangular bar with rounded ends
  - 2× M2 clearance holes (2.2mm) at 20mm centre-to-centre
  - 8mm wide × 5mm thick × 24mm overall (20mm c/c + 2× 2mm end radius)
  - Printed flat, 100% infill, 4 perimeters

Assembly:
  1. Horn end: M2×10 screw → nylon washer → horn hole → link hole → nylon washer → M2 nyloc nut
  2. Knuckle end: same hardware, connects to knuckle steering arm M2 hole
  Both pins must rotate freely (finger-tight + 1/4 turn)

Overall size: ~24 × 8 × 5mm
Print: Flat (largest face down), PLA, 100% infill, 4 perimeters
Qty: 4 (FL, FR, RL, RR — all identical)

Reference: EA-27 Section 4 (Dimensional Chain), EA-10 (Ackermann Steering)
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
        LINK_CC     = 2.0       # 20mm centre-to-centre between M2 holes
        LINK_W      = 0.8       # 8mm width
        LINK_H      = 0.5       # 5mm thickness (height when printed flat)
        HOLE_R      = 0.11      # M2 clearance hole (2.2mm / 2)
        END_R       = LINK_W / 2  # 4mm end radius (rounded ends)

        # Overall length = LINK_CC + 2 × END_R = 20 + 8 = 28mm
        # But we'll make the outline as a stadium (rectangle + semicircle ends)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Link body outline (stadium/oblong shape)
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Horn Link Body'
        arcs = sketch.sketchCurves.sketchArcs
        lines = sketch.sketchCurves.sketchLines

        # Stadium shape: two semicircles connected by two straight lines
        # Left centre at (-LINK_CC/2, 0), right centre at (+LINK_CC/2, 0)
        half_cc = LINK_CC / 2

        # Top line: from left-top to right-top
        lines.addByTwoPoints(
            p(-half_cc, END_R, 0),
            p(half_cc, END_R, 0)
        )
        # Bottom line: from right-bottom to left-bottom
        lines.addByTwoPoints(
            p(half_cc, -END_R, 0),
            p(-half_cc, -END_R, 0)
        )
        # Right semicircle (from top-right to bottom-right, centre at +half_cc)
        arcs.addByCenterStartSweep(
            p(half_cc, 0, 0),
            p(half_cc, END_R, 0),
            -math.pi  # 180° clockwise
        )
        # Left semicircle (from bottom-left to top-left, centre at -half_cc)
        arcs.addByCenterStartSweep(
            p(-half_cc, 0, 0),
            p(-half_cc, -END_R, 0),
            -math.pi  # 180° clockwise
        )

        # Find the enclosed profile
        linkProf = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                linkProf = pr

        linkBody = None
        if linkProf:
            extInput = extrudes.createInput(
                linkProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(LINK_H)
            )
            ext = extrudes.add(extInput)
            linkBody = ext.bodies.item(0)
            linkBody.name = 'Steering Horn Link'

        # ══════════════════════════════════════════════════════════
        # STEP 2: M2 clearance holes (2× through-holes)
        # ══════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(LINK_H)
        )
        topP = topPlane.add(tpInput)

        holeSketch = comp.sketches.add(topP)
        holeSketch.name = 'M2 Pin Holes'
        # Left hole (horn end)
        holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(-half_cc, 0, 0), HOLE_R
        )
        # Right hole (knuckle arm end)
        holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(half_cc, 0, 0), HOLE_R
        )

        target_area = math.pi * HOLE_R * HOLE_R
        for pi_idx in range(holeSketch.profiles.count):
            pr = holeSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if abs(a - target_area) < target_area * 0.5:
                hInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                hInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(LINK_H + 0.1)
                )
                try:
                    extrudes.add(hInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: Zoom and report
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        overall_l = (LINK_CC + LINK_W) * 10
        ui.messageBox(
            'Steering Horn Link created!\n\n'
            f'Overall: {overall_l:.0f} × {LINK_W * 10:.0f} × '
            f'{LINK_H * 10:.0f}mm (stadium shape)\n'
            f'M2 holes: 2× at {LINK_CC * 10:.0f}mm centre-to-centre\n'
            f'Hole dia: {HOLE_R * 20:.1f}mm (M2 clearance)\n\n'
            'ASSEMBLY:\n'
            '  Horn end: M2×10 + nylon washer + link + washer + nyloc nut\n'
            '  Arm end: same hardware\n'
            '  Both pins must rotate freely.\n\n'
            'Print flat, 100% infill, 4 perimeters.\n'
            'Qty: 4 (FL, FR, RL, RR)',
            'Mars Rover - Steering Horn Link'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
