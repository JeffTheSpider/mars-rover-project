---
description: Cross-check wiring diagrams against firmware pin definitions and EA docs
allowed-tools: Read, Glob, Grep, Bash(*), Agent
---

# Wiring Diagram Cross-Check

Parse the Mermaid wiring diagrams and cross-check against firmware pin definitions, EA-23 wire harness, and EA-09 GPIO map.

## Data Sources
1. **Wiring Diagrams**: `docs/diagrams/*.mmd` (power, signal, tray layout, cable routing)
2. **EA-09 GPIO Pin Map**: `docs/engineering/EA-09-gpio-pinmap.md`
3. **EA-19 Wiring Diagram**: `docs/engineering/EA-19-wiring-diagram.md`
4. **EA-23 Wire Harness**: `docs/engineering/EA-23-wire-harness.md`
5. **Firmware config.h**: `firmware/esp32/config.h` (PIN_* definitions)
6. **Firmware sensors.h**: `firmware/esp32/sensors.h` (ADC, encoder pins)
7. **Firmware motors.h**: `firmware/esp32/motors.h` (motor driver pins)
8. **Firmware steering.h**: `firmware/esp32/steering.h` (servo pins)

## Checks

### 1. Pin Definition Consistency
For every `PIN_*` in `config.h`:
- Verify it matches EA-09 GPIO map
- Verify it appears in the correct Mermaid diagram
- Verify it matches EA-23 wire harness connector assignments
- Flag any pin used in firmware but not in diagrams (or vice versa)

### 2. Motor Driver Wiring
- L298N IN1/IN2/IN3/IN4/ENA/ENB pins match across all sources
- Motor channel assignments (FL, FR, RL, RR) consistent
- PWM-capable pins used for ENA/ENB

### 3. Servo Wiring
- SG90 signal pins for 4 steering servos
- Verify PWM channels don't conflict with motor PWM
- Check power rail (5V from L298N regulator or separate BEC)

### 4. Sensor Wiring
- Battery voltage divider: ADC pin, resistor ratio, voltage range
- Encoder pins (if used in Phase 1)
- E-stop pin and pull-up/pull-down configuration

### 5. Power Distribution
- 2S LiPo → L298N motor voltage input
- 5V rail: source, loads, current budget
- 3.3V rail: ESP32 only
- Check for ground loops or missing common grounds

### 6. Wire Harness Completeness
Cross-reference EA-23's 58-wire schedule:
- Every wire has: source connector, destination connector, colour code, gauge
- Every firmware pin maps to a physical wire
- No orphan wires (in harness but not in firmware) or ghost pins (in firmware but not in harness)

### 7. Summary Report
```
=== Wiring Cross-Check Report ===
Pin definitions:  X/Y consistent across all sources
Motor wiring:     PASS/FAIL (details)
Servo wiring:     PASS/FAIL (details)
Sensor wiring:    PASS/FAIL (details)
Power distribution: PASS/FAIL (details)
Wire harness:     X/58 wires verified
Mismatches found: [list with source references]
```
