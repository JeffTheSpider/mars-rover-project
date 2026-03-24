"""
Mars Rover Phase 1 (0.4 Scale) Simplified Assembly
====================================================

Creates a dimensionally accurate simplified assembly of ALL Phase 1 Mars Rover
parts in Fusion 360. Uses boxes and cylinders at correct positions to verify
fit, clearance, and overall geometry before detailed part modelling.

Coordinate System (rover coordinates):
  - Origin: Centre of differential bar, body mid-length, mid-width, ground Z=0
  - X: Left-right (left negative, right positive)
  - Y: Front-rear (front positive, rear negative)
  - Z: Vertical (up positive)

ALL Fusion 360 API values are in CENTIMETERS (mm / 10).

References:
  EA-01  Suspension Geometry
  EA-08  Phase 1 Prototype Spec
  EA-10  Ackermann Steering
  EA-20  CAD Preparation Guide

Part List (24 printed + hardware):
  1x  Body frame (440x260x80mm box)
  2x  Rocker arm (180mm long rectangular tube)
  2x  Bogie arm (180mm long rectangular tube)
  1x  Differential bar (300mm steel rod + 3 adapters)
  6x  Wheel (80mm OD x 32mm wide cylinder)
  4x  Steering bracket (35x25x40mm)
  2x  Fixed wheel mount (25x25x30mm)
  6x  N20 motor (12x10x37mm)
  4x  SG90 servo (22.2x11.8x22.7mm)
  11x 608ZZ bearing (22mm OD x 8mm ID x 7mm)
  1x  ESP32-S3 DevKit (69x25mm)
  2x  L298N driver (43x43x27mm)
  1x  LiPo battery (70x35x18mm)
"""

import adsk.core
import adsk.fusion
import traceback
import math


# =============================================================================
# ALL DIMENSIONS IN CENTIMETERS (Fusion 360 API internal unit)
# Source: EA-08, EA-20, generate_rover_params.py at 0.4 scale
# =============================================================================

# -- Overall rover --
BODY_L = 44.0       # 440mm, Y-axis
BODY_W = 26.0       # 260mm, X-axis
BODY_H = 8.0        # 80mm,  Z-axis
BODY_WALL = 0.3     # 3mm walls
GROUND_CLEARANCE = 6.0  # 60mm, body bottom Z

TRACK_HALF = 14.0   # 140mm, half track width (X)
WHEELBASE_HALF = 18.0   # 180mm, half wheelbase (Y)

# -- Wheels --
WHEEL_OD = 8.0      # 80mm outer diameter
WHEEL_R = 4.0       # 40mm radius
WHEEL_W = 3.2       # 32mm width
WHEEL_Z = 4.0       # 40mm, wheel centre height (= radius, on ground)

# -- Rocker arms --
ROCKER_LEN = 18.0   # 180mm, body pivot to front wheel axle
ROCKER_W = 2.0      # 20mm cross-section width
ROCKER_H = 1.5      # 15mm cross-section height

# -- Bogie arms --
BOGIE_LEN = 18.0    # 180mm total (W2 to W3)
BOGIE_HALF = 9.0    # 90mm each side of pivot
BOGIE_W = 1.5       # 15mm cross-section width
BOGIE_H = 1.2       # 12mm cross-section height

# -- Differential bar --
DIFF_LEN = 30.0     # 300mm total rod length
DIFF_ROD_OD = 0.8   # 8mm rod
DIFF_ADAPTER_OD = 1.2  # 12mm adapter tube
DIFF_Z = 6.0        # 60mm, same as body bottom

# -- Pivots --
ROCKER_PIVOT_X = 12.5   # 125mm from centre
ROCKER_PIVOT_Y = 0.0    # at middle axle line
ROCKER_PIVOT_Z = 6.0    # 60mm, at body bottom / ground clearance

DIFF_END_X = 10.0   # 100mm, diff bar end position

