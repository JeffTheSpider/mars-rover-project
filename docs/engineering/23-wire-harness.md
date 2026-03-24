# Engineering Analysis 23: Wire Harness Specification

**Document**: EA-23
**Date**: 2026-03-23
**Purpose**: Define every wire, connector, colour code, routing path, and build sequence for the Phase 1 (0.4-scale) rover wire harness. This document provides a manufacturing-ready wire schedule so each harness can be cut, crimped, labelled, and tested before installation.
**Depends on**: EA-08 (Phase 1 Spec), EA-09 (GPIO Pin Map), EA-15 (Safety Systems), EA-19 (Phase 1 Wiring Guide)

---

## 1. Wire Schedule

All lengths include a 50mm service loop. Wire IDs use the format W001-W999. Lengths are measured from the electronics tray centre to destination unless otherwise noted.

### 1.1 Power Harness (Battery to Distribution)

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W001 | Battery + | Fuse holder (in) | 14 | Red | 100 | XT60 female | Spade / solder | Battery main positive |
| W002 | Battery - | GND bus | 14 | Black | 100 | XT60 female | Screw terminal | Battery main negative |
| W003 | Fuse holder (out) | Kill switch (in) | 14 | Red | 80 | Solder | Spade terminal | 5A ATC blade fuse |
| W004 | Kill switch (out) | Power distribution | 14 | Red | 80 | Spade terminal | Solder junction | Rear panel toggle switch |

### 1.2 Power Distribution (to Motor Drivers)

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W005 | Power distribution + | L298N #1 VCC | 16 | Red | 120 | Solder junction | Screw terminal | Left-side motor driver |
| W006 | GND bus | L298N #1 GND | 16 | Black | 120 | Solder junction | Screw terminal | Common ground |
| W007 | Power distribution + | L298N #2 VCC | 16 | Red | 150 | Solder junction | Screw terminal | Right-side motor driver |
| W008 | GND bus | L298N #2 GND | 16 | Black | 150 | Solder junction | Screw terminal | Common ground |

### 1.3 5V BEC / Regulator Output

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W009 | L298N #1 5V out | 5V bus (breadboard) | 22 | Red | 80 | Screw terminal | Breadboard | L298N onboard 78M05 regulator |
| W010 | L298N #1 GND | 5V bus GND rail | 22 | Black | 80 | Screw terminal | Breadboard | Shared ground reference |
| W011 | 5V bus | Servo VCC rail | 22 | Red | 60 | Breadboard | Breadboard | Distribution to all 4 servos |
| W012 | GND bus | Servo GND rail | 22 | Black | 60 | Breadboard | Breadboard | Common servo ground |

### 1.4 Motor Wires (6 motors, 2 wires each)

Motor positions relative to electronics tray centre:
- FL (W1): ~300mm (through rocker arm, steering bracket, longest front run)
- ML (W2): ~200mm (through rocker arm to bogie, mid-wheel fixed mount)
- RL (W3): ~250mm (through rocker arm, bogie arm, steering bracket)
- FR (W6): ~300mm (mirror of FL, right side)
- MR (W5): ~200mm (mirror of ML, right side)
- RR (W4): ~250mm (mirror of RL, right side)

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W013 | L298N #1 OUT1 | Motor W1 (FL) + | 20 | Red | 350 | Screw terminal | Solder to motor tab | Left front motor positive |
| W014 | L298N #1 OUT2 | Motor W1 (FL) - | 20 | Black | 350 | Screw terminal | Solder to motor tab | Left front motor negative |
| W015 | L298N #1 OUT3 | Motor W2 (ML) + (parallel W3) | 20 | Red | 250 | Screw terminal | Solder (Y-splice) | Left mid motor positive |
| W016 | L298N #1 OUT4 | Motor W2 (ML) - (parallel W3) | 20 | Black | 250 | Screw terminal | Solder (Y-splice) | Left mid motor negative |
| W017 | Y-splice (W015) | Motor W3 (RL) + | 20 | Red | 300 | Solder junction | Solder to motor tab | Left rear motor positive |
| W018 | Y-splice (W016) | Motor W3 (RL) - | 20 | Black | 300 | Solder junction | Solder to motor tab | Left rear motor negative |
| W019 | L298N #2 OUT1 | Motor W6 (FR) + | 20 | Red | 350 | Screw terminal | Solder to motor tab | Right front motor positive |
| W020 | L298N #2 OUT2 | Motor W6 (FR) - | 20 | Black | 350 | Screw terminal | Solder to motor tab | Right front motor negative |
| W021 | L298N #2 OUT3 | Motor W5 (MR) + (parallel W4) | 20 | Red | 250 | Screw terminal | Solder (Y-splice) | Right mid motor positive |
| W022 | L298N #2 OUT4 | Motor W5 (MR) - (parallel W4) | 20 | Black | 250 | Screw terminal | Solder (Y-splice) | Right mid motor negative |
| W023 | Y-splice (W021) | Motor W4 (RR) + | 20 | Red | 300 | Solder junction | Solder to motor tab | Right rear motor positive |
| W024 | Y-splice (W022) | Motor W4 (RR) - | 20 | Black | 300 | Solder junction | Solder to motor tab | Right rear motor negative |

