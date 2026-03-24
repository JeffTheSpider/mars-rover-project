# EA-22: Phase 1 Requirements Specification

**Version**: 1.0
**Date**: 2026-03-23
**Status**: Baselined for Phase 1 build
**Author**: Engineering audit process

## Purpose

This document defines formal requirements for the Phase 1 (0.4-scale) Mars Rover prototype. It establishes measurable success criteria, captures learning objectives, and provides traceability to test procedures (EA-21).

Every engineering project should begin with a requirements document. This one is written retrospectively but formalises what "success" looks like before committing to 72+ hours of printing and £150+ of parts.

---

## 1. Functional Requirements (FR)

| ID | Requirement | Priority | Verification | Source |
|----|------------|----------|-------------|--------|
| FR-01 | Drive forward/reverse on flat surfaces at controllable speed | Must | ST-SP01 | EA-02 |
| FR-02 | Ackermann steering with ±35° range, min turn radius 397mm | Must | ST-A01 | EA-10 |
| FR-03 | Point turn mode (best-effort, limited by servo range) | Should | Manual test | EA-10 |
| FR-04 | Crab walk mode (all wheels parallel) | Should | Manual test | EA-10 |
| FR-05 | WiFi remote control from phone (PWA) within 15m range | Must | ST-W01 | EA-16 |
| FR-06 | Real-time battery monitoring with 3-stage warning | Must | UT-M09 | EA-15 |
| FR-07 | Emergency stop within 100ms of button press | Must | UT-E01 | EA-15 |
| FR-08 | Rocker-bogie suspension articulates over 20mm obstacles | Must | ST-SU09 | EA-01 |
| FR-09 | All 6 wheels maintain ground contact on uneven terrain | Must | ST-SU09 | EA-01 |
| FR-10 | Survive drops from 50mm (table edge) without structural failure | Should | Drop test | EA-05 |

---

## 2. Performance Requirements (PR)

| ID | Requirement | Target | How Measured | Test Ref |
|----|------------|--------|-------------|----------|
| PR-01 | Max speed | 0.3 m/s (N20 100RPM × 80mm wheel) | Stopwatch over 5m | ST-SP01 |
| PR-02 | Runtime | ≥30 min continuous driving | Battery rundown test | ST-B01 |
| PR-03 | Acceleration | 0→max in ≤2s (ramp limited) | Logged via encoder | UT-M10 |
| PR-04 | Payload capacity | 500g on top deck | Static load test | ST-SU08 |
| PR-05 | Obstacle clearance | 20mm step (¼ wheel dia) | Obstacle course | ST-SU09 |
| PR-06 | Grade ability | 15° slope | Ramp test | ST-SU10 |
| PR-07 | Straight-line accuracy | <100mm drift per 5m | Drift test | ST-D07 |
| PR-08 | Command latency | <200ms button→wheel | Oscilloscope/logic analyser | UT-L01 |
| PR-09 | WiFi range | ≥15m line-of-sight | Range walk test | ST-W01 |
| PR-10 | Weight (total) | ≤1.5kg (with battery) | Kitchen scale | Weigh at assembly |
| PR-11 | Noise level | <60dB at 1m | Phone dB meter app | ST-N01 |
| PR-12 | Operating temp | 5–35°C ambient | Thermometer during tests | — |

### Derivations

- **PR-01**: N20 100RPM × π × 80mm wheel = 0.42 m/s theoretical. PWM limiting gives ~0.3 m/s practical max.
- **PR-02**: 2S 2200mAh = 16.3Wh. Average draw ~1.5A × 7.4V = 11.1W → ~88 min theoretical. 30 min target is conservative accounting for losses.
- **PR-04**: 500g = ~50% of rover weight. Top deck supported by 4 body quadrants at corners; M3 bolts at each joint.
- **PR-05**: Rule of thumb: obstacle ≤ ¼ wheel diameter. 80mm ÷ 4 = 20mm. Rocker-bogie helps exceed this.
- **PR-06**: tan(15°) × total weight × gravity = required traction force. N20 stall torque provides ~60× margin.

---

## 3. Physical Requirements (DIM)

