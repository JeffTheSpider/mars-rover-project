# Engineering Analysis 09: ESP32-S3 GPIO Pin Map & Wiring Diagram

**Document**: EA-09
**Date**: 2026-03-15
**Purpose**: Define the complete GPIO pin assignment for the ESP32-S3 DevKitC-1 motor controller, covering both Phase 1 (0.4 scale prototype) and Phase 2 (full scale), with wiring diagrams and peripheral allocation.
**Depends on**: EA-02 (Drivetrain), EA-04 (Compute/Sensors), EA-08 (Phase 1 Spec)

---

## 1. ESP32-S3 DevKitC-1 Overview

### 1.1 Module Selection

| Parameter | Value |
|-----------|-------|
| Module | ESP32-S3-WROOM-1 N16R8 |
| Flash | 16MB (Quad SPI) |
| PSRAM | 8MB (Octal SPI) |
| CPU | Dual-core Xtensa LX7, 240 MHz |
| WiFi | 802.11 b/g/n |
| Bluetooth | BLE 5.0 |
| USB | Native USB (CDC + JTAG) |
| Dev board | ESP32-S3-DevKitC-1 (USB-C) |
| Cost | ~$8 (AliExpress) |

### 1.2 Pins NOT Available for GPIO

The N16R8 module uses Octal SPI for PSRAM, which reserves the following GPIOs:

| GPIO | Function | Status |
|------|----------|--------|
| GPIO26 | SPICS1 (Octal PSRAM) | **RESERVED — DO NOT USE** |
| GPIO27 | SPIHD (Octal PSRAM) | **RESERVED — DO NOT USE** |
| GPIO28 | SPIWP (Octal PSRAM) | **RESERVED — DO NOT USE** |
| GPIO29 | SPICS0 (Flash) | **RESERVED — DO NOT USE** |
| GPIO30 | SPICLK (Flash) | **RESERVED — DO NOT USE** |
| GPIO31 | SPIQ (Flash) | **RESERVED — DO NOT USE** |
| GPIO32 | SPID (Flash) | **RESERVED — DO NOT USE** |
| GPIO33 | SPIIO4 (Octal PSRAM) | **RESERVED — DO NOT USE** |
| GPIO34 | SPIIO5 (Octal PSRAM) | **RESERVED — DO NOT USE** |
| GPIO35 | SPIIO6 (Octal PSRAM) | **RESERVED — DO NOT USE** |
| GPIO36 | SPIIO7 (Octal PSRAM) | **RESERVED — DO NOT USE** |
| GPIO37 | SPIDQS (Octal PSRAM) | **RESERVED — DO NOT USE** |

### 1.3 Strapping Pins

These pins affect boot mode. They can be used for GPIO but must not be pulled to unexpected states during boot:

| GPIO | Strapping Function | Safe Use |
|------|-------------------|----------|
| GPIO0 | Boot mode (HIGH = normal, LOW = download) | OK for output (has internal pull-up) |
| GPIO3 | JTAG signal source | OK for general use after boot |
| GPIO45 | VDD_SPI voltage (internal pull-down) | OK for output, avoid external pull-up |
| GPIO46 | Boot log verbosity (internal pull-down) | **Input only**. OK for input/interrupt |

### 1.4 Available GPIO Summary

After removing PSRAM/Flash pins (GPIO26-37), the ESP32-S3-DevKitC-1 exposes these GPIOs on the pin headers:

**GPIO0-21**: All available (22 pins)
**GPIO38-48**: All available except 43/44 if using USB (9 pins usable)

**USB pins**: GPIO19 (D-) and GPIO20 (D+) are used for native USB. If using USB for programming, these are NOT available for GPIO. However, we program via USB but can still use UART0 for other purposes.

**Total available GPIOs**: ~27 usable pins (varies by configuration).

---

## 2. Phase 1 Pin Assignment (0.4 Scale Prototype)

Phase 1 uses L298N drivers (2× dual H-bridge) and SG90 servos directly on ESP32 GPIO.

