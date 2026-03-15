# EA-19: Phase 1 Wiring Diagram

**Document**: EA-19
**Date**: 2026-03-15
**Purpose**: Complete wiring reference for the Phase 1 (0.4 scale) Mars Rover prototype. All connections, wire gauges, connectors, and circuit diagrams in one document.
**MCU**: ESP32-S3 DevKitC-1 N16R8
**Depends on**: EA-03 (Power System), EA-09 (GPIO Pin Map), EA-15 (Safety Systems)

---

## 1. Overview

This document provides the definitive wiring reference for the Phase 1 prototype rover. It covers every electrical connection from battery to MCU to actuators and sensors, with ASCII circuit diagrams, a master connection table, and assembly procedures.

**Phase 1 scope**:
- 2S LiPo battery (7.4V nominal)
- 2x L298N dual H-bridge motor drivers (4 motor channels for 6 motors)
- 4x SG90 steering servos (direct PWM from ESP32)
- Battery voltage monitoring (resistor divider on ADC)
- Software E-stop button on GPIO46
- Optional Hall effect encoders on 2 wheels (W1, W6)
- WiFi control via phone PWA (no Jetson in Phase 1)

**Key references**:
- EA-03 for wire gauges, fuse ratings, and power budget
- EA-09 for all GPIO assignments and LEDC channel mapping
- EA-15 for E-stop circuit, watchdog, and safety layers
- `firmware/esp32/config.h` for pin definitions used in code

---

## 2. Power Distribution

### 2.1 Main Power Path

```
                         PHASE 1 POWER DISTRIBUTION
    =====================================================================

    +------------+    +---------+    +---------+    +-------------------+
    | 2S LiPo    |    | 20A     |    | Kill    |    | Power             |
    | 7.4V nom   +--->+ Blade   +--->+ Switch  +--->+ Distribution      |
    | 8.4V full  |    | Fuse    |    | (rear   |    | Point (terminal   |
    | XT60 plug  |    | (ATC)   |    |  panel) |    |  block/solder)    |
    +-----+------+    +---------+    +---------+    +----+---------+----+
          |                                              |         |
          |  14 AWG silicone wire throughout              |         |
          |  this high-current path                      |         |
          |                                              |         |
          |         +------------------------------------+         |
          |         |                                              |
          |         v                                              v
          |  +------+--------+                          +----------+----+
          |  | L298N #1      |                          | L298N #2      |
          |  | (Left side)   |                          | (Right side)  |
          |  |               |                          |               |
          |  | VCC = 7.4V    |                          | VCC = 7.4V    |
          |  | 12V jumper ON |                          | 12V jumper ON |
          |  |               |                          |               |
          |  | 5V REG OUT ---+---+                      | 5V REG OUT    |
          |  +---------------+   |                      +-------+-------+
          |                      |                              |
          |                      v                              v
          |              +-------+-------+               (not used or
          |              | 5V Power Bus  |                tied to 5V bus
          |              | (breadboard)  |                as backup)
          |              +--+----+----+--+
          |                 |    |    |
          |                 v    v    v
          |          +------++ +--+---++ +----------+
          |          | ESP32 | | SG90  | | SG90     |
          |          | VIN   | | FL,FR | | RL,RR    |
          |          | (5V)  | | servos| | servos   |
          |          +-------+ +-------+ +----------+
          |
          +---[10k]---+---[4.7k]--- GND
                       |
                       +--- GPIO14 (battery ADC)
```

### 2.2 Voltage Rails

| Rail | Source | Voltage | Max Current | Wire Gauge | Fuse |
|------|--------|---------|-------------|------------|------|
| Battery main | 2S LiPo | 6.4-8.4V | 10A (Phase 1) | 14 AWG | 20A blade (ATC) |
| Motor power | Battery via kill switch | 7.4V nom | 5A per L298N | 16 AWG to each L298N | L298N thermal protection |
| 5V logic/servo | L298N #1 onboard regulator | 5.0V | ~1A (78M05 limit) | 22 AWG | ESP32 onboard USB fuse |
| 3.3V sensors | ESP32 onboard LDO | 3.3V | 0.5A | 22 AWG | Internal |

### 2.3 Wire Gauge Summary (from EA-03 section 5.4)

| Run | Max Current | Gauge | Notes |
|-----|-------------|-------|-------|
| Battery to kill switch to distribution | 10A | 14 AWG silicone | XT60 connectors at battery end |
| Distribution to each L298N VCC | 5A | 16 AWG | Screw terminals on L298N |
| L298N motor outputs to motors | 2A per channel | 18 AWG | Through rocker/bogie arms |
| 5V bus to ESP32 VIN | 0.5A | 22 AWG | Short run, Dupont or direct |
| 5V bus to servos | 0.65A each | 22 AWG | Dupont connectors |
| All signal wires | <100mA | 22 AWG | Dupont female-female jumpers |

