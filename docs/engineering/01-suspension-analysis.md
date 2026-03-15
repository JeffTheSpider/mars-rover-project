# Engineering Analysis 01: Rocker-Bogie Suspension Design

**Document**: EA-01
**Date**: 2026-03-15
**Purpose**: Define the rocker-bogie suspension geometry, calculate obstacle climbing capability, analyse stability limits, and specify structural requirements for all three build phases.

---

## 1. Rocker-Bogie Operating Principle

The rocker-bogie is a passive suspension that uses mechanical linkage geometry to keep all 6 wheels in ground contact without springs or powered articulation. It consists of:

- **Rocker**: A lever arm connecting the front wheel to the bogie assembly, pivoting on the body
- **Bogie**: A smaller lever arm connecting the middle and rear wheels
- **Differential bar**: A transverse bar linking left and right rockers, averaging their pitch angle so the body tilts at half the angle of either side

```
                   [Body Centre / Differential Pivot]
                        /              \
                       /                \
              [Rocker Pivot L]    [Rocker Pivot R]
              /           \       /           \
           W1(front)   [Bogie]  [Bogie]   W6(front)
                       /    \    /    \
                    W2(mid) W3  W4  W5(mid)
```

The differential bar ensures the body only experiences half the pitch angle that either side encounters, dramatically reducing body tilt over obstacles.

---

## 2. Geometry Design

### 2.1 Scaling from NASA Rovers

NASA's Curiosity rover dimensions (scaled ratios):

| Parameter | Curiosity (real) | Ratio to Wheelbase |
|-----------|-----------------|-------------------|
| Wheelbase (front-rear) | 2,800mm | 1.00 |
| Track width | 2,300mm | 0.82 |
| Wheel diameter | 500mm | 0.18 |
| Rocker arm length | ~1,400mm | 0.50 |
| Bogie arm length | ~900mm | 0.32 |
| Ground clearance | 660mm | 0.24 |
| Rocker:Bogie ratio | — | 1.56:1 |

### 2.2 Our Rover Geometry (Applying NASA Ratios)

Scaling to our 1100mm body length:

| Parameter | Calculated Value | Rounded/Adjusted | Notes |
|-----------|-----------------|-------------------|-------|
| Wheelbase (W1 to W3) | — | 900mm | Front wheel to rear wheel per side |
| Track width (wheel centre to centre) | 900 × 0.82 = 738mm | 700mm | Adjusted to fit 650mm body + wheel overhang |
| Wheel diameter | 900 × 0.18 = 162mm | 200mm | Rounded up for terrain capability |
| Rocker arm length (pivot to front wheel) | 900 × 0.50 = 450mm | 450mm | Front wheel to body pivot |
| Bogie arm length (total) | 900 × 0.32 = 288mm | 300mm | Bogie pivot to middle wheel + bogie pivot to rear wheel |
| Bogie front half | — | 150mm | Bogie pivot to middle wheel |
| Bogie rear half | — | 150mm | Bogie pivot to rear wheel |
| Ground clearance | 900 × 0.24 = 216mm | 150mm | Reduced — we don't need Mars-level clearance |
| Rocker:Bogie ratio | — | 1.50:1 | 450mm : 300mm |

### 2.3 Wheel Spacing

```
Side View (one side):

         [Body Pivot]
            |
    [Rocker Arm: 450mm]
   /                    \
  W1                [Bogie Pivot]
  |                  /         \
  |          [150mm]           [150mm]
  |            |                  |
  W1          W2                 W3

Wheel centres (horizontal):
  W1 ----[450mm]---- W2 ----[150mm]---- W3
                  (adjusted for angles)

Approximate ground-level spacing:
  W1 to W2: ~400mm
  W2 to W3: ~280mm
  W1 to W3 (wheelbase): ~680mm per side
```

### 2.4 Differential Bar

```
Front View:
                [Diff Bar Centre]
               /                 \
     [Left Rocker Pivot]  [Right Rocker Pivot]
              |                    |
        Left Rocker          Right Rocker

Diff bar length: ~500mm (centre to centre of rocker pivots)
Pivot type: Free rotation, sealed ball bearings
```

