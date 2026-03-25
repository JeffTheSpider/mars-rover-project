# Engineering Analysis 28: Systems Integration

**Document**: EA-28
**Date**: 2026-03-25
**Purpose**: Comprehensive integration reference mapping all cross-system interfaces — mechanical, electrical, and software — for the Phase 1 (0.4-scale) rover prototype. Validates every interface and identifies mismatches before printing and assembly.
**Depends on**: EA-00 through EA-27 (all prior engineering analyses)

---

## 1. Introduction & Scope

### 1.1 Purpose

This document serves as the single-source integration reference for the Phase 1 build. While EA-01 through EA-27 each address individual subsystems, this analysis maps how all systems connect — every mechanical joint, electrical wire, and software protocol that crosses subsystem boundaries.

### 1.2 Scope

The rover comprises **72 systems across 14 categories**:

| Category | Systems | Key EAs |
|----------|---------|---------|
| Suspension | Rocker arms, bogie arms, differential bar | EA-01, EA-25, EA-26 |
| Steering | Brackets, knuckles, horn links, servos | EA-10, EA-27 |
| Drivetrain | N20 motors, L298N drivers, wheels | EA-02 |
| Body | 4 quadrants, top deck, electronics tray | EA-08 |
| Power | Battery, fuse, switch, distribution | EA-03, EA-19 |
| Compute | ESP32-S3, GPIO allocation | EA-04, EA-09 |
| Sensors | Battery ADC, encoders, E-stop | EA-09, EA-15 |
| Firmware | 9 modules, state machine, safety | EA-12, EA-15 |
| Communication | WebSocket JSON, UART NMEA | EA-12, EA-16 |
| Phone App | PWA, D-pad, ARM/DISARM | EA-16 |
| Wiring | 57 wires, connectors, routing | EA-19, EA-23 |
| 3D Printing | CTC Bizer, PLA, slicer workflow | EA-11 |
| Safety | 4-layer defence-in-depth | EA-15 |
| ROS2 (Phase 2) | 10 nodes, Nav2, SLAM | EA-13 |

### 1.3 Architecture Hierarchy

```
Layer 3: SOFTWARE ────── Firmware, PWA, protocols
    ↕
Layer 2: ELECTRICAL ──── Power, signals, connectors
    ↕
Layer 1: PHYSICAL ────── Structure, bearings, fasteners
```

### 1.4 Companion Diagrams

| Diagram | File | Purpose |
|---------|------|---------|
| System Architecture | `docs/diagrams/ea28-system-architecture.svg` | Top-level block diagram |
| Mechanical Assembly | `docs/diagrams/ea28-mechanical-assembly.svg` | Structural tree |
| Power Distribution | `docs/diagrams/ea28-power-distribution.svg` | Power flow |
| Signal Flow | `docs/diagrams/ea28-signal-flow.svg` | GPIO to peripherals |
| Firmware State | `docs/diagrams/ea28-firmware-state.svg` | Operating states |
| Assembly DAG | `docs/diagrams/ea28-assembly-dag.svg` | Build dependency graph |

---

## 2. System Architecture Overview

### 2.1 Phase 1 Block Diagram

See `docs/diagrams/ea28-system-architecture.svg`.

**Phase 1 architecture** (single-processor):

```
Phone (PWA)
    │ WiFi WebSocket (JSON)
    ▼
ESP32-S3 (N16R8) ─── Firmware v0.3.0, 9 modules
    ├── Motor Control ──→ L298N ×2 ──→ N20 Motors ×6 ──→ Wheels ×6
    ├── Steering ──→ SG90 Servos ×4 ──→ Horn Links ──→ Knuckles
    ├── Sensors ──→ Battery ADC, Encoders (×2), E-stop
    └── Safety ──→ Arm/Disarm, Watchdog, Battery Cutoff, Stall Detect
```

**Phase 2 extension** (dual-processor): Adds Jetson Orin Nano (ROS2) upstream of ESP32 via UART.

### 2.2 Data Flow Summary

| Path | Protocol | Rate | Latency |
|------|----------|------|---------|
| Phone → ESP32 | WebSocket JSON (port 81) | On touch | ~50ms WiFi |
| ESP32 → Phone | WebSocket JSON broadcast | 5 Hz | ~50ms WiFi |
| ESP32 → Motors | L298N PWM + DIR (GPIO) | 1 kHz PWM | <1ms |
| ESP32 → Servos | 50 Hz PWM (LEDC) | 50 Hz | 20ms |
| ESP32 ← Battery | ADC 12-bit (GPIO14) | 1 Hz | <1ms |
| ESP32 ← E-stop | Digital input (GPIO46) | Interrupt | <1ms |
| Jetson ↔ ESP32 | UART NMEA 115200 (Phase 2) | 50 Hz | ~8ms |

---

## 3. Mechanical Integration Map

### 3.1 Suspension Load Path

The complete load chain from body to ground:

