"""
Reference Model — L298N Dual H-Bridge Motor Driver Module
===========================================================

NON-PRINTABLE reference body for visual fitment checking.
Dimensions from the common red-PCB Chinese module (generic).

Geometry:
  - PCB: 43 × 43 × 1.6mm
  - Heatsink: 25 × 15 × 20mm (aluminium, centre-rear)
  - 4× M3 mounting holes at ~37mm PCD (3mm from each edge)
  - Screw terminals: 2× 2-pin motor outputs (left/right edges)
                     1× 3-pin power input (rear edge)
  - Pin header: 6-pin control (front edge)
  - Overall height: ~27mm (PCB + heatsink)

Origin: Centre of PCB bottom face
Weight: ~30g

Reference: Components101, eTechnophiles, Smart-Prototyping
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
        # PCB
        PCB_L      = 4.30    # 43mm (Y)
        PCB_W      = 4.30    # 43mm (X)
        PCB_T      = 0.16    # 1.6mm

        # Mounting holes (M3, 4 corners)
        HOLE_INSET = 0.30    # 3mm from edge
        HOLE_R     = 0.15    # 3.0mm dia

        # Heatsink (aluminium block, centre-rear of board)
        HS_W       = 2.50    # 25mm width (X)
        HS_D       = 1.50    # 15mm depth (Y)
        HS_H       = 2.00    # 20mm height above PCB
        HS_Y_OFF   = 0.50    # 5mm offset toward rear (-Y)

        # Screw terminals (simplified as blocks)
        TERM_W     = 1.00    # 10mm per 2-pin block
        TERM_D     = 0.80    # 8mm depth
        TERM_H     = 1.00    # 10mm height above PCB
        # Power terminal (3-pin, rear edge)
        PTERM_W    = 1.52    # 15.2mm (3 × 5.08mm)

        # Control pin header (front edge)
        HDR_W      = 1.52    # 15.2mm (6 × 2.54mm)
        HDR_D      = 0.254   # 2.54mm
        HDR_H      = 0.85    # 8.5mm

        # Capacitors and other components (simplified as a raised area)
        CAP_H      = 0.80    # 8mm general component height

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: PCB
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'L298N PCB'
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-PCB_W / 2, -PCB_L / 2, 0),
            p(PCB_W / 2, PCB_L / 2, 0)
        )

        prof = sketch.profiles.item(0)
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(PCB_T)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'REF_L298N_PCB'

        topPlaneInput = comp.constructionPlanes.createInput()
        topPlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(PCB_T)
        )
        topP = comp.constructionPlanes.add(topPlaneInput)

        # ══════════════════════════════════════════════════════════
        # STEP 2: Heatsink (aluminium block)
        # ══════════════════════════════════════════════════════════

        hsSketch = comp.sketches.add(topP)
        hsSketch.name = 'Heatsink'
        hsSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-HS_W / 2, -HS_Y_OFF - HS_D / 2, 0),
            p(HS_W / 2, -HS_Y_OFF + HS_D / 2, 0)
        )

        hsProf = None
        maxArea = 0
        for pi_idx in range(hsSketch.profiles.count):
            pr = hsSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                hsProf = pr

        if hsProf:
            hsInput = extrudes.createInput(
                hsProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            hsInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(HS_H)
            )
            extrudes.add(hsInput)

        # ══════════════════════════════════════════════════════════
        # STEP 3: Screw terminals (3 blocks)
        # ══════════════════════════════════════════════════════════

        termSketch = comp.sketches.add(topP)
        termSketch.name = 'Screw Terminals'

        # Left motor terminal (left edge, +Y half)
        termSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-PCB_W / 2, 0.5, 0),
            p(-PCB_W / 2 + TERM_D, 0.5 + TERM_W, 0)
        )
        # Right motor terminal (right edge, +Y half)
        termSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(PCB_W / 2 - TERM_D, 0.5, 0),
            p(PCB_W / 2, 0.5 + TERM_W, 0)
        )
        # Power terminal (rear edge, centred)
        termSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-PTERM_W / 2, -PCB_L / 2, 0),
            p(PTERM_W / 2, -PCB_L / 2 + TERM_D, 0)
        )

        for pi_idx in range(termSketch.profiles.count):
            pr = termSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < 2.0 and a > 0.05:
                tInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                tInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(TERM_H)
                )
                try:
                    extrudes.add(tInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 4: Control pin header (front edge)
        # ══════════════════════════════════════════════════════════

        hdrSketch = comp.sketches.add(topP)
        hdrSketch.name = 'Control Header'
        hdrSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-HDR_W / 2, PCB_L / 2 - HDR_D - 0.3, 0),
            p(HDR_W / 2, PCB_L / 2 - 0.3, 0)
        )

        hdrProf = None
        maxArea = 0
        for pi_idx in range(hdrSketch.profiles.count):
            pr = hdrSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                hdrProf = pr

        if hdrProf:
            hdrInput = extrudes.createInput(
                hdrProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            hdrInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(HDR_H)
            )
            try:
                extrudes.add(hdrInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # STEP 5: Mounting holes (4× M3 through PCB)
        # ══════════════════════════════════════════════════════════

        holeTopInput = comp.constructionPlanes.createInput()
        holeTopInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(PCB_T)
        )
        holeTopP = comp.constructionPlanes.add(holeTopInput)

        holeSketch = comp.sketches.add(holeTopP)
        holeSketch.name = 'Mounting Holes'

        for sx in [-1, 1]:
            for sy in [-1, 1]:
                hx = sx * (PCB_W / 2 - HOLE_INSET)
                hy = sy * (PCB_L / 2 - HOLE_INSET)
                holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
                    p(hx, hy, 0), HOLE_R
                )

        for pi_idx in range(holeSketch.profiles.count):
            pr = holeSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < 0.1:
                hInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                hInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(PCB_T + 0.01)
                )
                try:
                    extrudes.add(hInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # Done
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        overall_h = PCB_T + HS_H
        ui.messageBox(
            'L298N Module reference model created!\n\n'
            f'PCB: {PCB_W*10:.0f} × {PCB_L*10:.0f} × {PCB_T*10:.1f}mm\n'
            f'Heatsink: {HS_W*10:.0f} × {HS_D*10:.0f} × {HS_H*10:.0f}mm\n'
            f'Mount holes: 4× M3, {HOLE_INSET*10:.0f}mm from edge\n'
            f'Overall height: {overall_h*10:.1f}mm\n\n'
            'This is a REFERENCE model — not for printing.',
            'REF — L298N Module'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