### 2.4 L298N Board Configuration

Both L298N boards require identical jumper setup:

```
    +--------------------------------------------------+
    |  L298N Motor Driver Board                        |
    |                                                  |
    |  POWER TERMINALS:                                |
    |    [+12V/VCC]  [GND]  [+5V OUT]                 |
    |       7.4V     GND     5V regulated              |
    |                                                  |
    |  12V JUMPER:  *** KEEP ON ***                    |
    |  (enables 78M05 onboard 5V regulator)            |
    |  Valid when VCC is 7-12V                         |
    |                                                  |
    |  ENA/ENB JUMPERS:  *** REMOVE BOTH ***           |
    |  (default jumpers short ENA/ENB to 5V            |
    |   for always-full-speed; we need PWM control)    |
    |                                                  |
    |  LOGIC PINS:                                     |
    |    [ENA] [IN1] [IN2]  [IN3] [IN4] [ENB]         |
    |     PWM   DIR   DIR    DIR   DIR   PWM           |
    |                                                  |
    |  MOTOR OUTPUTS:                                  |
    |    [OUT1] [OUT2]  [OUT3] [OUT4]                  |
    |     Motor A        Motor B                       |
    +--------------------------------------------------+
```

---

## 3. Motor Wiring (6 Motors via 2x L298N)

Phase 1 groups 6 motors into 4 channels. Front wheels get independent channels for Ackermann speed differential. Middle and rear wheels on each side are wired in parallel (same speed, same direction).

### 3.1 L298N #1 -- Left Side Motors

```
    L298N BOARD #1 (LEFT SIDE)
    ==========================

    POWER:                          LOGIC (from ESP32):
    +--------+-------+--------+    +------+------+------+------+------+------+
    | VCC    | GND   | 5V OUT |    | ENA  | IN1  | IN2  | IN3  | IN4  | ENB  |
    +---+----+---+---+---+----+    +--+---+--+---+--+---+--+---+--+---+--+---+
        |        |       |           |      |      |      |      |      |
      7.4V    GND bus  5V bus     GPIO4  GPIO5  GPIO6  GPIO15 GPIO16 GPIO7
     (from              (to       LEDC                              LEDC
      switch)          ESP32      Ch0                                Ch1
                       +servos)  (PWM)                              (PWM)

    MOTOR OUTPUTS:
    +--------+---------+--------+---------+
    | OUT1   | OUT2    | OUT3   | OUT4    |
    +----+---+---+-----+----+---+---+-----+
         |       |          |       |
         +---+---+          +---+---+
             |                  |
         W1 (FL)          W2 (ML) + W3 (RL)
       front-left         wired in parallel
       single motor       (red-to-red, black-to-black)
```

### 3.2 L298N #2 -- Right Side Motors

```
    L298N BOARD #2 (RIGHT SIDE)
    ===========================

    POWER:                          LOGIC (from ESP32):
    +--------+-------+--------+    +------+------+------+------+------+------+
    | VCC    | GND   | 5V OUT |    | ENA  | IN1  | IN2  | IN3  | IN4  | ENB  |
    +---+----+---+---+---+----+    +--+---+--+---+--+---+--+---+--+---+--+---+
        |        |       |           |      |      |      |      |      |
      7.4V    GND bus  (NC or     GPIO8  GPIO9  GPIO10 GPIO12 GPIO13 GPIO11
     (from            tie to      LEDC                              LEDC
      switch)         5V bus)     Ch2                                Ch3
                                 (PWM)                              (PWM)

    MOTOR OUTPUTS:
    +--------+---------+--------+---------+
    | OUT1   | OUT2    | OUT3   | OUT4    |
    +----+---+---+-----+----+---+---+-----+
         |       |          |       |
         +---+---+          +---+---+
             |                  |
         W6 (FR)          W5 (MR) + W4 (RR)
       front-right        wired in parallel
       single motor       (red-to-red, black-to-black)
```

### 3.3 Motor Channel Summary

