# Engineering Analysis 14: Weatherproofing & Environmental Protection

**Document**: EA-14
**Date**: 2026-03-15
**Purpose**: Define the weatherproofing strategy for each build phase, specify IP ratings, material protection, and environmental operating limits.
**Depends on**: EA-08 (Phase 1 Spec), EA-11 (3D Printing)

---

## 1. Environmental Requirements

### 1.1 Operating Conditions (Derby, UK)

| Parameter | Range | Design Target |
|-----------|-------|---------------|
| Temperature | -5°C to 35°C (UK extremes) | 0°C to 30°C operating |
| Humidity | 40-100% RH | Expect rain, dew, fog |
| Rainfall | ~700mm/year average | Must survive light rain |
| UV index | 1-7 (UK peak summer) | Sustained outdoor exposure |
| Wind | Up to 60 km/h gusts | Stability, not waterproofing concern |
| Terrain splash | Wet grass, puddles, mud | Undercarriage spray |
| Storage | Garden shed or indoors | Not permanently outdoor |

### 1.2 IP Rating Targets

| Phase | Target IP | Meaning | Notes |
|-------|-----------|---------|-------|
| Phase 1 (prototype) | IP20 | Protected from fingers, not water | Indoor/fair weather only |
| Phase 2 (3D printed) | IP44 | Splash-proof from all directions | Light rain, wet grass OK |
| Phase 3 (metal) | IP54 | Dust-protected + splash-proof | All-weather capable |

---

## 2. Phase 1 Protection (IP20 — Minimal)

Phase 1 is a prototype for indoor testing and fair-weather outdoor validation.

| Component | Protection | Method |
|-----------|-----------|--------|
| ESP32-S3 | None | Open breadboard mount |
| L298N drivers | None | Open mount |
| Battery | None | Velcro tray |
| Wiring | None | Exposed jumper wires |
| Motors | Inherent | N20 motors have no openings |
| Servos | Inherent | SG90 has basic splash resistance |

**Operating rule**: Do not operate Phase 1 in rain or on wet grass. Bring indoors after testing.

---

## 3. Phase 2 Protection (IP44 — Splash-Proof)

### 3.1 Zoning Strategy

Divide the rover into protection zones:

```
Top View — Protection Zones:

┌─────────────────────────────────────────┐
│              ZONE A: DRY BAY            │
│  (Jetson, ESP32, PCA9685, converters)   │
│  Sealed enclosure, IP54 minimum         │
├─────────────────────────────────────────┤
│           ZONE B: SPLASH ZONE           │
│  (Motors, servos, wiring harness)       │
│  Splash-resistant, drain holes          │
├─────────────────────────────────────────┤
│          ZONE C: WET ZONE               │
│  (Wheels, suspension, undercarriage)    │
│  Fully exposed, must tolerate water     │
└─────────────────────────────────────────┘
```

### 3.2 Zone A: Dry Electronics Bay

The electronics bay houses all sensitive components and must be the most protected area.

| Feature | Specification |
|---------|---------------|
| Construction | 3D printed PETG enclosure, 3mm walls |
| Seal method | Silicone gasket (2mm cord, compressed in groove) |
| Cable entry | IP44 cable glands (PG7 for signal, PG9 for power) |
| Ventilation | Labyrinth vent (allows airflow, blocks water spray) |
| Drain | 3mm drain hole at lowest point (if condensation forms) |
| Access | Removable lid with 8× M3 bolts (quick-release clips for Phase 3) |

**Components inside Zone A**:
- Jetson Orin Nano (with heatsink fan)
- ESP32-S3 DevKit
- PCA9685 PWM driver
- Buck converters (22V→12V, 22V→5V)
- BEC (22V→6V)
- Power distribution board
- USB hub
- microSD cards
- All signal wiring connections

**Conformal coating**: Apply MG Chemicals 422B silicone conformal coating spray to all PCBs. This adds a moisture barrier even if water enters the bay.

