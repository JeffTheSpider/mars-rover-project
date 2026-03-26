"""
Mars Rover Phase 1 — Trimesh Assembly with Collision Detection
================================================================

Positions all STL parts using exact bounding box data and exports
a colour-coded GLB file viewable in any 3D viewer.

Collision detection highlights interfering parts.

Usage: python assembly_trimesh.py
Output: D:\Mars Rover Project\temp\rover_assembly.glb

Coordinate system (mm):
  Origin: body centre, ground level (Z=0)
  X: +Right, Y: +Forward, Z: +Up
"""

import trimesh
import numpy as np
import os
import sys

STL_ROOT = r'D:\Mars Rover Project\3d-print'
OUT_DIR = r'D:\Mars Rover Project\temp'

# ══════════════════════════════════════════════════════════════════
# COLOURS (RGBA, 0-255)
# ══════════════════════════════════════════════════════════════════

COLOURS = {
    'body':        [210, 160, 100, 255],   # warm tan/orange
    'deck':        [220, 220, 220, 255],   # light grey
    'wheel':       [60, 60, 60, 255],      # dark charcoal
    'suspension':  [220, 120, 40, 255],    # Mars orange
    'steering':    [80, 160, 220, 255],    # sky blue
    'drivetrain':  [40, 180, 160, 255],    # teal
    'diffbar':     [160, 120, 80, 255],    # bronze
    'electronics': [80, 200, 80, 255],     # green
    'accessory':   [180, 180, 180, 255],   # light grey
}


# ══════════════════════════════════════════════════════════════════
# LAYOUT CONSTANTS (all mm)
# ══════════════════════════════════════════════════════════════════

# Body
BODY_W = 260        # X-axis total
BODY_L = 440        # Y-axis total
BODY_H = 120        # Z-axis total
GROUND_Z = 60       # body bottom

# Wheels
TRACK_HALF = 140    # half track width (wheel centre X)
WB_HALF = 180       # half wheelbase (front/rear Y)
WHEEL_R = 43        # wheel radius from STL (tread outer)

# Suspension pivots
DIFF_Z = 120        # diff bar Z (body mid-height)
ROCKER_X = 125      # rocker pivot X offset
BOGIE_Y = -90       # bogie pivot Y
BOGIE_Z = 55        # bogie pivot Z

# Connector positions (at arm tube ends, near wheels)
CONN_X = 120        # ~20mm inboard of wheel centre
CONN_Z = 60         # at body bottom height


# ══════════════════════════════════════════════════════════════════
# STL BOUNDING BOX DATA (from get_stl_info)
# Format: (min_x, min_y, min_z, max_x, max_y, max_z)
# Used to calculate origin offsets for correct placement
# ══════════════════════════════════════════════════════════════════

STL_BOUNDS = {
    'RoverWheelV3':           (-43, -43, -44, 43, 43, 8),
    'BodyQuadrant':           (-130.5, 0, 0, 0, 225.5, 120),
    'TopDeck':                (-133, 0, -5, 0, 223, 5),
    'RockerHubConnector':     (-22.5, 0, 0, 22.5, 40, 35),
    'BogiePivotConnector':    (-22.3, -15.1, -30, 22.3, 15.1, 15),
    'FrontWheelConnector':    (-17.5, 0, 0, 17.5, 30, 30),
    'MiddleWheelConnector':   (-15, 0, 0, 15, 25, 25),
    'DifferentialPivotHousing': (-15, -15, 0, 15, 15, 23),
    'DifferentialLink':       (-10, -42.5, 0, 10, 42.5, 6),
    'SteeringBracket':        (-17.5, -15, -5, 17.5, 15, 25),
    'SteeringKnuckle':        (-12.5, -15, 0, 26.5, 19.6, 41.5),
    'ServoMount':             (-20, -9, 0, 20, 9, 25),
    'SteeringHornLink':       (-14, -4, 0, 14, 4, 5),
    'FixedWheelMount':        (-12.5, -12.5, 0, 12.5, 12.5, 30),
    'ElectronicsTray':        (-60, -90, 0, 60, 90, 18),
    'BatteryTray':            (-47, -21, 0, 47, 21, 23),
    'CableClip':              (-5.6, -10.1, 0, 5.6, 5.6, 5),
}


def load_stl(subpath):
    """Load an STL file, return trimesh mesh or None."""
    path = os.path.join(STL_ROOT, subpath)
    if not os.path.exists(path):
        print(f'  MISSING: {path}')
        return None
    return trimesh.load(path)


