# EA-27: Steering System Design Package

**Date**: 2026-03-24
**Status**: Complete
**Revision**: 1.0
**Cross-references**: EA-10 (Ackermann math), EA-08 (Phase 1 spec), EA-25 (suspension audit), EA-26 (suspension design package)

---

## 1. Overview

This document defines the **complete physical steering mechanism** for the Mars Rover garden robot. EA-10 established the Ackermann steering mathematics (angles, radii, servo mapping) but left the mechanical linkage undefined. This EA closes that gap: every part, dimension, and interface from servo spline to wheel axle.

### 1.1 Architecture Decision

**Selected: Offset parallel drive with printed horn link (4-bar linkage)**

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Coaxial direct drive (servo IS pivot) | Simplest, zero backlash | SG90 bearings too weak for vertical load, packaging very tight at 0.4 scale | Rejected |
| Push-rod linkage | Servo can be remote, mechanical advantage | Extra parts, backlash at 2 joints, buckling risk on thin rod | Rejected |
| Bell crank | Good for single-servo dual-wheel | Wrong topology for 4-wheel independent steering | Rejected |
| **Offset parallel + link** | 608ZZ carries load, simple 2-pin link, 1:1 ratio, proven in Papaya Pathfinder | One extra part (horn link) | **Selected** |

**Rationale**: The SG90 servo shaft and the 608ZZ steering pivot shaft are both vertical and parallel, offset by ~20mm horizontally. A small printed link bar connects the servo horn tip to the knuckle steering arm tip, creating a simple 4-bar linkage. The 608ZZ bearing carries all radial and axial loads. The SG90 only provides torque — no structural load on its shaft.

### 1.2 Key Design Conflicts Resolved

| Conflict | Resolution |
|----------|------------|
| steering_bracket.py has N20 motor clip AND bearing seat | **Motor clip removed from bracket**. Bracket becomes pure bearing carrier. Motor moves to knuckle only. |
| steering_knuckle.py has motor pocket but no steering arm | **Steering arm extension added** to knuckle body for horn link attachment. |
| No servo-to-knuckle linkage defined anywhere | **New part: steering_horn_link.py** — printed 4-bar coupler link. |
| No mechanical hard stops for ±35° | **Tab-in-channel hard stops** added to bracket + knuckle. |
| F688ZZ vs 608ZZ for steering pivots | **608ZZ retained** — single bearing type for entire rover (BOM simplicity). |

---

## 2. Mechanism Analysis

### 2.1 Steering Architecture (Per Corner)

```
FRONT WHEEL CONNECTOR (fixed to arm tube)
    ├── STEERING BRACKET (bolted to front face, 2× M3)
    │     ├── 608ZZ bearing seat (top)
    │     ├── 8mm pivot bore (through)
    │     └── Hard stop channel (bottom, ±35°)
    │
    ├── SERVO MOUNT (bolted to side face, 2× M3)
    │     └── SG90 SERVO (M2 screws, shaft vertical/down)
    │           └── SERVO HORN (15mm single arm, horizontal sweep)
    │                 └── STEERING HORN LINK (M2 pin joint)
    │                       └── connects to KNUCKLE ARM
    │
    └── STEERING KNUCKLE (hangs below on 8mm pivot shaft)
          ├── Pivot socket (top, 8.2mm bore)
          ├── Steering arm (lateral extension, M2 hole for link)
          ├── Hard stop tab (radial, contacts bracket channel)
          ├── N20 motor pocket (middle)
          └── Wheel axle bore (bottom, 4mm horizontal)
```

### 2.2 4-Bar Linkage Geometry

```
                Servo shaft (S)              Steering pivot (P)
                    │                             │
                    │ horn_length                  │ arm_length
                    │ (15mm)                       │ (15mm)
                    ▼                              ▼
            Horn tip (H) ─────────────── Arm tip (A)
                         link_length (L)
```

**Parameters:**
- Servo shaft to steering pivot offset: D ≈ 20mm (from connector geometry)
- Servo horn radius (S→H): 15mm (standard SG90 single-arm horn)
- Knuckle arm radius (P→A): 15mm (matched to horn for 1:1 ratio)
- Link length (H→A): L = D = 20mm (at centre position, both arms parallel)

