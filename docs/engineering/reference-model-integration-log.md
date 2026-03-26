# Reference Model Integration Log

## Overview
Extracting reference CAD models (Curiosity wheel + suspension), scaling to 0.4x, combining for Phase 1 rover.

## Traceability Matrix

### Source Models
| Model | Source | Original Size | Scale Factor | Target Size |
|-------|--------|---------------|-------------|-------------|
| frame_assem_v6.STEP | GrabCAD reference rover | 761 x 401 x 796 mm | 0.4x | 304 x 160 x 318 mm |
| Curiosity Wheel v25.f3d | GrabCAD NASA Curiosity | 448mm OD x 404mm W | 0.1786x | 80mm OD |

### Suspension Components Retained (19 of 48 occurrences)
| Component | Count | Role | Full-Scale Size | 0.4x Size |
|-----------|-------|------|----------------|-----------|
| rb3 (right rocker-bogie) | 1 | Complete right suspension arm | 773 x 382 x 165 mm | 309 x 153 x 66 mm |
| rb (left rocker-bogie) | 1 | Complete left suspension arm | 752 x 355 x 165 mm | 301 x 142 x 66 mm |
| DIFFSUS2 (diff bar) | 1 | Differential mechanism bar | 32 x 20 x 482 mm | 13 x 8 x 193 mm |
| Rod End M8 | 2 | Rod-end bearings for diff | 30 x 12 x 48 mm | 12 x 5 x 19 mm |
| u calmp | 2 | U-clamps at diff pivot | 40 x 50 x 50 mm | 16 x 20 x 20 mm |
| Part1 (pivot pins) | 2 | Diff pivot pins | 8 x 56 x 8 mm | 3.2 x 22.6 x 3.2 mm |
| rb_hub angle_front back | 4 | Wheel hub connectors | 40 x 149 x 144 mm | 16 x 60 x 57 mm |
| motor shaft couple_sub_wood | 6 | Motor-to-wheel couplers | 50 x 50 x 20 mm | 20 x 20 x 8 mm |

### Components Deleted (29 occurrences)
| Component | Count | Reason |
|-----------|-------|--------|
| frame_v2 (body frame) | 1 | Using our 4-quadrant body design |
| sub_frame | 1 | Using our electronics tray |
| structural box | 2 | Body panels — we have our own |
| full_assembly_3 (robotic arm) | 1 | Phase 2 feature |
| Assem1dhfsuhfusufssMOUNT (arm mount) | 1 | Phase 2 feature |
| robo arm plate | 1 | Phase 2 feature |
| Servo full (loose servo) | 1 | Servos inside rb assemblies kept |
| Lidar mountin' | 1 | Phase 2 feature |
| rover front | 1 | Using our own front panel |
| Shutdown Button | 1 | Using our E-stop design |
| finalRim (wheels) | 7 | Replacing with Curiosity V5 wheels |
| treads tyre orgi (tyres) | 7 | Replacing with Curiosity V5 wheels |
| motorCAD2.0 (loose motors) | 4 | Motors inside rb assemblies kept |

## Key Dimensional Results

### Wheel Positions (0.4x scale, assembly coordinates in mm)
| Position | Side | X | Y | Z |
|----------|------|---|---|---|
| Front | Left | -96.8 | 86.1 | -141.0 |
| Front | Right | 96.8 | 96.4 | -148.2 |
| Middle | Left | -148.1 | 95.3 | -0.2 |
| Middle | Right | 148.1 | 90.1 | -3.2 |
| Rear | Left | -126.7 | 95.5 | 150.0 |
| Rear | Right | 124.7 | 90.4 | 147.1 |

### Key Dimensions Comparison
| Measurement | Original (full) | 0.4x Actual | Our Target | Delta |
|-------------|-----------------|-------------|------------|-------|
| Track width | 741 mm | 296.2 mm | 280 mm | +16.2 mm (+5.8%) |
| Wheelbase | 746 mm | 298.3 mm | 360 mm | -61.7 mm (-17.1%) |
| Tube cross-section | 20 mm | 8.0 mm | 8.0 mm | 0 (perfect) |
| Diff bar length | 482 mm | 192.8 mm | ~200 mm | -7.2 mm |
| Ground clearance (Y) | ~199 mm | ~76 mm | ~60 mm | +16 mm |

