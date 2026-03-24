---
description: Validate STL file — dimensions, manifold check, bed fit, print time estimate
argument: part name or STL path
---

# STL Validation Check

Validate a 3D-printable STL file for the Mars Rover project.

## Steps

1. **Find the STL**: If `$ARGUMENTS` is a part name, look in `D:/Mars Rover Project/3d-print/` subdirectories. If it's a path, use directly.

2. **Get STL info** using `mcp__3dprint__get_stl_info`:
   - Bounding box dimensions (mm)
   - Triangle count
   - Volume (cm³)
   - Whether it's manifold/watertight

3. **Check bed fit** against CTC Bizer:
   - Max: 225 × 145 × 150mm
   - Flag if ANY dimension exceeds bed limits
   - Suggest rotation if part fits in a different orientation

4. **Check dimensions** against EA-08 / generate_rover_params.py:
   - Compare bounding box to expected part dimensions
   - Flag >1mm deviations from spec

5. **Estimate print metrics**:
   - Filament: volume × 1.24 g/cm³ (PLA density) + 15% waste
   - Time estimate: volume / 15 cm³/hr (conservative for CTC Bizer)
   - Layer count: height / 0.2mm

6. **Visualize** using `mcp__3dprint__generate_stl_visualization` (SVG from 3 angles)

7. **Report** a summary table with PASS/FAIL for each check.
