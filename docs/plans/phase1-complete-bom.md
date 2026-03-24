# Phase 1 Complete Bill of Materials

Every single part needed to build the 0.4-scale Mars Rover prototype.

---

## A. 3D PRINTED PARTS (PLA on CTC Bizer)

### A1. Wheels
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Wheel | 6 | 80 OD × 32 wide (86 over grousers) | PLA | 2hr ea | 20g ea |

Features per wheel: 3.1mm D-shaft bore, M2 grub screw, 3× O-ring grooves, 12× grousers
Total: 6 wheels, ~12hr print, ~210g PLA

### A2. Suspension — Rocker Arms (Split — 2 pieces per side)
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Rocker arm front half | 2 | 195 × 20 × 15 | PLA | 1.5hr ea | 18g ea |
| Rocker arm rear half | 2 | 105 × 20 × 15 | PLA | 1hr ea | 10g ea |

Features: 608ZZ bearing seats at body pivot (both halves) and bogie pivot (rear half), servo mount tab (front half), half-lap joint with 2× M3 bolts at body pivot.
Split required: full rocker span is 270mm, exceeds CTC Bizer 225mm bed.
Total: 4 pieces, ~5hr print, ~56g PLA

### A3. Suspension — Bogie Arms
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Bogie arm | 2 | 180 × 15 × 12 | PLA | 1.5hr ea | 18g ea |

Features per arm: 608ZZ seat at rocker pivot, motor mount faces at each end
Total: 2 arms, ~3hr print, ~30g PLA

### A4. Differential Bar
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Diff bar adapter | 3 | 30 × 30 × 20 | PLA | 30min ea | 8g ea |

Features per adapter: 608ZZ bearing seat (22.15mm bore × 7.2mm depth, 30mm boss OD, 0.3mm entry chamfer), 8mm through-bore (press-fit on rod). All 3 copies identical — print ×3.
Total: 3 adapters, ~1.5hr print, ~24g PLA

### A5. Steering Brackets
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Steering bracket | 4 | 35 × 30 × 40 | PLA | 45min ea | 12g ea |

Features per bracket: 608ZZ seat (top), 8mm pivot bore, N20 motor clip, servo horn slot
Locations: FL, FR, RL, RR
Total: 4 brackets, ~3hr print, ~48g PLA

### A6. Fixed Wheel Mounts
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Fixed mount | 2 | 25 × 25 × 30 | PLA | 30min ea | 8g ea |

Features per mount: N20 motor clip, M3 bolt holes to bogie arm
Locations: ML, MR (middle wheels)
Total: 2 mounts, ~1hr print, ~16g PLA

### A7. Body Frame
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Body quadrant FL | 1 | 130 × 220 × 80 | PLA | 8hr | 80g |
| Body quadrant FR | 1 | 130 × 220 × 80 | PLA | 8hr | 80g |
| Body quadrant RL | 1 | 130 × 220 × 80 | PLA | 10hr | 95g |
| Body quadrant RR | 1 | 130 × 220 × 80 | PLA | 10hr | 95g |

Features: 4mm walls, internal ribs, rocker pivot bosses (608ZZ seats, trimmed to quadrant bounds), diff bar mount, cable channels, vent slots, tongue-and-groove seams, alignment dowels, heat-set insert pockets, cable exit holes, LED underglow pass-through holes (4× 5mm dia through floor), headlight holes (FL/FR front wall), taillight holes (RL/RR rear wall). Kill switch hole on RR only.
Y-split at Y=0 (centre) — all 4 quadrants 130×220mm, fits 225×145mm bed
Total: 4 quadrants, ~36hr print, ~350g PLA

### A8. Electronics Tray
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Electronics tray | 1 | 120 × 180 × 18 | PLA | 3hr | 40g |

Features: ESP32 standoffs (4× M2.5), 2× L298N standoffs (4× M2.5 each), mini breadboard standoffs (4× M2.5), LiPo cradle (70×35×25mm recess), battery strap anchor posts (×2), 4× floor wire channels (10mm wide × 3mm deep), 3× wall cable exits (10×5mm)
Total: 1 tray, ~3hr print, ~40g PLA

