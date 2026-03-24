# Phase 1 Prototype Data Capture Template

Record all measurements, observations, and issues during the build and test campaign.
This document is the single source of truth for prototype performance data.

**Started**: ____-__-__
**Firmware version**: v______
**PLA filament brand/colour**: ________________
**Printer**: CTC Bizer (225x145x150mm bed)

---

## 1. Build Log

Record time, issues, and observations for each assembly stage (per assembly-reference.md).

| Date | Stage | Time (min) | Issues | Photos | Notes |
|------|-------|-----------|--------|--------|-------|
| | Stage 1: Prepare printed parts (clean, heat-set inserts, shaft prep) | | | | |
| | Stage 2: Wheel sub-assemblies (x6 wheels + motors + grub screws) | | | | |
| | Stage 3: Bogie arms (x2 bogies + bearings + motor clips) | | | | |
| | Stage 4: Rocker arms (x2 rockers, 2-piece join, bearings) | | | | |
| | Stage 5: Steering assemblies (x4 brackets + servos + bearings) | | | | |
| | Stage 6: Differential bar (rod + 3 adapters + bearings) | | | | |
| | Stage 7: Body frame (4 quadrants joined, suspension mounted) | | | | |
| | Stage 8: Electronics tray (ESP32, L298N x2, breadboard, battery) | | | | |
| | Stage 9: Wiring and firmware (all connections, upload, first test) | | | | |
| | **Total** | **___** | | | |

---

## 2. Dimensional Verification

Measure each printed part after printing and compare to EA-08 design dimensions.
Use digital calipers. All values in millimetres.

### 2.1 Body Quadrants

| Part | Dimension | Expected (mm) | Measured (mm) | Delta (mm) | Pass? |
|------|-----------|--------------|--------------|--------|-------|
| Body FL | Length (Y) | 220 | | | |
| Body FL | Width (X) | 130 | | | |
| Body FL | Height (Z) | 80 | | | |
| Body FL | Wall thickness | 4.0 | | | |
| Body FR | Length (Y) | 220 | | | |
| Body FR | Width (X) | 130 | | | |
| Body FR | Height (Z) | 80 | | | |
| Body FR | Wall thickness | 4.0 | | | |
| Body RL | Length (Y) | 220 | | | |
| Body RL | Width (X) | 130 | | | |
| Body RL | Height (Z) | 80 | | | |
| Body RL | Wall thickness | 4.0 | | | |
| Body RR | Length (Y) | 220 | | | |
| Body RR | Width (X) | 130 | | | |
| Body RR | Height (Z) | 80 | | | |
| Body RR | Wall thickness | 4.0 | | | |

### 2.2 Bearing Seats (608ZZ: 22mm OD x 7mm W)

| Part | Seat bore (mm) | Expected (mm) | Seat depth (mm) | Expected (mm) | Fit quality |
|------|---------------|--------------|-----------------|--------------|-------------|
| Body FL rocker pivot | | 22.15 | | 7.2 | |
| Body FR rocker pivot | | 22.15 | | 7.2 | |
| Rocker L (body pivot) | | 22.15 | | 7.2 | |
| Rocker L (bogie pivot) | | 22.15 | | 7.2 | |
| Rocker R (body pivot) | | 22.15 | | 7.2 | |
| Rocker R (bogie pivot) | | 22.15 | | 7.2 | |
| Bogie L (centre pivot) | | 22.15 | | 7.2 | |
| Bogie R (centre pivot) | | 22.15 | | 7.2 | |
| Diff bar adapter 1 | | 22.15 | | 7.2 | |
| Diff bar adapter 2 | | 22.15 | | 7.2 | |
| Diff bar adapter 3 | | 22.15 | | 7.2 | |
| Steering bracket FL | | 22.15 | | 7.2 | |
| Steering bracket FR | | 22.15 | | 7.2 | |
| Steering bracket RL | | 22.15 | | 7.2 | |
| Steering bracket RR | | 22.15 | | 7.2 | |

**Fit quality key**: Tight (needs press/hammer), Firm (press by hand), Loose (falls out), Cracked

