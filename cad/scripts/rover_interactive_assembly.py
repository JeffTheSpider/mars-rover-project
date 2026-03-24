"""
Mars Rover Phase 1 (0.4 Scale) Interactive Assembly — Full Detail
==================================================================

Creates a complete assembly with correct rocker-bogie suspension geometry.
Body is semi-transparent so internal electronics are visible.

Rocker-bogie layout:
  - Body sits high, rocker arms extend OUT from body sides
  - Shoulder connectors link body wall to rocker arms
  - Rocker arms run along wheel line (X=±140mm), below body
  - Bogie arms at wheel centres, connecting middle and rear wheels
  - Diff bar passes through body connecting rocker pivots

ALL Fusion 360 API values are in CENTIMETERS (mm / 10).
References: EA-01, EA-08, EA-10, EA-20
"""

import adsk.core
import adsk.fusion
import traceback
import math


# =============================================================================
# DIMENSIONS (cm) — from EA-08/EA-20, 0.4 scale
# =============================================================================

# Body
BODY_L = 44.0       # 440mm Y
BODY_W = 26.0       # 260mm X (body edge at ±130mm)
BODY_H = 8.0        # 80mm Z
BODY_WALL = 0.3     # 3mm walls
GROUND_CLEARANCE = 6.0  # 60mm, body bottom Z

# Wheel layout
TRACK_HALF = 14.0       # 140mm half-track (X) — wheel centres
WHEELBASE_HALF = 18.0   # 180mm half-wheelbase (Y)

# Wheels
WHEEL_R = 4.0       # 40mm radius
WHEEL_W = 3.2       # 32mm width
WHEEL_Z = 4.0       # 40mm centre height (= radius, on ground)

# Rocker arms — pivot on body wall, extend out to wheel track line
ROCKER_W = 2.0      # 20mm cross-section width
ROCKER_H = 1.5      # 15mm cross-section height
ROCKER_PIVOT_X = 12.5  # 125mm — pivot inset 5mm from body wall (EA-08/EA-20)
ROCKER_PIVOT_Z = 6.0   # 60mm — at body bottom
ROCKER_ARM_Z = 4.2     # 42mm — close to wheel centres (40mm), slight clearance
ROCKER_ARM_X = 14.0    # arm runs at wheel track line (140mm)

# Bogie arms — at wheel centre height
BOGIE_W = 1.5       # 15mm cross-section
BOGIE_H = 1.2       # 12mm cross-section
BOGIE_PIVOT_Y = -9.0   # 90mm behind centre
BOGIE_PIVOT_Z = 4.0    # 40mm — at wheel centres

# Differential bar — on TOP of body (like Curiosity), 300mm rod
DIFF_LEN = 30.0     # 300mm rod (overhangs 25mm each side of 250mm pivot span)
DIFF_ROD_R = 0.4    # 8mm dia / 2
DIFF_ADAPTER_OD = 1.2
DIFF_END_X = 10.0   # 100mm — ends of diff bar rod
DIFF_LINK_W = 1.0   # 10mm wide linkage arm
DIFF_LINK_H = 0.8   # 8mm thick linkage arm

# Steering bracket — at each steered wheel
STEER_L = 3.5       # 35mm
STEER_W = 3.0       # 30mm
STEER_H = 4.0       # 40mm

# Fixed mount — middle wheels
FIXED_L = 2.5       # 25mm
FIXED_W = 2.5       # 25mm
FIXED_H = 3.0       # 30mm

# N20 motor
MOTOR_BODY_W = 1.2
MOTOR_BODY_H = 1.0
MOTOR_TOTAL_L = 3.7

# SG90 servo
SERVO_W = 2.22
SERVO_D = 1.18
SERVO_H = 2.27

# 608ZZ bearing
BEARING_OD = 2.2
BEARING_WIDTH = 0.7

# Electronics
ESP32_L = 6.9; ESP32_W = 2.5; ESP32_H = 0.6
L298N_L = 4.3; L298N_W = 4.3; L298N_H = 2.7
LIPO_L = 7.0; LIPO_W = 3.5; LIPO_H = 1.8

# Remote Sensing Mast (RSM) — front of deck, like Perseverance
MAST_H = 16.0       # 160mm tall (scaled from ~1.5m real)
MAST_R = 0.5        # 5mm radius pole
MAST_HEAD_W = 3.5   # 35mm camera head width
MAST_HEAD_D = 2.5   # 25mm depth
MAST_HEAD_H = 2.5   # 25mm height
MAST_Y = 15.0       # 150mm forward — front of deck (like Perseverance)

# Equipment deck (top surface)
DECK_L = 40.0       # 400mm — nearly full body length
DECK_W = 24.0       # 240mm — slightly narrower than body
DECK_H = 0.3        # 3mm thin panel

