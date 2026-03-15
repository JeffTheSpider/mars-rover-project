# Engineering Analysis 10: Ackermann Steering Geometry Calculations

**Document**: EA-10
**Date**: 2026-03-15
**Purpose**: Calculate steering angles, turning radii, and wheel speeds for all three steering modes (Ackermann, point turn, crab walk) with worked examples at specific turn radii. Provide servo angle mappings for firmware implementation.
**Depends on**: EA-01 (Suspension geometry), EA-02 (Drivetrain), EA-08 (Phase 1 dimensions)

---

## 1. Rover Geometry Reference

### 1.1 Full Scale (Phase 2/3)

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Wheelbase (front-to-rear axle) | L | 900mm |
| Track width (wheel centre-to-centre) | W | 700mm |
| Front-to-middle axle | L_fm | 450mm |
| Middle-to-rear axle | L_mr | 450mm |
| Half track width | W/2 | 350mm |
| Wheel radius | r | 100mm |
| Steering wheels | — | 4 (FL, FR, RL, RR) |
| Fixed wheels | — | 2 (ML, MR) |

### 1.2 Phase 1 (0.4 Scale)

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Wheelbase | L | 360mm |
| Track width | W | 280mm |
| Front-to-middle | L_fm | 180mm |
| Middle-to-rear | L_mr | 180mm |
| Half track width | W/2 | 140mm |
| Wheel radius | r | 40mm |

---

## 2. Ackermann Steering Theory

### 2.1 The Problem

When a vehicle turns, the inner wheels trace a smaller circle than the outer wheels. If all wheels are steered to the same angle, the inner wheels must scrub (slide sideways), causing tyre wear, increased resistance, and poor handling.

Ackermann steering geometry solves this by steering the inner wheel at a larger angle than the outer wheel, so all wheels' axle lines converge at the same Instantaneous Centre of Rotation (ICR).

### 2.2 Standard Ackermann (2-Axle Vehicle)

For a simple 2-axle vehicle with front-wheel steering:

```
cot(δ_outer) - cot(δ_inner) = W / L

Where:
  δ_inner = inner wheel steering angle (larger)
  δ_outer = outer wheel steering angle (smaller)
  W = track width
  L = wheelbase
```

### 2.3 Our Rover: 3-Axle, 4-Wheel Steering

Our rover has 3 axles (front, middle, rear) with steering on front and rear, middle fixed. The front and rear steering work in opposite directions — rear wheels turn opposite to front for tighter turning.

```
Top View — Turning Right (ICR on right side):

                ICR (Instantaneous Centre of Rotation)
                  *
                 /|\
                / | \
               /  |  \
              /   |   \
    W1(FL)---/----+----\---W6(FR)     Front axle: steer RIGHT
    δ_FL    /     |     \   δ_FR
           /      |      \
          /       |       \
    W2(ML)--------+--------W5(MR)    Middle axle: FIXED (no steer)
          \       |       /
           \      |      /
            \     |     /
    W3(RL)---\----+----/---W4(RR)    Rear axle: steer LEFT (opposite)
    δ_RL      \   |   /    δ_RR
               \  |  /
                \ | /
                 \|/
                  * (ICR is on this line, at distance R from centre)
```

For our 4-wheel-steer 6-wheel rover, the ICR lies on the line extending from the middle axle (the fixed axle). This simplifies the geometry:

**Front wheels steer toward the turn:**
```
tan(δ_front_inner) = L_fm / (R - W/2)
tan(δ_front_outer) = L_fm / (R + W/2)
```

**Rear wheels steer away from the turn (opposite direction):**
```
tan(δ_rear_inner) = L_mr / (R - W/2)
tan(δ_rear_outer) = L_mr / (R + W/2)
```

Where R is the turn radius measured from the ICR to the rover centre.

Since L_fm = L_mr = 450mm in our design, the front and rear angles are equal in magnitude but opposite in direction. This creates a symmetric 4-wheel-steer system.

---

## 3. Worked Examples (Full Scale)

### 3.1 Turn Radius = 5000mm (gentle)

```
L_fm = 450mm, W/2 = 350mm, R = 5000mm

Front inner:  δ = atan(450 / (5000 - 350)) = atan(450 / 4650) = atan(0.0968) = 5.53°
Front outer:  δ = atan(450 / (5000 + 350)) = atan(450 / 5350) = atan(0.0841) = 4.81°
Rear inner:   δ = -5.53° (opposite direction)
Rear outer:   δ = -4.81° (opposite direction)

Difference:   5.53° - 4.81° = 0.72° (small — nearly parallel at this radius)
```

