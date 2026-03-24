# Suspension System — Comprehensive Design & Build Plan

**Version:** 1.0
**Date:** 2026-03-24
**Status:** ACTIVE — CAD scripts created (EA-25 audit complete), awaiting Fusion 360 export & test prints

---

## 1. Design Summary

### Approach: Tube + Printed Connector (Hybrid)

Inspired by jakkra/Mars-Rover (PVC tubes), Sawppy (8mm rod frame), and MrOver (wire pass-throughs):

- **8mm steel rods** for structural arms (rocker + bogie tubes)
- **3D-printed PLA connectors** at every joint (bearing seats, tube sockets, wire channels)
- **608ZZ bearings** at all pivot points (8 total — EA-25 corrected from 11)
- **Chunky 5-spoke wheels** (jakkra-style, strong at 0.4 scale PLA)
- **2-part wheels**: PLA rim + removable TPU tire
- **Wire pass-through channels** in every connector (MrOver approach)

### Why This Approach

| Property | Fully Printed | Tube + Connector (Chosen) |
|----------|--------------|--------------------------|
| Strength | PLA layer adhesion limits | Steel tube in tension/compression |
| Print time | ~25h (long arms) | ~12h (small connectors only) |
| Cable routing | Channels in arm walls | Through hollow tubes + connector holes |
| Adjustability | None (reprint) | Cut tubes to length |
| Aesthetics | Blocky | NASA/industrial look |
| Weight | ~180g PLA | ~120g PLA + ~150g steel = ~270g |

---

## 2. Reference Library

### Downloaded Reference Files

| Source | License | Location | Key Parts |
|--------|---------|----------|-----------|
| **Sawppy V1** | MIT | `cad/reference/sawppy/` (24 STLs) | Rocker, bogie, diff bar (5-part), knuckles, wheel+hub |
| **jakkra Mars-Rover** | MIT | `cad/reference/jakkra/` (2 F3D) | Full rover assembly + flex wheel |
| **OpenPerseverance** | LGPL | `cad/reference/open-perseverance/` (4 STLs) | Tire, wheel rim, wheel holders |
| **Papaya Pathfinder** | Apache-2.0 | `cad/reference/papaya-pathfinder/` | N20 motor mounts, diff bar, rim+tire |
| **MrOver** | GPL-3.0 | `cad/reference/mrover/` | Tube joints with wire pass-throughs (OpenSCAD) |

### Key Learnings From References

