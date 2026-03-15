# Engineering Analysis 21: Test Procedures & Acceptance Criteria

**Document**: EA-21
**Date**: 2026-03-15
**Purpose**: Define structured test procedures, pass/fail criteria, and acceptance thresholds for every subsystem of the Mars rover across all build phases. Follows a V-model approach from unit tests through system-level acceptance.
**Depends on**: EA-08 (Phase 1 Spec), EA-09 (GPIO), EA-10 (Steering), EA-12 (UART Protocol), EA-15 (Safety Systems), EA-17 (Build Guide), EA-19 (Wiring)

---

## 1. Test Philosophy

### 1.1 V-Model Testing Approach

The rover follows a V-model development lifecycle where each design stage has a corresponding test stage:

```
Requirements  ─────────────────────────────────────  Acceptance Tests
    │                                                       ▲
    ▼                                                       │
System Design  ────────────────────────────────  System Tests
    │                                                  ▲
    ▼                                                  │
Module Design  ──────────────────────  Integration Tests
    │                                        ▲
    ▼                                        │
Implementation  ──────────  Unit Tests
```

| V-Model Stage | EA Documents | Test Level |
|---------------|-------------|------------|
| Requirements | EA-01 to EA-06 | Acceptance tests (Section 5) |
| System design | EA-08, EA-10, EA-13 | System tests (Section 4) |
| Module design | EA-09, EA-12, EA-15, EA-19 | Integration tests (Section 3) |
| Implementation | Firmware, ROS2 nodes | Unit tests (Section 2) |

### 1.2 Pass/Fail Criteria Methodology

Every test has:
- **Test ID**: Unique identifier (UT-xxx for unit, IT-xxx for integration, ST-xxx for system, AT-xxx for acceptance)
- **Description**: What is being tested
- **Setup**: Hardware/software prerequisites
- **Procedure**: Numbered steps to execute
- **Expected result**: Observable outcome if the system is working correctly
- **Pass criteria**: Quantitative threshold that must be met
- **Fail action**: What to do if the test fails

A test **passes** only if ALL pass criteria are met. A partial pass is recorded as a fail with notes.

### 1.3 Test Equipment Required

| Equipment | Purpose | Estimated Cost |
|-----------|---------|---------------|
| Multimeter (with continuity beep) | Voltage, current, resistance, continuity checks | Already owned |
| Tape measure (5m) | Driving accuracy, turn radius measurement | Already owned |
| Stopwatch / phone timer | Timing e-stop response, battery runtime | Already owned |
| Spirit level | Body levelness over obstacles | Already owned |
| Protractor or angle finder | Steering angle verification | ~$5 |
| USB-UART adapter (CP2102 or FTDI) | UART loopback and protocol testing | ~$5 |
| Serial terminal software (minicom/PuTTY) | UART debugging and monitoring | Free |
| Oscilloscope (optional) | PWM verification, signal integrity | Nice-to-have |
| Wooden blocks (20mm, 40mm) | Suspension obstacle tests | Scrap wood |
| 5m straight line (tape on floor) | Straight-line accuracy test | Masking tape |
| Bench power supply (optional) | Isolated motor testing | Nice-to-have |
| Phone with browser | WebSocket control, PWA testing | Already owned |
| Computer with Arduino CLI | Firmware upload, serial monitor | Already owned |

---

## 2. Unit Tests

### 2.1 ESP32-S3 Firmware Tests

#### Motor Control Module

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| UT-M01 | Individual motor forward | Single motor connected to L298N OUT1/OUT2, ESP32 powered, wheels off ground | 1. Upload motor test sketch. 2. Command motor W1 forward at 50% PWM. 3. Observe wheel rotation. | Wheel spins in the designated forward direction at moderate speed. | Wheel rotates forward continuously for 5 seconds without stall or reversal. |
| UT-M02 | Individual motor reverse | Same as UT-M01 | 1. Command motor W1 reverse at 50% PWM. 2. Observe wheel rotation. | Wheel spins in reverse direction. | Wheel rotates reverse continuously for 5 seconds. Direction is opposite to UT-M01. |
| UT-M03 | Motor speed ramp | Same as UT-M01, serial monitor open | 1. Command motor from 0% to 100% over 200ms. 2. Monitor PWM output on serial. | Motor accelerates gradually, no instant jump. | PWM increments by no more than RAMP_RATE (10) per 20ms tick. Serial output confirms ramp profile. |
| UT-M04 | Motor brake (coast) | Same as UT-M01 | 1. Spin motor at 50%. 2. Command IN1=LOW, IN2=LOW. 3. Try to spin wheel by hand. | Wheel decelerates and spins freely. | Wheel can be turned by hand with minimal resistance after 2 seconds. |
| UT-M05 | Motor brake (active) | Same as UT-M01 | 1. Spin motor at 50%. 2. Command IN1=HIGH, IN2=HIGH. 3. Try to spin wheel by hand. | Wheel stops and resists turning. | Wheel cannot be easily turned by hand (motor terminals shorted). |
| UT-M06 | PWM resolution | Same as UT-M01, multimeter on motor leads | 1. Set PWM to 25%, measure average voltage. 2. Set to 50%, measure. 3. Set to 75%, measure. 4. Set to 100%, measure. | Voltage scales proportionally with PWM duty cycle. | Measured voltage within 15% of theoretical (duty% x supply voltage, accounting for L298N drop). |
| UT-M07 | Parallel motor pair | W2+W3 wired in parallel to L298N OUT3/OUT4 | 1. Command left mid+rear forward at 50%. 2. Observe both wheels. | Both W2 and W3 spin in the same direction at similar speed. | Both wheels spin forward, neither stalls. |
| UT-M08 | Motor free-spin current | Ammeter in series with one motor output | 1. Command motor at 100% PWM, no load. 2. Read current. | Low current draw (motor spinning freely). | Current draw < 0.2A per motor at no load. |

