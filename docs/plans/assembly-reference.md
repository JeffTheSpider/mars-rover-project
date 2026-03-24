# Phase 1 Assembly Reference Guide

## Overview

9 sub-assembly stages from individual parts to rolling rover.
Each stage is self-contained and testable before proceeding.

**Total assembly time: ~6-7 hours** (after all parts printed and hardware ready)

| Stage | Description | Time Estimate |
|-------|-------------|---------------|
| 1 | Prepare printed parts (clean, inserts, shafts) | ~30 min |
| 2 | Wheel sub-assemblies (x6) | ~30 min |
| 3 | Bogie arms (x2) | ~20 min |
| 4 | Steering brackets + servos (x4) | ~45 min |
| 5 | Front wheel assemblies (x2) | ~20 min |
| 6 | Rocker-bogie suspension (x2) | ~30 min |
| 7 | Body frame | ~30 min |
| 8 | Final assembly — suspension to body | ~30 min |
| 9 | Electronics and wiring | ~90 min + 60 min testing |

---

## Tools Required

Gather everything before starting. Missing a tool mid-stage is frustrating.

### Assembly Tools
- M3 Allen key (2.5mm hex) -- body seams, rocker halves, servo mounts
- M2 Allen key (1.5mm hex) -- wheel grub screws
- Small Phillips screwdriver -- servo horn screws
- Soldering iron with fine tip -- heat-set inserts at 170-180C for PLA
- Tweezers / needle-nose pliers -- placing small hardware, routing wires
- Blue painter's tape -- temporary fixturing, labelling wire pairs

### Electrical Tools
- Multimeter -- continuity checks before powering, voltage verification
- Wire strippers -- 22-26 AWG range
- Crimping tool -- JST-XH connectors (2-pin motor, 3-pin servo)
- Solder + flux -- 100nF capacitors on motor terminals, wire repairs

### Measurement & Verification
- Kitchen scale -- weight verification of sub-assemblies
- Ruler / digital calipers -- dimensional checks, bearing seat verification
- USB-C cable -- ESP32-S3 programming and serial debug
- Phone with WiFi -- PWA control testing (connect to rover AP)

### Consumables
- 100nF ceramic capacitors (x6, already on shopping list)
- Heat-shrink tubing (assorted 2-5mm)
- Cable ties (small, 100mm)
- Isopropyl alcohol (cleaning bearing seats)

---

## Stage 1: Prepare Printed Parts (~30 min)

### 1.1 Clean and Inspect
- Remove all brims and support material
- Trim stringing with flush cutters
- Test-fit all 608ZZ bearing seats with a bearing (should press in firmly)
- Test-fit N20 motor shaft in wheel hub bore

### 1.2 Install Heat-Set Inserts