The differential bar transmits rotation from one rocker to the other through a central pivot. When the left side goes up, the right side compensates, and the body stays at the average angle.

**Differential bar angle range**: ±20 degrees from horizontal (sufficient for obstacles up to wheel diameter).

---

## 3. Obstacle Climbing Analysis

### 3.1 Theoretical Maximum

The theoretical maximum obstacle height for a rocker-bogie system is approximately **1.5× to 2× the wheel diameter** (source: NASA JPL, Wikipedia rocker-bogie article, multiple academic papers).

For our 200mm wheels: **Maximum theoretical obstacle = 300-400mm**.

However, this assumes:
- Sufficient motor torque to push the rover up
- Adequate traction (no wheel slip)
- Slow approach speed (quasi-static analysis)

### 3.2 Practical Climbing Calculation

**Step climbing analysis** (most common real-world obstacle):

For a wheel of radius r = 100mm approaching a step of height h:

```
The wheel contacts the step edge when:
  h ≤ r → wheel rolls over naturally
  h > r → wheel impacts step face

For h = r (100mm step with 100mm radius wheel):
  Contact angle θ = arccos((r-h)/r) = arccos(0) = 90°
  Required horizontal force = mg × tan(θ) → infinite at 90°

For h = 0.75r (75mm step):
  θ = arccos(0.25) = 75.5°
  Required force ratio = tan(75.5°) = 3.87 × weight on that wheel

For h = 0.5r (50mm step):
  θ = arccos(0.5) = 60°
  Required force ratio = tan(60°) = 1.73 × weight on that wheel
```

**Practical conclusion**: With 200mm wheels, the rover can reliably climb:
- **Kerbs up to 75mm** (standard UK dropped kerb: 15-25mm) — easily handled
- **Rough terrain steps up to 100mm** — requires good traction and torque
- **Maximum practical obstacle: ~150mm** (0.75× wheel diameter) — at torque limits

This is more than sufficient for Markeaton Park paths, grass, gravel, and standard pavement.

### 3.3 Climbing Sequence

```
Step 1: Front wheel (W1) contacts obstacle
         Rocker arm lifts W1 over obstacle
         Body tilts slightly forward
         W2, W3 maintain traction (push W1 up)

Step 2: Middle wheel (W2) contacts obstacle
         Bogie arm lifts W2
         W1 (now on top) and W3 push

Step 3: Rear wheel (W3) contacts obstacle
         W1 and W2 (both on top) pull W3 up
         Rocker geometry lifts W3

All transitions happen passively — no active suspension control needed.
```

---

## 4. Stability Analysis

### 4.1 Static Tilt Limits

```
Side tilt:
  Track width: 700mm (wheel centre to centre)
  CoG height (estimated): 300mm above ground

  Maximum static tilt angle before tipover:
  θ_max = arctan(track_width/2 / CoG_height)
  θ_max = arctan(350 / 300)
  θ_max = arctan(1.167)
  θ_max = 49.4°

Front/rear tilt:
  Wheelbase: 680mm
  CoG height: 300mm

  θ_max = arctan(340 / 300)
  θ_max = arctan(1.133)
  θ_max = 48.6°
```

**Result**: The rover can statically tilt to ~49° before tipping over. This provides a large safety margin — typical park slopes are 5-15°, maximum UK hillside slopes rarely exceed 30°.

### 4.2 Dynamic Considerations

At speed (3-5 km/h), dynamic forces add to tilt risk:

- **Centripetal force during turns**: At 5 km/h (1.39 m/s) with turning radius 1m:
  - a = v²/r = 1.93 m/s²
  - Effective tilt equivalent: arctan(1.93/9.81) = 11.1°
  - Remaining margin: 49.4° - 11.1° = 38.3° — still very safe

- **Terrain-induced tilt**: Differential bar halves the body tilt angle
  - If one side encounters a 200mm obstacle: body tilts ~8° (not the full 16°)

### 4.3 Safety Software Limits

Even though the physics allows 49°, we should implement software limits:

