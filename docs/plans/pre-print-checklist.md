# Pre-Print Verification Checklist

Before committing ~72 hours of print time, verify every CAD script and dimension.

**Printer**: CTC Bizer (225×145×150mm bed, PLA, x3g via GPX)
**Date**: 2026-03-23
**Audit version**: v2.0 (post comprehensive pre-print audit)

---

## 1. CAD Script Execution Verification

All 18 scripts run via BatchExportAll. 23 STL files expected after latest changes.
**Changes since v2.0**: Wheel redesigned (spoke holes, rim lips, TPU mode), TPU tire script added,
body walls 4mm, bogie arm 3mm walls, tray corner gussets, panel line grooves, corner chamfers.

| # | Script | Status | STL Size | Notes |
|---|--------|--------|----------|-------|
| 1 | `BearingTestPiece` | PASS | 58 KB | 30mm OD, 22.15mm bore verified |
| 2 | `CalibrationTestCard` | PASS | 266 KB | 7 test holes + bearing counterbore |
| 3 | `RoverWheel` | **UPDATED** | TBD | Spoke holes, rim lips, USE_TPU_TIRE toggle (re-export needed) |
| 3b | `RoverTire` | **NEW** | TBD | TPU tire 86mm OD, 70mm bore, 48 treads (re-export needed) |
| 4 | `SteeringBracket` | PASS | 65 KB | 608ZZ seat, motor clip, 8mm bore |
| 5 | `DiffBarAdapter` | PASS | 73 KB | 608ZZ seat, 8mm bore, 30mm boss OD |
| 6 | `BogieArm` | **UPDATED** | TBD | 180mm span, 3mm walls (was 2.5mm), re-export needed |
| 7 | `RockerArm` | PASS | 67+64 KB | TWO-PIECE: front 195mm + rear 118mm (105+boss), lap joint |
| 8 | `FixedWheelMount` | PASS | 35 KB | N20 clip, M3 bolt holes, zip-tie slot |
| 9 | `ServoMount` | PASS | 58 KB | SG90 pocket, M2 holes, 12mm circular horn slot |
| 10 | `ElectronicsTray` | **UPDATED** | TBD | Corner gussets added, re-export needed |
| 11 | `BodyQuadrant` (×4) | **UPDATED** | TBD | 4mm walls, panel line grooves, corner chamfers added, re-export needed |
| 12 | `TopDeck` (×4) | **UPDATED** | TBD | Panel line grid on top surface added, re-export needed |
| 13 | `StrainReliefClip` | PASS | 30 KB | U-channel, snap tab |
| 14 | `FuseHolderBracket` | PASS | 45 KB | 8mm clip channel, end walls |
| 15 | `SwitchMountPlate` | PASS | 30 KB | 15mm bore, M3 diagonal holes |

---

## 2. STL Dimensional Verification (all 19 current files)

Measured via `get_stl_info` bounding box. All dimensions in mm.

| Part | Expected | STL Actual | Bed Fit | Status |
|------|----------|------------|---------|--------|
| calibration_test_card | 80×30×5 | 80×30×5.4 | 80×30 YES | PASS |
| bearing_test_piece | 30×30×10 | 30×30×10 | 30×30 YES | PASS |
| rover_wheel | 86×86×32 | 86×86×32 | 86×86 YES | PASS |
| steering_bracket | 35×30×40 | 35×30×40 | 35×30 YES | PASS |
| fixed_wheel_mount | 25×25×30 | 25×25×30 | 25×25 YES | PASS |
| servo_mount | 40×15×25 | 40×15×25 | 40×15 YES | PASS |
| bogie_arm | 30×180×12 | 29.9×180×12 | 180×30 YES | PASS |
| rocker_arm_front | 30×195×15 | 30×195×15 | 195×30 YES | PASS |
| rocker_arm_rear | 30×118×15 | 30×118×15 | 118×30 YES | PASS (105mm arm + 13mm boss) |
| diff_bar_adapter | 30×30×20 | 30×30×20 | 30×30 YES | PASS |
| body_quadrant_fl | 130×220×80 | 130×220×80 | 220×130 YES | PASS |
| body_quadrant_fr | 130×220×80 | 130×220×80 | 220×130 YES | PASS |
| body_quadrant_rl | ≤225×145 | **140×235** | **NO** | **FAIL — script fixed (trim cut)** |
| body_quadrant_rr | ≤225×145 | **140×235** | **NO** | **FAIL — script fixed (trim cut)** |
| top_deck | 130×220×3 | 130×220×8 | 220×130 YES | **FAIL — only 1 tile, hollow (104 faces). Script fixed** |
| electronics_tray | 120×180×18 | 120×180×18 | 180×120 YES | PASS |
| strain_relief_clip | 18×10×11.5 | 18×10×11.5 | 18×10 YES | PASS (10mm body + 1.5mm snap tab) |
| fuse_holder_bracket | 15×40×12 | 15×40×12 | 40×15 YES | PASS |
| switch_mount_plate | 30×30×5 | 30×30×5 | 30×30 YES | PASS |

