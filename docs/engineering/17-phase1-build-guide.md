# Engineering Analysis 17: Phase 1 Build Guide

**Document**: EA-17
**Date**: 2026-03-15
**Purpose**: Step-by-step build guide for the 0.4-scale prototype rover, from ordering parts through to first drive. Designed to be followed linearly.
**Depends on**: EA-08 (Parts Spec), EA-09 (GPIO), EA-10 (Steering), EA-11 (3D Printing)

---

## Step 0: Prerequisites

### 0.1 Tools Required

| Tool | Purpose | Estimated Cost |
|------|---------|---------------|
| 3D Printer (CTC Bizer) | Print all structural parts (225×145×150mm bed, x3g via GPX) | Already owned |
| Soldering iron + solder | Heat-set inserts, wiring | Already owned |
| Wire strippers | Motor/servo wiring | Already owned |
| Hex key set (1.5mm, 2mm, 5mm) | M2, M3, M8 fasteners | ~$5 |
| Small Phillips screwdriver | SG90 servo screws | Already owned |
| Multimeter | Voltage checks, continuity | Already owned |
| 22mm drill bit (hand twist) | Ream bearing holes if needed | ~$3 |
| Needle-nose pliers | Holding nuts, crimping | Already owned |
| Tweezers | Placing heat-set inserts | Already owned |
| Hot glue gun | Cable management, temporary fixes | Already owned |
| Computer with Arduino IDE / CLI | Programming ESP32-S3 | Already owned |

### 0.2 Software Required

| Software | Purpose | Status |
|----------|---------|--------|
| Arduino IDE 2.x or arduino-cli | ESP32 programming | Install ESP32-S3 board support |
| Slicer (Cura) | Generate G-code for CTC Bizer | Install and configure for CTC Bizer |
| GPX 2.6.8 | Convert gcode → x3g for CTC Bizer | Installed at `C:\Users\charl\bin\gpx.exe` |
| Fusion 360 | CAD modelling | Installed with MCP-Link add-in |
| Web browser | Rover control UI | Already available |

---

## Step 1: Order Parts (~$102, delivery 1-3 weeks)

### 1.1 First Order (Start Immediately)

Order these first — filament arrives first so you can start printing while waiting for electronics.

| # | Item | Qty | Source | Est. Cost |
|---|------|-----|--------|-----------|
| 1 | PLA filament 1kg (grey or white) | 2 | Amazon | $30 |
| 2 | M3 heat-set inserts (brass, 5.7mm OD × 4.6mm) | 50 | AliExpress/Amazon | $3 |
| 3 | M3 bolt assortment (8mm, 12mm, 16mm socket cap) | 1 set | Amazon | $6 |
| 4 | M3 nut assortment | 1 set | included | — |
| 5 | M8 × 40mm hex bolts | 8 | Hardware store | $3 |
| 6 | M8 nyloc nuts | 8 | Hardware store | $2 |
| 7 | M8 washers | 16 | Hardware store | $1 |
| 8 | 608ZZ bearings | 12 | Amazon | $5 |

**Subtotal: ~$40**

### 1.2 Second Order (Electronics)

| # | Item | Qty | Source | Est. Cost |
|---|------|-----|--------|-----------|
| 9 | ESP32-S3 DevKitC-1 (N16R8, USB-C) | 1 | AliExpress | $8 |
| 10 | GA12-N20 DC gearmotors (6V, 100RPM, 1:100 ratio, metal gearbox) | 6 | AliExpress | $18 |
| 11 | SG90 micro servos | 4 | AliExpress | $8 |
| 12 | L298N motor driver modules | 2 | AliExpress | $6 |

**Subtotal: ~$40**

### 1.3 Third Order (Power + Misc)

| # | Item | Qty | Source | Est. Cost |
|---|------|-----|--------|-----------|
| 13 | 2S LiPo 2200mAh (7.4V, XT60) | 1 | Amazon/HobbyKing | $12 |
| 14 | 2S LiPo balance charger | 1 | Amazon | $8 |
| 15 | Power switch (toggle or rocker) | 1 | Amazon | $2 |
| 16 | Jumper wire set (M-M, M-F) | 1 | Amazon | $3 |
| 17 | Mini breadboard | 1 | Amazon | $2 |
| 18 | 8mm steel rod (300mm length) | 1 | Hardware store | $2 |
| 19 | 100nF ceramic capacitors | 6 | Amazon/AliExpress | $1 |