```
BODY FRAME (4 quadrants, 440×260×80mm)
    │
    ├── [608ZZ bearing ×2] ── Rocker pivot bosses (Z=60mm, X=±125mm)
    │
    ▼
DIFFERENTIAL BAR (300mm × 8mm steel rod)
    │
    ├── [608ZZ bearing ×1] ── Centre pivot in body
    ├── [M3 grub screw] ── Left rocker hub (rigid clamp)
    └── [M3 grub screw] ── Right rocker hub (rigid clamp)
    │
    ▼
ROCKER ARMS ×2 (270mm span: 180mm front + 90mm rear)
    │
    ├── Front arm tube (150mm rod) ──→ STEERING BRACKET ──→ [608ZZ] ──→ KNUCKLE + WHEEL
    │                                    └── SG90 SERVO ──→ HORN LINK (4-bar) ──→ KNUCKLE
    │
    └── Rear arm tube (60mm rod) ──→ BOGIE PIVOT [608ZZ bearing]
                                        │
                                        ▼
                                    BOGIE ARMS ×2 (180mm span: 90+90mm)
                                        │
                                        ├── Front tube (60mm) ──→ FIXED MOUNT ──→ WHEEL
                                        └── Rear tube (60mm) ──→ STEERING BRACKET ──→ WHEEL
```

**Load analysis** (EA-01 Section 5.1): At Phase 1 weight (~1.25 kg), max stress in PLA rocker arm is ~0.6 MPa — giving a **100× safety factor** against PLA tensile strength (60 MPa).

### 3.2 Differential Mechanism

The differential couples left and right rockers so the body stays level (EA-25/EA-26):

- **Diff bar** = the rocker pivot axis itself (300mm × 8mm steel rod)
- **Body** has 2× 608ZZ bearings in pivot bosses allowing rod rotation
- **Rocker hubs** clamp rigidly to the diff bar via M3 grub screws
- **Effect**: Left rocker tilts up → rod rotates → right rocker tilts down → body stays level (half angle)

This corrected design (EA-25 Section 2B) replaced the original 3-adapter approach, reducing bearing count from 11 to **9 total**.

### 3.3 Steering Mechanism

Each steered wheel (4 of 6) uses an offset parallel 4-bar linkage (EA-27):

```
SG90 Servo (shaft vertical)
    └── Servo Horn (15mm arm)
        └── Horn Link (20mm c/c, M2 pin joints)
            └── Steering Arm (15mm, on knuckle)
                └── Steering Knuckle (hangs below bearing)
                    ├── N20 Motor pocket
                    ├── Wheel axle bore
                    └── Hard stop tab (±35°)
```

**Key specs**:
- Angular ratio: 1:1 (horn arm = knuckle arm = 15mm)
- Non-linearity: <1° at ±35° (acceptable)
- Hard stops: tab-in-channel, 23× safety factor in PLA shear
- Servo soft limit in firmware: ±33° (2° margin before mechanical stop)

### 3.4 Fastener Schedule

| Fastener | Size | Qty | Purpose | EA Ref |
|----------|------|-----|---------|--------|
| 608ZZ bearing | 8×22×7mm | 9 (12 bought) | All pivots | EA-25 |
| M8×40 hex bolt | M8 | 4 | Rocker pivot shafts | EA-08 |
| M8×30 hex bolt | M8 | 4 | Steering pivot shafts | EA-27 |
| M8 nyloc nut | M8 | 8 | Lock nuts for M8 pivots | EA-08 |
| M8 washer | M8 | 16 | Bearing spacers (2 per pivot) | EA-08 |
| M3×12 socket cap | M3 | 34 | Body joins, brackets, lap joints | EA-08 |
| M3×8 socket cap | M3 | 20 | Electronics, motor brackets | EA-08 |
| M3 heat-set insert | 4.8mm OD × 5.5mm | 40 | All PLA screw bosses | EA-08 |
| M3 nyloc nut | M3 | 30 | General assembly | EA-08 |
| M3 washer | M3 | 30 | General assembly | EA-08 |
| M3×6 grub screw | M3 | 12 | Tube socket rod retention | EA-25 |
| M2×10 socket cap | M2 | 8 | Horn link pins (4 links × 2) | EA-27 |
| M2 nyloc nut | M2 | 8 | Horn link retention | EA-27 |
| M2 nylon washer | M2 | 16 | Pin joint friction reduction | EA-27 |
| M2×4 grub screw | M2 | 6 | Wheel hub set screws | EA-08 |
| 8mm steel rod | 2m total | 13 segments | Diff bar + arms + steering | EA-25 |

### 3.5 Tube-to-Connector Interface Matrix

All rod-to-connector joints use identical specifications (EA-25 Section 5A):

| Feature | Dimension | Tolerance |
|---------|-----------|-----------|
| Tube socket bore | 8.2mm | ±0.1mm |
| Tube socket depth | 15mm | ±0.5mm |
| M3 grub screw hole | 3.0mm × 6mm deep | ±0.1mm |
| Wall around socket | ≥4mm minimum | — |

**Rod cutting plan** (from 2× 1m rods):

| Segment | Qty | Length (mm) | Total (mm) |
|---------|-----|-------------|------------|
| Differential bar | 1 | 300 | 300 |
| Rocker front arm | 2 | 150 | 300 |
| Rocker rear arm | 2 | 60 | 120 |
| Bogie front arm | 2 | 60 | 120 |
| Bogie rear arm | 2 | 60 | 120 |
| Steering pivot shaft | 4 | 50 | 200 |
| **Total** | **13** | — | **1160mm** (42% margin from 2000mm) |

