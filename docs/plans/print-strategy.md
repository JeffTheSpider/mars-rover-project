# Phase 1 Print Strategy — CTC Bizer (PLA)

## Printer: CTC 3D Bizer (MakerBot Replicator Clone)
- **Build volume**: 225 × 145 × 150mm
- **Material**: PLA only
- **File format**: x3g (gcode → GPX converter → x3g → SD card)
- **Slicer**: Cura + GPX plugin
- **Nozzle**: 0.4mm (assumed)

---

## Print Order (test small → build big)

### Phase A: Calibration (before ANY rover parts)

| # | Part | Size (mm) | Time | Purpose |
|---|------|-----------|------|---------|
| A1 | Calibration Test Card | 80×30×5 | ~20min | Measure hole accuracy, XY accuracy |
| A2 | Bearing Test Piece | 30×30×10 | ~15min | 608ZZ press-fit validation |
| A3 | 20mm Calibration Cube | 20×20×20 | ~15min | XYZ dimensional accuracy |

**After printing A1-A3:**
1. Measure all holes with calipers
2. Measure outer dimensions
3. Test-fit 608ZZ bearing in A2
4. Update `cad/scripts/printer_calibration.py` with corrections
5. Reprint A2 if bearing fit is wrong (adjust ±0.05mm)

### Phase B: Individual Components (one of each, test fit)

| # | Part | Size (mm) | Qty Final | Orientation | Supports | Time Est |
|---|------|-----------|-----------|-------------|----------|----------|
| B1 | Wheel | 86×86×32 | 6 | Hub down | None | ~2hr |
| B2 | Steering bracket | 35×25×40 | 4 | Flat face down | None | ~45min |
| B3 | Fixed wheel mount | 25×25×30 | 2 | Flat face down | None | ~30min |
| B4 | Motor clip test | 20×15×12 | 1 | Clip opening up | None | ~15min |
| B5 | Bogie arm segment | 120×15×12 | 2 | Flat (lengthwise) | None | ~1.5hr |
| B6 | Rocker arm segment | 180×20×15 | 2 | Flat (lengthwise) | Minimal | ~2hr |
| B7 | Diff bar adapter | 30×22×22 | 3 | Flat end down | None | ~30min |

**After printing B1-B7:**
1. Test-fit all 608ZZ bearings in their seats
2. Test-fit N20 motors in clips/brackets
3. Test-fit M8 bolts through pivot holes
4. Test-fit SG90 servos in steering brackets
5. Check all clearances with parts assembled by hand
6. Update tolerances if needed, reprint failed parts

### Phase C: Full Production Run

| # | Part | Qty | Total Print Time Est |
|---|------|-----|---------------------|
| C1 | Wheels (×6) | 6 | ~12hr |
| C2 | Steering brackets (×4) | 4 | ~3hr |
| C3 | Fixed mounts (×2) | 2 | ~1hr |
| C4 | Bogie arms (×2) | 2 | ~3hr |
| C5 | Rocker arms (×2) | 2 | ~4hr |
| C6 | Diff bar adapters (×3) | 3 | ~1.5hr |
| C7 | Body quadrant FL | 1 | ~8hr |
| C8 | Body quadrant FR | 1 | ~8hr |
| C9 | Body quadrant RL | 1 | ~10hr |
| C10 | Body quadrant RR | 1 | ~10hr |
| C11 | Electronics tray | 1 | ~3hr |
| C12 | Top deck (×4 tiles) | 4 | ~4hr |

**Estimated total print time: ~69 hours** (matches EA-08 estimate)

---

## Print Settings by Part Type

### Structural Parts (rocker, bogie, steering brackets, mounts)
```
Layer height:     0.2mm
Perimeters:       4 (1.6mm walls)
Infill:           50% gyroid
Top/bottom:       5 solid layers
Speed:            40mm/s
Temp (nozzle):    200-210°C PLA
Temp (bed):       60°C
Cooling:          100% after layer 3
```

### Wheels
```
Layer height:     0.2mm
Perimeters:       4
Infill:           50% gyroid
Top/bottom:       5 solid layers
Speed:            40mm/s
Notes:            Print hub-down. Grousers print vertically (strong).
                  O-ring grooves face up (good surface finish).
```

### Body Panels
```
Layer height:     0.2mm
Perimeters:       4 (4mm walls — increased for structural strength)
Infill:           20% gyroid
Top/bottom:       4 solid layers
Speed:            45mm/s
Brim:             8mm (large footprint on CTC Bizer)
Notes:            Print open-side up. Internal ribs print with body.
                  Panel line grooves and corner chamfers are cosmetic.
```

