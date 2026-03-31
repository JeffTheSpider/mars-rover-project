# WHL-03: Spoke (Flexure)

**Part**: Curiosity V5 Spoke (x6 identical)
**Source**: GrabCAD "Curiosity Wheel v25" — unmodified
**Baseline File**: `cad/reference-wheels/CuriosityWheelV5_Approved_Baseline.f3d`
**Component .f3d**: `cad/reference-wheels/components/Spoke.f3d`
**Component STL**: `cad/reference-wheels/components/Spoke_1_fullscale.stl`
**Status**: Approved 2026-03-27

---

## 1. Description

Each spoke is a curved S-profile flexure that connects the central hub to the outer tread ring. Six identical spokes are arranged at 60-degree intervals around the wheel, transferring torque from the hub to the tread while providing radial compliance (shock absorption).

On the real Curiosity/Perseverance rover, the spokes are machined from titanium — a material chosen specifically for its high fatigue life and spring-like resilience (Ref-1). Each spoke acts as a leaf spring: stiff laterally (supporting the rover's weight) but compliant radially (absorbing impacts from rocks). NASA describes the spokes as "optimized to be as soft as possible while maintaining structural integrity" (Ref-2).

The curved S-profile means the spoke bends twice in two directions — first transitioning from the hub face plane to the radial direction, then from the radial direction to the circumferential direction near the tread (Ref-3). This compound curvature is what gives the Curiosity wheel its distinctive appearance.

## 2. Dimensions

### Full Scale (1.0x)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Bounding box | 218.0 x 137.5 x 102.5 mm | Per spoke |
| Radial extent | 73.5 to 224.0 mm | From hub root to tread tip |
| Span length | 150.5 mm | Radial distance hub-to-tread |
| Z extent | 46.8 to 81.8 mm | Axial range (35mm) |
| BRep faces | 127 | Per spoke |
| BRep edges | 288 | Per spoke |

### Phase 1 Scale (0.4x)

| Parameter | Value |
|-----------|-------|
| Bounding box | 87.2 x 55.0 x 41.0 mm |
| Radial extent | 29.4 to 89.6 mm |
| Span length | 60.2 mm |
| Z extent | 18.7 to 32.7 mm |

## 3. Geometry Features

### 3.1 Cross-Section
- Flat rectangular profile (leaf-spring shape), not round or I-beam
- Oriented for radial flexibility and lateral stiffness
- On real rover: thin titanium section (~2-3mm thick) with high fatigue resistance
- On our PLA model: the cross-section is cosmetically correct but **structurally rigid** — PLA does not flex like titanium

### 3.2 S-Curve Profile
- Compound curve from hub face → radial → circumferential
- 8 Z-normal planar faces define the top/bottom surfaces at various heights:
  - Hub end: Z = 46.8 to 50.8 mm
  - Mid-span: Z = 51.8 to 62.8 mm
  - Tread end: Z = 66.8 mm
- The spoke transitions through ~20 mm of Z height across its 150.5 mm radial span

### 3.3 Attachment Flanges
Each spoke has widened flanges at both ends for bolted attachment:

**Hub end (inner):**
- 2x socket head cap screw positions at r = 80.3 mm from wheel centre
- Flange bears against hub disc boss surface
- Spoke root overlaps hub disc by 14.0 mm (r = 73.5 to 87.5 mm)

**Tread end (outer):**
- 2x socket head cap screw positions at r = 227-229 mm from wheel centre
- Flange bears against tread inner bore/stiffening ring
- Spoke tip overlaps tread wall by 13.7 mm (r = 210.4 to 224.0 mm)

### 3.4 Hardware
- 4x "92290A316 Stainless Steel Socket Head Screw" nested occurrences per spoke
- 2 at hub end (r = 80.3 mm), 2 at tread end (r = 227-229 mm)
- **These are visual reference only** — decorative, not printable

## 4. Arrangement

- **Quantity**: 6 identical spokes per wheel
- **Angular spacing**: 60 degrees
- **Rotation**: Each spoke is rotated about the Z axis from the Spoke:1 base position
  - Spoke:1 = 0 deg, Spoke:2 = 60 deg, Spoke:3 = 120 deg
  - Spoke:4 = 180 deg, Spoke:5 = 240 deg, Spoke:6 = 300 deg
- **Z offset**: All spokes at Z = +78.8 mm (same as hub), offset to one side of the tread
- **Chirality**: All spokes curve in the same rotational direction (not alternating)

## 5. Interfaces

### 5.1 Spoke-to-Hub (see WHL-04 Section 3.2)
- **Real rover**: Bolted — 2x M5 SHCS per spoke into hub boss (Ref-4)
- **Our model**: 14.0 mm embedded overlap into hub disc
- Spoke root inner radius (73.5 mm) is less than hub outer radius (87.5 mm)

### 5.2 Spoke-to-Tread (see WHL-04 Section 3.1)
- **Real rover**: Bolted — 2x M5 SHCS per spoke into tread stiffening ring (Ref-4)
- **Our model**: 13.7 mm embedded overlap into tread wall
- Spoke tip outer radius (224.0 mm) is greater than tread inner radius (210.4 mm)

### 5.3 Spoke-to-Spoke
- No direct spoke-to-spoke interface
- 60-degree spacing ensures no physical contact between adjacent spokes
- Minimum circumferential gap between adjacent spoke tips: ~80 mm (full scale)

## 6. Structural Behaviour

### 6.1 Real Rover (Titanium)
- Spokes act as compliant springs — radial deflection absorbs impacts (Ref-2)
- Designed for >10,000 load cycles without fatigue failure
- Each spoke carries ~1/6 of the wheel's ground contact load
- Compliance is critical: NASA deliberately made spokes "as soft as possible" to reduce dynamic loads on the rover body

### 6.2 Phase 1 PLA Model
- **PLA spokes are rigid** — no meaningful flex under rover loads (~200g per wheel)
- Compliance must come from elsewhere (suspension geometry, rubber O-rings on tread)
- Spoke strength is not a concern at Phase 1 scale/weight
- Decorative function is primary — the S-curve profile looks correct

## 7. Print Feasibility (Phase 1 — 0.4x PLA)

### 7.1 Bed Fit
At 0.4x (87 x 55 x 41 mm), each spoke **fits the CTC Bizer bed** easily.

### 7.2 Print Orientation
- **Best**: Flat on the widest face, supports for the S-curve overhang
- **Alternative**: Standing on hub-end flange
- Requires supports in both orientations due to the compound curve

### 7.3 Structural Concerns
- Thin cross-section at 0.4x may be fragile
- Consider printing at 100% infill for structural parts
- Attachment flanges need sufficient area for bonding to hub/tread
- **Print 1-2 spares** — most likely part to break during assembly

### 7.4 Assembly Challenge
The biggest challenge is attaching spokes to tread and hub:
- No visible slots, channels, or alignment features on the tread inner surface
- No alignment features on the hub face
- See WHL-04 for assembly feasibility analysis and recommendations

## 8. References

| ID | Source | Content |
|----|--------|---------|
| Ref-1 | [Mars Rovers Studio: Designing the Spokes](https://buymarsrovers.com/designing-the-spokes-of-the-wheels-of-the-perseverance-mars-rover-replica.html) | Titanium spoke bending, material choice |
| Ref-2 | [NASA 3D-DIC Paper (IEEE 2023)](https://ntrs.nasa.gov/api/citations/20220015213) | "Optimized to be as soft as possible" — flexure characterisation |
| Ref-3 | [Mars Rovers Studio: Building and Testing](https://buymarsrovers.com/building-and-testing-the-wheel-skeleton-of-the-mars-perseverance-rover-replica.html) | S-curve spoke geometry and assembly |
| Ref-4 | GrabCAD Curiosity Wheel v25 model | 4x SHCS per spoke (2 hub, 2 tread) at measured positions |
| Ref-5 | [NASA "Reinventing the Wheel"](https://www3.nasa.gov/specials/wheels/) | Spoke compliance design philosophy |