# High-Gain Antenna (HGA) — rear deck, hexagonal dish on boom
HGA_BOOM_H = 4.0    # 40mm boom height
HGA_BOOM_R = 0.3    # 3mm boom radius
HGA_DISH_R = 2.0    # 20mm dish radius
HGA_DISH_H = 0.4    # 4mm dish thickness
HGA_Y = -12.0       # Rear of deck

# Low-Gain Antenna (LGA) — small cylinder on rear deck
LGA_H = 3.0         # 30mm tall
LGA_R = 0.25        # 2.5mm radius

# UHF Antenna — rear, near power
UHF_H = 5.0         # 50mm tall
UHF_R = 0.15        # 1.5mm radius

# RTG/MMRTG power unit — cylinder protruding from rear of body
RTG_R = 1.5         # 15mm radius
RTG_L = 4.0         # 40mm long cylinder
RTG_Y_OFFSET = 2.0  # protrudes 20mm behind body

# Robotic arm placeholder (front) — simplified for Phase 1 visual
ARM_SEG1_L = 8.0    # 80mm upper arm
ARM_SEG2_L = 6.0    # 60mm forearm
ARM_W = 1.0         # 10mm width
ARM_H = 1.0         # 10mm height


# =============================================================================
# Colours (RGB)
# =============================================================================
COLOURS = {
    'body':     (220, 195, 140),   # warm gold/sand (Curiosity-like)
    'deck':     (240, 220, 170),   # lighter gold for top deck
    'rocker':   (200, 170, 100),   # warm tan
    'bogie':    (190, 160,  90),   # slightly darker tan
    'shoulder': (180, 150,  80),   # dark tan
    'diff':     (170, 170, 180),   # silver
    'wheel':    ( 60,  60,  65),   # dark grey/charcoal
    'steer':    (180, 160, 110),   # warm bracket colour
    'fixed':    (180, 160, 110),   # matching warm tone
    'motor':    ( 50,  50,  55),   # near black
    'servo':    ( 40,  70, 160),   # blue servo
    'bearing':  (210, 210, 220),   # bright silver
    'esp32':    ( 30, 140,  30),   # green PCB
    'l298n':    (180,  30,  30),   # red PCB
    'lipo':     (230, 210,  30),   # yellow battery
    'mast':     (200, 200, 210),   # light silver/white
    'antenna':  (240, 240, 245),   # white
}


# =============================================================================
# Globals
# =============================================================================
_app = None
_design = None
_root = None
_appearances_cache = {}


# =============================================================================
# Helpers
# =============================================================================

def get_appearance(r, g, b, opacity=255):
    """Get or create a coloured appearance."""
    key = (r, g, b, opacity)
    if key in _appearances_cache:
        return _appearances_cache[key]

    name = f"Rover_{r}_{g}_{b}_{opacity}"
    appearances = _design.appearances

    for i in range(appearances.count):
        if appearances.item(i).name == name:
            _appearances_cache[key] = appearances.item(i)
            return _appearances_cache[key]

    base = None
    for li in range(_app.materialLibraries.count):
        lib = _app.materialLibraries.item(li)
        for ai in range(lib.appearances.count):
            a = lib.appearances.item(ai)
            aname = a.name.lower()
            if 'plastic' in aname and ('matte' in aname or 'generic' in aname):
                base = a
                break
            if 'generic' in aname:
                base = a
        if base:
            break

    if base is None:
        for li in range(_app.materialLibraries.count):
            lib = _app.materialLibraries.item(li)
            if lib.appearances.count > 0:
                base = lib.appearances.item(0)
                break

    if base is None:
        return None

    appear = appearances.addByCopy(base, name)
    for pi in range(appear.appearanceProperties.count):
        prop = appear.appearanceProperties.item(pi)
        if isinstance(prop, adsk.core.ColorProperty):
            try:
                prop.value = adsk.core.Color.create(r, g, b, 255)
            except:
                pass

    _appearances_cache[key] = appear
    return appear


def colour_body(body, col_key, opacity=255):
    """Apply colour to a body. Opacity: 0=invisible, 255=fully opaque."""
    if col_key not in COLOURS:
        return
    r, g, b = COLOURS[col_key]
    try:
        a = get_appearance(r, g, b, 255)  # Always use opaque appearance for colour
        if a:
            body.appearance = a
    except:
        pass
    # Use body.opacity for transparency (0.0=invisible, 1.0=opaque)
    if opacity < 255:
        try:
            body.opacity = opacity / 255.0
        except:
            pass


def new_component(name):
    """Create a new component under root."""
    mat = adsk.core.Matrix3D.create()
    occ = _root.occurrences.addNewComponent(mat)
    occ.component.name = name
    return occ, occ.component