### 2.1 Motor Control (L298N)

Each L298N controls 2 motors. Each motor needs: 1 PWM (EN) + 2 DIR (IN1, IN2) = 3 pins.
6 motors × 3 pins = 18 GPIO pins. This is too many.

**Optimisation**: Use PWM on EN pins only, with IN1/IN2 for direction (just 2 states: forward/reverse). We can share EN pins for motors on the same side that always run at the same speed:

| Group | Motors | EN (PWM) | IN1 | IN2 | Notes |
|-------|--------|----------|-----|-----|-------|
| Left front | W1 (FL) | GPIO4 | GPIO5 | GPIO6 | Independent — steering wheel |
| Left middle | W2 (ML) | GPIO7 | GPIO15 | GPIO16 | Can share speed with W1 |
| Left rear | W3 (RL) | GPIO4 (shared) | GPIO17 | GPIO18 | Shares PWM with W1 |
| Right front | W6 (FR) | GPIO8 | GPIO9 | GPIO10 | Independent — steering wheel |
| Right middle | W5 (MR) | GPIO11 | GPIO12 | GPIO13 | Can share speed with W6 |
| Right rear | W4 (RR) | GPIO8 (shared) | GPIO14 | GPIO21 | Shares PWM with W6 |

**Revised approach**: For Phase 1 simplicity, we give each motor individual control. The ESP32-S3 has enough PWM channels (8× LEDC channels available). Each motor needs 1 PWM + 1 DIR (use one IN pin for direction, tie the other to inverse via firmware or just control both).

**Final Phase 1 Motor Pin Assignment**:

| Function | GPIO | Peripheral | L298N Pin |
|----------|------|------------|-----------|
| Motor W1 (FL) PWM | GPIO4 | LEDC Ch0 | L298N #1 ENA |
| Motor W1 (FL) DIR_A | GPIO5 | GPIO | L298N #1 IN1 |
| Motor W1 (FL) DIR_B | GPIO6 | GPIO | L298N #1 IN2 |
| Motor W2 (ML) PWM | GPIO7 | LEDC Ch1 | L298N #1 ENB |
| Motor W2 (ML) DIR_A | GPIO15 | GPIO | L298N #1 IN3 |
| Motor W2 (ML) DIR_B | GPIO16 | GPIO | L298N #1 IN4 |
| Motor W3 (RL) PWM | GPIO17 | LEDC Ch2 | L298N #2 ENA |
| Motor W3 (RL) DIR_A | GPIO18 | GPIO | L298N #2 IN1 |
| Motor W3 (RL) DIR_B | GPIO8 | GPIO | L298N #2 IN2 |
| Motor W4 (RR) PWM | GPIO3 | LEDC Ch3 | L298N #2 ENB |
| Motor W4 (RR) DIR_A | GPIO9 | GPIO | L298N #2 IN3 |
| Motor W4 (RR) DIR_B | GPIO10 | GPIO | L298N #2 IN4 |
| Motor W5 (MR) PWM | GPIO11 | LEDC Ch4 | *Need 3rd L298N or multiplex* |
| Motor W5 (MR) DIR_A | GPIO12 | GPIO | |
| Motor W5 (MR) DIR_B | GPIO13 | GPIO | |
| Motor W6 (FR) PWM | GPIO14 | LEDC Ch5 | |
| Motor W6 (FR) DIR_A | GPIO21 | GPIO | |
| Motor W6 (FR) DIR_B | GPIO47 | GPIO | |

**Problem**: L298N is a dual H-bridge — each board controls 2 motors. 6 motors need 3× L298N boards, not 2.

**Phase 1 revision**: Use 3× L298N boards ($9 total instead of $6), or accept that middle wheels can share control with their side's front wheel (same speed, same direction). This is the simpler and cheaper approach:

### 2.2 Simplified Phase 1 Motor Control (4-channel)

For Phase 1, we can treat the rover as 4 independently-controlled groups:
- **Left side**: W1 + W2 + W3 (same speed, same direction)
- **Right side**: W4 + W5 + W6 (same speed, same direction)

