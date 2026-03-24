# Engineering Analysis 26: Suspension & Wheel System Design Package

**Document**: EA-26
**Date**: 2026-03-24
**Purpose**: Complete engineering-grade design package for the rocker-bogie suspension and wheel system. Defines every component, joint, interface, and parametric relationship required for CAD modelling and fabrication. Supersedes simplified treatments in EA-01 and EA-25 for suspension architecture.

**Scope**: Earth-use rover with Perseverance/Curiosity-inspired mobility. Passive suspension, no springs, no active damping. Designed for garden/park terrain (grass, gravel, mud, roots, kerbs up to 80mm).

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### 1.1 Mechanical Configuration

The rocker-bogie is a **12-DOF passive suspension** (before drive and steering) comprising:

- **6 wheel modules** (3 per side), each with independent drive
- **4 steering actuators** (front and rear wheels on each side; middle wheels fixed)
- **2 rocker arms** (one per side), each pivoting on the body about a lateral (Y) axis
- **2 bogie arms** (one per side), each pivoting on its rocker about a lateral (Y) axis
- **1 differential mechanism** coupling left and right rockers to equalise body pitch
- **1 chassis/body** acting as the structural reference frame

```
                    ┌──────── BODY ────────┐
                    │                      │
                    │   [Diff Pivot (Z)]   │
                    │    /            \     │
                    │  Link_L       Link_R  │
                    │  /                \   │
              ──────┼──────────────────────┼──────
             │ Rocker Pivot L    Rocker Pivot R │
             │  (Y-axis)           (Y-axis)     │
             └──────┬──────────────────┬────────┘
                    │                  │
           ┌───────┴───────┐  ┌───────┴───────┐
           │    Rocker_L   │  │    Rocker_R   │
           │  /         \  │  │  /         \  │
         Front_L    Bogie_L│  │Bogie_R    Front_R
         Wheel      Pivot  │  │ Pivot     Wheel
         (steer)   (Y-axis)│  │(Y-axis)  (steer)
                   /     \    │    /     \
               Mid_L   Rear_L  Rear_R  Mid_R
               Wheel   Wheel   Wheel   Wheel
              (fixed) (steer) (steer) (fixed)
```

### 1.2 Earth vs Mars Optimisation

| Aspect | Mars Rover | Our Earth Rover |
|--------|-----------|-----------------|
| Gravity | 3.72 m/s^2 | 9.81 m/s^2 (2.6x heavier effective load) |
| Terrain | Fine regolith, sharp rocks | Grass, gravel, mud, roots, kerbs |
| Speed | 0.04 m/s | 0.5-2.0 m/s |
| Wheel compliance | Thin titanium flexes | Rigid PLA + rubber O-rings (Phase 1); TPU tyre (Phase 2) |
| Max obstacle | 1.5x wheel diameter | 1.0x wheel diameter is sufficient |
| Mass priority | Extreme (launch cost) | Moderate (portability, motor sizing) |

**Earth-specific decisions**:
- Compliance via **tyre material** (TPU/rubber), not wheel structure. PLA wheels are rigid.
- Higher gravity means **bearing loads ~2.6x higher** than equivalent Mars rover — bearing selection matters.
- Higher speed means **steering backlash and wobble** are perceptible — bearing preload and shaft fit matter.
- Mud/grass means **wheel sinkage** is a real concern — wider tyres than Mars rovers.

### 1.3 Essential vs Optional Subsystems

| Subsystem | Status | Justification |
|-----------|--------|---------------|
| Rocker arms (2) | ESSENTIAL | Core suspension linkage |
| Bogie arms (2) | ESSENTIAL | Rear wheel pair articulation |
| Differential mechanism | ESSENTIAL | Without it, body freely rolls/pitches |
| Rocker pivot bearings (2) | ESSENTIAL | Load-bearing rotation |
| Bogie pivot bearings (2) | ESSENTIAL | Load-bearing rotation |
| Differential pivot bearing (1) | ESSENTIAL | Central equalisation point |
| Steering pivots (4) | ESSENTIAL | Turning capability |
| Drive motors (6) | ESSENTIAL | Propulsion |
| Hard stops on all pivots | ESSENTIAL | Prevent over-articulation and cable damage |
| Cable service loops | ESSENTIAL | Allow joint rotation without wire breakage |
| Wheel hub bearings | RECOMMENDED | Reduce friction, prevent wobble |
| Dust seals on bearings | OPTIONAL | Earth use, not critical for garden |
| Suspension locking | OPTIONAL | For transport/maintenance only |

---

## 2. DEGREES OF FREEDOM AND JOINT KINEMATICS

### 2.1 Complete DOF Map

> **Coordinate convention note**: This document uses descriptive axis names
> (lateral, longitudinal, vertical) rather than X/Y/Z letters. The project-wide
> convention is X = lateral, Y = forward, Z = up (matching EA-08 and all CAD scripts).
> Computed positions in Section 9.5 use this X-lateral/Y-forward/Z-up frame.

| Joint | Type | Axis | Travel | Continuous? | Limits Set By |
|-------|------|------|--------|-------------|---------------|
| Left rocker pivot | Revolute | Y (lateral) | +/- 25-35 deg | No | Hard stops on body |
| Right rocker pivot | Revolute | Y (lateral) | +/- 25-35 deg | No | Hard stops on body |
| Left bogie pivot | Revolute | Y (lateral) | +/- 25-35 deg | No | Hard stops on rocker |
| Right bogie pivot | Revolute | Y (lateral) | +/- 25-35 deg | No | Hard stops on rocker |
| Differential pivot | Revolute | X (longitudinal) | +/- 20-30 deg | No | Hard stops on body |
| Differential link L | Revolute (spherical) | Multi-axis | Per geometry | No | Link length |
| Differential link R | Revolute (spherical) | Multi-axis | Per geometry | No | Link length |
| FL steering pivot | Revolute | Z (vertical) | +/- 35 deg | No | Servo limit + hard stop |
| FR steering pivot | Revolute | Z (vertical) | +/- 35 deg | No | Servo limit + hard stop |
| RL steering pivot | Revolute | Z (vertical) | +/- 35 deg | No | Servo limit + hard stop |
| RR steering pivot | Revolute | Z (vertical) | +/- 35 deg | No | Servo limit + hard stop |
| FL drive | Revolute | Y (lateral) | Continuous | Yes | None (motor) |
| FM drive | Revolute | Y (lateral) | Continuous | Yes | None (motor) |
| FR rear drive | Revolute | Y (lateral) | Continuous | Yes | None (motor) |
| (... 3 more drive) | Revolute | Y (lateral) | Continuous | Yes | None (motor) |