### 2.3 Wheels

| Part | Dimension | Expected (mm) | Measured (mm) | Delta (mm) | Pass? |
|------|-----------|--------------|--------------|--------|-------|
| Wheel 1 (FL) | Outer diameter | 80.0 | | | |
| Wheel 1 (FL) | Width | 32.0 | | | |
| Wheel 1 (FL) | Hub bore (D-shaft) | 3.1 | | | |
| Wheel 2 (ML) | Outer diameter | 80.0 | | | |
| Wheel 2 (ML) | Width | 32.0 | | | |
| Wheel 2 (ML) | Hub bore (D-shaft) | 3.1 | | | |
| Wheel 3 (RL) | Outer diameter | 80.0 | | | |
| Wheel 4 (RR) | Outer diameter | 80.0 | | | |
| Wheel 5 (MR) | Outer diameter | 80.0 | | | |
| Wheel 6 (FR) | Outer diameter | 80.0 | | | |

### 2.4 Suspension Arms

| Part | Dimension | Expected (mm) | Measured (mm) | Delta (mm) | Pass? |
|------|-----------|--------------|--------------|--------|-------|
| Rocker L front half | Length | 195 | | | |
| Rocker L front half | Cross-section W | 20 | | | |
| Rocker L front half | Cross-section H | 15 | | | |
| Rocker L rear half | Length | 105 | | | |
| Rocker R front half | Length | 195 | | | |
| Rocker R rear half | Length | 105 | | | |
| Bogie L | Length (total) | 180 | | | |
| Bogie L | Cross-section W | 15 | | | |
| Bogie L | Cross-section H | 12 | | | |
| Bogie L | Wall thickness | 3.0 | | | |
| Bogie R | Length (total) | 180 | | | |

### 2.5 Steering & Motor Mounts

| Part | Dimension | Expected (mm) | Measured (mm) | Delta (mm) | Pass? |
|------|-----------|--------------|--------------|--------|-------|
| Steering bracket FL | N20 clip ID (W) | 12.2 | | | |
| Steering bracket FL | N20 clip ID (H) | 10.2 | | | |
| Steering bracket FL | SG90 pocket W | 22.4 | | | |
| Steering bracket FL | SG90 pocket D | 12.2 | | | |
| Fixed mount ML | N20 clip ID (W) | 12.2 | | | |
| Fixed mount MR | N20 clip ID (W) | 12.2 | | | |

### 2.6 Other Parts

| Part | Dimension | Expected (mm) | Measured (mm) | Delta (mm) | Pass? |
|------|-----------|--------------|--------------|--------|-------|
| Top deck FL | Length (Y) | 220 | | | |
| Top deck FL | Width (X) | 130 | | | |
| Top deck FL | Thickness | 3.0 | | | |
| Top deck FR | Phone mount boss spacing (long) | 80 | | | |
| Top deck FR | Phone mount boss spacing (short) | 60 | | | |
| Electronics tray | Length (Y) | 180 | | | |
| Electronics tray | Width (X) | 120 | | | |
| Electronics tray | LiPo recess (L x W x D) | 70x35x25 | | | |
| Diff bar adapter | Boss OD | 30 | | | |
| Diff bar adapter | 8mm bore | 8.0 | | | |

### 2.7 Overall Assembly

| Measurement | Expected (mm) | Measured (mm) | Delta (mm) | Pass? |
|-------------|--------------|--------------|--------|-------|
| Body overall length (Y) | 440 | | | |
| Body overall width (X) | 260 | | | |
| Body overall height (Z) | 80 | | | |
| Wheelbase front-to-rear (Y) | 360 | | | |
| Track width centre-to-centre (X) | 280 | | | |
| Ground clearance (under body) | 60 | | | |
| Diff bar rod length | 300 | | | |

---

## 3. Weight Log

Weigh each sub-assembly and compare to BOM estimates.
Use kitchen scale (1g resolution preferred).

