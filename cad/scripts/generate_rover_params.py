"""
Mars Rover CAD Parameter Generator
===================================

Defines ALL rover parameters as a Python dictionary for use by Fusion 360
API scripts. This file is standalone (no Fusion 360 imports) so it can be
reviewed, tested, and validated outside of Fusion 360.

Usage in Fusion 360 API script:
    import sys
    sys.path.insert(0, r"D:\\Mars Rover Project\\cad\\scripts")
    from generate_rover_params import get_params

    params = get_params(scale=0.4)   # Phase 1
    body_length = params["body"]["length"]

Usage standalone:
    python generate_rover_params.py          # prints Phase 1 (0.4 scale)
    python generate_rover_params.py --full   # prints Phase 2 (full scale)
    python generate_rover_params.py --both   # prints both side by side

References:
    EA-01  Suspension Analysis
    EA-08  Phase 1 Prototype Spec
    EA-10  Ackermann Steering Geometry
    EA-11  3D Printing Strategy
"""

import math

# ---------------------------------------------------------------------------
# Full-scale (Phase 2, scale = 1.0) master dimensions in mm
# Phase 1 values are derived by multiplying by SCALE (0.4)
# unless an override is specified.
# ---------------------------------------------------------------------------

FULL_SCALE_PARAMS = {

    # ------------------------------------------------------------------
    # Overall rover dimensions
    # ------------------------------------------------------------------
    "overall": {
        "body_length":          1100,   # mm, Y-axis, front to rear
        "body_width":            650,   # mm, X-axis, side to side
        "body_height":           400,   # mm, Z-axis, structural frame height (Phase 2)
        "driving_height":       1050,   # mm, ground to top of body (with mast, Phase 2)
        "wheelbase":             900,   # mm, front wheel to rear wheel per side
        "track_width":           700,   # mm, wheel centre to wheel centre
        "ground_clearance":      150,   # mm, under body frame
        "target_speed_kmh":        5,   # km/h
    },

    # ------------------------------------------------------------------
    # Body frame
    # ------------------------------------------------------------------
    "body": {
        "length":               1100,   # mm, outer
        "width":                 650,   # mm, outer
        "height":                300,   # mm, outer frame height (raised for NASA-like proportions)
        "wall_thickness":          4,   # mm, outer walls (NOT scaled -- 4mm for PLA rigidity)
        "rib_thickness":           2,   # mm, internal ribs (NOT scaled)
        "top_deck_thickness":      2,   # mm, cosmetic cover (NOT scaled)
        "top_deck_clips":          8,   # count
        "join_bolt_count":         6,   # M3 bolts along centre seam
    },

    # ------------------------------------------------------------------
    # Rocker arms (x2)
    # ------------------------------------------------------------------
    "rocker_arm": {
        "length":                450,   # mm, body pivot to front wheel axle
        "cross_section_w":        50,   # mm, outer width (Phase 2: 2020 extrusion)
        "cross_section_h":        38,   # mm, outer height
        "wall_thickness":          3,   # mm (NOT scaled)
        "body_pivot_bore":         8,   # mm, for 608ZZ inner race
        "body_pivot_boss_od":     22,   # mm, nominal 608ZZ OD
        "bogie_pivot_bore":        8,   # mm
        "bogie_pivot_boss_od":    22,   # mm
        "motor_mount_pcd":        25,   # mm, 4x M3 pitch circle diameter
        "motor_mount_holes":       4,   # count
    },

    # ------------------------------------------------------------------
    # Bogie arms (x2)
    # ------------------------------------------------------------------
    "bogie_arm": {
        "length":                450,   # mm, W2 axle to W3 axle (was 300, corrected for geometry)
        "pivot_to_wheel":        225,   # mm, bogie pivot to each wheel (symmetric)
        "cross_section_w":        38,   # mm, outer
        "cross_section_h":        30,   # mm, outer
        "wall_thickness":        2.5,   # mm (NOT scaled)
        "pivot_bore":              8,   # mm
    },

    # ------------------------------------------------------------------
    # Differential mechanism (EA-26 Section 9)
    # ------------------------------------------------------------------
    "differential_bar": {
        "rod_od":                  8,   # mm, steel rod outer diameter
        "bar_half_span":         325,   # mm, bar extends ±325mm (within body width, like Curiosity through-bar)
        "pivot_z_above_rocker":    0,   # mm, through-bar: diff bar IS the rocker pivot axis (like Curiosity/Perseverance)
        "bearing_seat_od":        22,   # mm, nominal 608ZZ OD (for central pivot)
        "bearing_seat_depth":      7,   # mm, nominal 608ZZ width
        "angular_range_deg":      25,   # +/- degrees from horizontal
        "pivot_housing_w":        40,   # mm, central pivot housing width (X)
        "pivot_housing_l":        40,   # mm, central pivot housing length (Y)
        "pivot_housing_h":        25,   # mm, central pivot housing height (Z)
    },

    "differential_link": {
        "count":                   2,   # one per side
        "rod_od":                  6,   # mm, link rod diameter (M6 threaded rod)
        "bar_attach_offset_z":     0,   # mm, through-bar: no separate links (set >0 for link mechanism)
        "rocker_attach_offset_z":  0,   # mm, through-bar: no separate links (set >0 for link mechanism)
        "ball_joint_bore":         3,   # mm, M3 rod-end bearing bore
        "ball_joint_od":          10,   # mm, rod-end bearing housing OD
        "ball_joint_length":      20,   # mm, rod-end bearing body length
        "ball_joint_angle_deg":   15,   # +/- degrees, typical M3 rod-end range
        "turnbuckle":           True,   # adjustable length via LH+RH thread ends
    },

    # ------------------------------------------------------------------
    # Wheels (x6)
    # ------------------------------------------------------------------
    "wheel": {
        "outer_diameter":        200,   # mm, including tread (tire OD)
        "radius":                100,   # mm
        "width":                 110,   # mm, total hub width
        "hub_bore_d_shaft":      3.0,   # mm, N20 D-shaft (Phase 1) -- NOT scaled
        "hub_bore_clearance":    0.1,   # mm, added to bore for print tolerance
        "d_flat_depth":          0.5,   # mm
        "hub_boss_od":            10,   # mm
        "hub_boss_length":         8,   # mm, shaft engagement
        "grouser_count":          12,   # chevron grousers per tire
        "grouser_depth":         7.5,   # mm, grouser/tread height
        "grouser_width_base":      3,   # mm (NOT scaled)
        "spoke_count":             6,   # spiral spokes
        "grub_screw_size":         2,   # M2
        # Two-piece wheel system (V4): hub/rim + interchangeable tire + beadlock ring
        "seat_diameter":         175,   # mm, tire band sits on this surface
        "flange_diameter":       185,   # mm, motor-side lip OD (retains tire)
        "rim_wall":             6.25,   # mm, rim wall thickness
        "tire_wall":               5,   # mm, tire band structural wall
        "tread_height":          7.5,   # mm, grouser height above tire wall
        "tire_width":             96,   # mm, tire band width (between lip and ring)
        "twist_angle":            25,   # degrees, spoke spiral twist (NOT scaled)
        "beadlock_screw_count":    4,   # M2 screws for ring retention (NOT scaled)
        "beadlock_screw_size":     2,   # M2 (NOT scaled)
        "beadlock_screw_radius":  84,   # mm, screw hole distance from centre
        # V5 Curiosity-inspired wheel (one-piece, replaces V4 hub+tire)
        # Scaled from GrabCAD Curiosity Wheel v25 (499mm OD -> 80mm at 0.4x)
        "v5_one_piece":          True, # single-piece PLA (hub+spokes+tread)
        "v5_source_od":          499,  # mm, original Curiosity model OD
        "v5_width_ratio":       0.81,  # width/OD ratio (404/499 from Curiosity)
        # At 0.4 scale: 80mm OD x 64.7mm wide, 6 curved spokes, chevron grousers
        # STL: 3d-print/wheels/CuriosityWheelV5.stl (360k faces, pre-scaled)
    },

    # ------------------------------------------------------------------
    # Reference model suspension (from frame_assem_v6.STEP, scaled 0.4x)
    # See docs/engineering/reference-model-integration-log.md for full details
    # ------------------------------------------------------------------
    "reference_suspension": {
        "source":               "frame_assem_v6.STEP (GrabCAD)",
        "scale_factor":          0.4,
        "track_width_actual":    296.2,  # mm at 0.4x (741mm full, vs 700mm target)
        "wheelbase_actual":      298.3,  # mm at 0.4x (746mm full, vs 900mm target)
        "tube_cross_section":      8.0,  # mm at 0.4x (20mm full -- matches 8mm rods!)
        "envelope_x":            304.4,  # mm, width
        "envelope_y":            159.7,  # mm, height
        "envelope_z":            318.3,  # mm, length
    },

    # ------------------------------------------------------------------
    # Steering assembly (x4 corners)
    # ------------------------------------------------------------------
    "steering": {
        "bracket_length":         88,   # mm (Phase 2)
        "bracket_width":          63,   # mm
        "bracket_height":         63,   # mm (EA-27: bearing carrier only, no motor)
        "bearing_seat_od":        22,   # mm, nominal
        "bearing_seat_depth":      7,   # mm, nominal
        "pivot_bore":              8,   # mm
        "pivot_to_wheel_centre":  50,   # mm, vertical offset
        "max_angle_deg":          35,   # +/- degrees
        "min_clearance_wheel_arm": 10,  # mm, at full lock (Phase 2)
        "servo_horn_length":      15,   # mm (NOT scaled -- SG90/MG996R horn)
        "horn_link_length":       50,   # mm, centre-to-centre M2 holes (EA-27)
        "horn_link_width":        20,   # mm (EA-27)
        "horn_link_thickness":  12.5,   # mm (EA-27)
        "knuckle_arm_length":   37.5,   # mm, pivot centre to link hole (EA-27)
        "hard_stop_tab_width":  12.5,   # mm (EA-27)
        "hard_stop_tab_radial":   20,   # mm (EA-27)
        "hard_stop_tab_thickness": 7.5, # mm (EA-27)
        "hard_stop_channel_deg":  70,   # degrees, ±35° total sweep (NOT scaled)
        "pivot_shaft_length":    125,   # mm, cut rod per steering pivot (EA-27)
        "servo_to_pivot_offset":  50,   # mm, horizontal distance between axes (EA-27)
    },

    # ------------------------------------------------------------------
    # Fixed wheel mounts (x2, middle wheels)
    # ------------------------------------------------------------------
    "fixed_mount": {
        "length":                 63,   # mm
        "width":                  63,   # mm
        "height":                 75,   # mm
    },

    # ------------------------------------------------------------------
    # Bearing: 608ZZ (used for all pivots and steering in Phase 1 & 2)
    # ------------------------------------------------------------------
    "bearing_608zz": {
        "inner_diameter":          8,   # mm (bore)
        "outer_diameter":         22,   # mm
        "width":                   7,   # mm
        "press_fit_oversize":   0.15,   # mm, added to OD for PLA seat (22.15mm actual)
        "seat_depth_extra":      0.2,   # mm, added to width for seat depth
        "quantity_phase1":        12,   # total bearings (9 needed + 3 spares, EA-25/EA-26)
        "quantity_phase2":        19,   # total bearings (adds wheel hub bearings)
        "weight_each_g":          12,   # grams
    },

    # ------------------------------------------------------------------
    # Fasteners
    # ------------------------------------------------------------------
    "fasteners": {
        # M8 pivot bolts
        "m8_bolt_40mm_qty":        4,   # rocker + bogie pivots
        "m8_bolt_30mm_qty":        4,   # steering pivots
        "m8_nyloc_nut_qty":        8,
        "m8_washer_qty":          16,   # 2 per pivot

        # M3 general
        "m3_12mm_qty":            30,   # body join, standoffs, brackets
        "m3_8mm_qty":             20,   # electronics, motor clips
        "m3_nut_qty":             30,
        "m3_washer_qty":          30,
        "m3_heat_set_insert_qty": 40,   # 5mm length, 5.7mm OD, brass knurled

        # M2 small
        "m2_8mm_qty":              8,   # SG90 servo mounting (4 servos x 2)
        "m2_10mm_qty":             8,   # horn link pin joints (4 links x 2 pins, EA-27)
        "m2_nyloc_nut_qty":        8,   # horn link pin retention (EA-27)
        "m2_nylon_washer_qty":    16,   # horn link pin joints, 2 per pin (EA-27)
        "m2_6mm_grub_qty":         6,   # wheel hub set screws
    },

    # ------------------------------------------------------------------
    # Heat-set inserts (M3)
    # ------------------------------------------------------------------
    "heat_set_insert": {
        "thread":                  3,   # M3
        "outer_diameter":        5.7,   # mm, knurled OD
        "length":                4.6,   # mm
        "hole_diameter":         4.8,   # mm, undersized for press
        "hole_depth":            5.5,   # mm, deeper than insert
        "min_wall_around":       2.4,   # mm, minimum (3 perimeters at 0.4mm)
        "chamfer":               0.5,   # mm x 45 deg at top
        "install_temp_pla_c":    175,   # degrees Celsius (170-180 range)
        "install_temp_petg_c":   220,   # degrees Celsius
        "install_temp_asa_c":    230,   # degrees Celsius
    },

    # ------------------------------------------------------------------
    # N20 gearmotor (x6)
    # ------------------------------------------------------------------
    "motor_n20": {
        "body_width":             12,   # mm (cross-section, verified)
        "body_height":            10,   # mm (cross-section, verified)
        "body_length":            15,   # mm (motor can only, per Pololu/generic datasheets)
        "gearbox_length":          9,   # mm (standard N20, varies by ratio)
        "total_length":           24,   # mm (motor + gearbox, measure your actual motor)
        "shaft_diameter":        3.0,   # mm, D-shaft
        "shaft_protrusion":       10,   # mm
        "mounting_screw_size":     2,   # M2
        "mounting_screw_spacing":  9,   # mm, centres
        "weight_each_g":          10,   # grams (typical N20 100RPM)
        "clip_inner_width":     12.2,   # mm, 0.2mm clearance
        "clip_inner_height":    10.2,   # mm, 0.2mm clearance
        "clip_wall_thickness":   2.0,   # mm
        "clip_snap_tab":         0.5,   # mm protrusion
        "shaft_exit_hole":       4.0,   # mm diameter
    },

    # ------------------------------------------------------------------
    # SG90 servo (x4, Phase 1)
    # ------------------------------------------------------------------
    "servo_sg90": {
        "body_width":           22.2,   # mm (without tabs)
        "body_depth":           11.8,   # mm
        "body_height":          22.7,   # mm
        "tab_width_total":      32.2,   # mm (with tabs, 5mm each side)
        "mount_hole_spacing":   27.5,   # mm, centre to centre
        "mount_hole_size":       2.2,   # mm, M2 clearance
        "shaft_offset_from_edge": 6.0,  # mm
        "horn_spline_teeth":      21,
        "horn_spline_od":        4.8,   # mm
        "pocket_min_depth":     12.0,   # mm
    },

    # ------------------------------------------------------------------
    # Body features
    # ------------------------------------------------------------------
    "body_features": {
        "rocker_pivot_x":        313,   # mm, +/- from centre (Phase 2)
        "rocker_pivot_y":          0,   # mm, at middle axle line
        "rocker_pivot_z":        300,   # mm, above ground (raised: ratio ~1.5× wheel ø, like Curiosity)
        "battery_tray_l":        175,   # mm
        "battery_tray_w":         88,   # mm
        "battery_tray_h":         63,   # mm
        "cable_channel_w":        10,   # mm (NOT scaled)
        "cable_channel_h":        10,   # mm (NOT scaled)
        "switch_mount_dia":       15,   # mm (NOT scaled)
        "vent_slot_width":         3,   # mm (NOT scaled)
        "vent_slot_count":         5,   # per side wall
    },

    # ------------------------------------------------------------------
    # Electronics layout (reference dimensions, NOT scaled)
    # ------------------------------------------------------------------
    "electronics": {
        "esp32_l":                63,   # mm (62.7mm per Espressif DXF, rounded)
        "esp32_w":                25,   # mm
        "esp32_mount_holes":       4,   # M3
        "l298n_l":                43,   # mm
        "l298n_w":                43,   # mm
        "l298n_h":                27,   # mm
        "l298n_mount_pcd":        37,   # mm
        "l298n_count":             2,
        "lipo_l":                 86,   # mm (2S 2200mAh, typical Gens Ace/Turnigy)
        "lipo_w":                 34,   # mm (varies 32-35mm by brand)
        "lipo_h":                 19,   # mm (varies 16-20mm by brand)
        "breadboard_l":           47,   # mm
        "breadboard_w":           35,   # mm
    },

    # ------------------------------------------------------------------
    # Clearances
    # ------------------------------------------------------------------
    "clearances": {
        "wheel_to_arm_at_lock":   10,   # mm, minimum at full steering lock
        "wheel_to_body":          10,   # mm, at max suspension travel
        "rocker_to_body":          3,   # mm, side clearance
        "bogie_to_rocker":         3,   # mm
        "diff_bar_to_body":        5,   # mm
        "motor_wire_clearance":    5,   # mm, to moving parts
        "cable_min_bend_radius":  15,   # mm, for stranded wire
        "wire_exit_hole_dia":      5,   # mm, at pivot points
    },

    # ------------------------------------------------------------------
    # Print settings (NOT scaled -- these are printer/material constants)
    # ------------------------------------------------------------------
    "print_settings": {
        "bed_x":                 225,   # mm, CTC Bizer
        "bed_y":                 145,   # mm
        "bed_z":                 150,   # mm
        "usable_x":             215,   # mm, with margins
        "usable_y":             135,   # mm
        "usable_z":             140,   # mm
        "bed_diagonal":          268,   # mm, max diagonal part (sqrt(225^2+145^2))
        "layer_height":          0.2,   # mm
        "nozzle_diameter":       0.4,   # mm
        "perimeters_structural":   4,   # walls for load-bearing parts
        "infill_structural":      50,   # percent, gyroid
        "infill_body_panel":      20,   # percent, gyroid
        "infill_connectors":      60,   # percent, for heat-set insert parts
        "pla_nozzle_temp":       200,   # degrees C (Phase 1, CTC Bizer)
        "pla_bed_temp":           60,   # degrees C
        "petg_nozzle_temp":      235,   # degrees C (Phase 2)
        "petg_bed_temp":          75,   # degrees C
        "asa_nozzle_temp":       250,   # degrees C (Phase 2)
        "asa_bed_temp":          100,   # degrees C
        "file_format":          "x3g",  # CTC Bizer via GPX converter
    },

    # ------------------------------------------------------------------
    # Steering geometry (from EA-10)
    # ------------------------------------------------------------------
    "steering_geometry": {
        "front_to_middle_axle":  450,   # mm (L_fm)
        "middle_to_rear_axle":   450,   # mm (L_mr)
        "half_track_width":      350,   # mm (W/2)
        "max_steering_angle_deg": 35,   # +/- degrees
        "min_turn_radius":       993,   # mm (at max steering angle)
        "point_turn_ideal_deg": 52.1,   # ideal angle (exceeds servo limit)
        "max_steering_rate_dps":  60,   # degrees per second
        "steering_deadband_deg":   1,   # +/- degrees
        "servo_centre_us":      1500,   # microseconds (PWM centre)
        "servo_us_per_deg":    11.11,   # microseconds per degree
    },

    # ------------------------------------------------------------------
    # Suspension geometry (from EA-01)
    # ------------------------------------------------------------------
    "suspension_geometry": {
        "rocker_swing_range_deg":  25,  # +/- degrees
        "bogie_swing_range_deg":   20,  # +/- degrees
        "diff_bar_range_deg":      25,  # +/- degrees (matches differential_bar.angular_range_deg)
        "max_obstacle_height":    150,  # mm (0.75 x wheel diameter)
        "cog_height":             232,  # mm above ground (EA-05 analysis)
        "static_tilt_limit_deg": 49.4,  # before tipover (side tilt)
    },
}