---

## 3. Hardware Fitment Verification

### 608ZZ Bearing Seats (9 locations)

| Script | Bore (mm) | Depth (mm) | Boss OD (mm) | Status |
|--------|-----------|------------|--------------|--------|
| steering_bracket | 22.15 | 7.2 | N/A (bracket width) | PASS |
| bogie_arm | 22.15 | 7.2 | 30.0 | PASS |
| rocker_arm (body pivot) | 22.15 | 7.2 | 30.0 | PASS |
| rocker_arm (bogie pivot) | 22.15 | 7.2 | 26.0 | PASS |
| diff_bar_adapter (×3) | 22.15 | 7.2 | 30.0 | PASS |
| body_quadrant RL/RR | 22.15 | 7.2 | 30.0 | PASS |

All 608ZZ seats: **22.15mm bore × 7.2mm depth** (0.15mm clearance, 0.2mm depth extra). PASS.

### N20 Motor Clips (6 locations)

| Script | Pocket (mm) | Shaft Exit | Status |
|--------|-------------|------------|--------|
| steering_bracket (×4) | 12.2×10.2×25 | 4.0mm hole | PASS |
| fixed_wheel_mount (×2) | 12.2×10.2×25 | 4.0mm hole + zip-tie | PASS |
| bogie_arm (×2 ends) | 12.2×10.2 | Open top cut | PASS |

All N20 clips: **12.2×10.2mm** (0.2mm clearance). PASS.

### SG90 Servo Pockets (4 locations)

| Script | Pocket (mm) | Tab Span | M2 Holes | Horn Slot | Status |
|--------|-------------|----------|----------|-----------|--------|
| servo_mount (×4) | 22.4×12.2×12 | 32.4mm | 27.5mm spacing, 2.4mm dia | 12mm circular | PASS |

### Heat-Set Insert Holes

All scripts use **4.8mm diameter × 5.5mm deep** for M3 × 5.7mm OD inserts. PASS.

| Location | Count |
|----------|-------|
| Body quadrant seams | ~22 |
| Steering bracket | 2 per part (×4 = 8) |
| Fixed wheel mount | 2 per part (×2 = 4) |
| Servo mount | 2 per part (×4 = 8) |
| **Total** | **~42** |

### D-Shaft Bore (6 wheels)

Wheel hub bore: **3.1mm** (0.1mm clearance on 3mm shaft), **0.5mm D-flat**, **M2 grub screw** (2mm × 5mm deep radial). PASS.

### 8mm Pivot Bores

All pivot parts have **8.0mm through-bore**: steering_bracket, bogie_arm, rocker_arm, diff_bar_adapter. PASS.

---

## 4. Cable Routing Verification

### Wire Features in Scripts

| Script | Feature | Dimensions | Status |
|--------|---------|------------|--------|
| bogie_arm | Wire routing slot | 5×4mm along boss | PASS |
| electronics_tray | Floor wire channels (×4) | 10mm wide × 3mm deep | PASS |
| electronics_tray | Wall cable exits (×3) | 10×5mm rectangular slots | PASS |
| body_quadrant | Side wall cable exits | 10×5mm slots (2 per RL/RR, 1 per FL/FR) | PASS |
| body_quadrant | Cable channel ridges | 10mm wide × 10mm tall | PASS |

### Wire Count Through Body Walls

- Motor wires: 6 motors × 2 wires = 12
- Servo wires: 4 servos × 3 wires = 12
- Encoder wires: 6 encoders × 2 wires = 12 (optional Phase 1)
- Power: 2 wires
- **Total**: ~26-38 wires through body walls

