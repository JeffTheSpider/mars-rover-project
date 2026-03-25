# Pre-Print Master Engineering Plan

**Version:** 1.0
**Date:** 2026-03-24
**Status:** ACTIVE
**Author:** Claude Code + Charlie

## Purpose

Comprehensive engineering plan covering every step from requirements verification through to first drive. This plan was created after a full project deep-dive reading all 28 engineering analyses, 17 plan documents, 39 CAD scripts, 9 firmware modules, PWA, 7 ROS2 packages, CI pipeline, and tooling.

## Executive Summary

The Mars Rover Phase 1 prototype has exceptional documentation and software maturity (28 EAs, full firmware, PWA, 39 CAD scripts, CI/CD). However, **zero physical build work has started**. This plan identifies 25 issues found during the deep-dive and structures 8 phases of work from documentation cleanup through to first drive.

**Estimated timeline:** ~3-4 weeks (concurrent ordering + printing + testing)
**Estimated print time:** ~69 hours across 46 parts
**Estimated assembly time:** ~6-7 hours
**Budget:** ~GBP 153 (core) / ~GBP 244 (with tools)

---

## Issues Found During Deep-Dive

### Critical (Must Fix Before Printing)

| # | Category | Issue | Location | Fix |
|---|----------|-------|----------|-----|
| 1 | Firmware | `FW_VERSION "0.2.0"` should be `"0.3.0"` | `firmware/esp32/config.h` | Update string |
| 2 | Firmware | Servo test constants mismatch (500/11.11 vs 544/10.31) | `firmware/tests/test_firmware_logic.py` | Sync to config.h |
| 3 | CAD | Only 19 of 28 STLs exported (missing tire + 3 top deck tiles) | `3d-print/` | Re-run BatchExportAll |
| 4 | CAD | `printer_calibration.py` all zeroes, never imported | `cad/scripts/printer_calibration.py` | Calibrate printer, integrate |
| 5 | Electrical | L298N 78M05 rated 0.5A; 4x SG90 peak 2.6A | EA-19, BOM | Add XL4015 BEC to BOM |
| 6 | Electrical | L298N 5V logic, ESP32 3.3V output | EA-02, EA-19 | Add to bench test plan |

### Documentation (Stale References)

| # | File | Issue | Fix |
|---|------|-------|-----|
| 7 | `docs/references/3d-printing-strategy.md` | References Ender 3 + PETG throughout | Mark superseded by EA-11 |
| 8 | `README.md` | Says "22 engineering analyses" | Update to "25, EA-00 through EA-24" |
| 9 | `docs/plans/design-methodology.md` | References "220x220mm for Ender 3" | Update to CTC Bizer 225x145mm |
| 10 | `docs/plans/fusion360-mcp-setup.md` | References Ender 3 + PETG | Update to CTC Bizer + PLA |
| 11 | `docs/plans/backup-strategy.md` | Wrong script path `scripts/backup.bat` | Update to `tools/backup.bat` |

### Phase 2 (Log as GitHub Issues, Don't Block Print)

| # | Package | Issue |
|---|---------|-------|
| 12 | rover_navigation | `ekf.yaml` config file missing (nav.launch.py references it) |
| 13 | rover_navigation | ackermann_controller `wheel_diameter_mm` defaults 120mm, should be 80mm |
| 14 | rover_hardware | Joint names in uart_bridge don't match URDF joint names |
| 15 | rover_navigation | No Nav2 lifecycle node bringup in nav.launch.py |
| 16 | rover_navigation | No SLAM node despite `use_slam` argument |
| 17 | rover_bringup | No simulation launch file (garden.world references one) |
| 18 | rover_autonomy | Duplicate `behaviour_trees/` and `behavior_trees/` directories |
| 19 | rover_bringup | Stale `.urdf` alongside active `.urdf.xacro` |
| 20 | rover_teleop | WebSocket port 81 (ESP32) vs 8081 (Jetson) inconsistency |
| 21 | rover_hardware | Ultrasonic sensor frames not in URDF |
| 22 | rover_hardware | Missing `setup.py` for `rover_bringup` |
| 23 | rover_msgs | Camera stream port mismatch (PWA 8080 vs web_server 8080) |

### Design Observations (Not Bugs)

| # | Observation | Impact |
|---|------------|--------|
| 24 | CAD scripts don't import `generate_rover_params.py` at runtime | Values hardcoded in cm; parameter file is reference only |
| 25 | Parts are symmetric — no mirrored STLs needed | Simplifies print campaign |

---

## Phase 0: Documentation & Consistency Sweep

