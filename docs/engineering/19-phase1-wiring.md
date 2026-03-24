# Engineering Analysis 19: Phase 1 Complete Wiring Guide

**Document**: EA-19
**Date**: 2026-03-15
**Purpose**: Provide a complete, step-by-step wiring reference for the 0.4-scale Phase 1 prototype rover. This document contains everything needed to wire the rover from bare components to a fully connected system.
**Depends on**: EA-03 (Power System), EA-08 (Phase 1 Spec), EA-09 (GPIO Pin Map), EA-15 (Safety Systems)

---

## 1. Power Distribution Diagram

### 1.1 Main Power Path

```
                           PHASE 1 POWER DISTRIBUTION
                           ==========================

  +-----------+     +--------+     +--------+     +------------------+
  | 2S LiPo   |     | 5A     |     | Kill   |     | Power            |
  | 7.4V      +---->+ Blade  +---->+ Switch +---->+ Distribution     |
  | 2200mAh   |     | Fuse   |     | (rear) |     | (solder/terminal)|
  | XT60 plug |     +--------+     +--------+     +----+------+------+
  +-----------+                                        |      |
                                                       |      |
                         +-----------------------------+      |
                         |                                    |
                         v                                    v
                  +------+-------+                     +------+-------+
                  | L298N #1     |                     | L298N #2     |
                  | (Left side)  |                     | (Right side) |
                  |              |                     |              |
                  | VCC: 7.4V   |                     | VCC: 7.4V   |
                  | GND: common |                     | GND: common |
                  |              |                     |              |
                  | 5V OUT ------+------+              | 5V OUT      |
                  +--------------+      |              +--------------+
                                        |
                                        v
                               +--------+--------+
                               | 5V Power Bus    |
                               | (breadboard)    |
                               +--+-----------+--+
                                  |           |
                                  v           v
                           +------+--+  +----+--------+
                           | ESP32   |  | 4x SG90     |
                           | S3 VIN  |  | Servos      |
                           | (5V)    |  | (4.8-6V)    |
                           +---------+  +-------------+
```

### 1.2 Power Flow Summary

```
Battery 7.4V (2S LiPo, XT60)
    |
    +-- 5A blade fuse (inline, ATC/ATO holder)
    |
    +-- Kill switch (panel-mount toggle, rear wall, 15mm hole)
    |
    +-- L298N #1 VCC (left side: W1, W2+W3)
    |       |
    |       +-- 5V regulated output --> 5V bus
    |               |
    |               +-- ESP32-S3 VIN pin (5V)
    |               +-- SG90 FL servo VCC
    |               +-- SG90 FR servo VCC
    |               +-- SG90 RL servo VCC
    |               +-- SG90 RR servo VCC
    |
    +-- L298N #2 VCC (right side: W6, W5+W4)
    |
    +-- Voltage divider (10k + 4.7k) --> GPIO14 ADC
    |
    GND (common ground bus, star topology from battery negative)
```

### 1.3 Fuse and Protection Details

| Protection | Rating | Type | Location |
|------------|--------|------|----------|
| Main fuse | 5A | ATC blade fuse in holder | Inline between battery and kill switch |
| L298N internal | Built-in | Thermal shutdown | On each L298N board |
| ESP32 | USB fuse on DevKit | Onboard | DevKit PCB |

**Phase 1 simplification**: A single 5A main fuse is sufficient. Phase 1 max stall draw is ~4.2A (all 6 N20 motors stalled), so 5A provides protection while allowing normal operation. The L298N boards have built-in thermal protection. Per-rail fuses (EA-15 section 3.2) are added in Phase 2 when the power system is more complex.

### 1.4 L298N Jumper Configuration

```
L298N Board Jumper Settings (BOTH boards):

    +-----------------------------------------+
    |  L298N Motor Driver                     |
    |                                          |
    |  [VCC]  [GND]  [5V]                     |
    |    |      |      |                       |
    |    7.4V   GND    5V output               |
    |                                          |
    |  12V JUMPER: [ON] <-- MUST be ON         |
    |  (enables onboard 5V regulator)          |
    |  Only valid when VCC <= 12V              |
    |                                          |
    |  ENA  IN1  IN2  IN3  IN4  ENB           |
    |  PWM jumpers: REMOVE both               |
    |  (we control ENA/ENB from ESP32 PWM)    |
    +-----------------------------------------+

CRITICAL: Remove the ENA and ENB jumpers on both L298N boards.
These jumpers short ENA/ENB to 5V (always full speed).
We need PWM speed control, so ENA/ENB connect to ESP32 GPIO.
```

---

## 2. ESP32-S3 Complete Connection Table

### 2.1 Pin-by-Pin Reference