Cable exits: 6 slots (2 per rear quad + 1 per front quad) × 10×5mm = adequate for wire bundles with strain relief clips.

---

## 5. Discrepancies Found & Fixed

| # | Issue | Fix Applied | Severity |
|---|-------|-------------|----------|
| B1 | body_quadrant RL/RR 140×235mm > 225mm bed | Added Step 4b trim cut in body_quadrant.py | **CRITICAL — fixed** |
| B2 | top_deck: only 1 tile exported (FL hardcoded) | Updated batch_export_all.py with 4-tile TopDeck handler | **CRITICAL — fixed** |
| B3 | top_deck: 104 faces / 5KB hollow shell | Fixed lip/clip/rib extrusion direction (downward from panel) | **CRITICAL — fixed** |
| D1 | Shopping list O-ring: "30-40mm OD" should be "70mm ID × 3mm" | Fixed in phase1-shopping-list.md | Medium |
| D2 | Shopping list bearing count: 10 should be 11 | Fixed in phase1-shopping-list.md | Low (both say buy 12) |
| D3 | Shopping list heat-set insert OD/L swapped: "OD 4.6mm, L 5mm" → "OD 5.7mm, L 4.6mm" | Fixed in phase1-shopping-list.md | Medium |
| D4 | Diff bar rod 200mm vs rocker pivot span 250mm | **RESOLVED — rod updated to 300mm** | Medium |

### Resolved: Diff Bar Rod Length

The 8mm steel rod was updated from 200mm to 300mm. The rocker pivot span is 250mm (±125mm). The 300mm rod provides 25mm overhang each side for diff bar adapters. Shopping list, BOM, CAD scripts, URDF, and assembly reference all updated to 300mm.

---

## 6. Left/Right Mirroring Check

All parts are symmetric about at least one axis. No mirrored STLs needed — just flip on print bed.

| Part | Symmetric? | L/R Handling |
|------|-----------|--------------|
| Steering bracket | Yes (about Y and X) | Print 4x, same orientation |
| Fixed wheel mount | Yes | Print 2x, same orientation |
| Bogie arm | Yes (about length axis) | Print 2x, same orientation |
| Rocker arm front | Yes (about length axis) | Print 2x, same orientation |
| Rocker arm rear | Yes (about length axis) | Print 2x, same orientation |
| Servo mount | Yes | Print 4x, same orientation |
| Body quadrant FL/FR | Mirror pair | Separate STLs (FL, FR) |
| Body quadrant RL/RR | Mirror pair | Separate STLs (RL, RR) |

---

## 7. Part Count & Quantity Summary

| Part | Qty Needed | STL Files | Print Copies | Status |
|------|-----------|-----------|--------------|--------|
| Calibration test card | 1 | 1 | 1 | OK |
| Bearing test piece | 1 | 1 | 1 | OK |
| Rover wheel | 6 | 1 | 6 | OK |
| Steering bracket | 4 | 1 | 4 | OK |
| Fixed wheel mount | 2 | 1 | 2 | OK |
| Servo mount | 4 | 1 | 4 | OK |
| Bogie arm | 2 | 1 | 2 | OK |
| Rocker arm front | 2 | 1 | 2 | OK |
| Rocker arm rear | 2 | 1 | 2 | OK |
| Diff bar adapter | 3 | 1 | 3 | OK |
| Body quadrant FL | 1 | 1 | 1 | OK |
| Body quadrant FR | 1 | 1 | 1 | OK |
| Body quadrant RL | 1 | 1 | 1 | FIXED |
| Body quadrant RR | 1 | 1 | 1 | FIXED |
| Top deck tile | 4 | 4 (after fix) | 1 each | FIXED |
| Electronics tray | 1 | 1 | 1 | OK |
| Strain relief clip | 10 | 1 | 10 | OK |
| Fuse holder bracket | 1 | 1 | 1 | OK |
| Switch mount plate | 1 | 1 | 1 | OK |
| **Total** | **46 parts** | **22 files** | | |

---

## 8. Recommended Print Order