# ---------------------------------------------------------------------------
# Parameters that are NOT scaled (print/hardware constants)
# ---------------------------------------------------------------------------
_NO_SCALE_KEYS = {
    # Body -- print/design constants
    "body.wall_thickness",
    "body.rib_thickness",
    "body.top_deck_thickness",
    "body.top_deck_clips",
    "body.join_bolt_count",

    # Rocker arm -- bearing/bolt sizes are hardware constants
    "rocker_arm.wall_thickness",
    "rocker_arm.body_pivot_bore",
    "rocker_arm.body_pivot_boss_od",
    "rocker_arm.bogie_pivot_bore",
    "rocker_arm.bogie_pivot_boss_od",
    "rocker_arm.motor_mount_pcd",
    "rocker_arm.motor_mount_holes",

    # Bogie arm
    "bogie_arm.wall_thickness",
    "bogie_arm.pivot_bore",

    # Differential bar — hardware constants
    "differential_bar.rod_od",
    "differential_bar.bearing_seat_od",
    "differential_bar.bearing_seat_depth",
    "differential_bar.angular_range_deg",

    # Differential links — hardware constants
    "differential_link.count",
    "differential_link.rod_od",
    "differential_link.ball_joint_bore",
    "differential_link.ball_joint_od",
    "differential_link.ball_joint_length",
    "differential_link.ball_joint_angle_deg",
    "differential_link.turnbuckle",

    # Wheel -- bore/grouser are print minimums, beadlock is hardware
    "wheel.hub_bore_d_shaft",
    "wheel.hub_bore_clearance",
    "wheel.d_flat_depth",
    "wheel.hub_boss_od",
    "wheel.hub_boss_length",
    "wheel.grouser_count",
    "wheel.grouser_depth",
    "wheel.grouser_width_base",
    "wheel.spoke_count",
    "wheel.grub_screw_size",
    "wheel.twist_angle",
    "wheel.beadlock_screw_count",
    "wheel.beadlock_screw_size",

    # Steering -- hardware constants
    "steering.bearing_seat_od",
    "steering.bearing_seat_depth",
    "steering.pivot_bore",
    "steering.max_angle_deg",
    "steering.servo_horn_length",
    "steering.hard_stop_channel_deg",

    # Body features -- cable channels, switch, vents are print minimums
    "body_features.cable_channel_w",
    "body_features.cable_channel_h",
    "body_features.switch_mount_dia",
    "body_features.vent_slot_width",
    "body_features.vent_slot_count",

    # Entire groups that are hardware specs (not geometry)
    "bearing_608zz",
    "fasteners",
    "heat_set_insert",
    "motor_n20",
    "servo_sg90",
    "electronics",
    "clearances",
    "print_settings",

    # Steering geometry -- angles and rates are not scaled
    "steering_geometry.max_steering_angle_deg",
    "steering_geometry.point_turn_ideal_deg",
    "steering_geometry.max_steering_rate_dps",
    "steering_geometry.steering_deadband_deg",
    "steering_geometry.servo_centre_us",
    "steering_geometry.servo_us_per_deg",

    # Suspension geometry -- angles are not scaled
    "suspension_geometry.rocker_swing_range_deg",
    "suspension_geometry.bogie_swing_range_deg",
    "suspension_geometry.diff_bar_range_deg",
    "suspension_geometry.static_tilt_limit_deg",
}


