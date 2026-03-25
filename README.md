# Mars Rover Garden Robot

A Mars rover-inspired outdoor robot designed for garden and park use. Features NASA-style rocker-bogie suspension, Ackermann steering, AI-powered navigation, robotic arms, solar charging, and a coffee table mode for stationary use.

**Status:** Design phase complete (29 engineering analyses, EA-00 through EA-28). All software scaffolded, awaiting hardware for validation.

## Key Specifications

| Spec | Phase 1 (0.4 Scale) | Phase 2 (Full Scale) | Phase 3 (Metal) |
|------|---------------------|----------------------|------------------|
| Dimensions | 440 x 260 mm | 1100 x 650 x 1050 mm | 1100 x 650 x 1050 mm |
| Weight | ~1.1 kg | ~16.7 kg | ~20.8 kg |
| Power | 2S LiPo 2200 mAh | 6S LiPo 20 Ah + 100 W solar | 6S LiPo 20 Ah + 100 W solar |
| Compute | ESP32-S3 | ESP32-S3 + Jetson Orin Nano Super | ESP32-S3 + Jetson Orin Nano Super |
| Motors | N20 100 RPM | Chihai 37mm 80 RPM | Chihai 37mm 80 RPM |
| Drivers | L298N | Cytron MDD10A | Cytron MDD10A |
| Servos | SG90 | MG996R | MG996R |
| Top Speed | ~2 km/h | 5 km/h | 5 km/h |
| Runtime | ~30 min | 4 hr driving | 4 hr driving |
| Budget | ~$102 | ~$1,631 | +$299 |
| Total Budget | | **$2,032** | |

## Build Phases

### Phase 1 -- 0.4 Scale 3D Printed Prototype
PLA 3D printed chassis at 40% scale. ESP32-S3 with 2x L298N motor drivers. Basic driving, steering, and WebSocket control via phone. 26 printed parts, approximately 69 hours of print time on a CTC Bizer.

### Phase 2 -- Full-Scale 3D Printed
Full-size PETG/ASA chassis reinforced with aluminium extrusion. Adds Jetson Orin Nano Super for AI and autonomous navigation, LIDAR, stereo cameras, GPS, robotic arms, mini fridge, solar panels, and coffee table mode.

### Phase 3 -- Full-Scale Metal Chassis
Machined aluminium and steel replacing 3D printed structural components. IP54 weatherproofing with cable glands and sealed enclosures for year-round outdoor operation.

## Architecture

```
Phone PWA (WebSocket)
        |
        v
Jetson Orin Nano Super          ESP32-S3 DevKitC-1 N16R8
  - ROS2 Humble                   - Motor control (4ch PWM)
  - Nav2 navigation                - Ackermann steering (4 servos)
  - SLAM mapping                   - Battery monitoring
  - YOLO object detection          - Encoder feedback
  - Behaviour trees                - E-stop handling
  - Dual EKF localization          - WebSocket server (Phase 1)
        |                                  ^
        +------ UART (115200/460800) ------+
```

The ESP32-S3 handles real-time motor control and sensor reading. The Jetson runs ROS2 for high-level autonomy, navigation, and perception. In Phase 1, the ESP32-S3 operates standalone with direct WebSocket control from the phone app. In Phase 2, the Jetson connects via UART and takes over navigation while the ESP32-S3 remains the low-level controller.

## Repository Structure

```
Mars Rover Project/
  docs/
    engineering/          # 29 engineering analysis documents (EA-00 to EA-28)
    plans/                # Master design document, task tracking
    references/           # Research notes (3D printing, ROS2)
    datasheets/           # Component datasheets
  firmware/
    esp32/                # ESP32-S3 Arduino firmware
      esp32.ino           #   Main loop, WiFi, watchdog
      config.h            #   Pin definitions, constants
      motors.h            #   4-channel L298N motor control
      steering.h          #   Ackermann / point turn / crab walk
      sensors.h           #   Battery ADC, encoders, E-stop
      rover_webserver.h   #   HTTP + WebSocket embedded UI
      ota.h               #   ArduinoOTA firmware updates
      uart_nmea.h         #   NMEA text UART protocol (Phase 1)
      uart_binary.h       #   COBS binary UART protocol (Phase 2)
  software/
    jetson/               # ROS2 Humble packages
      rover_bringup/      #   Launch files, config, URDF
      rover_hardware/     #   UART bridge node (C++)
      rover_navigation/   #   Ackermann controller, waypoint follower, geofence
      rover_perception/   #   YOLO detection, camera, depth
      rover_autonomy/     #   Behaviour trees (patrol, explore, return home)
      rover_teleop/       #   WebSocket server for phone app
      rover_msgs/         #   Custom messages (WheelSpeeds, SteeringAngles, etc.)
    pwa/                  # Phone control app (Catppuccin Mocha PWA)
  cad/                    # Fusion 360 CAD files (planned)
  3d-print/               # STL exports for printing (planned)
```

## Engineering Analyses