### 3.6 Bearing Interface Matrix

All 9 bearings are 608ZZ (8×22×7mm). Every seat is identical (EA-25 Section 5A):

| # | Location | Host Part | Shaft | EA Ref |
|---|----------|-----------|-------|--------|
| 1 | Body left rocker pivot | Body quadrant RL | Diff bar 300mm | EA-25 |
| 2 | Body right rocker pivot | Body quadrant RR | Diff bar 300mm | EA-25 |
| 3 | Body diff centre pivot | Body (centre) | Diff bar 300mm | EA-25 |
| 4 | Left rocker-to-bogie | Bogie pivot connector | 8mm rod segment | EA-01 |
| 5 | Right rocker-to-bogie | Bogie pivot connector | 8mm rod segment | EA-01 |
| 6 | FL steering pivot | Steering bracket | 50mm shaft | EA-27 |
| 7 | FR steering pivot | Steering bracket | 50mm shaft | EA-27 |
| 8 | RL steering pivot | Steering bracket | 50mm shaft | EA-27 |
| 9 | RR steering pivot | Steering bracket | 50mm shaft | EA-27 |

**Bearing seat**: 22.15mm bore × 7.2mm depth (0.15mm oversize for PLA press-fit, 0.2mm depth clearance).

**Shaft bore**: 8.1mm through-bore (corrected from 8.0mm — 0.1mm clearance for print tolerance, per Session Notes 2026-03-25).

---

## 4. Electrical Integration Map

### 4.1 Power Distribution

See `docs/diagrams/ea28-power-distribution.svg`.

**Phase 1 power path**:

```
2S LiPo (7.4V, 2200mAh, XT60)
    → 5A blade fuse (ATC holder)
    → Kill switch (toggle, rear panel)
    → L298N #1 VCC (left motors)
    → L298N #2 VCC (right motors)
    → GND bus (star topology from battery negative)

L298N #1 5V regulator (78M05, 0.5A max)
    → ESP32-S3 VIN
    → 4× SG90 servo VCC (via breadboard)
```

**Power budget**:

| Consumer | Voltage | Typical (A) | Peak (A) |
|----------|---------|-------------|----------|
| 6× N20 motors | 7.4V | 0.36 | 9.0 |
| 4× SG90 servos | 5V | 0.2 | 2.6 |
| ESP32-S3 | 3.3V (via 5V) | 0.15 | 0.5 |
| Sensors/LED | 3.3V | 0.05 | 0.1 |
| **Total** | — | **~0.76A** | **~12.2A** |

**Known issue**: L298N 5V regulator rated 0.5A continuous; 4× SG90 servos can draw 2.6A peak. Recommendation: add dedicated 5V BEC before servo testing.

**Runtime estimate**: 2200mAh ÷ 760mA typical ≈ **~2.9 hours** at low-effort driving (not the 10min worst-case from EA-03 which assumed full-scale motors).

### 4.2 Motor Control Signals

See `docs/diagrams/ea28-signal-flow.svg`.

| ESP32 GPIO | L298N Pin | Motor | Function |
|------------|-----------|-------|----------|
| GPIO4 | #1 ENA | W1 (FL) | PWM speed (LEDC Ch0, 1kHz) |
| GPIO5 | #1 IN1 | W1 (FL) | Direction A |
| GPIO6 | #1 IN2 | W1 (FL) | Direction B |
| GPIO7 | #1 ENB | W2+W3 (ML+RL) | PWM speed (LEDC Ch1, 1kHz) |
| GPIO15 | #1 IN3 | W2+W3 (ML+RL) | Direction A |
| GPIO16 | #1 IN4 | W2+W3 (ML+RL) | Direction B |
| GPIO8 | #2 ENA | W6 (FR) | PWM speed (LEDC Ch2, 1kHz) |
| GPIO9 | #2 IN1 | W6 (FR) | Direction A |
| GPIO10 | #2 IN2 | W6 (FR) | Direction B |
| GPIO11 | #2 ENB | W5+W4 (MR+RR) | PWM speed (LEDC Ch3, 1kHz) |
| GPIO12 | #2 IN3 | W5+W4 (MR+RR) | Direction A |
| GPIO13 | #2 IN4 | W5+W4 (MR+RR) | Direction B |

**Motor grouping**: 4 channels control 6 motors. Middle+rear motors on each side are wired in parallel (same speed, same direction). Only 4 independent speed channels available in Phase 1.

**L298N control truth table**:

| IN1 | IN2 | EN (PWM) | Motor Action |
|-----|-----|----------|-------------|
| HIGH | LOW | 0-255 | Forward (variable speed) |
| LOW | HIGH | 0-255 | Reverse (variable speed) |
| LOW | LOW | Any | Coast (free spin) |
| HIGH | HIGH | Any | Brake (short-circuit) |

**Critical**: Remove ENA/ENB jumpers on both L298N boards to enable PWM speed control.

### 4.3 Servo Control

