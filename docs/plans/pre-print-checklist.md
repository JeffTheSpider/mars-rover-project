# Pre-Print Verification Checklist

Before committing ~72 hours of print time, verify every CAD script, dimension, and interface.

**Printer**: CTC Bizer (225×145×150mm bed, PLA, x3g via GPX)
**Date**: 2026-03-25
**Version**: v3.0 (post EA-28 systems integration)
**Integration ref**: EA-28 (docs/engineering/28-systems-integration.md), EA-29 (CAD redesign)

---

## 1. CAD Script Execution Verification

29 STL exports from BatchExportAll across 6 stages. **All 29/29 STLs exported successfully** (2026-03-25, arc direction bug fixed and all STLs regenerated).

### Stage 1: Calibration (3 parts)

| # | Script | Export Name | Qty | Status |
|---|--------|------------|-----|--------|
| 1 | `CalibrationTestCard` | calibration_test_card.stl | 1 | EXPORTED |
| 2 | `BearingTestPiece` | bearing_test_piece.stl | 1 | EXPORTED |
| 3 | `TubeSocketTest` | tube_socket_test.stl | 1 | EXPORTED |

### Stage 2: Wheels (2 scripts, 12 parts)

| # | Script | Export Name | Qty | Status |
|---|--------|------------|-----|--------|
| 4 | `RoverWheelV3` | rover_wheel_v3.stl | 6 | EXPORTED |
| 5 | `RoverTire` | rover_tire.stl | 6 (TPU) | EXPORTED (CTC Bizer cannot print TPU — use O-rings or order externally) |

### Stage 3: Steering & Mounts (5 scripts, 18 parts)

| # | Script | Export Name | Qty | Status |
|---|--------|------------|-----|--------|
| 6 | `SteeringBracket` | steering_bracket.stl | 4 | EXPORTED |
| 7 | `FixedWheelMount` | fixed_wheel_mount.stl | 2 | EXPORTED |
| 8 | `ServoMount` | servo_mount.stl | 4 | EXPORTED |
| 9 | `SteeringKnuckle` | steering_knuckle.stl | 4 | EXPORTED |
| 10 | `SteeringHornLink` | steering_horn_link.stl | 4 | EXPORTED |

### Stage 4: Suspension Connectors (6 scripts, 23 parts)

| # | Script | Export Name | Qty | Status |
|---|--------|------------|-----|--------|
| 11 | `RockerHubConnector` | rocker_hub_connector.stl | 2 | EXPORTED |
| 12 | `BogiePivotConnector` | bogie_pivot_connector.stl | 2 | EXPORTED |
| 13 | `FrontWheelConnector` | front_wheel_connector.stl | 4 | EXPORTED |
| 14 | `MiddleWheelConnector` | middle_wheel_connector.stl | 2 | EXPORTED |
| 15 | `DifferentialPivotHousing` | differential_pivot_housing.stl | 1 | EXPORTED |
| 16 | `CableClip` | cable_clip.stl | 12 | EXPORTED |

### Stage 5: Body (2 scripts, 8 parts)

| # | Script | Export Name | Qty | Status |
|---|--------|------------|-----|--------|
| 17a | `BodyQuadrant` (FL) | body_quadrant_fl.stl | 1 | EXPORTED |
| 17b | `BodyQuadrant` (FR) | body_quadrant_fr.stl | 1 | EXPORTED |
| 17c | `BodyQuadrant` (RL) | body_quadrant_rl.stl | 1 | EXPORTED (trimmed for bed fit) |
| 17d | `BodyQuadrant` (RR) | body_quadrant_rr.stl | 1 | EXPORTED (trimmed for bed fit) |
| 18a | `TopDeck` (FL) | top_deck_fl.stl | 1 | EXPORTED |
| 18b | `TopDeck` (FR) | top_deck_fr.stl | 1 | EXPORTED (phone mount bosses) |
| 18c | `TopDeck` (RL) | top_deck_rl.stl | 1 | EXPORTED |
| 18d | `TopDeck` (RR) | top_deck_rr.stl | 1 | EXPORTED |

### Stage 6: Small Parts (3 scripts, 12 parts)

| # | Script | Export Name | Qty | Status |
|---|--------|------------|-----|--------|
| 19 | `ElectronicsTray` | electronics_tray.stl | 1 | EXPORTED |
| 20 | `StrainReliefClip` | strain_relief_clip.stl | 10 | EXPORTED |
| 21 | `FuseHolderBracket` | fuse_holder_bracket.stl | 1 | EXPORTED |
| 22 | `SwitchMountPlate` | switch_mount_plate.stl | 1 | EXPORTED |

**Total: 29 STL exports, ~76 printed parts** (excluding TPU tires)

> **BatchExportAll Status**: COMPLETE (2026-03-25). All 29/29 STLs exported successfully after CAD redesign. Arc direction bug was fixed and all STLs regenerated. All scripts now include fillets, chamfers, and use shared `cad_helpers.py` module. See EA-29 for full redesign documentation.

