# WHL-01: Tread (Outer Tire Ring)

**Part**: Curiosity V5 Tread
**Source**: GrabCAD "Curiosity Wheel v25" — modified baseline
**Baseline File**: `cad/reference-wheels/CuriosityWheelV5_Approved_Baseline.f3d`
**Component .f3d**: `cad/reference-wheels/components/Tread.f3d`
**Component STL**: `cad/reference-wheels/components/Tread_1_fullscale.stl`
**Status**: Approved 2026-03-27

---

## 1. Description

The tread is the outermost structural ring of the wheel. It is a single cylindrical drum with chevron-pattern grousers on the outer surface, directly inspired by the NASA/JPL Curiosity Mars rover wheel (Ref-1). The chevrons provide traction on loose terrain and self-cleaning properties.

On the real Curiosity rover, the tread is machined from a single billet of 7075-T7351 aluminium and includes the outer skin, chevron grousers, and an internal stiffening ring approximately one-third from the outer edge (Ref-2, Ref-3). The stiffening ring is the primary structural element — it carries the spoke attachment loads and prevents the thin skin from buckling.

The tread carries all ground contact loads and transmits drive torque from the spokes to the terrain surface.

## 2. Dimensions

### Full Scale (1.0x)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Outer diameter | 500.0 mm | Tip of chevron grousers |
| Inner diameter | 420.8 mm | Smooth inner bore surface |
| Wall thickness | 39.6 mm | Skin + grouser depth |
| Width (axial) | 404.0 mm | Full axial extent |
| BRep faces | 791 | — |
| BRep edges | 2,380 | — |

### Phase 1 Scale (0.4x)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Outer diameter | 200.0 mm | — |
| Inner diameter | 168.3 mm | — |
| Wall thickness | 15.8 mm | — |
| Width (axial) | 161.6 mm | Exceeds CTC Bizer Z (150mm) |

## 3. Geometry Features

### 3.1 Chevron Grousers
- V-shaped tread pattern on outer surface
- Oriented to shed debris when rotating forward
- Full-scale grouser depth: ~15-20 mm (Ref-4)
- On real Curiosity: grousers also encode "JPL" in Morse code — our model does not replicate this

### 3.2 Inner Bore
- Smooth cylindrical surface at r = 210.4 mm (full scale)
- This is the **spoke attachment zone** — spoke tips bear against this surface
- Two narrow cylindrical faces at axial ends (Z = +/-198 to +/-202 mm) — the edge rims

### 3.3 Internal Stiffening Ring
- Located approximately one-third from the outer edge of the tread (Ref-2)
- Primary spoke attachment structure on the real rover
- Spokes are bolted through to this ring with 2x SHCS per spoke (Ref-5)
- In our CAD model, this feature is simplified — the spoke tips embed 13.7 mm into the tread wall

### 3.4 Minor Bodies
The Tread component contains 6 additional small bodies (Body40, Body69, Body84-87):
- Dimensions: 3-28 mm range
- Located near the outer rim edge
- Purpose: Cosmetic/structural details from original GrabCAD model
- **Print recommendation**: Exclude from STL export; too small for FDM at any scale

## 4. Interfaces

### 4.1 Spoke-to-Tread (see WHL-04 Section 3.1)
- **Type (real rover)**: Bolted — 2x M5 SHCS per spoke through spoke flange into stiffening ring (Ref-5, Ref-6)
- **Type (our model)**: Embedded overlap — spoke tips extend 13.7 mm into tread wall
- **Overlap zone**: r = 210.4 mm (inner bore) to r = 224.0 mm (spoke tip extent)
- **Screw positions**: r = 227-229 mm from wheel centre (inside tread wall material)
- **Angular positions**: Every 60 degrees (6 spokes)

### 4.2 Ground Interface
- Direct ground contact via chevron grousers
- Real rover: Aluminium with machined cleats (Ref-1)
- Phase 1: PLA — consider rubber O-ring traction bands per EA-11

## 5. Print Feasibility (Phase 1 — 0.4x PLA)

### 5.1 Bed Fit
At 0.4x scale (200mm OD x 162mm wide), the tread **does not fit the CTC Bizer bed** (225 x 145 x 150 mm):
- Standing on edge: 200mm width exceeds 150mm Z height
- Lying flat: 200mm diameter exceeds 145mm Y bed dimension

**Options**:
1. Print as 2 or 4 axial segments, bond with CA glue
2. Scale to 0.3x (150mm OD x 121mm wide) — fits on bed standing up
3. Print as part of single-piece wheel (see WHL-04 Section 5)

### 5.2 Structural Concerns
- Thin chevron grousers may not resolve at 0.4x on FDM
- Wall thickness (15.8 mm at 0.4x) is adequate for PLA structural loads
- Inner bore must be smooth for spoke interface (if printed separately)

## 6. References

| ID | Source | Content |
|----|--------|---------|
| Ref-1 | [NASA "Reinventing the Wheel"](https://www3.nasa.gov/specials/wheels/) | Official Curiosity wheel anatomy |
| Ref-2 | [Planetary Society: Diagram of a Curiosity Wheel](https://www.planetary.org/space-images/diagram-of-a-curiosity-wheel) | Cross-section showing stiffening ring |
| Ref-3 | [NASA LLIS 22401: Premature Wear of MSL Wheels](https://llis.nasa.gov/lesson/22401) | Wheel failure modes and structural analysis |
| Ref-4 | [Emily Lakdawalla: Curiosity Wheel Damage](https://www.planetary.org/articles/08190630-curiosity-wheel-damage) | Grouser geometry and damage patterns |
| Ref-5 | GrabCAD Curiosity Wheel v25 model | 2x SHCS per spoke at tread end |
| Ref-6 | [NASA 3D-DIC Paper (IEEE 2023)](https://ntrs.nasa.gov/api/citations/20220015213) | Flexure characterisation and attachment detail |
