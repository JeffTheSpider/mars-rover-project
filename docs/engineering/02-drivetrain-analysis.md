# Engineering Analysis 02: Motor & Drivetrain Design

**Document**: EA-02
**Date**: 2026-03-15
**Purpose**: Calculate torque requirements, select motors and drivers, design steering system, and specify the complete drivetrain for all build phases.
**Depends on**: EA-05 (Weight Budget)

---

## 1. Requirements

| Parameter | Value | Source |
|-----------|-------|--------|
| Design weight (with safety factor) | 34.2 kg (22.8 kg × 1.5) | EA-05, Phase 3 loaded + 1.5× SF |
| Realistic operating weight | 18.7 kg (Phase 2 loaded) | EA-05 |
| Number of drive wheels | 6 | Design spec |
| Wheel diameter | 200mm (radius = 0.1m) | EA-01 |
| Target speed (flat) | 5 km/h = 1.39 m/s | Design spec |
| Target speed (slope) | 2 km/h = 0.56 m/s | Design spec |
| Maximum slope | 30° | Design spec (Markeaton Park) |
| Operating voltage | 12V (from 22.2V battery via buck converter) | EA-03 |

---

## 2. Torque Calculations

### 2.1 Flat Ground — Cruising

```
Rolling resistance force:
  F_roll = m × g × μ_r

Surface rolling resistance coefficients (μ_r):
  Pavement: 0.01 - 0.02
  Gravel:   0.02 - 0.04
  Short grass: 0.05 - 0.10
  Long grass:  0.10 - 0.15

Worst case (long grass):
  F_roll = 34.2 × 9.81 × 0.15 = 50.3 N

Torque per wheel (6 wheels sharing load):
  T_per_wheel = (F_roll / 6) × r_wheel
  T_per_wheel = (50.3 / 6) × 0.1
  T_per_wheel = 0.838 N·m = 8.55 kg·cm
```

### 2.2 Slope Climbing — 30°

```
Gravity component (pulling rover back down slope):
  F_gravity = m × g × sin(θ)
  F_gravity = 34.2 × 9.81 × sin(30°)
  F_gravity = 34.2 × 9.81 × 0.5
  F_gravity = 167.8 N

Rolling resistance on slope:
  F_roll = m × g × cos(θ) × μ_r
  F_roll = 34.2 × 9.81 × cos(30°) × 0.10
  F_roll = 34.2 × 9.81 × 0.866 × 0.10
  F_roll = 29.1 N

Total force required:
  F_total = F_gravity + F_roll = 167.8 + 29.1 = 196.9 N

Torque per wheel (6 wheels):
  T_per_wheel = (196.9 / 6) × 0.1
  T_per_wheel = 3.28 N·m = 33.5 kg·cm
```

### 2.3 Starting from Standstill on Grass

```
Static friction is higher than rolling resistance.
Starting force coefficient (grass): ~0.15 - 0.20

F_start = m × g × μ_static
F_start = 34.2 × 9.81 × 0.20 = 67.1 N

Plus any slope:
For flat start on grass:
  T_per_wheel = (67.1 / 6) × 0.1
  T_per_wheel = 1.12 N·m = 11.4 kg·cm

For start on 15° grassy slope:
  F_gravity = 34.2 × 9.81 × sin(15°) = 86.8 N
  F_start = 34.2 × 9.81 × cos(15°) × 0.20 = 64.8 N
  F_total = 86.8 + 64.8 = 151.6 N
  T_per_wheel = (151.6 / 6) × 0.1
  T_per_wheel = 2.53 N·m = 25.8 kg·cm
```

### 2.4 Summary of Torque Requirements

| Scenario | Force (N) | Torque/Wheel (N·m) | Torque/Wheel (kg·cm) |
|----------|-----------|--------------------|--------------------|
| Flat pavement cruise | 6.7 | 0.11 | 1.14 |
| Flat grass cruise | 50.3 | 0.84 | 8.55 |
| 15° slope grass | 151.6 | 2.53 | 25.8 |
| 30° slope grass | 196.9 | 3.28 | **33.5** |
| Start on flat grass | 67.1 | 1.12 | 11.4 |
| Start on 15° grass | 151.6 | 2.53 | 25.8 |