**Note**: W2+W3 (left mid + rear) are wired in parallel from L298N #1 channel B. W5+W4 (right mid + rear) are wired in parallel from L298N #2 channel B. The Y-splice is made by soldering both motor leads to a single wire, then heat-shrinking the junction.

### 1.5 Servo Signal Wires

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W025 | ESP32 GPIO1 | Servo FL signal | 26 | Orange | 350 | Dupont F | Servo header (M) | LEDC Ch4, 50Hz PWM |
| W026 | ESP32 GPIO2 | Servo FR signal | 26 | Orange | 350 | Dupont F | Servo header (M) | LEDC Ch5, 50Hz PWM |
| W027 | ESP32 GPIO41 | Servo RL signal | 26 | Orange | 400 | Dupont F | Servo header (M) | LEDC Ch6, 50Hz PWM |
| W028 | ESP32 GPIO42 | Servo RR signal | 26 | Orange | 400 | Dupont F | Servo header (M) | LEDC Ch7, 50Hz PWM |

### 1.6 Servo Power Wires

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W029 | 5V bus | Servo FL VCC | 22 | Red | 350 | Breadboard | Servo header (M) | 5V from L298N regulator |
| W030 | GND bus | Servo FL GND | 22 | Black | 350 | Breadboard | Servo header (M) | Common ground |
| W031 | 5V bus | Servo FR VCC | 22 | Red | 350 | Breadboard | Servo header (M) | |
| W032 | GND bus | Servo FR GND | 22 | Black | 350 | Breadboard | Servo header (M) | |
| W033 | 5V bus | Servo RL VCC | 22 | Red | 400 | Breadboard | Servo header (M) | |
| W034 | GND bus | Servo RL GND | 22 | Black | 400 | Breadboard | Servo header (M) | |
| W035 | 5V bus | Servo RR VCC | 22 | Red | 400 | Breadboard | Servo header (M) | |
| W036 | GND bus | Servo RR GND | 22 | Black | 400 | Breadboard | Servo header (M) | |

### 1.7 ESP32 Power

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W037 | 5V bus | ESP32 5V/VIN pin | 22 | Red | 100 | Breadboard | Dupont F | Powers ESP32 from L298N 5V |
| W038 | GND bus | ESP32 GND pin | 22 | Black | 100 | Breadboard | Dupont F | Common ground |

### 1.8 Battery Sense (ADC)

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W039 | Battery + (via 10k resistor) | Voltage divider midpoint | 26 | Brown | 80 | Solder (R1) | Breadboard node | R1 = 10k, 1% tolerance |
| W040 | Voltage divider midpoint | GND (via 4.7k resistor) | 26 | Black | 30 | Breadboard node | Solder (R2) | R2 = 4.7k, 1% tolerance |
| W041 | Voltage divider midpoint | ESP32 GPIO14 | 26 | Brown | 80 | Breadboard node | Dupont F | ADC1 Ch3, keep short |
| W042 | GPIO14 to GND (100nF cap) | — | — | — | — | — | — | Ceramic cap, solder on breadboard |