1. **Sawppy** (483 stars, most proven): 8mm rod frame, 608ZZ bearings, clip-on connectors. Rocker 98mm, bogie 147mm total. DiffBrace spans full 240mm body width.
2. **Papaya Pathfinder Mini**: Nearly identical to our Phase 1 (N20 motors, 2S LiPo, ESP32). 3-part diff bar (simpler than Sawppy's 5-part). 2-part wheels (rim + TPU tire).
3. **MrOver**: Only reference found with **dedicated 7×13mm wire pass-through holes** in suspension joints. Parametric OpenSCAD source. Uses carbon fibre tubes + thrust bearings.
4. **jakkra**: Chunky 5-spoke wheels suitable for PLA at small scale. PVC tube frame. Full Fusion 360 parametric source available.

---

## 3. Complete Parts List

### 3A. WHEELS (12 parts: 6 rims + 6 tires)

| # | Part | Qty | Material | Dimensions | Script |
|---|------|-----|----------|------------|--------|
| 1 | **Wheel Rim** | 6 | PLA | 80mm OD × 32mm wide, 5 chunky spokes, 3.1mm D-shaft bore | `rover_wheel_v3.py` (NEW) |
| 2 | **Wheel Tire** | 6 | TPU 95A | 86mm OD × 75mm bore × 32mm wide, tread pattern | `rover_tire.py` (UPDATE bore) |

**Wheel design decisions:**
- Rim seat OD: **75mm** (between rim lips, where tire sits)
- Tire bore: **75mm** (press-fit interference ~0.2mm)
- Rim outer OD: **80mm** (lip edge to lip edge)
- Tire outer OD: **86mm** (total diameter with tread)
- Rim lip height: **1.5mm** each side (axial retention)
- 5 chunky spokes (jakkra-style, 6-8mm wide — strong in PLA)
- 24 grousers on rim (used when no tire fitted)
- Hub boss: 8mm protrusion for shaft engagement
- M2 grub screw through hub wall for shaft retention
- Print hub-side down, no supports needed

### 3B. SUSPENSION CONNECTORS (10 parts: 5 types × 2 sides)

All connectors share these features:
- **Tube socket**: 8.2mm bore × 15mm deep (0.2mm clearance on 8mm rod)
- **M3 grub screw** through wall into tube (retention)
- **Wire channel**: 8×6mm rectangular pass-through (fits 5-7 wires)
- **Wall thickness**: 4mm minimum around sockets
- **Material**: PLA, 60% infill, 5 perimeters

#### Connector Type 1: Rocker Hub Connector (×2)

```
        ┌──────────┐
  ══════╪   HUB    ╪══════   ← 8mm tube sockets (front + rear)
        │  ◎ clamp │          ← 8mm diff bar clamp bore (M3 grub)
        │  ▢ wire  │          ← 8×6mm wire channels (×2)
        └────┬─────┘
             │
          DiffBar (8mm rod, clamped — NOT bearing)
```

- **Size**: ~45×40×35mm
- **Features**: 2× tube sockets (front arm, rear arm), 8mm diff bar clamp bore (press-fit + M3 grub screw), 2× wire channels from body side to each arm
- **Most complex connector** — 3 orthogonal bores (diff bar + 2 tube sockets)
- **Differential mechanism**: Connector clamps rigidly to diff bar. Diff bar passes through 608ZZ bearings in body pivot bosses. When one side tilts, bar rotates, tilting the other side — keeping body level.
- **Cable routing**: Wires enter from body side, split to front tube and rear tube
- **Script**: `rocker_hub_connector.py` ✅

#### Connector Type 2: Bogie Pivot Connector (×2)

```
     rocker rear tube
           ║
  ═════════╪  PIVOT  ╪═════════
  bogie    │  ◯ 608  │  bogie
  front    │  ▢ wire │  rear
           └─────────┘
```

- **Size**: ~50×40×30mm
- **Features**: 3× tube sockets (rocker-rear, bogie-front, bogie-rear), 1× 608ZZ bearing seat, 8mm pivot shaft bore, wire channel splitting to middle and rear wheels
- **Cable routing**: 7 wires enter from rocker rear tube, split: 2 to bogie front (middle motor), 5 to bogie rear (rear motor + servo)
- **Script**: `bogie_pivot_connector.py` ✅

#### Connector Type 3: Front Wheel Connector (×2)

```
  ══════╪  END  ╪
        │       │──── Steering bracket mount (M3 heat-set × 2)
        │ ▢wire │──── Servo mount tab
        └───────┘
```

- **Size**: ~35×30×28mm
- **Features**: 1× tube socket (rocker front), flat face for steering bracket (2× M3 heat-set), servo mount tab (2× M2 holes), wire exit port (5 wires: 2 motor + 3 servo)
- **Cable routing**: 5 wires exit tube, route to motor (2) and servo (3)
- **Script**: `front_wheel_connector.py` ✅

#### Connector Type 4: Rear Wheel Connector (×2)

- **Identical to Front Wheel Connector** — same steering bracket + servo mount interface
- **Size**: ~35×30×28mm
- **Cable routing**: 5 wires exit bogie rear tube to motor + servo
- **Script**: `front_wheel_connector.py` ✅ (same script, print ×4 total)

#### Connector Type 5: Middle Wheel Connector (×2)

```
  ══════╪  END  ╪
        │       │──── Fixed wheel mount interface (M3 heat-set × 2)
        └───────┘
```

- **Size**: ~30×25×25mm
- **Features**: 1× tube socket (bogie front), flat face for fixed wheel mount (2× M3 heat-set), wire exit port (2 wires: motor only, no servo)
- **Simplest connector** — no steering, fewer wires
- **Script**: `middle_wheel_connector.py` ✅

### 3C. STEERING & DRIVE (10 parts)

| # | Part | Qty | Description | Script |
|---|------|-----|-------------|--------|
| 3 | **Steering Bracket** | 4 | Corner wheel pivot housing (608ZZ + N20 clip) | `steering_bracket.py` |
| 4 | **Servo Mount** | 4 | SG90 bracket, drives steering rotation | `servo_mount.py` |
| 5 | **Fixed Wheel Mount** | 2 | Middle wheel motor mount (no steering) | `fixed_wheel_mount.py` |

### 3D. DRIVETRAIN (0 separate printed parts)

**EA-25 correction**: Diff bar adapters are **deprecated**. The 300mm diff bar
passes directly through 608ZZ bearings housed in the body pivot bosses
(built into `body_quadrant.py`). Rocker hub connectors clamp rigidly to
the diff bar ends via M3 grub screws. No separate adapters needed.

### 3D-ALT. CABLE MANAGEMENT

| # | Part | Qty | Description | Script |
|---|------|-----|-------------|--------|
| 6 | **Cable Clip** | 12 | Snap-fit C-clip for 8mm rod, wire channel | `cable_clip.py` ✅ |

### 3E. HARDWARE — Metal & Bearings

#### Tubes (8mm steel rod)

| # | Part | Qty | Length | Run |
|---|------|-----|--------|-----|
| 1 | Rocker Front Tube | 2 | 150mm | Hub connector → front wheel connector |
| 2 | Rocker Rear Tube | 2 | 60mm | Hub connector → bogie pivot connector |
| 3 | Bogie Front Tube | 2 | 60mm | Bogie pivot → middle wheel connector |
| 4 | Bogie Rear Tube | 2 | 60mm | Bogie pivot → rear wheel connector |
| 5 | Differential Bar | 1 | 300mm | Full width, 8mm steel rod |

**Tube lengths explained** (0.4x scale):
- Rocker front: 180mm arm - 15mm socket each end = **150mm** exposed tube
- Rocker rear: 90mm arm - 15mm socket each end = **60mm** exposed tube
- Bogie front/rear: 90mm arm - 15mm socket each end = **60mm** exposed tube
- **Total rod needed**: 2×150 + 6×60 + 300 = **960mm ≈ 1m of 8mm rod**

#### Bearings

| Location | Qty | Spec |
|----------|-----|------|
| Body diff-bar pivot bosses (L+R) | 2 | 608ZZ (22×8×7mm) |
| Bogie pivot (L+R) | 2 | 608ZZ |
| Steering pivots (FL, FR, RL, RR) | 4 | 608ZZ |
| **Total** | **8** | **~£5 for 10-pack (2 spare)** |

**EA-25 correction**: Reduced from 11 to 8. Diff bar bearings are in the body
pivot bosses (not separate adapters). Rocker hub connectors clamp to diff bar
(rigid, no bearing).

#### Fasteners

| Part | Qty | Use |
|------|-----|-----|
| M3 × 8mm socket cap | 30 | Connector + bracket assembly |
| M3 × 12mm socket cap | 10 | Through-connector joints |
| M3 heat-set insert (4.8mm × 5.5mm) | 40 | All printed connector sockets |
| M3 grub screw (set screw) | 8 | Tube retention in connectors |
| M8 × 40mm hex bolt | 4 | Rocker + bogie pivot shafts |
| M8 × 30mm hex bolt | 4 | Steering pivot shafts |
| M8 nyloc nut | 8 | All pivot shafts |
| M8 washer | 16 | Both sides of bearings |
| M2 × 6mm bolt | 8 | Servo tab mounting |
| M2 grub screw | 6 | Wheel shaft retention |

### 3F. ELECTRONICS (in suspension)

| Part | Qty | Wires | Location |
|------|-----|-------|----------|
| N20 100RPM motor | 6 | 2 each (12 total) | One per wheel |
| SG90 micro servo | 4 | 3 each (12 total) | 4 steered corners |
| **Total wires through suspension** | | **24** | |

---

## 4. Wire Routing Through Suspension

### Wire Counts Per Arm Segment

```
BODY → Rocker Hub Connector → Front Tube (5 wires) → Front Wheel
  │                          └ Rear Tube (7 wires) → Bogie Pivot
  │                                                    ├ Front (2) → Mid Wheel
  │                                                    └ Rear (5) → Rear Wheel
```

| Segment | Wires | Details |
|---------|-------|---------|
| Body → Rocker Hub | 12 (L) or 12 (R) | All wires for one side enter here |
| Rocker Front Tube | 5 | 2× motor + 3× servo (front wheel) |
| Rocker Rear Tube | 7 | 2+2 motor + 3 servo (mid + rear wheels) |
| Bogie Front Tube | 2 | Motor only (middle wheel, no servo) |
| Bogie Rear Tube | 5 | 2× motor + 3× servo (rear wheel) |

### Wire Channel Design

- **Channel size**: 8mm × 6mm rectangular (fits 7 wires of 20-26 AWG with room)
- **Channel position**: Along the tube socket, exits at connector faces
- **Pivot clearance**: +40mm wire loop at each pivot point (EA-23 spec)
- **Strain relief**: Hot glue anchor point 20mm before each pivot

---

## 5. Dimension Audit — Critical Fitments

All connectors MUST accommodate these hardware dimensions exactly:

| Hardware | Dimension | Tolerance | Used In |
|----------|-----------|-----------|---------|
| 608ZZ bearing seat | 22.15mm bore × 7.2mm deep | ±0.05mm | Hub, bogie pivot, steering |
| 8mm tube socket | 8.2mm bore × 15mm deep | ±0.1mm | All connectors |
| N20 motor clip | 12.2 × 10.2 × 25mm | ±0.1mm | Steering bracket, fixed mount |
| SG90 servo pocket | 22.4 × 12.2 × 12mm deep | ±0.1mm | Servo mount |
| Heat-set insert hole | 4.8mm × 5.5mm deep | ±0.05mm | All connectors |
| M3 clearance | 3.3mm | ±0.1mm | All bolt holes |
| M8 clearance | 8.4mm | ±0.1mm | Pivot shafts |
| Wire channel | 8 × 6mm | ±0.5mm | All connectors |

---

## 6. Assembly Hierarchy

```
Rover
├── Body (4 quadrants + 4 top deck tiles)
│   ├── Diff Bar Centre Mount (608ZZ bearing in body)
│   └── Rocker Pivot Bosses (L+R, in body quadrants)
│
├── Differential Bar Assembly (EA-25 simplified)
│   ├── 300mm 8mm Steel Rod
│   ├── 608ZZ bearing in body left pivot boss
│   └── 608ZZ bearing in body right pivot boss
│
├── LEFT Suspension
│   ├── Rocker Hub Connector (608ZZ on diff bar)
│   │   ├── Rocker Front Tube (150mm) ─────────────┐
│   │   │   └── Front Wheel Connector              │
│   │   │       ├── Steering Bracket FL (608ZZ)     │ 5 wires
│   │   │       │   ├── N20 Motor FL ←─── 2 wires  │
│   │   │       │   └── Wheel Rim FL + Tire         │
│   │   │       └── Servo Mount FL (SG90) ← 3 wires│
│   │   │                                           │
│   │   └── Rocker Rear Tube (60mm) ───────────────┐
│   │       └── Bogie Pivot Connector (608ZZ)      │ 7 wires
│   │           ├── Bogie Front Tube (60mm) ───────┐
│   │           │   └── Middle Wheel Connector     │ 2 wires
│   │           │       ├── Fixed Mount ML         │
│   │           │       │   ├── N20 Motor ML       │
│   │           │       │   └── Wheel Rim ML + Tire│
│   │           │                                   │
│   │           └── Bogie Rear Tube (60mm) ────────┐
│   │               └── Rear Wheel Connector       │ 5 wires
│   │                   ├── Steering Bracket RL    │
│   │                   │   ├── N20 Motor RL       │
│   │                   │   └── Wheel Rim RL + Tire│
│   │                   └── Servo Mount RL (SG90)  │
│   │
│   └── [Wire harness: 12 wires total for left side]
│
└── RIGHT Suspension (mirror of left)
    └── [Wire harness: 12 wires total for right side]
```

---

## 7. CAD Scripts Needed

### New Scripts — ALL CREATED ✅ (EA-25)

| # | Script | Part | Status | Notes |
|---|--------|------|--------|-------|
| 1 | `rover_wheel_v3.py` | Wheel Rim (5-spoke, jakkra-style) | ✅ Created | 80mm OD, 75mm seat, USE_TPU_TIRE toggle |
| 2 | `rocker_hub_connector.py` | Rocker Hub Connector | ✅ Created | Diff bar clamp + 2 tube sockets |
| 3 | `bogie_pivot_connector.py` | Bogie Pivot Connector | ✅ Created | 608ZZ + 3 tube sockets |
| 4 | `front_wheel_connector.py` | Front/Rear Wheel Connector | ✅ Created | Steered wheel end (×4) |
| 5 | `middle_wheel_connector.py` | Middle Wheel Connector | ✅ Created | Fixed wheel end (×2) |
| 6 | `cable_clip.py` | Cable Clip | ✅ Created | Snap-fit C-clip for 8mm rod |
| 7 | `tube_socket_test.py` | Tube Socket Test Piece | ✅ Created | Validates 8mm rod fit |
| 8 | `suspension_assembly_v2.py` | Full assembly (all parts) | PENDING | Validates all geometry together |

### Existing Scripts Updated ✅

| Script | Change | Status |
|--------|--------|--------|
| `rover_tire.py` | Bore 70mm → 75mm | ✅ Fixed |
| `rocker_arm.py` | Deprecated (EA-25) | ✅ Deprecated header added |
| `bogie_arm.py` | Deprecated (EA-25) | ✅ Deprecated header added |
| `diff_bar_adapter.py` | Deprecated (EA-25) | ✅ Deprecated header added |

---

## 8. Print Schedule

| Priority | Part | Qty | Est. Hours | Est. PLA | Notes |
|----------|------|-----|------------|----------|-------|
| 1 | Bearing Test Piece | 1 | 1h | 5g | Validate 608ZZ fit first |
| 2 | Calibration Test Card | 1 | 0.5h | 3g | Validate M3, M8 holes |
| 3 | **Rocker Hub Connector** | 1 (test) | 2h | 15g | Most complex — test first |
| 4 | Wheel Rim V3 | 1 (test) | 4h | 20g | Validate spoke strength |
| 5 | Rocker Hub Connector | 2 | 4h | 30g | Both sides |
| 6 | Bogie Pivot Connector | 2 | 4h | 30g | |
| 7 | Front Wheel Connector | 2 | 2h | 16g | |
| 8 | Rear Wheel Connector | 2 | 2h | 16g | |
| 9 | Middle Wheel Connector | 2 | 1.5h | 10g | |
| 10 | Wheel Rim V3 | 6 | 24h | 120g | 4h each |
| 11 | Steering Bracket | 4 | 18h | 104g | 4.5h each |
| 12 | Servo Mount | 4 | 6h | 32g | 1.5h each |
| 13 | Fixed Wheel Mount | 2 | 2h | 12g | |
| 14 | Diff Bar Adapter | 3 | 3h | 20g | |
| **Total** | | **33** | **~74h** | **~433g** | ~0.5 spool PLA |

---

## 9. Build Order (Assembly Sequence)

### Phase A: Validation Prints (Day 1)
1. Bearing test piece — validate 608ZZ seat (22.15mm bore)
2. Calibration test card — validate M3/M8 holes
3. First rocker hub connector (test print) — validate tube socket + bearing + wire channel
4. First wheel rim V3 (test print) — validate spoke strength + tire fit

### Phase B: Connectors (Days 2-3)
5. Remaining connectors (9 parts): hub ×2, bogie ×2, front ×2, rear ×2, middle ×2
6. Diff bar adapters ×3
7. Cut 8mm steel rod: 2×150mm, 6×60mm (hacksaw)

### Phase C: Drive Components (Days 4-6)
8. Steering brackets ×4 (longest prints at 4.5h each)
9. Servo mounts ×4
10. Fixed wheel mounts ×2

### Phase D: Wheels (Days 7-8)
11. Wheel rims ×6 (4h each, can run overnight)
12. TPU tires ×6 (friend's printer — coordinate separately)

### Phase E: Assembly (Day 9)
13. Dry-fit all connectors + tubes (no glue/screws)
14. Install heat-set inserts (170-180°C iron)
15. Assemble diff bar + adapters
16. Assemble left suspension: hub → tubes → connectors → brackets → motors → wheels
17. Assemble right suspension (mirror)
18. Wire routing: thread wires through tubes, connect at each joint
19. Mount to body quadrants

---

## 10. Design Iteration Plan

### Iteration 1: Validate Fitments
- Print test pieces, measure with calipers
- Adjust 608ZZ seat if needed (target: gentle press-fit, no hammer required)
- Adjust tube socket bore if needed (target: snug slide-fit)
- Validate wire channel size (fit 7 wires through 8×6mm channel)

### Iteration 2: Structural Test
- Assemble one bogie arm (2 connectors + 2 tubes)
- Hand-test: can it support 200g (rover weight / 3 wheels per side)?
- Twist test: any play in tube sockets? Tighten grub screws.

### Iteration 3: Full Suspension
- Assemble complete left side suspension
- Test articulation: rocker +/-15°, bogie +/-15°
- Test wire routing: no pinching at pivots?
- Mount to body, test diff bar operation

---

## 11. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tube socket too loose | Arms wobble | Reduce bore to 8.1mm, add knurled inner surface |
| 608ZZ seat too tight | Can't insert bearing | Increase bore to 22.2mm, or ream with drill |
| Spokes too thin | Wheel breaks under load | Use 5 chunky spokes (6-8mm), not 6 thin ones |
| Wire pinching at pivot | Electrical failure | Wire loop slack (+40mm), strain relief anchors |
| Connector splitting at layer lines | Structural failure | 5 perimeters, 60% infill, orient for vertical loads |
| Tube cutting inaccurate | Arms wrong length | Mark and measure twice, file to length |
| Heat-set inserts melt through | Weak mounting | 170°C (not 200°C), practice on scrap first |

---

## 12. Shopping List (Suspension-Specific Hardware)

| Item | Qty | Est. Cost | Source |
|------|-----|-----------|--------|
| 608ZZ bearing | 10 (2 spare, 8 needed) | £5 | Amazon |
| 8mm steel rod × 1m | 1 | £3 | Hardware store |
| M3 × 8mm socket cap bolt | 30 | £4 (box of 50) | Amazon |
| M3 × 12mm socket cap bolt | 10 | £3 (box of 20) | Amazon |
| M3 heat-set insert (M3×4.8×5.5) | 50 (10 spare) | £6 | Amazon |
| M3 grub screw (set screw) × 5mm | 10 | £3 | Amazon |
| M8 × 40mm hex bolt | 4 | £2 | Hardware store |
| M8 × 30mm hex bolt | 4 | £2 | Hardware store |
| M8 nyloc nut | 10 | £2 | Hardware store |
| M8 washer | 20 | £2 | Hardware store |
| M2 × 6mm bolt | 10 | £2 | Amazon |
| PLA filament (white/grey) | 1 spool (1kg) | £15 | Amazon |
| **Total** | | **~£49** | |

---

## Appendix A: Sawppy Dimension Reference

| Sawppy Part | Dimensions (mm) | Our Equivalent |
|-------------|-----------------|----------------|
| Rocker | 35 × 98 × 83 | Rocker hub + front tube |
| Bogie-Body | 20 × 57 × 40 | Bogie pivot + front tube |
| Bogie-Wheels | 38 × 90 × 49 | Bogie pivot + rear tube |
| Steering Knuckle | 97 × 40 × 110 | Steering bracket |
| Fixed Knuckle | 100 × 40 × 74 | Fixed wheel mount |
| DiffBrace | 240 × 90 × 6 | Diff bar rod (300mm) |
| DiffEnd | 55 × 60 × 19 | Diff bar adapter |
| Rod Support | 11 × 22 × 30 | Tube socket in connector |

## Appendix B: Scale Comparison

| Dimension | Full Scale | Phase 1 (0.4x) | Sawppy | Papaya Mini |
|-----------|-----------|-----------------|--------|-------------|
| Wheel diameter | 215mm | 86mm | 124mm | ~80mm |
| Track width | 650mm | 260mm | ~280mm | ~200mm |
| Rocker arm | 450mm | 180mm | 98mm | ~120mm |
| Bogie arm | 300mm | 180mm | 147mm | ~100mm |
| Diff bar span | 500mm | 200mm | 240mm | ~180mm |
| Motor | Chihai 37mm | N20 12mm | LX-16A servo | N20 |
| Steering | MG996R | SG90 | LX-16A servo | SG90 |
| Bearings | 608ZZ | 608ZZ | 608ZZ | M3 bolt pivot |