| ID | Requirement | Value | Tolerance | Source |
|----|------------|-------|-----------|--------|
| DIM-01 | Body envelope (each quadrant) | 220×130×80mm | ±2mm | EA-08 |
| DIM-02 | Overall footprint (assembled body) | 440×260mm | ±3mm | EA-08 |
| DIM-03 | Overall height (wheels down) | ~160mm | ±5mm | Measured |
| DIM-04 | Wheelbase | 360mm | ±1mm | EA-08, EA-10 |
| DIM-05 | Track width | 280mm | ±1mm | EA-08, EA-10 |
| DIM-06 | Wheel diameter | 80mm (86mm with tire) | ±0.5mm | CAD |
| DIM-07 | Ground clearance (wheel axis) | ~60mm | ±5mm | Measured |
| DIM-08 | Turning circle diameter | 794mm minimum (397mm radius) | ±20mm | EA-10 |
| DIM-09 | Bogie arm length | 180mm | ±0.5mm | EA-08 |
| DIM-10 | Rocker arm length (front half) | 180mm (body pivot to front wheel mount) | ±0.5mm | EA-08 |
| DIM-11 | Rocker arm length (rear half) | 90mm (body pivot to bogie pivot) | ±0.5mm | EA-08 |

### Print Bed Constraint

All parts must fit within CTC Bizer bed: **225×145×150mm**. Body quadrants at 220×130mm fit with 5mm and 15mm margin respectively. Diagonal printing not required.

---

## 4. Electrical Requirements (ELEC)

| ID | Requirement | Value | Source |
|----|------------|-------|--------|
| ELEC-01 | Battery | 2S LiPo 7.4V 2200mAh (16.3Wh) | EA-03 |
| ELEC-02 | Max continuous current | 3A (all motors + servos) | EA-19 |
| ELEC-03 | Stall current (all 6 motors) | 4.2A (0.7A each) | EA-02 |
| ELEC-04 | Fuse rating | 5A blade fuse | EA-15 |
| ELEC-05 | Motor voltage | 6V nominal (PWM-limited from 7.4V) | EA-02 |
| ELEC-06 | Servo power | 5V, 3A peak (dedicated BEC required) | EA-19 |
| ELEC-07 | Logic level | 3.3V (ESP32-S3) | EA-09 |
| ELEC-08 | WiFi | 2.4GHz 802.11n (ESP32-S3 onboard) | EA-04 |
| ELEC-09 | Motor noise suppression | 100nF ceramic cap per motor terminal pair | EA-19 |
| ELEC-10 | ADC filtering | 100nF cap on battery sense line | EA-19 |

### Critical Electrical Notes

1. **ELEC-06**: L298N's onboard 78M05 regulator is rated 0.5A continuous. Four SG90 servos draw up to 2.6A peak. A dedicated 5V 3A buck converter (XL4015 or similar) is **mandatory** for reliable operation.
2. **ELEC-07**: L298N datasheet specifies 5V logic. ESP32-S3 outputs 3.3V. The LM339 comparators inside the L298N typically switch at ~1.5V, so 3.3V works in practice, but this **must** be verified on the bench (see test UT-E01).
3. **ELEC-09**: Without motor caps, PWM noise couples into ADC readings and can cause WiFi interference.

---

## 5. Prototype Learning Objectives (LEARN)

Phase 1 is explicitly a learning prototype. These objectives define what we want to discover to inform Phase 2 design decisions.

| ID | Objective | How Captured | Informs |
|----|----------|-------------|---------|
| LEARN-01 | PLA structural adequacy under dynamic loads (flex, crack, delamination) | Visual inspection log, failure photos | Phase 2 material choice |
| LEARN-02 | N20 motor adequacy (torque, speed, noise, heat, longevity) | Motor temp log, noise measurement (ST-N01) | Phase 2 motor selection |
| LEARN-03 | SG90 servo precision and repeatability | Steering accuracy test (ST-A01) | Phase 2 servo selection |
| LEARN-04 | 608ZZ bearing press-fit reliability in PLA | Assembly ease, play measurement | Phase 2 bearing interface |
| LEARN-05 | Rocker-bogie suspension effectiveness at 0.4 scale | Obstacle course video (ST-SU09) | Phase 2 geometry tweaks |
| LEARN-06 | L298N driver suitability (voltage drop, heat, 3.3V logic) | Thermal test (ST-T01), logic test (UT-E01) | Phase 2 driver selection |
| LEARN-07 | Battery runtime vs usage patterns | Endurance test (ST-B01) | Phase 2 battery sizing |
| LEARN-08 | WiFi range and reliability in outdoor environment | Range test (ST-W01) | Phase 2 antenna/radio |
| LEARN-09 | CTC Bizer print quality for functional parts | Dimensional verification | Phase 2 printer decision |
| LEARN-10 | Assembly/disassembly ease for iteration | Build log time + frustration notes | Phase 2 modularity |
| LEARN-11 | Electronics tray layout effectiveness | Wiring ease, thermal clearance | Phase 2 tray redesign |
| LEARN-12 | Weight distribution and stability | Tilt angle test, centre of gravity | Phase 2 ballast/layout |

