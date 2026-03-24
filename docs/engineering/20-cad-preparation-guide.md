# EA-20: CAD Preparation Guide for Fusion 360

**Document**: EA-20
**Date**: 2026-03-15
**Purpose**: Provide a complete reference for modelling the 0.4-scale Phase 1 prototype rover in Fusion 360, including assembly hierarchy, master dimensions, critical geometry, hardware cutouts, print orientation, and design-for-assembly guidance.
**Depends on**: EA-01 (Suspension), EA-08 (Phase 1 Spec), EA-10 (Ackermann Steering), EA-11 (3D Printing Strategy)

---

## 1. Assembly Structure

### 1.1 Top-Down Assembly Hierarchy

Model the rover as a single Fusion 360 Design with the following component tree. Use top-down modelling: create the skeleton sketch in the top-level component, then derive geometry into child components via projected references.

```
ROVER_P1_040  (root assembly)
  +-- BODY
  |     +-- BODY_FRONT_LEFT
  |     +-- BODY_FRONT_RIGHT
  |     +-- BODY_REAR_LEFT
  |     +-- BODY_REAR_RIGHT
  |     +-- TOP_DECK_COVER
  |     +-- ELECTRONICS_TRAY
  +-- SUSPENSION_LEFT
  |     +-- ROCKER_ARM_LEFT
  |     +-- BOGIE_ARM_LEFT
  +-- SUSPENSION_RIGHT
  |     +-- ROCKER_ARM_RIGHT
  |     +-- BOGIE_ARM_RIGHT
  +-- DIFFERENTIAL
  |     +-- DIFF_BAR_ROD
  |     +-- DIFF_ADAPTER_LEFT
  |     +-- DIFF_ADAPTER_CENTRE
  |     +-- DIFF_ADAPTER_RIGHT
  +-- STEERING_FL
  |     +-- STEERING_BRACKET_FL
  |     +-- SERVO_SG90_FL
  +-- STEERING_FR
  |     +-- STEERING_BRACKET_FR
  |     +-- SERVO_SG90_FR
  +-- STEERING_RL
  |     +-- STEERING_BRACKET_RL
  |     +-- SERVO_SG90_RL
  +-- STEERING_RR
  |     +-- STEERING_BRACKET_RR
  |     +-- SERVO_SG90_RR
  +-- FIXED_MOUNT_ML
  +-- FIXED_MOUNT_MR
  +-- WHEEL_FL
  +-- WHEEL_FR
  +-- WHEEL_ML
  +-- WHEEL_MR
  +-- WHEEL_RL
  +-- WHEEL_RR
  +-- MOTOR_N20_x6  (reusable component, 6 instances)
  +-- BEARING_608ZZ  (reusable component, 11 instances)
  +-- FASTENERS  (folder of reusable bolts/nuts)
```

### 1.2 Component Naming Convention

```
<SYSTEM>_<PART>_<SIDE/POSITION>_<VERSION>

Examples:
  ROCKER_ARM_LEFT_v1
  STEERING_BRACKET_FL_v2
  WHEEL_GENERIC_v1  (instanced 6 times)
  BEARING_608ZZ_v1  (instanced 11 times)
```

- Use UPPER_SNAKE_CASE for component names.
- Suffix with `_v1`, `_v2` etc. when iterating designs.
- Side labels: LEFT / RIGHT for suspension, FL / FR / ML / MR / RL / RR for wheel-corner parts.
- Fasteners and hardware: prefix with `HW_` (e.g., `HW_M8x40_BOLT`).

### 1.3 Coordinate System

**Origin**: Centre of the differential bar, at the body's mid-length, mid-width, and ground level (Z = 0 is ground plane).

| Axis | Direction | Positive Convention |
|------|-----------|---------------------|
| X | Left-right | Positive = right (viewed from behind) |
| Y | Front-back | Positive = forward |
| Z | Up-down | Positive = up |

Key reference planes:
- **XZ plane (Y = 0)**: Middle axle line (ML/MR wheels)
- **YZ plane (X = 0)**: Rover centre line (symmetry plane)
- **XY plane (Z = 0)**: Ground plane

All dimensions below are in the rover coordinate system at 0.4 scale unless otherwise noted.

---

## 2. Master Dimensions Table

All values are Phase 1 (0.4 scale) in millimetres.