### 3.3 Zone B: Motor & Servo Area

Motors and servos are in the suspension arms and body extremities — they get splashed.

| Component | Protection Method |
|-----------|------------------|
| Chihai 37mm motors | Grease shaft bearings, seal motor body with RTV silicone around shaft exit |
| Cytron MDD10A drivers | Mount inside Zone A (they're small PCBs), run motor wires through cable glands |
| MG996R servos | Apply thin bead of silicone around case seam, grease output shaft |
| Encoder PCBs | Conformal coating + heat-shrink over solder joints |
| Wiring | Silicone-insulated wire (rated IP67), heat-shrink all connections |

### 3.4 Zone C: Undercarriage

Wheels, suspension arms, bearings, and the rover belly are fully exposed.

| Component | Protection Method |
|-----------|------------------|
| 608ZZ bearings | Already sealed (ZZ = metal shields), grease periodically |
| 3D printed arms | PETG/ASA is inherently water-resistant |
| Wheel hubs | PETG is waterproof, D-shaft bore sealed with grease |
| Fasteners | Stainless steel or zinc-plated (Phase 2), stainless only (Phase 3) |
| Aluminium extrusion | Naturally corrosion-resistant (oxide layer) |

### 3.5 Battery Compartment

Batteries need special attention — LiPo is dangerous when wet.

| Feature | Specification |
|---------|---------------|
| Location | Centre of body, low (good CoG) |
| Enclosure | Separate sealed compartment within Zone A |
| Seal | Silicone gasket + latched lid |
| Vent | Small silicone check valve (allows pressure equalisation, blocks water) |
| Padding | Foam liner (shock absorption + insulation) |
| Fire safety | LiPo fire bag material lining (silicone-coated fibreglass) |
| Connector | XT90 through panel-mount waterproof connector |

### 3.6 Cable Gland Schedule

| Location | Size | Cable(s) | Qty |
|----------|------|----------|-----|
| Electronics bay → left motors | PG9 | 3× motor pairs (12/14 AWG) | 1 |
| Electronics bay → right motors | PG9 | 3× motor pairs | 1 |
| Electronics bay → front servos | PG7 | 2× servo signal + power | 1 |
| Electronics bay → rear servos | PG7 | 2× servo signal + power | 1 |
| Electronics bay → mast | PG7 | Camera USB + servo signal | 1 |
| Electronics bay → each arm | PG7 | 4× servo signal + power | 2 |
| Electronics bay → sensors | PG7 | Ultrasonic, temp, weather | 2 |
| Electronics bay → top deck | PG7 | Solar input, LEDs | 1 |
| Battery bay → electronics bay | PG9 | XT90 power cable | 1 |
| **Total cable glands** | | | **11** |

---

## 4. Thermal Management

### 4.1 Heat Sources

| Component | Power Dissipation | Max Temp | Cooling |
|-----------|------------------|----------|---------|
| Jetson Orin Nano | 7-15W | 85°C (throttles) | Included heatsink + fan |
| Motor drivers (3×) | ~2W each idle, ~10W loaded | 80°C (derate) | Natural convection in Zone B |
| Buck converters | ~3W total | 85°C | Small heatsink, in Zone A |
| Motors (6×) | ~5W each driving | 120°C (insulation limit) | Open air in Zone C |
| Peltier cooler | 60W (when active) | Hot side 80°C | Dedicated aluminium heatsink + fan |

### 4.2 Summer Overheating (Worst Case)

In UK summer (30°C ambient), direct sunlight heats the body to ~50°C. Electronics bay air temperature could reach 55°C.

**Mitigations**:
1. **Solar panel shade**: When deployed, solar panels shade the top deck
2. **Ventilation**: Labyrinth vents on two sides of electronics bay (creates cross-flow)
3. **Light colour**: Print body panels in light grey or white (reflects more solar heat)
4. **Software thermal management**: Jetson monitors GPU temp, throttles at 80°C
5. **Avoid operation**: Software should warn user when ambient > 35°C

### 4.3 Winter Cold (Worst Case)

LiPo batteries lose capacity below 10°C and can be damaged if charged below 0°C.

**Mitigations**:
1. **Battery temperature sensor**: DS18B20 inside battery compartment
2. **Low-temp lockout**: Don't charge battery if temp < 5°C
3. **Pre-heat**: Run motors briefly to warm battery through internal resistance
4. **Storage**: Bring battery indoors in winter

---

## 5. Phase 3 Enhancements (IP54)

### 5.1 Metal Body Benefits

| Feature | Phase 2 (PETG) | Phase 3 (Aluminium) |
|---------|----------------|---------------------|
| Panel sealing | Silicone gasket in groove | Machined gasket groove, proper compression |
| Cable entry | PG cable glands | IP68 industrial cable glands |
| Fasteners | Zinc-plated steel | Stainless A4 (marine grade) |
| Panel joints | M3 bolts + inserts | Rivets or welded seams |
| Surface finish | UV clear coat spray | Powder coat or anodise |
| Impact resistance | 3D print may crack | Aluminium dents but doesn't crack |

### 5.2 Additional Phase 3 Sealing

- **Laser-cut silicone gaskets**: Custom gaskets cut to match each panel
- **O-ring sealed access hatches**: For battery and electronics bay
- **Waterproof connectors**: Amphenol or TE IP67 circular connectors for motor/sensor cables
- **Breather valve**: Gore-Tex membrane vent (allows air, blocks water)
- **Drain channels**: Machined into body floor, direct water away from electronics

---

## 6. Corrosion Prevention

### 6.1 Material Compatibility

Avoid galvanic corrosion when different metals are in contact:

| Metal Pair | Risk | Mitigation |
|-----------|------|------------|
| Aluminium + stainless steel | Moderate | Nylon washer between surfaces |
| Aluminium + zinc-plated steel | Low | Acceptable for Phase 2 |
| Aluminium + copper (wire) | Moderate | Tin-plated terminals, no bare copper on aluminium |
| Steel + steel | Rust | Use stainless or zinc-plated only |

### 6.2 Anti-Corrosion Treatments

| Material | Treatment | Reapply |
|----------|-----------|---------|
| Aluminium extrusion | None (natural oxide) | N/A |
| Steel fasteners | Zinc plating (Phase 2) / stainless (Phase 3) | N/A |
| Copper contacts (dock) | Tin plating or nickel plating | Check annually |
| 3D printed parts | N/A (plastic doesn't corrode) | UV coat every 2 years |
| Bearing surfaces | Light machine oil or white lithium grease | Every 6 months |

---

## 7. Operating Procedures

### 7.1 Pre-Operation Checklist

Before each outdoor session:
1. Check weather forecast — do not operate in heavy rain (Phase 2)
2. Inspect cable glands — ensure all are finger-tight
3. Check battery voltage — must be above warning threshold
4. Verify electronics bay lid is sealed
5. Check for condensation inside electronics bay (clear morning dew)

### 7.2 Post-Operation

After outdoor use, especially in wet conditions:
1. Wipe down body with dry cloth
2. Inspect electronics bay for moisture ingress
3. Open electronics bay if humidity sensor reads >80% inside
4. Dry wheels and suspension if muddy
5. Charge battery (if above 5°C)
6. Store indoors or in dry shed

### 7.3 Seasonal Maintenance

| Season | Task |
|--------|------|
| Spring | Replace silicone gaskets if hardened, grease bearings, check UV coating |
| Summer | Monitor thermal performance, clean solar panels, check fan filters |
| Autumn | Thorough clean before wet season, re-grease all bearings, inspect cables |
| Winter | Remove battery for indoor storage, full inspection, reprint any degraded parts |

---

*Document EA-14 v1.0 — 2026-03-15*