def make_transform(tx, ty, tz, rx_deg=0, ry_deg=0, rz_deg=0):
    """Build a 4x4 transform: rotation (Z,Y,X order) then translation. All in mm."""
    T = np.eye(4)

    if rz_deg:
        rz = np.radians(rz_deg)
        Rz = trimesh.transformations.rotation_matrix(rz, [0, 0, 1])
        T = T @ Rz

    if ry_deg:
        ry = np.radians(ry_deg)
        Ry = trimesh.transformations.rotation_matrix(ry, [0, 1, 0])
        T = T @ Ry

    if rx_deg:
        rx = np.radians(rx_deg)
        Rx = trimesh.transformations.rotation_matrix(rx, [1, 0, 0])
        T = T @ Rx

    T[0, 3] = tx
    T[1, 3] = ty
    T[2, 3] = tz
    return T


def colour_mesh(mesh, rgba):
    """Apply a solid colour to a mesh."""
    mesh.visual = trimesh.visual.ColorVisuals(
        mesh=mesh,
        face_colors=np.tile(rgba, (len(mesh.faces), 1))
    )
    return mesh


# ══════════════════════════════════════════════════════════════════
# PART DEFINITIONS
# ══════════════════════════════════════════════════════════════════
#
# Each entry: (stl_subpath, name, colour_key, x, y, z, rx, ry, rz)
# Positions in mm. Rotations in degrees.
#
# STL ORIGIN NOTES (from bounding box analysis):
#   Wheel: axle at XY origin, hub face Z=0, tread extends Z=-44
#          After +90°Y: hub→+X (inboard), tread→-X (outboard) → LEFT wheels
#          After -90°Y: hub→-X (inboard), tread→+X (outboard) → RIGHT wheels
#   BodyQuadrant: seam corner at origin (X=0, Y=0), extends -X, +Y
#   Connectors (FWC, MWC, RockerHub): X-centred, front/bottom at Y=0,Z=0
#          Need Y-rotation to face the right direction for each position
#   SteeringBracket: XY-centred, base 5mm below Z=0
#   SteeringKnuckle: kingpin near X=0, base Z=0, arm extends +X
#   Most other parts: XY-centred, base at Z=0