---

## 6. Design-for-Test Requirements (DFT)

| ID | Requirement | Rationale |
|----|------------|-----------|
| DFT-01 | Each sub-assembly testable independently before integration | Catch issues early, before full assembly |
| DFT-02 | Battery removable without tools (for charging) | LiPo should not be charged inside PLA enclosure |
| DFT-03 | Top deck removable for electronics access (snap clips) | Frequent access needed during development |
| DFT-04 | Motor wires long enough to test outside body | Allow bench testing of individual motors |
| DFT-05 | Test points accessible for multimeter probing | Need to verify voltages at motor drivers, BEC, battery |
| DFT-06 | USB-C port accessible without disassembly | Programming and serial debug during development |
| DFT-07 | Power LED visible from outside body | Confirms power state at a glance |

---

## 7. Modularity Requirements (MOD)

These requirements ensure the prototype can be iteratively improved without full rebuilds.

| ID | Requirement | Implementation | Source |
|----|------------|---------------|--------|
| MOD-01 | Body quadrants bolt together (not glued) | M3 heat-set inserts at seam flanges, 3mm steel dowel pins for alignment | EA-08 |
| MOD-02 | Electronics tray lifts out as complete unit | Tray sits on internal ledges, secured by top deck weight | EA-08 |
| MOD-03 | Each suspension arm removable independently (2 bolts) | M3 bolts through bearing bosses | EA-01 |
| MOD-04 | Servo mounts replaceable without disassembling suspension | Servo mount is separate piece, bolts to bogie/steering bracket | EA-08 |
| MOD-05 | Top deck tiles individually removable | Snap clips + alignment tabs, no fasteners | EA-08 |
| MOD-06 | Front panel designed for future arm mount | 4× M3 heat-set insert boss pattern (40×40mm square) on FL quadrant | EA-24 |
| MOD-07 | Spare GPIO pins accessible via header on electronics tray | 6 spare pins (GPIO 3, 17, 18, 21, 45, 47) broken out | EA-09 |
| MOD-08 | Wire harness uses JST connectors at every junction | No soldered joints inside body; all connections disconnectable | EA-23 |

---

## 8. Constraints

| Category | Constraint | Impact |
|----------|-----------|--------|
| Printer | CTC Bizer 225×145×150mm bed, PLA only, x3g format | Body split into 4 quadrants, no PETG/TPU |
| Budget | ~£102 Phase 1 budget | Limits component quality |
| Material | PLA only (CTC Bizer limitation) | Indoor/shade use only; UV and heat degrade PLA |
| Scale | 0.4× full design | Some features don't scale linearly (bearings, electronics) |
| Single extruder | Use left nozzle only on dual-extruder printer | No multi-material prints |

---

## 9. Acceptance Criteria

Phase 1 is considered **successful** if:

1. All **Must** functional requirements (FR-01, FR-02, FR-05, FR-06, FR-07, FR-08, FR-09) are met
2. At least 8 of 12 performance requirements meet target values
3. All 12 learning objectives have recorded data (even if the answer is "this didn't work")
4. The rover drives under WiFi control for ≥10 minutes without intervention
5. All sub-assemblies can be disassembled and reassembled within 30 minutes
6. Total weight is ≤1.5kg with battery

Phase 1 is considered **partially successful** if criteria 1 and 4 are met but others fall short.

Phase 1 is considered **failed** only if the rover cannot drive under WiFi control at all, indicating fundamental design errors that must be addressed before Phase 2.

---

## 10. Requirements Traceability Matrix

| Requirement | EA Doc | CAD Script | Firmware Module | Test |
|-------------|--------|-----------|----------------|------|
| FR-01 | EA-02 | rover_wheel.py | motors.h | ST-SP01 |
| FR-02 | EA-10 | steering_bracket.py | steering.h | ST-A01 |
| FR-05 | EA-16 | — | rover_webserver.h | ST-W01 |
| FR-06 | EA-15 | — | sensors.h | UT-M09 |
| FR-07 | EA-15 | — | sensors.h, esp32.ino | UT-E01 |
| FR-08 | EA-01 | rocker_arm.py, bogie_arm.py | — | ST-SU09 |
| ELEC-06 | EA-19 | — | — | Bench test |
| MOD-01 | EA-08 | body_quadrant.py | — | Assembly test |
| MOD-06 | EA-24 | body_quadrant.py | — | Visual |
| MOD-08 | EA-23 | — | — | Continuity test |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-23 | Initial requirements baseline for Phase 1 |
