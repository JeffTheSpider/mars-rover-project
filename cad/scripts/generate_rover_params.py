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
        "height":                200,   # mm, outer frame height (Phase 2 uses extrusion)
        "wall_thickness":          3,   # mm, outer walls (NOT scaled -- print minimum)
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
        "length":                300,   # mm, W2 axle to W3 axle
        "pivot_to_wheel":        150,   # mm, bogie pivot to each wheel (symmetric)
        "cross_section_w":        38,   # mm, outer
        "cross_section_h":        30,   # mm, outer
        "wall_thickness":        2.5,   # mm (NOT scaled)
        "pivot_bore":              8,   # mm
    },

    # ------------------------------------------------------------------
    # Differential bar
    # ------------------------------------------------------------------
    "differential_bar": {
        "length":                500,   # mm, centre to centre of rocker pivots
        "half_length":           250,   # mm, centre pivot to each end
        "rod_od":                  8,   # mm, steel rod outer diameter
        "adapter_tube_od":        12,   # mm, printed end cap OD
        "adapter_tube_id":         8,   # mm, press-fit onto rod
        "bearing_seat_od":        22,   # mm, nominal (see bearing oversize below)
        "bearing_seat_depth":      7,   # mm, nominal 608ZZ width
        "angular_range_deg":      20,   # +/- degrees from horizontal
        "adapter_count":           3,   # left, centre, right
    },

    # ------------------------------------------------------------------
    # Wheels (x6)
    # ------------------------------------------------------------------
    "wheel": {
        "outer_diameter":        200,   # mm, including tread
        "radius":                100,   # mm
        "width":                  80,   # mm, tread included
        "hub_bore_d_shaft":      3.0,   # mm, N20 D-shaft (Phase 1) -- NOT scaled
        "hub_bore_clearance":    0.1,   # mm, added to bore for print tolerance
        "d_flat_depth":          0.5,   # mm
        "hub_boss_od":            10,   # mm
        "hub_boss_length":         8,   # mm, shaft engagement
        "grouser_count":          12,   # chevron grousers
        "grouser_depth":           3,   # mm (NOT scaled -- print minimum)
        "grouser_width_base":      3,   # mm (NOT scaled)
        "spoke_count":             6,   # with flex zones
        "grub_screw_size":         2,   # M2
    },

    # ------------------------------------------------------------------
    # Steering assembly (x4 corners)
    # ------------------------------------------------------------------
    "steering": {
        "bracket_length":         88,   # mm (Phase 2)
        "bracket_width":          63,   # mm
        "bracket_height":        100,   # mm
        "bearing_seat_od":        22,   # mm, nominal
        "bearing_seat_depth":      7,   # mm, nominal
        "pivot_bore":              8,   # mm
        "pivot_to_wheel_centre":  50,   # mm, vertical offset
        "max_angle_deg":          35,   # +/- degrees
        "min_clearance_wheel_arm": 10,  # mm, at full lock (Phase 2)
        "servo_horn_length":      15,   # mm (NOT scaled -- SG90/MG996R horn)
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
        "press_fit_oversize":    0.1,   # mm, added to OD for PETG seat
        "seat_depth_extra":      0.2,   # mm, added to width for seat depth
        "quantity_phase1":        10,   # total bearings
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
        "install_temp_petg_c":   220,   # degrees Celsius
        "install_temp_asa_c":    230,   # degrees Celsius
    },

    # ------------------------------------------------------------------
    # N20 gearmotor (x6)
    # ------------------------------------------------------------------
    "motor_n20": {
        "body_width":             12,   # mm
        "body_height":            10,   # mm
        "body_length":            25,   # mm (motor only)
        "gearbox_length":         12,   # mm
        "total_length":           37,   # mm (motor + gearbox)
        "shaft_diameter":        3.0,   # mm, D-shaft
        "shaft_protrusion":       10,   # mm
        "mounting_screw_size":     2,   # M2
        "mounting_screw_spacing":  9,   # mm, centres
        "weight_each_g":          20,   # grams
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
        "rocker_pivot_z":        150,   # mm, above ground (Phase 2)
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
        "esp32_l":                69,   # mm
        "esp32_w":                25,   # mm
        "esp32_mount_holes":       4,   # M3
        "l298n_l":                43,   # mm
        "l298n_w":                43,   # mm
        "l298n_h":                27,   # mm
        "l298n_mount_pcd":        37,   # mm
        "l298n_count":             2,
        "lipo_l":                 70,   # mm (2S 2200mAh)
        "lipo_w":                 35,   # mm
        "lipo_h":                 18,   # mm
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
        "bed_x":                 220,   # mm, Ender 3
        "bed_y":                 220,   # mm
        "bed_z":                 250,   # mm
        "usable_x":             210,   # mm, with margins
        "usable_y":             210,   # mm
        "usable_z":             240,   # mm
        "layer_height":          0.2,   # mm
        "nozzle_diameter":       0.4,   # mm
        "perimeters_structural":   4,   # walls for load-bearing parts
        "infill_structural":      50,   # percent, gyroid
        "infill_body_panel":      20,   # percent, gyroid
        "infill_connectors":      60,   # percent, for heat-set insert parts
        "petg_nozzle_temp":      235,   # degrees C
        "petg_bed_temp":          75,   # degrees C
        "asa_nozzle_temp":       250,   # degrees C
        "asa_bed_temp":          100,   # degrees C
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
        "diff_bar_range_deg":      20,  # +/- degrees
        "max_obstacle_height":    150,  # mm (0.75 x wheel diameter)
        "cog_height":             300,  # mm above ground (estimated)
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

    # Differential bar
    "differential_bar.rod_od",
    "differential_bar.adapter_tube_od",
    "differential_bar.adapter_tube_id",
    "differential_bar.bearing_seat_od",
    "differential_bar.bearing_seat_depth",
    "differential_bar.angular_range_deg",
    "differential_bar.adapter_count",

    # Wheel -- bore/grouser are print minimums
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

    # Steering -- hardware constants
    "steering.bearing_seat_od",
    "steering.bearing_seat_depth",
    "steering.pivot_bore",
    "steering.max_angle_deg",
    "steering.servo_horn_length",

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
            if isinstance(value, (int, float)) and _should_scale(group_key, param_key):
                params[group_key][param_key] = round(value * scale, 2)

    # Phase 1 overrides (values from EA-08 that don't follow simple scaling)
    params["body"]["height"] = 80                # EA-08: 80mm body height
    params["overall"]["body_height"] = 80
    params["overall"]["driving_height"] = 420    # EA-08: no mast in Phase 1
    params["overall"]["target_speed_kmh"] = 2    # EA-08: 2 km/h for safety
    params["wheel"]["hub_boss_od"] = 10           # not scaled, print feature
    params["wheel"]["hub_boss_length"] = 8        # not scaled, shaft engagement
    params["body_features"]["rocker_pivot_x"] = 125  # EA-08: X=+/-125mm
    params["body_features"]["rocker_pivot_z"] = 60   # EA-08: Z=+60mm
    params["body_features"]["battery_tray_l"] = 70   # EA-08: fits 2S 2200mAh
    params["body_features"]["battery_tray_w"] = 35
    params["body_features"]["battery_tray_h"] = 25
    params["steering"]["bracket_length"] = 35        # EA-08: 35mm
    params["steering"]["bracket_width"] = 25         # EA-08: 25mm
    params["steering"]["bracket_height"] = 40        # EA-08: 40mm
    params["steering"]["pivot_to_wheel_centre"] = 20 # EA-10: 20mm vertical
    params["steering"]["min_clearance_wheel_arm"] = 5  # EA-08/EA-10: 5mm min
    params["fixed_mount"]["length"] = 25             # EA-08: 25mm
    params["fixed_mount"]["width"] = 25
    params["fixed_mount"]["height"] = 30
    params["steering_geometry"]["min_turn_radius"] = 397  # EA-10: 0.4 scale
    params["suspension_geometry"]["max_obstacle_height"] = 60  # 0.75 x 80mm wheel
    params["suspension_geometry"]["cog_height"] = 120  # estimated at 0.4 scale

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
