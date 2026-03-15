# Engineering Analysis 15: Safety Systems & Fault Handling

**Document**: EA-15
**Date**: 2026-03-15
**Purpose**: Define all safety mechanisms, fault detection, recovery procedures, and fail-safe behaviours for the rover across all operating modes.
**Depends on**: EA-03 (Power), EA-09 (GPIO), EA-12 (UART Protocol)

---

## 1. Safety Philosophy

The rover operates outdoors near people, pets, and property. Safety design follows these principles:

1. **Fail-safe**: Any single failure must result in the rover stopping, never accelerating or steering uncontrollably
2. **Defence in depth**: Multiple independent safety layers — no single point of failure can cause harm
3. **Watchdog pattern**: Proven in Clock/Lamp projects — if the control loop stops, motors stop
4. **Human override**: Physical E-stop always works, regardless of software state
5. **Graceful degradation**: Sensor failures reduce capability but don't cause unsafe behaviour

---

## 2. Safety Layers

```
Layer 1: HARDWARE (always active, no software dependency)
  ├── Physical E-stop button (mushroom, red, panel-mount)
  ├── Main fuse (20A, inline with battery)
  ├── Per-rail fuses (motor, servo, compute)
  └── Reverse polarity protection (diode or P-FET)

Layer 2: ESP32 FIRMWARE (runs independently of Jetson)
  ├── Task watchdog timer (5s timeout)
  ├── UART command timeout (200ms → stop motors)
  ├── Battery undervoltage cutoff (3.2V/cell)
  ├── Motor current limiting (software PWM cap)
  ├── Speed ramping (no instant full-speed)
  └── Encoder stall detection

Layer 3: JETSON SOFTWARE (highest-level intelligence)
  ├── Obstacle detection (depth camera + LIDAR)
  ├── Geofence boundary enforcement
  ├── Collision avoidance (Nav2 costmap)
  ├── Tilt angle monitoring (IMU → tip-over prevention)
  ├── Thermal monitoring (throttle at 80°C)
  └── Remote kill switch (phone app)

Layer 4: OPERATIONAL
  ├── Speed limits in autonomous mode
  ├── Operating area restrictions
  ├── Battery temperature lockout (<5°C no charge)
  └── Weather-based operation rules
```

---

## 3. Hardware Safety

### 3.1 Emergency Stop Button

| Parameter | Value |
|-----------|-------|
| Type | Red mushroom head, twist-to-release |
| Location | Rear of body, easily accessible |
| Mechanism | Normally-open momentary switch (Phase 1) / latching (Phase 2+) |
| Connection | GPIO46 (ESP32-S3, input-only pin) |
| Response time | <1ms (hardware interrupt on ESP32) |
| Effect | All motor PWM → 0, all servos hold position |
| Recovery | Release/twist button, then send resume command from phone |

**Phase 1**: Simple tactile button on GPIO46 (momentary press = toggle E-stop)
**Phase 2+**: Panel-mount mushroom button with NC contacts. Wire in series with motor driver enable lines for hardware-level motor cutoff even if ESP32 crashes.

### 3.2 Fuse Protection

| Fuse | Rating | Location | Protects |
|------|--------|----------|----------|
| Main | 20A blade fuse | Battery output | Entire rover from short circuit |
| Motor rail | 10A | After buck converter (12V) | Motor drivers from overcurrent |
| Servo rail | 5A | After BEC (6V) | PCA9685 + servos |
| Compute rail | 3A | After buck (5V) | Jetson + ESP32 + sensors |
| Solar input | 5A | Panel input | MPPT controller |

### 3.3 Reverse Polarity Protection

A P-channel MOSFET (IRF4905 or similar) on the battery input prevents damage if the battery is connected backwards:

```
Battery + ──[Fuse]──[P-FET drain]──── Rover +
                      |
                    [Gate]──[10kΩ]── Battery -
                      |
Battery - ────────────+──────────── Rover -
```

If polarity is correct, the P-FET's body diode conducts initially, pulling the gate low and turning the FET fully on (<10mΩ). If reversed, the gate goes high and the FET stays off.

---

## 4. Firmware Safety (ESP32-S3)

### 4.1 Watchdog Timer

```c
// Task watchdog — resets if main loop doesn't feed within 5 seconds
esp_task_wdt_init(5, true);  // 5s timeout, panic=true (resets ESP32)
esp_task_wdt_add(NULL);      // Add current (loopTask)

void loop() {
    esp_task_wdt_reset();  // Feed watchdog every loop iteration
    // ... control logic
}
```

If the main loop hangs (infinite loop, crash, deadlock), the watchdog triggers after 5 seconds and resets the ESP32. On reboot, all GPIO pins default to INPUT/LOW — motors stop naturally (no PWM = no power).

### 4.2 UART Command Timeout

From EA-12: if no MOT or PNG command is received within 200ms, ESP32 stops all motors.

```c
#define COMMAND_TIMEOUT_MS 200

void checkCommandTimeout() {
    if (millis() - lastCommandTime > COMMAND_TIMEOUT_MS) {
        if (motorTarget[0] != 0 || motorTarget[2] != 0) {
            stopAllMotors();
            sendError(8, "command_timeout");
        }
    }
}
```

