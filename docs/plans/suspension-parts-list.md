# Suspension Assembly — Complete Parts List

**Version:** 1.0
**Date:** 2026-03-24
**Status:** DESIGN DRAFT — for review and iteration

## Design Philosophy

Inspired by [jakkra/Mars-Rover](https://github.com/jakkra/Mars-Rover) and NASA [Perseverance](https://newscrewdriver.com/2020/11/21/perseverance-rover-interactive-3d-model/):

- **Metal tubes with printed connectors** (like jakkra's PVC approach) for structural arms
- **Printed joints** house bearings and provide attachment/pivot points
- **Perseverance-style wheels** with curved spokes and angled grousers
- **608ZZ bearings** at all pivot points (proven, cheap, available)

### Why Tubes + Printed Connectors?

| Property | Fully Printed Arms | Tube + Connector |
|----------|-------------------|------------------|
| Strength | Limited (PLA layer adhesion) | Excellent (metal tube in tension/compression) |
| Weight | Heavier (solid infill needed) | Lighter (hollow tube) |
| Stiffness | Moderate | Very high |
| Print time | Long (180mm arms) | Short (just connectors) |
| Adjustability | None (reprint to resize) | Cut tubes to length |
| Aesthetics | Okay | NASA-like (visible tubes) |
| Assembly | Bolt together | Press-fit + grub screw |

---

## Part Categories

### A. PRINTED PARTS (PLA, CTC Bizer)

#### A1. Suspension Connectors (NEW — replace monolithic arms)

| # | Part | Qty | Description | Key Features |
|---|------|-----|-------------|--------------|
| 1 | **Rocker Hub Connector** | 2 | Central joint where rocker meets body (diff bar pivot) | 608ZZ bearing seat, 8mm tube socket ×2 (front + rear), M3 heat-set ×4, diff bar bore |
| 2 | **Bogie Pivot Connector** | 2 | Joint where bogie arm meets rocker arm rear | 608ZZ bearing seat, 8mm tube socket ×3 (rocker rear + bogie front + bogie rear), M3 heat-set ×4 |
| 3 | **Front Wheel Connector** | 2 | End of rocker front tube, mounts steering bracket | 8mm tube socket ×1, steering bracket mount (M3 heat-set ×2), servo mount tab |
| 4 | **Middle Wheel Connector** | 2 | End of bogie front tube, mounts fixed wheel mount | 8mm tube socket ×1, motor mount (M3 heat-set ×2) |
| 5 | **Rear Wheel Connector** | 2 | End of bogie rear tube, mounts steering bracket | 8mm tube socket ×1, steering bracket mount (M3 heat-set ×2), servo mount tab |

**Connector design notes:**
- Each connector has a **socket** for the 8mm tube: 8.2mm bore × 15mm deep (0.2mm clearance)
- Tube is secured with a **M3 grub screw** through the connector wall into the tube
- Wall thickness around tube socket: 4mm minimum (structural)
- Bearing seats: 22.15mm bore × 7.2mm deep (standard 608ZZ, as per CAD audit)
- Material: PLA, 60% infill, 5 perimeters

#### A2. Steering & Drive Components (existing designs, may need socket adapters)

| # | Part | Qty | Description | Script |
|---|------|-----|-------------|--------|
| 6 | **Steering Bracket** | 4 | Corner wheel pivot housing (608ZZ + N20 motor clip) | `steering_bracket.py` |
| 7 | **Servo Mount** | 4 | SG90 servo bracket, drives steering rotation | `servo_mount.py` |
| 8 | **Fixed Wheel Mount** | 2 | Middle wheel motor mount (no steering) | `fixed_wheel_mount.py` |

#### A3. Drivetrain

| # | Part | Qty | Description | Script |
|---|------|-----|-------------|--------|
| 9 | **Diff Bar Adapter** | 3 | Press-fit on 8mm diff bar rod, provides bearing seat | `diff_bar_adapter.py` |

#### A4. Wheels

| # | Part | Qty | Description | Script |
|---|------|-----|-------------|--------|
| 10 | **Rover Wheel V2** | 6 | 80mm OD, Perseverance-style curved spokes, 24 grousers | `rover_wheel_v2.py` (**NEW**) |
| 11 | **Rover Tire** | 6 | TPU 95A tire (86mm OD, 70mm bore) — Phase 2 / friend's printer | `rover_tire.py` |

#### A5. Body (not part of suspension, but connects to it)

| # | Part | Qty | Description |
|---|------|-----|-------------|
| 12 | Body Quadrant | 4 | FL/FR/RL/RR panels (diff bar passes through rocker pivot bosses) |
| 13 | Top Deck Tile | 4 | FL/FR/RL/RR covers |

**Total printed parts for suspension: 27** (10 connectors + 4 steering + 4 servo + 2 fixed mount + 3 diff adapter + 6 wheels)
_Reduced from 33 if you count the old monolithic arms (2 rocker front + 2 rocker rear + 2 bogie = 6 arms eliminated, replaced by 10 smaller connectors)_

---

### B. HARDWARE — Metal Tubes & Rods

#### B1. Structural Tubes (8mm steel rod or aluminium tube)

| # | Part | Qty | Length | Description |
|---|------|-----|--------|-------------|
| 1 | **Rocker Front Tube** | 2 | ~165mm | Rocker hub connector → front wheel connector |
| 2 | **Rocker Rear Tube** | 2 | ~75mm | Rocker hub connector → bogie pivot connector |
| 3 | **Bogie Front Tube** | 2 | ~75mm | Bogie pivot connector → middle wheel connector |
| 4 | **Bogie Rear Tube** | 2 | ~75mm | Bogie pivot connector → rear wheel connector |
| 5 | **Differential Bar** | 1 | 300mm | 8mm steel rod, spans full width (existing design) |

**Tube options:**
- **8mm steel rod** (current design): cheap, strong, heavy. Socket = 8.2mm bore.
- **8mm OD aluminium tube** (6mm ID): lighter, weaker but sufficient at 0.4 scale. Same sockets.
- **10mm OD aluminium tube** (8mm ID): better for grip, needs wider sockets.
- **6mm carbon fibre rod**: lightest, most expensive. Very stiff.

**Recommendation for Phase 1:** 8mm steel rod (consistency with diff bar, cheapest, readily available from hardware store). Cut to length with hacksaw.

**Total tube length needed:** 2×165 + 4×75 + 300 = 930mm ≈ 1m of 8mm rod

#### B2. Bearings

| # | Part | Qty | Location | Spec |
|---|------|-----|----------|------|
| 1 | 608ZZ | 2 | Rocker body pivot (L+R) | 22×8×7mm |
| 2 | 608ZZ | 2 | Bogie pivot (L+R) | 22×8×7mm |
| 3 | 608ZZ | 1 | Diff bar centre (body mount) | 22×8×7mm |
| 4 | 608ZZ | 2 | Diff bar ends | 22×8×7mm |
| 5 | 608ZZ | 4 | Steering pivots (4 corners) | 22×8×7mm |
| **Total** | **608ZZ** | **11** | | **~£5 for 10-pack on Amazon** |

#### B3. Fasteners

| # | Part | Qty | Use |
|---|------|-----|-----|
| 1 | M3 × 8mm bolt | 30 | Connector assembly, bracket mounting |
| 2 | M3 × 12mm bolt | 10 | Through-connector joints |
| 3 | M3 heat-set insert (4.8mm × 5.5mm) | 40 | All printed connector sockets |
| 4 | M3 grub screw (set screw) | 8 | Tube retention in connectors |
| 5 | M2 × 6mm bolt | 8 | Servo tab mounting (4 servos × 2 screws) |
| 6 | M2 grub screw | 6 | Wheel shaft retention |
| 7 | 8mm shaft collar / E-clip | 10 | Axial retention on 8mm rods |

#### B4. 8mm Shafts (Axle Pins)

| # | Part | Qty | Length | Use |
|---|------|-----|--------|-----|
| 1 | 8mm steel pin | 2 | 35mm | Rocker body pivot axle |
| 2 | 8mm steel pin | 2 | 35mm | Bogie pivot axle |
| 3 | 8mm steel pin | 4 | 20mm | Steering pivot axle (through steering bracket bearing) |

---

### C. ELECTRONICS

| # | Part | Qty | Use |
|---|------|-----|-----|
| 1 | N20 100RPM motor (3V-6V) | 6 | One per wheel, 3.1mm D-shaft |
| 2 | SG90 micro servo | 4 | Steering (FL, FR, RL, RR) |
| 3 | L298N dual H-bridge | 2 | Motor drivers (3 motors per driver via parallel pairs) |

---

## Assembly Hierarchy

```
Rover
├── Differential Bar (300mm 8mm rod)
│   ├── DiffAdapter_L (press-fit, bearing)
│   ├── DiffAdapter_C (press-fit, bearing, body mount)
│   └── DiffAdapter_R (press-fit, bearing)
│
├── Suspension_Left
│   ├── Rocker Hub Connector (bearing on diff bar)
│   │   ├── Rocker Front Tube (165mm)
│   │   │   └── Front Wheel Connector
│   │   │       ├── Steering Bracket FL (608ZZ bearing)
│   │   │       │   ├── N20 Motor FL
│   │   │       │   └── Wheel FL (V2, Perseverance-style)
│   │   │       └── Servo Mount FL (SG90)
│   │   │
│   │   └── Rocker Rear Tube (75mm)
│   │       └── Bogie Pivot Connector (608ZZ bearing)
│   │           ├── Bogie Front Tube (75mm)
│   │           │   └── Middle Wheel Connector
│   │           │       ├── Fixed Wheel Mount ML
│   │           │       │   ├── N20 Motor ML
│   │           │       │   └── Wheel ML
│   │           │
│   │           └── Bogie Rear Tube (75mm)
│   │               └── Rear Wheel Connector
│   │                   ├── Steering Bracket RL
│   │                   │   ├── N20 Motor RL
│   │                   │   └── Wheel RL
│   │                   └── Servo Mount RL (SG90)
│
└── Suspension_Right (mirror of left)
```

---

## New Connector Parts to Design

These 5 connector types need CAD scripts written. They replace the monolithic rocker/bogie arms.

### 1. Rocker Hub Connector
```
        ┌──────┐
  ══════╪  HUB ╪══════    ← 8mm tube sockets (front + rear)
        │ ◯608 │           ← 608ZZ bearing for diff bar pivot
        └──┬───┘
           │
        DiffBar
```
- Size: ~40×35×30mm
- Features: 2× tube sockets (front + rear), 1× 608ZZ bearing seat, 1× 8mm diff bar bore
- This is the most complex connector

### 2. Bogie Pivot Connector
```
  ══════╪  PIVOT ╪══════   ← 8mm tube sockets (×3: rocker-rear + bogie-front + bogie-rear)
        │  ◯608  │          ← 608ZZ bearing for pivot axis
        └────────┘
```
- Size: ~45×35×25mm
- Features: 3× tube sockets, 1× 608ZZ bearing seat
- The rocker tube enters from the top, bogie tubes go front+rear

### 3. Front/Rear Wheel Connector
```
  ══════╪ END ╪
        │     │──── Steering bracket mount (M3 heat-set × 2)
        │     │──── Servo mount tab
        └─────┘
```
- Size: ~30×25×25mm
- Features: 1× tube socket, flat face for steering bracket, servo mount tab

### 4. Middle Wheel Connector
```
  ══════╪ END ╪
        │     │──── Fixed mount interface (M3 heat-set × 2)
        └─────┘
```
- Size: ~25×25×20mm
- Features: 1× tube socket, flat face for fixed wheel mount

---

## Comparison: Old vs New Approach

| Aspect | Old (Monolithic Arms) | New (Tube + Connector) |
|--------|----------------------|----------------------|
| Parts to print | 6 arms (2 rocker front, 2 rear, 2 bogie) | 10 connectors (5 types × 2 sides) |
| Print time | ~25 hrs (6 long arms) | ~12 hrs (10 small connectors) |
| Structural strength | PLA only (weak in bending) | Steel tube (excellent) |
| Total weight | ~180g (PLA arms) | ~120g (connectors) + ~150g (steel) = ~270g |
| Failure mode | Brittle snap at layer lines | Connector crush (graceful) |
| Adjustability | None | Cut tubes to length |
| Aesthetics | Blocky | NASA/industrial look |
| Complexity | Simple (one print) | More parts, more assembly |

**Verdict:** The tube + connector approach is better for a rover that needs to drive outdoors. The trade-off is slightly more weight and assembly complexity, but much better strength and a great look.

---

## Print Schedule (Suspension Only)

| Priority | Part | Qty | Est. Time | Est. PLA |
|----------|------|-----|-----------|----------|
| 1 | Bearing Test Piece | 1 | 1h | 5g |
| 2 | Calibration Test Card | 1 | 0.5h | 3g |
| 3 | Wheel V2 | 6 | 24h (4h each) | 120g |
| 4 | Rocker Hub Connector | 2 | 4h (2h each) | 30g |
| 5 | Bogie Pivot Connector | 2 | 4h | 30g |
| 6 | Front Wheel Connector | 2 | 2h | 16g |
| 7 | Rear Wheel Connector | 2 | 2h | 16g |
| 8 | Middle Wheel Connector | 2 | 1.5h | 10g |
| 9 | Steering Bracket | 4 | 18h (4.5h each) | 104g |
| 10 | Servo Mount | 4 | 6h (1.5h each) | 32g |
| 11 | Fixed Wheel Mount | 2 | 2h | 12g |
| 12 | Diff Bar Adapter | 3 | 3h | 20g |
| **Total** | | **31** | **~68h** | **~398g** |

---

## Next Steps

1. **Review this parts list together** — decide on tube material (steel vs aluminium)
2. **Design the 5 new connector types** — CAD scripts needed
3. **Run wheel V2 in Fusion 360** — evaluate aesthetics, iterate spoke curve
4. **Run suspension assembly** — see all parts together
5. **Drop reference screenshots** into `cad/reference/suspension-refs/` for design inspiration
6. **Order hardware** — 608ZZ bearings, 1m × 8mm steel rod, M3 fastener kit, heat-set inserts