| GPIO | Function | Direction | Connects To | Wire Gauge | Connector | Notes |
|------|----------|-----------|-------------|------------|-----------|-------|
| 0 | Status LED | Output | WS2812B or onboard LED | 22 AWG | Dupont | Data pin; add 330R series resistor for WS2812B |
| 1 | Servo FL signal | Output | SG90 FL signal (orange) | 22 AWG | Dupont | 50 Hz PWM via LEDC Ch4 |
| 2 | Servo FR signal | Output | SG90 FR signal (orange) | 22 AWG | Dupont | 50 Hz PWM via LEDC Ch5 |
| 3 | *Spare* | -- | -- | -- | -- | Strapping pin, safe after boot |
| 4 | Motor LF PWM | Output | L298N #1 ENA | 22 AWG | Dupont | 1 kHz PWM, LEDC Ch0 |
| 5 | Motor LF DIR_A | Output | L298N #1 IN1 | 22 AWG | Dupont | HIGH/LOW for direction |
| 6 | Motor LF DIR_B | Output | L298N #1 IN2 | 22 AWG | Dupont | Opposite of IN1 |
| 7 | Motor LR PWM | Output | L298N #1 ENB | 22 AWG | Dupont | 1 kHz PWM, LEDC Ch1 |
| 8 | Motor RF PWM | Output | L298N #2 ENA | 22 AWG | Dupont | 1 kHz PWM, LEDC Ch2 |
| 9 | Motor RF DIR_A | Output | L298N #2 IN1 | 22 AWG | Dupont | HIGH/LOW for direction |
| 10 | Motor RF DIR_B | Output | L298N #2 IN2 | 22 AWG | Dupont | Opposite of IN1 |
| 11 | Motor RR PWM | Output | L298N #2 ENB | 22 AWG | Dupont | 1 kHz PWM, LEDC Ch3 |
| 12 | Motor RR DIR_A | Output | L298N #2 IN3 | 22 AWG | Dupont | HIGH/LOW for direction |
| 13 | Motor RR DIR_B | Output | L298N #2 IN4 | 22 AWG | Dupont | Opposite of IN3 |
| 14 | Battery ADC | Input | Voltage divider output | 22 AWG | Dupont | ADC1 Ch3, max 3.3V |
| 15 | Motor LR DIR_A | Output | L298N #1 IN3 | 22 AWG | Dupont | HIGH/LOW for direction |
| 16 | Motor LR DIR_B | Output | L298N #1 IN4 | 22 AWG | Dupont | Opposite of IN3 |
| 17 | *Spare* | -- | -- | -- | -- | |
| 18 | *Spare* | -- | -- | -- | -- | |
| 19 | USB D- | -- | USB-C connector | -- | -- | Programming, do not use |
| 20 | USB D+ | -- | USB-C connector | -- | -- | Programming, do not use |
| 21 | *Spare* | -- | -- | -- | -- | |
| 26-37 | **RESERVED** | -- | PSRAM/Flash (N16R8) | -- | -- | **DO NOT CONNECT** |
| 38 | Encoder W1 Ch-A | Input | FL motor encoder A | 22 AWG | Dupont | PCNT, optional |
| 39 | Encoder W1 Ch-B | Input | FL motor encoder B | 22 AWG | Dupont | PCNT, optional |
| 40 | Encoder W6 Ch-A | Input | FR motor encoder A | 22 AWG | Dupont | PCNT, optional |
| 41 | Servo RL signal | Output | SG90 RL signal (orange) | 22 AWG | Dupont | 50 Hz PWM via LEDC Ch6 |
| 42 | Servo RR signal | Output | SG90 RR signal (orange) | 22 AWG | Dupont | 50 Hz PWM via LEDC Ch7 |
| 43 | UART0 TX | Output | USB CDC (serial monitor) | -- | -- | Used by USB serial |
| 44 | UART0 RX | Input | USB CDC (serial monitor) | -- | -- | Used by USB serial |
| 45 | *Spare* | -- | -- | -- | -- | Strapping pin, avoid pull-up |
| 46 | E-stop button | Input | Tactile button to 3.3V | 22 AWG | Dupont | Input-only, internal pull-down |
| 47 | *Spare* | -- | -- | -- | -- | |
| 48 | Encoder W6 Ch-B | Input | FR motor encoder B | 22 AWG | Dupont | PCNT, optional |
| 5V | Power input | -- | L298N #1 5V output | 22 AWG | Dupont/screw | Powers ESP32 via VIN/5V pin |
| GND | Ground | -- | Common ground bus | 22 AWG | Dupont/screw | Connect to GND bus |

### 2.2 Pin Usage Summary

- **Motor control**: 12 pins (GPIO 4-13, 15-16)
- **Servo control**: 4 pins (GPIO 1, 2, 41, 42)
- **Encoders (optional)**: 4 pins (GPIO 38-40, 48)
- **Battery ADC**: 1 pin (GPIO 14)
- **E-stop**: 1 pin (GPIO 46)
- **Status LED**: 1 pin (GPIO 0)
- **USB**: 2 pins (GPIO 19-20)
- **Spare**: 6 pins (GPIO 3, 17, 18, 21, 45, 47)
- **Reserved (PSRAM)**: 12 pins (GPIO 26-37)

---

## 3. Motor Wiring (L298N)

### 3.1 L298N Board #1 (Left Side Motors)