This gives skid-steering (tank drive) with only 2× L298N boards (4 channels for 2 sides). But we want Ackermann steering, so we need individual wheel speed control at minimum for front and rear independently.

**Compromise — 3-channel per side**:

| Channel | Motors | L298N | EN (PWM) | IN1 | IN2 | Rationale |
|---------|--------|-------|----------|-----|-----|-----------|
| L-Front | W1 (FL) | #1-A | GPIO4 | GPIO5 | GPIO6 | Steering wheel, independent speed |
| L-Mid+Rear | W2+W3 | #1-B | GPIO7 | GPIO15 | GPIO16 | Middle+rear wired in parallel |
| R-Front | W6 (FR) | #2-A | GPIO8 | GPIO9 | GPIO10 | Steering wheel, independent speed |
| R-Mid+Rear | W5+W4 | #2-B | GPIO11 | GPIO12 | GPIO13 | Middle+rear wired in parallel |

**Total motor GPIO: 12 pins** (4 PWM + 8 DIR) using 2× L298N boards.

Wiring W2+W3 in parallel from one L298N channel: both motors see the same voltage and direction. Since they're on the same side with no differential, this is fine for Phase 1.

### 2.3 Servo Control

| Function | GPIO | Peripheral | Notes |
|----------|------|------------|-------|
| Servo FL steering | GPIO1 | LEDC Ch6 | SG90, PWM 50Hz |
| Servo FR steering | GPIO2 | LEDC Ch7 | SG90, PWM 50Hz |
| Servo RL steering | GPIO42 | LEDC Ch8* | SG90, PWM 50Hz |
| Servo RR steering | GPIO41 | LEDC Ch9* | SG90, PWM 50Hz |

*ESP32-S3 has 8 LEDC channels. Channels 6-7 use the same timer. For servos (all 50Hz), sharing a timer is fine. The ESP32-S3 actually has 2× 4-channel LEDC groups = 8 channels total, which is exactly enough for 4 PWM motors + 4 servos.

### 2.4 Encoder Inputs (Optional for Phase 1)

N20 motors with encoders have 2 Hall effect channels (A/B) per motor. For Phase 1, we only need encoders on 2 wheels (left + right) for odometry:

| Function | GPIO | Peripheral | Notes |
|----------|------|------------|-------|
| Encoder W1 Ch-A | GPIO38 | PCNT/Interrupt | Front left |
| Encoder W1 Ch-B | GPIO39 | PCNT/Interrupt | Front left (optional, direction) |
| Encoder W6 Ch-A | GPIO40 | PCNT/Interrupt | Front right |
| Encoder W6 Ch-B | GPIO48 | PCNT/Interrupt | Front right (optional, direction) |

The ESP32-S3 has hardware Pulse Counter (PCNT) units — perfect for encoder counting without CPU load.

### 2.5 Miscellaneous

| Function | GPIO | Peripheral | Notes |
|----------|------|------------|-------|
| Battery voltage | GPIO14 | ADC1 Ch3 | Voltage divider (7.4V → 3.3V) |
| Status LED | GPIO0 | GPIO | Onboard LED or NeoPixel |
| Power button (optional) | GPIO46 | GPIO input | Input-only pin, internal pull-down |

### 2.6 Phase 1 Complete Pin Map