def make_box(comp, name, cx, cy, cz, sx, sy, sz, col_key='body', opacity=255):
    """Create a box centred at (cx, cy, cz) with size (sx, sy, sz) cm."""
    z_bot = cz - sz / 2.0
    planes = comp.constructionPlanes
    pi = planes.createInput()
    pi.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_bot))
    plane = planes.add(pi)

    sk = comp.sketches.add(plane)
    sk.name = f"SK_{name}"
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(cx - sx/2, cy - sy/2, 0),
        adsk.core.Point3D.create(cx + sx/2, cy + sy/2, 0),
    )

    prof = sk.profiles.item(0)
    ext_in = comp.features.extrudeFeatures.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(sz))
    body = comp.features.extrudeFeatures.add(ext_in).bodies.item(0)
    body.name = name
    colour_body(body, col_key, opacity)
    return body


def make_cylinder(comp, name, cx, cy, cz, radius, length, axis='X', col_key='wheel', opacity=255):
    """Create a cylinder centred at (cx, cy, cz) along given axis."""
    feats = comp.features.extrudeFeatures
    planes = comp.constructionPlanes
    p3 = adsk.core.Point3D.create

    if axis == 'Z':
        z_bot = cz - length / 2.0
        pi = planes.createInput()
        pi.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_bot))
        plane = planes.add(pi)
        sk = comp.sketches.add(plane)
        sk.name = f"SK_{name}"
        sk.sketchCurves.sketchCircles.addByCenterRadius(p3(cx, cy, 0), radius)
    elif axis == 'X':
        x_start = cx - length / 2.0
        pi = planes.createInput()
        pi.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x_start))
        plane = planes.add(pi)
        sk = comp.sketches.add(plane)
        sk.name = f"SK_{name}"
        sk.sketchCurves.sketchCircles.addByCenterRadius(p3(-cz, cy, 0), radius)
    elif axis == 'Y':
        y_start = cy - length / 2.0
        pi = planes.createInput()
        pi.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y_start))
        plane = planes.add(pi)
        sk = comp.sketches.add(plane)
        sk.name = f"SK_{name}"
        sk.sketchCurves.sketchCircles.addByCenterRadius(p3(cx, -cz, 0), radius)
    else:
        raise ValueError(f"Unknown axis: {axis}")

    prof = sk.profiles.item(0)
    ext_in = feats.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(length))
    body = feats.add(ext_in).bodies.item(0)
    body.name = name
    colour_body(body, col_key, opacity)
    return body


def make_arm(comp, name, x_centre, y_start, y_end, z, w, h, col_key='rocker'):
    """Box running along Y from y_start to y_end."""
    y_mid = (y_start + y_end) / 2.0
    y_len = abs(y_end - y_start)
    return make_box(comp, name, x_centre, y_mid, z, w, y_len, h, col_key)


def make_joint_geometry(occ, x, y, z):
    """Create a SketchPoint at (x, y, z) in the component, return its proxy as JointGeometry.

    The Fusion 360 API requires a SketchPoint/BRepVertex/ConstructionPoint for
    JointGeometry — raw Point3D is NOT accepted. We create a sketch on an offset
    plane at height Z, place a point at (X, Y), and return its assembly proxy.
    """
    comp = occ.component
    # Create offset plane at Z height
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z))
    plane = comp.constructionPlanes.add(pi)

    # Create sketch with a single point at (x, y) on that plane
    sk = comp.sketches.add(plane)
    sk.name = f'JP_{x:.1f}_{y:.1f}_{z:.1f}'
    sk.isVisible = False  # Hide helper sketches
    pt = sk.sketchPoints.add(adsk.core.Point3D.create(x, y, 0))

    # Get proxy in assembly context
    pt_proxy = pt.createForAssemblyContext(occ)
    return adsk.fusion.JointGeometry.createByPoint(pt_proxy)


def add_revolute_joint(occ1, occ2, origin, axis, angle_min_deg, angle_max_deg, name):
    """Create an as-built revolute joint at the specified pivot point.

    origin: (x, y, z) in assembly space — the actual pivot location.
    axis: 'X', 'Y', or 'Z' — the rotation axis (assembly coordinates).
          X = left-right axis (for rocking, wheel spin)
          Z = vertical axis (for steering yaw)
    """
    try:
        joints = _root.asBuiltJoints

        # Create joint geometry at the EXACT pivot point using a sketch point
        geo = make_joint_geometry(occ1, origin[0], origin[1], origin[2])

        ji = joints.createInput(occ1, occ2, geo)

        # Use predefined axis directions — much more reliable than custom Vector3D
        # (customRotationAxisEntity expects an entity, not a Vector3D)
        if axis == 'X':
            ji.setAsRevoluteJointMotion(
                adsk.fusion.JointDirections.XAxisJointDirection)
        elif axis == 'Y':
            ji.setAsRevoluteJointMotion(
                adsk.fusion.JointDirections.YAxisJointDirection)
        elif axis == 'Z':
            ji.setAsRevoluteJointMotion(
                adsk.fusion.JointDirections.ZAxisJointDirection)

        joint = joints.add(ji)
        joint.name = name

        try:
            rev_motion = adsk.fusion.RevoluteJointMotion.cast(joint.jointMotion)
            if rev_motion:
                rev_motion.rotationLimits.isMinimumValueEnabled = True
                rev_motion.rotationLimits.minimumValue = math.radians(angle_min_deg)
                rev_motion.rotationLimits.isMaximumValueEnabled = True
                rev_motion.rotationLimits.maximumValue = math.radians(angle_max_deg)
        except:
            pass  # Limits are optional

        return joint
    except:
        return None  # Joint creation failed — geometry still shows correctly


