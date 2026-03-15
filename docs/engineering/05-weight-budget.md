# Engineering Analysis 05: Weight Budget

**Document**: EA-05
**Date**: 2026-03-15
**Purpose**: Estimate total rover weight component-by-component, calculate centre of gravity, and determine impact on motor torque and power requirements.

---

## 1. Phase 2 Weight Budget (Full-Scale 3D Printed + Extrusion)

This is the primary weight estimate. Phase 2 is the first fully-featured build.

### 1.1 Subsystem 1: Chassis & Suspension

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| 2020 aluminium extrusion (body frame, 6m total) | 6m | 0.28 kg/m | 1,680g | Standard 2020 spec |
| 2020 extrusion (rocker arms, 2×450mm) | 0.9m | 0.28 kg/m | 252g | Standard 2020 spec |
| 2020 extrusion (bogie arms, 2×300mm) | 0.6m | 0.28 kg/m | 168g | Standard 2020 spec |
| 2020 extrusion (differential bar, 500mm) | 0.5m | 0.28 kg/m | 140g | Standard 2020 spec |
| 3D printed body panels (PETG, ~25 panels) | 25 | ~60g | 1,500g | ~220×130×3mm panels, 30% infill |
| 3D printed connectors/brackets | ~40 | ~15g | 600g | Heat-set insert brackets |
| 608ZZ bearings | 19 | 12g | 228g | Standard skateboard bearing |
| Wheel hubs (3D printed + motor mount) | 6 | 80g | 480g | PETG, 60% infill |
| Wheel tyres/treads (rubber or TPU) | 6 | 50g | 300g | 200mm dia, ~80mm wide |
| M3/M4/M5 fasteners, nuts, washers | lot | — | 300g | Estimated |
| **Subtotal: Chassis** | | | **5,648g** | |

### 1.2 Subsystem 2: Drivetrain

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| Chihai CHR-GM37-520 gearmotors | 6 | 185g | 1,110g | EA-02 spec, datasheet |
| Cytron MDD10A motor driver modules | 3 | 55g | 165g | Dual H-bridge per module |
| MG996R steering servos | 4 | 55g | 220g | Datasheet |
| Steering linkage brackets (3D printed) | 4 | 25g | 100g | PETG |
| Wheel encoders (hall effect) | 6 | 5g | 30g | Built into Chihai motors |
| Motor mounting hardware | 6 | 10g | 60g | Bolts, spacers |
| **Subtotal: Drivetrain** | | | **1,685g** | |

### 1.3 Subsystem 3: Power

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| 6S LiPo 10Ah battery pack | 2 | 850g | 1,700g | Typical 6S 10Ah ~800-900g |
| 6S BMS board | 1 | 50g | 50g | PCB + heatsink |
| Buck converter 22V→12V | 1 | 30g | 30g | Small module |
| Buck converter 22V→5V | 1 | 25g | 25g | Small module |
| BEC 22V→6V | 1 | 20g | 20g | Linear regulator |
| Power distribution board | 1 | 40g | 40g | Custom PCB or terminal block |
| Main fuse holder + fuses | 4 | 15g | 60g | Per rail |
| XT90 connectors + wiring | lot | — | 200g | 12-14 AWG silicone wire |
| E-stop button + wiring | 1 | 30g | 30g | Panel mount mushroom button |
| **Subtotal: Power (excl. solar)** | | | **2,155g** | |

### 1.4 Solar Panel Array

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| 25W folding solar panels | 4 | 400g | 1,600g | ~25W monocrystalline, foldable |
| MPPT charge controller | 1 | 80g | 80g | Small module (e.g., CN3791-based) |
| Hinge mechanisms + locks | 4 | 40g | 160g | Spring hinge + detent |
| Panel frame (3D printed) | 4 | 50g | 200g | PETG brackets |
| **Subtotal: Solar** | | | **2,040g** | |

