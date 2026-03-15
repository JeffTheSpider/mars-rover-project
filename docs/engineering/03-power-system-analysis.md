# Engineering Analysis 03: Battery & Power System Design

**Document**: EA-03
**Date**: 2026-03-15
**Purpose**: Select battery chemistry, design the power distribution system, specify solar charging, and calculate runtime estimates with efficiency losses.
**Depends on**: EA-02 (Drivetrain — power consumption), EA-05 (Weight Budget)

---

## 1. Power Budget (Refined from EA-02)

| Consumer | Voltage | Peak (A) | Typical (A) | Typical (W) |
|----------|---------|----------|-------------|-------------|
| 6× Drive motors | 12V | 24.0 | 1.2 | 14.4 |
| 4× Steering servos | 6V | 8.0 | 0.2 | 1.2 |
| Jetson Orin Nano | 5V | 3.0 | 2.0 | 10.0 |
| ESP32-S3 | 3.3V | 0.5 | 0.15 | 0.5 |
| 6× Cameras | 5V | 3.0 | 1.5 | 7.5 |
| RPLidar A1 | 5V | 1.0 | 0.7 | 3.5 |
| OAK-D Lite depth | 5V | 1.0 | 0.8 | 4.0 |
| Mini fridge (Peltier) | 12V | 5.0 | 3.0 | 36.0 |
| LED underglow + lights | 5V | 3.0 | 1.0 | 5.0 |
| Speaker/amp | 12V | 2.0 | 0.3 | 3.6 |
| Qi charger | 5V | 2.0 | 1.0 | 5.0 |
| Dashboard display | 5V | 0.3 | 0.2 | 1.0 |
| GPS + IMU + sensors | 3.3V | 0.2 | 0.1 | 0.3 |
| 4G modem | 5V | 0.5 | 0.3 | 1.5 |
| Arm servos (8×) | 6V | 16.0 | 1.0 | 6.0 |
| Mast servos (2×) | 6V | 4.0 | 0.3 | 1.8 |
| Weather station | 3.3V | 0.1 | 0.05 | 0.2 |

### Summary by Power Rail

| Rail | Peak (A) | Typical (A) | Typical (W) |
|------|----------|-------------|-------------|
| 12V | 31.0 | 4.5 | 54.0 |
| 6V (servos) | 28.0 | 1.5 | 9.0 |
| 5V | 13.8 | 6.7 | 33.5 |
| 3.3V | 0.8 | 0.3 | 1.0 |
| **Total at battery** | **~50A** | **~13A** | **97.5W** |

Note: The battery voltage (22.2V nominal) is higher than consumer voltages, so battery current is lower. Accounting for converter efficiency (~85%):

```
Battery current (typical):
  I_bat = P_total / (V_bat × η)
  I_bat = 97.5 / (22.2 × 0.85)
  I_bat = 5.17A

Battery current (peak, motors + fridge + arms):
  P_peak ≈ 300W (stall scenario)
  I_bat_peak = 300 / (22.2 × 0.85) = 15.9A
```

---

## 2. Battery Chemistry Comparison

| Parameter | LiPo | Li-ion 18650 | LiFePO4 |
|-----------|------|-------------|---------|
| **Nominal cell voltage** | 3.7V | 3.6-3.7V | 3.2V |
| **Energy density** | 150-200 Wh/kg | 150-250 Wh/kg | 90-120 Wh/kg |
| **Cycle life** | 300-500 cycles | 500-1000 cycles | 2000-5000 cycles |
| **Max discharge rate** | 10-50C | 1-5C | 1-5C |
| **Safety** | Moderate (fire risk if punctured) | Moderate | Excellent (very stable) |
| **Cost per Wh** | $0.15-0.25 | $0.10-0.20 | $0.20-0.40 |
| **Weight for 444Wh** | ~2.2-3.0 kg | ~1.8-3.0 kg | ~3.7-4.9 kg |
| **6S equivalent** | 6S (22.2V) | 6S (22.2V) | 7S (22.4V) |
| **Form factor** | Flat pouch | Cylindrical (need pack) | Prismatic or cylindrical |
| **Availability** | Excellent (RC hobby) | Excellent | Good (growing market) |

### Analysis

**LiPo (Recommended for Phase 2)**:
- Highest energy density = lightest pack
- High discharge rates easily handle our 16A peak
- Widely available in 6S configuration from RC hobby suppliers
- Lower cost per Wh than LiFePO4
- Drawback: shorter cycle life (300-500 vs 2000+), requires careful charging and storage

**LiFePO4 (Consider for Phase 3)**:
- Much longer cycle life — better for a rover that will be charged daily
- Safer chemistry — important for outdoor use
- But 40% heavier for same capacity
- 7S needed for similar voltage to 6S LiPo (22.4V vs 22.2V)