### Bearing Seats (all parts with 608ZZ pockets)
```
CRITICAL DIMENSIONS — print slowly near bearing seat
Layer height:     0.2mm (do NOT use adaptive)
Perimeters:       4 minimum around seat
Speed:            30mm/s for perimeters near seat
Bore diameter:    22.15mm (adjust per calibration)
Seat depth:       7.2mm
Entry chamfer:    0.3mm x 45°
```

### Heat-Set Insert Bosses
```
Hole diameter:    4.8mm
Hole depth:       5.5mm
Min wall around:  2.4mm (3 perimeters)
Chamfer at top:   0.5mm x 45°
Install temp:     170-180°C (PLA — LOWER than PETG!)
```

---

## CTC Bizer-Specific Notes

### Bed Adhesion
- PLA on heated bed (60°C) with glue stick or painter's tape
- CTC Bizer has heated aluminium bed
- For large flat parts (body panels): use brim (5mm, 3 lines)
- For small parts (brackets, adapters): skirt only

### Dual Extruder
- Use LEFT extruder only (unless doing dual-colour)
- Right extruder: remove nozzle and park, or it may catch on prints
- Alternatively: remove right extruder assembly to avoid interference

### File Workflow
```
Fusion 360 → Export STL
         ↓
    Cura → Slice → Save gcode
         ↓
    GPX → Convert gcode → x3g
         ↓
    SD Card → Insert in CTC Bizer → Print
```

### Bed Size Constraints
| Part | Dimensions | Fits on 225×145? | Notes |
|------|-----------|-----------------|-------|
| Wheel (86mm dia) | 86×86 | YES | Easily |
| Steering bracket | 35×25 | YES | Multiple per bed possible |
| Bogie arm | 120×15 | YES | Along 145mm axis |
| Rocker arm | 180×20 | YES | Along 225mm axis |
| Body FL quadrant | ~220×130 | YES | Fits 225mm with 2.5mm margin each side |
| Body RL quadrant | ~220×130 | YES | Pivot boss trimmed to quadrant bounds |

### Known CTC Bizer Issues
- **First layer**: May need manual Z offset adjustment via thumbscrews
- **Belt tension**: Check X and Y belts — stretch over time
- **Nozzle clogs**: After sitting unused, do cold pull with nylon to clean
- **Filament feed**: Dual extruder feed mechanism can be finicky
- **Cooling**: Stock fan may be inadequate — consider print speed reduction
- **Firmware**: May need Sailfish update for better performance

---

## Tolerance Compensation Strategy

After calibration prints, apply corrections globally:

```
Measured hole too small by Xmm:
  → Increase all hole diameters by Xmm in CAD

Measured hole too big by Xmm:
  → Decrease all hole diameters by Xmm in CAD

Measured outer dimension too small by Xmm:
  → Increase outer dimensions by Xmm in CAD
  → OR adjust slicer XY compensation

608ZZ bearing too tight:
  → Increase bore from 22.15 to 22.20mm (0.05mm steps)

608ZZ bearing too loose:
  → Decrease bore from 22.15 to 22.10mm

N20 motor clip too tight:
  → Increase clip inner width from 12.2 to 12.3mm

N20 motor clip too loose:
  → Decrease clip inner width from 12.2 to 12.1mm
```

All corrections feed into `cad/scripts/printer_calibration.py` which
is imported by all component scripts. Change once, rebuild all.

---

## Strength Considerations for PLA

### Weak Points
- **Layer adhesion** (Z-axis): PLA layers bond at ~60% of bulk strength
- **Print orientation matters**: Load-bearing features should be in XY plane
- **UV degradation**: PLA weakens in sunlight (outdoor use in Phase 2 needs PETG/ASA)
- **Heat sensitivity**: PLA softens at ~60°C (sun-baked surfaces)