```
                        L298N BOARD #1 (LEFT SIDE)
    ================================================================

    POWER SIDE:                         LOGIC SIDE:
    +--------+--------+---------+       +-----+-----+-----+-----+-----+-----+
    | +12V   | GND    | +5V OUT |       | ENA | IN1 | IN2 | IN3 | IN4 | ENB |
    +---+----+---+----+----+----+       +--+--+--+--+--+--+--+--+--+--+--+--+
        |        |         |               |     |     |     |     |     |
        |        |         |               |     |     |     |     |     |
      7.4V    GND bus   5V bus          GPIO4 GPIO5 GPIO6 GPIO15 GPIO16 GPIO7
     from      (common)  (to ESP32       (PWM)  (DIR)  (DIR)  (DIR)  (DIR)  (PWM)
     switch               + servos)

    MOTOR OUTPUT SIDE:
    +----------+-----------+----------+-----------+
    | OUT1     | OUT2      | OUT3     | OUT4      |
    +----+-----+-----+-----+----+-----+-----+----+
         |           |          |           |
         +-----+-----+          +-----+-----+
               |                      |
           W1 (FL)              W2+W3 (ML+RL)
         motor leads           motors in parallel
          (red/black)          (red to red, black to black)
```

**W2+W3 parallel wiring**: Solder the W2 and W3 motor leads together (red to red, black to black), then connect the joined pair to OUT3/OUT4. Both motors receive the same PWM and direction signal.

### 3.2 L298N Board #2 (Right Side Motors)

```
                        L298N BOARD #2 (RIGHT SIDE)
    ================================================================

    POWER SIDE:                         LOGIC SIDE:
    +--------+--------+---------+       +-----+-----+-----+-----+-----+-----+
    | +12V   | GND    | +5V OUT |       | ENA | IN1 | IN2 | IN3 | IN4 | ENB |
    +---+----+---+----+----+----+       +--+--+--+--+--+--+--+--+--+--+--+--+
        |        |         |               |     |     |     |     |     |
        |        |         |               |     |     |     |     |     |
      7.4V    GND bus    (NC or          GPIO8 GPIO9 GPIO10 GPIO12 GPIO13 GPIO11
     from      (common)  tie to           (PWM)  (DIR)  (DIR)  (DIR)  (DIR)  (PWM)
     switch              5V bus)

    MOTOR OUTPUT SIDE:
    +----------+-----------+----------+-----------+
    | OUT1     | OUT2      | OUT3     | OUT4      |
    +----+-----+-----+-----+----+-----+-----+----+
         |           |          |           |
         +-----+-----+          +-----+-----+
               |                      |
           W6 (FR)              W5+W4 (MR+RR)
         motor leads           motors in parallel
```

### 3.3 Motor Noise Suppression Capacitors

Install 100nF (0.1uF) ceramic capacitor across each motor's terminal pair (6x motors = 6 caps minimum). Solder directly to motor pins or as close as possible. Suppresses PWM noise that can affect ADC readings and WiFi.

```
EACH N20 MOTOR (x6):

    Motor terminal A ----+----[100nF]----+---- Motor terminal B
                         |               |
                    to L298N OUT      to L298N OUT

    Capacitor type: 100nF (104) ceramic disc or MLCC
    Voltage rating: 25V minimum (50V preferred)
    Placement: Solder directly across motor solder tabs
    If motor has 3 terminals: also add 100nF from each power terminal to case/ground tab
```

**Why this matters**: N20 DC motors generate significant electrical noise from brush commutation. Without suppression caps, this noise couples into the ESP32's ADC (causing erratic battery readings), disrupts WiFi (causing WebSocket disconnects), and can cause servo jitter.

### 3.4 Motor Direction Control Truth Table

| IN1 | IN2 | Motor Action |
|-----|-----|-------------|
| HIGH | LOW | Forward |
| LOW | HIGH | Reverse |
| LOW | LOW | Coast (free spin) |
| HIGH | HIGH | Brake (short circuit motor terminals) |

ENA/ENB control speed via PWM duty cycle (0-255 for 8-bit resolution).

### 3.5 Motor Wire Routing

```
ROUTING FROM BODY TO WHEELS:

Body (electronics bay)
    |
    +-- Cable channel (floor groove, 10x10mm)
    |
    +-- Through rocker arm pivot hole (leave slack for pivot motion)
    |       |
    |       +-- W1 motor (front, through steering bracket -- extra slack for steering rotation)
    |       |
    |       +-- Through bogie pivot (leave slack)
    |               |
    |               +-- W2 motor (middle, fixed mount)
    |               +-- W3 motor (rear, through steering bracket)
    |
    +-- Same routing for right side
```

**Wire length per motor**: Allow 400-500mm from L298N output terminal to motor. This accounts for routing through pivots with enough slack for full suspension and steering articulation.

---

## 4. Steering Servo Wiring

### 4.1 SG90 Servo Connections

Each SG90 servo has 3 wires:

| Wire Colour | Function | Connects To |
|-------------|----------|-------------|
| Orange/Yellow | Signal (PWM) | ESP32 GPIO (see table below) |
| Red | VCC (4.8-6V) | 5V power bus |
| Brown/Black | GND | Common ground bus |

### 4.2 Servo Pin Assignments

| Servo | Position | Signal GPIO | LEDC Channel | Timer |
|-------|----------|-------------|-------------|-------|
| FL steering | Front left, on rocker arm | GPIO 1 | Ch4 | Timer 1 |
| FR steering | Front right, on rocker arm | GPIO 2 | Ch5 | Timer 1 |
| RL steering | Rear left, on bogie arm | GPIO 41 | Ch6 | Timer 1 |
| RR steering | Rear right, on bogie arm | GPIO 42 | Ch7 | Timer 1 |

### 4.3 Servo Wiring Diagram