| Channel | L298N | EN (PWM) | IN_A | IN_B | Motors | GPIO defines in config.h |
|---------|-------|----------|------|------|--------|--------------------------|
| L-Front | #1-A | GPIO4 (LEDC Ch0) | GPIO5 | GPIO6 | W1 (FL) | MOTOR_LF_PWM/IN1/IN2 |
| L-Mid+Rear | #1-B | GPIO7 (LEDC Ch1) | GPIO15 | GPIO16 | W2+W3 parallel | MOTOR_LR_PWM/IN1/IN2 |
| R-Front | #2-A | GPIO8 (LEDC Ch2) | GPIO9 | GPIO10 | W6 (FR) | MOTOR_RF_PWM/IN1/IN2 |
| R-Mid+Rear | #2-B | GPIO11 (LEDC Ch3) | GPIO12 | GPIO13 | W5+W4 parallel | MOTOR_RR_PWM/IN1/IN2 |

### 3.4 Motor Direction Truth Table

| IN_A | IN_B | ENA/ENB | Motor Action |
|------|------|---------|--------------|
| HIGH | LOW | PWM duty | Forward at PWM speed |
| LOW | HIGH | PWM duty | Reverse at PWM speed |
| LOW | LOW | any | Coast (free spin) |
| HIGH | HIGH | any | Brake (motor terminals shorted) |

### 3.5 Motor PWM Configuration (from config.h)

| Parameter | Value |
|-----------|-------|
| Frequency | 1 kHz (MOTOR_PWM_FREQ) |
| Resolution | 8-bit, 0-255 (MOTOR_PWM_RES) |
| LEDC Timer | Timer 0 (MOTOR_LEDC_TIMER) |
| Channels | Ch0 (LF), Ch1 (LR), Ch2 (RF), Ch3 (RR) |

---

## 4. Steering Servo Wiring (4 Servos)

### 4.1 Power Bus

All 4 SG90 servos share a common 5V power bus sourced from the L298N #1 onboard 5V regulator. Each servo signal wire connects directly to an ESP32 GPIO.

```
    L298N #1                        5V POWER BUS
    5V OUT ----+----------+----------+----------+----------+---- ESP32 VIN
               |          |          |          |          |
              VCC        VCC        VCC        VCC        VCC
               |          |          |          |          |
    GPIO1 -SIG-[FL]       |          |          |          |
    GPIO2 -SIG-----------[FR]        |          |          |
    GPIO41 SIG----------------------[RL]        |          |
    GPIO42 SIG---------------------------------[RR]        |
               |          |          |          |          |
              GND        GND        GND        GND        GND
               |          |          |          |          |
    ===========+====GND===+====BUS===+===========+=========+=====
```

### 4.2 Servo Pin Assignments (from config.h)

| Servo | Position | Signal GPIO | LEDC Channel | Timer |
|-------|----------|-------------|--------------|-------|
| FL steering | Front left | GPIO1 (SERVO_FL_PIN) | Ch4 | Timer 1 |
| FR steering | Front right | GPIO2 (SERVO_FR_PIN) | Ch5 | Timer 1 |
| RL steering | Rear left | GPIO41 (SERVO_RL_PIN) | Ch6 | Timer 1 |
| RR steering | Rear right | GPIO42 (SERVO_RR_PIN) | Ch7 | Timer 1 |

### 4.3 SG90 Wire Colours

| Wire | Function | Connects To |
|------|----------|-------------|
| Orange/Yellow | Signal (PWM) | ESP32 GPIO (per table above) |
| Red | VCC (4.8-6V) | 5V power bus |
| Brown/Black | GND | Common ground bus |

### 4.4 Servo PWM Configuration (from config.h)

| Parameter | Value |
|-----------|-------|
| Frequency | 50 Hz (SERVO_PWM_FREQ) |
| Resolution | 16-bit (SERVO_PWM_RES) |
| Pulse range | 500-2400 us (SERVO_MIN_US to SERVO_MAX_US) |
| Centre | 1500 us / 90 degrees (SERVO_CENTER_US) |
| Max steering angle | +/- 35 degrees (STEER_MAX_ANGLE) |

### 4.5 Decoupling Capacitors

Add a 100uF electrolytic capacitor across the VCC and GND of each servo's power connection (at the 5V bus, not at the servo). This absorbs current spikes when servos move under load and prevents brownout on the ESP32.

```
    5V bus ----+----[100uF]----+---- GND bus
               |               |
              VCC             GND
               |               |
              [SG90 servo]
```

If all 4 servos stall simultaneously (peak ~2.6A total), the L298N 78M05 regulator (rated 0.5-1A) cannot supply enough current. For initial testing this is acceptable since only 1-2 servos typically move at once. If servos jitter or ESP32 browns out, add a dedicated 5V 3A buck converter (XL4015 module) powered directly from the 7.4V battery rail.

---

## 5. Sensor Wiring

### 5.1 BNO055 IMU (Phase 2 Only -- Not Installed in Phase 1)

Phase 1 does not include an IMU. In Phase 2, the BNO055 connects via I2C:

| Pin | Connection | Notes |
|-----|------------|-------|
| VIN | ESP32 3.3V | BNO055 breakout has onboard regulator |
| GND | Common GND bus | |
| SDA | GPIO1 | Shared I2C bus (Phase 2 only, GPIO1 is servo in Phase 1) |
| SCL | GPIO2 | Shared I2C bus (Phase 2 only, GPIO2 is servo in Phase 1) |

I2C address: 0x28 (default). In Phase 2, servos move to PCA9685, freeing GPIO1/GPIO2 for I2C.

### 5.2 Ultrasonic Sensors (Not Used)

Phase 1 does not include HC-SR04 ultrasonics. Phase 2 uses LIDAR instead (RPLidar A1 on Jetson USB).

### 5.3 Hall Effect Encoders (Optional, 2 Wheels)

N20 motors with Hall effect encoders provide odometry for wheels W1 (FL) and W6 (FR). Each encoder has 4 wires in addition to the 2 motor power leads:

```
    ENCODER WIRING (W1 and W6 only):

    ESP32 3.3V ----+----------------+---- Encoder W1 VCC
                   |                |
                   +----------------+---- Encoder W6 VCC
                   |
    GND bus -------+----------------+---- Encoder W1 GND
                   |                |
                   +----------------+---- Encoder W6 GND

    GPIO38 ------- Encoder W1 Ch-A  (PCNT Unit 0, ENC_W1_CHA)
    GPIO39 ------- Encoder W1 Ch-B  (PCNT Unit 0, ENC_W1_CHB)
    GPIO40 ------- Encoder W6 Ch-A  (PCNT Unit 1, ENC_W6_CHA)
    GPIO48 ------- Encoder W6 Ch-B  (PCNT Unit 1, ENC_W6_CHB)
```

Encoder signals are 3.3V logic. No pull-up resistors needed -- the ESP32-S3 PCNT (Pulse Counter) hardware handles counting without CPU load.

### 5.4 Battery Voltage Divider

```
    BATTERY VOLTAGE MONITORING:

    Battery + (7.4V) ----[R1: 10k, 1/4W 1%]----+----[R2: 4.7k, 1/4W 1%]---- GND
                                                 |
                                                 +---- GPIO14 (ADC1 Ch3)
                                                 |
                                                 +----[C1: 100nF ceramic]---- GND
                                                      (noise filter)

    Voltage at GPIO14:
      Nominal (7.4V):     7.4  x 4.7 / 14.7 = 2.37V
      Full charge (8.4V): 8.4  x 4.7 / 14.7 = 2.69V
      Cutoff (6.4V):      6.4  x 4.7 / 14.7 = 2.05V
      All within ESP32 ADC range (0-3.3V)

    Firmware scale factor: BATT_DIVIDER_RATIO = (10 + 4.7) / 4.7 = 3.128
    V_battery = ADC_reading_volts x 3.128
```

Build this on the mini breadboard. Keep leads short to minimise ADC noise.

---

## 6. E-Stop Circuit

### 6.1 Phase 1: Software E-Stop

Phase 1 uses a software E-stop -- a tactile button that signals the ESP32 to stop all motors. This is not a hardware power disconnect (that is added in Phase 2+).

GPIO46 is an input-only pin with an internal pull-down resistor. The circuit connects through a button to 3.3V:

```
    E-STOP CIRCUIT (Phase 1):

    ESP32 3.3V --------+
                        |
                   [Tactile Button]
                   (momentary, normally open)
                        |
                        +-------- GPIO46 (ESTOP_PIN)
                                  (input-only, internal pull-down)

    Normal state:   GPIO46 = LOW  (internal pull-down holds low)
    Button pressed: GPIO46 = HIGH (connected to 3.3V through button)

    Firmware: Rising-edge interrupt on GPIO46 toggles E-stop state.
    Response time: <1ms (hardware interrupt).
```

### 6.2 E-Stop Behaviour (from EA-15)

When triggered:
1. All motor PWM set to 0 (coast stop)
2. All servos hold current position
3. Status LED blinks red pattern
4. WebSocket broadcasts E-stop state to phone app
5. Requires button press again AND resume command from phone to clear

### 6.3 Phase 2+ Hardware E-Stop (Reference)

```
    PHASE 2+ HARDWARE E-STOP:

    Battery + --[Fuse]--[Mushroom Button NC]--[MOSFET/Relay]-- Motor power bus
                              |
                         Normally Closed
                         Red mushroom head
                         Twist-to-release
                              |
                         Parallel signal to GPIO46
                         (software detection even with
                          hardware cutoff active)

    Pressing the mushroom button:
      - NC contacts OPEN -> power physically disconnected from motors
      - GPIO46 also detects the press for software logging
      - Works even if ESP32 firmware has crashed
```