**Coordinate system** (rover body frame):
- **X**: Forward (direction of travel)
- **Y**: Left (port side)
- **Z**: Up (vertical)
- Origin: Centre of differential pivot

### 2.2 Coupled Motion

The differential mechanism creates a **kinematic constraint**: when the left rocker rotates by angle theta_L about Y, the right rocker rotates by approximately -theta_L (opposite direction, same magnitude). The body pitch angle becomes the average: `theta_body = (theta_L + theta_R) / 2`.

This is NOT a rigid constraint — it is enforced by a **mechanical linkage** (differential bar + links, or bevel gears). The quality of the constraint depends on link geometry and pivot placement.

---

## 3. FULL COMPONENT BREAKDOWN FOR CAD

### 3.1 Wheel Module (x6)

| Part | Function | Essential? | Interfaces | Load Type |
|------|----------|-----------|------------|-----------|
| Wheel body/rim | Ground contact, tyre seat | Yes | Tyre, hub | Radial load, impact |
| Tyre/tread surface | Traction, compliance | Yes | Wheel rim | Ground contact |
| Wheel hub | Connects wheel to axle | Yes | Wheel body, axle, bearings | Radial + axial |
| Axle/spindle | Rotation axis | Yes | Hub bearings, motor output | Bending, torsion |
| Drive motor + gearbox | Propulsion torque | Yes | Axle, motor mount bracket | Reaction torque |
| Motor mount bracket | Holds motor to arm | Yes | Rocker/bogie arm, motor | Shear, vibration |
| Bearings (x2 per wheel) | Support rotation | Recommended | Axle, housing | Radial load |

### 3.2 Steering Module (x4, steered wheels only)

| Part | Function | Essential? | Interfaces | Load Type |
|------|----------|-----------|------------|-----------|
| Steering knuckle/upright | Connects wheel assembly to steering pivot | Yes | Wheel axle, steering shaft | Bending, torsion |
| Steering pivot shaft | Vertical rotation axis | Yes | Knuckle, arm bearing | Shear |
| Steering bearings (x2) | Support vertical pivot | Yes | Shaft, housing in arm | Radial + thrust |
| Steering actuator (servo) | Drives steering angle | Yes | Knuckle via horn/linkage | Torque |
| Servo mount bracket | Holds servo to arm | Yes | Arm structure | Vibration |
| Mechanical end stops | Limit steering angle | Yes | Knuckle, arm | Impact |

### 3.3 Rocker Arm (x2)

| Part | Function | Essential? | Interfaces | Load Type |
|------|----------|-----------|------------|-----------|
| Rocker arm structure | Main structural link | Yes | Front wheel, bogie pivot, body pivot | Bending, torsion |
| Body pivot bearing housing | Supports rocker-to-body rotation | Yes | Body hardpoints, shaft | Radial + axial |
| Body pivot shaft | Y-axis rotation | Yes | Body bearings, rocker | Bending, shear |
| Bogie pivot bearing housing | Supports bogie rotation on rocker | Yes | Rocker end, bogie shaft | Radial |
| Differential arm attachment | Connects to differential link | Yes | Rocker pivot area | Tension/compression |
| Hard stop features | Limit rocker articulation | Yes | Body structure | Impact |
| Cable routing channels | Route wires along arm | Yes | Internal or clipped | Service only |

### 3.4 Bogie Arm (x2)

| Part | Function | Essential? | Interfaces | Load Type |
|------|----------|-----------|------------|-----------|
| Bogie arm structure | Links middle and rear wheels | Yes | Middle wheel, rear wheel, rocker pivot | Bending |
| Pivot shaft | Y-axis rotation on rocker | Yes | Rocker bearing housing | Shear, bending |
| Middle wheel mount | Attaches middle wheel module | Yes | Bogie arm, motor mount | Load transfer |
| Rear wheel mount | Attaches rear wheel module | Yes | Bogie arm, steering knuckle | Load transfer |
| Cable routing | Wires to middle + rear wheels | Yes | Along arm | Service only |

### 3.5 Differential Mechanism

| Part | Function | Essential? | Interfaces | Load Type |
|------|----------|-----------|------------|-----------|
| Differential pivot bearing + housing | Central pivot on body | Yes | Body top/cross-member | Radial + axial |
| Differential bar/beam | Connects left and right links | Yes | Central pivot, link ends | Bending, torsion |
| Left differential link | Connects bar end to left rocker | Yes | Bar end, rocker arm | Tension/compression |
| Right differential link | Connects bar end to right rocker | Yes | Bar end, rocker arm | Tension/compression |
| Link pivot joints (x4) | Allow angular misalignment | Yes | Bar ends, rocker attachment | Rotation |

**Critical note**: The differential links require **ball joints or universal joints** (not simple pins) because the bar rotates about X while the rockers rotate about Y. A rigid bar with pin joints will bind. The JPL Open Source Rover uses **turnbuckle rod ends with ball joints** for exactly this reason.

### 3.6 Chassis Interface Parts

| Part | Function | Essential? | Interfaces |
|------|----------|-----------|------------|
| Rocker pivot mounts (x2) | Support rocker shaft bearings | Yes | Body side walls, bearings |
| Differential pivot mount | Support central diff pivot | Yes | Body top cross-member |
| Differential link anchors | Where links attach to rockers | Yes | Near rocker pivot |
| Hard stop blocks | Physical rotation limits | Yes | Body near pivot mounts |
| Cable entry grommets | Protect wires entering body | Yes | Body walls |
| Body cross-members | Structural rigidity | Yes | Body frame |

---

## 4. PARAMETRIC GEOMETRY AND CRITICAL RATIOS

All dimensions expressed as ratios to wheel diameter D_w unless stated otherwise.

### 4.1 Wheel Diameter

**Rule**: D_w >= 2 * h_obstacle for flat-terrain obstacle climbing.

For Earth garden use with h_obstacle = 80mm (kerb), D_w >= 160mm. We use **200mm (full scale)** / **80mm (0.4x Phase 1)**.

**Why it matters**: Undersized wheels cannot roll over obstacles; the front wheel stalls against the face.

### 4.2 Wheelbase and Wheel Spacing

| Parameter | Ratio to D_w | Justification |
|-----------|-------------|---------------|
| Total wheelbase (front to rear) | 4.0 - 5.0 * D_w | Stability, obstacle straddling |
| Front-to-middle spacing | 2.0 - 2.5 * D_w | Rocker arm length, prevents front lifting |
| Middle-to-rear spacing | 1.5 - 2.0 * D_w | Bogie arm length, weight distribution |
| Track width | 3.0 - 4.0 * D_w | Lateral stability (wider = more stable but larger footprint) |