### 3.2 Turn Radius = 2000mm (moderate)

```
Front inner:  δ = atan(450 / (2000 - 350)) = atan(450 / 1650) = atan(0.2727) = 15.26°
Front outer:  δ = atan(450 / (2000 + 350)) = atan(450 / 2350) = atan(0.1915) = 10.84°
Rear inner:   δ = -15.26°
Rear outer:   δ = -10.84°

Difference:   15.26° - 10.84° = 4.42° (noticeable Ackermann correction)
```

### 3.3 Turn Radius = 1000mm (tight)

```
Front inner:  δ = atan(450 / (1000 - 350)) = atan(450 / 650) = atan(0.6923) = 34.70°
Front outer:  δ = atan(450 / (1000 + 350)) = atan(450 / 1350) = atan(0.3333) = 18.43°
Rear inner:   δ = -34.70°
Rear outer:   δ = -18.43°

Difference:   34.70° - 18.43° = 16.27° (large correction needed)
```

### 3.4 Minimum Turn Radius

Limited by maximum servo angle. MG996R has 180° range, but mechanical clearance limits steering to ±35° (70° total). At Phase 1, SG90 has the same practical limit.

```
Maximum inner angle: δ_max = 35°

R_min - W/2 = L_fm / tan(δ_max)
R_min = L_fm / tan(35°) + W/2
R_min = 450 / tan(35°) + 350
R_min = 450 / 0.7002 + 350
R_min = 642.7 + 350
R_min = 992.7mm ≈ 993mm

At this radius, the outer front wheel angle is:
δ_outer = atan(450 / (993 + 350)) = atan(450 / 1343) = atan(0.335) = 18.5°
```

**Minimum turn radius: ~1.0m** (ICR to rover centre). The rover sweeps a circle of ~1.35m radius at the outermost wheel.

### 3.5 Summary Table (Full Scale)

| Turn Radius (mm) | δ Front Inner | δ Front Outer | δ Rear Inner | δ Rear Outer | Notes |
|-------------------|--------------|---------------|-------------|-------------|-------|
| 993 (minimum) | 35.0° | 18.5° | -35.0° | -18.5° | Max servo angle |
| 1000 | 34.7° | 18.4° | -34.7° | -18.4° | Very tight |
| 1500 | 21.4° | 13.7° | -21.4° | -13.7° | Tight |
| 2000 | 15.3° | 10.8° | -15.3° | -10.8° | Moderate |
| 3000 | 9.7° | 7.5° | -9.7° | -7.5° | Normal |
| 5000 | 5.5° | 4.8° | -5.5° | -4.8° | Gentle |
| 10000 | 2.6° | 2.4° | -2.6° | -2.4° | Very gentle |
| ∞ (straight) | 0° | 0° | 0° | 0° | All straight |

### 3.6 Phase 1 (0.4 Scale) — Equivalent Table

| Turn Radius (mm) | δ Front Inner | δ Front Outer | Minimum R |
|-------------------|--------------|---------------|-----------|
| 397 (minimum) | 35.0° | 18.5° | ±35° limit |
| 500 | 26.6° | 15.9° | Tight |
| 800 | 15.3° | 11.5° | Moderate |
| 1000 | 11.8° | 9.5° | Normal |
| 2000 | 5.6° | 4.9° | Gentle |

Phase 1 minimum turn radius: ~0.40m.

---

## 4. Wheel Speed Differentials

### 4.1 Why Wheel Speeds Must Differ

When turning, each wheel traces a circle of different radius around the ICR. Wheels on larger circles must spin faster to avoid scrubbing.

### 4.2 Wheel Circle Radii

For a turn of radius R (to rover centre):

```
Middle-left:  R_ML = R - W/2 = R - 350
Middle-right: R_MR = R + W/2 = R + 350

Front-left:   R_FL = sqrt((R - W/2)² + L_fm²) = sqrt((R-350)² + 450²)
Front-right:  R_FR = sqrt((R + W/2)² + L_fm²) = sqrt((R+350)² + 450²)
Rear-left:    R_RL = sqrt((R - W/2)² + L_mr²) = sqrt((R-350)² + 450²)
Rear-right:   R_RR = sqrt((R + W/2)² + L_mr²) = sqrt((R+350)² + 450²)
```