def _should_scale(group_key, param_key):
    """Determine whether a parameter should be scaled."""
    full_key = f"{group_key}.{param_key}"
    # Check if the entire group is marked as no-scale
    if group_key in _NO_SCALE_KEYS:
        return False
    # Check if this specific parameter is marked as no-scale
    if full_key in _NO_SCALE_KEYS:
        return False
    # Don't scale counts, angles, percentages, temperatures, booleans
    if isinstance(param_key, str):
        for suffix in ("_count", "_qty", "_holes", "_deg", "_dps",
                        "_c", "_temp", "_kmh", "_us", "_percent",
                        "count", "clips"):
            if param_key.endswith(suffix):
                return False
    return True


def get_params(scale=0.4):
    """
    Return rover parameters scaled to the given factor.

    Args:
        scale: 0.4 for Phase 1 prototype, 1.0 for Phase 2 full scale.

    Returns:
        dict: Nested dictionary of all parameters in mm (unless noted).
    """
    import copy
    params = copy.deepcopy(FULL_SCALE_PARAMS)

    if scale == 1.0:
        # Add computed fields for full scale
        _add_computed(params, scale)
        return params

    for group_key, group in params.items():
        if not isinstance(group, dict):
            continue
        for param_key, value in group.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool) and _should_scale(group_key, param_key):
                params[group_key][param_key] = round(value * scale, 2)

    # Phase 1 overrides (values from EA-08 that don't follow simple scaling)
    params["body"]["height"] = 120               # Taller body for NASA-like proportions (body encloses pivot)
    params["overall"]["body_height"] = 120
    params["overall"]["driving_height"] = 420    # EA-08: no mast in Phase 1
    params["overall"]["target_speed_kmh"] = 2    # EA-08: 2 km/h for safety
    params["wheel"]["hub_boss_od"] = 14           # 14mm OD (wider for spoke strength at 0.4 scale, matches V4 CAD)
    params["wheel"]["hub_boss_length"] = 8        # not scaled, shaft engagement
    # Two-piece wheel V4 overrides (don't follow simple 0.4x scaling)
    params["wheel"]["seat_diameter"] = 70         # 70mm — tire band sits here
    params["wheel"]["flange_diameter"] = 74       # 74mm — motor-side lip OD
    params["wheel"]["rim_wall"] = 2.5             # 2.5mm rim wall
    params["wheel"]["tire_wall"] = 2              # 2mm tire structural wall (PLA minimum)
    params["wheel"]["tread_height"] = 3           # 3mm grouser height (PLA minimum)
    params["wheel"]["grouser_depth"] = 3          # 3mm (matches tread_height)
    params["wheel"]["tire_width"] = 40            # 40mm (between lip and beadlock ring)
    params["wheel"]["beadlock_screw_radius"] = 33.75  # 33.75mm from centre
    params["body_features"]["rocker_pivot_x"] = 125  # EA-08: X=+/-125mm
    params["body_features"]["rocker_pivot_z"] = 120  # Raised: 1.5× wheel ø above ground (like Curiosity, arms sweep ~24° down)
    params["body_features"]["battery_tray_l"] = 70   # EA-08: fits 2S 2200mAh
    params["body_features"]["battery_tray_w"] = 35
    params["body_features"]["battery_tray_h"] = 25
    params["steering"]["bracket_length"] = 35        # EA-08: 35mm
    params["steering"]["bracket_width"] = 30         # EA-08: increased from 25mm for bearing wall thickness
    params["steering"]["bracket_height"] = 25        # EA-27: reduced from 40mm (bearing carrier only, no motor)
    params["steering"]["pivot_to_wheel_centre"] = 20 # EA-10: 20mm vertical
    params["steering"]["min_clearance_wheel_arm"] = 5  # EA-08/EA-10: 5mm min
    params["steering"]["horn_link_length"] = 20      # EA-27: 50 * 0.4 = 20mm
    params["steering"]["horn_link_width"] = 8        # EA-27: 20 * 0.4 = 8mm
    params["steering"]["horn_link_thickness"] = 5    # EA-27: 12.5 * 0.4 = 5mm
    params["steering"]["knuckle_arm_length"] = 15    # EA-27: 37.5 * 0.4 = 15mm
    params["steering"]["hard_stop_tab_width"] = 5    # EA-27: 12.5 * 0.4 = 5mm
    params["steering"]["hard_stop_tab_radial"] = 8   # EA-27: 20 * 0.4 = 8mm
    params["steering"]["hard_stop_tab_thickness"] = 3  # EA-27: 7.5 * 0.4 = 3mm
    params["steering"]["pivot_shaft_length"] = 50    # EA-27: 125 * 0.4 = 50mm
    params["steering"]["servo_to_pivot_offset"] = 20 # EA-27: 50 * 0.4 = 20mm
    params["fixed_mount"]["length"] = 25             # EA-08: 25mm
    params["fixed_mount"]["width"] = 25
    params["fixed_mount"]["height"] = 30
    params["steering_geometry"]["min_turn_radius"] = 397  # EA-10: 0.4 scale
    params["suspension_geometry"]["max_obstacle_height"] = 60  # 0.75 x 80mm wheel
    params["suspension_geometry"]["cog_height"] = 120  # estimated at 0.4 scale

    # Differential mechanism Phase 1 overrides (from EA-26 assembly geometry)
    params["differential_bar"]["bar_half_span"] = 130     # 325 * 0.4 = 130mm (within body, like Curiosity)
    params["differential_bar"]["pivot_z_above_rocker"] = 0   # Through-bar: diff IS rocker pivot
    params["differential_bar"]["pivot_housing_w"] = 30    # smaller at 0.4 scale
    params["differential_bar"]["pivot_housing_l"] = 30
    params["differential_bar"]["pivot_housing_h"] = 20
    params["differential_link"]["bar_attach_offset_z"] = 0     # Through-bar: no separate links
    params["differential_link"]["rocker_attach_offset_z"] = 0   # Through-bar: no separate links

    # Add computed fields
    _add_computed(params, scale)

    return params


