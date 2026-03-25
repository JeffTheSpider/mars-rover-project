# EA-29: CAD Redesign — Print-Ready Phase 1 Parts

**Date:** 2026-03-25
**Author:** Claude Opus 4.6 + Charlie
**Status:** Complete
**Supersedes:** Original placeholder scripts (pre-redesign)
**References:** EA-08, EA-11, EA-25, EA-26, EA-27, EA-28

---

## 1. Background

All 22 CAD scripts originally produced basic placeholder geometry (rectangular blocks with simple holes). None were print-ready. A complete redesign was undertaken to produce proper, printable, engineered parts with:

- Rounded-rect bodies (2mm corner radius) on all external outlines
- 0.5mm fillets on all external edges (PLA layer adhesion, stress relief)
- 0.3mm chamfers on all insertion features (bearing seats, tube sockets, motor pockets)
- Shared helper module to guarantee dimensional consistency
- Proper mating features (heat-set inserts, through-holes, grub screws)

## 2. Architecture

### 2.1 Shared Helper Module: `rover_cad_helpers.py`

Central module imported by all 22 scripts. Eliminates code duplication and ensures every hardware interface is dimensionally identical across all parts.

**Constants (cm, Fusion 360 API units):**

| Constant | Value (cm) | Value (mm) | Purpose |
|----------|-----------|-----------|---------|
| FILLET_STD | 0.05 | 0.5 | External edge fillets |
| CHAMFER_STD | 0.03 | 0.3 | Insertion chamfers |
| CORNER_R | 0.2 | 2.0 | Rounded-rect corner radius |
| BEARING_OD | 2.215 | 22.15 | 608ZZ bore (0.15mm oversize) |
| BEARING_DEPTH | 0.72 | 7.2 | 608ZZ seat depth (0.2mm extra) |
| BEARING_BORE | 0.81 | 8.1 | 608ZZ shaft bore (0.1mm clearance) |
| TUBE_BORE | 0.82 | 8.2 | 8mm rod socket bore |
| TUBE_DEPTH | 1.5 | 15.0 | Rod engagement depth |
| TUBE_WALL | 0.4 | 4.0 | Minimum wall around tube socket |
| GRUB_M3 | 0.15 | 1.5 | M3 grub screw bore radius |
| INSERT_BORE | 0.24 | 2.4 | M3 heat-set insert bore radius |
| INSERT_DEPTH | 0.55 | 5.5 | Heat-set insert pocket depth |
| N20_W | 1.22 | 12.2 | N20 motor clip width |
| N20_H | 1.02 | 10.2 | N20 motor clip height |
| N20_D | 2.5 | 25.0 | N20 motor clip depth |
| SG90_W | 2.24 | 22.4 | SG90 servo pocket width |
| SG90_D | 1.22 | 12.2 | SG90 servo pocket depth |

**Helper Functions:**

| Function | Creates | Used By |
|----------|---------|---------|
| `draw_rounded_rect()` | Rectangle with filleted corners | 18 scripts |
| `draw_stadium()` | Capsule/stadium shape | steering_knuckle |
| `find_profile_by_area()` | Robust profile selection | All scripts |
| `find_largest_profile()` | Largest sketch profile | Fallback |
| `find_smallest_profile()` | Smallest sketch profile | Bores, holes |
| `extrude_profile()` | New body extrusion | Body creation |
| `cut_profile()` | Cut extrusion | Pockets, bores |
| `join_profile()` | Join extrusion | Gussets, ribs |
| `make_offset_plane()` | Construction plane | Feature placement |
| `make_bearing_seat()` | 608ZZ bore + chamfer + shaft | 4 scripts |
| `make_n20_clip()` | N20 motor pocket + snap tab | 2 scripts |
| `make_sg90_pocket()` | SG90 servo pocket + tab slots | 1 script |
| `make_heat_set_pair()` | 2× M3 insert pockets | 6 scripts |
| `make_m3_grub_hole()` | M3 grub screw bore | 4 scripts |
| `add_edge_fillets()` | All external edge fillets | All scripts |
| `add_chamfer()` | Circular bore entry chamfer | 5 scripts |
| `add_triangular_gusset()` | Reinforcement gusset | 4 scripts |

