# Bolt-On Wheel Mounting System — Design Decision Document

**Date**: 2026-03-26
**Status**: Implemented
**References**: EA-25 (Suspension Audit), EA-26 (Suspension Design), EA-30 (CAD Testing)

## 1. Problem Statement

The V5 Curiosity wheel (80mm OD, 6 spokes) and reference suspension (43 parts at 0.4x) are both ready, but the interface between them has three incompatibilities:

| Issue | Detail | Impact |
|-------|--------|--------|
| Reference motor shaft coupler OD | 20mm at 0.4x | 608ZZ bearing (22mm OD) won't fit inside it |
| Reference coupler bore | 2.5mm at 0.4x | N20 D-shaft is 3mm, doesn't fit |
| No bolt holes | Press-fit only design | No secure wheel-to-structure attachment |

## 2. Solution Overview

Replace reference couplers with our parametric wheel connectors, add matching bolt holes to V5 wheel hub, and introduce 608ZZ bearing + 8mm axle interface.

```
SUSPENSION ARM (8mm steel tube)
        |
[PARAMETRIC CONNECTOR] — tube socket + heat-set inserts
        |
[FIXED WHEEL MOUNT] — N20 motor clip (middle wheels)
    or [STEERING KNUCKLE] — N20 motor clip + steering pivot (front/rear)
        |
  [608ZZ BEARING] — decouples wheel loads from motor
        |
  [8mm AXLE STUB] — through bearing into wheel bore
        |
  [V5 WHEEL] — 4x M3 bolts on 20mm BCD
```

## 3. Design Decisions

### DD-01: 4x M3 on 20mm BCD (over 2x Linear 16mm)

**Decision**: Changed from 2x M3 heat-set inserts on 16mm linear spacing to 4x M3 on 20mm bolt circle diameter.

**Rationale**:
- **Equal load distribution**: 4 bolts at 90-degree intervals distribute clamping force evenly, preventing hub rocking
- **Self-centering**: BCD pattern naturally centers the wheel on the connector face
- **Torque resistance**: 4-point pattern resists rotational forces better than 2-point
- **Redundancy**: If one bolt loosens, 3 remaining bolts still hold (2-bolt pattern has no redundancy)

**Clearance analysis** (verified by alignment script):
- Inner clearance (bolt edge to bore edge): 4.3mm
- Outer clearance (bolt edge to hub face edge): 2.4mm
- Spoke root clearance: 0.4mm (acceptable — bolts pass between spokes, not through them)

**Trade-offs**:
- 4 bolts vs 2 bolts: More hardware (24 vs 12 bolts total), longer assembly time
- BCD vs linear: Slightly more complex manufacturing, but better engineering practice
- 20mm BCD vs larger: 20mm chosen as optimal fit — smaller risks spoke collision, larger risks hub edge breakout

### DD-02: Button Head Bolts (over Socket Cap Head)

**Decision**: Use M3x10 button head bolts (ISO 7380) instead of socket cap head (ISO 4762).

**Rationale**:
- Button head height: ~1.65mm (ISO) vs cap head: 3mm — lower profile
- Sits flush inside wheel hub cavity without interfering with spokes
- Sufficient strength for PLA-on-PLA clamping loads (~200g per wheel)
- Allen key socket for positive drive

### DD-03: 608ZZ Bearing at Each Wheel

**Decision**: Add 608ZZ bearing between wheel connector and wheel, transferring radial loads from motor shaft to structure.

**Rationale**:

| Factor | With 608ZZ | Without (direct D-shaft) |
|--------|-----------|----------------------|
| Radial load on motor | Near zero | ~210g per wheel |
| Shaft stiffness | 8mm axle (I=201mm^4) | 3mm D-shaft (I=3.98mm^4) = 50x less |
| Motor bearing life | Years | Months (constant side load) |
| Wheel wobble | None (precision bearing) | Increasing over time |
| Impact protection | Bearing absorbs hits | Motor gearbox takes damage |
| Cost | $0.50 each, $3 total | $0 |

**Trade-offs**:
- Requires 6 additional 608ZZ bearings (total project: 9 pivot + 6 wheel = 15)
- Original purchase was 12 bearings (9 allocated + 3 spare) — need 3 more
- Adds ~1mm to wheel-to-connector stack-up (bearing width 7mm)

### DD-04: 8mm Axle Stubs

**Decision**: Use 8mm diameter x 15mm steel axle stubs through 608ZZ bearings, driven by N20 motor via D-shaft coupler.