### 1.9 L298N #1 Control Signals (Left-Side Motors)

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W043 | ESP32 GPIO4 | L298N #1 ENA | 26 | Yellow | 120 | Dupont F | Dupont F | PWM, LEDC Ch0 (LF motor speed) |
| W044 | ESP32 GPIO5 | L298N #1 IN1 | 26 | Yellow | 120 | Dupont F | Dupont F | LF motor direction A |
| W045 | ESP32 GPIO6 | L298N #1 IN2 | 26 | Yellow | 120 | Dupont F | Dupont F | LF motor direction B |
| W046 | ESP32 GPIO7 | L298N #1 ENB | 26 | Yellow | 120 | Dupont F | Dupont F | PWM, LEDC Ch1 (LR motor speed) |
| W047 | ESP32 GPIO15 | L298N #1 IN3 | 26 | Yellow | 120 | Dupont F | Dupont F | LR motor direction A |
| W048 | ESP32 GPIO16 | L298N #1 IN4 | 26 | Yellow | 120 | Dupont F | Dupont F | LR motor direction B |

### 1.10 L298N #2 Control Signals (Right-Side Motors)

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W049 | ESP32 GPIO8 | L298N #2 ENA | 26 | Yellow | 170 | Dupont F | Dupont F | PWM, LEDC Ch2 (RF motor speed) |
| W050 | ESP32 GPIO9 | L298N #2 IN1 | 26 | Yellow | 170 | Dupont F | Dupont F | RF motor direction A |
| W051 | ESP32 GPIO10 | L298N #2 IN2 | 26 | Yellow | 170 | Dupont F | Dupont F | RF motor direction B |
| W052 | ESP32 GPIO11 | L298N #2 ENB | 26 | Yellow | 170 | Dupont F | Dupont F | PWM, LEDC Ch3 (RR motor speed) |
| W053 | ESP32 GPIO12 | L298N #2 IN3 | 26 | Yellow | 170 | Dupont F | Dupont F | RR motor direction A |
| W054 | ESP32 GPIO13 | L298N #2 IN4 | 26 | Yellow | 170 | Dupont F | Dupont F | RR motor direction B |

### 1.11 E-Stop and Indicators

| Wire ID | From | To | AWG | Colour | Length (mm) | Connector (From) | Connector (To) | Notes |
|---------|------|----|-----|--------|-------------|-------------------|-----------------|-------|
| W055 | ESP32 3.3V | E-stop button (one leg) | 24 | Red | 150 | Dupont F | Solder | GPIO46 has internal pull-down |
| W056 | E-stop button (other leg) | ESP32 GPIO46 | 24 | White | 150 | Solder | Dupont F | Active HIGH when pressed |
| W057 | ESP32 GPIO0 | Power LED anode (via 330R) | 24 | Red | 100 | Dupont F | Solder (LED) | Status LED / NeoPixel data |
| W058 | Power LED cathode | GND bus | 24 | Black | 100 | Solder (LED) | Breadboard | Return path |

### 1.12 Wire Schedule Summary

| Category | Wire IDs | Wire Count | Total Length (m) |
|----------|----------|------------|-----------------|
| Battery power | W001-W004 | 4 | 0.36 |
| Driver power | W005-W008 | 4 | 0.54 |
| 5V distribution | W009-W012 | 4 | 0.28 |
| Motor leads | W013-W024 | 12 | 3.60 |
| Servo signal | W025-W028 | 4 | 1.50 |
| Servo power | W029-W036 | 8 | 3.00 |
| ESP32 power | W037-W038 | 2 | 0.20 |
| Battery sense | W039-W042 | 3+cap | 0.19 |
| L298N #1 control | W043-W048 | 6 | 0.72 |
| L298N #2 control | W049-W054 | 6 | 1.02 |
| E-stop + LED | W055-W058 | 4 | 0.50 |
| **TOTAL** | **W001-W058** | **57 wires + 1 cap** | **~11.9 m** |

**Purchase recommendation**: 15m of 22 AWG stranded (signal, servo power), 5m of 20 AWG stranded (motors, indicators), 3m of 26 AWG stranded (GPIO signals), 2m of 14 AWG stranded (battery, fuse, switch), 2m of 16 AWG stranded (driver power). Buy multi-colour packs.

