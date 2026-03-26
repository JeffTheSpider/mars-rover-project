# Phase 1 Complete Bill of Materials

Every single part needed to build the 0.4-scale Mars Rover prototype.
Updated to reflect EA-25/26 tube+connector suspension and EA-27 steering.

---

## A. 3D PRINTED PARTS (PLA on CTC Bizer)

### A1. Calibration & Test Pieces (print first)
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| CalibrationTestCard | 1 | 50 × 50 × 5 | 15min | 5g |
| BearingTestPiece | 1 | 33 × 33 × 12 | 20min | 6g |
| TubeSocketTest | 1 | 30 × 25 × 30 | 15min | 5g |

Purpose: Validate printer calibration, bearing press-fit (22.15mm bore), and 8mm tube socket (8.2mm bore) before committing to real parts.
Total: 3 pieces, ~50min print, ~16g PLA

### A2. Wheels
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| RoverWheelV3 | 6 | 86 OD × 32 wide (over grousers) | 2hr ea | 20g ea |
| RoverTire (TPU) | 6 | 86 OD × 70 bore × 32 wide | 1hr ea | 10g ea |

Features per wheel: 3.1mm D-shaft bore, M2 grub screw, 3× O-ring grooves, 12× grousers, 5 spokes
Tires: TPU 95A, requires friend's TPU-capable printer. Fallback: O-rings in wheel grooves.
Total: 6 wheels + 6 tires, ~18hr print, ~180g PLA + 60g TPU

### A3. Steering System (EA-27)
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| SteeringBracket | 4 | 35 × 30 × 25 | 45min ea | 12g ea |
| SteeringKnuckle | 4 | 25 × 30 × 35 | 30min ea | 8g ea |
| SteeringHornLink | 4 | 20 × 8 × 5 | 10min ea | 2g ea |
| ServoMount | 4 | 40 × 15 × 25 | 20min ea | 5g ea |

SteeringBracket: 608ZZ bearing seat (top), 8mm pivot bore (through), hard stop walls (±35°), 2× M3 clearance through-holes. Bolts to connector face.
SteeringKnuckle: Tapered body, 8mm pivot shaft bore (top), N20 motor clip (bottom), steering arm + hard stop tab.
SteeringHornLink: 20mm c/c 4-bar link, 2× M2 pin holes. Connects servo horn to knuckle steering arm.
ServoMount: SG90 pocket (22.4×12.2×12mm), horn slot (12mm), 2× M3 heat-set inserts on bottom face.
Total: 16 pieces, ~7hr print, ~108g PLA

### A4. Drivetrain
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| FixedWheelMount | 2 | 30 × 25 × 28 | 30min ea | 8g ea |

Features: N20 motor clip, 2× M3 clearance through-holes. Bolts to middle wheel connector face.
Locations: ML, MR (middle wheels — not steered)
Total: 2 mounts, ~1hr print, ~16g PLA

### A5. Suspension Connectors (EA-25/26 tube+connector approach)
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| RockerHubConnector | 2 | 55 × 45 × 45 | 1.5hr ea | 25g ea |
| BogiePivotConnector | 2 | 55 × 45 × 35 | 1hr ea | 20g ea |
| FrontWheelConnector | 4 | 35 × 30 × 45 | 45min ea | 12g ea |
| MiddleWheelConnector | 2 | 30 × 30 × 45 | 40min ea | 10g ea |
| DifferentialPivotHousing | 1 | 50 × 45 × 40 | 1.5hr | 25g |
| DifferentialLink | 2 | 30 × 12 × 8 | 10min ea | 3g ea |
| CableClip | 12 | 18 × 12 × 10 | 5min ea | 1g ea |

RockerHubConnector: Hub body with 608ZZ bearing seat (rocker pivot), 3× tube sockets (8.2mm bore × 15mm deep) for front/rear/up tubes, M3 heat-set inserts, wire channel. Mounts on diff bar.
BogiePivotConnector: 608ZZ bearing seat (bogie pivot), 2× tube sockets (front/rear), wire channel. At rocker-bogie junction.
FrontWheelConnector: Tube socket (from bogie), bearing-mount face with M3 heat-set inserts for steering bracket. At FL/FR/RL/RR corners.
MiddleWheelConnector: Tube socket (from bogie), motor-mount face with M3 heat-set inserts for fixed wheel mount. At ML/MR.
DifferentialPivotHousing: 608ZZ bearing seat (diff bar pivot), mounts under body centre. Diff bar passes through.
DifferentialLink: Through-bar linkage rod with M3 rod-end bearing holes at each end. Connects diff bar to rocker hubs (EA-26).
CableClip: Snap-on cable management for 8mm tubes. 6mm U-channel, M3 attachment hole.
Total: 25 pieces, ~13hr print, ~180g PLA

