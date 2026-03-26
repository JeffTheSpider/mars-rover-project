# Mars Rover Phase 1 — Assembly Positioning Guide

## Coordinate System

| Axis | Direction | Positive |
|------|-----------|----------|
| X | Left-Right | +X = Right (viewed from behind) |
| Y | Front-Back | +Y = Forward |
| Z | Up-Down | +Z = Up |
| Origin | Centre of body, at ground level (Z=0) | |

All values in **mm** unless stated. Fusion 360 uses **cm** internally (divide by 10).

---

## 1. Overall Envelope (0.4 scale)

| Parameter | mm | cm (Fusion) |
|-----------|----|-------------|
| Body length (Y) | 440 | 44.0 |
| Body width (X) | 260 | 26.0 |
| Body height (Z) | 120 | 12.0 |
| Ground clearance | 60 | 6.0 |
| Body bottom Z | 60 | 6.0 |
| Body top Z | 180 | 18.0 |
| Track width (wheel-to-wheel) | 280 | 28.0 |
| Wheelbase (front-to-rear) | 360 | 36.0 |
| Wheel diameter | 80 | 8.0 |
| Wheel width | 32 | 3.2 |

---

## 2. Wheel Positions (6 wheels)

Centre of each wheel hub. Z=40mm = wheel radius (sitting on ground Z=0).

| Wheel | X (mm) | Y (mm) | Z (mm) | Steered? | Rotation |
|-------|--------|--------|--------|----------|----------|
| Front-Left (FL) | -140 | +180 | 40 | Yes | 90° around Y (hub faces left) |
| Front-Right (FR) | +140 | +180 | 40 | Yes | -90° around Y (hub faces right) |
| Middle-Left (ML) | -140 | 0 | 40 | No | 90° around Y |
| Middle-Right (MR) | +140 | 0 | 40 | No | -90° around Y |
| Rear-Left (RL) | -140 | -180 | 40 | Yes | 90° around Y |
| Rear-Right (RR) | +140 | -180 | 40 | Yes | -90° around Y |

Wheels are revolve solids around Z in STL. Need 90° Y rotation to orient hub outward.

---

## 3. Body Quadrants (4 from 1 STL)

STL `BodyQuadrant.stl` bounding box: X=[-131,0], Y=[0,226], Z=[0,120] mm.
Origin at body centre, extends -X (left) and +Y (forward).

| Quadrant | Translation (mm) | Rotation | Coverage |
|----------|-----------------|----------|----------|
| FL | (0, 0, 60) | none | X[-131,0], Y[0,226] |
| FR | (+131, 0, 60) | none | X[0,131], Y[0,226] |
| RL | (0, -226, 60) | none | X[-131,0], Y[-226,0] |
| RR | (+131, -226, 60) | 180° Z | X[0,131], Y[-226,0] |