| ESP32 GPIO | Servo | LEDC Channel | PWM Freq |
|------------|-------|-------------|----------|
| GPIO1 | FL (front-left) | Ch4 | 50 Hz |
| GPIO2 | FR (front-right) | Ch5 | 50 Hz |
| GPIO41 | RL (rear-left) | Ch6 | 50 Hz |
| GPIO42 | RR (rear-right) | Ch7 | 50 Hz |

**PWM range**: 544-2400µs, centre 1500µs (90°), 11.11µs/degree.
**Servo power**: All 4 share 5V from L298N regulator (or dedicated BEC).
**Rear servos**: Mounted inverted; firmware negates angle (handled in `steering.h`).

### 4.4 Sensor Inputs

| Sensor | GPIO | Type | Config | EA Ref |
|--------|------|------|--------|--------|
| Battery voltage | GPIO14 | ADC 12-bit | 10kΩ/4.7kΩ divider → ~2.37V | EA-19 |
| E-stop button | GPIO46 | Digital IN | Input-only, internal pull-down | EA-15 |
| Status LED | GPIO0 | Digital OUT | NeoPixel or single LED | EA-15 |
| Encoder W1 (FL) | GPIO38 | ISR | Rising edge, channel A | EA-09 |
| Encoder W6 (FR) | GPIO40 | ISR | Rising edge, channel A | EA-09 |
| Encoder W1 Ch B | GPIO39 | Digital IN | Direction detection | EA-09 |
| Encoder W6 Ch B | GPIO48 | Digital IN | Direction detection | EA-09 |

**Spare GPIO (Phase 1)**: GPIO3, 17, 18, 21, 45, 47 (6 pins).
**Reserved (N16R8 PSRAM)**: GPIO26-37 — must never connect.

### 4.5 Wire Harness Cross-Reference

57 wires documented in EA-23. Key wire groups:

| Category | Wire IDs | Count | Total Length | Gauge |
|----------|----------|-------|-------------|-------|
| Battery power | W001-W004 | 4 | 0.36m | 14 AWG |
| Driver power | W005-W008 | 4 | 0.54m | 16 AWG |
| 5V distribution | W009-W012 | 4 | 0.28m | 22 AWG |
| Motor leads | W013-W024 | 12 | 3.60m | 18 AWG |
| Servo signal | W025-W028 | 4 | 1.50m | 22 AWG |
| Servo power | W029-W036 | 8 | 3.00m | 22 AWG |
| ESP32 power | W037-W038 | 2 | 0.20m | 22 AWG |
| Battery ADC | W039-W042 | 3+cap | 0.19m | 22 AWG |
| L298N control | W043-W054 | 12 | 1.74m | 22 AWG |
| E-stop + LED | W055-W058 | 4 | 0.50m | 22 AWG |
| **Total** | **W001-W058** | **57** | **~11.9m** | — |

### 4.6 Connector Schedule

| Connector | Type | Rating | Location |
|-----------|------|--------|----------|
| Battery | XT60 female (on rover) | 60A | Electronics tray |
| Fuse | ATC blade holder | 5A | Inline battery-to-switch |
| Kill switch | Panel-mount toggle | 10A | Rear body wall (15mm hole) |
| L298N motor out | Screw terminals | 2A/ch | Motor driver board |
| L298N logic | Dupont headers | Signal | Motor driver board |
| Servo leads | Dupont 3-pin | 1A | Servo connector |
| ESP32 headers | Dupont M/F | Signal | DevKit pins |
| Motor pivot | JST-XH 2-pin | 2A | Body/arm pivot point |

**Colour code**: Red=VCC, Black=GND, Yellow=motor control, Orange=servo signal, Brown=ADC, White=E-stop.

---

## 5. Software Integration Map

### 5.1 Firmware Internal Architecture

ESP32-S3 firmware (v0.3.0) uses a single-translation-unit pattern with 9 modules:

```
esp32.ino (main)
    ├── config.h ─── Pin defs, geometry constants, timing
    ├── motors.h ─── 4-channel L298N control, speed ramping
    ├── steering.h ── 4-servo Ackermann/PointTurn/CrabWalk
    ├── sensors.h ── Battery ADC, encoder ISR, stall detect
    ├── leds.h ──── 5 LED patterns (idle/armed/driving/warning/error)
    ├── rover_webserver.h ── HTTP:80 + WebSocket:81
    ├── uart_nmea.h ── NMEA text protocol (Phase 1)
    ├── uart_binary.h ── COBS binary protocol (Phase 2, ifdef)
    └── ota.h ──── OTA firmware updates
```

**Module dependencies** (→ = calls functions from):
- `rover_webserver.h` → `motors.h`, `steering.h` (drive commands)
- `uart_nmea.h` → `motors.h`, `steering.h` (UART commands)
- `sensors.h` → `motors.h` (stopAllMotors on battery critical)
- `steering.h` → `motors.h` (setDrive for point turn)
- `leds.h` → reads global state variables

### 5.2 Main Loop Timing

```
Every iteration (~1ms):
    Feed watchdog ──→ WiFi check ──→ OTA ──→ WebServer ──→ UART

Every 20ms:
    updateMotors() ──→ updateSteering() ──→ checkStall()

Every 100ms:
    (Sensor polling — encoders are ISR-driven)

Every 200ms:
    sendWsStatus() ──→ Broadcast telemetry to phone

Every 1000ms:
    updateBattery() ──→ 3-stage voltage check

Continuous:
    Command timeout check: if (now - lastCommandTime > 2000ms) → stopAllMotors()
```

