# ESP32-S3 Motor Controller Firmware

Low-level brain for the Mars Rover. Version 0.2.0 (Phase 1 prototype).

## Phase 1 Features
- 4-channel motor control (6 motors as 4 groups via 2× L298N)
- 4 SG90 steering servos (Ackermann, point turn, crab walk)
- WiFi web server + WebSocket for phone control
- Battery voltage monitoring (ADC with moving average)
- 2 wheel encoders (optional, interrupt-driven)
- E-stop button support
- Task watchdog (5s timeout = stop all motors)
- Speed ramping (smooth acceleration/deceleration)

## Architecture
Single translation unit (.h includes from main .ino), non-blocking state machine ticks.
Same proven pattern as Clock/Lamp ESP8266 projects.

## Files
- `esp32.ino` — Main sketch (setup, loop, WiFi, status LED)
- `config.h` — Pin definitions, constants, geometry parameters
- `motors.h` — L298N motor control (PWM + direction)
- `steering.h` — Servo control, Ackermann geometry calculations
- `sensors.h` — Battery ADC, encoder ISRs, E-stop
- `rover_webserver.h` — WiFi web UI + WebSocket for phone control
- `ota.h` — ArduinoOTA wireless firmware updates
- `uart_nmea.h` — NMEA text UART protocol for Jetson (Phase 1)
- `uart_binary.h` — COBS binary UART protocol for Jetson (Phase 2)

## Dependencies
- ESP32 Arduino Core (v3.x)
- WebSocketsServer library (by Markus Sattler)

## Build
```bash
arduino-cli compile --fqbn esp32:esp32:esp32s3 --build-property "build.extra_flags=-DBOARD_HAS_PSRAM" .
```

## Phase 2 Additions (planned)
- Binary UART protocol (EA-18, COBS + CRC-16, 460800 baud)
- PCA9685 I2C PWM driver for 14 servos
- BNO055 IMU via I2C
- 6 individual motor channels (Cytron MDD10A)
- 6 wheel encoders (hardware PCNT)
- PID speed control

## Engineering References
- EA-08: Phase 1 parts specification
- EA-09: GPIO pin map and wiring diagram
- EA-10: Ackermann steering geometry
- EA-12: UART protocol (Phase 2)