Note: FR and RL are translation-only (T&G won't visually mate perfectly, acceptable for assembly view). RR uses 180° Z rotation for correct diagonal mirror.

Top deck tiles follow same pattern at Z = 60+120 = 180mm.
STL `TopDeck.stl` bounding box: ~133x223x10mm.

---

## 4. Suspension Pivots — The Spine

### Diff Bar (through-bar design)
- 300mm 8mm steel rod, horizontal along X axis
- At Z = **120mm** (body mid-height, NOT 60mm)
- Spans X = -130 to +130mm
- Central 608ZZ bearing at (0, 0, 120)
- Side 608ZZ bearings at (±125, 0, 120) — in body walls

### Rocker Hub Connectors (×2)
- Clamped to diff bar at rocker pivot
- **Position**: (±125, 0, 120)
- Part size: ~45×40×35mm
- Diff bar bore: 8.0mm press-fit
- Front tube socket: angled ~15° down toward front wheel
- Rear tube socket: angled ~20° down toward bogie pivot

### Bogie Pivot Connectors (×2)
- 608ZZ bearing for bogie rotation
- **Position**: (±125, -90, ~55)
- Part size: ~45×35×30mm
- 3 tube sockets: from rocker, to middle wheel, to rear wheel

---

## 5. How Parts Connect — Mating Interfaces

### 5.1 Tube-in-Socket (8mm rods)

All suspension arms are 8mm steel rods inserted into printed connectors.

```
[Connector] ←── 8.2mm bore, 15mm deep ←── [8mm rod] ──→ 8.2mm bore, 15mm deep ──→ [Connector]
                 M3 grub screw retains                    M3 grub screw retains
```

- Socket bore: 8.2mm (0.2mm clearance for slide-fit)
- Socket depth: 15mm
- Retention: M3 grub screw through socket wall

### 5.2 Bolt-Through-to-Heat-Set (M3 fasteners)

**Connectors** have heat-set inserts (brass, melted into PLA at 170°C).
**Brackets/mounts** have M3 clearance holes (3.2mm) and bolt through into the inserts.

| Joint | Connector (has inserts) | Bracket (has through-holes) | Bolt Spacing |
|-------|------------------------|----------------------------|--------------|
| Steering bracket → FW connector | FrontWheelConnector front face | SteeringBracket | 20mm |
| Servo mount → FW connector | FrontWheelConnector side face | ServoMount | 20mm |
| Fixed mount → MW connector | MiddleWheelConnector mount face | FixedWheelMount | 16mm |

Insert dimensions: 4.8mm bore × 5.5mm deep, 0.5mm entry chamfer.

### 5.3 Bearing Seat (608ZZ)

```
[Housing wall]
  |── 22.15mm bore × 7.2mm deep (bearing press-fits in)
  |── 0.3mm × 45° entry chamfer
  |── 8.1mm through-bore (shaft passes through bearing)
```

### 5.4 Steering Pivot (per steered wheel)

```
                    ┌─────────────────────┐
                    │  Steering Bracket    │ ← bolted to FW Connector front face
                    │  ┌───────────────┐  │
                    │  │ 608ZZ bearing  │  │ ← press-fit in bracket top
                    │  └───────┬───────┘  │
                    │          │ 8mm shaft │ ← 50mm cut rod
                    │  Hard stop channel  │ ← 70° open arc at bottom
                    └──────────┼──────────┘
                               │
                    ┌──────────┼──────────┐
                    │  Steering Knuckle   │ ← hangs on pivot shaft
                    │  - 8.2mm pivot bore │
                    │  - Hard stop tab    │ ← sweeps in bracket channel (±35°)
                    │  - Steering arm     │ ← 15mm lateral, M2 hole for horn link
                    │  - N20 motor clip   │ ← holds drive motor
                    │  - 4mm axle bore    │ ← wheel axle
                    └─────────────────────┘
```

### 5.5 Steering Linkage (4-bar, per steered wheel)

```
    Servo shaft (in ServoMount)          Steering pivot (in bracket)
         │                                      │
         │ 15mm (SG90 horn arm)                 │ 15mm (knuckle steering arm)
         ▼                                      ▼
    Horn tip ─────── 20mm HornLink ──────── Arm tip
              (M2 pin)              (M2 pin)
```

- Servo-to-pivot horizontal offset: 20mm
- Angular ratio: ~1:1
- ServoMount sits on the SIDE face of the FrontWheelConnector

---

## 6. Suspension Arm Routing (Left Side)

All positions approximate for visual assembly:

```
                        Front Wheel FL (-140, +180, 40)
                              │
                         [FW Connector] at ~(-120, +180, 60)
                              │ 150mm rod, angled down
                              │
    Diff Bar ──────── [Rocker Hub] at (-125, 0, 120) ──── 608ZZ in body wall
    (Z=120)                   │
                              │ 60mm rod, angled down
                              │
                         [Bogie Pivot] at (-125, -90, ~55)
                           /          \
                    60mm rod         60mm rod
                    /                      \
        [MW Connector]              [FW Connector]
        (-120, 0, 60)              (-120, -180, 60)
              │                          │
        Middle Wheel ML           Rear Wheel RL
        (-140, 0, 40)            (-140, -180, 40)
```

Right side is symmetric (positive X).

---

## 7. Connector Positions (Assembly Coordinates)

These are the positions to use in the assembly script. All in mm.

### Wheel Connectors (at end of arm tubes, between body and wheel)

| Part | X | Y | Z | Notes |
|------|---|---|---|-------|
| FW Conn FL | -120 | +180 | 60 | ~20mm inboard of wheel centre |
| FW Conn FR | +120 | +180 | 60 | |
| MW Conn ML | -120 | 0 | 60 | |
| MW Conn MR | +120 | 0 | 60 | |
| FW Conn RL | -120 | -180 | 60 | Rear steered wheels use same connector |
| FW Conn RR | +120 | -180 | 60 | |

### Suspension Connectors

| Part | X | Y | Z | Notes |
|------|---|---|---|-------|
| Rocker Hub L | -125 | 0 | 120 | On diff bar, body mid-height |
| Rocker Hub R | +125 | 0 | 120 | |
| Bogie Pivot L | -125 | -90 | 55 | Below rocker, between mid and rear |
| Bogie Pivot R | +125 | -90 | 55 | |
| Diff Pivot Housing | 0 | 0 | 120 | Body centre, same Z as rockers |

### Steering Sub-Assembly (per corner, relative to wheel connector)

The steering bracket bolts to the **front face** of the wheel connector.
The servo mount bolts to the **side face** of the wheel connector.
The knuckle hangs **below** the bracket on the pivot shaft.

| Part | Offset from Connector | Notes |
|------|----------------------|-------|
| Steering Bracket | flush on front face, centred | Same X,Y as connector, same Z |
| Servo Mount | flush on side face, offset 20mm in X toward body | X ± 20mm from connector |
| Steering Knuckle | below bracket, -25mm Z | Hangs on pivot shaft |
| Horn Link | between servo horn tip and knuckle arm tip | ~10mm in front of connector |

### Steering Absolute Positions (FL corner example)

| Part | X | Y | Z |
|------|---|---|---|
| FW Connector FL | -120 | +180 | 60 |
| Steering Bracket FL | -120 | +180 | 60 |
| Servo Mount FL | -100 | +180 | 60 |
| Knuckle FL | -120 | +180 | 35 |
| Horn Link FL | -110 | +182 | 55 |

For FR: mirror X signs. For RL/RR: mirror Y signs (and X for RR).

### Fixed Wheel Mounts (middle wheels)

| Part | X | Y | Z |
|------|---|---|---|
| Fixed Mount ML | -120 | 0 | 60 |
| Fixed Mount MR | +120 | 0 | 60 |

Bolted to the mount face of MiddleWheelConnector.

---

## 8. Internal Components

All inside the body cavity (Z = 60 to 180mm).

| Part | X | Y | Z | Notes |
|------|---|---|---|-------|
| Electronics Tray | 0 | +50 | 63 | On body floor, toward front |
| Battery Tray | 0 | -80 | 63 | On body floor, toward rear |
| Fuse Holder | +50 | -50 | 63 | Near battery |
| Switch Mount | -130 | +100 | 120 | On left body side wall, mid-height |
| Strain Relief 1 | -125 | 0 | 120 | At left rocker pivot exit |
| Strain Relief 2 | +125 | 0 | 120 | At right rocker pivot exit |

---

## 9. Diff Links and Cable Clips

### Diff Links (×2)
Through-bar design means these may be vestigial (bar IS the pivot). If included:

| Part | X | Y | Z |
|------|---|---|---|
| Diff Link L | -62 | 0 | 118 |
| Diff Link R | +62 | 0 | 118 |

### Cable Clips (×4 representative, many more in reality)

Along the arm tubes at ~80mm intervals:

| Part | X | Y | Z |
|------|---|---|---|
| Clip L-front-1 | -125 | +60 | 100 |
| Clip L-front-2 | -125 | +120 | 80 |
| Clip R-front-1 | +125 | +60 | 100 |
| Clip R-front-2 | +125 | +120 | 80 |

---

## 10. Bearings (9 total)

| # | Location | Position (mm) | In Part |
|---|----------|--------------|---------|
| 1 | Body left wall | (-125, 0, 120) | BodyQuadrant (pivot boss) |
| 2 | Body right wall | (+125, 0, 120) | BodyQuadrant (pivot boss) |
| 3 | Body centre | (0, 0, 120) | DiffPivotHousing |
| 4 | Left bogie | (-125, -90, 55) | BogiePivotConnector |
| 5 | Right bogie | (+125, -90, 55) | BogiePivotConnector |
| 6 | Steering FL | (-120, +180, 60) | SteeringBracket |
| 7 | Steering FR | (+120, +180, 60) | SteeringBracket |
| 8 | Steering RL | (-120, -180, 60) | SteeringBracket |
| 9 | Steering RR | (+120, -180, 60) | SteeringBracket |

---

## 11. Key Insight: What Touches What

### Parts that DIRECTLY CONTACT each other:

1. **Body quadrants** touch each other at T&G joints along X=0 and Y=0
2. **Top deck tiles** sit on top of body quadrants (snap clips)
3. **Diff bar rod** passes through: DiffPivotHousing → body wall bearings → RockerHubConnectors
4. **Arm rods** slide into tube sockets on connectors (15mm insertion each end)
5. **Steering bracket** bolts flush to FrontWheelConnector front face
6. **Servo mount** bolts flush to FrontWheelConnector side face
7. **Knuckle** hangs from steering bracket via 8mm pivot shaft + bearing
8. **Horn link** pins between servo horn tip and knuckle steering arm
9. **Fixed wheel mount** bolts flush to MiddleWheelConnector mount face
10. **Electronics tray** sits on body floor (clips or standoffs)
11. **Battery tray** sits on body floor
12. **Cable clips** clamp around 8mm arm tubes

### Parts that need GAPS (clearance):

1. Wheels ↔ body side walls: minimum 10mm
2. Knuckle hard stop tab ↔ bracket channel walls: 0.5mm either side
3. Horn link ↔ connector body: minimum 2mm at full steering lock
4. Servo horn ↔ bracket wall: minimum 2mm
5. Rocker arms ↔ body walls at full articulation: minimum 3mm

---

## 12. Assembly Script Constants (corrected, in cm)

```python
# Body
BODY_L = 44.0       # 440mm
BODY_W = 26.0       # 260mm
BODY_H = 12.0       # 120mm
GROUND_Z = 6.0      # 60mm

# Wheels
TRACK_HALF = 14.0   # 140mm
WB_HALF = 18.0      # 180mm
WHEEL_R = 4.0       # 40mm
WHEEL_W = 3.2       # 32mm
WHEEL_Z = 4.0       # 40mm (wheel centre)

# Suspension pivots — CORRECTED
DIFF_Z = 12.0       # 120mm — body mid-height (NOT 6.0!)
ROCKER_X = 12.5     # 125mm
BOGIE_Y = -9.0      # -90mm
BOGIE_Z = 5.5       # 55mm (NOT 4.0!)

# Connector positions
CONN_X = 12.0       # 120mm — ~20mm inboard of wheel centre
CONN_Z = 6.0        # 60mm — at body bottom height
```