### 5.3 WebSocket Protocol (Phase 1)

**Phone → ESP32 (on touch)**:
```json
{"cmd": "fwd|rev|left|right|fl|fr|bl|br|stop|arm|disarm", "speed": 0-100, "mode": 0-2}
```

**ESP32 → Phone (5 Hz broadcast)**:
```json
{"batt": 7.4, "pct": 78, "ml": 50, "mr": 50, "armed": true, "limit": 100, "stall": false, "estop": false}
```

**Modes**: 0=Ackermann, 1=Point Turn, 2=Crab Walk.

### 5.4 UART Protocol (Phase 1 / Phase 2 Debug)

NMEA-style text protocol at 115200 baud (EA-12):

**Commands (Jetson/Debug → ESP32)**: 11 message types
- `$MOT,w1,w2,w3,w4,w5,w6*XX` — Motor speeds (-100 to +100%)
- `$STR,fl,fr,rl,rr*XX` — Steering angles (-35° to +35°)
- `$STP*XX` — Emergency stop
- `$PNG*XX` — Ping (watchdog heartbeat)
- `$LED,mode,r,g,b*XX` — LED control
- Plus: BUZ, RSM, REQ, CFG, SVO, MOD

**Responses (ESP32 → Jetson/Debug)**: 7 message types
- `$ENC,c1,0,0,0,0,c6*XX` — Encoder counts (50 Hz)
- `$BAT,v,0.00,pct*XX` — Battery (1 Hz)
- `$STS,state,uptime,temp*XX` — Status (1 Hz)
- Plus: IMU, ACK, ERR, PON

**Bandwidth**: 8,310 B/s = 72% of 115200 baud capacity, 28% headroom.

### 5.5 Safety Interlocks

See `docs/diagrams/ea28-firmware-state.svg`.

**Defence-in-depth (4 layers)**:

| Layer | Mechanism | Timeout | EA Ref |
|-------|-----------|---------|--------|
| **L1 Hardware** | E-stop button (GPIO46), 5A fuse, kill switch | Instant | EA-15 |
| **L2 Firmware** | Task watchdog, command timeout, battery cutoff, stall detect, speed ramp | 200ms-5s | EA-15 |
| **L3 Software** | Arm-before-drive requirement, battery speed limiting | N/A | EA-15 |
| **L4 Operational** | Speed limits by mode, manual override | N/A | EA-15 |

**Motor command accepted only when ALL conditions met**:
1. `!estopActive`
2. `!batteryCritical`
3. `roverArmed` (explicit arm command from user)
4. `(now - lastCommandTime) < CMD_TIMEOUT_MS` (2000ms)

**Motors stop immediately on ANY trigger**:
- E-stop pressed (hardware interrupt, <1ms)
- Battery critical (<3.2V/cell)
- Command timeout (>2000ms no command)
- Watchdog fires (>5s loop hang → hard reset)
- Stall detected (no encoder movement for 2s at PWM>20%)
- Disarm command received

### 5.6 Command Flow

Complete path from user input to motor movement:

```
User touches D-pad (phone)
    → touchstart event fires
    → WebSocket JSON: {"cmd":"fwd","speed":50,"mode":0}
    → WiFi (~50ms)
    → ESP32 WebSocket server (port 81)
    → processCommand()
    → Safety checks (armed? estop? battery?)
    → applyAckermann(0) + setDrive(50, 50)
    → motorTarget[0..3] updated
    → updateMotors() (next 20ms tick)
    → Speed ramped by RAMP_RATE (10%/20ms)
    → setMotor() → L298N PWM + DIR pins
    → Motor turns → wheel rotates
    → Encoder ISR fires
    → Telemetry broadcast back to phone (200ms)
```

**Total latency**: ~70ms (WiFi 50ms + processing 1ms + PWM update 20ms).

---

## 6. Cross-Domain Interface Matrix

The master table of every interface crossing subsystem boundaries.