This handles: Jetson crash, UART cable disconnect, software freeze on Jetson side.

### 4.3 Battery Undervoltage

Three-stage battery protection:

| Stage | Trigger (per cell) | Action |
|-------|-------------------|--------|
| Normal | >3.5V | Full operation |
| Warning | 3.4-3.5V | Reduce max speed to 50%, LED amber, buzzer beep |
| Critical | 3.2-3.4V | Stop all motors, LED red, buzzer alarm, send phone notification |
| Dangerous | <3.2V | Full shutdown (deep sleep), refuse to start without charge |

### 4.4 Speed Ramping

Motors never jump from 0 to 100% instantly. The ramp rate limits acceleration:

```c
#define RAMP_RATE 10  // Max change per 20ms tick = 500%/second

void updateMotors() {
    for (int i = 0; i < 4; i++) {
        int8_t diff = motorTarget[i] - motorSpeed[i];
        if (diff > RAMP_RATE) diff = RAMP_RATE;
        if (diff < -RAMP_RATE) diff = -RAMP_RATE;
        setMotor(i, motorSpeed[i] + diff);
    }
}
```

Time from 0 to 100%: 200ms (10 ticks × 20ms). Fast enough to be responsive, slow enough to prevent mechanical shock and wheel spin.

### 4.5 Encoder Stall Detection

If encoders report zero movement but motors are commanded >20%, the wheels are stalled (stuck on obstacle, motor failure, stripped gear):

```c
void checkStall() {
    static uint32_t stallTimer = 0;

    if (abs(motorSpeed[0]) > 20 || abs(motorSpeed[2]) > 20) {
        int32_t w1, w6;
        getAndResetEncoders(&w1, &w6);

        if (abs(w1) < 2 && abs(w6) < 2) {
            // Both wheels not moving despite motor command
            if (millis() - stallTimer > 2000) {
                // Stalled for 2+ seconds
                stopAllMotors();
                sendError(3, "motor_stall");
            }
        } else {
            stallTimer = millis();
        }
    } else {
        stallTimer = millis();
    }
}
```

### 4.6 Safe Boot Sequence

On power-up, the ESP32 follows a defensive startup:

1. All GPIO to safe state (motors off, servos centred)
2. Read battery voltage — refuse to start if < 3.2V/cell
3. Check E-stop state
4. Initialise subsystems (motors, servos, sensors)
5. Connect WiFi (Phase 1) or wait for UART (Phase 2)
6. **Wait for explicit "arm" command** before accepting drive commands
7. Blink status LED to indicate ready state

The "arm" step prevents the rover from driving immediately on power-up. The user must explicitly enable driving from the phone app or by sending a UART command.

---

## 5. Jetson Software Safety (Phase 2)

### 5.1 Obstacle Avoidance

Two independent obstacle detection systems:

**System A: LIDAR (RPLidar A1)**
- 360° 2D scan at 5.5 Hz
- Safety zones:
  - **Stop zone**: <300mm from any obstacle → immediate stop
  - **Slow zone**: 300-800mm → reduce to 30% speed
  - **Caution zone**: 800-2000mm → reduce to 70% speed
- Works in all lighting conditions

**System B: Depth Camera (OAK-D Lite)**
- Forward-facing stereo depth, 80° FOV
- Detects obstacles at 200mm-8m range
- Identifies traversable terrain vs obstacles
- Works in daylight (limited in dark — supplemented by LIDAR)

Both systems run independently. Either one triggering "stop" overrides the other.

### 5.2 Tilt Protection

BNO055 IMU monitors roll and pitch angles:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Normal | <15° tilt | Full speed |
| Caution | 15-25° tilt | Reduce to 50% speed, alert user |
| Danger | 25-35° tilt | Stop, reverse slowly |
| Critical | >35° tilt | Emergency stop, alarm, assume stuck/tipping |

### 5.3 Geofence

Software-defined boundary stored as GPS polygon:

```python
# Geofence check runs at 1Hz
def check_geofence(lat, lon, fence_polygon):
    if not point_in_polygon(lat, lon, fence_polygon):
        # Outside boundary
        stop_motors()
        alert_user("Rover outside geofence!")
        navigate_to_nearest_fence_point()
```

Default geofence: 100m radius circle around home location. Configurable from phone app.

### 5.4 Autonomous Speed Limits

| Mode | Max Speed | Steering Limit |
|------|-----------|----------------|
| Manual (phone control) | 5 km/h (100%) | ±35° |
| Autonomous (Nav2) | 3 km/h (60%) | ±25° |
| Return-to-home | 2 km/h (40%) | ±20° |
| Obstacle detected | 1 km/h (20%) | ±15° |
| Near humans (YOLO) | 1 km/h (20%) | ±15° |

### 5.5 Human Detection

YOLO v8 running on Jetson detects people in camera feeds:
- If a person is detected within 3m: reduce speed to 20%, alert user
- If a person is detected within 1m: stop, wait until clear
- If a small child or pet is detected: stop immediately at any distance within 5m

### 5.6 Remote Kill Switch