### A9. Top Deck
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Top deck tile FL | 1 | 130 × 220 × 3 | PLA | 1hr | 15g |
| Top deck tile FR | 1 | 130 × 220 × 3 | PLA | 1hr | 15g |
| Top deck tile RL | 1 | 130 × 220 × 3 | PLA | 1hr | 15g |
| Top deck tile RR | 1 | 130 × 220 × 3 | PLA | 1hr | 15g |

Features: 3mm panel + edge lips (3mm hang-down on outer edges), snap clips on seam edges (4 per tile), stiffening ribs on underside (cross pattern, 2mm wide × 4mm deep). FR tile has 4× phone holder mounting bosses (8mm OD × 3mm tall, M3 heat-set insert holes, 60×80mm rectangle pattern).
Total: 4 tiles, ~4hr print, ~60g PLA

### A10. Servo Mounts
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Servo mount bracket | 4 | 40 × 15 × 25 | PLA | 20min ea | 5g ea |

Features: SG90 pocket (22.4×12.2×12mm), tab slot (32.4mm wide × 2.5mm), 2× M2 mount holes (27.5mm spacing, 2.4mm dia), 12mm circular horn slot (clears ±35°), 2× M3 heat-set inserts on bottom
Located on rocker/bogie arms near steering brackets
Total: 4 mounts, ~1.5hr print, ~20g PLA

### A11. Strain Relief Clips
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Strain relief clip | 10 | 18 × 10 × 11.5 | PLA | 10min ea | 2g ea |

Features per clip: U-channel (6mm wide × 5mm deep), snap tab, 2× M3 holes
Locations: rocker pivots (×4), bogie pivots (×4), body cable exits (×2)
Total: 10 clips, ~1.5hr print, ~20g PLA

### A12. Fuse Holder Bracket
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Fuse holder bracket | 1 | 15 × 40 × 12 | PLA | 15min | 4g |

Features: 8mm clip channel, 3mm end walls, 2× M3 mounting holes
Location: electronics tray or body wall near battery
Total: 1 bracket, ~15min print, ~4g PLA

### A13. Switch Mount Plate
| Part | Qty | Dimensions (mm) | Material | Print Time | Weight Est |
|------|-----|-----------------|----------|------------|------------|
| Switch mount plate | 1 | 30 × 30 × 5 | PLA | 15min | 3g |

Features: 15mm centre bore, 2× M3 diagonal holes, reinforcement plate
Location: inside RR body quadrant rear wall
Total: 1 plate, ~15min print, ~3g PLA

---