**Temperature: 170-180C** (PLA -- do NOT use PETG's 220C)

| Part | Insert Count | Locations |
|------|-------------|-----------|
| Body quadrant FL | ~6 | X-seam + Y-seam edges |
| Body quadrant FR | ~6 | X-seam + Y-seam edges |
| Body quadrant RL | ~6 | X-seam + Y-seam edges |
| Body quadrant RR | ~6 | X-seam + Y-seam edges |
| Steering brackets (x4) | 2 each | Arm mounting faces |
| Fixed wheel mounts (x2) | 2 each | Arm mounting faces |
| Servo mounts (x4) | 2 each | Bracket attachment |
| Top deck FR tile | 4 | Phone mount bosses |

**Technique**: Place insert on hole. Press iron straight down. Wait 2-3 seconds. Pull iron straight out. Let cool 10 seconds. Insert should be flush with surface.

### 1.3 Prepare Shaft Hardware
- Cut 8mm steel rod to 300mm length (differential bar)
- Deburr ends with file
- Test through 608ZZ bore (should slide freely)

### Troubleshooting -- Stage 1
- **Insert goes in crooked**: Let it cool, then reheat and straighten. If badly misaligned, use iron to melt it out and press in a fresh insert.
- **Insert sits proud (above surface)**: Press iron down again gently until flush. Do not force -- PLA will deform around the insert.
- **Bearing seat too tight**: Slightly ream hole with a round file or wrap 220-grit sandpaper around a dowel. Remove material slowly. Never hammer a bearing in -- PLA will crack.
- **Bearing seat too loose**: Apply a thin coat of CA (superglue) to the bore, let it cure 5 minutes, then press bearing in. This is a one-time fix -- the bearing will be permanent.

> **TEST GATE**: All heat-set inserts flush. All bearing seats accept 608ZZ with firm hand pressure. All shaft sections slide through bearing bores freely.

---

## Stage 2: Wheel Sub-Assemblies x6 (~30 min)

### Parts per wheel:
- 1x PLA rim (rover_wheel.py)
- 1x TPU tire (rover_tire.py) -- if available
- 1x N20 motor (GA12-N20 6V 100RPM)
- 1x M2 x 4mm grub screw

### Assembly:
1. If using TPU tires: press TPU tire onto PLA rim (rim lips retain tire)
2. Solder 100nF ceramic capacitor across motor terminals (do all 6 motors now)
3. Insert N20 motor D-shaft into wheel hub bore
4. Align D-flat on shaft with flat in bore
5. Thread M2 grub screw into radial hole, tighten against shaft D-flat

### Verify:
- [ ] Wheel spins freely on motor shaft
- [ ] No wobble (D-flat aligned)
- [ ] Grub screw holds wheel firmly (try to pull wheel off by hand -- should not budge)
- [ ] Tire seated between both rim lips (if using TPU)
- [ ] 100nF capacitor soldered to EVERY motor (noise suppression)

### Troubleshooting -- Stage 2
- **Wheel wobbles on shaft**: D-flat not aligned. Loosen grub screw, rotate wheel until D-flat seats, retighten.
- **Grub screw won't grip**: Shaft may have rotated past the D-flat. Use calipers to find the flat side, align, retighten.
- **TPU tire won't seat**: Warm the tire slightly (hair dryer, 30 seconds) to make it more pliable. Stretch over rim lips.
- **Motor shaft too loose in bore**: Wrap one layer of painter's tape around the shaft as a shim. Or apply a drop of threadlocker.

> **TEST GATE**: All 6 wheels spin freely by hand with no wobble. Grub screws hold firm. Capacitors soldered on all 6 motors.

---

## Stage 3: Bogie Arms x2 -- left and right (~20 min)

### Parts per bogie:
- 1x Bogie arm (bogie_arm.py)
- 1x 608ZZ bearing (centre pivot)
- 2x Wheel sub-assemblies (middle + rear)

### Assembly:
1. Press 608ZZ bearing into bogie arm centre pivot boss
2. Snap N20 motors into motor clip pockets at each end
3. Route motor wires through wire slot alongside pivot boss

### Verify:
- [ ] Bearing seated flush in boss
- [ ] Both motors snap-fit securely (should click in, not fall out when inverted)
- [ ] Wheels spin freely
- [ ] Wire routing doesn't bind when bogie pivots

### Troubleshooting -- Stage 3
- **Bearing won't press in**: Slightly ream hole with round file. Remove material gradually -- 0.1mm at a time. Never force -- PLA will crack.
- **Motor doesn't clip in**: Check for brim remnants in the clip pocket. Clean with a craft knife. Motor should snap in with moderate thumb pressure.
- **Wires snag on pivot**: Re-route wires through the dedicated wire channel. Use a small cable tie at the pivot to keep wires constrained but with enough slack to allow full articulation.

> **TEST GATE**: Each bogie arm pivots freely on 608ZZ bearing with no binding. Acceptable play: <0.5mm axial. Both motors held securely. Wires do not bind through full pivot range.

---

## Stage 4: Steering Assemblies x4 (~45 min)

*Updated per EA-27: steering bracket is now a bearing carrier only (no motor clip).
Motor is in the knuckle. Horn link provides the servo-to-knuckle connection.*

### Parts per steered wheel:
- 1x Steering bracket (steering_bracket.py — bearing carrier + hard stops)
- 1x 608ZZ bearing (pivot bearing)
- 1x 8mm steel rod segment (~50mm, steering pivot shaft)
- 1x SG90 servo
- 1x Servo mount (servo_mount.py)
- 1x Steering knuckle (steering_knuckle.py — carries motor + wheel axle)
- 1x Steering horn link (steering_horn_link.py — 4-bar linkage coupler)
- 2x M2x10mm screws (link pin joints)
- 2x M2 nyloc nuts (link pin retention)
- 4x M2 nylon washers (smooth rotation at pins)

### Assembly:
1. Press 608ZZ bearing into bracket top bore (C-clamp, flush with top face)
2. Insert 8mm pivot rod through bracket bore + bearing inner race
3. Bolt servo mount to front wheel connector side face (2x M3x12 into heat-set inserts)
4. Insert SG90 servo into mount pocket, secure with 2x M2x8 Phillips screws
5. Attach single-arm horn to SG90 spline (centred = straight ahead), tighten horn screw
6. Snap N20 motor into knuckle motor pocket (shaft exits through axle bore side)
7. Slide knuckle pivot socket over pivot rod (rod protrudes below bracket)
8. Tighten M3 grub screw in knuckle socket to retain rod
9. Connect horn link:
   - Horn end: M2x10 → nylon washer → horn hole → link hole → nylon washer → M2 nyloc nut
   - Knuckle arm end: same hardware to knuckle steering arm M2 hole
   - Finger-tight + 1/4 turn — pins must rotate freely
10. Bolt steering bracket to connector front face (2x M3x12 into heat-set inserts)

### Verify:
- [ ] Bearing seated, pivot shaft rotates freely (flick inner race)
- [ ] Servo centred at 1500us — horn perpendicular to bracket
- [ ] Horn link operates smoothly (manually sweep ±35°)
- [ ] Hard stops engage at ±35° — knuckle tab contacts bracket walls
- [ ] Motor spins freely in knuckle pocket
- [ ] Motor wires have 15mm slack loop for steering sweep

### Troubleshooting -- Stage 4
- **Servo jitters at rest**: Check power supply. Likely 5V BEC voltage droop under load (see EA-19). Try powering servo from a separate 5V source to confirm.
- **Horn link binds**: Pin joints too tight. Loosen M2 nyloc 1/8 turn. Nylon washers essential for smooth rotation.
- **Hard stops don't engage at ±35°**: Tab or walls may be under-printed. Verify with protractor. Sand if too tall, add shim if too short.
- **Servo doesn't respond**: Check 3-pin wiring order: Brown=GND, Red=5V, Orange=Signal.
- **Bearing feels gritty**: Spin bearing 30 seconds to distribute grease. Flush with IPA if persistent.

> **TEST GATE**: Command each servo to 1111us (−35°), 1500us (centre), 1889us (+35°). Verify smooth motion through full range. Hard stops engage. Horn link operates freely. All 4 assemblies done.

---

## Stage 5: Steered Wheel Assemblies x4 (~20 min)

*Updated per EA-27: motor is now in the knuckle (not the bracket).
All 4 steered wheels follow the same assembly (FL, FR, RL, RR).*

### Parts per wheel:
- 1x Steering assembly (from Stage 4)
- 1x Wheel sub-assembly (from Stage 2)

### Assembly:
1. Motor is already in the knuckle from Stage 4
2. Insert motor D-shaft through knuckle axle bore
3. Press wheel hub bore onto motor D-shaft
4. Tighten M2 grub screw against D-flat

### Verify:
- [ ] Wheel turns with motor (driving) — spin by hand, check motor shaft engagement
- [ ] Wheel turns with servo (steering) — manually rotate horn link
- [ ] No mechanical interference through full ±35° steering range
- [ ] Wheel doesn't hit arm tube at full lock (≥5mm gap per EA-08)
- [ ] Motor wires have adequate slack through full steering sweep

### Troubleshooting -- Stage 5
- **Wheel wobbles**: D-flat not aligned in hub bore. Loosen grub screw, rotate wheel until D-flat seats.
- **Wheel hits bracket when steered**: Motor not fully seated in knuckle clip. Check for brim remnants in pocket.
- **Motor wire pulls tight at full steer**: Route wire through connector wire exit hole with 15mm slack loop. Secure with zip-tie anchor at neutral position.

> **TEST GATE**: Each steered wheel drives smoothly while steering through full ±35° range. No mechanical interference. Wires have adequate slack. All 4 steered wheels + 2 fixed wheels = 6 total ready for suspension assembly.

---

## Stage 6: Rocker-Bogie Suspension x2 -- left and right (~30 min)

### Parts per side:
- 1x Rocker arm front half (rocker_arm.py)
- 1x Rocker arm rear half (rocker_arm.py)
- 1x Bogie arm sub-assembly (from Stage 3)
- 1x Front wheel assembly (from Stage 5)
- 1x Fixed wheel mount (fixed_wheel_mount.py) -- for rear-most steered wheel
- M3 bolts for joining rocker halves
- 8mm shaft sections for pivot pins

### Assembly:
1. Bolt rocker arm front + rear halves together (M3 x 12mm into heat-set inserts)
2. Insert 8mm pivot pin through rocker and bogie arm bearing
3. Attach front wheel assembly to rocker arm front via 8mm pivot
4. Attach fixed wheel mount to rear steered wheel position

### Verify:
- [ ] Bogie pivots freely on rocker
- [ ] All 3 wheels on this side touch a flat surface simultaneously
- [ ] Suspension articulates smoothly over ~20mm obstacle
- [ ] No binding or interference at any position

### Troubleshooting -- Stage 6
- **Bogie doesn't pivot freely**: Check 8mm shaft for burrs. Deburr with file. Verify bearing inner race spins on shaft (bearing may have been pressed onto shaft too tightly).
- **Wheels don't all touch ground**: One pivot may be binding. Work through each joint individually. The most common cause is a bearing that isn't fully seated.
- **Rocker halves don't align**: Bolt holes between halves may be slightly misaligned. Ream with a 3mm drill bit if necessary. Do not over-torque -- the heat-set inserts will pull out.

> **TEST GATE**: Place each suspension side on a flat surface. All 3 wheels touch. Push one end down 20mm -- the other end lifts smoothly. Suspension returns to level when released. No binding at any position.

---

## Stage 7: Body Frame (~30 min)

### Parts:
- 4x Body quadrants (FL, FR, RL, RR)
- 3mm dowel pins (alignment)
- M3 x 12mm bolts (into seam heat-set inserts)

### Assembly:
1. Dry-fit all 4 quadrants -- check alignment with dowel pins
2. Join FL + FR (X-seam bolts)
3. Join RL + RR (X-seam bolts)
4. Join front pair to rear pair (Y-seam bolts)
5. Verify all seams flush and square

### Verify:
- [ ] All 4 quadrants flush at seams
- [ ] Body frame is square (measure diagonals -- should be equal within 2mm)
- [ ] Rocker pivot bores on RL/RR sides accessible
- [ ] Kill switch hole (RR) is clear
- [ ] Cable exit holes aligned
- [ ] LED underglow holes (4x) in floor are clear
- [ ] Headlight holes (FL/FR) and taillight holes (RL/RR) are clear

### Troubleshooting -- Stage 7
- **Body quadrants don't align**: Check dowel pin holes are clear of print debris. Sand dowel pins lightly if needed. Don't force -- PLA corners will crack.
- **Seams not flush**: One quadrant may have warped during printing. Place on a flat surface and check for rock. If warped, try clamping with painter's tape and running a heat gun briefly over the seam (be very careful with PLA -- it softens at ~60C).
- **Diagonal measurements off by >3mm**: Loosen all bolts, re-seat dowel pins, and re-tighten in a star pattern (FL-RR, FR-RL, then seams).

> **TEST GATE**: Body frame sits flat on table with no rock. Diagonals equal within 2mm. All pivot bores and cable holes are clear and accessible.

---

## Stage 8: Final Assembly -- Suspension to Body (~30 min)

### Assembly:
1. Insert 8mm pivot pins through body rocker pivot bores
2. Attach left suspension assembly to left body pivots
3. Attach right suspension assembly to right body pivots
4. Insert differential bar through body centre, connecting left and right rockers
5. Secure diff bar with printed adapters at each end

### Verify:
- [ ] Rover sits level on flat surface
- [ ] All 6 wheels touch ground simultaneously
- [ ] Push down on one corner -- opposite wheels lift smoothly
- [ ] Differential bar allows body to remain level while wheels articulate
- [ ] Body height is correct (~80mm ground clearance at 0.4 scale)

### Troubleshooting -- Stage 8
- **Not all 6 wheels touch ground**: One suspension side may be binding. Remove from body and re-check Stage 6 test gate. Also verify diff bar adapters aren't clamping the bar too tightly.
- **Differential bar too short**: The 300mm rod should span the 250mm rocker pivot span with 25mm overhang each side. If it doesn't reach, measure actual span and recut.
- **Body rocks on flat surface**: Differential bar may be binding. Ensure it rotates freely in the body centre bore. Lubricate with a drop of light machine oil if needed.

> **TEST GATE**: Place rover on flat surface -- all 6 wheels touch. Place one wheel on a 20mm book -- rover remains stable, no wheels lift off. Differential bar rotates smoothly. Ground clearance ~80mm.

---

## Stage 9: Electronics and Wiring (~90 min assembly + 60 min testing)

### Parts:
- 1x Electronics tray
- 1x ESP32-S3 DevKitC-1
- 2x L298N motor drivers
- 1x 2S LiPo 2200mAh
- 1x Power switch
- 1x 5A fuse + holder
- Jumper wires, strain relief clips

### Assembly:
1. Mount ESP32 on tray standoffs (M2.5 screws)
2. Mount L298N drivers on tray standoffs
3. Place LiPo in battery cradle, secure with strap
4. Wire per EA-19 wiring diagram:
   - Battery -> switch -> fuse -> L298N VCC
   - L298N -> motors (solder 100nF caps across motor terminals first!)
   - ESP32 GPIO -> L298N IN1-IN4 (see EA-09 pin map)
   - ESP32 -> servos (signal + 5V from L298N regulator)
5. Route wires through cable channels
6. Secure with strain relief clips at exit points
7. **STOP: Pre-power checks (see below)**
8. Place tray inside body frame
9. Attach top deck tiles (snap clips)

### Pre-Power Safety Checks (MANDATORY)
Before connecting battery for the first time:
1. Multimeter continuity: check there is NO short between battery +/- terminals
2. Multimeter continuity: verify each motor connects to correct L298N output pair
3. Visual inspection: no bare wire touching chassis or other wires
4. Verify fuse is installed in holder
5. Verify E-stop switch is in the OFF position

### First Power-Up Sequence:
1. Connect USB-C to ESP32 first (powers ESP32 only, no motors)
2. Verify serial output on computer (115200 baud)
3. Verify WiFi AP "MarsRover" appears on phone
4. Connect phone to AP, open PWA
5. NOW connect battery (with E-stop OFF / switch off)
6. Turn on switch -- verify battery voltage reading on PWA
7. Test one motor at a time: low speed, forward, then reverse
8. Test one servo at a time: centre, left, right
9. If anything is wrong, hit E-stop immediately

### Verify:
- [ ] No short circuits (multimeter continuity check before powering)
- [ ] Battery voltage correct (7.4-8.4V)
- [ ] ESP32 boots and creates WiFi AP
- [ ] All 6 motors respond to commands (correct direction)
- [ ] All 4 servos sweep correctly (+/-35 degrees)
- [ ] E-stop (kill switch) cuts power instantly
- [ ] Battery voltage telemetry displays on phone PWA
- [ ] All 3 steering modes work (Ackermann, point turn, crab walk)

### Troubleshooting -- Stage 9
- **ESP32 won't boot**: Check USB-C cable is data-capable (not charge-only). Try a different cable. Check for solder bridges on ESP32 pins.
- **WiFi won't connect**: Check ESP32 is in AP mode. Default SSID: "MarsRover". Try restarting phone WiFi. Try forgetting the network and reconnecting. If SSID doesn't appear, check serial output for boot errors.
- **Motor runs backwards**: Swap the two motor wires at the L298N output terminals. Do NOT change firmware -- physical wiring fix is simpler and more reliable.
- **Motor doesn't run at all**: Check L298N enable jumper is in place. Check 100nF capacitor isn't shorting motor terminals. Measure voltage at L298N output with multimeter.
- **Servo jitters at rest**: Likely 5V supply issue. L298N 5V regulator may not provide enough current for 4 servos simultaneously. Test with fewer servos connected. May need separate 5V BEC (see EA-19).
- **Battery voltage reads wrong**: Check voltage divider resistor values on ADC input (see EA-09). Calibrate ADC_VDIV_RATIO in config.h.
- **E-stop doesn't work**: Check switch wiring. Switch should be in series with battery positive lead, BEFORE the fuse.
- **Servo doesn't centre correctly**: Adjust SERVO_CENTRE_TRIM in config.h. Each servo may need individual trim of +/-50us.
- **Steering seems reversed (left command turns right)**: Swap SERVO_FL/SERVO_FR pin assignments in config.h. Or physically swap the servo connectors.

> **TEST GATE**: Full system operational. All motors drive correct direction. All servos steer correct direction. WiFi connected from phone. PWA displays telemetry. E-stop kills power. Battery voltage reading accurate. Rover drives forward in a straight line (trim motors if needed via MOTOR_TRIM constants).

---

## Post-Assembly Checklist

Run through this complete checklist before declaring the build "done":

### Mechanical
- [ ] All 6 wheels spin freely by hand
- [ ] Suspension articulates without binding
- [ ] Body frame is rigid (no flex at seams)
- [ ] Electronics tray secure inside body
- [ ] All wires routed, no pinch points
- [ ] Top deck snaps on cleanly
- [ ] Battery sits securely, no rattle
- [ ] No loose bolts (torque check all M3 joints)

### Electrical
- [ ] WiFi connects from phone within 5 seconds
- [ ] Forward/reverse/left/right all work
- [ ] Steering angles look correct (not reversed)
- [ ] Point turn mode works (front wheels opposite to rear)
- [ ] Crab walk mode works (all wheels same angle)
- [ ] Speed slider affects all motors proportionally
- [ ] E-stop cuts all power immediately
- [ ] Battery voltage telemetry is accurate (+/-0.2V of multimeter reading)

### Weight Verification
- [ ] Weigh completed rover on kitchen scale
- [ ] Expected: ~1.1-1.3 kg (depending on battery and wiring)
- [ ] Record actual weight: _______ g

---

## Torque Sequence

| Joint | Fastener | Torque | Notes |
|-------|----------|--------|-------|
| Body seam | M3 x 12mm | 0.5 N-m max (finger tight + 1/4 turn) | Don't strip PLA insert |
| Rocker halves | M3 x 12mm | 0.5 N-m max (finger tight + 1/4 turn) | Same |
| Servo mount | M3 x 8mm | 0.5 N-m max | Into heat-set inserts |
| Servo horn | Servo screw | 0.2 N-m max (gentle) | Servo plastic is soft |
| Servo to mount | Small Phillips | 0.2 N-m max | Don't crack servo ears |
| Wheel grub | M2 x 4mm | Snug | Allen key 1.5mm, onto D-flat |
| ESP32 standoffs | M2.5 | Finger tight | Don't crack PCB |
| L298N standoffs | M3 | Finger tight + 1/4 turn | Check no shorts underneath |
| Diff bar adapters | M3 grub | Snug | If equipped |

**General rule for PLA heat-set inserts**: Finger tight + 1/4 turn maximum (0.5 N-m). PLA inserts strip or pull out easily. If an insert spins, remove the bolt, reheat the insert with the iron, press it in deeper, and let it cool before retrying.

---

## Quick Reference: Wire Colour Convention

Adopt a consistent colour scheme and label every wire pair. Suggested convention:

| Signal | Colour |
|--------|--------|
| Battery + | Red |
| Battery - | Black |
| Motor power A | Red/White stripe |
| Motor power B | Black/White stripe |
| Servo signal | Orange or Yellow |
| Servo 5V | Red |
| Servo GND | Brown |
| GPIO signals | Blue or Green |
| Ground bus | Black |

Label every JST connector with painter's tape and a marker (e.g., "M-LF" for motor left front, "S-RF" for servo right front).
