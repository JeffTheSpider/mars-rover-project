# Mars Rover Garden Robot — Master Todo List

**Created**: 2026-03-15
**Last Updated**: 2026-03-15 (evening)
**Status**: Design phase complete, all software scaffolded, awaiting hardware for validation

---

## Legend

- [ ] Not started
- [~] In progress
- [x] Complete

---

## 1. DOCUMENTATION & CONSISTENCY (Can do now — no hardware needed)

### 1.1 Design Doc Updates
- [x] Update design doc v1.2 → v1.3 with all research-backed corrections
  - [x] Update EA reference from "EA-01 through EA-12" to "EA-01 through EA-18"
  - [x] Update Nav2 controller section (DWB → RegulatedPurePursuit)
  - [x] Update EKF section (single → dual EKF architecture)
  - [x] Update motion model (REEDS_SHEPP → DUBIN)
  - [x] Remove spin recovery behavior references
  - [x] Add USB camera tiered bandwidth approach
  - [x] Add carbon fiber reinforcement mention for Phase 2
  - [x] Cross-reference EA-18 binary protocol for Phase 2

### 1.2 Cross-Reference Audit (DONE — 3 HIGH issues fixed, 3 MEDIUM noted, 5 LOW noted)
- [x] Verify all 18 EAs reference each other correctly where dependent
- [x] Check EA-02 torque calcs match EA-05 weight budget values — consistent (34.2kg design weight)
- [x] Check EA-03 power budget matches EA-02 motor selections — consistent (peak 24A = 6×4A stall)
- [x] Check EA-06 cost breakdown matches all component selections — **fixed**: filament $10→$20
- [x] Verify EA-08 Phase 1 spec dimensions match EA-01 suspension geometry — consistent (0.4× scaling)
- [x] Verify EA-09 GPIO pinmap covers all sensors in EA-04 — **gap confirmed**: 6× ultrasonic, 3× DS18B20, audio, LCD need I2C expander (PCA9535/PCF8574). BME280/BH1750/VEML6075 fit on existing I2C bus
- [x] Verify EA-10 Ackermann values match EA-08 wheelbase dimensions — consistent (900mm/360mm)
- [x] Verify EA-17 build guide references correct EA numbers — correct
- [x] **Fixed**: EA-02 Ackermann wheelbase 680mm→900mm (was using projected ground distance)
- [x] **Fixed**: EA-05 motor name JGB37-520→Chihai CHR-GM37-520 (185g, matching EA-02)
- [x] **Fixed**: EA-05 motor driver BTS7960→Cytron MDD10A (matching EA-02)

### 1.3 Missing Documentation
- [x] Create project README.md at repository root (project overview, phase status, quick links)
- [x] Create `docs/datasheets/README.md` listing required datasheets with download links
- [x] Create wiring diagram document for Phase 1 (EA-19: ESP32-S3 → motors/sensors/servos)
- [x] Create CAD preparation guide (EA-20, reference dimensions from EA-08 for Fusion 360)
- [x] Create test procedures & acceptance criteria (EA-21)
- [x] Create Master Engineering Handbook (EA-00, compiles all EAs)
- [x] Create design methodology document (V-model, phases, review gates)
- [x] Create Fusion 360 MCP setup guide
- [x] Create parametric CAD generation script (cad/scripts/generate_rover_params.py)
- [x] Document the backup strategy (`docs/plans/backup-strategy.md` + `scripts/backup.bat`)

---

## 2. SOFTWARE — Config & Launch Fixes (Can do now)

### 2.1 Nav2 & Localization (DONE this session)
- [x] Fix nav2_params.yaml: DWBLocalPlanner → RegulatedPurePursuitController
- [x] Fix nav2_params.yaml: REEDS_SHEPP → DUBIN motion model
- [x] Fix nav2_params.yaml: Remove spin recovery behavior
- [x] Fix nav2_params.yaml: Add `use_rotate_to_heading: false`
- [x] Fix ekf.yaml: Single EKF → Dual EKF (local + global)
- [x] Fix ekf.yaml: Add navsat_transform configuration
- [x] Fix nav.launch.py: Single ekf_node → dual ekf_local + ekf_global + navsat_transform
- [x] Fix hardware.launch.py: Inline placeholder URDF → real xacro file reference

