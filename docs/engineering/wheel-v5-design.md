# Wheel V5 Design — Curiosity-Inspired Adaptation

**Document**: Wheel Component Design Specification
**Version**: 5.0
**Date**: 2026-03-26
**Status**: Active — replaces V3 (single-piece) and V4 (scripted two-piece)
**Reference Model**: `cad/reference-wheels/curiosity-mars-rover-wheel-1.snapshot.2/Curiosity Wheel v25.f3d`

---

## 1. Design Decision

We are adopting the downloaded Curiosity Mars Rover wheel CAD model (Curiosity Wheel v25, Fusion 360) as the **reference design** for our wheel system. This replaces the previous scripted approaches (V3 single-piece, V4 spiral-spoke hub).

**Why**: The Curiosity model has professional-quality curved S-spokes, authentic chevron grousers, rectangular lightening holes, and a proper hub/spoke/tread architecture that would take weeks to recreate parametrically. We will scale and adapt it rather than reinvent it.

### Version History

| Version | Approach | Status |
|---------|----------|--------|
| V1 | Simple cylinder + flat spokes | Superseded |
| V2 | Improved spokes, single piece | Superseded |
| V3 | Revolve profile + arc spokes, single piece | Superseded |
| V4 | Two-piece (scripted hub + tire bands + beadlock) | Superseded by V5 |
| **V5** | **Curiosity reference model, scaled + adapted** | **Active** |

---

## 2. Curiosity Wheel — Original Analysis

### 2.1 Model Structure (from IGES import)

| Component | Original Size | Count | Notes |
|-----------|--------------|-------|-------|
| **Tread ring** | 448mm OD x 404mm wide | 1 (3 bodies) | Chevron grousers + lightening holes |
| **Hub disc** | 175mm OD x 30mm thick | 1 | Central bore + radial ribs + bolt bosses |
| **Spokes** | 218 x 138 x 103mm | 6 | Curved S-profile titanium |
| **Screws** | M5 SHCS, 16mm long | 30 | 5 per spoke (2 at tread, 2 at hub, 1 mid) |

### 2.2 Key Radii (from model)

| Feature | Radius | Diameter |
|---------|--------|----------|
| Tread OD | 224.0mm | 448.0mm |
| Tread ID (inner skin) | 210.4mm | 420.8mm |
| Hub OD | 87.5mm | 175.0mm |
| Hub bore | 26.0mm | 52.0mm |
| Spoke inner attach | 67.5mm | 135.0mm |
| Spoke outer attach | ~204mm | ~408mm |

### 2.3 Tread Geometry

The tread ring (Body1: 797 faces, 2335 edges) has:
- **Chevron grousers**: V-shaped treads on the outer surface, angled for directional grip
- **Rectangular lightening holes**: Cut through the cylindrical skin between grousers, arranged in circumferential rows — provide compliance (flex) and weight reduction
- **Structural ribs**: Thickened bands between hole rows maintain hoop strength
- **Two small marker bodies**: Body2 (3.0mm) and Body3 (3.0mm) — likely JPL Morse code tread marks (real Curiosity stamps "JPL" in its tracks)

---

## 3. Curiosity Tread Material Analysis — NO RUBBER

### 3.1 Real Curiosity Wheel Construction

**The real Curiosity rover wheels contain ZERO rubber.** The entire wheel — tread, skin, and grousers — is machined from a single block of **7075-T7351 aluminium alloy**.

| Property | Curiosity Wheel |
|----------|----------------|
| **Tread material** | Machined aluminium (7075-T73) |
| **Skin thickness** | 0.75mm (thinnest machinable) |
| **Grouser height** | 7.5mm |
| **Grouser spacing** | 15 degrees apart (24 grousers) |
| **Spoke material** | Titanium (curved, springy) |
| **Hub material** | Aluminium |
| **Fasteners** | Stainless steel socket head cap screws |
| **Rubber/polymer** | **NONE** |