#### Steering Module

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| UT-S01 | Servo centre position | Single SG90 connected to ESP32, horn attached loosely | 1. Send 1500us pulse to servo. 2. Measure horn angle with protractor. | Servo moves to mechanical centre position. | Horn within 5 degrees of straight-ahead position. |
| UT-S02 | Servo sweep range | Same as UT-S01 | 1. Sweep from 500us to 2400us in 100us steps. 2. Observe range of motion. 3. Listen for grinding at extremes. | Servo sweeps approximately 180 degrees without mechanical binding. | Full range of motion achieved. No grinding or stalling at endpoints. |
| UT-S03 | Ackermann angle calculation | Serial monitor open, no hardware needed | 1. Command a turn with radius = 500mm (Phase 1 scale). 2. Read calculated FL, FR, RL, RR angles from serial. | Inner wheel angle is larger than outer wheel angle. Rear wheels are opposite sign to front. | Angles match EA-10 Section 5 worked examples within 1.0 degree. |
| UT-S04 | Servo trim adjustment | Servo mounted on steering bracket | 1. Set centre (1500us). 2. Observe if wheel is straight. 3. Apply trim offset. 4. Re-centre. | Trim offset corrects any mechanical misalignment. | After trim, wheel straight-ahead when centred. Deviation < 2 degrees. |
| UT-S05 | Steering mode switch | All 4 servos connected | 1. Switch from Ackermann to Point Turn mode. 2. Switch to Crab Walk mode. 3. Switch back to Ackermann. | Servos reconfigure to correct angles for each mode. | All 4 wheels reach correct positions within 500ms of mode change. No servo jitter on switch. |

#### Sensor Module

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| UT-SN01 | Battery ADC reading | Voltage divider on GPIO14, multimeter on battery | 1. Read ADC value. 2. Calculate battery voltage using scale factor (3.128). 3. Compare to multimeter reading. | ADC-derived voltage matches multimeter. | Within 5% of multimeter reading across the range 6.4V to 8.4V. |
| UT-SN02 | Battery voltage stages | Bench supply set to test voltages, or wait for discharge | 1. Set voltage to 7.0V (normal). Verify normal operation. 2. Set to 6.8V (warning). Verify warning. 3. Set to 6.4V (critical). Verify motor cutoff. | Three-stage battery protection activates at correct thresholds. | Warning triggers at 3.4-3.5V/cell (6.8-7.0V pack). Critical triggers at 3.2-3.4V/cell (6.4-6.8V pack). |
| UT-SN03 | Encoder pulse counting | Encoder W1 connected to GPIO38/39, serial monitor | 1. Slowly rotate wheel one full revolution by hand. 2. Read tick count from serial. | Tick count matches encoder specification (pulses per revolution). | Tick count within 5% of rated PPR per revolution. Count increments on forward rotation, decrements on reverse. |
| UT-SN04 | Encoder quadrature | Same as UT-SN03 | 1. Rotate wheel forward, record count direction. 2. Rotate wheel backward, record count direction. | Forward and reverse produce opposite count directions. | Forward: positive increment. Reverse: negative increment. No missed counts over 10 revolutions. |

#### E-Stop Module

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| UT-E01 | E-stop button detection | Tactile button on GPIO46, serial monitor | 1. Press E-stop button. 2. Read GPIO46 state on serial. 3. Release button. | GPIO reads HIGH when pressed (connected to 3.3V via internal pull-down). | GPIO46 transitions from LOW to HIGH on press, returns to LOW on release. No bounce (debounce in firmware). |
| UT-E02 | E-stop motor cutoff | Motors running at 50%, E-stop button ready | 1. Start all motors at 50% PWM. 2. Press E-stop button. 3. Observe motors. 4. Measure time from press to stop. | All motors immediately stop. | All motor PWM set to 0 within 20ms of button press. No motor movement after stop. |
| UT-E03 | E-stop persistence | Motors stopped by E-stop | 1. While in E-stop state, command motors via WebSocket. 2. Observe motors. | Motor commands are rejected while E-stop is active. | No motor movement occurs. WebSocket reports E-stop state. |
| UT-E04 | E-stop recovery | Rover in E-stop state | 1. Press E-stop button again to release. 2. Send resume command from phone app. 3. Command motors forward. | Rover returns to normal operation after explicit recovery. | Motors respond to commands only after BOTH button release AND resume command received. |

