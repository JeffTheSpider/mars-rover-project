# Mars Rover Garden Robot — Complete Design Document

**Project**: Charlie's Mars Rover
**Date**: 2026-03-14
**Version**: 1.0
**Status**: Design Phase

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
| Weight target (metal) | 25-35 kg |
| Budget | ~1,500-2,000 |
| Top speed target | 3-5 km/h |
| Runtime (driving) | ~2 hours |
| Runtime (stationary) | ~6 hours |
| Terrain | All surfaces — grass, gravel, slopes, pavement |
| Control modes | Manual, autonomous, hybrid |
| Compute | Jetson Orin Nano + ESP32-S3 |
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
| 2 | Drivetrain | 6 DC motors (drive) + 4 servo motors (steering corners) |
| 3 | Power | LiPo batteries, solar panels, BMS, charging systems |
| 4 | Compute & Networking | Jetson Orin Nano + ESP32-S3, WiFi/4G, phone app |
| 5 | Vision & Sensors | Cameras, LIDAR, depth sensor, GPS, IMU, ultrasonics |
| 6 | Robotic Arms & Mast | Folding camera mast, articulated arms with grippers |
| 7 | Software | ROS2, AI vision, navigation, phone PWA, firmware |
| 8 | Accessories | Mini fridge, phone charging, LEDs, weather station, speaker, display |

### Dual-Controller Architecture

```
[Jetson Orin Nano]                    [ESP32-S3]
  - AI vision                          - Motor PWM control (6x)
  - Path planning                      - Servo steering (4x)
  - Camera streams                     - Battery monitoring (ADC)
  - GPS navigation                     - Sensor polling
  - Phone app server                   - Watchdog / safety
  - ROS2 nodes                        - LED control
  - Voice commands                     - Weather station
  - LIDAR SLAM                        - E-stop monitor
        |                                    |
        +------------- UART/I2C ------------+
```

The Jetson handles all "smart" processing. The ESP32-S3 handles real-time motor/sensor control. If the Jetson crashes, the ESP32 safely stops all motors (watchdog pattern, proven on Clock/Lamp projects).

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

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| Overall length | 1100mm | Coffee table proportions |
| Overall width | 650mm | Fits through standard doorways |
| Ground clearance | 150mm | Clears park terrain, kerbs |
| Wheel diameter | 200mm | Large enough for rough ground |
| Wheel width | 80mm | Good traction, not too heavy |
| Body height (wheels to deck) | 300mm | Room for electronics bay |
| Mast height (extended) | 600mm above deck | Good camera vantage |
| Total height (mast up) | ~1050mm | Practical standing height |
| Total height (mast down) | ~450mm | Standard coffee table height |
| Weight target | 25-35kg (metal version) | Carriable by two people |

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

### Power Budget

| Consumer | Voltage | Peak Draw | Typical Draw |
|----------|---------|-----------|--------------|
| 6x Drive motors | 12V | 30A (stall) | 6A (cruising) |
| 4x Steering servos | 6V | 8A (peak) | 1A (holding) |
| Jetson Orin Nano | 5V | 3A (15W) | 2A (10W) |
| ESP32-S3 + sensors | 5V | 0.5A | 0.3A |
| Cameras (x6) | 5V | 3A total | 2A |
| LIDAR | 5V | 1A | 0.7A |
| Mini fridge (Peltier) | 12V | 5A | 3A |
| LED underglow + lights | 5V | 3A | 1A |
| Speaker/amp | 12V | 2A | 0.5A |
| Qi charger | 5V | 2A | 1A |
| Dashboard display | 5V | 0.5A | 0.3A |
| Weather station | 3.3V | 0.1A | 0.05A |
| **Total** | | **~55A peak** | **~17A typical** |

### Battery Design

```
Main Battery Pack: 6S LiPo (22.2V nominal, 25.2V full)
Capacity: 20Ah (444Wh)
Config: 2x 6S 10Ah packs in parallel (swappable)

[Battery Pack A: 6S 10Ah]  [Battery Pack B: 6S 10Ah]
         |                           |
         +------ Parallel -----------+
                    |
            [BMS: 6S balance + overcurrent + temp]
                    |
            [Power Distribution Board]
                    |
    +---------------+---------------+---------------+
    |               |               |               |
[12V Buck]      [6V BEC]       [5V Buck]       [3.3V LDO]
Motors,         Steering        Jetson,         Weather
Fridge,         Servos          Cameras,        sensors
Speaker                         LEDs, Qi,
                                Display
```

### Estimated Runtime

| Mode | Draw | Runtime (444Wh) |
|------|------|------------------|
| Driving + all systems | ~204W (17A x 12V) | ~2 hours |
| Stationary (coffee table, fridge on) | ~72W (6A x 12V) | ~6 hours |
| Idle (sensors only) | ~12W (1A x 12V) | ~37 hours |