def _add_computed(params, scale):
    """Add derived/computed values to the parameter dictionary."""
    b = params["bearing_608zz"]
    params["computed"] = {
        "bearing_seat_od":      b["outer_diameter"] + b["press_fit_oversize"],
        "bearing_seat_depth":   b["width"] + b["seat_depth_extra"],
        "wheel_hub_bore":       params["wheel"]["hub_bore_d_shaft"]
                                + params["wheel"]["hub_bore_clearance"],
        "scale_factor":         scale,
        "phase":                1 if scale < 1.0 else 2,
    }
    # Wheel positions in rover coordinate system
    hw = params["overall"]["track_width"] / 2   # half track width
    hb = params["overall"]["wheelbase"] / 2     # half wheelbase
    wr = params["wheel"]["outer_diameter"] / 2  # wheel radius
    params["wheel_positions"] = {
        "FL": {"x": -hw, "y":  hb, "z": wr},
        "ML": {"x": -hw, "y": 0.0, "z": wr},
        "RL": {"x": -hw, "y": -hb, "z": wr},
        "RR": {"x":  hw, "y": -hb, "z": wr},
        "MR": {"x":  hw, "y": 0.0, "z": wr},
        "FR": {"x":  hw, "y":  hb, "z": wr},
    }

    # Differential geometry (computed)
    db = params["differential_bar"]
    dl = params["differential_link"]
    bf = params["body_features"]
    rpz = bf["rocker_pivot_z"]                    # rocker pivot Z
    dpz = rpz + db["pivot_z_above_rocker"]        # diff pivot Z
    rpx = bf["rocker_pivot_x"]                    # rocker pivot X

    # Through-bar mode: diff bar IS rocker pivot, no separate links
    through_bar = (db["pivot_z_above_rocker"] == 0 and
                   dl["bar_attach_offset_z"] == 0)

    if through_bar:
        params["differential_computed"] = {
            "diff_pivot_z":           round(dpz, 1),
            "mechanism_type":         "through-bar",
            "link_length":            0,
            "link_angle_from_horiz_deg": 0,
        }
    else:
        # Link mechanism mode (EA-26 original design)
        link_top_z = dpz - dl["bar_attach_offset_z"]
        link_bot_z = rpz + dl["rocker_attach_offset_z"]
        link_top_x = db["bar_half_span"]
        link_bot_x = rpx
        dx = link_top_x - link_bot_x
        dz = link_top_z - link_bot_z
        link_len = (dx**2 + dz**2) ** 0.5
        link_angle = math.degrees(math.atan2(abs(dz), abs(dx)))
        params["differential_computed"] = {
            "diff_pivot_z":           round(dpz, 1),
            "mechanism_type":         "bar-and-link",
            "link_top_z":             round(link_top_z, 1),
            "link_bot_z":             round(link_bot_z, 1),
            "link_length":            round(link_len, 1),
            "link_angle_from_horiz_deg": round(link_angle, 1),
            "link_top_pos":           f"(±{link_top_x}, 0, {link_top_z})",
            "link_bot_pos":           f"(±{link_bot_x}, 0, {link_bot_z})",
        }


