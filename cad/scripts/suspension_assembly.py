"""
Mars Rover Suspension Assembly — NASA-Proportioned Rocker-Bogie
================================================================

Pure-geometry visualisation of the complete rocker-bogie suspension
with Curiosity/Perseverance-inspired proportions:
  - Rocker pivot at 1.5× wheel diameter above ground
  - Arms sweep ~24° down from body to wheels
  - Through-bar differential (like Curiosity) — bar IS rocker pivot axis
  - Wider wheels (width/diameter ≈ 0.55)

Generates all parts as primitive solids (cylinders, spheres, boxes)
so it runs immediately with NO STL dependencies.

All dimensions loaded from generate_rover_params.py.

Coordinate System:
  Origin = body centre at ground level
  X = left(-) / right(+)     (track width)
  Y = rear(-) / front(+)     (wheelbase)
  Z = up(+)                  (vertical, ground = 0)

ALL Fusion 360 API values in CENTIMETERS (mm / 10).

Reference: EA-26 Suspension Design, EA-01 Geometry, EA-27 Steering
"""

import adsk.core
import adsk.fusion
import traceback
import math
import os
import sys


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

        design.designType = adsk.fusion.DesignTypes.DirectDesignType

        # ==============================================================
        # LOAD PARAMETERS
        # ==============================================================
        params_path = r"D:\Mars Rover Project\cad\scripts"
        if params_path not in sys.path:
            sys.path.insert(0, params_path)

        # Force reimport to pick up changes
        if 'generate_rover_params' in sys.modules:
            del sys.modules['generate_rover_params']
        from generate_rover_params import get_params

        P = get_params(scale=0.4)  # Phase 1

        # --- Wheel ---
        WHEEL_R      = P["wheel"]["outer_diameter"] / 2.0
        WHEEL_WIDTH  = P["wheel"]["width"]
        WHEEL_Z      = WHEEL_R   # wheel centres at radius above ground

        # --- Layout ---
        TRACK_HALF   = P["overall"]["track_width"] / 2.0
        WB_HALF      = P["overall"]["wheelbase"] / 2.0

        # --- Body ---
        BODY_W       = P["body"]["width"]
        BODY_L       = P["body"]["length"]
        BODY_H       = P["body"]["height"]
        GND_CLR      = P["overall"]["ground_clearance"]

        # --- Rocker pivot (high, like Curiosity) ---
        ROCKER_PIV_X = P["body_features"]["rocker_pivot_x"]
        ROCKER_PIV_Z = P["body_features"]["rocker_pivot_z"]

        # --- Bogie pivot: calculated so arms descend at same angle as rocker ---
        # Rocker forward arm drops from pivot to front wheel:
        #   slope = (pivot_Z - wheel_Z) / WB_HALF
        # Bogie pivot is on the rear rocker arm at distance pivot_to_wheel
        BOGIE_DIST   = P["bogie_arm"]["pivot_to_wheel"]  # horizontal dist behind hub
        arm_slope    = (ROCKER_PIV_Z - WHEEL_Z) / WB_HALF  # mm drop per mm of Y
        BOGIE_PIV_Y  = -BOGIE_DIST
        BOGIE_PIV_Z  = ROCKER_PIV_Z - arm_slope * BOGIE_DIST  # same descent angle

        # --- Differential (through-bar like Curiosity) ---
        DIFF_PIV_Z   = P["differential_computed"]["diff_pivot_z"]
        DIFF_BAR_LEN = P["differential_bar"]["bar_half_span"]
        THROUGH_BAR  = P["differential_computed"].get("mechanism_type") == "through-bar"

        # --- Steel rod ---
        ROD_R        = P["differential_bar"]["rod_od"] / 2.0
        BALL_R       = P["differential_link"]["ball_joint_od"] / 2.0

        # --- Motor envelope ---
        MOTOR_L      = P["motor_n20"]["body_length"]
        MOTOR_W      = P["motor_n20"]["body_width"]
        MOTOR_H      = P["motor_n20"]["body_height"]

        # --- Differential housing ---
        DPIV_HW = P["differential_bar"]["pivot_housing_w"]
        DPIV_HL = P["differential_bar"]["pivot_housing_l"]
        DPIV_HH = P["differential_bar"]["pivot_housing_h"]

        # --- Link params (only used in link mode) ---
        DIFF_LINK_BAR_R = P["differential_link"]["bar_attach_offset_z"]
        DIFF_LINK_RKR_R = P["differential_link"]["rocker_attach_offset_z"]
        DIFF_LINK_ROD   = P["differential_link"]["rod_od"] / 2.0

        # ==============================================================
        # KEY POSITIONS (mm, origin = body centre at ground level)
        # ==============================================================

        # Rocker hubs (on body sides, high up)
        HUB_L    = (-ROCKER_PIV_X,  0,           ROCKER_PIV_Z)
        HUB_R    = ( ROCKER_PIV_X,  0,           ROCKER_PIV_Z)

        # Wheels (at track width, ground level + radius)
        FRONT_L  = (-TRACK_HALF,    WB_HALF,     WHEEL_Z)
        MID_L    = (-TRACK_HALF,    0,            WHEEL_Z)
        REAR_L   = (-TRACK_HALF,   -WB_HALF,     WHEEL_Z)

        FRONT_R  = ( TRACK_HALF,    WB_HALF,     WHEEL_Z)
        MID_R    = ( TRACK_HALF,    0,            WHEEL_Z)
        REAR_R   = ( TRACK_HALF,   -WB_HALF,     WHEEL_Z)

        # Bogie pivots (on rocker rear arm, elevated above wheels)
        BOGIE_L  = (-TRACK_HALF,    BOGIE_PIV_Y, BOGIE_PIV_Z)
        BOGIE_R  = ( TRACK_HALF,    BOGIE_PIV_Y, BOGIE_PIV_Z)

        # Differential (through-bar at rocker pivot height)
        DIFF_PIV   = (0, 0, DIFF_PIV_Z)
        DIFF_BAR_L = (-DIFF_BAR_LEN, 0, DIFF_PIV_Z)
        DIFF_BAR_R = ( DIFF_BAR_LEN, 0, DIFF_PIV_Z)

        # For link mode: link endpoints
        if not THROUGH_BAR:
            LINK_BAR_L = (-DIFF_BAR_LEN, 0, DIFF_PIV_Z - DIFF_LINK_BAR_R)
            LINK_BAR_R = ( DIFF_BAR_LEN, 0, DIFF_PIV_Z - DIFF_LINK_BAR_R)
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
            """Create a cylinder between two 3D points (mm)."""
            tmp = adsk.fusion.TemporaryBRepManager.get()
            p1 = adsk.core.Point3D.create(mm(start[0]), mm(start[1]), mm(start[2]))
            p2 = adsk.core.Point3D.create(mm(end[0]), mm(end[1]), mm(end[2]))
            cyl = tmp.createCylinderOrCone(p1, mm(radius), p2, mm(radius))
            body = comp.bRepBodies.add(cyl)
            body.name = name
            return body

        def create_sphere(comp, name, centre, radius=BALL_R):
            """Create a sphere at given point (mm)."""
            tmp = adsk.fusion.TemporaryBRepManager.get()
            c = adsk.core.Point3D.create(mm(centre[0]), mm(centre[1]), mm(centre[2]))
            sph = tmp.createSphere(c, mm(radius))
            body = comp.bRepBodies.add(sph)
            body.name = name
            return body

        def create_box(comp, name, centre, sx, sy, sz):
            """Create a box centred at given point (mm)."""
            tmp = adsk.fusion.TemporaryBRepManager.get()
            orient = adsk.core.OrientedBoundingBox3D.create(
                adsk.core.Point3D.create(mm(centre[0]), mm(centre[1]), mm(centre[2])),
                adsk.core.Vector3D.create(1, 0, 0),
                adsk.core.Vector3D.create(0, 1, 0),
                mm(sx), mm(sy), mm(sz))
            box = tmp.createBox(orient)
            body = comp.bRepBodies.add(box)
            body.name = name
            return body

        def create_wheel(comp, name, centre, side='L'):
            """Create wheel disc at given centre."""
            hw = WHEEL_WIDTH / 2
            if side == 'L':
                p1 = (centre[0] + hw, centre[1], centre[2])
                p2 = (centre[0] - hw, centre[1], centre[2])
            else:
                p1 = (centre[0] - hw, centre[1], centre[2])
                p2 = (centre[0] + hw, centre[1], centre[2])
            create_tube(comp, f'{name}_Tyre', p1, p2, WHEEL_R)

        def add_comp(parent, name):
            """Add a new sub-component."""
            occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            occ.component.name = name
            return occ, occ.component

        # ==============================================================
        # BUILD ASSEMBLY
        # ==============================================================

        # --- GROUND PLANE ---
        gnd_occ, gnd_comp = add_comp(root, 'Ground')
        create_box(gnd_comp, 'GroundPlane',
                   (0, 0, -1), TRACK_HALF * 3, WB_HALF * 3, 2)

        # --- BODY OUTLINE (transparent reference box) ---
        body_occ, body_comp = add_comp(root, 'Body')
        body_centre_z = GND_CLR + BODY_H / 2
        create_box(body_comp, 'BodyFrame',
                   (0, 0, body_centre_z), BODY_W, BODY_L, BODY_H)

        # --- DIFFERENTIAL MECHANISM ---
        diff_occ, diff_comp = add_comp(root, 'Differential')

        # Diff bar (through-bar: runs from one rocker to the other, through body)
        create_tube(diff_comp, 'DiffBar', DIFF_BAR_L, DIFF_BAR_R, ROD_R)

        # Central pivot bearing (where body holds the bar)
        create_sphere(diff_comp, 'DiffPivot', DIFF_PIV, 8.0)

        # Pivot housing on body
        create_box(diff_comp, 'DiffPivotHousing', DIFF_PIV,
                   DPIV_HW, DPIV_HL, DPIV_HH)

        if not THROUGH_BAR:
            # Link mechanism mode (EA-26 original)
            for side, bar_pt, rkr_pt in [
                ('L', LINK_BAR_L, LINK_RKR_L),
                ('R', LINK_BAR_R, LINK_RKR_R),
            ]:
                create_tube(diff_comp, f'DiffLink_{side}', bar_pt, rkr_pt,
                            DIFF_LINK_ROD)
                create_sphere(diff_comp, f'BallJoint_{side}_Bar', bar_pt, BALL_R)
                create_sphere(diff_comp, f'BallJoint_{side}_Rkr', rkr_pt, BALL_R)

        # --- SUSPENSION SIDES ---
        def build_side(parent, s, hub, front, bogie, mid, rear):
            """Build one complete side of the rocker-bogie suspension."""

            side_occ, sc = add_comp(parent, f'Suspension_{s}')

            # === ROCKER ARM ===
            # Hub connector at body pivot (where rocker clamps to diff bar)
            create_box(sc, f'RockerHub_{s}', hub, 30, 25, 22)
            create_sphere(sc, f'RockerPivotBearing_{s}', hub, 11)

            # Rocker forward tube: hub → front wheel connector
            create_tube(sc, f'RockerFwd_{s}', hub, front, ROD_R)
            # Rocker rear tube: hub → bogie pivot
            create_tube(sc, f'RockerRear_{s}', hub, bogie, ROD_R)

            # === BOGIE ARM ===
            # Bogie pivot connector (where bogie pivots on rocker)
            create_box(sc, f'BogiePivot_{s}', bogie, 28, 22, 20)
            create_sphere(sc, f'BogieBearing_{s}', bogie, 11)

            # Bogie forward tube: bogie → middle wheel
            create_tube(sc, f'BogieFwd_{s}', bogie, mid, ROD_R)
            # Bogie rear tube: bogie → rear wheel
            create_tube(sc, f'BogieRear_{s}', bogie, rear, ROD_R)

            # === WHEEL CONNECTORS ===
            create_box(sc, f'FrontConn_{s}', front, 22, 18, 18)
            create_box(sc, f'MiddleConn_{s}', mid, 20, 16, 16)
            create_box(sc, f'RearConn_{s}', rear, 22, 18, 18)

            # === STEERING (front + rear wheels) ===
            for tag, pos in [('F', front), ('R', rear)]:
                shaft_top = (pos[0], pos[1], pos[2] + 10)
                shaft_bot = (pos[0], pos[1], pos[2] - 18)
                create_tube(sc, f'SteerShaft_{tag}{s}',
                            shaft_top, shaft_bot, 3)
                knuckle_z = pos[2] - 10
                create_box(sc, f'Knuckle_{tag}{s}',
                           (pos[0], pos[1], knuckle_z), 20, 22, 14)

            # === WHEELS ===
            for tag, pos in [('F', front), ('M', mid), ('R', rear)]:
                create_wheel(sc, f'Wheel_{tag}{s}', pos, s)

            # === MOTORS (inboard of each wheel) ===
            for tag, pos in [('F', front), ('M', mid), ('R', rear)]:
                inboard = 16 if s == 'L' else -16
                create_box(sc, f'Motor_{tag}{s}',
                           (pos[0] + inboard, pos[1], pos[2]),
                           MOTOR_W, MOTOR_L, MOTOR_H)

        # Build both sides
        build_side(root, 'L', HUB_L, FRONT_L, BOGIE_L, MID_L, REAR_L)
        build_side(root, 'R', HUB_R, FRONT_R, BOGIE_R, MID_R, REAR_R)

        # ==============================================================
        # ZOOM TO FIT
        # ==============================================================
        app.activeViewport.fit()

        count = sum(1 for _ in root.allOccurrences)

        fwd_angle = math.degrees(math.atan2(ROCKER_PIV_Z - WHEEL_Z, WB_HALF))
        bogie_angle = math.degrees(math.atan2(BOGIE_PIV_Z - WHEEL_Z, BOGIE_DIST))

        ui.messageBox(
            f'Suspension assembly created — {count} components\n\n'
            f'NASA-proportioned geometry (0.4 scale):\n'
            f'  Wheel ø × W:         {WHEEL_R*2:.0f} × {WHEEL_WIDTH:.0f} mm\n'
            f'  Wheel centres Z:     {WHEEL_Z:.0f} mm\n'
            f'  Bogie pivot Z:       {BOGIE_PIV_Z:.0f} mm\n'
            f'  Rocker pivot Z:      {ROCKER_PIV_Z:.0f} mm\n'
            f'  Diff pivot Z:        {DIFF_PIV_Z:.0f} mm\n'
            f'  Rocker arm angle:    {fwd_angle:.1f}° down\n'
            f'  Bogie arm angle:     {bogie_angle:.1f}° down\n'
            f'  Track width:         {TRACK_HALF*2:.0f} mm\n'
            f'  Wheelbase:           {WB_HALF*2:.0f} mm\n'
            f'  Diff bar span:       {DIFF_BAR_LEN*2:.0f} mm\n'
            f'  Diff mechanism:      {"through-bar" if THROUGH_BAR else "bar+links"}\n'
            f'  Body:                {BODY_W:.0f}×{BODY_L:.0f}×{BODY_H:.0f} mm\n\n'
            'Close dialog, then orbit to inspect.',
            'Mars Rover Suspension (NASA Proportions)')

    except:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}',
                          'Suspension Assembly Error')