### 2.2 URDF / Simulation
- [x] Uncomment Gazebo plugins in rover.urdf.xacro (diff_drive, joint_state, LiDAR, IMU, depth camera)
- [x] Create standalone `simulation.launch.py` for Gazebo testing
- [x] Add Gazebo world file for garden environment (grass + gravel path + slopes + obstacles + furniture)
- [ ] Test URDF loads correctly: `check_urdf rover.urdf` (requires Jetson)
- [ ] Verify TF tree matches EA-13 specification (requires Jetson)

### 2.3 ROS2 Node Implementation (All scaffolded — needs on-hardware testing)
- [x] `uart_bridge_node.cpp` — NMEA parsing implemented (ENC, IMU, USS, BAT, STS + odometry)
  - [x] Parse $RENC (encoder data) + compute differential drive odometry
  - [x] Parse $RIMU (IMU quaternion, gyro, accel with covariance)
  - [x] Parse $RBAT (battery voltage + SoC)
  - [x] Parse $REST / $RSTS (E-stop and status)
  - [x] Parse $RUSS (6x ultrasonic → Range messages)
  - [x] Send $CMTR (motor commands)
  - [x] Send $CSTR (steering commands)
  - [x] Handle watchdog timeout
  - [x] Publish to ROS2 topics (/wheel_odom, /imu/data, /battery_state, /ultrasonic/*)
- [x] `ackermann_controller.py` — Ackermann geometry implemented (EA-10)
- [x] `geofence_node.py` — GPS boundary check with haversine
- [x] `waypoint_follower.py` — GPS waypoint navigation via Nav2 action server
- [x] `camera_manager.py` — tiered USB camera management (3 tiers)
- [x] `yolo_node.py` — TensorRT YOLO inference node
- [x] `depth_processor.py` — OAK-D stereo depth + PointCloud2
- [x] `mission_planner.py` — BT.CPP behaviour tree integration
- [x] `joy_mapper.py` — gamepad teleop with dead zone + speed modes
- [x] `web_server_node.py` — WebSocket server for PWA telemetry
- [ ] **All nodes need on-hardware validation** (requires Jetson + sensors)

### 2.4 ESP32-S3 Firmware (Phase 1 — All scaffolded, needs on-hardware testing)
- [x] Implement full NMEA protocol parser (EA-12) — checksum, command routing, telemetry
- [x] Implement motor control (L298N, 4 channels) — PWM, direction, acceleration ramping
- [x] Implement Ackermann steering (EA-10) — 4 servos, point turn, crab walk
- [x] Implement encoder reading (6 channels) — interrupt-driven, speed/distance/odometry
- [x] Implement IMU reading (BNO055 via I2C) — quaternion, gyro, accel, calibration
- [x] Implement battery monitoring — ADC voltage divider, SoC lookup, low battery warning
- [x] Implement E-stop system (EA-15) — hardware pin, software command, UART watchdog
- [x] Implement ultrasonic sensors (6 channels) — non-blocking trigger/echo, median filter
- [x] Add WiFi AP mode for initial configuration
- [x] Add OTA firmware update support
- [x] Test compile for ESP32-S3 DevKitC-1 (971KB/74% flash, 48KB/14% RAM — ESP32 Core v3.3.7)
- [ ] **All modules need on-hardware validation** (requires ESP32-S3 + peripherals)

---

## 3. CAD & MECHANICAL (Requires Fusion 360 — Charlie's involvement)

### 3.1 Fusion 360 CAD Design
- [ ] Install and set up Fusion 360
- [ ] Create assembly structure (top-down design)
- [ ] Design body/chassis (main enclosure with 4 access panels)
- [ ] Design rocker arms (left + right, 608ZZ bearing mounts)
- [ ] Design bogie arms (left + right, 608ZZ bearing mounts)
- [ ] Design differential bar mechanism
- [ ] Design wheel hubs (Mars-aesthetic curved spokes, EA-11)
- [ ] Design TPU tyres (interference fit: 0.3mm Phase 1)
- [ ] Design steering knuckles (4x, servo horn mount)
- [ ] Design motor mounts (6x, N20/Chihai motor)
- [ ] Design mast base and pan/tilt mechanism
- [ ] Design arm mounting points (Phase 2 prep)
- [ ] Design solar panel mount rails
- [ ] Design mini fridge compartment (Phase 2)
- [ ] Design electronics tray (ESP32, BMS, power dist)
- [ ] Design cable routing channels
- [ ] Create 3D-printable segment plan (EA-11 segmentation strategy)
- [ ] Add heat-set insert hole locations (4.2mm for M3, verify with test print)
- [ ] Export STL files with correct orientation annotations
- [ ] Create assembly drawing with exploded views

### 3.2 3D Printing (After CAD complete)
- [ ] Print test block for heat-set insert hole sizing (4.2mm vs 4.8mm)
- [ ] Print test block for TPU interference fit (0.2, 0.3, 0.4mm)
- [ ] Print Phase 1 chassis segments (~65hr print time per EA-08)
- [ ] Print wheel hubs (6x) and TPU tyres (6x)
- [ ] Print rocker and bogie arms
- [ ] Print steering knuckles (4x)
- [ ] Print motor mounts (6x)
- [ ] Print differential bar
- [ ] Print electronics tray
- [ ] Print mast parts
- [ ] Post-processing: sand, clean, verify fits
- [ ] Install heat-set inserts (soldering iron, 200°C for PETG)

---

## 4. ELECTRONICS & WIRING (After CAD/print, before firmware testing)

### 4.1 Phase 1 Component Procurement
- [x] Create Phase 1 shopping list with specific UK supplier links (see `docs/plans/phase1-shopping-list.md`)
  - [ ] ESP32-S3 DevKitC-1 N16R8
  - [ ] L298N motor drivers (x2, for 4 motor channels + 2 spare)
  - [ ] N20 or Chihai 12V DC gear motors (x6)
  - [ ] MG996R steering servos (x4)
  - [ ] Hall effect encoders (x6, or motors with built-in encoders)
  - [ ] BNO055 IMU breakout
  - [ ] HC-SR04 ultrasonic sensors (x6)
  - [ ] 3S LiPo battery (for Phase 1 testing)
  - [ ] LM2596 buck converters (12V→5V, 12V→3.3V)
  - [ ] 608ZZ bearings (x10+)
  - [ ] M3 heat-set inserts (CNC Kitchen style, 100-pack)
  - [ ] M3 screws assorted (M3x8, M3x12, M3x16, M3x20)
  - [ ] JST connectors (for modular wiring)
  - [ ] Wire (22AWG signal, 18AWG power)
  - [ ] E-stop mushroom button (normally closed)
  - [ ] Kill switch for battery
  - [ ] PETG filament (2-3 spools, 1kg each)
  - [ ] TPU filament (1 spool for tyres)

### 4.2 Electronics Assembly
- [ ] Create wiring harness diagram (from EA-09 GPIO pinmap)
- [ ] Solder/connect ESP32-S3 development breadboard
- [ ] Wire motor drivers (L298N, power + signal)
- [ ] Wire steering servos (signal + 5V power bus)
- [ ] Wire encoder sensors (interrupt pins)
- [ ] Wire IMU (I2C SDA/SCL + power)
- [ ] Wire ultrasonic sensors (trigger/echo pins)
- [ ] Wire battery monitoring (voltage divider)
- [ ] Wire E-stop circuit (breaks motor power, signals ESP32)
- [ ] Wire power distribution (battery → BMS → buck converters → rails)
- [ ] Cable management and labelling
- [ ] Bench test all electronics before installing in chassis

---

## 5. PHASE 1 BUILD & TEST (Physical assembly + initial testing)

### 5.1 Mechanical Assembly
- [ ] Assemble rocker-bogie suspension to chassis
- [ ] Install 608ZZ bearings at all pivot points
- [ ] Attach differential bar
- [ ] Install steering knuckles and servos
- [ ] Mount motors to motor mounts
- [ ] Attach wheels and TPU tyres
- [ ] Install electronics tray in chassis
- [ ] Route all cables through channels
- [ ] Verify wheel clearance and steering range of motion
- [ ] Check centre of gravity (should be low and centred)

### 5.2 Firmware Bring-Up (on bench, before full assembly)
- [ ] Flash ESP32-S3 with Phase 1 firmware
- [ ] Verify UART communication (NMEA messages over serial monitor)
- [ ] Test individual motor control (forward/reverse each motor)
- [ ] Test steering servos (full range, centre calibration)
- [ ] Test encoder reading (spin wheels by hand, verify counts)
- [ ] Test IMU orientation (tilt in each axis, verify data)
- [ ] Test ultrasonic sensors (hand in front of each, verify distance)
- [ ] Test battery voltage reading
- [ ] Test E-stop (hardware and software)
- [ ] Test watchdog timeout (disconnect UART, verify motors stop)

### 5.3 Integration Testing
- [ ] Drive straight line test (encoder-based distance verification)
- [ ] Ackermann turn test (verify inner/outer wheel angle differential)
- [ ] Point turn test (front/rear opposite)
- [ ] Crab walk test (all wheels same angle)
- [ ] Obstacle detection test (ultrasonics → emergency stop)
- [ ] Slope test (30° incline, verify torque is sufficient)
- [ ] Battery runtime test (continuous driving, log voltage over time)
- [ ] Terrain test: grass, gravel, pavement, mixed
- [ ] Suspension articulation test (one wheel on obstacle, verify body stays level)

---

## 6. PHASE 2 — JETSON + FULL AUTONOMY (After Phase 1 validated)

### 6.1 Jetson Orin Nano Super Setup
- [ ] Flash JetPack 6.x
- [ ] Install ROS2 Humble (or Jazzy)
- [ ] Build rover workspace (`colcon build` all 7 packages)
- [ ] Configure UART connection to ESP32 (/dev/ttyTHS1)
- [ ] Test `ros2 launch rover_bringup hardware.launch.py`

### 6.2 Sensor Integration
- [ ] Mount and configure RPLidar A1 (USB, test with `ros2 launch rplidar_ros rplidar.launch.py`)
- [ ] Mount and configure OAK-D Lite (DepthAI + ROS2 driver)
- [ ] Mount and configure USB cameras (udev rules for persistent names)
- [ ] Mount and configure GPS module (u-blox M8N/M9N, NMEA → ROS2)
- [ ] Calibrate cameras (checkerboard calibration → update camera_params.yaml)
- [ ] Verify TF tree (`ros2 run tf2_tools view_frames`)

### 6.3 Navigation Stack
- [ ] Test SLAM (slam_toolbox online_async, drive around garden, save map)
- [ ] Test localization (load saved map, verify position)
- [ ] Test Nav2 path planning (send goal via rviz2 or foxglove)
- [ ] Test obstacle avoidance (place obstacle, verify replanning)
- [ ] Tune RegulatedPurePursuit parameters (lookahead, velocities)
- [ ] Tune costmap parameters (inflation radius, obstacle clearing)
- [ ] Test geofence boundary (drive toward edge, verify warning/stop)
- [ ] Test waypoint following (GPS waypoints in garden)

### 6.4 Perception
- [ ] Export YOLOv8n to TensorRT FP16 engine
- [ ] Test object detection (people, animals, obstacles)
- [ ] Integrate detections into costmap
- [ ] Test depth estimation from OAK-D stereo
- [ ] Verify detection → obstacle avoidance pipeline end-to-end

### 6.5 Autonomy
- [x] Create BT.CPP v4 behaviour tree XML missions (patrol, explore, return_home, safety_subtree)
- [ ] Test patrol mission (predefined waypoints, loop)
- [ ] Test explore mission (frontier exploration)
- [ ] Test return-to-home on low battery
- [ ] Test behaviour tree safety pre-emption
- [ ] Test PWA remote control via WebSocket

### 6.6 Binary UART Upgrade (EA-18)
- [x] Implement COBS framing on ESP32-S3 (uart_binary.h, gated by PHASE2_BINARY_PROTOCOL)
- [x] Implement CRC-16/CCITT on both ends
- [x] Switch baud rate to 460800
- [x] Implement packed struct message encoding
- [ ] Verify with loopback test
- [ ] Switch `#define PHASE2_BINARY_PROTOCOL` compile flag
- [ ] Benchmark: measure actual latency and bandwidth utilisation

### 6.7 Phase 2 Mechanical Upgrades
- [ ] Reprint chassis at 1.0 scale in PETG/ASA
- [ ] Apply carbon fiber strip reinforcement to rocker/bogie arms
- [ ] Apply UV protection (sand → primer → paint → clear coat)
- [ ] Install weatherproofing (IP44/IP54 seals per EA-14)
- [ ] Install solar panels + MPPT controller
- [ ] Install 6S LiPo pack with BMS
- [ ] Build and install robotic arms
- [ ] Build and install camera mast (pan/tilt)
- [ ] Install mini fridge compartment

---

## 7. PHASE 3 — METAL CHASSIS (Long-term)

- [ ] Design metal chassis (aluminium extrusion or sheet metal)
- [ ] Machine/order metal rocker and bogie arms
- [ ] Upgrade bearings (sealed for outdoor use)
- [ ] Upgrade motors (larger, sealed, with metal gearboxes)
- [ ] Add suspension springs/dampers
- [ ] Full weatherproofing to IP55+
- [ ] Glass coffee table surface
- [ ] Professional wiring harness

---

## 8. PWA APP ENHANCEMENTS (Can do anytime)

- [x] Implement real-time telemetry dashboard (battery, speed, heading, GPS, IMU, uptime)
- [x] Implement live camera streaming (MJPEG from Jetson web_server_node, source selector, snapshot)
- [x] Implement interactive map (Leaflet.js, rover position, geofence circle, waypoints, trail)
- [x] Implement gamepad input support (Gamepad API, controller mapping, speed modes)
- [x] Implement D-pad touch control for manual driving (in PWA and ESP32 embedded web UI)
- [x] Implement mission planner UI (patrol/explore/return home, status indicator)
- [x] Implement settings page (speed limit, sensitivity, steering mode, geofence, servo trim)
- [x] Implement firmware update trigger (OTA from PWA via Jetson, progress bar, restart button)
- [x] Implement diagnostic log viewer (color-coded, 200 entries, auto-scroll)
- [x] Add PWA install prompt and offline indicator
- [x] Dark/light theme toggle (Catppuccin Mocha ↔ Latte, saved to localStorage)

---

## 9. TESTING & QUALITY (Ongoing)

- [x] Write ROS2 unit tests for each Python node (pytest: Ackermann, geofence, waypoints, camera, mission)
- [x] Write ESP32 firmware unit tests (42 pytest tests: NMEA, Ackermann, battery, COBS, CRC-16)
- [x] Create simulation test suite (21 Gazebo scenarios: mobility, sensors, nav, terrain, safety)
- [x] Create integration test: UART bridge round-trip (30 tests: NMEA codec, commands, odometry, streams)
- [ ] Create integration test: full Nav2 stack in simulation
- [x] Set up CI/CD for ROS2 packages (GitHub Actions: ESP32 compile, ROS2 build, lint, docs check)
- [ ] Performance benchmarks: YOLO FPS, EKF update rate, UART throughput

---

## 10. PROJECT MANAGEMENT

- [x] Complete all 21 engineering analyses (EA-00 through EA-21)
- [x] Create Phase 1 firmware skeleton (all modules implemented)
- [x] Create ROS2 package scaffolding (all 10 nodes implemented)
- [x] Create PWA app
- [x] Research: 3D printing materials, ROS2 architecture, binary protocols
- [x] Create project README.md
- [x] Create Phase 1 shopping list (`docs/plans/phase1-shopping-list.md`)
- [x] Fix nav2_params.yaml (RegulatedPurePursuit, DUBIN, no spin)
- [x] Fix ekf.yaml (dual EKF + navsat_transform)
- [x] Fix launch files (hardware, nav, simulation)
- [x] Enable Gazebo plugins in URDF
- [x] Complete uart_bridge_node.cpp (IMU, USS, odometry)
- [x] Back up project to C: and E: drives (periodic)
- [x] Consolidate reference docs' best findings into EAs (EA-04: TensorRT export, EA-09: I2C expander strategy, EA-11: insert sizing + UV protection, EA-13: dual EKF + udev + use_sim_time)
- [x] Update CLAUDE.md when significant changes happen
- [ ] Maintain this todo list as work progresses

---

## Priority Order (Recommended)

1. ~~**Now (no hardware)**: Documentation fixes, config corrections, firmware implementation, simulation setup~~ **DONE**
2. **When back from holiday**: Fusion 360 CAD design, 3D print test blocks, order Phase 1 parts (see shopping list)
3. **After parts arrive**: 3D printing (~65hr), electronics bench test
4. **After print + electronics**: Phase 1 mechanical assembly, firmware bring-up on real hardware
5. **After Phase 1 works**: Jetson setup, sensor integration, Nav2 tuning
6. **After navigation works**: YOLO, autonomy, binary protocol, PWA telemetry
7. **Phase 2**: Full-scale reprint, reinforcement, solar, arms, mast, fridge
8. **Phase 3**: Metal chassis (long-term)

---

*Total items: ~180+ tasks across 10 categories*
*Software/documentation tasks: ~90% complete (all scaffolded, awaiting hardware validation)*
*Next physical milestone: CAD design in Fusion 360 + order Phase 1 components*