**Subtotal: ~$30**

**Grand total: ~$109** (slightly over $102 budget due to larger filament spool — worth the extra margin for reprints).

---

## Step 2: 3D Printing (~65 hours over 8-10 days)

### 2.1 Printer Setup

1. Level bed (paper or 0.1mm feeler gauge — slight drag)
2. Load PLA filament (left extruder only)
3. Set PLA temperature: **200-210°C nozzle, 60°C bed**
4. Apply glue stick or painter's tape for adhesion
5. Right nozzle: remove or park (raise 1-2mm above left)
6. Run calibration test card (from `3d-print/calibration/`) to verify dimensions
7. See `docs/plans/ctc-bizer-guide.md` for full CTC Bizer setup

### 2.2 Print Order

Print parts in this order — each validates dimensions for subsequent parts.

| Day | Part | Qty | Time | Weight | Notes |
|-----|------|-----|------|--------|-------|
| 1 | Bearing test block | 1 | 0.5 hr | 5g | Test 608ZZ fit. Adjust bore ±0.1mm if needed |
| 1-2 | Wheels | 6 | 12 hr | 150g | Print 2 at a time overnight |
| 3 | Left bogie arm | 1 | 2.5 hr | 20g | Test pivot geometry |
| 3 | Right bogie arm | 1 | 2.5 hr | 20g | Mirror of left |
| 4 | Left rocker arm | 1 | 4 hr | 35g | Longer print |
| 4 | Right rocker arm | 1 | 4 hr | 35g | Mirror of left |
| 5 | Differential bar adapters | 3 | 3 hr | 15g | Small, quick |
| 5-6 | Steering brackets | 4 | 6 hr | 48g | Print 2 at a time |
| 6 | Fixed motor mounts | 2 | 2 hr | 16g | Simple parts |
| 7 | Body quadrant FL | 1 | 8 hr | ~60g | Open face up, 8mm brim |
| 7-8 | Body quadrant FR | 1 | 8 hr | ~60g | **Overnight print** |
| 8-9 | Body quadrant RL | 1 | 10 hr | ~100g | **Overnight print** (rocker pivot boss) |
| 9-10 | Body quadrant RR | 1 | 10 hr | ~100g | **Overnight print** (rocker pivot boss) |
| 10 | Top deck tiles (×4) | 4 | 4 hr | ~20g | Flat panel down |
| 10 | Electronics tray | 1 | 3 hr | ~30g | Flat bottom down |
| 10 | Small parts (clips, brackets) | ~12 | 2 hr | ~15g | Strain relief, fuse, switch mount |

### 2.3 Print Settings Summary

All parts use PLA on CTC Bizer:
- **PLA, 0.2mm layer, 4 walls, 50% gyroid infill** (structural)
- **PLA, 0.2mm layer, 3 walls, 20% gyroid infill** (body panels, top deck)
- **200-210°C nozzle, 60°C bed, 40mm/s, 100% cooling after layer 3**
- See `docs/plans/print-strategy.md` for per-part slicer profiles
- See `docs/plans/ctc-bizer-guide.md` for CTC Bizer specifics
- **File workflow**: Cura → gcode → `gpx -m cr1d input.gcode output.x3g` → SD card

### 2.4 After Each Print

1. Remove from bed (flex PEI sheet or use spatula)
2. Remove any support material
3. Trim stringing with heat gun or lighter (quick pass)
4. Test-fit any bearings (ream with 22mm drill bit if too tight)
5. Label the part with a marker (L/R, top/bottom) to avoid confusion

---

## Step 3: Prepare Parts (1-2 hours)

### 3.1 Install Heat-Set Inserts