---

## 2. Connector Schedule

| Connector ID | Type | Pin Count | Location | Connects To | Crimp/Solder |
|-------------|------|-----------|----------|-------------|--------------|
| C001 | XT60 female (rover side) | 2 | Battery bay, body floor | Battery XT60 male | Solder |
| C002 | Inline ATC fuse holder | 2 | Between battery and switch | W001 positive, W003 positive | Solder / crimp spade |
| C003 | Panel-mount toggle switch | 2 | Rear body wall, 15mm hole | W003 (in), W004 (out) | Spade terminal |
| C004 | L298N #1 screw terminal (power) | 3 | L298N #1 board | VCC (W005), GND (W006), 5V out (W009) | Stripped wire |
| C005 | L298N #1 screw terminal (motors) | 4 | L298N #1 board | OUT1-OUT4 (W013-W016) | Stripped wire |
| C006 | L298N #1 header (logic) | 6 | L298N #1 board | ENA, IN1-IN4, ENB (W043-W048) | Dupont F |
| C007 | L298N #2 screw terminal (power) | 3 | L298N #2 board | VCC (W007), GND (W008), 5V (NC) | Stripped wire |
| C008 | L298N #2 screw terminal (motors) | 4 | L298N #2 board | OUT1-OUT4 (W019-W022) | Stripped wire |
| C009 | L298N #2 header (logic) | 6 | L298N #2 board | ENA, IN1-IN4, ENB (W049-W054) | Dupont F |
| C010 | ESP32 header (left) | — | ESP32-S3 DevKitC-1 | GPIO0-18 pins as needed | Dupont F |
| C011 | ESP32 header (right) | — | ESP32-S3 DevKitC-1 | GPIO38-48, 5V, GND | Dupont F |
| C012 | SG90 FL header | 3 | Servo connector (keyed) | VCC (W029), GND (W030), SIG (W025) | Dupont F into servo plug |
| C013 | SG90 FR header | 3 | Servo connector (keyed) | VCC (W031), GND (W032), SIG (W026) | Dupont F into servo plug |
| C014 | SG90 RL header | 3 | Servo connector (keyed) | VCC (W033), GND (W034), SIG (W027) | Dupont F into servo plug |
| C015 | SG90 RR header | 3 | Servo connector (keyed) | VCC (W035), GND (W036), SIG (W028) | Dupont F into servo plug |
| C016 | Tactile push button | 2 | Top deck or rear panel | E-stop: 3.3V (W055), GPIO46 (W056) | Solder |
| C017 | 5mm LED + 330R resistor | 2 | Front panel or top deck | Status: GPIO0 (W057), GND (W058) | Solder |
| C018 | Mini breadboard | — | Electronics tray centre | Voltage divider, 5V/GND bus | Push-fit |

### 2.1 Connector Purchasing List

| Type | Quantity | Source | Notes |
|------|----------|--------|-------|
| XT60 male+female pair | 2 pairs | AliExpress | Gold-plated, pre-tinned leads |
| ATC/ATO inline fuse holder | 1 | Amazon/eBay | With 5A blade fuse |
| Panel-mount toggle switch | 1 | Amazon | SPST, 15mm panel hole, 10A rating |
| Dupont female-female jumper 20cm | 40 | AliExpress | Multi-colour pack |
| Dupont female-female jumper 30cm | 20 | AliExpress | For longer servo/motor runs |
| Mini breadboard (170 tie points) | 1 | Amazon | For voltage divider and bus |
| Tactile push button (12mm) | 1 | Amazon | Panel-mount preferred |
| 5mm LED (green or white) | 1 | Component kit | For power/status indicator |
| 330R resistor | 1 | Component kit | LED current limiter |
| 10k resistor (1%) | 1 | Component kit | Voltage divider R1 |
| 4.7k resistor (1%) | 1 | Component kit | Voltage divider R2 |
| 100nF ceramic capacitor | 7 | Component kit | 6 for motor noise + 1 for ADC filter |
| Heat-shrink tubing assorted | 1 pack | Amazon | 2:1 ratio, 2-6mm diameters |

