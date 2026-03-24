# Master Engineering Handbook

**Document**: EA-00
**Date**: 2026-03-15
**Purpose**: Comprehensive reference compiling all engineering analyses (EA-01 through EA-24) into one authoritative document. Summarises key specifications, decisions, and cross-references for the Mars Rover Garden Robot project.
**Status**: Living document -- updated as EAs are revised.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Mechanical Design Summary](#2-mechanical-design-summary)
3. [Electrical Design Summary](#3-electrical-design-summary)
4. [Software Architecture Summary](#4-software-architecture-summary)
5. [Safety & Environmental](#5-safety--environmental)
6. [Build Planning](#6-build-planning)
7. [Master Specifications Table](#7-master-specifications-table)
8. [Document Index](#8-document-index)
9. [Glossary](#9-glossary)
10. [Revision History](#10-revision-history)

---

## 1. Project Overview

### 1.1 Mission Statement

A Mars rover-inspired outdoor garden robot capable of autonomous navigation, object detection, environmental monitoring, and remote control via a phone PWA. Designed as a hobby project with incremental build phases, progressing from a small 3D-printed prototype to a full-scale metal-bodied rover.

### 1.2 Build Phases

| Phase | Scale | Body | Brain | Goal |
|-------|-------|------|-------|------|
| Phase 1 | 0.4x | 3D printed (PLA) | ESP32-S3 only | Validate rocker-bogie mechanics, basic WiFi driving |
| Phase 2 | 1.0x | 3D printed (PETG/ASA) + aluminium extrusion | ESP32-S3 + Jetson Orin Nano Super | Full feature set: AI vision, SLAM, arms, solar, fridge |
| Phase 3 | 1.0x | Aluminium sheet + tube | Same as Phase 2 | Durability, weatherproofing (IP54), outdoor permanence |

### 1.3 System Architecture

The rover uses a dual-processor architecture:

- **ESP32-S3 (N16R8)**: Real-time motor controller. Handles PWM for 6 motors and 4 (Phase 1) or 14 (Phase 2) servos, encoder reading, battery monitoring, E-stop, and safety watchdogs. Communicates upstream via UART.
- **Jetson Orin Nano Super** (Phase 2+): AI brain running ROS2 Humble. Handles SLAM, Nav2 path planning, YOLO object detection, camera processing, and high-level autonomy. Communicates downstream to ESP32 via UART.
- **Phone PWA**: Remote control interface. Connects via WebSocket (Phase 1 direct to ESP32, Phase 2 via Jetson). Catppuccin Mocha dark theme with Mars red accent.

```
Phone (PWA)
    |
    | WebSocket (WiFi)
    v
Jetson Orin Nano Super (Phase 2)     <-- ROS2, Nav2, YOLO, SLAM
    |
    | UART (text Phase 1 / binary Phase 2)
    v
ESP32-S3 (N16R8)                     <-- Motor control, safety, sensors
    |
    +-- 6x DC motors (via L298N / Cytron MDD10A)
    +-- 4-14x servos (direct PWM / via PCA9685)
    +-- Encoders, IMU, GPS, battery ADC
    +-- E-stop, watchdog, safety systems
```

### 1.4 Design Heritage (EA-07)

The design draws from three NASA-derived open-source rover projects:

| Project | What We Take | What We Skip |
|---------|-------------|-------------|
| JPL Open Source Rover | Rocker-bogie geometry ratios, differential bar concept | Complex aluminium machining, expensive servos |
| Sawppy | Hybrid construction (extrusion skeleton + 3D printed connectors + heat-set inserts) | Specific CAD files (we design our own) |
| ExoMy (ESA) | All-printed prototype approach for Phase 1 validation | Simplified suspension (no rocker-bogie) |

**Selected approach**: Sawppy-inspired hybrid construction. 2020 aluminium V-slot extrusion forms the structural skeleton; 3D-printed connectors (PLA for Phase 1, PETG for Phase 2) join extrusions and house bearings; M3 brass heat-set inserts provide threaded attachment points.

---

## 2. Mechanical Design Summary

### 2.1 Suspension -- Rocker-Bogie (EA-01)

The rocker-bogie is a passive, linkage-based suspension with no springs or dampers. Each side has a rocker arm (pivots at the body) connected to a bogie arm (pivots at the rocker end). This gives 6-point ground contact and the ability to climb obstacles equal to the wheel diameter.

**Full-Scale Geometry (Phase 2/3)**:

| Parameter | Value | Source |
|-----------|-------|--------|
| Wheelbase (front to rear) | 900 mm | EA-01 s2.1 |
| Track width (left to right) | 700 mm | EA-01 s2.1 |
| Wheel diameter | 200 mm | EA-01 s2.2 |
| Wheel width | 80 mm | EA-01 s2.2 |
| Rocker arm length | 450 mm | EA-01 s2.3 |
| Bogie arm length | 300 mm | EA-01 s2.3 |
| Ground clearance | 150 mm | EA-01 s2.4 |
| Max obstacle height | 150 mm (1x wheel dia.) | EA-01 s3.1 |
| Body tilt limit | ~49 deg | EA-01 s3.2 |
| Bearings | 608ZZ (8mm bore), 19 total | EA-01 s4 |

**Phase 1 (0.4 Scale)**:

| Parameter | Value |
|-----------|-------|
| Wheelbase | 360 mm |
| Track width | 280 mm |
| Wheel diameter | 80 mm |
| Body dimensions | 440 x 260 x 80 mm |
| Max obstacle | 60 mm |

The differential bar connects left and right rocker arms through the body, ensuring equal-and-opposite tilt. Phase 1 uses a simple pivot; Phase 2+ uses a proper differential mechanism.

**Rocker-Bogie Behaviour**:
- When one wheel encounters an obstacle, the rocker pivots and the bogie adjusts, keeping all 6 wheels on the ground.
- The body tilts at half the angle of the suspension articulation (differential bar effect).
- No springs or shock absorbers needed -- the geometry itself provides passive compliance.
- Maximum obstacle height equals wheel diameter (fundamental rocker-bogie property from JPL geometry ratios).

### 2.2 Steering -- Ackermann Geometry (EA-10)

Four-wheel steering with three selectable modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| Ackermann | Inner wheels turn more than outer; all wheels track concentric arcs | Normal driving, curves |
| Point Turn | Front and rear wheels steer in opposite directions; rover spins in place | Tight spaces, 0-radius turn |
| Crab Walk | All 4 wheels steer same angle; rover moves sideways | Parallel parking, lateral approach |

**Key Steering Specs**:

| Parameter | Value | Source |
|-----------|-------|--------|
| Max steering angle | +/-35 deg | EA-10 s2.1 |
| Min turn radius (Ackermann) | 993 mm (full scale) | EA-10 s2.2 |
| Steering servos (Phase 1) | 4x SG90 (1.8 kg-cm) | EA-02 s4.1 |
| Steering servos (Phase 2) | 4x MG996R (13 kg-cm) | EA-02 s4.2 |
| Speed-dependent limit | Angle restricted at higher speeds | EA-10 s3.3 |

Ackermann geometry is computed in firmware using `atan()` from the wheelbase and track width. The inner wheel angle is always greater than the outer to prevent tyre scrub (EA-10 s2.3).

### 2.3 Dimensions and Weight (EA-05, EA-08)

| Metric | Phase 1 | Phase 2 | Phase 3 | Source |
|--------|---------|---------|---------|--------|
| Body length | 440 mm | ~1100 mm | ~1100 mm | EA-08 s2, EA-05 |
| Body width | 260 mm | ~700 mm | ~700 mm | EA-08 s2, EA-05 |
| Body height | 80 mm | ~200 mm | ~200 mm | EA-08 s2, EA-05 |
| Total weight (empty) | 1.1 kg | 16.7 kg | 20.8 kg | EA-05 s3 |
| Total weight (loaded) | 1.1 kg | 18.7 kg | 22.8 kg | EA-05 s3 |
| Centre of gravity height | -- | 232 mm | 232 mm | EA-05 s4 |
| Tilt limit (loaded) | -- | 56.5 deg | 56.5 deg | EA-05 s4 |
| Wheel ground pressure | -- | 5.1 kPa | 6.2 kPa | EA-05 s5 |

### 2.4 3D Printing Strategy (EA-11)

| Parameter | Phase 1 | Phase 2 | Source |
|-----------|---------|---------|--------|
| Primary material | PLA | ASA (structural) + PETG (internal) | EA-11 s2 |
| Printer | CTC Bizer (225x145x150 mm) | TBD (PETG-capable) | EA-11 s3 |
| Total parts | 26 | ~65 | EA-08 s4, EA-11 s4 |
| Print time | ~69 hrs | ~317 hrs | EA-08 s4, EA-11 s5 |
| Filament mass | ~1 kg | ~5.5 kg | EA-08 s4, EA-11 s5 |
| Filament cost | ~$20 | $130-160 | EA-11 s5 |
| Insert type | M3 brass heat-set (5.7 mm OD) | Same | EA-11 s6 |
| Insert pull-out force | 600-900 N | 600-900 N | EA-11 s6 |
| UV protection | None (indoor use) | ASA inherent + optional clear coat | EA-11 s7 |

Phase 1 prints are designed to fit the 225x145 mm CTC Bizer bed (body splits into 4 quadrants). Larger Phase 2 parts split into interlocking segments with heat-set insert joints.

**Print Settings (recommended)**:

| Parameter | PETG | ASA |
|-----------|------|-----|
| Nozzle temp | 230-240 C | 240-260 C |
| Bed temp | 70-80 C | 90-110 C |
| Layer height | 0.2 mm (structural), 0.12 mm (bearings) | 0.2 mm |
| Infill | 25-40% gyroid | 30-50% gyroid |
| Walls | 3-4 perimeters | 4 perimeters |
| Enclosure | Not required | Required (warping) |

**Heat-Set Insert Specification** (EA-11 s6):
- Type: M3 brass, knurled, tapered
- OD: 5.7 mm (hole prints at 5.0 mm, insert melts into surrounding plastic)
- Length: 4.0 mm (short) or 6.0 mm (structural)
- Pull-out force: 600-900 N in PETG
- Installation: soldering iron at 220 C, press vertically, allow 10s cooling

---

## 3. Electrical Design Summary

### 3.1 Power System (EA-03)

**Phase 1**:

| Parameter | Value | Source |
|-----------|-------|--------|
| Battery | 2S LiPo 2200 mAh, 7.4 V, XT60 | EA-03 s2.1 |
| Main fuse | 5A blade (ATC) | EA-19 s1.3 |
| Motor drivers | 2x L298N dual H-bridge | EA-02 s3.1 |
| 5V regulation | L298N onboard 78M05 (0.5-1A) | EA-19 s1.4 |
| Typical draw | ~3-4A | EA-03 s3.1 |
| Runtime (driving) | ~30 min | EA-03 s3.1 |

**Phase 2/3**:

| Parameter | Value | Source |
|-----------|-------|--------|
| Battery | 2x 6S LiPo 10000 mAh (22.2 V, 444 Wh total) | EA-03 s2.2 |
| Motor drivers | 3x Cytron MDD10A (10A/ch) | EA-02 s3.2 |
| Buck 22V to 12V | 10A converter (Jetson, motors) | EA-03 s4.1 |
| Buck 22V to 5V | 8A converter (logic, cameras) | EA-03 s4.2 |
| UBEC 22V to 6V | 5A (14 servos via PCA9685) | EA-03 s4.3 |
| Solar panels | 4x 25W monocrystalline (2S2P, 100W) | EA-03 s5 |
| MPPT controller | CN3722 module | EA-03 s5.2 |
| Typical system draw | 97.5 W | EA-03 s3.2 |
| Runtime (driving, no solar) | ~4 hrs | EA-03 s3.2 |
| Low-battery stages | 20% warning, 10% limp mode, 5% auto-dock | EA-03 s6, EA-15 s3 |

### 3.2 Drivetrain (EA-02)

| Parameter | Phase 1 | Phase 2/3 | Source |
|-----------|---------|-----------|--------|
| Motors | 6x N20 100 RPM (6V, with encoder) | 6x Chihai CHR-GM37-520 80 RPM (12V) | EA-02 s2 |
| Stall torque | ~1.5 kg-cm | 35 kg-cm | EA-02 s2 |
| Drivers | 2x L298N (4 channels for 6 motors) | 3x Cytron MDD10A (6 independent channels) | EA-02 s3 |
| Grouping | W1 independent, W2+W3 parallel, W6 independent, W5+W4 parallel | All 6 independent | EA-02 s3, EA-19 s3 |
| Encoders | Hall effect on W1 and W6 (optional) | Hall effect on all 6 (0.32 mm/count) | EA-02 s5 |
| Top speed | ~2 km/h | ~5 km/h | EA-02 s6 |
| Worst-case torque | -- | 33.5 kg-cm (20 deg slope + soft ground) | EA-02 s7 |

### 3.3 ESP32-S3 GPIO Pin Map (EA-09)

**Phase 1 Pin Usage (20 active pins)**:

| Function | GPIOs | Count |
|----------|-------|-------|
| Motor PWM (LEDC Ch0-3) | 4, 7, 8, 11 | 4 |
| Motor direction (IN1-IN4) | 5, 6, 9, 10, 12, 13, 15, 16 | 8 |
| Servo signals (LEDC Ch4-7) | 1, 2, 41, 42 | 4 |
| Battery ADC | 14 | 1 |
| E-stop (input-only) | 46 | 1 |
| Status LED | 0 | 1 |
| Encoders (optional, PCNT) | 38, 39, 40, 48 | 4 |
| USB (reserved) | 19, 20 | 2 |
| PSRAM (DO NOT USE) | 26-37 | 12 |

**Phase 2 additions**: GPIO1 and GPIO2 reassigned from servos to I2C bus (BNO055 IMU, PCA9685). All 14 servos move to PCA9685 I2C PWM driver. UART1 on GPIO43/44 connects to Jetson. Total: 28 active pins (EA-09 s3).

### 3.4 Compute and Sensors (EA-04)

| Component | Spec | Cost | Source |
|-----------|------|------|--------|
| Jetson Orin Nano Super | 67 TOPS, 8GB, JetPack 6.x | $249 | EA-04 s2.1 |
| ESP32-S3 DevKit | N16R8, 16MB flash, 8MB PSRAM | $8 | EA-04 s2.2 |
| Body cameras | 4x Arducam 120 deg USB | $60 | EA-04 s3.1 |
| Zoom camera | ELP 10x optical zoom USB | $50 | EA-04 s3.2 |
| Depth camera | OAK-D Lite (stereo + neural) | $89 | EA-04 s3.3 |
| Night vision | Pi NoIR v3 (CSI) + 4x IR LEDs | $30 | EA-04 s3.4 |
| LIDAR | RPLidar A1 (12m range, 360 deg) | $73 | EA-04 s4.1 |
| GPS | BN-220 (u-blox M8) | $12 | EA-04 s4.2 |
| IMU | BNO055 (9-axis, sensor fusion) | $15 | EA-04 s4.3 |
| Ultrasonic | 6x HC-SR04 | $9 | EA-04 s4.4 |
| PWM driver | PCA9685 16-ch I2C | $3 | EA-04 s5 |

### 3.5 Wiring Overview (EA-19)

Phase 1 wiring uses a simple topology:

1. **Battery** (2S LiPo, XT60) -> **5A fuse** -> **kill switch** -> **power distribution point**
2. Distribution splits to 2x L298N VCC (7.4V) and voltage divider (GPIO14 ADC)
3. L298N #1 onboard 5V regulator powers **5V bus** (ESP32 VIN + 4 servos)
4. All grounds connect via **star topology** to battery negative
5. Signal wires: 22 AWG Dupont female-female jumpers throughout (removable for debugging)
6. Motor wires: 18 AWG through rocker/bogie arm channels with 50mm slack at pivots

Key wiring rules (EA-19 s11):
- Remove L298N ENA/ENB jumpers (we control PWM from ESP32)
- Keep L298N 12V jumper ON (enables 5V regulator at VCC <= 12V)
- GPIO 26-37 reserved for PSRAM -- never connect anything
- GPIO46 is input-only (E-stop)
- Common ground is critical -- all GND points must connect via star topology to battery negative
- 100nF cap on GPIO14 for ADC noise filtering
- Colour code: red=power, black=GND, orange=PWM, yellow=direction, green=encoder, blue=ADC

**Wire Gauge Summary** (EA-03 s5.4, EA-19 s9):

| Run | Current | Gauge | Notes |
|-----|---------|-------|-------|
| Battery to distribution | 10A (P1) | 14 AWG silicone | XT60 connectors |
| Distribution to L298N | 5A per board | 16 AWG | Screw terminals |
| L298N output to motor | 2A per channel | 18 AWG | Through rocker/bogie arms, 50mm slack at pivots |
| 5V bus (ESP32 + servos) | 0.5-1A | 22 AWG | Dupont connectors |
| All signal wires | <100 mA | 22 AWG | Dupont female-female |

**Phase 1 to Phase 2 Electrical Migration**:

| Component | Phase 1 | Phase 2 Change | Reason |
|-----------|---------|---------------|--------|
| Motor drivers | 2x L298N (4ch) | 3x Cytron MDD10A (6ch) | Independent control for all 6 wheels |
| Servo control | Direct ESP32 PWM (4 servos) | PCA9685 I2C (14 servos) | Free GPIO1/2 for I2C bus |
| Battery | 2S 2200mAh (7.4V) | 2x 6S 10000mAh (22.2V) | 4hr runtime, solar compatible |
| Power regulation | L298N onboard 5V | 3x dedicated buck/UBEC | Higher current capacity |
| UART | USB serial debug only | UART1 to Jetson (binary COBS) | AI brain connection |
| Sensors | Battery ADC only | IMU, GPS, LIDAR, cameras | Full autonomy |

---

## 4. Software Architecture Summary

### 4.1 ROS2 Architecture (EA-13)

Phase 2 runs ROS2 Humble on the Jetson (Ubuntu 22.04, JetPack 6.x). Six ROS2 packages:

| Package | Purpose | Key Nodes |
|---------|---------|-----------|
| `rover_bringup` | Launch files, params, URDF | -- |
| `rover_description` | URDF/Xacro model, TF tree | `robot_state_publisher` |
| `rover_hardware` | ESP32 UART bridge | `esp32_bridge_node` |
| `rover_navigation` | Nav2 config, EKF, maps | `nav2`, `robot_localization` |
| `rover_perception` | Cameras, YOLO, depth | `yolo_node`, `camera_nodes` |
| `rover_autonomy` | Behaviour trees, missions | `bt_navigator` |

**Navigation stack (Nav2)**:
- Controller: RegulatedPurePursuit (smooth path following)
- Planner: SmacPlannerHybrid with DUBIN model (car-like kinematics)
- Costmap: 2-layer (static from SLAM map + obstacle layer from LIDAR/depth)
- Localisation: Dual EKF via `robot_localization` -- local filter (no GPS, high rate) + global filter (with GPS, lower rate)
- Mapping: `slam_toolbox` in async mode for online map building

**AI Vision**:
- YOLO v8n via TensorRT on Jetson GPU: ~60 FPS object detection
- OAK-D Lite: on-device depth + optional neural inference
- 4x body cameras: 360-degree coverage for obstacle detection and recording

**Estimated Resource Usage** (EA-13 s7):

| Resource | Estimate |
|----------|----------|
| CPU | ~56% of 6 cores |
| GPU | ~50% |
| RAM | ~1.87 GB of 8 GB |
| Disk (OS + ROS2 + models) | ~12 GB |

### 4.2 UART Protocols

Two protocol versions, one per build phase:

**Phase 1 -- Text NMEA (EA-12)**:

| Parameter | Value |
|-----------|-------|
| Format | `$CMD,data*XOR\n` (ASCII, human-readable) |
| Baud rate | 115200 |
| Checksum | XOR of all chars between `$` and `*` |
| Message types | 18 |
| Utilisation | 72% at 50 Hz motor commands |
| Round-trip latency | 7.7 ms |
| Safety timeout | 200 ms (motors stop if no command received) |

**Phase 2 -- Binary COBS (EA-18)**:

| Parameter | Value |
|-----------|-------|
| Format | COBS-framed binary packets with CRC-16/CCITT |
| Baud rate | 460800 |
| Encoding | Packed C structs, integer-only (no float) |
| Message types | 14 |
| Utilisation | 12% at 50 Hz |
| Round-trip latency | 1.6 ms |
| Safety timeout | 500 ms (with 200 ms ramp-down to stop) |
| Framing | COBS eliminates 0x00 from payload; 0x00 = frame delimiter |

The transition from text to binary in Phase 2 provides 5x lower latency, 6x lower bandwidth usage, and hardware CRC error detection.

**Protocol Comparison**:

| Metric | Phase 1 (Text) | Phase 2 (Binary) | Improvement |
|--------|---------------|------------------|-------------|
| Baud rate | 115200 | 460800 | 4x |
| Motor command size | ~30 bytes | ~12 bytes | 2.5x smaller |
| Bus utilisation | 72% | 12% | 6x lower |
| Round-trip latency | 7.7 ms | 1.6 ms | 5x faster |
| Error detection | XOR checksum (8-bit) | CRC-16/CCITT (16-bit) | More robust |
| Encoding | ASCII text | Packed C structs | Machine-efficient |
| Human-readable | Yes | No (use debug tools) | Trade-off |

**UART Safety**: Both protocols implement motor safety timeouts. If the ESP32 receives no motor command within the timeout period, it autonomously ramps motors down to zero. Phase 2 adds a 200ms ramp-down period before full stop (EA-18 s5) to prevent abrupt deceleration.

### 4.3 PWA Control App (EA-16)

| Feature | Detail | Source |
|---------|--------|--------|
| Theme | Catppuccin Mocha dark, Mars red (#E74C3C) accent | EA-16 s2 |
| Controls | D-pad + virtual joystick (touch), WASD (desktop) | EA-16 s3 |
| Protocol | WebSocket JSON (Phase 1 direct, Phase 2 via Jetson) | EA-16 s4 |
| Camera feeds | MJPEG streams from body cameras and zoom | EA-16 s5 |
| Telemetry | Battery %, speed, GPS, IMU, temperature | EA-16 s6 |
| Offline | Service worker (network-first), installable PWA | EA-16 s7 |
| Map | Leaflet.js with GPS track overlay and geofence editor | EA-16 s8 |

---

## 5. Safety & Environmental

### 5.1 Four-Layer Safety Architecture (EA-15)

| Layer | Components | Response Time | Source |
|-------|-----------|---------------|--------|
| **Hardware** | E-stop button (GPIO46), main fuse (5A), kill switch, relay | <1 ms (interrupt) | EA-15 s2.1 |
| **Firmware** | Watchdog (5s), UART timeout (200/500 ms), stall detection, tilt protection, battery undervoltage | 20-500 ms | EA-15 s2.2 |
| **Software** | Obstacle avoidance zones, geofence, human detection (YOLO), speed limits | 100-500 ms | EA-15 s2.3 |
| **Operational** | Pre-flight checks, manual override, remote E-stop via PWA | User-dependent | EA-15 s2.4 |

**Key Safety Behaviours**:
- **UART timeout**: If ESP32 receives no motor command within timeout period, motors ramp down to stop (EA-12 s5, EA-18 s5)
- **Battery protection**: 3-stage -- 20% warning LED, 10% limp mode (50% max speed), 5% auto-dock/shutdown (EA-15 s3)
- **Speed ramping**: 0-100% in 200 ms (smooth acceleration, prevents wheel spin) (EA-15 s4)
- **Stall detection**: If encoder count doesn't change while motor PWM > 0 for 2s, reduce power (EA-15 s4)
- **Tilt protection**: If IMU pitch/roll exceeds 45 deg, stop all motors (EA-15 s5)
- **Geofence**: GPS-defined polygon boundary; rover stops at edge (EA-15 s6)
- **Human detection**: YOLO detects people; rover slows or stops within safety radius (EA-15 s7)

**Phase 1 E-Stop** (EA-19 s6): Software-only. Tactile button on GPIO46 (input-only, internal pull-down). Button connects GPIO46 to 3.3V. Rising-edge interrupt toggles E-stop state. All motors coast-stop, servos hold position, status LED blinks red.

**Phase 2+ E-Stop**: Hardware disconnect. Red mushroom button with normally-closed contacts in series with motor power bus. Physical power cutoff even if firmware crashes.

### 5.2 Weatherproofing (EA-14)

Three-zone strategy applied progressively across phases:

| Zone | Contents | Phase 1 | Phase 2 | Phase 3 |
|------|----------|---------|---------|---------|
| A (Dry) | Jetson, ESP32, BMS, cameras | IP20 (indoor only) | IP44 (splash-proof lid + gasket) | IP54 (sealed enclosure + cable glands) |
| B (Splash) | Motors, servos, wiring | Exposed | Silicone conformal coat, shrink wrap | Sealed housings, IP44 connectors |
| C (Wet) | Wheels, undercarriage, axles | Exposed | Stainless fasteners, drain holes | Full stainless, sealed bearings (6001-2RS) |

**Phase progression**: IP20 (Phase 1, indoor testing only) -> IP44 (Phase 2, light rain survivable) -> IP54 (Phase 3, outdoor permanent with dust/splash protection).

Cable gland count: 11 in Phase 3 (EA-14 s4). Thermal management via passive ventilation in Phase 2, optional fan in Phase 3 for Jetson enclosure (EA-14 s5). Seasonal maintenance schedule defined in EA-14 s7.

**Weatherproofing Progression Detail**:

| Feature | Phase 1 (IP20) | Phase 2 (IP44) | Phase 3 (IP54) |
|---------|---------------|---------------|----------------|
| Electronics enclosure | Open body shell | Gasketed lid, silicone sealant | Sealed aluminium box, cable glands |
| Motor protection | None | Conformal coat, heat shrink | Sealed motor housings |
| Connectors | Dupont (open) | JST-XH (splash-resistant) | IP44 rated circular connectors |
| Cable routing | External ok | Internal channels | Fully enclosed, grommet seals |
| Bearing seals | 608ZZ (open) | 608ZZ + grease | 6001-2RS (rubber sealed) |
| Operating conditions | Indoor only | Light rain, dry grass | All weather except heavy rain/snow |

---

## 6. Build Planning

### 6.1 Phase 1 Build Timeline (EA-17)

A 14-day plan with 3 ordering batches:

| Days | Activity | Depends On |
|------|----------|------------|
| 1-2 | Order batch 1 (filament). Start printing body parts. | -- |
| 3-5 | Print suspension arms, wheel hubs. Order batch 2 (electronics). | Batch 1 delivered |
| 6-8 | Print wheels, brackets. Solder power system. | Prints done, batch 2 delivered |
| 9-10 | Assemble chassis. Install heat-set inserts. Order batch 3 (battery, fasteners). | Prints done |
| 11-12 | Wire motors, servos, ESP32. Upload firmware. | All parts delivered |
| 13 | Testing: individual motors, servos, E-stop. | Wiring complete |
| 14 | Integration test: drive on floor, obstacle test. | All tests pass |

**Phase 1 Print Schedule**: ~65 hours over 10 days. 22 parts printed in dependency order: body shell first (need it to dry-fit electronics), then suspension arms, then wheels and brackets last (EA-08 s4, EA-17 s3).

### 6.2 Cost Summary (EA-06)

| Phase | Component Cost | Contingency | Budget Total |
|-------|---------------|-------------|--------------|
| Phase 1 (0.4 prototype) | $102 | included | $102 |
| Phase 2 (full 3D print) | $1,482.50 | $148.25 (10%) | $1,630.75 |
| Phase 3 (metal, additional) | $260 | $39 (15%) | $299 |
| **Grand Total** | **$1,844.50** | **$187.25** | **$2,031.75** |

**Phase 2 Cost Breakdown by Category**:

| Category | Cost | Source |
|----------|------|--------|
| Compute & Electronics | $292 | EA-06 s2.1 |
| Cameras & Vision | $229 | EA-06 s2.2 |
| Navigation Sensors | $109 | EA-06 s2.3 |
| Drivetrain | $141 | EA-06 s2.4 |
| Arms & Mast | $68 | EA-06 s2.5 |
| Power System | $185 | EA-06 s2.6 |
| Solar | $103 | EA-06 s2.7 |
| Accessories | $96.50 | EA-06 s2.8 |
| Structure & Hardware | $234 | EA-06 s2.9 |
| Docking Station | $25 | EA-06 s2.10 |

**Minimum Viable Rover** (if budget constrained): Compute + cameras + drivetrain + power + structure = **$764**. Everything else (arms, solar, fridge, weather station, LIDAR) can be added incrementally (EA-06 s5).

### 6.3 Phase 2 Prioritised Build Order (EA-06)

12-stage purchasing order to spread costs and enable incremental testing:

| Order | Components | Cost | Enables |
|-------|-----------|------|---------|
| 1 | Structure (filament, extrusion, fasteners, bearings) | $234 | Printed/assembled chassis |
| 2 | Drivetrain (motors, drivers, steering servos) | $141 | Rolling chassis |
| 3 | Power (batteries, BMS, converters, wiring) | $185 | Powered driving |
| 4 | Compute (Jetson, ESP32, SD cards, USB hub) | $292 | AI brain |
| 5 | Body cameras (4x Arducam) | $60 | 360-degree vision |
| 6 | Nav sensors (LIDAR, GPS, IMU, ultrasonic) | $109 | Autonomous navigation |
| 7 | Depth + zoom cameras | $139 | Full vision suite |
| 8 | Arms + mast (servos, slip ring) | $68 | Manipulation |
| 9 | Solar (panels, MPPT, hinges) | $103 | Solar charging |
| 10 | Accessories (fridge, LEDs, weather, speaker, display) | $96 | Full features |
| 11 | Docking station | $25 | Autonomous charging |
| 12 | Night vision (NoIR camera, IR LEDs) | $30 | Night operation |

### 6.4 Cost Reduction Options (EA-06)

| Saving | Action | Impact |
|--------|--------|--------|
| -$100 | Jetson Orin Nano 8GB instead of Super | Lower AI performance (40 vs 67 TOPS) |
| -$89 | Skip OAK-D Lite, use stereo pair | Lose on-device neural inference |
| -$103 | Defer solar panels | Mains/dock charging only |
| -$73 | Defer RPLidar, ultrasonic-only navigation | Lose SLAM mapping |
| -$68 | Defer robotic arms | Lose manipulation capability |
| -$96 | Skip accessories | Core rover still functional |

### 6.5 Phase 1 Shopping List (EA-06, EA-17)

Three ordering batches, structured so printing can begin immediately:

**Batch 1 (order first, start printing while waiting for batches 2-3)**:
- 1x PLA filament 1kg spool ($20)

**Batch 2 (electronics)**:
- 1x ESP32-S3 DevKit N16R8 ($8)
- 6x N20 DC gearmotors 6V 100RPM with encoder ($18)
- 4x SG90 micro servos ($8)
- 2x L298N motor drivers ($6)
- 1x breadboard + jumper wires ($5)
- 1x switch + wiring ($3)

**Batch 3 (assembly hardware + battery)**:
- 1x 2S LiPo 2200mAh ($12)
- 1x LiPo charger ($8)
- 9x 608ZZ bearings — buy 12 ($5)
- 1x M3 fastener set ($6)
- 50x M3 heat-set inserts ($3)

**Total Phase 1**: $102 (EA-06 s1)

### 6.6 Open Source Heritage (EA-07)

| Attribute | JPL OSR | Sawppy | ExoMy | Our Rover |
|-----------|---------|--------|-------|-----------|
| Suspension | Rocker-bogie | Rocker-bogie | Modified rocker | Rocker-bogie (JPL ratios) |
| Construction | Aluminium machined | Extrusion + 3D print | All 3D print | Extrusion + 3D print (Sawppy method) |
| Steering | 4-wheel servo | 4-wheel servo | 4-wheel servo | 4-wheel Ackermann |
| Motors | Servocity | Hobby gearmotors | Hobby servos | Chihai gearmotors + encoders |
| Compute | Arduino + RPi | Arduino + RPi | RPi | ESP32-S3 + Jetson Orin Nano |
| AI / Vision | None | None | Basic camera | YOLO + SLAM + depth |
| Cost | ~$2,500 | ~$500-600 | ~$250 | ~$2,032 (all phases) |

---

## 7. Master Specifications Table

Comprehensive table of every key specification, its value, and the source EA.

### 7.1 Mechanical Specs

| Spec | Value | Phase | Source EA |
|------|-------|-------|----------|
| Wheel diameter | 80 mm / 200 mm | P1 / P2 | EA-01 s2.2 |
| Wheel width | 32 mm / 80 mm | P1 / P2 | EA-01 s2.2 |
| Wheelbase | 360 mm / 900 mm | P1 / P2 | EA-01 s2.1 |
| Track width | 280 mm / 700 mm | P1 / P2 | EA-01 s2.1 |
| Rocker arm length | 180 mm / 450 mm | P1 / P2 | EA-01 s2.3 |
| Bogie arm length | 180 mm / 300 mm | P1 / P2 | EA-01 s2.3 |
| Ground clearance | 60 mm / 150 mm | P1 / P2 | EA-01 s2.4 |
| Max obstacle height | 60 mm / 150 mm | P1 / P2 | EA-01 s3.1 |
| Body tilt limit | -- / ~49 deg | -- / P2 | EA-01 s3.2 |
| CoG tilt limit (loaded) | -- / 56.5 deg | -- / P2 | EA-05 s4 |
| Max steering angle | +/-35 deg | All | EA-10 s2.1 |
| Min turn radius (Ackermann) | 397 mm / 993 mm | P1 / P2 | EA-10 s2.2 |
| Total bearings | 9 / 19 | P1 / P2 | EA-01 s4, EA-25 s2B |
| Bearing type | 608ZZ (8mm) | P1/P2 | EA-01 s4 |
| Bearing type (Phase 3) | 6001-2RS sealed | P3 | EA-06 s4 |

### 7.2 Drivetrain Specs

| Spec | Value | Phase | Source EA |
|------|-------|-------|----------|
| Motor (Phase 1) | N20 DC, 6V, 100 RPM, with encoder | P1 | EA-02 s2.1, EA-06 s1 |
| Motor (Phase 2) | Chihai CHR-GM37-520, 12V, 80 RPM | P2 | EA-02 s2.2 |
| Motor stall torque | 1.5 / 35 kg-cm | P1 / P2 | EA-02 s2 |
| Motor driver (Phase 1) | 2x L298N dual H-bridge | P1 | EA-02 s3.1 |
| Motor driver (Phase 2) | 3x Cytron MDD10A (10A/ch) | P2 | EA-02 s3.2 |
| Motor PWM frequency | 1 kHz | All | EA-09 s2, EA-19 s3.5 |
| Motor PWM resolution | 8-bit (0-255) | All | EA-19 s3.5 |
| Motor channels (Phase 1) | 4 (FL, LM+LR, FR, RM+RR) | P1 | EA-19 s3.3 |
| Motor channels (Phase 2) | 6 (all independent) | P2 | EA-02 s3.2 |
| Encoder resolution | 0.32 mm/count | P2 | EA-02 s5 |
| Top speed | ~2 / ~5 km/h | P1 / P2 | EA-02 s6 |
| Steering servo (Phase 1) | 4x SG90, 1.8 kg-cm | P1 | EA-02 s4.1 |
| Steering servo (Phase 2) | 4x MG996R, 13 kg-cm | P2 | EA-02 s4.2 |
| Steering servo (Phase 3) | 4x DS3218, 20 kg-cm | P3 | EA-06 s4 |
| Servo PWM frequency | 50 Hz | All | EA-19 s4.4 |
| Servo pulse range | 500-2400 us | All | EA-19 s4.4 |
| Servo centre | 1500 us | All | EA-19 s4.4 |

### 7.3 Electrical Specs

| Spec | Value | Phase | Source EA |
|------|-------|-------|----------|
| MCU | ESP32-S3-WROOM-1 N16R8 | All | EA-04 s2.2, EA-09 |
| Flash | 16 MB | All | EA-09 s1 |
| PSRAM | 8 MB (GPIO 26-37 reserved) | All | EA-09 s1 |
| AI computer | Jetson Orin Nano Super, 67 TOPS | P2+ | EA-04 s2.1 |
| Battery (Phase 1) | 2S LiPo 2200 mAh, 7.4V | P1 | EA-03 s2.1 |
| Battery (Phase 2) | 2x 6S LiPo 10000 mAh, 22.2V, 444 Wh | P2 | EA-03 s2.2 |
| Main fuse | 5A blade (Phase 1), 20A + per-rail (Phase 2) | All | EA-19 s1.3, EA-15 s3.2 |
| Solar | 4x 25W mono (100W total, 2S2P) | P2 | EA-03 s5 |
| MPPT | CN3722 module | P2 | EA-03 s5.2 |
| Typical power draw | 3-4A (P1) / 97.5W (P2) | P1/P2 | EA-03 s3 |
| Runtime | ~30 min (P1) / ~4 hrs (P2) | P1/P2 | EA-03 s3 |
| Battery ADC divider | 10k / 4.7k (scale 3.128) | All | EA-19 s5.1 |
| PWM driver | PCA9685 16-ch I2C | P2 | EA-04 s5 |

### 7.4 Sensor Specs

| Spec | Value | Phase | Source EA |
|------|-------|-------|----------|
| LIDAR | RPLidar A1, 12m range, 360 deg | P2 | EA-04 s4.1 |
| GPS | BN-220, u-blox M8, 10 Hz | P2 | EA-04 s4.2 |
| IMU | BNO055, 9-axis, sensor fusion | P2 | EA-04 s4.3 |
| Ultrasonic | 6x HC-SR04, 4m range | P2 | EA-04 s4.4 |
| Body cameras | 4x Arducam 120 deg USB | P2 | EA-04 s3.1 |
| Zoom camera | ELP 10x optical USB | P2 | EA-04 s3.2 |
| Depth camera | OAK-D Lite, stereo + neural | P2 | EA-04 s3.3 |
| Night vision | Pi NoIR v3 CSI + 4x 850nm IR LEDs | P2 | EA-04 s3.4 |
| Weather: temp/humidity/pressure | BME280 | P2 | EA-06 s2.8 |
| Weather: wind | Cup anemometer | P2 | EA-06 s2.8 |
| Weather: rain | YL-83 | P2 | EA-06 s2.8 |
| Weather: UV | VEML6075 | P2 | EA-06 s2.8 |
| Weather: light | BH1750 | P2 | EA-06 s2.8 |
| Current monitoring | 4x INA219 | P2 | EA-06 s2.8 |
| Temperature probes | 3x DS18B20 | P2 | EA-06 s2.8 |

### 7.5 Software Specs

| Spec | Value | Phase | Source EA |
|------|-------|-------|----------|
| ROS2 distro | Humble Hawksbill | P2 | EA-13 s1 |
| OS (Jetson) | Ubuntu 22.04 (JetPack 6.x) | P2 | EA-13 s1 |
| Nav2 controller | RegulatedPurePursuit | P2 | EA-13 s3 |
| Nav2 planner | SmacPlannerHybrid (DUBIN) | P2 | EA-13 s3 |
| SLAM | slam_toolbox (async) | P2 | EA-13 s4 |
| Localisation | Dual EKF (local + global) | P2 | EA-13 s5 |
| Object detection | YOLO v8n via TensorRT, ~60 FPS | P2 | EA-13 s6 |
| UART baud | 115200 (P1) / 460800 (P2) | P1/P2 | EA-12 s2, EA-18 s2 |
| UART protocol | Text NMEA (P1) / Binary COBS+CRC-16 (P2) | P1/P2 | EA-12, EA-18 |
| UART safety timeout | 200 ms (P1) / 500 ms (P2) | P1/P2 | EA-12 s5, EA-18 s5 |
| WiFi control port | HTTP 80, WebSocket 81 | P1 | EA-16 s4 |
| PWA theme | Catppuccin Mocha + Mars red | All | EA-16 s2 |
| Watchdog timeout | 5 s | All | EA-15 s2.2 |
| E-stop GPIO | 46 (input-only, internal pull-down) | All | EA-15 s2.1, EA-19 s6 |
| Speed ramp time | 200 ms (0-100%) | All | EA-15 s4 |

### 7.6 Weight Specs

| Spec | Phase 1 | Phase 2 | Phase 3 | Source EA |
|------|---------|---------|---------|----------|
| Chassis (empty) | 0.4 kg | 5.2 kg | 8.5 kg | EA-05 s3 |
| Electronics | 0.2 kg | 2.8 kg | 2.8 kg | EA-05 s3 |
| Drivetrain | 0.3 kg | 4.2 kg | 4.2 kg | EA-05 s3 |
| Power system | 0.2 kg | 4.5 kg | 5.3 kg | EA-05 s3 |
| Total (empty) | 1.1 kg | 16.7 kg | 20.8 kg | EA-05 s3 |
| Payload capacity | -- | 2.0 kg | 2.0 kg | EA-05 s3 |
| Total (loaded) | 1.1 kg | 18.7 kg | 22.8 kg | EA-05 s3 |

### 7.7 Printing Specs

| Spec | Phase 1 | Phase 2 | Source EA |
|------|---------|---------|----------|
| Material | PLA | ASA (structural) + PETG (internal) | EA-11 s2 |
| Printer bed | 220 x 220 mm | Same | EA-11 s3 |
| Part count | 22 | ~65 | EA-08 s4, EA-11 s4 |
| Total print time | ~65 hrs | ~317 hrs | EA-08 s4, EA-11 s5 |
| Filament used | ~1 kg | ~5.5 kg | EA-08 s4, EA-11 s5 |
| Filament cost | ~$20 | $130-160 | EA-11 s5 |
| Insert type | M3 brass heat-set, 5.7 mm OD | Same | EA-11 s6 |
| Insert pull-out force | 600-900 N | Same | EA-11 s6 |

### 7.8 Communication Specs

| Spec | Value | Phase | Source EA |
|------|-------|-------|----------|
| WiFi | 802.11 b/g/n (ESP32-S3) | All | EA-09, EA-16 |
| HTTP server port | 80 | P1 | EA-16 s4 |
| WebSocket port | 81 | P1 | EA-16 s4 |
| WiFi hostname | "rover" | P1 | EA-16 s4 |
| UART TX/RX GPIOs | 43/44 | P2 | EA-09, EA-18 |
| UART baud (Phase 1) | 115200 | P1 | EA-12 s2 |
| UART baud (Phase 2) | 460800 | P2 | EA-18 s2 |
| UART message rate | 50 Hz motor commands | All | EA-12 s3, EA-18 s3 |
| I2C bus (Phase 2) | GPIO1 (SDA), GPIO2 (SCL), 400 kHz | P2 | EA-09 s3 |
| I2C devices | PCA9685 (0x40), BNO055 (0x28) | P2 | EA-04, EA-09 |

### 7.9 Robotic Arms & Mast Specs (Phase 2)

| Spec | Value | Source EA |
|------|-------|----------|
| Arm servos | 8x MG996R (13 kg-cm) | EA-06 s2.5 |
| Mast servos | 2x MG996R (pan/tilt) | EA-06 s2.5 |
| Mast slip ring | 12-wire, 22mm bore | EA-06 s2.5 |
| Total arm/mast servos | 10 | EA-06 s2.5 |
| PWM driver | PCA9685 (shared with steering) | EA-04 s5 |
| Servo power | 6V UBEC, 5A | EA-03 s4.3 |

### 7.10 Accessories Specs (Phase 2)

| Accessory | Components | Cost | Source EA |
|-----------|-----------|------|----------|
| Mini fridge | Peltier TEC1-12706, heatsink+fan, foam insulation | $15 | EA-06 s2.8 |
| Wireless charging | Qi 15W module, USB-C PD trigger | $12 | EA-06 s2.8 |
| Lighting | WS2812B strip (2m), 2x 3W headlights, indicators | $15 | EA-06 s2.8 |
| Audio | 2x 3W speakers, MAX98357A amp, 2x SPH0645 mics | $16 | EA-06 s2.8 |
| Weather station | BME280, anemometer, rain, UV, light sensors | $22 | EA-06 s2.8 |
| Display | 3.5" IPS LCD (SPI) | $12 | EA-06 s2.8 |
| Docking station | 4x spring copper contacts, 24V 5A PSU, ArUco marker | $25 | EA-06 s2.10 |

---

## 8. Document Index

| EA | Title | File | Key Content | Dependencies |
|----|-------|------|-------------|--------------|
| EA-01 | Suspension Analysis | `01-suspension-analysis.md` | Rocker-bogie geometry, bearing selection, obstacle capability, 0.4 scale ratios | -- |
| EA-02 | Drivetrain Analysis | `02-drivetrain-analysis.md` | Motor selection (N20/Chihai), driver selection (L298N/Cytron), torque calculations, encoder specs, servo selection | EA-01 |
| EA-03 | Power System Analysis | `03-power-system-analysis.md` | Battery sizing (2S/6S LiPo), wire gauges, fuse ratings, buck converters, solar panels, MPPT, docking station, low-battery behaviour | EA-02 |
| EA-04 | Compute & Sensors Analysis | `04-compute-sensors-analysis.md` | Jetson Orin Nano vs alternatives, ESP32-S3, camera selection (Arducam/ELP/OAK-D/NoIR), LIDAR, GPS, IMU, ultrasonic, PCA9685 | EA-01, EA-02, EA-03 |
| EA-05 | Weight Budget | `05-weight-budget.md` | Mass breakdown by subsystem per phase, centre of gravity, tilt stability, ground pressure | EA-01 to EA-04 |
| EA-06 | Cost Breakdown | `06-cost-breakdown.md` | Detailed BOM per phase, shopping list, prioritised build order, cost reduction options, grand total $2,032 | EA-01 to EA-05 |
| EA-07 | Open Source Review | `07-open-source-review.md` | JPL OSR, Sawppy, ExoMy comparison; Sawppy hybrid construction selected; design heritage mapping | -- |
| EA-08 | Phase 1 Prototype Spec | `08-phase1-prototype-spec.md` | 0.4 scale dimensions (440x260x80mm), 22 printed parts, 65hr print, assembly sequence, coordinate system | EA-01, EA-07 |
| EA-09 | ESP32-S3 GPIO Pin Map | `09-esp32-gpio-pinmap.md` | All GPIO assignments: motor control, servo, encoder, ADC, I2C, UART, LEDC channel mapping, Phase 1 vs Phase 2 | EA-02, EA-04 |
| EA-10 | Ackermann Steering | `10-ackermann-steering.md` | 3 steering modes, turn radius formula, speed-dependent limits, firmware implementation with C code | EA-01, EA-02 |
| EA-11 | 3D Printing Strategy | `11-3d-printing-strategy.md` | PLA (Phase 1) / ASA+PETG (Phase 2), CTC Bizer constraints, heat-set inserts (600-900N pull-out), print times, UV protection | EA-01, EA-05, EA-08 |
| EA-12 | UART Protocol (Text) | `12-uart-protocol.md` | Phase 1 text NMEA protocol, 115200 baud, 18 message types, XOR checksum, 200ms safety timeout | EA-09 |
| EA-13 | ROS2 Architecture | `13-ros2-architecture.md` | ROS2 Humble, 6 packages, Nav2 config, dual EKF, SLAM, YOLO TensorRT, behaviour trees, resource estimates | EA-04, EA-09, EA-12 |
| EA-14 | Weatherproofing | `14-weatherproofing.md` | 3-zone strategy (A/B/C), IP20->IP44->IP54 progression, cable glands, thermal management, seasonal maintenance | EA-03, EA-04, EA-11 |
| EA-15 | Safety Systems | `15-safety-systems.md` | 4-layer architecture (HW/FW/SW/OPS), E-stop, watchdog, battery protection, speed ramping, stall detection, tilt, geofence, human detection | EA-03, EA-09, EA-13 |
| EA-16 | PWA App Design | `16-pwa-app-design.md` | Catppuccin Mocha theme, D-pad/joystick controls, WebSocket protocol, MJPEG camera, Leaflet map, service worker | EA-12, EA-13 |
| EA-17 | Phase 1 Build Guide | `17-phase1-build-guide.md` | 14-day timeline, 3 ordering batches, 10-step build process, print schedule, assembly sequence, testing procedures | EA-06, EA-08, EA-11 |
| EA-18 | Binary UART Protocol | `18-binary-uart-protocol.md` | Phase 2 COBS+CRC-16 protocol, 460800 baud, packed C structs, integer-only encoding, 14 message types, 500ms timeout | EA-09, EA-12 |
| EA-19 | Phase 1 Wiring Guide | `19-phase1-wiring.md` | Complete wiring reference, power distribution diagram, L298N config, motor/servo/sensor connections, E-stop circuit, test procedures, checklist | EA-03, EA-08, EA-09, EA-15 |
| EA-20 | CAD Preparation Guide | `20-cad-preparation-guide.md` | Parametric dimensions from EA-08, Fusion 360 assembly structure, component reference for CAD modelling | EA-08, EA-11 |
| EA-21 | Test Procedures & Acceptance Criteria | `21-test-procedures.md` | Acceptance criteria for firmware, electronics, integration, and autonomy testing across all phases | EA-08, EA-09, EA-15, EA-17 |
| EA-22 | Phase 1 Requirements Specification | `22-requirements-specification.md` | Formal requirements (FR, PR, DIM, ELEC, LEARN, DFT, MOD) with traceability to tests | EA-08, EA-10, EA-21 |
| EA-23 | Wire Harness Specification | `23-wire-harness.md` | Wire schedule (58 wires), connector schedule, cable routing, colour codes, harness build order | EA-09, EA-19 |
| EA-24 | Robotic Arm Feasibility Study | `24-robotic-arm-study.md` | Phase 2 arm concept (3-DOF), weight/CoG analysis, Phase 1 mount preparation | EA-05, EA-08 |


### 8.1 Document Dependency Graph

```
EA-01 (Suspension)
  |
  +-- EA-02 (Drivetrain) -- depends on wheel/track dims
  |     |
  |     +-- EA-03 (Power) -- depends on motor current
  |     |     |
  |     |     +-- EA-05 (Weight) -- depends on all component selections
  |     |     |     |
  |     |     |     +-- EA-06 (Cost) -- depends on complete BOM
  |     |     |
  |     |     +-- EA-14 (Weatherproofing) -- depends on power, compute, printing
  |     |     +-- EA-19 (Wiring) -- depends on power, GPIO, safety
  |     |
  |     +-- EA-04 (Compute/Sensors) -- depends on motor drivers, power budget
  |     |     |
  |     |     +-- EA-09 (GPIO) -- depends on all connected components
  |     |     |     |
  |     |     |     +-- EA-12 (UART Text) -- depends on GPIO assignments
  |     |     |     +-- EA-18 (UART Binary) -- depends on GPIO, text protocol
  |     |     |     +-- EA-15 (Safety) -- depends on GPIO, power, compute
  |     |     |
  |     |     +-- EA-13 (ROS2) -- depends on compute, sensors, UART
  |     |
  |     +-- EA-10 (Steering) -- depends on geometry, servos
  |
  +-- EA-07 (Open Source) -- independent survey
  +-- EA-08 (Phase 1 Spec) -- depends on geometry, open source review
  +-- EA-11 (3D Printing) -- depends on geometry, weight, Phase 1 spec
  +-- EA-16 (PWA) -- depends on UART, ROS2
  +-- EA-17 (Build Guide) -- depends on cost, Phase 1 spec, printing
```

### 8.2 Quick Reference: Which EA to Consult

| Question | Consult |
|----------|---------|
| What size are the wheels/arms? | EA-01 |
| Which motor/driver should I use? | EA-02 |
| How long will the battery last? | EA-03 |
| What camera/sensor should I buy? | EA-04 |
| How heavy is the rover? | EA-05 |
| How much does everything cost? | EA-06 |
| What open-source designs exist? | EA-07 |
| What are the Phase 1 dimensions? | EA-08 |
| Which GPIO does X connect to? | EA-09 |
| How does steering geometry work? | EA-10 |
| How do I print the parts? | EA-11 |
| What is the Phase 1 UART format? | EA-12 |
| How is ROS2 structured? | EA-13 |
| How do I waterproof it? | EA-14 |
| What safety systems are needed? | EA-15 |
| How does the phone app work? | EA-16 |
| What is the Phase 1 build order? | EA-17 |
| What is the Phase 2 UART format? | EA-18 |
| How do I wire Phase 1? | EA-19 |

---

## 9. Glossary

| Term | Definition |
|------|-----------|
| **Ackermann steering** | Geometry where inner wheels turn more than outer, so all wheels trace concentric arcs without tyre scrub |
| **ASA** | Acrylonitrile Styrene Acrylate -- UV-resistant 3D printing filament for outdoor structural parts |
| **BMS** | Battery Management System -- monitors cell voltages, prevents over-charge/discharge |
| **COBS** | Consistent Overhead Byte Stuffing -- framing method that eliminates 0x00 from payload, using 0x00 as delimiter |
| **Crab walk** | Steering mode where all 4 wheels point the same direction, causing lateral movement |
| **CRC-16/CCITT** | 16-bit cyclic redundancy check polynomial (0x1021) for error detection in binary UART |
| **Cytron MDD10A** | Dual 10A motor driver with independent channels and simple PWM+DIR control |
| **Differential bar** | Mechanical linkage connecting left and right rocker arms through the body for equal-opposite tilt |
| **Dual EKF** | Two Extended Kalman Filters: local (high rate, no GPS) and global (lower rate, with GPS) for sensor fusion |
| **E-stop** | Emergency stop -- immediately halts all motor activity |
| **FQBN** | Fully Qualified Board Name -- Arduino CLI identifier for target hardware |
| **Heat-set insert** | Brass threaded insert pressed into 3D-printed plastic with a soldering iron, providing reusable M3 threads |
| **IP rating** | Ingress Protection rating (e.g. IP54 = dust-protected + splash-proof) |
| **L298N** | Dual H-bridge motor driver, 2 channels, up to 2A per channel with onboard 5V regulator |
| **LEDC** | LED Control peripheral on ESP32, used for PWM generation (motors and servos) |
| **MPPT** | Maximum Power Point Tracking -- solar charge controller algorithm for optimal energy harvest |
| **Nav2** | ROS2 navigation framework providing path planning, obstacle avoidance, and waypoint following |
| **NMEA** | National Marine Electronics Association -- text protocol format used for Phase 1 UART |
| **OAK-D Lite** | Luxonis stereo depth camera with onboard AI accelerator (Myriad X) |
| **OTA** | Over-The-Air firmware update |
| **PCA9685** | 16-channel 12-bit PWM driver, controlled via I2C, used for servo control in Phase 2 |
| **PCNT** | Pulse Counter -- ESP32-S3 hardware peripheral for counting encoder pulses without CPU load |
| **PETG** | Polyethylene Terephthalate Glycol -- 3D printing filament with good strength and layer adhesion |
| **Point turn** | Steering mode where front and rear wheels steer opposite directions, rotating in place (zero radius) |
| **PWA** | Progressive Web App -- installable web application with offline support |
| **RegulatedPurePursuit** | Nav2 controller that follows a path with speed regulation for curves and obstacles |
| **Rocker-bogie** | Passive linkage suspension allowing 6-wheel ground contact over uneven terrain |
| **ROS2** | Robot Operating System 2 -- middleware framework for robotics |
| **Sawppy** | Open-source Mars rover replica using aluminium extrusion + 3D-printed connectors |
| **slam_toolbox** | ROS2 package for Simultaneous Localisation and Mapping using LIDAR |
| **SmacPlannerHybrid** | Nav2 path planner using state-lattice search with Dubin/Reeds-Shepp car-like motion |
| **TensorRT** | NVIDIA inference engine that optimises neural networks for GPU deployment |
| **UBEC** | Universal Battery Eliminator Circuit -- voltage regulator for servo power |
| **URDF** | Unified Robot Description Format -- XML description of robot geometry for ROS2 |
| **V-slot** | Aluminium extrusion profile with V-shaped grooves for linear motion or structural framing |
| **YOLO** | You Only Look Once -- real-time object detection neural network |

---

## 10. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-15 | Initial release compiling EA-01 through EA-19 |
| 1.1 | 2026-03-15 | Added EA-20 (CAD Preparation) and EA-21 (Test Procedures) to Document Index |

---

*Document EA-00 v1.0 -- 2026-03-15*
*This is a reference document. For full details on any topic, consult the source EA listed in the Document Index (Section 8).*
