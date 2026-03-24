"""
Mars Rover Fuse Holder Bracket — Phase 1 (0.4 Scale)
======================================================

Mounting bracket for an inline ATC/ATO blade fuse holder.
Clips onto the electronics tray or body wall.

Dimensions: 40 × 15 × 12mm
  - Clip channel: 8mm wide × 6mm deep (holds standard inline fuse holder body)
  - 4× M3 bolt holes for tray/wall mounting (2 per side of channel)
  - End walls retain fuse holder from sliding out

Qty: 1

Print orientation: Flat (bottom down)
Supports: None
Perimeters: 3
Infill: 40%

Reference: EA-15 (safety), EA-19 (wiring)
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
        BRKT_L = 4.0        # 40mm length (Y)
        BRKT_W = 1.5        # 15mm width (X)
        BRKT_H = 1.2        # 12mm height (Z)
        BASE_H = 0.3        # 3mm base thickness
        CLIP_W = 0.8        # 8mm fuse holder channel width
        CLIP_D = 0.6        # 6mm channel depth (from top)
        WALL_T = 0.2        # 2mm side wall thickness
        END_WALL = 0.3      # 3mm end wall thickness
        HOLE_R = 0.165      # M3 clearance
        HOLE_Y1 = -1.2      # Hole 1 Y position
        HOLE_Y2 = 1.2       # Hole 2 Y position

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════════
        # Step 1: Solid block
        # ══════════════════════════════════════════════════════════════

        sketch1 = comp.sketches.add(comp.xYConstructionPlane)
        sketch1.name = 'Fuse Bracket Base'
        sketch1.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-BRKT_W / 2, -BRKT_L / 2, 0),
            p(BRKT_W / 2, BRKT_L / 2, 0)
        )

        prof = sketch1.profiles.item(0)
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(BRKT_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'Fuse Holder Bracket'

        # ══════════════════════════════════════════════════════════════
        # Step 2: Clip channel (cut from top, leaving base + end walls)
        # ══════════════════════════════════════════════════════════════

        topPlane = comp.constructionPlanes
        tpInput = topPlane.createInput()
        tpInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BRKT_H)
        )
        topP = topPlane.add(tpInput)

        chSketch = comp.sketches.add(topP)
        chSketch.name = 'Fuse Channel'
        chSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-CLIP_W / 2, -BRKT_L / 2 + END_WALL, 0),
            p(CLIP_W / 2, BRKT_L / 2 - END_WALL, 0)
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
                True, adsk.core.ValueInput.createByReal(CLIP_D)
            )
            extrudes.add(chInput)

        # ══════════════════════════════════════════════════════════════
        # Step 3: M3 mounting holes through base
        # ══════════════════════════════════════════════════════════════

        holeSketch = comp.sketches.add(topP)
        holeSketch.name = 'Mount Holes'
        # Holes in the side walls on BOTH sides of the channel
        hole_x_pos = (CLIP_W / 2 + BRKT_W / 2) / 2   # right side midpoint
        hole_x_neg = -hole_x_pos                       # left side midpoint
        for hx in [hole_x_pos, hole_x_neg]:
            holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(hx, HOLE_Y1, 0), HOLE_R
            )
            holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(hx, HOLE_Y2, 0), HOLE_R
            )

        for pi in range(holeSketch.profiles.count):
            pr = holeSketch.profiles.item(pi)
            a = pr.areaProperties().area
            if a < 0.2:
                hInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                hInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(BRKT_H + 0.1)
                )
                try:
                    extrudes.add(hInput)
                except:
                    pass

        # ── Report ──
        app.activeViewport.fit()
        ui.messageBox(
            'Fuse Holder Bracket created!\n\n'
            f'Size: {BRKT_L * 10:.0f} × {BRKT_W * 10:.0f} × '
            f'{BRKT_H * 10:.0f}mm\n'
            f'Channel: {CLIP_W * 10:.0f}mm wide × '
            f'{CLIP_D * 10:.0f}mm deep\n'
            f'End walls: {END_WALL * 10:.0f}mm thick\n'
            f'Mounting: 4× M3 holes (both sides of channel)\n\n'
            'Qty needed: 1\n'
            'Print flat, 40% infill.',
            'Mars Rover - Fuse Holder Bracket'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