### PRINTED PARTS SUMMARY
| Category | Parts | Total Print Time | Total PLA |
|----------|-------|-----------------|-----------|
| Wheels (PLA rims) | 6 | 12hr | 120g (spoke holes save ~90g) |
| Rocker arm halves | 4 | 5hr | 56g |
| Bogie arms | 2 | 3hr | 36g (3mm walls, +6g) |
| Diff bar adapters | 3 | 1.5hr | 24g |
| Steering brackets | 4 | 3hr | 48g |
| Fixed mounts | 2 | 1hr | 16g |
| Body quadrants | 4 | 36hr | 510g (4mm walls, +160g) |
| Electronics tray | 1 | 3hr | 42g (corner gussets +2g) |
| Top deck | 4 | 4hr | 60g |
| Servo mounts | 4 | 1.5hr | 20g |
| Strain relief clips | 10 | 1.5hr | 20g |
| Fuse holder bracket | 1 | 0.25hr | 4g |
| Switch mount plate | 1 | 0.25hr | 3g |
| TPU tires (friend's printer) | 6 | ~6hr | 60g TPU |
| **TOTAL PLA** | **46 parts** | **~72hr** | **~1024g** |
| **TOTAL TPU** | **6 tires** | **~6hr** | **~60g** |

**PLA needed: 2× 1kg spools** (~1024g parts + ~260g supports/brim/waste/test prints = ~1284g total)
**TPU needed: 250g spool** (60g tires + margin for test prints)

---

## B. BEARINGS

| Part | Size | Qty | Purpose | Location |
|------|------|-----|---------|----------|
| 608ZZ | 8×22×7mm | 1 | Left rocker body pivot | Body left side |
| 608ZZ | 8×22×7mm | 1 | Right rocker body pivot | Body right side |
| 608ZZ | 8×22×7mm | 1 | Left rocker-bogie pivot | Left rocker rear |
| 608ZZ | 8×22×7mm | 1 | Right rocker-bogie pivot | Right rocker rear |
| 608ZZ | 8×22×7mm | 1 | Diff bar centre | Body centre |
| 608ZZ | 8×22×7mm | 1 | Diff bar left end | Left rocker |
| 608ZZ | 8×22×7mm | 1 | Diff bar right end | Right rocker |
| 608ZZ | 8×22×7mm | 1 | Steering pivot FL | Front left |
| 608ZZ | 8×22×7mm | 1 | Steering pivot FR | Front right |
| 608ZZ | 8×22×7mm | 1 | Steering pivot RL | Rear left |
| 608ZZ | 8×22×7mm | 1 | Steering pivot RR | Rear right |
| **TOTAL** | | **11** | | |

**Note**: All 4 steering positions (FL, FR, RL, RR) use 608ZZ bearings. Buy 12 (1 spare).

---

## C. MOTORS

| Part | Qty | Specs | Purpose |
|------|-----|-------|---------|
| N20 gearmotor 100RPM | 6 | 12×10×37mm, 3mm D-shaft, 6V | Wheel drive (×6) |
| SG90 micro servo | 4 | 22.2×11.8×22.7mm | Steering (FL, FR, RL, RR) |

---

## D. FASTENERS

### D1. M8 (Pivot Bolts)
| Part | Qty | Purpose |
|------|-----|---------|
| M8 × 40mm hex bolt | 4 | Rocker + bogie pivot shafts |
| M8 × 30mm hex bolt | 4 | Steering pivot shafts |
| M8 nyloc nut | 8 | Lock all M8 pivots |
| M8 flat washer | 16 | 2 per pivot (both sides) |

### D2. M3 (General Assembly)
| Part | Qty | Purpose |
|------|-----|---------|
| M3 × 12mm socket cap | 34 | Body joins, standoffs, brackets, rocker arm joints (×4) |
| M3 × 8mm socket cap | 20 | Electronics, motor clips |
| M3 nut | 30 | General |
| M3 flat washer | 30 | General |
| M3 × 5mm brass heat-set insert | 40 | 5.7mm OD, knurled |

### D3. M2 (Small Fasteners)
| Part | Qty | Purpose |
|------|-----|---------|
| M2 × 8mm pan head | 8 | SG90 servo mounting (4 servos × 2) |
| M2 × 4mm grub/set screw | 6 | Wheel hub shaft retention (tighten against D-flat on N20 shaft) |

### D4. Alignment
| Part | Qty | Purpose |
|------|-----|---------|
| 3mm × 20mm steel dowel pin | 4 | Body quadrant alignment |

---

## E. STRUCTURAL HARDWARE

| Part | Qty | Specs | Purpose |
|------|-----|-------|---------|
| 8mm steel rod | 1 | 300mm long, straight | Differential bar shaft (rocker pivots at X=±125mm = 250mm span + 25mm overhang each side for adapters) |
| Rubber O-ring | 18 | 70mm ID × 3mm cross-section | Wheel traction bands (3 per wheel) |
| 100nF ceramic capacitor | 7 | | Motor noise suppression (6x motor + 1x ADC) |

---

## F. ELECTRONICS

| Part | Qty | Specs | Purpose |
|------|-----|-------|---------|
| ESP32-S3 DevKitC-1 N16R8 | 1 | 69×25mm | Main controller |
| L298N motor driver | 2 | 43×43×27mm | 3 motors each |
| 2S LiPo battery | 1 | 7.4V 2200mAh, 70×35×18mm | Power |
| XT60 connector pair | 1 | | Battery connection |
| Toggle switch | 1 | 15mm panel mount | Main power |
| E-stop tactile button | 1 | Momentary, NC, panel mount | Emergency stop — cuts motor power (EA-15) |
| 5A mini blade fuse | 1 | ATC/ATO standard | Overcurrent protection |
| 5V 3A buck converter (XL4015) | 1 | Input 7-35V, output 5V 3A | Dedicated servo power — replaces L298N 5V regulator (EA-19) |
| LED (green) | 1 | 3mm or 5mm | Power indicator (EA-15) |
| Resistor 330 ohm | 1 | 1/4W | LED current limit / WS2812B data line series resistor (EA-15) |
| Mini breadboard | 1 | 47×35mm | Prototyping connections (47x35mm -- verify fits electronics tray standoff pattern) |
| Dupont jumper wires | 40 | M-M and M-F mix | Connections |
| JST-XH connectors | 6 | 2-pin | Motor connections |
| 22AWG silicone wire | 3m | Red, black, colours | Power + signal |

---

## G. WIRING

| Connection | Wire | Length Est | Notes |
|------------|------|-----------|-------|
| Battery → switch | 18AWG | 150mm | High current path |
| Switch → L298N × 2 | 18AWG | 200mm ea | Power distribution |
| L298N → motors × 6 | 22AWG | 300mm ea | Through cable channels |
| ESP32 → L298N × 2 | 22AWG signal | 150mm ea | PWM + direction |
| ESP32 → servos × 4 | 22AWG signal | 250mm ea | PWM signal |
| Servo power | 22AWG | 200mm | From 5V buck converter to servo rail |
| Buck converter input | 18AWG | 150mm | Battery rail → XL4015 input |
| Battery voltage divider | Resistors | On breadboard | ADC monitoring |

---

## H. CONSUMABLES & SUNDRIES

| Part | Qty | Purpose | Notes |
|------|-----|---------|-------|
| Small zip ties (100mm) | 20+ | Wire bundle management | At strain relief clips, arm pivots |
| Velcro cable ties | 10+ | Reusable wire management | Inside body, battery strap |
| Hot glue sticks (7mm) | 5+ | Strain relief, connector securing | Requires hot glue gun |

Note: 100nF capacitors listed in Section E. Heat shrink tubing listed in shopping list wiring section.

---

## I. OPTIONAL / RECOMMENDED

| Part | Qty | Purpose | Priority |
|------|-----|---------|----------|
| Loctite threadlock (blue) | 1 | M8 nyloc backup | Medium |
| Cyanoacrylate (super glue) | 1 | Emergency repairs | Low |
| Soldering iron (for heat-sets) | 1 | Insert installation | HIGH |
| Digital calipers | 1 | Calibration measurement | HIGH |
| 608ZZ bearing (spare) | 2 | In case of fit issues | Medium |
| PLA filament 1kg spool | 1 | Fresh, sealed | HIGH |
| SD card 8GB+ (for CTC Bizer) | 1 | x3g file transfer via SD card (CTC Bizer workflow) | HIGH |
| USB-C data cable (1m+) | 1 | ESP32-S3 programming and serial debug (development tool) | HIGH |

---

## COST ESTIMATE

| Category | Est Cost (GBP) |
|----------|---------------|
| 608ZZ bearings (×12 inc spares) | £8 |
| N20 motors (×6) | £18 |
| SG90 servos (×4) | £8 |
| M8 hardware kit | £5 |
| M3 hardware kit | £6 |
| M2 hardware kit (grub screws + servo screws) | £3 |
| 3mm dowel pins (×4) | £2 |
| Heat-set inserts (×50) | £6 |
| Steel rod 8mm × 300mm | £3 |
| O-rings (×20) | £4 |
| ESP32-S3 DevKitC-1 | £12 |
| L298N drivers (×2) | £6 |
| 5V 3A buck converter (servo BEC) | £3 |
| E-stop button + green LED + resistor | £1.50 |
| 2S LiPo 2200mAh | £12 |
| Wire, connectors, misc | £8 |
| PLA filament 2× 1kg | £28 |
| SD card 8GB (CTC Bizer) | £4 |
| USB-C data cable (ESP32) | £3 |
| **TOTAL** | **~£141** |

---

## ASSEMBLY ORDER

1. Print calibration pieces → calibrate printer
2. Print & test-fit: 1 wheel + 1 steering bracket + 1 motor
3. Print all wheels (×6)
4. Print steering brackets (×4) + fixed mounts (×2)
5. Print bogie arms (×2) + rocker arms (×2)
6. Print diff bar adapters (×3)
7. Sub-assemble: wheels + motors + brackets
8. Sub-assemble: bogie arms + middle/rear wheel assemblies
9. Sub-assemble: rocker arms + front wheel + bogie
10. Install diff bar + bearings
11. Print body quadrants (×4)
12. Join body quadrants
13. Install suspension into body
14. Print & install electronics tray
15. Wire everything
16. Flash firmware
17. Test drive!