| Sub-Assembly | Expected (g) | Measured (g) | Delta (g) | Notes |
|-------------|-------------|-------------|-------|-------|
| **Wheels** | | | | |
| Wheel 1 (FL) — PLA rim only | ~35 | | | |
| Wheel 2 (ML) | ~35 | | | |
| Wheel 3 (RL) | ~35 | | | |
| Wheel 4 (RR) | ~35 | | | |
| Wheel 5 (MR) | ~35 | | | |
| Wheel 6 (FR) | ~35 | | | |
| TPU tire (if used) x6 | ~60 total | | | 10g each |
| **Suspension** | | | | |
| Rocker arm front half L | ~18 | | | |
| Rocker arm rear half L | ~10 | | | |
| Rocker arm front half R | ~18 | | | |
| Rocker arm rear half R | ~10 | | | |
| Bogie arm L | ~15 | | | |
| Bogie arm R | ~15 | | | |
| Diff bar adapter x3 | ~24 total | | | ~8g each |
| **Steering & Mounts** | | | | |
| Steering bracket FL | ~12 | | | |
| Steering bracket FR | ~12 | | | |
| Steering bracket RL | ~12 | | | |
| Steering bracket RR | ~12 | | | |
| Fixed mount ML | ~8 | | | |
| Fixed mount MR | ~8 | | | |
| Servo mount x4 | ~20 total | | | ~5g each |
| **Body** | | | | |
| Body quadrant FL | ~80 | | | |
| Body quadrant FR | ~80 | | | |
| Body quadrant RL | ~95 | | | |
| Body quadrant RR | ~95 | | | |
| **Other Printed** | | | | |
| Top deck FL | ~15 | | | |
| Top deck FR | ~15 | | | |
| Top deck RL | ~15 | | | |
| Top deck RR | ~15 | | | |
| Electronics tray | ~40 | | | |
| Strain relief clips x10 | ~20 total | | | ~2g each |
| Fuse holder bracket | ~4 | | | |
| Switch mount plate | ~3 | | | |
| **Total PLA printed** | **~1024** | **____** | | |
| | | | | |
| **Non-Printed** | | | | |
| N20 motors x6 | ~120 | | | ~20g each |
| SG90 servos x4 | ~36 | | | ~9g each |
| 608ZZ bearings x11 | ~132 | | | ~12g each |
| M8 bolts + nuts + washers | ~50 est | | | |
| M3 hardware (all) | ~30 est | | | |
| 8mm steel rod (300mm) | ~50 est | | | |
| ESP32-S3 DevKitC-1 | ~10 | | | |
| L298N x2 | ~60 | | | ~30g each |
| 5V buck converter | ~15 | | | |
| 2S LiPo 2200mAh | ~130 | | | |
| Wiring + connectors | ~50 est | | | |
| O-rings x18 | ~20 est | | | |
| **Total non-printed** | **~693 est** | **____** | | |
| | | | | |
| **GRAND TOTAL** | **~1250** | **____** | | Target ~1.25kg |

---

## 4. Electrical Verification

Test all electrical connections before first drive. Multimeter required.

### 4.1 Power Rail Checks (no motors connected)

| Test Point | Expected | Measured | Pass? | Notes |
|-----------|---------|---------|-------|-------|
| Battery voltage (no load, full charge) | 7.4-8.4V | | | |
| Battery voltage (after 1min idle) | 7.2-8.4V | | | |
| Switch ON — voltage at L298N #1 VCC | 7.4-8.4V | | | |
| Switch ON — voltage at L298N #2 VCC | 7.4-8.4V | | | |
| Buck converter output (servo BEC) | 5.0V +/-0.1V | | | |
| ESP32 3.3V rail | 3.3V +/-0.1V | | | |
| L298N #1 5V output pin | 4.8-5.2V | | | |
| L298N #2 5V output pin | 4.8-5.2V | | | |

### 4.2 Motor Output Checks (motors disconnected)