**Li-ion 18650 (Not recommended)**:
- Would need to build a custom pack (spot welder, BMS, etc.)
- Lower discharge rates than LiPo
- Best energy density but requires more engineering effort
- Risk of cell inconsistency in DIY packs

### Decision

**Phase 2: 6S LiPo** — lightest, cheapest, readily available in hobby shops, adequate cycle life for prototyping.

**Phase 3: Consider upgrading to LiFePO4** — if the rover will be used daily, the 5-10× longer cycle life justifies the weight penalty.

---

## 3. Battery Pack Design

### 3.1 Capacity Selection

From our power budget:
- Typical driving consumption: ~97.5W
- Target driving runtime: 2+ hours
- Required energy: 97.5W × 2h = 195 Wh

Adding 20% margin for ageing and incomplete discharge:
- Required capacity: 195 × 1.2 = 234 Wh

At 22.2V nominal (6S):
- Required capacity: 234 / 22.2 = **10.5 Ah**

**Selected: 2× 6S 10Ah LiPo packs in parallel = 20Ah total (444 Wh)**

This gives approximately 2× the minimum required capacity, providing:
- 4+ hours driving runtime (with typical mix of driving and stationary)
- Redundancy (can operate on one pack if the other fails)
- Swappable packs (can carry spares)

### 3.2 Discharge Rate Verification

```
Peak current: 15.9A
C rating needed: I_peak / Capacity = 15.9 / 20 = 0.8C

Even a conservative 10C LiPo can deliver: 10 × 20 = 200A
Our peak draw of 15.9A is trivial for any hobby LiPo.

Standard 12C packs (commonly available) deliver: 12 × 10 = 120A per pack.
```

**Conclusion**: Even cheap, low-C-rating 6S packs (10-12C) far exceed our current requirements. No need for expensive high-discharge racing packs.

### 3.3 Specific Product Recommendations

| Product | Capacity | C-Rating | Weight | Dimensions (approx.) | Price (UK) |
|---------|----------|----------|--------|----------------------|------------|
| Turnigy High Capacity 6S 10000mAh 12C | 10Ah | 12C | ~850g | 185×70×58mm | ~$50 |
| Zeee 6S 10000mAh 120C | 10Ah | 120C | ~950g | 168×69×54mm | ~$65 |
| HOOVO 6S 10000mAh 120C | 10Ah | 120C | ~920g | 170×70×52mm | ~$55 |

**Recommended: Turnigy High Capacity 6S 10000mAh 12C** — cheapest, lightest, 12C is more than enough. Two packs = ~$100, ~1.7 kg total.

### 3.4 Battery Mounting

```
Pack dimensions: ~185×70×58mm each
Two packs side by side: ~185×140×58mm
Location: Centre-bottom of body (lowest point for CoG)
Mounting: Velcro straps + 3D printed cradle with XT90 quick-disconnect
Access: Bottom panel removes for battery swaps
```

---

## 4. Battery Management System (BMS)

### 4.1 Requirements

| Parameter | Requirement |
|-----------|-------------|
| Cell count | 6S (22.2V nominal, 25.2V full) |
| Max charge current | 10A (1C charge rate) |
| Max discharge current | 30A continuous (15.9A peak × 2 safety) |
| Balance current | ≥100mA per cell |
| Over-charge protection | 4.25V per cell |
| Over-discharge protection | 3.0V per cell (configurable to 3.2V) |
| Over-current protection | 40A cutoff |
| Temperature monitoring | NTC thermistor input |
| Short circuit protection | Required |

### 4.2 Recommendation

**Standard 6S 30A BMS board** — available from AliExpress/Amazon for ~$10-15.

One BMS per battery pack, so 2 total. Each BMS handles:
- Balance charging (equalises cells during charge)
- Over-discharge cutoff (protects cells from damage)
- Over-current protection (prevents fires)
- Temperature sensing (optional NTC input)

**Note**: For parallel packs, each pack has its own BMS. They connect in parallel after the BMS output.

---

## 5. Power Distribution

### 5.1 Converter Selection

| Rail | Converter Type | Input | Output | Current | Efficiency | Product Example | Price |
|------|---------------|-------|--------|---------|------------|-----------------|-------|
| 12V | Buck (step-down) | 22.2V | 12V | 10A continuous | ~90% | LM2596-based module or XL4016 | ~$5 |
| 6V | BEC (UBEC) | 22.2V | 6V | 5A continuous | ~85% | Hobbywing 5A UBEC | ~$8 |
| 5V | Buck (step-down) | 22.2V | 5V | 8A continuous | ~88% | XL4015 5A or LM2596 adj | ~$4 |
| 3.3V | LDO (from 5V) | 5V | 3.3V | 0.5A | ~66% (LDO) | AMS1117-3.3V | ~$0.50 |

