# Mars Rover Garden Robot - Project Instructions

## Overview
Mars rover-inspired outdoor robot for garden and park use. Rocker-bogie suspension, 6 wheels (4 steered), AI vision, robotic arms, solar power, coffee table mode.

## Project Location
- Root: `D:\Mars Rover Project\`
- Design doc: `docs/plans/2026-03-14-mars-rover-design.md` (v1.3)
- Engineering analyses: `docs/engineering/` (EA-00 through EA-28)
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
| 08 | Phase 1 Spec | 24 parts (4-segment body), all CAD dimensions, 69hr print |
| 09 | GPIO Pin Map | ESP32-S3 N16R8, Phase 1: 20 pins, Phase 2: 28 pins |
| 10 | Ackermann Steering | 3 modes, min radius 993mm, servo mapping |
| 11 | 3D Printing | PLA (Phase 1), CTC Bizer, settings, heat-set inserts, 4-quadrant body |
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
| 22 | Requirements Spec | Formal FR/PR/DIM/ELEC/LEARN/DFT/MOD requirements for Phase 1 |
| 23 | Wire Harness | 58-wire schedule, connectors, cable routing, colour codes, build order |
| 24 | Robotic Arm Study | Phase 2 arm feasibility, 3-DOF concept, Phase 1 mount prep |
| 25 | Suspension Audit | Tube+connector approach, 9 bearings (EA-26 added diff pivot), dim matrix, wire routing |
| 26 | Suspension Design Package | Full 18-section design: diff mechanism (bar+link+ball joints), steering knuckles, parametric ratios, DOF map |
| 27 | Steering System Design | Complete physical steering mechanism: offset parallel drive, horn link 4-bar linkage, hard stops, clearance envelope |
| 28 | Systems Integration | Cross-domain interface matrix (42 interfaces), assembly DAG, integration test plan, 6 diagrams |

## Key Specs
- Size: 1100mm x 650mm x 1050mm (full) / 440x260mm (0.4 scale Phase 1)
- Weight: ~1.25kg (Phase 1, ~1024g PLA + battery + hardware) / 16.7kg (Phase 2) / 20.8kg (Phase 3)
- Suspension: Rocker-bogie, 9× 608ZZ bearings, 8mm steel rods + printed connectors (EA-25/EA-26)
- Power: 2S LiPo 2200mAh (Phase 1) / 6S 20Ah + 100W solar (Phase 2)
- Compute: ESP32-S3 DevKitC-1 N16R8 (Phase 1) / + Jetson Orin Nano Super (Phase 2)
- Motors: N20 100RPM (Phase 1) / Chihai 37mm 80RPM (Phase 2)
- Drivers: L298N (Phase 1, 3.3V logic concern) / Cytron MDD10A (Phase 2)
- Servos: SG90 (Phase 1) / MG996R (Phase 2)
- Steering: Ackermann (4-wheel), point turn, crab walk; ±35° max; min radius 397mm (Phase 1) / 993mm (full scale) (0.4 scale)
- Budget: ~$102 (Phase 1) / ~$2,032 total

## Build Phases
1. **Phase 1** (0.4 scale, current): PLA prototype, ESP32-S3 + 2× L298N, basic driving ($102)
2. **Phase 2** (full scale): PETG/ASA + aluminium extrusion, all electronics ($1,631)
3. **Phase 3** (full scale): Machined aluminium/steel, IP54 weatherproof ($299 additional)

## 3D Printer
- **Model**: CTC 3D Bizer (MakerBot Replicator 1 Dual clone)
- **Bed size**: 225×145×150mm
- **Material**: PLA only (no PETG, no TPU)
- **File format**: x3g (NOT standard gcode) — uses GPX converter
- **Slicer workflow**: Fusion 360 → STL → Cura → gcode → GPX (`gpx -m cr1d`) → x3g → SD card
- **GPX**: v2.6.8 installed at `C:\Users\charl\bin\gpx.exe`, machine type `cr1d`
- **Extruders**: Dual (use left only), remove/park right nozzle
- **Impact**: Body splits into 4 quadrants (not 2 halves). Rigid PLA wheels with rubber O-ring traction bands.
- **Heat-set inserts**: 170-180°C for PLA (lower than PETG's 200-220°C)
- **Bed adhesion**: Heated bed 60°C + glue stick or painter's tape, brim for large parts
- **Phase 2 upgrade**: Will need PETG/ASA-capable printer for outdoor durability

## CAD Workflow
- **Tool**: Fusion 360 Personal (free) + MCP-Link add-in
- **MCP server**: `cad/fusion-mcp/` (AuraFriday/Fusion-360-MCP-Server)
- **MCP-Link server**: `cad/mcp-link-server/` (runs at https://127-0-0-1.local.aurafriday.com:31173/sse)
- **Parameters**: `cad/scripts/generate_rover_params.py` — all dimensions for Phase 1 (0.4x) and Phase 2 (1.0x)
- **Design order**: bearing test → wheels → bogies → rockers → diff bar → steering → motor mounts → body → electronics tray

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
- CAD: Fusion 360 Personal (installed, MCP-Link add-in connected)
- 3D Printer: CTC Bizer (225×145×150mm bed, x3g via GPX 2.6.8 `cr1d`, Cura slicer)
- GPX: v2.6.8 (`C:\Users\charl\bin\gpx.exe`) — `gpx -m cr1d input.gcode output.x3g`
- Jetson: Ubuntu 22.04 + ROS2 Humble (Phase 2)

## MCP Servers (`.mcp.json`)
| Server | Purpose | Notes |
|--------|---------|-------|
| fusion360 | Fusion 360 via MCP-Link (AuraFriday) | 13 sub-tools: python, system, terminal, sqlite, context7, etc. |
| 3dprint | STL manipulation, slicing, printer control | get_stl_info, slice, scale, rotate, visualize |
| github | GitHub API (issues, PRs, code search) | PAT from `gh auth token` |
| mermaid | Diagram generation (preview + save) | SVG/PNG/PDF output |
| math | SymPy/SciPy math computations | Algebra, calculus, unit conversion |
| kicad | KiCad PCB/schematic tools | Needs KiCad installed (Phase 2) |
| cadquery | CadQuery parametric CAD | Python-based CSG modeling |
| text-to-model | 64 Fusion 360 CAD tools (JIS parts, sketches) | Disabled — enable when Fusion 360 running with add-in |
| jlcpcb | JLCPCB component search & BOM | For parts ordering |

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

## Project Status (as of 2026-03-24)
- All 29 engineering analyses complete (EA-00 through EA-28; EA-28 = systems integration)
- Full engineering audit complete: all stale values swept (bogie 180mm, diff bar, CTC Bizer, PLA, 9 bearings — EA-25/EA-26)
- All ROS2 nodes scaffolded (10 nodes across 7 packages)
- All ESP32 firmware modules complete (9 headers: config, motors, steering, sensors, webserver, uart_nmea, uart_binary, ota, leds)
- ESP32-S3 firmware compiles successfully (1045KB flash 79%, 53KB RAM 16%, v0.3.0)
- Firmware safety: arm-before-drive, battery speed limit, stall detect, rate-limited steering, 5 LED patterns
- PWA phone app complete (ARM/DISARM, telemetry, drive, map, mission, settings, camera, OTA)
- Gazebo garden world + 21 simulation test scenarios
- ROS2 unit tests: 164 pytest tests across 6 test files (with mock framework)
- ESP32 firmware unit tests: 42 pytest host-based tests (all passing)
- CI/CD: GitHub Actions (ESP32 compile, firmware tests, ROS2 build, Python lint, docs check EA-00 to EA-28)
- 39 Fusion 360 CAD scripts (27 active + 4 deprecated + 6 reference models + 2 superseded)
- EA-25/EA-26 suspension complete: tube+connector approach, 9 bearings (not 11), through-bar diff mechanism
- BatchExportAll updated: 28 STL exports (DifferentialLink removed)
- 10 diagrams rendered to SVG (4 wiring + 6 integration from EA-28)
- Print strategy, Phase 1 BOM, maintenance guide, disassembly guide, data capture template all complete
- ESP32 Arduino core v3.3.7 installed locally, pytest + flake8 + mmdc installed
- **Next step**: Re-run BatchExportAll in Fusion 360, set up CTC Bizer printer, order Phase 1 parts

## Key Learnings
- ESP32 Arduino Core v3.x: `esp_task_wdt_init()` takes `esp_task_wdt_config_t*` struct, not int+bool
- Windows case-insensitive FS: local `webserver.h` collides with ESP32 library `WebServer.h` — renamed to `rover_webserver.h`
- Include guard `WEBSERVER_H` collided with ESP32 library's own guard — use `ROVER_WEBSERVER_H`
- Single-translation-unit: forward-declare functions used before definition in same .h file