### A6. Body Frame
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| BodyQuadrant FL | 1 | 130 × 220 × 120 | 8hr | 80g |
| BodyQuadrant FR | 1 | 130 × 220 × 120 | 8hr | 80g |
| BodyQuadrant RL | 1 | 130 × 220 × 120 | 10hr | 95g |
| BodyQuadrant RR | 1 | 130 × 220 × 120 | 10hr | 95g |

Features: 4mm walls, internal ribs, rocker pivot bosses, cable channels, vent slots, tongue-and-groove seams, alignment dowels (3mm), heat-set insert pockets, LED holes, headlight/taillight holes. Kill switch hole on RR only.
Y-split at Y=0 — all 4 quadrants ~130×220mm, fits 225×145mm CTC Bizer bed.
Total: 4 quadrants, ~36hr print, ~350g PLA

### A7. Top Deck
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| TopDeck FL | 1 | 130 × 220 × 3 | 1hr | 15g |
| TopDeck FR | 1 | 130 × 220 × 3 | 1hr | 15g |
| TopDeck RL | 1 | 130 × 220 × 3 | 1hr | 15g |
| TopDeck RR | 1 | 130 × 220 × 3 | 1hr | 15g |

Features: 3mm panel + edge lips, snap clips on seam edges, stiffening ribs (underside). FR tile has phone holder mounting bosses (M3 heat-set inserts).
Total: 4 tiles, ~4hr print, ~60g PLA

### A8. Internal Components
| Part | Qty | Dimensions (mm) | Print Time | Weight Est |
|------|-----|-----------------|------------|------------|
| ElectronicsTray | 1 | 120 × 180 × 18 | 3hr | 40g |
| BatteryTray | 1 | 94 × 42 × 23 | 1hr | 15g |
| StrainReliefClip | 10 | 18 × 10 × 11.5 | 10min ea | 2g ea |
| FuseHolderBracket | 1 | 15 × 40 × 12 | 15min | 4g |
| SwitchMount | 1 | 30 × 30 × 5 | 15min | 3g |

ElectronicsTray: ESP32 edge-clip cradle, 2× L298N standoffs, breadboard standoffs, wire channels, cable exits.
BatteryTray: 86×34×19mm LiPo cradle, strap slots, XT60+JST-XH access cutouts, corner gussets.
StrainReliefClip: U-channel (6mm wide × 5mm deep), snap tab, 2× M3 holes. At cable routing points.
FuseHolderBracket: 8mm clip channel, 2× M3 mounting holes.
SwitchMount: 15mm centre bore, 2× M3 diagonal holes. Inside RR body quadrant.
Total: 14 pieces, ~6hr print, ~82g PLA

---

