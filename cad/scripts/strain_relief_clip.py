"""
Mars Rover Strain Relief Clip — Phase 1 (0.4 Scale)
=====================================================

U-channel clip with snap tab for anchoring wire bundles at pivot
entry/exit points on the body walls and suspension arms.

Dimensions: 18 × 10 × 10mm (increased for bolt-hole edge clearance)
  - U-channel: 6mm wide × 5mm deep (holds ~4 wires of 22AWG)
  - Base tab: 18 × 10mm with 2× M3 bolt holes (1.85mm edge wall)
  - Snap tab: 1.5mm thick PLA finger retains wires (increased for durability)
  - Channel walls: 2mm thick (increased for PLA strength)

Qty: 8-12 (2 per rocker pivot, 2 per bogie pivot, extras for body exits)

Print orientation: Upright (U-channel opening at top)
Supports: None
Perimeters: 3
Infill: 50% (small part, needs strength)

Reference: EA-19 (wiring), EA-17 (build guide)
"""

import adsk.core
import adsk.fusion
import traceback


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
        CLIP_L = 1.8        # 18mm length (X) — increased for bolt edge clearance
        CLIP_W = 1.0        # 10mm width (Y) — increased
        CLIP_H = 1.0        # 10mm height (Z)
        BASE_H = 0.3        # 3mm base thickness
        WALL_T = 0.2        # 2mm channel wall thickness (increased from 1.5mm)
        CHANNEL_W = 0.6     # 6mm channel width
        CHANNEL_D = 0.5     # 5mm channel depth
        SNAP_T = 0.15       # 1.5mm snap tab thickness (increased from 1mm)
        SNAP_OVERHANG = 0.15  # 1.5mm inward overhang
        HOLE_R = 0.165      # M3 clearance (3.3mm dia)
        HOLE_SPACING = 1.0  # 10mm between holes (edge wall: 9-1.65-0 = 2.35mm)

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════════
        # Step 1: Base block
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Clip Base'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-CLIP_L / 2, -CLIP_W / 2, 0),
            p(CLIP_L / 2, CLIP_W / 2, 0)
        )

        prof = sketch1.profiles.item(0)
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(CLIP_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'Strain Relief Clip'

        # ══════════════════════════════════════════════════════════════
        # Step 2: U-channel cut (from top)
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(CLIP_H)
        )
        topP = topPlane.add(tpInput)

        chSketch = comp.sketches.add(topP)
        chSketch.name = 'U-Channel'
        chSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-CLIP_L / 2 + WALL_T, -CHANNEL_W / 2, 0),
            p(CLIP_L / 2 - WALL_T, CHANNEL_W / 2, 0)
        )

        chProf = None
        minArea = float('inf')
        for pi in range(chSketch.profiles.count):
            pr = chSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                chProf = pr

        if chProf:
            chInput = extrudes.createInput(
                chProf, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            chInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(CHANNEL_D)
            )
            extrudes.add(chInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: Snap tabs (thin inward ledges at top of channel walls)
        # ══════════════════════════════════════════════════════════════

        snapSketch = comp.sketches.add(topP)
        snapSketch.name = 'Snap Tabs'
        sl = snapSketch.sketchCurves.sketchLines

        # Left snap tab
        sl.addTwoPointRectangle(
            p(-CLIP_L / 2 + WALL_T, -CHANNEL_W / 2, 0),
            p(-CLIP_L / 2 + WALL_T + SNAP_OVERHANG,
              CHANNEL_W / 2, 0)
        )
        # Right snap tab
        sl.addTwoPointRectangle(
            p(CLIP_L / 2 - WALL_T - SNAP_OVERHANG, -CHANNEL_W / 2, 0),
            p(CLIP_L / 2 - WALL_T, CHANNEL_W / 2, 0)
        )

        for pi in range(snapSketch.profiles.count):
            pr = snapSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.5:
                sInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                sInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(SNAP_T)
                )
                try:
                    extrudes.add(sInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════════
        # Step 4: M3 mounting holes through base
        # ══════════════════════════════════════════════════════════════

        holeSketch = comp.sketches.add(topP)
        holeSketch.name = 'Mount Holes'
        holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(-HOLE_SPACING / 2, 0, 0), HOLE_R
        )
        holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(HOLE_SPACING / 2, 0, 0), HOLE_R
        )

        for pi in range(holeSketch.profiles.count):
            pr = holeSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.2:
                hInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                hInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(CLIP_H + 0.1)
                )
                try:
                    extrudes.add(hInput)
                except:
                    pass

        # ── Report ──
        app.activeViewport.fit()
        ui.messageBox(
            'Strain Relief Clip created!\n\n'
            f'Size: {CLIP_L * 10:.0f} × {CLIP_W * 10:.0f} × '
            f'{CLIP_H * 10:.0f}mm\n'
            f'Channel: {CHANNEL_W * 10:.0f}mm wide × '
            f'{CHANNEL_D * 10:.0f}mm deep\n'
            f'Snap tabs: {SNAP_T * 10:.0f}mm thick, '
            f'{SNAP_OVERHANG * 10:.0f}mm overhang\n'
            f'Mounting: 2× M3 holes, {HOLE_SPACING * 10:.0f}mm spacing\n\n'
            'Qty needed: 8-12\n'
            'Print upright, 50% infill.',
            'Mars Rover - Strain Relief Clip'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
