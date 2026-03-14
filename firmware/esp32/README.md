# ESP32-S3 Motor Controller Firmware

Low-level brain for the Mars Rover. Handles:
- 6x DC gearmotor PWM control with PID
- 4x steering servo control (Ackermann, point-turn, crab)
- Sensor polling (ultrasonic, encoders, IMU, temp)
- Battery monitoring (voltage ADC, current sensing)
- LED control (underglow, headlights, indicators)
- Safety watchdog (5s timeout = stop all motors)
- UART communication with Jetson Orin Nano

## Architecture
Single translation unit (.h includes from main .cpp), non-blocking state machine ticks.
Same proven pattern as Clock/Lamp ESP8266 projects.