| GPIO | Function | Direction | Peripheral |
|------|----------|-----------|------------|
| 0 | Status LED / NeoPixel | Output | RMT |
| 1 | Servo FL | Output | LEDC Ch6 |
| 2 | Servo FR | Output | LEDC Ch7 |
| 3 | Motor W4 (RR) PWM — *or spare* | Output | LEDC Ch3 |
| 4 | Motor L-Front PWM | Output | LEDC Ch0 |
| 5 | Motor L-Front DIR_A | Output | GPIO |
| 6 | Motor L-Front DIR_B | Output | GPIO |
| 7 | Motor L-Mid+Rear PWM | Output | LEDC Ch1 |
| 8 | Motor R-Front PWM | Output | LEDC Ch2 |
| 9 | Motor R-Front DIR_A | Output | GPIO |
| 10 | Motor R-Front DIR_B | Output | GPIO |
| 11 | Motor R-Mid+Rear PWM | Output | LEDC Ch3 |
| 12 | Motor R-Mid+Rear DIR_A | Output | GPIO |
| 13 | Motor R-Mid+Rear DIR_B | Output | GPIO |
| 14 | Battery voltage (ADC) | Input | ADC1 |
| 15 | Motor L-Mid+Rear DIR_A | Output | GPIO |
| 16 | Motor L-Mid+Rear DIR_B | Output | GPIO |
| 17 | *Spare* | — | — |
| 18 | *Spare* | — | — |
| 19 | USB D- | — | USB |
| 20 | USB D+ | — | USB |
| 21 | *Spare* | — | — |
| 26-37 | **RESERVED (PSRAM/Flash)** | — | — |
| 38 | Encoder W1 Ch-A | Input | PCNT |
| 39 | Encoder W1 Ch-B | Input | PCNT |
| 40 | Encoder W6 Ch-A | Input | PCNT |
| 41 | Servo RL | Output | LEDC |
| 42 | Servo RR | Output | LEDC |
| 43 | UART0 TX (USB serial) | Output | UART0 |
| 44 | UART0 RX (USB serial) | Input | UART0 |
| 45 | *Spare (strapping pin)* | — | — |
| 46 | Power button | Input | GPIO (input-only) |
| 47 | *Spare* | — | — |
| 48 | Encoder W6 Ch-B | Input | PCNT |

**Used: 20 pins | Spare: 5 pins (3, 17, 18, 21, 45, 47) | Reserved: 12 pins | USB: 4 pins**

---

## 3. Phase 2 Pin Assignment (Full Scale)

Phase 2 adds the PCA9685 I2C PWM driver, which offloads all 14 servo PWM signals to I2C. It also upgrades from L298N to Cytron MDD10A motor drivers (simpler: 1 PWM + 1 DIR per motor).

### 3.1 Motor Control (Cytron MDD10A)

Each MDD10A controls 2 motors. Each motor needs: 1 PWM + 1 DIR = 2 pins.
6 motors × 2 pins = 12 GPIO pins, using 3× MDD10A boards.

| Function | GPIO | Peripheral | MDD10A | Notes |
|----------|------|------------|--------|-------|
| Motor W1 (FL) PWM | GPIO4 | LEDC Ch0 | #1 M1-PWM | 25kHz PWM |
| Motor W1 (FL) DIR | GPIO5 | GPIO | #1 M1-DIR | HIGH=fwd, LOW=rev |
| Motor W2 (ML) PWM | GPIO6 | LEDC Ch1 | #1 M2-PWM | |
| Motor W2 (ML) DIR | GPIO7 | GPIO | #1 M2-DIR | |
| Motor W3 (RL) PWM | GPIO15 | LEDC Ch2 | #2 M1-PWM | |
| Motor W3 (RL) DIR | GPIO16 | GPIO | #2 M1-DIR | |
| Motor W4 (RR) PWM | GPIO17 | LEDC Ch3 | #2 M2-PWM | |
| Motor W4 (RR) DIR | GPIO18 | GPIO | #2 M2-DIR | |
| Motor W5 (MR) PWM | GPIO8 | LEDC Ch4 | #3 M1-PWM | |
| Motor W5 (MR) DIR | GPIO9 | GPIO | #3 M1-DIR | |
| Motor W6 (FR) PWM | GPIO10 | LEDC Ch5 | #3 M2-PWM | |
| Motor W6 (FR) DIR | GPIO11 | GPIO | #3 M2-DIR | |

### 3.2 I2C Bus (Shared)

| Function | GPIO | Peripheral | Device |
|----------|------|------------|--------|
| I2C SDA | GPIO1 | I2C0 SDA | PCA9685 + BNO055 + INA219 (×4) |
| I2C SCL | GPIO2 | I2C0 SCL | PCA9685 + BNO055 + INA219 (×4) |