| Order | Part(s) | Est. Time | Why This Order |
|-------|---------|-----------|----------------|
| 1 | Calibration test card | 30min | Verify printer accuracy |
| 2 | Bearing test piece | 15min | Test 608ZZ press-fit before committing |
| 3 | 1× Wheel + 1× Steering bracket | 2h45m | Test motor fit, bearing fit, assembly |
| 4 | 1× Servo mount | 20min | Test SG90 fit |
| 5 | Remaining 5× Wheels | 10hr | Batch if fit is good |
| 6 | 3× Steering brackets + 2× Fixed mounts | 3.5hr | Complete wheel mounts |
| 7 | 3× Servo mounts | 1hr | Complete servo mounts |
| 8 | 2× Bogie arms | 3hr | Suspension assembly |
| 9 | 2× Rocker front + 2× rear halves | 5hr | Suspension (split design) |
| 10 | 3× Diff bar adapters | 1.5hr | Differential bar |
| 11 | Electronics tray | 3hr | Wire + test electronics |
| 12 | Body quadrant FL | 8hr | Start body (overnight) |
| 13 | Body quadrant FR | 8hr | Continue body |
| 14 | Body quadrant RL | 10hr | Largest piece (overnight) |
| 15 | Body quadrant RR | 10hr | Has kill switch hole |
| 16 | 4× Top deck tiles | 4hr | Cosmetic last |
| 17 | 10× Strain relief clips | 1.5hr | Batch print |
| 18 | Fuse bracket + Switch plate | 30min | Small parts, last |

**Total estimated print time: ~72 hours** (~3 days continuous or ~5 days practical)

---

## 9. Pre-First-Print Checklist

- [ ] CTC Bizer powered on, bed levelled
- [ ] PLA filament loaded (left extruder only)
- [ ] Right nozzle removed or parked (prevent scratching)
- [ ] Bed adhesion: glue stick or painter's tape applied
- [ ] Bed temp: 60°C
- [ ] Nozzle temp: 200-210°C (PLA)
- [ ] SD card available with x3g files
- [ ] GPX conversion tested: `gpx -m cr1d test.gcode test.x3g`
- [ ] Cura profile set for CTC Bizer (0.4mm nozzle, 0.2mm layer height)
- [ ] First print: calibration test card or bearing test piece

---

## 10. Slicer Settings Reference

| Setting | Value | Notes |
|---------|-------|-------|
| Layer height | 0.2mm | Standard quality |
| Nozzle diameter | 0.4mm | Stock CTC nozzle |
| Perimeters/walls | 3 (body panels), 4 (structural brackets) | |
| Infill | 20% gyroid (body), 30% (tray), 40-60% (brackets) | |
| Top/bottom layers | 4 | |
| Supports | Off for most parts, on for overhangs >45° | |
| Bed temp | 60°C | PLA on heated bed |
| Nozzle temp | 205°C | Adjust ±5° for your filament |
| Speed | 40-50 mm/s | CTC Bizer is not fast |
| Brim | 5mm for large parts (body quadrants) | Bed adhesion |
| Retraction | 1-2mm at 25mm/s | Direct drive (not Bowden) |

---

## 11. Post-Audit Action Items

1. ~~**Deploy fixed scripts**~~ DONE — body_quadrant.py, top_deck.py, batch_export_all.py deployed to Fusion 360 Scripts folder
2. **Re-run BatchExportAll** in Fusion 360 to regenerate all STLs (RL/RR quadrants trimmed + LED/light holes, 4× top deck tiles with FR phone mount)
3. **Verify** re-exported STLs via `get_stl_info` (RL/RR must be ≤225×145mm, top deck >5KB each, body quadrants have new holes)
4. **Verify diff bar rod length** during assembly (300mm rod, 250mm pivot span, 25mm overhang each side)
5. **Backup** all files to D:\Backup and E:\Backup

### Phase 1 Enhancement Features Added (2026-03-23)
- **LED underglow holes**: 4× 5mm diameter pass-throughs in body quadrant floor (15mm inset from outer wall)
- **Headlight holes**: 2× 5mm diameter through front wall of FL/FR quadrants (40mm apart, 60% up wall)
- **Taillight holes**: 2× 5mm diameter through rear wall of RL/RR quadrants (40mm apart, 60% up wall)
- **Phone holder mount**: 4× M3 heat-set insert bosses on FR top deck tile (8mm OD × 3mm tall, 60×80mm pattern)

---

*Pre-Print Checklist v2.0 — 2026-03-23 (post-audit)*
