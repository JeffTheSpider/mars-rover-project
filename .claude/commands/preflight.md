---
description: Pre-print checklist — verify STL, check bed fit, estimate filament, Cura/GPX workflow
argument-hint: <STL filename or part name>
allowed-tools: Bash(*), Read, Glob, Grep, Agent
---

# Pre-Print Checklist

Run a complete pre-print validation for the Mars Rover project before sending a part to the CTC Bizer.

## Printer Specs (CTC Bizer)
- **Bed**: 225 × 145 × 150mm
- **Material**: PLA only
- **File format**: x3g via GPX (`gpx -m cr1d input.gcode output.x3g`)
- **Slicer**: Cura → gcode → GPX → x3g → SD card
- **Extruders**: Dual (use left only)
- **Heated bed**: 60°C + glue stick or painter's tape
- **Heat-set inserts**: 170–180°C (PLA range)

## Target: $ARGUMENTS

## Checklist Steps

### 1. Locate STL File
- Search `3d-print/` subdirectories for the STL matching the argument
- If not found, check if the CAD script exists in `cad/scripts/` — remind user to run BatchExportAll in Fusion 360
- Report: filename, path, file size, last modified date

### 2. STL Analysis
- Use the 3dprint MCP server's `get_stl_info` tool to get dimensions
- If MCP unavailable, use `python3` with numpy-stl or report that manual check needed
- Report: X × Y × Z dimensions in mm

### 3. Bed Fit Check
- Compare STL bounding box to 225 × 145 × 150mm
- Check ALL orientations — suggest optimal orientation if default doesn't fit
- If part exceeds bed in all orientations: **FAIL** — suggest splitting or scaling
- Report: PASS/FAIL with orientation recommendation

### 4. Wall Thickness Check
- Cross-reference the part's CAD script in `cad/scripts/` for WALL parameter
- Minimum recommended: 2.0mm for structural, 1.5mm for non-structural
- Report: wall thickness and whether it meets minimum

### 5. Filament Estimate
- Rough estimate: volume (cm³) × 1.24 g/cm³ (PLA density) × 1.15 (infill + support waste)
- Report: estimated weight (grams) and approximate print time at 50mm/s

### 6. Cura Settings Recommendation
Based on the part type, suggest settings:
- **Structural** (suspension, steering, mounts): 0.2mm layer, 40-60% infill, 3-4 walls, brim
- **Body panels** (quadrants, deck): 0.2mm layer, 15-20% infill, 3 walls, brim
- **Test pieces** (calibration, bearing test): 0.15mm layer, 30% infill, 3 walls
- **Wheels**: 0.2mm layer, 30% infill, 4 walls, no supports
- Report: layer height, infill %, walls, support needed, adhesion type

### 7. Post-Print Reminders
- Heat-set insert locations (if applicable — check CAD script for INSERT_* parameters)
- Bearing seats that need test-fitting (608ZZ: 22.15mm bore)
- Parts that mate with this one (check assembly dependencies)

### 8. GPX Command
Generate the exact GPX command:
```
gpx -m cr1d <filename>.gcode <filename>.x3g
```

## Output Format
Present as a clear checklist with PASS/FAIL/WARN for each step and a final GO/NO-GO recommendation.
