# Engineering Analysis 06: Detailed Cost Breakdown

**Document**: EA-06
**Date**: 2026-03-15
**Purpose**: Provide a detailed, research-backed cost estimate for each build phase, with specific product recommendations and a prioritised shopping list.
**Depends on**: EA-01 through EA-05 (all component selections)

---

## 1. Phase 1: 0.4 Scale Prototype

**Goal**: Validate rocker-bogie mechanics, basic driving. ESP32-S3 only, no AI.

| # | Component | Specification | Qty | Unit Price | Total | Source |
|---|-----------|--------------|-----|-----------|-------|--------|
| 1 | ESP32-S3 DevKit | N16R8, USB-C | 1 | $8 | $8 | AliExpress |
| 2 | N20 DC gearmotors (6V, 100RPM) | With encoder | 6 | $3 | $18 | AliExpress |
| 3 | SG90 micro servos | 1.8 kg·cm | 4 | $2 | $8 | AliExpress |
| 4 | L298N motor drivers | Dual H-bridge | 2 | $3 | $6 | AliExpress |
| 5 | 2S LiPo 2200mAh | 7.4V, XT30 | 1 | $12 | $12 | HobbyKing/Amazon |
| 6 | LiPo charger | 2S balance charger | 1 | $8 | $8 | Amazon |
| 7 | PLA/PETG filament | 500g spool | 1 | $10 | $10 | Amazon |
| 8 | 608ZZ bearings (Phase 1 pivot) | 8mm bore, or 3mm mini | 10 | $0.50 | $5 | Amazon |
| 9 | M3 fastener set | Bolts, nuts, washers | 1 set | $6 | $6 | Amazon |
| 10 | M3 heat-set inserts | Brass, for PETG | 50 | $0.06 | $3 | AliExpress |
| 11 | Breadboard + jumper wires | For prototyping | 1 | $5 | $5 | Amazon |
| 12 | Switch + wiring | Power switch, wire | 1 | $3 | $3 | Amazon |
| | | | | **Phase 1 Total** | **$92** | |

### Phase 1 Shopping List (Order of Purchase)

1. **First order (start printing while waiting)**: Filament ($10)
2. **Second order (electronics)**: ESP32-S3, motors, servos, L298N, wiring ($48)
3. **Third order (assembly)**: Bearings, fasteners, heat-set inserts, battery ($34)

---

## 2. Phase 2: Full-Scale 3D Printed + Extrusion

**Goal**: Complete rover with all features, fully functional.

### 2.1 Compute & Electronics

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 1 | Jetson Orin Nano Super DevKit | 1 | $249 | $249 |
| 2 | ESP32-S3 DevKit | 1 | $8 | $8 |
| 3 | PCA9685 16-ch PWM driver | 1 | $3 | $3 |
| 4 | USB 3.0 hub (powered) | 1 | $12 | $12 |
| 5 | microSD card 128GB (Jetson) | 1 | $10 | $10 |
| 6 | microSD card 128GB (recording) | 1 | $10 | $10 |
| | **Subtotal: Compute** | | | **$292** |

### 2.2 Cameras & Vision

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 7 | Arducam 120° USB cameras | 4 | $15 | $60 |
| 8 | ELP 10× optical zoom USB | 1 | $50 | $50 |
| 9 | OAK-D Lite depth camera | 1 | $89 | $89 |
| 10 | Pi NoIR Camera v3 (CSI) | 1 | $25 | $25 |
| 11 | IR LED 850nm (high power) | 4 | $1.25 | $5 |
| | **Subtotal: Cameras** | | | **$229** |

### 2.3 Navigation Sensors

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 12 | RPLidar A1 | 1 | $73 | $73 |
| 13 | BN-220 GPS (u-blox M8) | 1 | $12 | $12 |
| 14 | BNO055 IMU breakout | 1 | $15 | $15 |
| 15 | HC-SR04 ultrasonic | 6 | $1.50 | $9 |
| | **Subtotal: Nav Sensors** | | | **$109** |

### 2.4 Drivetrain

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 16 | Chihai 37mm 12V 80RPM w/encoder | 6 | $12 | $72 |
| 17 | Cytron MDD10A motor drivers | 3 | $15 | $45 |
| 18 | MG996R steering servos | 4 | $6 | $24 |
| | **Subtotal: Drivetrain** | | | **$141** |

### 2.5 Robotic Arms & Mast

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 19 | MG996R arm servos | 8 | $6 | $48 |
| 20 | MG996R mast servos | 2 | $6 | $12 |
| 21 | Slip ring (12-wire, 22mm) | 1 | $8 | $8 |
| | **Subtotal: Arms/Mast** | | | **$68** |

