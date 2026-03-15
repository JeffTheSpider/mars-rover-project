# Engineering Analysis 11: 3D Printing Strategy

**Document**: EA-11
**Date**: 2026-03-15
**Purpose**: Define material selection, print settings, part segmentation, print orientation, heat-set insert specifications, and post-processing for all 3D printed rover components across all build phases.
**Depends on**: EA-01 (Suspension), EA-05 (Weight), EA-08 (Phase 1 Spec)
**See also**: `docs/references/3d-printing-strategy.md` — supplementary research with community project data and additional Ender 3 tips

---

## 1. Material Selection

### 1.1 Material Comparison for Rover Application

| Property | PLA | PETG | ABS | ASA | PA (Nylon) |
|----------|-----|------|-----|-----|------------|
| **Tensile strength** | 60 MPa | 50 MPa | 40 MPa | 45 MPa | 70 MPa |
| **Layer adhesion** | Good | Very good | Moderate | Moderate | Excellent |
| **Impact resistance** | Low (brittle) | High | High | High | Very high |
| **Heat resistance (HDT)** | 52°C | 70°C | 98°C | 98°C | 180°C |
| **UV resistance** | Poor | Moderate | Poor | **Excellent** | Good |
| **Moisture absorption** | Low | Low | Very low | Very low | **High** |
| **Outdoor durability** | 6-12 months | 1-3 years | 6-12 months (UV) | **3-5 years** | 2-4 years |
| **Print difficulty** | Easy | Easy | Moderate (warps) | Moderate (warps) | Hard (hygroscopic) |
| **Enclosure needed** | No | No | Yes | Yes | Yes |
| **Bed adhesion** | Good (60°C) | Good (75°C) | Needs glue (100°C) | Needs glue (100°C) | Needs glue (70°C) |
| **Cost (1kg spool)** | $18-22 | $20-25 | $18-22 | $25-30 | $35-50 |
| **Acetone smoothable** | No | No | **Yes** | **Yes** | No |
| **Food-safe (fridge)** | With coating | **PETG is food-safe** | No | No | No |

### 1.2 Material Recommendations by Phase

| Phase | Primary Material | Rationale |
|-------|-----------------|-----------|
| **Phase 1 (prototype)** | **PETG** | Best balance: strong layer adhesion, good impact resistance, easy to print, survives outdoor testing in UK weather. PLA is acceptable for initial indoor testing but will warp in sun. |
| **Phase 2 (outdoor use)** | **ASA** for structural, **PETG** for body panels | ASA is the best outdoor material: excellent UV resistance, ABS-like properties without the brittleness. PETG for non-structural panels (food-safe for fridge area, easier to print). |
| **Phase 3 (metal)** | **PETG/ASA** for retained plastic parts | Only camera housings, cable clips, and decorative elements remain plastic in Phase 3. |

### 1.3 Why Not PLA?

PLA is unsuitable for the rover because:
1. **Heat deflection at 52°C**: A black rover in UK summer sun can reach 50-60°C internally. PLA will soften and deform.
2. **UV degradation**: PLA becomes brittle after 6-12 months of outdoor UV exposure.
3. **Brittleness**: PLA shatters on impact — a rover tipping over or hitting an obstacle could crack structural parts.
4. **PLA is acceptable only for**: Initial test prints, bearing test pieces, and throwaway prototypes that won't leave the desk.

### 1.4 Ender 3 Compatibility

Charlie's printer is an Ender 3 (220×220×250mm bed). Material compatibility:

| Material | Ender 3 Compatible? | Modifications Needed |
|----------|---------------------|---------------------|
| PLA | Yes, native | None |
| PETG | Yes, native | Blue painter's tape or PEI sheet recommended |
| ABS | Possible but poor | Needs enclosure (cardboard box works) |
| ASA | Possible but poor | Needs enclosure + good ventilation (fumes) |
| Nylon | Difficult | Needs all-metal hotend + enclosure + dry box |

**For Phase 2 ASA**: Build a simple cardboard/foam board enclosure around the Ender 3 to maintain chamber temperature ~40°C. Print near a window or with a fan exhausting fumes — ASA produces styrene vapour (mild, less than ABS but still requires ventilation).

---

## 2. Print Settings by Part Category

### 2.1 Structural Parts (Rocker Arms, Bogie Arms, Motor Mounts)

