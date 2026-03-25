# Engineering Analysis 30: CAD Testing Plan

**Document**: EA-30
**Date**: 2026-03-25
**Author**: Claude Opus 4.6 + Charlie
**Status**: Active
**Purpose**: Define a systematic, budget-conscious testing plan for validating all 29 Phase 1 STLs before committing to the full ~72-hour print campaign.
**Depends on**: EA-08 (Phase 1 Spec), EA-11 (3D Printing Strategy), EA-25 (Suspension Audit), EA-26 (Suspension Design), EA-27 (Steering System), EA-28 (Systems Integration), EA-29 (CAD Redesign)
**See also**: `docs/plans/pre-print-checklist.md`, `docs/plans/pre-print-master-plan.md`

---

## 1. Testing Philosophy

### 1.1 Core Principles

Every gram of PLA, every hour of print time, and every heat-set insert costs real money and irreplaceable time. The CTC Bizer is an older machine that has not been used in years. The CAD scripts have never produced a physical part. This testing plan exists to catch problems when they are cheap to fix (a 15-minute test print) rather than expensive to discover (an 8-hour body quadrant that doesn't mate with its neighbour).

**The three rules:**

1. **Never batch-print untested geometry.** Print one, measure it, confirm fitment, then print the remaining copies.
2. **Test interfaces, not aesthetics.** A bearing seat that is 0.1mm too tight will wreck the entire suspension. A cosmetic blemish on a body panel is irrelevant at this stage.
3. **Fix at the source.** If a bearing bore is wrong, adjust `BEARING_OD` in `rover_cad_helpers.py` so every part that uses `make_bearing_seat()` inherits the correction. Do not sand individual parts to fit.

### 1.2 The Test-Print-Validate-Adjust Cycle

```
  +-- DESIGN -------+     +-- PRINT --------+     +-- VALIDATE -----+
  |                  |     |                  |     |                  |
  | rover_cad_       | --> | Slice in Cura    | --> | Measure with     |
  | helpers.py       |     | gpx -m cr1d      |     | digital calipers |
  | (shared dims)    |     | Print on Bizer   |     | (+-0.02mm)       |
  |                  |     |                  |     |                  |
  +------------------+     +------------------+     +--------+---------+
          ^                                                  |
          |               PASS? -----> Continue              |
          |                                                  |
          +--- ADJUST <---- FAIL? ---------------------------+
               (change shared constant by 0.05mm)
```

Every test print follows this cycle. The key insight is that `rover_cad_helpers.py` is the single source of truth for all hardware interface dimensions. A tolerance fix to one constant propagates automatically to every script that uses it.

### 1.3 Budget Context

| Item | Cost | Notes |
|------|------|-------|
| PLA filament | ~GBP 18/kg spool | Phase 1 needs ~1 kg total |
| Calibration prints (all 4 phases below) | ~50g PLA, ~GBP 1 | Less than 5% of total filament |
| Full print campaign | ~1000g PLA, ~GBP 18 | ~72 hours, 76 parts |
| Heat-set inserts | ~GBP 3 for 50 | M3, 5.7mm OD, brass knurled |
| Failed full-size part | 30-200g PLA + 1-10 hours | This is what we are trying to avoid |

Spending 2-3 hours and 50g of filament on calibration prints can save 20+ hours and 300g+ of wasted material from a single bad tolerance propagating through the entire build.

### 1.4 Tools Required

- Digital calipers (resolution 0.02mm or better) -- essential, non-negotiable
- 608ZZ bearing (at least 1 from the 12 ordered)
- 8mm steel rod offcut (~50mm is sufficient for socket testing)
- M3 heat-set insert (at least 2 for test installation)
- Soldering iron with conical or insert tip
- N20 motor (1 from the 6 ordered)
- SG90 servo (1 from the 4 ordered)
- M3x12mm bolt + nut (at least 2)
- Marker pen (for marking tight/loose areas)

---

## 2. Phase 1: Calibration Prints (MUST DO FIRST)

These three prints establish the baseline accuracy of the CTC Bizer and validate the two most critical press-fit interfaces (608ZZ bearing and 8mm tube socket). **Do not print any rover parts until all three calibration prints pass.**

### 2.1 Print #1: `calibration_test_card.stl`

**Location**: `3d-print/calibration/calibration_test_card.stl`
**Estimated print time**: ~30 minutes
**Estimated filament**: ~8g PLA
**Purpose**: General printer dimensional accuracy across multiple feature sizes.

| Slicer Setting | Value |
|----------------|-------|
| Layer height | 0.2mm |
| Walls | 4 |
| Infill | 50% gyroid |
| Nozzle temp | 205 C |
| Bed temp | 60 C |
| Speed | 40 mm/s |
| Supports | Off |
| Brim | None |

**Measurements to take** (record all in a table with target, actual, and deviation):

| Feature | Target (mm) | Actual (mm) | Deviation (mm) | Pass/Fail |
|---------|-------------|-------------|-----------------|-----------|
| Overall X dimension | (as designed) | | | +/-0.3mm |
| Overall Y dimension | (as designed) | | | +/-0.3mm |
| Overall Z dimension | (as designed) | | | +/-0.3mm |
| Hole diameter (small) | 3.0mm | | | +/-0.15mm |
| Hole diameter (medium) | 8.0mm | | | +/-0.15mm |
| Hole diameter (large) | 22.0mm | | | +/-0.15mm |
| Boss/post diameter | (as designed) | | | +/-0.2mm |
| Wall thickness | 4.0mm | | | +/-0.2mm |

**Pass criteria**: All features within stated tolerances.

**If FAIL**:
- If holes are consistently undersized: this is normal for FDM. Calculate the average hole shrinkage factor. Expect 0.1-0.3mm undersized.
- If outer dimensions are oversized: check e-steps calibration (over-extrusion). Reduce flow rate by 2-5% in Cura.
- If Z-height is wrong: check first layer height (Z-offset too close = elephant's foot, too far = poor adhesion).
- Record all correction factors in `cad/scripts/printer_calibration.py`.

### 2.2 Print #2: `bearing_test_piece.stl`

**Location**: `3d-print/calibration/bearing_test_piece.stl`
**Estimated print time**: ~15-20 minutes
**Estimated filament**: ~6g PLA
**Purpose**: Validate 608ZZ bearing press-fit at 22.15mm bore, 7.2mm depth.

This is the single most critical test print. Nine bearings must fit into seats across 4 different part types (steering_bracket, bogie_pivot_connector, body_quadrant, and the bearing test piece itself). The shared `BEARING_OD` constant (22.15mm, which is 22.0mm nominal + 0.15mm oversize for PLA) governs all of them.

| Slicer Setting | Value |
|----------------|-------|
| Layer height | 0.2mm |
| Walls | 4-5 |
| Infill | 60% gyroid |
| Nozzle temp | 205 C |
| Bed temp | 60 C |
| Speed | 35-40 mm/s |
| Supports | Off |
| Brim | None |

**Test procedure**:

1. Remove print from bed, allow to cool to room temperature (PLA contracts as it cools).
2. Measure the bearing bore diameter with calipers at 3 points (0, 60, 120 degrees). Record all three.
3. Measure the bore depth. Target: 7.2mm.
4. Attempt to seat a 608ZZ bearing (22.0mm OD, 7.0mm width) by hand pressure only.
5. Rate the fit:

| Rating | Description | Action |
|--------|-------------|--------|
| **A -- Perfect** | Bearing pushes in with firm hand pressure, stays in place when inverted, no rattle | PASS -- proceed to Phase 2 |
| **B -- Slightly tight** | Bearing enters with strong thumb pressure or light tap with plastic handle | Acceptable for now, note it. May loosen after a few insertions. |
| **C -- Too tight** | Bearing will not enter without hammering or the print cracks | FAIL -- increase `BEARING_OD` by 0.05mm in `rover_cad_helpers.py`, re-export, reprint |
| **D -- Too loose** | Bearing drops in freely and rattles or falls out when inverted | FAIL -- decrease `BEARING_OD` by 0.05mm in `rover_cad_helpers.py`, re-export, reprint |
| **E -- Way off** | Bearing doesn't remotely fit (>0.5mm discrepancy) | Printer calibration issue. Return to Print #1 and diagnose. |

**Also measure**:
- Shaft bore (8.1mm target): slide 8mm rod through the centre hole. Should pass through freely with minimal play.
- Entry chamfer: visually confirm 0.3mm chamfer is present at bore mouth.

**Maximum iterations**: 3. If the bearing still does not fit after 3 reprints with 0.05mm adjustments each time, investigate whether the printer has a systematic dimensional error (e.g., X/Y steps per mm are miscalibrated).

### 2.3 Print #3: `tube_socket_test.stl`

**Location**: `3d-print/calibration/tube_socket_test.stl`
**Estimated print time**: ~15 minutes
**Estimated filament**: ~5g PLA
**Purpose**: Validate 8mm steel rod socket bore (8.2mm) and M3 grub screw retention.

The tube-and-connector suspension design (EA-25/EA-26) requires every connector to accept 8mm steel rods in slide-fit sockets, retained by M3 grub screws. The `TUBE_BORE` constant (8.2mm = 8.0mm nominal + 0.2mm clearance) governs all 6 suspension connector scripts.

| Slicer Setting | Value |
|----------------|-------|
| Layer height | 0.2mm |
| Walls | 4-5 |
| Infill | 60% gyroid |
| Nozzle temp | 205 C |
| Bed temp | 60 C |
| Speed | 35-40 mm/s |
| Supports | Off |
| Brim | None |

**Test procedure**:

1. Measure the tube socket bore with calipers. Target: 8.2mm.
2. Insert an 8mm steel rod into the socket.
3. Rate the fit:

| Rating | Description | Action |
|--------|-------------|--------|
| **A -- Perfect** | Rod slides in smoothly with slight friction, stays when released, can be pulled out by hand | PASS |
| **B -- Tight but usable** | Rod enters with light twisting/rocking, doesn't rattle | Acceptable -- note. May improve with use. |
| **C -- Too tight** | Rod will not enter or requires excessive force | FAIL -- increase `TUBE_BORE` by 0.05mm |
| **D -- Too loose** | Rod falls out under gravity, significant play | FAIL -- decrease `TUBE_BORE` by 0.05mm |

4. Test socket depth: rod should seat to 15mm depth (mark rod at 15mm with tape, insert until tape touches socket face).
5. Test M3 grub screw hole: thread an M3 set screw into the radial hole. It should engage and be able to press against the rod to lock it in place.
6. Test wall integrity: with the rod inserted and grub screw tightened, apply moderate lateral force to the rod. The socket wall (4mm minimum, controlled by `TUBE_WALL`) should not crack or deform visibly.

**Maximum iterations**: 3 (same approach as bearing test).

### 2.4 Calibration Phase Summary

| Print | Time | Filament | Pass Criteria |
|-------|------|----------|---------------|
| Calibration test card | 30 min | 8g | All features within tolerance |
| Bearing test piece | 20 min | 6g | 608ZZ Rating A or B |
| Tube socket test | 15 min | 5g | 8mm rod Rating A or B |
| **Possible reprints** (up to 3 iterations each) | +90 min max | +33g max | |
| **Total worst case** | ~2.5 hours | ~52g | |

**Go/No-Go gate**: All three prints must achieve at least Rating B before proceeding to Phase 2. Record the validated (golden) dimensions:

- Golden bearing bore: _____ mm (target 22.15mm)
- Golden tube socket bore: _____ mm (target 8.2mm)
- Golden shaft bore: _____ mm (target 8.1mm)

---

## 3. Phase 2: Critical Interface Validation

With the CTC Bizer calibrated and basic fits confirmed, Phase 2 tests the actual rover parts that must mate together. Print ONE of each mating pair and verify the interface before committing to full quantities.

### 3.1 Test Set A: Front Steering Corner

Print these two parts together (they fit on the bed simultaneously):

| Part | STL | Print Time | Filament |
|------|-----|------------|----------|
| front_wheel_connector (x1) | `suspension/front_wheel_connector.stl` | ~45 min | ~12g |
| steering_bracket (x1) | `steering/steering_bracket.stl` | ~45 min | ~15g |

**Interface checks**:

| Check | What to Verify | Target | Tool |
|-------|---------------|--------|------|
| Bolt hole alignment | 2x M3 mounting holes at 16mm spacing | Holes align when parts are mated; M3 bolt passes through both | M3x12 bolt + light |
| Heat-set insert pocket | 2x 4.8mm x 5.5mm pockets in front_wheel_connector | Insert installs flush at 170-180 C, M3 bolt threads in cleanly | Soldering iron + insert + M3 bolt |
| M3 through-hole | 2x 3.3mm clearance holes in steering_bracket | M3 bolt slides through freely | M3 bolt |
| Bearing seat (steering bracket) | 22.15mm bore, 7.2mm depth in steering_bracket | 608ZZ fits (should match calibration result) | 608ZZ bearing |
| Tube socket (front_wheel_connector) | 8.2mm bore, 15mm depth, M3 grub | 8mm rod slides in (should match calibration result) | 8mm rod |
| Assembled clearance | Parts bolt together without fouling | No interference between bodies when bolted at 16mm spacing | Visual + finger check |

**Pass criteria**: All 6 checks pass. The two parts bolt together cleanly with an M3 bolt passing through the bracket's clearance hole into the connector's heat-set insert.

### 3.2 Test Set B: Middle Wheel Station

| Part | STL | Print Time | Filament |
|------|-----|------------|----------|
| middle_wheel_connector (x1) | `suspension/middle_wheel_connector.stl` | ~45 min | ~14g |
| fixed_wheel_mount (x1) | `steering/fixed_wheel_mount.stl` | ~30 min | ~8g |

**Interface checks**:

| Check | What to Verify | Target |
|-------|---------------|--------|
| Bolt hole alignment | 2x M3 at 16mm spacing | Holes align, bolt passes through |
| Heat-set insert pocket | In middle_wheel_connector | Insert installs cleanly |
| M3 through-hole | In fixed_wheel_mount | Bolt slides through freely |
| N20 motor clip | 12.2 x 10.2 x 25mm pocket in fixed_wheel_mount | N20 motor snaps in, does not fall out, shaft protrudes through exit hole |
| Tube socket | In middle_wheel_connector | 8mm rod fits (should match calibration) |

**Pass criteria**: All checks pass. Motor clips securely. Bolt alignment correct.

### 3.3 Test Set C: Differential Pivot

| Part | STL | Print Time | Filament |
|------|-----|------------|----------|
| differential_pivot_housing (x1) | `suspension/differential_pivot_housing.stl` | ~60 min | ~20g |

**Interface checks**:

| Check | What to Verify | Target |
|-------|---------------|--------|
| Bearing seat | 22.15mm bore for 608ZZ (centre pivot) | 608ZZ fits per calibration |
| Diff bar bore | 8.2mm through-bore for 8mm differential bar rod | Rod slides through freely, grub screw locks it |
| Flange bolt holes | M3 mounting holes for body attachment | M3 bolts pass through |
| Structural integrity | Part does not crack under moderate hand force | No visible cracking at bearing boss or flange junctions |

### 3.4 Test Set D: Steering Linkage

Print these three small parts together:

| Part | STL | Print Time | Filament |
|------|-----|------------|----------|
| steering_knuckle (x1) | `steering/steering_knuckle.stl` | ~30 min | ~8g |
| servo_mount (x1) | `steering/servo_mount.stl` | ~30 min | ~10g |
| steering_horn_link (x1) | `steering/steering_horn_link.stl` | ~10 min | ~2g |

**Interface checks**:

| Check | What to Verify | Target |
|-------|---------------|--------|
| SG90 pocket (servo_mount) | 22.4 x 12.2 x 12mm pocket + 32.4mm tab slots | SG90 drops in from top, tabs rest on ledges, no rattle |
| N20 clip (steering_knuckle) | 12.2 x 10.2 x 25mm motor pocket | N20 motor snaps in securely |
| Steering arm extension (knuckle) | Arm with M2 pin hole for horn link | M2 pin/screw passes through |
| Horn link pin holes | 20mm centre-to-centre, 2x M2 holes | M2 screws fit both holes, 20mm spacing verified with calipers |
| Hard stop tab (knuckle) | Tab-in-channel for +/-35 deg limit | Visual check that tab clears channel at neutral and contacts at ~35 deg rotation |

### 3.5 Test Set E: Heat-Set Insert Validation Block

This is not a rover part -- it is a simple test block to validate the heat-set insert installation process before committing to installing ~40 inserts across the actual rover parts.

**Option A**: Use the front_wheel_connector from Test Set A (it already has insert pockets).
**Option B**: Print a dedicated 30x30x15mm test block with 3 insert pockets at the CAD-specified 4.8mm bore and 5.5mm depth.

**Test procedure**:

1. Heat soldering iron to 170 C (PLA -- lower than PETG's 200-220 C).
2. Place brass insert (M3, 5.7mm OD, knurled) on top of pocket.
3. Press iron tip into the insert thread and push straight down. The surrounding PLA should melt and flow around the knurls.
4. Insert should seat flush with surface (or 0.2mm below) within 2-3 seconds.
5. Allow 10 seconds to cool.
6. Thread an M3x12 bolt into the insert. It should thread smoothly with no binding.
7. Unthread and re-thread 3 times to confirm.

**Pass/Fail criteria**:

| Result | Description | Action |
|--------|-------------|--------|
| PASS | Insert flush, straight, bolt threads smoothly 3 times | Proceed with confidence |
| Insert crooked | Insert entered at an angle | Technique issue -- practice. Use insert tip if available. Does not require CAD changes. |
| Surrounding PLA cracked | Material fractured around insert | Temperature too high -- reduce to 160 C. Or wall thickness insufficient -- increase `INSERT_BORE` wall requirement. |
| Insert sinks too deep | Insert pushed below flush | Do not push past flush. Reduce iron temperature or press duration. |
| Insert won't seat | Pocket too tight for insert OD | Increase `INSERT_BORE` by 0.1mm (currently 4.8mm / 2.4mm radius). |
| Bolt won't thread | PLA flowed into insert thread | Temperature too high -- reduce 10 C. Or clean insert thread with M3 tap after installation. |

### 3.6 Phase 2 Summary

| Test Set | Parts | Print Time | Filament | Key Interface |
|----------|-------|------------|----------|---------------|
| A: Front steering corner | 2 | ~90 min | ~27g | Bolt alignment, bearing, tube socket |
| B: Middle wheel station | 2 | ~75 min | ~22g | Bolt alignment, N20 clip |
| C: Differential pivot | 1 | ~60 min | ~20g | Bearing, diff bar bore |
| D: Steering linkage | 3 | ~70 min | ~20g | SG90 pocket, horn link geometry |
| E: Heat-set inserts | (reuse A) | 0 | 0 | Insert installation process |
| **Total** | **8 parts** | **~5 hours** | **~89g** | |

**Go/No-Go gate**: All interface checks pass. Any failures must be traced back to a shared constant in `rover_cad_helpers.py`, adjusted, re-exported via BatchExportAll, and the specific test piece reprinted before proceeding.

---

## 4. Phase 3: Structural Load Testing

Phase 1 is a 1.25 kg prototype operating indoors on flat surfaces. PLA at 60 MPa tensile strength provides enormous safety margins. Nevertheless, certain parts bear concentrated loads and should be tested by hand to confirm they will not fail during normal operation.

### 4.1 Load-Bearing Hierarchy

Parts ranked by structural criticality (highest to lowest):

| Rank | Part | Primary Load | Failure Mode | Consequence |
|------|------|-------------|--------------|-------------|
| 1 | rocker_hub_connector | Suspension articulation torque at body pivot | Tube socket cracks, bearing boss shears | Entire suspension side detaches |
| 2 | bogie_pivot_connector | Vertical load from 2 wheels, pivot torque | Bearing boss cracks, tube sockets split | Bogie detaches from rocker |
| 3 | differential_pivot_housing | Diff bar bending moment, body attachment | Flange bolts pull out, bearing boss cracks | Differential mechanism fails |
| 4 | front_wheel_connector | Vertical load from 1 wheel, steering torque | Tube socket cracks at grub screw hole | Wheel assembly detaches |
| 5 | steering_bracket | Steering torque + vertical load through bearing | Bearing bore deforms, mounting holes strip | Wheel cannot steer |
| 6 | body_quadrant (x4) | All loads from suspension pivots | Bearing boss cracks where it meets panel wall | Entire side sags |
| 7 | fixed_wheel_mount | Motor torque reaction, vertical load | N20 clip cracks, bolts pull from inserts | Middle wheel loses drive |

### 4.2 Hand-Test Procedures

These tests require no equipment beyond the printed parts, hardware, and your hands. They should be performed on the single test prints from Phase 2 before committing to full quantities.

**Test 4.2.1: Tube Socket Twist Test**

- Parts: rocker_hub_connector or front_wheel_connector with 8mm rod inserted and grub screw tightened.
- Procedure: Grip the connector body in one hand and the protruding rod in the other. Apply a firm twisting force (try to rotate the rod relative to the connector). Then apply a firm bending force (try to lever the rod sideways).
- Pass: Rod does not rotate in socket. No visible cracking at the socket walls or grub screw hole. No audible cracking sounds.
- Fail: Rod slips in socket (grub screw not engaging), or wall cracks appear (wall too thin or infill too low).

**Test 4.2.2: Bearing Boss Compression Test**

- Parts: Any part with a bearing seat (steering_bracket, bogie_pivot_connector) with 608ZZ bearing installed.
- Procedure: Place the part on a flat surface. Press firmly on the bearing with your thumb (approximately 5-10 kg force). Rock the bearing side to side.
- Pass: No deformation, no cracking, bearing does not move relative to the part.
- Fail: Bearing boss cracks, or bearing shifts in the seat.

**Test 4.2.3: N20 Motor Clip Retention Test**

- Parts: steering_knuckle or fixed_wheel_mount with N20 motor inserted.
- Procedure: Hold the part and try to pull the motor out by gripping the motor body. Shake the part vigorously.
- Pass: Motor stays clipped in. Motor does not rattle. Shaft still turns freely.
- Fail: Motor slides out with light force, or motor rattles significantly.

**Test 4.2.4: Bolt Pull-Out Test (Heat-Set Insert)**

- Parts: Any part with installed heat-set insert (from Phase 2 Test Set E).
- Procedure: Thread an M3x12 bolt through a mating bracket into the insert. Tighten with a screwdriver (not a ratchet or power tool -- just firm hand tightening). Then try to pull the bolt out axially.
- Pass: Insert remains seated. No cracking. Bolt holds firmly.
- Fail: Insert pulls out of PLA, or surrounding material cracks.

**Test 4.2.5: Body Quadrant Seam Flex Test**

- Parts: 2 adjacent body quadrants (e.g., FL + FR) bolted together at the seam.
- Procedure: Hold one quadrant flat and try to flex the other up/down at the seam. Apply moderate force.
- Pass: Seam feels rigid. No visible gap opening. No bolt loosening.
- Fail: Seam flexes more than ~2mm, or gap opens between panels.

### 4.3 PLA Infill and Perimeter Recommendations by Structural Tier

Based on the load hierarchy above:

| Tier | Parts | Walls | Infill | Layer Height | Rationale |
|------|-------|-------|--------|-------------|-----------|
| **Critical** (Rank 1-3) | rocker_hub_connector, bogie_pivot_connector, differential_pivot_housing | 5 | 60% gyroid | 0.16mm | Maximum wall thickness around tube sockets and bearing bores. 0.16mm layers for better resolution on critical bore features. |
| **Structural** (Rank 4-5) | front_wheel_connector, middle_wheel_connector, steering_bracket, fixed_wheel_mount | 4-5 | 50-60% gyroid | 0.2mm | High infill around motor clips and bearing seats. Standard layer height adequate. |
| **Body** (Rank 6) | body_quadrant (x4) | 4 | 20% gyroid | 0.2mm | Large panels do not need high infill. Strength comes from walls and ribs. Add 5-8mm brim for bed adhesion. |
| **Light duty** | servo_mount, steering_horn_link, cable_clip, strain_relief_clip, top_deck tiles | 3 | 30% gyroid | 0.2mm | Low loads. Filament savings. |
| **Minimal** | fuse_holder_bracket, switch_mount_plate, battery_tray | 3 | 20-30% gyroid | 0.2mm | Near-zero structural load. |

---

## 5. Phase 4: Sub-Assembly Integration

After individual parts pass Phase 2 interface checks and Phase 3 load tests, build three sub-assemblies to verify that parts work together as a system.

### 5.1 Sub-Assembly A: Rocker-Bogie Arm (1 side)

**Parts needed** (all previously printed and tested):

| Part | Qty | Source |
|------|-----|--------|
| rocker_hub_connector | 1 | Phase 2 or new print |
| bogie_pivot_connector | 1 | New print |
| front_wheel_connector | 2 | Phase 2 + 1 new |
| middle_wheel_connector | 1 | Phase 2 |
| 608ZZ bearing | 3 | (rocker pivot, bogie pivot, front steering) |
| 8mm steel rod segments | 3 | Cut to length per EA-25 |
| M3 grub screws | 3 | To lock rods in sockets |

**Assembly procedure**:

1. Press bearings into rocker_hub_connector (body pivot) and bogie_pivot_connector.
2. Cut three 8mm rod segments: rocker front tube, rocker rear tube, bogie tube (lengths from `generate_rover_params.py`).
3. Insert rod ends into tube sockets. Tighten M3 grub screws.
4. Verify that the bogie pivots freely around its bearing relative to the rocker.
5. Verify that the rocker sub-assembly can pivot around the body pivot bearing.

**Checks**:

| Check | Target | Method |
|-------|--------|--------|
| Articulation range (bogie) | +/-20 deg freely | Hold rocker, tilt bogie by hand |
| Articulation range (rocker) | +/-25 deg freely | Hold body pivot, tilt rocker |
| No binding at any angle | Smooth motion throughout range | Slow sweep, feel for catches |
| Rod retention | Rods do not slip under articulation | Inspect grub screws after 20 articulation cycles |
| Wire routing clearance | Wires could pass through channels | Visual check of channel size at full articulation |

**Failure modes to watch for**:
- Tube socket cracking at grub screw hole under articulation load: increase `TUBE_WALL` or add reinforcement rib.
- Bearing binding when rod is under lateral load: check bore alignment (may need reaming).
- Rods too long/short (connectors don't reach): re-check tube lengths against `generate_rover_params.py`.

### 5.2 Sub-Assembly B: Steering Corner (1 wheel)

**Parts needed**:

| Part | Qty |
|------|-----|
| steering_bracket | 1 (from Phase 2 Test Set A) |
| steering_knuckle | 1 (from Phase 2 Test Set D) |
| servo_mount | 1 (from Phase 2 Test Set D) |
| steering_horn_link | 1 (from Phase 2 Test Set D) |
| front_wheel_connector | 1 (from Phase 2 Test Set A) |
| SG90 servo | 1 |
| N20 motor | 1 |
| 608ZZ bearing | 1 |
| M3x12 bolts + nuts | 4 |
| M2x10 screws + nuts | 2 (horn link pins) |

**Assembly procedure**:

1. Install 608ZZ bearing into steering_bracket.
2. Install SG90 servo into servo_mount.
3. Bolt servo_mount to steering_bracket (or to front_wheel_connector depending on design).
4. Install N20 motor into steering_knuckle.
5. Connect steering_horn_link between servo horn and knuckle steering arm using M2 pin screws.
6. Bolt front_wheel_connector to steering_bracket.

**Checks**:

| Check | Target | Method |
|-------|--------|--------|
| Steering sweep | +/-35 deg from centre | Rotate servo horn by hand, observe knuckle rotation |
| Hard stop engagement | Knuckle tab contacts channel walls at ~35 deg | Visual check at both extremes |
| No binding | Smooth rotation through full range | Slow sweep by hand, feel for catches |
| Servo horn link geometry | Link does not collide with bracket body at any angle | Observe clearance at full lock |
| Motor shaft clearance | Motor shaft protrudes through knuckle exit hole at all steering angles | Visual check |
| Bolt interference | All bolts tightened without fouling other components | Try to tighten all bolts with assembled parts |

### 5.3 Sub-Assembly C: Body Shell (2 quadrants)

**Parts needed**:

| Part | Qty |
|------|-----|
| body_quadrant_fl | 1 (new print, ~8 hours) |
| body_quadrant_fr | 1 (new print, ~8 hours) |
| M3x12 bolts | ~6 |
| M3 heat-set inserts | ~6 |
| 3mm alignment dowel pins | 2 (if designed into the seam) |

**Note**: This is the most expensive test (16 hours of print time, ~120g PLA for both quadrants). Consider printing only one quadrant first and verifying that:
- The bearing seat boss locations match the suspension geometry.
- The seam tongue-and-groove features are correctly formed.
- The part fits on the CTC Bizer bed (225x145mm limit; body quadrants are 220x130mm nominal for FL/FR and up to 140x220mm for RL/RR).

If the first quadrant passes all checks, print the second and test the seam.

**Checks**:

| Check | Target | Method |
|-------|--------|--------|
| Bed fit | Part printed without exceeding bed edges | Visual during print |
| Bearing seat boss | 22.15mm bore at correct Z-height (60mm from base) | Calipers + 608ZZ test fit |
| Seam alignment | FL/FR quadrants mate with <0.5mm gap at tongue-and-groove | Join quadrants, measure gap with feeler gauge |
| Bolt alignment at seam | M3 bolt holes line up across seam boundary | Shine light through both holes |
| Overall dimensions | Length, width, height match expected | Calipers on each axis |
| Internal clearance | Space for electronics tray and wire routing | Visual inspection of interior cavity |
| Cable exit slots | 10x5mm slots present and correctly positioned | Visual + wire test |
| Kill switch bore (RR only) | 15mm bore in rear wall | 15mm drill bit or caliper check |

### 5.4 Phase 4 Summary

| Sub-Assembly | New Prints Required | Print Time | Filament | Key Validation |
|-------------|-------------------|------------|----------|----------------|
| A: Rocker-bogie arm | bogie_pivot_connector, 1x front_wheel_connector | ~90 min | ~25g | Articulation, rod retention |
| B: Steering corner | (reuse Phase 2 parts) | 0 | 0 | Full steering sweep, linkage geometry |
| C: Body shell (2 quadrants) | body_quadrant_fl + fr | ~16 hours | ~120g | Bed fit, seam alignment, bearing boss |
| **Total** | | **~18 hours** | **~145g** | |

---

## 6. Tolerance Adjustment Procedure

### 6.1 When to Adjust

Adjust shared constants only when:
- A calibration print clearly fails (Rating C, D, or E).
- A mating interface is demonstrably wrong (parts will not assemble).
- The same issue appears consistently across multiple prints (not a one-off fluke).

Do NOT adjust because:
- A single print feels "a bit snug" (Rating B is acceptable).
- You think it "should be" different based on theory.
- You want to pre-compensate for a problem that hasn't occurred.

### 6.2 Adjustment Constants and Increments

All adjustable constants are in `D:\Mars Rover Project\cad\scripts\rover_cad_helpers.py`.

| Constant | Current Value (cm) | Current Value (mm) | Adjustment Step | Direction | Affects |
|----------|-------------------|-------------------|-----------------|-----------|---------|
| `BEARING_OD` | 2.215 | 22.15 | 0.005 cm (0.05mm) | Increase if tight, decrease if loose | 4 scripts: steering_bracket, bogie_pivot_connector, bearing_test_piece, diff_pivot_housing |
| `BEARING_DEPTH` | 0.72 | 7.2 | 0.005 cm (0.05mm) | Increase if bearing proud, decrease if too deep | Same 4 scripts |
| `BEARING_BORE` | 0.81 | 8.1 | 0.005 cm (0.05mm) | Increase if shaft tight, decrease if loose | All bearing locations |
| `TUBE_BORE` | 0.82 | 8.2 | 0.005 cm (0.05mm) | Increase if rod tight, decrease if loose | 6 scripts: all connectors |
| `TUBE_DEPTH` | 1.5 | 15.0 | 0.05 cm (0.5mm) | Rarely needs adjustment | 6 scripts |
| `INSERT_BORE` | 0.48 | 4.8 | 0.01 cm (0.1mm) | Increase if insert won't seat, decrease if it falls in | 6 scripts with heat-set pockets |
| `N20_W` | 1.22 | 12.2 | 0.005 cm (0.05mm) | Increase if motor tight, decrease if loose | 2 scripts: steering_knuckle, fixed_wheel_mount |
| `N20_H` | 1.02 | 10.2 | 0.005 cm (0.05mm) | Same | Same 2 scripts |
| `SG90_W` | 2.24 | 22.4 | 0.01 cm (0.1mm) | Increase if servo tight, decrease if loose | 1 script: servo_mount |
| `SG90_D` | 1.22 | 12.2 | 0.01 cm (0.1mm) | Same | Same |

### 6.3 Adjustment Procedure

1. **Identify the failed interface** (e.g., "608ZZ bearing won't enter bearing_test_piece bore").
2. **Measure the printed feature** with calipers (e.g., bore reads 21.95mm, target was 22.15mm, so PLA contracted 0.20mm).
3. **Calculate the required adjustment** (e.g., need 22.15mm + 0.20mm = 22.35mm actual bore, so increase `BEARING_OD` from 2.215 to 2.235 cm).
4. **BUT**: Apply adjustment in small steps. Do not jump the full calculated amount. Start with 0.05mm (0.005 cm) and retest.
5. **Edit `rover_cad_helpers.py`**:
   ```python
   # Before (original):
   BEARING_OD = 2.215          # 22.15mm (22mm + 0.15mm press-fit oversize)

   # After (adjusted +0.05mm):
   BEARING_OD = 2.22           # 22.20mm (22mm + 0.20mm press-fit oversize, CTC Bizer cal.)
   ```
6. **Update the comment** to note the reason and the printer it was calibrated for.
7. **Re-export affected STLs**:
   - Option A (targeted): Run only the affected script(s) in Fusion 360 and manually export the STL.
   - Option B (full): Run `BatchExportAll` in Fusion 360 to regenerate all 29 STLs. This is safer because it guarantees all parts using the changed constant are updated.
8. **Re-slice and re-print** the test piece.
9. **Retest** the fit.
10. **Record the final validated value** as the "golden dimension" for this printer.

### 6.4 Re-Export Workflow

After any constant change in `rover_cad_helpers.py`:

```
1. Save rover_cad_helpers.py
2. Deploy to Fusion 360 Scripts directory:
   copy "D:\Mars Rover Project\cad\scripts\rover_cad_helpers.py"
         "%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\RoverCadHelpers\"
   (or use /deploy-scripts skill)
3. Open Fusion 360
4. Run BatchExportAll (Shift+S > BatchExportAll > Run)
5. Wait for all 29 STLs to regenerate (~3-5 min)
6. Verify the changed STL:
   - Use 3dprint MCP get_stl_info to check bounding box dimensions
   - Or open in Cura and measure the feature visually
7. Re-slice, re-convert with gpx, reprint test piece
```

### 6.5 Version Tracking

Keep a log of all tolerance adjustments:

| Date | Constant | Old Value (mm) | New Value (mm) | Reason | Test Print Result |
|------|----------|----------------|----------------|--------|-------------------|
| (example) | BEARING_OD | 22.15 | 22.20 | Bearing test piece bore measured 21.95mm, too tight | Rating A after adjustment |

---

## 7. Print Settings Matrix

### 7.1 CTC Bizer Universal Settings

These settings apply to ALL prints on the CTC Bizer:

| Setting | Value | Notes |
|---------|-------|-------|
| Printer | CTC 3D Bizer | MakerBot Replicator 1 Dual clone |
| Extruder | Left only | Right nozzle removed/parked |
| Nozzle diameter | 0.4mm | Standard |
| Filament | PLA 1.75mm | White or grey |
| Nozzle temp | 205 C (+/-5) | 200-210 C range for PLA |
| Bed temp | 60 C | Heated bed |
| Bed adhesion | Glue stick or painter's tape | Re-apply every 3-5 prints |
| Cooling fan | 100% after layer 2 | PLA benefits from max cooling |
| Retraction | 1-2mm at 25 mm/s | Short retraction for this machine |
| Print speed | 40-50 mm/s | Slower = better layer adhesion |
| Travel speed | 120-150 mm/s | Non-printing moves |
| First layer speed | 20 mm/s | Half speed for adhesion |
| First layer height | 0.3mm (150% of layer height) | Compensates for bed levelling variance |
| Z-hop | 0.2mm on retract | Prevents nozzle dragging across top of print |
| File format | x3g (via GPX) | `gpx -m cr1d input.gcode output.x3g` |
| SD card | Required | CTC Bizer prints from SD only |

### 7.2 Per-Part Settings

| Part | Layer Height | Walls | Infill | Top/Bottom | Speed | Supports | Brim | Orientation | Est. Time | Est. Filament |
|------|-------------|-------|--------|------------|-------|----------|------|-------------|-----------|---------------|
| **Calibration** | | | | | | | | | | |
| calibration_test_card | 0.2mm | 4 | 50% gyroid | 4 | 40 mm/s | No | No | Flat (Z up) | 30 min | 8g |
| bearing_test_piece | 0.2mm | 5 | 60% gyroid | 5 | 35 mm/s | No | No | Bearing bore up (Z) | 20 min | 6g |
| tube_socket_test | 0.2mm | 5 | 60% gyroid | 5 | 35 mm/s | No | No | Socket opening up | 15 min | 5g |
| **Wheels** | | | | | | | | | | |
| rover_wheel_v3 (x6) | 0.2mm | 3 | 25% gyroid | 4 | 45 mm/s | No | No | Tread face on bed | 50 min ea | 22g ea |
| rover_tire (x6) | -- | -- | -- | -- | -- | -- | -- | CTC cannot print TPU | -- | -- |
| **Steering** | | | | | | | | | | |
| steering_bracket (x4) | 0.16mm | 5 | 60% gyroid | 5 | 35 mm/s | No | No | Bearing seat on top | 50 min ea | 15g ea |
| fixed_wheel_mount (x2) | 0.2mm | 4 | 50% gyroid | 5 | 40 mm/s | No | No | Motor pocket opening up | 30 min ea | 8g ea |
| servo_mount (x4) | 0.2mm | 4 | 50% gyroid | 4 | 40 mm/s | No | No | Servo pocket opening up | 30 min ea | 10g ea |
| steering_knuckle (x4) | 0.2mm | 4 | 50% gyroid | 5 | 40 mm/s | No | No | Motor pocket opening up | 30 min ea | 8g ea |
| steering_horn_link (x4) | 0.2mm | 3 | 30% gyroid | 4 | 40 mm/s | No | No | Flat (Z up) | 10 min ea | 2g ea |
| **Suspension** | | | | | | | | | | |
| rocker_hub_connector (x2) | 0.16mm | 5 | 60% gyroid | 5 | 35 mm/s | No | No | Bearing bore up (Z) | 50 min ea | 18g ea |
| bogie_pivot_connector (x2) | 0.16mm | 5 | 60% gyroid | 5 | 35 mm/s | No | No | Bearing bore up (Z) | 50 min ea | 16g ea |
| front_wheel_connector (x4) | 0.2mm | 4 | 50% gyroid | 5 | 40 mm/s | No | No | Tube socket opening up | 45 min ea | 12g ea |
| middle_wheel_connector (x2) | 0.2mm | 4 | 50% gyroid | 5 | 40 mm/s | No | No | Tube socket opening up | 45 min ea | 14g ea |
| differential_pivot_housing (x1) | 0.16mm | 5 | 60% gyroid | 5 | 35 mm/s | See note | No | Bearing bore up (Z) | 60 min | 20g |
| cable_clip (x12) | 0.2mm | 3 | 30% gyroid | 3 | 45 mm/s | No | No | U-channel up | 8 min ea | 1g ea |
| **Body** | | | | | | | | | | |
| body_quadrant_fl (x1) | 0.2mm | 4 | 20% gyroid | 4 | 45 mm/s | Pivot boss | 8mm brim | Flat (exterior down) | 8 hrs | 60g |
| body_quadrant_fr (x1) | 0.2mm | 4 | 20% gyroid | 4 | 45 mm/s | Pivot boss | 8mm brim | Flat (exterior down) | 8 hrs | 60g |
| body_quadrant_rl (x1) | 0.2mm | 4 | 20% gyroid | 4 | 45 mm/s | Pivot boss | 8mm brim | Flat (exterior down) | 10 hrs | 70g |
| body_quadrant_rr (x1) | 0.2mm | 4 | 20% gyroid | 4 | 45 mm/s | Pivot boss | 8mm brim | Flat (exterior down) | 10 hrs | 70g |
| top_deck_fl (x1) | 0.2mm | 3 | 20% grid | 4 | 50 mm/s | No | 5mm brim | Flat (exterior down) | 60 min | 12g |
| top_deck_fr (x1) | 0.2mm | 3 | 20% grid | 4 | 50 mm/s | No | 5mm brim | Flat (exterior down) | 60 min | 12g |
| top_deck_rl (x1) | 0.2mm | 3 | 20% grid | 4 | 50 mm/s | No | 5mm brim | Flat (exterior down) | 60 min | 12g |
| top_deck_rr (x1) | 0.2mm | 3 | 20% grid | 4 | 50 mm/s | No | 5mm brim | Flat (exterior down) | 60 min | 12g |
| **Small Parts** | | | | | | | | | | |
| electronics_tray (x1) | 0.2mm | 3 | 30% gyroid | 4 | 45 mm/s | No | No | Flat (open side up) | 3 hrs | 35g |
| strain_relief_clip (x10) | 0.2mm | 3 | 50% gyroid | 3 | 45 mm/s | No | No | U-channel up | 12 min ea | 2g ea |
| fuse_holder_bracket (x1) | 0.2mm | 3 | 40% gyroid | 3 | 45 mm/s | No | No | Flat | 30 min | 5g |
| switch_mount_plate (x1) | 0.2mm | 4 | 60% gyroid | 4 | 40 mm/s | No | No | Flat | 20 min | 4g |
| battery_tray (x1) | 0.2mm | 4 | 40% gyroid | 4 | 40 mm/s | No | No | Open side up | 45 min | 10g |

**Notes on supports**:
- Body quadrants: The rocker pivot boss protrudes inward at a Z-height of 60mm. Depending on overhang angle, this boss may require tree supports inside the body cavity. Check in Cura preview. Supports should be configured for easy removal (0.3mm Z-gap, 50% support density, zigzag pattern).
- Differential pivot housing: If the flanges create overhangs >45 degrees, enable support for those areas only (paint-on supports in Cura).
- All other parts are designed with self-supporting geometry (overhangs <45 degrees, per EA-29 Section 3.5).

### 7.3 Batch Printing Opportunities

When printing multiple copies of the same part, place them on the bed simultaneously to save time on heat-up, bed adhesion prep, and post-processing setup. CTC Bizer bed (225x145mm) can fit:

| Batch | Parts per Bed | Total Prints | Notes |
|-------|--------------|-------------|-------|
| 6x cable clips | 6 | 2 beds | Small enough to tile 2x3 |
| 4x steering_horn_links | 4 | 1 bed | Very small parts, tile easily |
| 2x steering_brackets | 2 | 2 beds | 35x30mm each, fit side by side |
| 2x front_wheel_connectors | 2 | 2 beds | Moderate size |
| 6x rover_wheels | 2-3 per bed | 2-3 beds | 80x80mm each, 2 fit on 225x145 |
| 10x strain_relief_clips | 10 | 1 bed | Very small, tile all at once |

---

## 8. Risk Register

### 8.1 Tolerance and Fitment Risks

| ID | Risk | Likelihood | Impact | Mitigation | Fallback |
|----|------|-----------|--------|------------|----------|
| T-01 | Bearing seat too tight (608ZZ won't enter) | Medium | High | Calibration print #2 catches this. Adjust `BEARING_OD` +0.05mm per iteration. Max 3 iterations. | Ream printed bore with 22mm drill bit by hand. Not ideal (damages chamfer) but functional. |
| T-02 | Bearing seat too loose (608ZZ falls out) | Low | High | Decrease `BEARING_OD` -0.05mm. PLA usually shrinks, so too-loose is uncommon. | Apply thin layer of CA glue or thread-lock to outer race before insertion. Permanent but effective. |
| T-03 | Tube socket too tight (8mm rod won't enter) | Medium | Medium | Calibration print #3 catches this. Adjust `TUBE_BORE` +0.05mm. | Ream with 8mm drill bit. |
| T-04 | Tube socket too loose (rod rattles) | Low | Medium | Decrease `TUBE_BORE` -0.05mm. Grub screw should compensate for minor looseness. | Wrap rod end with 1 layer of PTFE tape before insertion. |
| T-05 | N20 motor clip too tight (motor cracks PLA) | Low | Medium | Phase 2 Test Set D validates this. Adjust `N20_W`/`N20_H` +0.05mm. | Warm the clip with a heat gun (80 C, below PLA glass transition) to soften slightly during insertion. |
| T-06 | SG90 servo pocket wrong size | Low | Low | Phase 2 Test Set D validates this. Adjust `SG90_W`/`SG90_D`. | File the pocket opening wider. SG90 pockets are drop-in, not press-fit, so tolerance is less critical. |
| T-07 | Heat-set inserts crack the PLA | Medium | Medium | Phase 2 Test Set E validates process. Use 170 C (not 180+). Ensure >=2.4mm wall around insert. | If cracking occurs: reduce temp to 160 C. If still cracking: increase `INSERT_BORE` by 0.1mm for a gentler melt zone. Alternatively, switch to epoxy-in inserts (no heat required). |
| T-08 | Heat-set inserts pull out under bolt load | Low | Medium | Ensure 60%+ infill around insert locations. Perpendicular-to-layer orientation preferred. | Replace with M3 nut epoxied into a pocket (more work but higher pull-out strength). |

### 8.2 Geometric and Alignment Risks

| ID | Risk | Likelihood | Impact | Mitigation | Fallback |
|----|------|-----------|--------|------------|----------|
| G-01 | Body quadrants don't align at seams | Medium | High | Phase 4 Sub-Assembly C validates this with 2 quadrants. Check tongue-and-groove, bolt holes, and dowel pin locations. | File seam edges for better fit. Add 0.5mm packing shims (cardboard or PLA strips) at gaps. Worst case: re-design seam with looser tolerances and fill gap with epoxy putty. |
| G-02 | Body quadrant exceeds CTC Bizer bed size | Low (pre-verified) | Critical | RL/RR quadrants pre-verified at 140x220mm (fits 145x225mm bed with 5mm margin). Slice in Cura and check preview before printing. | If unexpectedly too large: enable "trim to bed" in Cura, or add a trim plane in the BodyQuadrant script to shave 5mm from the exceeding dimension. |
| G-03 | Bolt spacing mismatch between mating parts | Low (post-audit) | High | EA-29 Section 4.3 documented and fixed the 15mm vs 16mm spacing bug. Phase 2 Test Sets A and B validate all bolt interfaces. | If discovered: fix the script with mismatched spacing, re-export, reprint only the wrong part. |
| G-04 | Bearing boss Z-height doesn't match suspension geometry | Low | High | Phase 4 Sub-Assembly C checks that the body's bearing boss at Z=60mm aligns with the rocker hub connector geometry. | Shim with printed spacer rings if off by <2mm. Re-design if off by more. |
| G-05 | Steering hard stops don't limit rotation correctly | Medium | Low | Phase 4 Sub-Assembly B tests full steering sweep. Hard stops should engage at +/-35 deg. | If hard stops are in the wrong place: file down or add material (CA glue + baking soda fills small gaps). |

### 8.3 Printer Risks

| ID | Risk | Likelihood | Impact | Mitigation | Fallback |
|----|------|-----------|--------|------------|----------|
| P-01 | CTC Bizer fails to print after years of storage | Medium | Critical | Pre-print master plan Phase 3 covers full printer setup: belt tension, rod cleaning, nozzle check, bed levelling. Calibration test card is the first print for this reason. | Service or replace the machine. Budget impact: ~GBP 50-100 for parts, or ~GBP 180 for a new Ender 3 V3 SE. |
| P-02 | Large body panels warp off bed | Medium | Medium | Use 60 C bed, glue stick, 8mm brim. Print with door/window closed (no drafts). First layer at 20 mm/s. | If warping persists: try painter's tape + glue combo. Increase brim to 12mm. Reduce infill to 15% to lower internal stress. |
| P-03 | Filament quality issues (bubbles, inconsistent diameter) | Low | Medium | Use reputable PLA brand (eSun, Hatchbox, etc.). Store in sealed bag with desiccant. | Dry filament in oven at 45 C for 4-6 hours. If still bad, replace spool. |
| P-04 | GPX conversion produces incorrect x3g | Low | Medium | Test with calibration card first. Verify GPX version (`gpx --version` should be 2.6.8). Machine type must be `cr1d`. | Try alternate machine types (`r1d`, `r1`). Check GPX GitHub issues for CTC Bizer-specific problems. |
| P-05 | SD card read errors | Low | Low | Use a known-good SD card (4GB-16GB, FAT32 format). | Try different SD card. Reformat to FAT32. Some Sailfish printers are picky about card size (use <=8GB). |

---

## 9. Go/No-Go Checklist

### 9.1 Phase Gate: Ready to Begin Full Print Campaign

All of the following must be true before printing the remaining parts:

**Printer Calibration**:
- [ ] CTC Bizer prints cleanly (no layer shifts, no under-extrusion, no warping on calibration card)
- [ ] Calibration test card dimensions within +/-0.3mm on all axes
- [ ] GPX conversion workflow confirmed working (gcode -> x3g -> SD -> print)
- [ ] Bed levelling verified (consistent first layer across entire bed)

**Critical Fits**:
- [ ] 608ZZ bearing fits bearing_test_piece at Rating A or B
- [ ] 8mm steel rod fits tube_socket_test at Rating A or B
- [ ] Golden dimensions recorded for bearing bore and tube bore

**Interface Validation (Phase 2)**:
- [ ] front_wheel_connector + steering_bracket bolt together correctly
- [ ] middle_wheel_connector + fixed_wheel_mount bolt together correctly
- [ ] differential_pivot_housing bearing bore and diff bar bore validated
- [ ] SG90 servo fits servo_mount pocket
- [ ] N20 motor clips into steering_knuckle and fixed_wheel_mount
- [ ] Steering horn link 20mm c/c pin holes verified
- [ ] At least 2 heat-set inserts successfully installed and tested

**Structural (Phase 3)**:
- [ ] Tube socket twist test passed (no cracking)
- [ ] Bearing boss compression test passed (no deformation)
- [ ] N20 motor clip retention test passed (motor stays in)
- [ ] Heat-set insert pull-out test passed (insert holds under bolt torque)

**Sub-Assembly (Phase 4, minimum)**:
- [ ] Steering corner assembled and sweeps +/-35 deg without binding
- [ ] At least 1 body quadrant printed, bed fit confirmed, bearing boss verified

### 9.2 Filament Budget Summary

| Testing Phase | Parts | Filament | Print Time |
|--------------|-------|----------|------------|
| Phase 1: Calibration | 3 prints + up to 9 reprints | ~19g base + ~52g reprints max = ~71g | ~2.5 hrs max |
| Phase 2: Interface validation | 8 parts | ~89g | ~5 hrs |
| Phase 3: Load testing | (reuse Phase 2 parts) | 0g | 0 hrs (hand tests) |
| Phase 4: Sub-assembly | 1 new connector + 2 body quadrants | ~145g | ~18 hrs |
| **Total testing** | | **~305g max** | **~25.5 hrs max** |
| **Remaining full campaign** | ~65 parts | ~700g | ~47 hrs |
| **Project total** | ~76 parts | **~1005g (~1 spool)** | **~72 hrs** |

The testing phases consume about 30% of the total filament budget and 35% of the total print time. This is a worthwhile investment: the alternative is discovering a tolerance error after printing 6 wheels, 4 steering brackets, and 4 steering knuckles (28 parts, ~160g, ~8 hours) that all need reprinting.

### 9.3 Abort Criteria

Stop the testing process and reassess if any of the following occur:

| Condition | Action |
|-----------|--------|
| CTC Bizer cannot achieve +/-0.3mm dimensional accuracy after calibration | Investigate: belt tension, stepper driver issues, nozzle wear. Consider replacing printer. |
| Bearing bore cannot achieve Rating B after 3 iterations of BEARING_OD adjustment | Printer may have axis-specific scaling error. Measure X vs Y bore independently. Calibrate steps/mm. |
| Any structural test causes a clean fracture (PLA snaps) | Infill/wall settings are inadequate. Increase to 80% infill, 6 walls for that part. If still fracturing: the part design needs reinforcement (thicker walls, gussets). |
| Body quadrant warps badly during print (>2mm lift at corners) | Adhesion strategy needs improvement. Try: more glue, roughened painter's tape, slower first layer (15 mm/s), enclosure (cardboard box around printer). |
| Multiple shared-constant adjustments conflict (bearing needs bigger, tube needs smaller) | Printer may have different X/Y scaling. Calibrate per-axis steps/mm in firmware. |

---

## 10. Testing Timeline

Assuming the CTC Bizer is set up and filament is loaded (per Pre-Print Master Plan Phase 3):

| Day | Activity | Duration | Cumulative |
|-----|----------|----------|------------|
| 1 AM | Phase 1: Print and test calibration card | 1 hr | 1 hr |
| 1 AM | Phase 1: Print and test bearing test piece | 30 min | 1.5 hrs |
| 1 AM | Phase 1: Print and test tube socket test | 30 min | 2 hrs |
| 1 PM | Phase 1: Iterate if needed (up to 3 reprints) | 2 hrs max | 4 hrs |
| 1 PM | Phase 2 Set A: Print front_wheel_connector + steering_bracket | 1.5 hrs | 5.5 hrs |
| 1 PM | Phase 2 Set A+E: Test all interfaces + heat-set inserts | 30 min | 6 hrs |
| 2 AM | Phase 2 Set B: Print middle_wheel_connector + fixed_wheel_mount | 1.25 hrs | 7.25 hrs |
| 2 AM | Phase 2 Set C: Print differential_pivot_housing | 1 hr | 8.25 hrs |
| 2 AM | Phase 2 Set D: Print steering_knuckle + servo_mount + horn_link | 1.25 hrs | 9.5 hrs |
| 2 PM | Phase 2: Test all interfaces | 1 hr | 10.5 hrs |
| 2 PM | Phase 3: All hand tests | 30 min | 11 hrs |
| 2 PM | Phase 4 Sub-Assembly A+B: Assemble and test | 1 hr | 12 hrs |
| 3 | Phase 4 Sub-Assembly C: Print body_quadrant_fl (overnight) | 8 hrs | 20 hrs |
| 4 | Phase 4 Sub-Assembly C: Print body_quadrant_fr (overnight) | 8 hrs | 28 hrs |
| 5 AM | Phase 4 Sub-Assembly C: Test body seam alignment | 1 hr | 29 hrs |
| 5 AM | Go/No-Go review | 30 min | 29.5 hrs |

**Total testing duration**: ~3-5 days (including overnight body prints).

After the Go/No-Go gate passes, the remaining ~47 hours of printing can proceed with high confidence that every part will fit, every bearing will seat, and every bolt will align.

---

## Appendix A: Measurement Recording Template

Copy this template for each test print session:

```
DATE: ___________
PART: ___________
STL FILE: ___________
SLICER: Cura _____ (version)
SETTINGS: Layer=___mm, Walls=___, Infill=___%, Speed=___mm/s
FILAMENT: PLA _____ (brand/colour)
NOZZLE TEMP: ___C    BED TEMP: ___C
PRINT TIME (actual): ___min
FILAMENT USED: ___g

MEASUREMENTS:
  Feature 1 (___________): Target=___mm, Actual=___mm, Dev=___mm
  Feature 2 (___________): Target=___mm, Actual=___mm, Dev=___mm
  Feature 3 (___________): Target=___mm, Actual=___mm, Dev=___mm

FITMENT TEST:
  Component tested: ___________
  Rating: ___  (A/B/C/D/E)
  Notes: ___________

ACTION:
  [ ] PASS — proceed to next test
  [ ] ADJUST — change ___________ from ___ to ___ in rover_cad_helpers.py
  [ ] REPRINT — iteration #___
  [ ] INVESTIGATE — ___________
```

## Appendix B: Quick-Reference Card for Shared Constants

Print this and keep it next to the printer:

```
rover_cad_helpers.py — CRITICAL DIMENSIONS
==========================================
608ZZ Bearing Seat:   BEARING_OD    = 22.15mm  (adjust ±0.05mm)
608ZZ Seat Depth:     BEARING_DEPTH =  7.2mm
608ZZ Shaft Bore:     BEARING_BORE  =  8.1mm
Tube Socket Bore:     TUBE_BORE     =  8.2mm   (adjust ±0.05mm)
Tube Socket Depth:    TUBE_DEPTH    = 15.0mm
Heat-Set Insert Bore: INSERT_BORE   =  4.8mm   (adjust ±0.1mm)
N20 Motor Clip:       N20_W/H       = 12.2×10.2mm
SG90 Servo Pocket:    SG90_W/D      = 22.4×12.2mm
Corner Radius:        CORNER_R      =  2.0mm
Standard Fillet:      FILLET_STD    =  0.5mm
Entry Chamfer:        CHAMFER_STD   =  0.3mm
```

---

*Document EA-30 v1.0 -- 2026-03-25 (CAD Testing Plan for Phase 1 print campaign)*
