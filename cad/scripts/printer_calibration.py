"""
Printer Calibration Config
==========================

Stores measured tolerances from calibration test prints on the CTC Bizer.
All rover component scripts import from this file so changing one value
here updates ALL parts.

Usage:
    from printer_calibration import get_corrections

    corr = get_corrections()
    actual_bore = design_bore + corr["hole_oversize"]

After printing the calibration test card, measure each hole with
calipers and update the values below.
"""


# ---------------------------------------------------------------------------
# Measured calibration values (UPDATE THESE after test prints)
# ---------------------------------------------------------------------------

# How much LARGER holes print vs designed diameter (mm)
# Positive = holes come out bigger than designed (common)
# Negative = holes come out smaller than designed
# Measure the calibration card holes and calculate average error
HOLE_DIAMETER_ERROR_MM = 0.0  # TODO: measure and update

# How much SMALLER outer dimensions print vs designed (mm)
# Positive = parts shrink (PLA typically 0.2-0.5%)
# Measure the calibration card outer dimensions
OUTER_DIMENSION_ERROR_MM = 0.0  # TODO: measure and update

# XY dimensional accuracy (mm per 100mm)
# Measure the 80mm calibration card length, calculate error per 100mm
XY_ERROR_PER_100MM = 0.0  # TODO: measure and update

# Z (layer) dimensional accuracy (mm per 10mm)
# Measure the 5mm calibration card height
Z_ERROR_PER_10MM = 0.0  # TODO: measure and update

# Bearing press-fit adjustment (mm added to 22.0mm OD)
# Start at 0.15mm (as per EA-08), adjust based on bearing test piece
BEARING_PRESS_FIT_OVERSIZE_MM = 0.15  # Updated from bearing test

# First layer squish - does first layer spread wider?
FIRST_LAYER_SPREAD_MM = 0.0  # TODO: measure and update


def get_corrections():
    """Return correction dict for use in CAD scripts."""
    return {
        "hole_oversize": HOLE_DIAMETER_ERROR_MM,
        "outer_shrinkage": OUTER_DIMENSION_ERROR_MM,
        "xy_error_per_100": XY_ERROR_PER_100MM,
        "z_error_per_10": Z_ERROR_PER_10MM,
        "bearing_press_fit": BEARING_PRESS_FIT_OVERSIZE_MM,
        "first_layer_spread": FIRST_LAYER_SPREAD_MM,
    }


def compensate_hole(design_diameter_mm):
    """Return compensated hole diameter for printing (in mm)."""
    return design_diameter_mm - HOLE_DIAMETER_ERROR_MM


def compensate_outer(design_dimension_mm):
    """Return compensated outer dimension for printing (in mm)."""
    return design_dimension_mm + OUTER_DIMENSION_ERROR_MM


def compensate_bearing_seat(nominal_od_mm=22.0):
    """Return bearing seat bore diameter for press-fit (in mm)."""
    return nominal_od_mm + BEARING_PRESS_FIT_OVERSIZE_MM - HOLE_DIAMETER_ERROR_MM


if __name__ == "__main__":
    print("Printer Calibration Config")
    print("=" * 50)
    corr = get_corrections()
    for k, v in corr.items():
        print(f"  {k:.<35} {v:+.3f} mm")
    print()
    print("Compensated dimensions:")
    print(f"  M2 hole (2.0mm design): ........ {compensate_hole(2.0):.2f}mm")
    print(f"  M3 clearance (3.4mm design): ... {compensate_hole(3.4):.2f}mm")
    print(f"  M3 heat-set (4.8mm design): .... {compensate_hole(4.8):.2f}mm")
    print(f"  M8 clearance (8.4mm design): ... {compensate_hole(8.4):.2f}mm")
    print(f"  608ZZ seat (22.0mm + fit): ..... {compensate_bearing_seat():.2f}mm")