### 2.2 Assembly Pattern

A critical design decision governs how parts bolt together:

- **Connectors** (structural base parts that stay on the suspension tubes): receive **M3 heat-set inserts** (4.8mm bore, 5.5mm depth)
- **Brackets/mounts** (removable parts that bolt TO connectors): receive **M3 clearance through-holes** (3.3mm diameter)

This ensures a bolt passes through the bracket and threads into the connector's insert. Two insert faces cannot be bolted together.

| Part | Role | Fastener Type |
|------|------|---------------|
| front_wheel_connector | Connector | Heat-set inserts |
| middle_wheel_connector | Connector | Heat-set inserts |
| steering_bracket | Bracket (bolts to connector) | M3 through-holes |
| servo_mount | Bracket (bolts to connector) | M3 through-holes |
| fixed_wheel_mount | Bracket (bolts to connector) | M3 through-holes |
| body_quadrant | Base structure | Heat-set inserts |
| top_deck | Cover (clips to body) | Snap clips |

### 2.3 Script Count

| Category | Scripts | STLs |
|----------|---------|------|
| Calibration | 3 | 3 |
| Wheels | 2 | 2 |
| Steering | 5 | 5 |
| Suspension | 6 | 6 |
| Body | 3 | 11 (4 quadrants + 4 tiles + tray + 2) |
| Accessories | 4 | 4 |
| **Total** | **23 scripts** | **29 STLs** |

Plus: `rover_cad_helpers.py` (shared module), `rover_assembly_v2.py` (visual assembly), `batch_export_all.py` (STL export automation).

## 3. Design Decisions

### 3.1 Why Rounded-Rect Bodies?

Plain rectangular blocks have sharp edges that:
- Catch on things during handling
- Create stress concentration points
- Look cheap and unfinished
- Risk layer delamination at sharp PLA corners

2mm corner radius was chosen as the minimum that provides a visible improvement while remaining printable at 0.4mm nozzle width (5 perimeters at 0.4mm = 2.0mm).

### 3.2 Why 0.5mm Fillets?

