# Session Handoff — 2026-03-26 (Evening)

## Session Summary
Implemented the bolt-on wheel mounting system (4x M3 on 20mm BCD, 608ZZ bearings, 8mm axles) across all connector scripts and the V5 wheel STL. Then diagnosed and fixed mesh defects in the original GrabCAD Curiosity wheel model by re-opening the .f3d source, combining all 40 bodies into a single clean solid (B-rep boolean union), re-exporting, and using manifold3d to fix the hub holes (removed 12 small rivet holes, re-cut 12 decorative holes at perfect 30-degree spacing).

## Completed This Session

### Bolt-On Wheel Mounting System
- [x] Added `make_heat_set_bcd()` function to `rover_cad_helpers.py` + constants (WHEEL_BCD, WHEEL_BOLT_COUNT, M3_CLEARANCE)
- [x] Updated `middle_wheel_connector.py`: 2x M3 linear 16mm -> 4x M3 on 20mm BCD
- [x] Updated `front_wheel_connector.py`: steering mount 2x linear -> 4x BCD
- [x] Updated `fixed_wheel_mount.py`: through-holes 2x linear -> 4x BCD
- [x] Created `add_wheel_bolt_holes.py`: manifold3d boolean subtraction to add bolt holes to wheel STLs
- [x] Created `wheel_mounting_assembly.py`: assembly builder with hardware meshes + alignment verification
- [x] All alignment checks PASS (inner 4.3mm, outer 2.4mm, spoke 0.4mm clearance)
- [x] Created hardware visualization STLs: `3d-print/hardware/{M3x10_ButtonHead,608ZZ_Bearing,8mm_AxleStub}.stl`
- [x] Created design doc: `docs/engineering/bolt-on-wheel-mounting-design.md` (9 sections, 5 design decisions, 5 lessons)
- [x] Updated integration log with bolt pattern spec and bearing count

### V5 Wheel Mesh Fix (GrabCAD Source Model)
- [x] Diagnosed hub defects: 448 non-manifold edges, 264 disconnected components, 12 small rivet holes, misaligned decorative hole
- [x] Root cause: multi-body concatenation via trimesh without topological merging
- [x] Fix: opened original `Curiosity Wheel v25.f3d` in Fusion 360
- [x] Combined 8 bodies (hub + 6 spokes + tread) into single solid via Combine feature (B-rep boolean union)
- [x] Re-exported as clean STL: watertight=True, 0 non-manifold edges, 1 component
- [x] Used manifold3d to fill hub face, re-cut 12 decorative holes at perfect positions
- [x] Added 4x M3 bolt holes on 20mm BCD
- [x] Saved full-scale master: `temp/CuriosityV5_master_fullscale_fixed.stl` (reusable at any scale)
- [x] Saved Phase 1 (80mm): `3d-print/wheels/CuriosityV5_Complete.stl`
- [x] Comprehensive research reports: `temp/wheel_hub_defect_analysis.txt`, `temp/wheel_origin_research.txt`

### Documentation & Memory
- [x] Created `memory/wheel-mounting-learnings.md` (manifold3d patterns, bolt design rules, bearing decoupling)
- [x] Updated `MEMORY.md` (bearing count 9->15, wheel bolt pattern, axle specs, bolt-on doc reference)

## In Progress
- [ ] **Fusion 360 visual approval of fixed wheel**: The fixed wheel (291K faces, watertight, clean hub) was loaded into Fusion 360 via JSON import. User needs to visually inspect the hub to confirm the decorative holes look correct and the small rivet holes are gone. Last loaded as mesh body "V5 Wheel (Fixed - Clean Hub)" in an Untitled document.
- [ ] **HubSpokes STL not re-created from fixed mesh**: The R<36mm face extraction was in the killed script. Need to re-run.
- [ ] **Incremental assembly in Fusion 360**: User wanted to build up the assembly one part at a time (wheel -> axle -> bearing -> bolts -> connector) for visual approval. Only the wheel has been loaded so far.

## Next Steps (Priority Order)
1. **Get user approval on fixed wheel in Fusion 360** — Ask Charlie to inspect the hub (top-down view). If the 12 decorative holes look symmetric and the small rivet holes are gone, proceed. If not, iterate.
2. **Re-create HubSpokes STL** — Extract faces within R<36mm from the fixed Complete STL, save as `CuriosityV5_HubSpokes.stl`
3. **Continue incremental assembly in Fusion 360** — Add 8mm axle stub, then 608ZZ bearing, then M3 bolts, then wheel connector — each for user approval
4. **Commit all changes** — Large batch of new files and modifications (see Uncommitted Changes below)
5. **Run BatchExportAll** — The connector scripts were modified but their STLs haven't been re-exported from Fusion 360
6. **Set up CTC Bizer printer** — Needs physical setup, calibration prints
7. **Order Phase 1 parts** — Including 6 extra 608ZZ bearings (total 18 needed)

