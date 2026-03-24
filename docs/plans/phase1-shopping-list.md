# Phase 1 Shopping List

**Budget**: ~£80 (EA-06 estimates $102 / ~£80 at current rates)
**Purpose**: 0.4 scale prototype — basic driving and steering validation
**Date**: 2026-03-15

---

## Electronics

### 1. Microcontroller

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| ESP32-S3 DevKitC-1 N16R8 (USB-C) | 1 | £7 | [AliExpress](https://www.aliexpress.com/w/wholesale-esp32-s3-devkitc-1-n16r8.html) / [Amazon UK](https://www.amazon.co.uk/s?k=esp32-s3+devkitc) | 16MB flash, 8MB PSRAM. Get the official Espressif layout or YD-ESP32-S3 clone. Must be N16R8 variant for Phase 2 PSRAM needs. Amazon ~£12 but faster delivery. |

### 2. Motor Drivers

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| L298N Dual H-Bridge Motor Driver Module | 2 | £2.50 each (£5) | [Amazon UK](https://www.amazon.co.uk/s?k=L298N+motor+driver) / [The Pi Hut](https://thepihut.com) | Each board drives 2 motor channels. W2+W3 wired in parallel on L298N #1 channel B; W5+W4 in parallel on #2 channel B. Onboard 5V regulator powers ESP32 + servos. |

### 3. Motors

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| GA12-N20 DC Gearmotor 6V 100RPM with Hall Encoder | 6 | £2.50 each (£15) | [AliExpress](https://www.aliexpress.com/w/wholesale-n20-gear-motor-encoder-100rpm-6v.html) / [Amazon UK](https://www.amazon.co.uk/s?k=N20+gear+motor+encoder+100rpm) | **IMPORTANT: Confirm GA12-N20, 1:100 gear ratio, metal gearbox, 3mm D-shaft**. Rated torque ~2 kg·cm, stall ~10-16 kg·cm. Plastic gearbox versions strip under load — insist on metal. 12×10×37mm body. AliExpress ~£1.50 each (2-4 week shipping). Amazon ~£3-4 each. |

### 4. Servos

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| SG90 Micro Servo 9g | 4 | £1.50 each (£6) | [Amazon UK](https://www.amazon.co.uk/s?k=SG90+micro+servo) / [The Pi Hut](https://thepihut.com/products/tower-pro-sg90-digital-9g-micro-servo) | 1.8 kg-cm at 4.8V, sufficient for 1 kg prototype steering. Comes with mounting screws and horn set. MG90S (metal gear, ~£3 each) is a worthy upgrade if budget allows — more durable. |

### 5. Sensors (Optional for Phase 1)

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| BNO055 IMU Breakout (9-DOF) | 1 | £12 | [Pimoroni](https://shop.pimoroni.com) / [Amazon UK](https://www.amazon.co.uk/s?k=BNO055+breakout) | Optional for Phase 1 — useful for tilt/orientation testing but not required for basic driving. Defer to Phase 2 if budget-tight. I2C address 0x28. |
| HC-SR04 Ultrasonic Sensor | 2 | £1.50 each (£3) | [Amazon UK](https://www.amazon.co.uk/s?k=HC-SR04+ultrasonic) / [CPC Farnell](https://cpc.farnell.com) | Optional — 2 front-facing for basic obstacle detection. Defer to Phase 2 if budget-tight. |

### 6. Power

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| 2S LiPo 7.4V 2200mAh (XT60) | 1 | £10 | [Amazon UK](https://www.amazon.co.uk/s?k=2S+LiPo+2200mAh) / [HobbyKing UK](https://hobbyking.com) | 30C+ discharge rating. Check connector matches your charger. XT60 standard throughout. Gives ~45 min runtime at 3A draw. |
| 2S/3S LiPo Balance Charger | 1 | £8 | [Amazon UK](https://www.amazon.co.uk/s?k=2S+LiPo+balance+charger) | IMAX B6 mini clone or similar. Essential safety item — never charge LiPo without a balance charger. If you already own one, skip this. |
| LiPo Safe Bag | 1 | £4 | [Amazon UK](https://www.amazon.co.uk/s?k=lipo+safe+bag) | Fireproof charging/storage bag. Non-negotiable safety item for LiPo use. |

### 7. Safety

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| Mini Toggle Switch (SPST, panel mount) | 1 | £1 | [Amazon UK](https://www.amazon.co.uk/s?k=mini+toggle+switch+panel+mount) / [CPC Farnell](https://cpc.farnell.com) | Main power switch. 15mm panel mount hole in rear body wall. Rated for 5A+ at 12V. |
| Inline Blade Fuse Holder + 5A Fuse | 1 | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=inline+blade+fuse+holder) | Between battery and L298N power rail. Protects against short circuits. |
| E-Stop Tactile Button (momentary, NC, panel mount) | 1 | £1 | [Amazon UK](https://www.amazon.co.uk/s?k=momentary+push+button+panel+mount+normally+closed) / [CPC Farnell](https://cpc.farnell.com) | Emergency stop — normally-closed momentary button. Press to cut motor power. Wired in series with motor power rail. Panel mount in body wall. See EA-15 safety systems. |
| Green LED (3mm or 5mm) + 330 ohm Resistor | 1 | £0.50 | [Amazon UK](https://www.amazon.co.uk/s?k=green+LED+5mm) / [CPC Farnell](https://cpc.farnell.com) | Power indicator — lights when main switch is on. Mount in body wall near switch. 330 ohm resistor (WS2812B data line series resistor). See EA-15. |

### 8. Servo Power

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| 5V 3A Buck Converter (XL4015 or similar) | 1 | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=5V+3A+buck+converter+XL4015) / [AliExpress](https://www.aliexpress.com/w/wholesale-5V+3A+buck+converter.html) | **CRITICAL**: Dedicated 5V servo power supply. Replaces L298N onboard 5V regulator which cannot supply 4 servos + ESP32 reliably under load. Input 7-35V from battery, output 5V 3A. Wired to servo power rail only. See EA-19 wiring diagram. |

---

## Mechanical

### 1. Bearings

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| 608ZZ Bearings (8x22x7mm) | 12 | £0.40 each (£5) | [Amazon UK](https://www.amazon.co.uk/s?k=608ZZ+bearings) | Phase 1 needs 9: 2 rocker pivots, 2 bogie pivots, 1 diff pivot, 4 steering pivots (EA-25/EA-26). Buy 12 for spares. Same as skateboard bearings — buy a 10-pack + 2 singles, or a 20-pack for Phase 2 stock. |

### 2. Fasteners

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| M3 Heat-Set Inserts (OD 5.7mm, L 4.6mm, brass) | 50 pack | £4 | [Amazon UK](https://www.amazon.co.uk/s?k=M3+heat+set+inserts+brass) / [CNC Kitchen style from AliExpress](https://www.aliexpress.com/w/wholesale-m3-heat-set-insert.html) | CNC Kitchen / Ruthex style knurled brass. Hole prints at 4.8mm; insert melts into plastic. Need ~40 for Phase 1 body + brackets (more with 4-segment body). Get 100-pack (£6) if planning ahead for Phase 2. **PLA insert temp: ~170-180C** (lower than PETG's 200-220C) — go slow to avoid melting surrounding plastic. |
| M3 Socket Cap Screw Assortment (6/8/10/12/16/20mm) | 1 set | £5 | [Amazon UK](https://www.amazon.co.uk/s?k=M3+socket+cap+screw+assortment) | Need ~50 screws in various lengths. A 300-piece assortment box covers Phase 1 and Phase 2. |
| M3 Nut + Washer Assortment | 1 set | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=M3+nut+washer+assortment) | Often bundled with screw kits. Need ~30 nuts, ~30 washers. |
| M8 x 40mm Hex Bolt | 4 | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=M8+hex+bolt+40mm) / Local hardware store | Rocker + bogie pivot shafts. Stainless preferred. |
| M8 x 30mm Hex Bolt | 4 | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=M8+hex+bolt+30mm) | Steering pivot shafts. |
| M8 Nyloc Nuts | 8 | £1.50 | [Amazon UK](https://www.amazon.co.uk/s?k=M8+nyloc+nut) | Lock nuts for all M8 pivots — prevents loosening under vibration. |
| M8 Washers | 16 | £1.50 | [Amazon UK](https://www.amazon.co.uk/s?k=M8+washer+stainless) | 2 per pivot (both sides of each bearing). |
| M2 x 8mm Screws | 8 | £1 | [Amazon UK](https://www.amazon.co.uk/s?k=M2+screw+assortment) | SG90 servo mounting (4 servos x 2 screws). Often included with servo packaging. |
| M2 × 4mm Grub/Set Screws (hex socket) | 6 | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=M2+grub+set+screw+4mm) / [CPC Farnell](https://cpc.farnell.com) | Wheel hub shaft retention — tighten against D-flat on N20 3mm shaft to prevent wheels slipping. 1 per wheel. Buy a few spares. See wheel CAD script. |
| M2 × 10mm Socket Cap Screws | 8 | £1 | [Amazon UK](https://www.amazon.co.uk/s?k=M2+socket+cap+screw+10mm) | Steering horn link pin joints — 2 per link × 4 links. Stainless preferred. EA-27. |
| M2 Nyloc Nuts | 8 | £1 | [Amazon UK](https://www.amazon.co.uk/s?k=M2+nyloc+nut) | Horn link pin retention — self-locking, essential for vibration. EA-27. |
| M2 Nylon Flat Washers | 16 | £1 | [Amazon UK](https://www.amazon.co.uk/s?k=M2+nylon+washer) | Horn link pin joints — 2 per pin, smooth rotation on PLA. EA-27. |
| 3mm × 20mm Steel Dowel Pins | 4 | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=3mm+steel+dowel+pin+20mm) / [RS Components](https://uk.rs-online.com) | Body quadrant alignment — press-fit into matching 3.0mm holes at quadrant seams. Prevents lateral shift when bolting quadrants together. See EA-08 body design. |

### 3. Shafts

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| 8mm Steel Rod, 1m length | 2 | £3 each (£6) | [Amazon UK](https://www.amazon.co.uk/s?k=8mm+steel+rod+1m) / Local hardware store / [RS Components](https://uk.rs-online.com) | Cut to lengths: 1× 400mm (diff bar, EA-26), 2× 150mm (rocker front tubes), 6× 60mm (2 rocker rear + 2 bogie front + 2 bogie rear). 8mm fits 608ZZ bearing inner race. Silver steel or mild steel both fine. Total ~1060mm — needs 2× 1m rods. |
| 8mm Shaft Collars (bore 8mm) | 4 | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=8mm+shaft+collar) | Retain diff bar ends + rocker pivot shafts. Alternatively use printed adapters with M3 grub screws. |
| M3 Rod-End Bearings (Heim joints) | 4 | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=M3+rod+end+bearing+heim+joint) / [AliExpress](https://www.aliexpress.com/w/wholesale-M3+rod+end+bearing.html) | For differential links — ball joints at each end of each link (2 links × 2 ends). Allow angular misalignment between diff bar (X-axis) and rocker (Y-axis). See EA-26 Section 9. |
| M3 x 20mm Bolts (for diff links) | 4 | £1 | Included in M3 assortment | Through-bolts for attaching rod-end bearings to diff link bar ends. |

---

## 3D Printing

**Printer**: CTC 3D Bizer (225×145mm bed) — PLA only (no PETG or TPU capability).

> **Body segmentation**: The CTC Bizer's 225×145mm bed requires the rover body (440×260mm at 0.4 scale) to be split into **4 quadrants** to fit the build plate. All quadrants are ~220×130mm (Y_SPLIT=0, pivot boss trimmed to bounds). This adds ~4 joining surfaces, increasing total filament usage by ~50g and requiring ~24 additional heat-set inserts for segment-to-segment bolting.

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| PLA Filament 1.75mm, 1kg spool | 2 | £14 each (£28) | [Amazon UK](https://www.amazon.co.uk/s?k=PLA+filament+1kg) | Recommended brand: eSUN PLA+ or Sunlu PLA — both print well and are widely available on Amazon UK. Total print weight ~850g + 280g waste/failures = ~1130g (extra joining surfaces from 4-segment body). Two spools gives comfortable margin. Colour: grey or black (mars rover aesthetic). |

> **Wheel traction (preferred)**: Separate **TPU 95A tires** (rover_tire.py) press-fit onto PLA rims. Requires a friend's TPU-capable printer or online printing service. 86mm OD × 70mm bore × 32mm wide, 48 tread ribs. ~10g each.
>
> **Wheel traction (fallback)**: If no TPU printer available, set `USE_TPU_TIRE=False` in rover_wheel.py to enable O-ring groove mode. Use **rubber O-rings** (70mm ID × 3mm cross-section) in wheel rim grooves. Buy a bag of 20+ (~£3).

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| TPU 95A Filament 250g (optional) | 1 | £8 | [Amazon UK](https://www.amazon.co.uk/s?k=TPU+95A+filament) | For 6 tires on a friend's TPU-capable printer. 60g needed + margin. |
| O-Rings 70mm ID × 3mm (fallback) | 20 | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=70mm+ID+3mm+O-ring) | Only needed if NOT using TPU tires. 18 needed (3 per wheel × 6) + spares. |

---

## Wiring & Connectors

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| 22AWG Silicone Wire (6 colours, 5m each) | 1 set | £6 | [Amazon UK](https://www.amazon.co.uk/s?k=22AWG+silicone+wire+set) | Signal wires for motors, servos, encoders. Silicone is flexible and heat-resistant. |
| 18AWG Silicone Wire (red + black, 3m each) | 1 set | £4 | [Amazon UK](https://www.amazon.co.uk/s?k=18AWG+silicone+wire) | Power wires from battery to L298N boards. |
| JST-XH Connector Kit (2.54mm pitch) | 1 kit | £6 | [Amazon UK](https://www.amazon.co.uk/s?k=JST+XH+connector+kit) | For making neat motor/servo connections. Includes 2/3/4/5-pin housings + crimps. |
| Dupont Connector Kit (2.54mm) | 1 kit | £5 | [Amazon UK](https://www.amazon.co.uk/s?k=dupont+connector+kit) | For breadboard jumper wires and ESP32 header connections. Male + female pins + housings. |
| XT60 Connectors (male + female pair) | 2 pairs | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=XT60+connector) | Battery to power switch connection. Match your LiPo connector type. |
| Half-Size Breadboard (400 tie points) | 1 | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=half+size+breadboard) / [Pimoroni](https://shop.pimoroni.com) | For prototyping servo/encoder connections before soldering. |
| Heat Shrink Tubing Assortment | 1 kit | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=heat+shrink+tubing+assortment) | Various diameters (1.5-10mm). Essential for insulating solder joints. |
| Voltage Divider Resistors: 10k + 4.7k (1/4W) | 2 each | £0.50 | [Amazon UK](https://www.amazon.co.uk/s?k=resistor+assortment) / [CPC Farnell](https://cpc.farnell.com) | For battery voltage monitoring on GPIO14. Buy a resistor assortment kit if you don't have one. |

---

## Consumables & Sundries

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| 100nF Ceramic Capacitors (104) | 6+ | £1 | [Amazon UK](https://www.amazon.co.uk/s?k=100nF+ceramic+capacitor) / [CPC Farnell](https://cpc.farnell.com) | Motor terminal noise suppression — solder one across each motor's ±terminals. Buy a pack of 20-50 (cheap). Referenced in CLAUDE.md conventions and EA-19. |
| Small Zip Ties (100mm) | 1 bag (100) | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=100mm+zip+ties) | Wire bundle management at strain relief points, securing motor wires to suspension arms. Referenced in EA-17, EA-19. |
| Velcro Cable Ties (reusable) | 1 pack (20) | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=velcro+cable+ties) | Reusable wire management inside body, battery retention strap. Referenced in EA-08, EA-14. |
| Hot Glue Sticks (7mm, clear) | 1 pack (20) | £2 | [Amazon UK](https://www.amazon.co.uk/s?k=hot+glue+sticks+7mm) | Strain relief at solder joints, securing connectors, temporary fixturing. Referenced in EA-19. Requires hot glue gun. |

---

## Tools (if not already owned)

| Item | Qty | Approx Price | Where to Buy | Notes |
|------|-----|-------------|--------------|-------|
| Soldering Iron (temperature controlled) | 1 | £25-40 | [Amazon UK](https://www.amazon.co.uk/s?k=soldering+iron+temperature+controlled) | If you don't have one. Pinecil or TS100 are excellent portable options. Need pointed tip for wiring + conical tip for heat-set inserts. |
| Heat-Set Insert Tip (for soldering iron) | 1 | £5 | [Amazon UK](https://www.amazon.co.uk/s?k=heat+set+insert+tip+soldering+iron) / [CNC Kitchen](https://cnckitchen.store) | M3 size. Fits most soldering irons with standard tips. Makes inserting brass inserts clean and straight. |
| Wire Stripper / Crimper | 1 | £8 | [Amazon UK](https://www.amazon.co.uk/s?k=wire+stripper+crimper) | Self-adjusting type recommended. Essential for JST/Dupont crimping. |
| Multimeter | 1 | £10-15 | [Amazon UK](https://www.amazon.co.uk/s?k=digital+multimeter) | If you don't have one. Needed for voltage checks, continuity testing. |
| Hex Key Set (1.5, 2, 2.5, 4, 5mm) | 1 set | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=hex+key+set+metric) | 2mm for M3 socket caps, 5mm for M8 hex bolts. |
| SD Card 8GB (or larger) | 1 | £4 | [Amazon UK](https://www.amazon.co.uk/s?k=sd+card+8gb) | For CTC Bizer printer — load x3g files via SD card. Not a rover component but essential for print workflow. Any speed class works. |
| USB-C Cable (data + power, 1m+) | 1 | £3 | [Amazon UK](https://www.amazon.co.uk/s?k=USB-C+data+cable) | ESP32-S3 programming and serial debug. Must be a data cable (not charge-only). 1-2m length for comfortable bench work. |

---

## Total Estimated Cost

### Core Components (required)

| Category | Estimated Cost |
|----------|---------------|
| Microcontroller (ESP32-S3) | £7 |
| Motor drivers (2x L298N) | £5 |
| Motors (6x N20 w/ encoder) | £15 |
| Servos (4x SG90) | £6 |
| Power (2S LiPo + charger + safe bag) | £22 |
| Servo power (5V 3A buck converter) | £3 |
| Safety (switch + fuse + E-stop + LED) | £4.50 |
| Bearings (12x 608ZZ) | £5 |
| Fasteners (M3 set + M8 + M2 grub screws + dowel pins + heat-set inserts) | £24 |
| Shafts (8mm rod + collars) | £4 |
| Filament (2x 1kg PLA) | £28 |
| Wiring & connectors | £30 |
| **Core Total** | **~£153** |

### Consumables & Sundries

| Category | Estimated Cost |
|----------|---------------|
| 100nF ceramic capacitors | £1 |
| Zip ties (100mm bag) | £2 |
| Velcro cable ties | £3 |
| Hot glue sticks | £2 |
| **Consumables Total** | **~£8** |

### Optional Phase 1 Items

| Category | Estimated Cost |
|----------|---------------|
| BNO055 IMU | £12 |
| HC-SR04 ultrasonic (x2) | £3 |
| Rubber O-rings 70mm ID × 3mm (wheel traction) | £3 |
| **Optional Total** | **~£18** |

### Tools (if needed)

| Category | Estimated Cost |
|----------|---------------|
| Soldering iron | £30 |
| Heat-set insert tip | £5 |
| Wire stripper/crimper | £8 |
| Multimeter | £12 |
| Hex key set | £3 |
| SD card 8GB (CTC Bizer) | £4 |
| USB-C cable (ESP32 programming) | £3 |
| **Tools Total** | **~£65** |

### Budget Summary

| | Cost |
|---|------|
| Core components | ~£153 |
| Consumables & sundries | ~£8 |
| Optional sensors/traction | ~£18 |
| Tools (if needed) | ~£65 |
| **Grand Total (everything)** | **~£244** |
| **Grand Total (core + consumables, have tools)** | **~£161** |

> **Note**: The EA-06 estimate of $102/~£80 assumes AliExpress pricing for most components with 2-4 week shipping and only 1x 500g filament spool. The figures above use Amazon UK pricing (typically 1.5-2x AliExpress) and 2x 1kg PLA spools for realistic print margin. To hit the EA-06 budget, order motors, ESP32, servos, drivers, heat-set inserts, and connectors from AliExpress (~£50 saving) and accept the longer delivery time.

---

## Recommended Buy Order

### Order 1: Filament (buy now, start printing while waiting for electronics)

| Item | Cost | Why First |
|------|------|-----------|
| 2x PLA filament (1kg) | £28 | ~65 hours of printing ahead. Start with bearing test piece, then wheels, then structural parts. Body needs 4 quadrants to fit CTC Bizer's 225×145mm bed — start printing early. Printing can happen in parallel with electronics shipping. |

### Order 2: Electronics (buy next — AliExpress for budget, Amazon for speed)

| Item | Source | Cost |
|------|--------|------|
| ESP32-S3 DevKitC-1 N16R8 | AliExpress (£7) or Amazon (£12) | £7-12 |
| 6x N20 100RPM motors w/ encoder | AliExpress (£10) or Amazon (£18) | £10-18 |
| 4x SG90 servos | AliExpress (£4) or Amazon (£6) | £4-6 |
| 2x L298N motor drivers | AliExpress (£3) or Amazon (£5) | £3-5 |
| Breadboard | Amazon | £3 |
| Dupont connector kit | Amazon | £5 |
| Wire (22AWG + 18AWG) | Amazon | £10 |

**Why second**: You need the ESP32 and motors in hand to bench-test before final assembly. Order from AliExpress early to overlap with print time.

### Order 3: Mechanical Hardware (buy once CAD is finalised and first prints are done)

| Item | Source | Cost |
|------|--------|------|
| 12x 608ZZ bearings | Amazon | £5 |
| M3 fastener set + heat-set inserts | Amazon | £12 |
| M8 bolts, nyloc nuts, washers | Amazon / hardware store | £7 |
| M2 × 4mm grub screws (×6) + 3mm dowel pins (×4) | Amazon | £4 |
| 8mm steel rod + shaft collars | Amazon / hardware store | £4 |

**Why third**: You need actual printed parts in hand to verify bearing press-fit dimensions and bolt lengths before committing to quantities.

### Order 4: Power (buy last — only when ready for powered testing)

| Item | Source | Cost |
|------|--------|------|
| 2S LiPo 2200mAh | Amazon | £10 |
| LiPo balance charger | Amazon | £8 |
| LiPo safe bag | Amazon | £4 |
| Power switch + fuse holder + E-stop button | Amazon | £4 |
| Green LED + 330 ohm resistor | Amazon | £0.50 |
| 5V 3A buck converter (servo BEC) | Amazon / AliExpress | £3 |
| XT60 connectors | Amazon | £2 |
| JST-XH connector kit | Amazon | £6 |
| Heat shrink tubing | Amazon | £3 |
| Resistors (voltage divider) | Amazon | £0.50 |

**Why last**: No point having a LiPo sitting around while printing and assembling. It only becomes relevant once the chassis is built and electronics are wired. Bench testing can use a USB power bank or lab supply.

---

## Bench Testing Checklist (before full assembly)

Once Order 2 arrives, test these on the breadboard before building into the chassis:

- [ ] ESP32-S3 powers on via USB, uploads firmware (Arduino IDE / PlatformIO)
- [ ] L298N drives a single N20 motor forward/reverse via ESP32 PWM
- [ ] SG90 servo sweeps 0-180 degrees via ESP32 LEDC
- [ ] Encoder pulses read correctly on ESP32 GPIO interrupt
- [ ] 5V buck converter outputs stable 5V under servo load (check with multimeter)
- [ ] All 6 motors spin (test each individually)
- [ ] E-stop button cuts motor power when pressed, restores when released
- [ ] Battery voltage divider reads correctly on GPIO14 ADC
- [ ] Green power LED illuminates when main switch is on

---

*Phase 1 Shopping List v1.0 — 2026-03-15*
