"""
Reference Model — N20 Micro Gearmotor (GA12-N20, 100RPM 6V)
=============================================================

NON-PRINTABLE reference body for visual fitment checking.
Accurate to ±0.2mm from Pololu / generic GA12-N20 datasheets.

Geometry:
  - Gearbox housing: 12.0 × 10.0 × 9.0mm (rounded rect, R1 corners)
  - Motor can: 12.0 × 10.0 × 15.0mm (stadium cross-section)
  - D-shaft: 3.0mm dia, 2.5mm D-flat, 10mm protrusion
  - Rear terminals: 2× tabs, 1.5mm wide, 7mm c/c, 1.5mm protrusion
  - Overall: 12 × 10 × 34mm (gearbox + motor + shaft)

Origin: Centre of gearbox output face (shaft protrudes in +Z)
Orientation: Shaft along Z-axis, 12mm face along X, 10mm face along Y

Weight: ~10g

Reference: Pololu 100:1 HP 6V, HandsOnTec GA12-N20, NFP JGA12-N20
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
        # Gearbox (output end)
        GB_W       = 1.20    # 12.0mm width (X)
        GB_H       = 1.00    # 10.0mm height (Y)
        GB_L       = 0.90    # 9.0mm length (Z, into motor)
        GB_R       = 0.10    # 1.0mm corner radius

        # Motor can (rear section)
        MOT_W      = 1.20    # 12.0mm (matches gearbox)
        MOT_H      = 1.00    # 10.0mm (matches gearbox)
        MOT_L      = 1.50    # 15.0mm length

        # D-shaft (output)
        SHAFT_R    = 0.15    # 3.0mm dia / 2
        SHAFT_FLAT = 0.125   # 2.5mm D-flat width / 2
        SHAFT_L    = 1.00    # 10.0mm protrusion

        # Rear terminals
        TERM_W     = 0.15    # 1.5mm tab width
        TERM_T     = 0.03    # 0.3mm tab thickness
        TERM_L     = 0.15    # 1.5mm protrusion
        TERM_SPACE = 0.70    # 7.0mm c/c spacing

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures
        fillets = comp.features.filletFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Gearbox housing (rounded rectangle)
        # Origin at centre of output face, gearbox extends in -Z
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Gearbox Cross-Section'
        sl = sketch.sketchCurves.sketchLines
        sa = sketch.sketchCurves.sketchArcs

        hw = GB_W / 2
        hh = GB_H / 2
        r = GB_R

        # Rounded rectangle (lines + arcs)
        # Bottom-left to bottom-right
        sl.addByTwoPoints(p(-hw + r, -hh, 0), p(hw - r, -hh, 0))
        # Bottom-right corner arc
        sa.addByCenterStartSweep(p(hw - r, -hh + r, 0), p(hw - r, -hh, 0), -math.pi / 2)
        # Right side
        sl.addByTwoPoints(p(hw, -hh + r, 0), p(hw, hh - r, 0))
        # Top-right corner arc
        sa.addByCenterStartSweep(p(hw - r, hh - r, 0), p(hw, hh - r, 0), -math.pi / 2)
        # Top
        sl.addByTwoPoints(p(hw - r, hh, 0), p(-hw + r, hh, 0))
        # Top-left corner arc
        sa.addByCenterStartSweep(p(-hw + r, hh - r, 0), p(-hw + r, hh, 0), -math.pi / 2)
        # Left side
        sl.addByTwoPoints(p(-hw, hh - r, 0), p(-hw, -hh + r, 0))
        # Bottom-left corner arc
        sa.addByCenterStartSweep(p(-hw + r, -hh + r, 0), p(-hw, -hh + r, 0), -math.pi / 2)

        gbProf = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                gbProf = pr

        gbBody = None
        if gbProf:
            extInput = extrudes.createInput(
                gbProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            # Extrude in -Z (flip direction)
            extInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(GB_L)
            )
            ext = extrudes.add(extInput)
            gbBody = ext.bodies.item(0)
            gbBody.name = 'REF_N20_Gearbox'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Motor can (same cross-section, extends further back)
        # ══════════════════════════════════════════════════════════

        # Offset plane at rear of gearbox
        gbRearInput = comp.constructionPlanes.createInput()
        gbRearInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(-GB_L)
        )
        gbRearP = comp.constructionPlanes.add(gbRearInput)

        motSketch = comp.sketches.add(gbRearP)
        motSketch.name = 'Motor Can Cross-Section'
        msl = motSketch.sketchCurves.sketchLines
        msa = motSketch.sketchCurves.sketchArcs

        # Stadium shape (same 12×10mm but with larger corner radius = 5mm = half height)
        mr = MOT_H / 2  # 5.0mm radius for full stadium ends

        # Top flat
        msl.addByTwoPoints(p(-hw + mr, hh, 0), p(hw - mr, hh, 0))
        # Right semicircle
        msa.addByCenterStartSweep(p(hw - mr, 0, 0), p(hw - mr, hh, 0), -math.pi)
        # Bottom flat
        msl.addByTwoPoints(p(hw - mr, -hh, 0), p(-hw + mr, -hh, 0))
        # Left semicircle
        msa.addByCenterStartSweep(p(-hw + mr, 0, 0), p(-hw + mr, -hh, 0), -math.pi)

        motProf = None
        maxArea = 0
        for pi_idx in range(motSketch.profiles.count):
            pr = motSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                motProf = pr

        if motProf:
            motInput = extrudes.createInput(
                motProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            motInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(MOT_L)
            )
            extrudes.add(motInput)

        # ══════════════════════════════════════════════════════════
        # STEP 3: D-shaft (output, +Z from origin)
        # ══════════════════════════════════════════════════════════

        shaftSketch = comp.sketches.add(comp.xYConstructionPlane)
        shaftSketch.name = 'D-Shaft'
        sc = shaftSketch.sketchCurves.sketchCircles
        sc.addByCenterRadius(p(0, 0, 0), SHAFT_R)

        shaftProf = None
        minArea = float('inf')
        for pi_idx in range(shaftSketch.profiles.count):
            pr = shaftSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                shaftProf = pr

        if shaftProf:
            shaftInput = extrudes.createInput(
                shaftProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            shaftInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(SHAFT_L)
            )
            extrudes.add(shaftInput)

        # D-flat cut (remove material from one side of shaft)
        shaftTopInput = comp.constructionPlanes.createInput()
        shaftTopInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(SHAFT_L)
        )
        shaftTopP = comp.constructionPlanes.add(shaftTopInput)

        dflatSketch = comp.sketches.add(shaftTopP)
        dflatSketch.name = 'D-Flat Cut'
        dsl = dflatSketch.sketchCurves.sketchLines
        # Cut a rectangle on one side (the +Y side)
        dsl.addTwoPointRectangle(
            p(-SHAFT_R - 0.01, SHAFT_FLAT, 0),
            p(SHAFT_R + 0.01, SHAFT_R + 0.01, 0)
        )

        dflatProf = None
        minArea = float('inf')
        for pi_idx in range(dflatSketch.profiles.count):
            pr = dflatSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                dflatProf = pr

        if dflatProf:
            dflatInput = extrudes.createInput(
                dflatProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            dflatInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(SHAFT_L + 0.01)
            )
            try:
                extrudes.add(dflatInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Rear solder terminals (2× flat tabs)
        # ══════════════════════════════════════════════════════════

        rearZ = -(GB_L + MOT_L)
        rearPlaneInput = comp.constructionPlanes.createInput()
        rearPlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(rearZ)
        )
        rearP = comp.constructionPlanes.add(rearPlaneInput)

        termSketch = comp.sketches.add(rearP)
        termSketch.name = 'Solder Terminals'
        tsl = termSketch.sketchCurves.sketchLines

        for sign in [-1, 1]:
            cx = sign * TERM_SPACE / 2
            tsl.addTwoPointRectangle(
                p(cx - TERM_W / 2, -TERM_T / 2, 0),
                p(cx + TERM_W / 2, TERM_T / 2, 0)
            )

        for pi_idx in range(termSketch.profiles.count):
            pr = termSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < 0.01:
                tInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                tInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(TERM_L)
                )
                try:
                    extrudes.add(tInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # Done
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        total_l = GB_L + MOT_L + SHAFT_L
        ui.messageBox(
            'N20 Gearmotor reference model created!\n\n'
            f'Gearbox: {GB_W*10:.0f} × {GB_H*10:.0f} × {GB_L*10:.0f}mm\n'
            f'Motor can: {MOT_W*10:.0f} × {MOT_H*10:.0f} × {MOT_L*10:.0f}mm\n'
            f'D-shaft: {SHAFT_R*20:.0f}mm dia × {SHAFT_L*10:.0f}mm\n'
            f'Terminals: 2× {TERM_W*10:.1f}mm tabs, {TERM_SPACE*10:.0f}mm c/c\n'
            f'Overall: {GB_W*10:.0f} × {GB_H*10:.0f} × {total_l*10:.0f}mm\n\n'
            'This is a REFERENCE model — not for printing.\n'
            'Use for visual fitment checking only.',
            'REF — N20 Gearmotor'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
