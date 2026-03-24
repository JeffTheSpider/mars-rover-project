# Engineering Analysis 08: Phase 1 Prototype Parts Specification

**Document**: EA-08
**Date**: 2026-03-15
**Purpose**: Define exact dimensions, print specifications, and assembly details for every component of the 0.4-scale prototype rover, providing sufficient detail for CAD modelling and 3D printing.
**Depends on**: EA-01 (Suspension), EA-02 (Drivetrain), EA-05 (Weight Budget), EA-06 (Cost)

---

## 1. Phase 1 Overview

| Parameter | Full Scale | 0.4 Scale | Notes |
|-----------|-----------|-----------|-------|
| Body length | 1100mm | 440mm | Fits 4 quadrants on 225×145mm bed |
| Body width | 650mm | 260mm | Fits 2 segments across width |
| Body height (driving) | 1050mm | 420mm | Without mast (no mast in Phase 1) |
| Wheelbase (front-rear) | 900mm | 360mm | Per-side, front wheel to rear wheel |
| Track width (centre-centre) | 700mm | 280mm | Wheel centre to wheel centre |
| Wheel diameter | 200mm | 80mm | Printable in one piece |
| Wheel width | 80mm | 32mm | Tread included |
| Rocker arm length | 675mm | 270mm | Full span: bogie pivot through body pivot to front wheel (180mm front + 90mm rear) |
| Bogie arm length (total) | 450mm | 180mm | Bogie pivot to each wheel = 90mm |
| Differential bar length | 500mm | 200mm nominal (300mm rod) | Centre to rocker pivot. Buy 300mm rod for 25mm overhang each side. |
| Ground clearance | 150mm | 60mm | Under body frame |
| Target weight | — | ~1.1 kg | EA-05 estimate |
| Target speed | 5 km/h | 2 km/h | Reduced for safety at scale |
| Budget | — | $102 | EA-06 |

---

## 2. Coordinate System

All dimensions reference a right-hand coordinate system:
- **X**: Left-right (positive = right when viewed from behind)
- **Y**: Front-back (positive = forward)
- **Z**: Up-down (positive = up)
- **Origin**: Centre of body, ground level

```
Top View (looking down, +Z towards viewer):

              +Y (forward)
                |
     W1(FL) ----+---- W6(FR)      Front axle line: Y = +180mm
                |
     W2(ML) ----+---- W5(MR)      Middle axle line: Y = 0mm
                |
     W3(RL) ----+---- W4(RR)      Rear axle line: Y = -180mm
                |
    -X --------ORIGIN-------- +X

    Left side:  X = -140mm (wheel centres)
    Right side: X = +140mm (wheel centres)
```

---

## 3. Chassis Body

### 3.1 Body Frame

The body is a rectangular box frame at 0.4 scale: 440mm × 260mm × 80mm tall. At this scale, we skip aluminium extrusion and print the entire frame as interlocking segments.

**Frame design**: Open-top box with internal ribs for mounting electronics.

| Segment | Dimensions (L×W×H) | Print Orientation | Notes |
|---------|-------------------|-------------------|-------|
| Body front-left | 220×130×80mm | Flat (XY plane) | Includes left front rocker pivot mount |
| Body front-right | 220×130×80mm | Flat (XY plane) | Includes right front rocker pivot mount |
| Body rear-left | 220×130×80mm | Flat (XY plane) | Includes left rear electronics bay |
| Body rear-right | 220×130×80mm | Flat (XY plane) | Includes right rear electronics bay |

Each segment fits within the CTC Bizer's 225×145mm bed. All four quadrants are 220×130mm (Y_SPLIT = 0mm, equal split) and fit flat on the bed. The body is split along both the X (left/right) and Y (front/rear) centre lines.

**Join method**: M3 bolts through heat-set inserts at all seams. 6× M3×12mm bolts along the Y-axis (front/rear) join line, 6× M3×12mm bolts along the X-axis (left/right) join line, plus 4× at the centre cross junction (22 bolts total for body joins).

**Wall thickness**: 3mm outer walls, 2mm internal ribs.