---

## 2. Hardware Fitment Verification

All dimensions from EA-28 Section 3 cross-domain interface matrix.

### 608ZZ Bearing Seats (9 locations — EA-28 M-01 to M-07)

| Location | Host Part | Bore | Depth | Boss OD | Status |
|----------|-----------|------|-------|---------|--------|
| Body L rocker pivot | body_quadrant RL | 22.15mm | 7.2mm | 30mm | Pending |
| Body R rocker pivot | body_quadrant RR | 22.15mm | 7.2mm | 30mm | Pending |
| Body diff centre | body (centre) | 22.15mm | 7.2mm | 30mm | Pending |
| L rocker-to-bogie | bogie_pivot_connector | 22.15mm | 7.2mm | 30mm | Pending |
| R rocker-to-bogie | bogie_pivot_connector | 22.15mm | 7.2mm | 30mm | Pending |
| FL steering pivot | steering_bracket | 22.15mm | 7.2mm | N/A | Pending |
| FR steering pivot | steering_bracket | 22.15mm | 7.2mm | N/A | Pending |
| RL steering pivot | steering_bracket | 22.15mm | 7.2mm | N/A | Pending |
| RR steering pivot | steering_bracket | 22.15mm | 7.2mm | N/A | Pending |

### Tube Socket Interfaces (all connectors — EA-28 M-04 to M-06)

| Feature | Dimension | Tolerance |
|---------|-----------|-----------|
| Bore | 8.2mm | ±0.1mm |
| Depth | 15mm | ±0.5mm |
| M3 grub hole | 3.0mm × 6mm deep | ±0.1mm |
| Minimum wall | ≥4mm | — |

### N20 Motor Clips (6 locations)

| Part | Pocket (W×H×D) | Shaft Exit |
|------|-----------------|------------|
| steering_knuckle (×4) | 12.2×10.2×25mm | 4.0mm hole |
| fixed_wheel_mount (×2) | 12.2×10.2×25mm | 4.0mm hole + zip-tie |

### SG90 Servo Pockets (4 locations)

| Part | Pocket | Tab Span | M2 Holes | Horn Slot |
|------|--------|----------|----------|-----------|
| servo_mount (×4) | 22.4×12.2×12mm | 32.4mm | 27.5mm spacing | 12mm circular |

### Heat-Set Insert Holes (~40 total)