### 2.6 Power System

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 22 | Turnigy 6S 10000mAh 12C LiPo | 2 | $50 | $100 |
| 23 | 6S BMS board (30A) | 2 | $8 | $16 |
| 24 | 6S LiPo balance charger | 1 | $20 | $20 |
| 25 | Buck converter 22V→12V (10A) | 1 | $5 | $5 |
| 26 | Buck converter 22V→5V (8A) | 1 | $4 | $4 |
| 27 | UBEC 22V→6V (5A) | 1 | $8 | $8 |
| 28 | XT90 connectors (pair) | 4 | $1.50 | $6 |
| 29 | Blade fuse holder + fuses | 4 | $2 | $8 |
| 30 | E-stop mushroom button | 1 | $3 | $3 |
| 31 | Main relay (30A, 24V coil) | 1 | $5 | $5 |
| 32 | Silicone wire (10-16 AWG assorted) | lot | $10 | $10 |
| | **Subtotal: Power** | | | **$185** |

### 2.7 Solar

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 33 | 25W monocrystalline panels | 4 | $20 | $80 |
| 34 | CN3722 solar MPPT module | 1 | $15 | $15 |
| 35 | Panel hinges (stainless spring) | 4 | $2 | $8 |
| | **Subtotal: Solar** | | | **$103** |

### 2.8 Accessories

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 36 | Peltier TEC1-12706 | 1 | $4 | $4 |
| 37 | Aluminium heatsink + fan (fridge) | 1 | $8 | $8 |
| 38 | Foam insulation (fridge lining) | 1 | $3 | $3 |
| 39 | Qi wireless charger module (15W) | 1 | $8 | $8 |
| 40 | USB-C PD trigger board | 1 | $4 | $4 |
| 41 | USB-A panel mount port | 1 | $2 | $2 |
| 42 | WS2812B LED strip (2m, 60/m) | 1 | $8 | $8 |
| 43 | High-power white LEDs (3W, headlights) | 2 | $1.50 | $3 |
| 44 | Red LEDs + amber LEDs (indicators) | 8 | $0.50 | $4 |
| 45 | 3W speakers | 2 | $3 | $6 |
| 46 | MAX98357A I2S amp | 1 | $4 | $4 |
| 47 | SPH0645 MEMS microphone | 2 | $3 | $6 |
| 48 | BME280 breakout | 1 | $3 | $3 |
| 49 | Cup anemometer (small) | 1 | $12 | $12 |
| 50 | YL-83 rain sensor | 1 | $2 | $2 |
| 51 | VEML6075 UV sensor | 1 | $3 | $3 |
| 52 | BH1750 light sensor | 1 | $2 | $2 |
| 53 | INA219 current sensor | 4 | $2 | $8 |
| 54 | DS18B20 temp sensor | 3 | $1.50 | $4.50 |
| 55 | 3.5" IPS LCD (SPI) | 1 | $12 | $12 |
| | **Subtotal: Accessories** | | | **$96.50** |

### 2.9 Structure & Hardware

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 56 | PETG filament (1kg spools) | 4 | $15 | $60 |
| 57 | 2020 V-slot aluminium extrusion (1m) | 6 | $4 | $24 |
| 58 | 2020 corner brackets | 20 | $0.50 | $10 |
| 59 | 2020 T-nuts | 50 | $0.15 | $7.50 |
| 60 | 608ZZ bearings | 19 | $0.50 | $9.50 |
| 61 | M3 heat-set inserts | 100 | $0.06 | $6 |
| 62 | M3 bolt/nut assortment | 1 set | $8 | $8 |
| 63 | M4 bolt/nut assortment | 1 set | $6 | $6 |
| 64 | M5 bolt/nut assortment | 1 set | $6 | $6 |
| 65 | Nyloc nuts assortment | 1 set | $4 | $4 |
| 66 | Cable ties + heatshrink | lot | $5 | $5 |
| 67 | Connectors (JST, Dupont, barrel) | lot | $8 | $8 |
| | **Subtotal: Structure** | | | **$154** |

### 2.10 Docking Station

| # | Component | Qty | Unit Price | Total |
|---|-----------|-----|-----------|-------|
| 68 | Spring copper contact pads | 4 | $2 | $8 |
| 69 | 24V 5A power supply | 1 | $12 | $12 |
| 70 | ArUco marker (printed) | 1 | $0 | $0 |
| 71 | Base plate (plywood/acrylic) | 1 | $5 | $5 |
| | **Subtotal: Docking** | | | **$25** |

---

## 3. Phase 2 Cost Summary