def _calculate_ackermann(params, turn_radius_mm):
    """Calculate Ackermann steering angles for a given turn radius."""
    sg = params["steering_geometry"]
    l_fm = sg["front_to_middle_axle"]
    w_half = sg["half_track_width"]

    r = abs(turn_radius_mm)
    delta_inner = math.degrees(math.atan2(l_fm, r - w_half))
    delta_outer = math.degrees(math.atan2(l_fm, r + w_half))
    return delta_inner, delta_outer


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------

def print_params(params, title="Rover Parameters"):
    """Print all parameters in a formatted table."""
    print("=" * 78)
    print(f"  {title}")
    print(f"  Scale: {params.get('computed', {}).get('scale_factor', '?')}x "
          f"  Phase: {params.get('computed', {}).get('phase', '?')}")
    print("=" * 78)

    for group_key in sorted(params.keys()):
        group = params[group_key]
        if not isinstance(group, dict):
            continue

        print(f"\n  [{group_key}]")
        print(f"  {'Parameter':<40} {'Value':>12}  {'Unit':<6}")
        print(f"  {'-'*40} {'-'*12}  {'-'*6}")

        for param_key in sorted(group.keys()):
            value = group[param_key]
            if isinstance(value, dict):
                # Nested dict (e.g., wheel_positions)
                for sub_key, sub_val in sorted(value.items()):
                    label = f"  {param_key}.{sub_key}"
                    print(f"  {label:<40} {str(sub_val):>12}")
                continue

            # Determine unit
            unit = "mm"
            if param_key.endswith(("_count", "_qty", "_holes", "count", "clips",
                                     "phase1", "phase2", "teeth")):
                unit = ""
            elif param_key.endswith("_deg") or param_key.endswith("_dps"):
                unit = "deg" if "_dps" not in param_key else "deg/s"
            elif param_key.endswith(("_c", "_temp")):
                unit = "deg C"
            elif param_key.endswith("_kmh"):
                unit = "km/h"
            elif param_key.endswith("_g"):
                unit = "g"
            elif param_key.endswith("_us"):
                unit = "us"
            elif param_key.endswith("_percent") or param_key.startswith("infill"):
                unit = "%"
            elif param_key in ("scale_factor", "phase", "thread"):
                unit = ""
            elif param_key == "servo_us_per_deg":
                unit = "us/deg"

            if isinstance(value, float):
                val_str = f"{value:.2f}"
            else:
                val_str = str(value)

            print(f"  {param_key:<40} {val_str:>12}  {unit:<6}")