```
                    5V Power Bus (from L298N #1 5V output)
                    ==========================================
                         |        |        |        |
                        VCC      VCC      VCC      VCC
                         |        |        |        |
    ESP32 GPIO1 ---SIG--[FL]     |        |        |
    ESP32 GPIO2 ---SIG----------[FR]      |        |
    ESP32 GPIO41 --SIG-------------------[RL]      |
    ESP32 GPIO42 --SIG----------------------------[RR]
                         |        |        |        |
                        GND      GND      GND      GND
                         |        |        |        |
                    ==========================================
                    Common Ground Bus
```

### 4.4 Servo Power Considerations

The 4 SG90 servos can draw up to 2.6A peak (4 x 0.65A if all stalling simultaneously). The L298N 78M05 regulator is rated for 0.5A continuous, 1A peak — this is NOT enough for all servos.

**CRITICAL: The L298N's onboard 78M05 regulator is rated 0.5A continuous, but 4x SG90 servos can draw up to 2.6A peak. Add a dedicated 5V 3A buck converter module (XL4015 or similar, ~GBP 3) powered directly from the battery. Connect all servo VCC lines to BEC output, NOT to L298N 5V pin.**

```
RECOMMENDED 5V BEC WIRING:

    Battery 7.4V ----[5A Fuse]----[Kill Switch]----+
                                                    |
                                              +-----+-----+
                                              |           |
                                           L298N #1    L298N #2
                                           (motors)    (motors)
                                              |
                                              +----[XL4015 5V 3A BEC]----+
                                                       |                  |
                                                    5V OUT              GND
                                                       |                  |
                                              +--------+--------+        |
                                              |        |        |        |
                                           SG90 FL  SG90 FR  SG90 RL    |
                                              |        |     SG90 RR    |
                                              |        |        |        |
                                              +--------+--------+--------+
                                                     Common GND

    XL4015 module: Vin 7.4V, Vout 5.0V (adjust trim pot), Imax 3A
    Approximate cost: GBP 2-3 (eBay/AliExpress)
```

**For Phase 1 initial bench testing only** (rover on blocks, brief runs):
- Only 1-2 servos move at a time in normal use (~1A total)
- The L298N 5V output can handle this for basic testing
- If you see servos jittering or ESP32 brownout, the BEC is mandatory before further testing

---

## 5. Sensor Wiring

### 5.1 Battery Voltage Divider

```
BATTERY VOLTAGE MONITORING CIRCUIT:

    Battery + (7.4V) ----[10kR R1]----+----[4.7kR R2]---- GND
                                      |
                                      +---- GPIO14 (ADC)

    Components:
      R1 = 10kR (1/4W, 1% tolerance)
      R2 = 4.7kR (1/4W, 1% tolerance)

    Calculations:
      V_adc = V_bat x R2 / (R1 + R2)
      V_adc = 7.4 x 4.7 / 14.7 = 2.37V  (nominal)
      V_adc = 8.4 x 4.7 / 14.7 = 2.69V  (fully charged)
      V_adc = 6.4 x 4.7 / 14.7 = 2.05V  (cutoff)
      All within ESP32-S3 ADC range (0-3.3V)

    Scale factor in firmware: (R1 + R2) / R2 = 14.7 / 4.7 = 3.128
    V_bat = ADC_reading_volts x 3.128

    PLACEMENT: Build this on the mini breadboard.
    Solder R1 and R2 directly if desired, or use breadboard.
    Keep leads short to reduce noise.

    ADC FILTERING CAPACITOR (REQUIRED):
    Add 100nF ceramic cap between GPIO14 (battery sense ADC) and GND for ADC filtering.
    This smooths out PWM noise from motors and provides a stable ADC reading.
    Solder directly between the voltage divider midpoint and GND, as close
    to the ESP32 GPIO14 pin as possible.

    +---- GPIO14 ----+
    |                 |
    [4.7kR to GND]  [100nF to GND]
```

### 5.2 Encoder Wiring (Optional for Phase 1)

N20 motors with Hall effect encoders have 4 wires (in addition to the 2 motor power wires):

| Encoder Wire | Function | Connects To |
|-------------|----------|-------------|
| VCC | Encoder power | 3.3V (from ESP32 3.3V pin) |
| GND | Ground | Common ground bus |
| Ch-A | Pulse output A | ESP32 GPIO (see below) |
| Ch-B | Pulse output B (90-degree offset) | ESP32 GPIO (see below) |

```
ENCODER CONNECTIONS (only W1 and W6 for Phase 1):

    ESP32 3.3V ----+--------+----- Encoder W1 VCC
                   |        |
                   |        +----- Encoder W6 VCC
                   |
    GND bus -------+--------+----- Encoder W1 GND
                   |        |
                   |        +----- Encoder W6 GND
                   |
    GPIO38 --------+-------------- Encoder W1 Ch-A
    GPIO39 --------+-------------- Encoder W1 Ch-B
    GPIO40 --------+-------------- Encoder W6 Ch-A
    GPIO48 --------+-------------- Encoder W6 Ch-B
```

**Note**: Encoders are optional in Phase 1. Only install them on the front-left (W1) and front-right (W6) wheels for basic odometry. The ESP32-S3 PCNT hardware handles pulse counting without CPU load.

### 5.3 No I2C Sensors in Phase 1