| Category | Cost |
|----------|------|
| Compute & Electronics | $292 |
| Cameras & Vision | $229 |
| Navigation Sensors | $109 |
| Drivetrain | $141 |
| Arms & Mast | $68 |
| Power System | $185 |
| Solar | $103 |
| Accessories | $96.50 |
| Structure & Hardware | $154 |
| Docking Station | $25 |
| **Phase 2 Total** | **$1,402.50** |

### With 10% Contingency

| | Amount |
|---|--------|
| Phase 2 components | $1,402.50 |
| Contingency (10%) | $140.25 |
| **Phase 2 Budget Total** | **$1,542.75** |

---

## 4. Phase 3: Metal Build (Additional Costs)

| # | Component | Cost |
|---|-----------|------|
| 1 | Aluminium sheet (1.5mm, 2m²) | $60 |
| 2 | Aluminium rectangular tube (rocker/bogie arms) | $25 |
| 3 | Steel rod (axles, differential bar) | $15 |
| 4 | Upgraded servos: 4× DS3218 (steering) | $40 |
| 5 | 6001-2RS sealed bearings (replace 608ZZ) | $15 |
| 6 | Paint / powder coat / anodising | $30 |
| 7 | Weatherproof gaskets + cable glands (IP54) | $15 |
| 8 | Tempered glass top panel (optional) | $25 |
| 9 | Stainless steel fasteners upgrade | $15 |
| 10 | Machining consumables (drill bits, taps) | $20 |
| | **Phase 3 Additional Total** | **$260** |
| | Contingency (15%) | $39 |
| | **Phase 3 Budget Total** | **$299** |

---

## 5. Grand Total

| Phase | Component Cost | Contingency | Budget Total |
|-------|---------------|-------------|-------------|
| Phase 1 (0.4 prototype) | $92 | included | $92 |
| Phase 2 (full 3D print) | $1,402.50 | $140.25 | $1,542.75 |
| Phase 3 (metal, additional) | $260 | $39 | $299 |
| **Grand Total** | **$1,754.50** | **$179.25** | **$1,933.75** |

### Budget Assessment

**$1,933.75 falls within the $1,500-2,000 target budget.** There is ~$66 of headroom for unexpected costs.

### Cost Reduction Options (if needed)

| Saving | Action | Impact |
|--------|--------|--------|
| -$100 | Buy Jetson Orin Nano 8GB ($149) instead of Super ($249) | Lower AI FPS (40 vs 67 TOPS), still functional |
| -$89 | Skip OAK-D Lite, use stereo camera pair instead | Lose on-device AI, need software depth estimation |
| -$103 | Defer solar panels to later | No solar charging, mains/dock only |
| -$73 | Defer RPLidar, use ultrasonic-only navigation | Lose SLAM mapping, basic obstacle avoidance only |
| -$68 | Defer robotic arms to later | Lose manipulation, simpler build |
| -$96 | Skip accessories (fridge, weather, speaker) | Core rover still functional without luxuries |

If budget is tight, the rover is fully functional with just: **compute + cameras + drivetrain + power + structure = $764**. Everything else can be added incrementally.

---

## 6. Prioritised Build Order (Phase 2)

Suggested purchasing order to spread costs and test incrementally:

| Order | Components | Cost | What It Enables |
|-------|-----------|------|-----------------|
| 1 | Structure: filament, extrusion, fasteners, bearings | $154 | Print and assemble chassis |
| 2 | Drivetrain: motors, drivers, steering servos | $141 | Rolling chassis, basic driving |
| 3 | Power: batteries, BMS, converters, wiring | $185 | Powered driving |
| 4 | Compute: Jetson, ESP32, SD cards, USB hub | $292 | Smart brain installed |
| 5 | Body cameras: 4× Arducam | $60 | 360° vision |
| 6 | Nav sensors: LIDAR, GPS, IMU, ultrasonic | $109 | Autonomous navigation |
| 7 | Depth + zoom cameras | $139 | Full vision suite |
| 8 | Arms + mast: servos, slip ring | $68 | Manipulation |
| 9 | Solar: panels, MPPT, hinges | $103 | Solar charging |
| 10 | Accessories: fridge, LEDs, weather, speaker, display | $96 | Full feature set |
| 11 | Docking station | $25 | Autonomous charging |
| 12 | Night vision: NoIR camera, IR LEDs | $30 | Night capability |

---

## 7. References

All prices based on searches conducted 2026-03-15 from UK/international sources:
- Amazon UK, AliExpress, HobbyKing, Pololu, SparkFun, Adafruit
- Prices are approximate and subject to change
- Shipping costs not included (estimated additional 5-10%)

---

*Document EA-06 v1.0 — 2026-03-15*