I2C addresses:
- PCA9685: 0x40 (default)
- BNO055: 0x28 (default)
- INA219 #1: 0x40 → **CONFLICT with PCA9685** — use 0x41 (A0 jumper)
- INA219 #2: 0x44
- INA219 #3: 0x45
- INA219 #4: 0x4C

**Note**: PCA9685 default address 0x40 conflicts with INA219 default. Set INA219 #1 to address 0x41 by bridging its A0 solder jumper.

### 3.3 PCA9685 Channel Assignment

The PCA9685 provides 16 PWM channels at 50Hz for all servos:

| PCA9685 Ch | Function | Servo Type |
|------------|----------|------------|
| 0 | Steering FL | MG996R |
| 1 | Steering FR | MG996R |
| 2 | Steering RL | MG996R |
| 3 | Steering RR | MG996R |
| 4 | Mast pan | MG996R |
| 5 | Mast tilt | MG996R |
| 6 | Left arm shoulder | MG996R |
| 7 | Left arm elbow | MG996R |
| 8 | Left arm wrist | MG996R |
| 9 | Left arm gripper | MG996R |
| 10 | Right arm shoulder | MG996R |
| 11 | Right arm elbow | MG996R |
| 12 | Right arm wrist | MG996R |
| 13 | Right arm gripper | MG996R |
| 14 | *Spare* | — |
| 15 | *Spare* | — |

### 3.4 UART to Jetson

| Function | GPIO | Peripheral | Notes |
|----------|------|------------|-------|
| UART1 TX (to Jetson RX) | GPIO43 | UART1 TX | 115200 baud |
| UART1 RX (from Jetson TX) | GPIO44 | UART1 RX | 115200 baud |

**Note**: GPIO43/44 are also used by UART0 (USB CDC). On the DevKitC-1, USB CDC uses the native USB controller (GPIO19/20), so UART0 on GPIO43/44 is available for reassignment to UART1 for Jetson communication.

**Level shifting**: Jetson GPIO is 3.3V, ESP32-S3 GPIO is 3.3V. No level shifter needed — direct connection is safe.

### 3.5 Encoder Inputs (All 6 Wheels)

| Function | GPIO | Peripheral | Notes |
|----------|------|------------|-------|
| Encoder W1 Ch-A | GPIO38 | PCNT Unit 0 | Interrupt-capable |
| Encoder W1 Ch-B | GPIO39 | PCNT Unit 0 | Direction detection |
| Encoder W2 Ch-A | GPIO40 | PCNT Unit 1 | |
| Encoder W2 Ch-B | GPIO41 | PCNT Unit 1 | |
| Encoder W3 Ch-A | GPIO42 | PCNT Unit 2 | |
| Encoder W3 Ch-B | GPIO48 | PCNT Unit 2 | |
| Encoder W4 Ch-A | GPIO47 | PCNT Unit 3 | |
| Encoder W4 Ch-B | GPIO21 | PCNT Unit 3 | |
| Encoder W5 Ch-A | GPIO14 | PCNT Unit 4* | Reused from ADC (Phase 1) |
| Encoder W5 Ch-B | GPIO13 | PCNT Unit 4* | |
| Encoder W6 Ch-A | GPIO12 | PCNT Unit 5* | |
| Encoder W6 Ch-B | GPIO3 | PCNT Unit 5* | |

*ESP32-S3 has 4 hardware PCNT units. Encoders 5-6 use software counting via GPIO interrupts, or we multiplex PCNT units (read count → swap to next encoder → read count, at 1kHz cycle). This is feasible because at 80 RPM with ~200 PPR, the max pulse rate is ~267 Hz per channel — well within software interrupt handling capability.

### 3.6 Miscellaneous Phase 2