**Features to model**:
- 2× rocker pivot holes (left/right): 8mm bore for 608ZZ bearings, located at Y=0, Z=+60mm, X=±125mm
- Electronics mounting bosses: 4× M3 standoffs for ESP32, 4× M3 for L298N drivers
- Battery tray: 70×35×25mm recess in floor centre (fits 2S 2200mAh LiPo)
- Cable routing channels: 10×10mm grooves in floor
- Switch mount: 15mm diameter hole in rear wall for power switch
- Ventilation slots: 5× 3mm slots in each side wall (motor driver cooling)

### 3.2 Top Deck (Optional Cover)

| Parameter | Value |
|-----------|-------|
| Dimensions | 440×260×2mm |
| Material | PLA, 100% infill (thin panel) |
| Attachment | 8× snap clips along edges |
| Features | Decorative panel lines (Mars rover aesthetic) |

This is cosmetic and can be omitted for easier access during development.

### 3.3 Body Print Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PLA | Suitable for Phase 1 indoor testing; Phase 2 should use PETG/ASA for outdoor durability |
| Layer height | 0.2mm | Balance of speed and quality |
| Walls/perimeters | 4 | Structural frame — needs rigidity |
| Infill | 30% gyroid | Good strength-to-weight ratio |
| Top/bottom layers | 5 | Floor takes the weight |
| Support | Minimal — design for supportless printing | Pivot holes are horizontal cylinders — print as vertical posts with teardrop profile |
| Estimated print time | ~7 hrs per segment (28 hrs total for 4 segments) | At 50mm/s |
| Estimated weight | ~110g per segment (440g total frame, slightly more due to extra joining walls) | |

---

## 4. Rocker Arms (2× required)

### 4.1 Geometry

Each rocker arm connects the front wheel axle to the body pivot, with the bogie pivot at the rear end.

```
Side View (left rocker):

    [Body Pivot]
         |
    [Rocker Arm: 180mm]
    /                  \
   W1 (front)    [Bogie Pivot]
   Y=+180mm         Y=0mm
```

| Parameter | Value |
|-----------|-------|
| Total length | 270mm full span (body pivot to front wheel = 180mm, body pivot to bogie pivot = 90mm). Must be printed in 2 halves — see Section 4.3. |
| Cross-section | Rectangular tube: 20mm × 15mm outer, 3mm walls |
| Body pivot end | 8mm bore for 608ZZ bearing, 22mm OD boss |
| Bogie pivot mount | 8mm bore for 608ZZ bearing, 22mm OD boss |
| Front wheel axle mount | Motor mounting face with 4× M3 holes on 25mm PCD |
| Material | PLA |

### 4.2 Rocker Pivot Detail

```
Cross-section at body pivot:

    ┌──────────────────┐
    │    ┌──────────┐  │
    │    │  608ZZ   │  │  22mm OD bearing boss
    │    │  8mm ID  │  │
    │    └──────────┘  │
    └──────────────────┘

Bearing: 608ZZ (8mm ID × 22mm OD × 7mm W)
Shaft: M8 bolt through body frame, nyloc nut
```

### 4.3 Two-Piece Split (Bed Fit)

The full 270mm rocker arm exceeds the CTC Bizer bed (225×145mm) in all orientations, including diagonal (268mm max). The arm is split into two pieces joined by a half-lap joint at the body pivot (Y=0):

```
Split Design:

    FRONT HALF (180mm)          REAR HALF (105mm)
    ┌─────────────────┐         ┌──────────┐
    │ Front wheel     │ Joint   │  Bogie   │
    │ Y=+180mm        │◄──────►│  Y=-90mm  │
    │                 │ at Y=0  │          │
    └─────────────────┘         └──────────┘

Half-lap joint detail (side view):

    Front half         Rear half
    ┌────────┬────┐   ┌────┬──────────┐
    │        │    │   │    │          │
    │ full   │half│   │half│  full    │
    │ height │ht  │   │ht  │  height  │
    │        │    │   │    │          │
    └────────┴────┘   └────┴──────────┘
             ← 15mm overlap →
         2× M3 bolts through joint
```

| Piece | Length | Fits Bed? |
|-------|--------|-----------|
| Front half (Y=0 to Y=+180mm + 15mm overlap) | ~195mm | YES (225mm bed) |
| Rear half (Y=-90mm to Y=0 + 15mm overlap) | ~105mm | YES |