---

## 7. Communication

### 7.1 USB for Programming and Debug

| Function | GPIO | Notes |
|----------|------|-------|
| USB D- | GPIO19 | Native USB on ESP32-S3 DevKitC-1 |
| USB D+ | GPIO20 | USB-C connector on dev board |
| UART0 TX | GPIO43 | USB CDC serial monitor output |
| UART0 RX | GPIO44 | USB CDC serial monitor input |

Programming is done via USB-C. Serial monitor is available at 115200 baud for debug output.

### 7.2 UART to Jetson (Phase 2 Only)

Phase 1 does not connect to a Jetson. In Phase 2:

```
    ESP32-S3                  Jetson Orin Nano
    ========                  ================
    GPIO43 (UART1 TX) -----> RX (UART pin)
    GPIO44 (UART1 RX) <----- TX (UART pin)
    GND -------------------- GND

    Baud: 115200
    Logic: Both 3.3V -- no level shifter needed
    Protocol: Binary UART (EA-18)
    Wire: 22 AWG, <300mm, twisted pair recommended
```

### 7.3 WiFi (Phase 1 Control)

Phase 1 uses WiFi for control via phone PWA:
- SSID configured in config.h (WIFI_SSID)
- HTTP server on port 80 (WEB_SERVER_PORT)
- WebSocket on port 81 (WS_PORT)
- Hostname: "rover" (WIFI_HOSTNAME)

---

## 8. Complete Connection Table

### 8.1 Master Wiring List