---

## 3. Colour Code Standard

| Colour | Purpose | Used By |
|--------|---------|---------|
| Red | VCC / Positive power (7.4V, 5V, 3.3V) | W001, W003-W005, W007, W009, W011, W029, W031, W033, W035, W037, W055 |
| Black | GND / Negative / Return | W002, W006, W008, W010, W012, W014, W016, W018, W020, W022, W024, W030, W032, W034, W036, W038, W040, W058 |
| Yellow | Motor control signals (PWM, DIR) | W043-W054 (L298N ENA/ENB, IN1-IN4) |
| Orange | Servo signal (PWM) | W025-W028 (GPIO to servo headers) |
| Brown | Analog / sensor signals | W039, W041 (battery ADC) |
| White | E-stop / special signals | W056 (E-stop to GPIO46) |
| Green | Encoder signal (Phase 2) | Reserved for GPIO38-40, GPIO48 |
| Blue | I2C SDA (Phase 2) | Reserved for GPIO1 (when servos move to PCA9685) |

### 3.1 Colour Code Fallback

When coloured wire is unavailable, use masking tape flags every 100mm with these markings:

| Flag Label | Meaning |
|------------|---------|
| `+` | Positive power |
| `-` or `G` | Ground |
| `P` + number | PWM signal (e.g., `P4` = GPIO4 PWM) |
| `D` + number | Direction signal (e.g., `D5` = GPIO5 DIR) |
| `S` + number | Servo signal (e.g., `S1` = GPIO1 servo FL) |
| `A` | ADC / analog |
| `E` | E-stop |

---

## 4. Cable Routing

### 4.1 Body Quadrant Exit Points

Each body quadrant has cable exit slots (10x10mm grooves in the floor and side walls). Wires are grouped by destination and routed through the nearest quadrant exit.

#### FL Body Quadrant (Front-Left)

| Wire IDs | Description | Count |
|----------|-------------|-------|
| W013, W014 | Motor W1 (FL) power | 2 |
| W025, W029, W030 | Servo FL (signal + VCC + GND) | 3 |
| **Total** | | **5 wires** |

Route: Exit through floor slot at Y=+180mm, X=-100mm. Run along left rocker arm tube to front wheel / steering bracket.

#### FR Body Quadrant (Front-Right)

| Wire IDs | Description | Count |
|----------|-------------|-------|
| W019, W020 | Motor W6 (FR) power | 2 |
| W026, W031, W032 | Servo FR (signal + VCC + GND) | 3 |
| W057, W058 | Headlight / status LED (if mounted front) | 2 |
| **Total** | | **7 wires** |

Route: Exit through floor slot at Y=+180mm, X=+100mm. Run along right rocker arm tube to front wheel / steering bracket. LED wires exit through front wall hole.

#### RL Body Quadrant (Rear-Left)

| Wire IDs | Description | Count |
|----------|-------------|-------|
| W015, W016, W017, W018 | Motors W2+W3 (ML+RL) power | 4 |
| W027, W033, W034 | Servo RL (signal + VCC + GND) | 3 |
| **Total** | | **7 wires** |

Route: Exit through floor slot at Y=-90mm, X=-100mm. W2 motor wires branch off at the bogie pivot (mid-wheel fixed mount). W3 motor wires and servo RL wires continue along the bogie arm to the rear steering bracket. Taillight wires (if installed) exit through rear wall.

#### RR Body Quadrant (Rear-Right)

| Wire IDs | Description | Count |
|----------|-------------|-------|
| W021, W022, W023, W024 | Motors W5+W4 (MR+RR) power | 4 |
| W028, W035, W036 | Servo RR (signal + VCC + GND) | 3 |
| **Total** | | **7 wires** |

Route: Mirror of RL quadrant. Exit through floor slot at Y=-90mm, X=+100mm. W5 branches at bogie pivot; W4 and servo RR continue to rear steering bracket.

#### Bottom (Electronics Tray Access)