The half-lap joint provides:
- Shear resistance (interlocking step prevents vertical movement)
- 2× M3 bolts through the overlap zone for tension
- Self-alignment during assembly
- The shared M8 body pivot bolt adds additional constraint

**Qty**: 4 pieces total (2 front halves + 2 rear halves) instead of 2 whole arms.

### 4.4 Rocker Print Settings

| Setting | Value |
|---------|-------|
| Print orientation | On side (longest axis horizontal, load axis along layers) |
| Walls | 4 |
| Infill | 50% gyroid |
| Layer height | 0.2mm |
| Estimated print time | ~4 hrs each |
| Estimated weight | ~35g each (70g total) |

### 4.5 Reinforcement

At 0.4 scale with ~1 kg total weight, the rocker arms experience very low loads (~0.17 kg per wheel). No metal reinforcement needed — PLA at 50% infill is more than sufficient.

**Verification**: Rocker arm bending moment at worst case (single wheel on obstacle, 2× load = 0.34 kg):
```
M = F × d = 0.34 × 9.81 × 0.090 = 0.30 N·m
Section modulus (20×15mm rectangle, 3mm walls): S ≈ 0.5 cm³
Stress = M/S = 0.30 / 0.5e-6 = 0.6 MPa

PLA tensile strength: ~60 MPa
Safety factor: 60 / 0.6 = 100×  ← massively over-engineered at this scale
```

---

## 5. Bogie Arms (2× required)

### 5.1 Geometry

Each bogie arm connects the middle and rear wheels, pivoting on the rocker arm.

```
Side View (left bogie):

         [Bogie Pivot] (connects to rocker)
         /            \
    [90mm]           [90mm]
       |                |
      W2              W3
   (middle)          (rear)
```

| Parameter | Value |
|-----------|-------|
| Total length | 180mm (W2 axle to W3 axle) |
| Pivot to each wheel | 90mm |
| Cross-section | 15mm × 12mm outer, 2.5mm walls |
| Pivot bore | 8mm for 608ZZ bearing |
| Wheel axle mounts | Motor mounting face with 4× M3 holes |
| Material | PLA |

### 5.2 Bogie Print Settings

| Setting | Value |
|---------|-------|
| Print orientation | On side |
| Walls | 4 |
| Infill | 50% gyroid |
| Layer height | 0.2mm |
| Estimated print time | ~2.5 hrs each |
| Estimated weight | ~20g each (40g total) |

---

## 6. Differential Bar

### 6.1 Geometry

The differential bar connects left and right rocker pivots, averaging their pitch angle. At 0.4 scale, this is a simple bar with pivot bearings at each end and a centre pivot for body attachment.

```
Front View:

              [Centre Pivot]
              /             \
    [100mm]                  [100mm]
       |                        |
  [Left Rocker]          [Right Rocker]
   Pivot                   Pivot
```

| Parameter | Value |
|-----------|-------|
| Total length | 200mm (centre to centre of rocker pivots) |
| Cross-section | Round tube: 12mm OD, 8mm ID (press-fit 8mm shaft) |
| Centre pivot | 8mm bore for 608ZZ bearing (attaches to body) |
| End pivots | 8mm bore for 608ZZ bearing (attaches to rockers) |
| Material | PLA or steel rod (8mm) with printed end caps |

### 6.2 Design Decision: Printed vs Metal

For Phase 1, the differential bar experiences torsional loads as it averages left/right rocker angles. Options:

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| 3D printed tube | Cheap, integrated bearing mounts | Torsional weakness in FDM layers | Acceptable at 0.4 scale |
| 8mm steel rod | Very strong, precise | Need printed adapters for bearings | Better for reliability |
| M8 threaded rod | Cheap, available, strong | Thread surface adds friction | Budget option |

**Recommendation**: 8mm steel rod (from a hardware store, ~$2 for 300mm) with 3D printed bearing adapters at each end. The rod slots through 608ZZ bearings directly (8mm ID is a perfect fit).

### 6.3 Print Settings (End Adapters)

| Setting | Value |
|---------|-------|
| Qty | 3 (left end, centre, right end) |
| Material | PLA |
| Walls | 4 |
| Infill | 60% |
| Print time | ~1 hr each |
| Weight | ~5g each (15g total, plus rod ~40g) |

---

## 7. Wheels (6× required)

### 7.1 Dimensions