#### UART Module (Phase 2 preparation, testable with loopback)

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| UT-U01 | UART TX output | ESP32 TX (GPIO43) connected to USB-UART adapter RX, serial terminal on PC | 1. ESP32 sends `$PNG*19\n` every second. 2. Monitor on PC serial terminal. | Ping messages appear on PC terminal. | All messages received with correct format and checksum. 0% loss over 60 seconds. |
| UT-U02 | UART RX parsing | USB-UART adapter TX connected to ESP32 RX (GPIO44), serial terminal | 1. Type `$MOT,50,50,50,-50,-50,-50*7A\n` from PC terminal. 2. Observe ESP32 serial output for ACK. | ESP32 parses command and responds with ACK. | ESP32 prints parsed motor values matching input. Sends `$ACK,MOT*2A\n` back. |
| UT-U03 | Checksum validation | Same as UT-U02 | 1. Send message with correct checksum. 2. Send message with incorrect checksum (change one hex digit). | Correct message is processed. Incorrect message is rejected. | Valid message: ACK received. Invalid message: ERR code 1 (checksum mismatch) received. No motor action on bad checksum. |
| UT-U04 | UART timeout safety | USB-UART adapter connected, motors running | 1. Send MOT commands at 50Hz for 5 seconds. 2. Stop sending commands. 3. Wait 200ms. 4. Observe motors. | Motors stop after 200ms of no commands. | Motors reach 0% PWM within 250ms of last received command. ERR code 8 (command_timeout) sent. |

### 2.2 ROS2 Node Tests (pytest) — Phase 2

All ROS2 node tests use the pytest framework with `launch_testing` for integration, and direct function calls for unit testing.

#### ackermann_controller Node

| Test ID | Description | Mock Inputs | Expected Outputs | Pass Criteria |
|---------|-------------|------------|-----------------|---------------|
| UT-R01 | Forward straight | `Twist(linear.x=1.0, angular.z=0.0)` | WheelSpeeds: all 6 equal positive values. SteeringAngles: all 4 at 0.0 degrees. | All wheel speeds within 1% of each other. All steering angles within 0.5 degrees of zero. |
| UT-R02 | Reverse straight | `Twist(linear.x=-1.0, angular.z=0.0)` | WheelSpeeds: all 6 equal negative values. SteeringAngles: all 4 at 0.0. | All wheel speeds within 1% of each other (negative). Steering at zero. |
| UT-R03 | Ackermann left turn | `Twist(linear.x=1.0, angular.z=0.5)` | Inner (left) wheels slower than outer (right). FL angle > FR angle (magnitude). RL/RR opposite sign to FL/FR. | Angles match EA-10 Ackermann formula within 1.0 degree. Inner wheel speed < outer wheel speed. |
| UT-R04 | Ackermann right turn | `Twist(linear.x=1.0, angular.z=-0.5)` | Mirror of UT-R03. | Angles match EA-10 formula. Symmetrical to UT-R03. |
| UT-R05 | Point turn left | `Twist(linear.x=0.0, angular.z=1.0)` | Left wheels reverse, right wheels forward. All wheels angled towards centre of rover. | Left speed negative, right speed positive. Angles match point-turn geometry from EA-10. |
| UT-R06 | Zero velocity | `Twist(linear.x=0.0, angular.z=0.0)` | WheelSpeeds: all zero. SteeringAngles: hold previous or go to zero. | All speeds exactly 0. No oscillation. |
| UT-R07 | Speed clamping | `Twist(linear.x=10.0, angular.z=0.0)` (exceeds max) | WheelSpeeds: clamped to max allowed value. | No wheel speed exceeds 100% (the PWM maximum). |

#### uart_bridge Node

| Test ID | Description | Mock Inputs | Expected Outputs | Pass Criteria |
|---------|-------------|------------|-----------------|---------------|
| UT-R08 | Publish encoder data | Inject `$ENC,100,98,97,-102,-100,-99*XX\n` into mock serial | `/encoders` topic publishes JointState with 6 position values. | Published within 5ms of injection. Values match parsed data. |
| UT-R09 | Publish IMU data | Inject `$IMU,0.998,0.012,-0.005,0.001,0.15,-0.08,9.79*XX\n` | `/imu/data` topic publishes Imu message with quaternion and accel. | Quaternion normalised (magnitude within 0.001 of 1.0). Accel values match parsed data. |
| UT-R10 | Publish battery data | Inject `$BAT,7.42,1.23,85*XX\n` | `/battery` topic publishes BatteryState. | Voltage, current, percentage match parsed values. |
| UT-R11 | Subscribe cmd_vel | Publish `Twist(1.0, 0.0)` to `/cmd_vel` | Serial output contains `$MOT,...*XX\n` and `$STR,...*XX\n` | Messages appear on serial within one cycle (20ms). Checksums are valid. |
| UT-R12 | E-stop forwarding | Publish `Bool(True)` to `/estop` | Serial output contains `$STP*1C\n` | STP message sent within 5ms. Higher priority than queued MOT/STR. |

