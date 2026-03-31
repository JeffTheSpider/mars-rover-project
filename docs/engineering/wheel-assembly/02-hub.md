# WHL-02: Hub (Central Disc)

**Part**: Curiosity V5 Hub
**Source**: GrabCAD "Curiosity Wheel v25" — modified baseline
**Baseline File**: `cad/reference-wheels/CuriosityWheelV5_Approved_Baseline.f3d`
**Component .f3d**: `cad/reference-wheels/components/Hub.f3d`
**Component STL**: `cad/reference-wheels/components/Hub_1_fullscale.stl`
**Status**: Approved 2026-03-27 (3 modifications applied — see Section 7)

---

## 1. Description

The hub is the central load-bearing disc that connects the wheel to the drive axle. It transfers torque from the motor/axle to the spokes, which in turn drive the tread ring. The hub also provides the mounting interface to the rover's suspension structure via the axle bore and bolt pattern.

On the real Curiosity rover, the hub is machined from aluminium with reinforcing ribs, bolt bosses for spoke attachment, and a central bore for the drive actuator spline (Ref-1). Our model reproduces the external geometry faithfully from the GrabCAD source.

## 2. Dimensions

### Full Scale (1.0x)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Outer diameter | 175.0 mm | Hub disc outer edge |
| Thickness | 30.0 mm | Axial thickness of disc |
| Central bore | 52.0 mm | Through-bore for axle |
| Z position | +48.8 to +78.8 mm | Offset to spoke side of wheel |
| BRep faces | 1,004 | High detail — ribs, bosses, fillets |
| BRep edges | 2,285 | — |

### Phase 1 Scale (0.4x)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Outer diameter | 70.0 mm | Fits CTC Bizer bed easily |
| Thickness | 12.0 mm | — |
| Central bore | 20.8 mm | 0.4x of 52mm |

## 3. Geometry Features

### 3.1 Central Bore
- 52.0 mm diameter through-bore (full scale)
- On real rover: accommodates drive actuator spline shaft
- On our rover: will need adaptation for 608ZZ bearing + 8mm axle interface (see DD-01)

### 3.2 Reinforcing Ribs
- Complex web pattern radiating from bore to outer edge
- 12 primary ribs visible on the front face
- Provides stiffness while minimising weight
- Includes raised bosses at spoke attachment points

### 3.3 Bolt Holes (Corrected)
- **6x 6.0 mm diameter** through-holes for spoke attachment
- Arranged on **73.0 mm BCD** (bolt circle diameter) at **60-degree intervals**
- Positions: 0, 60, 120, 180, 240, 300 degrees
- Original model had one hole misplaced at 20 degrees — **corrected** (see Section 7)

### 3.4 Decorative Rivet Details
- 178x 0.5 mm radius (1.0 mm diameter) cylindrical features across hub face
- Simulate bolt/rivet heads on the real machined hub
- At 0.4x scale these become 0.4 mm — below FDM resolution, will not print

### 3.5 Decorative Screw Components
- 6x "92290A316 Stainless Steel Socket Head Screw" nested occurrences
- Positioned at the 6 bolt hole locations
- Visual reference only — not structural, not printable
- **Hidden in assembly view** (non-printable hardware)

## 4. Interfaces

### 4.1 Spoke-to-Hub (see WHL-04 Section 3.2)
- **Type (real rover)**: Bolted — 2x M5 SHCS per spoke through spoke root into hub boss (Ref-2)
- **Type (our model)**: Embedded overlap — spoke roots extend 14.0 mm into hub disc
- **Overlap zone**: r = 73.5 mm (spoke inner reach) to r = 87.5 mm (hub outer edge)
- **Screw positions**: r = 80.3 mm from wheel centre (at hub boss locations)
- **Bolt holes**: 6x 6.0 mm on 73.0 mm BCD (one per spoke root)

### 4.2 Axle Interface
- Central bore: 52.0 mm (full scale) / 20.8 mm (0.4x)
- On real rover: splined connection to drive actuator
- On our rover (Phase 1): 608ZZ bearing (22mm OD, 8mm ID) + 8mm axle stub
- **Adaptation required**: The 20.8 mm bore at 0.4x is close to the 22 mm 608ZZ OD — may need a printed adapter sleeve or bore modification

### 4.3 Rover Structure Interface
- Via 4x M3 bolt pattern on wheel connectors (see bolt-on-wheel-mounting-design.md)
- 20 mm BCD, button head bolts, heat-set inserts in connector
- This interface is on the **connector side**, not directly on the hub

## 5. Hub Position Within Wheel

The hub is **not centred axially** within the tread ring:
- Tread Z range: -202.0 to +202.0 mm (404 mm wide)
- Hub Z range: +48.8 to +78.8 mm
- Hub is offset **78.8 mm from tread centreline** toward one face
- This is correct to the original Curiosity design — the hub sits on one side, with spokes curving across to the tread

## 6. Print Feasibility (Phase 1 — 0.4x PLA)

### 6.1 Bed Fit
At 0.4x (70mm OD x 12mm thick), the hub **easily fits** the CTC Bizer bed.

### 6.2 Print Orientation
- Print flat (face down) for best surface quality on the visible face
- 12 mm height — fast print, ~30 minutes

### 6.3 Structural Concerns
- Reinforcing ribs at 0.4x become very thin — may need wall thickness increase
- Central bore needs post-processing if used for bearing seat
- 6x bolt holes at 0.4x become 2.4 mm — printable on FDM
- Decorative rivet details (0.4 mm) will not print — cosmetic loss only

## 7. Modifications from Original GrabCAD Model

Three modifications were applied to create the approved baseline (2026-03-27):

| ID | Modification | Method | Rationale |
|----|-------------|--------|-----------|
| WHL-02-M1 | **Hole3 shrunk to 0.01mm** | Diameter parameter change | 3x 2.5mm alignment/dowel pin holes at 40mm radius, 120 deg spacing. Not needed for our build. Cannot suppress — downstream fillets depend on edges. |
| WHL-02-M2 | **Hole1 shrunk to 0.01mm + new cut at 0/60/120/180/240/300 deg** | Shrink original + extrude cut at end of timeline | Original had 6x 6mm holes with one misplaced at 20 deg instead of 0 deg. Downstream cross-component features (Spoke Combine3, Fillets 1-9) prevented moving the original. Ghost edges preserved for all dependencies. |
| WHL-02-M3 | **Hole2 shrunk to 0.01mm** | Diameter parameter change | 2x 2.5mm holes at top/bottom (90/270 deg) of hub. Not needed. |
| WHL-02-M4 | **Screw:5 moved from 20 deg to 0 deg** | Transform change + Rigid 6 joint suppressed | Decorative screw component was at old wrong hole position. Joint suppressed to prevent recompute snap-back. |

**Key constraint**: Features cannot be suppressed or moved mid-timeline because Spoke and Tread components have Combine and Fillet features that reference Hub body edges. The "shrink to 0.01mm" approach preserves all edge topology while making features invisible.

## 8. References

| ID | Source | Content |
|----|--------|---------|
| Ref-1 | [NASA "Reinventing the Wheel"](https://www3.nasa.gov/specials/wheels/) | Hub-to-actuator interface |
| Ref-2 | GrabCAD Curiosity Wheel v25 model | 2x SHCS per spoke at hub end, boss geometry |
| Ref-3 | `docs/engineering/bolt-on-wheel-mounting-design.md` | Our wheel-to-connector bolt pattern design |