These parts bear mechanical loads and must resist bending/shear forces.

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PETG (Phase 1) / ASA (Phase 2) | Strength + outdoor durability |
| Layer height | 0.2mm | Good strength, reasonable speed |
| Nozzle | 0.4mm standard | Default, widely available |
| Walls/perimeters | 4 (1.6mm wall thickness) | Primary load path is through walls |
| Top/bottom layers | 5 (1.0mm) | Prevents puncture and adds rigidity |
| Infill | 50% gyroid | High strength-to-weight ratio |
| Print speed | 40-50 mm/s | Slower for better layer adhesion |
| Temperature (PETG) | 235°C nozzle, 75°C bed | Standard PETG |
| Temperature (ASA) | 250°C nozzle, 100°C bed | Requires enclosure |
| Cooling fan | 30-50% (PETG), 0% first layers (ASA) | PETG needs some cooling; ASA needs minimal |
| Retraction | 5mm at 40mm/s (Bowden) | Prevents stringing on PETG |

### 2.2 Body Panels (Cosmetic + Light Structural)

Flat or curved panels that form the rover body shell.

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PETG / ASA | Weather resistance |
| Layer height | 0.2mm | Good surface finish |
| Walls | 3 (1.2mm) | Adequate for panels |
| Top/bottom layers | 4 | Smooth surface |
| Infill | 15-20% gyroid | Panels don't bear heavy loads |
| Print speed | 50-60 mm/s | Faster for large flat parts |
| Notes | Print face-down for best top surface | Bed side = exterior surface |

### 2.3 Wheels

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PETG (hub) | Impact-resistant |
| Layer height | 0.2mm | Smooth tread surface |
| Walls | 3 | Hub is reinforced by spokes |
| Infill | 25% gyroid | Lightweight but rigid |
| Print orientation | Flat (tread face on bed) | Strongest axis is radial |
| Notes | D-shaft bore may need reaming | Print slightly undersized, ream to fit |

### 2.4 Connectors & Brackets (Heat-Set Insert Parts)

Small parts that join extrusions or hold bearings.

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PETG / ASA | Must hold heat-set inserts |
| Layer height | 0.16mm | Better resolution for insert holes |
| Walls | 4-5 | Maximum wall around inserts |
| Infill | 60-80% | Dense for insert retention |
| Print speed | 35-40 mm/s | Precision over speed |
| Top/bottom layers | 5 | Strength |

---

## 3. Heat-Set Insert Specification

### 3.1 Insert Selection

| Parameter | Value |
|-----------|-------|
| Size | M3 × 5.7mm (OD) × 4.6mm (length) |
| Material | Brass, knurled |
| Thread | M3 (0.5mm pitch) |
| Supplier | CNC Kitchen style / AliExpress bulk |
| Cost | ~$0.06 each |
| Pull-out strength (PETG) | 600-900 N (60-90 kg·f) |
| Torque resistance | ~2.5 N·m |

### 3.2 Hole Design for Inserts

| Feature | Dimension | Notes |
|---------|-----------|-------|
| Hole diameter | 4.8mm | Slightly undersized vs insert OD (5.7mm) — plastic flows around knurls |
| Hole depth | 5.5mm | 1mm deeper than insert to allow full seating |
| Wall thickness around hole | ≥2.4mm (3 walls at 0.4mm line width) | Prevents blowout |
| Chamfer at top | 0.5mm × 45° | Guides insert during installation |
| Bottom | Flat (blind hole) | Don't use through-hole unless needed |

### 3.3 Installation Method

| Step | Detail |
|------|--------|
| Tool | Soldering iron with M3 insert tip (or standard conical tip) |
| Temperature | **220°C for PETG**, 230°C for ASA |
| Technique | Place insert on hole, press straight down with iron tip inside insert thread. Let the heat melt the surrounding plastic — do NOT force. Takes 2-3 seconds. |
| Depth | Flush with surface or 0.2mm below |
| Alignment | Press straight — crooked inserts compromise thread engagement |
| Cool time | 10 seconds before handling |
| Quality check | Thread an M3 bolt in/out — should go smooth with no binding |

### 3.4 Insert Orientation vs Print Layers

**Best**: Insert axis perpendicular to print layers (inserted from top or bottom face). The knurls grip into layer lines, maximising pull-out strength.

**Acceptable**: Insert axis parallel to layers (inserted from side). Slightly lower pull-out strength (~70% of perpendicular) because the knurls push layers apart rather than gripping into them.