At 0.4x scale (D_w = 80mm): wheelbase = 360mm, track = 280mm — **Verified**: matches EA-08 Section 1 table exactly.

### 4.3 Rocker Arm Length

The rocker arm has two segments from its body pivot:
- **Forward segment** (pivot to front wheel): Determined by front wheel Y-position minus body pivot Y-position
- **Rearward segment** (pivot to bogie pivot): Determined by bogie pivot Y-position minus body pivot Y-position

**NASA ratio**: Forward : Rearward approximately **1.5:1 to 2.0:1**. The forward arm is longer because the front wheel is the primary obstacle climber and needs leverage.

**Rocker pivot height**: Should be at or slightly above the wheel centre height. Too high = excessive body roll. Too low = inadequate ground clearance.

`Z_rocker_pivot = Z_wheel_centre + (0 to 0.5 * D_w)`

### 4.4 Bogie Arm Length and Pivot Position

The bogie pivot divides the bogie arm into front (to middle wheel) and rear (to rear wheel) segments.

**Pivot position along bogie**: The pivot should be located such that the **static load is distributed equally** between middle and rear wheels when on flat ground. This means the pivot is at the centre of gravity of the two wheel loads, which on flat ground is approximately:

`L_bogie_front / L_bogie_rear = 1.0` (equal subdivision for equal static loading)

However, NASA designs use approximately **0.8:1 to 1.2:1** ratio, biased slightly toward the rear to improve rear-wheel obstacle climbing.

### 4.5 Differential Bar Geometry

The differential bar spans between the two rocker pivot points. Its effective lever arm determines how well it equalises pitch.

**Bar length**: Must span at least the distance between the two rocker pivot projections onto the bar axis. For a bar along the X (forward) axis pivoting about Z (vertical):

`L_bar >= 2 * Y_rocker_pivot_offset`

Where Y_rocker_pivot_offset is the lateral distance from centreline to rocker pivot.

**Link geometry**: Each differential link connects a bar end to a rocker arm. The link length and attachment points determine the **motion ratio** (how much rocker rotation produces bar rotation). For 1:1 equalisation, the links should be:
- Equal length left and right
- Attached at equal distances from the rocker pivot axis
- Attached at equal distances from the bar pivot axis

**Computed** (see Section 9.5): Link length = 85.0mm (Phase 1) / 212.1mm (full scale). Bar half-span = 200mm (Phase 1) / 500mm (full). Attachment offsets: r_bar = r_rocker = 30mm (Phase 1) / 75mm (full), giving 1:1 motion ratio. Link angle = 28.1 deg from horizontal.

### 4.6 Belly Clearance

`Z_belly >= D_w / 2` (minimum — wheel radius above ground)

Better: `Z_belly >= 0.6 * D_w` to provide margin for terrain undulation.

At 0.4x scale: Z_belly >= 48mm. Our current value is 60mm — adequate.

---

## 5. ANGLES, ARTICULATION LIMITS, AND WHEEL MOTION ENVELOPES

### 5.1 Rocker Articulation

| Parameter | Value | Basis |
|-----------|-------|-------|
| Nominal angle | 0 deg (level ground) | Flat terrain |
| Max upward (front wheel high) | +25 deg | Limited by belly clearance and rear wheel ground contact |
| Max downward (front wheel low) | -25 deg | Limited by front wheel-to-body clearance |
| Hard stop margin | 5 deg inside max | Prevent metal-on-metal at extremes |

**Why +/- 25 deg**: At 25 deg rocker tilt with the 1:1 differential, the body tilts only 12.5 deg. This is conservative for PLA hard stops and electronics stability. Matches `generate_rover_params.py` value.

### 5.2 Bogie Articulation

| Parameter | Value | Basis |
|-----------|-------|-------|
| Nominal angle | 0 deg | Flat terrain |
| Max upward (middle wheel high) | +25 deg | Clearance to rocker arm structure |
| Max downward (middle wheel low) | -25 deg | Clearance to rocker arm structure |

### 5.3 Steering Sweep

| Parameter | Value | Basis |
|-----------|-------|-------|
| Max steering angle (front) | +/- 35 deg | Ackermann geometry, turning radius |
| Max steering angle (rear) | +/- 35 deg | Counter-steering for tight turns |
| Middle wheels | 0 deg (fixed) | No steering, simplifies design |

### 5.4 Interference Checks Required

Before finalising CAD, verify at ALL extreme positions:

1. **Wheel-to-body clearance**: At max rocker articulation, does any wheel contact the body? Check with steering at full lock simultaneously.
2. **Wheel-to-arm clearance**: At max bogie articulation + full steering lock, does the wheel contact the rocker or bogie arm?
3. **Cable routing**: At max articulation + full steering, do cables exceed their minimum bend radius?
4. **Differential link travel**: At max asymmetric articulation (one side +25, other -25), do the links reach their geometric limit or bind?
5. **Ground clearance**: At max articulation, does the belly or any structural member contact the ground?

**Recommendation**: Run a CAD motion study sweeping all joints through their full range. Flag any interference distance < 5mm.

---

## 6. WHEEL MODULE DESIGN

### 6.1 Wheel Architecture

```
            ┌───────────────────────────────────┐
            │         Tyre (TPU/rubber)          │
            │  ┌───────────────────────────┐    │
            │  │     Rim/Wheel Body (PLA)  │    │
            │  │  ┌─────────────────────┐  │    │
            │  │  │   Hub (PLA/metal)   │  │    │
            │  │  │  [Bearing] [Bearing]│  │    │
            │  │  │     === Axle ===    │  │    │
            │  │  └─────────────────────┘  │    │
            │  └───────────────────────────┘    │
            └───────────────────────────────────┘
                        │
                    Motor + Gearbox
```

### 6.2 Component Specifications

**Wheel body**: Disc or spoked design. For PLA Phase 1, **5-spoke design** (jakkra-style) provides strength with printability. Grousers/tread on outer surface.

**Hub**: Press-fit or bolted to wheel body. Contains **2x bearings** (radial ball, e.g., 608ZZ for full scale, 684ZZ or 694ZZ for 0.4 scale) spaced along the axle for moment resistance.

**Axle**: Steel shaft, press-fit to motor output or coupled via set screw/D-flat. Diameter matched to bearing bore.

**Key datums**:
- Wheel rotation axis (Y) is the **primary datum**
- Hub bearing seats must be **concentric** to wheel axis within 0.05mm (bearing press-fit tolerance)
- Tyre seat diameter must be **concentric** to hub within 0.2mm