### Solar Panel Array

```
Folded (coffee table):        Deployed:
  +----------+               /Panel 1\
  | Panels   |              /---------\
  | stacked  |    -->      |  Top Deck  |
  | on deck  |              \---------/
  +----------+               \Panel 2/
```

- 4x folding panels, ~25W each = 100W total
- MPPT charge controller (Victron SmartSolar or similar)
- Hinged arms with locking detents
- Full charge from solar: ~4-5 hours in good sun
- Extends driving runtime significantly when panels deployed while driving

### Charging Methods

| Method | Details |
|--------|---------|
| Solar | 100W panels, MPPT controller, ~4-5hr full charge |
| Mains | Barrel jack, 24V charger, ~2hr full charge |
| Docking station | Spring-loaded copper contacts, autonomous dock |

### Safety Features

- BMS per pack: over-charge, over-discharge, over-current, temperature protection
- E-stop: physical red button on body AND software kill from phone
- Low battery auto-return: alert at 20%, autonomous return-to-home at 10%
- Fuse per rail: individual fuses on 12V, 6V, 5V rails
- Battery temperature monitoring: shutdown if packs exceed 60C

---

## 5. Vision & Sensors

### Camera Array

| Camera | Type | Location | Purpose |
|--------|------|----------|---------|
| Front main | Wide-angle RGB (IMX477 or similar) | Front body, below deck | Primary driving view, AI object detection |
| Rear | Wide-angle RGB | Rear body | Reversing camera, rear obstacle detection |
| Left | Wide-angle RGB | Left body panel | 360 coverage |
| Right | Wide-angle RGB | Right body panel | 360 coverage |
| Mast cam | 30x optical zoom (USB camera module) | Top of mast, pan-tilt mount | Long-range observation, zoom |
| Depth camera | Intel RealSense D435i or OAK-D Lite | Front body, next to main cam | Depth mapping, obstacle avoidance, 3D scanning |
| Night vision | IR camera + IR LED array | Mast or front body | Low-light / night operation |

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
| LIDAR (RPLidar A1/A2) | 1 | Front body, ~20cm height | 2D/360° mapping, SLAM, obstacle detection |
| GPS (u-blox NEO-M8N) | 1 | Top deck (clear sky view) | Position tracking, waypoint navigation, geofencing |
| IMU (BNO055) | 1 | Centre of body | Orientation, tilt detection, dead reckoning |
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
|                     JETSON ORIN NANO                           |
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
|  | - 4x servo steer |  | - 6x wheel enc   |  | - E-stop     | |
|  | - PID speed ctrl |  | - IMU polling    |  | - Tilt limit | |
|  | - Brake control  |  | - Temp sensors   |  | - Overcurr   | |
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
/imu_node ------+--> /ekf_filter --> /odom_fused --> /nav2_controller
/wheel_odom ----+

/nav2_controller --> /cmd_vel --> /motor_bridge --> [ESP32 UART]

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

UART at 115200 baud, simple binary packet protocol:

```
Packet format:
[SYNC: 0xAA] [CMD: 1 byte] [LEN: 1 byte] [DATA: N bytes] [CRC: 1 byte]

Commands (Jetson -> ESP32):
  0x01: Set motor speeds (6x int16)
  0x02: Set steering angles (4x int16)
  0x03: Set LED pattern (1x uint8 + RGB)
  0x04: Set arm servos (8x uint16)
  0x05: Request sensor data
  0x06: E-stop
  0x07: Set brake

Commands (ESP32 -> Jetson):
  0x81: Sensor data (ultrasonics, encoders, IMU, temps)
  0x82: Battery status (voltage, current, SOC%)
  0x83: Safety alert (tilt, overcurrent, stall)
  0x84: Heartbeat (every 100ms)
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

## 9. Bill of Materials (Estimated)

### Phase 1: 0.4 Scale Prototype

| Category | Item | Est. Cost |
|----------|------|-----------|
| **Motors** | 6x N20 micro gearmotors (6V, 100RPM) | 18 |
| **Servos** | 4x SG90 micro servos (steering) | 8 |
| **Electronics** | ESP32-S3 DevKit | 8 |
| **Electronics** | Motor driver (2x L298N or DRV8833) | 8 |
| **Power** | 2S LiPo 2200mAh + charger | 15 |
| **Sensors** | HC-SR04 ultrasonic (x4) | 6 |
| **Sensors** | MPU6050 IMU | 3 |
| **Structure** | PLA/PETG filament (~500g) | 10 |
| **Hardware** | M3/M4 bolts, nuts, bearings | 10 |
| **Camera** | ESP32-CAM module (basic testing) | 8 |
| | **Phase 1 Total** | **~94** |

### Phase 2: Full-Scale 3D Printed

| Category | Item | Est. Cost |
|----------|------|-----------|
| **Compute** | Jetson Orin Nano 8GB | 200 |
| **Compute** | ESP32-S3 DevKit | 8 |
| **Motors** | 6x JGB37-520 12V DC gearmotors (60RPM) | 60 |
| **Servos** | 4x MG996R servos (steering) | 24 |
| **Servos** | 8x MG996R servos (2 arms, 4 per arm) | 48 |
| **Servos** | 2x MG996R (mast pan-tilt) | 12 |
| **Motor drivers** | 3x BTS7960 dual H-bridge (2 motors each) | 18 |
| **Power** | 2x 6S 10Ah LiPo packs | 120 |
| **Power** | 6S BMS board | 15 |
| **Power** | Buck converters (12V, 5V) + BEC (6V) | 20 |
| **Power** | MPPT charge controller | 25 |
| **Solar** | 4x 25W folding panels | 80 |
| **Cameras** | 4x wide-angle USB cameras (body) | 40 |
| **Cameras** | 1x 30x zoom USB camera (mast) | 35 |
| **Cameras** | 1x OAK-D Lite depth camera | 80 |
| **Cameras** | 1x IR camera + IR LEDs | 25 |
| **LIDAR** | RPLidar A1 | 80 |
| **GPS** | u-blox NEO-M8N + antenna | 15 |
| **IMU** | BNO055 9-DOF | 15 |
| **Sensors** | 6x HC-SR04 ultrasonic | 9 |
| **Sensors** | 6x wheel encoders (optical) | 12 |
| **Sensors** | INA219 current sensors (x4) | 8 |
| **Sensors** | DS18B20 temp sensors (x3) | 4 |
| **Weather** | BME280 + anemometer + rain + UV + light | 25 |
| **Fridge** | Peltier TEC1-12706 + heatsink + fan + insulation | 20 |
| **Charging** | Qi wireless charger module (15W) | 10 |
| **Charging** | USB-C PD trigger board + USB-A port | 8 |
| **Audio** | 2x 3W speakers + MAX98357A amp | 10 |
| **Audio** | 2x MEMS microphones (SPH0645) | 6 |
| **Display** | 3.5" IPS LCD (SPI) | 12 |
| **LEDs** | WS2812B strips (2m) + high-power white/red/amber | 15 |
| **LEDs** | IR LED array (4x 850nm) | 5 |
| **Networking** | USB 4G modem dongle | 25 |
| **Structure** | PETG filament (~3-4kg) | 60 |
| **Structure** | 2020 aluminium extrusion (6m total) | 20 |
| **Structure** | M3/M4/M5 bolts, nuts, bearings, brackets | 25 |
| **Structure** | Slip ring (mast 360 rotation) | 8 |
| **Docking** | Spring copper contacts + 24V PSU | 15 |
| **Misc** | Wiring, connectors, heatshrink, PCB | 30 |
| **Misc** | microSD card (128GB) | 10 |
| | **Phase 2 Total** | **~1,270** |

### Phase 3: Metal Build (Additional Costs)

| Category | Item | Est. Cost |
|----------|------|-----------|
| **Materials** | Aluminium sheet/bar stock | 100-200 |
| **Materials** | Steel for axles, shafts | 30-50 |
| **Servos** | Upgrade to DS3218 (25kg) for arms | 40 |
| **Hardware** | Bearings, bushings (metal grade) | 30 |
| **Finishing** | Paint, anodizing, gaskets (IP54) | 40 |
| **Glass** | Acrylic/tempered glass top panel | 25 |
| | **Phase 3 Additional** | **~300-400** |

### Total Project Budget

| Phase | Cost |
|-------|------|
| Phase 1 (0.4 prototype) | ~94 |
| Phase 2 (full 3D print) | ~1,270 |
| Phase 3 (metal, additional) | ~350 |
| **Grand Total** | **~1,714** |

This fits within the 1,500-2,000 budget. Phase 1 is cheap enough to validate the design before committing to the big spend in Phase 2.

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
2. **Design Phase 1 prototype in CAD** — rocker-bogie geometry first
3. **Simulate suspension** — test articulation range in Fusion 360
4. **Print Phase 1 parts** — start with wheels and rocker arms
5. **Order Phase 1 electronics** — ESP32-S3, N20 motors, SG90 servos, L298N drivers
6. **Write ESP32 firmware** — basic motor control + WiFi web server
7. **Assemble and test** — validate the design before Phase 2

---

*Document generated 2026-03-14. Version 1.0.*
*This is a living document — will be updated as the design evolves.*