Phase 1 does not include:
- BNO055 IMU (added in Phase 2, I2C on GPIO1/GPIO2)
- HC-SR04 ultrasonics (not used — Phase 2 uses LIDAR instead)
- INA219 current sensors (Phase 2)

GPIO1 and GPIO2 are used for servo signals in Phase 1. In Phase 2, servos move to the PCA9685 I2C PWM driver, freeing GPIO1/GPIO2 for the I2C bus.

---

## 6. E-Stop Circuit

### 6.1 Phase 1 E-Stop (Software Kill)

Phase 1 uses a simple tactile button that signals the ESP32 to stop all motors. This is a software E-stop, not a hardware power disconnect.

```
E-STOP CIRCUIT (Phase 1):

    ESP32 3.3V ----[10kR pull-up]----+---- GPIO46
                                     |
                                [Tactile Button]
                                     |
                                    GND

    Normal state: GPIO46 reads HIGH (pull-up to 3.3V)
    Button pressed: GPIO46 reads LOW (pulled to GND)

    WAIT -- GPIO46 has internal pull-DOWN, not pull-up.
    Revised circuit:

    ESP32 3.3V ----+
                   |
              [Tactile Button]
                   |
                   +---- GPIO46 (input-only, internal pull-down)

    Normal state: GPIO46 reads LOW (internal pull-down)
    Button pressed: GPIO46 reads HIGH (connected to 3.3V)

    In firmware: rising edge interrupt on GPIO46 toggles E-stop state.
```

### 6.2 E-Stop Behaviour

When E-stop is triggered:
1. All motor PWM immediately set to 0 (coast stop)
2. All servos hold current position
3. Status LED blinks red pattern
4. WebSocket broadcasts E-stop state to phone app
5. E-stop state persists until button pressed again AND resume command received

### 6.3 Future Phase 2+ Hardware E-Stop

```
PHASE 2+ HARDWARE E-STOP (for reference):

    Battery + ---[Fuse]---[E-Stop NC contacts]---[Relay/MOSFET]--- Motor power bus
                               |
                          [NC = Normally Closed]
                          [Red mushroom, twist-to-release]
                               |
                          Parallel signal wire to ESP32 GPIO46

    Effect: Physical power disconnect to motors even if ESP32 crashes.
    The mushroom button uses NC contacts so pressing OPENS the circuit.
```

---

## 7. UART to Jetson (Phase 2 Reference)

Phase 1 does not connect to a Jetson. This section is included for forward planning.

```
UART CONNECTION (Phase 2):

    ESP32-S3              Jetson Orin Nano
    =========             ================
    GPIO43 (TX) --------> RX (UART pin)
    GPIO44 (RX) <-------- TX (UART pin)
    GND         ---------- GND

    Baud rate: 115200
    Logic level: Both 3.3V -- NO level shifter needed
    Protocol: Binary UART (see EA-18)
    Wire: 22 AWG, keep under 300mm, twisted pair recommended
```

---

## 8. Connector Strategy

### 8.1 Connector Types by Application

| Application | Connector | Rating | Notes |
|-------------|-----------|--------|-------|
| Battery to rover | XT60 (male on battery, female on rover) | 60A continuous | Gold-plated, solder connection |
| Battery to fuse | Inline blade fuse holder | 5A | ATC/ATO standard automotive fuse |
| Fuse to kill switch | Ring terminals or spade connectors | 5A+ | 14 AWG crimp terminals |
| Kill switch to L298N | Screw terminals on L298N | 5A+ | 14 AWG stripped wire |
| L298N motor outputs | Screw terminals on L298N | 2A per channel | 16 AWG stripped wire |
| Motor leads | Direct solder | -- | Solder wires directly to N20 motor tabs |
| ESP32 to L298N logic | Dupont female-female | Signal level | Removable for debugging |
| ESP32 to servo signal | Dupont female-female | Signal level | Servo header is male |
| Servo power/ground | Dupont or breadboard | 1A per servo | From 5V BEC (see 4.4) |
| Encoder signals | Dupont female-female | Signal level | If encoders installed |
| Voltage divider | Breadboard or solder | -- | Resistors on mini breadboard |
| Motor-to-arm wiring | JST-XH 2-pin | 2A | Disconnect at body for arm removal |
| Servo extension | JST-XH 3-pin | 1A | Disconnect at arm pivot for servicing |
| BEC output to servo bus | JST-VH 2-pin | 3A | Positive-locking for main 5V distribution |

**JST Connector Notes**: Use JST-XH (2.5mm pitch) connectors at every point where wires cross a removable boundary (body-to-arm pivot, electronics tray). This allows arms to be detached for repair without desoldering. Pre-crimp 22 AWG wires into JST-XH housings. Use different pin counts or keying to prevent misconnection: 2-pin for motor pairs, 3-pin for servo extensions, 4-pin for encoder cables. Label both halves of each connector pair with matching numbers (M1, M2, ... S1, S2, ... E1, E2).

### 8.2 Development Phase Philosophy

For Phase 1 (prototype/dev):
- **Use Dupont connectors everywhere on signal lines** -- easy to disconnect, rearrange, and debug
- **Use screw terminals on L298N** -- provides solid connection without soldering to the board
- **Solder only where necessary** -- motor leads, fuse holder, kill switch
- **Label everything** -- use masking tape flags on wires with GPIO numbers written on them