def build_parts_list():
    """Return list of (subpath, name, colour_key, transform_4x4)."""
    parts = []

    def add(subpath, name, colour, tx, ty, tz, rx=0, ry=0, rz=0):
        T = make_transform(tx, ty, tz, rx, ry, rz)
        parts.append((subpath, name, colour, T))

    # ── BODY (4 quadrants) ──
    # FL: as-is at origin (extends -X, +Y from seam corner)
    add('body/BodyQuadrant.stl', 'Body FL', 'body', 0, 0, GROUND_Z)
    # FR: shift +X by quadrant width (130.5mm)
    add('body/BodyQuadrant.stl', 'Body FR', 'body', 130.5, 0, GROUND_Z)
    # RL: shift -Y by quadrant length (225.5mm)
    add('body/BodyQuadrant.stl', 'Body RL', 'body', 0, -225.5, GROUND_Z)
    # RR: 180° Z rotation only (maps -X,+Y to +X,-Y — correct diagonal)
    add('body/BodyQuadrant.stl', 'Body RR', 'body', 0, 0, GROUND_Z, rz=180)

    # ── TOP DECK (4 tiles) ──
    DECK_Z = GROUND_Z + BODY_H + 5  # deck sits on top, Z-centred at ±5mm
    add('body/TopDeck.stl', 'Deck FL', 'deck', 0, 0, DECK_Z)
    add('body/TopDeck.stl', 'Deck FR', 'deck', 133, 0, DECK_Z)
    add('body/TopDeck.stl', 'Deck RL', 'deck', 0, -223, DECK_Z)
    add('body/TopDeck.stl', 'Deck RR', 'deck', 0, 0, DECK_Z, rz=180)

    # ── WHEELS (6) ──
    # Wheel STL: axle at origin, hub face Z=0, tread Z=-44
    # +90°Y → tread faces -X (outboard for LEFT wheels)
    # -90°Y → tread faces +X (outboard for RIGHT wheels)
    WZ = WHEEL_R  # wheel centre Z = radius, sitting on ground

    add('wheels/RoverWheelV3.stl', 'Wheel FL', 'wheel',
        -TRACK_HALF, WB_HALF, WZ, ry=90)
    add('wheels/RoverWheelV3.stl', 'Wheel FR', 'wheel',
        TRACK_HALF, WB_HALF, WZ, ry=-90)
    add('wheels/RoverWheelV3.stl', 'Wheel ML', 'wheel',
        -TRACK_HALF, 0, WZ, ry=90)
    add('wheels/RoverWheelV3.stl', 'Wheel MR', 'wheel',
        TRACK_HALF, 0, WZ, ry=-90)
    add('wheels/RoverWheelV3.stl', 'Wheel RL', 'wheel',
        -TRACK_HALF, -WB_HALF, WZ, ry=90)
    add('wheels/RoverWheelV3.stl', 'Wheel RR', 'wheel',
        TRACK_HALF, -WB_HALF, WZ, ry=-90)

    # ── SUSPENSION CONNECTORS ──

    # Rocker hub connectors — on diff bar at body mid-height
    # STL: X-centred, front at Y=0, base at Z=0. Part extends +Y, +Z.
    # Need to centre vertically on diff bar: shift Z down by half height (35/2=17.5)
    RH_Z_OFF = -17.5  # centre on diff bar
    add('suspension/RockerHubConnector.stl', 'Rocker Hub L', 'suspension',
        -ROCKER_X, 0, DIFF_Z + RH_Z_OFF)
    add('suspension/RockerHubConnector.stl', 'Rocker Hub R', 'suspension',
        ROCKER_X, 0, DIFF_Z + RH_Z_OFF)

    # Bogie pivot connectors — at rocker-bogie junction
    # STL: XY-centred on pivot bore, Z offset (pivot at Z=0)
    add('suspension/BogiePivotConnector.stl', 'Bogie Pivot L', 'suspension',
        -ROCKER_X, BOGIE_Y, BOGIE_Z)
    add('suspension/BogiePivotConnector.stl', 'Bogie Pivot R', 'suspension',
        ROCKER_X, BOGIE_Y, BOGIE_Z)

    # Front wheel connectors — at steered wheel positions
    # STL: X-centred, front at Y=0, base at Z=0. Extends +Y, +Z.
    # Centre on connector position: shift Y by -half_depth, Z by -half_height
    FWC_Y_OFF = -15   # centre Y (30mm deep / 2)
    FWC_Z_OFF = -15   # centre Z (30mm tall / 2)
    for name_sfx, sign_x, y_pos in [('FL', -1, WB_HALF), ('FR', 1, WB_HALF),
                                      ('RL', -1, -WB_HALF), ('RR', 1, -WB_HALF)]:
        add('suspension/FrontWheelConnector.stl', f'FW Conn {name_sfx}', 'suspension',
            sign_x * CONN_X, y_pos + FWC_Y_OFF, CONN_Z + FWC_Z_OFF)

    # Middle wheel connectors
    MWC_Y_OFF = -12.5  # centre Y (25mm / 2)
    MWC_Z_OFF = -12.5  # centre Z (25mm / 2)
    add('suspension/MiddleWheelConnector.stl', 'MW Conn L', 'suspension',
        -CONN_X, MWC_Y_OFF, CONN_Z + MWC_Z_OFF)
    add('suspension/MiddleWheelConnector.stl', 'MW Conn R', 'suspension',
        CONN_X, MWC_Y_OFF, CONN_Z + MWC_Z_OFF)

    # Differential pivot housing — body centre
    # STL: XY-centred, base at Z=0
    add('suspension/DifferentialPivotHousing.stl', 'Diff Pivot', 'diffbar',
        0, 0, DIFF_Z - 11.5)  # centre on diff bar

    # Differential links
    add('suspension/DifferentialLink.stl', 'Diff Link L', 'diffbar',
        -ROCKER_X / 2, 0, DIFF_Z - 3)
    add('suspension/DifferentialLink.stl', 'Diff Link R', 'diffbar',
        ROCKER_X / 2, 0, DIFF_Z - 3)

    # Cable clips (representative positions along front arm tubes)
    add('suspension/CableClip.stl', 'Clip L1', 'accessory',
        -ROCKER_X, 60, 100)
    add('suspension/CableClip.stl', 'Clip L2', 'accessory',
        -ROCKER_X, 120, 80)
    add('suspension/CableClip.stl', 'Clip R1', 'accessory',
        ROCKER_X, 60, 100)
    add('suspension/CableClip.stl', 'Clip R2', 'accessory',
        ROCKER_X, 120, 80)

    # ── STEERING (at each steered wheel) ──

    for name_sfx, sign_x, y_pos in [('FL', -1, WB_HALF), ('FR', 1, WB_HALF),
                                      ('RL', -1, -WB_HALF), ('RR', 1, -WB_HALF)]:
        cx = sign_x * CONN_X

        # Steering bracket — bolts to FW connector front face
        # STL: XY-centred, base 5mm below Z=0
        add('steering/SteeringBracket.stl', f'Steer Bracket {name_sfx}', 'steering',
            cx, y_pos, CONN_Z - 10)

        # Steering knuckle — hangs below bracket on pivot shaft
        # STL: kingpin near X=0, base Z=0, extends +Z (41.5mm)
        # Place below bracket, pivot shaft connects them
        add('steering/SteeringKnuckle.stl', f'Knuckle {name_sfx}', 'steering',
            cx, y_pos, CONN_Z - 45)

        # Servo mount — on FW connector side face, offset toward body
        # STL: XY-centred, base Z=0
        servo_x = cx + sign_x * (-20)  # 20mm toward body centre
        add('steering/ServoMount.stl', f'Servo {name_sfx}', 'steering',
            servo_x, y_pos, CONN_Z - 10)

        # Horn link — between servo and knuckle arm
        # STL: XY-centred, base Z=0
        link_x = cx + sign_x * (-10)  # between servo and pivot
        add('steering/SteeringHornLink.stl', f'Horn Link {name_sfx}', 'steering',
            link_x, y_pos + 2, CONN_Z - 5)

    # ── DRIVETRAIN (middle wheels) ──
    # Fixed wheel mount: XY-centred, base Z=0
    add('drivetrain/FixedWheelMount.stl', 'Fixed Mount L', 'drivetrain',
        -CONN_X, 0, CONN_Z - 15)
    add('drivetrain/FixedWheelMount.stl', 'Fixed Mount R', 'drivetrain',
        CONN_X, 0, CONN_Z - 15)

    # ── ELECTRONICS (inside body) ──
    add('body/ElectronicsTray.stl', 'Electronics Tray', 'electronics',
        0, 50, GROUND_Z + 3)
    add('body/BatteryTray.stl', 'Battery Tray', 'electronics',
        0, -80, GROUND_Z + 3)

    # ── ACCESSORIES ──
    add('body/StrainReliefClip.stl', 'Strain Relief L', 'accessory',
        -ROCKER_X, 0, DIFF_Z)
    add('body/StrainReliefClip.stl', 'Strain Relief R', 'accessory',
        ROCKER_X, 0, DIFF_Z)
    add('body/FuseHolderBracket.stl', 'Fuse Holder', 'accessory',
        50, -50, GROUND_Z + 3)
    add('body/SwitchMount.stl', 'Switch Mount', 'accessory',
        -130, 100, DIFF_Z)

    return parts