| Component | Wire Colour | From | To | Wire Gauge | Connector | Notes |
|-----------|-------------|------|----|------------|-----------|-------|
| **POWER** | | | | | | |
| Battery + | Red | 2S LiPo XT60 | Fuse holder input | 14 AWG | XT60 | Keyed connector prevents polarity reversal |
| Fuse to switch | Red | Fuse holder output | Kill switch terminal 1 | 14 AWG | Ring/spade | 20A ATC blade fuse |
| Switch to dist. | Red | Kill switch terminal 2 | Distribution point | 14 AWG | Ring/spade | Panel-mount toggle on rear wall |
| Dist. to L298N #1 | Red | Distribution point | L298N #1 VCC screw terminal | 16 AWG | Stripped wire | |
| Dist. to L298N #2 | Red | Distribution point | L298N #2 VCC screw terminal | 16 AWG | Stripped wire | |
| Battery - | Black | 2S LiPo XT60 | Common GND bus | 14 AWG | XT60 | Star topology from battery negative |
| GND to L298N #1 | Black | GND bus | L298N #1 GND screw terminal | 16 AWG | Stripped wire | |
| GND to L298N #2 | Black | GND bus | L298N #2 GND screw terminal | 16 AWG | Stripped wire | |
| 5V to ESP32 | Red | L298N #1 5V out | ESP32 VIN/5V pin | 22 AWG | Dupont | |
| GND to ESP32 | Black | GND bus | ESP32 GND pin | 22 AWG | Dupont | |
| **MOTORS** | | | | | | |
| W1 motor + | Red | L298N #1 OUT1 | W1 (FL) motor red lead | 18 AWG | Screw/solder | |
| W1 motor - | Black | L298N #1 OUT2 | W1 (FL) motor black lead | 18 AWG | Screw/solder | Swap leads if direction is reversed |
| W2+W3 motor + | Red | L298N #1 OUT3 | W2+W3 red leads (paralleled) | 18 AWG | Screw/solder | Solder W2 and W3 red together |
| W2+W3 motor - | Black | L298N #1 OUT4 | W2+W3 black leads (paralleled) | 18 AWG | Screw/solder | Solder W2 and W3 black together |
| W6 motor + | Red | L298N #2 OUT1 | W6 (FR) motor red lead | 18 AWG | Screw/solder | |
| W6 motor - | Black | L298N #2 OUT2 | W6 (FR) motor black lead | 18 AWG | Screw/solder | |
| W5+W4 motor + | Red | L298N #2 OUT3 | W5+W4 red leads (paralleled) | 18 AWG | Screw/solder | Solder W5 and W4 red together |
| W5+W4 motor - | Black | L298N #2 OUT4 | W5+W4 black leads (paralleled) | 18 AWG | Screw/solder | Solder W5 and W4 black together |
| **MOTOR LOGIC** | | | | | | |
| LF PWM | Orange | ESP32 GPIO4 | L298N #1 ENA | 22 AWG | Dupont F-F | LEDC Ch0, 1 kHz |
| LF DIR_A | Yellow | ESP32 GPIO5 | L298N #1 IN1 | 22 AWG | Dupont F-F | |
| LF DIR_B | Yellow | ESP32 GPIO6 | L298N #1 IN2 | 22 AWG | Dupont F-F | |
| LR PWM | Orange | ESP32 GPIO7 | L298N #1 ENB | 22 AWG | Dupont F-F | LEDC Ch1, 1 kHz |
| LR DIR_A | Yellow | ESP32 GPIO15 | L298N #1 IN3 | 22 AWG | Dupont F-F | |
| LR DIR_B | Yellow | ESP32 GPIO16 | L298N #1 IN4 | 22 AWG | Dupont F-F | |
| RF PWM | Orange | ESP32 GPIO8 | L298N #2 ENA | 22 AWG | Dupont F-F | LEDC Ch2, 1 kHz |
| RF DIR_A | Yellow | ESP32 GPIO9 | L298N #2 IN1 | 22 AWG | Dupont F-F | |
| RF DIR_B | Yellow | ESP32 GPIO10 | L298N #2 IN2 | 22 AWG | Dupont F-F | |
| RR PWM | Orange | ESP32 GPIO11 | L298N #2 ENB | 22 AWG | Dupont F-F | LEDC Ch3, 1 kHz |
| RR DIR_A | Yellow | ESP32 GPIO12 | L298N #2 IN3 | 22 AWG | Dupont F-F | |
| RR DIR_B | Yellow | ESP32 GPIO13 | L298N #2 IN4 | 22 AWG | Dupont F-F | |
| **SERVOS** | | | | | | |
| FL servo signal | Orange | ESP32 GPIO1 | SG90 FL signal (orange) | 22 AWG | Dupont F-F | LEDC Ch4, 50 Hz |
| FR servo signal | Orange | ESP32 GPIO2 | SG90 FR signal (orange) | 22 AWG | Dupont F-F | LEDC Ch5, 50 Hz |
| RL servo signal | Orange | ESP32 GPIO41 | SG90 RL signal (orange) | 22 AWG | Dupont F-F | LEDC Ch6, 50 Hz |
| RR servo signal | Orange | ESP32 GPIO42 | SG90 RR signal (orange) | 22 AWG | Dupont F-F | LEDC Ch7, 50 Hz |
| Servo VCC (x4) | Red | 5V power bus | SG90 VCC (red wire, all 4) | 22 AWG | Dupont | Shared 5V bus |
| Servo GND (x4) | Black | GND bus | SG90 GND (brown wire, all 4) | 22 AWG | Dupont | Common ground |
| **SENSORS** | | | | | | |
| Battery ADC | Blue | Voltage divider midpoint | ESP32 GPIO14 | 22 AWG | Dupont | Keep short, add 100nF cap |
| Divider R1 | -- | Battery + | Divider midpoint | Component lead | Breadboard | 10k ohm, 1% |
| Divider R2 | -- | Divider midpoint | GND | Component lead | Breadboard | 4.7k ohm, 1% |
| Filter cap | -- | GPIO14 | GND | Component lead | Breadboard | 100nF ceramic |
| **E-STOP** | | | | | | |
| E-stop 3.3V | Red | ESP32 3.3V | Tactile button pin 1 | 22 AWG | Dupont | |
| E-stop signal | White | Tactile button pin 2 | ESP32 GPIO46 | 22 AWG | Dupont | Internal pull-down, input-only |
| **STATUS LED** | | | | | | |
| LED data | Green | ESP32 GPIO0 | WS2812B data in (or onboard) | 22 AWG | Dupont | Add 330 ohm series resistor for WS2812B |
| **ENCODERS (OPTIONAL)** | | | | | | |
| Enc W1 VCC | Red | ESP32 3.3V | Encoder W1 VCC | 22 AWG | Dupont | |
| Enc W1 GND | Black | GND bus | Encoder W1 GND | 22 AWG | Dupont | |
| Enc W1 Ch-A | Green | Encoder W1 A | ESP32 GPIO38 | 22 AWG | Dupont | PCNT Unit 0 |
| Enc W1 Ch-B | Green | Encoder W1 B | ESP32 GPIO39 | 22 AWG | Dupont | PCNT Unit 0 |
| Enc W6 VCC | Red | ESP32 3.3V | Encoder W6 VCC | 22 AWG | Dupont | |
| Enc W6 GND | Black | GND bus | Encoder W6 GND | 22 AWG | Dupont | |
| Enc W6 Ch-A | Green | Encoder W6 A | ESP32 GPIO40 | 22 AWG | Dupont | PCNT Unit 1 |
| Enc W6 Ch-B | Green | Encoder W6 B | ESP32 GPIO48 | 22 AWG | Dupont | PCNT Unit 1 |