# =============================================================================
# Geometry builder — shared by both modes
# =============================================================================

def build_geometry(comp_or_func, is_assembly=False):
    """
    Build all rover geometry.
    In Part mode: comp_or_func is the root component, all bodies go there.
    In Assembly mode: comp_or_func is new_component function, returns occs dict.
    """
    body_z = GROUND_CLEARANCE + BODY_H / 2.0   # 10.0cm centre
    body_top_z = GROUND_CLEARANCE + BODY_H     # 14.0cm top of body
    electronics_z = GROUND_CLEARANCE + BODY_WALL
    diff_z = body_top_z + 0.5                   # 145mm — diff bar sits ON TOP of body
    steer_z = WHEEL_Z                           # 40mm — bracket at wheel centre height
    fixed_z = WHEEL_Z                           # 40mm — mount at wheel centre height

    wheel_positions = {
        'FL': (-TRACK_HALF,  WHEELBASE_HALF, WHEEL_Z),
        'FR': ( TRACK_HALF,  WHEELBASE_HALF, WHEEL_Z),
        'ML': (-TRACK_HALF,  0.0,            WHEEL_Z),
        'MR': ( TRACK_HALF,  0.0,            WHEEL_Z),
        'RL': (-TRACK_HALF, -WHEELBASE_HALF, WHEEL_Z),
        'RR': ( TRACK_HALF, -WHEELBASE_HALF, WHEEL_Z),
    }
    steer_corners = ['FL', 'FR', 'RL', 'RR']
    occs = {}

    def get_comp(name):
        if is_assembly:
            occ, c = new_component(name)
            occs[name] = occ
            return c
        else:
            return comp_or_func

    # =========================================================================
    # 1. BODY — Perseverance-style: WEB + equipment deck + instruments
    # =========================================================================
    c = get_comp('Body')
    body_top_z = GROUND_CLEARANCE + BODY_H  # top of body

    # Main body / Warm Electronics Box (semi-transparent)
    make_box(c, 'WEB', 0, 0, body_z, BODY_W, BODY_L, BODY_H, 'body', 80)

    # Equipment deck — flat platform on top (like Perseverance's deck)
    deck_z = body_top_z + DECK_H / 2.0
    make_box(c, 'EquipmentDeck', 0, 0, deck_z, DECK_W, DECK_L, DECK_H, 'deck')

    # ── Remote Sensing Mast (RSM) — front of deck ──
    mast_base_z = body_top_z
    mast_top_z = mast_base_z + MAST_H
    mast_mid_z = (mast_base_z + mast_top_z) / 2.0
    make_cylinder(c, 'RSM_Pole', 0, MAST_Y, mast_mid_z,
                  MAST_R, MAST_H, 'Z', 'mast')
    # Mast head — houses SuperCam + Mastcam-Z
    head_z = mast_top_z + MAST_HEAD_H / 2.0
    make_box(c, 'MastHead', 0, MAST_Y, head_z,
             MAST_HEAD_W, MAST_HEAD_D, MAST_HEAD_H, 'mast')
    # SuperCam lens (circular, front of head)
    make_cylinder(c, 'SuperCam', 0, MAST_Y + MAST_HEAD_D / 2.0 + 0.15,
                  head_z + 0.3, 0.6, 0.4, 'Y', 'motor')
    # Mastcam-Z pair (two small boxes below head)
    for ex in [-0.9, 0.9]:
        make_box(c, f'MastcamZ_{"L" if ex < 0 else "R"}',
                 ex, MAST_Y, head_z - MAST_HEAD_H / 2.0 - 0.5,
                 0.6, 0.8, 0.6, 'motor')

    # ── High-Gain Antenna (HGA) — rear deck, on boom ──
    hga_base_z = body_top_z
    hga_boom_mid_z = hga_base_z + HGA_BOOM_H / 2.0
    make_cylinder(c, 'HGA_Boom', 5.0, HGA_Y, hga_boom_mid_z,
                  HGA_BOOM_R, HGA_BOOM_H, 'Z', 'antenna')
    # Dish on top of boom
    hga_dish_z = hga_base_z + HGA_BOOM_H + HGA_DISH_H / 2.0
    make_cylinder(c, 'HGA_Dish', 5.0, HGA_Y, hga_dish_z,
                  HGA_DISH_R, HGA_DISH_H, 'Z', 'antenna')

    # ── Low-Gain Antenna (LGA) — small stick near HGA ──
    lga_mid_z = body_top_z + LGA_H / 2.0
    make_cylinder(c, 'LGA', 3.0, HGA_Y - 2.0, lga_mid_z,
                  LGA_R, LGA_H, 'Z', 'antenna')

    # ── UHF Antenna — rear, near power ──
    uhf_mid_z = body_top_z + UHF_H / 2.0
    make_cylinder(c, 'UHF_Antenna', -4.0, -BODY_L / 2.0 + 3.0, uhf_mid_z,
                  UHF_R, UHF_H, 'Z', 'antenna')

    # ── RTG/MMRTG power unit — cylinder protruding from rear ──
    rtg_y = -BODY_L / 2.0 - RTG_L / 2.0 + RTG_Y_OFFSET
    rtg_z = body_z  # same height as body centre
    make_cylinder(c, 'MMRTG', 0, rtg_y, rtg_z,
                  RTG_R, RTG_L, 'Y', 'diff')
    # RTG heat fins (4 thin plates radiating outward)
    for angle_deg in [0, 90, 180, 270]:
        angle_rad = math.radians(angle_deg)
        fin_x = math.cos(angle_rad) * (RTG_R + 0.5)
        fin_z = rtg_z + math.sin(angle_rad) * (RTG_R + 0.5)
        make_box(c, f'RTG_Fin_{angle_deg}',
                 fin_x, rtg_y, fin_z,
                 0.3, RTG_L * 0.8, 1.5, 'diff')

    # ── Robotic arm placeholder — front of body ──
    arm_base_y = BODY_L / 2.0 - 3.0   # near front of body
    arm_base_z = body_z                # mid-height of body
    # Upper arm segment — extends forward
    make_box(c, 'Arm_Upper', 3.0, arm_base_y + ARM_SEG1_L / 2.0, arm_base_z,
             ARM_W, ARM_SEG1_L, ARM_H, 'diff')
    # Forearm — angled down
    make_box(c, 'Arm_Forearm', 3.0, arm_base_y + ARM_SEG1_L + ARM_SEG2_L / 2.0,
             arm_base_z - 2.0,
             ARM_W, ARM_SEG2_L, ARM_H, 'diff')
    # Turret head
    make_cylinder(c, 'Arm_Turret', 3.0, arm_base_y + ARM_SEG1_L + ARM_SEG2_L,
                  arm_base_z - 2.0, 1.0, 1.0, 'Y', 'bearing')

    # ── Electronics inside body ──
    esp_z = electronics_z + ESP32_H / 2.0
    make_box(c, 'ESP32_DevKit', 0, 5.0, esp_z, ESP32_W, ESP32_L, ESP32_H, 'esp32')
    l298n_z = electronics_z + L298N_H / 2.0
    make_box(c, 'L298N_Driver_1', -6.0, -3.0, l298n_z, L298N_W, L298N_L, L298N_H, 'l298n')
    make_box(c, 'L298N_Driver_2',  6.0, -3.0, l298n_z, L298N_W, L298N_L, L298N_H, 'l298n')
    lipo_z = electronics_z + LIPO_H / 2.0
    make_box(c, 'LiPo_2S', 0, -8.0, lipo_z, LIPO_W, LIPO_L, LIPO_H, 'lipo')

    # =========================================================================
    # 2. DIFFERENTIAL BAR — ON TOP of body (like Curiosity/Perseverance)
    #    300mm rod at body top, with vertical linkage arms going DOWN
    #    to rocker pivots at X=±125, Z=60
    # =========================================================================
    c = get_comp('DiffBar')
    # Main rod: 300mm along X, on top of body
    make_cylinder(c, 'DiffRod', 0, 0, diff_z, DIFF_ROD_R, DIFF_LEN, 'X', 'diff')
    # Adapters/bearings at centre and both ends
    for suffix, ax in [('_L', -DIFF_END_X), ('_C', 0.0), ('_R', DIFF_END_X)]:
        make_cylinder(c, f'DiffAdapter{suffix}', ax, 0, diff_z,
                      DIFF_ADAPTER_OD / 2.0, BEARING_WIDTH, 'X', 'bearing')
    # Vertical linkage arms: from diff bar ends (X=±100, Z=top) DOWN to
    # rocker pivots (X=±125, Z=60). These are the visible connecting rods.
    for sign, suffix in [(-1, '_L'), (1, '_R')]:
        link_x = sign * DIFF_END_X          # ±100mm at top
        pivot_x = sign * ROCKER_PIVOT_X     # ±125mm at bottom
        # Vertical portion: goes from diff_z down to pivot Z
        vert_mid_z = (diff_z + ROCKER_PIVOT_Z) / 2.0
        vert_h = diff_z - ROCKER_PIVOT_Z
        make_box(c, f'DiffLinkVert{suffix}',
                 link_x, 0, vert_mid_z,
                 DIFF_LINK_W, DIFF_LINK_W, vert_h, 'diff')
        # Horizontal portion: from diff bar end (X=100) outward to rocker pivot (X=125)
        horiz_cx = (link_x + pivot_x) / 2.0
        horiz_len = abs(pivot_x - link_x)
        make_box(c, f'DiffLinkHoriz{suffix}',
                 horiz_cx, 0, ROCKER_PIVOT_Z,
                 horiz_len, DIFF_LINK_W, DIFF_LINK_H, 'diff')

    # =========================================================================
    # 3. ROCKER ARMS — angled from body pivot DOWN to wheel height
    #    Real rover geometry: arm hangs below body, reaching down to wheels
    #    Pivot at (X=125, Y=0, Z=60), arm drops to Z=40 at wheel centres
    #    Front wheel at Y=+180, Bogie pivot at Y=-90
    # =========================================================================
    for side, sign in [('L', -1), ('R', 1)]:
        c = get_comp(f'Rocker_{side}')
        arm_x = sign * ROCKER_ARM_X      # ±140mm — wheel track line
        pivot_x = sign * ROCKER_PIVOT_X  # ±125mm — on body wall (inset 5mm)

        # Pivot boss — cylindrical boss at body wall where 608ZZ bearing sits
        make_cylinder(c, f'Bearing_Rocker_{side}',
                      pivot_x, 0, ROCKER_PIVOT_Z,
                      BEARING_OD / 2.0, BEARING_WIDTH + 0.6, 'X', 'bearing')

        # Outward strut: from pivot (X=125) out to track line (X=140) at pivot Z
        strut_cx = (pivot_x + arm_x) / 2.0
        strut_len = abs(arm_x - pivot_x)  # 15mm
        make_box(c, f'RockerStrut_{side}',
                 strut_cx, 0, ROCKER_PIVOT_Z,
                 strut_len, ROCKER_W, ROCKER_H, 'rocker')

        # Vertical drop: from pivot height (Z=60) DOWN to wheel height (Z=40)
        # This is the key visual — the arm hangs below the body
        drop_z = (ROCKER_PIVOT_Z + WHEEL_Z) / 2.0   # midpoint Z=50
        drop_h = ROCKER_PIVOT_Z - WHEEL_Z            # 20mm drop
        make_box(c, f'RockerDrop_{side}',
                 arm_x, 0, drop_z,
                 ROCKER_W, ROCKER_W, drop_h, 'rocker')

        # Front arm: from pivot Y=0 to front wheel Y=+180, at WHEEL height
        make_arm(c, f'RockerFrontArm_{side}',
                 arm_x, 0.0, WHEELBASE_HALF,
                 WHEEL_Z, ROCKER_W, ROCKER_H, 'rocker')

        # Rear arm: from pivot Y=0 to bogie pivot Y=-90, at WHEEL height
        make_arm(c, f'RockerRearArm_{side}',
                 arm_x, BOGIE_PIVOT_Y, 0.0,
                 WHEEL_Z, ROCKER_W, ROCKER_H, 'rocker')

    # =========================================================================
    # 4. BOGIE ARMS — at wheel centres height, outside body
    # =========================================================================
    for side, sign in [('L', -1), ('R', 1)]:
        c = get_comp(f'Bogie_{side}')
        arm_x = sign * TRACK_HALF

        make_arm(c, f'BogieArm_{side}',
                 arm_x, -WHEELBASE_HALF, 0.0,
                 BOGIE_PIVOT_Z, BOGIE_W, BOGIE_H, 'bogie')

        # Bearing at bogie pivot on rocker
        make_cylinder(c, f'Bearing_Bogie_{side}',
                      arm_x, BOGIE_PIVOT_Y, BOGIE_PIVOT_Z,
                      BEARING_OD / 2.0, BEARING_WIDTH, 'X', 'bearing')

    # =========================================================================
    # 5. STEERING BRACKETS + motors + servos + bearings at steered wheels
    # =========================================================================
    for tag in steer_corners:
        wx, wy, wz = wheel_positions[tag]
        c = get_comp(f'Steer_{tag}')

        make_box(c, f'SteerBracket_{tag}', wx, wy, steer_z,
                 STEER_W, STEER_L, STEER_H, 'steer')

        # 608ZZ bearing at steering pivot (vertical axis)
        make_cylinder(c, f'Bearing_Steer_{tag}', wx, wy,
                      steer_z + STEER_H / 2.0,
                      BEARING_OD / 2.0, BEARING_WIDTH, 'Z', 'bearing')

        # Motor inboard of wheel
        if wx < 0:
            motor_x = wx + WHEEL_W / 2.0 + MOTOR_TOTAL_L / 2.0
        else:
            motor_x = wx - WHEEL_W / 2.0 - MOTOR_TOTAL_L / 2.0
        make_box(c, f'Motor_{tag}', motor_x, wy, wz,
                 MOTOR_TOTAL_L, MOTOR_BODY_W, MOTOR_BODY_H, 'motor')

        # Servo beside bracket
        servo_y_off = STEER_L / 2.0 + SERVO_D / 2.0 + 0.2
        servo_y = wy - servo_y_off if wy > 0 else wy + servo_y_off
        make_box(c, f'Servo_{tag}', wx, servo_y, steer_z,
                 SERVO_W, SERVO_D, SERVO_H, 'servo')

    # =========================================================================
    # 6. FIXED MOUNTS + motors at middle wheels
    # =========================================================================
    for tag in ['ML', 'MR']:
        wx, wy, wz = wheel_positions[tag]
        c = get_comp(f'Fixed_{tag}')

        make_box(c, f'FixedMount_{tag}', wx, wy, fixed_z,
                 FIXED_W, FIXED_L, FIXED_H, 'fixed')

        if wx < 0:
            motor_x = wx + WHEEL_W / 2.0 + MOTOR_TOTAL_L / 2.0
        else:
            motor_x = wx - WHEEL_W / 2.0 - MOTOR_TOTAL_L / 2.0
        make_box(c, f'Motor_{tag}', motor_x, wy, wz,
                 MOTOR_TOTAL_L, MOTOR_BODY_W, MOTOR_BODY_H, 'motor')

    # =========================================================================
    # 7. WHEELS — outer tyre + inner hub for more realistic look
    # =========================================================================
    for tag, (wx, wy, wz) in wheel_positions.items():
        c = get_comp(f'Wheel_{tag}')
        # Outer wheel (tyre)
        make_cylinder(c, f'Wheel_{tag}', wx, wy, wz,
                      WHEEL_R, WHEEL_W, 'X', 'wheel')
        # Inner hub (slightly wider, smaller radius, silver)
        make_cylinder(c, f'Hub_{tag}', wx, wy, wz,
                      WHEEL_R * 0.45, WHEEL_W + 0.4, 'X', 'bearing')
        # Axle stub
        make_cylinder(c, f'Axle_{tag}', wx, wy, wz,
                      0.4, WHEEL_W + 1.0, 'X', 'diff')

    # =========================================================================
    # 8. Additional bearings — diff bar centre bearing on body
    # =========================================================================
    if not is_assembly:
        c = comp_or_func
    else:
        c = occs['Body'].component
    # Diff bar centre bearing (mounted on body top, 608ZZ)
    make_cylinder(c, 'Bearing_Diff_Centre', 0, 0, diff_z,
                  BEARING_OD / 2.0, BEARING_WIDTH, 'X', 'bearing')
    # Body-side rocker pivot bearings (2x, pressed into body walls)
    for sign, suffix in [(-1, 'L'), (1, 'R')]:
        make_cylinder(c, f'Bearing_BodyPivot_{suffix}',
                      sign * ROCKER_PIVOT_X, 0, ROCKER_PIVOT_Z,
                      BEARING_OD / 2.0, BEARING_WIDTH, 'X', 'bearing')

    return occs, wheel_positions, steer_corners, steer_z, fixed_z, diff_z