### 5.2 Efficiency Analysis

```
Total power at loads: 97.5W (typical)

Power at battery (accounting for conversion losses):
  12V rail: 54W / 0.90 = 60.0W from battery
  6V rail:  9W / 0.85 = 10.6W from battery
  5V rail:  33.5W / 0.88 = 38.1W from battery
  3.3V rail: 1W / (0.88 × 0.66) = 1.7W from battery

Total from battery: 110.4W
Overall system efficiency: 97.5 / 110.4 = 88.3%

Battery current: 110.4 / 22.2 = 4.97A
```

### 5.3 Runtime Calculations (Revised with Efficiency)

| Mode | Load Power | Battery Power | Battery Current | Runtime (444Wh) |
|------|-----------|---------------|-----------------|-----------------|
| Driving (all systems) | 97.5W | 110.4W | 5.0A | **4.0 hours** |
| Driving (no fridge) | 61.5W | 69.6W | 3.1A | **6.4 hours** |
| Stationary (coffee table + fridge) | 55W | 62.3W | 2.8A | **7.1 hours** |
| Idle (sensors only) | 12W | 13.6W | 0.6A | **32.6 hours** |

**Key insight**: Removing the fridge (36W) nearly doubles driving runtime. The fridge should be software-togglable and default to OFF while driving.

### 5.4 Wire Gauge Selection

```
Using American Wire Gauge (AWG) standards:
  - Rule of thumb: 10A per mm² of copper cross-section
  - Voltage drop: keep <3% on each run

Battery to distribution board (30A peak, ~300mm run):
  V_drop = I × R = 30 × (ρ × L / A)
  For 3% drop on 22.2V: max resistance = 0.022Ω
  Required: 10 AWG (5.26mm²) — 3.28Ω/km → 0.001Ω for 300mm ✓

12V rail to motors (10A peak, ~500mm average run):
  For 3% drop on 12V: max resistance = 0.036Ω
  Required: 14 AWG (2.08mm²) — 8.29Ω/km → 0.004Ω for 500mm ✓

5V rail to Jetson/cameras (~8A, ~300mm):
  For 3% drop on 5V: max resistance = 0.019Ω
  Required: 16 AWG (1.31mm²) — 13.2Ω/km → 0.004Ω for 300mm ✓

6V servo rail (~5A, ~400mm):
  14 AWG sufficient

Signal/low power:
  22-24 AWG (standard hookup wire)
```

| Run | Max Current | Wire Gauge | Notes |
|-----|-----------|------------|-------|
| Battery → PDB | 30A | 10 AWG silicone | XT90 connectors |
| PDB → 12V buck | 10A | 14 AWG | Fused |
| PDB → 5V buck | 8A | 16 AWG | Fused |
| PDB → 6V BEC | 5A | 16 AWG | Fused |
| 12V → Motors | 5A each | 16 AWG | 6 runs |
| 5V → Jetson | 3A | 18 AWG | Short run |
| Signal wires | <0.5A | 22 AWG | Standard |

---

## 6. Solar Panel System

### 6.1 Panel Selection

For our rover, we need panels that:
- Fold flat onto the top deck (1100×650mm available area)
- Provide meaningful charging (≥50W to charge in reasonable time)
- Are lightweight (total solar weight in EA-05: 2,040g budget)
- Survive outdoor use

### 6.2 UK Solar Irradiance

```
UK average solar irradiance:
  Summer peak: ~900-1000 W/m²
  Summer average (6 useful hours): ~500 W/m²
  Winter average (3 useful hours): ~200 W/m²
  Annual average: ~100-120 W/m² (weighted over daylight hours)

Derby (52.9°N) receives approximately:
  Summer: 4.5-5.5 peak sun hours (PSH) per day
  Winter: 0.8-1.5 PSH per day
  Annual average: ~2.8 PSH per day
```

### 6.3 Charging Time Calculations

```
With 100W panel array (4× 25W):
  Actual output = Panel rating × (irradiance / 1000) × MPPT efficiency

Summer:
  Actual output = 100 × (500/1000) × 0.85 = 42.5W average
  Time to charge from empty: 444Wh / 42.5W = 10.4 hours
  Time for 2-hour drive top-up: 110W × 2h / 42.5W = 5.2 hours

Winter:
  Actual output = 100 × (200/1000) × 0.85 = 17W average
  Time to charge from empty: 444Wh / 17W = 26 hours (impractical)
  Time for 1-hour drive top-up: 110W / 17W = 6.5 hours
```