### 2.1 Overall Dimensions

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| Body (outer) | Length (Y) | 440 | +/-1.0 | 4 quadrant prints on 225x145mm bed (Y split at Y=0) |
| Body (outer) | Width (X) | 260 | +/-1.0 | 4 quadrant prints on 225x145mm bed (X split at X=0) |
| Body (outer) | Height (Z) | 80 | +/-0.5 | Open-top box frame |
| Body (inner cavity) | Length | 434 | derived | 3mm walls each end |
| Body (inner cavity) | Width | 254 | derived | 3mm walls each side |
| Body (inner cavity) | Height | 74 | derived | 3mm floor, open top |
| Body wall thickness | Outer walls | 3.0 | +/-0.2 | 4 perimeters at 0.4mm nozzle |
| Body wall thickness | Internal ribs | 2.0 | +/-0.2 | |
| Top deck cover | L x W x H | 440 x 260 x 2 | +/-0.5 | Optional, cosmetic |
| Wheelbase (per side) | Front-to-rear axle (Y) | 360 | +/-1.0 | W1-to-W3 ground spacing |
| Track width | Wheel centre-to-centre (X) | 280 | +/-1.0 | Left to right |
| Ground clearance | Under body frame (Z) | 60 | +/-2.0 | |
| Driving height | Ground to top of body | 420 | reference | Without mast (no mast in Phase 1) |

### 2.2 Rocker Arms (x2)

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| Rocker arm | Total length | 180 | +/-0.5 | Body pivot to front wheel axle |
| Rocker arm | Cross-section outer | 20 x 15 | +/-0.3 | Rectangular tube |
| Rocker arm | Wall thickness | 3.0 | +/-0.2 | |
| Rocker arm | Body pivot bore | 8.0 | H7 (+0.000/+0.015) | For 608ZZ inner race |
| Rocker arm | Body pivot boss OD | 22.1 | +0.0/-0.1 | Press-fit for 608ZZ outer race |
| Rocker arm | Bogie pivot bore | 8.0 | H7 | For 608ZZ inner race |
| Rocker arm | Bogie pivot boss OD | 22.1 | +0.0/-0.1 | Press-fit for 608ZZ |
| Rocker arm | Front motor mount face | 25mm PCD | +/-0.2 | 4x M3 holes on pitch circle |
| Rocker arm | Weight (each) | ~35g | estimate | PLA, 50% gyroid infill |

### 2.3 Bogie Arms (x2)

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| Bogie arm | Total length | 180 | +/-0.5 | W2 axle to W3 axle (full scale 450mm x 0.4) |
| Bogie arm | Pivot to each wheel | 90 | +/-0.3 | Symmetric |
| Bogie arm | Cross-section outer | 15 x 12 | +/-0.3 | Rectangular tube |
| Bogie arm | Wall thickness | 2.5 | +/-0.2 | |
| Bogie arm | Pivot bore | 8.0 | H7 | For 608ZZ |
| Bogie arm | Motor mount faces | 4x M3 | +/-0.2 | Each end |
| Bogie arm | Weight (each) | ~20g | estimate | |

### 2.4 Differential Bar

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| Differential bar | Rod length | 300 | +/-1.0 | 250mm pivot span + 25mm overhang each side |
| Differential bar | Rod OD | 8.0 | h9 | Steel rod, fits 608ZZ bore |
| Differential bar | Rod ID (if tube) | N/A | N/A | Solid 8mm steel rod recommended |
| Diff adapter (x3) | Tube OD | 12.0 | +/-0.3 | Printed end caps |
| Diff adapter | Tube ID | 8.0 | +0.05/-0.00 | Press-fit onto rod |
| Diff adapter | Bearing seat OD | 22.1 | +0.0/-0.1 | For 608ZZ |
| Diff adapter | Bearing seat depth | 7.2 | +/-0.1 | Full 608ZZ width + 0.2mm |
| Diff adapter | Weight (each) | ~5g | estimate | |

### 2.5 Wheels (x6)

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| Wheel | Outer diameter | 80 | +/-0.5 | Including tread grousers |
| Wheel | Width | 32 | +/-0.3 | Tread included |
| Wheel | Hub bore (D-shaft) | 3.1 | +0.05/-0.00 | 0.1mm clearance for N20 3mm D-shaft |
| Wheel | D-flat depth | 0.5 | +/-0.1 | |
| Wheel | Hub boss OD | 10 | +/-0.3 | |
| Wheel | Hub boss length | 8 | +/-0.3 | Full shaft engagement |
| Wheel | Grousers (count) | 12 | -- | Chevron pattern |
| Wheel | Grouser depth | 3.0 | +/-0.2 | |
| Wheel | Grouser width (base) | 3.0 | +/-0.2 | |
| Wheel | Spoke count | 6 | -- | With flex zones |
| Wheel | M2 grub screw hole | 2.0 | +/-0.1 | Perpendicular to shaft |
| Wheel | Weight (each) | ~25g | estimate | |