| Parameter | Value |
|-----------|-------|
| Outer diameter | 80mm |
| Width | 32mm |
| Hub bore | Matches N20 motor shaft (3mm D-shaft) |
| Tread pattern | 12× chevron grousers, 3mm deep |
| Spoke design | 6-spoke with flex zones (compliant wheel) |
| Material | PLA (rigid hub + tread) with rubber O-ring traction bands |

### 7.2 Wheel Design Options

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A: Rigid PLA | Entire wheel PLA, rigid grousers only | Simplest, one print | Hard ride, poor grip on smooth surfaces |
| B: PLA + O-rings | PLA wheel with grooves for rubber O-ring traction bands | Good grip, simple assembly, no TPU needed | Need correctly sized O-rings |
| C: Compliant spoke | PLA with thin flex spokes + O-rings | Some compliance, good grip | Complex geometry, PLA may be too brittle for flex spokes |

**Recommendation**: Option B — rigid PLA wheels with circumferential grooves for standard rubber O-rings. The O-rings provide traction on smooth surfaces without requiring TPU printing (which the CTC printer cannot do). Use 2-3 O-rings per wheel in machined grooves. Standard 70mm ID × 3mm cross-section O-rings fit the 80mm OD wheel well.

### 7.3 Hub-to-Motor Interface

N20 gearmotors have a 3mm D-shaft output. The wheel hub needs:

```
Hub Cross-Section:

     ┌─────────────┐
     │  ○ ○ ○ ○ ○  │  ← Tread grousers
     │ ┌─────────┐ │
     │ │         │ │  ← 6-spoke pattern
     │ │  [3mm   │ │
     │ │   D-shaft│ │  ← D-profile bore
     │ │  bore]  │ │
     │ └─────────┘ │
     └─────────────┘
```

| Feature | Dimension |
|---------|-----------|
| D-shaft bore | 3.1mm (0.1mm clearance for print tolerance) |
| D-flat depth | 0.5mm |
| Hub boss OD | 10mm |
| Hub boss length | 8mm (engages full shaft length) |
| Set screw | M2 grub screw perpendicular to shaft (backup retention) |

### 7.4 Wheel Print Settings

| Setting | Value |
|---------|-------|
| Print orientation | Flat (wheel face down on bed, axle vertical) |
| Walls | 3 |
| Infill | 25% (spokes are structural, body is decorative) |
| Layer height | 0.2mm |
| Support | None (design spokes for bridging) |
| Estimated print time | ~2 hrs each (12 hrs total) |
| Estimated weight | ~25g each (150g total) |

---

## 8. Steering Assembly (4× corners)

### 8.1 Overview

The front two and rear two wheels have steering capability via SG90 micro servos. Each steering assembly consists of:
1. Servo mount (bolted to rocker/bogie arm end)
2. Steering horn (connects servo to wheel pivot)
3. Wheel pivot bearing (608ZZ)
4. Motor mount bracket (holds N20 motor, rotates with steering)

### 8.2 Steering Mechanism

```
Top View (one steering corner):

    [Rocker/Bogie Arm End]
            |
    [608ZZ Bearing] ← Steering pivot axis (vertical)
            |
    [Steering Bracket] ← Rotates ±35° (limited by geometry)
        |         |
    [SG90]    [N20 Motor]
    servo      + wheel
```

| Parameter | Value |
|-----------|-------|
| Steering range | ±35° (70° total, limited by arm geometry) |
| Servo | SG90, 1.8 kg·cm torque at 4.8V |
| Steering pivot bearing | 608ZZ (8mm bore) |
| Servo horn length | 15mm (gives adequate mechanical advantage) |
| Servo mount | M2 screws into PLA bracket |

### 8.3 Steering Bracket

The steering bracket is the rotating part that holds the motor and turns with the servo.

| Parameter | Value |
|-----------|-------|
| Dimensions | 35mm × 25mm × 40mm |
| Material | PLA, 4 walls, 40% infill |
| Features | 608ZZ bearing seat (top), N20 motor clip (bottom), servo horn receiver |
| Weight | ~12g each |
| Print orientation | Upright (bearing seat on top, motor clip on bottom) |
| Print time | ~1.5 hrs each |

### 8.4 Fixed Wheel Mounts (2× middle wheels)

The middle wheels (W2, W5) don't steer. They mount directly to the bogie arm ends.