**Conclusion**: Solar panels are a supplementary charging method, not primary. In summer, they can meaningfully extend runtime. In winter, they provide trickle charging only. Mains charging is the primary method.

### 6.4 MPPT Controller

```
Panel voltage (4× 25W in parallel): ~18-20V open circuit, ~17V at max power
Battery voltage: 22.2-25.2V (6S LiPo)

Problem: Panel voltage (17V) is LOWER than battery voltage (22.2V).
A standard buck MPPT won't work — we need a BOOST MPPT controller.

Options:
  1. Wire panels in series-parallel: 2S2P = ~36V, 50W → buck MPPT to 25.2V ✓
  2. Use a boost MPPT controller (less common, more expensive)
  3. Use panels rated at higher voltage (24V panels instead of 12V)

Recommendation: Wire panels 2S2P (two strings of 2 panels in series, strings in parallel)
  - Each string: 2 × 18V = 36V open circuit
  - Two strings in parallel: 36V, ~3A combined
  - Standard buck MPPT charges the 6S LiPo (25.2V max) efficiently
```

**MPPT Controller**: Victron SmartSolar 75/10 (~$60) or cheaper CN3722-based module (~$15).

For budget: **CN3722 solar MPPT module** — charges multi-cell LiPo from solar panels, ~$15.

---

## 7. Charging System Summary

| Method | Input | Charge Current | Charge Time (0→100%) | Cost |
|--------|-------|---------------|---------------------|------|
| Mains (24V charger) | 240V AC → 24V DC | 5-10A | 2-4 hours | ~$20 (charger) |
| Solar (4× 25W, 2S2P) | Sunlight | 1-2A (summer) | 10-26 hours | ~$100 (panels) + $15 (MPPT) |
| Docking station | 24V DC (spring contacts) | 5A | 4 hours | ~$15 (contacts + PSU) |

### Docking Station Design

```
Station base:
  [24V PSU (5A)] → [Spring-loaded copper pads (+/-)]
                         ↕ contact
  [Rover underside copper pads] → [Charge controller input]

Alignment: ArUco marker or IR beacon on station
           Rover uses camera to align, drives onto contacts
           Current sensing confirms connection
```

---

## 8. Safety Design

### 8.1 Protection Layers

| Layer | Component | Protection |
|-------|-----------|------------|
| Cell level | BMS (per pack) | Over-charge (4.25V), over-discharge (3.0V), balance |
| Pack level | BMS (per pack) | Over-current (40A), short circuit, temperature |
| Rail level | Blade fuses | 15A (12V), 10A (5V), 8A (6V) |
| System level | E-stop button | Physical disconnect (contactor or high-current relay) |
| Software | ESP32 monitoring | Voltage/current/temp logging, low-battery return-to-home |

### 8.2 E-Stop Implementation

```
Physical button (panel-mount mushroom, normally closed):
  Battery+ → [E-Stop NC] → [Main contactor/relay] → Power distribution

When pressed:
  - NC contact opens → main relay drops out → all power cut
  - Spring-loaded, twist-to-release (prevents accidental engagement)
  - Red, visible, accessible from all sides of rover

Software E-stop (from phone):
  - ESP32 GPIO → relay coil → same main contactor
  - Watchdog: if ESP32 crashes, relay drops out (fail-safe)
```

### 8.3 Low Battery Behaviour

| Battery SOC | Action |
|-------------|--------|
| 30% | Dashboard warning, phone notification |
| 20% | Reduce max speed to 50%, fridge OFF, arms stowed |
| 15% | Alert: "Return to home recommended" |
| 10% | Auto return-to-home initiated (if GPS available) |
| 5% | Stop all motion, enter hibernate (sensors + GPS only) |
| 3% | Complete shutdown (protect cells from over-discharge) |

---

## 9. References

- [6S LiPo Battery Guide 2025 — XRCCars](https://www.xrccars.com/6s-lipo-battery-guide-2025-voltage-capacity-best-models/)
- [LiFePO4 vs LiPo — Grepow](https://www.grepow.com/blog/lifepo4-vs-lipo-what-is-the-difference.html)
- [UK Solar Irradiance Data — Met Office](https://www.metoffice.gov.uk/weather/learn-about/weather/types-of-weather/sunshine/solar-radiation)
- [Turnigy High Capacity 6S 10000mAh — HobbyKing](https://hobbyking.com/en_us/turnigy-high-capacity-10000mah-6s-12c-multi-rotor-lipo-pack-w-xt90.html)
- [Wire Gauge Current Capacity — PowerStream](https://www.powerstream.com/Wire_Size.htm)

---

*Document EA-03 v1.0 — 2026-03-15*