### 2.6 Steering Assembly (x4 corners)

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| Steering bracket | L x W x H | 35 x 25 x 40 | +/-0.3 | Rotates on 608ZZ |
| Steering bracket | Bearing seat OD | 22.1 | +0.0/-0.1 | Top face |
| Steering bracket | Bearing seat depth | 7.2 | +/-0.1 | |
| Steering bracket | Pivot bore | 8.0 | H7 | M8 bolt through |
| Steering bracket | N20 clip inner W | 12.2 | +0.1/-0.0 | 0.2mm clearance |
| Steering bracket | N20 clip inner H | 10.2 | +0.1/-0.0 | |
| Steering bracket | Clip wall thickness | 2.0 | +/-0.2 | |
| Steering bracket | Snap tab protrusion | 0.5 | +/-0.1 | |
| Steering bracket | Motor shaft exit hole | 4.0 | +/-0.2 | |
| Steering bracket | Servo horn length | 15 | +/-0.3 | SG90 horn |
| Steering bracket | Weight (each) | ~12g | estimate | |
| Steering | Max angle | +/-35 deg | -- | Limited by arm geometry |
| Steering | Pivot-to-wheel-centre | 20 | +/-0.5 | Vertical offset |
| Steering | Wheel-to-arm clearance | >= 5 | minimum | At full lock (35 deg) |

### 2.7 Fixed Wheel Mounts (x2, middle wheels)

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| Fixed mount | L x W x H | 25 x 25 x 30 | +/-0.3 | |
| Fixed mount | N20 motor clip | Same as steering bracket clip | | |
| Fixed mount | M3 bolt holes to bogie | 2x M3 clearance (3.4mm) | +/-0.1 | |
| Fixed mount | Weight (each) | ~8g | estimate | |

### 2.8 N20 Gearmotor (x6)

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| N20 motor | Body dimensions | 12 x 10 x 25 | reference | Motor body only |
| N20 motor | Gearbox length | 12 | reference | Total length = 37mm |
| N20 motor | Total length | 37 | reference | Motor + gearbox |
| N20 motor | Shaft diameter | 3.0 (D-shaft) | reference | |
| N20 motor | Shaft protrusion | 10 | reference | |
| N20 motor | Mounting screws | 2x M2, 9mm centres | reference | |
| N20 motor | Weight (each) | ~20g | reference | |

### 2.9 608ZZ Bearing (x11)

| Part | Dimension | Value (mm) | Tolerance | Notes |
|------|-----------|------------|-----------|-------|
| 608ZZ | Inner diameter (bore) | 8.0 | -- | Standard |
| 608ZZ | Outer diameter | 22.0 | -- | Standard |
| 608ZZ | Width | 7.0 | -- | Standard |
| 608ZZ | Seal type | ZZ | -- | Metal shields both sides |
| 608ZZ | Weight (each) | 12g | -- | |

### 2.10 Body Features

| Feature | Dimension | Value (mm) | Tolerance | Notes |
|---------|-----------|------------|-----------|-------|
| Rocker pivot holes | Bore | 8.0 | H7 | At Y=0, Z=+60, X=+/-125 |
| Rocker pivot holes | Boss OD | 22.1 | +0.0/-0.1 | 608ZZ seat |
| Battery tray recess | L x W x H | 70 x 35 x 25 | +/-1.0 | Floor centre, fits 2S 2200mAh LiPo |
| Cable routing channels | Cross-section | 10 x 10 | +/-0.5 | Grooves in floor |
| Switch mount | Diameter | 15 | +/-0.3 | Rear wall, power switch |
| Ventilation slots | Width x count | 3mm x 5 | +/-0.2 | Each side wall |
| ESP32 standoffs | 4x M3 | PCD per DevKit | +/-0.3 | 69x25mm board |
| L298N standoffs | 4x M3 | 37mm PCD | +/-0.3 | 43x43mm board, 2 sets |
| Body join seams | Bolts | 12x M3x12 | -- | 6 per seam (Y=0 and X=0), see Section 5.3 |
| Top deck clips | Count | 8 | -- | Snap clips along edges |

### 2.11 Electronics Components (mounting reference)