**Angular ratio**: For equal crank and rocker arms with parallel axes, the ratio is approximately 1:1 for angles up to ±40°. At ±35°:
- Servo input: 35°
- Knuckle output: ~34.2° (0.8° non-linearity — acceptable, firmware trims compensate)

### 2.3 Torque Budget

| Parameter | Value | Source |
|-----------|-------|--------|
| SG90 torque at 4.8V | 1.2–1.8 kg-cm | Datasheet (conservative–typical) |
| Rover mass per steered wheel | ~210g (1.25kg ÷ 6) | EA-05 weight budget |
| Steering torque required (flat surface) | ~0.3 kg-cm | μ × Fn × contact_radius |
| Steering torque required (rough terrain, worst case) | ~0.8 kg-cm | 2× safety factor on grass/gravel |
| SG90 torque margin | 1.5× – 2.25× | Adequate for Phase 1 |

**Conclusion**: SG90 is adequate for Phase 1. MG90S (metal gear, 2.2 kg-cm) recommended as drop-in upgrade if gear stripping occurs.

---

## 3. Component Breakdown

### 3.1 Parts Per Steered Wheel (×4 = FL, FR, RL, RR)

| Part | Script | New/Updated | Qty Each | Total | Weight Est. |
|------|--------|-------------|----------|-------|-------------|
| Front wheel connector | front_wheel_connector.py | Unchanged | 1 | 4 | ~18g |
| Steering bracket | steering_bracket.py | **Updated** (motor clip removed, hard stop added) | 1 | 4 | ~8g |
| Servo mount | servo_mount.py | Unchanged | 1 | 4 | ~6g |
| Steering knuckle | steering_knuckle.py | **Updated** (arm extension + hard stop tab added) | 1 | 4 | ~10g |
| **Steering horn link** | **steering_horn_link.py** | **NEW** | 1 | 4 | ~1g |
| SG90 servo | (purchased) | — | 1 | 4 | 9g |
| 608ZZ bearing | (purchased) | — | 1 | 4 | 12g |
| 8mm steel rod segment | (cut from stock) | — | 1 | 4 | ~8g |
| M2×10 screw (link pins) | (purchased) | — | 2 | 8 | <1g |
| M2 nyloc nut (link pins) | (purchased) | — | 2 | 8 | <1g |

### 3.2 Parts For Fixed Wheels (×2 = ML, MR)

| Part | Script | Status | Qty Each | Total |
|------|--------|--------|----------|-------|
| Middle wheel connector | middle_wheel_connector.py | Unchanged | 1 | 2 |
| Fixed wheel mount | fixed_wheel_mount.py | Unchanged | 1 | 2 |

### 3.3 New Hardware Required (EA-27 additions to BOM)

| Item | Qty | Purpose | Notes |
|------|-----|---------|-------|
| M2×10mm socket cap screw | 8 | Horn link pin joints (2 per link × 4 links) | Stainless steel preferred |
| M2 nyloc nut | 8 | Retain link pins | Self-locking — essential for vibration |
| M2 flat washer (nylon) | 16 | Smooth rotation at pin joints (2 per pin) | Reduces friction on PLA |

---

## 4. Dimensional Chain

### 4.1 Servo Spline to Wheel Contact Patch

```
SG90 SERVO SPLINE (21T, 4.8mm OD)
  ↓ press-fit (0.05mm interference)
SERVO HORN (15mm single-arm, plastic)
  ↓ M2 pin joint (2.2mm clearance hole + nylon washer)
STEERING HORN LINK (20mm centre-to-centre, 8mm wide, 5mm thick PLA)
  ↓ M2 pin joint (2.2mm clearance hole + nylon washer)
KNUCKLE STEERING ARM (15mm from pivot centre, integrated with knuckle body)
  ↓ rigid (one-piece printed)
STEERING KNUCKLE BODY (25 × 30 × 40mm)
  ↓ pivot socket (8.2mm bore, M3 grub screw retention)
8mm STEEL PIVOT SHAFT (press-fit through 608ZZ bearing)
  ↓ bearing (8mm bore / 22mm OD / 7mm width)
608ZZ BEARING (in steering bracket seat, 22.15mm × 7.2mm)
  ↓ press-fit in bracket
STEERING BRACKET (bolted to front wheel connector, 2× M3)
  ↓ M3 bolts into heat-set inserts
FRONT WHEEL CONNECTOR (tube socket receives 8mm arm rod)
  ↓ tube + grub screw
SUSPENSION ARM (rocker front or bogie rear tube)
```