| Parameter | Value |
|-----------|-------|
| Dimensions | 25mm × 25mm × 30mm |
| Features | N20 motor clip, M3 bolt holes to bogie arm |
| Weight | ~8g each |
| Print time | ~1 hr each |

---

## 9. Motor Mounting

### 9.1 N20 Gearmotor Dimensions

Standard N20 micro gearmotors (with encoder):

| Parameter | Value |
|-----------|-------|
| Body dimensions | 12mm × 10mm × 25mm (motor) + 12mm (gearbox) = 37mm total |
| Shaft | 3mm D-shaft, 10mm protrusion |
| Mounting | 2× M2 screws on 9mm centres (some have flat face for adhesive) |
| Weight | ~20g each |
| Voltage | 6V rated (7.4V max from 2S LiPo — use PWM limiting) |
| RPM | 100 RPM (at 6V, no load) |
| Stall torque | ~0.5 kg·cm |
| Encoder | Hall effect, 2-channel, ~7 pulses/rev motor shaft (×gear ratio) |

### 9.2 Motor Clip Design

Rather than screws (M2 is fiddly), use a snap-fit clip that holds the N20 by its gearbox housing:

```
Front View:

    ┌────────────┐
    │  ┌──────┐  │
    │  │ N20  │  │  ← Clip arms flex over motor body
    │  │motor │  │
    │  └──clip┘  │  ← Snap tab at bottom
    │            │
    └────────────┘
```

| Feature | Dimension |
|---------|-----------|
| Clip inner width | 12.2mm (0.2mm clearance) |
| Clip inner height | 10.2mm |
| Clip wall thickness | 2mm |
| Snap tab protrusion | 0.5mm |
| Shaft exit hole | 4mm diameter |

---

## 10. Bearings

### 10.1 Bearing Specification

All pivot points use 608ZZ bearings (the same as skateboard bearings — cheap and widely available).

| Parameter | Value |
|-----------|-------|
| Type | 608ZZ deep groove ball bearing |
| Inner diameter (bore) | 8mm |
| Outer diameter | 22mm |
| Width | 7mm |
| Seal | ZZ (metal shields both sides) |
| Load rating (dynamic) | 3.45 kN |
| Weight | 12g each |
| Cost | ~$0.50 each |

### 10.2 Bearing Locations (Phase 1)

| Location | Qty | Shaft | Notes |
|----------|-----|-------|-------|
| Body left rocker pivot | 1 | M8 bolt | Rocker rotates on bearing |
| Body right rocker pivot | 1 | M8 bolt | Rocker rotates on bearing |
| Left rocker-bogie pivot | 1 | M8 bolt | Bogie swings on bearing |
| Right rocker-bogie pivot | 1 | M8 bolt | Bogie swings on bearing |
| Differential bar centre | 1 | 8mm rod | Bar rotates freely |
| Differential bar left end | 1 | 8mm rod | Connects to left rocker |
| Differential bar right end | 1 | 8mm rod | Connects to right rocker |
| Steering pivot FL | 1 | M8 bolt | Wheel turns for steering |
| Steering pivot FR | 1 | M8 bolt | Wheel turns for steering |
| Steering pivot RL | 1 | M8 bolt | Wheel turns for steering |
| Steering pivot RR | 1 | M8 bolt | Wheel turns for steering |
| **Total** | **11** | | ~$5.50 total cost |

Note: Phase 1 uses 11 bearings (not 19 like Phase 2). Buy 12 to have a spare in case of fit issues. Phase 2 adds bearings for wheel hubs, arm joints, and mast — not needed at 0.4 scale.

### 10.3 Bearing Press-Fit Dimensions

For 3D printed PLA bearing seats:

| Feature | Dimension | Notes |
|---------|-----------|-------|
| Bearing seat ID | 22.15mm | 0.15mm oversize for press fit (PLA shrinks slightly less than PETG) |
| Bearing seat depth | 7.2mm | Full bearing width + 0.2mm |
| Shaft hole | 8.0mm | Exact — bearing inner race doesn't rotate relative to shaft |
| Retention | Snap ring groove or printed lip | Prevents bearing walking out |

**Important**: Test-print a bearing test piece first. PLA print tolerance varies by printer — adjust the 22.15mm bore ±0.1mm based on test fit on the CTC printer. Target: bearing should press in firmly by hand without needing a hammer.