| ID | From System | To System | Type | Specification | EA Ref | Status |
|----|-------------|-----------|------|---------------|--------|--------|
| **Mechanical Interfaces** | | | | | | |
| M-01 | Body quadrant | Diff bar | M | 608ZZ bearing seat (22.15×7.2mm) | EA-25 | Verified |
| M-02 | Diff bar | Rocker hub | M | 8mm rod, M3 grub screw clamp | EA-25 | Verified |
| M-03 | Rocker arm | Bogie pivot | M | 608ZZ bearing, 8mm rod | EA-01 | Verified |
| M-04 | Rocker front tube | Steering bracket | M | 8.2mm socket, 15mm deep | EA-25 | Verified |
| M-05 | Bogie front tube | Fixed mount | M | 8.2mm socket, 15mm deep | EA-25 | Verified |
| M-06 | Bogie rear tube | Steering bracket | M | 8.2mm socket, 15mm deep | EA-25 | Verified |
| M-07 | Steering bracket | Knuckle | M | 608ZZ bearing, 50mm shaft | EA-27 | Verified |
| M-08 | Servo horn | Horn link | M | M2×10 pin + nylon washer | EA-27 | Verified |
| M-09 | Horn link | Knuckle arm | M | M2×10 pin + nylon washer | EA-27 | Verified |
| M-10 | Knuckle | Wheel | M | N20 3mm D-shaft, 8mm engage | EA-08 | Verified |
| M-11 | Fixed mount | Wheel | M | N20 3mm D-shaft, 8mm engage | EA-08 | Verified |
| M-12 | Bracket hard stop | Knuckle tab | M | ±35° channel, 0.3mm clearance | EA-27 | Verified |
| M-13 | Body quadrants (×4) | Each other | M | 22× M3×12 + heat-set inserts | EA-08 | Verified |
| M-14 | Body | Electronics tray | M | M3 standoff bosses | EA-08 | Verified |
| M-15 | Body rear wall | Kill switch | M | 15mm bore | EA-08 | Verified |
| **Electrical Interfaces** | | | | | | |
| E-01 | Battery | Fuse | E | XT60, 14AWG, W001 | EA-19 | Verified |
| E-02 | Fuse | Kill switch | E | 5A ATC blade, W003 | EA-19 | Verified |
| E-03 | Switch | L298N ×2 VCC | E | 16AWG, W004-W005/W007 | EA-19 | Verified |
| E-04 | L298N #1 5V | ESP32 VIN | E | 22AWG, W037 | EA-19 | Verified |
| E-05 | L298N #1 5V | Servo VCC (×4) | E | 22AWG, W029-W036 | EA-19 | **Concern** |
| E-06 | Battery+ | ADC divider | E | 10kΩ+4.7kΩ+100nF, W039-W042 | EA-19 | Verified |
| E-07 | ESP32 GPIO4-16 | L298N #1/#2 logic | E | 22AWG, W043-W054, 3.3V logic | EA-19 | **Marginal** |
| E-08 | ESP32 GPIO1,2,41,42 | Servo signals | E | 22AWG, W025-W028, 50Hz PWM | EA-19 | Verified |
| E-09 | L298N OUT | Motor terminals | E | 18AWG, W013-W024 + 100nF caps | EA-19 | Verified |
| E-10 | E-stop button | GPIO46 | E | Pull-down, W056 | EA-19 | Verified |
| E-11 | LED | GPIO0 | E | Signal level, W055 | EA-19 | Verified |
| E-12 | GND bus | All modules | E | Star topology from battery− | EA-19 | Verified |
| **Software Interfaces** | | | | | | |
| S-01 | Phone PWA | ESP32 WebSocket | S | JSON, port 81, WiFi | EA-16 | Verified |
| S-02 | Phone PWA | ESP32 HTTP | S | HTML, port 80, WiFi | EA-16 | Verified |
| S-03 | ESP32 WebSocket | Motor control | S | processCommand() → setDrive() | EA-16 | Verified |
| S-04 | ESP32 WebSocket | Steering | S | processCommand() → applyAckermann() | EA-16 | Verified |
| S-05 | ESP32 UART TX | Debug/Jetson | S | NMEA $ENC/$BAT/$STS, 115200 | EA-12 | Verified |
| S-06 | Debug/Jetson | ESP32 UART RX | S | NMEA $MOT/$STR/$STP, 115200 | EA-12 | Verified |
| S-07 | Battery ADC | Safety logic | S | 3-stage threshold check | EA-15 | Verified |
| S-08 | E-stop ISR | Motor control | S | Immediate motor stop | EA-15 | Verified |
| S-09 | Encoder ISR | Stall detect | S | 2s no-movement threshold | EA-15 | Verified |
| S-10 | Watchdog timer | System reset | S | 5s timeout → hard reset | EA-15 | Verified |
| S-11 | Arm/Disarm | Motor enable gate | S | roverArmed flag | EA-15 | Verified |
| S-12 | OTA module | Firmware update | S | ArduinoOTA, port 3232 | EA-17 | Untested |
| **Cross-Domain Interfaces** | | | | | | |
| X-01 | SG90 servo | Steering mechanism | M+E | PWM signal → mechanical rotation | EA-27 | Verified |
| X-02 | N20 motor | Wheel drive | M+E | L298N output → mechanical torque | EA-02 | Verified |
| X-03 | Battery | ADC + safety logic | E+S | Voltage → divider → ADC → firmware | EA-19 | Verified |
| X-04 | E-stop button | Motor shutdown | M+E+S | Physical → GPIO → ISR → motors off | EA-15 | Verified |
| X-05 | Wire harness | Suspension pivots | M+E | Wires through arm channels at pivots | EA-23 | Verified |
| X-06 | Body cable exits | Wire routing | M+E | 10×5mm slots, 6 exits | EA-23 | Verified |

**Summary**: 42 interfaces identified. 40 verified, 1 concern (E-05: servo power), 1 marginal (E-07: 3.3V logic). 1 untested (S-12: OTA).

---

## 7. Assembly Dependency Graph

See `docs/diagrams/ea28-assembly-dag.svg`.

### 7.1 Critical Path

The longest dependency chain determines minimum build time:

```
Calibration print (30min) → Bearing test (15min) → All prints (~72hrs)
    → Heat-set inserts (1hr) → Rod cutting (30min)
    → Suspension assembly (3hrs) → Mount to body (1hr)
    → Servo + motor mount (2hrs) → Wiring (3hrs)
    → Firmware upload (30min) → Bench test (1hr) → First drive
```

**Critical path total**: ~82 hours (dominated by 3D printing).

### 7.2 Assembly Phases (EA-17)

| Phase | Activity | Duration | Prerequisites |
|-------|----------|----------|---------------|
| 0 | Calibration + bearing test | 45 min | Printer set up |
| 1 | Print all parts | ~72 hrs | Phase 0 pass |
| 2 | Parts arrive (electronics) | 1-3 weeks | Orders placed |
| 3 | Install heat-set inserts | 1 hr | All parts printed |
| 4 | Cut steel rods | 30 min | Rod purchased |
| 5 | Build suspension (both sides) | 3 hrs | Phases 3-4 |
| 6 | Mount to body | 1 hr | Phase 5 + body printed |
| 7 | Wire motors, mount to clips | 2 hrs | Phase 6 + motors arrived |
| 8 | Wire electronics | 3 hrs | Phase 7 + ESP32 + L298N |
| 9 | Upload firmware | 30 min | Phase 8 |
| 10 | Bench test | 1 hr | Phase 9 |
| 11 | First drive | 1 hr | Phase 10 pass |

### 7.3 Parallelisable Work

While 3D printing runs (~72 hours), these can proceed in parallel:
- Order all electronics (Phase 1 BOM, ~$102)
- Solder motor wires + capacitors (when motors arrive)
- Flash ESP32 with firmware (when ESP32 arrives)
- Set up Cura slicer profiles for CTC Bizer
- Cut steel rods to length (when rods purchased)

---

## 8. Integration Test Plan

### 8.1 Pre-Assembly Fit Checks

| Test | Method | Pass Criteria | EA Ref |
|------|--------|---------------|--------|
| 608ZZ bearing seat | Press bearing into test piece | Firm hand-fit, no wobble | EA-25 |
| N20 motor clip | Snap motor into steering bracket | Holds motor, can be removed | EA-08 |
| SG90 servo pocket | Insert servo into servo mount | Tabs seat flush, M2 holes align | EA-08 |
| 8mm rod in socket | Insert rod into tube socket | Slides freely, grub screw holds | EA-25 |
| D-shaft in wheel hub | Press wheel onto N20 shaft | Firm fit on D-flat, M2 grub backup | EA-08 |
| Heat-set insert | Install test insert at 170°C | Pulls out at >20N, sits flush | EA-08 |
| M3 bolt in insert | Thread M3 bolt into insert | 2+ full turns before bottoming | EA-08 |
| Body quadrant join | Align 2 quadrants, bolt together | Seam gap <0.5mm, bolts tighten | EA-08 |

### 8.2 Electrical Continuity Checks (Before Power-On)

| Test | Points | Expected | Risk If Skipped |
|------|--------|----------|-----------------|
| Battery+ to L298N VCC | XT60+ → switch → L298N screw terminal | Continuity (switch ON) | Dead system |
| Battery− to GND bus | XT60− → all GND points | Continuity | Erratic behaviour |
| No short: +V to GND | All power rails | Open circuit | Fire/damage |
| No short: 5V to GND | 5V bus to GND | Open circuit | Burnt regulator |
| ADC divider R1 | Battery+ to GPIO14 junction | ~10kΩ | Bad readings |
| ADC divider R2 | GPIO14 junction to GND | ~4.7kΩ | Bad readings |
| Motor polarity | L298N OUT to motor wire | Consistent red/black | Wrong direction |

### 8.3 Firmware Smoke Test Sequence

1. **Serial monitor** (115200): Verify startup banner shows v0.3.0
2. **WiFi connect**: Verify IP address displayed
3. **Web UI**: Navigate to IP in browser, verify page loads
4. **Battery reading**: Status shows ~7.4V, percentage >80%
5. **LED pattern**: Slow pulse (disarmed state)
6. **ARM**: Press ARM button → LED changes to double blink
7. **Servo centre**: All 4 wheels straight after ARM
8. **Motor test (wheels off ground)**: Press forward → all wheels spin forward
9. **E-stop**: Press E-stop → all motors stop, LED SOS pattern
10. **Timeout test**: ARM, send forward, wait 3 seconds → motors stop automatically

### 8.4 End-to-End Drive Test

Cross-reference EA-21 test procedures (UT-M01 through UT-M09, UT-S01 through UT-S06).

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Straight line (5m) | Mark 5m line, drive at 30% | Deviation <200mm |
| Turn radius | Full lock left, measure radius | Within 50mm of EA-10 calc (397mm) |
| Point turn | Engage mode 1, rotate 360° | Completes within 2m diameter |
| Obstacle climb | Drive over 20mm book | All 6 wheels maintain contact |
| Suspension articulation | Place under 1 wheel (40mm block) | Body stays within 5° of level |
| Battery warning | Drive until warning LED | Warning at ~7.0V (3.5V/cell) |

---

## 9. Risk Register