**Rationale**:
- 8mm matches 608ZZ inner bore exactly (standard sizing)
- Bending stiffness: I = pi*d^4/64. 8mm: 201mm^4 vs 3mm: 3.98mm^4 = **50x stiffer**
- V5 wheel hub bore is 8.2mm — perfect 0.1mm clearance fit for 8mm axle
- 15mm length provides ~7mm in bearing + ~3mm through connector + ~5mm into wheel bore

### DD-05: Through-Bolt Direction (Wheel Side Into Connector)

**Decision**: Bolts insert from the wheel side (through clearance holes in hub) into heat-set inserts in the connector.

**Rationale**:
- Bolt heads are recessed inside the wheel hub cavity — no external protrusions
- Heat-set inserts in PLA connector provide threaded engagement in the structural part
- Wheel removal is straightforward: unscrew 4 bolts, slide wheel off axle
- Alternative (bolts from connector side) would require reaching through the suspension structure

## 4. Component Modifications

### V5 Wheel Hub (CuriosityV5_Complete.stl, CuriosityV5_HubSpokes.stl)

**Change**: Added 4x M3 clearance holes (3.2mm dia) through hub back face plate.

**Method**: manifold3d boolean subtraction (trimesh mesh -> manifold3d Manifold -> subtract cylinders -> export)

**Script**: `cad/scripts/add_wheel_bolt_holes.py`

**Verification**:
- 4/4 holes verified in both STL files
- Hole diameter: 3.2mm (M3 clearance)
- Hole depth: full hub face thickness (~4.8mm)
- Center bore intact at 8.2mm
- Bolt inner edge to bore outer edge: 3.4mm clearance
- Original files backed up as `*_pre_boltholes.stl`

### Middle Wheel Connector (middle_wheel_connector.py)

**Change**: Bottom face bolt pattern changed from 2x M3 heat-set inserts on 16mm linear spacing to 4x M3 on 20mm BCD.

**Script changes**:
- Added imports: `WHEEL_BCD`, `WHEEL_BOLT_COUNT`, `make_heat_set_bcd`
- Replaced `make_heat_set_pair(spacing=1.6)` with `make_heat_set_bcd(bcd=2.0, count=4)`

### Front/Rear Wheel Connector (front_wheel_connector.py)

**Change**: Steering bracket mount changed from 2x M3 linear to 4x M3 on 20mm BCD for interface standardization.

### Fixed Wheel Mount (fixed_wheel_mount.py)

**Change**: Through-hole pattern changed from 2x M3 linear 16mm to 4x M3 on 20mm BCD to match connector inserts.

### Shared Helpers (rover_cad_helpers.py)

**Added**:
- `make_heat_set_bcd()` function — places N heat-set pockets on a bolt circle
- `M3_CLEARANCE` constant (1.6mm radius = 3.2mm dia)
- `WHEEL_BCD` constant (2.0 cm = 20mm)
- `WHEEL_BOLT_COUNT` constant (4)

## 5. New Hardware Components

### M3x10 Button Head Bolts
- **Spec**: ISO 7380 M3x10mm, A2 stainless
- **Head**: 5.5mm OD x 1.65mm (modeled as 3mm for visual clarity)
- **Qty**: 24 (4 per wheel x 6 wheels)
- **STL**: `3d-print/hardware/M3x10_ButtonHead.stl` (visualization only)

### 8mm Axle Stubs
- **Spec**: 8mm dia x 15mm, mild steel
- **Source**: Cut from 8mm steel rod stock
- **Qty**: 6 (one per wheel)
- **STL**: `3d-print/hardware/8mm_AxleStub.stl` (visualization only)

### Additional 608ZZ Bearings
- **Spec**: 608ZZ (8x22x7mm), ABEC-1 or better
- **Qty**: 6 at wheels + 9 at pivots = 15 total (was 12 purchased, need 3 more)
- **STL**: `3d-print/hardware/608ZZ_Bearing.stl` (visualization only)

## 6. Verification Results

Full alignment check performed by `wheel_mounting_assembly.py`:

| Check | Value | Threshold | Result |
|-------|-------|-----------|--------|
| Bolt inner clearance (all 4) | 4.3mm | >1.0mm | PASS |
| Bolt outer clearance (all 4) | 2.4mm | >1.0mm | PASS |
| Spoke clearance (all 4) | 0.4mm | >0.0mm | PASS |
| Axle-bearing clearance | 0.0mm | >=0.0mm | PASS |
| Axle-bore clearance | 0.1mm | >0.0mm | PASS |
| Bearing seat wall thickness | 4.0mm | >=3.0mm | PASS |