### 8.3 Colour Code Convention

| Wire Colour | Function |
|-------------|----------|
| Red | Positive power (VCC, 5V, 7.4V) |
| Black | Ground (GND) |
| Orange | PWM signals (motor speed, servo position) |
| Yellow | Direction signals (motor IN1-IN4) |
| Green | Encoder signals |
| Blue | ADC / analogue signals |
| White | UART TX |
| Grey | UART RX |

Use this consistently. When you run out of coloured wire, use masking tape flags.

---

## 9. Wire Gauge Reference

From EA-03 section 5.4, adapted for Phase 1:

| Run | Max Current | Wire Gauge | Cross-Section | Resistance | Voltage Drop (500mm) |
|-----|-------------|------------|---------------|------------|---------------------|
| Battery to distribution | 10A (Phase 1) | 14 AWG | 2.08 mm2 | 8.29 R/km | 0.041V (0.6%) |
| Distribution to L298N VCC | 5A per board | 16 AWG | 1.31 mm2 | 13.2 R/km | 0.033V (0.4%) |
| L298N output to motor | 2A per channel | 18 AWG | 0.82 mm2 | 21.0 R/km | 0.021V (0.3%) |
| 5V bus to ESP32 | 0.5A | 22 AWG | 0.33 mm2 | 52.9 R/km | 0.013V (0.3%) |
| 5V bus to servos | 0.65A each | 22 AWG | 0.33 mm2 | 52.9 R/km | 0.017V (0.3%) |
| Signal wires (all) | <100 mA | 22 AWG | 0.33 mm2 | -- | Negligible |
| Encoder signals | <10 mA | 22-24 AWG | 0.20 mm2 | -- | Negligible |

**Phase 1 simplification**: Since the 2S LiPo only delivers 4-5A typical (10A absolute max with all motors stalling), 14 AWG for the battery run and 16 AWG for motor power is conservative and safe. All signal wires are 22 AWG Dupont jumper wire.

---

## 10. Cable Routing Notes

### 10.1 Routing Paths

```
TOP VIEW — CABLE ROUTING:

+--------------------------------------------+
|                                             |
|  [L298N #1]     [ESP32-S3]     [L298N #2]  |
|   Left side      Centre         Right side  |
|     |              |               |        |
|     |    [Mini Breadboard]         |        |
|     |   (voltage divider,          |        |
|     |    servo bus, E-stop)        |        |
|     |              |               |        |
|  ===+==============+===============+===     | <-- Floor cable channel
|     |              |               |        |     (10x10mm groove)
|     |         [2S LiPo]           |        |
|     |         [Battery]           |        |
|     |              |               |        |
|     |         [Kill Switch]        |        |
|     |         [Fuse holder]        |        |
+--+--+--+---+---+--+--+---+---+--+--+---+--+
   |     |   |   |     |   |   |     |   |
   W1    W2  W3  SG90s      W4  W5  W6  SG90s
```

### 10.2 Routing Rules

1. **Power wires (14-16 AWG)**: Run along the floor cable channel. Keep away from signal wires to reduce EMI.
2. **Signal wires (22 AWG)**: Bundle together with small cable ties. Route above or beside power wires, not twisted around them.
3. **Motor wires to wheels**: Route through the rocker arm tubes. Leave 50mm extra slack at each pivot point (body pivot, bogie pivot, steering pivot) to allow full articulation.
4. **Servo wires**: Route alongside motor wires through the arm tubes. Servo leads are typically 150mm long — extend with 22 AWG wire and Dupont connectors if needed.
5. **Strain relief**: Use hot glue or small cable clamps at pivot entry/exit points to prevent wire fatigue from repeated flexing.
6. **No tight bends**: Minimum bend radius of 10x wire diameter (about 5mm for 22 AWG).

### 10.3 Wire Length Estimates

| Connection | Approximate Length | Qty |
|------------|-------------------|-----|
| Battery to fuse to switch to L298N | 200mm total run | 1 set |
| L298N to each motor (via rocker/bogie) | 400-500mm | 6 (12 wires) |
| ESP32 to L298N #1 logic pins | 100-150mm | 6 wires |
| ESP32 to L298N #2 logic pins | 150-200mm | 6 wires |
| ESP32 to each servo signal | 200-400mm | 4 wires |
| 5V bus to each servo VCC/GND | 200-400mm | 8 wires (4 pairs) |
| Voltage divider to battery/GPIO14 | 100mm | 3 wires |
| E-stop button to ESP32 | 150mm | 2 wires |
| Encoder wires (if installed) | 400-500mm | 8 wires (4 per wheel) |

**Total wire needed**: Approximately 8-10 metres of 22 AWG (signal), 2 metres of 16 AWG (motor power), 0.5 metres of 14 AWG (battery). Buy a 10m roll of each.

---

## 11. Common Wiring Mistakes to Avoid