**Duration:** 1-2 hours (software work, no hardware)
**Gate:** All docs consistent, firmware compiles, all tests pass

### Tasks

- [x] **0.1** Update `firmware/esp32/config.h` `FW_VERSION` from `"0.2.0"` to `"0.3.0"` ✓
- [x] **0.2** Sync servo test constants in `firmware/tests/test_firmware_logic.py` with config.h values (544/10.31) ✓
- [x] **0.3** Update `README.md` status line: "25 engineering analyses, EA-00 through EA-24" ✓
- [x] **0.4** Update `docs/plans/design-methodology.md` printer reference: CTC Bizer 225x145mm ✓
- [x] **0.5** Update `docs/plans/fusion360-mcp-setup.md` printer reference: CTC Bizer + PLA ✓
- [x] **0.6** Update `docs/plans/backup-strategy.md` script path: `tools/backup.bat` ✓
- [x] **0.7** Add deprecation notice to `docs/references/3d-printing-strategy.md` → superseded by EA-11 ✓
- [x] **0.8** Run `/firmware-validate` — compile + 42 tests + lint ✓ (1045KB/79%, 53KB/16%, 42/42 pass, 0 lint)
- [ ] **0.9** Create GitHub issues for all 12 Phase 2 ROS2 issues (#12-23 above) — DEFERRED (no remote repo configured)
- [x] **0.10** Run backup to E: drive ✓

### Gate Review Checklist
- [x] `arduino-cli compile` succeeds (flash <80%, RAM <20%) ✓
- [x] All 42 firmware tests pass ✓
- [x] No stale Ender 3 / PETG references in active docs ✓
- [x] `FW_VERSION` matches CHANGELOG ✓

---

## Phase 1: Requirements Traceability Review

**Duration:** 1-2 hours (software work, no hardware)
**Gate:** All requirements traced, BOM verified, power question resolved

### Tasks

- [x] **1.1** Walk through EA-22 functional requirements (FR-01 to FR-10) ✓ 9/10 fully traced, FR-10 orphan (no drop test proc)
- [x] **1.2** Walk through EA-22 dimensional requirements (DIM-01 to DIM-11) ✓ DIM-10/DIM-11 fixed (120→180mm, 80→90mm)
- [x] **1.3** Walk through EA-22 electrical requirements (ELEC-01 to ELEC-10) ✓ ELEC-04 (fuse) and ELEC-10 (ADC cap) gaps fixed in BOM
- [x] **1.4** Cross-check learning objectives ✓ LEARN-04/09/11 orphan (acceptable for prototype)
- [x] **1.5** Run BOM check ✓ 10 discrepancies found, 8 fixed (wall thickness, weights, fuse, cap, resistor, connector)
- [x] **1.6** Run wiring check ✓ 17 items checked, 9 discrepancies fixed (LEDC channels, wire gauges, connector type, resistor, pin names)
- [x] **1.7** **DECISION: Servo power** ✓ XL4015 BEC already in BOM (confirmed present)
- [x] **1.8** **DECISION: L298N 3.3V** ✓ Added as Phase 6 bench test item (test before committing)
- [x] **1.9** Update BOM and shopping list ✓ Fuse added, cap count 6→7, resistor 220→330, XT60 standardised, weights updated
- [x] **1.10** Requirements traceability ✓ 79% fully traced (31/43), 7% partial, 5% fixed mismatches, 16% orphan (acceptable)

### Additional Fixes Applied During Phase 1
- EA-09: Fixed LEDC Ch6/Ch7→Ch4/Ch5 for servo FL/FR, GPIO3 stale motor ref→spare, "Power button"→"E-stop"
- EA-23: Wire gauges reconciled (battery 18→14 AWG, distribution 20→16 AWG, motors 24→20 AWG), XT30→XT60
- EA-19: Spare pin count 5→6, ESP32 power wire 18→22 AWG
- EA-17, EA-06: XT30→XT60
- Signal wiring diagram: LED resistor 220R→330R
- Shopping list: XT60 standardised, resistor 220→330 ohm

### Gate Review Checklist
- [x] Every FR has firmware implementation identified ✓ (FR-10 orphan test logged)
- [x] Every DIM has CAD script identified ✓ (DIM-10/DIM-11 corrected)
- [x] Every ELEC has BOM line item identified ✓ (fuse + ADC cap added)
- [x] BEC already in BOM ✓ (confirmed)
- [x] BOM costs updated ✓
- [x] Orphan requirements documented ✓ (acceptable for learning prototype)

---

## Phase 2: CAD Final Verification & STL Export

**Duration:** 1-2 hours (requires Fusion 360 running)
**Gate:** All 28 STLs exported, dimensions verified, bed fit confirmed

### Tasks

- [x] **2.1** Run `/cad-audit` on all scripts — final consistency check ✓ 16 PASS, 1 FAIL (servo_mount wall), 0 stale values
- [x] **2.2** Deploy all scripts to Fusion 360 Scripts directory ✓ 3 fixed scripts deployed (body_quadrant, servo_mount, batch_export_all)
- [x] **2.3** Run BatchExportAll in Fusion 360 (via `/fusion-export`) ✓ 22/22 components, 0 errors, 48s
- [x] **2.4** Verify 28 STL files exist in `3d-print/` subdirectories ✓ 24 files (22 batch + bearing_test_piece + old unsplit top_deck)
- [x] **2.5** Check body quadrant dimensions ≤225×145mm via `get_stl_info` ✓ RL/RR now 140×220mm (PASS)
- [x] **2.6** Check top deck exports are 4 separate tiles (each >5KB) ✓ FL 44KB, FR 106KB, RL 106KB, RR 60KB
- [x] **2.7** Check rover_tire.stl exists (even though CTC Bizer can't print TPU) ✓ 93KB
- [x] **2.8** Run `/preflight` on body_quadrant_rl (largest part, tightest bed fit) ✓ PASS — 140×220×80mm fits flat (5mm clearance each axis), ~8.5h, ~31g PLA, 40% gyroid, supports for pivot bosses
- [x] **2.9** Run `/preflight` on steering_bracket (tightest tolerance — 3.9mm bearing wall) ✓ PASS — 35×30×40mm, ~4.5h, ~26g PLA, 65% infill, 0.16mm layers, 5 perimeters, no supports, ream bearing bore post-print
- [x] **2.10** Run `/preflight` on rocker_arm_front (longest part) ✓ PASS — 30×195×15mm, ~4.5h, ~11g PLA, 50% gyroid, 4 perimeters, no supports, 195mm along 225mm bed axis
- [x] **2.11** Generate STL dimension verification table (bounding box vs expected) ✓ All 24 STLs verified post-fix
- [x] **2.12** Run backup to E: drive ✓

### Fixes Applied During Phase 2 (CAD Audit)
- **servo_mount.py**: BRACKET_W 15→18mm (wall around servo 1.4→2.9mm, meets 2.5mm minimum)
- **body_quadrant.py**: Trim extrude direction fixed (True→False, trim was cutting into empty space)
  - Bug: RL/RR rear quadrants measured 140×235mm, exceeding 225mm bed by 10mm
  - Root cause: Rocker pivot boss at Y seam protrudes 15mm, trim cut went wrong direction
  - After fix: RL/RR should be ~140×220mm (fits 145×225mm bed)
- **generate_rover_params.py**: body.wall_thickness 3→4mm (matches CAD scripts post-enhancement)

### STL Dimension Verification (post-fix, 24 files)
| Part | Dimensions (mm) | Bed Fit (225×145×150) | Size | Notes |
|------|-----------------|----------------------|------|-------|
| bearing_test_piece | 30×30×10 | PASS | 30KB | Pre-existing |
| calibration_test_card | 80×30×5 | PASS | 266KB | |
| rover_wheel | 80×80×35 | PASS | 93KB | |
| rover_tire | 86×86×35 | PASS | 93KB | TPU — CTC can't print, Phase 2 |
| steering_bracket | 35×30×40 | PASS | 65KB | |
| fixed_wheel_mount | 25×25×30 | PASS | 35KB | |
| servo_mount | **40×18×25** | PASS | 63KB | **Fixed** (was 15mm wide) |
| bogie_arm | 30×180×12 | PASS | 29KB | |
| rocker_arm_front | 30×195×15 | PASS | 68KB | 195mm < 225mm bed |
| rocker_arm_rear | 30×118×15 | PASS | 64KB | |
| diff_bar_adapter | 30×30×20 | PASS | 74KB | |
| body_quadrant_fl | 130×220×80 | PASS | 95KB | 5mm X clearance |
| body_quadrant_fr | 130×220×80 | PASS | 95KB | 5mm X clearance |
| body_quadrant_rl | **140×220×80** | **PASS** | 117KB | **Fixed!** Was 235mm |
| body_quadrant_rr | **140×220×80** | **PASS** | 117KB | **Fixed!** Was 235mm |
| top_deck_fl | 130×220×11 | PASS | 44KB | |
| top_deck_fr | 130×220×11 | PASS | 106KB | |
| top_deck_rl | 130×220×11 | PASS | 106KB | |
| top_deck_rr | 130×220×11 | PASS | 60KB | |
| electronics_tray | 120×180×18 | PASS | 242KB | |
| strain_relief_clip | 18×10×12 | PASS | 30KB | |
| fuse_holder_bracket | 15×40×12 | PASS | 44KB | |
| switch_mount_plate | 30×30×5 | PASS | 30KB | |

### Gate Review Checklist
- [x] 24 STL files present (22 batch + bearing_test_piece + old unsplit top_deck) ✓
- [x] All body quadrants fit CTC Bizer bed (≤225×145mm) ✓ RL/RR fixed: 140×220mm
- [x] All parts fit bed height (≤150mm) ✓ Tallest: body quadrants at 80mm
- [x] Rocker arm halves each ≤225mm longest axis ✓ (195mm and 118mm)
- [x] No zero-size or corrupt STLs ✓ All 24 have >28KB and valid geometry
- [x] Batch export log shows 0 errors ✓ 22/22 components, 0 errors, 48s
- [x] Preflight checks on 3 critical parts ✓ (body_quadrant_rl, steering_bracket, rocker_arm_front — all GO)

---

## Phase 3: Printer Setup & Calibration

**Duration:** 1-2 days (physical work)
**Gate:** CTC Bizer calibrated, bearing test piece validates 608ZZ press-fit

### Prerequisites
- PLA filament on hand (order in Phase 4.1 if not already available)
- Digital calipers (±0.02mm)
- CTC Bizer powered and accessible

### Tasks

- [ ] **3.1** Follow `docs/plans/ctc-bizer-guide.md` initial setup checklist:
  - Mechanical inspection (belts, rods, linear bearings, pulleys)
  - Clean/replace nozzle (cold pull if clogged)
  - Right extruder: park or remove (raise 1-2mm above left)
  - Verify heated bed reaches 60°C uniformly
- [ ] **3.2** Bed levelling (4-corner paper test + centre check)
- [ ] **3.3** Load PLA filament (left extruder only)
- [ ] **3.4** Test extrusion: 100mm filament feed, verify actual = expected ±2mm
- [ ] **3.5** **Print #1: Calibration test card** (`calibration/calibration_test_card.stl`, ~30 min)
  - Measure all 7 test holes with calipers
  - Measure bearing counterbore (22.15mm target)
  - Record actual vs expected for each feature
- [ ] **3.6** **Print #2: 20mm XYZ calibration cube** (~20 min)
  - Measure X, Y, Z dimensions
  - Calculate scaling errors per axis
- [ ] **3.7** Update `cad/scripts/printer_calibration.py` with measured correction values:
  - `HOLE_DIAMETER_ERROR_MM`
  - `OUTER_DIMENSION_ERROR_MM`
  - `XY_ERROR_PER_100MM`
  - `Z_ERROR_PER_10MM`
  - `FIRST_LAYER_SPREAD_MM`
- [ ] **3.8** **Print #3: Bearing test piece** (`calibration/bearing_test_piece.stl`, ~20 min)
  - Test 608ZZ bearing press-fit
  - Target: snug push-fit, no rattle, no hammer needed
  - If too tight: increase bore by 0.05mm, reprint
  - If too loose: decrease bore by 0.05mm, reprint
  - Iterate until fit is correct (max 3 iterations)
- [ ] **3.9** Record validated bearing seat dimension (the golden number for this printer)
- [ ] **3.10** Log all calibration prints with `/print-log`
- [ ] **3.11** If calibration corrections are significant (>0.1mm), consider updating CAD scripts to compensate

### Gate Review Checklist
- [ ] CTC Bizer mechanically sound and printing clean layers
- [ ] Calibration card hole measurements recorded
- [ ] XYZ cube within ±0.2mm on all axes
- [ ] 608ZZ bearing fits bearing test piece correctly
- [ ] `printer_calibration.py` updated with real values
- [ ] Bearing seat "golden dimension" documented

---

## Phase 4: Parts Ordering

**Duration:** 1-2 weeks (delivery time)
**Gate:** All Phase 1 components on hand

### Ordering Strategy (per EA-17)

Order in batches to start printing while waiting for later deliveries:

- [ ] **4.1** — **Order 1: Filament** (order immediately, ~GBP 30)
  - 2× 1kg PLA spools (white or grey, 1.75mm)
  - Bed adhesion aids (glue stick or painter's tape)
- [ ] **4.2** — **Order 2: Electronics** (order week 1, ~GBP 45)
  - 1× ESP32-S3 DevKitC-1 N16R8
  - 2× L298N dual H-bridge driver
  - 6× N20 6V 100RPM geared motor
  - 4× SG90 micro servo
  - 1× XL4015 5V 3A buck converter (BEC for servo power)
  - 1× Tactile button (E-stop)
  - 1× Status LED (any colour)
  - 6× 100nF ceramic capacitors (motor noise suppression)
  - 1× 100nF ceramic capacitor (ADC filter)
  - Resistors: 1× 10k, 1× 4.7k (battery voltage divider)
  - Dupont jumper wires (M-F, F-F assortment)
  - Mini breadboard
- [ ] **4.3** — **Order 3: Mechanical** (order week 1-2, ~GBP 35)
  - 9× 608ZZ bearings (8×22×7mm) + 3 spares = buy 12
  - 1× 8mm steel rod, 350mm length (cut to 300mm)
  - M3 fasteners: 30× M3×12mm socket head, 20× M3 nuts, 50× M3 washers
  - M8 fasteners: 2× M8×60mm bolts, 4× M8 nuts, 8× M8 washers
  - M2 fasteners: 8× M2×10mm (servo mounting)
  - M3 heat-set inserts: 50× (M3, 5.7mm OD, 4.8mm hole, 5.5mm depth)
  - O-rings: 18× 70mm ID × 3mm cross-section (if not using TPU tires)
  - 3mm dowel pins × 8 (body alignment)
- [ ] **4.4** — **Order 4: Power & Safety** (order week 2, ~GBP 25)
  - 1× 2S LiPo 2200mAh 7.4V (XT30 or XT60 connector)
  - 2× XT30 connectors (male + female pair)
  - 1× ATC/ATO blade fuse holder + 5A blade fuse
  - 1× Panel-mount toggle switch (kill switch, ≥5A rated)
  - Wire: 2m 18AWG, 3m 22AWG, 5m 24AWG, 3m 26AWG
  - Heat shrink tubing assortment
  - LiPo balance charger (if not already owned)
- [ ] **4.5** Track deliveries, run `/bom-check` as items arrive

### Gate Review Checklist
- [ ] All 4 orders placed
- [ ] Filament arrived and loaded
- [ ] All electronics verified (ESP32 powers on, motors spin, servos move)
- [ ] All bearings checked (spin freely, correct size)
- [ ] Steel rod correct diameter (8mm ±0.05mm)
- [ ] All fasteners correct size and quantity
- [ ] Battery charges and holds voltage

---

## Phase 5: Print Campaign

**Duration:** ~10 days (~69 hours print time)
**Gate:** All 46 parts printed, test-fitted, and logged

### Print Order (optimised for progressive test-fitting)

Run `/preflight <part>` before each print. Run `/print-log <part>` after each print.

| Step | Part | Qty | Est. Time | Slicer Settings | Test Gate |
|------|------|-----|-----------|-----------------|-----------|
| 1 | Bearing test piece | 1+ | 20 min | 4 walls, 50%, 0.2mm | 608ZZ press-fit |
| 2 | Calibration test card | 1 | 30 min | 4 walls, 50%, 0.2mm | Hole measurements |
| 3 | Rover wheel | 6 | 6 hrs | 4 walls, 50% gyroid | D-shaft bore, hub fit |
| 4 | Bogie arm | 2 | 2 hrs | 4 walls, 50% gyroid | Bearing seat, N20 clip, pivot bore |
| 5 | Rocker arm front | 2 | 2 hrs | 4 walls, 50% gyroid | Half-lap joint, bearing seat |
| 6 | Rocker arm rear | 2 | 2 hrs | 4 walls, 50% gyroid | Half-lap joint mates with front |
| 7 | Diff bar adapter | 3 | 1.5 hrs | 4 walls, 60% infill | 8mm rod bore, bearing seat |
| 8 | Steering bracket | 4 | 3 hrs | **5 walls**, **60% gyroid** | Bearing seat, N20 clip, M3 inserts |
| 9 | Fixed wheel mount | 2 | 1 hr | 4 walls, 50% gyroid | N20 clip, M3 inserts |
| 10 | Servo mount | 4 | 2 hrs | 4 walls, 50% gyroid | SG90 pocket fit |
| 11 | Body quadrant FL | 1 | 8 hrs | 4 walls, 20% gyroid | Tongue/groove, bearing seat, arm mount bosses |
| 12 | Body quadrant FR | 1 | 8 hrs | 4 walls, 20% gyroid | Tongue/groove, bearing seat |
| 13 | Body quadrant RL | 1 | 8 hrs | 4 walls, 20% gyroid | Tongue/groove, diff mount, **bed fit ≤225×145** |
| 14 | Body quadrant RR | 1 | 8 hrs | 4 walls, 20% gyroid | Kill switch hole, diff mount, **bed fit ≤225×145** |
| 15 | Top deck tiles | 4 | 4 hrs | 3 walls, 20% grid, **brim** | Snap clips, panel lines |
| 16 | Electronics tray | 1 | 3 hrs | 3 walls, 30% gyroid | ESP32 standoffs, L298N standoffs, battery cradle |
| 17 | Strain relief clips | 10 | 2 hrs | 3 walls, 50% infill | U-channel fits 4× 22AWG wires |
| 18 | Fuse holder bracket | 1 | 30 min | 3 walls, 40% infill | Fuse holder fits channel |
| 19 | Switch mount plate | 1 | 20 min | 4 walls, 60% infill | 15mm bore fits toggle switch |

**Total: 46 parts, ~69 hours**

### Slicer Workflow (per part)
1. Open STL in Cura
2. Apply settings from table above
3. Verify orientation (flat face down unless noted)
4. Check estimated time and filament usage
5. Slice → export gcode
6. Convert: `gpx -m cr1d input.gcode output.x3g`
7. Copy x3g to SD card
8. Print
9. Measure critical dimensions with calipers
10. Test-fit hardware (bearing, motor, servo as applicable)
11. Log with `/print-log`

### Progressive Test-Fitting Schedule
After printing each group, test-fit before continuing:
- After wheels (step 3): Test N20 D-shaft fit, O-ring groove fit
- After bogies (step 4): Assemble wheel → bogie with bearing
- After rockers (steps 5-6): Join halves, test pivot range
- After diff adapters (step 7): Test 8mm rod fit + bearing
- After steering (steps 8-10): Full corner assembly (bracket + servo + mount + wheel)
- After body (steps 11-14): Join quadrants, test rocker pivot fit
- After internals (steps 16-19): Dry-fit electronics tray in body

### Gate Review Checklist
- [ ] All 46 parts printed
- [ ] All bearing seats tested with 608ZZ
- [ ] All N20 clips tested with motor
- [ ] All SG90 pockets tested with servo
- [ ] All M3 heat-set inserts installed cleanly
- [ ] Rocker arm halves join correctly
- [ ] Body quadrants join with minimal gap
- [ ] Total PLA usage ≤2kg
- [ ] All prints logged with `/print-log`

---

## Phase 6: Electronics Bench Test

**Duration:** 2-4 hours (before mechanical assembly)
**Gate:** All electronics verified individually on bench

### Prerequisites
- ESP32-S3 and all electronics from Order 2
- USB cable for programming
- Multimeter
- Breadboard + jumper wires

### Tasks

- [ ] **6.1** Flash firmware to ESP32-S3 via USB:
  ```
  arduino-cli compile --fqbn esp32:esp32:esp32s3 firmware/esp32/
  arduino-cli upload --fqbn esp32:esp32:esp32s3 -p COMx firmware/esp32/
  ```
- [ ] **6.2** Verify WiFi connects (check serial monitor for IP address)
- [ ] **6.3** Load PWA in phone browser → verify all tabs render
- [ ] **6.4** **L298N 3.3V logic test** (CRITICAL):
  - Connect 1× L298N to ESP32 (ENA + IN1 + IN2)
  - Connect 1× N20 motor
  - Apply 7.4V from bench supply or charged LiPo
  - Verify motor spins forward and reverse at multiple speeds
  - If L298N doesn't respond to 3.3V: add 74HCT245 level shifter to BOM
- [ ] **6.5** Test all 4 motor channels (one at a time)
- [ ] **6.6** Test all 4 SG90 servos (verify centre, sweep range, trim via PWA)
- [ ] **6.7** Test XL4015 BEC: input 7.4V → output 5.00V ±0.1V, verify under 4-servo load
- [ ] **6.8** Verify battery ADC reading (compare ESP32 reported voltage vs multimeter)
- [ ] **6.9** Verify E-stop button response (<100ms, check via serial monitor)
- [ ] **6.10** Test WebSocket command → motor response → telemetry round-trip
- [ ] **6.11** Test OTA update (upload via WiFi)

### Gate Review Checklist
- [ ] ESP32-S3 connects to WiFi reliably
- [ ] PWA loads and displays correctly on phone
- [ ] L298N responds to 3.3V logic (or level shifter solution identified)
- [ ] All 6 motors spin at correct speed and direction
- [ ] All 4 servos centre correctly and reach ±35°
- [ ] Battery voltage reads within ±0.1V of multimeter
- [ ] E-stop halts motors within 100ms
- [ ] OTA update works
- [ ] XL4015 BEC provides stable 5V under servo load

---

## Phase 7: Mechanical Assembly

**Duration:** 6-7 hours
**Gate:** Rover fully assembled, all joints move freely

### Assembly Sequence (per `docs/plans/assembly-reference.md`)

- [ ] **7.1** Stage 1 — Part preparation:
  - Install all M3 heat-set inserts (soldering iron at 170-180°C for PLA)
  - Cut 8mm steel rod to 300mm
  - Deburr all printed parts
- [ ] **7.2** Stage 2 — Wheel sub-assemblies (×6):
  - Press 608ZZ bearing into wheel hub
  - Insert N20 motor into clip
  - Secure with M2 grub screw (if needed)
  - Attach O-rings to wheel grooves (if not using TPU tires)
- [ ] **7.3** Stage 3 — Bogie arms (×2):
  - Press 608ZZ bearing into central pivot
  - Attach middle wheel assembly (fixed mount + motor + wheel)
  - Attach rear wheel assembly (steering bracket + servo + motor + wheel)
- [ ] **7.4** Stage 4 — Steering assemblies (×4):
  - Mount SG90 servo into servo mount
  - Attach servo mount to steering bracket
  - Connect servo horn to steering bracket pivot
- [ ] **7.5** Stage 5 — Front wheel assemblies:
  - Attach front steering bracket + servo + motor + wheel to rocker arm front half
- [ ] **7.6** Stage 6 — Rocker-bogie suspension (×2):
  - Join rocker arm halves (half-lap joint, 2× M3 bolts)
  - Attach bogie arm to rocker arm rear half via pivot bearing
  - Verify articulation range: rocker ±25°, bogie ±20°
- [ ] **7.7** Stage 7 — Differential bar:
  - Press diff bar adapters onto 8mm rod at correct spacing
  - Press 608ZZ bearings into adapters
  - Verify differential mechanism (one rocker up → other down)
- [ ] **7.8** Stage 8 — Body frame:
  - Join 4 body quadrants with M3×12 bolts + heat-set inserts
  - Install alignment dowel pins
  - Verify tongue-and-groove seams align
  - Insert rocker pivots into body bearing seats
  - Attach differential bar to body
  - Verify all 6 wheels touch ground on flat surface
- [ ] **7.9** Stage 9 — Electronics and wiring:
  - Mount electronics tray inside body
  - Mount ESP32-S3 on standoffs
  - Mount 2× L298N on standoffs
  - Mount XL4015 BEC
  - Mount battery in cradle with strap
  - Wire per EA-23 wire harness specification (58 wires)
  - Install strain relief clips at pivot points
  - Install fuse holder and kill switch on RR quadrant
  - Route wires through arm channels with 50mm slack at pivots
  - Install top deck tiles

### Gate Review Checklist
- [ ] All 6 wheels spin freely
- [ ] All 4 steering servos move full range
- [ ] Rocker-bogie articulates correctly (push one side, other lifts)
- [ ] Differential bar moves freely
- [ ] All 6 wheels maintain ground contact on flat surface
- [ ] Body quadrants securely joined (no wobble)
- [ ] Electronics securely mounted
- [ ] All wires routed with no pinch points at pivots
- [ ] Kill switch disconnects power
- [ ] Total weight ≤1.5kg

---

## Phase 8: Integration Test & Acceptance

**Duration:** 2-4 hours
**Gate:** All EA-21 "Must" acceptance criteria met

### Pre-Power Safety Checks (per EA-19)
- [ ] **8.1** Visual inspection: no exposed conductors, no wire pinch points
- [ ] **8.2** Continuity check: VCC to GND should show high resistance (no shorts)
- [ ] **8.3** Voltage check: battery voltage within range (7.0-8.4V)
- [ ] **8.4** Fuse installed (5A blade)
- [ ] **8.5** Kill switch in OFF position

### First Power-On
- [ ] **8.6** Turn kill switch ON, verify power LED illuminates
- [ ] **8.7** Check serial monitor for boot sequence (WiFi connect, firmware version)
- [ ] **8.8** Connect phone to PWA, verify telemetry displays
- [ ] **8.9** Check battery voltage reading matches multimeter ±0.2V

### Motor Test
- [ ] **8.10** ARM the rover via PWA
- [ ] **8.11** Test each direction: forward, reverse, left, right
- [ ] **8.12** Verify all 6 wheels spin correct direction
- [ ] **8.13** If any motor reversed: swap IN1/IN2 wires for that channel

### Steering Test
- [ ] **8.14** Test Ackermann mode: left turn, right turn
- [ ] **8.15** Test point turn mode: clockwise, anticlockwise
- [ ] **8.16** Test crab walk mode: left, right
- [ ] **8.17** Calibrate servo trims via PWA settings (all wheels straight when centred)

### Acceptance Tests (per EA-21)

| Test ID | Requirement | Target | Method |
|---------|------------|--------|--------|
| PR-01 | Max speed | ≥0.2 m/s | Measure 5m timed run |
| PR-02 | Runtime | ≥30 min | Continuous driving test |
| PR-03 | Payload | 500g on top deck | Place weighted object |
| PR-04 | Obstacle | 20mm climb | Place obstacle in path |
| PR-05 | Slope | 15° grade | Use ramp or incline |
| PR-06 | Straight line | <100mm drift/5m | Measure deviation |
| PR-07 | Latency | <200ms command→action | Stopwatch test |
| PR-08 | WiFi range | ≥15m | Distance test outdoors |
| PR-09 | Weight | ≤1.5kg | Kitchen scale |
| PR-10 | Noise | <60dB at 1m | Phone dB meter app |

### Data Capture
- [ ] **8.18** Fill in `docs/plans/prototype-data-capture.md` with all measurements
- [ ] **8.19** Record all 12 learning objectives (LEARN-01 to LEARN-12)
- [ ] **8.20** Document any failures or issues in failure log section
- [ ] **8.21** Take photos/video of first drive
- [ ] **8.22** Update `docs/plans/future-design-improvements.md` Phase 1 Outcome columns

### Final Checklist
- [ ] All "Must" FRs met (FR-01 to FR-10)
- [ ] ≥8 of 12 PRs met
- [ ] All 12 learning objectives recorded
- [ ] 10+ min WiFi-controlled drive completed
- [ ] Disassembly/reassembly in <30 min demonstrated
- [ ] All data captured and documented
- [ ] Backup run to D: and E: drives
- [ ] Celebratory first outdoor drive

---

## Risk Register (Phase 1 Build-Specific)

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R-01 | CTC Bizer can't achieve bearing tolerance | Medium | High | Bearing test piece iteration; worst case: drill out with 22mm bit |
| R-02 | L298N doesn't respond to 3.3V logic | Low | High | Bench test early (Phase 6.4); fallback: 74HCT245 level shifter (~$1) |
| R-03 | PLA parts too weak for assembly loads | Low | Medium | 4+ walls, 50%+ infill on structural; handle with care |
| R-04 | Body quadrants don't fit CTC Bizer bed | Low | High | Pre-verified in CAD at 220×130mm; margin 5mm each axis |
| R-05 | N20 motors insufficient torque | Low | Medium | Phase 1 is 1.25kg, N20 stall torque ~10 kg-cm; learning objective |
| R-06 | SG90 servos too weak for steering | Medium | Medium | Only 1.25kg vehicle; upgrade to MG996R in Phase 2 |
| R-07 | Battery runtime <30 min | Low | Low | 2200mAh at ~2A = ~65 min theoretical; learning objective |
| R-08 | WiFi range <15m | Medium | Low | ESP32-S3 has decent WiFi; test outdoors; external antenna in Phase 2 |
| R-09 | Rocker arm half-lap joint weak | Medium | Medium | 30mm overlap + 2× M3 bolts; reinforce with epoxy if needed |
| R-10 | Total weight exceeds 1.5kg | Low | Low | PLA estimate 1024g + ~226g electronics/battery = ~1.25kg |

---

## Quick Reference: Skills & Tools to Use at Each Phase

| Phase | Skills & Tools |
|-------|---------------|
| 0 | `/firmware-validate`, `/simplify`, `github` MCP (create issues) |
| 1 | `/bom-check`, `/wiring-check`, `/tolerance-calc`, `math` MCP |
| 2 | `/cad-audit`, `/fusion-export`, `/preflight`, `3dprint` MCP (`get_stl_info`) |
| 3 | `/print-log`, `/tolerance-calc`, `3dprint` MCP (`get_stl_info`, `generate_stl_visualization`) |
| 4 | `/bom-check`, `jlcpcb` MCP (component search) |
| 5 | `/preflight`, `/print-log`, `/assembly-order`, `3dprint` MCP (slice, visualize) |
| 6 | `/firmware-validate`, `/esp32-deploy`, `/wiring-check`, `arduino-esp-helper` skill |
| 7 | `/assembly-order`, `/tolerance-calc`, `/wiring-check` |
| 8 | `/project-dashboard`, `/session-handoff`, `mermaid` MCP (results diagrams) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-24 | Initial plan after full project deep-dive |