#### geofence_node

| Test ID | Description | Mock Inputs | Expected Outputs | Pass Criteria |
|---------|-------------|------------|-----------------|---------------|
| UT-R13 | Inside geofence | NavSatFix at centre of defined polygon | No estop published. No warning. | Node does not publish to `/estop`. |
| UT-R14 | Outside geofence | NavSatFix 10m outside polygon boundary | `/estop` topic publishes `Bool(True)`. Warning logged. | Estop published within 1 second of fix reception. |
| UT-R15 | Fence boundary edge | NavSatFix exactly on polygon edge | Behaviour depends on implementation (inside or outside). | Consistent behaviour. No crash or exception. |

### 2.3 UART Protocol Tests

These tests verify the protocol defined in EA-12 independently of rover hardware.

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| UT-P01 | Loopback test (ESP32) | ESP32 TX (GPIO43) jumpered to RX (GPIO44) | 1. ESP32 sends `$PNG*19\n`. 2. ESP32 reads its own message back. 3. Validate checksum. | Message received matches sent message. | 100% match over 1000 messages. Zero checksum failures. |
| UT-P02 | Loopback test (Jetson/PC) | USB-UART adapter with TX jumpered to RX | 1. Python script sends 100 messages per second. 2. Reads them back. 3. Validates checksums. | All messages received intact. | 100% match over 10,000 messages. |
| UT-P03 | Message format validation | Any serial connection | 1. Send 20 different message types. 2. For each: verify starts with `$`, ends with `\n`, has `*` before 2-char hex checksum. | All messages conform to format. | Every message matches regex `^\$[A-Z]{2,3}(,[^*]+)?\*[0-9A-F]{2}\n$` |
| UT-P04 | Checksum calculation | Software-only (unit test function) | 1. Calculate checksum for `$MOT,50,-50` (expected: `0x7A`). 2. Calculate for `$STP` (expected: `0x1C`). 3. Calculate for `$PNG` (expected: `0x19`). | All checksums match EA-12 examples. | 100% match for all test vectors. |
| UT-P05 | Throughput measurement | ESP32 connected to PC via USB-UART | 1. ESP32 sends ENC+IMU at 50Hz for 10 seconds. 2. PC counts received messages. 3. Calculate throughput in bytes/second. | Throughput matches EA-12 bandwidth analysis. | Measured throughput within 10% of theoretical (8,310 B/s). Message loss < 0.1%. |
| UT-P06 | Framing recovery | PC sends to ESP32 | 1. Send garbage bytes (0x00-0xFF random). 2. Immediately send valid `$PNG*19\n`. 3. Check ESP32 responds with PON. | ESP32 recovers from garbage and processes valid message. | Valid PON response received. No crash. Recovery within 2 message periods (40ms). |

---

## 3. Integration Tests

### 3.1 UART Round-Trip (Phase 2)

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| IT-01 | Jetson-ESP32 ping-pong | Jetson connected to ESP32 via 3-wire UART (TX, RX, GND) | 1. Jetson sends `$PNG*19\n`. 2. ESP32 responds with `$PON*08\n`. 3. Measure round-trip time. 4. Repeat 1000 times. | Consistent round-trip response. | Mean latency < 10ms. Max latency < 20ms. 0% message loss over 1000 exchanges. |
| IT-02 | Sustained bidirectional | Same as IT-01 | 1. Jetson sends MOT+STR at 50Hz. 2. ESP32 responds with ENC+IMU at 50Hz. 3. Run for 60 seconds. 4. Count sent vs received messages. | Both sides maintain 50Hz exchange. | Message loss < 0.5% in each direction. No buffer overflow. No checksum errors. |
| IT-03 | UART under WiFi load | Same as IT-01, plus WiFi active (ESP32 serving web page) | 1. Start web server on ESP32. 2. Connect phone to web UI. 3. Run IT-02 simultaneously. 4. Compare message loss to IT-02 baseline. | UART communication unaffected by WiFi activity. | Message loss increase < 1% compared to IT-02 baseline. |

### 3.2 Motor Control Loop

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| IT-10 | cmd_vel to wheel rotation | Full system: Jetson + ESP32 + motors + encoders. Wheels off ground. | 1. Publish `Twist(linear.x=0.5)` to `/cmd_vel`. 2. ackermann_controller converts to WheelSpeeds. 3. uart_bridge sends MOT command. 4. ESP32 drives motors. 5. Encoders report back. 6. Verify `/encoders` topic shows positive ticks. | Complete pipeline from ROS2 command to physical wheel movement and feedback. | Encoder ticks appear within 100ms of cmd_vel publish. Tick rate proportional to commanded speed (within 20%). |
| IT-11 | Speed proportionality | Same as IT-10 | 1. Command 25% speed, record encoder tick rate. 2. Command 50%, record. 3. Command 75%, record. 4. Command 100%, record. | Tick rate scales roughly linearly with commanded speed. | Linear correlation coefficient (R-squared) > 0.9 across the 4 data points. |
| IT-12 | Direction reversal | Same as IT-10 | 1. Command forward at 50% for 3 seconds. 2. Command reverse at 50% for 3 seconds. 3. Monitor encoder direction. | Encoder count direction reverses when motor direction reverses. | Encoder sign flips within 500ms of direction change. No encoder count stall during transition. |
| IT-13 | Emergency stop in loop | Same as IT-10, motors running | 1. Motors at 50%. 2. Press physical E-stop. 3. Monitor encoder output. 4. Monitor motor PWM. | Motors stop, encoder ticks drop to zero. | Motors reach 0 PWM within 20ms. Encoder tick rate drops to 0 within 200ms (wheel inertia). |

