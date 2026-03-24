# Phase 1 Maintenance Guide

## Overview

The Mars Rover Phase 1 prototype uses PLA plastic, press-fit bearings, and small hobby electronics. PLA is not as durable as PETG or metal -- it creeps under sustained load, is brittle in cold weather, and degrades in direct sunlight. Regular maintenance keeps the rover operational and catches small problems before they become big ones.

**Golden rule**: If something feels wrong, stop and inspect. A 5-minute check now prevents a 2-hour repair later.

---

## After Every Session

**Time: ~5 minutes**

These checks should become automatic habit every time the rover comes back inside.

### Visual Inspection
- [ ] Check all 4 body quadrant seams for cracks or separation
- [ ] Check for loose bolts (any visible gaps at joints)
- [ ] Check for disconnected or pinched wires (especially at suspension pivot points)
- [ ] Check wheels for damage, debris wrapped around axles, or loose grub screws

### Quick Mechanical Check
- [ ] Spin each wheel by hand -- should rotate freely with no grinding
- [ ] Wiggle each wheel laterally -- should have minimal play (<0.5mm)
- [ ] Check wheel grub screws (M2) are tight (give each a gentle turn with 1.5mm Allen key)

### Battery Care
- [ ] Power off rover (E-stop / switch off)
- [ ] Disconnect battery from rover (XT30 connector)
- [ ] Check battery for puffing, heat, or physical damage
- [ ] Charge battery using balance charger (NEVER leave unattended)
- [ ] Store battery in LiPo-safe bag when not in use
- [ ] Do NOT store battery inside the rover long-term

### Cleaning
- [ ] Brush off dirt, grass, and debris from bearings, wheels, and body
- [ ] Check bearing pivot points for grit or debris (blow out with compressed air if available)
- [ ] Wipe down body panels if dirty (damp cloth, no solvents on PLA)

---

## Weekly (If Used Regularly)

**Time: ~15 minutes**

### Bearings and Pivots
- [ ] Check all bearing pivots for excessive play (>1mm axial play indicates wear)
- [ ] Rotate each bearing by hand -- should spin smoothly, no grinding or roughness
- [ ] Check 8mm pivot shafts for wear marks or bending
- [ ] Check differential bar rotates freely in body bore

### Suspension
- [ ] Place rover on flat surface -- all 6 wheels should touch
- [ ] Press down on each corner -- suspension should articulate smoothly and return to level
- [ ] Check bogie arm pivot for binding or stiffness

### Motors and Servos
- [ ] Inspect motor wires at suspension pivot points for chafing or fraying
- [ ] Check servo horn screws are tight (small Phillips, very gentle)
- [ ] Command each servo to centre (90 degrees) -- verify they all point straight ahead
- [ ] Run each motor briefly -- listen for unusual grinding or clicking

### Electronics
- [ ] Verify WiFi connection quality (connect phone, check responsiveness)
- [ ] Check battery voltage under no-load (should be >7.8V for healthy 2S LiPo)
- [ ] If voltage is <7.4V under no-load, the battery is over-discharged -- charge immediately
- [ ] Check all JST connectors are fully seated (gentle push on each)
- [ ] Visually inspect electronics tray for anything loose

---

## Monthly

**Time: ~30 minutes**

### Fastener Retorque
- [ ] Re-tighten ALL M3 bolts to 0.5 N-m max (PLA creeps under sustained load)
  - Body seam bolts (x16 approx)
  - Rocker arm half-join bolts
  - Servo mount bolts
  - Fixed wheel mount bolts
- [ ] Check wheel grub screws (M2) -- retighten onto D-flat
- [ ] Check diff bar adapter grub screws (if equipped)

### Heat-Set Insert Check
- [ ] Wiggle-test each heat-set insert boss (grab the bolt head and wiggle)
- [ ] If an insert spins or pulls out, it needs re-setting:
  1. Remove the bolt
  2. Reheat soldering iron to 175C
  3. Press insert back in firmly
  4. Let cool 30 seconds before re-bolting

### Wire and Cable Check
- [ ] Inspect all wire routing through body cable exit slots for wear
- [ ] Check strain relief clips are still secure
- [ ] Look for any bare copper showing through wire insulation
- [ ] Check solder joints on motor capacitors (100nF) -- reflow if cracked