| Function | GPIO | Peripheral | Notes |
|----------|------|------------|-------|
| Battery voltage ADC | GPIO14 | ADC1 Ch3 | Voltage divider (22.2V → 3.3V max) |
| NeoPixel LED strip | GPIO0 | RMT Ch0 | Status LEDs (WS2812B) |
| E-stop button | GPIO46 | GPIO input | Input-only, internal pull-down, active HIGH |
| Buzzer | GPIO45 | LEDC Ch6 | PWM tone generation |

### 3.7 Phase 2 Complete Pin Map

| GPIO | Phase 2 Function | Dir | Peripheral |
|------|-----------------|-----|------------|
| 0 | NeoPixel LED strip | Out | RMT |
| 1 | I2C SDA | I/O | I2C0 |
| 2 | I2C SCL | Out | I2C0 |
| 3 | Encoder W6 Ch-B | In | GPIO ISR |
| 4 | Motor W1 PWM | Out | LEDC Ch0 |
| 5 | Motor W1 DIR | Out | GPIO |
| 6 | Motor W2 PWM | Out | LEDC Ch1 |
| 7 | Motor W2 DIR | Out | GPIO |
| 8 | Motor W5 PWM | Out | LEDC Ch4 |
| 9 | Motor W5 DIR | Out | GPIO |
| 10 | Motor W6 PWM | Out | LEDC Ch5 |
| 11 | Motor W6 DIR | Out | GPIO |
| 12 | Encoder W6 Ch-A | In | GPIO ISR |
| 13 | Encoder W5 Ch-B | In | GPIO ISR |
| 14 | Encoder W5 Ch-A / Battery ADC | In | PCNT / ADC (muxed) |
| 15 | Motor W3 PWM | Out | LEDC Ch2 |
| 16 | Motor W3 DIR | Out | GPIO |
| 17 | Motor W4 PWM | Out | LEDC Ch3 |
| 18 | Motor W4 DIR | Out | GPIO |
| 19 | USB D- | — | USB |
| 20 | USB D+ | — | USB |
| 21 | Encoder W4 Ch-B | In | PCNT |
| 26-37 | **RESERVED (PSRAM/Flash)** | — | — |
| 38 | Encoder W1 Ch-A | In | PCNT |
| 39 | Encoder W1 Ch-B | In | PCNT |
| 40 | Encoder W2 Ch-A | In | PCNT |
| 41 | Encoder W2 Ch-B | In | PCNT |
| 42 | Encoder W3 Ch-A | In | PCNT |
| 43 | UART1 TX → Jetson | Out | UART1 |
| 44 | UART1 RX ← Jetson | In | UART1 |
| 45 | Buzzer | Out | LEDC Ch6 |
| 46 | E-stop button | In | GPIO (input-only) |
| 47 | Encoder W4 Ch-A | In | PCNT |
| 48 | Encoder W3 Ch-B | In | PCNT |

**Used: 28 pins | Reserved: 12 pins (PSRAM/Flash) | USB: 2 pins**
**All 28 available GPIOs are allocated** — zero spare pins in Phase 2.

---

## 4. Wiring Diagrams

### 4.1 Phase 1 Wiring Overview

```
                    ┌─────────────────────────────────────┐
                    │          ESP32-S3 DevKitC-1          │
                    │                                      │
    Servos ←────────┤ GPIO1,2,41,42 (LEDC PWM 50Hz)      │
                    │                                      │
    L298N #1 ←──────┤ GPIO4,5,6 (W1)  GPIO7,15,16 (W2+3) │
    L298N #2 ←──────┤ GPIO8,9,10 (W6) GPIO11,12,13 (W5+4)│
                    │                                      │
    Encoders ──────→┤ GPIO38,39 (W1)  GPIO40,48 (W6)     │
                    │                                      │
    Battery ADC ──→ ┤ GPIO14 (voltage divider)            │
    Status LED ←────┤ GPIO0 (NeoPixel/built-in)           │
    Power btn ─────→┤ GPIO46 (input-only)                 │
                    │                                      │
    USB ←──────────→┤ GPIO19,20 (programming + serial)    │
                    └─────────────────────────────────────┘

Power:
    2S LiPo (7.4V) → Switch → L298N VCC (both boards)
    L298N 5V out → ESP32 VIN (via 5V pin)
    L298N 5V out → SG90 servo VCC (all 4)
    GND: common ground (battery, L298N, ESP32, servos)
```