# -- Bogie pivot (at rear end of rocker, near body pivot Y) --
# The rocker goes from body pivot (Y=0) to front wheel (Y=+18).
# In a rocker-bogie, the rocker also extends backward to the bogie pivot.
# To get wheels at Y=0 and Y=-18: bogie pivot at Y=-9, arms 9cm each.
# NOTE: Bogie arm is 180mm total (90mm each side of pivot).
# Full scale bogie = 450mm × 0.4 = 180mm.
# The rocker extends backward past body pivot to bogie pivot
# at Y=-9cm. Bogie arms are 9cm each, placing:
#   middle wheel at -9+9 = Y=0  (correct)
#   rear wheel at -9-9 = Y=-18  (correct)
# This is a known geometry refinement documented in this script.
BOGIE_PIVOT_Y = -9.0    # 90mm behind body centre
BOGIE_PIVOT_Z = 4.0     # 40mm, at wheel axle height approximately
BOGIE_ARM_HALF = 9.0    # 90mm from pivot to each wheel (adjusted)

# -- Steering brackets --
STEER_L = 3.5       # 35mm
STEER_W = 2.5       # 25mm
STEER_H = 4.0       # 40mm
STEER_PIVOT_TO_WHEEL = 2.0  # 20mm vertical offset

# -- Fixed wheel mounts (middle wheels) --
FIXED_L = 2.5       # 25mm
FIXED_W = 2.5       # 25mm
FIXED_H = 3.0       # 30mm

# -- N20 motor --
MOTOR_BODY_W = 1.2   # 12mm
MOTOR_BODY_H = 1.0   # 10mm
MOTOR_TOTAL_L = 3.7  # 37mm (motor + gearbox)
MOTOR_SHAFT_L = 1.0  # 10mm shaft protrusion

# -- SG90 servo --
SERVO_W = 2.22       # 22.2mm
SERVO_D = 1.18       # 11.8mm
SERVO_H = 2.27       # 22.7mm

# -- 608ZZ bearing --
BEARING_OD = 2.2     # 22mm
BEARING_ID = 0.8     # 8mm
BEARING_WIDTH = 0.7  # 7mm

# -- Electronics --
ESP32_L = 6.9        # 69mm
ESP32_W = 2.5        # 25mm
ESP32_H = 0.6        # 6mm (approximate board + components height)

L298N_L = 4.3        # 43mm
L298N_W = 4.3        # 43mm
L298N_H = 2.7        # 27mm

LIPO_L = 7.0         # 70mm
LIPO_W = 3.5         # 35mm
LIPO_H = 1.8         # 18mm


# =============================================================================
# Colour definitions (RGB 0-255) for visual differentiation
# =============================================================================
COLOURS = {
    'body':     (100, 100, 110),   # grey
    'rocker':   (200, 120,  50),   # orange
    'bogie':    (220, 160,  60),   # gold
    'diff':     (160, 160, 170),   # light grey (steel)
    'wheel':    ( 60,  60,  65),   # dark grey
    'steer':    ( 80, 160, 200),   # blue
    'fixed':    ( 80, 200, 160),   # teal
    'motor':    ( 50,  50,  55),   # near black
    'servo':    ( 50,  80, 180),   # blue
    'bearing':  (200, 200, 210),   # silver
    'esp32':    ( 40, 120,  40),   # green
    'l298n':    (180,  40,  40),   # red
    'lipo':     (220, 200,  40),   # yellow
}


# =============================================================================
# Helper functions
# =============================================================================