**Critical requirement: Each motor must deliver at least 33.5 kg·cm at the wheel under worst-case conditions (30° slope, full weight, grass surface).**

Note: This is stall-adjacent torque. Motors should be rated for at least 2× this at rated load for thermal safety: **minimum rated torque = 15-20 kg·cm, stall torque = 35+ kg·cm**.

---

## 3. RPM Calculations

### 3.1 Target Wheel Speed

```
Target speed: 5 km/h = 1.39 m/s
Wheel circumference: π × 0.2m = 0.628m
Wheel RPM: (1.39 / 0.628) × 60 = 132.8 RPM

Target speed: 2 km/h (slope) = 0.56 m/s
Wheel RPM: (0.56 / 0.628) × 60 = 53.5 RPM
```

**Target wheel RPM: 50-135 RPM** (variable via PWM speed control)

### 3.2 Motor-to-Wheel Gearing

If using direct drive (motor shaft = wheel axle): motor must output 50-135 RPM.
If using additional gear reduction: motor RPM can be higher with proportionally more torque at the wheel.

**Recommendation**: Direct drive with a gearmotor rated at ~100-200 RPM no-load. This simplifies the drivetrain (no external gearing) and reduces failure points.

---

## 4. Motor Selection

### 4.1 Candidate Comparison

| Motor | Voltage | No-Load RPM | Rated Torque | Stall Torque | Rated Current | Stall Current | Weight | Price (each) |
|-------|---------|-------------|-------------|-------------|---------------|---------------|--------|-------------|
| **JGB37-520 (107RPM)** | 12V | 107 | 2.8 kg·cm | 11 kg·cm | 0.17A | 2.5A | 175g | ~$8 |
| **JGB37-520 (66RPM)** | 12V | 66 | 5.0 kg·cm | 20 kg·cm | 0.20A | 3.0A | 175g | ~$8 |
| **JGB37-520 (45RPM)** | 12V | 45 | 8.0 kg·cm | 25 kg·cm | 0.25A | 3.5A | 175g | ~$8 |
| **JGA25-370 (130RPM)** | 12V | 130 | 1.5 kg·cm | 6 kg·cm | 0.15A | 1.5A | 100g | ~$6 |
| **Pololu 37D (100RPM)** | 12V | 100 | 9.0 kg·cm | 30 kg·cm | 0.3A | 5.0A | 210g | ~$25 |
| **Pololu 37D (70RPM)** | 12V | 70 | 14 kg·cm | 45 kg·cm | 0.35A | 6.5A | 210g | ~$25 |
| **Chihai CHR-GM37-520 (80RPM)** | 12V | 80 | 10 kg·cm | 35 kg·cm | 0.25A | 4.0A | 185g | ~$12 |

### 4.2 Analysis

Our requirement: **33.5 kg·cm stall torque minimum** (30° slope worst case).

Evaluating each:
- **JGB37-520 (107RPM)**: 11 kg·cm stall — **INSUFFICIENT** (only 33% of requirement)
- **JGB37-520 (66RPM)**: 20 kg·cm stall — **INSUFFICIENT** (60% of requirement)
- **JGB37-520 (45RPM)**: 25 kg·cm stall — **MARGINAL** (75%, no safety margin)
- **JGA25-370**: 6 kg·cm stall — **FAR TOO WEAK**
- **Pololu 37D (100RPM)**: 30 kg·cm stall — **MARGINAL** (90%)
- **Pololu 37D (70RPM)**: 45 kg·cm stall — **SUFFICIENT** (134%, good margin)
- **Chihai CHR-GM37-520 (80RPM)**: 35 kg·cm stall — **SUFFICIENT** (104%, tight)

### 4.3 Important Consideration: Real-World vs Worst-Case