| Component | Dimensions (mm) | Mount Pattern |
|-----------|----------------|---------------|
| ESP32-S3 DevKit | 69 x 25 | 4x M3 standoffs |
| L298N driver (x2) | 43 x 43 x 27 | 4x M3 standoffs, 37mm PCD |
| 2S LiPo 2200mAh | 70 x 35 x 18 | Battery tray + Velcro strap |
| Power switch | 15mm panel mount | Rear wall hole |
| Mini breadboard | 47 x 35 | Adhesive back |

---

## 3. Critical Geometry

### 3.1 Rocker Pivot Point Location

The rocker pivots are the primary connection between the body and suspension.

| Parameter | Value | Reference |
|-----------|-------|-----------|
| X position | +/-125mm from centre line | Inset from body side wall (260/2 - 5mm clearance) |
| Y position | 0mm (middle axle line) | Aligns with XZ plane |
| Z position | +60mm above ground | Body floor at Z=60, pivots at floor level |
| Pivot axis | Parallel to Y axis | Rocker swings in the XZ plane (roll motion) |

### 3.2 Bogie Pivot Point Location

Each bogie pivots at the rear end of the rocker arm.

| Parameter | Value | Reference |
|-----------|-------|-----------|
| Relative to rocker body pivot | 180mm along rocker arm | At the rocker's far end from the front wheel |
| X offset from rocker pivot | 0mm | Same X as rocker (coplanar) |
| Pivot axis | Parallel to X axis | Bogie swings in the YZ plane (pitch motion) |

At neutral suspension (flat ground):
- Bogie pivot Y = 0mm (same Y as rocker pivot, middle axle line)
- Bogie pivot Z = approximately +40mm (depends on arm angle at rest)

### 3.3 Differential Bar Pivot and Linkage Points

```
Front View (looking forward, +Y into page):

         [Centre Pivot]
         X=0, Y=0, Z=+60
        /                 \
  100mm                    100mm
      /                       \
[Left End]              [Right End]
X=-100, Z=+60           X=+100, Z=+60
    |                        |
  [Left Rocker]        [Right Rocker]
  Pivot                  Pivot
  X=-125                 X=+125
```

| Point | X (mm) | Y (mm) | Z (mm) | Notes |
|-------|--------|--------|--------|-------|
| Diff bar centre pivot | 0 | 0 | +60 | Attached to body frame |
| Diff bar left end | -100 | 0 | +60 | Connected to left rocker via linkage |
| Diff bar right end | +100 | 0 | +60 | Connected to right rocker via linkage |
| Left rocker pivot | -125 | 0 | +60 | On body frame |
| Right rocker pivot | +125 | 0 | +60 | On body frame |

The 25mm gap between diff bar end (X=+/-100) and rocker pivot (X=+/-125) is bridged by the differential adapter linkage.

**Differential bar angular range**: +/-20 degrees from horizontal.

### 3.4 Steering Axis Locations (4 Corners)

Steering pivots are vertical axes (parallel to Z) at each steered wheel position.

| Wheel | X (mm) | Y (mm) | Z (mm) | Notes |
|-------|--------|--------|--------|-------|
| FL steering pivot | -140 | +180 | ~+40 | On rocker arm front end |
| FR steering pivot | +140 | +180 | ~+40 | On rocker arm front end |
| RL steering pivot | -140 | -180 | ~+40 | On bogie arm rear end |
| RR steering pivot | +140 | -180 | ~+40 | On bogie arm rear end |
| ML (fixed, no steering) | -140 | 0 | ~+40 | Direct mount on bogie |
| MR (fixed, no steering) | +140 | 0 | ~+40 | Direct mount on bogie |

### 3.5 Wheel Axis Offsets from Steering Axis

The wheel rotates about the motor shaft axis (horizontal, parallel to X). This axis is offset below the steering pivot axis (vertical, parallel to Z).

| Parameter | Value (mm) | Notes |
|-----------|------------|-------|
| Vertical offset (steering pivot to wheel centre) | 20 | Wheel axle is 20mm below steering pivot |
| Lateral offset (steering axis to wheel centre plane) | 0 | Wheel centre is directly below steering axis |
| Steering bracket height accounts for this offset | 40 | 608ZZ at top, motor clip at bottom |

### 3.6 Wheel Positions at Neutral (Flat Ground)