def set_body_colour(body, rgb):
    """Apply an RGB colour to a BRep body."""
    r, g, b = rgb
    colour_prop = body.appearance
    # Create a simple appearance
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    appearances = design.appearances

    # Try to find or create an appearance
    appear_name = f"RoverColour_{r}_{g}_{b}"
    appear = None
    for i in range(appearances.count):
        if appearances.item(i).name == appear_name:
            appear = appearances.item(i)
            break

    if appear is None:
        # Copy from existing and modify
        lib = app.materialLibraries.itemByName('Fusion 360 Appearance Library')
        if lib:
            base_appear = None
            for cat_idx in range(lib.appearances.count):
                a = lib.appearances.item(cat_idx)
                if 'Plastic' in a.name and 'Matte' in a.name:
                    base_appear = a
                    break
            if base_appear is None:
                # Fallback: use first appearance
                if lib.appearances.count > 0:
                    base_appear = lib.appearances.item(0)

            if base_appear:
                appear = design.appearances.addByCopy(base_appear, appear_name)
                # Set the colour
                for prop in appear.appearanceProperties:
                    if hasattr(prop, 'value') and isinstance(prop, adsk.core.ColorProperty):
                        prop.value = adsk.core.Color.create(r, g, b, 255)

    if appear:
        body.appearance = appear


def create_box(comp, name, x, y, z, sx, sy, sz, colour_key='body'):
    """
    Create a box body centred at (x, y, z) with size (sx, sy, sz).
    All values in cm. Returns the created BRep body.

    Uses XY plane sketch at offset z - sz/2 (bottom of box).
    """
    sketches = comp.sketches
    features = comp.features

    # Create offset plane at the bottom Z of the box
    z_bottom = z - sz / 2.0

    # Create construction plane offset from XY
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        comp.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(z_bottom)
    )
    offset_plane = planes.add(plane_input)

    # Create sketch on offset plane
    sketch = sketches.add(offset_plane)
    sketch.name = f"SK_{name}"

    # Draw rectangle centred at (x, y)
    lines = sketch.sketchCurves.sketchLines
    x1 = x - sx / 2.0
    y1 = y - sy / 2.0
    x2 = x + sx / 2.0
    y2 = y + sy / 2.0

    lines.addTwoPointRectangle(
        adsk.core.Point3D.create(x1, y1, 0),
        adsk.core.Point3D.create(x2, y2, 0)
    )

    # Get profile and extrude
    prof = sketch.profiles.item(0)
    ext_input = features.extrudeFeatures.createInput(
        prof,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    ext_input.setDistanceExtent(
        False,
        adsk.core.ValueInput.createByReal(sz)
    )
    ext_feature = features.extrudeFeatures.add(ext_input)

    body = ext_feature.bodies.item(0)
    body.name = name

    # Apply colour
    if colour_key in COLOURS:
        try:
            set_body_colour(body, COLOURS[colour_key])
        except:
            pass  # Colour is cosmetic, don't fail on it

    return body


def create_cylinder(comp, name, cx, cy, cz, radius, height, axis='X',
                    colour_key='wheel'):
    """
    Create a cylinder body.

    axis='X': cylinder axis along X (wheel orientation, rotating about X)
    axis='Y': cylinder axis along Y
    axis='Z': cylinder axis along Z (vertical)

    Centre of cylinder is at (cx, cy, cz).
    For axis='X': extends from cx-height/2 to cx+height/2
    For axis='Z': extends from cz-height/2 to cz+height/2
    """
    sketches = comp.sketches
    features = comp.features

    if axis == 'Z':
        # Sketch on XY plane offset to bottom of cylinder
        z_bottom = cz - height / 2.0
        planes = comp.constructionPlanes
        plane_input = planes.createInput()
        plane_input.setByOffset(
            comp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(z_bottom)
        )
        offset_plane = planes.add(plane_input)
        sketch = sketches.add(offset_plane)
        sketch.name = f"SK_{name}"
        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx, cy, 0), radius
        )
        prof = sketch.profiles.item(0)
        ext_input = features.extrudeFeatures.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_input.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(height)
        )
        ext_feature = features.extrudeFeatures.add(ext_input)

    elif axis == 'X':
        # Sketch on YZ plane offset to left side of cylinder
        x_start = cx - height / 2.0
        planes = comp.constructionPlanes
        plane_input = planes.createInput()
        plane_input.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(x_start)
        )
        offset_plane = planes.add(plane_input)
        sketch = sketches.add(offset_plane)
        sketch.name = f"SK_{name}"
        # On YZ plane: sketch X -> world Y (negated Z rule doesn't apply to
        # the circle centre for Y), sketch Y -> world Z (negated).
        # BUT for a circle, we just need (cy, cz) mapped correctly.
        # YZ plane: sketch_x -> -Z world, sketch_y -> Y world
        # So to get circle at world (cy, cz): sketch_x = -cz, sketch_y = cy
        # Actually, per the SKILL.md: YZ plane sketch X -> -World Z,
        # sketch Y -> World Y. Extrusion +distance -> +X.
        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(-cz, cy, 0), radius
        )
        prof = sketch.profiles.item(0)
        ext_input = features.extrudeFeatures.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_input.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(height)
        )
        ext_feature = features.extrudeFeatures.add(ext_input)

    elif axis == 'Y':
        # Sketch on XZ plane offset to rear of cylinder
        y_start = cy - height / 2.0
        planes = comp.constructionPlanes
        plane_input = planes.createInput()
        plane_input.setByOffset(
            comp.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(y_start)
        )
        offset_plane = planes.add(plane_input)
        sketch = sketches.add(offset_plane)
        sketch.name = f"SK_{name}"
        # XZ plane: sketch_x -> World X, sketch_y -> -World Z
        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx, -cz, 0), radius
        )
        prof = sketch.profiles.item(0)
        ext_input = features.extrudeFeatures.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_input.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(height)
        )
        ext_feature = features.extrudeFeatures.add(ext_input)

    body = ext_feature.bodies.item(0)
    body.name = name

    if colour_key in COLOURS:
        try:
            set_body_colour(body, COLOURS[colour_key])
        except:
            pass

    return body


