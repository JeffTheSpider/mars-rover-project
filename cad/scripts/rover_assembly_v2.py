"""
Mars Rover Phase 1 — Full Assembly Visualisation (V2)
======================================================

Imports ALL 29 STL exports and positions them in a complete rover
assembly with colour-coded subsystems. This shows how every printed
part fits together in the final Phase 1 (0.4 scale) prototype.

Coordinate System (rover coordinates, cm):
  Origin: Centre of body, at ground level (Z=0)
  X: Left (+) / Right (-)
  Y: Front (+) / Rear (-)
  Z: Up (+)

Subsystem Colours:
  Body/panels   — warm grey
  Wheels        — dark charcoal
  Suspension    — Mars orange
  Steering      — sky blue
  Drivetrain    — teal
  Electronics   — green
  Accessories   — light grey

Usage: Run as Script in Fusion 360 (Shift+S > RoverAssemblyV2 > Run)
Requires: All 29 STLs exported via BatchExportAll first.

Reference: EA-01, EA-08, EA-25, EA-26, EA-27, EA-28
"""

import adsk.core
import adsk.fusion
import traceback
import math
import os


# ══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

STL_ROOT = r'D:\Mars Rover Project\3d-print'

# Phase 1 (0.4 scale) rover layout — ALL VALUES IN CENTIMETERS
# Source: generate_rover_params.py at scale=0.4

# Body
BODY_L = 44.0           # 440mm, Y-axis
BODY_W = 26.0           # 260mm, X-axis
BODY_H = 12.0           # 120mm, Z-axis (updated from EA-08)
GROUND_Z = 6.0          # 60mm ground clearance, body bottom Z

# Wheel layout
TRACK_HALF = 14.0       # 140mm, half track width (X)
WB_HALF = 18.0          # 180mm, half wheelbase (Y)
WHEEL_R = 4.0           # 40mm radius
WHEEL_W = 3.2           # 32mm width
WHEEL_Z = WHEEL_R       # wheel centre Z = radius (on ground)

# Suspension
DIFF_Z = GROUND_Z       # diff bar at body bottom
ROCKER_X = 12.5         # 125mm, rocker pivot X offset
BOGIE_Y = -9.0          # 90mm behind body centre
BOGIE_Z = WHEEL_Z       # at wheel axle height

# Connector offsets (approximate — where connectors sit on tubes)
CONN_OFFSET = 2.0       # 20mm from parent junction


# ══════════════════════════════════════════════════════════════════════
# COLOUR PALETTE — Mars rover aesthetic
# ══════════════════════════════════════════════════════════════════════

COLOURS = {
    'body':         (180, 175, 165),    # warm stone grey
    'deck':         (200, 195, 185),    # lighter stone
    'wheel':        ( 55,  55,  60),    # dark charcoal
    'suspension':   (210, 120,  45),    # Mars orange
    'steering':     ( 70, 150, 210),    # sky blue
    'drivetrain':   ( 60, 190, 160),    # teal
    'electronics':  ( 60, 160,  80),    # circuit green
    'accessory':    (170, 170, 175),    # light grey
    'diffbar':      (160, 160, 170),    # steel grey
    'calibration':  (220, 220, 200),    # off-white
}


# ══════════════════════════════════════════════════════════════════════
# PART DEFINITIONS
# ══════════════════════════════════════════════════════════════════════
# (stl_subpath, display_name, colour_key, [(x, y, z, rx, ry, rz), ...])
# rx, ry, rz = rotation in degrees around each axis (applied in Z, Y, X order)

