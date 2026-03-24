"""
Mars Rover TPU Tire — Phase 1 (0.4 Scale)
==========================================

Separate TPU 95A tire that press-fits onto the PLA wheel rim.
Inspired by NASA Perseverance's 48 gently curved tread pattern.

Dimensions:
  - Inner bore: 75mm (interference fit on 75mm rim seat — EA-25 corrected from 70mm)
  - Outer diameter: 86mm (matches current total wheel OD with grousers)
  - Width: 32mm (matches rim)
  - Wall thickness: 3mm radial (at thinnest between treads)
  - Tread: 48 gently curved treads, 2mm deep × 2mm wide

Assembly: Press-fit onto PLA rim. Rim lips (1.5mm) prevent axial slip.
No adhesive needed — TPU friction + rim lips hold securely.

Print settings (friend's TPU-capable printer):
  - Material: TPU 95A
  - Nozzle: 210-230°C
  - Bed: 50-60°C
  - Speed: 25mm/s max
  - Cooling fan: 0-10%
  - Retraction: 3mm at 25mm/s (direct drive) or disable (Bowden)
  - Infill: 100% (thin walls, solid for grip)
  - Layer height: 0.2mm
  - Perimeters: 3

Quantity needed: 6 tires

Reference: EA-08, rover_wheel.py (USE_TPU_TIRE=True)
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
            ui.messageBox('No active design. Create or open a design first.')
            return

        # ── Parameters (cm — Fusion API unit) ──
        TIRE_OD_R = 4.3         # 43mm radius (86mm OD)
        TIRE_ID_R = 3.75        # 37.5mm radius (75mm bore — matches 75mm rim seat, EA-25)
        TIRE_W = 3.2            # 32mm width
        WALL_THICK = TIRE_OD_R - TIRE_ID_R  # 8mm radial (3mm between treads)

        # Tread pattern
        TREAD_COUNT = 48        # Perseverance-style (48 treads)
        TREAD_DEPTH = 0.2       # 2mm tread depth (raised above base)
        TREAD_WIDTH = 0.2       # 2mm tread width at tip

        comp = design.rootComponent
        p = adsk.core.Point3D.create

        # ══════════════════════════════════════════════════════════════
        # STEP 1: Create tire body via revolve
        # Annular cross-section on XZ plane, revolve around Y axis
        # ══════════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Tire Cross Section'
        lines = sketch.sketchCurves.sketchLines

        # Annular rectangle: inner bore to outer surface
        pts = [
            (TIRE_ID_R, 0),
            (TIRE_OD_R - TREAD_DEPTH, 0),  # Base surface (treads add on top)
            (TIRE_OD_R - TREAD_DEPTH, TIRE_W),
            (TIRE_ID_R, TIRE_W),
        ]

        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            lines.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        axis = lines.addByTwoPoints(p(0, 0, 0), p(0, TIRE_W, 0))
        axis.isConstruction = True

        profile = sketch.profiles.item(0)
        revolves = comp.features.revolveFeatures
        revInput = revolves.createInput(
            profile, axis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        revInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(2 * math.pi))
        tireRev = revolves.add(revInput)

        tireBody = tireRev.bodies.item(0)
        tireBody.name = 'Tire'

        # ══════════════════════════════════════════════════════════════
        # STEP 2: Add raised tread ribs
        # Each tread is a thin raised rib spanning the full tire width.
        # Create one tread via thin revolve, then circular pattern.
        # The treads are straight radial ribs (simplified from S-curves
        # since Fusion API sketch-based S-curves are complex).
        # The visual effect is similar to Perseverance at 0.4 scale.
        # ══════════════════════════════════════════════════════════════

        treadSketch = comp.sketches.add(comp.xZConstructionPlane)
        treadSketch.name = 'Tread Rib'
        trl = treadSketch.sketchCurves.sketchLines

        # Tread cross-section: rectangle from base surface to full OD
        tread_base_r = TIRE_OD_R - TREAD_DEPTH - 0.01  # slight overlap for join
        tread_tip_r = TIRE_OD_R

        trl.addByTwoPoints(p(tread_base_r, 0, 0), p(tread_tip_r, 0, 0))
        trl.addByTwoPoints(p(tread_tip_r, 0, 0), p(tread_tip_r, TIRE_W, 0))
        trl.addByTwoPoints(p(tread_tip_r, TIRE_W, 0), p(tread_base_r, TIRE_W, 0))
        trl.addByTwoPoints(p(tread_base_r, TIRE_W, 0), p(tread_base_r, 0, 0))

        treadAxis = trl.addByTwoPoints(p(0, 0, 0), p(0, TIRE_W, 0))
        treadAxis.isConstruction = True

        treadProf = treadSketch.profiles.item(0)

        # Revolve a thin angular slice for one tread
        tread_angle = TREAD_WIDTH / TIRE_OD_R  # angular width in radians
        treadRevInput = revolves.createInput(
            treadProf, treadAxis,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        treadRevInput.setAngleExtent(False, adsk.core.ValueInput.createByReal(tread_angle))
        treadRev = revolves.add(treadRevInput)

        # Circular pattern all treads
        if TREAD_COUNT > 1:
            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(treadRev)
            zAxis = comp.zConstructionAxis
            patterns = comp.features.circularPatternFeatures
            patInput = patterns.createInput(inputEntities, zAxis)
            patInput.quantity = adsk.core.ValueInput.createByReal(TREAD_COUNT)
            patInput.totalAngle = adsk.core.ValueInput.createByReal(2 * math.pi)
            patInput.isSymmetric = False
            patterns.add(patInput)

        # ══════════════════════════════════════════════════════════════
        # STEP 3: Zoom and report
        # ══════════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'Mars Rover TPU Tire created!\n\n'
            f'Outer diameter: {TIRE_OD_R * 20:.0f}mm (with treads)\n'
            f'Inner bore: {TIRE_ID_R * 20:.0f}mm (press-fit on rim)\n'
            f'Width: {TIRE_W * 10:.0f}mm\n'
            f'Wall thickness: {(TIRE_OD_R - TIRE_ID_R - TREAD_DEPTH) * 10:.0f}mm (base)\n'
            f'Treads: {TREAD_COUNT}x raised ribs, {TREAD_DEPTH * 10:.0f}mm deep\n\n'
            'Material: TPU 95A (flexible)\n'
            'Print at 210-230°C, 25mm/s, minimal retraction.\n'
            'Assembly: Press-fit onto PLA rim (rover_wheel.py, USE_TPU_TIRE=True).\n'
            'Rim lips prevent axial movement.\n\n'
            'Qty needed: 6 tires',
            'Mars Rover - TPU Tire'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