### 6.3 Drive Motor Packaging

Motor + gearbox sits **inboard** of the wheel (between wheel and arm). Envelope must be defined before arm geometry is finalised.

For Phase 1 (N20 motors): ~12mm x 10mm x 25mm gearbox + 12mm diameter x 15mm motor body.

Motor axis must be **coaxial** with wheel axis. Motor mount must resist **reaction torque** (equal to motor stall torque) — this is a common failure point in 3D-printed designs.

---

## 7. ROCKER DESIGN

### 7.1 Structural Concept

The rocker is a **planar structural member** loaded primarily in bending (vertical loads from wheels create bending moment about the body pivot). Secondary loads: torsion from off-axis wheel forces.

```
    Front Wheel ─── [Forward Arm] ─── BODY PIVOT ─── [Rear Arm] ─── Bogie Pivot
    Attachment                         (Y-axis)                       (Y-axis)
```

### 7.2 Cross-Section Design

| Region | Dominant Load | Design Logic |
|--------|--------------|-------------|
| Forward arm (mid-span) | Bending | Maximise section height, I-beam or box section |
| Body pivot zone | Bearing support + bending | Thick-walled circular boss for shaft/bearings |
| Rear arm (mid-span) | Bending (lower than forward arm because shorter) | Can be lighter than forward arm |
| Bogie pivot zone | Bearing support | Circular boss, similar to body pivot but smaller loads |
| Differential link attachment | Tension/compression from link | Local reinforcement, heat-set insert or through-bolt |

### 7.3 Pivot Placement

The body pivot location along the rocker determines the **force distribution** between front wheel and bogie:

**For equal wheel loading on flat ground**:
```
F_front * L_forward = (F_middle + F_rear) * L_rear
```

Where F_front = 1 wheel load, F_middle + F_rear = 2 wheel loads. Therefore:
```
L_forward / L_rear = 2.0
```

The forward arm should be **twice** the length of the rear arm for equal static loading.

**Practical adjustment**: NASA designs use ~1.5:1 to 2.0:1 because the bogie's own pivot placement further redistributes rear loads.

### 7.4 Fabrication (Phase 1: 3D Print)

For our tube + connector approach (EA-25):
- **8mm steel rod** forms the structural member
- **PLA printed connectors** at each node (body pivot, front wheel, bogie pivot)
- Connectors have **tube sockets** (8.2mm bore, 15mm deep) with M3 grub screws
- This approach is **structurally sound** for Phase 1 loads (~200g per arm in bending)

For Phase 2 (full scale):
- Aluminium extrusion (15mm or 20mm series) or steel tube
- Printed or machined joint blocks

---

## 8. BOGIE DESIGN

### 8.1 Structural Concept

The bogie is a **simpler version** of the rocker — a beam with a pivot in the middle and wheel mounts at each end.

```
    Middle Wheel ─── [Front Segment] ─── BOGIE PIVOT ─── [Rear Segment] ─── Rear Wheel
    Mount (fixed)                        (Y-axis on rocker)                  Mount (steered)
```

### 8.2 Pivot Position

For equal loading between middle and rear wheels:
```
L_bogie_front = L_bogie_rear (equal division)
```

Biasing the pivot rearward slightly improves rear-wheel obstacle climbing. Recommend:
```
L_bogie_front / L_bogie_rear = 0.9 to 1.1
```

### 8.3 Bearing at Bogie Pivot

The bogie must rotate freely on the rocker. This requires a bearing (not a friction bushing) because:
- The joint sees **continuous oscillation** during driving
- Binding at this joint causes the rover to **drag wheels** instead of articulating
- For 0.4 scale: 608ZZ bearing (8mm bore) is appropriate
- For full scale: 6001ZZ or 6002ZZ (12mm bore)

### 8.4 Clearance During Articulation

At maximum bogie pitch (+/- 25 deg), the arm ends sweep through an arc. Verify:
- Wheel at end of arm doesn't contact rocker arm structure
- Motor/gearbox housing doesn't contact rocker arm
- Cables have slack to accommodate the sweep

---

## 9. DIFFERENTIAL / ROCKER COUPLING DESIGN

**This is the most commonly omitted or incorrectly implemented part of hobby rover builds.**

### 9.1 Functional Requirement

The differential must:
1. **Couple** left and right rocker rotations so they are approximately equal and opposite
2. **Equalise** the body pitch angle to the average of the two rocker angles
3. **NOT resist** rocker motion (it must be free to move, not act as a spring)
4. **Support** the body weight transferred through the rocker pivots

Without a differential, the body is supported by two independent pivots and will **freely roll and pitch** to whatever angle gravity dictates. The rover becomes uncontrollable.

### 9.2 Mechanism Options

#### Option A: Differential Bar + Link (Curiosity-style)

```
    BODY (top view)
    ┌──────────────────────────────────┐
    │            Diff Bar              │
    │     ┌──────[Pivot]──────┐       │
    │     │    (rotates in X) │       │
    │   Link_L              Link_R    │
    │     │                    │      │
    │  Attach_L            Attach_R   │
    │  (on left             (on right │
    │   rocker)              rocker)  │
    └──────────────────────────────────┘
```

**Bar**: A beam mounted on the body top, pivoting about the **X-axis** (longitudinal). When one end rises, the other falls.

**Links**: Connect each bar end to the corresponding rocker arm. These links must accommodate the fact that the bar rotates about X while the rockers rotate about Y. Therefore, the links need **ball joints** (rod-end bearings / Heim joints) at each end, or **universal joints**.

**Advantages**: Simple, visible, easy to inspect. Used by Curiosity.
**Disadvantages**: Requires ball joints. Bar must be rigid enough not to flex.

#### Option B: Bevel Gear Differential (Spirit/Opportunity-style)

Three bevel gears inside a housing: left rocker gear, right rocker gear, and body gear. When one rocker turns, the body gear forces the other rocker to turn opposite.

**Advantages**: Compact, hidden, precise 1:1 coupling.
**Disadvantages**: Requires machined gears or commercial bevel gear set. More complex to fabricate.

#### Option C: Spur Gear Differential

A simpler gear arrangement using spur gears with an idler. Left and right rocker shafts extend inward; each carries a spur gear. An idler gear between them reverses rotation.

**Advantages**: Can use off-the-shelf spur gears. Easily 3D printed at low precision.
**Disadvantages**: Backlash in printed gears. Requires precise shaft alignment.

### 9.3 Recommended Implementation

**For Phase 1 (0.4 scale, 3D printed)**: **Option A — Differential Bar + Link** with M3 rod-end bearings (Heim joints) at each link end.

