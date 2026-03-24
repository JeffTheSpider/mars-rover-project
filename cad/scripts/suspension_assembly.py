"""
Mars Rover Suspension Assembly — Tube + Connector (EA-25)
==========================================================

Imports connector STLs and generates steel rod cylinders to visualise
the complete rocker-bogie suspension.  Uses the EA-25 tube + connector
design that replaced the earlier monolithic arm approach.

Builds: Differential bar + Left side + Right side (mirrored)

Parts per side (connector STLs + steel rod cylinders):
  Connectors:
    1x Rocker hub connector   (clamped to diff bar)
    1x Bogie pivot connector  (608ZZ bearing, 3 tube sockets)
    2x Front wheel connector  (front + rear, tube socket + steering mount)
    1x Middle wheel connector (tube socket + fixed mount)
  Steering & Mounts:
    2x Steering bracket       (front + rear corners)
    2x Servo mount            (front + rear corners)
    1x Fixed wheel mount      (middle wheel)
  Wheels:
    3x Wheel V3               (front, middle, rear)
  Steel Rods (generated as cylinders):
    1x Rocker front tube (150mm, hub -> front wheel)
    1x Rocker rear tube  (60mm, hub -> bogie pivot)
    1x Bogie front tube  (60mm, pivot -> middle wheel)
    1x Bogie rear tube   (60mm, pivot -> rear wheel)
  Clips:
    3x Cable clip             (on rod midpoints)

Shared:
  1x Differential bar (300mm x 8mm rod)

Total: 20 parts x 2 sides + 1 diff bar = 41 components

Coordinate System (rover standard):
  Origin = centre of differential bar, mid-length, mid-width, ground Z=0
  X = left(-) / right(+)     (track width direction)
  Y = rear(-) / front(+)     (wheelbase direction)
  Z = up(+)                  (vertical)

ALL Fusion 360 API values in CENTIMETERS (mm / 10).

Instructions:
  1. Open Fusion 360 -> File -> New Design
  2. Ensure STLs exist (run BatchExportAll first)
  3. Shift+S -> search "SuspensionAssembly" -> Run
  4. Wait ~60s for STL imports + tube generation
  5. Use orbit/pan to inspect assembly

Reference: EA-01, EA-08, EA-20, EA-25
"""