### Wheels and Treads
- [ ] Clean wheel treads -- remove embedded debris
- [ ] If using O-rings: check they haven't rolled off the rim groove. Replace if stretched or cracked.
- [ ] If using TPU tires: check for tears or delamination from PLA rim
- [ ] Check all 6 wheels for cracks in PLA (especially at spoke lightening holes)

### Safety Systems
- [ ] Verify E-stop button cuts ALL power immediately (test with motor running at low speed)
- [ ] Check fuse is correct rating (5A) and not blown
- [ ] Verify battery voltage ADC reading matches multimeter (within 0.2V)

---

## Seasonal / Quarterly

**Time: ~45 minutes**

### Deep Inspection
- [ ] Remove top deck tiles and lift out electronics tray
- [ ] Inspect all internal wiring for damage, corrosion, or loose connections
- [ ] Check ESP32 and L298N for signs of overheating (discolouration, melted plastic)
- [ ] Clean dust from ESP32 and L298N boards with compressed air
- [ ] Inspect battery connector (XT30) for burns or looseness

### PLA Degradation Check
PLA degrades in UV sunlight and moisture. If the rover spends time outdoors:
- [ ] Check for surface chalking or colour fading (early UV damage)
- [ ] Check for brittleness -- gently flex thin features (clips, tabs)
- [ ] Check for warping from heat exposure (PLA softens at ~60C)
- [ ] If any structural part shows degradation, reprint it

### Firmware Update Check
- [ ] Check if new firmware version is available
- [ ] Back up current config.h settings before updating
- [ ] Update via USB-C (or OTA if configured)
- [ ] After update: verify all motors, servos, WiFi, E-stop still work

---

## After Any Crash / Drop / Tip-Over

**Time: ~20 minutes for full inspection**

A crash or drop can cause hidden damage that isn't immediately visible. Always do a full inspection.

### Immediate Actions
1. Hit E-stop or power off immediately
2. Disconnect battery
3. Do NOT attempt to drive until inspection is complete

### Structural Inspection
- [ ] Check all 4 body quadrants for cracks (especially corners and bolt holes)
- [ ] Check all bearing bosses for cracks (the thin wall around each 608ZZ seat)
- [ ] Check rocker and bogie arms for fractures (flex gently by hand -- cracked PLA will creak)
- [ ] Check steering brackets for cracks (high stress concentration at pivot)
- [ ] Check differential bar adapters for cracks
- [ ] Check top deck tiles for broken clips

### Mechanical Verification
- [ ] Verify all 6 wheels spin freely (no bent shafts or jammed bearings)
- [ ] Verify all 4 servos respond to commands (no stripped gears -- listen for clicking/buzzing)
- [ ] Check all 8mm pivot shafts -- not bent (roll on flat surface to check)
- [ ] Verify suspension articulates fully on both sides

### Electronics Inspection
- [ ] Check electronics tray -- all components still seated on standoffs
- [ ] Check battery for puffing, dents, or puncture (CRITICAL -- damaged LiPo is a fire hazard)
- [ ] Check all JST connectors still plugged in
- [ ] Check for broken solder joints (especially motor capacitors and wire terminations)
- [ ] Visually inspect ESP32 and L298N boards for cracks or component damage

### Full System Test
- [ ] Power up (USB-C first, then battery)
- [ ] Verify WiFi AP appears
- [ ] Test all 6 motors individually (forward + reverse)
- [ ] Test all 4 servos individually (left, centre, right)
- [ ] Test E-stop
- [ ] Test each steering mode (Ackermann, point turn, crab walk)
- [ ] Drive forward 2 metres -- verify straight tracking

If ANY item fails inspection, repair before driving.

---

## Component Replacement SOPs

### Bearing Replacement (608ZZ)

**When**: Bearing feels gritty, seized, or has excessive play (>1mm axial).

1. Remove the relevant suspension arm (2x M3 bolts)
2. Push old bearing out from the opposite side using an 8mm rod and gentle taps with a mallet
3. Inspect the PLA bore:
   - If bore is round and undamaged: proceed to step 4
   - If bore is cracked, oval, or worn: reprint the part
4. Press new 608ZZ bearing in from the correct side (flush with outer face)
5. Use a flat surface (e.g., table) and press down firmly with palm -- do NOT hammer
6. Verify smooth rotation before reassembly
7. Reinstall arm with original bolts (check heat-set inserts are still solid)