Rationale:
- Ball-joint rod ends are cheap (~$5 for 10pcs M3)
- Bar can be an 8mm steel rod (same stock as suspension tubes)
- All joints are visible and adjustable
- No gear backlash to manage
- The JPL Open Source Rover uses this approach (with turnbuckle ball joints)

**For Phase 2 (full scale)**: Either Option A with larger rod ends (M5) or Option B with a small bevel gear set if compactness is needed.

### 9.4 Differential Bar Geometry Detail

```
    Side View:
                      Diff Pivot (X-axis rotation)
                          │
                     ─────┼─────  ← Diff Bar
                    /     │     \
               Link_L     │    Link_R
                  /       │       \
           ──────┼────────┼────────┼──────
          Rocker_L   Body Centre   Rocker_R
          Pivot                    Pivot
```

**Pivot axis**: The differential bar pivots about the **X-axis** (longitudinal/forward axis). This is perpendicular to the rocker axes (Y, lateral).

**Link attachment points**:
- On bar: At each end of the bar, offset from the pivot by distance `r_bar`
- On rocker: Near the rocker body-pivot, offset by distance `r_rocker`
- Motion ratio: `r_bar / r_rocker` should be 1.0 for equal coupling

**Link type**: Rigid rods with **ball joints at both ends** (M3 rod-end bearings / Heim joints). Length adjustable via turnbuckle (threaded rod with LH + RH ends) for alignment tuning.

### 9.5 Computed Differential Dimensions

Calculated from rover geometry (see `generate_rover_params.py` differential_computed):

| Parameter | Phase 1 (0.4x) | Full Scale | Notes |
|-----------|:--------------:|:----------:|-------|
| Diff bar half-span | 200mm | 500mm | Bar extends ±this from pivot |
| Diff pivot Z | 80mm | 200mm | 20mm / 50mm above rocker pivot |
| Link bar attach offset (below bar end) | 30mm | 75mm | `r_bar` for motion ratio |
| Link rocker attach offset (above rocker pivot) | 30mm | 75mm | `r_rocker` for motion ratio |
| **Link length** | **85.0mm** | **212.1mm** | sqrt(dx² + dz²) |
| Link angle from horizontal | 28.1° | 28.1° | Constant across scales |
| Link top position | (±200, 0, 50) | (±500, 0, 125) | Ball joint on bar end |
| Link bottom position | (±125, 0, 90) | (±313, 0, 225) | Ball joint on rocker |
| Motion ratio (r_bar / r_rocker) | 1.0 | 1.0 | Equal = 1:1 coupling |

**Ball joint specification**: M3 rod-end bearing (Heim joint), ~±15° angular range, housing OD 10mm. 4 required (2 per link × 2 links).

**Link construction (Phase 1)**: Printed PLA flat bar (dog-bone shape), 85mm long × 15mm wide × 6mm thick, 80% infill, 5 perimeters. M3 bolt through-holes at each end for rod-end bearings.

---

## 10. CHASSIS INTERFACES AND HARDPOINTS

### 10.1 Required Mounting Points

| Hardpoint | Location | Loads | Requirements |
|-----------|----------|-------|-------------|
| Left rocker pivot mount | Body side wall, mid-length | Vertical (1/3 rover weight each side) + bending | Double-shear bearing mount preferred |
| Right rocker pivot mount | Body side wall, mid-length | Same as left | Symmetric placement |
| Differential pivot mount | Body top, centreline | Torsion from bar | Rigid cross-member |
| Diff link pass-through | Body side walls near rocker pivots | Link tension/compression | Clearance holes with grommets |

### 10.2 Double-Shear vs Single-Shear Pivot Mounts

**Double-shear** (shaft supported on both sides of the arm): Distributes bending load, prevents shaft deflection. **Strongly recommended** for rocker pivots.

**Single-shear** (shaft cantilevered from one side): Simpler but creates bending moment on shaft. Acceptable for bogie pivots (lower loads).

For Phase 1 (0.4 scale, ~1.25 kg total):
- Rocker pivots: Single-shear is acceptable due to low loads
- Full scale: Must use double-shear

### 10.3 Hardpoint Spacing Effects

| If pivot is too far forward... | Body pitches nose-down on obstacles |
| If pivot is too far back... | Front wheel loses ground contact on descents |
| If pivots are too high... | CG rises, tip-over risk increases |
| If pivots are too low... | Belly clearance reduces |

**Recommendation**: Place rocker pivots at body mid-length (Y), at wheel-centre height (Z), and as close to the body side walls as possible (X) to maximise interior space.

---

## 11. BEARINGS, SHAFTS, AXES, AND MOUNTING LOGIC

### 11.1 Bearing Selection Guide

| Joint | Load Type | Phase 1 (0.4x) | Phase 2 (1.0x) |
|-------|-----------|----------------|----------------|
| Rocker body pivot | Radial + light axial | 608ZZ (8x22x7) | 6002ZZ (15x32x9) |
| Bogie pivot | Radial only | 608ZZ | 6001ZZ (12x28x8) |
| Differential pivot | Radial + axial | 608ZZ | 6001ZZ + thrust washer |
| Wheel hub | Radial | 684ZZ (4x9x4) or 694ZZ | 608ZZ |
| Steering pivot | Radial + thrust | 2x F688ZZ flanged (8x16x5) | 2x F6001ZZ flanged |

### 11.2 Shaft Sizing

| Shaft | Phase 1 | Phase 2 | Material |
|-------|---------|---------|----------|
| Rocker pivot | 8mm | 15mm | Stainless steel |
| Bogie pivot | 8mm | 12mm | Stainless steel |
| Differential pivot | 8mm | 12mm | Stainless steel |
| Wheel axle | 4mm (N20 output) | 8mm | Steel |
| Steering shaft | 5mm (servo horn) | 8mm | Steel |

### 11.3 Retention

Every shaft needs **axial retention** to prevent walking out:
- **E-clips**: Cheap, effective, requires groove in shaft
- **Shoulder + nut**: More secure, needs threaded shaft end
- **Grub screw in collar**: Works for low-load cases (Phase 1)
- **Press-fit with adhesive**: Permanent, difficult to service

**Recommendation**: E-clips for Phase 1 (available in 8mm size), shoulder + nut for Phase 2.

### 11.4 Spacer Strategy

Between bearing faces and structural members, use **spacers** to:
1. Set correct bearing preload (light preload for smooth rotation)
2. Prevent axial play
3. Allow disassembly without bearing damage

Material: Nylon or brass washers (printed PLA spacers acceptable for Phase 1).

---

