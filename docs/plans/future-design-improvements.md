# Future Design Improvements — Phase 2 Planning

**Version**: 1.0
**Date**: 2026-03-23
**Purpose**: Capture all design ideas, lessons learned from Phase 1 prototype, and improvement plans for Phase 2 (full-scale, outdoor-capable rover).

## How to Use This Document
After completing Phase 1, fill in the "Phase 1 Outcome" column for each item based on actual testing data (see prototype-data-capture.md). This transforms assumptions into engineering decisions.

---

## 1. Chassis & Structure

| Aspect | Phase 1 | Phase 2 Plan | Phase 1 Outcome (fill after testing) |
|--------|---------|-------------|--------------------------------------|
| Material | PLA (indoor only) | PETG/ASA primary, aluminium extrusion frame | Was PLA strong enough? Where did it fail? |
| Body construction | 4 quadrants, bolted | 2 halves or 4 quadrants on alu frame | Was 4-quadrant join rigid enough? |
| Wall thickness | 4mm | TBD based on Phase 1 | Any flex or cracking? |
| Scale | 0.4× (440×260mm) | 1.0× (1100×650mm) | Did 0.4 scale compromise anything? |
| Panel lines/aesthetics | Grooves + chamfers | Proper Mars rover styling, paint | Did panel lines print well? |
| Weatherproofing | None (indoor) | IP44 minimum (EA-14) | N/A for Phase 1 |

## 2. Suspension

| Aspect | Phase 1 | Phase 2 Plan | Phase 1 Outcome |
|--------|---------|-------------|-----------------|
| Bearings | 608ZZ press-fit in PLA | 608ZZ in aluminium housings | Did bearings stay seated? Play after use? |
| Bogie arms | PLA solid, 180mm | Alu tube or printed PETG, 450mm | Any flex under load? |
| Rocker arms | PLA 2-piece, 200mm total | Alu or printed PETG, 500mm | Adequate stiffness? |
| Diff bar | 8mm steel rod, 300mm | Proper diff mechanism or longer rod | Rod straight? Any binding? |
| Articulation | Passive, no damping | Consider torsion springs or dampers | Too much bounce? Stability issues? |

## 3. Drivetrain

| Aspect | Phase 1 | Phase 2 Plan | Phase 1 Outcome |
|--------|---------|-------------|-----------------|
| Motors | N20 100RPM (6×) | Chihai 37mm 80RPM (6×) | Enough torque? Too noisy? Heat? |
| Drivers | L298N (2×) | Cytron MDD10A (3×, one per motor pair) | Voltage drop acceptable? 3.3V logic work? |
| Wheels | 80mm PLA, D-flat + grub screw | Larger wheels, proper hub with keyway | Grub screw hold? Wheel slip on shaft? |
| Tires | PLA grousers or TPU tire | Proper rubber tires | Traction adequate? |
| Encoders | None (Phase 1) | Magnetic encoders on each motor | Was odometry needed for testing? |

## 4. Steering

| Aspect | Phase 1 | Phase 2 Plan | Phase 1 Outcome |
|--------|---------|-------------|-----------------|
| Servos | SG90 (4×) | MG996R (4×) | Precision adequate? Jitter? Lifespan? |
| Linkage | Direct horn-to-bracket | Proper linkage with ball joints | Any slop in steering? |
| Calibration | Firmware trim values | Auto-calibration routine | How much trim was needed? |
| Ackermann | Software approximation | True Ackermann linkage geometry | Was software Ackermann good enough? |

## 5. Power System

| Aspect | Phase 1 | Phase 2 Plan | Phase 1 Outcome |
|--------|---------|-------------|-----------------|
| Battery | 2S 2200mAh (16.3Wh) | 6S 20Ah (444Wh) | Runtime achieved? |
| Charging | Remove battery, external charger | Onboard BMS + charging port | Was removal convenient? |
| BEC | XL4015 5V 3A | Integrated power distribution board | BEC reliable? Heat issues? |
| Solar | None | 100W panel on top deck | N/A |
| Fuse | 5A blade | 5A + per-motor poly fuses | Did fuse ever blow? |
| Monitoring | ADC voltage only | Current sensing + fuel gauge IC | Was voltage monitoring sufficient? |

## 6. Electronics & Compute

| Aspect | Phase 1 | Phase 2 Plan | Phase 1 Outcome |
|--------|---------|-------------|-----------------|
| Controller | ESP32-S3 only | ESP32-S3 + Jetson Orin Nano | Was ESP32 adequate for Phase 1 tasks? |
| Communication | WiFi WebSocket | WiFi + UART to Jetson (EA-12/EA-18) | WiFi range/reliability? |
| Sensors | Battery ADC only | LIDAR, cameras, IMU, GPS, encoders | N/A |
| Electronics tray | PLA tray, M2.5 standoffs | Proper PCB mounting, aluminium tray | Was tray layout effective? |
| Wiring | JST connectors, hand-crimped | Proper wire harness, cable chains | Were JST connectors reliable? |