### 4.2 Phase 2 Wiring Overview

```
                    ┌─────────────────────────────────────┐
                    │          ESP32-S3 DevKitC-1          │
                    │                                      │
    I2C bus ←──────→┤ GPIO1 (SDA), GPIO2 (SCL)            │
    (PCA9685,       │                                      │
     BNO055,        │                                      │
     INA219×4)      │                                      │
                    │                                      │
    MDD10A #1 ←─────┤ GPIO4,5 (W1)  GPIO6,7 (W2)         │
    MDD10A #2 ←─────┤ GPIO15,16 (W3) GPIO17,18 (W4)      │
    MDD10A #3 ←─────┤ GPIO8,9 (W5)  GPIO10,11 (W6)       │
                    │                                      │
    Encoders ──────→┤ GPIO38-42,47,48,21,3,12-14 (12 ch)  │
                    │                                      │
    UART ←─────────→┤ GPIO43 (TX), GPIO44 (RX) → Jetson   │
                    │                                      │
    NeoPixel ←──────┤ GPIO0 (RMT)                          │
    Buzzer ←────────┤ GPIO45 (LEDC)                        │
    E-stop ────────→┤ GPIO46 (input-only)                  │
    USB ←──────────→┤ GPIO19,20                            │
                    └─────────────────────────────────────┘

I2C Bus Devices (3.3V):
    ├── PCA9685 (0x40) → 14× MG996R servos (6V power from BEC)
    ├── BNO055 (0x28) → IMU
    ├── INA219 #1 (0x41) → Battery current
    ├── INA219 #2 (0x44) → Motor current
    ├── INA219 #3 (0x45) → Compute current
    └── INA219 #4 (0x4C) → Solar current

PCA9685 Servo Power: Separate 6V BEC from battery, NOT from ESP32 3.3V
    6S LiPo → Hobbywing 6V BEC → PCA9685 V+ terminal → all 14 servos
```

### 4.3 Voltage Divider for Battery Monitoring

```
Phase 1 (7.4V battery):
    VBAT ──[10kΩ]──┬──[4.7kΩ]── GND
                   │
                   └── GPIO14 (ADC)

    V_adc = 7.4 × 4.7 / (10 + 4.7) = 2.37V (within 3.3V ADC range)
    Scale factor: (10 + 4.7) / 4.7 = 3.128
    Reading: V_bat = ADC_voltage × 3.128

Phase 2 (22.2V battery):
    VBAT ──[100kΩ]──┬──[15kΩ]── GND
                    │
                    └── GPIO14 (ADC)

    V_adc = 22.2 × 15 / (100 + 15) = 2.90V (within 3.3V ADC range)
    V_max = 25.2 × 15 / (100 + 15) = 3.29V (fully charged, still < 3.3V)
    Scale factor: (100 + 15) / 15 = 7.667
```

---

## 5. PWM Configuration

### 5.1 Motor PWM

| Parameter | Phase 1 (L298N) | Phase 2 (Cytron MDD10A) |
|-----------|-----------------|------------------------|
| Frequency | 1 kHz | 25 kHz |
| Resolution | 8-bit (0-255) | 10-bit (0-1023) |
| Channels | LEDC Ch0-Ch3 (4 motor groups) | LEDC Ch0-Ch5 (6 individual motors) |
| Timer | Timer 0 | Timer 0 |

**Why 25 kHz for Phase 2**: Above audible range — eliminates motor whine. L298N can't handle >20 kHz (old BJT design), but Cytron MDD10A uses MOSFETs rated for 25 kHz.

### 5.2 Servo PWM