| ID | Risk | Domain | Probability | Impact | Score | Mitigation | Status |
|----|------|--------|-------------|--------|-------|------------|--------|
| R-01 | L298N 5V insufficient for 4 servos | Electrical | High | Medium | **H** | Add dedicated 5V BEC (XL4015, ~$3) | Open |
| R-02 | L298N 3.3V logic marginal | Electrical | Low | Medium | **M** | 100nF caps on motor terminals; works in practice | Accepted |
| R-03 | Bearing doesn't press-fit in PLA | Mechanical | Medium | Medium | **M** | Print test piece first; ream with 22.2mm drill | Mitigated |
| R-04 | Diff bar slips in rocker hub | Mechanical | Medium | High | **H** | M3 grub screw + thread-lock; fallback: D-flat on rod | Open |
| R-05 | PLA connector cracks at tube socket | Mechanical | Medium | High | **H** | 4mm walls, 60% infill, 5 perimeters | Mitigated |
| R-06 | Wire bundles too thick for channels | Electrical | Medium | Medium | **M** | Standardised 8×6mm channels; use 26AWG | Mitigated |
| R-07 | Body pivot boss wall too thin | Mechanical | Low | Medium | **M** | 3.9mm wall; ream if needed; snap ring backup | Mitigated |
| R-08 | CTC Bizer dimensional accuracy | Mechanical | Medium | High | **H** | Calibration test card first; adjust bore ±0.1mm | Open |
| R-09 | WiFi range insufficient | Software | Medium | Low | **L** | Accept ~10m limit; Phase 2 adds antenna | Accepted |
| R-10 | Phase 1 battery runtime too short | Electrical | Low | Low | **L** | Bench-test on blocks; runtime ~2.9hrs typical | Accepted |
| R-11 | Motor stalls on grass | Mechanical | Medium | Low | **L** | Reduce speed; Phase 2 motors 10× stronger | Accepted |
| R-12 | Servo horn link fails at joint | Mechanical | Low | Low | **L** | 23× safety factor; SG90 fails first | Accepted |

---

## 10. Open Issues & Recommendations

### 10.1 Action Items

| # | Issue | Priority | Recommendation |
|---|-------|----------|----------------|
| 1 | Servo power overload (R-01) | **High** | Add XL4015 5V 3A BEC to Phase 1 BOM before servo testing |
| 2 | Pre-print-checklist.md stale | **High** | Rewrite using EA-28 integration data (companion deliverable) |
| 3 | OTA firmware update untested | Medium | Test OTA via `espota.py` before sealing electronics |
| 4 | CTC Bizer needs calibration | **High** | Print calibration card + bearing test before committing |
| 5 | WiFi credentials in config.h | Low | Acceptable for Phase 1 (local dev); Phase 2 uses secrets |
| 6 | Encoder-based stall detect | Low | Optional in Phase 1 (no encoders on all motors) |
| 7 | Body quadrant RL/RR bed fit | **Resolved** | Trim cut added to `body_quadrant.py` |
| 8 | Top deck 4-tile export | **Resolved** | Fixed in `batch_export_all.py` |

### 10.2 Phase 2 Forward Compatibility

Phase 1 design decisions that support Phase 2 upgrade path:

| Phase 1 Design | Phase 2 Upgrade | Compatibility |
|----------------|-----------------|---------------|
| 4-channel L298N motor control | 6-channel Cytron MDD10A | Firmware GPIO remap only |
| SG90 servos on LEDC GPIO | MG996R on PCA9685 I2C | Module swap in steering.h |
| NMEA text UART | COBS binary UART | uart_binary.h already exists |
| WebSocket direct to ESP32 | WebSocket via Jetson ROS2 | Protocol unchanged |
| 2S LiPo 7.4V | 6S LiPo 22.2V + BMS | Power system redesign |
| PLA body (0.4 scale) | PETG/ASA + aluminium (1.0) | Full mechanical redesign |

### 10.3 Traceability Summary

| EA Document | Sections Integrated | Key Interfaces |
|-------------|-------------------|----------------|
| EA-01 | Suspension geometry, bearing layout | M-01 to M-06 |
| EA-02 | Motor specs, driver selection | E-07, E-09, X-02 |
| EA-03 | Power budget, battery specs | E-01 to E-06, X-03 |
| EA-08 | Phase 1 dimensions, BOM | M-10 to M-15 |
| EA-09 | GPIO pin allocation | E-07, E-08, E-10, E-11 |
| EA-10 | Ackermann geometry, steering angles | S-04, X-01 |
| EA-12 | UART protocol, message types | S-05, S-06 |
| EA-13 | ROS2 architecture (Phase 2 ref) | — |
| EA-15 | Safety systems, interlocks | S-07 to S-11, X-04 |
| EA-16 | PWA design, WebSocket protocol | S-01 to S-04 |
| EA-17 | Build guide, assembly sequence | Section 7 |
| EA-19 | Wiring diagram, connector strategy | E-01 to E-12, X-05, X-06 |
| EA-21 | Test procedures | Section 8 |
| EA-23 | Wire harness schedule | Section 4.5 |
| EA-25 | Suspension tube+connector design | M-01 to M-06 |
| EA-26 | Differential mechanism | M-01, M-02 |
| EA-27 | Steering system, horn link 4-bar | M-07 to M-12, X-01 |

---

*Document EA-28 v1.0 — 2026-03-25*