### 3.3 Sensor Pipeline (Phase 2)

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| IT-20 | IMU to EKF | BNO055 IMU connected, robot_localization running | 1. Place rover on flat surface. 2. Read `/odom` orientation. 3. Rotate rover 90 degrees by hand. 4. Read `/odom` orientation again. | Odometry orientation changes by approximately 90 degrees. | Measured rotation within 10 degrees of actual 90-degree turn. |
| IT-21 | Encoder to EKF | Encoders connected, robot_localization running | 1. Push rover forward 1 metre (measured). 2. Read `/odom` position change. | Odometry position increases by approximately 1 metre. | Reported distance within 10% of measured 1 metre. |
| IT-22 | TF tree completeness | Full sensor suite running | 1. Run `ros2 run tf2_tools view_frames`. 2. Examine output PDF. | Complete TF tree from `map` through `odom`, `base_link`, to all sensor frames. | All expected frames present. No broken links. No stale transforms (all updated within 1 second). |
| IT-23 | LIDAR to costmap | RPLidar running, Nav2 costmap active | 1. Place a box 500mm in front of rover. 2. View costmap in RViz. 3. Verify obstacle appears in costmap. | Obstacle is marked in the costmap at the correct relative position. | Obstacle position in costmap within 50mm of measured physical position. Obstacle appears within 2 seconds. |
| IT-24 | Obstacle avoidance response | LIDAR + Nav2 running, obstacle placed in path | 1. Send navigation goal beyond obstacle. 2. Observe rover behaviour. | Rover plans path around obstacle. | Rover does not collide with obstacle. Path deviates around it. Goal reached within 30 seconds. |

### 3.4 Navigation Stack (Phase 2, Gazebo Simulation)

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| IT-30 | Gazebo spawn and drive | Gazebo sim with rover URDF, teleop active | 1. Launch Gazebo with rover model. 2. Send cmd_vel forward. 3. Observe rover movement in sim. | Rover moves forward in simulation. | Rover translates in the correct direction. No physics explosion or model collapse. |
| IT-31 | Sim navigation goal | Gazebo + Nav2 + SLAM, empty world | 1. Create a map via SLAM (drive around). 2. Send a goal pose 3 metres away. 3. Wait for Nav2 to navigate. | Rover autonomously drives to goal. | Rover arrives within 300mm of goal position. Arrival within 60 seconds. No collisions. |
| IT-32 | SLAM map quality | Gazebo with walls/obstacles, SLAM running | 1. Drive rover around a known environment. 2. Save the SLAM map. 3. Compare to ground truth. | Map is geometrically accurate. | Wall positions within 100mm of ground truth. No phantom obstacles. Map covers > 90% of traversed area. |
| IT-33 | Localisation stability | Saved map loaded, AMCL running | 1. Load pre-built map. 2. Place rover at known location. 3. Drive around for 60 seconds. 4. Check localisation drift. | Rover stays localised on the map. | Position error < 200mm after 60 seconds of driving. No localisation jumps > 500mm. |

---

## 4. System Tests

### 4.1 Driving Tests

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| ST-D01 | Straight-line accuracy | 5m tape line on flat floor. Rover at one end. | 1. Command forward at 50% speed. 2. Drive 5 metres. 3. Measure lateral deviation from tape line at endpoint. | Rover arrives near the 5m mark without significant drift. | Lateral deviation < 200mm over 5 metres (< 4% drift). |
| ST-D02 | Straight-line accuracy (full speed) | Same as ST-D01 | 1. Command forward at 100% speed. 2. Drive 5 metres. 3. Measure lateral deviation. | Rover tracks reasonably straight at full speed. | Lateral deviation < 300mm over 5 metres. |
| ST-D03 | Turn radius verification | Open floor, measuring tape | 1. Command Ackermann turn at maximum steering angle. 2. Drive a full circle. 3. Measure the circle diameter. | Measured turn radius matches EA-10 calculated minimum. | Measured radius within 20% of EA-10 calculated minimum turn radius (~420mm for Phase 1 at 35 degrees). |
| ST-D04 | Point turn accuracy | Marker placed at rover centre on floor | 1. Command point turn at 30% speed. 2. Rotate 360 degrees. 3. Measure displacement of rover centre from starting marker. | Rover rotates roughly in place. | Centre displacement < 100mm after one full 360-degree rotation. |
| ST-D05 | Speed measurement | 2m measured course, stopwatch | 1. Command forward at 100% speed. 2. Time how long to travel 2 metres. 3. Calculate speed. | Speed matches expected maximum (approximately 2 km/h for Phase 1). | Measured speed within 30% of calculated maximum from EA-02 (gear ratio x motor RPM x wheel circumference). |
| ST-D06 | Low-speed control | Flat floor | 1. Command forward at 10% speed. 2. Observe movement. | Rover moves at very low speed without stalling. | Rover moves continuously for 5 seconds at 10% speed. No stalling or jerky motion. |
| ST-D07 | Steering mode transitions | Open floor, phone connected | 1. Drive forward in Ackermann mode. 2. Switch to Crab Walk while moving. 3. Switch to Point Turn. 4. Switch back to Ackermann. | Smooth transitions between steering modes. | No servo jitter, no sudden direction change, no motor interruption during mode switch. |