| Parameter | Phase 1 (SG90) | Phase 2 (PCA9685 → MG996R) |
|-----------|----------------|---------------------------|
| Frequency | 50 Hz | 50 Hz (set on PCA9685) |
| Pulse range | 500-2400 μs | 500-2500 μs |
| Centre | 1500 μs (90°) | 1500 μs (90°) |
| Resolution | LEDC 16-bit | PCA9685 12-bit (4096 steps) |
| Channels | LEDC Ch4-Ch7 | PCA9685 Ch0-Ch13 |

### 5.3 LEDC Channel Allocation

ESP32-S3 has 8 LEDC channels across 4 timers:

**Phase 1**:
| Timer | Channel | Function |
|-------|---------|----------|
| Timer 0 | Ch0 | Motor L-Front PWM (1 kHz) |
| Timer 0 | Ch1 | Motor L-Mid+Rear PWM (1 kHz) |
| Timer 0 | Ch2 | Motor R-Front PWM (1 kHz) |
| Timer 0 | Ch3 | Motor R-Mid+Rear PWM (1 kHz) |
| Timer 1 | Ch4 | Servo FL (50 Hz) |
| Timer 1 | Ch5 | Servo FR (50 Hz) |
| Timer 1 | Ch6 | Servo RL (50 Hz) |
| Timer 1 | Ch7 | Servo RR (50 Hz) |

**Phase 2**:
| Timer | Channel | Function |
|-------|---------|----------|
| Timer 0 | Ch0-Ch5 | 6× Motor PWM (25 kHz) |
| Timer 1 | Ch6 | Buzzer (variable freq) |
| Timer 1 | Ch7 | *Spare* |

Servos move to PCA9685 in Phase 2, freeing up 4 LEDC channels.

---

## 6. I2C Bus Design (Phase 2)

### 6.1 Bus Configuration

| Parameter | Value |
|-----------|-------|
| Clock speed | 400 kHz (Fast Mode) |
| Pull-up resistors | 4.7 kΩ to 3.3V (on PCA9685 breakout board) |
| Max bus length | ~50cm (sufficient — all devices inside body) |
| SDA | GPIO1 |
| SCL | GPIO2 |

### 6.2 Bus Bandwidth Analysis

At 400 kHz I2C, each byte transfer takes ~25μs (8 data + 1 ACK).

| Device | Data per read | Read frequency | Bandwidth |
|--------|--------------|----------------|-----------|
| BNO055 (quaternion + accel) | 20 bytes | 100 Hz | 2,000 B/s |
| INA219 ×4 (voltage + current) | 8 bytes × 4 | 10 Hz | 320 B/s |
| PCA9685 (write servo positions) | 4 bytes × 14 | 50 Hz | 2,800 B/s |
| **Total** | | | **5,120 B/s** |

At 400 kHz, the I2C bus can handle ~16,000 B/s (after addressing overhead). Our 5,120 B/s is 32% utilisation — plenty of headroom.

---

## 7. Safety Features

### 7.1 E-Stop

The emergency stop button on GPIO46 (input-only pin, internal pull-down):
- Normally LOW (pull-down)
- Button press → HIGH → firmware immediately sets all motor PWM to 0
- All servos hold current position (PCA9685 continues driving)
- Status LED blinks red
- Buzzer sounds 3 short beeps
- Recovery: press button again to clear E-stop state

### 7.2 Watchdog

ESP32-S3 Task Watchdog Timer (TWDT):
- 5 second timeout
- Motor control task must feed watchdog every loop
- If watchdog triggers: all motors stop, buzzer alarm, LED error pattern
- Same proven pattern as Clock/Lamp projects

### 7.3 Undervoltage Protection

Battery voltage monitored via ADC at 10 Hz:
- Phase 1: 2S LiPo cutoff at 6.4V (3.2V per cell — safe minimum for LiPo)
- Phase 2: 6S LiPo cutoff at 19.2V (3.2V per cell)
- Warning at 3.4V/cell: reduce max speed to 50%
- Critical at 3.2V/cell: stop all motors, alert via LED + buzzer

---

*Document EA-09 v1.0 — 2026-03-15*