### Features Requiring Adaptation (Task 5)
| Feature | After 0.4x Scale | Required Size | Action |
|---------|-------------------|---------------|--------|
| Pivot pins (Part1) | 3.2mm dia | 8.0mm dia (608ZZ) | Re-bore |
| Bearing seats | ~3.5mm | 22.15mm (608ZZ) | Re-cut |
| Motor pockets (inside rb) | ~12.8 x 12.8 x 40mm | 12.2 x 10.2 x 24mm (N20) | Resize |
| Servo pockets (inside rb) | ~12 x 20 x 24mm | 22.4 x 12.2 x 22.7mm (SG90) | Re-cut |
| Shaft coupler bore | ~1.2mm D-shaft | 3.1mm (N20 D-shaft) | Re-bore |
| Heat-set inserts | scaled down | 4.8mm x 5.5mm | Re-cut |
| M3/M4 screw holes | scaled down | 3.2mm / 4.2mm | Re-bore |

## Change Log

### Step 1: Isolate Suspension (COMPLETED)
- Imported frame_assem_v6.STEP fresh into Fusion 360
- Deleted 29 non-suspension occurrences (3 passes, reverse-order deletion)
- 19 suspension occurrences retained
- Checkpoint: `checkpoints/suspension_clean_fullscale.stl`

### Step 2: Scale to 0.4x (COMPLETED)
- **FAILED APPROACH 1**: Scale body proxies via Fusion 360 Scale feature
  - Bodies scaled but occurrence positions unchanged
  - Result: 0.4x-sized parts at full-scale distances
- **FAILED APPROACH 2**: Scale occurrence transforms + body geometry separately
  - Double-positioned some components, broke assembly
  - Undo via API failed (executeTextCommand 'Commands.Undo' returned 0 ops)
  - Had to re-import STEP file from scratch
- **SUCCESSFUL APPROACH**: Export STLs + full 4x4 transforms, scale with Python/trimesh
  - Export each occurrence as individual STL from Fusion 360
  - Extract full 4x4 transform matrices (not just translation!)
  - Apply transform to STL geometry, then scale by 0.4
  - Result: 304.4 x 159.7 x 318.3 mm (matches expected 304 x 160 x 318)

### Step 3: Scale Curiosity Wheel (IN PROGRESS)
- TBD

## Lessons Learned (for future MCP/CAD skill creation)

### 1. NEVER scale assemblies in Fusion 360 via API
- **Problem**: Fusion 360's Scale feature only affects body geometry, NOT occurrence transforms
- **Symptom**: Parts shrink but stay at original positions = exploded view
- **Root cause**: Occurrence transforms are separate from body geometry in the assembly hierarchy
- **Workaround**: Export STLs + full 4x4 transform matrices, scale externally with trimesh

### 2. ALWAYS extract full 4x4 transform matrices, not just translations
- **Problem**: STEP imports often have rotated occurrences, not just translated
- **Symptom**: Translation-only positioning gives wrong results for rotated sub-assemblies
- **Fix**: Use `transform.getCell(row, col)` to extract full 4x4 matrix
- **Note**: Column 3 (translation) is in cm in Fusion 360, multiply by 10 for mm

### 3. Create checkpoints before destructive operations
- **Problem**: Fusion 360 API undo (`executeTextCommand('Commands.Undo')`) may not work
- **Symptom**: 0 operations undone, corrupted state, no way back
- **Fix**: Export checkpoint STLs before any modification. Save combined + individual parts.
- **Pattern**: Export before modify, verify after modify, rollback to checkpoint if wrong

### 4. Fusion 360 STL export coordinate space
- **For sub-assemblies (rb3, rb)**: STL includes all child geometry positioned in the sub-assembly's local space. The occurrence transform positions the whole sub-assembly in world space.
- **For simple components**: STL geometry is in component-local space (usually near origin)
- **Both need**: The occurrence's 4x4 transform applied to get world position

### 5. STEP import assembly structure
- Components may share definitions (same component, multiple occurrences)
- Each occurrence has its own 4x4 transform (rotation + translation)
- Sub-assemblies contain child occurrences with their own transforms
- The transform hierarchy is: world = parent_transform * child_transform * body_local

### 6. Safe Fusion 360 MCP patterns
- NEVER call `document.close()` — crashes Fusion 360
- NEVER rely on API undo — it may not work after MCP operations
- ALWAYS create new documents with `app.documents.add()` for fresh starts
- ALWAYS save important state as STL/JSON checkpoints before modifications
- Use `design.timeline.item(n).entity.deleteMe()` to remove specific features (when it works)
- Transform manipulation (setting `occ.transform`) bypasses the timeline — cannot be undone