### 1.5 Subsystem 4: Compute & Networking

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| Jetson Orin Nano 8GB (dev kit) | 1 | 280g | 280g | With carrier board + heatsink |
| ESP32-S3 DevKit | 1 | 10g | 10g | Small PCB |
| microSD card (128GB) | 1 | 2g | 2g | — |
| USB 4G dongle | 1 | 30g | 30g | Standard USB modem |
| WiFi antenna (external) | 1 | 15g | 15g | SMA pigtail + antenna |
| 4G antenna (external) | 1 | 15g | 15g | If separate from dongle |
| USB hub | 1 | 30g | 30g | For camera connections |
| **Subtotal: Compute** | | | **382g** | |

### 1.6 Subsystem 5: Vision & Sensors

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| Wide-angle USB cameras (body) | 4 | 15g | 60g | Small USB camera modules |
| 30x zoom USB camera (mast) | 1 | 80g | 80g | Larger module with optics |
| OAK-D Lite depth camera | 1 | 61g | 61g | Luxonis spec |
| IR camera module | 1 | 20g | 20g | NoIR camera |
| IR LED array (850nm) | 4 | 5g | 20g | High-power IR LEDs |
| RPLidar A1 | 1 | 170g | 170g | Slamtec spec |
| GPS module (u-blox NEO-M8N) | 1 | 16g | 16g | With ceramic antenna |
| IMU (BNO055) | 1 | 3g | 3g | Small breakout board |
| Ultrasonic sensors (HC-SR04) | 6 | 9g | 54g | Datasheet |
| Current sensors (INA219) | 4 | 3g | 12g | Small breakout |
| Temperature sensors (DS18B20) | 3 | 2g | 6g | TO-92 package |
| Camera mounts (3D printed) | 7 | 10g | 70g | Custom brackets |
| **Subtotal: Sensors** | | | **572g** | |

### 1.7 Subsystem 6: Robotic Arms & Mast

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| Camera mast (3D printed, telescoping) | 1 | 200g | 200g | 600mm extended, PETG |
| Mast pan servo (MG996R) | 1 | 55g | 55g | — |
| Mast tilt servo (MG996R) | 1 | 55g | 55g | — |
| Slip ring (12-wire) | 1 | 30g | 30g | For continuous 360° rotation |
| Mast hinge + lock mechanism | 1 | 50g | 50g | Spring + solenoid |
| Arm segments (3D printed, 2 arms) | 8 | 40g | 320g | PETG, 4 segments per arm |
| Arm servos (MG996R) | 8 | 55g | 440g | 4 per arm |
| Gripper mechanism (3D printed) | 2 | 30g | 60g | Servo-driven |
| Arm mounting brackets | 2 | 25g | 50g | PETG, bolted to body |
| **Subtotal: Arms & Mast** | | | **1,260g** | |

### 1.8 Subsystem 7: Accessories