| ID | Title |
|----|-------|
| EA-00 | Master Engineering Handbook (compiled reference to all EAs) |
| EA-01 | Suspension Analysis (rocker-bogie geometry, NASA scaling, 608ZZ bearings) |
| EA-02 | Drivetrain Analysis (torque calculations, motor selection, driver selection) |
| EA-03 | Power System Analysis (LiPo sizing, solar charging, BMS, wire gauge) |
| EA-04 | Compute and Sensors (Jetson Orin Nano, cameras, LIDAR, GPS, IMU) |
| EA-05 | Weight Budget (per-component breakdown, centre of gravity analysis) |
| EA-06 | Cost Breakdown (phase-by-phase BOM, $2,032 total) |
| EA-07 | Open Source Review (Sawppy + JPL hybrid design approach) |
| EA-08 | Phase 1 Prototype Spec (26 parts, all CAD dimensions, 69 hr print) |
| EA-09 | ESP32-S3 GPIO Pin Map (N16R8, Phase 1: 20 pins, Phase 2: 28 pins) |
| EA-10 | Ackermann Steering (3 modes, min radius 397 mm at 0.4 scale, servo mapping) |
| EA-11 | 3D Printing Strategy (PLA Phase 1, CTC Bizer, heat-set inserts, 4-quadrant body) |
| EA-12 | UART Protocol (NMEA-style text, 115200 baud, 18 message types) |
| EA-13 | ROS2 Architecture (node graph, Nav2, SLAM, EKF, YOLO, behaviour trees) |
| EA-14 | Weatherproofing (IP44/IP54, zones, cable glands, thermal management) |
| EA-15 | Safety Systems (4-layer safety, E-stop, fuses, watchdog, geofence) |
| EA-16 | PWA App Design (Catppuccin Mocha, D-pad, camera feed, nav map) |
| EA-17 | Phase 1 Build Guide (step-by-step, ~14 day timeline, troubleshooting) |
| EA-18 | Binary UART Protocol (COBS + CRC-16, 460800 baud, 12% utilisation) |
| EA-19 | Phase 1 Wiring (complete wiring reference, connector strategy) |
| EA-20 | CAD Preparation Guide (parametric dimensions, Fusion 360 assembly) |
| EA-21 | Test Procedures (acceptance criteria, firmware/electronics/integration) |
| EA-22 | Requirements Specification (formal FR/PR/DIM/ELEC/LEARN/DFT/MOD) |
| EA-23 | Wire Harness (58-wire schedule, connectors, cable routing, colour codes) |
| EA-24 | Robotic Arm Study (Phase 2 feasibility, 3-DOF concept, Phase 1 mount prep) |
| EA-25 | Suspension Audit (tube+connector approach, 9 bearings, dimension matrix) |
| EA-26 | Suspension Design Package (diff mechanism, steering knuckles, parametric ratios) |
| EA-27 | Steering System Design (horn link 4-bar linkage, hard stops, clearance envelope) |
| EA-28 | Systems Integration (42 cross-domain interfaces, assembly DAG, integration test plan) |

## Key Features

- **Rocker-Bogie Suspension** -- NASA-derived 6-wheel suspension with 608ZZ bearings and 8 mm shafts. Each side articulates independently to maintain all wheels in ground contact over uneven terrain.

- **Ackermann Steering (3 Modes)** -- Four steered wheels with computed Ackermann geometry. Supports standard steering (minimum radius 993 mm), point turn (zero-radius rotation), and crab walk (lateral movement).

- **Dual EKF Localization** -- Two extended Kalman filters via robot_localization: one fusing wheel odometry + IMU for local tracking, one adding GPS for global position.

- **Autonomous Navigation** -- Nav2 with RegulatedPurePursuit controller, slam_toolbox for SLAM mapping, costmap with obstacle avoidance.

- **AI Object Detection** -- YOLOv8 via TensorRT on Jetson Orin Nano Super for real-time garden object detection (plants, obstacles, pets, people).

- **Behaviour Trees** -- BT.CPP behaviour trees for autonomous missions: patrol routes, exploration, and return-to-home.

- **Solar Charging** -- 100 W panel array (2S2P configuration) with MPPT charge controller for extended outdoor operation.

- **Robotic Arms** -- Dual servo-driven arms for interaction and carrying tasks (Phase 2).

- **Mini Fridge** -- Peltier-cooled compartment for drinks during garden use (Phase 2).

- **Coffee Table Mode** -- Flat top surface with retractable elements for use as a stationary outdoor table (Phase 2).

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Real-time control | ESP32-S3, Arduino framework, FreeRTOS |
| AI / Navigation | Jetson Orin Nano Super, Ubuntu 22.04 |
| Middleware | ROS2 Humble |
| Navigation | Nav2, RegulatedPurePursuit controller |
| Mapping | slam_toolbox (SLAM) |
| Localization | robot_localization (dual EKF) |
| Perception | YOLOv8 + TensorRT |
| Autonomy | BT.CPP (behaviour trees) |
| Communication | UART (ESP32 <-> Jetson), WebSocket (Jetson <-> PWA) |
| Phone App | Progressive Web App (Catppuccin Mocha, vanilla JS) |
| CAD | Fusion 360 |
| 3D Printing | PLA (Phase 1), PETG/ASA (Phase 2+), CTC Bizer |

## Getting Started

Phase 1 build instructions are documented in [EA-17: Phase 1 Build Guide](docs/engineering/17-phase1-build-guide.md), which covers a step-by-step timeline over approximately 14 days including 3D printing, electronics assembly, firmware flashing, and testing.

Prerequisites:
- Arduino CLI v1.4.1+ with `esp32:esp32:esp32s3` board package
- CTC Bizer (or similar) 3D printer with PLA filament
- ESP32-S3 DevKitC-1 N16R8 development board

To compile the Phase 1 firmware:
```bash
arduino-cli compile --fqbn esp32:esp32:esp32s3 firmware/esp32/
```

For the full design rationale and specifications, see the [master design document](docs/plans/2026-03-14-mars-rover-design.md).