| Wheel | Label | X (mm) | Y (mm) | Z (mm) | Notes |
|-------|-------|--------|--------|--------|-------|
| Front-left | W1 / FL | -140 | +180 | +40 | Centre of wheel (radius = 40mm, ground at Z=0) |
| Middle-left | W2 / ML | -140 | 0 | +40 | |
| Rear-left | W3 / RL | -140 | -180 | +40 | |
| Rear-right | W4 / RR | +140 | -180 | +40 | |
| Middle-right | W5 / MR | +140 | 0 | +40 | |
| Front-right | W6 / FR | +140 | +180 | +40 | |

### 3.7 Suspension Articulation Range

| Motion | Range | Limit |
|--------|-------|-------|
| Rocker swing (roll) | +/-25 degrees | Mechanical stop on body |
| Bogie swing (pitch) | +/-20 degrees | Limited by arm geometry |
| Differential bar twist | +/-20 degrees | One rocker up = other down |
| Body pitch halving | Diff bar averages left/right | Body tilts half the angle of either side |

---

## 4. Bearing & Hardware Cutouts

### 4.1 608ZZ Bearing Press-Fit Holes

All 11 bearing locations use the same pocket geometry.

| Feature | Dimension (mm) | Notes |
|---------|---------------|-------|
| Bearing seat bore diameter | 22.1 | 0.1mm oversize for PLA press fit (PLA shrinks ~0.2-0.4%) |
| Bearing seat depth | 7.2 | Full 608ZZ width (7mm) + 0.2mm clearance |
| Shaft through-hole | 8.0 | Bearing inner race sits on shaft |
| Retention feature | Printed lip (0.5mm) or snap ring groove | Prevents bearing walking out |
| Chamfer at entry | 0.3mm x 45 deg | Guides bearing during installation |

**Critical note**: Test-print a bearing test block before printing structural parts. Adjust the 22.1mm bore +/-0.1mm based on your printer's actual dimensional accuracy. Target: bearing presses in firmly by hand, no hammer needed.

### 4.2 M3 Heat-Set Insert Holes

Per EA-11 specifications, adapted for PLA.

| Feature | Dimension (mm) | Notes |
|---------|---------------|-------|
| Insert type | M3 x 5.7mm OD x 4.6mm length | Brass, knurled |
| Hole diameter | 4.8 | Undersized vs 5.7mm OD; plastic flows around knurls |
| Hole depth | 5.5 | 1mm deeper than insert for full seating |
| Wall thickness around hole | >= 2.4 | 3 perimeters at 0.4mm line width minimum |
| Chamfer at top | 0.5mm x 45 deg | Guides insert during installation |
| Bottom | Flat (blind hole) | Unless through-hole specifically needed |
| Installation temperature | 170-180 deg C | For PLA (lower than PETG to prevent warping) |

**Quantity needed**: 46 inserts across all parts (12 body join seams, remainder for standoffs, brackets).

### 4.3 8mm Shaft Holes

For M8 bolts and the differential bar steel rod.

| Feature | Dimension (mm) | Notes |
|---------|---------------|-------|
| Shaft hole diameter | 8.0 | H7 tolerance: +0.000 / +0.015mm |
| M8 bolt clearance hole | 8.4 | Where bolt passes through (not bearing seat) |
| Washer recess (optional) | 16mm dia x 1.5mm deep | For M8 washer counterbore |

### 4.4 SG90 Servo Mounting Pattern

| Feature | Dimension (mm) | Notes |
|---------|---------------|-------|
| Servo body | 22.2 x 11.8 x 22.7 (without tabs) | Standard SG90 |
| Servo body + tabs | 32.2 x 11.8 x 22.7 | Tabs add 5mm each side |
| Mounting tab holes | 2x M2 clearance (2.2mm) | One each side |
| Tab hole spacing | 27.5mm centre-to-centre | Across the servo body |
| Tab hole to servo centre | 5mm from body edge | |
| Shaft centre from edge | 6mm from tab edge | Offset from centre |
| Horn arm length | 15mm | Single-arm horn |
| Horn spline | 21T, 4.8mm OD | Standard micro servo spline |
| Servo pocket depth | 12mm minimum | Clears body below tabs |

### 4.5 N20 Motor Mount Pattern

Using snap-fit clip design (not screws).

| Feature | Dimension (mm) | Notes |
|---------|---------------|-------|
| Motor body envelope | 12 x 10 x 37 (with gearbox) | Total L includes gearbox |
| Clip inner width | 12.2 | 0.2mm clearance on motor body |
| Clip inner height | 10.2 | 0.2mm clearance |
| Clip wall thickness | 2.0 | Flex arms |
| Snap tab protrusion | 0.5 | Retains motor in clip |
| Shaft exit hole | 4.0 diameter | Centred on motor face |
| Alternative: M2 screw holes | 2x M2, 9mm centres | If clip proves unreliable |