### 7. Python trimesh is the reliable scaling tool
- `mesh.apply_transform(4x4_matrix)` — position in world space
- `mesh.apply_scale(factor)` — uniform scale from origin
- `trimesh.util.concatenate(meshes)` — combine for visualization
- Export to STL (printing) or GLB (3D viewing)

### 8. Dimensional validation checklist
After scaling, always verify:
- [ ] Tube cross-sections match rod diameter (8mm)
- [ ] Track width within tolerance
- [ ] Wheelbase within tolerance
- [ ] Individual part sizes are proportional
- [ ] Hardware features flagged for adaptation (bearings, motors, servos)

## File Manifest

### Checkpoints
- `cad/reference=suspension/checkpoints/suspension_clean_fullscale.stl` — Combined full-scale after cleanup

### Full-Scale Exports
- `cad/reference=suspension/extracted/full-scale/*.stl` — 19 individual part STLs
- `cad/reference=suspension/extracted/full-scale/assembly_positions.json` — Translation-only positions (partial)
- `cad/reference=suspension/extracted/full-scale/assembly_transforms.json` — Full 4x4 transforms (authoritative)

### 0.4x Scale Exports
- `cad/reference=suspension/extracted/0.4-scale/*.stl` — 19 positioned + scaled STLs
- `cad/reference=suspension/extracted/0.4-scale/suspension_assembly_0.4x.stl` — Combined suspension
- `cad/reference=suspension/extracted/0.4-scale/suspension_assembly_0.4x.glb` — 3D visualization
- `cad/reference=suspension/extracted/0.4-scale/rover_suspension_wheels_0.4x.stl` — Full rover (suspension + 6 wheels)
- `cad/reference=suspension/extracted/0.4-scale/rover_suspension_wheels_0.4x.glb` — Full rover GLB
- `cad/reference=suspension/extracted/0.4-scale/wheel_FL.stl` through `wheel_RR.stl` — 6 positioned wheels

### Curiosity Wheel V5
- `cad/reference-wheels/curiosity_wheel_v5_80mm.stl` — 80mm OD, centered at origin (360k faces)
- `3d-print/wheels/CuriosityWheelV5.stl` — Print-ready copy

### Print Directory
- `3d-print/reference-suspension/suspension_assembly_0.4x.stl` — Assembly reference
- `3d-print/reference-suspension/rover_suspension_wheels_0.4x.stl` — Full rover reference

### Updated Scripts
- `cad/scripts/batch_export_all.py` — V4 wheel entries commented out, V5 notes added
- `cad/scripts/generate_rover_params.py` — V5 wheel params + reference_suspension section added

### Individual Suspension Parts (Step 9)

#### Printable Parts — 13 Unique Designs (27 instances)
| Part | Size (0.4x mm) | Qty | Role | Watertight |
|------|----------------|-----|------|------------|
| rb_hub angle | 29.4 x 23.9 x 26.4 | 2 | Rocker hub (main pivot, 2 bodies) | No |
| rb_angle_148.06_new | 28.0 x 25.1 x 39.4 | 2 | 148-degree tube angle connector | Yes |
| rb_angle | 28.0 x 25.3 x 29.2 | 2 | Standard tube angle connector | Yes |
| rb_angle_100.82 | 16.0 x 23.6 x 41.1 | 2 | 100-degree tube angle connector | Yes |
| rb_link_diff | 26.0 x 49.6 x 21.1 | 2 | Differential link (diff bar to rocker) | Yes |
| rb_hub angle_front back | 57.4 x 60.0 x 19.5 | 4 | Wheel hub connector (tube to shaft coupler) | Yes |
| motor shaft couple_sub_wood | 8.0 x 20.0 x 20.0 | 6 | Motor-to-wheel shaft coupler | Yes |
| servo_mount | 24.0 x 12.0 x 20.0 | 1 | Servo mount (straight, rb3 side) | Yes |
| servo_mount_24.18_left | 24.0 x 16.0 x 22.2 | 1 | Angled servo mount (rb3 side) | Yes |
| servo_mount_24.18 | 24.0 x 16.8 x 22.9 | 1 | Angled servo mount (rb side) | Yes |
| servo_mount_rb only | 24.0 x 12.0 x 20.0 | 1 | Servo mount (rb side) | Yes |
| u calmp | 16.0 x 20.1 x 20.1 | 2 | U-clamp (diff bar pivot) | Yes |
| DIFFSUS2 | 192.8 x 8.0 x 13.1 | 1 | Differential bar | Yes |