All holes: **4.8mm diameter × 5.5mm deep** for M3 × 5.7mm OD brass inserts.
Install temperature: **170-180°C** (PLA — lower than PETG's 200-220°C).

### Shaft Bores

| Feature | Dimension | Parts |
|---------|-----------|-------|
| 608ZZ shaft bore | 8.1mm | All bearing locations |
| Wheel hub D-shaft | 3.1mm + 0.5mm D-flat | rover_wheel_v3 |
| D-shaft M2 grub screw | 2mm × 5mm deep radial | rover_wheel_v3 |

---

## 3. Bed Fit Verification

All parts must fit within CTC Bizer: **225×145×150mm**.

| Part | Largest Dimension | Bed Footprint | Fits? |
|------|-------------------|---------------|-------|
| body_quadrant_fl | 220×130×80mm | 220×130 | YES |
| body_quadrant_fr | 220×130×80mm | 220×130 | YES |
| body_quadrant_rl | ≤225×145×80mm | ≤225×145 | YES (trim cut applied) |
| body_quadrant_rr | ≤225×145×80mm | ≤225×145 | YES (trim cut applied) |
| electronics_tray | 120×180×18mm | 180×120 | YES |
| rover_wheel_v3 | 86×86×32mm | 86×86 | YES |
| rocker_hub_connector | ~45×40×35mm | 45×40 | YES |
| All other parts | <100mm any axis | <100mm | YES |

---

## 4. Integration Verification (EA-28 Cross-Reference)

### Mechanical Interfaces

- [ ] Diff bar length 300mm fits body width (250mm pivot span + 25mm overhang each side)
- [ ] Rocker tube angles match `generate_rover_params.py` values
- [ ] All tube sockets accept 8mm rod with slide fit
- [ ] Horn link 20mm c/c matches servo horn + knuckle arm geometry
- [ ] Hard stop channels allow ±35° rotation
- [ ] All parts symmetric — no mirrored STLs needed (L/R flip on bed)

### Electrical Clearances

- [ ] Wire channel 8×6mm accommodates wire bundles at each joint
- [ ] Body cable exits (10×5mm × 6 slots) align with wire routing
- [ ] Electronics tray standoffs align with ESP32 + L298N mounting holes
- [ ] Kill switch bore (15mm) in rear body wall
- [ ] Battery tray recess fits 2S LiPo (86×34×19mm)

### Assembly Compatibility

- [ ] Body quadrant join seams align (M3 bolt holes match)
- [ ] Rocker pivot boss Z-height matches suspension geometry (Z=60mm)
- [ ] All M3 bolt holes clear heat-set insert positions
- [ ] Strain relief clips fit on wire bundles

---

## 5. Pre-First-Print Checklist

- [ ] CTC Bizer powered on and bed levelled
- [ ] PLA filament loaded (left extruder only)
- [ ] Right nozzle removed or parked (prevent scratching)
- [ ] Bed adhesion: glue stick or painter's tape applied
- [ ] Bed temp: 60°C
- [ ] Nozzle temp: 200-210°C (PLA)
- [ ] SD card available with x3g files
- [ ] GPX conversion tested: `gpx -m cr1d test.gcode test.x3g`
- [ ] Cura profile set for CTC Bizer (0.4mm nozzle, 0.2mm layer)
- [ ] First print: calibration test card (verify dimensional accuracy)
- [ ] Second print: bearing test piece (verify 608ZZ press-fit)
- [ ] Third print: tube socket test (verify 8mm rod slide fit)

---

## 6. Slicer Settings Reference

| Setting | Structural Parts | Body Panels | Small Parts |
|---------|-----------------|-------------|-------------|
| Layer height | 0.2mm | 0.2mm | 0.2mm |
| Nozzle | 0.4mm | 0.4mm | 0.4mm |
| Walls | 4-5 | 3-4 | 3 |
| Infill | 40-60% gyroid | 20% gyroid | 30% gyroid |
| Top/bottom layers | 4 | 4 | 4 |
| Supports | Off (most parts) | Off | Off |
| Bed temp | 60°C | 60°C | 60°C |
| Nozzle temp | 205°C ±5 | 205°C ±5 | 205°C ±5 |
| Speed | 40-50 mm/s | 40-50 mm/s | 40-50 mm/s |
| Brim | None | 5-8mm (body quads) | None |
| Retraction | 1-2mm @ 25mm/s | 1-2mm @ 25mm/s | 1-2mm @ 25mm/s |

**File workflow**: Fusion 360 → STL → Cura → gcode → `gpx -m cr1d input.gcode output.x3g` → SD card

---

## 7. Print Order (Recommended)

| Order | Part(s) | Qty | Est. Time | Purpose |
|-------|---------|-----|-----------|---------|
| 1 | Calibration test card | 1 | 30 min | Verify printer accuracy |
| 2 | Bearing test piece | 1 | 15 min | Test 608ZZ press-fit |
| 3 | Tube socket test | 1 | 15 min | Test 8mm rod fit |
| 4 | 1× Wheel + 1× Steering bracket | 2 | 3 hrs | Test motor fit, bearing fit |
| 5 | 1× Servo mount + 1× Horn link | 2 | 45 min | Test SG90 fit, link geometry |
| 6 | Remaining 5× Wheels | 5 | 10 hrs | Batch overnight |
| 7 | 3× Steering brackets + 2× Fixed mounts | 5 | 4 hrs | Complete wheel mounts |
| 8 | 3× Servo mounts + 3× Horn links | 6 | 2 hrs | Complete steering |
| 9 | 4× Steering knuckles | 4 | 3 hrs | Test with bracket + bearing |
| 10 | Connectors (hub, bogie, front, middle, diff) | 11 | 8 hrs | Suspension connectors |
| 11 | 12× Cable clips | 12 | 2 hrs | Batch print |
| 12 | Electronics tray | 1 | 3 hrs | Wire test before body |
| 13 | Body quadrant FL | 1 | 8 hrs | Start body (overnight) |
| 14 | Body quadrant FR | 1 | 8 hrs | Overnight |
| 15 | Body quadrant RL | 1 | 10 hrs | Largest (overnight, trimmed) |
| 16 | Body quadrant RR | 1 | 10 hrs | Kill switch hole (overnight) |
| 17 | 4× Top deck tiles | 4 | 4 hrs | Cosmetic last |
| 18 | 10× Strain relief + fuse + switch | 12 | 2 hrs | Small parts, last |

**Total estimated print time: ~72 hours** (~3 days continuous or ~5 days practical)

---

## 8. Post-Print Assembly Verification

After all parts printed, before assembly:

- [ ] All bearing test piece fits verified (608ZZ, 8mm rod, tube socket)
- [ ] Heat-set inserts installed in all parts (~40 inserts at 170-180°C)
- [ ] 8mm steel rods cut to length (13 segments from 2× 1m rods)
- [ ] Rod ends deburred with file
- [ ] All parts labelled (L/R, FL/FR/RL/RR)
- [ ] Refer to EA-17 (Build Guide) for step-by-step assembly
- [ ] Refer to EA-28 (Integration) for interface verification

---

*Pre-Print Checklist v3.1 — 2026-03-25 (post CAD redesign, 29/29 STLs exported, EA-29)*