### 4.2 Key Interface Dimensions

| Interface | Dimension | Tolerance | Notes |
|-----------|-----------|-----------|-------|
| 608ZZ bearing seat OD | 22.15mm | ±0.05mm | Press-fit, 0.15mm oversize |
| 608ZZ bearing seat depth | 7.2mm | ±0.05mm | 0.2mm extra for clearance |
| Pivot shaft bore | 8.0mm H7 | +0.000/+0.015mm | Ground 8mm rod preferred |
| Pivot socket (knuckle) | 8.2mm | ±0.1mm | 0.2mm clearance on rod |
| N20 motor clip width | 12.2mm | +0.1/-0.0mm | 0.2mm clearance |
| N20 motor clip height | 10.2mm | +0.1/-0.0mm | 0.2mm clearance |
| Wheel axle bore | 4.0mm | ±0.1mm | N20 D-shaft clearance |
| SG90 pocket | 22.4 × 12.2mm | ±0.1mm | 0.2mm/0.4mm clearance |
| Horn link M2 holes | 2.2mm | ±0.1mm | M2 clearance |
| Horn link centre distance | 20.0mm | ±0.3mm | Matches servo-to-pivot offset |
| Heat-set insert bore | 4.8mm | ±0.05mm | For M3 brass inserts |

---

## 5. Bearing Decision

### 5.1 608ZZ vs F688ZZ Analysis

| Parameter | 608ZZ | F688ZZ |
|-----------|-------|--------|
| Bore | 8mm | 8mm |
| OD | 22mm | 16mm (flange 18mm) |
| Width | 7mm | 5mm |
| Dynamic load | 3,390 N | 1,064 N |
| Weight | 12.9g | 4.5g |
| Cost | ~£0.40 | ~£1.00 |
| Flange | No | Yes (built-in axial location) |
| Housing bore required | 22mm (large, hard to bridge in print) | 16mm (easier to print) |

### 5.2 Decision: Retain 608ZZ

**Rationale:**
1. **Single bearing type** for entire rover (9 positions × 1 type = simpler BOM)
2. 608ZZ already purchased (12 units specified in shopping list)
3. Higher load rating provides generous safety margin
4. All existing scripts, connectors, and assemblies designed around 22mm OD
5. F688ZZ would require redesigning bracket, connector, and all bearing seats

**Trade-off acknowledged**: F688ZZ would allow a more compact knuckle (6mm smaller housing bore) and provides free axial location via flange. If a redesign opportunity arises for Phase 2, F688ZZ should be reconsidered.

---

## 6. Hard Stop Design

### 6.1 Mechanism

**Type**: Integrated tab-in-channel (printed into bracket and knuckle)

```
TOP VIEW — Steering bracket bottom face:

         ┌─ stop wall ─┐
         │   (3mm wide) │
    ─────┘              └─────     ← bracket inner wall
              ╱    ╲
            ╱   70°  ╲             ← 70° open channel
          ╱    sweep   ╲
    ─────╱               ╲─────
         │   stop wall   │
         └───────────────┘

    KNUCKLE TAB rotates within this 70° channel.
    Contact at ±35° from centre = mechanical hard stop.
```

### 6.2 Dimensions

| Feature | Dimension | Notes |
|---------|-----------|-------|
| Bracket stop walls | 3mm wide × 5mm tall × 3mm thick | Below bearing seat, inside bracket bore |
| Knuckle hard stop tab | 5mm wide × 8mm radial × 3mm thick | Near pivot socket top, extends outward |
| Channel angular width | 70° (±35° from centre) | Matches EA-10 max steering angle |
| Tab-to-wall clearance | 0.3mm | At the stop position |
| Tab material | PLA, 100% infill locally | Print orientation: tab in XY plane (strongest) |

### 6.3 Stop Force Analysis

At ±35° limit:
- Worst-case servo stall torque: 2.5 kg-cm = 0.245 N-m
- Tab contact radius: ~11mm from pivot centre
- Contact force: F = T/r = 0.245/0.011 = 22.3 N
- PLA shear strength: ~35 MPa
- Tab cross-section: 5 × 3mm = 15mm²
- Tab shear capacity: 35 × 15 = 525 N

**Safety factor: 525/22.3 = 23.5×** — hard stop is vastly overstrength. The SG90 will stall or strip its own gears long before the PLA tab fails.