### 4.2 Suspension Tests

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| ST-SU01 | Single wheel obstacle | Place a 20mm block under one wheel | 1. Slowly drive over the block with one front wheel. 2. Observe body pitch/roll. 3. Check that all other wheels remain on the ground. | Rocker-bogie absorbs the obstacle. Body stays approximately level. | Body tilt < 5 degrees. All 5 other wheels maintain ground contact (visual check). |
| ST-SU02 | Larger single-wheel obstacle | Place a 40mm block under one wheel | 1. Slowly drive one wheel onto the block. 2. Observe rocker-bogie articulation. 3. Check for loss of ground contact on any wheel. | Suspension articulates to accommodate larger obstacle. | Body tilt < 10 degrees. At least 5 of 6 wheels maintain ground contact. |
| ST-SU03 | Diagonal obstacle | Place 40mm blocks under front-left and rear-right wheels simultaneously | 1. Place rover so FL and RR wheels are on blocks. 2. Observe body levelness. 3. Check remaining wheels for ground contact. | Differential bar distributes load. Body stays relatively level. | Body tilt < 10 degrees in both roll and pitch. At least 4 of 6 wheels maintain ground contact. |
| ST-SU04 | Maximum obstacle height | Progressively taller blocks (20mm, 30mm, 40mm, 50mm, 60mm) | 1. Drive one wheel onto each block height. 2. Note at which height the rover fails (high-centres, tips, or loses too many wheels). | Rover handles obstacles up to 40mm (50% wheel diameter). | Rover successfully traverses 40mm obstacle without tipping or losing drive traction on more than 1 wheel. |
| ST-SU05 | Continuous rough terrain | Scatter 5-6 objects (pens, small books, cables) on the floor | 1. Drive over the scattered objects at 30% speed for 1 minute. 2. Observe stability. | Rover navigates over small irregular obstacles without tipping or stalling. | Rover completes the course without stopping, tipping, or losing more than 1 wheel contact at any time. Wire routing undamaged. |
| ST-SU06 | Differential bar operation | Rover on flat surface | 1. Push down on left rocker arm. 2. Observe right rocker arm. | Right rocker lifts as left is pushed down (seesaw action). | Motion is smooth, no binding. Approximately 1:1 ratio (push 10mm down on one side, other side lifts approximately 10mm). |

### 4.3 Battery & Power Tests

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| ST-P01 | Runtime at cruising speed | Fully charged battery (8.4V). Timer. | 1. Drive rover at 50% speed continuously on flat floor. 2. Record time until low-battery warning triggers. | Battery lasts a reasonable duration at cruising speed. | Runtime > 15 minutes at continuous 50% speed. |
| ST-P02 | Runtime at max speed | Fully charged battery. Timer. | 1. Drive rover at 100% speed continuously. 2. Record time until low-battery warning. | Shorter runtime than cruising but still usable. | Runtime > 8 minutes at continuous 100% speed. |
| ST-P03 | Voltage monitoring accuracy | Multimeter on battery terminals, phone app showing voltage | 1. Read voltage on multimeter. 2. Read voltage displayed on phone app (from ADC). 3. Compare. 4. Repeat at 3 different charge levels. | ADC reading matches multimeter. | ADC-reported voltage within 5% of multimeter reading at all 3 charge levels. |
| ST-P04 | Low-battery warning | Partially discharged battery (or bench supply at 7.0V) | 1. Set battery voltage to warning threshold (3.4-3.5V/cell = 6.8-7.0V). 2. Observe LED, buzzer, phone notification. | Warning indicators activate. Speed reduced to 50%. | LED changes to amber. Phone app shows warning within 5 seconds. Max speed reduced. |
| ST-P05 | Low-battery shutdown | Battery near cutoff (or bench supply at 6.4V) | 1. Set battery voltage to critical threshold (3.2V/cell = 6.4V). 2. Observe motor cutoff. | Motors stop. LED red. Alarm sounds. | Motors stop within 2 seconds of reaching critical voltage. Rover refuses to drive until charged above 3.5V/cell. |
| ST-P06 | Power-on sequence | Battery connected, switch off | 1. Turn switch on. 2. Measure voltages at ESP32 VIN, L298N 5V output. 3. Observe ESP32 boot (serial monitor). | Clean power-up with correct voltages. | ESP32 VIN reads 4.8-5.2V. No brownout resets. Serial shows clean boot message within 5 seconds. |
| ST-P07 | No-load current draw | Ammeter in series with battery, rover idle (WiFi connected, no motor commands) | 1. Measure current with rover powered on, idle. | Idle current is low. | Total idle current < 200mA (ESP32 WiFi + L298N quiescent). |

