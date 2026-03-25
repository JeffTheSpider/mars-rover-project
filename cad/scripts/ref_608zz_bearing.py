"""
Reference Model — 608ZZ Deep Groove Ball Bearing
==================================================

NON-PRINTABLE reference body for visual fitment checking.
Exact dimensions per ISO 15:2017 / JIS B 1521.

Geometry:
  - Outer diameter: 22.000mm
  - Inner diameter: 8.000mm
  - Width: 7.000mm
  - Chamfer: 0.3mm (inner + outer edges)
  - Metal shields (ZZ): flush with faces
  - Shield inner clearance dia: ~12.2mm

Origin: Centre of bearing, axis along Z
Weight: ~12g

Reference: ISO 608, MinebeaMitsumi 608ZZ, ISK Bearings
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
        OD         = 2.200    # 22.000mm outer diameter
        ID         = 0.800    # 8.000mm inner diameter
        W          = 0.700    # 7.000mm width
        CHAMFER    = 0.030    # 0.3mm edge chamfer

        # Shield detail
        SHIELD_ID  = 1.220    # 12.2mm shield inner clearance
        SHIELD_T   = 0.030    # 0.3mm shield thickness
        SHIELD_RECESS = 0.050 # 0.5mm recess depth in outer ring

        OD_R = OD / 2
        ID_R = ID / 2
        SHIELD_ID_R = SHIELD_ID / 2

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        revolves = comp.features.revolveFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Outer ring (revolve annular cross-section)
        # Bearing centred at origin, axis along Z, width symmetric
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xZConstructionPlane)
        sketch.name = 'Bearing Cross-Section'
        sl = sketch.sketchCurves.sketchLines

        hw = W / 2

        # Outer ring profile (with shield recesses and chamfers)
        # Start at inner bore, bottom face, go clockwise
        # Inner bore bottom (with chamfer)
        pts = [
            (ID_R,          -hw + CHAMFER),   # 0: bore bottom (chamfered)
            (ID_R - CHAMFER, -hw),             # 1: bore bottom chamfer
            (ID_R - CHAMFER,  hw),             # 2: bore top chamfer
            (ID_R,           hw - CHAMFER),    # 3: bore top (chamfered)
            (ID_R,           hw),              # 4: inner ring top face

            # Inner ring top → shield gap
            (SHIELD_ID_R,    hw),              # 5: shield inner edge top

            # Shield recess in outer ring (top side)
            (SHIELD_ID_R,    hw - SHIELD_RECESS), # 6
            (OD_R - SHIELD_RECESS, hw - SHIELD_RECESS), # 7
            (OD_R - SHIELD_RECESS, hw),        # 8

            # Outer ring top face (with chamfer)
            (OD_R - CHAMFER, hw),              # 9: outer top chamfer
            (OD_R,           hw - CHAMFER),    # 10: outer top (chamfered)

            # Outer ring OD
            (OD_R,          -hw + CHAMFER),    # 11: outer bottom (chamfered)
            (OD_R - CHAMFER, -hw),             # 12: outer bottom chamfer

            # Shield recess (bottom side)
            (OD_R - SHIELD_RECESS, -hw),       # 13
            (OD_R - SHIELD_RECESS, -hw + SHIELD_RECESS), # 14
            (SHIELD_ID_R,   -hw + SHIELD_RECESS), # 15

            # Back to inner ring
            (SHIELD_ID_R,   -hw),              # 16: shield inner edge bottom
            (ID_R,          -hw),              # 17: inner ring bottom face
        ]

        # Draw closed profile
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            sl.addByTwoPoints(p(x1, y1, 0), p(x2, y2, 0))

        # Revolution axis (Y axis on the XZ sketch = Z world axis)
        axis = sl.addByTwoPoints(p(0, -hw - 0.1, 0), p(0, hw + 0.1, 0))
        axis.isConstruction = True

        # Find largest profile
        brgProf = None
        maxArea = 0
        for pi_idx in range(sketch.profiles.count):
            pr = sketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                brgProf = pr

        brgBody = None
        if brgProf:
            revInput = revolves.createInput(
                brgProf, axis,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            revInput.setAngleExtent(
                False, adsk.core.ValueInput.createByReal(2 * math.pi)
            )
            rev = revolves.add(revInput)
            brgBody = rev.bodies.item(0)
            brgBody.name = 'REF_608ZZ_Bearing'

        # ══════════════════════════════════════════════════════════
        # Done
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            '608ZZ Bearing reference model created!\n\n'
            f'Outer diameter: {OD*10:.1f}mm\n'
            f'Inner diameter: {ID*10:.1f}mm\n'
            f'Width: {W*10:.1f}mm\n'
            f'Chamfer: {CHAMFER*10:.1f}mm\n'
            f'Shield inner clearance: {SHIELD_ID*10:.1f}mm\n\n'
            'This is a REFERENCE model — not for printing.\n'
            'Use for visual fitment checking only.',
            'REF — 608ZZ Bearing'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