---

## 7. Clearance Envelope

### 7.1 Wheel Sweep at Maximum Steering + Suspension Articulation

**Worst case**: ±35° steering + ±25° rocker swing (simultaneous)

| Check | Clearance Required | Clearance Available | Pass? |
|-------|-------------------|--------------------|----|
| Wheel rear edge to arm tube at full lock | ≥5mm | 6.6mm (EA-08 calculation) | Yes |
| Horn link to connector body at full lock | ≥2mm | ~5mm | Yes |
| Servo horn to bracket wall | ≥2mm | ~4mm (horn slot 12mm dia) | Yes |
| Knuckle body to connector bottom at max rocker | ≥3mm | ~8mm | Yes |
| Motor body to bracket wall | ≥2mm | ~5mm | Yes |
| Servo wire to moving parts | ≥3mm | ~8mm (wire exits through connector bottom) | Yes |

### 7.2 Critical Geometry

The wheel sweeps an arc of 18.4mm outward at 35° lock (from EA-08). The arm tube is 180mm from the connector (Phase 1 bogie arm), so the wheel clears the tube. The horn link sweeps within the space between the servo mount and the steering bracket — both are fixed to the connector, so the link operates in a well-defined volume.

### 7.3 Compound Motion

When rocker swings ±25° AND steering is at ±35°:
- The connector tilts with the rocker, carrying both servo and bracket
- The knuckle tilts with the connector (stays aligned)
- The wheel weight vector changes angle but stays within the pivot bore clearance
- No additional interference occurs because the entire steering assembly moves as a unit with the rocker

---

## 8. Integration with EA-25/EA-26

### 8.1 Front Wheel Connector Interface

The front_wheel_connector.py provides:
- **Front face**: 2× M3 heat-set inserts at 20mm spacing → steering bracket bolts here
- **Side face**: 2× M3 heat-set inserts at 20mm spacing → servo mount bolts here
- **Bottom**: 10×8mm wire exit → servo 3-wire + motor 2-wire exit here
- **Top**: 8.2mm tube socket → arm tube inserts here

No changes to front_wheel_connector.py are required.

### 8.2 Wire Routing Through Steering Joint

Per steered wheel, 5 wires pass through:
- Motor power: 2 wires (22 AWG, red + black)
- Servo signal: 3 wires (26 AWG, orange/red/brown)

Route: ESP32 → body cable channel → rocker pivot (5mm hole) → arm tube interior → connector wire exit → motor + servo

The servo wire must have enough slack for ±35° steering rotation. Required slack at the connector: ~15mm loop. Use a small zip-tie anchor on the connector to provide strain relief.

### 8.3 8mm Steel Rod Inventory Update

Steering pivot shafts are 8mm steel rod segments cut to length. Per steered wheel:
- Shaft length: bracket_height + 2× washer + nut = 40 + 2 + 4 = 46mm (round to 50mm)
- 4× 50mm segments for steering pivots

This adds to the rod-cutting plan (see `/rod-cutting` command).

---

## 9. Phase 1 Simplifications

| Full Design Feature | Phase 1 Simplification | Reason |
|--------------------|-----------------------|--------|
| MG996R metal gear servo | SG90 plastic gear | Cost, adequate torque at 0.4 scale |
| Sealed bearing with dust cover | Open 608ZZ (metal shields) | Indoor/garden use, dust minimal |
| Hardened ground pivot shaft | Standard 8mm mild steel rod | Adequate for PLA bearing seat |
| Adjustable tie-rod (turnbuckle) | Fixed-length printed link | Simplicity, trim via firmware |
| Anti-Ackermann compensation | Parallel 1:1 linkage | Non-linearity <1° at ±35° |
| Feedback potentiometer | Open-loop servo PWM | SG90 has no feedback; Phase 2 uses closed-loop MG996R |
| Metal hard stops (adjustable) | Printed tab-in-channel | Adequate strength in PLA, free |
| IP54 seal on steering joint | No seal | Indoor/dry garden use for Phase 1 |

---

## 10. Parametric Dimensions

### 10.1 New Parameters for `generate_rover_params.py`

Added to `steering` group:

| Parameter | Full Scale (mm) | Phase 1 (mm) | Scaled? | Notes |
|-----------|----------------|--------------|---------|-------|
| `horn_link_length` | 50 | 20 | Yes | Centre-to-centre of M2 holes |
| `horn_link_width` | 20 | 8 | Yes | Link bar width |
| `horn_link_thickness` | 12.5 | 5 | Yes | Link bar thickness |
| `knuckle_arm_length` | 37.5 | 15 | Yes | Pivot centre to M2 link hole |
| `hard_stop_tab_width` | 12.5 | 5 | Yes | Tab width on knuckle |
| `hard_stop_tab_radial` | 20 | 8 | Yes | Tab radial extent from pivot |
| `hard_stop_tab_thickness` | 7.5 | 3 | Yes | Tab thickness |
| `hard_stop_channel_deg` | 70 | 70 | No | Angular channel width (±35°) |
| `pivot_shaft_length` | 125 | 50 | Yes | Cut rod length per pivot |
| `servo_to_pivot_offset` | 50 | 20 | Yes | Horizontal distance between axes |

Added to `fasteners` group:

| Parameter | Value | Notes |
|-----------|-------|-------|
| `m2_10mm_qty` | 8 | Horn link pin joints |
| `m2_nyloc_nut_qty` | 8 | Link pin retention |
| `m2_nylon_washer_qty` | 16 | Smooth pin joint rotation |

### 10.2 Updated Bearing Allocation

No change to bearing count:
- 9 bearings needed (2 rocker + 2 bogie + 1 diff + 4 steering)
- 12 purchased (9 + 3 spares)

---

## 11. CAD Script Checklist

### 11.1 New Script

| Script | Part | Key Dims (Phase 1) | Interfaces |
|--------|------|-------------------|------------|
| `steering_horn_link.py` | Printed link bar | 20 × 8 × 5mm, 2× M2 holes at 20mm c/c | Horn tip (M2 pin) ↔ Knuckle arm (M2 pin) |

### 11.2 Updated Scripts

| Script | Change Summary |
|--------|---------------|
| `steering_bracket.py` | Remove N20 motor clip + shaft exit hole. Add hard stop walls (2× 3mm blocks at ±35°). Reduce height from 40mm to 25mm (bearing carrier only). |
| `steering_knuckle.py` | Add steering arm extension (15mm lateral + M2 hole). Add hard stop tab (5×8×3mm radial). Update docstring. |
| `generate_rover_params.py` | Add 10 new steering params + 3 fastener params. |
| `batch_export_all.py` | Add SteeringHornLink entry (Stage 3). |

### 11.3 Unchanged Scripts

| Script | Why Unchanged |
|--------|--------------|
| `servo_mount.py` | Horn slot, pocket, and mount holes are correct as-is |
| `front_wheel_connector.py` | Bolt patterns match updated bracket and servo mount |
| `fixed_wheel_mount.py` | Middle wheels have no steering |
| `middle_wheel_connector.py` | Middle wheels have no steering |

---

## 12. Failure Modes

| Failure | Cause | Prevention | Detection |
|---------|-------|------------|-----------|
| SG90 gear strip | Impact load or hard stop collision | Firmware ±33° soft limit (2° before hard stop); hard stop protects gear train | Steering angle doesn't reach target; recalibrate or replace SG90 |
| Horn link pin pulls out | Vibration loosens M2 nut | Use M2 nyloc nuts (self-locking) | Visual check during assembly |
| Horn spline strip | Repeated over-torque | Avoid commanding full lock under load; horn screw tight | Steering slop increases; replace horn |
| Bearing seat cracks | Bearing press-fit too tight or layer adhesion poor | 22.15mm seat (not 22.0mm); 5 perimeters; print flat | Visual crack at bearing seat edge |
| Hard stop tab shears off | Extreme impact (23× overstrength, so very unlikely) | Print with tab in XY plane; 100% infill locally | Physical inspection; re-print bracket |
| Knuckle pivot binds | Rod/socket friction too high | 0.2mm clearance; light grease on rod | Steering feels stiff; check alignment |
| Wheel hits arm at full lock | Incorrect clearance geometry | EA-08 confirms 6.6mm clearance; verify after assembly | Mark arm tube at theoretical limit |

---

## 13. Assembly Instructions (Steering Stage)

### Stage 4: Steering Brackets + Servos (×4)

**Prerequisites**: All printed parts cleaned, heat-set inserts installed, 8mm rods cut.