| Alert Level | Tilt Angle | Action |
|-------------|-----------|--------|
| Normal | 0-15° | Normal operation |
| Warning | 15-25° | Slow to half speed, alert on phone |
| Danger | 25-35° | Stop forward motion, alert with alarm |
| Critical | 35°+ | Full stop, engage brakes, send emergency notification |

---

## 5. Structural Requirements

### 5.1 Load Analysis

Worst case: all weight on one side during maximum tilt.

- Total rover weight (Phase 2): ~20 kg
- Maximum load on one rocker arm: ~15 kg (75% during tilt)
- Maximum load on one bogie arm: ~10 kg
- Maximum load per wheel: ~7 kg (when 3 wheels carry most weight)

Forces on rocker arm (bending):
```
  F = 15 kg × 9.81 m/s² = 147 N
  Arm length: 450mm
  Bending moment at pivot: M = F × L = 147 × 0.225 = 33.1 N·m
  (using half the arm length as effective lever)
```

### 5.2 Phase 1: 3D Printed (0.4 Scale)

At 0.4 scale, loads are dramatically reduced (weight ~2-3 kg):

| Parameter | Requirement |
|-----------|-------------|
| Material | PLA or PETG |
| Rocker arm cross-section | 15mm × 10mm minimum |
| Wall thickness | 2.4mm (6 perimeters at 0.4mm) |
| Infill | 40% gyroid or 30% cubic |
| Bogie arm cross-section | 12mm × 8mm minimum |
| Pivot holes | 5mm for M5 bolt + bearing |
| Print orientation | Flat (load along layer lines, not across) |

### 5.3 Phase 2: Full-Scale 3D Printed + Extrusion

At full scale with 20 kg total weight:

| Parameter | Requirement |
|-----------|-------------|
| Frame material | 2020 aluminium extrusion (V-slot or T-slot) |
| Rocker arms | 2020 extrusion with 3D printed end brackets |
| Bogie arms | 2020 extrusion with 3D printed end brackets |
| Connectors | PETG, 3mm walls, M3 heat-set inserts (Sawppy method) |
| Infill (connectors) | 60%+ for structural parts |
| Pivot bearings | 608ZZ (8mm bore, 22mm OD) — standard skateboard bearings |
| Differential bar | 2020 extrusion or 10mm steel rod |
| Bolt grade | M5 stainless steel (body), M3 (connectors) |

### 5.4 Phase 3: Metal

| Parameter | Requirement |
|-----------|-------------|
| Rocker arms | 6061 aluminium, 25mm × 15mm rectangular tube, 2mm wall |
| Bogie arms | 6061 aluminium, 20mm × 12mm rectangular tube, 2mm wall |
| Body frame | 2040 aluminium extrusion or welded box section |
| Pivots | Sealed ball bearings (6001-2RS, 12mm bore) |
| Differential bar | 12mm steel rod with universal joints |
| Fasteners | M5 stainless steel, nyloc nuts |
| Surface finish | Anodised aluminium or powder coated |

---

## 6. Bearing Selection

### 6.1 Pivot Points (6 total per rover)

| Pivot Location | Quantity | Recommended Bearing | Bore | OD | Load Rating |
|---------------|----------|-------------------|------|-----|-------------|
| Body-to-rocker (main) | 2 | 608ZZ (Ph2) / 6001-2RS (Ph3) | 8mm / 12mm | 22mm / 28mm | 3.4kN / 5.1kN |
| Rocker-to-bogie | 2 | 608ZZ (Ph2) / 6001-2RS (Ph3) | 8mm / 12mm | 22mm / 28mm | 3.4kN / 5.1kN |
| Differential bar centre | 1 | 608ZZ (Ph2) / 6001-2RS (Ph3) | 8mm / 12mm | 22mm / 28mm | 3.4kN / 5.1kN |
| Diff bar to rocker | 2 | 608ZZ (Ph2) / 6001-2RS (Ph3) | 8mm / 12mm | 22mm / 28mm | 3.4kN / 5.1kN |

608ZZ bearings are cheap (~$0.50 each), universally available, and rated at 3.4 kN static — far exceeding our maximum 147N load. They are the standard bearing used in skateboard wheels and by most open-source rover projects.