| Component | Qty | Unit Weight | Total Weight | Source/Basis |
|-----------|-----|-------------|--------------|-------------|
| Peltier cooler (TEC1-12706) | 1 | 22g | 22g | Datasheet |
| Fridge heatsink + fan | 1 | 100g | 100g | Aluminium heatsink |
| Fridge insulation box (3D printed) | 1 | 150g | 150g | PETG + foam lining |
| Fridge lid + hinge | 1 | 40g | 40g | PETG |
| Qi wireless charger module | 1 | 30g | 30g | 15W module |
| USB-C PD trigger board | 1 | 10g | 10g | Small PCB |
| USB-A port | 1 | 5g | 5g | Panel mount |
| WS2812B LED strips (2m) | 2m | 30g/m | 60g | Standard density |
| High-power LEDs (headlight, tail, indicators) | 10 | 3g | 30g | With heatsinks |
| Speakers (3W) | 2 | 30g | 60g | Full-range drivers |
| MAX98357A amplifier | 1 | 5g | 5g | Small breakout |
| MEMS microphones (SPH0645) | 2 | 1g | 2g | Tiny I2S mics |
| BME280 weather sensor | 1 | 1g | 1g | — |
| Anemometer (cup type) | 1 | 50g | 50g | Small hobby unit |
| Rain sensor (YL-83) | 1 | 5g | 5g | — |
| UV sensor (VEML6075) | 1 | 1g | 1g | — |
| Light sensor (BH1750) | 1 | 1g | 1g | — |
| Dashboard LCD (3.5" IPS) | 1 | 50g | 50g | SPI display |
| Dashboard housing (3D printed) | 1 | 30g | 30g | PETG |
| **Subtotal: Accessories** | | | **652g** | |

### 1.9 Miscellaneous

| Component | Weight | Notes |
|-----------|--------|-------|
| Internal wiring harness | 300g | All cables, connectors, heatshrink |
| Cable management (3D printed clips) | 50g | Various clips and guides |
| Top deck surface (acrylic sheet, optional) | 500g | 3mm clear acrylic, 1100×650mm |
| Contingency (10%) | ~1,500g | Unforeseen additions |
| **Subtotal: Misc** | **2,350g** | |

---

## 2. Phase 2 Total Weight Summary

| Subsystem | Weight (g) | Percentage |
|-----------|-----------|------------|
| Chassis & Suspension | 5,648 | 33.7% |
| Drivetrain | 1,685 | 10.1% |
| Power (batteries + BMS) | 2,155 | 12.9% |
| Solar Panels | 2,040 | 12.2% |
| Compute & Networking | 382 | 2.3% |
| Vision & Sensors | 572 | 3.4% |
| Arms & Mast | 1,260 | 7.5% |
| Accessories | 652 | 3.9% |
| Miscellaneous + Contingency | 2,350 | 14.0% |
| **TOTAL** | **16,744g** | **100%** |

### **Phase 2 estimated weight: ~16.7 kg**

This is within our design target of 15-20 kg for the 3D printed version, and well under the 25-35 kg budget for Phase 3 (metal), leaving headroom for the heavier metal components.

---

## 3. Phase 3 Weight Estimate (Metal)

Replacing 3D printed structural parts with aluminium:

| Change | Weight Difference |
|--------|------------------|
| Body panels: PETG → 1.5mm aluminium sheet | +2,500g (alu is heavier than printed panels) |
| Rocker/bogie arms: 2020 extrusion → alu tube | +200g |
| Wheel hubs: PETG → machined aluminium | +600g |
| Remove 3D printed connectors (now welded/bolted alu) | -600g |
| Weatherproofing gaskets + seals | +300g |
| Acrylic top → tempered glass (if chosen) | +1,000g |
| Heavier fasteners (M5 → M6) | +100g |
| **Net change** | **+4,100g** |

### **Phase 3 estimated weight: ~20.8 kg**

Still under the 25 kg lower target, leaving capacity for payload (drinks in fridge, phone on charger, etc.).

---

## 4. Phase 1 Weight Estimate (0.4 Scale)

At 0.4 scale with simplified electronics:

| Component | Weight |
|-----------|--------|
| 3D printed chassis (PLA, scaled) | 400g |
| N20 micro gearmotors (6x) | 120g |
| SG90 micro servos (4x) | 36g |
| ESP32-S3 DevKit | 10g |
| Motor drivers (2x L298N) | 90g |
| 2S LiPo 2200mAh | 130g |
| Wiring + fasteners | 100g |
| Wheels (6x, 80mm dia) | 180g |
| **TOTAL Phase 1** | **~1,066g** |

Phase 1 target: ~1 kg. N20 motors are rated for 0.5 kg·cm which is sufficient for this weight.

---

## 5. Centre of Gravity Analysis

### 5.1 Phase 2 CoG Estimation

Using coordinate system: origin at ground level, centre of rover footprint.

| Subsystem | Weight (kg) | X (mm) | Y (mm) | Z (mm) |
|-----------|------------|--------|--------|--------|
| Chassis & Suspension | 5.65 | 0 | 0 | 200 |
| Drivetrain (wheels) | 1.69 | 0 | 0 | 100 |
| Batteries (centre-low) | 2.16 | 0 | 0 | 180 |
| Solar (top deck) | 2.04 | 0 | 0 | 380 |
| Compute (electronics bay) | 0.38 | 0 | 50 | 220 |
| Sensors (distributed) | 0.57 | 0 | 100 | 250 |
| Arms & Mast (top, slight front) | 1.26 | 0 | 150 | 350 |
| Accessories (centre) | 0.65 | 0 | 0 | 250 |
| Misc | 2.35 | 0 | 0 | 250 |

**Weighted CoG height**:
```
Z_cog = Σ(mi × zi) / Σ(mi)
Z_cog = (5.65×200 + 1.69×100 + 2.16×180 + 2.04×380 + 0.38×220
         + 0.57×250 + 1.26×350 + 0.65×250 + 2.35×250) / 16.75
Z_cog = (1130 + 169 + 389 + 775 + 84 + 143 + 441 + 163 + 588) / 16.75
Z_cog = 3,882 / 16.75
Z_cog = 232mm above ground
```

**Result: Centre of gravity at ~232mm above ground level.**

This is lower than our estimated 300mm in the stability analysis (EA-01), meaning the rover is MORE stable than calculated — tilt limit increases from 49° to approximately:

```
θ_max = arctan(350 / 232) = arctan(1.51) = 56.5°
```

Excellent stability margin.

### 5.2 CoG with Mast Extended

When the mast is extended (600mm above deck = ~880mm above ground), the mast + cameras add ~0.5 kg at 880mm height:

```
Z_cog_mast = (16.75 × 232 + 0.5 × 880) / (16.75 + 0.5)
Z_cog_mast = (3,886 + 440) / 17.25
Z_cog_mast = 4,326 / 17.25
Z_cog_mast = 251mm
```

Mast extension raises CoG by only 19mm (232 → 251mm) because the mast is light relative to the total weight. Stability remains excellent.

### 5.3 CoG with Fridge Loaded

A full fridge (4-6 cans = ~2 kg extra) at ~300mm height:

```
Z_cog_loaded = (16.75 × 232 + 2.0 × 300) / (16.75 + 2.0)
Z_cog_loaded = (3,886 + 600) / 18.75
Z_cog_loaded = 4,486 / 18.75
Z_cog_loaded = 239mm
```

Barely changes — the heavy batteries and chassis keep the CoG low.

---

## 6. Weight Impact on Drivetrain

These weight figures feed directly into EA-02 (Drivetrain Analysis):

| Scenario | Total Weight | Per-Wheel Load (6 wheels) | Notes |
|----------|-------------|--------------------------|-------|
| Phase 1 (empty) | 1.1 kg | 0.18 kg | Very light |
| Phase 2 (empty) | 16.7 kg | 2.79 kg | Design target |
| Phase 2 (loaded, fridge full) | 18.7 kg | 3.12 kg | Realistic operating weight |
| Phase 3 (empty) | 20.8 kg | 3.47 kg | Metal version |
| Phase 3 (loaded) | 22.8 kg | 3.80 kg | Metal + full fridge |
| Phase 3 (max, loaded + person sitting) | — | — | NOT designed for sitting — 80+ kg would exceed motor torque |

### Critical Weight for Motor Sizing

**Use Phase 3 loaded weight (22.8 kg) with 1.5× safety factor = 34.2 kg** for motor torque calculations. This ensures motors are never under-sized even in worst case.

---

## 7. Summary

| Phase | Empty Weight | Loaded Weight | CoG Height | Tilt Limit |
|-------|-------------|---------------|------------|------------|
| Phase 1 | 1.1 kg | 1.1 kg | ~80mm | >60° |
| Phase 2 | 16.7 kg | 18.7 kg | 232mm | 56.5° |
| Phase 3 | 20.8 kg | 22.8 kg | ~245mm | ~55° |

All phases are well within stability limits and below the weight targets set in the design document.

---

*Document EA-05 v1.0 — 2026-03-15*
