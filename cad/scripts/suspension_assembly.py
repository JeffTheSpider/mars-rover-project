"""
Mars Rover Suspension Assembly — Full EA-26 Architecture
==========================================================

Pure-geometry visualisation of the complete rocker-bogie suspension
including the DIFFERENTIAL LINKAGE (bar + ball-joint links) that
was missing from earlier versions.

Generates all parts as primitive solids (cylinders, spheres, boxes)
so it runs immediately with NO STL dependencies. This serves as the
master spatial reference for the suspension system.

Component count per side:
  Rocker arm (tube):           1  (hub → front wheel)
  Rocker arm (tube):           1  (hub → bogie pivot)
  Bogie arm (tube):            1  (bogie → middle wheel)
  Bogie arm (tube):            1  (bogie → rear wheel)
  Rocker hub connector:        1  (simplified box at diff bar)
  Bogie pivot connector:       1  (simplified box with bearing)
  Front wheel connector:       1
  Rear wheel connector:        1
  Middle wheel connector:      1
  Wheel + tyre (cylinder):     3
  Motor envelope (box):        3
  Steering knuckle (box):      2  (front + rear, steered)
  Servo envelope (box):        2  (front + rear)
  Diff link:                   1  (rod with ball joints)
  Ball joints (spheres):       2  (one per link end)

Shared:
  Differential bar:            1  (tube, pivots about X-axis)
  Differential pivot:          1  (sphere at centre)

Total: ~25 parts x 2 sides + 3 shared = ~53 components

Coordinate System:
  Origin = differential pivot centre
  X = left(-) / right(+)     (track width)
  Y = rear(-) / front(+)     (wheelbase)
  Z = up(+)                  (vertical, ground = 0)

ALL Fusion 360 API values in CENTIMETERS (mm / 10).

Reference: EA-26 Suspension & Wheel System Design Package
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
        # GEOMETRY CONSTANTS (all mm, from EA-26 + EA-08)
        # ==============================================================

        # --- Wheel & terrain ---
        WHEEL_DIA    = 80.0     # 0.4x scale wheel diameter
        WHEEL_R      = WHEEL_DIA / 2.0
        WHEEL_WIDTH  = 35.0     # tyre width
        TYRE_THICK   = 3.0      # tyre over rim

        # --- Layout (rover coordinate frame) ---
        TRACK_HALF   = 140.0    # wheel centre X from centreline
        WB_HALF      = 180.0    # front/rear wheel Y from centre
        GND_CLR      = 60.0     # belly clearance (body bottom Z)
        WHEEL_Z      = WHEEL_R  # wheel centre Z (sitting on ground)

        # --- Rocker geometry ---
        ROCKER_PIV_X = 125.0    # rocker pivot X (on body sides)
        ROCKER_PIV_Z = 60.0     # rocker pivot Z (at body bottom)

        # --- Bogie geometry ---
        BOGIE_PIV_Y  = -90.0    # bogie pivot Y (behind body centre)
        BOGIE_PIV_Z  = 45.0     # bogie pivot Z

        # --- Differential geometry (NEW in EA-26) ---
        DIFF_PIV_Z   = 80.0     # diff pivot Z (above body, on top deck)
        DIFF_BAR_LEN = 200.0    # diff bar half-length (extends ±100mm from pivot)
        DIFF_LINK_BAR_R = 30.0  # link attachment offset on bar (from pivot, along Z)
        DIFF_LINK_RKR_R = 30.0  # link attachment offset on rocker (from pivot, along Z)

        # --- Steel rod ---
        ROD_R        = 4.0      # 8mm diameter rod
        BALL_R       = 5.0      # ball joint sphere radius (visual)
        CONN_SIZE    = 20.0     # connector block half-size (visual)

        # --- Motor envelope ---
        MOTOR_L      = 25.0     # N20 gearbox length
        MOTOR_W      = 12.0     # N20 width
        MOTOR_H      = 10.0     # N20 height

        # ==============================================================
        # KEY POSITIONS (mm)
        # ==============================================================
        # Left side
        HUB_L    = (-ROCKER_PIV_X,  0,           ROCKER_PIV_Z)
        FRONT_L  = (-TRACK_HALF,    WB_HALF,     WHEEL_Z)
        BOGIE_L  = (-TRACK_HALF,    BOGIE_PIV_Y, BOGIE_PIV_Z)
        MID_L    = (-TRACK_HALF,    0,            WHEEL_Z)
        REAR_L   = (-TRACK_HALF,   -WB_HALF,     WHEEL_Z)

        # Right side (mirror X)
        HUB_R    = ( ROCKER_PIV_X,  0,           ROCKER_PIV_Z)
        FRONT_R  = ( TRACK_HALF,    WB_HALF,     WHEEL_Z)
        BOGIE_R  = ( TRACK_HALF,    BOGIE_PIV_Y, BOGIE_PIV_Z)
        MID_R    = ( TRACK_HALF,    0,            WHEEL_Z)
        REAR_R   = ( TRACK_HALF,   -WB_HALF,     WHEEL_Z)

        # Differential (shared)
        DIFF_PIV = (0, 0, DIFF_PIV_Z)
        DIFF_BAR_L = (-DIFF_BAR_LEN, 0, DIFF_PIV_Z)  # bar left end
        DIFF_BAR_R = ( DIFF_BAR_LEN, 0, DIFF_PIV_Z)  # bar right end

        # Differential link endpoints
        # Bar end: offset below bar end by DIFF_LINK_BAR_R
        LINK_BAR_L = (-DIFF_BAR_LEN, 0, DIFF_PIV_Z - DIFF_LINK_BAR_R)
        LINK_BAR_R = ( DIFF_BAR_LEN, 0, DIFF_PIV_Z - DIFF_LINK_BAR_R)
        # Rocker end: offset above rocker pivot by DIFF_LINK_RKR_R
        LINK_RKR_L = (-ROCKER_PIV_X, 0, ROCKER_PIV_Z + DIFF_LINK_RKR_R)
        LINK_RKR_R = ( ROCKER_PIV_X, 0, ROCKER_PIV_Z + DIFF_LINK_RKR_R)

        # ==============================================================
        # HELPER FUNCTIONS
        # ==============================================================
        root = design.rootComponent

        def mm(val):
            """Convert mm to cm for Fusion API."""
            return val / 10.0

        def create_tube(comp, name, start, end, radius=ROD_R):
            """Create a steel rod cylinder between two 3D points.
            All coordinates in mm."""
            tmp = adsk.fusion.TemporaryBRepManager.get()
            p1 = adsk.core.Point3D.create(mm(start[0]), mm(start[1]), mm(start[2]))
            p2 = adsk.core.Point3D.create(mm(end[0]), mm(end[1]), mm(end[2]))
            cyl = tmp.createCylinderOrCone(p1, mm(radius), p2, mm(radius))
            if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
                bf = comp.features.baseFeatures.add()
                bf.startEdit()
                body = comp.bRepBodies.add(cyl, bf)
                bf.finishEdit()
            else:
                body = comp.bRepBodies.add(cyl)
            body.name = name
            return body

        def create_sphere(comp, name, centre, radius=BALL_R):
            """Create a sphere (for ball joints). Centre in mm."""
            tmp = adsk.fusion.TemporaryBRepManager.get()
            c = adsk.core.Point3D.create(mm(centre[0]), mm(centre[1]), mm(centre[2]))
            sph = tmp.createSphere(c, mm(radius))
            if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
                bf = comp.features.baseFeatures.add()
                bf.startEdit()
                body = comp.bRepBodies.add(sph, bf)
                bf.finishEdit()
            else:
                body = comp.bRepBodies.add(sph)
            body.name = name
            return body

        def create_box(comp, name, centre, sx, sy, sz):
            """Create a box centred at given point. Dimensions in mm."""
            tmp = adsk.fusion.TemporaryBRepManager.get()
            orient = adsk.core.OrientedBoundingBox3D.create(
                adsk.core.Point3D.create(mm(centre[0]), mm(centre[1]), mm(centre[2])),
                adsk.core.Vector3D.create(1, 0, 0),
                adsk.core.Vector3D.create(0, 1, 0),
                mm(sx), mm(sy), mm(sz))
            box = tmp.createBox(orient)
            if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
                bf = comp.features.baseFeatures.add()
                bf.startEdit()
                body = comp.bRepBodies.add(box, bf)
                bf.finishEdit()
            else:
                body = comp.bRepBodies.add(box)
            body.name = name
            return body

        def create_wheel(comp, name, centre, side='L'):
            """Create wheel (thick disc) + tyre ring at given centre."""
            # Wheel disc along X-axis (lateral)
            dx = -WHEEL_WIDTH/2 if side == 'L' else WHEEL_WIDTH/2
            p1 = (centre[0] - dx, centre[1], centre[2])
            p2 = (centre[0] + dx, centre[1], centre[2])
            # Rim
            create_tube(comp, f'{name}_Rim', p1, p2, WHEEL_R - TYRE_THICK)
            # Tyre
            create_tube(comp, f'{name}_Tyre', p1, p2, WHEEL_R)

        def add_comp(parent, name):
            """Add a new sub-component. Returns (occurrence, component)."""
            occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            occ.component.name = name
            return occ, occ.component

        def midpt(a, b):
            return ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2)

        # ==============================================================
        # BUILD ASSEMBLY
        # ==============================================================

        # ----------------------------------------------------------
        # DIFFERENTIAL MECHANISM (EA-26 Section 9)
        # ----------------------------------------------------------
        diff_occ, diff_comp = add_comp(root, 'Differential')

        # Diff bar (rotates about X through DIFF_PIV)
        create_tube(diff_comp, 'DiffBar', DIFF_BAR_L, DIFF_BAR_R, ROD_R)

        # Central pivot (sphere to show pivot point)
        create_sphere(diff_comp, 'DiffPivot', DIFF_PIV, 8.0)

        # Pivot bearing housing (box around pivot)
        create_box(diff_comp, 'DiffPivotMount', DIFF_PIV, 30, 30, 20)

        # Left differential link (bar end → left rocker)
        create_tube(diff_comp, 'DiffLink_L', LINK_BAR_L, LINK_RKR_L, 3.0)
        create_sphere(diff_comp, 'BallJoint_L_Top', LINK_BAR_L, BALL_R)
        create_sphere(diff_comp, 'BallJoint_L_Bot', LINK_RKR_L, BALL_R)

        # Right differential link (bar end → right rocker)
        create_tube(diff_comp, 'DiffLink_R', LINK_BAR_R, LINK_RKR_R, 3.0)
        create_sphere(diff_comp, 'BallJoint_R_Top', LINK_BAR_R, BALL_R)
        create_sphere(diff_comp, 'BallJoint_R_Bot', LINK_RKR_R, BALL_R)

        # ----------------------------------------------------------
        # BODY OUTLINE (simplified box for reference)
        # ----------------------------------------------------------
        body_occ, body_comp = add_comp(root, 'Body_Reference')
        body_w = ROCKER_PIV_X * 2  # body width = distance between pivots
        body_l = 200.0             # body length (Y)
        body_h = 30.0              # body height
        body_cz = GND_CLR + body_h / 2
        create_box(body_comp, 'BodyShell', (0, 0, body_cz), body_w, body_l, body_h)

        # Rocker pivot mounts on body (visible bosses)
        create_tube(body_comp, 'RockerPivotMount_L',
                    (-ROCKER_PIV_X - 10, 0, ROCKER_PIV_Z),
                    (-ROCKER_PIV_X + 10, 0, ROCKER_PIV_Z), 12)
        create_tube(body_comp, 'RockerPivotMount_R',
                    ( ROCKER_PIV_X - 10, 0, ROCKER_PIV_Z),
                    ( ROCKER_PIV_X + 10, 0, ROCKER_PIV_Z), 12)

        # ----------------------------------------------------------
        # SUSPENSION SIDES
        # ----------------------------------------------------------
        def build_side(parent, s, hub, front, bogie, mid, rear,
                       link_rkr):
            """Build one complete side of the suspension.
            s = 'L' or 'R'. All positions in mm."""

            side_occ, side_comp = add_comp(parent, f'Suspension_{s}')

            # === ROCKER ARM ===
            # Hub connector (box at diff bar clamp point)
            create_box(side_comp, f'RockerHub_{s}', hub, 40, 35, 30)
            # Rocker pivot bearing (visible ring)
            create_sphere(side_comp, f'RockerPivot_{s}', hub, 11)

            # Rocker tubes
            create_tube(side_comp, f'RockerFrontTube_{s}', hub, front, ROD_R)
            create_tube(side_comp, f'RockerRearTube_{s}', hub, bogie, ROD_R)

            # Diff link attachment point on rocker
            create_sphere(side_comp, f'DiffLinkAttach_{s}', link_rkr, BALL_R)

            # === BOGIE ARM ===
            # Bogie pivot connector (box with bearing)
            create_box(side_comp, f'BogiePivot_{s}', bogie, 35, 30, 25)
            create_sphere(side_comp, f'BogieBearing_{s}', bogie, 11)

            # Bogie tubes
            create_tube(side_comp, f'BogieFrontTube_{s}', bogie, mid, ROD_R)
            create_tube(side_comp, f'BogieRearTube_{s}', bogie, rear, ROD_R)

            # === WHEEL CONNECTORS ===
            create_box(side_comp, f'FrontWheelConn_{s}', front,
                       30, 25, 25)
            create_box(side_comp, f'MiddleWheelConn_{s}', mid,
                       25, 20, 20)
            create_box(side_comp, f'RearWheelConn_{s}', rear,
                       30, 25, 25)

            # === STEERING KNUCKLES (front + rear only) ===
            for tag, pos in [('F', front), ('R', rear)]:
                # Steering pivot shaft (vertical)
                shaft_top = (pos[0], pos[1], pos[2] + 20)
                shaft_bot = (pos[0], pos[1], pos[2] - 15)
                create_tube(side_comp, f'SteerShaft_{tag}{s}',
                            shaft_top, shaft_bot, 3.0)
                # Knuckle (box hanging below)
                create_box(side_comp, f'Knuckle_{tag}{s}',
                           (pos[0], pos[1], pos[2] - 10),
                           20, 15, 20)
                # Servo envelope
                servo_y = pos[1] - 25 if tag == 'F' else pos[1] + 25
                create_box(side_comp, f'Servo_{tag}{s}',
                           (pos[0], servo_y, pos[2] + 5),
                           23, 12, 23)

            # === WHEELS (3x) ===
            for tag, pos in [('F', front), ('M', mid), ('R', rear)]:
                create_wheel(side_comp, f'Wheel_{tag}{s}', pos, s)

            # === MOTOR ENVELOPES (3x, inboard of wheels) ===
            for tag, pos in [('F', front), ('M', mid), ('R', rear)]:
                inboard = 20 if s == 'L' else -20
                motor_c = (pos[0] + inboard, pos[1], pos[2])
                create_box(side_comp, f'Motor_{tag}{s}', motor_c,
                           MOTOR_W, MOTOR_L, MOTOR_H)

            # === CABLE CLIPS (on tube midpoints) ===
            for tag, a, b in [
                ('RkrF', hub, front),
                ('RkrR', hub, bogie),
                ('BogR', bogie, rear),
            ]:
                mp = midpt(a, b)
                create_box(side_comp, f'CableClip_{s}_{tag}',
                           mp, 12, 8, 10)

        # Build left side
        build_side(root, 'L', HUB_L, FRONT_L, BOGIE_L, MID_L, REAR_L,
                   LINK_RKR_L)

        # Build right side
        build_side(root, 'R', HUB_R, FRONT_R, BOGIE_R, MID_R, REAR_R,
                   LINK_RKR_R)

        # ==============================================================
        # ZOOM TO FIT AND REPORT
        # ==============================================================
        app.activeViewport.fit()

        count = 0
        for _ in root.allOccurrences:
            count += 1

        ui.messageBox(
            'EA-26 Suspension Assembly created!\n\n'
            f'Components: {count}\n\n'
            'NEW vs old design:\n'
            '  + Differential bar with PIVOT (not just a rod)\n'
            '  + 2x Differential links with BALL JOINTS\n'
            '  + Body reference outline\n'
            '  + Rocker pivot mounts (bearing bosses)\n'
            '  + Steering knuckles + pivot shafts\n'
            '  + Servo envelopes\n'
            '  + Motor envelopes at each wheel\n'
            '  + Bogie pivot connectors with bearings\n\n'
            'Hierarchy:\n'
            '  Differential/\n'
            '    Bar + Pivot + 2x Links + 4x Ball Joints\n'
            '  Body_Reference/\n'
            '    Shell + Pivot Mounts\n'
            '  Suspension_L/ + Suspension_R/\n'
            '    Rocker (hub + 2 tubes)\n'
            '    Bogie (pivot + 2 tubes)\n'
            '    3x Wheel connectors\n'
            '    2x Steering knuckles + servos\n'
            '    3x Wheels + Motors\n'
            '    3x Cable clips\n\n'
            'All geometry is parametric primitives.\n'
            'Replace with detailed STLs as they are exported.\n\n'
            'Reference: EA-26 Suspension Design Package',
            'Mars Rover Suspension (EA-26)')

    except:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}',
                          'Suspension Assembly Error')