Assembly GLB exported to `temp/wheel_mounting_assembly.glb` for visual inspection.

## 7. Updated Parts List

### Wheel Mounting Hardware (per wheel)
| Item | Qty | Spec |
|------|-----|------|
| M3x10 button head bolt | 4 | ISO 7380, A2 stainless |
| M3 heat-set insert | 4 | 4.8mm bore x 5.5mm, brass knurled |
| 608ZZ bearing | 1 | 8x22x7mm |
| 8mm axle stub | 1 | 15mm long, mild steel |

### Project Bearing Count Update
| Use | Qty | Subtotal |
|-----|-----|----------|
| Rocker pivots | 2 | 2 |
| Bogie pivots | 2 | 4 |
| Differential pivot | 1 | 5 |
| Steering pivots | 4 | 9 |
| **Wheel axles** | **6** | **15** |
| Spares | 3 | **18** |

**Purchase update**: Originally 12 bearings purchased (9+3 spare). Now need 18 total (15+3 spare). **Order 6 more 608ZZ bearings.**

## 8. Lessons Learned (For Future Skill Development)

### L-01: manifold3d for Boolean Operations on Non-Watertight Meshes
- trimesh boolean requires watertight meshes, but reference STLs often aren't
- manifold3d (`pip install manifold3d`) handles non-manifold meshes natively
- Pattern: `trimesh.load() -> manifold3d.Manifold(Mesh(verts, faces)) -> boolean ops -> back to trimesh`
- manifold3d API: `cylinder(height, radius_low, radius_high)`, `translate([x,y,z])`, subtraction with `-`

### L-02: Bolt Pattern Standardization
- Standardizing all mounting interfaces to the same BCD simplifies assembly and reduces error
- BCD patterns are self-centering (unlike linear bolt patterns)
- Always verify bolt clearance to adjacent features (bore, spokes, edges) before committing

### L-03: Assembly Visualization for Interface Verification
- Building assembly in trimesh catches alignment issues before printing
- Color-coding by component type (wheel=dark, bolt=steel, bearing=silver) aids visual inspection
- JSON verification report provides auditable proof of clearance checks

### L-04: Bearing-Decoupled Motor Mounting
- Direct motor shaft to wheel is acceptable for prototype but damages motors long-term
- 608ZZ bearings at $0.50 each are cheap insurance for motor longevity
- The design pattern: motor -> coupler -> axle through bearing -> wheel

### L-05: Parameter Traceability Through Shared Constants
- Adding constants to `rover_cad_helpers.py` (WHEEL_BCD, M3_CLEARANCE) ensures all scripts use the same values
- Every script that creates bolt holes imports from the same source
- Changes to the bolt pattern only need updating in one place

## 9. Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `cad/scripts/add_wheel_bolt_holes.py` | Created | Adds M3 bolt holes to wheel STLs via manifold3d |
| `cad/scripts/wheel_mounting_assembly.py` | Created | Builds assembly, generates hardware meshes, verifies alignment |
| `cad/scripts/rover_cad_helpers.py` | Modified | Added make_heat_set_bcd, M3_CLEARANCE, WHEEL_BCD constants |
| `cad/scripts/middle_wheel_connector.py` | Modified | 2x linear -> 4x BCD bolt pattern |
| `cad/scripts/front_wheel_connector.py` | Modified | 2x linear -> 4x BCD steering mount |
| `cad/scripts/fixed_wheel_mount.py` | Modified | 2x linear -> 4x BCD through-holes |
| `3d-print/wheels/CuriosityV5_Complete.stl` | Modified | Added 4x M3 bolt holes |
| `3d-print/wheels/CuriosityV5_HubSpokes.stl` | Modified | Added 4x M3 bolt holes |
| `3d-print/hardware/M3x10_ButtonHead.stl` | Created | Visualization mesh |
| `3d-print/hardware/8mm_AxleStub.stl` | Created | Visualization mesh |
| `3d-print/hardware/608ZZ_Bearing.stl` | Created | Visualization mesh |
| `temp/wheel_mounting_assembly.glb` | Created | Full assembly visualization |
| `temp/wheel_mounting_verification.json` | Created | Alignment check results |
| `docs/engineering/bolt-on-wheel-mounting-design.md` | Created | This document |