The 33.5 kg·cm requirement assumes:
- Full 34.2 kg weight (Phase 3 + fridge loaded + 1.5× safety factor)
- 30° slope (very steep — steeper than most park paths)
- Long grass surface
- All conditions simultaneously

In reality, Phase 2 (16.7 kg empty) on a typical park path (15° max, short grass):
```
T_realistic = ((16.7 × 9.81 × sin(15°) + 16.7 × 9.81 × cos(15°) × 0.05) / 6) × 0.1
T_realistic = ((42.4 + 7.9) / 6) × 0.1
T_realistic = 0.84 N·m = 8.5 kg·cm
```

Even the JGB37-520 (107RPM) handles this at its rated torque.

### 4.4 Decision Matrix

| Criterion | Weight | JGB37-520 (45RPM) | Pololu 37D (70RPM) | Chihai (80RPM) |
|-----------|--------|-------------------|--------------------|-----------------|
| Stall torque | 30% | 6/10 (25 kg·cm) | 9/10 (45 kg·cm) | 7/10 (35 kg·cm) |
| Speed range | 15% | 4/10 (45RPM max = 2.8 km/h) | 7/10 (70RPM = 4.4 km/h) | 8/10 (80RPM = 5 km/h) |
| Cost (×6) | 25% | 9/10 ($48 total) | 4/10 ($150 total) | 7/10 ($72 total) |
| Availability | 10% | 8/10 (Amazon/AliExpress) | 7/10 (Pololu direct) | 6/10 (AliExpress) |
| Encoder option | 10% | 8/10 (hall encoder variant) | 9/10 (built-in encoder) | 7/10 (encoder variant) |
| Weight | 10% | 8/10 (175g) | 6/10 (210g) | 7/10 (185g) |
| **Weighted Score** | | **6.85** | **6.95** | **7.05** |

### 4.5 Recommendation

**Primary: Chihai CHR-GM37-520 80RPM with hall encoder** (~$12 each, $72 for 6)

Rationale:
- 35 kg·cm stall torque meets the worst-case requirement (just)
- 80 RPM gives top speed of 5 km/h (matches target exactly)
- Hall encoder variant enables PID speed control and odometry
- Good balance of cost, performance, and availability
- Same 37mm form factor as JGB37-520 — well-documented mounting dimensions

**Fallback: Pololu 37D 70RPM** ($25 each, $150 for 6) — if Chihai stall torque proves insufficient in testing. Pololu motors have better quality control and documentation.

**Phase 1: N20 micro gearmotors** (~$3 each) — sufficient for the 1 kg prototype at 0.4 scale.

---

## 5. Motor Driver Selection

### 5.1 Requirements

- Control 6 motors independently (forward/reverse/speed via PWM)
- Handle stall current of motors (up to 4-5A per motor)
- 12V operating voltage
- ESP32-S3 compatible (3.3V logic)

### 5.2 Candidate Comparison

| Driver | Channels | Max Current (per channel) | Voltage | Logic Level | Price | Size |
|--------|----------|--------------------------|---------|-------------|-------|------|
| **BTS7960** | 1 (H-bridge) | 43A continuous | 6-27V | 3.3-5V | ~$6 | Large |
| **L298N** | 2 (dual H-bridge) | 2A continuous | 5-35V | 5V (need level shift) | ~$3 | Medium |
| **DRV8833** | 2 (dual H-bridge) | 1.5A continuous | 2.7-10.8V | 3.3V native | ~$2 | Small |
| **Cytron MDD10A** | 2 (dual) | 10A continuous | 5-25V | 3.3-5V | ~$15 | Medium |
| **TB6612FNG** | 2 (dual) | 1.2A continuous | 4.5-13.5V | 3.3-5V | ~$2 | Small |

### 5.3 Analysis

- **L298N**: 2A is too low for our motor stall currents (4-5A). Would need current limiting.
- **DRV8833**: 1.5A — far too low. 10.8V max — can't run at 12V.
- **TB6612FNG**: 1.2A — far too low.
- **BTS7960**: 43A — massively overspec but reliable, cheap, well-documented. Need 6 modules (one per motor).
- **Cytron MDD10A**: 10A — perfect current rating. 2 channels = need 3 modules.