def create_arm(comp, name, x_centre, y_start, y_end, z, width, height,
               colour_key='rocker'):
    """
    Create a rectangular arm (box) running along Y-axis.
    Centred at x_centre, from y_start to y_end, at height z.
    """
    y_mid = (y_start + y_end) / 2.0
    y_len = abs(y_end - y_start)
    return create_box(comp, name, x_centre, y_mid, z, width, y_len, height,
                      colour_key)


# =============================================================================
# Main script
# =============================================================================

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox(
                'No active design. Please create or open a design first.',
                'Rover Assembly'
            )
            return

        # Use the root component for the assembly
        comp = design.rootComponent

        # Check if there are already bodies (warn user)
        if comp.bRepBodies.count > 0:
            result = ui.messageBox(
                f'The design already has {comp.bRepBodies.count} bodies.\n'
                'Continue and add rover assembly bodies?\n\n'
                'Click Yes to continue, No to cancel.',
                'Rover Assembly',
                adsk.core.MessageBoxButtonTypes.YesNoButtonType
            )
            if result == adsk.core.DialogResults.DialogNo:
                return

        ui.messageBox(
            'Creating Phase 1 (0.4 scale) rover assembly.\n'
            'This will create ~35 simplified bodies.\n\n'
            'Please wait...',
            'Rover Assembly'
        )

        # =====================================================================
        # 1. BODY FRAME
        # =====================================================================
        # Body: 440x260x80mm box, bottom at Z=60mm (ground clearance)
        body_z = GROUND_CLEARANCE + BODY_H / 2.0  # centre Z = 60 + 40 = 100mm = 10cm
        create_box(comp, 'BODY_FRAME',
                   0, 0, body_z,
                   BODY_W, BODY_L, BODY_H,
                   'body')

        # =====================================================================
        # 2. WHEELS (6x)
        # =====================================================================
        # Wheel positions from EA-20 Section 3.6 (all at Z=40mm = 4.0cm centre)
        # Cylinders with axis along X (wheel rotates about X-axis)
        wheel_positions = {
            'WHEEL_FL': (-TRACK_HALF,  WHEELBASE_HALF, WHEEL_Z),
            'WHEEL_ML': (-TRACK_HALF,  0.0,            WHEEL_Z),
            'WHEEL_RL': (-TRACK_HALF, -WHEELBASE_HALF, WHEEL_Z),
            'WHEEL_RR': ( TRACK_HALF, -WHEELBASE_HALF, WHEEL_Z),
            'WHEEL_MR': ( TRACK_HALF,  0.0,            WHEEL_Z),
            'WHEEL_FR': ( TRACK_HALF,  WHEELBASE_HALF, WHEEL_Z),
        }
        for wname, (wx, wy, wz) in wheel_positions.items():
            create_cylinder(comp, wname, wx, wy, wz,
                          WHEEL_R, WHEEL_W, axis='X', colour_key='wheel')

        # =====================================================================
        # 3. ROCKER ARMS (2x)
        # =====================================================================
        # Each rocker: body pivot (Y=0, Z=60mm) forward to front wheel (Y=+180mm)
        # The rocker also extends backward to the bogie pivot.
        #
        # Left rocker: X=-125mm (12.5cm)
        # Front end at Y=+180mm (front wheel)
        # Rear end at Y=-90mm (bogie pivot, adjusted for wheel spacing)

        rocker_z = ROCKER_PIVOT_Z  # 6.0cm (60mm)

        # Left rocker: from bogie pivot (Y=-9) to front wheel (Y=+18)
        create_arm(comp, 'ROCKER_ARM_L',
                   -ROCKER_PIVOT_X,
                   BOGIE_PIVOT_Y, WHEELBASE_HALF,
                   rocker_z, ROCKER_W, ROCKER_H,
                   'rocker')

        # Right rocker: mirror of left
        create_arm(comp, 'ROCKER_ARM_R',
                   ROCKER_PIVOT_X,
                   BOGIE_PIVOT_Y, WHEELBASE_HALF,
                   rocker_z, ROCKER_W, ROCKER_H,
                   'rocker')

        # =====================================================================
        # 4. BOGIE ARMS (2x)
        # =====================================================================
        # Each bogie: from bogie pivot, forward to middle wheel, backward to rear
        # Bogie pivot at Y=-9cm (adjusted for geometry)
        # Middle wheel at Y=0, rear wheel at Y=-18cm
        # So bogie spans from Y=-18 to Y=0, centred at Y=-9

        bogie_z = BOGIE_PIVOT_Z  # 4.0cm (40mm, near wheel centre)

        # Left bogie
        create_arm(comp, 'BOGIE_ARM_L',
                   -TRACK_HALF,
                   -WHEELBASE_HALF, 0.0,
                   bogie_z, BOGIE_W, BOGIE_H,
                   'bogie')

        # Right bogie
        create_arm(comp, 'BOGIE_ARM_R',
                   TRACK_HALF,
                   -WHEELBASE_HALF, 0.0,
                   bogie_z, BOGIE_W, BOGIE_H,
                   'bogie')

        # =====================================================================
        # 5. DIFFERENTIAL BAR
        # =====================================================================
        # Horizontal rod along X-axis at Y=0, Z=60mm
        # Total length 200mm (20cm), from X=-10 to X=+10
        create_cylinder(comp, 'DIFF_BAR_ROD',
                       0, 0, DIFF_Z,
                       DIFF_ROD_OD / 2.0, DIFF_LEN,
                       axis='X', colour_key='diff')

        # Diff adapters at left end, centre, right end
        for suffix, ax in [('_L', -DIFF_END_X), ('_C', 0.0), ('_R', DIFF_END_X)]:
            create_cylinder(comp, f'DIFF_ADAPTER{suffix}',
                           ax, 0, DIFF_Z,
                           DIFF_ADAPTER_OD / 2.0, BEARING_WIDTH,
                           axis='X', colour_key='diff')

        # =====================================================================
        # 6. STEERING BRACKETS (4x corners)
        # =====================================================================
        # At each steered wheel position (FL, FR, RL, RR)
        # The bracket sits above the wheel, with its bottom at the steering
        # pivot height and extending upward.
        # Steering pivot is at approximately Z=40mm + 20mm offset = Z=60mm top
        # Bracket extends from ~Z=20mm to Z=60mm (40mm tall)
        steer_positions = {
            'STEER_FL': (-TRACK_HALF,  WHEELBASE_HALF),
            'STEER_FR': ( TRACK_HALF,  WHEELBASE_HALF),
            'STEER_RL': (-TRACK_HALF, -WHEELBASE_HALF),
            'STEER_RR': ( TRACK_HALF, -WHEELBASE_HALF),
        }
        steer_z_centre = WHEEL_Z + STEER_PIVOT_TO_WHEEL / 2.0  # 4.0 + 1.0 = 5.0cm

        for sname, (sx, sy) in steer_positions.items():
            create_box(comp, sname,
                       sx, sy, steer_z_centre,
                       STEER_W, STEER_L, STEER_H,
                       'steer')

        # =====================================================================
        # 7. FIXED WHEEL MOUNTS (2x middle wheels)
        # =====================================================================
        fixed_z_centre = WHEEL_Z + FIXED_H / 2.0 / 2.0  # slightly above wheel centre

        create_box(comp, 'FIXED_MOUNT_ML',
                   -TRACK_HALF, 0.0, fixed_z_centre,
                   FIXED_W, FIXED_L, FIXED_H,
                   'fixed')
        create_box(comp, 'FIXED_MOUNT_MR',
                   TRACK_HALF, 0.0, fixed_z_centre,
                   FIXED_W, FIXED_L, FIXED_H,
                   'fixed')

        # =====================================================================
        # 8. N20 MOTORS (6x, one per wheel)
        # =====================================================================
        # Motors sit inside the steering brackets / fixed mounts, with shaft
        # pointing outward (along X-axis) toward the wheel.
        # Simplified: small box at each wheel position, inboard of wheel.
        for mname, (wx, wy, wz) in wheel_positions.items():
            motor_name = mname.replace('WHEEL', 'MOTOR')
            # Motor is inboard of wheel (toward body centre)
            if wx < 0:
                motor_x = wx + WHEEL_W / 2.0 + MOTOR_TOTAL_L / 2.0
            else:
                motor_x = wx - WHEEL_W / 2.0 - MOTOR_TOTAL_L / 2.0

            create_box(comp, motor_name,
                       motor_x, wy, wz,
                       MOTOR_TOTAL_L, MOTOR_BODY_W, MOTOR_BODY_H,
                       'motor')

        # =====================================================================
        # 9. SG90 SERVOS (4x, at steered corners)
        # =====================================================================
        # Servos mount on the arm end, driving the steering bracket rotation.
        # Position: adjacent to steering bracket, offset in Y.
        for sname, (sx, sy) in steer_positions.items():
            servo_name = sname.replace('STEER', 'SERVO')
            # Servo sits beside the steering bracket along Y
            servo_y_offset = STEER_L / 2.0 + SERVO_D / 2.0 + 0.2  # 2mm gap
            # Place servo on the body-side of the bracket
            if sy > 0:
                servo_y = sy - servo_y_offset
            else:
                servo_y = sy + servo_y_offset

            create_box(comp, servo_name,
                       sx, servo_y, steer_z_centre,
                       SERVO_W, SERVO_D, SERVO_H,
                       'servo')

        # =====================================================================
        # 10. 608ZZ BEARINGS (10x, at all pivot points)
        # =====================================================================
        # Bearing locations from EA-08/EA-20:
        # 2x rocker body pivots (left/right)
        # 2x bogie pivots (left/right)
        # 1x diff bar centre pivot
        # 2x diff bar end pivots
        # 4x steering pivots (but simplified — some overlap with steering)
        # Total per EA: 11 bearings (not all are separate visual elements)

        # Show bearings at the key structural pivots as small cylinders
        bearing_positions = {
            'BEARING_ROCKER_L': (-ROCKER_PIVOT_X, 0, ROCKER_PIVOT_Z),
            'BEARING_ROCKER_R': ( ROCKER_PIVOT_X, 0, ROCKER_PIVOT_Z),
            'BEARING_BOGIE_L':  (-TRACK_HALF, BOGIE_PIVOT_Y, BOGIE_PIVOT_Z),
            'BEARING_BOGIE_R':  ( TRACK_HALF, BOGIE_PIVOT_Y, BOGIE_PIVOT_Z),
            'BEARING_DIFF_C':   (0, 0, DIFF_Z),
            'BEARING_DIFF_L':   (-DIFF_END_X, 0, DIFF_Z),
            'BEARING_DIFF_R':   ( DIFF_END_X, 0, DIFF_Z),
        }
        for bname, (bx, by, bz) in bearing_positions.items():
            # Bearings are small cylinders along X-axis
            # Use slightly larger OD than bearing for visibility
            create_cylinder(comp, bname,
                           bx, by, bz,
                           BEARING_OD / 2.0, BEARING_WIDTH,
                           axis='X', colour_key='bearing')

        # =====================================================================
        # 11. ELECTRONICS (mounted inside body)
        # =====================================================================
        # All electronics sit on the body floor (Z = 60mm = 6.0cm)
        electronics_floor = GROUND_CLEARANCE + BODY_WALL  # 6.0 + 0.3 = 6.3cm

        # ESP32-S3 DevKit — centre of body, slightly forward
        esp_z = electronics_floor + ESP32_H / 2.0
        create_box(comp, 'ESP32_DEVKIT',
                   0, 5.0, esp_z,
                   ESP32_W, ESP32_L, ESP32_H,
                   'esp32')

        # L298N drivers (x2) — on either side of ESP32
        l298n_z = electronics_floor + L298N_H / 2.0
        create_box(comp, 'L298N_DRIVER_1',
                   -6.0, -3.0, l298n_z,
                   L298N_W, L298N_L, L298N_H,
                   'l298n')
        create_box(comp, 'L298N_DRIVER_2',
                   6.0, -3.0, l298n_z,
                   L298N_W, L298N_L, L298N_H,
                   'l298n')

        # LiPo battery — centre of body, rear
        lipo_z = electronics_floor + LIPO_H / 2.0
        create_box(comp, 'LIPO_2S_2200',
                   0, -8.0, lipo_z,
                   LIPO_W, LIPO_L, LIPO_H,
                   'lipo')

        # =====================================================================
        # DONE
        # =====================================================================
        body_count = comp.bRepBodies.count
        ui.messageBox(
            f'Rover assembly created successfully!\n\n'
            f'Total bodies: {body_count}\n\n'
            f'Parts created:\n'
            f'  - 1x Body frame (440x260x80mm)\n'
            f'  - 6x Wheels (80mm OD x 32mm wide)\n'
            f'  - 2x Rocker arms (180mm+ long)\n'
            f'  - 2x Bogie arms (180mm span)\n'
            f'  - 1x Differential bar + 3 adapters\n'
            f'  - 4x Steering brackets\n'
            f'  - 2x Fixed wheel mounts\n'
            f'  - 6x N20 motors\n'
            f'  - 4x SG90 servos\n'
            f'  - 7x 608ZZ bearings (visible pivots)\n'
            f'  - 1x ESP32, 2x L298N, 1x LiPo\n\n'
            f'All dimensions are Phase 1 (0.4 scale).\n'
            f'Origin = centre of body, ground level Z=0.\n\n'
            f'Use Section Analysis or Inspect > Measure to verify\n'
            f'clearances and fit.',
            'Rover Assembly Complete'
        )

    except:
        if ui:
            ui.messageBox(
                f'Rover Assembly Failed:\n\n{traceback.format_exc()}',
                'Error'
            )