Note: Front and rear on the same side have identical circle radii (because L_fm = L_mr).

### 4.3 Speed Ratios

If the rover centre moves at speed V_centre:
```
ω_centre = V_centre / R  (angular velocity of turn)

V_wheel = ω_centre × R_wheel

Speed ratio = R_wheel / R_centre = R_wheel / R
```

### 4.4 Worked Example: R = 2000mm, V = 5 km/h

```
R_ML = 2000 - 350 = 1650mm
R_MR = 2000 + 350 = 2350mm
R_FL = sqrt(1650² + 450²) = sqrt(2,722,500 + 202,500) = sqrt(2,925,000) = 1710mm
R_FR = sqrt(2350² + 450²) = sqrt(5,522,500 + 202,500) = sqrt(5,725,000) = 2393mm

Speed ratios (normalised to centre speed):
  W2 (ML): 1650/2000 = 0.825  → 4.13 km/h
  W5 (MR): 2350/2000 = 1.175  → 5.88 km/h
  W1 (FL): 1710/2000 = 0.855  → 4.28 km/h
  W6 (FR): 2393/2000 = 1.197  → 5.98 km/h
  W3 (RL): 1710/2000 = 0.855  → 4.28 km/h (same as FL)
  W4 (RR): 2393/2000 = 1.197  → 5.98 km/h (same as FR)
```

### 4.5 Phase 1 Simplification