---

## 11. Electronics Layout

### 11.1 Components

| Component | Dimensions | Mount | Location |
|-----------|-----------|-------|----------|
| ESP32-S3 DevKit | 69mm × 25mm | 4× M3 standoffs | Centre of body, accessible |
| L298N driver #1 | 43mm × 43mm × 27mm | 4× M3 standoffs | Left side (drives W1, W2, W3) |
| L298N driver #2 | 43mm × 43mm × 27mm | 4× M3 standoffs | Right side (drives W4, W5, W6) |
| 2S LiPo 2200mAh | 70mm × 35mm × 18mm | Battery tray (Velcro strap) | Centre floor, low CoG |
| Power switch | 15mm panel mount | Rear wall hole | Easily accessible |
| Breadboard (mini) | 47mm × 35mm | Adhesive back | For servo connections |

### 11.2 Wiring Routing

```
Top View — Electronics Layout:

+--------------------------------------------+
|  [L298N #1]          [ESP32-S3]  [L298N #2] |
|     |                    |           |       |
|     |    [Breadboard]    |           |       |
|     |         |          |           |       |
|  ===|=========|==========|===========|===    | ← Cable channel (floor groove)
|     |         |          |           |       |
|     |    [2S LiPo]       |           |       |
|     |    [Battery]       |           |       |
|     |                  [Switch]      |       |
+----+------+-------+-------+--------+-------+
     |      |       |       |        |       |
    W1     W2      W3      W4      W5      W6
    +SG90  (fixed) +SG90   +SG90  (fixed)  +SG90
```

### 11.3 Power Distribution

```
2S LiPo (7.4V) → Power Switch → Distribution:
  ├─→ L298N #1 VCC (drives 3 motors, accepts up to 12V)
  ├─→ L298N #2 VCC (drives 3 motors)
  ├─→ L298N #1 5V regulator output → ESP32 VIN (5V)
  └─→ 4× SG90 servos (SG90 rated 4.8-6V, powered from L298N 5V reg)
```

**Note**: The L298N board has an onboard 5V regulator (78M05). With motor voltage ≤12V, the jumper stays ON and the 5V pin becomes an output. This powers the ESP32 and servos without needing a separate regulator.

**Current budget**:
- 6× N20 motors at stall: 6 × 0.7A = 4.2A (from 7.4V rail)
- 4× SG90 servos: 4 × 0.65A = 2.6A peak (from 5V reg, but not all stall simultaneously)
- ESP32-S3: ~0.3A (from 5V)
- Realistic draw: ~2-3A average from battery
- 2S 2200mAh → ~45min at 3A, ~1.5hr at 1.5A typical

---

## 12. Fastener Inventory

### 12.1 Phase 1 Fastener List

| Fastener | Size | Qty | Purpose |
|----------|------|-----|---------|
| M8 × 40mm hex bolt | M8 | 4 | Rocker + bogie pivot shafts |
| M8 × 30mm hex bolt | M8 | 4 | Steering pivot shafts |
| M8 nyloc nut | M8 | 8 | Lock nuts for all M8 pivots |
| M8 washer | M8 | 16 | 2 per pivot (both sides of bearing) |
| M3 × 12mm socket cap | M3 | 34 | Body join, standoffs, brackets, rocker arm lap joints (4) |
| M3 × 8mm socket cap | M3 | 20 | Electronics mounting, motor clips |
| M3 nut | M3 | 30 | General assembly |
| M3 washer | M3 | 30 | General assembly |
| M3 × 5mm heat-set insert | M3 | 40 | Press into PLA for screw bosses (170-180°C, lower than PETG) |
| M2 × 8mm | M2 | 8 | SG90 servo mounting (4 servos × 2 screws) |
| M2 × 6mm grub screw | M2 | 6 | Wheel hub set screws (backup retention) |

### 12.2 Tools Required

