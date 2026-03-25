"""
Reference Model — TowerPro SG90 Micro Servo
=============================================

NON-PRINTABLE reference body for visual fitment checking.
Accurate to ±0.3mm from TowerPro datasheets and community measurements.

Geometry:
  - Body: 22.2 × 11.8 × 22.7mm (blue plastic case)
  - Mounting tabs: 32.3mm total width, 2.5mm thick
  - Tab position: 15.9mm from bottom
  - Gear cover: 11.8mm dia × 1.5mm raised circular boss
  - Output shaft: 4.8mm spline dia, offset 6mm from edge
  - Shaft protrusion: 4.0mm above gear cover top
  - Wire exit: bottom rear face

Origin: Centre of body bottom face
Orientation: Shaft in +Z, tabs along X, wire exit in -Y

Weight: ~9g

Reference: TowerPro official dims (A-F), HandsOnTec datasheet,
           Hackaday.io SG-90 measurements, Espressif devkit examples
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
        # Main body
        BODY_W     = 2.22    # 22.2mm width (X, along tab axis)
        BODY_D     = 1.18    # 11.8mm depth (Y)
        BODY_H     = 2.27    # 22.7mm total height (Z)

        # Mounting tabs
        TAB_TOTAL  = 3.23    # 32.3mm total width including tabs
        TAB_T      = 0.25    # 2.5mm tab thickness (Z)
        TAB_BOT    = 1.59    # 15.9mm from bottom to tab underside

        # Mounting holes in tabs
        HOLE_SPACE = 2.75    # 27.5mm c/c
        HOLE_R     = 0.10    # 2.0mm dia

        # Gear cover (raised circular boss on top)
        GEAR_R     = BODY_D / 2  # 5.9mm radius (fills depth)
        GEAR_H     = 0.15    # 1.5mm raised above body top

        # Output shaft (spline)
        SHAFT_OFFSET = 0.60  # 6.0mm from one edge of body (X)
        SHAFT_R    = 0.24    # 4.8mm dia / 2
        SHAFT_PROT = 0.40    # 4.0mm above gear cover top
        SHAFT_COLLAR_R = 0.30  # 6.0mm dia collar
        SHAFT_COLLAR_H = 0.20 # 2.0mm collar height

        # Wire exit
        WIRE_R     = 0.15    # ~3mm bundle dia / 2
        WIRE_L     = 0.50    # 5mm stub length for visual

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: Main body block
        # Origin at centre of bottom face, body extends +Z
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Servo Body'
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-BODY_W / 2, -BODY_D / 2, 0),
            p(BODY_W / 2, BODY_D / 2, 0)
        )

        prof = sketch.profiles.item(0)
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(BODY_H)
        )
        ext = extrudes.add(extInput)
        body = ext.bodies.item(0)
        body.name = 'REF_SG90_Servo'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Mounting tabs (extend beyond body width)
        # ══════════════════════════════════════════════════════════

        tabPlaneInput = comp.constructionPlanes.createInput()
        tabPlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(TAB_BOT)
        )
        tabP = comp.constructionPlanes.add(tabPlaneInput)

        tabSketch = comp.sketches.add(tabP)
        tabSketch.name = 'Mounting Tabs'
        tabSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-TAB_TOTAL / 2, -BODY_D / 2, 0),
            p(TAB_TOTAL / 2, BODY_D / 2, 0)
        )

        tabProf = None
        maxArea = 0
        for pi_idx in range(tabSketch.profiles.count):
            pr = tabSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                tabProf = pr

        if tabProf:
            tabInput = extrudes.createInput(
                tabProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            tabInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(TAB_T)
            )
            extrudes.add(tabInput)

        # Tab mounting holes
        tabTopInput = comp.constructionPlanes.createInput()
        tabTopInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(TAB_BOT + TAB_T)
        )
        tabTopP = comp.constructionPlanes.add(tabTopInput)

        holeSketch = comp.sketches.add(tabTopP)
        holeSketch.name = 'Tab Holes'
        for sign in [-1, 1]:
            holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
                p(sign * HOLE_SPACE / 2, 0, 0), HOLE_R
            )

        for pi_idx in range(holeSketch.profiles.count):
            pr = holeSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < 0.05:
                hInput = extrudes.createInput(
                    pr, adsk.fusion.FeatureOperations.CutFeatureOperation
                )
                hInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(TAB_T + 0.01)
                )
                try:
                    extrudes.add(hInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: Gear cover (raised circular boss on top face)
        # Offset toward shaft side of body
        # ══════════════════════════════════════════════════════════

        topPlaneInput = comp.constructionPlanes.createInput()
        topPlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H)
        )
        topP = comp.constructionPlanes.add(topPlaneInput)

        # Shaft X position: offset from -X edge by SHAFT_OFFSET
        shaft_x = -BODY_W / 2 + SHAFT_OFFSET

        gearSketch = comp.sketches.add(topP)
        gearSketch.name = 'Gear Cover'
        gearSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(shaft_x, 0, 0), GEAR_R
        )

        gearProf = None
        minArea = float('inf')
        for pi_idx in range(gearSketch.profiles.count):
            pr = gearSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                gearProf = pr

        if gearProf:
            gearInput = extrudes.createInput(
                gearProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            gearInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(GEAR_H)
            )
            extrudes.add(gearInput)

        # ══════════════════════════════════════════════════════════
        # STEP 4: Output shaft (collar + spline cylinder)
        # ══════════════════════════════════════════════════════════

        gearTopInput = comp.constructionPlanes.createInput()
        gearTopInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H + GEAR_H)
        )
        gearTopP = comp.constructionPlanes.add(gearTopInput)

        # Collar
        collarSketch = comp.sketches.add(gearTopP)
        collarSketch.name = 'Shaft Collar'
        collarSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(shaft_x, 0, 0), SHAFT_COLLAR_R
        )

        collarProf = None
        minArea = float('inf')
        for pi_idx in range(collarSketch.profiles.count):
            pr = collarSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                collarProf = pr

        if collarProf:
            collarInput = extrudes.createInput(
                collarProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            collarInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(SHAFT_COLLAR_H)
            )
            extrudes.add(collarInput)

        # Spline (simplified as cylinder)
        splinePlaneInput = comp.constructionPlanes.createInput()
        splinePlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BODY_H + GEAR_H + SHAFT_COLLAR_H)
        )
        splineP = comp.constructionPlanes.add(splinePlaneInput)

        splineSketch = comp.sketches.add(splineP)
        splineSketch.name = 'Spline Shaft'
        splineSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(shaft_x, 0, 0), SHAFT_R
        )

        splineProf = None
        minArea = float('inf')
        for pi_idx in range(splineSketch.profiles.count):
            pr = splineSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                splineProf = pr

        if splineProf:
            splineInput = extrudes.createInput(
                splineProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            splineInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(
                    SHAFT_PROT - SHAFT_COLLAR_H)
            )
            extrudes.add(splineInput)

        # ══════════════════════════════════════════════════════════
        # STEP 5: Wire exit stub (bottom rear, -Y side)
        # ══════════════════════════════════════════════════════════

        wireSketch = comp.sketches.add(comp.xYConstructionPlane)
        wireSketch.name = 'Wire Exit'
        wireSketch.sketchCurves.sketchCircles.addByCenterRadius(
            p(0, -BODY_D / 2, 0), WIRE_R
        )

        wireProf = None
        minArea = float('inf')
        for pi_idx in range(wireSketch.profiles.count):
            pr = wireSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a < minArea:
                minArea = a
                wireProf = pr

        if wireProf:
            wireInput = extrudes.createInput(
                wireProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            wireInput.setDistanceExtent(
                True, adsk.core.ValueInput.createByReal(WIRE_L)
            )
            try:
                extrudes.add(wireInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # Done
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        overall_h = BODY_H + GEAR_H + SHAFT_PROT
        ui.messageBox(
            'SG90 Servo reference model created!\n\n'
            f'Body: {BODY_W*10:.1f} × {BODY_D*10:.1f} × {BODY_H*10:.1f}mm\n'
            f'Tabs: {TAB_TOTAL*10:.1f}mm wide × {TAB_T*10:.1f}mm thick\n'
            f'  Tab holes: {HOLE_SPACE*10:.1f}mm c/c, {HOLE_R*20:.1f}mm dia\n'
            f'  Bottom to tab: {TAB_BOT*10:.1f}mm\n'
            f'Gear cover: {GEAR_R*20:.1f}mm dia × {GEAR_H*10:.1f}mm\n'
            f'Shaft: {SHAFT_R*20:.1f}mm spline, offset {SHAFT_OFFSET*10:.0f}mm\n'
            f'Overall height: {overall_h*10:.1f}mm\n\n'
            'This is a REFERENCE model — not for printing.\n'
            'Use for visual fitment checking only.',
            'REF — SG90 Servo'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