### 4.4 Safety Tests

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| ST-SF01 | E-stop response time | Motors at 100% speed, phone recording video of wheels, E-stop ready | 1. While driving at full speed, press E-stop button. 2. Review video frame-by-frame to measure time from button press to wheel stop. | Motors stop almost instantly. | Response time < 50ms from button press to motor PWM at zero (measured via serial timestamp or video analysis at 60fps = 1 frame = 16ms). |
| ST-SF02 | WebSocket disconnect timeout | Phone controlling rover, motors at 30% | 1. Drive forward. 2. Turn off phone WiFi (simulating disconnect). 3. Measure time until rover stops. | Rover stops after losing WebSocket connection. | Motors stop within 2 seconds of WebSocket disconnect (per EA-15 Phase 1 timeout). |
| ST-SF03 | UART watchdog timeout (Phase 2) | Jetson sending commands, then Jetson process killed | 1. Kill the uart_bridge process on Jetson. 2. Measure time until ESP32 stops motors. | ESP32 detects command timeout and stops. | Motors stop within 250ms (200ms timeout + execution time). ERR code 8 sent on UART. |
| ST-SF04 | Watchdog timer recovery | ESP32 firmware with forced hang (test mode) | 1. Trigger firmware hang (e.g., infinite loop in test code). 2. Wait for watchdog. 3. Observe reboot. | ESP32 reboots after 5 seconds, motors default to off. | ESP32 reboots within 6 seconds. All GPIOs reset to safe state. Motors remain off until explicit arm command. |
| ST-SF05 | Speed ramp verification | Serial monitor, motor at 0% | 1. Command instant jump from 0% to 100%. 2. Monitor actual PWM output on serial (every 20ms tick). | PWM ramps up gradually, not jumping to 100%. | PWM increases by no more than 10 per 20ms tick (RAMP_RATE from EA-15). Time from 0 to 100% is approximately 200ms. |
| ST-SF06 | Stall detection (if encoders installed) | Block one wheel so it cannot rotate, command motor at 50% | 1. Block W1 wheel with hand. 2. Command W1 motor at 50%. 3. Wait 2 seconds. | ESP32 detects stall and stops motor. | Motor stopped within 3 seconds of stall condition. ERR code 3 (motor stall) reported. |
| ST-SF07 | Safe boot sequence | Power cycle ESP32 | 1. Power off. 2. Power on. 3. Observe serial output. 4. Check motor/servo state before arming. | ESP32 boots to safe state, awaiting arm command. | No motor movement before arm command. All servos at centre. Battery voltage checked. E-stop state verified. |

### 4.5 WiFi & Communication Tests (Phase 1)

| Test ID | Description | Setup | Procedure | Expected Result | Pass Criteria |
|---------|-------------|-------|-----------|-----------------|---------------|
| ST-W01 | WiFi connection time | ESP32 powered off, router on | 1. Power on ESP32. 2. Time how long until WiFi connected (serial monitor). | Connection within a few seconds. | WiFi connected within 10 seconds. IP address assigned. |
| ST-W02 | WebSocket latency | Phone connected to rover web UI | 1. Tap forward button. 2. Measure time until motor responds (video sync or serial timestamp). | Low latency control. | Command-to-motor latency < 100ms (WebSocket + ESP32 processing). |
| ST-W03 | WiFi range | Open outdoor area, phone connected | 1. Drive rover away from phone (or walk away). 2. Note distance at which control becomes unreliable. 3. Note distance at which connection drops. | Usable control range established. | Reliable control at 10m minimum. Connection maintained at 15m minimum. |
| ST-W04 | WiFi reconnection | Phone connected, WiFi operational | 1. Briefly power-cycle the router (or move rover out of range and back). 2. Observe rover behaviour during disconnect. 3. Check if WebSocket reconnects automatically. | Rover stops during disconnect, reconnects when WiFi returns. | Motors stop within 2 seconds of WiFi loss. WebSocket reconnects within 30 seconds of WiFi restoration. No manual intervention required. |

---

## 5. Acceptance Criteria Summary Table

### 5.1 Phase 1 Acceptance Criteria

All tests in this table must pass before Phase 1 is considered complete and Phase 2 design can begin.