---

## 9. Connector Strategy

### 9.1 Connector Types

| Application | Connector | Current Rating | Why |
|-------------|-----------|---------------|-----|
| Battery to rover | XT60 (male on battery, female on rover) | 60A continuous | Gold-plated, keyed to prevent polarity reversal |
| Battery to fuse | Inline ATC blade fuse holder | 20A | Standard automotive, easy to replace |
| Fuse to kill switch | Ring terminals or spade connectors | 20A | Crimped on 14 AWG |
| Kill switch to L298N | Screw terminals (on L298N board) | 20A | 14-16 AWG stripped wire into screw terminal |
| L298N motor outputs | Screw terminals (on L298N board) | 2A per channel | 18 AWG stripped wire |
| Motor leads | Direct solder to N20 motor tabs | -- | Solder + heat shrink |
| ESP32 to L298N logic | Dupont female-female jumpers | Signal level | Removable for debugging |
| ESP32 to servo signal | Dupont female-female jumpers | Signal level | SG90 header is male |
| Servo power/ground | Dupont or breadboard bus | 0.65A each | From 5V bus |
| Voltage divider | Breadboard-mounted | -- | Resistors on mini breadboard |
| E-stop button | Dupont or solder | Signal level | Tactile button on breadboard or panel |

### 9.2 Phase 1 Philosophy

- **Dupont connectors on all signal lines**: Easy to disconnect, swap, and debug during development. No soldering required for signal changes.
- **Screw terminals on L298N**: Solid mechanical connection without soldering to the driver board.
- **Solder only where necessary**: Motor leads, fuse holder, kill switch.
- **Label everything**: Masking tape flags on every wire with the GPIO number written on them.

### 9.3 Phase 2+ Upgrades

| Phase 1 Connector | Phase 2+ Upgrade |
|-------------------|-----------------|
| Dupont signal wires | JST-XH (2.5mm pitch, locking) |
| XT60 battery | XT90 (higher current for 6S) |
| Breadboard divider | Soldered PCB |
| Dupont servo | JST-XH or direct to PCA9685 |

---

## 10. Assembly Notes

### 10.1 Recommended Soldering/Crimping Order

Build and test in this order. Each step should be verified before proceeding to the next.

**Step 1: Battery Lead**
1. Solder XT60 female connector to 14 AWG leads (red = +, black = -)
2. Solder inline blade fuse holder on positive lead
3. Install 20A blade fuse
4. Solder kill switch inline after fuse
5. Test: connect battery, flip switch, measure voltage at output

**Step 2: Power Distribution**
1. Split positive lead to reach both L298N VCC terminals
2. Connect GND bus (battery negative to both L298N GND and ESP32 GND)
3. Verify L298N jumpers: 12V ON, ENA/ENB REMOVED
4. Test: power on, measure 5V at L298N #1 5V output

**Step 3: ESP32 Power**
1. Connect L298N #1 5V output to ESP32 VIN pin
2. Connect ESP32 GND to GND bus
3. Test: power on, ESP32 power LED illuminates, USB serial responds

**Step 4: Voltage Divider**
1. Build divider on breadboard (10k + 4.7k + 100nF cap)
2. Connect to battery + and GND
3. Connect midpoint to GPIO14
4. Test: read ADC in firmware, verify voltage matches multimeter within 5%

**Step 5: Motor Wiring (one at a time)**
1. Connect L298N #1 logic pins (GPIO4-7, 15-16) with Dupont jumpers
2. Solder motor W1 leads, connect to L298N #1 OUT1/OUT2
3. Test W1: upload test sketch, verify forward/reverse at 30% PWM
4. Parallel-solder W2+W3 leads, connect to OUT3/OUT4
5. Test W2+W3
6. Repeat for L298N #2 (GPIO8-13) with W6 and W5+W4

**Step 6: Servo Wiring**
1. Connect 5V bus to all 4 servo VCC (red wires)
2. Connect GND bus to all 4 servo GND (brown wires)
3. Connect signal wires: GPIO1 (FL), GPIO2 (FR), GPIO41 (RL), GPIO42 (RR)
4. Install 100uF decoupling caps on 5V bus
5. Test: send 1500us centre pulse, verify each servo centres

**Step 7: E-Stop**
1. Wire tactile button between ESP32 3.3V and GPIO46
2. Test: verify GPIO46 reads LOW normally, HIGH when pressed

**Step 8: Encoders (Optional)**
1. Connect encoder VCC to 3.3V, GND to GND bus
2. Connect Ch-A/Ch-B to assigned GPIOs
3. Test: spin wheel by hand, verify pulse count in serial monitor