### 3.2 Why No Rubber on Mars?

1. **Temperature**: Mars surface ranges -140C to +30C. Rubber becomes brittle glass below -60C
2. **UV radiation**: No ozone layer on Mars — UV destroys rubber in weeks
3. **Vacuum outgassing**: Low atmospheric pressure (0.6 kPa) causes rubber to outgas volatiles
4. **Weight**: Rubber adds mass without benefit — Mars gravity is 38% of Earth
5. **Grip not needed**: On Mars regolith, the thin aluminium skin *floats* on loose sand while grousers dig in for traction. Rubber friction is irrelevant on granular terrain

### 3.3 Curiosity Wheel Damage History

Despite the all-metal construction, Curiosity's wheels suffered significant damage:
- **Within 1 year**: Visible punctures and tears in the 0.75mm skin
- **Cause**: Sharp Mars rocks concentrated stress on the thin skin between grousers
- **Lesson for Perseverance**: Thicker skin (1.0mm), narrower but taller (52.5cm x 20cm), redesigned tread to reduce stress concentrations

### 3.4 Implications for Our Rover

Our rover operates on **Earth** (garden/park), not Mars. Key differences:

| Factor | Mars (Curiosity) | Earth (Our Rover) |
|--------|------------------|-------------------|
| Surface | Regolith, sharp rocks | Grass, paths, gravel, mud |
| Gravity | 3.7 m/s2 | 9.8 m/s2 |
| Temperature | -140 to +30C | -5 to +35C (UK) |
| Traction need | Low (light rover, loose soil) | High (heavier rover, varied surfaces) |
| Material | Machined aluminium | 3D printed PLA |
| Wheel count | 6 (rocker-bogie) | 6 (rocker-bogie) |

**Conclusion**: We **do** benefit from a traction surface on Earth. Options:

1. **PLA grousers only** (simplest) — Curiosity-style chevrons printed integral with tread
2. **Rubber O-ring bands** in grooves (our existing plan) — adds grip on hard surfaces
3. **Rubber spray coating** (Plasti Dip) — thin rubber layer on tread surface
4. **Interchangeable tire bands** (V4 concept) — snap-on PLA bands with different tread patterns

**Recommendation**: Option 1 (integral PLA chevron grousers) as the primary design, matching the Curiosity aesthetic. If traction is insufficient on smooth surfaces during testing, add rubber O-ring bands in circumferential grooves.

---

## 4. V5 Adaptation Plan

### 4.1 Scaling

| Dimension | Curiosity (original) | V5 (0.4 scale) | Method |
|-----------|---------------------|-----------------|--------|
| Tread OD | 448mm | **80mm** | Scale 0.1786x |
| Tread width | 404mm | **40mm** | Scale 0.099x (adjusted to match project spec) |
| Hub OD | 175mm | **31mm** | Scale 0.1786x |
| Hub bore | 52mm | **8.1mm** (N20 D-shaft clearance) | Adapted for motor |
| Skin thickness | 0.75mm | **2.0mm** (PLA minimum) | DFM adapted |
| Grouser height | 7.5mm | **3.0mm** | Project spec (EA-08) |

**Note**: Width does not scale proportionally — Curiosity's wheel is nearly as wide as it is tall. Our rover needs 40mm width per EA-08 spec, giving a more conventional aspect ratio.

### 4.2 Structural Adaptations for PLA

The Curiosity wheel is machined aluminium + titanium. PLA printing requires:

| Feature | Curiosity | V5 PLA Adaptation |
|---------|-----------|-------------------|
| Spokes | Separate titanium, bolted | **Integral with hub** (single print) |
| Skin thickness | 0.75mm | **2.0mm minimum** (PLA wall requirement) |
| Lightening holes | Through-skin rectangular | **Decorative only** — optional, may weaken PLA |
| Grousers | Machined integral | **Printed integral** (same approach) |
| Hub-to-axle | Bolted flange | **D-shaft bore** (3.1mm) + M3 grub screw |
| Spoke-to-tread | 30x M5 bolts | **Printed integral** |
| Spoke count | 6 (titanium) | **6** (PLA, thicker cross-section) |