| Test ID | Description | Target Value | Tolerance | Phase |
|---------|-------------|-------------|-----------|-------|
| ST-D01 | Straight-line accuracy (5m) | 0mm lateral deviation | < 200mm | 1 |
| ST-D03 | Minimum turn radius | EA-10 calculated value (~420mm) | Within 20% | 1 |
| ST-D04 | Point turn displacement | 0mm displacement | < 100mm per 360 degrees | 1 |
| ST-D05 | Maximum speed | ~2 km/h (Phase 1 target) | Within 30% | 1 |
| ST-SU01 | 20mm obstacle (single wheel) | Body level, all wheels grounded | Tilt < 5 degrees | 1 |
| ST-SU02 | 40mm obstacle (single wheel) | Body level, 5/6 wheels grounded | Tilt < 10 degrees | 1 |
| ST-SU04 | Maximum obstacle height | 40mm (50% wheel diameter) | Must clear 40mm | 1 |
| ST-P01 | Battery runtime (50% speed) | > 15 minutes | Minimum 15 min | 1 |
| ST-P03 | Voltage monitoring accuracy | Match multimeter | Within 5% | 1 |
| ST-P05 | Low-battery shutdown | Stops at 6.4V | Within 0.2V | 1 |
| ST-SF01 | E-stop response time | < 20ms | < 50ms | 1 |
| ST-SF02 | WebSocket disconnect stop | < 2 seconds | < 3 seconds | 1 |
| ST-SF05 | Speed ramp (0 to 100%) | ~200ms | 150-250ms | 1 |
| ST-SF07 | Safe boot (no unintended motion) | No motor movement | Zero movement before arm | 1 |
| ST-W01 | WiFi connection time | < 5 seconds | < 10 seconds | 1 |
| ST-W02 | WebSocket command latency | < 50ms | < 100ms | 1 |
| ST-W03 | WiFi range | > 15m | > 10m minimum | 1 |
| UT-M01-M08 | All motor unit tests | Pass | All pass | 1 |
| UT-S01-S05 | All servo unit tests | Pass | All pass | 1 |
| UT-SN01-SN02 | Battery ADC and staging | Pass | All pass | 1 |
| UT-E01-E04 | All E-stop unit tests | Pass | All pass | 1 |

### 5.2 Phase 2 Additional Acceptance Criteria

| Test ID | Description | Target Value | Tolerance | Phase |
|---------|-------------|-------------|-----------|-------|
| IT-01 | UART round-trip latency | < 10ms mean | < 20ms max | 2 |
| IT-02 | UART sustained 50Hz (60s) | < 0.5% loss | < 1% loss | 2 |
| IT-10 | cmd_vel to encoder feedback | < 100ms pipeline | < 200ms | 2 |
| IT-20 | IMU 90-degree turn accuracy | 90 degrees | Within 10 degrees | 2 |
| IT-21 | Encoder 1m distance accuracy | 1.0 metre | Within 10% | 2 |
| IT-23 | LIDAR obstacle in costmap | 50mm accuracy | Within 100mm | 2 |
| IT-31 | Sim navigation to goal | Arrive within 300mm | Within 500mm | 2 |
| IT-32 | SLAM map accuracy | Walls within 100mm | Within 200mm | 2 |
| ST-SF03 | UART watchdog motor stop | < 250ms | < 500ms | 2 |
| UT-P01-P06 | All UART protocol tests | Pass | All pass | 2 |
| UT-R01-R15 | All ROS2 node tests | Pass | All pass | 2 |

### 5.3 Phase 3 Additional Acceptance Criteria

| Test ID | Description | Target Value | Tolerance | Phase |
|---------|-------------|-------------|-----------|-------|
| — | Full-scale straight-line (10m) | < 300mm deviation | < 500mm | 3 |
| — | Full-scale turn radius | EA-10 full-scale calculated | Within 15% | 3 |
| — | Full-scale obstacle (100mm) | Clear without tipping | 100mm minimum | 3 |
| — | Battery runtime (autonomous) | > 2 hours | > 1.5 hours | 3 |
| — | Autonomous navigation (outdoor, 50m) | Arrive at GPS goal | Within 1m | 3 |
| — | Human detection stop distance | Stop within 1m of person | Within 1.5m | 3 |
| — | Geofence boundary compliance | Stay inside fence | Overshoot < 2m | 3 |
| — | Anti-theft alarm response | Alert within 5 seconds | Within 10 seconds | 3 |
| — | Weather resistance (rain, 30min) | No electrical failure | No water ingress | 3 |

---

## 6. Test Reporting

### 6.1 Test Report Format

Each test execution should be recorded with:

```
Test ID:        ST-D01
Date:           2026-XX-XX
Tester:         Charlie
Firmware:       v0.1.0
Hardware rev:   Phase 1 prototype
Result:         PASS / FAIL
Measured value: 150mm lateral deviation
Notes:          Slight pull to the right, likely W5 motor running faster.
                Adjusted motor calibration offset by -5%.
Follow-up:      Re-test after calibration change.
```

### 6.2 Test Tracking

Maintain a test results spreadsheet or checklist:

| Test ID | Status | Date Tested | Result | Notes |
|---------|--------|------------|--------|-------|
| UT-M01 | Not tested | — | — | — |
| UT-M02 | Not tested | — | — | — |
| ... | ... | ... | ... | ... |

Mark each test as: **Not tested**, **Pass**, **Fail**, or **Blocked** (prerequisite not met).

A phase is complete when ALL tests for that phase show **Pass**.

---

*Document EA-21 v1.0 — 2026-03-15*