#### 4.1 Steering Bracket Preparation (×4)
1. Press-fit 608ZZ bearing into bracket seat (use C-clamp, bearing flush with top face)
2. Verify bearing spins freely (flick inner race)
3. Insert 8mm steel pivot rod through bracket bore + bearing inner race
4. Rod should extend ~5mm below bracket bottom and ~5mm above bracket top

#### 4.2 Servo Mount + SG90 (×4)
1. Drop SG90 into servo mount pocket (tabs rest on ledges)
2. Secure with 2× M2×8 screws through tabs into mount body
3. Attach single-arm horn to SG90 spline (centred = straight ahead)
4. Tighten horn screw (small Phillips)

#### 4.3 Steering Knuckle + Motor (×4)
1. Snap N20 motor into knuckle motor pocket (shaft exits through axle bore side)
2. Verify motor shaft spins freely
3. Slide knuckle pivot socket over the 8mm rod protruding from bracket bottom
4. Tighten M3 grub screw in knuckle socket to retain rod

#### 4.4 Horn Link Connection (×4)
1. Insert M2×10 screw through nylon washer → horn tip hole → link hole → nylon washer → M2 nyloc nut
2. Finger-tight + ¼ turn — link must rotate freely on pin
3. Repeat for knuckle arm end of link
4. Manually sweep steering ±35° — verify smooth motion and hard stops engage

#### 4.5 Bolt to Connector (×4)
1. Bolt steering bracket to connector front face (2× M3×12 into heat-set inserts)
2. Bolt servo mount to connector side face (2× M3×12 into heat-set inserts)
3. Verify horn link operates freely — no binding or rubbing

#### 4.6 Servo Calibration
1. Power SG90 at 1500µs PWM → horn should be centred (perpendicular to bracket)
2. If not, remove horn, rotate to centre, re-press onto spline
3. Command ±35° (1111µs / 1889µs) → verify knuckle reaches limit
4. Trim: if centre is off by >2°, adjust in firmware `SERVO_TRIM_FL/FR/RL/RR`

---

## 14. Appendix: Design-Driving Parameters

### A. SG90 Servo Specifications (from datasheet)

| Parameter | Value |
|-----------|-------|
| Operating voltage | 4.8–6.0V |
| Stall torque at 4.8V | 1.2–1.8 kg-cm |
| Speed at 4.8V | 0.12 sec/60° |
| Rotation range | ~180° (PWM 544–2400µs) |
| Body: W×D×H | 22.2 × 11.8 × 22.7mm |
| With tabs | 32.2mm total width |
| Horn spline | 21 teeth, 4.8mm OD |
| Weight | 9g |

### B. 608ZZ Bearing Specifications

| Parameter | Value |
|-----------|-------|
| Inner diameter | 8mm |
| Outer diameter | 22mm |
| Width | 7mm |
| Dynamic load rating | 3,390 N |
| Static load rating | 1,370 N |
| Max speed (grease) | 34,000 RPM |
| Weight | 12.9g |

### C. Ackermann Steering Quick Reference (from EA-10)

| Parameter | Phase 1 (0.4×) | Phase 2 (1.0×) |
|-----------|----------------|----------------|
| Max steering angle | ±35° | ±35° |
| Minimum turn radius | 397mm | 993mm |
| Wheelbase | 360mm | 900mm |
| Track width | 280mm | 700mm |
| Servo centre PWM | 1500µs | 1500µs |
| Servo µs/degree | 11.11 | 11.11 |

### D. Reference Rover Comparison

| Feature | Sawppy V1 | Micro Sawppy MSB3 | Papaya Pathfinder | **Our Design** |
|---------|-----------|-------------------|-------------------|----------------|
| Steering bearing | LX-16A internal | 623 (3×10×4) | 608ZZ (8×22×7) | **608ZZ** |
| Servo | LX-16A (13 kg-cm) | SG90 | SG90/MG996R | **SG90 (Phase 1)** |
| Linkage | Rigid coupler | Direct drive | Horn + link | **Horn + printed link** |
| Hard stops | Cast into knuckle | Software only | Integral knuckle | **Tab-in-channel** |
| Servo coupling weakness | Coupler cracks | Gear strip | Horn strip | **Link pins (replaceable)** |

---

*Document end. See EA-10 for full Ackermann mathematics, EA-08 for Phase 1 build guide, EA-25/EA-26 for suspension integration.*