**Spare bearings to keep on hand**: 2-3 (buy 608ZZ in packs of 10 -- they're cheap)

### Motor Replacement (N20)

**When**: Motor doesn't spin, makes grinding noise, or has significantly lower torque than others.

1. Disconnect motor JST-XH 2-pin connector from wiring harness
2. Remove wheel (loosen M2 grub screw with 1.5mm Allen key, pull wheel off shaft)
3. Unclip motor from N20 clip mount (flex clip gently, pull motor out)
4. Transfer the 100nF capacitor: desolder from old motor, solder to new motor terminals
   - Or solder a fresh 100nF cap if the old one is damaged
5. Clip new motor into mount
6. Reconnect JST-XH connector
7. Test motor direction: run forward command
   - If direction is wrong: swap the two motor wires at the JST connector
8. Reattach wheel, align D-flat, tighten M2 grub screw

### Servo Replacement (SG90)

**When**: Servo buzzes but doesn't move (stripped gears), jitters constantly, or doesn't respond.

1. Disconnect servo JST-XH 3-pin connector from wiring harness
2. Remove 2x servo mount screws (tiny Phillips from servo ears)
3. Remove servo horn screw (top centre)
4. Pull horn off servo spline
5. Pull old servo from servo mount pocket
6. Insert new servo into pocket
7. Secure with 2x screws (very gentle torque -- 0.2 N-m max)
8. Reconnect JST-XH connector
9. Command servo to centre (1500us / 90 degrees)
10. Attach horn at straight-ahead position (cross-type horn)
11. Tighten horn screw
12. Verify full +/-35 degree sweep -- no grinding, no binding

**SG90 gear strip indicator**: The servo buzzes loudly and you can feel vibration, but the output shaft doesn't move or moves erratically. This means the internal nylon gears have stripped. The servo cannot be repaired -- replace it.

### Battery Replacement / Upgrade

**Phase 1 options**:
| Battery | Capacity | Runtime (est.) | Notes |
|---------|----------|----------------|-------|
| 2S 2200mAh | 16.3 Wh | ~45 min | Standard, fits tray |
| 2S 3000mAh | 22.2 Wh | ~60 min | Same footprint, ~15% longer |
| 2S 5000mAh | 37.0 Wh | ~100 min | May need tray modification |

**Replacement procedure**:
1. Power off, disconnect old battery
2. Remove battery strap
3. Lift old battery out of tray cradle
4. Place new battery in cradle (verify polarity of XT30 connector!)
5. Secure with strap
6. Reconnect XT30
7. Power on, verify voltage reading on PWA

**Phase 2**: 6S 20Ah (completely different form factor, requires Phase 2 chassis)

### PLA Part Replacement

**When**: Part is cracked, warped, or degraded.

PLA parts are designed to be reprinted. Keep the Fusion 360 scripts and slicer profiles for easy replacement.

1. Identify the damaged part
2. Disassemble the minimum necessary to remove it (see disassembly-guide.md)
3. Reprint the part using original slicer settings (see print-strategy.md)
4. Install heat-set inserts in new part if required
5. Reassemble using original hardware
6. Run the relevant stage test gate from assembly-reference.md

**Common parts to keep as spares**: Body quadrant corners, steering brackets, servo mounts (these see the most stress).

---

## Maintenance Log Template

Keep a simple log of maintenance performed. This helps track wear patterns and predict when parts will need replacement.

```
Date: ________
Session #: ________
Runtime since last maintenance: ________ hours (estimate)

Checks performed:
- [ ] After-session visual inspection
- [ ] Weekly bearing/pivot check
- [ ] Monthly retorque
- [ ] Post-crash inspection

Issues found:
_________________________________
_________________________________

Actions taken:
_________________________________
_________________________________

Parts replaced:
_________________________________

Notes:
_________________________________
```

---

## Storage

### Short-term (between sessions)
- Remove battery, store in LiPo bag
- Store rover indoors, away from direct sunlight (UV degrades PLA)
- Cover with a cloth or place in a box to keep dust out of bearings

### Long-term (weeks/months)
- Remove battery and store separately (storage charge: 3.8V/cell = 7.6V for 2S)
- Remove any rubber bands, O-rings, or TPU tires (rubber degrades when stretched)
- Cover and store in a cool, dry location
- When returning to use: full monthly inspection before driving