In Phase 1, middle+rear motors on each side are wired in parallel (same speed). This means W2+W3 get the same voltage and W4+W5 get the same voltage. The speed difference between middle and rear wheels at the same side is zero (they're on identical circle radii with our symmetric design), so this is actually correct.

The only compromise is that front wheels on Phase 1 also share speed with their side's mid+rear. For gentle turns this is fine. For tight turns, the front wheel's larger circle radius means it should spin slightly faster — the small speed error causes minor scrubbing that's acceptable at prototype scale.

---

## 5. Point Turn Mode

### 5.1 Geometry

In point turn (zero-radius turn), the rover rotates about its own centre. The ICR is at the rover's centre point.

```
Top View — Point Turn (clockwise):

    W1(FL)←──────── * ────────→W6(FR)
      ↓                          ↑
      ↓                          ↑
    W2(ML)←──────── * ────────→W5(MR)
      ↓                          ↑
      ↓                          ↑
    W3(RL)←──────── * ────────→W4(RR)

Left side: drives BACKWARD
Right side: drives FORWARD
Middle wheels: drive along track width direction
Front/rear: angled to point tangent to their circle
```

### 5.2 Steering Angles for Point Turn

Each steered wheel must point tangent to the circle it traces around the centre:

```
Front-left:   δ_FL = atan(L_fm / (W/2)) = atan(450 / 350) = 52.1°
Front-right:  δ_FR = -atan(L_fm / (W/2)) = -52.1°  (opposite direction)
Rear-left:    δ_RL = -atan(L_mr / (W/2)) = -52.1°
Rear-right:   δ_RR = atan(L_mr / (W/2)) = 52.1°
```

**Problem**: 52.1° exceeds our ±35° servo limit.

### 5.3 Practical Point Turn

Since we can't achieve the ideal 52.1° angle, we have two options:

**Option A: Skid-steer point turn** — All wheels straight, left side reverse, right side forward. The wheels scrub sideways. This works but wears treads and requires more torque.

**Option B: Best-effort angled point turn** — Steer all 4 wheels to their maximum (±35°), then skid-steer. Reduces scrubbing compared to straight wheels:

```
At ±35° (best we can do):
- Scrubbing angle: 52.1° - 35° = 17.1° of slip
- Significantly less scrub than 0° (straight wheels)
- Middle wheels always scrub (no steering) but only 2 of 6 wheels
```

**Recommendation**: Use Option B. Steer front wheels to ±35° inward, rear wheels to ±35° outward, then run left side backward and right side forward. The 17.1° residual slip is acceptable on grass/gravel.

### 5.4 Point Turn Wheel Speeds

All wheels trace circles of the same radius from the rover centre:
```
Middle wheels: R = W/2 = 350mm
Front/rear:    R = sqrt(350² + 450²) = sqrt(325,000) = 570mm
```

For a desired rotation rate ω_turn:
```
V_middle = ω_turn × 350mm
V_front_rear = ω_turn × 570mm

Speed ratio (front/rear to middle): 570/350 = 1.63
```

So front and rear wheels should spin 1.63× faster than middle wheels for slip-free rotation.

**Phase 1 simplification**: Middle and rear share speed, so set them to the average: (1.0 + 1.63) / 2 ≈ 1.3× front speed. Acceptable approximation.

### 5.5 Point Turn Speed Limit

At the prototype scale, limit point turn speed to 50% max to prevent tip-over (high lateral forces on a light rover).

---

## 6. Crab Walk Mode

### 6.1 Geometry

Crab walk moves the rover sideways without rotating. All 4 steered wheels turn to the same angle, and all 6 motors drive at the same speed.

```
Top View — Crab Walk Right:

    W1(FL)→  →  →  →W6(FR)→
         ↗              ↗
    W2(ML)→  →  →  →W5(MR)→     All wheels pointed ~45° right
         ↗              ↗        All driving forward at same speed
    W3(RL)→  →  →  →W4(RR)→
```

### 6.2 Steering Angles

All 4 steered wheels set to the same angle α (the desired direction of travel):

```
δ_FL = δ_FR = δ_RL = δ_RR = α

Where α = desired travel direction:
  0° = forward (normal driving)
  90° = pure sideways right
  -90° = pure sideways left
  45° = diagonal forward-right
  etc.
```

Limited by servo range: α ∈ [-35°, +35°]. The rover can crab walk at up to 35° off its heading — it cannot move purely sideways (would need 90°).

### 6.3 Practical Crab Walk

At α = 35° (maximum), the rover moves at an angle of 35° from its heading. The forward component is cos(35°) = 0.82 of speed, and the lateral component is sin(35°) = 0.57 of speed.

For parking-style manoeuvres, this is sufficient. For true sideways movement, use point turn to rotate 90°, then drive forward.

### 6.4 Motor Speeds in Crab Walk

All motors run at the same speed and direction. The middle (fixed) wheels will experience some side-slip at large crab angles — this is the trade-off of having fixed middle wheels.

Side-slip angle on middle wheels = α (the crab angle). At α = 35°, this is significant but acceptable on grass/gravel. On pavement, limit crab angle to ~15° to reduce tyre scrub.

---

## 7. Servo Calibration & Mapping

### 7.1 Servo PWM to Angle Mapping

Standard servo PWM:
```
500 μs  = 0° (full left)
1500 μs = 90° (centre)
2500 μs = 180° (full right)

Microseconds per degree = (2500 - 500) / 180 = 11.11 μs/°
```

### 7.2 Steering Angle to Servo PWM

Define steering angle convention:
- 0° = straight ahead
- Positive = turning right (clockwise from above)
- Negative = turning left

```
Servo PWM = 1500 + (steering_angle × 11.11)

Examples:
  0° (straight):    1500 μs
  +35° (max right): 1500 + 35 × 11.11 = 1889 μs
  -35° (max left):  1500 - 35 × 11.11 = 1111 μs
```

### 7.3 Servo Direction Convention

Not all servos are mounted the same way. Define which direction is "positive" for each:

| Servo | Mounted | Positive PWM = | Sign Convention |
|-------|---------|----------------|-----------------|
| FL | Left side | Wheel turns RIGHT | Normal (+) |
| FR | Right side | Wheel turns RIGHT | Normal (+) |
| RL | Left side | Wheel turns LEFT | **Inverted (-)** |
| RR | Right side | Wheel turns LEFT | **Inverted (-)** |

The rear servos are inverted because they're mounted with opposite orientation (mirror image of front). In firmware, apply a sign flip for rear servos:

```c
void setSteeringAngle(int servo, float angle_deg) {
    float pwm_us;

    // Rear servos are inverted
    if (servo == SERVO_RL || servo == SERVO_RR) {
        angle_deg = -angle_deg;
    }

    // Clamp to ±35°
    angle_deg = constrain(angle_deg, -35.0, 35.0);

    // Convert to PWM
    pwm_us = 1500.0 + (angle_deg * 11.11);

    // Apply per-servo trim offset (calibrated during setup)
    pwm_us += servo_trim[servo];

    // Write to servo
    setServoPWM(servo, pwm_us);
}
```

### 7.4 Trim Calibration

Each servo has manufacturing variation. A calibration routine should:
1. Set all servos to 1500 μs (nominal centre)
2. Visually check if each wheel points straight
3. Adjust trim offset (±50 μs range typically) until straight
4. Save trim values to EEPROM/flash

**Phase 1 calibration process**:
- Place rover on flat surface
- Use a straight edge along the side to check wheel alignment
- Adjust trim in firmware until all wheels are parallel
- Save and test

---

## 8. Firmware Implementation

### 8.1 Ackermann Calculation Function

```c
// Calculate Ackermann steering angles for a desired turn radius
// R_mm: turn radius in mm (positive = right turn, negative = left)
// Returns 4 servo angles in degrees

struct SteeringAngles {
    float fl, fr, rl, rr;
};

SteeringAngles calculateAckermann(float R_mm) {
    SteeringAngles angles;

    if (abs(R_mm) < R_MIN) {
        // Below minimum radius — clamp
        R_mm = (R_mm > 0) ? R_MIN : -R_MIN;
    }

    float R = abs(R_mm);
    int sign = (R_mm > 0) ? 1 : -1;  // Right turn = positive

    // Front wheel angles
    float delta_inner = atan2(L_FM, R - W_HALF) * RAD_TO_DEG;
    float delta_outer = atan2(L_FM, R + W_HALF) * RAD_TO_DEG;

    // Rear wheel angles (opposite direction, same magnitude)
    // For our symmetric design (L_fm == L_mr), rear = -front

    if (sign > 0) {  // Right turn: right side is inner
        angles.fr = delta_inner * sign;   // inner front
        angles.fl = delta_outer * sign;   // outer front
        angles.rr = -delta_inner * sign;  // inner rear (opposite)
        angles.rl = -delta_outer * sign;  // outer rear (opposite)
    } else {  // Left turn: left side is inner
        angles.fl = delta_inner * sign;
        angles.fr = delta_outer * sign;
        angles.rl = -delta_inner * sign;
        angles.rr = -delta_outer * sign;
    }

    return angles;
}
```

### 8.2 Wheel Speed Calculation Function

```c
// Calculate relative wheel speeds for a desired turn radius
// Returns 6 speed multipliers (1.0 = nominal speed)

struct WheelSpeeds {
    float w1_fl, w2_ml, w3_rl, w4_rr, w5_mr, w6_fr;
};

WheelSpeeds calculateWheelSpeeds(float R_mm) {
    WheelSpeeds speeds;

    if (abs(R_mm) > 50000) {
        // Essentially straight — all wheels same speed
        speeds.w1_fl = speeds.w2_ml = speeds.w3_rl = 1.0;
        speeds.w4_rr = speeds.w5_mr = speeds.w6_fr = 1.0;
        return speeds;
    }

    float R = abs(R_mm);

    // Circle radii for each wheel
    float R_inner_mid = R - W_HALF;
    float R_outer_mid = R + W_HALF;
    float R_inner_end = sqrt(sq(R - W_HALF) + sq(L_FM));
    float R_outer_end = sqrt(sq(R + W_HALF) + sq(L_FM));

    // Normalise to centre speed (R)
    float inner_mid_ratio = R_inner_mid / R;
    float outer_mid_ratio = R_outer_mid / R;
    float inner_end_ratio = R_inner_end / R;
    float outer_end_ratio = R_outer_end / R;

    if (R_mm > 0) {  // Right turn: right = inner
        speeds.w5_mr = inner_mid_ratio;  // MR inner
        speeds.w2_ml = outer_mid_ratio;  // ML outer
        speeds.w6_fr = inner_end_ratio;  // FR inner
        speeds.w1_fl = outer_end_ratio;  // FL outer
        speeds.w4_rr = inner_end_ratio;  // RR inner
        speeds.w3_rl = outer_end_ratio;  // RL outer
    } else {  // Left turn: left = inner
        speeds.w2_ml = inner_mid_ratio;
        speeds.w5_mr = outer_mid_ratio;
        speeds.w1_fl = inner_end_ratio;
        speeds.w6_fr = outer_end_ratio;
        speeds.w3_rl = inner_end_ratio;
        speeds.w4_rr = outer_end_ratio;
    }

    return speeds;
}
```

### 8.3 Steering Mode Selection

```c
enum SteeringMode {
    STEER_ACKERMANN,  // Normal driving with Ackermann correction
    STEER_POINT_TURN, // Rotate in place
    STEER_CRAB_WALK,  // Move diagonally without rotating
    STEER_STRAIGHT    // All wheels straight
};

void applySteeringMode(SteeringMode mode, float param) {
    switch (mode) {
        case STEER_ACKERMANN:
            // param = turn radius in mm (+ = right, - = left)
            applyAckermann(param);
            break;

        case STEER_POINT_TURN:
            // param = rotation speed (-100 to +100, + = clockwise)
            applyPointTurn(param);
            break;

        case STEER_CRAB_WALK:
            // param = crab angle in degrees (-35 to +35)
            applyCrabWalk(param);
            break;

        case STEER_STRAIGHT:
            // param = speed (-100 to +100)
            applyStraight(param);
            break;
    }
}
```

---

## 9. Steering Response & Safety

### 9.1 Maximum Steering Rate

Don't slam servos from one extreme to another — it creates mechanical shock, can strip gears, and destabilises the rover.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Max steering rate | 60°/s | Full lock-to-lock in ~1.2 seconds |
| Steering acceleration | 120°/s² | Ramp up/down smoothly |
| Dead band | ±1° | Ignore steering commands within ±1° of centre |
| Update rate | 50 Hz | Match servo PWM frequency |

### 9.2 Speed-Dependent Steering Limit

At higher speeds, limit maximum steering angle to prevent rollover:

| Speed | Max Steering Angle | Min Turn Radius |
|-------|-------------------|-----------------|
| 0-1 km/h | ±35° | 993mm |
| 1-2 km/h | ±35° | 993mm |
| 2-3 km/h | ±25° | 1,314mm |
| 3-4 km/h | ±20° | 1,586mm |
| 4-5 km/h | ±15° | 2,028mm |

### 9.3 Steering Input Smoothing

Apply exponential moving average to joystick/command input:

```c
float smoothed_steering = 0;
const float ALPHA = 0.15;  // Lower = smoother, higher = more responsive

void updateSteering(float raw_input) {
    smoothed_steering = ALPHA * raw_input + (1.0 - ALPHA) * smoothed_steering;
}
```

---

## 10. Phase 1 vs Phase 2 Steering Comparison

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| Servo type | SG90 (1.8 kg·cm) | MG996R via PCA9685 (11 kg·cm) |
| Servo control | Direct LEDC PWM | PCA9685 I2C |
| Steering range | ±35° | ±35° |
| Min turn radius | 397mm | 993mm |
| Ackermann correction | Yes (firmware) | Yes (firmware) |
| Point turn | Best-effort (±35°) | Best-effort (±35°) |
| Crab walk | Yes (±35° max) | Yes (±35° max) |
| Speed-dependent limit | Not needed (<2 km/h) | Yes (see table) |
| Encoder feedback | 2 wheels (optional) | 6 wheels |
| Closed-loop speed | No (open-loop PWM) | Yes (PID per wheel) |

---

## 11. Key Dimensions for CAD

### 11.1 Steering Assembly Envelope (Phase 1, 0.4 Scale)

| Dimension | Value | Notes |
|-----------|-------|-------|
| Steering pivot to wheel centre (vertical) | 20mm | Wheel axle below pivot |
| Steering bracket width | 35mm | Clears wheel + motor |
| Steering bracket depth | 25mm | Along arm direction |
| Steering bracket height | 40mm | Pivot to motor mount |
| SG90 mounting: centre to arm end | 15mm | Standard SG90 horn |
| Minimum clearance: wheel to arm | 5mm | At full lock (35°) |
| Wheel sweep radius at full lock | 56mm | Wheel centre traces this circle |

### 11.2 Clearance Check at Full Lock

At ±35° steering, verify the wheel doesn't hit the rocker/bogie arm:

```
Phase 1:
  Wheel radius: 40mm
  Wheel width: 32mm
  At 35°, the rear edge of the wheel swings:
    Swing = 32 × sin(35°) = 32 × 0.574 = 18.4mm outward

  Minimum clearance between wheel edge and arm:
    Available space - swing = 25 - 18.4 = 6.6mm  ✓ (sufficient)
```

At full scale (Phase 2), the wheel is wider (80mm) and the swing is larger:
```
  Swing = 80 × sin(35°) = 80 × 0.574 = 45.9mm
```
The steering bracket must be designed with sufficient offset to accommodate this. Size the bracket so the wheel-to-arm gap is ≥10mm at full lock.

---

*Document EA-10 v1.0 — 2026-03-15*