### 11.1 Power Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Reversed battery polarity | Destroys ESP32, L298N, servos | Always use keyed connectors (XT60). Double-check with multimeter before first power-on. |
| L298N ENA/ENB jumpers left ON | Motors run at full speed, uncontrollable | REMOVE both jumpers. Connect ENA/ENB to ESP32 PWM pins. |
| L298N 12V jumper removed when VCC < 12V | No 5V output, ESP32 has no power | Keep jumper ON when VCC is between 7-12V. Only remove if using external 5V supply. |
| Powering servos from ESP32 3.3V pin | Brownout/reset, insufficient current | Servos need 5V from L298N 5V output or dedicated BEC. |
| No common ground | Erratic behaviour, signals unreadable | ALL grounds must connect: battery GND, L298N GND, ESP32 GND, servo GND, encoder GND. |
| Undersized battery wire | Overheating, fire risk, voltage sag | Use 14 AWG minimum for battery runs. |

### 11.2 Signal Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Connecting to reserved GPIOs (26-37) | Board crashes, PSRAM fails | Mark GPIO 26-37 pins with tape. NEVER connect anything. |
| Motor direction wires swapped | Motor runs backwards | Not dangerous — fix in firmware by swapping IN1/IN2 logic, or swap wires. |
| Servo signal to wrong GPIO | Wrong wheel steers | Label every wire with GPIO number. |
| Long unshielded ADC wire | Noisy battery readings | Keep voltage divider close to ESP32. Add 100nF cap on ADC pin. |
| GPIO46 used as output | Pin damage | GPIO46 is INPUT ONLY. Never configure as output. |
| Forgetting pull-up/down on E-stop | Floating input, random triggers | GPIO46 has internal pull-down. Verify with multimeter before trusting. |

### 11.3 Mechanical Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Wires too short at pivots | Wire snaps on articulation | Add 50mm extra slack at every pivot. |
| Wires routed outside chassis | Snagged on obstacles | Route through internal cable channels. |
| No strain relief | Wire fatigue failure | Hot glue at pivot entry points. |
| Bare wire touching chassis | Short circuit | Use heat shrink on all solder joints. Use insulated wire throughout. |
| Servo plugged in backwards | Servo damaged or no function | SG90 plugs are keyed — match orange=signal, red=VCC, brown=GND. |

---

## 12. Test Procedures

### 12.1 Pre-Power Checklist

Perform ALL of these checks with a multimeter BEFORE connecting the battery for the first time.

**Step 1: Visual Inspection**
- [ ] All solder joints clean (no cold joints, no bridges)
- [ ] No bare wire exposed where it could short
- [ ] L298N ENA/ENB jumpers REMOVED
- [ ] L298N 12V jumper ON
- [ ] XT60 connector on battery lead is female (battery side is male)
- [ ] Fuse installed in holder (5A blade fuse)
- [ ] Kill switch in OFF position

**Step 2: Continuity Checks (multimeter in continuity/beep mode)**
- [ ] Battery positive to L298N #1 VCC: continuity THROUGH fuse and switch (switch ON)
- [ ] Battery positive to L298N #2 VCC: continuity THROUGH fuse and switch
- [ ] Battery negative to L298N #1 GND: continuity
- [ ] Battery negative to L298N #2 GND: continuity
- [ ] Battery negative to ESP32 GND: continuity
- [ ] No continuity between battery positive and GND (NO SHORT CIRCUIT)
- [ ] No continuity between 5V bus and GND
- [ ] No continuity between any ESP32 GPIO and GND (unless intentional pull-down)
- [ ] No continuity between any ESP32 GPIO and VCC

**Step 3: Resistance Checks**
- [ ] Voltage divider: measure R1 (should read ~10kR between battery+ and ADC node)
- [ ] Voltage divider: measure R2 (should read ~4.7kR between ADC node and GND)
- [ ] E-stop button: infinite resistance when open, ~0R when pressed

### 12.2 First Power-On Sequence

Do this in order. Stop immediately if anything is unexpected.

1. **Kill switch OFF**. Connect battery via XT60.
2. **Measure battery voltage** at L298N #1 VCC terminal (should read 7.4-8.4V, switch still OFF).
   - If zero: fuse blown or bad connection. Debug.
3. **Turn kill switch ON**. Measure again at L298N VCC.
   - Should read battery voltage (7.4-8.4V).
4. **Measure 5V output** at L298N #1 5V pin.
   - Should read 4.8-5.2V. If zero: 12V jumper is off, or VCC is too high.
5. **Measure ESP32 VIN** pin.
   - Should read 4.8-5.2V. Power LED on DevKit should illuminate.
6. **Measure GPIO14 (ADC)** voltage.
   - Should read ~2.0-2.7V (battery voltage / 3.128). If 0V: divider wiring wrong.
7. **Check no magic smoke**. Feel L298N boards and ESP32 — if anything is hot, power off immediately.

### 12.3 Motor Testing Sequence

Test each motor INDIVIDUALLY before enabling all:

1. Upload firmware with simple test sketch (one motor at a time, low PWM)
2. **Motor W1 (FL)**: Command forward at 30% speed
   - Verify wheel spins in expected direction
   - If backwards: swap IN1/IN2 wires or fix in firmware
   - Verify speed changes with PWM (30%, 50%, 100%)
3. Repeat for Motor W6 (FR), then W2+W3 (left mid+rear), then W5+W4 (right mid+rear)
4. **Test motor brake**: set both IN1=HIGH, IN2=HIGH — wheel should resist turning
5. **Test motor coast**: set both IN1=LOW, IN2=LOW — wheel should spin freely
6. **Measure current draw**: connect multimeter in series with one L298N motor output
   - Free spin at 100%: should be <0.2A
   - Stalled: should be <0.7A per motor. If higher, something is binding.