### 5.4 Recommendation

**Cytron MDD10A** (or similar dual 10A H-bridge) — 3 modules for 6 motors.

Rationale:
- 10A per channel handles stall current with margin
- Dual channel means 3 boards (vs 6 for BTS7960) — simpler wiring
- 3.3V logic compatible — direct ESP32-S3 connection
- More appropriately rated than BTS7960 (less wasted capacity)
- Cost: 3 × $15 = $45

**Fallback**: 3× BTS7960 dual modules (some modules have 2 channels) — $18 total but bulkier.

**Phase 1**: 2× L298N ($6 total) — sufficient for N20 motors at <0.5A.

---

## 6. Steering System

### 6.1 Steering Torque Calculation

```
The torque to turn a wheel on a surface:
  T_steer = μ_s × F_normal × r_contact

Where:
  μ_s = surface friction coefficient (~0.5 for rubber on grass)
  F_normal = weight on one steered wheel
  r_contact = effective contact radius of tyre (~25mm for 80mm wide wheel)

Worst case (Phase 3 loaded, weight biased to one wheel):
  F_normal = 5 kg × 9.81 = 49.1 N  (one wheel carrying ~5kg)
  T_steer = 0.5 × 49.1 × 0.025 = 0.61 N·m = 6.3 kg·cm
```

**Minimum steering servo torque: 6.3 kg·cm** with 2× safety factor = **12.6 kg·cm**.

### 6.2 Servo Selection

| Servo | Torque (4.8V) | Torque (6V) | Speed | Weight | Price |
|-------|--------------|-------------|-------|--------|-------|
| **MG996R** | 11 kg·cm | 13 kg·cm | 0.14s/60° | 55g | ~$6 |
| **DS3218** | 19 kg·cm | 21 kg·cm | 0.14s/60° | 60g | ~$10 |
| **MG995** | 8.5 kg·cm | 10 kg·cm | 0.17s/60° | 55g | ~$4 |
| **PDI-6221MG** | 16 kg·cm | 20 kg·cm | 0.16s/60° | 62g | ~$8 |

### 6.3 Recommendation

**Phase 2: MG996R** ($6 each, $24 for 4) — 13 kg·cm at 6V meets our 12.6 kg·cm requirement. The most widely used hobby servo, well-documented, cheap.

**Phase 3: DS3218** ($10 each, $40 for 4) — 21 kg·cm at 6V provides ample margin for heavier metal construction. Metal gears, more durable.

**Phase 1: SG90** ($2 each, $8 for 4) — 1.8 kg·cm is fine for the 1 kg prototype.

### 6.4 Ackermann Steering Geometry

```
For correct Ackermann steering (inner wheel turns more than outer):

  tan(θ_inner) = L / (R - W/2)
  tan(θ_outer) = L / (R + W/2)

Where:
  L = wheelbase = 680mm
  W = track width = 700mm
  R = turning radius

For R = 1000mm (tight turn):
  θ_inner = arctan(680 / (1000 - 350)) = arctan(1.046) = 46.3°
  θ_outer = arctan(680 / (1000 + 350)) = arctan(0.504) = 26.7°

For R = 2000mm (gentle turn):
  θ_inner = arctan(680 / (2000 - 350)) = arctan(0.412) = 22.4°
  θ_outer = arctan(680 / (2000 + 350)) = arctan(0.289) = 16.1°

Minimum turning radius (servo max 60° from centre):
  R_min = L / tan(60°) + W/2
  R_min = 680 / 1.732 + 350
  R_min = 393 + 350 = 743mm

Point turn (opposite steering):
  R_min = 0 (rotates on the spot)
```

### 6.5 Steering Modes (Software-Controlled)