---

## 5. Print Orientation & Segmentation

### 5.1 Print Orientation for Each Part

| Part | Print Orientation | Rationale | Support Needed |
|------|-------------------|-----------|----------------|
| Body quadrants (x4) | Flat (XY plane, floor on bed) | Largest face down, structural floor; all quadrants ~220x130mm fit on 225x145mm bed | Minimal (teardrop pivot holes on inner quadrants) |
| Top deck cover | Flat (outer face on bed) | Best surface finish on visible side | None |
| Rocker arm (x2) | On side (longest axis horizontal) | Load axis along layer lines, not across | Minimal (teardrop bearing holes) |
| Bogie arm (x2) | On side | Same rationale as rocker | Minimal |
| Diff bar adapters (x3) | Upright (bearing seat on top) | Bearing bore prints as circle in XY | None |
| Wheels (x6) | Flat (tread face on bed, axle vertical) | Strongest axis is radial, smooth tread surface | None (design spokes for bridging) |
| Steering brackets (x4) | Upright (bearing seat on top, motor clip on bottom) | Bearing bore in XY, motor clip overhang manageable | Yes (motor clip overhang) |
| Fixed wheel mounts (x2) | Upright | Motor clip on bottom | Minimal |
| Bearing test piece | Any orientation matching target part | Validates bore dimensions | Minimal |

### 5.2 Segmentation Plan

The body exceeds the CTC 225×145mm bed in both axes. All other parts fit comfortably.

| Part | Full Size | Exceeds Bed? | Segments | Segment Size | Join Method |
|------|-----------|-------------|----------|-------------|-------------|
| Body | 440 x 260 x 80 | Yes (both axes) | 4 quadrants (front-left, front-right, rear-left, rear-right) | All: ~220x130x80 | 12x M3x12 bolts + heat-set inserts + alignment features (see 5.3) |
| Rocker arm | 180mm long | No | 1 piece | Fits in 200mm axis | N/A |
| Bogie arm | 180mm long | No | 1 piece | Fits in 200mm axis | N/A |
| Diff bar | 300mm rod + adapters | No (adapters are small) | Rod + 3 printed adapters | Adapters ~20mm each | Steel rod core |
| Wheels | 80mm dia | No | 1 piece each | Fits easily | N/A |
| Steering brackets | 35 x 25 x 40 | No | 1 piece each | Small | N/A |
| Fixed mounts | 25 x 25 x 30 | No | 1 piece each | Small | N/A |

**Note on rocker arms**: At 180mm length, the rocker arm fits within the 225mm bed axis with comfortable margin. Orient the rocker arm along the longest bed axis.

**Note on bogie arms**: At 180mm length (full scale 450mm x 0.4), the bogie arm fits within the 225mm bed axis.

### 5.3 Body Join / Interlock Design

The body is split into 4 quadrants at two planes:
- **Y = 0** (front/rear split, at middle axle line)
- **X = 0** (left/right split at the rover centre line)

Split planes:
- **X = 0**: Left/right split (260mm / 2 = 130mm per side -- fits 145mm bed axis)
- **Y = 0**: Front/rear split at centre (440mm / 2 = 220mm per half -- fits 225mm bed axis)

All 4 quadrants are 220x130mm, which fits comfortably on the CTC Bizer 225x145mm bed without needing diagonal orientation or offset splits.

```
Top view of body quadrants:

              X = 0 (left/right split)
                |
    FRONT-LEFT  |  FRONT-RIGHT
    220x130mm   |  220x130mm
                |
  Y=0 ---------+--------- Y=0 (front/rear split, at centre)
                |
    REAR-LEFT   |  REAR-RIGHT
    220x130mm   |  220x130mm
                |
```

```
Cross-section at Y=0 seam (looking from side):

Front quadrant          Rear quadrant
+----------+  +  +----------+
|  +-[M3]--+--+--+-[insert]-+  |
|  |       | lip | |         |  |
|  +-------+ 10mm+-----------+  |
|          |    |              |
+----------+  +----------+

Same lip/bolt pattern applies to X=0 seam.
```

**Fasteners**:
- Y=0 seam (front/rear): 6x M3x12mm bolts (3 per side wall + 3 through floor)
- X=0 seam (left/right): 6x M3x12mm bolts (3 per front/rear wall + 3 through floor)
- Total: 12x M3x12mm bolts + 12x M3 heat-set inserts for body join