| Test Point | Expected | Measured | Pass? | Notes |
|-----------|---------|---------|-------|-------|
| L298N #1 OUT1/OUT2 (motor stopped) | 0V | | | |
| L298N #1 OUT3/OUT4 (motor stopped) | 0V | | | |
| L298N #2 OUT1/OUT2 (motor stopped) | 0V | | | |
| L298N #2 OUT3/OUT4 (motor stopped) | 0V | | | |

### 4.3 ADC Calibration

| Test Point | Expected | Measured | Pass? | Notes |
|-----------|---------|---------|-------|-------|
| Battery sense ADC (raw value at 8.4V) | ~2700 | | | |
| Battery sense ADC (raw value at 7.4V) | ~2400 | | | |
| Firmware-reported voltage vs multimeter | Within 5% | | | |
| Voltage divider ratio (measured) | 3.128 (config.h) | | | |

### 4.4 GPIO Signal Checks

| Signal | GPIO | Expected state (idle) | Measured | Pass? |
|--------|------|-----------------------|---------|-------|
| Motor 1 IN1 | per EA-09 | LOW | | |
| Motor 1 IN2 | per EA-09 | LOW | | |
| Motor 1 ENA | per EA-09 | LOW (PWM 0) | | |
| E-stop input | GPIO46 | LOW (not pressed) | | |
| Servo FL PWM | per EA-09 | 1500us centre | | |
| Servo FR PWM | per EA-09 | 1500us centre | | |
| Servo RL PWM | per EA-09 | 1500us centre | | |
| Servo RR PWM | per EA-09 | 1500us centre | | |

### 4.5 Continuity Checks

| Connection | From | To | Continuity? | Notes |
|-----------|------|-----|-------------|-------|
| Battery positive | XT60 + | Switch terminal 1 | | |
| Switch output | Switch terminal 2 | L298N VCC bus | | |
| Ground bus | Battery - | ESP32 GND, L298N GND | | |
| Motor 1 wires | L298N OUT1 | Motor W1 terminal | | |
| Motor 2 wires | L298N OUT2 | Motor W2 terminal | | |
| Motor 3 wires | L298N OUT3 | Motor W3 terminal | | |
| Motor 4 wires | L298N OUT4 | Motor W4 terminal | | |
| Motor 5 wires | L298N OUT5 | Motor W5 terminal | | |
| Motor 6 wires | L298N OUT6 | Motor W6 terminal | | |

---

## 5. Performance Baseline

One row per performance requirement. Fill in after running each test from EA-21.

| Test ID | Requirement | Target | Actual | Pass/Fail | Date | Notes |
|---------|------------|--------|--------|-----------|------|-------|
| ST-SP01 | PR-01: Maximum speed | >=0.2 m/s (target 0.3) | | | | |
| ST-B01 | PR-02: Battery endurance | >=30 min at 50% | | | | |
| ST-D05 | PR-03: Speed control | Proportional, measurable | | | | |
| ST-SU08 | PR-04: Payload capacity | 500g, <2mm deflection | | | | |
| ST-SU09 | PR-05: Obstacle traverse | 20mm step, 15deg ramp | | | | |
| ST-SU10 | PR-06: Grade ability | >=15 degrees | | | | |
| ST-D01 | PR-07: Straight-line (5m) | <200mm drift | | | | |
| UT-L01 | PR-08: Command latency | <200ms avg | | | | |
| ST-W05 | PR-09: WiFi range | >=15m at >90% | | | | |
| ST-A01 | PR-10: Steering accuracy | <3 deg error | | | | |
| ST-N01 | PR-11: Noise level | <60dB at 1m | | | | |
| ST-T01 | PR-12: Thermal endurance | <50C after 30min | | | | |
| ST-D03 | FR-01: Min turn radius | ~420mm (within 20%) | | | | |
| ST-D04 | FR-02: Point turn | <100mm displacement/360deg | | | | |
| ST-D08 | FR-03: Steering modes | Ackermann/Point/Crab | | | | |
| ST-SU01 | FR-08: 20mm obstacle | Tilt <5deg, 6 wheels down | | | | |
| ST-SU04 | FR-09: Max obstacle height | >=40mm (50% wheel dia) | | | | |
| ST-SF01 | SF-01: E-stop response | <50ms | | | | |
| ST-SF02 | SF-02: WebSocket disconnect | Stop <2s | | | | |
| ST-SF07 | SF-03: Safe boot | No unintended motion | | | | |
| UT-E01 | ELEC-07: L298N 3.3V logic | Motor responds to all | | | | |
| ST-P03 | ELEC-08: Voltage monitoring | Within 5% of multimeter | | | | |
| UT-M10 | ELEC-09: Acceleration ramp | 0->max <=2s, <5A spike | | | | |