## Decisions Made
- **4x M3 on 20mm BCD** (over 2x linear 16mm) — Self-centering, equal load distribution, torque resistance, redundancy. Full rationale in bolt-on-wheel-mounting-design.md DD-01
- **Button head bolts** (over socket cap head) — Lower profile (1.65mm vs 3mm), fits in wheel hub cavity. DD-02
- **608ZZ bearing at each wheel** — Decouples radial loads from motor. 50x stiffer axle. $3 total. DD-03
- **8mm axle stubs** (15mm) — Matches 608ZZ bore, 8.2mm wheel bore. DD-04
- **Through-bolt from wheel side** — Bolt heads recessed in hub, heat-set inserts in connector. DD-05
- **Fix wheel via .f3d Combine** (over mesh-only repair) — Saves a clean full-scale master for Phase 2 reuse
- **Remove 12 rivet holes** — Too small for FDM at any scale, purely cosmetic. Fill and leave clean hub face
- **Re-cut 12 decorative holes at perfect positions** — Fix the misaligned hole from original GrabCAD model

## Open Questions
- Does the fixed wheel hub look correct in Fusion 360? (needs Charlie's visual approval)
- Should the 12 decorative holes alternate in size (original design has 18.8mm and 19.9mm alternating) or all be the same size?

## Uncommitted Changes

### Modified (6 files)
```
M cad/scripts/batch_export_all.py        (minor updates)
M cad/scripts/fixed_wheel_mount.py       (2x linear -> 4x BCD through-holes)
M cad/scripts/front_wheel_connector.py   (steering mount 2x -> 4x BCD)
M cad/scripts/generate_rover_params.py   (new wheel/bolt params)
M cad/scripts/middle_wheel_connector.py  (mount face 2x -> 4x BCD)
M cad/scripts/rover_cad_helpers.py       (make_heat_set_bcd, constants)
```

### New Files (many)
```
3d-print/hardware/M3x10_ButtonHead.stl   (visualization)
3d-print/hardware/608ZZ_Bearing.stl      (visualization)
3d-print/hardware/8mm_AxleStub.stl       (visualization)
3d-print/wheels/CuriosityV5_Complete.stl  (fixed, with bolt holes)
3d-print/wheels/CuriosityV5_Complete_clean.stl (fixed, no bolt holes)
3d-print/wheels/CuriosityV5_Complete_clean_no_bolts.stl (backup)
3d-print/wheels/CuriosityV5_Complete_pre_boltholes.stl (original backup)
3d-print/wheels/CuriosityV5_HubSpokes.stl (needs re-gen from fixed mesh)
3d-print/wheels/CuriosityV5_HubSpokes_pre_boltholes.stl (original backup)
3d-print/wheels/CuriosityV5_Tread.stl
3d-print/wheels/CuriosityWheelV5.stl
cad/scripts/add_wheel_bolt_holes.py
cad/scripts/wheel_mounting_assembly.py
cad/scripts/rover_wheel_hub_v4.py
cad/scripts/rover_beadlock_ring.py
cad/scripts/rover_tire_*.py              (5 tire scripts)
cad/reference-wheels/                    (GrabCAD source + fullscale STLs)
docs/engineering/bolt-on-wheel-mounting-design.md
docs/engineering/reference-model-integration-log.md
docs/engineering/wheel-v5-design.md
```

### Temp files (not for commit)
```
temp/CuriosityV5_combined_fullscale.stl
temp/CuriosityV5_master_fullscale_fixed.stl
temp/assembly-parts/*.json
temp/wheel_hub_defect_analysis.txt
temp/wheel_origin_research.txt
```

## Memory Files Updated
- `MEMORY.md` — Bearing count 9->15, wheel bolt pattern, axle specs, bolt-on doc link
- `wheel-mounting-learnings.md` — NEW: manifold3d patterns, bolt design rules, bearing decoupling, assembly verification

## Environment State
- Fusion 360 running with ~16 Untitled documents open (accumulated during session)
  - One contains the combined BRep solid (8 wheel bodies merged)
  - One contains the fixed wheel mesh loaded for inspection
  - Close all except the fixed wheel one at next session start
- manifold3d installed (`pip install manifold3d`) — persists
- temp/assembly-parts/ has JSON files for Fusion import (can be cleaned up)
- No background processes running

## Key Files for Next Session
| File | Purpose |
|------|---------|
| `temp/CuriosityV5_master_fullscale_fixed.stl` | Full-scale master wheel (499mm OD), re-scale for any phase |
| `3d-print/wheels/CuriosityV5_Complete.stl` | Phase 1 wheel (80mm, fixed hub, bolt holes) |
| `3d-print/wheels/CuriosityV5_Complete_clean.stl` | Phase 1 wheel (80mm, fixed hub, NO bolt holes) |
| `cad/scripts/wheel_mounting_assembly.py` | Assembly builder + verification |
| `docs/engineering/bolt-on-wheel-mounting-design.md` | Full design rationale |
| `temp/wheel_hub_defect_analysis.txt` | Detailed hub defect analysis |
| `temp/wheel_origin_research.txt` | GrabCAD model origin + conversion pipeline research |

## Learnings for Future Skills
1. **Fusion 360 .f3d import**: Use `importManager.createFusionArchiveImportOptions()`, not `documents.open()`
2. **Combine bodies from different components**: Copy proxies to root with `body.createForAssemblyContext(occ).copyToComponent(root)`, then use `combineFeatures`
3. **STL import to Fusion 360**: No native STL import via API; parse binary STL manually, convert mm->cm, use `root.meshBodies.addByTriangleMeshData()`
4. **Large JSON export**: Never iterate per-face in Python; use numpy vectorization (`v[f.flatten()].flatten().tolist()`)
5. **GrabCAD model quality**: Always combine multi-body models into single solid before STL export to avoid non-manifold interfaces
6. **Full-scale master pattern**: Fix geometry at full scale, save master STL, then scale for each phase
