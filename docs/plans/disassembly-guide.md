# Phase 1 Disassembly Guide

## Overview

This guide covers the complete disassembly of the Phase 1 Mars Rover prototype, as well as partial disassembly procedures for common tasks. Disassembly is essentially the reverse of the assembly-reference.md, but with important fragility warnings and wire disconnect sequencing.

**Read the fragility notes before starting.** PLA parts are brittle and do not tolerate prying, twisting, or over-torquing. Work slowly and methodically.

---

## Safety First

**ALWAYS perform these steps before ANY disassembly, even partial.**

1. **Power off ESP32** -- hold reset button or disconnect USB-C
2. **Disconnect battery FIRST** -- pull the XT30 connector apart (grip the connector body, not the wires)
3. **Wait 10 seconds** for capacitors on L298N boards to discharge
4. **Remove battery from rover** -- lift out of tray cradle, store in LiPo-safe bag
5. **Verify power is off** -- no LEDs lit on ESP32 or L298N boards

> Never work on a powered rover. Even "off" with the switch, the battery is still connected to the fuse and switch terminals. Disconnect the XT30.

---

## Wire Disconnect Sequence

Wires must be disconnected in a specific order to avoid accidental shorts or damage.

### Disconnect Order (power off first!)
1. **Battery** -- XT30 connector (already done in safety steps above)
2. **Motor connectors** -- 6x JST-XH 2-pin (one per motor)
3. **Servo connectors** -- 4x JST-XH 3-pin (one per servo)
4. **Sensor / signal connectors** -- E-stop, battery ADC, encoders (if any)
5. **ESP32 USB-C** -- last to disconnect

### Reconnect Order (REVERSE -- ESP32 first, battery last)
1. **ESP32 USB-C** -- verify boot and WiFi before connecting power
2. **Sensor / signal connectors**
3. **Servo connectors** -- 4x JST-XH 3-pin
4. **Motor connectors** -- 6x JST-XH 2-pin
5. **Battery** -- XT30 connector (last! Only after all other connections verified)

> Label every JST connector before disconnecting. Use painter's tape and a marker. Labels like "M-LF" (motor left front), "S-RR" (servo right rear), etc. You will thank yourself during reassembly.

---

## Full Disassembly Procedure

### Step 1: Remove Top Deck Tiles (~2 min)

- Locate the snap clips on each of the 4 top deck tiles (FL, FR, RL, RR)
- **Lift straight up** -- do NOT pry from the side
- If clips are tight, gently press inward on the clip tabs while lifting
- Set tiles aside on a soft surface (clips are fragile)

**FRAGILITY WARNING**: Top deck clips are thin PLA, typically 1-2mm. They break easily if pried from the wrong angle or if the tile is twisted during removal. Always lift straight up. If a clip breaks, the tile can be reprinted.

### Step 2: Disconnect All JST Connectors (~5 min)

- Follow the wire disconnect sequence above
- Grip each JST connector by the plastic housing, NOT by the wires
- Pull straight out -- do not wiggle side to side
- As you disconnect each one, label it with painter's tape
- Take a photo of the electronics tray wiring layout before disconnecting (helpful for reassembly)

**TIP**: If a JST connector is stuck, use tweezers or needle-nose pliers to grip the connector body. Never pull by the wires -- they will rip out of the crimp terminals.

### Step 3: Lift Out Electronics Tray (~2 min)

- Verify ALL wires between tray and body/suspension are disconnected
- Check for any wires still routed through body cable exit slots
- Lift tray straight up and out of the body
- Set aside on a clean, dry, non-conductive surface (NOT on a metal table)

**FRAGILITY WARNING**: If any wire is still connected and you lift the tray, you will rip the wire out of its solder joint or pull a JST connector apart. Double-check everything is disconnected.

### Step 4: Remove Body Quadrant Bolts (~5 min)

- Remove all M3 x 12mm bolts from the body seams
- Use 2.5mm Allen key
- Keep bolts organised -- bag and label:
  - "X-seam front" (between FL and FR)
  - "X-seam rear" (between RL and RR)
  - "Y-seam left" (between FL and RL)
  - "Y-seam right" (between FR and RR)
- This matters less for identical bolts, but helps if you have mixed lengths

### Step 5: Separate Body Quadrants (~5 min)