---

## 6. Failure Log

Record every failure, breakage, reprint, or unexpected behaviour.

| Date | Component | Description | Root Cause | Fix Applied | Time Lost (min) | Recurrence? |
|------|-----------|-------------|-----------|-------------|-----------------|-------------|
| | _example: Wheel 3_ | _Grub screw stripped D-flat_ | _Over-tightened_ | _Reprinted wheel, use less torque_ | _180_ | _No_ |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |

---

## 7. Phase 2 Improvement Ideas

Capture observations during Phase 1 that inform the full-scale Phase 2 design.

| Category | Observation | Suggested Change | Priority (H/M/L) |
|----------|------------|-----------------|-------------------|
| Structural | | | |
| Suspension | | | |
| Drivetrain | | | |
| Electronics | | | |
| Steering | | | |
| Wiring | | | |
| Software | | | |
| Print quality | | | |
| Assembly process | | | |
| Weight/balance | | | |

---

## 8. Print Quality Notes

Record print settings and quality observations for each part (optional but useful for Phase 2 calibration).

| Part | Print Date | Layer (mm) | Walls | Infill | Bed Temp | Nozzle Temp | Time (min) | Quality (1-5) | Notes |
|------|-----------|-----------|-------|--------|----------|-------------|-----------|---------------|-------|
| Bearing test piece | | 0.2 | 4 | 50% | 60 | 200 | | | |
| Calibration card | | 0.2 | 3 | 25% | 60 | 200 | | | |
| Wheel 1 | | 0.2 | 3 | 25% | 60 | 200 | | | |
| Steering bracket 1 | | 0.2 | 5 | 60% | 60 | 200 | | | |
| Body FL | | 0.2 | 4 | 30% | 60 | 200 | | | |
| Body FR | | 0.2 | 4 | 30% | 60 | 200 | | | |
| Body RL | | 0.2 | 4 | 30% | 60 | 200 | | | |
| Body RR | | 0.2 | 4 | 30% | 60 | 200 | | | |

**Quality scale**: 1=Failed/unusable, 2=Poor (visible defects), 3=Acceptable, 4=Good, 5=Excellent

---

## 9. Servo Calibration Record

Record final servo trim values after UT-S05 calibration procedure.

| Servo | Location | Initial offset (deg) | Trim applied (us) | Final offset (deg) | Firmware constant |
|-------|----------|---------------------|-------------------|--------------------|--------------------|
| 1 | FL | | | | SERVO_TRIM_FL |
| 2 | FR | | | | SERVO_TRIM_FR |
| 3 | RL | | | | SERVO_TRIM_RL |
| 4 | RR | | | | SERVO_TRIM_RR |

**Trim formula**: trim_us = deviation_deg x 10.31 us/deg (from config.h US_PER_DEG)

---

## 10. Motor Trim Calibration

Record per-motor trim offsets after ST-D07 straight-line drift test.

| Motor | Location | Drift direction | Trim offset applied | Firmware constant |
|-------|----------|----------------|--------------------|--------------------|
| W1 | FL | | | MOTOR_TRIM_LF |
| W2 | ML | | | MOTOR_TRIM_LR |
| W3 | RL | | | — (paired with W2) |
| W4 | RR | | | MOTOR_TRIM_RR |
| W5 | MR | | | MOTOR_TRIM_RF |
| W6 | FR | | | — (paired with W5) |

---

*Template v1.0 — 2026-03-23*
*References: EA-08 (Part Spec), EA-21 (Test Procedures), phase1-complete-bom.md, assembly-reference.md*