Using soldering iron at **170-180°C** with a pointed tip (PLA — lower than PETG's 220°C!):

| Part | Number of Inserts | Locations |
|------|-------------------|-----------|
| Body quadrant FL | ~6 | Seam edges (X + Y seam) |
| Body quadrant FR | ~6 | Seam edges (X + Y seam) |
| Body quadrant RL | ~6 | Seam edges (X + Y seam) |
| Body quadrant RR | ~6 | Seam edges (X + Y seam) |
| Rocker arms (×2) | 4 each | Motor mount + bogie pivot |
| Bogie arms (×2) | 4 each | Motor mounts + rocker pivot |
| Steering brackets (×4) | 2 each | Servo mount |
| Fixed motor mounts (×2) | 2 each | Arm attachment |
| **Total** | **~40 inserts** | |

**Technique**: Place insert on hole, press straight down with iron tip. Wait 2-3 seconds for plastic to melt around knurls. Don't force — let the heat do the work. Pull iron straight out. Let cool 10 seconds.

### 3.2 Prepare Differential Bar

1. Cut 8mm steel rod to 300mm length (hacksaw or Dremel cutoff wheel)
2. Deburr both ends with file
3. Test-fit through 608ZZ bearings (should slide smoothly through 8mm bore)
4. Press-fit printed adapters onto rod ends (friction fit + M3 grub screw if needed)

### 3.3 Prepare Wheels

1. Test-fit N20 motor D-shaft into wheel hub bore
2. If too tight: ream with 3mm drill bit
3. If too loose: add a wrap of electrical tape on motor shaft
4. Set aside — wheels go on last

---

## Step 4: Build Suspension (2-3 hours)

### 4.1 Left Side Assembly

```
Step 4.1.1: Bogie arm
  1. Press 608ZZ bearing into bogie arm's rocker pivot boss
  2. Press 608ZZ bearings into bogie arm's wheel mount positions
     (middle and rear)
  3. Set aside

Step 4.1.2: Rocker arm
  1. Press 608ZZ bearing into rocker arm's body pivot boss
  2. Press 608ZZ bearing into rocker arm's bogie pivot boss
  3. Set aside

Step 4.1.3: Connect rocker to bogie
  1. Align rocker arm's bogie pivot with bogie arm's rocker pivot
  2. Insert M8 × 40mm bolt through: washer → rocker bearing → bogie bearing → washer
  3. Thread M8 nyloc nut (finger-tight + ¼ turn)
  4. Verify: bogie should swing freely ±30° relative to rocker

Step 4.1.4: Mount steering brackets
  1. Attach steering bracket to rocker arm front end:
     - Insert M8 × 30mm bolt through steering bracket's 608ZZ bearing
     - Bolt through rocker arm's front wheel mount
     - Nyloc nut (finger-tight)
     - Verify: bracket rotates freely (this is the steering axis)
  2. Attach SG90 servo to steering bracket (M2 screws)
  3. Attach servo horn to rocker arm's steering linkage point

Step 4.1.5: Mount fixed motor bracket
  1. Bolt fixed motor bracket to bogie arm's middle wheel position
  2. M3 × 12mm bolts into heat-set inserts

Step 4.1.6: Mount rear steering bracket
  1. Same as step 4.1.4 but on bogie arm's rear wheel position
  2. Attach second SG90 servo
```

### 4.2 Right Side Assembly

Mirror of left side (steps 4.1.1 through 4.1.6).

### 4.3 Differential Bar

1. Slide steel rod through body frame's centre 608ZZ bearing
2. Attach left adapter to left rocker arm's body pivot
3. Attach right adapter to right rocker arm's body pivot
4. Verify: pushing one rocker down should lift the other (seesaw motion)

### 4.4 Mount to Body

1. Join body front and rear halves (6× M3 bolts through heat-set inserts)
2. Insert M8 bolts through body frame's rocker pivot holes
3. Slide on rocker arm bearings
4. Add washers and nyloc nuts (finger-tight + ¼ turn)
5. Verify: both rockers swing freely, differential bar operates correctly

### 4.5 Suspension Test

Place assembled chassis on a table. Press down on one side — the other side should lift. Place a book under one wheel — all 6 wheel positions should contact the table surface (or within 2mm). If not, check bearing alignment and pivot freedom.

---

## Step 5: Install Motors & Wheels (1-2 hours)

### 5.1 Wire Motors

Before mounting, solder wires and noise suppression capacitors to all 6 motors:
1. Solder a **100nF (0.1μF) ceramic capacitor** directly across each motor's terminals (keeps leads as short as possible). This suppresses electrical noise that can interfere with the ESP32's WiFi and I2C.
2. Cut 12 pieces of wire, ~200mm each (6 motors × 2 wires)
3. Strip 5mm at each end
4. Solder to motor terminals (red = +, black = -)
5. Add heat-shrink over solder joints and capacitor
6. Label each motor wire pair: W1(FL), W2(ML), W3(RL), W4(RR), W5(MR), W6(FR)

**Note on L298N logic levels**: The L298N is specified for 5V logic, but ESP32-S3 outputs 3.3V. This usually works (the HIGH threshold is ~2.3V) but is technically out of spec. If motors respond sluggishly, add a 4-channel logic level shifter (~$1) between ESP32 and L298N. Phase 2's Cytron MDD10A natively accepts 3.3V logic.

### 5.2 Mount Motors

1. Snap N20 motors into all 6 motor clips (steering brackets + fixed mounts)
2. Route wires along rocker/bogie arms towards body
3. Secure wires with small zip ties or tape every 50mm

### 5.3 Attach Wheels

1. Press wheels onto 3mm D-shafts
2. Push until hub boss fully engages shaft (8mm engagement)
3. Tighten M2 grub screw (if using) perpendicular to shaft
4. Spin each wheel by hand — verify free rotation with no wobble

### 5.4 Motor Test

Before wiring to driver boards, test each motor with a 6V battery or bench supply:
1. Touch wires to power — motor should spin
2. Reverse wires — motor should spin opposite direction
3. All 6 motors confirmed working? Proceed

---

## Step 6: Wire Electronics (2-3 hours)

### 6.1 Mount Electronics to Body

1. Mount ESP32-S3 DevKit on standoffs in body centre
2. Mount L298N #1 on left side standoffs
3. Mount L298N #2 on right side standoffs
4. Place battery in tray (don't connect yet)
5. Mount power switch in rear wall

### 6.2 Motor Wiring

Connect motors to L298N driver boards:

| L298N #1 | Motor | Wire Colour |
|----------|-------|-------------|
| OUT1/OUT2 | W1 (FL) | — |
| OUT3/OUT4 | W2+W3 (ML+RL) in parallel | Join both red, join both black |

| L298N #2 | Motor | Wire Colour |
|----------|-------|-------------|
| OUT1/OUT2 | W6 (FR) | — |
| OUT3/OUT4 | W5+W4 (MR+RR) in parallel | Join both red, join both black |

**Parallel wiring for W2+W3**: Twist W2 red + W3 red together, solder to OUT3. Twist W2 black + W3 black together, solder to OUT4. Same for W5+W4.

### 6.3 ESP32 to L298N Wiring

| ESP32 GPIO | L298N Pin | Function |
|------------|-----------|----------|
| GPIO4 | #1 ENA | Left front motor PWM |
| GPIO5 | #1 IN1 | Left front direction A |
| GPIO6 | #1 IN2 | Left front direction B |
| GPIO7 | #1 ENB | Left mid+rear motor PWM |
| GPIO15 | #1 IN3 | Left mid+rear direction A |
| GPIO16 | #1 IN4 | Left mid+rear direction B |
| GPIO8 | #2 ENA | Right front motor PWM |
| GPIO9 | #2 IN1 | Right front direction A |
| GPIO10 | #2 IN2 | Right front direction B |
| GPIO11 | #2 ENB | Right mid+rear motor PWM |
| GPIO12 | #2 IN3 | Right mid+rear direction A |
| GPIO13 | #2 IN4 | Right mid+rear direction B |

**Remove the ENA/ENB jumpers** on both L298N boards — we're using PWM on the EN pins.

### 6.4 Servo Wiring

| ESP32 GPIO | Servo | Wire Colour |
|------------|-------|-------------|
| GPIO1 | Servo FL (front-left steering) | Orange = signal |
| GPIO2 | Servo FR (front-right steering) | Orange = signal |
| GPIO41 | Servo RL (rear-left steering) | Orange = signal |
| GPIO42 | Servo RR (rear-right steering) | Orange = signal |

Servo power (red wire): Connect all 4 to L298N #1's 5V output pin.
Servo ground (brown wire): Connect all 4 to common ground.

### 6.5 Power Wiring

```
Battery (+) → Switch → L298N #1 VCC (+12V input)
                     → L298N #2 VCC (+12V input)

Battery (-) → L298N #1 GND
           → L298N #2 GND
           → ESP32 GND

L298N #1 5V out → ESP32 VIN (5V input)
L298N #1 5V out → Servo VCC (all 4 servos)
```

### 6.6 Battery Voltage Divider (Optional)

If you want battery monitoring:
1. Solder a 10kΩ resistor from battery + to GPIO14
2. Solder a 4.7kΩ resistor from GPIO14 to GND
3. This divides 7.4V to ~2.4V (safe for 3.3V ADC)

### 6.7 Wiring Checklist

Before powering on, verify:
- [ ] All motor polarities consistent (red to OUT+, black to OUT-)
- [ ] L298N VCC connected to battery (not 5V)
- [ ] L298N jumpers removed from ENA/ENB pins
- [ ] ESP32 powered from L298N 5V out (not battery directly)
- [ ] All servo signal wires on correct GPIO pins
- [ ] All grounds connected together (battery, L298N ×2, ESP32, servos)
- [ ] No bare wire touching other bare wire
- [ ] Battery NOT connected yet

---

## Step 7: Upload Firmware (30 minutes)

### 7.1 Install ESP32-S3 Board Support

```bash
# If using arduino-cli:
arduino-cli core install esp32:esp32

# Or in Arduino IDE:
# File → Preferences → Additional Boards Manager URLs:
# https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
# Tools → Board → Boards Manager → search "esp32" → Install
```

### 7.2 Install Libraries

```bash
arduino-cli lib install "WebSockets"
# Or in Arduino IDE: Sketch → Include Library → Manage Libraries → "WebSockets" by Markus Sattler
```

### 7.3 Configure Firmware

Edit `firmware/esp32/config.h`:
1. Set `WIFI_SSID` to your WiFi name (case-sensitive!)
2. Set `WIFI_PASS` to your WiFi password
3. Verify all GPIO pin numbers match your wiring

### 7.4 Upload

```bash
# Connect ESP32-S3 via USB-C
# Select correct COM port

arduino-cli compile --fqbn esp32:esp32:esp32s3 "D:/Mars Rover Project/firmware/esp32/"
arduino-cli upload --fqbn esp32:esp32:esp32s3 --port COMX "D:/Mars Rover Project/firmware/esp32/"
```

### 7.5 Verify Upload

1. Open Serial Monitor (115200 baud)
2. You should see:
   ```
   ========================================
     Mars Rover Phase 1 — v0.1.0
     ESP32-S3 Motor Controller
   ========================================
   [MOTOR] Initialised 4 channels
   [STEER] Initialised 4 servos (centred)
   [SENSOR] Initialised (ADC + 2 encoders + E-stop)
   [WIFI] Connecting to VM9388584......
   [WIFI] Connected! IP: 192.168.0.XXX
   [WIFI] Open http://192.168.0.XXX in browser
   [WEB] Server on port 80, WebSocket on port 81
   [MAIN] Setup complete — ready to drive!
   ```
3. Note the IP address — you'll need it for the phone

---

## Step 8: First Power-On Test (30 minutes)

### 8.1 Safety First

1. Place rover on a raised surface (books, box) with wheels off the ground
2. Connect battery
3. Turn on power switch
4. Verify: status LED lights up, Serial Monitor shows startup messages
5. Verify: all servos click to centre position
6. Verify: no motor movement (motors should be stopped until commanded)

### 8.2 Connect Phone

1. Open phone browser
2. Navigate to `http://192.168.0.XXX` (the IP from Serial Monitor)
3. You should see the Mars Rover P1 control page
4. Verify: battery voltage and percentage display in status bar

### 8.3 Test Motors (Wheels Off Ground!)

1. Set speed slider to 20%
2. Press ↑ (forward) — all wheels should spin forward
3. Release — all wheels should stop
4. Press ↓ (reverse) — all wheels should spin backward
5. Press ← (left) — left wheels slower/reverse, right wheels faster
6. Press → (right) — opposite
7. If any motor spins the wrong way: swap its two wires at the L298N

### 8.4 Test Steering

1. Press ← — front wheels should turn left, rear wheels turn right (Ackermann)
2. Press → — opposite
3. Switch to "Point Turn" mode — wheels should angle for rotation
4. Switch to "Crab Walk" mode — all wheels should angle the same way
5. If any servo is off-centre when straight: adjust trim in Settings

### 8.5 Calibrate Servos

1. Set all wheels straight (press STOP, Ackermann mode)
2. Look along the side of the rover — are all wheels aligned?
3. If a wheel is angled slightly: use the trim slider for that servo in Settings
4. Typical trim: ±20 μs (2-3 degrees)

---

## Step 9: First Drive! (1 hour)

### 9.1 Ground Test (Indoor, Flat Floor)

1. Place rover on flat floor (hardwood/tile/carpet)
2. Set speed to 20%
3. Drive forward 1 metre — observe straight tracking
4. If it pulls left/right: one motor may be slightly faster — adjust in firmware
5. Turn left, turn right — observe smooth steering
6. Test point turn — rover should rotate roughly in place
7. Test emergency stop (STOP button) — instant stop

### 9.2 Suspension Test

1. Drive over a small obstacle (pencil, 10mm height)
2. One wheel should ride over while others stay on the ground
3. Observe rocker-bogie articulation — body should stay relatively level
4. Try a larger obstacle (book, 20mm height)
5. Try driving across a threshold (doorframe strip)

### 9.3 Outdoor Test (Dry Weather Only!)

1. Take rover outside to a dry pavement/patio
2. Test driving on concrete — should be smooth
3. Test driving on short grass — verify adequate traction
4. Test a gentle slope (5-10°) — should climb without slipping
5. Test turning on grass — verify wheels don't dig in excessively
6. Monitor battery voltage — stop at ~7.0V warning

### 9.4 Record Results

Note down:
- [ ] Straight-line tracking accuracy (does it drift?)
- [ ] Turning radius (measure with tape — compare to EA-10 calculation)
- [ ] Obstacle climbing height (what's the max?)
- [ ] Battery life (how long before warning?)
- [ ] Any mechanical issues (loose joints, stripped gears, wobbly wheels)
- [ ] WiFi range (how far can you go before losing connection?)

These results inform Phase 2 design decisions!

---

## Step 10: Iterate & Improve

Based on test results, common issues and fixes:

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Wheel falls off shaft | D-bore too loose | Reprint with 0.05mm smaller bore, or add grub screw |
| Rover pulls to one side | Motor speed mismatch | Add software speed calibration per motor |
| Steering wobbles | Bearing seat loose | Reprint with 0.05mm smaller bore |
| Motor stalls on grass | Insufficient torque | Reduce speed, or accept Phase 2 motors are stronger |
| WiFi drops at 10m | ESP32 antenna too close to motors | Add external antenna or accept range limit |
| Battery lasts 20min | L298N is inefficient (30-40% loss) | Normal — Phase 2 uses MDD10A (95% efficiency) |
| Servo twitches | PWM noise from motor drivers | Add 100μF capacitor on servo power rail |
| Body flexes | Frame walls too thin | Reprint with 5 walls instead of 4, or add internal ribs |

---

## Build Timeline Summary

| Day | Activity | Duration |
|-----|----------|----------|
| 1 | Order parts + start printing bearing test | 1 hr |
| 1-10 | 3D printing (batches, ~65 hrs total) | Background task |
| Parts arrive | Inspect all components | 30 min |
| Day 11 | Install heat-set inserts, prepare diff bar | 2 hrs |
| Day 12 | Build suspension (both sides) | 3 hrs |
| Day 12 | Mount to body, test articulation | 1 hr |
| Day 13 | Wire motors, mount to clips | 2 hrs |
| Day 13 | Wire L298N boards + ESP32 + servos | 2 hrs |
| Day 13 | Upload firmware, bench test | 1 hr |
| Day 14 | First drive! Calibrate servos, test modes | 2 hrs |
| Day 14 | Outdoor test (weather permitting) | 1 hr |
| **Total** | | **~14 days** (most is waiting for prints + delivery) |

---

*Document EA-17 v1.0 — 2026-03-15*