**Rule**: Where possible, design parts so inserts go in perpendicular to layers. If this conflicts with the best print orientation for strength, prioritise the print orientation and accept slightly lower insert strength (still far exceeds our loads).

---

## 4. Part Segmentation Strategy

### 4.1 Ender 3 Build Volume

| Dimension | Value | Usable (with margins) |
|-----------|-------|----------------------|
| X | 220mm | 210mm |
| Y | 220mm | 210mm |
| Z | 250mm | 240mm |

### 4.2 Phase 1 Segmentation (0.4 Scale)

Body is 440mm × 260mm × 80mm — exceeds the 220mm bed in X direction.

| Part | Full Dimension | Segments | Segment Size | Join Method |
|------|---------------|----------|-------------|-------------|
| Body | 440×260×80 | 2 halves | 220×260×80 each | M3 bolts + heat-set inserts |
| Rocker arm | 180mm long | 1 piece | Fits in 210mm | No segmentation |
| Bogie arm | 120mm long | 1 piece | Fits easily | No segmentation |
| Diff bar | 200mm long | 1 piece + rod | Adapters fit easily | Steel rod core |
| Wheels | 80mm dia | 1 piece each | Fits easily | No segmentation |
| Steering brackets | 35×25×40 | 1 piece each | Small | No segmentation |

**Total segments**: 2 (body halves) + 2 rockers + 2 bogies + 3 diff adapters + 6 wheels + 4 steering + 2 fixed mounts + 1 cover = **22 parts**

### 4.3 Phase 2 Segmentation (Full Scale)

Body is 1100mm × 650mm × 400mm — needs extensive segmentation.

| Part | Full Dimension | Segments | Join Method |
|------|---------------|----------|-------------|
| Top deck | 1100×650mm | ~30 tiles (220×130mm each, 5×6 grid) | M3 inserts + alignment pins |
| Side panels | 1100×200mm | 5 per side (220×200mm each) | M3 inserts |
| Electronics bay floor | 650×440mm | 6 panels (220×220mm) | M3 inserts + 2020 extrusion ribs |
| Rocker arm shell | 450mm long | 2 halves (225mm each) | M3 bolts + internal aluminium rod |
| Bogie arm shell | 300mm long | 2 halves (150mm each) | M3 bolts + internal aluminium rod |
| Wheel | 200mm dia × 80mm | 2 halves (glued + bolted) | M3 through-bolts |
| Camera mast | 600mm tall × 60mm OD | 3 sections (200mm each) | Telescoping fit |
| Arm segments | ~150mm each | 1 piece each | Direct |
| Fridge housing | 200×150×200mm | 4 panels | M3 inserts |
| Camera mounts | <100mm each | 1 piece each | Direct |

**Total Phase 2 parts**: ~80-100 printed pieces.

### 4.4 Join Design for Segmented Parts

**Method 1: Bolt + Heat-Set Insert** (primary method)

```
Cross-section of body panel join:

Panel A                    Panel B
┌──────────┐  ┌──────────────┐
│  ┌─[M3]──┼──┼─[insert]─┐  │
│  │       ││  ││          │  │
│  └───────┼┘  └┼──────────┘  │
│          │    │              │
└──────────┘  └──────────────┘

Overlap lip: 10mm on each panel
Insert spacing: 40-60mm apart
```

**Method 2: Alignment Pin + Bolt** (for precision joints)

```
Alignment pin (3mm steel rod) ensures panels are flush:

Panel A:  ○ pin hole (3.1mm)    Panel B:  ○ pin hole (3.1mm)
          ● bolt hole                     ⊗ heat-set insert

Pin goes in first (aligns panels), then bolt tightens.
```