| Wire IDs | Description | Count |
|----------|-------------|-------|
| W001-W012 | All power wiring (battery, fuses, distribution, BEC) | 12 |
| W037-W042 | ESP32 power and battery sense | 5 |
| W043-W054 | All L298N control signals | 12 |
| **Total** | | **29 wires** |

These wires stay inside the electronics tray and do not exit the body. The L298N boards, ESP32, and breadboard are all mounted on the tray floor.

#### Top (Accessible from Above)

| Wire IDs | Description | Count |
|----------|-------------|-------|
| W055, W056 | E-stop button | 2 |
| W057, W058 | Power/status LED (if top-mounted) | 2 |
| USB-C cable | ESP32 programming / serial debug | 1 cable |
| **Total** | | **4 wires + 1 cable** |

Route through top deck openings or rear panel cutouts. The E-stop button mounts on the top deck or rear wall. USB-C exits through a slot in the rear wall for programming access.

### 4.2 Cable Routing Map (Top View)

```
+--------------------------------------------------+
|  FL Quadrant           |          FR Quadrant     |
|                        |                          |
|  [5 wires]             |              [7 wires]   |
|   exit ←               |               → exit    |
|                        |                          |
|       [L298N #1]   [ESP32-S3]   [L298N #2]       |
|        Left side    (centre)     Right side       |
|           ↑    ↖      ↑↓      ↗     ↑            |
|           |      [Mini Breadboard]    |            |
|           |    (5V bus, divider,      |            |
|           |     servo distribution)   |            |
|           |            |              |            |
|  [7 wires]       [2S LiPo]          [7 wires]    |
|   exit ←          Battery             → exit      |
|                   [Kill Sw]                        |
|  RL Quadrant      [Fuse]      RR Quadrant         |
|                        |                          |
+--------------------------------------------------+

            E-stop + USB-C exit top/rear
```

### 4.3 Pivot Routing Rules

Wires pass through three pivot points on each side. Each pivot requires extra slack to accommodate full articulation without wire fatigue.

| Pivot Point | Rotation Range | Extra Slack Required | Strain Relief |
|-------------|---------------|---------------------|---------------|
| Body-to-rocker pivot | ~30 degrees | +40mm loop | Hot glue anchor 20mm before pivot hole |
| Rocker-to-bogie pivot | ~30 degrees | +40mm loop | Hot glue anchor 20mm before pivot hole |
| Steering pivot (servo) | +/-35 degrees | +30mm loop | Secure to arm with cable tie, leaving loop at servo bracket |

**Critical**: The 50mm service loop in the wire schedule already accounts for general slack. The pivot slack is in addition -- wire lengths in Section 1 already include this allowance.

---

## 5. Wire Length Calculations

All measurements from the electronics tray centre (approximately X=0, Y=0, Z=+40mm inside the body).

### 5.1 Measurement Method

```
Wire length = Path distance (tray → exit slot → arm routing → destination)
            + 50mm service loop
            + pivot slack allowances (included in path estimate)
```

### 5.2 Detailed Length Derivations

#### Motor W1 (FL) -- Wires W013, W014

| Segment | Distance | Path |
|---------|----------|------|
| Tray centre to L298N #1 OUT1 | 60mm | Across tray to left-side driver |
| L298N #1 to FL floor exit slot | 40mm | Down and through cable channel |
| Floor exit to body pivot | 50mm | Along body floor to rocker mount |
| Through rocker arm to front wheel | 180mm | Full front rocker arm length |
| Service loop | 50mm | Standard allowance |
| Pivot slack (body + steering) | ~30mm | Two pivots on path |
| **Total** | **~350mm** | Rounded up from 410mm accounting for path overlap |

**Note**: Wire lengths in the schedule are practical estimates. The L298N sits adjacent to the exit slot, so the internal run is short. The bulk of the length is the rocker arm run to the wheel.

#### Motor W2 (ML) -- Wires W015, W016

| Segment | Distance |
|---------|----------|
| L298N #1 OUT3 to floor exit | 40mm |
| Floor exit to body pivot | 50mm |
| Body pivot to bogie pivot (rear rocker section) | 90mm |
| Bogie pivot to mid-wheel mount | 30mm |
| Service loop + slack | 50mm |
| **Total** | **~250mm** |

