"""
Reference Model — 2S 2200mAh LiPo Battery
============================================

NON-PRINTABLE reference body for visual fitment checking.
Based on typical Gens Ace / Turnigy 2S 2200mAh 50C dimensions.

Geometry:
  - Body: 86 × 34 × 19mm (soft pouch with shrink wrap)
  - XT60 connector: 16 × 8 × 7.5mm (on one end)
  - Balance lead: JST-XH 3-pin (2S), small block
  - Wire exit: from short end, ~60mm leads

Origin: Centre of battery body bottom face
Orientation: Wires exit in -Y direction

Weight: ~120g

NOTE: LiPo sizes vary by brand. Measure your actual battery
and update dimensions if different. Common range:
  73-105mm × 32-35mm × 16-20mm

Reference: Gens Ace 2200mAh 2S 50C, Amazon listings
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
        # Battery body
        BAT_L      = 8.60    # 86mm length (Y)
        BAT_W      = 3.40    # 34mm width (X)
        BAT_H      = 1.90    # 19mm height (Z)
        BAT_R      = 0.20    # 2mm edge radius (soft pouch corners)

        # XT60 connector (main discharge)
        XT60_W     = 1.60    # 16mm width
        XT60_D     = 0.80    # 8mm depth
        XT60_H     = 0.75    # 7.5mm height
        XT60_PROT  = 0.50    # 5mm wire stub

        # Balance connector (JST-XH 3-pin)
        BAL_W      = 0.75    # 7.5mm width
        BAL_D      = 0.60    # 6mm depth
        BAL_H      = 0.45    # 4.5mm height

        # Wire stubs (for visual)
        WIRE_R     = 0.15    # 3mm bundle
        WIRE_L     = 1.00    # 10mm stub

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Battery body (rounded-edge box)
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Battery Body'
        sl = sketch.sketchCurves.sketchLines
        sa = sketch.sketchCurves.sketchArcs

        hw = BAT_W / 2
        hl = BAT_L / 2
        r = BAT_R

        # Rounded rectangle
        sl.addByTwoPoints(p(-hw + r, -hl, 0), p(hw - r, -hl, 0))
        sa.addByCenterStartSweep(p(hw - r, -hl + r, 0), p(hw - r, -hl, 0), -math.pi / 2)
        sl.addByTwoPoints(p(hw, -hl + r, 0), p(hw, hl - r, 0))
        sa.addByCenterStartSweep(p(hw - r, hl - r, 0), p(hw, hl - r, 0), -math.pi / 2)
        sl.addByTwoPoints(p(hw - r, hl, 0), p(-hw + r, hl, 0))
        sa.addByCenterStartSweep(p(-hw + r, hl - r, 0), p(-hw + r, hl, 0), -math.pi / 2)
        sl.addByTwoPoints(p(-hw, hl - r, 0), p(-hw, -hl + r, 0))
        sa.addByCenterStartSweep(p(-hw + r, -hl + r, 0), p(-hw, -hl + r, 0), -math.pi / 2)

        batProf = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                batProf = pr

        batBody = None
        if batProf:
            extInput = extrudes.createInput(
                batProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BAT_H)
            )
            ext = extrudes.add(extInput)
            batBody = ext.bodies.item(0)
            batBody.name = 'REF_2S_LiPo'

        # ══════════════════════════════════════════════════════════
        # STEP 2: XT60 connector (wire exit end, -Y)
        # ══════════════════════════════════════════════════════════

        xtSketch = comp.sketches.add(comp.xYConstructionPlane)
        xtSketch.name = 'XT60 Connector'
        xtSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-XT60_W / 2, -BAT_L / 2 - XT60_PROT, 0),
            p(XT60_W / 2, -BAT_L / 2, 0)
        )

        xtProf = None
        maxArea = 0
        for pi_idx in range(xtSketch.profiles.count):
            pr = xtSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                xtProf = pr

        if xtProf:
            # XT60 sits at battery mid-height
            xt_z = (BAT_H - XT60_H) / 2
            xtInput = extrudes.createInput(
                xtProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            xtInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(xt_z + XT60_H)
            )
            try:
                extrudes.add(xtInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: Balance connector (JST-XH, same end, offset)
        # ══════════════════════════════════════════════════════════

        balSketch = comp.sketches.add(comp.xYConstructionPlane)
        balSketch.name = 'Balance Connector'
        balSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(BAT_W / 2 - BAL_W - 0.2, -BAT_L / 2 - 0.30, 0),
            p(BAT_W / 2 - 0.2, -BAT_L / 2, 0)
        )

        balProf = None
        maxArea = 0
        for pi_idx in range(balSketch.profiles.count):
            pr = balSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                balProf = pr

        if balProf:
            balInput = extrudes.createInput(
                balProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            balInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(BAT_H)
            )
            try:
                extrudes.add(balInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # Done
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            '2S LiPo Battery reference model created!\n\n'
            f'Body: {BAT_W*10:.0f} × {BAT_L*10:.0f} × {BAT_H*10:.0f}mm\n'
            f'XT60 connector: {XT60_W*10:.0f} × {XT60_D*10:.0f} × {XT60_H*10:.1f}mm\n'
            f'Balance: JST-XH 3-pin (2S)\n'
            f'Weight: ~120g\n\n'
            'NOTE: LiPo dimensions vary by brand!\n'
            'Your actual battery may be 73-105mm long.\n'
            'Measure and update BAT_L/BAT_W/BAT_H if different.\n\n'
            'This is a REFERENCE model — not for printing.',
            'REF — 2S LiPo Battery'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