**Alignment features** (critical for 4-segment registration):
- **Dowel pin holes**: 4x 3mm steel dowel pins in the floor at each quadrant corner near the centre cross (+/-20mm from origin). Each pin bridges two adjacent quadrants for precise alignment.
- **Tongue-and-groove joints**: Along both seam lines, add a 2mm x 2mm tongue on one half and a matching 2.2mm x 2.2mm groove on the other. This prevents lateral sliding during assembly and adds shear strength.
- **Alignment tabs**: 2x 5mm wide x 10mm long x 3mm tall interlocking tabs at each seam midpoint, alternating male/female between adjacent quadrants. Provides positive location during bolt-up.

**Assembly order**: Start with rear-left quadrant. Add rear-right (align X=0 seam, insert dowels, bolt). Then add front-left to rear-left (align Y=0 seam). Finally add front-right, aligning both seams simultaneously.

### 5.4 Support Structure Requirements

| Part | Support Location | Support Type | Removal Notes |
|------|-----------------|-------------|---------------|
| Body quadrants | Rocker pivot holes (horizontal cylinders, on inner quadrants only) | Use teardrop profile to avoid supports | Ream to round after printing |
| Rocker arm | Bearing boss holes | Teardrop profile | Ream with 22mm drill |
| Bogie arm | Bearing boss hole | Teardrop profile | Ream |
| Steering bracket | Motor clip overhang at bottom | Tree supports in slicer | Remove carefully |
| All other parts | None | Designed for supportless printing | N/A |

---

## 6. Design for Assembly

### 6.1 Assembly Sequence

Build from the inside out, bottom to top, one side then the other.

**Stage 1: Prepare Printed Parts**
1. Remove all support material
2. Ream all 608ZZ bearing seats with 22mm drill bit (test fit each bearing)
3. Ream all 8mm shaft holes
4. Ream all D-shaft bores in wheel hubs
5. Install all M3 heat-set inserts (soldering iron at 170-180 deg C, 3 seconds each)
6. Dry-fit all joints before adding fasteners

**Stage 2: Build Left Suspension**
1. Press 608ZZ into rocker arm body-pivot boss
2. Press 608ZZ into rocker arm bogie-pivot boss
3. Press 608ZZ into bogie arm rocker-pivot boss
4. Join rocker-to-bogie via M8 bolt + washers + nyloc nut (finger-tight, must rotate freely)
5. Mount steering bracket to rocker front end (608ZZ + M8 bolt)
6. Mount fixed motor bracket to bogie middle position
7. Mount steering bracket to bogie rear position

**Stage 3: Build Right Suspension**
8. Repeat steps 1-7 for right side

**Stage 4: Install Differential Bar**
9. Slide 8mm steel rod through centre adapter (with 608ZZ bearing, mounted in body frame)
10. Attach left end adapter to left rocker pivot linkage
11. Attach right end adapter to right rocker pivot linkage
12. Verify both rockers seesaw freely

**Stage 5: Mount Suspension to Body**
13. Join body quadrants: rear-left + rear-right first, then front-left + front-right, then front to rear (12x M3x12 + dowel pins + alignment tabs)
14. Insert M8 bolts through body rocker pivot holes
15. Slide on rocker arm bearings, add washers and nyloc nuts
16. Verify +/-25 deg rocker swing range

**Stage 6: Motors and Wheels**
17. Snap N20 motors into all 6 motor clips
18. Route motor wires through arms to body cavity
19. Press wheels onto 3mm D-shafts
20. Secure with M2 grub screws
21. Verify all 6 wheels spin freely

**Stage 7: Servos**
22. Mount SG90 servos in steering brackets (M2 screws)
23. Attach servo horns to steering pivot arms
24. Centre all servos (1500us PWM = straight ahead)
25. Verify +/-35 deg steering range without binding

**Stage 8: Electronics**
26. Mount ESP32-S3 on M3 standoffs
27. Mount L298N boards on M3 standoffs
28. Wire motors to L298N outputs
29. Wire L298N control pins to ESP32 GPIOs
30. Wire servo signals to ESP32 GPIOs (power from 5V rail)
31. Secure battery with Velcro strap in battery tray
32. Connect battery via power switch

### 6.2 Access Panel Locations

| Panel | Location | Purpose | Attachment |
|-------|----------|---------|------------|
| Top deck cover | Full top of body | Access all electronics | 8x snap clips (tool-free removal) |
| Battery access | Floor centre (flip rover) | Battery swap | Velcro strap release |
| Power switch | Rear wall | On/off without opening | 15mm panel mount switch |