### 12.4 Servo Testing Sequence

1. **Centre all servos** before mounting: send 1500us pulse to each servo
2. **Sweep test**: slowly sweep from 500us to 2400us
   - Verify full rotation range (~180 degrees for SG90)
   - Listen for grinding (indicates mechanical stop contact)
3. **Mount servos**: align steering to straight-ahead at 1500us centre position
4. **Steering range test**: command +35 and -35 degrees
   - Verify no mechanical binding with suspension arms
   - Adjust centre trim in firmware if wheels are not straight at 1500us

### 12.5 System Integration Test

Once individual motors and servos are verified:

1. Place rover on blocks (wheels off the ground)
2. Command forward at 50% — all wheels should spin same direction
3. Command reverse — all wheels reverse
4. Command left turn — left wheels slow/reverse, right wheels forward
5. Command right turn — opposite of left
6. Command steering — front and rear wheels should toe appropriately
7. **E-stop test**: while motors are running, press E-stop button
   - All motors must stop within 20ms
   - Servos hold position
   - Status LED blinks
8. **Battery monitor test**: read ADC value, verify it matches multimeter reading (within 5%)
9. **Place on ground**: test low-speed driving on flat surface
10. **Obstacle test**: drive over small obstacles (book, 20mm ramp) to verify suspension articulates without wire snag

---

## 13. Complete Wiring Checklist

Use this checklist during assembly. Check off each connection as you make it.

### Power Connections
- [ ] Battery XT60 female soldered to 14 AWG leads (red=+, black=-)
- [ ] 5A blade fuse holder inline on positive lead
- [ ] Kill switch wired inline on positive lead (after fuse)
- [ ] Positive lead splits to L298N #1 VCC and L298N #2 VCC
- [ ] Negative lead connects to common GND bus
- [ ] L298N #1 GND to GND bus
- [ ] L298N #2 GND to GND bus
- [ ] L298N #1 5V output to 5V power bus
- [ ] ESP32 VIN/5V pin to 5V bus
- [ ] ESP32 GND to GND bus
- [ ] 4x servo VCC (red) to 5V bus
- [ ] 4x servo GND (brown) to GND bus

### Motor Connections (L298N #1 — Left)
- [ ] GPIO4 to L298N #1 ENA (PWM, left front)
- [ ] GPIO5 to L298N #1 IN1
- [ ] GPIO6 to L298N #1 IN2
- [ ] GPIO7 to L298N #1 ENB (PWM, left mid+rear)
- [ ] GPIO15 to L298N #1 IN3
- [ ] GPIO16 to L298N #1 IN4
- [ ] W1 motor leads to L298N #1 OUT1/OUT2
- [ ] W2 motor leads (parallel with W3) to L298N #1 OUT3/OUT4
- [ ] W3 motor leads (parallel with W2) to L298N #1 OUT3/OUT4

### Motor Connections (L298N #2 — Right)
- [ ] GPIO8 to L298N #2 ENA (PWM, right front)
- [ ] GPIO9 to L298N #2 IN1
- [ ] GPIO10 to L298N #2 IN2
- [ ] GPIO11 to L298N #2 ENB (PWM, right mid+rear)
- [ ] GPIO12 to L298N #2 IN3
- [ ] GPIO13 to L298N #2 IN4
- [ ] W6 motor leads to L298N #2 OUT1/OUT2
- [ ] W5 motor leads (parallel with W4) to L298N #2 OUT3/OUT4
- [ ] W4 motor leads (parallel with W5) to L298N #2 OUT3/OUT4

### Servo Signal Connections
- [ ] GPIO1 to SG90 FL signal (orange wire)
- [ ] GPIO2 to SG90 FR signal (orange wire)
- [ ] GPIO41 to SG90 RL signal (orange wire)
- [ ] GPIO42 to SG90 RR signal (orange wire)

### Sensor Connections
- [ ] 10kR resistor from battery+ to breadboard node
- [ ] 4.7kR resistor from breadboard node to GND
- [ ] GPIO14 to breadboard node (voltage divider midpoint)
- [ ] 100nF capacitor from GPIO14 to GND (ADC filtering)

### E-Stop Connection
- [ ] Tactile button between 3.3V and GPIO46

### Encoder Connections (Optional)
- [ ] Encoder W1 VCC to ESP32 3.3V
- [ ] Encoder W1 GND to GND bus
- [ ] Encoder W1 Ch-A to GPIO38
- [ ] Encoder W1 Ch-B to GPIO39
- [ ] Encoder W6 VCC to ESP32 3.3V
- [ ] Encoder W6 GND to GND bus
- [ ] Encoder W6 Ch-A to GPIO40
- [ ] Encoder W6 Ch-B to GPIO48

### Final Checks
- [ ] All L298N ENA/ENB jumpers REMOVED
- [ ] L298N 12V jumper ON (both boards)
- [ ] No wire touching GPIO 26-37 (PSRAM reserved)
- [ ] All solder joints heat-shrinked
- [ ] Wire slack at all pivot points
- [ ] Strain relief at pivot entries
- [ ] All wires labelled with GPIO numbers

---

*Document EA-19 v1.0 -- 2026-03-15*