## 12. STEERING GEOMETRY AND PIVOT REQUIREMENTS

### 12.1 Steering Axis Location

The steering pivot (king-pin) axis should intersect the ground at or near the **wheel contact patch centre**. This minimises:
- **Scrub radius**: Lateral distance between steering axis ground intersection and contact patch centre. Zero scrub = minimal steering torque.
- **Trail**: Longitudinal distance between steering axis ground intersection and contact patch centre. Positive trail provides self-centering.

For our rover (low speed), scrub radius is less critical than for cars, but **zero or small positive scrub** is recommended to reduce servo torque requirement.

### 12.2 Pivot Implementation

The steering pivot is a **vertical shaft** through the rocker/bogie arm end, with the wheel assembly below:

```
    Arm Structure
        │
    [Bearing]──── Steering Shaft (Z-axis)
        │
    [Bearing]
        │
    Steering Knuckle
        │
    Wheel Assembly
```

**Actuator**: Servo horn connected to the knuckle via direct drive or linkage. For Phase 1 (SG90 servo), direct drive to a horn arm is simplest.

### 12.3 Ackermann Geometry

For proper Ackermann steering (inner wheel turns more than outer), the steering linkage geometry must be designed so that the turning circle centres of all steered wheels converge to a single point.

For our **4-wheel steering** (front and rear steer, middle fixed):
- Front and rear wheels steer in **opposite directions** for minimum turning radius
- Steering angles calculated per EA-10

### 12.4 Cable Routing Through Steering Pivot

**This is a major design trap**. The steering pivot rotates +/- 35 deg. Motor power and encoder wires must pass through this joint.

Options:
1. **Service loop**: Extra wire length coiled around the pivot axis. Wire must be flexible and have bend radius > 5x wire diameter.
2. **Spiral wrap**: Wire wound helically around the pivot shaft. Accommodates rotation but adds friction.
3. **Slip ring**: Electrical rotary joint. Overkill for +/- 35 deg.

**Recommendation**: Service loop with **strain relief clips** above and below the pivot. Allow at least `2 * pi * r_loop * (35/360)` of free wire length where r_loop is the loop radius.

---

## 13. CABLE ROUTING / STRAIN RELIEF / SERVICE LOOP REQUIREMENTS

### 13.1 Joints Requiring Cable Service

| Joint | Rotation Range | Wires Through | Service Method |
|-------|---------------|---------------|----------------|
| Rocker body pivot | +/- 30 deg | 6-8 (3 motors + 2 servos + encoder) | Service loop inside body at pivot |
| Bogie pivot | +/- 25 deg | 4-6 (2 motors + 1 servo + encoder) | Service loop at pivot |
| Steering pivot (x4) | +/- 35 deg | 2 (motor power) | Service loop around pivot shaft |
| Differential pivot | +/- 25 deg | None | No wires cross this joint |

### 13.2 Minimum Free Length Calculation

```
Free_length = arc_length = R_loop * theta_max (radians) * 2 (both directions)
```

For rocker pivot with R_loop = 15mm, theta_max = 30 deg = 0.524 rad:
```
Free_length = 15 * 0.524 * 2 = 15.7mm minimum
```

Add 50% safety factor: **~24mm** of service loop per rocker pivot.

### 13.3 Cable Routing Path

```
Body Interior
    │
    ├── Through grommet in body wall
    │
    ├── Service loop at rocker pivot (inside rocker connector)
    │
    ├── Along rocker arm tube (cable clips every 50-80mm)
    │
    ├── Service loop at bogie pivot (inside bogie connector)
    │
    ├── Along bogie arm tube (cable clips)
    │
    ├── Service loop at steering pivot
    │
    └── Into motor/servo at wheel
```

### 13.4 Wire Channel Dimensions

Following EA-25 specification:
- **Main channels** (rocker arm): 8 x 6mm (8 wires max)
- **Branch channels** (bogie arm): 6 x 4mm (4 wires max)
- **Minimum bend radius**: 5x wire diameter (for 22AWG: bend radius >= 4mm)

---

## 14. STRUCTURAL LOAD PATHS

### 14.1 Load Flow Diagram

```
Ground Contact
    ↓
Wheel Tyre (compression)
    ↓
Wheel Rim → Hub (compression, radial)
    ↓
Hub Bearings (radial load)
    ↓
Axle/Spindle (bending between bearings)
    ↓
Motor Mount Bracket (shear)
    ↓
Rocker or Bogie Arm (bending about pivot)
    ↓
Pivot Shaft (shear at bearing faces)
    ↓
Pivot Bearings (radial load)
    ↓
Body Pivot Mount (bolted/bonded to body structure)
    ↓
Body Frame (global bending/torsion)
    ↓
Differential Link (tension/compression, alternating)
    ↓
Differential Bar (bending about pivot)
    ↓
Differential Pivot Mount on Body
```

### 14.2 Critical Stress Points

| Location | Load Type | Failure Mode | Design Response |
|----------|-----------|-------------|----------------|
| Rocker arm mid-span | Bending | Fracture/buckling | Maximise section depth, add ribs |
| Rocker pivot boss | Hoop stress from bearing | Cracking | Thick wall (>= 4mm), high infill |
| Connector tube sockets | Shear from grub screw | Splitting | >= 4mm wall, 5 perimeters |
| Differential link joints | Tension/compression | Pull-out | Ball joint properly threaded |
| Motor mount | Reaction torque | Deformation | Gussets, multiple fasteners |
| Steering knuckle | Bending from wheel load | Fracture | Thick section, short unsupported span |

---

## 15. WHAT MUST BE SOLVED BY CALCULATION BEFORE CAD IS FINALISED

### 15.1 Priority 1 — Must Know Before Starting CAD

| Parameter | Depends On | Analysis Needed |
|-----------|-----------|----------------|
| Wheel diameter | Target obstacle height | D_w >= 2 * h_obstacle |
| Track width | Stability requirement, body width | Tip-over analysis at max articulation |
| Wheelbase | Wheel diameter, terrain | Obstacle straddling, weight distribution |
| Rocker arm lengths (fwd/rear) | Wheelbase, pivot position | Static equilibrium, equal wheel loading |
| Bogie arm lengths | Rear wheel spacing, pivot position | Static equilibrium |
| Rocker pivot height | Belly clearance, wheel centre | Z_pivot = Z_wheel + offset |
| Differential bar length | Rocker pivot spacing (Y) | Must span both pivots with link clearance |

### 15.2 Priority 2 — Must Know Before Detail Design