### 6.3 Cable Routing Channel Dimensions

| Feature | Dimension (mm) | Notes |
|---------|---------------|-------|
| Floor channels | 10 x 10 cross-section | Grooves in body floor |
| Channel path | From each side wall to centre | Motor wires route inward to drivers |
| Servo wire entry | Through arm/bracket | 3-wire (signal/power/ground) per servo |
| Minimum bend radius | 15mm | For stranded wire harness |
| Wire exit from arm | 5mm diameter hole | At rocker pivot (allows arm rotation) |

### 6.4 Clearance Requirements

| Clearance | Minimum (mm) | Condition | Notes |
|-----------|-------------|-----------|-------|
| Wheel to arm (steering) | 5 | At full lock (+/-35 deg) | Wheel rear edge swings 18.4mm at 35 deg |
| Wheel to body | 10 | At max suspension travel | Prevent rubbing |
| Rocker arm to body | 3 | At +/-25 deg swing | Side clearance |
| Bogie arm to rocker arm | 3 | At +/-20 deg swing | |
| Differential bar to body | 5 | At +/-20 deg twist | |
| Motor wires to moving parts | 5 | Throughout travel range | Prevent pinching |
| Steering bracket to arm end | 2 | All positions | Bearing width + washer stack |

---

## 7. Design Checklist

Complete each item before exporting STL files for printing.

### 7.1 Geometry Validation

- [ ] All 608ZZ bearing seats are 22.1mm OD x 7.2mm deep
- [ ] All 8mm shaft holes are correctly sized (H7 for bearing seats, 8.4mm for clearance)
- [ ] All M3 heat-set insert holes are 4.8mm diameter x 5.5mm deep with 0.5mm chamfer
- [ ] All M3 clearance holes are 3.4mm diameter
- [ ] N20 motor clip dimensions: 12.2mm x 10.2mm inner, 2mm walls
- [ ] D-shaft bore is 3.1mm with 0.5mm D-flat
- [ ] SG90 servo pocket and mounting holes match datasheet
- [ ] Body join seams (Y=0 and X=0) each have 10mm overlap lips, 6x M3 bolt positions, dowel pin holes, and tongue-and-groove joints
- [ ] Cable routing channels are at least 10mm x 10mm

### 7.2 Clearance & Motion

- [ ] Animate rocker swing +/-25 deg -- no collisions with body or diff bar
- [ ] Animate bogie swing +/-20 deg -- no collisions with rocker arm
- [ ] Animate diff bar +/-20 deg -- no collisions with body cavity
- [ ] Animate steering +/-35 deg -- wheel clears arm with >= 5mm gap
- [ ] Verify ground clearance >= 60mm at all articulation positions
- [ ] Verify wheel-to-body clearance at max suspension + max steering combined

### 7.3 Assembly Feasibility

- [ ] All fasteners are accessible with standard hex keys (2mm for M3, 5mm for M8)
- [ ] Heat-set inserts can be installed with straight soldering iron access
- [ ] Bearings can be pressed in without obstruction from adjacent features
- [ ] Motor clips allow motor insertion/removal (test with draft model)
- [ ] Servo can be installed/removed from bracket without disassembling other parts
- [ ] Battery tray allows battery insertion/removal with rover assembled
- [ ] Wire routing holes align between adjacent parts at all articulation angles

### 7.4 Print Readiness

- [ ] No part segment exceeds 140mm x 190mm x 150mm (CTC usable volume with margin)
- [ ] Print orientation is set per Section 5.1 table
- [ ] Horizontal bearing holes use teardrop profile (or supports are planned)
- [ ] Wall thickness around all inserts >= 2.4mm
- [ ] No unsupported overhangs > 45 deg (or supports planned)
- [ ] Bridges are <= 30mm span (or supports planned)
- [ ] Part has flat, stable surface on build plate (no rocking)
- [ ] Draft angle on snap-fit features >= 1 deg

### 7.5 Export

- [ ] Export each component as individual STL (not full assembly)
- [ ] Verify STL is watertight (no non-manifold edges) -- use Fusion 360 Mesh > Repair
- [ ] Filename matches component name: `ROCKER_ARM_LEFT_v1.stl`
- [ ] Include print orientation note in filename or companion text file
- [ ] Save Fusion 360 `.f3d` archive backup before exporting

---

*Document EA-20 v1.0 -- 2026-03-15*