**Method 3: Dovetail** (for body panels that don't need disassembly)

```
Panel A              Panel B
┌─────────\    /─────────┐
│          \  /          │
│           \/           │
│           /\           │
│          /  \          │
└─────────/    \─────────┘

Print tolerance: 0.2mm gap for sliding fit
Secured with CA glue after assembly
```

---

## 5. Print Orientation Guidelines

### 5.1 General Principle

**Layers should be perpendicular to the primary load direction.** FDM parts are weakest in the Z-axis (layer adhesion) and strongest in X/Y (within layers).

### 5.2 Orientation by Part

| Part | Primary Load | Print Orientation | Support Needed |
|------|-------------|-------------------|----------------|
| Rocker arm | Bending (vertical loads on wheels) | **On side** — longest axis horizontal, load direction along layer lines | Minimal — teardrop bearing holes |
| Bogie arm | Bending (vertical loads) | **On side** — same rationale | Minimal |
| Wheel hub | Radial (motor torque) | **Flat** — tread face on bed, layers stack along axle | None if designed with bridging |
| Body panels | Flat pressure | **Flat** — outer face on bed (best surface finish on bed side) | None |
| Steering bracket | Vertical load + torque | **Upright** — bearing seat on top | Yes — motor clip overhang |
| Connectors | Tension (bolt pull-out) | **Bolt axis perpendicular to bed** — inserts go in from top | None |
| Mast sections | Bending (wind, vibration) | **Upright** — layers wrap around circumference | None if round |

### 5.3 Rocker Arm Orientation Detail

```
WRONG — weak Z-axis takes the load:

   Bed
   ├───────────────────────────┤
   │  ████████████████████████ │ ← layers
   │  ████████████████████████ │
   │  ████████████████████████ │
   ├───────────────────────────┤
   Load applied here (down) → layers peel apart (delamination)

RIGHT — strong X-axis takes the load:

   Bed
   ├────────┤
   │ ██████ │ ← layers
   │ ██████ │
   │ ██████ │
   │ ██████ │
   │ ██████ │    Load applied here (left/right)
   │ ██████ │    → layers resist in shear (strong)
   │ ██████ │
   ├────────┤
```

### 5.4 Bearing Hole Orientation

Round holes printed horizontally (axis parallel to bed) tend to sag at the top due to gravity during bridging. Solutions:

1. **Teardrop profile**: Design the hole as a teardrop (point at top). The pointed top bridges cleanly. Ream to round after printing.

```
    /\         ← Point bridges cleanly
   /  \
  |    |       ← Circular lower portion
  |    |
   \  /
    \/
```

2. **Print with supports**: Less preferred — support material is hard to remove from inside a bearing seat.

3. **Print hole axis vertical**: If the part geometry allows, orient so the bearing bore is vertical. Circles print perfectly in XY.

---

## 6. Wheel Manufacturing

### 6.1 Phase 1 Wheels (80mm diameter)

**Design**: One-piece PETG wheel with integrated grousers (tread pattern).

```
Cross-section:

    ┌─┐  ┌─┐  ┌─┐  ┌─┐  ┌─┐    ← Grousers (3mm deep, 3mm wide)
    │ │  │ │  │ │  │ │  │ │
────┘ └──┘ └──┘ └──┘ └──┘ └────  ← Tyre surface

    │←── 80mm diameter ──→│

    ┌───────[Hub]───────┐
    │    ┌───────────┐  │
    │    │   ┌───┐   │  │   ← 6 spokes connecting hub to rim
    │    │   │3mm│   │  │
    │    │   │ D │   │  │   ← D-shaft bore (3.1mm)
    │    │   └───┘   │  │
    │    └───────────┘  │
    └───────────────────┘
```

**Spoke pattern options**:
- **Straight radial spokes** (simplest): 6-8 rectangular spokes (4mm wide × 6mm tall). Prints flat with no supports. Adequate for Phase 1.
- **Curved/swept spokes** (recommended for Mars aesthetic): Spokes curve in one direction like a turbine. Curvature is in X/Y plane so prints without support. Better at absorbing lateral impacts. Looks like Curiosity/Perseverance wheels.

Grouser pattern: **Chevron** (V-shaped, point facing forward)
- 12 grousers evenly spaced (30° apart)
- 3mm depth, 3mm wide at base, 2mm wide at tip
- Chevron angle: 120° (60° from centre line)
- Good for grass (digs in for traction) and gravel (self-cleaning)

### 6.2 Phase 2 Wheels (200mm diameter)

**Design**: Two-piece construction — PETG hub + TPU tyre.

**Hub** (printed in two halves, bolted together around motor shaft):
- 6-spoke design with central D-shaft bore
- 4× M3 mounting bolts (through both halves)
- Outer rim: groove for TPU tyre retention

**TPU tyre** (printed as a flexible ring):
- Material: TPU 95A (Shore 95A hardness — semi-flexible)
- Width: 80mm
- Thickness: 8mm
- Chevron grousers: 5mm deep, 4mm wide
- Printed flat as a ring (180mm ID, 200mm OD)
- Stretches over hub rim — interference fit (0.3mm Phase 1, 0.5mm Phase 2) + optional CA glue

**TPU printing notes**:
- TPU requires direct drive extruder (Bowden tube has too much flex)
- If Ender 3 has Bowden: print grousers in PETG instead (less grip but printable)
- Alternative: use rubber O-rings or strips glued to PETG wheel rim

### 6.3 Motor Shaft Interface

| Phase | Motor | Shaft | Interface |
|-------|-------|-------|-----------|
| Phase 1 | N20 | 3mm D-shaft | D-bore in hub + M2 grub screw |
| Phase 2 | Chihai 37mm | 6mm D-shaft | D-bore in hub + M3 grub screw |

**D-shaft bore design**:
- Print bore 0.1mm oversized (3.1mm / 6.1mm)
- D-flat: 0.5mm deep (Phase 1) / 1.0mm deep (Phase 2)
- Grub screw hole: perpendicular to shaft, tapped M2/M3
- Bore length: ≥8mm (Phase 1) / ≥15mm (Phase 2) for adequate engagement

---

## 7. Post-Processing

### 7.1 Standard Post-Processing

| Step | Method | Purpose |
|------|--------|---------|
| 1 | Remove supports | Clean up overhangs |
| 2 | Trim stringing | Hot air gun or lighter (quick pass) |
| 3 | Ream bearing holes | 22mm drill bit by hand | Ensure 608ZZ fits |
| 4 | Ream shaft bores | Appropriate drill bit | Ensure motor shaft fits |
| 5 | Install heat-set inserts | Soldering iron at 220°C | Before assembly |
| 6 | Test-fit all joints | Dry assembly | Catch issues before final assembly |

### 7.2 UV Protection (Phase 2 Outdoor Parts)

PETG parts used outdoors should be protected from UV:

| Method | Durability | Effort | Cost | Notes |
|--------|-----------|--------|------|-------|
| UV-resistant spray paint | 2-3 years | Low | $10 | Rustoleum 2× spray, 2 coats |
| Automotive clear coat | 3-5 years | Low | $8 | 2K clear coat, very durable |
| Epoxy coating | 5+ years | Medium | $20 | XTC-3D or similar, fills layer lines too |
| Print in ASA instead | 5+ years | None | $5 extra/kg | Best solution — UV-resistant material |

**Recommendation**: Print structural parts in ASA for inherent UV resistance. For PETG body panels, apply 2 coats of automotive clear coat spray — quick, cheap, effective.

### 7.3 Waterproofing (Phase 2)

The rover will encounter rain. Electronic bays need weatherproofing:

| Method | Application | Notes |
|--------|------------|-------|
| Silicone gaskets | Panel joints | Cut from silicone sheet, compressed between panels |
| Hot glue seams | Non-removable panel joints | Quick, flexible, waterproof |
| Conformal coating | PCBs (ESP32, motor drivers) | Protects electronics from moisture |
| Drain holes | Body floor corners | Let condensation escape, prevent pooling |
| IP54 cable glands | Wire entry points | Thread through gland, tighten nut |
| Coroplast splash guards | Under body | Cheap, light, deflects road spray from wheels |

---

## 8. Estimated Print Times

### 8.1 Phase 1 Total

From EA-08 print summary:
- 22 parts
- ~65 hours total print time
- ~1 kg filament needed

At an average of 6-8 hours of printing per day (overnight prints), Phase 1 printing takes **~8-10 days**.

### 8.2 Phase 2 Total

| Category | Parts | Est. Time |
|----------|-------|-----------|
| Body panels (top deck) | 30 | 90 hrs |
| Body panels (sides) | 10 | 30 hrs |
| Electronics bay | 6 | 18 hrs |
| Rocker arms (2× 2 halves) | 4 | 24 hrs |
| Bogie arms (2× 2 halves) | 4 | 12 hrs |
| Wheels (6× 2 halves) | 12 | 36 hrs |
| Steering brackets | 4 | 8 hrs |
| Fixed motor mounts | 2 | 4 hrs |
| Camera mast sections | 3 | 9 hrs |
| Arm segments | 12 | 24 hrs |
| Fridge housing | 4 | 12 hrs |
| Camera mounts | 7 | 7 hrs |
| Connectors/brackets | 40 | 40 hrs |
| Diff bar adapters | 3 | 3 hrs |
| **TOTAL** | **~141** | **~317 hrs** |

At 8 hours printing per day: **~40 days of printing**.

### 8.4 Community Benchmarks

These open-source rover builds provide useful reference points:
- **Sawppy** (Roger Cheng): ~3 kg filament, 3 spools. PLA prototyped then reprinted in PETG. 3 perimeters, 0.4mm nozzle. Wheels print outer-face-down without supports.
- **ExoMy** (ESA): 1.5 kg PLA, 0.15mm layers, 20% infill. ~2 weeks print time for all structural parts. 2.5 kg total rover weight.

### 8.3 Filament Budget (Phase 2)

| Material | Weight | Spools (1kg) | Cost |
|----------|--------|-------------|------|
| PETG (body panels, brackets) | ~3.5 kg | 4 | $80-100 |
| ASA (structural: arms, mounts) | ~1.0 kg | 1 | $25-30 |
| TPU (wheel tyres) | ~0.3 kg | 1 | $25-30 |
| Failed prints/waste (~15%) | ~0.7 kg | — | included |
| **TOTAL** | **~5.5 kg** | **6 spools** | **~$130-160** |

The EA-06 budget allocated $60 for 4× PETG 1kg spools. The revised estimate is $130-160 for complete filament needs — an additional ~$70-100. This should be flagged as a budget adjustment.

---

## 9. Common Failure Modes & Prevention

| Failure Mode | Cause | Prevention |
|-------------|-------|------------|
| Warping (corners lift from bed) | Uneven cooling, poor adhesion | PEI sheet, 75°C bed, brim on large parts |
| Layer delamination | Under-extrusion, too fast, too cold | Calibrate e-steps, slow down, raise temp 5°C |
| Bearing seat too tight | Print shrinkage | Test-print bearing block first, adjust ±0.1mm |
| Bearing seat too loose | Over-extrusion | Reduce flow by 2-5%, reprint |
| Heat-set insert crooked | Rushed installation | Use insert tip, go slow, press straight |
| Heat-set insert blowout | Insufficient wall thickness | Ensure ≥2.4mm wall around insert |
| Stringing between parts | Wet filament, poor retraction | Dry filament (4hrs at 65°C), increase retraction |
| Elephant's foot (first layer bulge) | Nozzle too close, bed too hot | Raise nozzle 0.02mm, reduce bed temp 5°C |
| Part snaps at layer line | Weak inter-layer adhesion | More walls, higher temp, slower speed |
| D-shaft bore too tight | Thermal contraction | Print 0.1mm oversized, ream to fit |

### 9.1 Filament Drying

Both PETG and ASA absorb moisture from air, degrading print quality:

| Material | Max moisture | Dry temp | Dry time | Storage |
|----------|-------------|----------|----------|---------|
| PETG | 0.08% | 65°C | 4-6 hours | Vacuum bag + desiccant |
| ASA | 0.04% | 80°C | 4-6 hours | Vacuum bag + desiccant |
| TPU | 0.15% | 50°C | 4-8 hours | Vacuum bag + desiccant |

**Drying method**: Kitchen oven at minimum setting with door cracked, or a food dehydrator ($30). Print straight from the dryer if possible.

---

## 10. Recommended Print Sequence (Phase 2)

The build sequence should match the assembly order from EA-08, starting with the hardest-to-replace structural parts:

1. **Bearing test blocks** — validate all bearing seat dimensions
2. **Heat-set insert test block** — validate insert hole size
3. **2020 extrusion connectors** (40×) — needed first for frame assembly
4. **Rocker arms** (4 halves) — long prints, structural
5. **Bogie arms** (4 halves) — structural
6. **Differential bar adapters** (3×)
7. **Steering brackets** (4×) — needs servo + motor for test fit
8. **Fixed motor mounts** (2×)
9. **Wheels** (12 halves) — can print while assembling suspension
10. **TPU tyres** (6×) — last (need hub dimensions confirmed)
11. **Electronics bay floor panels** (6×) — needed for electronics layout
12. **Side panels** (10×) — can print while wiring electronics
13. **Camera mounts** (7×) — needed for sensor installation
14. **Camera mast sections** (3×)
15. **Arm segments** (12×) — can print during software development
16. **Fridge housing** (4×) — low priority
17. **Top deck panels** (30×) — last — cosmetic, can run rover without them

---

*Document EA-11 v1.0 — 2026-03-15*
