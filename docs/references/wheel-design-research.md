# Mars Rover Wheel Design Research

**Date:** 2026-03-26
**Purpose:** Find open-source wheel designs to adapt rather than designing from scratch.
**Key decision:** Two-piece hub + interchangeable tire system with Mars rover aesthetics (spiral spokes, chevron grousers).

---

## Our Target Specs

- 80mm diameter, 32mm width (0.4 scale)
- N20 motor with 3mm D-shaft
- 4mm axle bore through knuckle
- Printable on CTC Bizer (225×145×150mm, PLA)
- Two-piece: rigid hub/rim + swappable tire/tread

---

## Top Candidate Designs

### 1. jakkra Mars-Rover 2020 Wheel ★★★ (RECOMMENDED)
- **URL:** https://github.com/jakkra/Mars-Rover (CAD/rover_2020_wheel_flex.f3d)
- **License:** MIT
- **Format:** Fusion 360 .f3d (directly editable!)
- **Design:** Two-piece (PLA hub + TPU outer tire), 6 curved spring-like spokes (Perseverance style)
- **Tread:** Chevron grousers
- **Dimensions:** ~125mm diameter (needs scaling to 80mm)
- **Hub:** Pololu 1081 adapter for JGA25-370 motor (4mm D-shaft) — needs redesign for 3mm N20
- **Adaptation:** MEDIUM — scale down, redesign hub bore for N20, convert outer tire from TPU to PLA+O-rings or beadlock
- **Why best:** Fusion 360 native, MIT license, two-piece, beautiful Perseverance aesthetics

### 2. Sawppy Rover Wheel ★★★
- **URL:** https://github.com/Roger-random/Sawppy_Rover
- **License:** MIT
- **Format:** Onshape + STL
- **Design:** One-piece, 6 curved spokes (Curiosity style), 48 curved grousers
- **Dimensions:** ~120mm diameter
- **Hub:** 8mm bore for steel drive shaft
- **Adaptation:** MEDIUM-HARD — one-piece (no separate tire), Onshape not Fusion 360, 8mm bore vs our 3mm
- **Key value:** Most community-tested rover wheel, excellent FDM-optimised spoke design

### 3. OpenPerseverance (JeanetteMueller) ★★☆
- **URL:** https://github.com/JeanetteMueller/OpenPerseverance
- **License:** CC0 (public domain — no restrictions!)
- **Format:** STL only (no parametric CAD)
- **Design:** FOUR-PIECE: Tire.stl + Wheel Rim.stl + WheelHolder.stl + WheelHolderCenter.stl
- **Tread:** Perseverance-accurate curved grousers (48 treads)
- **Dimensions:** ~150-200mm (needs significant scaling)
- **Adaptation:** HARD — STL only, large scale, different motor

### 4. 120x60mm Two-Piece Rover Wheel ★★☆
- **URL:** Found via STLFinder (original source TBD)
- **Format:** STL
- **Design:** Two-piece (outer wheel + inner hub via slot channels)
- **Hub:** 3mm shaft bore (matches N20 directly!)
- **Dimensions:** 120mm × 60mm
- **Adaptation:** EASY mechanically — already has 3mm bore, but aesthetics are plain (not Mars-like)

### 5. N20-Specific Wheels (Functional Reference)
- **O-Ring Wheels for N20:** https://www.printables.com/model/71090 (small ~25mm)
- **Big Wheels for N20:** https://www.printables.com/model/881194 (68mm, silicone hairbands)
- **Simple N20 Wheels:** https://www.printables.com/model/572952 (PLA hub + TPU tire)

---

## Tire Attachment Mechanisms

| Method | Description | Swap Ease | Strength | Best For |
|--------|-------------|-----------|----------|----------|
| **Beadlock ring** | Tire clamped between rim and ring with M2 screws | Easy (4-6 screws) | High | Our recommended approach |
| **Press-fit** | TPU tire stretches over hub | Moderate | Medium | TPU tires (Phase 1C) |
| **Lipped channel** | Tire sits in groove, lips prevent lateral migration | Moderate | Good | Simple single-material |
| **Snap clips** | Integral snap features on rim | Quick | Lower | Rapid testing |
| **O-ring grooves** | Circumferential grooves accept rubber O-rings | Easiest | Low | Hard surface only |
| **Screw-through** | Bolts through rim and tire bead | Slow | Highest | Competition rovers |

**Recommended for us:** Simplified beadlock (4× M2 screws) — easy to swap, secure, works with PLA or TPU tires.

---

## Interchangeable Tire Tread Patterns

| Pattern | Terrain | Description |
|---------|---------|-------------|
| **Mars Chevron** | Garden soil, gravel, loose substrate | Angled V-pattern grousers (Curiosity/Perseverance style) |
| **Deep Lugs** | Mud, wet grass | Widely-spaced tall blocks, self-cleaning gaps |
| **Paddle** | Sand, snow, loose substrate | Full-width perpendicular scoops |
| **Smooth/Slick** | Indoor, hard floor, pavement | No tread, maximum contact patch |
| **All-Terrain Hybrid** | Mixed conditions | Combination chevrons + lateral channels |
| **Hex Lattice** | All-terrain (TPU only) | Honeycomb structure acts as suspension + tread |

---

## Parametric Wheel Generators

| Project | URL | License | Notes |
|---------|-----|---------|-------|
| Highly Configurable Wheel | https://github.com/alexfranke/Highly-Configurable-Wheel | Permissive | OpenSCAD, 46 params, 13 tread patterns |
| OpenScadWheelGenerator | https://github.com/UladzimirKapylou/OpenScadWheelGenerator | MIT | Two-piece hub+tire generation |
| openWheel | https://github.com/sarinkhan/openWheel | GPL-3.0 | Wheels, tweels, tires, tracks |

---

## TPU on CTC Bizer — Feasibility

The CTC Bizer has direct-drive MK8 extruders which CAN handle TPU with modification:
- **Required:** Filament guide insert (Printables #18671 or Thingiverse #1524455)
- **Settings:** 225-230°C, 40-60°C bed, 20-40mm/s speed, 1-2mm retraction
- **Material:** Shore 95A recommended (easier than softer grades)
- **Priority:** Get PLA working first, then try TPU after calibration

---

## Recommended Approach

1. **Import jakkra `rover_2020_wheel_flex.f3d`** into Fusion 360 as reference
2. **Adapt the hub:** Scale to 80mm, redesign bore for 3mm N20 D-shaft, keep spiral spoke aesthetic
3. **Redesign retention:** Add beadlock-style rim groove with M2 screw retention ring
4. **Create tire set:** 3-4 interchangeable PLA tread bands (Mars chevron, lugs, paddle, smooth)
5. **Phase 1C:** Try TPU tires once CTC Bizer is calibrated with PLA

---

## Key Sources

- jakkra Mars-Rover: https://github.com/jakkra/Mars-Rover
- Sawppy Rover: https://github.com/Roger-random/Sawppy_Rover
- Sawppy Wheel Blog: https://newscrewdriver.com/2018/05/10/sawppy-feet-1-0-rover-wheel-design-for-3d-printing/
- OpenPerseverance: https://github.com/JeanetteMueller/OpenPerseverance
- Highly Configurable Wheel: https://github.com/alexfranke/Highly-Configurable-Wheel
- CTC Bizer TPU Guide: https://www.thingiverse.com/thing:1524455
- Beadlock Reference: https://www.thingiverse.com/thing:2950547
- Palmiga OpenRC Wheels: https://www.thingiverse.com/thing:526969
- NASA Perseverance Wheels: https://mars.nasa.gov/mars2020/spacecraft/rover/wheels/
