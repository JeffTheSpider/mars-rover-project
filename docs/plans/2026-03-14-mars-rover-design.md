# Mars Rover Garden Robot — Complete Design Document

**Project**: Charlie's Mars Rover
**Date**: 2026-03-14 (updated 2026-03-15)
**Version**: 1.3
**Status**: Design Phase — Engineering Analysis Complete, Phase 1 Firmware Started
**Engineering References**: EA-01 through EA-18 in `docs/engineering/`
**Research References**: `docs/references/` (3D printing materials, ROS2 architecture)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Chassis & Suspension](#3-chassis--suspension)
4. [Power System](#4-power-system)
5. [Compute & Networking](#5-compute--networking)
6. [Vision & Sensors](#6-vision--sensors)
7. [Robotic Arms & Mast](#7-robotic-arms--mast)
8. [Software Architecture](#8-software-architecture)
9. [Accessories](#9-accessories)
10. [Bill of Materials](#10-bill-of-materials)
11. [Build Phases](#11-build-phases)
12. [Risk Register](#12-risk-register)

---

## 1. Project Overview

### Purpose
A Mars rover-inspired outdoor robot that serves as a functional vehicle, AI-powered exploration platform, utility robot, learning project, and coffee table when parked.

### Key Parameters

| Parameter | Value |
|-----------|-------|
| Size (LxWxH driving) | 1100mm x 650mm x 1050mm |
| Size (coffee table) | 1100mm x 650mm x 450mm |
| Weight (Phase 2, 3D printed) | ~16.7 kg (EA-05) |
| Weight (Phase 3, metal) | ~20.8 kg (EA-05) |
| Budget | $2,031.75 total (EA-06) |
| Top speed target | 5 km/h (132.8 wheel RPM) (EA-02) |
| Runtime (driving, all systems) | ~4.0 hours (EA-03) |
| Runtime (driving, no fridge) | ~6.4 hours (EA-03) |
| Runtime (stationary) | ~12+ hours (EA-03) |
| Typical power draw | 97.5W (5.17A at battery) (EA-03) |
| Terrain | All surfaces — grass, gravel, slopes, pavement |
| Max slope | 30° (33.5 kg·cm torque/wheel worst case) (EA-02) |
| Control modes | Manual, autonomous, hybrid |
| Compute | Jetson Orin Nano Super ($249) + ESP32-S3 (EA-04) |
| CAD | Fusion 360 |
| 3D Printer | Ender 3 (220x220x250mm) |

### Build Phases

| Phase | Scale | Material | Goal |
|-------|-------|----------|------|
| 1 | 0.4x (~45x28cm) | PLA/PETG | Test rocker-bogie, basic driving |
| 2 | 1.0x (110x65cm) | PLA/PETG + aluminium extrusion | Full electronics, all features |
| 3 | 1.0x (110x65cm) | Aluminium/steel machined + 3D printed housings | Production quality, weatherproof |

---

## 2. System Architecture

### Subsystems (8 total)

| # | Subsystem | Description |
|---|-----------|-------------|
| 1 | Chassis & Suspension | Rocker-bogie linkage, body frame, coffee table conversion |
| 2 | Drivetrain | 6× Chihai 37mm 80RPM DC gearmotors + 4× MG996R steering servos (EA-02) |
| 3 | Power | 2× 6S 10Ah LiPo (444Wh), 100W solar, BMS, buck converters (EA-03) |
| 4 | Compute & Networking | Jetson Orin Nano Super (67 TOPS) + ESP32-S3 + PCA9685 PWM driver (EA-04) |
| 5 | Vision & Sensors | 4× Arducam 120° + ELP 10× zoom + OAK-D Lite + Pi NoIR + RPLidar A1 (EA-04) |
| 6 | Robotic Arms & Mast | Folding camera mast, articulated arms with grippers |
| 7 | Software | ROS2, AI vision, navigation, phone PWA, firmware |
| 8 | Accessories | Mini fridge, phone charging, LEDs, weather station, speaker, display |

### Dual-Controller Architecture

```
[Jetson Orin Nano Super]              [ESP32-S3]
  - AI vision (67 TOPS)               - Motor PWM control (6×)
  - Path planning (Nav2)              - Sensor polling (6× ultrasonic)
  - Camera streams (7×)               - Wheel encoder reading (6×)
  - GPS navigation                     - Battery monitoring (ADC)
  - Phone app server                   - IMU polling (BNO055, I2C)
  - ROS2 Isaac nodes                  - Watchdog / safety
  - Voice commands                     - LED control (WS2812B)
  - LIDAR SLAM                        - Weather station sensors
        |                                    |
        +------------- UART 115200 ---------+
                                             |
                                      [PCA9685 I2C]
                                        - 14× servo PWM
                                        (4 steering + 8 arm + 2 mast)
```

The Jetson handles all "smart" processing. The ESP32-S3 handles real-time motor/sensor control via PCA9685 I2C PWM driver (solves GPIO pin shortage — 50 pins needed, 36 available, EA-04). If the Jetson crashes, the ESP32 safely stops all motors (watchdog pattern, proven on Clock/Lamp projects).

---

## 3. Chassis & Suspension

### Rocker-Bogie Geometry

NASA's rocker-bogie suspension uses no springs and no axles — pure geometry keeps all 6 wheels on the ground over uneven terrain.

```
Side View:
                    [Differential Bar]
                         /    \
                        /      \
            [Rocker L]            [Rocker R]
           /          \          /          \
         W1    [Bogie L]      [Bogie R]    W6
              /       \      /       \
            W2        W3   W4        W5

Top View (1100mm x 650mm):
    +-------------------------------------+
    |  W1(s)                      W6(s)   |   s = steered
    |    |                          |     |
    |    +--[Rocker]--+  +--[Rocker]--+   |
    |    |            |  |            |   |
    |  W2             +--+           W5   |
    |    |            |  |            |   |
    |    +--[Bogie]---+  +--[Bogie]---+   |
    |    |                          |     |
    |  W3(s)                      W4(s)   |   s = steered
    +-------------------------------------+
```

### Dimensions

| Parameter | Value | Reasoning / Source |
|-----------|-------|-----------|
| Overall length | 1100mm | Coffee table proportions |
| Overall width | 650mm | Fits through standard doorways |
| Track width (wheel-to-wheel) | 700mm | NASA ratio 0.82× wheelbase, adjusted for body (EA-01) |
| Wheelbase (W1-W3) | 900mm | Front to rear wheel per side (EA-01) |
| Rocker arm length | 450mm | NASA ratio 0.50× wheelbase (EA-01) |
| Bogie arm length | 300mm (150+150) | NASA ratio 0.32× wheelbase, 1.50:1 rocker:bogie (EA-01) |
| Ground clearance | 150mm | Adequate for park terrain, kerbs |
| Wheel diameter | 200mm | Max obstacle climb ~150mm practical (EA-01) |
| Wheel width | 80mm | Good traction, not too heavy |
| Body height (wheels to deck) | 300mm | Room for electronics bay |
| Mast height (extended) | 600mm above deck | Good camera vantage |
| Total height (mast up) | ~1050mm | Practical standing height |
| Total height (mast down) | ~450mm | Standard coffee table height |
| Weight (Phase 2) | 16.7 kg | Component-by-component estimate (EA-05) |
| Weight (Phase 3) | 20.8 kg | +4.1 kg for metal panels/hubs (EA-05) |
| Centre of gravity | 232mm above ground | Calculated from component positions (EA-05) |
| Max tilt angle (before tip) | 49° (conservative) | With elevated CoG estimate (EA-01) |
| Bearings | 19× 608ZZ (8mm bore) | All pivot points + wheel axles (EA-01) |

### Wheel Design

Each wheel features:
- Cleats/grousers on the tread (Mars rover aesthetic)
- Flexible spoke design (not solid disc) for compliance over bumps
- Hub motor mount — each wheel has its own DC gearmotor
- Corner steering — W1, W3, W4, W6 have servo-driven steering; W2, W5 are fixed

### Steering Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Normal (Ackermann) | 4 corner wheels turn proportionally | Regular driving |
| Point turn | All 4 steered wheels turn opposite | Spin on the spot, tight spaces |
| Crab walk | All 4 steered wheels turn same direction | Lateral/sideways movement |

### Coffee Table Conversion

- Mast folds flat with a locking hinge
- Solar panels fold in and lay flat
- Optional clear acrylic/glass top panel clicks on for smooth surface
- Wheels lock straight, parking brake engages (motor brake)
- LEDs switch to ambient warm glow underglow
- Wheels remain at sides in normal position (no retraction needed)

### Body Frame Structure

Modular tray system designed for Ender 3 (220x220mm bed):

```
Top deck:  [Panel A1][Panel A2][Panel A3][Panel A4][Panel A5]
           Each ~220x130mm, bolted with alignment pins + M4 bolts

Frame:     2020 aluminium extrusion rails as skeleton
           Gives rigidity that 3D printed panels alone can't provide

Bottom:    Sealed electronics bay with cable pass-throughs
           IP54 rated gaskets for weather resistance (Phase 3)
```

Phase 2 uses aluminium extrusion skeleton + printed panels bolted on.
Phase 3 replaces printed panels with sheet aluminium/steel.

---

## 4. Power System

### Power Budget (EA-03)

| Consumer | Voltage | Peak (A) | Typical (A) | Typical (W) |
|----------|---------|----------|-------------|-------------|
| 6× Drive motors (Chihai 37mm) | 12V | 24.0 | 1.2 | 14.4 |
| 4× Steering servos (MG996R) | 6V | 8.0 | 0.2 | 1.2 |
| Jetson Orin Nano Super | 5V | 3.0 | 2.0 | 10.0 |
| ESP32-S3 | 3.3V | 0.5 | 0.15 | 0.5 |
| 6× Cameras | 5V | 3.0 | 1.5 | 7.5 |
| RPLidar A1 | 5V | 1.0 | 0.7 | 3.5 |
| OAK-D Lite depth | 5V | 1.0 | 0.8 | 4.0 |
| Mini fridge (Peltier) | 12V | 5.0 | 3.0 | 36.0 |
| LED underglow + lights | 5V | 3.0 | 1.0 | 5.0 |
| Speaker/amp | 12V | 2.0 | 0.3 | 3.6 |
| Qi charger | 5V | 2.0 | 1.0 | 5.0 |
| Dashboard display | 5V | 0.3 | 0.2 | 1.0 |
| GPS + IMU + sensors | 3.3V | 0.2 | 0.1 | 0.3 |
| 8× Arm servos + 2× Mast servos | 6V | 20.0 | 1.3 | 7.8 |
| Weather station | 3.3V | 0.1 | 0.05 | 0.2 |
| 4G modem | 5V | 0.5 | 0.3 | 1.5 |
| **Total at battery** | | **~50A peak** | **~13A typical** | **97.5W** |

Battery current (typical): 97.5W / (22.2V × 0.85 efficiency) = **5.17A**

### Battery Design (EA-03)

```
Main Battery Pack: 6S LiPo (22.2V nominal, 25.2V full)
Capacity: 20Ah (444Wh)
Config: 2× Turnigy 6S 10000mAh 12C in parallel (swappable)
Weight: ~1.7 kg total (850g each)
Dimensions: ~185×70×58mm per pack
Peak current: 15.9A (trivial for 12C packs — can deliver 120A each)

[Battery Pack A: 6S 10Ah]  [Battery Pack B: 6S 10Ah]
         |                           |
     [BMS A: 6S 30A]          [BMS B: 6S 30A]
         |                           |
         +------ Parallel -----------+
                    |
            [E-Stop + Main Relay (30A)]
                    |
            [Power Distribution Board]
                    |
    +---------------+---------------+---------------+
    |               |               |               |
[Buck 22V→12V]  [UBEC 22V→6V]  [Buck 22V→5V]  [LDO 5V→3.3V]
XL4016 10A      Hobbywing 5A    XL4015 8A      AMS1117
90% eff         85% eff         88% eff         66% eff
Motors,         Steering+Arm    Jetson,         Weather
Fridge,         Servos          Cameras,        sensors
Speaker                         LEDs, Qi,
                                Display
```

### Estimated Runtime (EA-03 — calculated with converter efficiencies)

| Mode | Power Draw | Runtime (444Wh) |
|------|-----------|------------------|
| Driving + all systems (incl. fridge) | 97.5W | ~4.0 hours |
| Driving without fridge | 61.5W | ~6.4 hours |
| Stationary (coffee table, fridge on) | ~50W | ~8 hours |
| Idle (sensors + compute only) | ~25W | ~16 hours |

### Solar Panel Array

```
Folded (coffee table):        Deployed:
  +----------+               /Panel 1\
  | Panels   |              /---------\
  | stacked  |    -->      |  Top Deck  |
  | on deck  |              \---------/
  +----------+               \Panel 2/
```

- 4× 25W monocrystalline panels = 100W total
- Wired 2S2P (~36V open circuit) — higher than battery voltage for buck MPPT (EA-03)
- CN3722 solar MPPT charge controller (~$15) (EA-06)
- Spring-loaded stainless hinges with locking detents
- Full charge from solar: ~10hrs (summer UK) to ~26hrs (winter UK) (EA-03)
- Realistic solar contribution: extends runtime by 1-3 hours depending on season

### Charging Methods

| Method | Details |
|--------|---------|
| Solar | 100W panels (2S2P), CN3722 MPPT, ~10-26hr full charge (UK) (EA-03) |
| Mains | Barrel jack, 24V 5A charger, ~4hr full charge |
| Docking station | Spring-loaded copper contacts, autonomous dock |

### Safety Features

- BMS per pack: over-charge, over-discharge, over-current, temperature protection
- E-stop: physical red button on body AND software kill from phone
- Low battery auto-return: alert at 20%, autonomous return-to-home at 10%
- Fuse per rail: individual fuses on 12V, 6V, 5V rails
- Battery temperature monitoring: shutdown if packs exceed 60C

---

## 5. Compute & Vision & Sensors (EA-04)

### Camera Array

| Camera | Type | Location | Purpose | Ref |
|--------|------|----------|---------|-----|
| Front main | Arducam B0205 120° USB ($15) | Front body, below deck | Primary driving view, AI object detection | EA-04 |
| Rear | Arducam B0205 120° USB ($15) | Rear body | Reversing camera, rear obstacle detection | EA-04 |
| Left | Arducam B0205 120° USB ($15) | Left body panel | 360 coverage | EA-04 |
| Right | Arducam B0205 120° USB ($15) | Right body panel | 360 coverage | EA-04 |
| Mast cam | ELP 10× optical zoom USB ($50) | Top of mast, pan-tilt mount | Long-range observation, zoom | EA-04 |
| Depth camera | OAK-D Lite ($89) | Front body, next to main cam | Stereo depth, on-device AI, 86° FOV | EA-04 |
| Night vision | Pi NoIR Camera v3 CSI ($25) + 4× IR 850nm LEDs ($5) | Mast | Low-light / night operation | EA-04 |

### 360-Degree View System

```
        [Mast Cam - Zoom + Pan/Tilt]
                   |
    [Left]----[Front]----[Right]
                   |
               [Rear]

Software stitches 4 body cams into panoramic view.
Phone app: swipe to rotate through 360 degrees.
Mast cam is independent — zoom/pan controlled separately.
```

### Sensor Suite

| Sensor | Quantity | Location | Purpose |
|--------|----------|----------|---------|
| RPLidar A1 ($73) | 1 | Front body, ~20cm height | 2D/360° SLAM, 12m range, 8000 samples/s (EA-04) |
| BN-220 GPS (u-blox M8) ($12) | 1 | Top deck (clear sky view) | Position tracking, waypoints, geofencing (EA-04) |
| BNO055 IMU ($15) | 1 | Centre of body | 9-DOF orientation, on-chip fusion, tilt detection (EA-04) |
| Ultrasonic (HC-SR04) | 6 | 2 front, 2 side, 2 rear | Close-range obstacle detection (< 4m) |
| Wheel encoders | 6 | Each wheel hub | Odometry, speed measurement |
| Current sensors (INA219) | 4 | Each power rail | Power monitoring, consumption tracking |
| Temperature (DS18B20) | 3 | Battery bay, electronics bay, ambient | Thermal monitoring |
| Voltage divider | 1 | Battery main | Battery voltage monitoring (ESP32 ADC) |

### AI Vision Pipeline (Jetson)

```
Camera Feeds (6x)
      |
[CSI/USB Capture] --> [Pre-process: resize, normalize]
      |
[YOLO v8 / MobileNet] --> Object Detection
      |                     - People
      |                     - Animals
      |                     - Obstacles
      |                     - Vehicles
      |                     - Signs/text
      |
[Depth Fusion] --> Combine RGB detection with depth map
      |
[ROS2 costmap] --> Navigation layer
      |
[Path Planner] --> Avoid obstacles, plan route
```

### LIDAR SLAM (Simultaneous Localization and Mapping)

```
LIDAR Scan (360° @ 8000 samples/sec)
      |
[Hector SLAM / Cartographer] --> 2D occupancy grid map
      |
[Map Server] --> Stores map of environment
      |
[AMCL Localization] --> "Where am I on this map?"
      |
[Navigation Stack] --> Plan path through known map
```

The rover builds a map as it drives. Next time it visits the same location, it knows where it is and can navigate autonomously using the saved map. At Markeaton Park, after one manual drive-through, it could navigate the paths autonomously.

### Sensor Fusion

```
GPS --------+
IMU --------+---> [Extended Kalman Filter] ---> Fused Position/Orientation
Wheel Enc --+           |
LIDAR ------+     [Confidence Score]
                        |
                  High confidence: use for autonomous nav
                  Low confidence: alert user, slow down
```

Multiple sensor inputs are fused using an EKF (Extended Kalman Filter) to produce a single, accurate position estimate. GPS alone is ~3m accuracy; fused with IMU + wheel encoders + LIDAR, this drops to ~10cm.

---

## 6. Robotic Arms & Mast

### Camera Mast

```
Extended:                    Folded (coffee table):
    [Pan-Tilt Head]              _____________
         |                      |  Mast laid  |
    [Extension Tube]            |  flat on    |
    600mm telescoping           |  top deck   |
         |                      |_____________|
    [Hinge Joint]
         |
    [Body Mount]
```

| Parameter | Value |
|-----------|-------|
| Height above deck (extended) | 600mm |
| Rotation range (pan) | 360 degrees continuous |
| Tilt range | -30 to +90 degrees |
| Pan motor | MG996R servo or NEMA 17 stepper |
| Tilt motor | MG996R servo |
| Fold mechanism | Spring-loaded hinge with solenoid lock |
| Cameras on mast | 30x zoom cam, IR night vision cam |

### Pan-Tilt Head Design

```
Top View:                    Side View:
    +-------+                [Tilt Servo]---[Camera Mount]
    | Zoom  |                     |              |
    | Cam   |                [Pan Servo]    [Zoom Cam]
    +-------+                     |         [IR Cam]
    | IR    |                [Bearing]
    | Cam   |                     |
    +-------+                [Mast Tube]

Pan: slip ring for continuous 360 rotation (no cable wrap)
Tilt: standard servo arm, -30 to +90 degrees
```

### Robotic Arms (x2)

Two articulated arms, one on each side of the body:

```
Arm Layout (each arm):

[Shoulder Joint]---[Upper Arm]---[Elbow Joint]---[Forearm]---[Wrist]---[Gripper]
     |                180mm           |             150mm       |         |
  [Servo 1]                      [Servo 2]                 [Servo 3] [Servo 4]
  Rotation                       Bend                      Rotation  Open/Close

Degrees of Freedom: 4 per arm (shoulder rotate, elbow bend, wrist rotate, gripper)
```

| Parameter | Value |
|-----------|-------|
| Reach per arm | ~350mm from shoulder |
| Payload per arm | ~500g (Phase 2 3D print), ~2kg (Phase 3 metal) |
| Servos per arm | 4x MG996R (or DS3218 for metal version) |
| Gripper opening | 0-80mm |
| Stow position | Folded along body sides |
| Control | Manual from phone app + pre-programmed gestures |

### Arm Use Cases

| Use Case | Description |
|----------|-------------|
| Picking up objects | Grab a drink from the fridge, pass items |
| Camera positioning | Mount a GoPro/phone on gripper for unique angles |
| Waving/gestures | Social interaction, wave hello |
| Tool holding | Hold a torch, phone, or sensor for inspection |
| Self-maintenance | Potentially press own buttons, open panels |
| Park interaction | Pick up litter, interact with environment |

### Arm Stowage

```
Driving Mode:                     Deployed:
+--[Arm folded]---------+        +----[Arm extended]-->
|                       |        |
|     Body              |        |     Body
|                       |        |
+--[Arm folded]---------+        +----[Arm extended]-->
```

Arms fold flush against the body sides when not in use. Magnets or spring clips hold them in place during driving. When the rover is in coffee table mode, arms can be fully stowed underneath the deck.

---

## 7. Software Architecture

### Overview

```
+---------------------------------------------------------------+
|                        PHONE APP (PWA)                         |
|  Joystick | Camera | Map | Arms | Settings | Dashboard        |
+------------------------------+--------------------------------+
                               |
                          WebSocket / WebRTC
                               |
+------------------------------+--------------------------------+
|                  JETSON ORIN NANO SUPER (67 TOPS)              |
|  +------------------+  +------------------+  +--------------+ |
|  | ROS2 Core        |  | Web Server       |  | AI Pipeline  | |
|  | - Nav2 stack     |  | - Express/Flask  |  | - YOLO v8    | |
|  | - SLAM           |  | - WebSocket      |  | - Depth      | |
|  | - Sensor fusion  |  | - WebRTC streams |  | - Tracking   | |
|  | - Path planning  |  | - REST API       |  | - OCR/text   | |
|  +------------------+  +------------------+  +--------------+ |
|  +------------------+  +------------------+  +--------------+ |
|  | Camera Manager   |  | Arm Controller   |  | Telemetry    | |
|  | - 7 camera feeds |  | - IK solver      |  | - GPS log    | |
|  | - 360 stitch     |  | - Gesture lib    |  | - Battery    | |
|  | - Recording      |  | - Safety limits  |  | - Speed      | |
|  +------------------+  +------------------+  +--------------+ |
|                               |                                |
|                          UART / I2C                            |
|                               |                                |
+------------------------------+--------------------------------+
|                        ESP32-S3                                |
|  +------------------+  +------------------+  +--------------+ |
|  | Motor Controller |  | Sensor Hub       |  | Safety       | |
|  | - 6x PWM drive   |  | - 6x ultrasonic  |  | - Watchdog   | |
|  | - PCA9685 servos |  | - 6x wheel enc   |  | - E-stop     | |
|  | - PID speed ctrl |  | - BNO055 IMU     |  | - Tilt limit | |
|  | - Cytron MDD10A  |  | - Temp sensors   |  | - Overcurr   | |
|  +------------------+  +------------------+  +--------------+ |
|  +------------------+  +------------------+                    |
|  | LED Controller   |  | Power Monitor    |                    |
|  | - Underglow      |  | - Voltage ADC    |                    |
|  | - Headlights     |  | - Current sense  |                    |
|  | - Status LEDs    |  | - Solar MPPT     |                    |
|  +------------------+  +------------------+                    |
+---------------------------------------------------------------+
```

### ROS2 Node Graph

```
/camera_front ----+
/camera_rear -----+
/camera_left -----+--> /image_stitcher --> /panoramic_view --> /web_server
/camera_right ----+
/camera_mast ---------> /zoom_controller --> /web_server
/camera_depth --------> /depth_processor --> /costmap

/lidar_scan ----------> /slam_node --> /map_server
                             |
                        /amcl_node --> /robot_pose

/gps_node ------+
/imu_node ------+--> /ekf_local  --> /odom (smooth, no GPS jumps)
/wheel_odom ----+        |
                    /ekf_global --> /odom/global (with GPS)
                    /navsat_transform (GPS NavSatFix → odom)

/nav2_controller (RegulatedPurePursuit, DUBIN planner) --> /cmd_vel
  --> /ackermann_controller --> /motor_bridge --> [ESP32 UART]

/ai_detector ------> /object_tracker --> /obstacle_layer --> /costmap

/joystick_input ---> /teleop_node --> /cmd_vel (overrides nav2 in manual mode)

/battery_monitor --> /power_manager --> /auto_return (at 10%)

/weather_station --> /telemetry_publisher --> /web_server

/arm_left_controller --> /arm_ik_solver --> [ESP32 servo commands]
/arm_right_controller -> /arm_ik_solver --> [ESP32 servo commands]

/anti_theft -------> /geofence_monitor --> /alarm_trigger
                                      --> /notification_sender
```

### ESP32-S3 Firmware Architecture

```
main.cpp
  |
  +-- config.h              // Pin definitions, constants
  +-- motor_controller.h    // PID speed control, 6 motors
  +-- steering_controller.h // Servo angles, Ackermann calc
  +-- sensor_hub.h          // Ultrasonic, encoders, IMU
  +-- power_monitor.h       // Battery ADC, current sensing
  +-- led_controller.h      // NeoPixel underglow, headlights
  +-- safety.h              // Watchdog, e-stop, tilt limits
  +-- comms.h               // UART protocol to Jetson
  +-- wifi_fallback.h       // Backup WiFi AP if Jetson down
```

Single translation unit architecture (like Clock/Lamp) — .h files included from main .cpp. Non-blocking state machine ticks throughout (proven pattern from existing projects).

### Communication Protocol (Jetson <-> ESP32)

**Phase 1 (debug/development)**: NMEA-style text protocol at 115200 baud (EA-12)
- Human-readable sentences: `$CMTR,150,-150,200,-200,100,-100*4A`
- 18 message types, ASCII checksum, 50Hz command rate
- Easy to debug via serial monitor or telnet

**Phase 2 (production)**: Binary COBS + CRC-16 at 460800 baud (EA-18)
- Consistent Overhead Byte Stuffing framing (zero-delimiter)
- CRC-16/CCITT error detection, 12% bandwidth utilisation
- Packed C structs with scaled integers (no float)
- Compile-time switch: `#define PHASE2_BINARY_PROTOCOL`

```
Phase 2 message IDs:
Commands (Jetson -> ESP32):
  0x01: Motor speeds (6x int16, ±1000 = ±100%)
  0x02: Steering angles (4x uint16, 0-1800 = 0.0-180.0°)
  0x03: LED control (pattern + RGB)
  0x04: Arm servos (8x uint16)
  0x05: Config set (key-value)
  0x0E: Ping
  0x0F: E-stop (triple-sent for reliability)

Telemetry (ESP32 -> Jetson):
  0x81: Encoder data (6x tick count + dt)
  0x82: IMU data (quaternion + gyro + accel, scaled int16)
  0x83: Ultrasonic distances (6x uint16 mm)
  0x84: Battery status (voltage, current, SoC, temp)
  0x85: System status (mode, errors, uptime)
  0x8E: Pong (response to ping)
  0x8F: E-stop acknowledgement
```

### Phone App (PWA)

Browser-based progressive web app, similar architecture to the existing Hub PWA:

```
Pages/Views:
  /drive          - Live camera + joystick controls
  /cameras        - All camera feeds, 360 view, zoom control
  /map            - GPS map, waypoints, route planning, geofence
  /arms           - Arm control (manual + gestures)
  /dashboard      - Battery, speed, temp, system health
  /settings       - WiFi, control sensitivity, camera quality
  /recordings     - Saved photos/videos
  /autonomy       - Set destinations, patrol routes
  /security       - Anti-theft settings, geofence, alarm

Tech Stack:
  - HTML/CSS/JS (vanilla or lightweight framework)
  - WebSocket for real-time control (<50ms latency)
  - WebRTC for camera streams
  - Gamepad API for physical controller support
  - Service Worker for offline capability
  - Catppuccin Mocha theme (consistent with Hub)
```

### Control Mode State Machine

```
                    +------------+
                    |    BOOT    |
                    +-----+------+
                          |
                    +-----v------+
                    |   IDLE     | <--- Coffee table mode
                    +-----+------+
                          |
              +-----------+-----------+
              |           |           |
        +-----v----+ +---v------+ +--v--------+
        |  MANUAL  | | AUTONOMOUS| |  HYBRID   |
        | Phone    | | GPS/SLAM  | | Auto+     |
        | joystick | | waypoints | | override  |
        +-----+----+ +---+------+ +--+--------+
              |           |           |
              +-----------+-----------+
                          |
                    +-----v------+
                    | RETURNING  |  <--- Auto return-to-home
                    +-----+------+
                          |
                    +-----v------+
                    |  DOCKING   |  <--- Autonomous dock
                    +-----+------+
                          |
                    +-----v------+
                    | CHARGING   |
                    +------------+

Emergency transitions (from any state):
  Any --> E_STOP (physical button or phone kill)
  Any --> TILT_SAFE (IMU detects >45 degree tilt)
  Any --> LOW_BATTERY (10% SOC)
```

### Data Logging & Storage

| Data | Storage | Retention |
|------|---------|-----------|
| GPS tracks | SQLite on Jetson | Permanent, exportable as GPX |
| Camera snapshots | microSD card | Until card full (FIFO) |
| Video recordings | microSD card | Manual delete |
| Sensor telemetry | SQLite | 30 days rolling |
| Maps (SLAM) | Files on Jetson | Permanent |
| Error logs | Text files | 7 days rolling |
| Battery cycles | SQLite | Permanent (health tracking) |

### OTA Updates

| Component | Method |
|-----------|--------|
| Jetson software | SSH + git pull, or rsync from PC |
| ESP32 firmware | OTA via WiFi (same pattern as Clock/Lamp) |
| Phone app | Service worker auto-update (like Hub PWA) |

---

## 8. Accessories

### Mini Fridge

| Parameter | Value |
|-----------|-------|
| Type | Peltier thermoelectric cooler (TEC1-12706) |
| Capacity | ~4-6 cans or 2 bottles |
| Cooling | Ambient -15C to -20C (so ~5C on a 20C day) |
| Power | 12V, 3-5A (36-60W) |
| Location | Centre of body, accessible from top deck |
| Insulation | Foam lined compartment, hinged lid |
| Control | On/off from phone app, temperature display on dashboard |

```
Top deck cutout:
+---------------------------+
|     [Solar]  [Mast]       |
|  +--------+              |
|  | Fridge  | <-- hinged   |
|  | Lid     |    lid       |
|  +--------+              |
|     [Qi Pad]  [Display]   |
+---------------------------+
```

### Phone Charging

| Method | Details |
|--------|---------|
| Qi wireless pad | Embedded in top deck surface, 15W fast charge |
| USB-C port | Side of body, PD capable, 20W |
| USB-A port | Side of body, 5V 2.4A, for accessories |

### LED System

| Zone | LEDs | Purpose |
|------|------|---------|
| Underglow | WS2812B strip (60+ LEDs around body perimeter) | Ambient lighting, status indication |
| Headlights | 2x high-power white LED (3W each) | Front illumination for cameras |
| Tail lights | 2x red LED | Rear visibility |
| Indicators | 4x amber LED (corners) | Turn signals when steering |
| Mast light | 1x RGB LED | Status beacon, visible from distance |
| IR array | 4x IR LED (850nm) | Night vision illumination |

LED Colour Modes:

| Mode | Colour | Pattern |
|------|--------|---------|
| Manual control | Blue | Steady glow |
| Autonomous | Green | Gentle pulse |
| Hybrid | Cyan | Steady |
| Low battery | Red | Slow flash |
| Charging | Amber | Breathing |
| Docking | White | Fast pulse |
| Coffee table | Warm white (2700K) | Ambient glow |
| Anti-theft alarm | Red | Rapid strobe |
| Party mode | Rainbow | Cycling animation |

### Weather Station

| Sensor | Model | Measurement |
|--------|-------|-------------|
| Temperature + humidity | BME280 | -40 to +85C, 0-100% RH |
| Barometric pressure | BME280 (built-in) | 300-1100 hPa |
| Wind speed | Anemometer (cup type) | 0-30 m/s |
| Wind direction | Vane (optional) | 0-360 degrees |
| Rain detector | YL-83 | Rain yes/no + intensity |
| UV index | VEML6075 | UV-A and UV-B |
| Light level | BH1750 | 0-65535 lux |

Location: Weather sensors mounted on mast (wind/rain) and body (temp/pressure/UV/light). Data displayed on dashboard screen and phone app.

### Speaker & Microphone System

| Component | Details |
|-----------|---------|
| Speaker | 2x 3W full-range drivers, sealed enclosure in body |
| Amplifier | MAX98357A I2S amp (Jetson native) |
| Microphone | 2x MEMS mic (SPH0645) for stereo pickup |
| Functions | Two-way audio, voice commands, music playback, alarm siren |

Audio Features:
- Talk through rover from phone (intercom mode)
- Voice command processing (on Jetson or cloud)
- Play music when in coffee table mode (Bluetooth speaker mode)
- Alarm siren for anti-theft (120dB capable with larger driver)
- Startup/shutdown sounds
- Obstacle warning beeps

### Dashboard Display

| Parameter | Value |
|-----------|-------|
| Display | 3.5" or 5" IPS LCD (SPI or HDMI) |
| Location | Rear or side of body, visible when approaching |
| Content | Battery %, speed, GPS coords, temp, mode, IP address |
| Backlight | Auto-dim with light sensor |

```
+---------------------------+
|  ROVER STATUS      12:34  |
|  Battery: 78% ████████░░  |
|  Speed: 2.3 km/h          |
|  GPS: 52.9378, -1.4947    |
|  Temp: 18C  Mode: AUTO    |
|  WiFi: Connected (4G)     |
|  Solar: 45W generating    |
+---------------------------+
```

### Return-to-Home System

```
Trigger: Manual button press OR 10% battery auto-trigger

1. Save current GPS position as "resume point"
2. Load "home" GPS coordinates from saved config
3. Plan route using known map (if available) or GPS waypoints
4. Switch to autonomous navigation
5. Drive to home location using SLAM + GPS fusion
6. Align with docking station using IR beacons or vision
7. Dock and begin charging
8. Send phone notification: "Rover docked and charging"
```

### Docking Station

```
Docking Station (home base):
+---------------------------+
|  [Guide Rails / Ramp]     |
|                           |
|  [Charging Contacts]      |  <-- spring-loaded copper pads
|  [+ positive] [- negative]|     mate with rover underside
|                           |
|  [IR Beacon / ArUco tag]  |  <-- rover aligns visually
|                           |
|  [24V Power Supply]       |
+---------------------------+

Rover underside:
  [Copper contact pads]  <-- recessed, spring-loaded
  Position: centre of belly, aligned with docking station
```

### Anti-Theft System

| Layer | Mechanism | Details |
|-------|-----------|---------|
| Geofence | Virtual boundary on map | Configurable polygon, alert if crossed |
| Motion detect | IMU detects movement when parked | Sensitivity adjustable |
| GPS tracking | Position logged every 10s | Viewable on phone map in real-time |
| Alarm | Speaker siren + LED strobe | 120dB capable |
| Phone alert | Push notification | Includes GPS coordinates |
| Motor lock | Software disable + brake | Requires PIN to unlock |
| Kill switch | Remote disable from phone | Rover becomes inert |
| Camera recording | Auto-record all cameras on alarm | Saves to SD card |

---

## 9. Bill of Materials (EA-06 — Research-Backed Costs)

### Phase 1: 0.4 Scale Prototype — $102

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 1 | ESP32-S3 DevKit (N16R8, USB-C) | 1 | $8 | $8 |
| 2 | N20 DC gearmotors (6V, 100RPM, with encoder) | 6 | $3 | $18 |
| 3 | SG90 micro servos (1.8 kg·cm) | 4 | $2 | $8 |
| 4 | L298N motor drivers (dual H-bridge) | 2 | $3 | $6 |
| 5 | 2S LiPo 2200mAh (7.4V, XT30) | 1 | $12 | $12 |
| 6 | LiPo charger (2S balance) | 1 | $8 | $8 |
| 7 | PETG filament (1kg spool) | 1 | $20 | $20 |
| 8 | 608ZZ bearings | 10 | $0.50 | $5 |
| 9 | M3 fastener set + heat-set inserts | 1 set | $9 | $9 |
| 10 | Breadboard + jumper wires + switch | 1 | $8 | $8 |
| | **Phase 1 Total** | | | **$102** |

### Phase 2: Full-Scale 3D Printed — $1,482.50 (+10% contingency = $1,630.75)

| Category | Items | Subtotal |
|----------|-------|----------|
| Compute & Electronics | Jetson Orin Nano Super ($249), ESP32-S3, PCA9685, USB hub, 2× microSD | $292 |
| Cameras & Vision | 4× Arducam 120° ($60), ELP 10× zoom ($50), OAK-D Lite ($89), Pi NoIR ($25), IR LEDs ($5) | $229 |
| Navigation Sensors | RPLidar A1 ($73), BN-220 GPS ($12), BNO055 IMU ($15), 6× HC-SR04 ($9) | $109 |
| Drivetrain | 6× Chihai 37mm 80RPM w/encoder ($72), 3× Cytron MDD10A ($45), 4× MG996R ($24) | $141 |
| Arms & Mast | 8× MG996R arm ($48), 2× MG996R mast ($12), slip ring ($8) | $68 |
| Power System | 2× Turnigy 6S 10Ah 12C ($100), 2× BMS ($16), charger ($20), converters ($17), wiring ($32) | $185 |
| Solar | 4× 25W panels ($80), CN3722 MPPT ($15), hinges ($8) | $103 |
| Accessories | Fridge ($15), Qi charger ($8), USB ports ($6), LEDs ($15), speakers ($10), weather sensors ($20), display ($12), INA219×4 ($8), DS18B20×3 ($4.50) | $96.50 |
| Structure & Hardware | 4× PETG 1kg ($60), 6× 2020 extrusion ($24), brackets ($10), T-nuts ($7.50), bearings ($9.50), fasteners ($20), connectors ($13), cable ties ($5) | $234 |
| Docking Station | Copper contacts ($8), 24V PSU ($12), base plate ($5) | $25 |
| | **Phase 2 Total** | **$1,482.50** |
| | **+ 10% Contingency** | **$1,630.75** |

### Phase 3: Metal Build (Additional) — $260 (+15% contingency = $299)

| Item | Cost |
|------|------|
| Aluminium sheet (1.5mm, 2m²) | $60 |
| Aluminium rectangular tube (rocker/bogie arms) | $25 |
| Steel rod (axles, differential bar) | $15 |
| 4× DS3218 upgraded steering servos | $40 |
| 6001-2RS sealed bearings | $15 |
| Paint / powder coat / anodising | $30 |
| Weatherproof gaskets + cable glands (IP54) | $15 |
| Tempered glass top panel (optional) | $25 |
| Stainless steel fasteners upgrade | $15 |
| Machining consumables (drill bits, taps) | $20 |
| **Phase 3 Additional** | **$260 (+$39 contingency = $299)** |

### Total Project Budget

| Phase | Components | Contingency | Budget Total |
|-------|-----------|-------------|-------------|
| Phase 1 (0.4 prototype) | $102 | included | $102 |
| Phase 2 (full 3D print) | $1,482.50 | $148.25 | $1,630.75 |
| Phase 3 (metal, additional) | $260 | $39 | $299 |
| **Grand Total** | **$1,844.50** | **$187.25** | **$2,031.75** |

**$2,031.75 slightly exceeds the $1,500-2,000 target budget** by ~$32. This is due to revised filament estimates (EA-08, EA-11, EA-17). Consider the cost reduction options in EA-06 or a modest budget adjustment. If budget is tight, core rover (compute + cameras + drivetrain + power + structure) works for **$764** — everything else can be added incrementally.

---

## 10. Build Phases — Detailed

### Phase 1: 0.4 Scale Prototype

**Goal**: Prove rocker-bogie geometry works, basic driving, validate dimensions.

**What gets tested**:
- Rocker-bogie suspension articulation over obstacles
- Motor torque vs weight ratio
- Steering geometry (Ackermann, point turn, crab)
- Basic ESP32 motor control firmware
- 3D print assembly method (bolt-together segments)
- Wheel grip on grass, gravel, slopes

**What does NOT go in Phase 1**:
- No Jetson (ESP32 only)
- No cameras (except optional ESP32-CAM for fun)
- No arms, no mast
- No fridge, no charging, no weather
- No AI, no LIDAR, no GPS
- Simple RC control from phone via WiFi (web server on ESP32)

**Print segments** (220x220mm bed):
- Chassis: ~6-8 segments (body is ~440x260mm at 0.4 scale)
- Rocker arms: 2x (each fits in one print)
- Bogie arms: 2x (each fits in one print)
- Wheels: 6x (each ~80mm diameter, one per print)
- Differential bar: 1x
- Total: ~15-20 prints, estimated 40-60 hours print time

### Phase 2: Full-Scale 3D Printed

**Goal**: Full electronics integration, all features working, software complete.

**Print segments** (220x220mm bed, body is 1100x650mm):
- Top deck: ~25-30 panels (220x130mm each, 2 layers of panels)
- Side panels: ~12 panels
- Electronics bay: ~8 panels
- Rocker arms: 4 segments each (reinforced with aluminium rod)
- Bogie arms: 2 segments each
- Wheels: 6x (printed in halves, bolted together)
- Mast: 3-4 sections (telescoping)
- Arm segments: ~12 pieces (6 per arm)
- Fridge housing: 4 panels
- Camera mounts: 7x custom brackets
- Total: ~80-100 prints, estimated 200-300 hours print time

**Reinforcement strategy**:
- 2020 aluminium extrusion as skeleton (bolted to printed panels)
- Aluminium rods through rocker/bogie arms for strength
- Metal wheel axles with printed hubs
- Steel bolts at all stress points

### Phase 3: Metal Build

**Goal**: Production quality, weatherproof, long-term durability.

**Machining required**:
- Wheel hubs: lathe (aluminium)
- Axles: lathe (steel)
- Rocker/bogie arms: mill or waterjet (aluminium plate)
- Chassis frame: welded aluminium box section or extrusion
- Body panels: sheet aluminium, bent/formed
- Custom brackets: mill

**3D printed parts retained**:
- Camera housings (complex geometry, low stress)
- Fridge insulation housing
- Cable management clips
- Dashboard display bezel
- Gripper fingers
- Decorative elements (cleats, logos)

---

## 11. Risk Register

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| 1 | Rocker-bogie too complex to print | High | Medium | Phase 1 validates at small scale first |
| 2 | Weight exceeds motor torque | High | Medium | Calculate torque requirements, size motors accordingly |
| 3 | Battery life insufficient | Medium | Low | 444Wh is generous; solar extends runtime |
| 4 | 3D printed parts break under load | High | Medium | Aluminium extrusion skeleton, Phase 3 replaces with metal |
| 5 | Jetson overheats outdoors | Medium | Medium | Heatsink + fan, thermal throttling, shade from solar panels |
| 6 | WiFi range insufficient at park | Medium | High | 4G modem as backup, antenna on mast |
| 7 | Rain damages electronics | High | Medium | IP54 sealing in Phase 3, weather awareness in software |
| 8 | Budget overrun | Medium | Medium | Phase 1 is cheap validation; buy Phase 2 incrementally |
| 9 | LIDAR SLAM too complex | Low | Medium | Start with GPS-only nav, add SLAM incrementally |
| 10 | Theft at park | High | Low | GPS tracking, alarm, geofence, motor lock, camera recording |
| 11 | Peltier fridge draws too much power | Low | Low | Software-controlled, only runs when stationary/charging |
| 12 | Print time too long (300hrs) | Low | High | Print in parallel batches, accept timeline |

---

## 12. Next Steps

1. **Install Fusion 360** — download and set up for CAD modelling
2. **Design Phase 1 prototype in CAD** — use dimensions from EA-08, rocker-bogie geometry first
3. **Simulate suspension** — test articulation range in Fusion 360
4. **Print Phase 1 parts** — follow EA-08 §13.3 print order, EA-11 for settings
5. **Order Phase 1 electronics** — ESP32-S3, N20 motors, SG90 servos, L298N drivers ($102, EA-06)
6. ~~**Write ESP32 firmware**~~ — ✅ DONE: `firmware/esp32/` — motor control + WiFi web server + Ackermann steering
7. **Assemble and test** — follow EA-08 §14 assembly sequence, calibrate servos

---

---

## 13. Engineering Analysis Documents

All design decisions in this document are backed by detailed engineering analyses:

| Doc | Title | Key Decisions |
|-----|-------|---------------|
| EA-01 | Suspension Analysis | Rocker-bogie geometry (NASA ratio scaling), 150mm obstacle climb, 49° tilt limit, 19× 608ZZ bearings |
| EA-02 | Drivetrain Analysis | 33.5 kg·cm worst-case torque, Chihai 37mm 80RPM motors, Cytron MDD10A drivers, MG996R servos |
| EA-03 | Power System Analysis | 6S LiPo (444Wh), 97.5W typical draw, 4hr runtime, 2S2P solar config, wire gauge calcs |
| EA-04 | Compute & Sensors | Jetson Orin Nano Super (67 TOPS), PCA9685 servo driver, full camera/sensor suite |
| EA-05 | Weight Budget | 16.7 kg Phase 2, 20.8 kg Phase 3, CoG at 232mm above ground |
| EA-06 | Cost Breakdown | $2,031.75 grand total, prioritised build order, cost reduction options |
| EA-07 | Open Source Review | Sawppy construction + JPL geometry hybrid approach recommended |
| EA-08 | Phase 1 Prototype Spec | All parts dimensioned for CAD, 22 printed parts, 65hr print time, assembly sequence |
| EA-09 | ESP32-S3 GPIO Pin Map | Complete pin assignment for Phase 1 (20 pins) and Phase 2 (28 pins), wiring diagrams |
| EA-10 | Ackermann Steering | Steering angle calculations, min turn radius 993mm, point turn, crab walk, servo mapping |
| EA-11 | 3D Printing Strategy | PETG/ASA material selection, print settings, heat-set inserts, part segmentation, ~317hr Phase 2 |
| EA-12 | UART Protocol | Text-based NMEA-style protocol, 115200 baud, 50Hz control loop, 18 message types |
| EA-13 | ROS2 Architecture | Node graph, Nav2 config, SLAM, EKF fusion, YOLO pipeline, behaviour trees, ~56% CPU / ~50% GPU |
| EA-14 | Weatherproofing | IP44 Phase 2 / IP54 Phase 3, zone-based protection, cable glands, thermal management |
| EA-15 | Safety Systems | 4-layer safety (HW/FW/SW/OPS), fault handling, anti-theft, human detection limits |
| EA-16 | PWA App Design | Catppuccin Mocha phone UI, D-pad + joystick, camera streaming, navigation map |
| EA-17 | Phase 1 Build Guide | Step-by-step from ordering to first drive, ~14 day timeline, troubleshooting |

---

*Document generated 2026-03-14. Updated to v1.2 on 2026-03-15 with EA-01 through EA-17 and Phase 1 firmware.*
*This is a living document — will be updated as the design evolves.*