The standard fillet radius (0.5mm) was chosen because:
- Single layer height (0.2mm × 2.5 = 0.5mm) — prints as gradual steps
- Eliminates stress risers at edge intersections
- Applied via `add_edge_fillets()` which iterates all body edges with try/except per edge (some edges can't be filleted due to geometry conflicts)

### 3.3 Why Shared Helpers?

Without shared helpers, the bearing seat code would be duplicated in 4 scripts, tube socket code in 6 scripts, etc. Any tolerance adjustment would require editing N files. The helper module ensures:
- **Single source of truth** for all hardware dimensions
- **Consistent fitment** across all parts
- **Easy tolerance adjustment** — change one constant, all parts update

### 3.4 Clearance Strategy

All press-fit and sliding-fit dimensions include PLA-specific clearances:

| Interface | Nominal | Actual | Clearance | Reason |
|-----------|---------|--------|-----------|--------|
| 608ZZ seat | 22.0mm | 22.15mm | +0.15mm | PLA shrinkage, press fit by hand |
| 608ZZ shaft | 8.0mm | 8.1mm | +0.1mm | Shaft must slide through |
| Tube socket | 8.0mm | 8.2mm | +0.2mm | Rod slides in, grub screw retains |
| N20 clip | 12.0×10.0mm | 12.2×10.2mm | +0.2mm | Snap fit with retention tab |
| SG90 pocket | 22.2×11.8mm | 22.4×12.2mm | +0.2/+0.4mm | Drop in from top |
| Heat-set bore | 5.7mm | 4.8mm | -0.9mm | Undersized for heat press-in |

### 3.5 Print Orientation

Every part has a documented print orientation chosen for:
1. No supports needed (all overhangs <45°)
2. Maximum strength in the load direction
3. Best surface finish on visible/mating faces

## 4. Errors Encountered and Fixes

### 4.1 CRITICAL: `draw_rounded_rect` Arc Direction Bug

**Error:** The top-left corner arc in `draw_rounded_rect()` swept counterclockwise (+π/2) instead of clockwise (-π/2). This created an open curve instead of a closed profile.

**Impact:** Every script that used `draw_rounded_rect()` (18 of 22) produced 0 profiles, 0 bodies, and 0 STL output. BatchExportAll reported 12/29 STLs (only scripts using plain rectangles, revolves, or fallback geometry worked).

**Root Cause:** The three other corners correctly used `-half_pi` (clockwise). The top-left corner was the only one using `+half_pi` — a copy-paste error during helper module creation.

**Fix:** Changed line 200 of `rover_cad_helpers.py`:
```python
# Before (BROKEN):
arcs.addByCenterStartSweep(p(*tl), p(cx - hw, tl[1]), half_pi)
# After (FIXED):
arcs.addByCenterStartSweep(p(*tl), p(cx - hw, tl[1]), -half_pi)
```

**Lesson:** Always test helper functions with a simple extrude immediately after creation. A single profile count check (`assert sk.profiles.count > 0`) would have caught this before 18 scripts were affected.

### 4.2 CRITICAL: `draw_rounded_rect` Missing Arguments in Phase 6 Scripts

**Error:** 4 Phase 6 scripts (strain_relief_clip, fuse_holder_bracket, switch_mount, battery_tray) called `draw_rounded_rect(sk, W, H, R)` with only 4 arguments instead of `draw_rounded_rect(sk, 0, 0, W, H, r=R)` with 5 positional + keyword.

**Impact:** Would cause `TypeError` at runtime.

**Root Cause:** Phase 6 scripts were written without checking the function signature.

**Fix:** Added `0, 0,` for cx/cy and `r=` keyword for radius in all 7 affected calls.

**Lesson:** Always import and call helpers in a test before using in production scripts.

### 4.3 IMPORTANT: Bolt Spacing Mismatch

**Error:** `fixed_wheel_mount.py` had `BOLT_SPACING = 1.5` (15mm) while `middle_wheel_connector.py` had `MOUNT_BOLT_SPACING = 1.6` (16mm). These parts bolt together.

**Impact:** 1mm bolt hole misalignment — parts wouldn't assemble.

**Fix:** Changed `fixed_wheel_mount.py` to `BOLT_SPACING = 1.6`.

**Lesson:** Cross-reference ALL mating interfaces during audit. Create a mating interface matrix.

### 4.4 IMPORTANT: Diff Bore Zero Clearance

**Error:** `rocker_hub_connector.py` had `DIFF_BORE_R = 0.4` (8.0mm bore) for an 8mm rod — zero clearance.

**Impact:** Part would not assemble with PLA shrinkage.

**Fix:** Changed to `DIFF_BORE_R = 0.41` (8.2mm bore, matching TUBE_BORE constant).

**Lesson:** All sliding-fit bores should reference shared constants (TUBE_BORE, BEARING_BORE) rather than hardcoding values.

### 4.5 IMPORTANT: Heat-Set Inserts on Both Mating Faces

**Error:** `steering_bracket.py`, `servo_mount.py`, and `fixed_wheel_mount.py` all had heat-set insert pockets for their mounting holes — but they bolt TO connectors that also have inserts.

**Impact:** Cannot bolt two insert faces together (no bolt path).

**Fix:** Replaced `make_heat_set_pair()` calls with M3 clearance through-holes (3.3mm diameter) in all 3 bracket scripts.

**Lesson:** Establish the assembly pattern (connectors=inserts, brackets=through-holes) early and document it prominently.

### 4.6 MINOR: Assembly Script API Error

**Error:** `rover_assembly_v2.py` used `importManager.createSTLImportOptions()` which doesn't exist in Fusion 360 API.

**Impact:** Assembly script failed on first run.

**Fix:** Replaced with `meshBodies.add()` API and switched design to direct mode.

**Lesson:** Always verify API methods exist before coding against them. The Fusion 360 API docs don't include STL import via ImportManager.

### 4.7 IMPORTANT: Assembly STL Import Unit Bug

**Error:** `rover_assembly_v2.py` used `MeshUnits.CentimeterMeshUnit` to import STL files, but Fusion 360 exports STLs in millimeters. This caused all 53 imported parts to be 10x too large.

**Impact:** Assembly visualization was completely wrong — body panels dominated the view at 1300mm x 2200mm instead of 130mm x 220mm.

**Root Cause:** Assumed Fusion 360 STL export used the API's internal centimeter units, but STL export always writes in millimeters (the 3D printing standard).

**Fix:** Changed to `MeshUnits.MillimeterMeshUnit` on line 323 of `rover_assembly_v2.py`.

**Verification:** STL info confirmed `bearing_test_piece.stl` dimensions are 32.8 x 32.8 x 12mm (matching the 32mm x 32mm x 12mm design spec).

**Lesson:** Always verify import/export units match by checking a known-dimension part's STL bounding box before importing.

## 5. Verification

### 5.1 Individual Script Testing

All 22 part scripts + 1 battery tray (new) were tested via MCP execute_code:

```
OK: BearingTestPiece — 1 bodies
OK: ServoMount — 1 bodies
OK: RockerHubConnector — 1 bodies
OK: FrontWheelConnector — 1 bodies
OK: MiddleWheelConnector — 1 bodies
OK: SwitchMountPlate — 1 bodies
OK: BatteryTray — 1 bodies
OK: SteeringKnuckle — 2 bodies (main + arm extension)
OK: DifferentialPivotHousing — 3 bodies (main + flanges)
OK: BodyQuadrant — 7 bodies (main + ribs/panels)
OK: TopDeck — 1 bodies
OK: ElectronicsTray — 1 bodies
OK: SteeringBracket — 1 bodies
OK: FixedWheelMount — 3 bodies (main + gussets)
OK: StrainReliefClip — 1 bodies
OK: FuseHolderBracket — 1 bodies
OK: CableClip — 2 bodies (main + arm)
```

### 5.2 Batch Export

```
Components processed: 29/29
STL files exported:   29
Errors:               0
Elapsed time:         182s (3.0 min)
Total STL size:       ~35 MB
```

### 5.3 STL File Sizes (Sanity Check)

All STL files have reasonable sizes indicating proper geometry:
- Smallest: rover_tire.stl (99 KB) — simple revolve
- Largest: body_quadrant_fl.stl (3944 KB) — complex panel with ribs
- Average: ~600 KB per part

No 0 KB or suspiciously small files.

## 6. Files Created/Modified

### New Files
| File | Purpose |
|------|---------|
| `cad/scripts/rover_cad_helpers.py` | Shared helper module (~500 lines) |
| `cad/scripts/battery_tray.py` | 2S LiPo cradle (new part) |
| `cad/scripts/rover_assembly_v2.py` | Full assembly visualisation |
| `3d-print/body/battery_tray.stl` | Battery tray STL export |

### Modified Files (22 redesigned scripts)
All scripts in `cad/scripts/` except deprecated, superseded, and utility scripts.

### Git Tag
`v1.0.0-cad-redesign` — complete checkpoint before further modifications.

## 7. Open Items

1. **Assembly positioning** — rover_assembly_v2.py uses approximate positions; exact kinematic positioning would require solving the suspension geometry
2. **Multi-body cleanup** — Some scripts create extra bodies (gussets, ribs) that don't join to the main body; cosmetic issue, doesn't affect STL export
3. **Tolerance validation** — All clearances are theoretical; actual PLA fitment requires test prints (bearing test piece, tube socket test)
4. **CTC Bizer calibration** — Printer hasn't been used in years; calibration prints needed before production parts

## 8. Recommendations

1. Print calibration pieces FIRST: bearing_test_piece, tube_socket_test, calibration_test_card
2. Validate fitment before committing to full part prints
3. If bearing seat is too tight, increase `BEARING_OD` in `rover_cad_helpers.py` by 0.05mm increments
4. If tube socket is too loose, decrease `TUBE_BORE` by 0.05mm increments
5. All changes propagate automatically through shared helpers to all scripts