**Step 9: Status LED**
1. Connect WS2812B data to GPIO0 with 330 ohm series resistor
2. Connect WS2812B VCC to 5V, GND to GND
3. Test: verify LED lights up with test pattern

### 10.2 Cable Management

```
    CABLE ROUTING (top view):

    +--------------------------------------------+
    |                                             |
    |  [L298N #1]     [ESP32-S3]     [L298N #2]  |
    |   Left side      Centre         Right side  |
    |     |              |               |        |
    |     |    [Mini Breadboard]         |        |
    |     |   (divider, servo bus,       |        |
    |     |    E-stop, decoupling)       |        |
    |     |              |               |        |
    |  ===+==============+===============+===     |  <-- Floor cable channel
    |     |              |               |        |      (10x10mm groove in
    |     |         [2S LiPo]           |        |       3D-printed body)
    |     |         [Battery]           |        |
    |     |              |               |        |
    |     |         [Kill Switch]        |        |
    |     |         [Fuse Holder]        |        |
    +--+--+--+---+---+--+--+---+---+--+--+---+--+
       |     |   |   |     |   |   |     |   |
       W1    W2  W3  SG90s      W4  W5  W6  SG90s
       FL    ML  RL  FL,RL      RR  MR  FR  FR,RR
    (left side)                    (right side)
```

**Routing rules**:
1. Power wires (14-16 AWG) run along the floor cable channel, separated from signal wires
2. Signal wires (22 AWG) bundle together with small cable ties
3. Motor wires route through rocker arm tubes with 50mm slack at each pivot
4. Servo leads extend with 22 AWG wire + Dupont if the stock 150mm lead is too short
5. Strain relief with hot glue at pivot entry/exit points
6. Minimum bend radius: 5mm (10x wire diameter for 22 AWG)

### 10.3 Testing Sequence

| Step | Test | Pass Criteria |
|------|------|---------------|
| 1 | Visual inspection | No shorts, correct jumpers, fuse installed |
| 2 | Continuity: battery+ to L298N VCC (switch ON) | Beep |
| 3 | Continuity: battery- to all GND points | Beep |
| 4 | No short: battery+ to GND | No beep |
| 5 | Power on: measure 5V at L298N regulator output | 4.8-5.2V |
| 6 | Power on: ESP32 power LED illuminates | LED on |
| 7 | ADC: GPIO14 reads correct battery voltage | Within 5% of multimeter |
| 8 | E-stop: GPIO46 LOW normally, HIGH when pressed | Correct logic levels |
| 9 | Motor W1: forward/reverse at 30% PWM | Spins correct direction |
| 10 | Motor W6: forward/reverse at 30% PWM | Spins correct direction |
| 11 | Motors W2+W3: forward/reverse | Both spin same direction |
| 12 | Motors W5+W4: forward/reverse | Both spin same direction |
| 13 | Servo FL: centres at 1500us, sweeps +/-35 deg | Smooth movement, no binding |
| 14 | Servo FR, RL, RR: same test | Smooth movement, no binding |
| 15 | E-stop during motor run: all motors stop | Stop within 20ms |
| 16 | Wheels on ground: low-speed drive test | Straight-line tracking |
| 17 | Articulation test: drive over 20mm obstacle | No wire snag at pivots |

### 10.4 Wire Length Estimates

| Connection | Approximate Length | Quantity |
|------------|-------------------|----------|
| Battery to fuse to switch to distribution | 200mm total | 1 set (2 wires) |
| Distribution to each L298N VCC/GND | 100-150mm | 4 wires |
| L298N motor output to each wheel motor | 400-500mm | 12 wires (6 motors x 2) |
| ESP32 to L298N #1 logic pins | 100-150mm | 6 wires |
| ESP32 to L298N #2 logic pins | 150-200mm | 6 wires |
| ESP32 to each servo signal | 200-400mm | 4 wires |
| 5V bus to each servo VCC/GND | 200-400mm | 8 wires (4 pairs) |
| Voltage divider to battery/GPIO14 | 100mm | 3 wires |
| E-stop button to ESP32 | 150mm | 2 wires |
| Encoder wires (if installed) | 400-500mm | 8 wires (4 per wheel) |

**Total wire needed**: ~8-10m of 22 AWG (signal), ~2m of 18 AWG (motor output), ~1m of 16 AWG (power distribution), ~0.5m of 14 AWG (battery run).

---

*Document EA-19 v1.0 -- 2026-03-15*
*Cross-references: EA-03 (Power System), EA-09 (GPIO Pin Map), EA-15 (Safety Systems)*