#### Motor W3 (RL) -- Wires W017, W018

| Segment | Distance |
|---------|----------|
| Y-splice junction (at W015/W016) | 0mm (branches from ML wires) |
| Bogie pivot to rear wheel mount | 90mm |
| Extra length for steering articulation | 30mm |
| Service loop | 50mm |
| **Total** | **~300mm** (from Y-splice, ~550mm total from L298N) |

#### Servo FL -- Wires W025, W029, W030

| Segment | Distance |
|---------|----------|
| ESP32/breadboard to FL floor exit | 80mm |
| Floor exit through rocker arm to steering bracket | 230mm |
| Service loop + pivot slack | 50mm |
| **Total** | **~350mm** |

#### Servo RL -- Wires W027, W033, W034

| Segment | Distance |
|---------|----------|
| ESP32/breadboard to RL floor exit | 80mm |
| Floor exit through rocker + bogie arm to rear steering bracket | 270mm |
| Service loop + pivot slack | 50mm |
| **Total** | **~400mm** |

#### L298N #1 Control (ESP32 to driver) -- Wires W043-W048

| Segment | Distance |
|---------|----------|
| ESP32 header (centre-right of tray) to L298N #1 (left of tray) | 60-80mm |
| Service loop | 50mm |
| **Total** | **~120mm** |

#### L298N #2 Control (ESP32 to driver) -- Wires W049-W054

| Segment | Distance |
|---------|----------|
| ESP32 header (centre-left of tray) to L298N #2 (right of tray) | 100-120mm |
| Service loop | 50mm |
| **Total** | **~170mm** |

#### Battery Sense -- Wires W039-W041

| Segment | Distance |
|---------|----------|
| Battery + terminal to breadboard R1 | ~50mm |
| Breadboard node to GPIO14 | ~30mm |
| Service loop (keep short for ADC noise) | 20mm |
| **Total per wire** | **~80mm** |

---

## 6. Harness Build Order

Build and test each harness sub-assembly individually before connecting to the rover. This catches wiring errors early and prevents damage to components.

### Step 1: Battery Harness (W001-W004)

**Build**:
1. Solder XT60 female connector to 14 AWG red and black leads (100mm each)
2. Solder inline fuse holder to red lead (W001 to W003 junction)
3. Install 5A blade fuse
4. Attach spade terminals to kill switch leads
5. Wire kill switch inline (W003 in, W004 out)
6. Heat-shrink all solder joints

**Test**:
- Continuity: XT60+ through fuse through switch to output (switch ON)
- No continuity: XT60+ to output (switch OFF)
- No short: XT60+ to XT60- reads open circuit
- Insert 2S LiPo: measure 7.4-8.4V at output with switch ON

### Step 2: Motor Harnesses (W013-W024)

**Build** (make 6 motor wire pairs, identical except length):
1. Cut 20 AWG red and black to length per schedule
2. Strip 5mm at each end
3. Tin one end (for motor tab soldering later)
4. Add Dupont or bare wire at L298N end (stripped for screw terminal)
5. For W2+W3 pair: create Y-splice (solder W15+W17 red together, W16+W18 black together, heat-shrink)
6. For W5+W4 pair: same Y-splice treatment
7. Label each wire pair with motor position (FL, ML, RL, FR, MR, RR)

**Test**:
- Continuity end-to-end on each wire
- No short between red and black in each pair
- Y-splices: verify both branches have continuity to common end

### Step 3: Servo Harnesses (W025-W036)

**Build** (make 4 sets, each set = 3 wires):
1. Cut signal wire (26 AWG orange) to length
2. Cut VCC wire (22 AWG red) to length
3. Cut GND wire (22 AWG black) to length
4. Crimp or attach Dupont female connectors at ESP32/breadboard end
5. At servo end, use matching Dupont female to mate with servo JR/Futaba header
6. Bundle the 3 wires (signal + VCC + GND) with small cable tie every 80mm
7. Label each bundle (FL, FR, RL, RR)

**Test**:
- Each wire has end-to-end continuity
- No cross-shorts between the 3 wires in each bundle
- Verify colour order matches servo header: orange=signal, red=VCC, brown/black=GND

