"""
Reference Model — ESP32-S3-DevKitC-1 v1.1 (N16R8)
====================================================

NON-PRINTABLE reference body for visual fitment checking.
Dimensions from official Espressif DXF mechanical drawing.

Geometry:
  - PCB: 62.7 × 25.4 × 1.6mm (green board)
  - Pin headers: 2 × 22 pins, 2.54mm pitch, 22.86mm row spacing
  - Pin headers protrude 2.5mm below PCB, 8.5mm above
  - ESP32-S3-WROOM-1 module: 25.5 × 18.0 × 3.2mm (metal shield)
  - USB-C connector: 8.9 × 7.3 × 3.2mm (on bottom edge)
  - Reset + Boot buttons: 2× 3.5 × 3.0 × 1.5mm

Origin: Centre of PCB bottom face
Orientation: USB connector in -Y direction, pin headers along Y

Weight: ~10g

Reference: Espressif DXF_ESP32-S3-DevKitC-1_V1.1_20220429,
           ESP32-S3-WROOM-1 datasheet
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
        PCB_L      = 6.27    # 62.7mm length (Y)
        PCB_W      = 2.54    # 25.4mm width (X)
        PCB_T      = 0.16    # 1.6mm thickness (Z)

        # Pin headers (through-hole, 2 rows of 22)
        PIN_PITCH  = 0.254   # 2.54mm
        PIN_COUNT  = 22
        PIN_ROW_X1 = 0.127   # 1.27mm from left edge (J1)
        PIN_ROW_X2 = 2.413   # 24.13mm from left edge (J3)
        PIN_Y_START = 0.796  # 7.96mm from bottom edge (pin 1)
        PIN_BELOW  = 0.25    # 2.5mm below PCB (for breadboard)
        PIN_ABOVE  = 0.85    # 8.5mm above PCB
        PIN_BLOCK_W = 0.254  # 2.54mm header block width
        PIN_BLOCK_D = 0.254  # 2.54mm header block depth per pin

        # WROOM-1 module (metal shielded, on top face)
        MOD_L      = 2.55    # 25.5mm length
        MOD_W      = 1.80    # 18.0mm width
        MOD_H      = 0.32    # 3.2mm height (shield + PCB)
        # Module centred on X, top portion of board
        MOD_Y_END  = PCB_L - 0.15  # ~1.5mm from top edge (antenna keepout)
        MOD_Y_START = MOD_Y_END - MOD_L

        # USB-C connector (bottom edge, centred-right)
        USB_W      = 0.89    # 8.9mm width
        USB_D      = 0.73    # 7.3mm depth (protrudes beyond PCB)
        USB_H      = 0.32    # 3.2mm height
        USB_X      = 1.94    # 19.4mm from left edge (centre of USB)
        USB_PROT   = 0.15    # 1.5mm protrusion beyond PCB edge

        # Buttons (Reset + Boot, side of board)
        BTN_W      = 0.35    # 3.5mm
        BTN_D      = 0.30    # 3.0mm
        BTN_H      = 0.15    # 1.5mm above PCB

        comp = design.rootComponent
        p = adsk.core.Point3D.create
        extrudes = comp.features.extrudeFeatures

        # ══════════════════════════════════════════════════════════
        # STEP 1: PCB (green board)
        # Origin at centre of bottom face
        # ══════════════════════════════════════════════════════════

        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'PCB Outline'
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
        body.name = 'REF_ESP32_PCB'

        # ══════════════════════════════════════════════════════════
        # STEP 2: Pin header blocks (2 rows, simplified as bars)
        # ══════════════════════════════════════════════════════════

        header_y_start = -PCB_L / 2 + PIN_Y_START
        header_length = (PIN_COUNT - 1) * PIN_PITCH

        for row_x_offset in [PIN_ROW_X1, PIN_ROW_X2]:
            hx = -PCB_W / 2 + row_x_offset

            # Pin block above PCB (black plastic header)
            hSketch = comp.sketches.add(comp.xYConstructionPlane)
            hSketch.name = 'Pin Header'
            hSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                p(hx - PIN_BLOCK_W / 2, header_y_start, 0),
                p(hx + PIN_BLOCK_W / 2, header_y_start + header_length, 0)
            )

            hProf = None
            maxArea = 0
            for pi_idx in range(hSketch.profiles.count):
                pr = hSketch.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if a > maxArea:
                    maxArea = a
                    hProf = pr

            if hProf:
                # Above PCB
                aboveInput = extrudes.createInput(
                    hProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                aboveInput.setDistanceExtent(
                    False, adsk.core.ValueInput.createByReal(PCB_T + PIN_ABOVE)
                )
                try:
                    extrudes.add(aboveInput)
                except:
                    pass

            # Pins below PCB (for breadboard)
            pSketch = comp.sketches.add(comp.xYConstructionPlane)
            pSketch.name = 'Pins Below'
            pSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                p(hx - 0.05, header_y_start, 0),
                p(hx + 0.05, header_y_start + header_length, 0)
            )

            pProf = None
            minArea = float('inf')
            for pi_idx in range(pSketch.profiles.count):
                pr = pSketch.profiles.item(pi_idx)
                a = pr.areaProperties().area
                if a < minArea:
                    minArea = a
                    pProf = pr

            if pProf:
                pinInput = extrudes.createInput(
                    pProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                pinInput.setDistanceExtent(
                    True, adsk.core.ValueInput.createByReal(PIN_BELOW)
                )
                try:
                    extrudes.add(pinInput)
                except:
                    pass

        # ══════════════════════════════════════════════════════════
        # STEP 3: WROOM-1 module (metal shield box on top)
        # ══════════════════════════════════════════════════════════

        topPlaneInput = comp.constructionPlanes.createInput()
        topPlaneInput.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(PCB_T)
        )
        topP = comp.constructionPlanes.add(topPlaneInput)

        modSketch = comp.sketches.add(topP)
        modSketch.name = 'WROOM-1 Module'
        mod_y_centre = -PCB_L / 2 + (MOD_Y_START + MOD_Y_END) / 2
        modSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(-MOD_W / 2, mod_y_centre - MOD_L / 2, 0),
            p(MOD_W / 2, mod_y_centre + MOD_L / 2, 0)
        )

        modProf = None
        maxArea = 0
        for pi_idx in range(modSketch.profiles.count):
            pr = modSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                modProf = pr

        if modProf:
            modInput = extrudes.createInput(
                modProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            modInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(MOD_H)
            )
            extrudes.add(modInput)

        # ══════════════════════════════════════════════════════════
        # STEP 4: USB-C connector (bottom edge, protrudes)
        # ══════════════════════════════════════════════════════════

        usb_cx = -PCB_W / 2 + USB_X
        usb_y_start = -PCB_L / 2 - USB_PROT

        usbSketch = comp.sketches.add(comp.xYConstructionPlane)
        usbSketch.name = 'USB-C Connector'
        usbSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(usb_cx - USB_W / 2, usb_y_start, 0),
            p(usb_cx + USB_W / 2, usb_y_start + USB_D, 0)
        )

        usbProf = None
        maxArea = 0
        for pi_idx in range(usbSketch.profiles.count):
            pr = usbSketch.profiles.item(pi_idx)
            a = pr.areaProperties().area
            if a > maxArea:
                maxArea = a
                usbProf = pr

        if usbProf:
            usbInput = extrudes.createInput(
                usbProf, adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            usbInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(PCB_T + USB_H)
            )
            try:
                extrudes.add(usbInput)
            except:
                pass

        # ══════════════════════════════════════════════════════════
        # Done
        # ══════════════════════════════════════════════════════════

        app.activeViewport.fit()

        ui.messageBox(
            'ESP32-S3-DevKitC-1 reference model created!\n\n'
            f'PCB: {PCB_W*10:.1f} × {PCB_L*10:.1f} × {PCB_T*10:.1f}mm\n'
            f'Pin headers: 2 × {PIN_COUNT} pins, {PIN_PITCH*10:.2f}mm pitch\n'
            f'WROOM-1 module: {MOD_W*10:.1f} × {MOD_L*10:.1f} × {MOD_H*10:.1f}mm\n'
            f'USB-C: {USB_W*10:.1f} × {USB_D*10:.1f} × {USB_H*10:.1f}mm\n\n'
            'NOTE: PCB is 62.7mm long (not 69mm as previously assumed).\n'
            'Verify with your physical board.\n\n'
            'This is a REFERENCE model — not for printing.',
            'REF — ESP32-S3-DevKitC-1'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