| Tool | Size | Purpose |
|------|------|---------|
| Hex key | 2mm | M3 socket cap screws |
| Hex key | 5mm | M8 hex bolts |
| Soldering iron | Pointed tip, 170-180°C | Heat-set insert installation (PLA requires lower temp than PETG's 200-220°C) |
| Wire strippers | — | Wiring |
| Small Phillips screwdriver | #1 | SG90 mounting screws |
| Multimeter | — | Voltage checks, continuity |

---

## 13. Print Summary

### 13.1 All Parts to Print

| # | Part | Qty | Material | Est. Time | Est. Weight |
|---|------|-----|----------|-----------|-------------|
| 1 | Body front-left segment | 1 | PLA | 7 hrs | 110g |
| 2 | Body front-right segment | 1 | PLA | 7 hrs | 110g |
| 3 | Body rear-left segment | 1 | PLA | 7 hrs | 110g |
| 4 | Body rear-right segment | 1 | PLA | 7 hrs | 110g |
| 5 | Top deck cover | 1 | PLA | 4 hrs | 60g |
| 6 | Rocker arm front half (×2) | 2 | PLA | 1.5 hrs ea | 18g ea |
| 7 | Rocker arm rear half (×2) | 2 | PLA | 1 hr ea | 10g ea |
| 8 | Left bogie arm | 1 | PLA | 2.5 hrs | 20g |
| 9 | Right bogie arm | 1 | PLA | 2.5 hrs | 20g |
| 10 | Differential bar end adapters | 3 | PLA | 3 hrs | 15g |
| 11 | Wheels | 6 | PLA | 12 hrs | 150g |
| 12 | Steering brackets | 4 | PLA | 6 hrs | 48g |
| 13 | Fixed wheel mounts | 2 | PLA | 2 hrs | 16g |
| 14 | Bearing test piece | 1 | PLA | 0.5 hrs | 5g |
| | **TOTAL** | **26 core parts** | | **~70 hrs** | **~850g** |

**Note**: This table lists core structural/mechanical parts only. The complete BOM (`docs/plans/phase1-complete-bom.md`) lists 46 parts total, including servo mounts (×4), strain relief clips (×10), fuse holder bracket (×1), switch mount plate (×1), and top deck tiles (×4). The BOM is the authoritative parts list for ordering and printing.

### 13.2 Filament Usage

| Factor | Value |
|--------|-------|
| Part weight total | 844g |
| Extra joining surfaces (~5%) | 42g |
| Support material (~10%) | 84g |
| Skirt/brim/purge (~5%) | 42g |
| Failed prints (~15%) | 127g |
| **Total filament needed** | **~1,139g** |
| **Spools to buy** | 2× 1kg PLA (gives good margin for reprints) |

**Recommendation**: Buy 2× 1kg spools PLA (~$15-18 each). The 4-segment body design uses slightly more filament than the 2-half design due to additional joining walls and overlap surfaces. PLA is cheaper than PETG, which partially offsets the extra material. PLA is suitable for Phase 1 indoor testing; Phase 2 outdoor parts should use PETG or ASA for UV and heat resistance.

### 13.3 Print Order (Recommended)

1. **Bearing test piece** — validate bore dimensions on CTC printer before printing structural parts
2. **Wheels (6×)** — small, fast, can print overnight while designing larger parts
3. **Left & right bogie arms** — small, quick validation of pivot geometry
4. **Left & right rocker arms** — longer prints, do these once bogie fit is confirmed
5. **Differential bar adapters** — quick prints
6. **Steering brackets (4×)** — medium complexity
7. **Fixed wheel mounts (2×)** — simple
8. **Body front-left segment** — 7 hrs, fits CTC bed (150×200mm)
9. **Body front-right segment** — 7 hrs
10. **Body rear-left segment** — 7 hrs
11. **Body rear-right segment** — 7 hrs
12. **Top deck cover** — last, optional for initial testing (may need 2 pieces if 440×260mm exceeds bed)

---

## 14. Assembly Sequence

### Step 1: Prepare Printed Parts
1. Remove support material (minimal if designed correctly)
2. Test-fit all 608ZZ bearings — ream with 22mm drill bit if too tight
3. Install M3 heat-set inserts in all screw bosses (soldering iron, 170-180°C for PLA, 2-3 seconds each — lower temp than PETG to avoid melting too much surrounding material)
4. Dry-fit all joints before adding fasteners

### Step 2: Build Suspension (One Side)
1. Press 608ZZ bearing into rocker arm body pivot boss
2. Press 608ZZ bearing into rocker arm bogie pivot boss
3. Press 608ZZ bearing into bogie arm rocker pivot boss
4. Slide M8 bolt through rocker-bogie pivot, add washers and nyloc nut (finger-tight, must rotate freely)
5. Mount steering bracket to rocker arm front end (608ZZ bearing + M8 bolt)
6. Mount fixed motor bracket to bogie arm middle position
7. Mount steering bracket to bogie arm rear position
8. Repeat for other side

### Step 3: Install Differential Bar
1. Slide 8mm rod through centre 608ZZ bearing (in body frame)
2. Attach left end adapter to left rocker pivot
3. Attach right end adapter to right rocker pivot
4. Verify both rockers seesaw freely when differential bar is connected

### Step 4: Mount Rockers to Body
1. Insert M8 bolts through body frame rocker pivot holes
2. Slide on rocker arm bearings
3. Add washers and nyloc nuts
4. Verify full range of motion: rockers should swing ±25° freely

### Step 5: Install Motors & Wheels
1. Snap N20 motors into all 6 motor clips
2. Route motor wires up through rocker/bogie arms to body
3. Press wheels onto 3mm D-shafts
4. Secure with M2 grub screws
5. Verify all wheels spin freely

### Step 6: Install Servos
1. Mount SG90 servos to steering brackets (M2 screws)
2. Attach servo horns to steering pivot arms
3. Centre all servos (90° = straight ahead)
4. Verify ±35° steering range without mechanical binding

### Step 7: Electronics
1. Mount ESP32-S3 DevKit on standoffs
2. Mount L298N boards on standoffs
3. Wire motors to L298N outputs (colour code: red/black per motor)
4. Wire L298N inputs to ESP32 GPIO pins
5. Wire servos to ESP32 GPIO pins (signal only — power from 5V rail)
6. Connect battery via power switch
7. Test each motor individually before driving

### Step 8: Test & Calibrate
1. Power on — verify 5V on ESP32
2. Test each motor direction (forward/reverse)
3. Test each servo range
4. Calibrate servo centre positions in firmware
5. Place on ground — test basic forward/reverse/turn
6. Test rocker-bogie articulation over obstacles (books, bricks)

---

## 15. Phase 1 Dimensions Summary (CAD Reference)

All dimensions in millimetres at 0.4 scale:

| Component | X (width) | Y (length) | Z (height) | Notes |
|-----------|----------|-----------|-----------|-------|
| Body (outer) | 260 | 440 | 80 | Box frame |
| Body (inner cavity) | 254 | 434 | 74 | 3mm walls |
| Rocker arm | 20 | 180 | 15 | Rectangular tube |
| Bogie arm | 15 | 180 | 12 | Rectangular tube |
| Differential bar | — | 300 (rod) | — | 8mm round rod + 3 printed adapters |
| Wheel | 32 (width) | — | 80 (dia) | Includes tread |
| Steering bracket | 35 | 25 | 40 | Rotates on 608ZZ |
| Fixed motor mount | 25 | 25 | 30 | Bolted to arm end |
| 608ZZ bearing seat OD | 22.1 | — | 7.2 (depth) | Press-fit in printed parts |
| N20 motor clip ID | 12.2 | — | 10.2 | Snap-fit |
| Battery tray | 70 | 35 | 25 | Floor recess |

---

## 16. Phase 1 → Phase 2 Transition Notes

What carries over from Phase 1 to Phase 2:
- **ESP32-S3 DevKit**: Same board, new firmware with UART to Jetson
- **Firmware concepts**: Motor control code, servo calibration values, steering geometry
- **Design lessons**: Print tolerances, bearing fit, wiring routing

What does NOT carry over:
- **Printed parts**: Too small and PLA not durable enough outdoors — all parts reprinted at full scale in PETG/ASA
- **N20 motors**: Replaced with Chihai 37mm gearmotors
- **SG90 servos**: Replaced with MG996R (much higher torque)
- **L298N drivers**: Replaced with Cytron MDD10A (much higher current)
- **2S LiPo**: Replaced with 6S LiPo pack
- **Bearings**: 608ZZ reused where possible, additional bearings added

The Phase 1 prototype becomes a display piece / desk toy once Phase 2 is built.

---

*Document EA-08 v1.2 — 2026-03-23 — Corrected bed size to 225×145mm (CTC Bizer), PLA material, 4-segment body*
