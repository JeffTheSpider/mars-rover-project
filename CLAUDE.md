# Mars Rover Garden Robot - Project Instructions

## Overview
Mars rover-inspired outdoor robot for garden and park use. Rocker-bogie suspension, 6 wheels (4 steered), AI vision, robotic arms, solar power, coffee table mode.

## Project Location
- Root: `D:\Mars Rover Project\`
- Design doc: `docs/plans/2026-03-14-mars-rover-design.md` (v1.3)
- Engineering analyses: `docs/engineering/` (EA-00 through EA-21)
- Shopping list: `docs/plans/phase1-shopping-list.md`
- Master todo: `docs/plans/todo-master.md`
- Firmware: `firmware/esp32/` (ESP32-S3 Phase 1 motor controller)
- ROS2 packages: `software/jetson/` (7 packages)
- Phone app: `software/pwa/` (Catppuccin Mocha PWA)
- CAD files: `cad/` (Fusion 360, not yet started)
- 3D print files: `3d-print/` (STL exports, not yet started)

## Engineering Analysis Documents
| EA | Topic | Key Content |
|----|-------|-------------|
| 01 | Suspension | Rocker-bogie geometry, NASA scaling, 608ZZ bearings |
| 02 | Drivetrain | Torque calcs, N20/Chihai motors, L298N/Cytron drivers |
| 03 | Power | 6S LiPo 444Wh, solar 2S2P, BMS, wire gauge |
| 04 | Compute/Sensors | Jetson Orin Nano, cameras, LIDAR, GPS, IMU |
| 05 | Weight Budget | 16.7kg Phase 2, 20.8kg Phase 3, CoG analysis |
| 06 | Cost | $2,031.75 total, phase-by-phase breakdown |
| 07 | Open Source Review | Sawppy + JPL hybrid approach |
| 08 | Phase 1 Spec | 22 parts, all CAD dimensions, 65hr print |
| 09 | GPIO Pin Map | ESP32-S3 N16R8, Phase 1: 20 pins, Phase 2: 28 pins |
| 10 | Ackermann Steering | 3 modes, min radius 993mm, servo mapping |
| 11 | 3D Printing | PETG/ASA, settings, heat-set inserts, segmentation |
| 12 | UART Protocol | NMEA-style text, 115200 baud, 18 msg types, 50Hz (Phase 1/debug) |
| 13 | ROS2 Architecture | Node graph, Nav2, SLAM, EKF, YOLO, behaviour trees |
| 14 | Weatherproofing | IP44/IP54, zones, cable glands, thermal |
| 15 | Safety Systems | 4-layer, E-stop, fuses, watchdog, geofence |
| 16 | PWA App Design | Catppuccin Mocha, D-pad, camera, nav map |
| 17 | Phase 1 Build Guide | Step-by-step, ~14 day timeline, troubleshooting |
| 18 | Binary UART Protocol | COBS + CRC-16, 460800 baud, binary structs, 12% utilisation (Phase 2) |
| 19 | Wiring Diagram | Phase 1 complete wiring reference, ASCII diagrams, connector strategy |
| 20 | CAD Preparation | Parametric dimensions from EA-08, Fusion 360 assembly structure |
| 21 | Test Procedures | Acceptance criteria for firmware, electronics, integration, autonomy |

## Key Specs
- Size: 1100mm x 650mm x 1050mm (full) / 440x260mm (0.4 scale Phase 1)
- Weight: ~1.1kg (Phase 1) / 16.7kg (Phase 2) / 20.8kg (Phase 3)
- Suspension: Rocker-bogie, 608ZZ bearings, 8mm shafts
- Power: 2S LiPo 2200mAh (Phase 1) / 6S 20Ah + 100W solar (Phase 2)
- Compute: ESP32-S3 DevKitC-1 N16R8 (Phase 1) / + Jetson Orin Nano Super (Phase 2)
- Motors: N20 100RPM (Phase 1) / Chihai 37mm 80RPM (Phase 2)
- Drivers: L298N (Phase 1, 3.3V logic concern) / Cytron MDD10A (Phase 2)
- Servos: SG90 (Phase 1) / MG996R (Phase 2)
- Steering: Ackermann (4-wheel), point turn, crab walk; ±35° max; min radius 397mm (0.4 scale)
- Budget: ~$102 (Phase 1) / ~$2,032 total

## Build Phases
1. **Phase 1** (0.4 scale, current): PETG prototype, ESP32-S3 + 2× L298N, basic driving ($102)
2. **Phase 2** (full scale): PETG/ASA + aluminium extrusion, all electronics ($1,631)
3. **Phase 3** (full scale): Machined aluminium/steel, IP54 weatherproof ($299 additional)

## Firmware (`firmware/esp32/`)
- Arduino framework, ESP32-S3 DevKitC-1
- `config.h` — Pin defs, geometry constants, timing
- `motors.h` — 4-channel L298N control with speed ramping
- `steering.h` — Ackermann/point turn/crab walk via SG90 servos
- `sensors.h` — Battery ADC (10-sample average), encoders, E-stop
- `rover_webserver.h` — HTTP + WebSocket, embedded Catppuccin Mocha UI
- `esp32.ino` — Main loop, WiFi, watchdog, non-blocking timing
- Compile: `arduino-cli compile --fqbn esp32:esp32:esp32s3`
- Upload: USB or OTA (espota.py)

## ROS2 Packages (`software/jetson/`)
- `rover_bringup` — Launch files, config YAML, URDF model
- `rover_hardware` — UART bridge node (C++, EA-12 protocol)
- `rover_navigation` — Ackermann controller, waypoint follower, geofence
- `rover_perception` — YOLO detection, camera manager, depth processor
- `rover_autonomy` — Behaviour trees (patrol, explore, return home)
- `rover_teleop` — Web server node (WebSocket for phone PWA)
- `rover_msgs` — Custom messages (WheelSpeeds, SteeringAngles, RoverStatus, Detection)

## Phone PWA (`software/pwa/`)
- Catppuccin Mocha/Latte themes (dark/light toggle), Mars red accent (#f38ba8)
- D-pad with touch-and-hold (touchstart/touchend)
- 3 steering modes, speed slider, E-stop
- Live MJPEG camera streaming (4 sources: front, rear, mast, depth)
- System panel: firmware version, OTA trigger, restart, CPU temp, WiFi RSSI
- WebSocket JSON protocol
- Service worker network-first (v1)
- Responsive: phone portrait/landscape, tablet, desktop

## Development Environment
- OS: Windows 11
- Arduino CLI: v1.4.1 (`C:\Users\charl\bin\arduino-cli.exe`)
- ESP32 board: `esp32:esp32:esp32s3` (DevKitC-1 N16R8)
- Node.js: v24.13.1
- Python: 3.14
- CAD: Fusion 360 (to be installed)
- 3D Printer: Ender 3 (220×220×250mm bed)
- Jetson: Ubuntu 22.04 + ROS2 Humble (Phase 2)

## Conventions
- ESP32 firmware follows Clock/Lamp project patterns (single translation unit, .h includes, non-blocking state machines)
- Phone PWA follows Hub project patterns (Catppuccin Mocha, WebSocket, service worker, Plus Jakarta Sans)
- All physical measurements in millimetres unless stated
- UART protocol: NMEA-style `$CMD,data*XOR\n`
- Document all design decisions in engineering analysis documents
- 100nF ceramic capacitors on all motor terminals (noise suppression)
- L298N requires 5V logic; ESP32-S3 outputs 3.3V — works in practice but monitor
- Nav2: Use RegulatedPurePursuit (not DWB) for Ackermann rovers — cannot spin in place
- Nav2: DUBIN motion model (forward-only), not REEDS_SHEPP (allows reverse planning)
- Nav2: `use_rotate_to_heading: false` is CRITICAL for Ackermann
- Dual EKF: local (odom frame, smooth, no GPS) + global (map frame, with GPS, may jump)
- Gazebo diff_drive plugin: set `publish_odom_tf: false` when EKF publishes odom→base_link TF
- UK magnetic declination: -0.0175 rad (for navsat_transform)

## Project Status (as of 2026-03-15)
- All 22 engineering analyses complete (EA-00 master handbook through EA-21)
- All ROS2 nodes scaffolded (10 nodes across 7 packages)
- All ESP32 firmware modules scaffolded (7 modules incl. OTA, NMEA, binary UART)
- ESP32-S3 firmware compiles successfully (1042KB flash 79%, 53KB RAM 16%, v0.2.0)
- PWA phone app complete (telemetry, drive, map, mission, settings, camera stream, OTA)
- Gazebo garden world + 21 simulation test scenarios
- ROS2 unit tests: 134 pytest tests across 5 test files
- ESP32 firmware unit tests: 42 pytest host-based tests (NMEA, Ackermann, battery, COBS)
- Research references: YOLO garden detection, Gazebo simulation best practices
- CI/CD: GitHub Actions (ESP32 compile, ROS2 build, Python lint, docs check)
- All config/launch files corrected to match EA research
- Fusion 360 MCP setup guide ready (`docs/plans/fusion360-mcp-setup.md`)
- **Next step**: Install Fusion 360 + MCP server, then CAD design + order Phase 1 components

## Key Learnings
- ESP32 Arduino Core v3.x: `esp_task_wdt_init()` takes `esp_task_wdt_config_t*` struct, not int+bool
- Windows case-insensitive FS: local `webserver.h` collides with ESP32 library `WebServer.h` — renamed to `rover_webserver.h`
- Include guard `WEBSERVER_H` collided with ESP32 library's own guard — use `ROVER_WEBSERVER_H`
- Single-translation-unit: forward-declare functions used before definition in same .h file