### 4.3 What We Keep from Curiosity

1. **S-curved spoke profile** — the iconic Curiosity look
2. **6 spokes** at 60-degree intervals
3. **Chevron grouser pattern** on tread surface
4. **Hub disc** with radial rib reinforcement between spokes
5. **Overall proportions** — hub-to-tread ratio, spoke curvature

### 4.4 What We Change

1. **Single piece**: Hub + spokes + tread ring printed as one PLA part (no bolted assembly)
2. **Motor bore**: Replace 52mm central bore with 8.1mm N20 D-shaft + boss
3. **Wall thickness**: All walls minimum 2.0mm for PLA strength
4. **No lightening holes**: Skin stays solid for PLA stiffness (optional cosmetic holes in Phase 2)
5. **Width**: 40mm (not 404mm scaled) — per project specification
6. **Beadlock option**: Retained from V4 if interchangeable tire bands are desired later
7. **Grub screw**: M3 radial set screw in hub boss to lock on D-shaft

### 4.5 Two Approaches Available

#### Approach A: Scale the Reference Model (Manual in Fusion 360)
1. Open `Curiosity Wheel v25.f3d` in Fusion 360
2. Combine spoke + hub + tread into single body
3. Scale to 0.1786x
4. Modify hub bore for N20 shaft
5. Adjust wall thicknesses
6. Export as STL

**Pros**: Fastest path, preserves all Curiosity detail
**Cons**: Non-parametric, manual editing, hard to version control

#### Approach B: Recreate in Script Using Curiosity as Reference
1. Write `rover_wheel_hub_v5.py` inspired by Curiosity geometry
2. Use measurements from reference model for spoke curves
3. Parametric — can be regenerated, version controlled, batch exported

**Pros**: Consistent with project workflow, parametric, reproducible
**Cons**: May not capture all Curiosity nuance, more development time

**Recommendation**: Approach A for initial prototype (get it printed quickly), then Approach B for the final production script if dimensional changes are needed.

---

## 5. Traction Strategy

### 5.1 Phase 1: Printed PLA Grousers (Curiosity-Style)