The phone app has a prominent red "KILL" button:
- Sends emergency stop via WebSocket → Jetson → UART → ESP32
- Also sends a direct WiFi HTTP request to ESP32 as backup
- If 4G connection is available and WiFi fails, routes through 4G
- Kill state persists until physically reset at the rover

---

## 6. Fault Recovery

### 6.1 Fault Classification

| Class | Examples | Recovery |
|-------|----------|----------|
| **Transient** | WiFi dropout, GPS glitch, single bad sensor reading | Auto-retry, ignore isolated readings |
| **Degraded** | One camera failed, GPS lost, one ultrasonic noisy | Continue with reduced capability, alert user |
| **Critical** | All motors stalled, battery critical, E-stop, Jetson crash | Stop everything, alert user, wait for intervention |
| **Hardware** | Motor driver burned, servo stripped, broken wire | Cannot auto-recover — needs physical repair |

### 6.2 Sensor Failure Handling

| Sensor | Failure Detection | Fallback |
|--------|-------------------|----------|
| GPS | No fix for 30s, position jump >100m | Navigate by LIDAR SLAM + dead reckoning only |
| IMU (BNO055) | I2C timeout, calibration lost | Stop autonomous mode, manual only |
| LIDAR | No scan data for 2s | Reduce speed to 20%, use depth camera only |
| Depth camera | USB disconnect, no frames | Use LIDAR only for obstacle detection |
| Encoders | Zero movement with motors running | Stall detection (§4.5) |
| Ultrasonic | Stuck at 0 or max range | Ignore that sensor, use remaining 5 |
| Battery ADC | Reading 0V or >30V (impossible) | Assume ADC fault, conservative cutoff |

### 6.3 Communication Failure Handling

| Failure | Detection | Response |
|---------|-----------|----------|
| WiFi lost (phone) | No heartbeat for 5s | Continue autonomous, alert when reconnected |
| UART lost (Jetson ↔ ESP32) | No message for 200ms | ESP32 stops motors, Jetson logs error |
| 4G lost | No data for 60s | Switch to WiFi-only, continue operation |
| All comms lost | WiFi + 4G + Bluetooth down | Return to home (if GPS works) or stop in place |

### 6.4 ESP32 Crash Recovery

If the ESP32 resets (watchdog, brownout, firmware bug):

1. ESP32 restarts in ~2 seconds
2. All motors default to OFF (GPIO reset to INPUT)
3. ESP32 runs safe boot sequence (§4.6)
4. Jetson detects UART timeout, logs crash event
5. Jetson waits for ESP32 to reconnect (heartbeat)
6. Jetson re-sends configuration (servo trims, PID gains)
7. Jetson re-arms rover if operator confirms

### 6.5 Jetson Crash Recovery

If the Jetson crashes or reboots:

1. ESP32 detects UART timeout (200ms)
2. ESP32 stops all motors (fail-safe)
3. ESP32 blinks status LED pattern: "waiting for brain"
4. ESP32 continues monitoring battery, E-stop, encoders
5. Jetson reboots (~60s for Ubuntu + ROS2 startup)
6. Jetson reconnects UART, re-establishes communication
7. Jetson re-initialises sensors and navigation
8. Operator must re-arm from phone app

---

## 7. Anti-Theft System

### 7.1 Layers

| Layer | Mechanism | Response |
|-------|-----------|----------|
| **Geofence** | GPS boundary check (1 Hz) | Alert + return-to-home |
| **Motion detect** | IMU acceleration >0.5g when parked | Alert + start recording |
| **GPS tracking** | Position logged every 10s when armed | Continuous until disarmed |
| **Alarm** | Speaker siren (120dB) + LED strobe | Activate after 5s of unauthorised motion |
| **Phone alert** | Push notification via 4G | Includes GPS coords + camera snapshot |
| **Motor lock** | Software disable + brake (short motor terminals) | Requires 6-digit PIN to unlock |
| **Remote disable** | Kill switch from phone app | Rover becomes inert brick |
| **Camera recording** | All cameras record to SD on alarm | 10min loop, timestamps in filename |

### 7.2 Arming

Anti-theft arms automatically when:
- Rover has been stationary for 5+ minutes
- Phone app is disconnected (no active user)
- Explicit "arm" command from phone

Disarm requires:
- Phone app connection (authenticated)
- 6-digit PIN entry
- Or physical button sequence on rover (backup)

---

## 8. Phase 1 Safety Summary

Phase 1 is a small, lightweight (1.1 kg) prototype with limited speed. Safety is proportionally simpler:

| Feature | Implemented in Phase 1? |
|---------|------------------------|
| E-stop button | Yes (GPIO46) |
| Watchdog timer | Yes (5s) |
| Battery undervoltage | Yes (3-stage) |
| Speed ramping | Yes |
| Command timeout | Yes (2s for WebSocket disconnect) |
| Obstacle avoidance | No (no sensors — manual driving only) |
| Tilt protection | No (no IMU) |
| Geofence | No (no GPS) |
| Stall detection | Optional (if encoders connected) |
| Anti-theft | No (too small/cheap to steal) |

---

*Document EA-15 v1.0 — 2026-03-15*