| Parameter | Depends On | Analysis Needed |
|-----------|-----------|----------------|
| Steering angle limits | Turning radius target | Ackermann calculation (EA-10) |
| Hard stop angles (all pivots) | Interference study | CAD motion study at extremes |
| Bearing selection | Load calculation per joint | Force balance at max articulation |
| Shaft diameters | Bearing bore, bending load | Shaft bending stress check |
| Cable free lengths | Joint travel ranges | Arc length calculation per joint |
| Diff link lengths | Bar geometry, rocker offset | Geometric construction |
| Diff link ball-joint range | Max articulation | Check rod-end angular capacity |

### 15.3 Priority 3 — Can Refine Iteratively

| Parameter | Depends On |
|-----------|-----------|
| Wall thickness at stress points | FEA or hand calc from loads |
| Infill percentage | Material testing (calibration prints) |
| Gusset/rib placement | Visual inspection of CAD for thin sections |
| Cable clip spacing | Wire count and stiffness |
| Fastener torque | Joint clamping requirements |

---

## 16. CAD ASSEMBLY ORDER

The recommended workflow prevents rework by establishing datums before detail:

1. **Skeleton sketch**: Create a 2D side-view sketch with all pivot points, wheel centres, and key dimensions. This is the master geometry — everything references it.

2. **Wheel module**: Design wheel, hub, bearings, axle as a self-contained subassembly. This establishes the wheel diameter and motor packaging envelope.

3. **Bogie arm**: Design from bogie pivot to middle and rear wheel mounts. Verify clearance at max articulation.

4. **Rocker arm**: Design from body pivot through forward arm (to front wheel) and rear arm (to bogie pivot). Longer and more complex than bogie.

5. **Body pivot mounts**: Design the bearing housings that mount to the body. Must match rocker pivot geometry.

6. **Differential bar + links**: Design from the two rocker attachment points. Verify link travel at max articulation.

7. **Differential pivot mount**: Mount on body top cross-member. Establish bar rotation clearance.

8. **Steering modules**: Design knuckle, pivot shaft, servo mount at each steered wheel position. Verify clearance at full lock.

9. **Cable routing**: Add wire channels, clips, and service loops. Verify at all extreme positions.

10. **Motion envelope check**: Run motion study sweeping all joints. Flag any interference.

**Why this order**: Each step depends on the geometry established by the previous step. Starting with the skeleton sketch means you can change global dimensions without reworking detail parts.

---

## 17. CAD CHECKLIST OF ALL PARTS TO MODEL

### Wheel Parts (per wheel, x6 total)
- [ ] Wheel rim/body
- [ ] Tyre (separate body or integrated tread)
- [ ] Hub
- [ ] Axle/spindle
- [ ] Hub bearings (x2)
- [ ] Motor + gearbox (simplified envelope)
- [ ] Motor mount bracket

### Steering Parts (per steered wheel, x4 total)
- [ ] Steering knuckle/upright
- [ ] Steering pivot shaft
- [ ] Steering bearings (x2)
- [ ] Servo + mount bracket
- [ ] Mechanical end stops
- [ ] Service loop retention (strain relief clip)

### Rocker Parts (x2, left + right)
- [ ] Rocker arm structure (tube + connectors for Phase 1)
- [ ] Body pivot bearing housing
- [ ] Body pivot shaft
- [ ] Bogie pivot bearing housing
- [ ] Differential link attachment point
- [ ] Cable routing channels/clips
- [ ] Hard stop features

### Bogie Parts (x2, left + right)
- [ ] Bogie arm structure (tube + connectors for Phase 1)
- [ ] Pivot shaft
- [ ] Pivot bearing (608ZZ)
- [ ] Middle wheel mount
- [ ] Rear wheel mount
- [ ] Cable routing channels/clips
- [ ] Hard stop features

### Differential Parts (x1 set)
- [ ] Differential bar (8mm steel rod or extrusion)
- [ ] Differential pivot bearing + housing
- [ ] Differential pivot mount (on body)
- [ ] Left link (rod + 2x ball joints)
- [ ] Right link (rod + 2x ball joints)
- [ ] Link attachment brackets on rocker arms (x2)
- [ ] Link attachment brackets on bar ends (x2)

### Chassis Interface Parts
- [ ] Left rocker pivot mount (on body)
- [ ] Right rocker pivot mount (on body)
- [ ] Differential pivot cross-member
- [ ] Hard stop blocks (x4, one per rocker direction)
- [ ] Cable grommets (x2, where wires exit body)

### Service/Cable Parts
- [ ] Cable clips (x12-16, along arms)
- [ ] Service loop retainers at pivots
- [ ] Wire protection sleeves at pivot entries

### Optional Realism Parts
- [ ] Decorative rocker covers
- [ ] Wheel hubcaps
- [ ] Cable conduit (corrugated tube)

---

## 18. FAILURE MODES / DESIGN TRAPS TO AVOID

### 18.1 Omitting the Differential

**Why it happens**: Builders assume the two rocker pivots alone will keep the body stable. They won't — without a differential, the body freely pitches and rolls.

**Detection**: Remove the differential from CAD. If the body has no constraint against pitch, it's wrong.

**Prevention**: Always include a differential mechanism. Even a simple bar + links works.

### 18.2 Using Pin Joints Instead of Ball Joints on Diff Links

**Why it happens**: Builders use simple pivot pins at diff link ends. The diff bar rotates about X; rockers rotate about Y. A pin joint that only allows rotation about one axis will **bind** at the other.

**Detection**: In CAD motion study, apply asymmetric rocker articulation. If the link shows over-constraint or binding, the joint type is wrong.

**Prevention**: Use **ball joints** (M3 rod-end bearings / Heim joints) at each end of each diff link. Or use universal joints.

### 18.3 Insufficient Wheel-to-Arm Clearance

**Why it happens**: Designers check clearance at neutral position only.

**Detection**: Run motion study at max articulation + full steering lock.

**Prevention**: Allow minimum 5mm clearance at all extreme positions.

### 18.4 Cable Routing Ignoring Joint Motion

**Why it happens**: Cables routed neatly at neutral position get pinched or pulled at articulation extremes.

**Detection**: Manually check cable paths at all extreme positions.

**Prevention**: Design service loops with calculated free length. Add strain relief clips at fixed points on either side of each joint.

### 18.5 Wrong Pivot Axis Orientation

**Why it happens**: Confusing rover coordinate axes. Rocker pivots must rotate about **Y** (lateral). Differential pivots about **X** (longitudinal). Steering about **Z** (vertical).

**Detection**: Check that each pivot axis is perpendicular to the intended motion plane.

**Prevention**: Label every pivot with its axis in the CAD model.

### 18.6 Rocker/Bogie Arm Too Flexible