### PRINTED PARTS SUMMARY
| Category | Parts | Total Print Time | Total PLA |
|----------|-------|-----------------|-----------|
| Calibration/test | 3 | 50min | 16g |
| Wheels (PLA rims) | 6 | 12hr | 120g |
| Steering system | 16 | 7hr | 108g |
| Drivetrain (fixed mounts) | 2 | 1hr | 16g |
| Suspension connectors | 25 | 13hr | 180g |
| Body quadrants | 4 | 36hr | 350g |
| Top deck tiles | 4 | 4hr | 60g |
| Internal components | 14 | 6hr | 82g |
| TPU tires (friend's printer) | 6 | ~6hr | 60g TPU |
| **TOTAL PLA** | **74 parts** | **~80hr** | **~932g** |
| **TOTAL TPU** | **6 tires** | **~6hr** | **~60g** |

**PLA needed: 2× 1kg spools** (~932g parts + ~350g supports/brim/waste/test prints = ~1282g total)
**TPU needed: 250g spool** (60g tires + margin for test prints)

---

## B. BEARINGS

| Part | Size | Qty | Purpose | Location |
|------|------|-----|---------|----------|
| 608ZZ | 8×22×7mm | 1 | Left rocker body pivot | RockerHubConnector L |
| 608ZZ | 8×22×7mm | 1 | Right rocker body pivot | RockerHubConnector R |
| 608ZZ | 8×22×7mm | 1 | Left rocker-bogie pivot | BogiePivotConnector L |
| 608ZZ | 8×22×7mm | 1 | Right rocker-bogie pivot | BogiePivotConnector R |
| 608ZZ | 8×22×7mm | 1 | Diff bar centre pivot | DifferentialPivotHousing |
| 608ZZ | 8×22×7mm | 1 | Steering pivot FL | SteeringBracket FL |
| 608ZZ | 8×22×7mm | 1 | Steering pivot FR | SteeringBracket FR |
| 608ZZ | 8×22×7mm | 1 | Steering pivot RL | SteeringBracket RL |
| 608ZZ | 8×22×7mm | 1 | Steering pivot RR | SteeringBracket RR |
| **TOTAL** | | **9** | | |

**Note**: EA-26 through-bar diff mechanism — no bearings at diff bar ends (DifferentialLinks use M3 rod-end bearings instead). Buy 12 (9 + 3 spares).

---

## C. MOTORS

| Part | Qty | Specs | Purpose |
|------|-----|-------|---------|
| N20 gearmotor 100RPM | 6 | 12×10×24mm (15mm can + 9mm gearbox), 3mm D-shaft, 6V, ~10g | Wheel drive (×6) |
| SG90 micro servo | 4 | 22.2×11.8×22.7mm, 9g, 1.8 kg-cm at 4.8V | Steering (FL, FR, RL, RR) |

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
| M3 × 12mm socket cap | 34 | Body joins, standoffs, brackets, connector bolting |
| M3 × 8mm socket cap | 20 | Electronics, motor clips |
| M3 nut | 30 | General |
| M3 flat washer | 30 | General |
| M3 × 5mm brass heat-set insert | 40 | 5.7mm OD, knurled — in connectors, body, servo mounts |

### D3. M2 (Small Fasteners)
| Part | Qty | Purpose |
|------|-----|---------|
| M2 × 8mm pan head | 8 | SG90 servo mounting (4 servos × 2) |
| M2 × 4mm grub/set screw | 6 | Wheel hub shaft retention |
| M2 × 10mm socket cap | 8 | Steering horn link pin joints (EA-27) |
| M2 nyloc nut | 8 | Horn link pin retention (EA-27) |
| M2 nylon flat washer | 16 | Horn link smooth rotation (EA-27) |

### D4. Alignment
| Part | Qty | Purpose |
|------|-----|---------|
| 3mm × 20mm steel dowel pin | 4 | Body quadrant alignment |

---

## E. STRUCTURAL HARDWARE

| Part | Qty | Specs | Purpose |
|------|-----|-------|---------|
| 8mm steel rod | 2 | 1m lengths — cut to: 1×400mm (diff bar), 2×150mm (rocker front), 6×60mm (rocker rear + bogie) | Suspension tube framework |
| M3 rod-end bearing (heim joint) | 4 | Ball joint, M3 thread | Differential links (2 links × 2 ends, EA-26) |
| M3 × 20mm bolt | 4 | | Through-bolt for rod-end bearings to diff link ends |
| 8mm shaft collar | 4 | Bore 8mm, set screw | Retain diff bar + rocker pivot shafts |
| Rubber O-ring | 18 | 70mm ID × 3mm cross-section | Wheel traction bands (3/wheel) — only if NOT using TPU tires |
| 100nF ceramic capacitor | 7 | | Motor noise suppression (6× motor + 1× ADC) |

**Rod cutting plan** (from 2× 1m rods):
| Rod | Cut | Length | Purpose |
|-----|-----|--------|---------|
| Rod 1 | 1 | 400mm | Differential bar |
| Rod 1 | 2-3 | 2× 150mm | Left + right rocker front tubes |
| Rod 1 | 4-6 | 3× 60mm | Rocker rear + bogie short tubes |
| Rod 2 | 1-3 | 3× 60mm | Remaining bogie short tubes |
| Rod 2 | - | 820mm spare | Future use |

Total: 9 tube pieces, ~1060mm from 2000mm stock.

---

## F. ELECTRONICS

| Part | Qty | Specs | Purpose |
|------|-----|-------|---------|
| ESP32-S3 DevKitC-1 N16R8 | 1 | 63×25mm, USB-C | Main controller |
| L298N motor driver | 2 | 43×43×27mm | 3 motors each |
| 2S LiPo battery | 1 | 7.4V 2200mAh, 86×34×19mm | Power |
| XT60 connector pair | 1 | | Battery connection |
| Toggle switch | 1 | 15mm panel mount | Main power |
| E-stop tactile button | 1 | Momentary, NC, panel mount | Emergency stop (EA-15) |
| 5A mini blade fuse | 1 | ATC/ATO standard | Overcurrent protection |
| 5V 3A buck converter (XL4015) | 1 | Input 7-35V, output 5V 3A | Dedicated servo power (EA-19) |
| LED (green) | 1 | 3mm or 5mm | Power indicator |
| Resistor 330 ohm | 1 | 1/4W | LED current limit |
| Mini breadboard | 1 | 47×35mm | Prototyping connections |
| Dupont jumper wires | 40 | M-M and M-F mix | Connections |
| JST-XH connectors | 6 | 2-pin | Motor connections |
| 22AWG silicone wire | 3m | Red, black, colours | Power + signal |

---

## G. WIRING

| Connection | Wire | Length Est | Notes |
|------------|------|-----------|-------|
| Battery → switch | 18AWG | 150mm | High current path |
| Switch → L298N × 2 | 18AWG | 200mm ea | Power distribution |
| L298N → motors × 6 | 22AWG | 300mm ea | Through cable channels + tubes |
| ESP32 → L298N × 2 | 22AWG signal | 150mm ea | PWM + direction |
| ESP32 → servos × 4 | 22AWG signal | 250mm ea | PWM signal |
| Servo power | 22AWG | 200mm | From 5V buck converter to servo rail |
| Buck converter input | 18AWG | 150mm | Battery rail → XL4015 input |
| Battery voltage divider | Resistors | On breadboard | ADC monitoring |

---

## H. CONSUMABLES & SUNDRIES

| Part | Qty | Purpose | Notes |
|------|-----|---------|-------|
| Small zip ties (100mm) | 20+ | Wire bundle management | At strain relief clips, tube junctions |
| Velcro cable ties | 10+ | Reusable wire management | Inside body, battery strap |
| Hot glue sticks (7mm) | 5+ | Strain relief, connector securing | Requires hot glue gun |

---

## I. OPTIONAL / RECOMMENDED

| Part | Qty | Purpose | Priority |
|------|-----|---------|----------|
| Loctite threadlock (blue) | 1 | M8 nyloc backup | Medium |
| Cyanoacrylate (super glue) | 1 | Emergency repairs | Low |
| Soldering iron (for heat-sets) | 1 | Insert installation | HIGH |
| Digital calipers | 1 | Calibration measurement | HIGH |
| 608ZZ bearing (spare) | 3 | In case of fit issues | Medium |
| PLA filament 1kg spool | 1 | Fresh, sealed | HIGH |
| SD card 8GB+ (for CTC Bizer) | 1 | x3g file transfer | HIGH |
| USB-C data cable (1m+) | 1 | ESP32-S3 programming | HIGH |

---

## COST ESTIMATE

| Category | Est Cost (GBP) |
|----------|---------------|
| 608ZZ bearings (×12 inc spares) | £8 |
| N20 motors (×6) | £18 |
| SG90 servos (×4) | £8 |
| M8 hardware kit | £5 |
| M3 hardware kit + heat-set inserts | £12 |
| M2 hardware kit (grub + servo + horn link) | £5 |
| 3mm dowel pins (×4) | £2 |
| Steel rod 8mm × 1m (×2) | £6 |
| Shaft collars (×4) | £3 |
| Rod-end bearings M3 (×4) | £3 |
| O-rings (×20) (only if no TPU) | £4 |
| ESP32-S3 DevKitC-1 | £12 |
| L298N drivers (×2) | £6 |
| 5V 3A buck converter | £3 |
| E-stop + LED + resistor | £1.50 |
| 2S LiPo 2200mAh | £12 |
| Wire, connectors, misc | £8 |
| PLA filament 2× 1kg | £28 |
| SD card 8GB | £4 |
| USB-C data cable | £3 |
| **TOTAL** | **~£153** |

---

## ASSEMBLY ORDER

1. Print calibration pieces → calibrate CTC Bizer
2. Print & test-fit: 1 bearing test + 1 tube socket test → verify 608ZZ and 8mm rod fit
3. Print 1 wheel + 1 steering bracket → test-fit with N20 motor and 608ZZ bearing
4. Print all wheels (×6)
5. Print steering: brackets (×4) + knuckles (×4) + horn links (×4) + servo mounts (×4)
6. Print drivetrain: fixed wheel mounts (×2)
7. Cut 8mm rods to length (9 pieces from 2× 1m rods)
8. Print suspension connectors: rocker hub (×2) + bogie pivot (×2) + wheel connectors (×4+2)
9. Print diff housing (×1) + diff links (×2) + cable clips (×12)
10. Sub-assemble: wheels + motors + brackets/knuckles on connectors
11. Sub-assemble: bogie arms (tube + connectors + middle/rear wheels)
12. Sub-assemble: rocker arms (tube + connectors + front wheel + bogie)
13. Install diff bar + bearings + links
14. Print body quadrants (×4) — longest print batch (~36hr)
15. Print top deck tiles (×4)
16. Join body quadrants with dowels + M3 bolts
17. Install suspension into body via rocker pivot bearings
18. Print & install electronics tray + battery tray
19. Print accessories: strain relief (×10) + fuse bracket + switch mount
20. Wire everything (EA-19, EA-23)
21. Flash firmware
22. Test drive!

---

*Phase 1 BOM v2.0 — 2026-03-26 — Updated for EA-25/26/27 tube+connector design*