def main():
    print('Mars Rover Phase 1 — Trimesh Assembly Builder')
    print('=' * 50)

    parts = build_parts_list()
    scene = trimesh.Scene()
    loaded = 0
    failed = 0
    failed_names = []

    for subpath, name, colour_key, transform in parts:
        mesh = load_stl(subpath)
        if mesh is None:
            failed += 1
            failed_names.append(name)
            continue

        rgba = COLOURS.get(colour_key, [180, 180, 180, 255])
        colour_mesh(mesh, rgba)
        scene.add_geometry(mesh, node_name=name, transform=transform)
        loaded += 1

    print(f'\nLoaded: {loaded} parts')
    if failed:
        print(f'Failed: {failed} parts: {", ".join(failed_names)}')

    # ── Collision detection ──
    print('\n--- Collision Detection ---')
    try:
        manager = trimesh.collision.CollisionManager()
        for subpath, name, colour_key, transform in parts:
            mesh = load_stl(subpath)
            if mesh is not None:
                manager.add_object(name, mesh, transform=transform)

        is_collision, pairs = manager.in_collision_internal(return_names=True)
        if is_collision:
            print(f'Found {len(pairs)} colliding pairs:')
            for a, b in sorted(pairs):
                print(f'  {a} <-> {b}')
        else:
            print('No collisions detected!')
    except Exception as e:
        print(f'Collision detection unavailable: {e}')
        print('(Install python-fcl for collision support: pip install python-fcl)')

    # ── Export ──
    os.makedirs(OUT_DIR, exist_ok=True)
    glb_path = os.path.join(OUT_DIR, 'rover_assembly.glb')
    scene.export(glb_path)
    print(f'\nExported: {glb_path}')
    print('Open in Windows 3D Viewer, VS Code, or https://gltf-viewer.donmccurdy.com/')

    # Also export a combined STL for quick slicer preview
    combined_path = os.path.join(OUT_DIR, 'rover_assembly_combined.stl')
    try:
        meshes = []
        for subpath, name, colour_key, transform in parts:
            mesh = load_stl(subpath)
            if mesh is not None:
                meshes.append(mesh.apply_transform(transform))
        combined = trimesh.util.concatenate(meshes)
        combined.export(combined_path)
        print(f'Combined STL: {combined_path}')
    except Exception as e:
        print(f'Combined STL export failed: {e}')

    return scene


if __name__ == '__main__':
    main()