# =============================================================================
# Main
# =============================================================================

def run(context):
    global _app, _design, _root
    ui = None
    try:
        _app = adsk.core.Application.get()
        ui = _app.userInterface
        _design = adsk.fusion.Design.cast(_app.activeProduct)
        if not _design:
            ui.messageBox('No active design.', 'Error')
            return

        _root = _design.rootComponent

        if _root.occurrences.count > 0 or _root.bRepBodies.count > 0:
            r = ui.messageBox(
                'Design has existing content. Continue?',
                'Rover Assembly',
                adsk.core.MessageBoxButtonTypes.YesNoButtonType)
            if r == adsk.core.DialogResults.DialogNo:
                return

        # Try assembly mode first, fall back to part mode
        interactive = False
        try:
            occs, wheel_positions, steer_corners, steer_z, fixed_z, diff_z = \
                build_geometry(new_component, is_assembly=True)
            interactive = True
        except RuntimeError as e:
            if 'Part Design' in str(e) or 'one component' in str(e):
                occs, wheel_positions, steer_corners, steer_z, fixed_z, diff_z = \
                    build_geometry(_root, is_assembly=False)
            else:
                raise

        # Create joints (only in assembly mode) — entirely optional
        joints_created = 0
        joints_failed = 0
        if interactive:
            try:
                # CRITICAL: Ground the body FIRST so joints know what stays fixed
                occs['Body'].isGrounded = True

                def try_joint(*args, **kwargs):
                    nonlocal joints_created, joints_failed
                    j = add_revolute_joint(*args, **kwargs)
                    if j:
                        joints_created += 1
                    else:
                        joints_failed += 1

                # Diff bar pivot — rolls around X axis (left-right), on top of body
                try_joint(occs['DiffBar'], occs['Body'],
                          (0, 0, diff_z), 'X', -15, 15, 'J_DiffBar')

                # Rocker pivots on body — rock around X axis (up/down rocking)
                for side, sign in [('L', -1), ('R', 1)]:
                    try_joint(
                        occs[f'Rocker_{side}'], occs['Body'],
                        (sign * ROCKER_PIVOT_X, 0, ROCKER_PIVOT_Z),
                        'X', -30, 30, f'J_Rocker_{side}')

                # Bogie pivots on rockers — articulate around X axis (up/down)
                for side, sign in [('L', -1), ('R', 1)]:
                    try_joint(
                        occs[f'Bogie_{side}'], occs[f'Rocker_{side}'],
                        (sign * TRACK_HALF, BOGIE_PIVOT_Y, BOGIE_PIVOT_Z),
                        'X', -25, 25, f'J_Bogie_{side}')

                # Steering pivots — front wheels on rockers, rotate around Z (yaw)
                for tag in ['FL', 'FR']:
                    wx, wy, _ = wheel_positions[tag]
                    try_joint(
                        occs[f'Steer_{tag}'], occs[f'Rocker_{tag[1]}'],
                        (wx, wy, steer_z), 'Z', -35, 35, f'J_Steer_{tag}')

                # Steering pivots — rear wheels on bogies, rotate around Z (yaw)
                for tag in ['RL', 'RR']:
                    wx, wy, _ = wheel_positions[tag]
                    try_joint(
                        occs[f'Steer_{tag}'], occs[f'Bogie_{tag[1]}'],
                        (wx, wy, steer_z), 'Z', -35, 35, f'J_Steer_{tag}')

                # Fixed mounts on bogies — rigid (no rotation)
                for tag in ['ML', 'MR']:
                    wx, wy, _ = wheel_positions[tag]
                    try_joint(
                        occs[f'Fixed_{tag}'], occs[f'Bogie_{tag[1]}'],
                        (wx, wy, fixed_z), 'Z', 0, 0, f'J_Fixed_{tag}')

                # Wheel spin — all wheels rotate around X axis (axle)
                for tag in steer_corners:
                    wx, wy, wz = wheel_positions[tag]
                    try_joint(
                        occs[f'Wheel_{tag}'], occs[f'Steer_{tag}'],
                        (wx, wy, wz), 'X', -360, 360, f'J_Wheel_{tag}')

                for tag in ['ML', 'MR']:
                    wx, wy, wz = wheel_positions[tag]
                    try_joint(
                        occs[f'Wheel_{tag}'], occs[f'Fixed_{tag}'],
                        (wx, wy, wz), 'X', -360, 360, f'J_Wheel_{tag}')

            except:
                pass  # All joint creation failed — geometry still intact

        # Zoom to fit
        _app.activeViewport.fit()

        # Report
        if interactive:
            n_comp = _root.occurrences.count
            try:
                n_joints = _root.asBuiltJoints.count
            except:
                n_joints = 0
            n_bodies = sum(_root.occurrences.item(i).component.bRepBodies.count
                           for i in range(n_comp))
            joint_info = f'{joints_created} joints created'
            if joints_failed > 0:
                joint_info += f' ({joints_failed} skipped)'
            if joints_created > 0:
                joint_info += '\nDrag to articulate. Right-click joint > Animate.'
            msg = (f'Assembly created!\n\n'
                   f'{n_comp} components, {n_bodies} bodies\n'
                   f'{joint_info}')
        else:
            n_bodies = _root.bRepBodies.count
            msg = (f'Static assembly created!\n\n'
                   f'{n_bodies} bodies (Part Design mode — no joints)\n\n'
                   f'For joints: File > New Design (Assembly type)')

        ui.messageBox(msg, 'Mars Rover Assembly')

    except:
        if ui:
            ui.messageBox(f'Error:\n\n{traceback.format_exc()}', 'Error')
