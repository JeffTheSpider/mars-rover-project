# Mars Rover Garden Robot

A Mars rover-inspired outdoor robot designed for garden and park use. Features NASA-style rocker-bogie suspension, 4-wheel Ackermann steering, AI-powered autonomous navigation, and phone-based WebSocket control.

**Current status:** Phase 1 design complete. 23 print-ready STL files exported. Firmware compiles. Ready to print and build.

![Phase](https://img.shields.io/badge/Phase_1-0.4_Scale_Prototype-blue)
![Parts](https://img.shields.io/badge/Parts-23_types_(79_pieces)-green)
![Print Time](https://img.shields.io/badge/Print_Time-~40_hours-orange)
![Budget](https://img.shields.io/badge/Budget-~%24102-brightgreen)

---

## What Is This?

A 440x260mm (0.4 scale) 3D-printed Mars rover prototype with:
- **6 wheels** with individual N20 motors
- **4-wheel steering** (Ackermann geometry, point turn, crab walk)
- **Rocker-bogie suspension** using 9x 608ZZ bearings and 8mm steel rods
- **ESP32-S3** brain with WiFi control from a phone app
- **Phone PWA** for driving, camera view, telemetry, and mission planning

Phase 1 is a working proof-of-concept. Phase 2 adds a Jetson Orin Nano for autonomous navigation with ROS2.

---

## Quick Reference

| Spec | Value |
|------|-------|
| Size (Phase 1) | 440 x 260 x ~120 mm |
| Weight | ~1.25 kg |
| Power | 2S LiPo 2200 mAh (~30 min runtime) |
| Brain | ESP32-S3 DevKitC-1 N16R8 |
| Drive motors | 6x N20 100 RPM (3V-6V) |
| Steering servos | 4x SG90 micro servo |
| Motor drivers | 2x L298N dual H-bridge |
| Steering range | +/-35 degrees, min radius 397mm |
| Top speed | ~2 km/h |
| Budget | ~$102 (Phase 1 only) |
| Printer | CTC Bizer (225x145x150mm bed, PLA) |
| Print time | ~40 hours total (79 pieces from 23 part types) |

---

## How The Suspension Works

```
                    BODY (4 quadrants)
                         |
              +----------+-----------+
              |                      |
         Rocker L                Rocker R
         /       \               /       \
    Front L    Bogie L      Front R    Bogie R
                /    \                  /    \
          Middle L  Rear L       Middle R  Rear R
```

Each side has a **rocker** (front + bogie pivot) and a **bogie** (middle + rear). The two sides connect through a **differential bar** that passes through a central pivot, so when one side goes up, the other tilts down. This keeps all 6 wheels on the ground over obstacles up to 1 wheel diameter.

**Joints:** 608ZZ bearings at every pivot point (rocker, bogie, differential, steering).
**Arms:** 8mm steel rods press into printed connectors with M3 grub screws.

---

## 3D Printed Parts

23 unique part types, 79 total pieces. All designed in Fusion 360 with print-ready features (fillets, chamfers, rounded corners). All fit on a 225x145mm print bed.

### Part List

| # | Part | Size (mm) | Qty | Category | Purpose |
|---|------|-----------|-----|----------|---------|
| 1 | BearingTestPiece | 33x33x12 | 1 | Calibration | Test 608ZZ bearing press-fit |
| 2 | TubeSocketTest | 59x20x19 | 1 | Calibration | Test 8mm rod fit (3 bore variants) |
| 3 | RoverWheelV3 | 86x86x52 | 6 | Wheels | 80mm OD, 5 spokes, O-ring grooves |
| 4 | RoverTire | 86x86x44 | 6 | Wheels | TPU tire with 48 tread ribs |
| 5 | SteeringBracket | 35x30x30 | 4 | Steering | Upper steering pivot (608ZZ + hard stops) |
| 6 | SteeringKnuckle | 39x35x42 | 4 | Steering | Lower pivot + N20 motor pocket |
| 7 | SteeringHornLink | 28x8x5 | 4 | Steering | Connects SG90 horn to knuckle arm |
| 8 | ServoMount | 40x18x25 | 4 | Steering | SG90 servo pocket, bolts to connector |
| 9 | FixedWheelMount | 25x25x30 | 2 | Drivetrain | N20 mount for middle wheels (non-steered) |
| 10 | FrontWheelConnector | 35x30x30 | 4 | Suspension | Tube socket + steering + servo mounts |
| 11 | MiddleWheelConnector | 30x25x25 | 2 | Suspension | Tube socket + motor mount face |
| 12 | RockerHubConnector | 45x40x35 | 2 | Suspension | Diff bar + 2x tube sockets |
| 13 | BogiePivotConnector | 45x30x45 | 2 | Suspension | 608ZZ pivot + 3x angled tube sockets |
| 14 | DifferentialPivotHousing | 30x30x23 | 1 | Suspension | Central diff bearing + body mount |
| 15 | DifferentialLink | 20x85x6 | 2 | Suspension | Link between diff pivot and rocker hubs |
| 16 | CableClip | 11x16x5 | 12 | Suspension | Friction clip for wire routing on rods |
| 17 | BodyQuadrant | 131x226x120 | 4 | Body | Quarter of rover body shell |
| 18 | TopDeck | 133x223x10 | 4 | Body | Snap-on top panels with solar texture |
| 19 | ElectronicsTray | 120x180x18 | 1 | Body | ESP32 + L298N + LiPo mounting |
| 20 | BatteryTray | 94x42x23 | 1 | Body | 2S LiPo cradle with strap slots |
| 21 | StrainReliefClip | 18x10x12 | 10 | Accessories | Cable strain relief with snap tabs |
| 22 | FuseHolderBracket | 19x40x14 | 1 | Accessories | Inline fuse holder mount |
| 23 | SwitchMount | 30x30x5 | 1 | Accessories | Kill switch toggle mount |

### STL Files

All ready-to-slice STLs are in `3d-print/` organised by category:

```
3d-print/
  calibration/     BearingTestPiece.stl, TubeSocketTest.stl
  wheels/          RoverWheelV3.stl, RoverTire.stl
  steering/        SteeringBracket.stl, SteeringKnuckle.stl, SteeringHornLink.stl, ServoMount.stl
  drivetrain/      FixedWheelMount.stl
  suspension/      FrontWheelConnector.stl, MiddleWheelConnector.stl, RockerHubConnector.stl,
                   BogiePivotConnector.stl, DifferentialPivotHousing.stl, DifferentialLink.stl,
                   CableClip.stl
  body/            BodyQuadrant.stl, TopDeck.stl, ElectronicsTray.stl, BatteryTray.stl,
                   StrainReliefClip.stl, FuseHolderBracket.stl, SwitchMount.stl
  gcode/           (empty — for sliced gcode files)
  screenshots/     Multi-angle renders of each part
```

**Note:** BodyQuadrant and TopDeck each export as 4 variants (FL/FR/RL/RR) when run through the batch exporter in Fusion 360. The single STLs in the repo are the FL variant.

### Print Settings (PLA on CTC Bizer)

| Setting | Structural Parts | Body Panels | Small Parts |
|---------|-----------------|-------------|-------------|
| Layer height | 0.2mm | 0.2mm | 0.15mm |
| Infill | 60% | 40% | 80% |
| Perimeters | 5 | 4 | 4 |
| Support | No (designed to print flat) | No | No |
| Bed temp | 60C | 60C | 60C |
| Nozzle temp | 210C | 210C | 210C |

Print the calibration pieces first to validate bearing and tube socket fits before committing to the full print run.

---

## How It All Fits Together

### Steering Mechanism (4 corner wheels)

```
  Connector ---- 8mm rod ---- Rocker/Bogie
      |
  Steering Bracket (608ZZ bearing pivot)
      |
  Steering Knuckle (N20 motor pocket)
      |                    |
  Wheel (on N20 shaft)    Steering Arm
                              |
                          Horn Link
                              |
                          SG90 Servo (in Servo Mount)
```

The SG90 servo rotates a horn link that pushes/pulls the steering arm on the knuckle, turning it around the bearing in the bracket. The N20 motor sits inside the knuckle and directly drives the wheel. Hard stops limit rotation to +/-35 degrees.

### Middle Wheels (fixed, not steered)

```
  Middle Wheel Connector ---- 8mm rod ---- Bogie Pivot
      |
  Fixed Wheel Mount (N20 motor pocket)
      |
  Wheel (on N20 shaft)
```

### Hardware Interfaces

All mating parts use consistent hardware:
- **608ZZ bearings:** 22.15mm bore x 7.2mm deep (steering, bogie, diff pivots)
- **8mm tube sockets:** 8.2mm bore x 15mm deep + M3 grub screw
- **M3 heat-set inserts:** 4.8mm bore x 5.5mm deep (in connectors)
- **M3 through-holes:** 3.2mm clearance (in brackets and mounts)
- **N20 motor pockets:** 12.2 x 10.2 x 25mm with 4mm shaft exit
- **SG90 servo pockets:** 22.4 x 12.2 x 12mm

See [cad-dimensions-reference.md](docs/engineering/cad-dimensions-reference.md) for the full dimension table with every part.

---

## Electronics (Phase 1)

```
2S LiPo 2200mAh (7.4V)
    |
    +-- 20A blade fuse
    |
    +-- Kill switch (15mm toggle)
    |
    +-- L298N #1 (Left: FL, ML, RL motors)
    |
    +-- L298N #2 (Right: FR, MR, RR motors)
    |
    +-- ESP32-S3 DevKitC-1 (via 5V from L298N regulator)
    |
    +-- 4x SG90 servos (from ESP32 PWM pins)
```

The ESP32-S3 runs a WebSocket server. Connect with the phone PWA to drive.

See [EA-09: GPIO Pin Map](docs/engineering/09-esp32-gpio-pinmap.md) and [EA-19: Wiring](docs/engineering/19-phase1-wiring.md) for full wiring details.

---

## Repository Structure

```
Mars Rover Project/
  README.md                 <-- You are here
  CLAUDE.md                 # AI assistant project instructions

  docs/
    engineering/            # 31 engineering analyses (EA-00 to EA-30)
    plans/                  # Design doc, BOM, build guide, print strategy
    diagrams/               # 10 system diagrams (Mermaid -> SVG)
    references/             # Open-source rover research, component specs
    datasheets/             # Component datasheets

  cad/
    scripts/                # 44 Fusion 360 Python scripts
      rover_cad_helpers.py  #   Shared helper module (888 lines)
      generate_rover_params.py  # Parametric dimensions (0.4x and 1.0x)
      bearing_test_piece.py #   ... 23 part scripts
      batch_export_all.py   #   Exports all 23+ STLs in one run
      rover_assembly_v2.py  #   Full rover assembly visualisation
      ref_*.py              #   6 reference component models
    reference/              # Imported open-source CAD models
    fusion-mcp/             # Fusion 360 MCP server (AuraFriday)

  3d-print/                 # Print-ready STL files (23 types)
    calibration/            #   Test pieces
    wheels/                 #   Wheel + tire
    steering/               #   Bracket, knuckle, horn link, servo mount
    drivetrain/             #   Fixed wheel mount
    suspension/             #   7 connector/clip types
    body/                   #   Body, deck, trays, accessories
    screenshots/            #   Multi-angle part renders

  firmware/
    esp32/                  # ESP32-S3 Arduino firmware (v0.3.0)
      esp32.ino             #   Main loop, WiFi, watchdog
      config.h              #   Pin defs, geometry, timing constants
      motors.h              #   4ch L298N control + speed ramping
      steering.h            #   Ackermann / point turn / crab walk
      sensors.h             #   Battery ADC, encoders, E-stop
      rover_webserver.h     #   HTTP + WebSocket + embedded UI
      ota.h                 #   Over-the-air firmware updates
      uart_nmea.h           #   NMEA text protocol (Phase 1)
      uart_binary.h         #   COBS binary protocol (Phase 2)
      leds.h                #   5 LED status patterns
    tests/                  # 42 pytest firmware unit tests

  software/
    jetson/                 # ROS2 Humble packages (Phase 2)
      rover_bringup/        #   Launch files, config, URDF
      rover_hardware/       #   UART bridge (C++)
      rover_navigation/     #   Ackermann controller, waypoints, geofence
      rover_perception/     #   YOLO, cameras, depth
      rover_autonomy/       #   Behaviour trees
      rover_teleop/         #   WebSocket phone bridge
      rover_msgs/           #   Custom message types
    pwa/                    # Phone app (Catppuccin Mocha PWA)

  tools/                    # Utility scripts, MCP servers
```

---

## Key Documents for Understanding the Design

If you're new to this project, read these in order:

1. **[Master Design Document](docs/plans/2026-03-14-mars-rover-design.md)** -- The original design vision and spec
2. **[EA-08: Phase 1 Spec](docs/engineering/08-phase1-prototype-spec.md)** -- Exact dimensions, part list, print order
3. **[EA-25: Suspension Audit](docs/engineering/25-suspension-audit.md)** -- How the tube+connector suspension works
4. **[EA-27: Steering Design](docs/engineering/27-steering-system-design.md)** -- The 4-bar linkage steering mechanism
5. **[CAD Dimensions Reference](docs/engineering/cad-dimensions-reference.md)** -- Every part's exact dimensions and interfaces
6. **[EA-17: Build Guide](docs/engineering/17-phase1-build-guide.md)** -- Step-by-step build instructions (~14 days)
7. **[Phase 1 BOM](docs/plans/phase1-complete-bom.md)** -- Complete bill of materials (~$102)
8. **[Print Strategy](docs/plans/print-strategy.md)** -- Print order, settings, estimated times

---

## Engineering Analysis Documents

31 engineering analyses covering every aspect of the design:

| ID | Topic | What It Covers |
|----|-------|----------------|
| EA-00 | [Master Handbook](docs/engineering/00-master-handbook.md) | Index and cross-reference to all EAs |
| EA-01 | [Suspension](docs/engineering/01-suspension-analysis.md) | Rocker-bogie geometry, NASA scaling, bearing selection |
| EA-02 | [Drivetrain](docs/engineering/02-drivetrain-analysis.md) | Torque calculations, N20 vs Chihai, L298N vs Cytron |
| EA-03 | [Power](docs/engineering/03-power-system-analysis.md) | LiPo sizing, solar, BMS, wire gauge calculations |
| EA-04 | [Compute](docs/engineering/04-compute-sensors-analysis.md) | Jetson Orin Nano, cameras, LIDAR, GPS, IMU selection |
| EA-05 | [Weight](docs/engineering/05-weight-budget.md) | Per-component mass breakdown, centre of gravity |
| EA-06 | [Cost](docs/engineering/06-cost-breakdown.md) | Phase-by-phase BOM ($2,032 total) |
| EA-07 | [Open Source](docs/engineering/07-open-source-review.md) | Sawppy + JPL rover design comparison |
| EA-08 | [Phase 1 Spec](docs/engineering/08-phase1-prototype-spec.md) | All CAD dimensions, part list, print order |
| EA-09 | [GPIO Pins](docs/engineering/09-esp32-gpio-pinmap.md) | ESP32-S3 pin assignments (20 pins Phase 1) |
| EA-10 | [Steering](docs/engineering/10-ackermann-steering.md) | Ackermann geometry, 3 modes, servo mapping |
| EA-11 | [3D Printing](docs/engineering/11-3d-printing-strategy.md) | PLA settings, CTC Bizer, heat-set insert technique |
| EA-12 | [UART Protocol](docs/engineering/12-uart-protocol.md) | NMEA-style text protocol, 18 message types |
| EA-13 | [ROS2](docs/engineering/13-ros2-architecture.md) | Node graph, Nav2, SLAM, EKF, behaviour trees |
| EA-14 | [Weatherproofing](docs/engineering/14-weatherproofing.md) | IP44/IP54 zones, cable glands (Phase 2+) |
| EA-15 | [Safety](docs/engineering/15-safety-systems.md) | E-stop, fuses, watchdog, geofence |
| EA-16 | [PWA Design](docs/engineering/16-pwa-app-design.md) | Catppuccin Mocha phone app UI/UX |
| EA-17 | [Build Guide](docs/engineering/17-phase1-build-guide.md) | Step-by-step ~14 day build timeline |
| EA-18 | [Binary UART](docs/engineering/18-binary-uart-protocol.md) | COBS + CRC-16, 460800 baud (Phase 2) |
| EA-19 | [Wiring](docs/engineering/19-phase1-wiring.md) | Complete Phase 1 wiring diagram |
| EA-20 | [CAD Prep](docs/engineering/20-cad-preparation-guide.md) | Parametric dimensions, Fusion 360 setup |
| EA-21 | [Test Procedures](docs/engineering/21-test-procedures.md) | Acceptance criteria for all subsystems |
| EA-22 | [Requirements](docs/engineering/22-requirements-specification.md) | Formal FR/PR/DIM/ELEC requirements |
| EA-23 | [Wire Harness](docs/engineering/23-wire-harness.md) | 58-wire schedule, connectors, colour codes |
| EA-24 | [Robotic Arms](docs/engineering/24-robotic-arm-study.md) | Phase 2 arm feasibility study |
| EA-25 | [Suspension Audit](docs/engineering/25-suspension-audit.md) | Tube+connector redesign, 9 bearings |
| EA-26 | [Suspension Design](docs/engineering/26-suspension-design-package.md) | Differential mechanism, DOF map |
| EA-27 | [Steering Design](docs/engineering/27-steering-system-design.md) | Horn link 4-bar, hard stops, clearance |
| EA-28 | [Integration](docs/engineering/28-systems-integration.md) | 42 cross-domain interfaces, assembly DAG |
| EA-29 | [CAD Redesign](docs/engineering/EA-29-cad-redesign.md) | Print-ready parts, shared helpers, error log |
| EA-30 | [CAD Testing](docs/engineering/EA-30-cad-testing-plan.md) | Calibration prints, tolerance adjustment |

---

## CAD Scripts

All part geometry is generated by Python scripts running in Fusion 360 (Scripts and Add-Ins). The scripts use a shared helper library (`rover_cad_helpers.py`) for consistent hardware interfaces.

### Running a script in Fusion 360

1. Open Fusion 360
2. Press **Shift+S** (Scripts and Add-Ins)
3. Select the script name (PascalCase, e.g. "SteeringBracket")
4. Click **Run**
5. The part will be created in the active design

### Batch export all STLs

Run the `BatchExportAll` script in Fusion 360. It creates a new design for each part, runs the script, exports the STL, then closes the design. Takes about 5-10 minutes for all 23+ files.

### Script naming

| Source file | Fusion 360 folder |
|-------------|-------------------|
| `cad/scripts/steering_bracket.py` | `Scripts/SteeringBracket/SteeringBracket.py` |
| `cad/scripts/rover_wheel_v3.py` | `Scripts/RoverWheelV3/RoverWheelV3.py` |

Snake_case source files are deployed to PascalCase Fusion 360 script folders using the `/deploy-scripts` command.

---

## Firmware

ESP32-S3 firmware (Arduino framework). Compiles to 1045KB flash (79%), 53KB RAM (16%).

```bash
# Compile
arduino-cli compile --fqbn esp32:esp32:esp32s3 firmware/esp32/

# Upload (USB)
arduino-cli upload --fqbn esp32:esp32:esp32s3 -p COM3 firmware/esp32/
```

Features:
- 4-channel PWM motor control with speed ramping
- Ackermann steering with 3 modes (standard, point turn, crab walk)
- Arm-before-drive safety (must explicitly arm before motors will spin)
- Battery voltage monitoring with speed limiting at low voltage
- Motor stall detection
- WebSocket server with embedded Catppuccin Mocha UI
- OTA firmware updates
- 5 LED status patterns (idle, armed, driving, low battery, error)

---

## Phone App

Progressive Web App with Catppuccin Mocha dark theme. Connect via WebSocket to the ESP32-S3's IP address.

Features: D-pad driving, 3 steering modes, speed slider, E-stop button, battery telemetry, camera streams, OTA update trigger.

See `software/pwa/` and [EA-16: PWA Design](docs/engineering/16-pwa-app-design.md).

---

## Build Phases

### Phase 1 (Current) -- 0.4 Scale PLA Prototype (~$102)

3D printed PLA chassis at 40% scale. ESP32-S3 with 2x L298N motor drivers. Basic driving and phone control via WebSocket. 23 part types, 79 pieces, ~40 hours print time on CTC Bizer.

### Phase 2 -- Full Scale (~$1,631 additional)

Full-size PETG/ASA chassis with aluminium extrusion reinforcement. Adds Jetson Orin Nano Super for ROS2 autonomous navigation, LIDAR, stereo cameras, GPS, robotic arms, mini fridge, solar panels, and coffee table mode.

### Phase 3 -- Metal Chassis (~$299 additional)

Machined aluminium and steel replacing 3D printed structural components. IP54 weatherproofing for year-round outdoor operation.

---

## Phase 1 Shopping List

See [Phase 1 Complete BOM](docs/plans/phase1-complete-bom.md) for the full list. Key items:

| Item | Qty | Notes |
|------|-----|-------|
| ESP32-S3 DevKitC-1 N16R8 | 1 | Main controller |
| L298N motor driver | 2 | 3 motors each |
| N20 100RPM geared motor | 6 | 3V-6V, 3mm D-shaft |
| SG90 micro servo | 4 | Steering (corner wheels only) |
| 608ZZ bearings | 12 | 9 needed + 3 spares |
| 8mm steel rod (1m) | 2 | Cut to length for suspension arms |
| M3 heat-set inserts | ~40 | 4.8mm OD x 5.5mm |
| M3x8 bolts + nuts | ~30 | Assembly fasteners |
| M2x10 bolts + nyloc nuts | 8 | Steering horn links |
| 2S LiPo 2200mAh | 1 | 7.4V, XT60 connector |
| 20A blade fuse + holder | 1 | Main power protection |
| Toggle switch (15mm) | 1 | Kill switch |
| PLA filament | ~500g | White or grey |

---

## System Diagrams

10 rendered SVG diagrams in `docs/diagrams/`:

| Diagram | Description |
|---------|-------------|
| [system-architecture](docs/diagrams/ea28-system-architecture.svg) | High-level system block diagram |
| [mechanical-assembly](docs/diagrams/ea28-mechanical-assembly.svg) | Mechanical assembly hierarchy |
| [power-distribution](docs/diagrams/ea28-power-distribution.svg) | Power system routing |
| [signal-flow](docs/diagrams/ea28-signal-flow.svg) | Signal and data flow |
| [firmware-state](docs/diagrams/ea28-firmware-state.svg) | ESP32 firmware state machine |
| [assembly-dag](docs/diagrams/ea28-assembly-dag.svg) | Assembly dependency graph |
| [cable-routing-map](docs/diagrams/cable-routing-map.svg) | Physical cable routing paths |
| [electronics-tray-layout](docs/diagrams/electronics-tray-layout.svg) | Electronics tray component layout |

---

## Next Steps

1. Set up CTC Bizer printer (hasn't been used in years -- needs calibration)
2. Print calibration pieces (BearingTestPiece, TubeSocketTest) to validate fits
3. Order Phase 1 components (see BOM)
4. Print all parts in dependency order (see [assembly-order](docs/plans/assembly-reference.md))
5. Assemble suspension, then steering, then body
6. Wire electronics, flash firmware, test

---

## License

Personal project. Not currently open source.