### Design for PLA Strength
| Feature | Best Practice |
|---------|--------------|
| Pivot bosses | Print upright, 4+ perimeters, 50%+ infill |
| Motor clips | Print with flex arms in XY plane (layers don't cross snap line) |
| Wheel grousers | Print hub-down so grousers are vertical (strong) |
| Body walls | 4mm walls = 4+ perimeters at 0.4mm nozzle (strong shell) |
| Rocker/bogie arms | Print flat — bending loads in XY plane (strong direction) |

### Worst Orientations (AVOID)
- Wheel printed on its side (grousers would delaminate)
- Steering bracket printed upside down (bearing seat quality poor)
- Rocker arm printed standing up (bending loads across layers)

---

## Per-Part Slicer Profile Table

Comprehensive slicer settings for every Phase 1 part on the CTC Bizer.

| Part | Walls | Infill% | Pattern | Layer (mm) | Speed (mm/s) | Brim | Support | Notes |
|------|-------|---------|---------|------------|---------------|------|---------|-------|
| Calibration Test Card | 3 | 30 | Grid | 0.2 | 40 | No | No | Measure first |
| Bearing Test Piece | 4 | 50 | Gyroid | 0.2 | 30 | No | No | Slow for bearing seat |
| Wheel (PLA rim) | 4 | 50 | Gyroid | 0.2 | 40 | No | No | Hub-side down |
| TPU Tire (friend) | 3 | 100 | - | 0.2 | 25 | No | No | TPU 95A, 210-230°C |
| Steering Bracket | **5** | **60** | Gyroid | **0.16** | **30** | No | No | Finer layers for bearing seat |
| Fixed Wheel Mount | 4 | 50 | Gyroid | 0.2 | 35 | No | No | Horizontal shaft exit |
| Servo Mount | 4 | 50 | Gyroid | 0.2 | 35 | No | No | Flat face down |
| Bogie Arm | 4 | 50 | Gyroid | 0.2 | 40 | No | No | Flat (15mm face down) |
| Rocker Arm (×2) | 4 | 50 | Gyroid | 0.2 | 40 | No | Minimal | Print flat |
| Diff Bar Adapter | 4 | 50 | Gyroid | 0.2 | 35 | No | No | Flat end down |
| Body Quadrant (×4) | **4** | 20 | Gyroid | 0.2 | 45 | **8mm** | No | Open face up, 4mm walls |
| Top Deck Tile (×4) | 3 | 20 | Grid | 0.2 | 50 | 5mm | No | Flat (panel down) |
| Electronics Tray | 3 | 30 | Gyroid | 0.2 | 40 | 5mm | No | Flat bottom down |
| Strain Relief Clip | 3 | **40** | Gyroid | 0.2 | 35 | No | No | Higher infill for snap-fit |
| Fuse Holder Bracket | 3 | 30 | Gyroid | 0.2 | 40 | No | No | Standard |
| Switch Mount Plate | 3 | 20 | Grid | 0.2 | 50 | No | No | Thin, cosmetic |

**Bold** = differs from default profile for that part type.

### Key Slicer Settings Notes

1. **Steering bracket at 0.16mm layers**: The 608ZZ bearing seat is the tightest tolerance feature. Finer layers give better bore accuracy and surface finish.
2. **Body quadrant 8mm brim**: Large footprint (220×130mm) on CTC Bizer's 225×145 bed. Brim prevents corner lifting.
3. **Strain relief clip 40% infill**: Snap-fit arms need strength to flex without breaking.
4. **Body walls 4mm = 4 perimeters**: At 0.4mm nozzle and ~0.45mm line width, 4 perimeters ≈ 1.8mm per side. Slicer fills remaining with infill.

---

## Wall Strength Analysis (PLA)

### Wall Count vs Strength (0.4mm nozzle, 0.45mm line width)

| Walls | Total (mm) | Tensile (MPa)* | Use Case |
|-------|-----------|----------------|----------|
| 2 | 0.9 | ~20 | Cosmetic only (top deck, switch plate) |
| 3 | 1.35 | ~30 | Light structural (body panels, tray) |
| 4 | 1.8 | ~40 | Moderate structural (wheels, rocker/bogie arms) |
| 5 | 2.25 | ~45 | High structural (steering bracket bearing walls) |

*Approximate — PLA perimeters are stronger than infill because continuous extrusion.

### Infill Pattern Ranking (Strength per gram)

1. **Gyroid** — Best all-round: isotropic, good interlayer bonding, vibration-damping
2. **Cubic** — Good compression strength, slightly more material than gyroid
3. **Grid** — Good for thin cosmetic parts, weak in one axis
4. **Lines** — Weakest, only for non-structural parts

### Print Orientation Rules

| Load Direction | Best Orientation |
|---------------|-----------------|
| Bending (XY) | Print flat — layers parallel to bending plane |
| Compression (Z) | Print upright — layers perpendicular to load |
| Tension (Z) | AVOID — weakest direction (layer adhesion) |
| Shear | Print flat — maximum layer overlap area |

**Rule of thumb**: Orient so that the primary load direction is in the XY plane (across layers, not splitting them apart).