#### Metal Tubes — 8mm Steel Rod Cutting Plan (0.4x)
| Tube Name (full-scale) | Full Length | 0.4x Length | Qty | Total |
|-------------------------|-----------|-------------|-----|-------|
| al pipe 427.5 mm | 427.5mm | 171.0mm | 2 | 342.0mm |
| al pipe 262 mm | 262mm | 104.8mm | 2 | 209.6mm |
| al pipe 229 mm | 229mm | 91.6mm | 2 | 183.2mm |
| al pipe 195 mm | 195mm | 78.0mm | 2 | 156.0mm |
| **Total** | | | **8** | **890.8mm** |

#### Hardware (metal, not printed)
| Part | Size (0.4x mm) | Qty | Notes |
|------|----------------|-----|-------|
| Part1 (pivot pins) | 3.2 x 22.6 | 2 | Need 8mm dia pins (3.2mm too small) |
| Rod End M8 (main+ball) | 12 x 19mm + 5.9mm ball | 2 | Need full-size M8 rod ends |

#### Reference Only (not printed)
| Part | Size (0.4x mm) | Qty | Notes |
|------|----------------|-----|-------|
| motorCAD2.0 | 40.4 x 12.8 x 12.8 | 2 | Ref motor position — using N20 (12x10x24mm) |

### Individual Part Files
- `cad/reference=suspension/extracted/full-scale/individual/*.stl` — 43 full-scale STLs
- `cad/reference=suspension/extracted/full-scale/individual/part_transforms.json` — 4x4 world transforms
- `cad/reference=suspension/extracted/0.4-scale/individual/*_04x.stl` — 43 scaled STLs
- `cad/reference=suspension/extracted/0.4-scale/individual/individual_parts_catalog.json` — Full catalog
- `cad/reference=suspension/extracted/0.4-scale/individual/printable_parts_assembly_04x.stl` — Combined printable
- `3d-print/reference-suspension/individual/ref_*.stl` — 13 unique printable designs

## Status Summary

| Step | Status | Key Outcome |
|------|--------|-------------|
| 1. Isolate suspension | COMPLETE | 29 deleted, 19 kept, checkpoint saved |
| 2. Scale to 0.4x | COMPLETE | 304 x 160 x 318mm envelope, tubes = 8mm |
| 3. Scale Curiosity wheel | COMPLETE | 80mm OD x 64.7mm wide |
| 4. Combine wheels + suspension | COMPLETE | 361 x 190 x 378mm with wheels |
| 5. Identify adaptations | COMPLETE | 8 feature categories need 1:1 sizing |
| 6. Fitment audit | COMPLETE | Tubes perfect, bearings/motors/servos undersized |
| 7. Export STLs | COMPLETE | 19 suspension + 6 wheel + 2 combined STLs |
| 8. Documentation | COMPLETE | This log + params + batch_export updated |
| 9. Individual parts | COMPLETE | 43 parts: 27 printable, 8 tubes, 6 hardware, 2 reference |

## Wheel-to-Suspension Attachment Design

### Interface Analysis
| Parameter | Value | Notes |
|-----------|-------|-------|
| V5 hub bore | 3.10mm dia | At wheel center |
| N20 D-shaft | 3.0mm (with D-flat) | 10mm protrusion from gearbox |
| Clearance | 0.10mm | Slight press-fit with D-flat keying |
| Hub depth | 16.41mm | 10mm shaft engagement (sufficient) |
| Spoke tip radius | 29.57mm | Spoke tips do NOT reach tread |
| Tread inner radius | 33.64mm | 4.07mm gap from spoke tips |

### Attachment Method
1. **V5 wheel hub bore (3.1mm)** slides directly onto **N20 D-shaft (3.0mm)**
2. **D-flat prevents rotation** — positive engagement, no slipping
3. **Axial retention**: CA glue or friction fit (only 4g wheel, minimal axial load)
4. **N20 motor held by clip** in the suspension connector (existing parametric design)
5. **No external bearing at 0.4x** — N20 internal bearings handle the Phase 1 loads (~200g per wheel)