### Step 4: L298N Control Signal Wires (W043-W054)

**Build**:
1. Use pre-made Dupont female-female jumper wires (20cm for #1, 30cm for #2, trimmed as needed)
2. If making custom: cut 26 AWG yellow wire, crimp Dupont female both ends
3. Label each wire with GPIO number and L298N pin name (e.g., "GPIO4 -> ENA")

**Test**:
- Continuity on each jumper
- Verify correct GPIO number on each label by cross-referencing config.h pin definitions

### Step 5: Sensor and Indicator Wires (W039-W042, W055-W058)

**Build**:
1. Voltage divider: solder R1 (10k) and R2 (4.7k) onto mini breadboard
2. Wire battery+ tap to R1 input (W039, brown, 80mm)
3. Wire divider midpoint to GPIO14 (W041, brown, 80mm)
4. Solder 100nF cap from midpoint to GND rail on breadboard
5. E-stop: solder leads to tactile button, attach Dupont at ESP32 end
6. Status LED: solder 330R resistor to LED anode lead, attach Dupont at GPIO0 end

**Test**:
- Voltage divider: apply known voltage (e.g., 7.4V from battery), measure midpoint = ~2.37V
- E-stop: continuity when pressed, open when released
- LED: apply 3.3V across LED+resistor, verify it lights

### Step 6: Final Assembly Integration

1. Mount L298N #1, L298N #2, ESP32-S3, and breadboard on electronics tray
2. Connect all internal harnesses (power, control signals, 5V bus)
3. Perform full continuity and no-short check per EA-19 Section 12.1
4. Connect battery, follow first power-on sequence per EA-19 Section 12.2
5. Route external harnesses (motors, servos) through body exit slots
6. Secure all pivot crossings with hot glue strain relief
7. Cable-tie bundles inside rocker and bogie arm tubes
8. Final system integration test per EA-19 Section 12.5

---

## 7. Mermaid Diagram References

The following Mermaid diagram source files provide visual representations of the wiring harness. These are located in `docs/diagrams/` and can be rendered with any Mermaid-compatible viewer or the `mmdc` CLI tool.

| Diagram File | Content | Relevant Harness Sections |
|-------------|---------|--------------------------|
| `docs/diagrams/power-distribution.mmd` | Battery to fuse to switch to L298N to 5V bus | W001-W012, W037-W038 |
| `docs/diagrams/signal-wiring.mmd` | ESP32 GPIO to L298N logic, servo signals, ADC | W025-W028, W039-W054 |
| `docs/diagrams/electronics-tray-layout.mmd` | Physical placement of components on tray | All internal wires |
| `docs/diagrams/cable-routing-map.mmd` | Wire paths from body to wheels through arms | W013-W024, W025-W036 |

To render any diagram as SVG:
```bash
mmdc -i docs/diagrams/power-distribution.mmd -o docs/diagrams/power-distribution.svg -t dark
```

---

## 8. Cross-Reference to Other Documents

| Topic | Document | Relevant Section |
|-------|----------|-----------------|
| GPIO pin assignments (definitive) | EA-09 Section 2.2-2.6 | All signal wires |
| Pin definitions in firmware | `firmware/esp32/config.h` | W043-W054 (GPIO numbers) |
| Complete wiring guide and test procedures | EA-19 Sections 1-12 | All harness sections |
| Safety systems and E-stop behaviour | EA-15 Sections 2-3 | W055-W056 |
| Phase 1 prototype dimensions | EA-08 Sections 1-8 | Wire length calculations |
| Power system design | EA-03 | Wire gauge selection |
| Wire gauge reference table | EA-19 Section 9 | AWG selection rationale |
| Motor noise suppression | EA-19 Section 3.3 | 100nF caps on all 6 motors |

---

## 9. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-23 | Initial release. 57 wires + 1 capacitor = 58 line items, 18 connectors, full routing specification. |
| 1.1 | 2026-03-24 | Standardised on XT60 connectors, aligned wire gauges with EA-19 (14 AWG battery, 16 AWG distribution, 20 AWG motors). |

---

*Document EA-23 v1.1 -- 2026-03-24*