### 6.2 Wheel Bearings

Each wheel hub needs 2 bearings (supporting the wheel on its axle):

| Location | Bearing | Quantity | Notes |
|----------|---------|----------|-------|
| Wheel hub (inner) | 608ZZ | 6 | Same as pivot bearings for standardisation |
| Wheel hub (outer) | 608ZZ | 6 | |
| Total wheel bearings | 608ZZ | 12 | |

**Total 608ZZ bearings needed**: 7 (pivots) + 12 (wheels) = **19 bearings**
At ~$0.50 each = **~$10 total** for all bearings.

---

## 7. Known Failure Modes & Mitigations

| Failure Mode | Cause | Likelihood | Impact | Mitigation |
|-------------|-------|------------|--------|------------|
| 3D printed connector cracking | Layer delamination under load | Medium (Ph2) | Medium | PETG not PLA, print flat, 60%+ infill, heat-set inserts |
| Bearing seizure | Dirt/water ingress | Low | Low | Use ZZ (shielded) or 2RS (sealed) bearings |
| Differential bar binding | Misalignment, debris | Low | High | Clearance tolerances, periodic cleaning |
| Rocker arm bending | Overload (sitting on rover) | Low | High | "Do not sit" warning, 2020 extrusion resists bending |
| Bogie arm failure | Impact with large obstacle at speed | Medium | Medium | Slow speed + software obstacle detection |
| Pivot bolt loosening | Vibration | Medium | Low | Nyloc nuts, thread-lock compound |
| Extrusion joint loosening | Vibration | Medium | Low | Spring washers, periodic tightening schedule |

---

## 8. CAD Modelling Priorities

When starting in Fusion 360, model these components first:

1. **Wheel** — most constrained (must fit motor, bearing, tyre)
2. **Bogie arm** — simplest linkage piece
3. **Rocker arm** — longer, more complex
4. **Differential bar assembly** — central pivot mechanism
5. **Body mounting points** — where rockers attach to body frame
6. **Full suspension assembly** — verify articulation range

### Test in Simulation
- Apply 150N downward force on each rocker pivot → check stress in arms
- Articulate one side up 200mm → check differential bar angle
- Verify no collisions between wheel and body at maximum articulation
- Check ground clearance at all articulation positions

---

## 9. Summary of Key Dimensions

| Parameter | Phase 1 (0.4×) | Phase 2 (1.0×) | Phase 3 (1.0×) |
|-----------|----------------|----------------|----------------|
| Wheelbase (per side) | 360mm | 900mm | 900mm |
| Track width | 280mm | 700mm | 700mm |
| Wheel diameter | 80mm | 200mm | 200mm |
| Rocker arm | 180mm | 450mm | 450mm |
| Bogie arm | 120mm | 300mm | 300mm |
| Ground clearance | 60mm | 150mm | 150mm |
| Max obstacle | 60mm | 150mm | 150mm |
| Bearings | 3mm bore (Ph1) | 608ZZ (8mm) | 6001-2RS (12mm) |
| Arm material | PLA/PETG solid | 2020 extrusion | 6061 aluminium tube |

---

## 10. References

- [Rocker-Bogie — Wikipedia](https://en.wikipedia.org/wiki/Rocker-bogie)
- [JPL OSR Rocker-Bogie Documentation](https://open-source-rover.readthedocs.io/en/latest/mechanical/rocker_bogie/)
- [Design of Rocker-Bogie Mechanism — IJISRT](https://ijisrt.com/wp-content/uploads/2017/05/Design-of-Rocker-Bogie-Mechanism-1.pdf)
- [IOSR Design and Optimization of a Mars Rover's Rocker-Bogie](https://www.iosrjournals.org/iosr-jmce/papers/vol14-issue5/Version-3/L1405037479.pdf)
- [Sawppy Rover — GitHub](https://github.com/Roger-random/Sawppy_Rover)
- [Printables — RC Rocker-Bogie Chassis](https://www.printables.com/model/164147-rc-rocker-bogie-chassis-mini-martian-rover)

---

*Document EA-01 v1.0 — 2026-03-15*