## 7. Robotic Arm (New for Phase 2)

See EA-24 for detailed feasibility study.

| Aspect | Phase 2 Plan | Notes |
|--------|-------------|-------|
| DOF | 3 (shoulder pitch, elbow pitch, wrist roll) | |
| Servos | 2× MG996R + 1× SG90 | Via PCA9685 I2C driver |
| Reach | ~375mm (full scale) | |
| End effector | Camera mount initially, gripper later | |
| Mount | 4× M3 bolts to Phase 1 front mount pattern | Verify mount holds during Phase 1 |

## 8. Software & Autonomy

| Aspect | Phase 1 | Phase 2 Plan | Phase 1 Outcome |
|--------|---------|-------------|-----------------|
| Control | WiFi PWA direct | ROS2 Nav2 autonomous + PWA teleop | Was PWA control responsive? |
| Navigation | Manual only | SLAM + waypoint following | N/A |
| Vision | None | YOLO object detection, depth camera | N/A |
| Behaviour | Drive commands only | Behaviour trees (patrol, explore, return) | N/A |

## 9. Cameras & Sensors (Phase 2)

| Sensor | Purpose | Mount Location | Phase 1 Prep |
|--------|---------|---------------|-------------|
| Front camera | Driving/navigation | Front body wall | Headlight holes could hold camera |
| Rear camera | Reverse driving | Rear body wall | Taillight holes |
| Mast camera | Overview/inspection | Mast on RL top deck | Mast mount bosses installed |
| Depth camera | Obstacle avoidance | Front, beside camera | N/A |
| RPLidar A1 | 360° SLAM | Top deck centre | N/A |
| BNO055 IMU | Orientation | Electronics tray | N/A |
| GPS module | Outdoor positioning | Top deck (sky view) | N/A |

## 10. Aesthetic & Cosmetic (Phase 2)

| Feature | Phase 1 | Phase 2 Plan |
|---------|---------|-------------|
| Paint | None (raw PLA) | Mars rover gold/silver spray paint |
| Decals | None | NASA-style mission patches, "JPL" markings |
| Antenna | 15mm cosmetic nub | Functional WiFi antenna + cosmetic dish |
| RTG detail | 2× small raised pads | Detailed MMRTG replica (cosmetic) |
| MLI edges | 0.5mm ridges | Actual gold/silver foil trim pieces |
| Mast | Mount points only | Full camera mast with pan/tilt |
| Wheels | Straight treads | Custom tread pattern (Morse code message?) |

## 11. Manufacturing Improvements

| Aspect | Phase 1 Learning | Phase 2 Plan |
|--------|-----------------|-------------|
| Printer | CTC Bizer (225×145mm, PLA) | Upgrade to PETG/ASA-capable printer |
| Print time | ~69 hours estimated | Optimise with larger nozzle, thicker layers for non-visible parts |
| Post-processing | Sand + heat-set inserts | Vapour smoothing (ASA), paint, assembly jigs |
| Quality control | Caliper measurements | Go/no-go gauges for critical fits |
| Fasteners | M3 + M2 + heat-set inserts | Standardise on fewer fastener sizes |

## 12. Budget & Timeline

| Phase | Budget | Timeline | Status |
|-------|--------|----------|--------|
| Phase 1 | £102 | ~2 weeks print + 1 week assembly | In progress |
| Phase 2 | £1,631 | ~2 months | Planning |
| Phase 3 | £299 additional | ~1 month | Future |

## 13. Key Questions to Answer from Phase 1

These must be answered before finalising Phase 2 design:

1. Is PLA adequate for any outdoor components, or must everything be PETG/ASA?
2. Does the rocker-bogie geometry work at 0.4 scale, or are there scaling issues?
3. Are N20 motors sufficient for indoor use, or should Phase 2 budget for all new motors?
4. Is the L298N driver acceptable, or should Phase 2 use Cytron from the start?
5. How much runtime do we actually get vs the 88-minute theoretical?
6. Is the 4-quadrant body design worth keeping, or should Phase 2 use 2 halves?
7. How well do press-fit 608ZZ bearings hold in printed parts over time?
8. Is the electronics tray layout practical for wiring and maintenance?
9. What's the actual WiFi range outdoors?
10. How much does the prototype actually weigh vs the 1.25kg estimate?

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-23 | Initial template, pre-Phase 1 build |