- Separate front pair from rear pair first (Y-seam, usually the easier joint)
- Then separate FL from FR, and RL from RR (X-seams)
- **Pull apart gently** -- dowel pins may be tight
- If dowel pins resist, do NOT pry with a screwdriver against PLA -- you will gouge it
- Instead: grip both quadrants firmly, one in each hand, and pull straight apart with steady force
- If truly stuck: gently tap on the dowel pin end with a small punch from inside to push it out

**FRAGILITY WARNING**: Body quadrant corners are stress concentration points, especially around bolt holes. Do not twist quadrants relative to each other. Pull straight apart only.

### Step 6: Remove Wheels (~5 min)

- Loosen each M2 grub screw with 1.5mm Allen key
- Pull wheel straight off motor D-shaft
- If wheel is stuck: do NOT twist or pry. The D-flat may be jammed. Loosen grub screw fully and pull firmly.
- Keep grub screws with their respective wheels (push screw back into hole finger-tight)

### Step 7: Remove Motors (~5 min)

- Motor JST connectors should already be disconnected (Step 2)
- Flex the N20 motor clip gently and pull motor straight out
- Do NOT yank motor by its wires
- If motor is stuck in clip: gently flex the clip open with a flat screwdriver blade, then pull motor

**FRAGILITY WARNING**: N20 motor clips are thin PLA. Excessive flexing will snap the clip. Be gentle. If a clip breaks, the entire parent part (bogie arm, steering bracket, or fixed wheel mount) needs reprinting.

### Step 8: Remove Servo Mounts (~10 min)

- Remove the 2x tiny Phillips screws from each servo's ears
- Pull servo out of mount pocket
- Remove the 2x M3 bolts attaching servo mount to steering bracket (2.5mm Allen key)
- Separate servo mount from bracket

**FRAGILITY WARNING**: Servo mount screw holes are small and in thin PLA. They strip very easily. When removing the Phillips screws, press firmly into the screw head while turning to avoid cam-out. If a screw hole strips, you can reprint the servo mount or use a slightly larger screw.

### Step 9: Separate Suspension Arms (~10 min)

This is the most involved step. Support both sides of each joint while removing bolts.

- Remove M3 bolts at each suspension joint (2x per joint)
- Support both the rocker and bogie arm while removing the last bolt -- unsupported arms can fall and bend the 8mm pivot shaft
- Slide 8mm pivot pins out of bearings
- Separate front wheel assemblies from rocker arms
- Unbolt rocker arm halves (front + rear) if full disassembly is needed

**FRAGILITY WARNING**: Heat-set insert bosses can pull out if a bolt is seized and you apply too much torque. If a bolt doesn't turn easily, try a drop of penetrating oil on the thread (unusual for new builds but possible if grit has entered the thread).

### Step 10: Remove Bearings (ONLY if replacing)

**Do NOT remove bearings unless they are being replaced.** Press-fit bearings deform the PLA bore slightly each time they are inserted or removed. After 2-3 removal cycles, the bore will be too loose to hold a bearing.

If removal is necessary:
1. Support the part firmly on a flat surface
2. Place an 8mm rod (or bolt) against the bearing inner race from the opposite side
3. Tap gently with a small mallet
4. Bearing should push out -- if it doesn't move, tap slightly harder but remain controlled
5. Inspect bore for cracks or deformation
6. If bore is damaged: reprint the part (do not try to glue a bearing into a damaged bore under load)

---

## Partial Disassembly Guides

These cover the most common maintenance tasks without a full teardown.

### "Just access electronics" (~2 min)

For firmware updates, wiring changes, or component swaps:

1. Remove top deck tiles (lift straight up)
2. Disconnect USB-C if connected
3. Disconnect battery XT30
4. Lift out electronics tray

No need to touch body, suspension, or wheels.

### "Replace one body quadrant" (~15 min)

For reprinting a cracked or damaged quadrant:

1. Remove top deck tiles
2. Disconnect any wires that route through the damaged quadrant's cable slots
3. Remove M3 bolts on the two seams adjacent to the damaged quadrant
4. Pull out dowel pins
5. Remove damaged quadrant
6. Install new quadrant (with heat-set inserts already installed)
7. Reinsert dowel pins, bolt seams
8. Re-route wires, replace top deck tiles

### "Swap a motor" (~5 min)

For replacing a dead or noisy motor:

1. Disconnect motor JST-XH 2-pin connector (trace wire from the wheel)
2. Remove wheel (loosen M2 grub screw, pull off shaft)
3. Unclip motor from N20 clip (flex clip gently)
4. Transfer 100nF capacitor to new motor (or solder a new cap)
5. Clip new motor into mount
6. Reconnect JST connector
7. Test motor direction -- swap wires if reversed
8. Reattach wheel, tighten grub screw against D-flat

### "Replace a servo" (~10 min)

For replacing a servo with stripped gears:

1. Disconnect servo JST-XH 3-pin connector
2. Remove servo horn screw (top centre Phillips)
3. Pull horn off spline
4. Remove 2x tiny Phillips screws from servo ears
5. Pull servo from mount pocket
6. Insert new servo
7. Secure with 2x screws (gentle!)
8. Reconnect JST connector
9. Command servo to centre (90 degrees / 1500us)
10. Attach horn at straight-ahead position
11. Tighten horn screw
12. Verify full +/-35 degree sweep

### "Replace a bearing" (~15 min)

For a seized or gritty bearing:

1. Remove the relevant suspension arm from the rover (2x M3 bolts)
2. Remove wheel and motor from that arm (if bearing is at wheel end)
3. Push old bearing out with 8mm rod + mallet from opposite side
4. Inspect bore (reprint part if bore is damaged)
5. Press new 608ZZ bearing in (flush with outer face)
6. Verify smooth rotation
7. Reinstall motor, wheel, and arm

### "Access battery only" (~1 min)

For charging or battery swap:

1. Remove FR or FL top deck tile (just one is enough)
2. Disconnect XT30 connector
3. Loosen battery strap
4. Lift battery out
5. Reverse to reinstall

---

## Fragility Reference Table

Quick reference for the most fragile parts and how to handle them.

| Part | Fragile Feature | Risk | Handling |
|------|----------------|------|----------|
| Top deck tiles | Snap clips (1-2mm PLA) | Break if pried sideways | Lift straight up only |
| Body quadrant corners | Bolt holes, thin walls | Crack if twisted | Pull straight apart, no twisting |
| Servo mount | Screw holes (small PLA) | Strip if over-torqued | Max 0.2 N-m, press firmly while turning |
| Heat-set insert bosses | PLA around brass insert | Pull out if over-torqued | Max 0.5 N-m for M3 bolts |
| N20 motor clips | Thin PLA flex arms | Snap if over-flexed | Gentle flex only, replace parent part if broken |
| Wire-to-motor solder joints | Solder joint on motor terminal | Break if wire pulled | Handle at connector, not at solder joint |
| 608ZZ bearing bores | PLA bore wall | Deforms with repeated removal | Remove only if replacing, reprint if loose |
| Steering bracket pivot | Thin wall around bearing | Cracks from impact | Inspect after any crash |
| Wheel spoke holes | Lightening cutouts | Stress risers | Avoid dropping wheels on hard surfaces |
| ESP32 PCB | Solder pads, antenna | Crack if flexed or dropped | Handle by edges, don't press on components |

---

## Reassembly Notes

After any disassembly, reassemble following the assembly-reference.md stage order. Key reminders:

1. **Run each test gate** as you complete each stage -- do not skip ahead
2. **Check heat-set inserts** before bolting -- if any spin, re-set with soldering iron (175C)
3. **Label wires** before disconnecting and verify labels during reconnection
4. **Torque limits** -- never exceed 0.5 N-m for M3 into PLA inserts, 0.2 N-m for servo screws
5. **Battery last** -- always the final connection when reassembling
6. **First power-up sequence** -- USB-C first, verify boot, then battery (see Stage 9 in assembly-reference.md)

---

## Hardware Organisation

When doing a full disassembly, keep hardware organised to make reassembly straightforward.

### Suggested Bag Labels
- **Bag A**: Body seam bolts (M3 x 12mm) + dowel pins
- **Bag B**: Rocker half-join bolts (M3 x 12mm)
- **Bag C**: Servo mount bolts (M3 x 8mm)
- **Bag D**: Servo Phillips screws (tiny, from servo package)
- **Bag E**: Wheel grub screws (M2 x 4mm, keep with wheels)
- **Bag F**: Pivot shafts (8mm rod sections)
- **Bag G**: Differential bar (300mm, 8mm rod)
- **Bag H**: Diff bar adapters + grub screws

Use small zip-lock bags or a compartmented parts organiser. Do not pile all fasteners together -- M3 x 8mm and M3 x 12mm look nearly identical but are different lengths.
