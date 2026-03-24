# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-24

### Added
- EA-22 Requirements Specification (formal FR/PR/DIM/ELEC/LEARN/DFT/MOD)
- EA-23 Wire Harness (58-wire schedule, connectors, cable routing, colour codes)
- EA-24 Robotic Arm Study (Phase 2 feasibility, 3-DOF concept, Phase 1 mount prep)
- Maintenance guide with after-session, weekly, monthly, and crash checklists
- Disassembly guide with per-component procedures
- Prototype data capture template (build log, dimensional verification, performance)
- Future design improvements document (Phase 2 lessons learned template)
- Firmware: arm-before-drive safety (ARM/DISARM commands via WebSocket and UART)
- Firmware: battery-based speed limiting (50% at warning, 0% at critical)
- Firmware: stall detection (2s timeout, PWM > 20% threshold)
- Firmware: steering rate limiting (60 deg/s max, smooth interpolation)
- Firmware: 5 LED patterns (idle, armed, driving, warning, error/SOS)
- Firmware: leds.h module with arm/disarm interface
- PWA: ARM/DISARM toggle buttons on Drive tab
- PWA: telemetry cards for arm state, speed limit, stall detection
- PWA: gamepad and D-pad gated on armed state
- ROS2: /rover/arm topic subscriber in UART bridge node
- UART: $ARM and $DSA NMEA commands
- CAD: camera mast mount (RL top deck tile, 4x M3 heat-set)
- CAD: antenna dish detail (RR top deck tile, cosmetic)
- CAD: arm mount bosses (FL body quadrant, 4x M3 for Phase 2 arm)
- CAD: RTG-style radiator fin detail (RL/RR rear wall, cosmetic)
- CAD: MLI blanket edge ridges (all quadrants, cosmetic)
- CAD: rover tire script (TPU 95A, 86mm OD, 48 treads)
- Wiring diagrams: 4 Mermaid source files + rendered SVGs
- CI: firmware unit test job (42 pytest tests)
- CI: docs check now covers EA-00 through EA-24
- MIT LICENSE file
- CHANGELOG.md (this file)

### Changed
- Body quadrant walls: 3mm -> 4mm, added panel line grooves and corner chamfers
- Bogie arm walls: 2.5mm -> 3mm
- Bogie arm length: 120mm -> 180mm (corrected 0.4x scaling of 450mm)
- Diff bar rod: 200mm -> 300mm (250mm pivot span + 25mm overhang each side)
- Rocker arm bogie pivot boss: 26mm -> 30mm OD (wall thickness fix)
- Cable exit holes: 10x5mm -> 12x8mm (JST-XH connector compatible)
- Electronics tray: added 4 corner gussets (5x5x2mm)
- Wheel: added spoke holes, rim lips, USE_TPU_TIRE toggle
- Top deck: added panel line grid (30mm spacing, 0.5mm deep)
- Bearing oversize: 0.1mm -> 0.15mm in generate_rover_params.py
- Battery color thresholds in PWA: 50/20% -> 30/5% (matches firmware)
- Service worker cache bumped to rover-v5
- Printer references: Ender 3 -> CTC Bizer throughout
- Material references: PETG -> PLA for Phase 1 throughout
- Bearing count: 10 -> 11 throughout
- Parts count: 22 -> 26, print time: 65hr -> 69hr
- URDF: bogie length 0.120 -> 0.180, diff bar 0.200 -> 0.300
- .gitignore: added .x3g, .gcode, .pytest_cache, coverage files

### Fixed
- motorCurrent[] undefined in esp32.ino -> changed to motorSpeed[]
- RAD_TO_DEG undefined in steering.h -> added #ifndef guard to config.h
- OTA port hardcoded 3232 in ota.h -> uses OTA_PORT from config.h
- URDF typo: <xac:property -> <xacro:property
- EA-00 master handbook: stale Ender 3 and PETG references
- EA-02 summary table: min turn radius ~300mm -> 397mm
- EA-08 summary table: bogie 120 -> 180, body quadrant text
- EA-11: major rewrite for CTC Bizer, PLA, 4 quadrants, x3g workflow
- EA-15: watchdog API updated for ESP32 Arduino Core v3.x
- EA-19: added motor caps, 5V BEC documentation
- EA-20: bogie, bearing count, Y_SPLIT corrections
- Pre-print checklist: diff bar rod flag resolved (200 -> 300mm)
- Assembly reference: servo centre 1472us -> 1500us

## [0.2.0] - 2026-03-23

### Added
- Complete ESP32-S3 firmware (7 modules: config, motors, steering, sensors, webserver, UART, OTA)
- Firmware compiles: 1042KB flash (79%), 53KB RAM (16%)
- PWA phone app (Catppuccin Mocha/Latte, D-pad, camera, telemetry, settings, OTA)
- 7 ROS2 packages scaffolded (10 nodes)
- 42 firmware host-based pytest tests
- 134 ROS2 pytest tests with mock framework
- GitHub Actions CI/CD (compile, build, lint, docs check)
- Gazebo garden world + 21 simulation scenarios
- 22 engineering analysis documents (EA-00 through EA-21)
- 18 Fusion 360 CAD scripts for all Phase 1 parts
- Print strategy, pre-print checklist, assembly reference
- CTC Bizer guide, shopping list, complete BOM

### Changed
- Initial project structure established

## [0.1.0] - 2026-03-14

### Added
- Initial project design document (v1.3)
- Project directory structure
- Basic README with architecture overview