| Mode | Front Inner | Front Outer | Rear Inner | Rear Outer | Result |
|------|-------------|-------------|------------|------------|--------|
| Normal | +θ_i | +θ_o | -θ_o | -θ_i | Standard car-like turn |
| Point Turn | +45° | +45° | -45° | -45° | Rotate on the spot |
| Crab Walk | +θ | +θ | +θ | +θ | Sideways movement |
| Arc Turn | +θ_i | +θ_o | 0° | 0° | Front-steer only |

All modes are software-selectable from the phone app. The ESP32-S3 calculates servo angles based on desired turn radius and mode.

---

## 7. Wheel Encoder Specification

### 7.1 Requirements

- Measure wheel speed for PID control
- Measure distance for odometry
- Resolution sufficient for smooth low-speed control

### 7.2 Encoder Type: Hall Effect (built into motor)

The recommended Chihai motors are available with built-in hall encoders (2-channel, quadrature).

```
Typical hall encoder specification:
  Pulses per revolution (motor shaft): 11 PPR
  Quadrature (×4): 44 counts per motor revolution
  With gear ratio ~1:45 (for 80RPM variant):
    Counts per wheel revolution: 44 × 45 = 1,980 counts

  Wheel circumference: 628mm
  Distance per count: 628 / 1,980 = 0.317mm

  At 5 km/h (1390mm/s): 4,385 counts/s = 4.4 kHz
```

**Resolution: 0.32mm per count** — excellent for odometry and PID control.
**Frequency at max speed: 4.4 kHz** — easily handled by ESP32-S3 interrupt pins.

---

## 8. Power Consumption Profile

| Scenario | Per Motor (A) | Total 6 Motors (A) | Total Power (W) |
|----------|--------------|-------------------|-----------------|
| Cruising flat pavement | 0.15 | 0.9 | 10.8 |
| Cruising grass | 0.20 | 1.2 | 14.4 |
| Climbing 15° slope | 0.50 | 3.0 | 36.0 |
| Climbing 30° slope | 1.00 | 6.0 | 72.0 |
| Stall (stuck) | 4.00 | 24.0 | 288.0 |
| Steering servos (active turning) | — | 1.0 | 6.0 |
| Steering servos (holding) | — | 0.2 | 1.2 |

**Typical driving power draw: 15-40W** (motors only).
**Maximum sustained: 72W** (steep slope, not sustainable for long).
**Motor stall: 288W** — software should detect stall within 2 seconds and cut power.

---

## 9. Summary of Drivetrain Specifications

| Component | Phase 1 | Phase 2 | Phase 3 |
|-----------|---------|---------|---------|
| Drive motors | N20 6V 100RPM | Chihai 37mm 12V 80RPM | Same (or upgrade) |
| Motor torque (stall) | 0.5 kg·cm | 35 kg·cm | 35+ kg·cm |
| Motor drivers | 2× L298N | 3× Cytron MDD10A | Same |
| Steering servos | SG90 (1.8 kg·cm) | MG996R (13 kg·cm) | DS3218 (21 kg·cm) |
| Wheel encoders | None | Hall effect (built-in) | Hall effect (built-in) |
| Top speed | 3 km/h | 5 km/h | 5 km/h |
| Min turning radius | ~300mm | 743mm | 743mm |
| Max slope | 15° | 30° | 30° |

---

## 10. References

- [JGB37-520 Specifications — Abra Electronics](https://abra-electronics.com/electromechanical/motors/gear-motors/metal-gearmotors/jgb37-520-series/)
- [Pololu 37D Metal Gearmotors](https://www.pololu.com/category/116/37d-metal-gearmotors)
- [BTS7960 Motor Driver Datasheet](https://www.ovaga.com/blog/transistor/bts7960-motor-driver-datasheet-and-circuit-diagram)
- [Cytron MDD10A Motor Driver](https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver)
- [Ackermann Steering Geometry — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_steering_geometry)
- [Rolling Resistance Coefficients — Engineering Toolbox](https://www.engineeringtoolbox.com/rolling-friction-resistance-d_1303.html)

---

*Document EA-02 v1.0 — 2026-03-15*