import adsk.core
import adsk.fusion
import traceback
import math
import os


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('No active design. Create a new design first.',
                          'Suspension Assembly')
            return

        # ==============================================================
        # STL FILE PATHS (EA-25 tube + connector parts)
        # ==============================================================
        BASE = r'D:\Mars Rover Project\3d-print'
        STL = {
            'rocker_hub':   os.path.join(BASE, 'suspension', 'rocker_hub_connector.stl'),
            'bogie_pivot':  os.path.join(BASE, 'suspension', 'bogie_pivot_connector.stl'),
            'front_conn':   os.path.join(BASE, 'suspension', 'front_wheel_connector.stl'),
            'middle_conn':  os.path.join(BASE, 'suspension', 'middle_wheel_connector.stl'),
            'cable_clip':   os.path.join(BASE, 'suspension', 'cable_clip.stl'),
            'steering':     os.path.join(BASE, 'steering', 'steering_bracket.stl'),
            'servo_mount':  os.path.join(BASE, 'steering', 'servo_mount.stl'),
            'fixed_mount':  os.path.join(BASE, 'steering', 'fixed_wheel_mount.stl'),
            'wheel':        os.path.join(BASE, 'wheels', 'rover_wheel_v3.stl'),
        }

        # Track which STLs are available (don't abort on missing — just skip)
        available = {k for k, v in STL.items() if os.path.exists(v)}
        missing = [k for k in STL if k not in available]
        skipped = []  # filled during build

        # ==============================================================
        # ASSEMBLY GEOMETRY (all mm, converted to cm for API)
        # ==============================================================
        TRACK_HALF   = 140.0    # half track width (wheel centre X)
        WB_HALF      = 180.0    # half wheelbase (front wheel Y)
        GND_CLR      = 60.0     # body bottom / diff bar Z
        WHEEL_Z      = 40.0     # wheel centre Z (= wheel radius)
        ROCKER_PIV_X = 125.0    # rocker pivot X (diff bar clamp point)
        ROCKER_PIV_Z = 60.0     # rocker pivot Z (at body bottom)
        BOGIE_PIV_Y  = -90.0    # bogie pivot Y (on rocker rear)
        BOGIE_PIV_Z  = 45.0     # bogie pivot Z
        ROD_RADIUS   = 4.0      # 8mm diameter steel rod

        # ----------------------------------------------------------
        # Node positions (x, y, z) in mm
        # Left side: X negative.  Right side: X positive.
        # ----------------------------------------------------------
        HUB_L   = (-ROCKER_PIV_X,  0,          ROCKER_PIV_Z)
        FRONT_L = (-TRACK_HALF,     WB_HALF,    WHEEL_Z)
        BOGIE_L = (-TRACK_HALF,     BOGIE_PIV_Y, BOGIE_PIV_Z)
        MID_L   = (-TRACK_HALF,     0,           WHEEL_Z)
        REAR_L  = (-TRACK_HALF,    -WB_HALF,    WHEEL_Z)

        HUB_R   = ( ROCKER_PIV_X,  0,          ROCKER_PIV_Z)
        FRONT_R = ( TRACK_HALF,     WB_HALF,    WHEEL_Z)
        BOGIE_R = ( TRACK_HALF,     BOGIE_PIV_Y, BOGIE_PIV_Z)
        MID_R   = ( TRACK_HALF,     0,           WHEEL_Z)
        REAR_R  = ( TRACK_HALF,    -WB_HALF,    WHEEL_Z)

        # ==============================================================
        # HELPER FUNCTIONS
        # ==============================================================
        root = design.rootComponent
        import_mgr = app.importManager

        def mm(val):
            """Convert mm to cm for Fusion API."""
            return val / 10.0

        def import_stl(parent_comp, stl_key, comp_name):
            """Import STL into a new sub-component. Returns occurrence,
            or None if the STL file is missing (skips gracefully)."""
            if stl_key not in available:
                skipped.append(comp_name)
                return None
            stl_path = STL[stl_key]
            occ = parent_comp.occurrences.addNewComponent(
                adsk.core.Matrix3D.create())
            occ.component.name = comp_name

            # Try STL-specific import, then mesh import (API varies by version)
            opts = None
            for method in ['createSTLImportOptions', 'createMeshImportOptions']:
                if hasattr(import_mgr, method):
                    opts = getattr(import_mgr, method)(stl_path)
                    break
            if opts is None:
                skipped.append(f'{comp_name} (no import method)')
                return occ  # empty component as placeholder

            # Set units to mm if the property exists
            try:
                opts.units = adsk.fusion.MeshUnits.MillimeterMeshUnit
            except (AttributeError, RuntimeError):
                pass  # STLImportOptions may not have units property

            import_mgr.importToTarget(opts, occ.component)
            return occ

        def transform_occurrence(occ, tx=0, ty=0, tz=0,
                                 rx=0, ry=0, rz=0, mirror_x=False):
            """Apply translation + rotation to an occurrence.
            tx/ty/tz in mm.  rx/ry/rz in degrees."""
            xform = adsk.core.Matrix3D.create()
            for angle, axis in [(rx, (1, 0, 0)),
                                (ry, (0, 1, 0)),
                                (rz, (0, 0, 1))]:
                if angle != 0:
                    rot = adsk.core.Matrix3D.create()
                    rot.setToRotation(
                        math.radians(angle),
                        adsk.core.Vector3D.create(*axis),
                        adsk.core.Point3D.create(0, 0, 0))
                    xform.transformBy(rot)
            if mirror_x:
                m = adsk.core.Matrix3D.create()
                m.setWithArray([
                    -1, 0, 0, 0,
                     0, 1, 0, 0,
                     0, 0, 1, 0,
                     0, 0, 0, 1])
                xform.transformBy(m)
            trans = xform.translation
            trans.x += mm(tx)
            trans.y += mm(ty)
            trans.z += mm(tz)
            xform.translation = trans
            occ.transform = xform

        def create_tube(parent_comp, name, start, end, radius=ROD_RADIUS):
            """Create an 8mm steel-rod cylinder between two 3D points.
            start/end: (x, y, z) tuples in mm.  Returns the occurrence."""
            occ = parent_comp.occurrences.addNewComponent(
                adsk.core.Matrix3D.create())
            tube_comp = occ.component
            tube_comp.name = name

            tmp = adsk.fusion.TemporaryBRepManager.get()
            p1 = adsk.core.Point3D.create(
                mm(start[0]), mm(start[1]), mm(start[2]))
            p2 = adsk.core.Point3D.create(
                mm(end[0]), mm(end[1]), mm(end[2]))
            cyl = tmp.createCylinderOrCone(p1, mm(radius), p2, mm(radius))

            # Handle both parametric and direct design modes
            if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
                bf = tube_comp.features.baseFeatures.add()
                bf.startEdit()
                body = tube_comp.bRepBodies.add(cyl, bf)
                bf.finishEdit()
            else:
                body = tube_comp.bRepBodies.add(cyl)
            body.name = f'{name}_Rod'
            return occ

        def midpt(a, b):
            """Midpoint of two (x,y,z) tuples."""
            return ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2)

        # ----------------------------------------------------------
        def place(parent_comp, stl_key, comp_name, **kwargs):
            """Import STL + transform in one call. Skips if STL missing."""
            occ = import_stl(parent_comp, stl_key, comp_name)
            if occ:
                transform_occurrence(occ, **kwargs)

        def build_side(parent_comp, s, hub, front, bogie, mid, rear):
            """Build one side of the suspension.
            s: 'L' or 'R'.  Positions are (x,y,z) in mm."""

            # --- Rocker Hub Connector (clamped to diff bar) ---
            place(parent_comp, 'rocker_hub', f'RockerHub_{s}',
                  tx=hub[0], ty=hub[1], tz=hub[2])

            # --- Steel rod tubes (4 per side, always generated) ---
            create_tube(parent_comp, f'RockerFrontTube_{s}', hub, front)
            create_tube(parent_comp, f'RockerRearTube_{s}',  hub, bogie)
            create_tube(parent_comp, f'BogieFrontTube_{s}',  bogie, mid)
            create_tube(parent_comp, f'BogieRearTube_{s}',   bogie, rear)

            # --- Bogie Pivot Connector (608ZZ bearing, 3 tube sockets) ---
            place(parent_comp, 'bogie_pivot', f'BogiePivot_{s}',
                  tx=bogie[0], ty=bogie[1], tz=bogie[2])

            # --- Front Wheel Connector (also used at rear — both steer) ---
            place(parent_comp, 'front_conn', f'WheelConn_F{s}',
                  tx=front[0], ty=front[1], tz=front[2])
            place(parent_comp, 'front_conn', f'WheelConn_R{s}',
                  tx=rear[0], ty=rear[1], tz=rear[2], rz=180)

            # --- Middle Wheel Connector (fixed, no steering) ---
            place(parent_comp, 'middle_conn', f'WheelConn_M{s}',
                  tx=mid[0], ty=mid[1], tz=mid[2])

            # --- Steering Brackets (front + rear steered wheels) ---
            place(parent_comp, 'steering', f'SteerBracket_F{s}',
                  tx=front[0], ty=front[1], tz=front[2] - 5)
            place(parent_comp, 'steering', f'SteerBracket_R{s}',
                  tx=rear[0], ty=rear[1], tz=rear[2] - 5)

            # --- Servo Mounts (front + rear, offset 30mm inboard on Y) ---
            place(parent_comp, 'servo_mount', f'ServoMount_F{s}',
                  tx=front[0], ty=front[1] - 30, tz=front[2])
            place(parent_comp, 'servo_mount', f'ServoMount_R{s}',
                  tx=rear[0], ty=rear[1] + 30, tz=rear[2])

            # --- Fixed Wheel Mount (middle wheel, no servo) ---
            place(parent_comp, 'fixed_mount', f'FixedMount_M{s}',
                  tx=mid[0], ty=mid[1], tz=mid[2])

            # --- Wheels V3 (3x per side) ---
            w_rot = 90 if s == 'L' else -90
            for tag, pos in [('F', front), ('M', mid), ('R', rear)]:
                place(parent_comp, 'wheel', f'Wheel_{tag}{s}',
                      tx=pos[0], ty=pos[1], tz=pos[2], ry=w_rot)

            # --- Cable Clips (3x on longest tube midpoints) ---
            for clip_name, cpos in [
                (f'CableClip_{s}_RkrFront', midpt(hub, front)),
                (f'CableClip_{s}_RkrRear',  midpt(hub, bogie)),
                (f'CableClip_{s}_BogRear',  midpt(bogie, rear)),
            ]:
                place(parent_comp, 'cable_clip', clip_name,
                      tx=cpos[0], ty=cpos[1], tz=cpos[2])

        # ==============================================================
        # BUILD THE ASSEMBLY
        # ==============================================================

        # --- Differential Bar (shared, spans X = -150 to +150) ---
        diff_occ = root.occurrences.addNewComponent(
            adsk.core.Matrix3D.create())
        diff_occ.component.name = 'DifferentialBar'
        create_tube(diff_occ.component, 'DiffBarRod',
                    (-150, 0, GND_CLR), (150, 0, GND_CLR))

        # --- Left Suspension ---
        left_occ = root.occurrences.addNewComponent(
            adsk.core.Matrix3D.create())
        left_occ.component.name = 'Suspension_Left'
        build_side(left_occ.component, 'L',
                   HUB_L, FRONT_L, BOGIE_L, MID_L, REAR_L)

        # --- Right Suspension (mirror of left) ---
        right_occ = root.occurrences.addNewComponent(
            adsk.core.Matrix3D.create())
        right_occ.component.name = 'Suspension_Right'
        build_side(right_occ.component, 'R',
                   HUB_R, FRONT_R, BOGIE_R, MID_R, REAR_R)

        # ==============================================================
        # ZOOM TO FIT AND REPORT
        # ==============================================================
        app.activeViewport.fit()

        part_count = 0
        for _ in root.allOccurrences:
            part_count += 1

        skip_msg = ''
        if skipped:
            skip_msg = (f'\nSkipped ({len(skipped)} missing STLs):\n  ' +
                        '\n  '.join(skipped[:12]))
            if len(skipped) > 12:
                skip_msg += f'\n  ... and {len(skipped)-12} more'
            skip_msg += ('\n\nRun BatchExportAll in Fusion 360 to '
                         'generate the STL files, then re-run this script.')

        stl_count = len(available)
        ui.messageBox(
            'Suspension Assembly created!\n\n'
            f'Components placed: {part_count}\n'
            f'STL types found: {stl_count}/{len(STL)}\n\n'
            'Structure (EA-25 tube + connector):\n'
            '  DifferentialBar/ (300mm x 8mm rod)\n'
            '  Suspension_Left/\n'
            '    Hub + 4 tubes + bogie pivot\n'
            '    3 wheel connectors + steering + servos\n'
            '    3 wheels + 3 cable clips\n'
            '  Suspension_Right/ (mirror)\n'
            f'{skip_msg}\n\n'
            'Reference: EA-25 Suspension Audit',
            'Mars Rover Suspension Assembly (EA-25)')

    except:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}',
                          'Suspension Assembly Error')