def print_comparison():
    """Print Phase 1 and Phase 2 parameters side by side."""
    p1 = get_params(scale=0.4)
    p2 = get_params(scale=1.0)

    print("=" * 92)
    print("  Mars Rover Parameters -- Phase 1 (0.4x) vs Phase 2 (1.0x)")
    print("=" * 92)

    all_groups = sorted(set(list(p1.keys()) + list(p2.keys())))

    for group_key in all_groups:
        g1 = p1.get(group_key, {})
        g2 = p2.get(group_key, {})
        if not isinstance(g1, dict) and not isinstance(g2, dict):
            continue

        print(f"\n  [{group_key}]")
        print(f"  {'Parameter':<36} {'Phase 1':>10}  {'Phase 2':>10}  {'Unit':<6}")
        print(f"  {'-'*36} {'-'*10}  {'-'*10}  {'-'*6}")

        all_keys = sorted(set(
            list(g1.keys() if isinstance(g1, dict) else []) +
            list(g2.keys() if isinstance(g2, dict) else [])
        ))

        for param_key in all_keys:
            v1 = g1.get(param_key, "--") if isinstance(g1, dict) else "--"
            v2 = g2.get(param_key, "--") if isinstance(g2, dict) else "--"

            # Skip nested dicts for comparison view (wheel_positions etc.)
            if isinstance(v1, dict) or isinstance(v2, dict):
                continue

            # Determine unit
            unit = "mm"
            if param_key.endswith(("_count", "_qty", "_holes", "count", "clips",
                                     "phase1", "phase2", "teeth")):
                unit = ""
            elif param_key.endswith("_deg") or param_key.endswith("_dps"):
                unit = "deg" if "_dps" not in param_key else "deg/s"
            elif param_key.endswith(("_c", "_temp")):
                unit = "deg C"
            elif param_key.endswith("_kmh"):
                unit = "km/h"
            elif param_key.endswith("_g"):
                unit = "g"
            elif param_key.endswith("_us"):
                unit = "us"
            elif param_key in ("scale_factor", "phase", "thread"):
                unit = ""
            elif param_key == "servo_us_per_deg":
                unit = "us/deg"

            def fmt(v):
                if v == "--":
                    return "--"
                if isinstance(v, float):
                    return f"{v:.2f}"
                return str(v)

            print(f"  {param_key:<36} {fmt(v1):>10}  {fmt(v2):>10}  {unit:<6}")


if __name__ == "__main__":
    import sys

    if "--both" in sys.argv:
        print_comparison()
    elif "--full" in sys.argv:
        params = get_params(scale=1.0)
        print_params(params, "Mars Rover Parameters -- Phase 2 (Full Scale)")
    else:
        params = get_params(scale=0.4)
        print_params(params, "Mars Rover Parameters -- Phase 1 (0.4 Scale)")

    print()