PARTS = [
    # ── Body quadrants ──
    ('body/body_quadrant_fl.stl', 'Body FL', 'body',
     [(0, 0, GROUND_Z, 0, 0, 0)]),
    ('body/body_quadrant_fr.stl', 'Body FR', 'body',
     [(0, 0, GROUND_Z, 0, 0, 0)]),
    ('body/body_quadrant_rl.stl', 'Body RL', 'body',
     [(0, 0, GROUND_Z, 0, 0, 0)]),
    ('body/body_quadrant_rr.stl', 'Body RR', 'body',
     [(0, 0, GROUND_Z, 0, 0, 0)]),

    # ── Top deck tiles ──
    ('body/top_deck_fl.stl', 'Deck FL', 'deck',
     [(0, 0, GROUND_Z + BODY_H, 0, 0, 0)]),
    ('body/top_deck_fr.stl', 'Deck FR', 'deck',
     [(0, 0, GROUND_Z + BODY_H, 0, 0, 0)]),
    ('body/top_deck_rl.stl', 'Deck RL', 'deck',
     [(0, 0, GROUND_Z + BODY_H, 0, 0, 0)]),
    ('body/top_deck_rr.stl', 'Deck RR', 'deck',
     [(0, 0, GROUND_Z + BODY_H, 0, 0, 0)]),

    # ── Wheels (6) — created as revolve around Z, need 90° Y rotation ──
    ('wheels/rover_wheel_v3.stl', 'Wheel FL', 'wheel',
     [(TRACK_HALF + WHEEL_W/2, WB_HALF, WHEEL_Z, 0, 90, 0)]),
    ('wheels/rover_wheel_v3.stl', 'Wheel FR', 'wheel',
     [(-TRACK_HALF - WHEEL_W/2, WB_HALF, WHEEL_Z, 0, -90, 0)]),
    ('wheels/rover_wheel_v3.stl', 'Wheel ML', 'wheel',
     [(TRACK_HALF + WHEEL_W/2, 0, WHEEL_Z, 0, 90, 0)]),
    ('wheels/rover_wheel_v3.stl', 'Wheel MR', 'wheel',
     [(-TRACK_HALF - WHEEL_W/2, 0, WHEEL_Z, 0, -90, 0)]),
    ('wheels/rover_wheel_v3.stl', 'Wheel RL', 'wheel',
     [(TRACK_HALF + WHEEL_W/2, -WB_HALF, WHEEL_Z, 0, 90, 0)]),
    ('wheels/rover_wheel_v3.stl', 'Wheel RR', 'wheel',
     [(-TRACK_HALF - WHEEL_W/2, -WB_HALF, WHEEL_Z, 0, -90, 0)]),

    # ── Suspension connectors — Mars orange ──
    # Rocker hub connectors (on diff bar, one per side)
    ('suspension/rocker_hub_connector.stl', 'Rocker Hub L', 'suspension',
     [(ROCKER_X, 0, DIFF_Z, 0, 0, 0)]),
    ('suspension/rocker_hub_connector.stl', 'Rocker Hub R', 'suspension',
     [(-ROCKER_X, 0, DIFF_Z, 0, 0, 0)]),

    # Bogie pivot connectors (at rocker-bogie junction)
    ('suspension/bogie_pivot_connector.stl', 'Bogie Pivot L', 'suspension',
     [(ROCKER_X, BOGIE_Y, BOGIE_Z, 0, 0, 0)]),
    ('suspension/bogie_pivot_connector.stl', 'Bogie Pivot R', 'suspension',
     [(-ROCKER_X, BOGIE_Y, BOGIE_Z, 0, 0, 0)]),

    # Front wheel connectors (at 4 steered wheel positions)
    ('suspension/front_wheel_connector.stl', 'FW Conn FL', 'suspension',
     [(TRACK_HALF - 2, WB_HALF, WHEEL_Z + 2, 0, 0, 0)]),
    ('suspension/front_wheel_connector.stl', 'FW Conn FR', 'suspension',
     [(-TRACK_HALF + 2, WB_HALF, WHEEL_Z + 2, 0, 0, 0)]),
    ('suspension/front_wheel_connector.stl', 'FW Conn RL', 'suspension',
     [(TRACK_HALF - 2, -WB_HALF, WHEEL_Z + 2, 0, 0, 0)]),
    ('suspension/front_wheel_connector.stl', 'FW Conn RR', 'suspension',
     [(-TRACK_HALF + 2, -WB_HALF, WHEEL_Z + 2, 0, 0, 0)]),

    # Middle wheel connectors
    ('suspension/middle_wheel_connector.stl', 'MW Conn L', 'suspension',
     [(TRACK_HALF - 2, 0, WHEEL_Z + 2, 0, 0, 0)]),
    ('suspension/middle_wheel_connector.stl', 'MW Conn R', 'suspension',
     [(-TRACK_HALF + 2, 0, WHEEL_Z + 2, 0, 0, 0)]),

    # Differential pivot housing (body centre)
    ('suspension/differential_pivot_housing.stl', 'Diff Pivot', 'diffbar',
     [(0, 0, DIFF_Z, 0, 0, 0)]),

    # Cable clips (representative — 4 along each side tube)
    ('suspension/cable_clip.stl', 'Clip L1', 'accessory',
     [(ROCKER_X, 6, DIFF_Z, 0, 0, 0)]),
    ('suspension/cable_clip.stl', 'Clip L2', 'accessory',
     [(ROCKER_X, 12, DIFF_Z, 0, 0, 0)]),
    ('suspension/cable_clip.stl', 'Clip R1', 'accessory',
     [(-ROCKER_X, 6, DIFF_Z, 0, 0, 0)]),
    ('suspension/cable_clip.stl', 'Clip R2', 'accessory',
     [(-ROCKER_X, 12, DIFF_Z, 0, 0, 0)]),

    # ── Steering — sky blue ──
    # Steering brackets (above each steered wheel)
    ('steering/steering_bracket.stl', 'Steer Bracket FL', 'steering',
     [(TRACK_HALF, WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),
    ('steering/steering_bracket.stl', 'Steer Bracket FR', 'steering',
     [(-TRACK_HALF, WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),
    ('steering/steering_bracket.stl', 'Steer Bracket RL', 'steering',
     [(TRACK_HALF, -WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),
    ('steering/steering_bracket.stl', 'Steer Bracket RR', 'steering',
     [(-TRACK_HALF, -WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),

    # Steering knuckles (below brackets, around wheel axle)
    ('steering/steering_knuckle.stl', 'Knuckle FL', 'steering',
     [(TRACK_HALF, WB_HALF, WHEEL_Z, 0, 0, 0)]),
    ('steering/steering_knuckle.stl', 'Knuckle FR', 'steering',
     [(-TRACK_HALF, WB_HALF, WHEEL_Z, 0, 0, 0)]),
    ('steering/steering_knuckle.stl', 'Knuckle RL', 'steering',
     [(TRACK_HALF, -WB_HALF, WHEEL_Z, 0, 0, 0)]),
    ('steering/steering_knuckle.stl', 'Knuckle RR', 'steering',
     [(-TRACK_HALF, -WB_HALF, WHEEL_Z, 0, 0, 0)]),

    # Servo mounts (next to steering brackets)
    ('steering/servo_mount.stl', 'Servo FL', 'steering',
     [(TRACK_HALF - 3, WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),
    ('steering/servo_mount.stl', 'Servo FR', 'steering',
     [(-TRACK_HALF + 3, WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),
    ('steering/servo_mount.stl', 'Servo RL', 'steering',
     [(TRACK_HALF - 3, -WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),
    ('steering/servo_mount.stl', 'Servo RR', 'steering',
     [(-TRACK_HALF + 3, -WB_HALF, WHEEL_Z + 4, 0, 0, 0)]),

    # Steering horn links
    ('steering/steering_horn_link.stl', 'Horn Link FL', 'steering',
     [(TRACK_HALF - 1.5, WB_HALF + 1, WHEEL_Z + 3, 0, 0, 0)]),
    ('steering/steering_horn_link.stl', 'Horn Link FR', 'steering',
     [(-TRACK_HALF + 1.5, WB_HALF + 1, WHEEL_Z + 3, 0, 0, 0)]),
    ('steering/steering_horn_link.stl', 'Horn Link RL', 'steering',
     [(TRACK_HALF - 1.5, -WB_HALF + 1, WHEEL_Z + 3, 0, 0, 0)]),
    ('steering/steering_horn_link.stl', 'Horn Link RR', 'steering',
     [(-TRACK_HALF + 1.5, -WB_HALF + 1, WHEEL_Z + 3, 0, 0, 0)]),

    # ── Drivetrain — teal ──
    # Fixed wheel mounts (middle wheels, no steering)
    ('steering/fixed_wheel_mount.stl', 'Fixed Mount L', 'drivetrain',
     [(TRACK_HALF, 0, WHEEL_Z + 2, 0, 0, 0)]),
    ('steering/fixed_wheel_mount.stl', 'Fixed Mount R', 'drivetrain',
     [(-TRACK_HALF, 0, WHEEL_Z + 2, 0, 0, 0)]),

    # ── Electronics — green ──
    ('body/electronics_tray.stl', 'Electronics Tray', 'electronics',
     [(0, 5, GROUND_Z + 0.3, 0, 0, 0)]),
    ('body/battery_tray.stl', 'Battery Tray', 'electronics',
     [(0, -8, GROUND_Z + 0.3, 0, 0, 0)]),

    # ── Accessories — light grey ──
    ('body/strain_relief_clip.stl', 'Strain Relief 1', 'accessory',
     [(8, 0, GROUND_Z + 0.3, 0, 0, 0)]),
    ('body/strain_relief_clip.stl', 'Strain Relief 2', 'accessory',
     [(-8, 0, GROUND_Z + 0.3, 0, 0, 0)]),
    ('body/fuse_holder_bracket.stl', 'Fuse Holder', 'accessory',
     [(5, -5, GROUND_Z + 0.3, 0, 0, 0)]),
    ('body/switch_mount_plate.stl', 'Switch Mount', 'accessory',
     [(-5, 10, GROUND_Z + BODY_H / 2, 0, 0, 90)]),
]


# ══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def make_transform(x, y, z, rx_deg=0, ry_deg=0, rz_deg=0):
    """Create a Matrix3D with translation and optional rotation (degrees)."""
    transform = adsk.core.Matrix3D.create()

    # Apply rotations (Z, then Y, then X — extrinsic)
    if rz_deg != 0:
        rz = math.radians(rz_deg)
        rot = adsk.core.Matrix3D.create()
        rot.setToRotation(rz, adsk.core.Vector3D.create(0, 0, 1),
                          adsk.core.Point3D.create(0, 0, 0))
        transform.transformBy(rot)

    if ry_deg != 0:
        ry = math.radians(ry_deg)
        rot = adsk.core.Matrix3D.create()
        rot.setToRotation(ry, adsk.core.Vector3D.create(0, 1, 0),
                          adsk.core.Point3D.create(0, 0, 0))
        transform.transformBy(rot)

    if rx_deg != 0:
        rx = math.radians(rx_deg)
        rot = adsk.core.Matrix3D.create()
        rot.setToRotation(rx, adsk.core.Vector3D.create(1, 0, 0),
                          adsk.core.Point3D.create(0, 0, 0))
        transform.transformBy(rot)

    # Apply translation
    trans = transform.translation
    trans.x += x
    trans.y += y
    trans.z += z
    transform.translation = trans

    return transform


def apply_colour(body, rgb):
    """Apply an RGB colour to a body (BRep or Mesh)."""
    r, g, b = rgb
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)

    appear_name = f'Rover_{r}_{g}_{b}'
    appear = None

    # Check if appearance already exists
    for i in range(design.appearances.count):
        if design.appearances.item(i).name == appear_name:
            appear = design.appearances.item(i)
            break

    if appear is None:
        # Find a base plastic appearance from the library
        lib = app.materialLibraries.itemByName('Fusion 360 Appearance Library')
        if lib:
            base = None
            for i in range(lib.appearances.count):
                a = lib.appearances.item(i)
                if 'Plastic' in a.name and 'Matte' in a.name:
                    base = a
                    break
            if base is None and lib.appearances.count > 0:
                base = lib.appearances.item(0)

            if base:
                appear = design.appearances.addByCopy(base, appear_name)
                for prop in appear.appearanceProperties:
                    if isinstance(prop, adsk.core.ColorProperty):
                        prop.value = adsk.core.Color.create(r, g, b, 255)

    if appear:
        body.appearance = appear


def import_stl_to_component(app, comp, stl_path, name):
    """Import an STL file into a component. Returns the mesh body or None."""
    if not os.path.exists(stl_path):
        return None

    importMgr = app.importManager
    stlOpts = importMgr.createSTLImportOptions(stl_path)
    stlOpts.isViewFit = False

    try:
        importMgr.importToTarget(stlOpts, comp)
        # Return the last mesh body added
        if comp.meshBodies.count > 0:
            mesh = comp.meshBodies.item(comp.meshBodies.count - 1)
            mesh.name = name
            return mesh
    except:
        pass

    return None


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('No active design.')
            return

        rootComp = design.rootComponent
        imported = 0
        failed = 0
        failed_names = []

        for stl_sub, base_name, colour_key, positions in PARTS:
            stl_path = os.path.join(STL_ROOT, stl_sub)
            rgb = COLOURS.get(colour_key, (180, 180, 180))

            for i, pos in enumerate(positions):
                x, y, z = pos[0], pos[1], pos[2]
                rx = pos[3] if len(pos) > 3 else 0
                ry = pos[4] if len(pos) > 4 else 0
                rz = pos[5] if len(pos) > 5 else 0

                # Unique name for this instance
                if len(positions) > 1:
                    inst_name = f'{base_name} {i+1}'
                else:
                    inst_name = base_name

                # Create sub-component with transform
                transform = make_transform(x, y, z, rx, ry, rz)
                occ = rootComp.occurrences.addNewComponent(transform)
                comp = occ.component
                comp.name = inst_name

                # Import STL
                mesh = import_stl_to_component(app, comp, stl_path, inst_name)
                if mesh:
                    try:
                        apply_colour(mesh, rgb)
                    except:
                        pass
                    imported += 1
                else:
                    failed += 1
                    failed_names.append(inst_name)

        # ── Add reference geometry: ground plane ──
        try:
            ground_sk = rootComp.sketches.add(rootComp.xYConstructionPlane)
            ground_sk.name = 'Ground Plane'
            # Draw a large rectangle representing ground
            gl = ground_sk.sketchCurves.sketchLines
            gl.addTwoPointRectangle(
                adsk.core.Point3D.create(-25, -25, 0),
                adsk.core.Point3D.create(25, 25, 0)
            )
        except:
            pass

        # ── Add reference geometry: diff bar (8mm steel rod) ──
        try:
            diff_sk = rootComp.sketches.add(rootComp.xYConstructionPlane)
            diff_sk.name = 'Diff Bar Reference'
            # Simple line showing diff bar extent
            dl = diff_sk.sketchCurves.sketchLines
            dl.addByTwoPoints(
                adsk.core.Point3D.create(-15, 0, DIFF_Z),
                adsk.core.Point3D.create(15, 0, DIFF_Z)
            )
        except:
            pass

        # ── Zoom to fit ──
        vp = app.activeViewport
        vp.fit()

        # ── Report ──
        fail_msg = ''
        if failed > 0:
            fail_msg = f'\n\nMissing STLs ({failed}):\n' + '\n'.join(f'  - {n}' for n in failed_names[:10])

        ui.messageBox(
            f'Mars Rover Assembly V2\n'
            f'{"=" * 40}\n\n'
            f'Parts imported: {imported}\n'
            f'Failed: {failed}{fail_msg}\n\n'
            f'COLOUR KEY:\n'
            f'  Warm grey  — Body panels\n'
            f'  Charcoal   — Wheels\n'
            f'  Orange     — Suspension connectors\n'
            f'  Blue       — Steering system\n'
            f'  Teal       — Drivetrain (fixed mounts)\n'
            f'  Green      — Electronics\n'
            f'  Light grey — Accessories\n\n'
            f'Layout: Phase 1, 0.4 scale\n'
            f'Track: {TRACK_HALF*20:.0f}mm | Wheelbase: {WB_HALF*20:.0f}mm\n'
            f'Body: {BODY_L*10:.0f}×{BODY_W*10:.0f}×{BODY_H*10:.0f}mm\n'
            f'Ground clearance: {GROUND_Z*10:.0f}mm',
            'Mars Rover - Assembly V2'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