The primary tread pattern follows Curiosity's chevron design:
- 12-24 chevron grousers (scaled from Curiosity's 24)
- 3mm tall (per EA-08 spec)
- V-shaped for directional grip and self-cleaning
- Printed integral with tread ring

Expected performance:
- **Grass**: Good — grousers dig into soft surface
- **Gravel/paths**: Good — grousers grip irregularities
- **Smooth concrete**: Poor — PLA-on-concrete has low friction
- **Wet surfaces**: Poor — no rubber compliance

### 5.2 Phase 1 Enhancement: Rubber O-Ring Bands

If PLA traction is insufficient on smooth/wet surfaces:
- Machine 2-3 circumferential grooves in tread between grousers
- Fit standard rubber O-rings (e.g., 76mm ID x 3mm cross-section)
- O-rings provide rubber contact patch without full tire change
- Cost: ~$5 for a bag of O-rings

### 5.3 Phase 2: Interchangeable Tire Bands (Retained from V4)

The V4 tire band concept remains available for Phase 2:
- Hub has 70mm OD tire seat + beadlock ring mounting
- Snap-on PLA tire bands with different tread patterns (Mars, smooth, offroad, paddle)
- Allows seasonal tread changes

---

## 6. Bill of Materials — Wheel Assembly (V5)

### Per Wheel
| Item | Qty | Material | Notes |
|------|-----|----------|-------|
| Wheel (hub+spokes+tread) | 1 | PLA | Single print, Curiosity-inspired |
| M3 x 5mm grub screw | 1 | Steel | Locks wheel to D-shaft |

### Per Rover (6 wheels)
| Item | Qty | Notes |
|------|-----|-------|
| Wheels | 6 | ~15g PLA each, ~3hr print each |
| M3 grub screws | 6 | From Phase 1 hardware kit |
| Rubber O-rings (optional) | 12-18 | 76mm ID x 3mm, if needed for traction |

---

## 7. Print Specifications

| Parameter | Value |
|-----------|-------|
| **Orientation** | Hub face down (spokes print upward) |
| **Material** | PLA |
| **Layer height** | 0.2mm |
| **Infill** | 50% gyroid |
| **Perimeters** | 4 |
| **Supports** | Yes — for spoke overhangs |
| **Bed adhesion** | Brim (8mm) |
| **Estimated time** | ~3 hours per wheel |
| **Estimated weight** | ~15g per wheel |
| **Bed fit** | 80mm diameter — well within 225x145mm |

---

## 8. Interface Compatibility

The V5 wheel maintains all existing interfaces:

| Interface | Dimension | Mates With |
|-----------|-----------|------------|
| D-shaft bore | 3.1mm (0.1mm clearance on 3mm shaft) | N20 motor |
| Hub boss OD | ~12mm | Fixed wheel mount bore |
| Grub screw | M3, radial through hub boss | Locks on D-shaft flat |
| Wheel OD | 80mm | Ground contact, clearance envelope |
| Wheel width | 40mm | Fixed wheel mount width slot |

---

## 9. File Inventory

### Reference Model
| File | Size | Format |
|------|------|--------|
| `cad/reference-wheels/.../Curiosity Wheel v25.f3d` | 4.2MB | Fusion 360 native (parametric) |
| `cad/reference-wheels/.../Curiosity Wheel v25.iges` | 12.7MB | IGES (importable) |
| `cad/reference-wheels/.../Curiosity Wheel v25.obj` | 44.9MB | OBJ mesh |
| `cad/reference-wheels/.../Curiosity Wheel v25.sat` | 19.1MB | ACIS SAT |

### Previous Scripts (retained for reference / alternative)
| Script | Purpose | Status |
|--------|---------|--------|
| `rover_wheel_hub_v4.py` | Scripted spiral spoke hub | Available (V4) |
| `rover_tire_mars.py` | Mars chevron tire band | Available (V4 tire) |
| `rover_tire_smooth.py` | Smooth indoor tire band | Available (V4 tire) |
| `rover_tire_offroad.py` | Deep lug tire band | Available (V4 tire) |
| `rover_tire_paddle.py` | Paddle sand tire band | Available (V4 tire) |
| `rover_beadlock_ring.py` | Tire retention ring | Available (V4 accessory) |

### V5 Target
| File | Purpose | Status |
|------|---------|--------|
| `rover_wheel_v5.py` or manual F360 | Curiosity-adapted single-piece wheel | **To be created** |

---

## 10. Sources

- [NASA Mars 2020 Rover Wheels](https://mars.nasa.gov/mars2020/spacecraft/rover/wheels/)
- [NASA's Memory Wheels — USC Viterbi](https://illumin.usc.edu/nasas-memory-wheels/)
- [How NASA Reinvented The Wheel — Medium](https://medium.com/predict/how-nasa-reinvented-the-wheel-83bbc8f528ed)
- [Diagram of a Curiosity Wheel — Planetary Society](https://www.planetary.org/space-images/diagram-of-a-curiosity-wheel)
- [Metal Tires for Mars — Space.com](https://www.space.com/39305-metal-tires-for-mars-rovers.html)
- [What material are Curiosity's wheels? — Quora](https://www.quora.com/What-material-are-NASAs-Curiosity-rovers-wheels-made-of-Would-they-have-lasted-longer-if-they-were-mass-of-car-tyre-rubber)
- [Leo Rover Blog — Different Shades of Wheel](https://www.leorover.tech/post/different-shades-of-wheel)