**Why it happens**: Using thin-walled 3D prints or undersized tubes without checking deflection.

**Detection**: Apply expected loads in FEA or hand-calculate beam deflection.

**Prevention**: For 3D prints: >= 4mm walls, >= 40% infill. For metal tubes: check section modulus against bending moment.

### 18.7 Overconstrained Assembly

**Why it happens**: Too many fixed joints. The system must be free to articulate.

**Detection**: Count DOF. If motion study shows locked joints, the assembly is over-constrained.

**Prevention**: Ensure every intended rotation has a bearing or joint that permits it. Don't glue or fix joints that must rotate.

### 18.8 Hard Stops Placed Too Late in Design

**Why it happens**: Hard stops are treated as an afterthought.

**Detection**: Absence of stop features in early CAD iterations.

**Prevention**: Add hard stop geometry as part of the pivot housing design, not as a bolt-on.

### 18.9 Differential Bar Deflection

**Why it happens**: Using thin rod for the bar (e.g., Sawppy's original 8mm steel bar bending under load).

**Detection**: Calculate bar bending deflection under worst-case asymmetric load.

**Prevention**: Use stiffer section (thicker rod, tube, or extrusion). Add a brace if needed.

### 18.10 Bearing Seats Wrong Size

**Why it happens**: Not accounting for 3D printer tolerances. A nominally 22mm bore printed at 21.8mm won't accept a 608ZZ bearing.

**Detection**: Print test pieces before committing to full parts.

**Prevention**: Print calibration/test pieces (we have TubeSocketTest and BearingTestPiece scripts). Use crush ribs or slightly oversized bores with adhesive.

---

## APPENDIX A: DESIGN-DRIVING PARAMETER LIST

All variables that must be defined before CAD can be finalised:

| # | Parameter | Symbol | Current Value (0.4x) | Must Be Solved? |
|---|-----------|--------|---------------------|-----------------|
| 1 | Wheel diameter | D_w | 80mm | Set by obstacle req |
| 2 | Target obstacle height | h_obs | 40mm (kerb edge) | User input |
| 3 | Total wheelbase | WB | 360mm | From D_w ratio |
| 4 | Track width | TW | 280mm | From stability |
| 5 | Rocker forward arm length | L_rf | 180mm | From wheel spacing |
| 6 | Rocker rear arm length | L_rr | 90mm | From pivot to bogie |
| 7 | Bogie front arm length | L_bf | 90mm | From pivot to mid wheel |
| 8 | Bogie rear arm length | L_br | 90mm | From pivot to rear wheel |
| 9 | Rocker pivot height | Z_rp | 60mm | From belly clearance |
| 10 | Bogie pivot height | Z_bp | 45mm | From arm geometry |
| 11 | Rocker pivot X offset | X_rp | 125mm | From body width |
| 12 | Steering max angle | alpha_max | 35 deg | From turning radius |
| 13 | Rocker articulation limit | theta_r | +/- 30 deg | From interference |
| 14 | Bogie articulation limit | theta_b | +/- 25 deg | From interference |
| 15 | Diff bar half-span | L_diff_half | 200mm (Phase 1) / 500mm (full) | Bar extends beyond body for link geometry |
| 16 | Diff link length | L_link | 85.0mm (Phase 1) / 212.1mm (full) | Computed in Section 9.5 |
| 17 | Diff link attachment offset (bar) | r_bar | 30mm (Phase 1) / 75mm (full) | Computed in Section 9.5 |
| 18 | Diff link attachment offset (rocker) | r_rocker | 30mm (Phase 1) / 75mm (full) | Computed in Section 9.5 |
| 19 | Rover mass | M | 1.25 kg | From weight budget |
| 20 | Bearing type (rocker pivot) | — | 608ZZ | From load calc |

## APPENDIX B: MINIMUM VIABLE CAD ARCHITECTURE (First Pass)

Model these parts for a clean structural layout:

1. Skeleton sketch (side view) with all pivot points
2. Wheel (single part, simplified, correct OD)
3. Rocker arm (single solid body, correct pivot points)
4. Bogie arm (single solid body, correct pivot points)
5. Differential bar (cylinder)
6. Differential links (cylinders with ball joint markers)
7. Body (box with pivot mount holes)
8. Joints defined with correct axis and limits

**Goal**: Verify geometry, motion, clearances. ~10 parts total.

## APPENDIX C: HIGH-FIDELITY CAD ARCHITECTURE (Full Detail)

Everything from Appendix B plus:

1. Wheel split into rim + tyre + hub + bearings
2. Motor + gearbox envelopes at each wheel
3. Steering knuckles with pivot bearings
4. Servo mounts with horn linkage
5. Rocker/bogie split into tubes + connectors (EA-25 approach)
6. Bearing seats with correct dimensions in all housings
7. Fastener holes (M3 heat-set inserts)
8. Cable channels and clips
9. Hard stops modelled as geometry
10. Differential links with real rod-end bearing geometry
11. Service loops modelled as flexible splines
12. Assembly constraints with motion limits

**Goal**: Directly generate printable STLs and assembly instructions. ~60-80 parts total.

---

## REFERENCES

- [Rocker-Bogie Wikipedia](https://en.wikipedia.org/wiki/Rocker-bogie)
- [Mars Rover Rocker-Bogie Differential](https://alicesastroinfo.com/2012/07/mars-rover-rocker-bogie-differential/)
- [JPL Open Source Rover — Rocker-Bogie Assembly](https://open-source-rover.readthedocs.io/en/latest/mechanical/rocker_bogie/)
- [JPL Open Source Rover — Body/Differential](https://open-source-rover.readthedocs.io/en/latest/mechanical/body/index.html)
- [Rocker-Bogie Suspension DeepWiki](https://deepwiki.com/nasa-jpl/open-source-rover/3.3-rocker-bogie-suspension)
- [Hackaday: Rocker Bogie Suspension](https://hackaday.com/2023/09/14/rocker-bogie-suspension-the-beloved-solution-to-extra-planetary-rovers/)
- [NASA NTRS: Challenges of Designing the Rocker-Bogie](https://ntrs.nasa.gov/api/citations/20040084284/downloads/20040084284.pdf)
- [NASA NTRS: Mars Science Laboratory Differential Restraint](https://esmats.eu/amspapers/pastpapers/pdfs/2012/jordan.pdf)
- [Sawppy Rover](https://hackaday.io/project/158208-sawppy-the-rover)
- [Beatty Robotics: Differential for Mars Rover](https://beatty-robotics.com/differential-for-mars-rover/)
- EA-01, EA-08, EA-10, EA-20, EA-25 (this project)