### One-Piece Wheel (Phase 1)
- **MUST print as single piece** using `CuriosityV5_Complete.stl`
- Spoke tips don't reach tread inner wall (4.07mm gap)
- Original design uses 30 screws to bridge this gap (impractical at 80mm scale)
- Single-piece print creates solid connection via infill between spokes and tread
- Weight: ~4g per wheel (20% infill), 24g total for 6 wheels

### Two-Piece Wheel (Phase 2 — future)
- Requires adapter ring or extended spoke tips to bridge 4mm gap
- Tread: TPU for flexibility, hub+spokes: PLA for rigidity
- Snap-fit or press-fit interface at spoke-tread junction

### Print Notes
- Orientation: flat (tread surface down), 80mm footprint
- CTC Bizer: 2 wheels per print (80+80+5mm gap = 165mm < 225mm bed)
- Estimated print time: ~2hr per wheel, ~6hr for all 6 (3 prints of 2)
- Supports: minimal (hub bore may need support)

## Hybrid Assembly Strategy (Recommended)

### Use Reference STL As-Is (structural connectors — correct angles, no hardware features)
| Part | Qty | Size (0.4x) | Role |
|------|-----|-------------|------|
| rb_angle_148.06_new | 2 | 28×25×39mm | 148° tube angle connector |
| rb_angle | 2 | 28×25×29mm | Standard tube angle connector |
| rb_angle_100.82 | 2 | 16×24×41mm | 100° tube angle connector |
| rb_link_diff | 2 | 26×50×21mm | Differential link |
| u calmp | 2 | 16×20×20mm | U-clamp (diff bar pivot) |
| DIFFSUS2 | 1 | 193×8×13mm | Differential bar |

### Replace with Parametric Designs (need full-size hardware features)
| Reference Part | Qty | Replace With | Reason |
|---------------|-----|-------------|--------|
| motor shaft couple_sub_wood | 6 | front/middle_wheel_connector.py | Need N20 clip (12.2×10.2mm) |
| servo_mount (all variants) | 4 | servo_mount.py + steering_bracket.py | Need SG90 pocket (22.4×12.2mm) |
| rb_hub angle_front back | 4 | Integrated into wheel connectors | Need 608ZZ seat (22.15mm) |
| rb_hub angle | 2 | rocker_hub_connector.py | Need bearing seat + tube sockets |

### Hardware (buy at full size, not 0.4x scaled)
| Part | Qty | Actual Size Needed | Notes |
|------|-----|--------------------|-------|
| Pivot pins | 2 | 8mm dia × 23mm | Reference Part1 is only 3.2mm dia at 0.4x |
| Rod end bearings | 2 | M8 rod ends | Reference scaled ones too small |
| 8mm steel rods | 8 | See cutting plan | 891mm total rod length |

### Keep As-Is (V5 Curiosity Wheel)
- `CuriosityV5_Complete.stl` — 80mm OD, single piece
- Modified with 4x M3 bolt holes on 20mm BCD for bolt-on mounting

## Bolt-On Wheel Mounting (2026-03-26)

### Design Change
Replaced direct D-shaft press-fit with bolt-on mounting through 608ZZ bearings.

**Previous design**: Wheel bore (3.1mm) press-fits onto N20 D-shaft (3mm)
**New design**: 8mm axle through 608ZZ bearing, wheel bolts to connector via 4x M3

### Bolt Pattern Specification
| Parameter | Value |
|-----------|-------|
| Pattern | 4x M3 clearance holes on 20mm BCD |
| Hole diameter | 3.2mm (M3 clearance) |
| Bolt circle diameter | 20.0mm |
| Bolt positions | 0, 90, 180, 270 degrees |
| Bolt spec | M3x10 button head (ISO 7380) |
| Mating feature | M3 heat-set inserts in connector |

### Updated Parts List
| Item | Qty | Notes |
|------|-----|-------|
| M3x10 button head bolts | 24 | 4 per wheel |
| M3 heat-set inserts (additional) | 24 | For wheel mounting faces |
| 608ZZ bearings (additional) | 6 | At wheel positions |
| 8mm axle stubs | 6 | 15mm length, mild steel |

### Bearing Count Update
Previous: 12 purchased (9 pivot + 3 spare)
New total needed: 15 (9 pivot + 6 wheel) + 3 spare = 18
Action: Order 6 more 608ZZ bearings

### Verification
All alignment checks passed — see `temp/wheel_mounting_verification.json`
Full design rationale — see `docs/engineering/bolt-on-wheel-mounting-design.md`
