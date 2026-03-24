# Engineering Analysis 11: 3D Printing Strategy

**Document**: EA-11
**Date**: 2026-03-15
**Purpose**: Define material selection, print settings, part segmentation, print orientation, heat-set insert specifications, and post-processing for all 3D printed rover components across all build phases.
**Depends on**: EA-01 (Suspension), EA-05 (Weight), EA-08 (Phase 1 Spec)
**See also**: `docs/references/3d-printing-strategy.md` and `docs/references/3d-printing-materials-research.md` — supplementary research with community project data, CNC Kitchen strength test numbers, and additional printing tips

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
| **Phase 1 (prototype)** | **PLA** | Low cost, easy to print on CTC Bizer (which only supports PLA), adequate strength for a 1.1 kg indoor prototype. Heat-set inserts work at 170-180°C. Phase 2 will upgrade to PETG/ASA for outdoor durability. |
| **Phase 2 (outdoor use)** | **ASA** for structural, **PETG** for body panels | ASA is the best outdoor material: excellent UV resistance, ABS-like properties without the brittleness. PETG for non-structural panels (food-safe for fridge area, easier to print). Will require a PETG/ASA-capable printer (not the CTC Bizer). |
| **Phase 3 (metal)** | **PETG/ASA** for retained plastic parts | Only camera housings, cable clips, and decorative elements remain plastic in Phase 3. |

### 1.3 Why PLA for Phase 1

PLA is the right choice for the Phase 1 indoor prototype:

1. **CTC Bizer compatibility**: The CTC Bizer only supports PLA reliably. No heated chamber, no all-metal hotend — PLA prints perfectly on this machine.
2. **Low cost**: PLA is the cheapest filament (~$18-22/kg). Phase 1 uses ~1 kg total, so <$25 in material.
3. **Easy to print**: PLA is the most forgiving material — minimal warping, no enclosure needed, prints at 200-210°C with 60°C bed and 100% fan.
4. **Adequate for indoor use**: At 1.1 kg total rover weight, PLA's 60 MPa tensile strength provides a 60x safety margin over the N20 motor loads. The prototype will operate indoors, so UV degradation and heat deflection (52°C) are not concerns.
5. **Heat-set inserts work well**: Brass inserts install cleanly in PLA at 170-180°C (lower than the 220°C used for PETG).
6. **Phase 2 upgrade path**: When the rover moves to full-scale outdoor operation, all structural parts will be reprinted in PETG/ASA on a more capable printer. PLA Phase 1 parts serve as proven templates.

**PLA limitations to be aware of**:
- Will soften above 52°C — do not leave in direct sun or a hot car
- Brittle under impact — handle with care, avoid drops
- Not UV-stable — prototype is for indoor/sheltered use only

### 1.4 Printer: CTC Bizer (MakerBot Replicator 1 Dual Clone)

| Specification | Value |
|---------------|-------|
| **Model** | CTC 3D Bizer (MakerBot Replicator 1 Dual clone) |
| **Build volume** | 225 × 145 × 150mm |
| **Extruders** | Dual (use left nozzle only; park/remove right nozzle) |
| **Firmware** | MakerBot/Sailfish (not Marlin) |
| **File format** | **x3g** (NOT standard gcode) — requires GPX converter |
| **Heated bed** | Yes |
| **Material support** | PLA only (no all-metal hotend for PETG/ABS/ASA) |
| **Bed adhesion** | Heated bed 60°C + glue stick or painter's tape; brim for large parts |
| **Status** | Older machine, needs setup and calibration before first print |

**Material compatibility**:

| Material | CTC Bizer Compatible? | Notes |
|----------|----------------------|-------|
| PLA | **Yes** — primary material | 200-210°C nozzle, 60°C bed |
| PETG | No | Requires all-metal hotend (PTFE tube degrades above 240°C) |
| ABS/ASA | No | Requires enclosed chamber + all-metal hotend |
| TPU | No | Requires direct drive extruder (CTC Bizer is Bowden-fed) |

**x3g file format workflow**:

The CTC Bizer uses x3g format (not standard gcode). The full workflow is:

```
Fusion 360 → STL → Cura (slice) → .gcode → GPX (convert) → .x3g → SD card → Print
```

GPX command: `gpx -m cr1d input.gcode output.x3g`
GPX v2.6.8 installed at `C:\Users\charl\bin\gpx.exe`, machine type `cr1d` (CTC Replicator 1 Dual).

**For Phase 2**: A PETG/ASA-capable printer will be needed (e.g., Bambu Lab A1, Prusa MK4, or similar). Budget ~$200-400 for a Phase 2 printer upgrade.

---

## 2. Print Settings by Part Category

### 2.1 Structural Parts (Rocker Arms, Bogie Arms, Motor Mounts)

These parts bear mechanical loads and must resist bending/shear forces.

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PLA (Phase 1) / ASA (Phase 2) | PLA adequate for 1.1 kg indoor prototype; ASA for outdoor durability |
| Layer height | 0.2mm | Good strength, reasonable speed |
| Nozzle | 0.4mm standard | Default, widely available |
| Walls/perimeters | 4 (1.6mm wall thickness) | Primary load path is through walls |
| Top/bottom layers | 5 (1.0mm) | Prevents puncture and adds rigidity |
| Infill | 50% gyroid | High strength-to-weight ratio |
| Print speed | 40-50 mm/s | Slower for better layer adhesion |
| Temperature (PLA) | **200-210°C nozzle, 60°C bed** | Standard PLA on CTC Bizer |
| Temperature (ASA) | 250°C nozzle, 100°C bed | Requires enclosure (Phase 2 printer) |
| Cooling fan | **100% (PLA)**, 0% first layers (ASA) | PLA benefits from maximum cooling |
| Retraction | 5mm at 40mm/s (Bowden) | Prevents stringing |

### 2.2 Body Panels (Cosmetic + Light Structural)

Flat or curved panels that form the rover body shell. Phase 1 body is split into 4 quadrants (FL/FR/RL/RR), each 220x130mm.

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PLA (Phase 1) / ASA (Phase 2) | PLA for indoor prototype; ASA for weather resistance |
| Layer height | 0.2mm | Good surface finish |
| Walls | 4 (1.6mm / 4mm wall for Phase 1 body quadrants) | Thicker walls for rigidity and panel line grooves |
| Top/bottom layers | 4 | Smooth surface |
| Infill | 15-20% gyroid | Panels don't bear heavy loads |
| Print speed | 50-60 mm/s | Faster for large flat parts |
| Temperature (PLA) | **200-210°C nozzle, 60°C bed** | Standard PLA |
| Cooling fan | **100%** | PLA benefits from maximum cooling |
| Notes | Print face-down for best top surface | Bed side = exterior surface |

### 2.3 Wheels

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PLA (Phase 1 hub) | Adequate for indoor prototype; rigid PLA wheels with rubber O-ring traction bands |
| Layer height | 0.2mm | Smooth tread surface |
| Walls | 3 | Hub is reinforced by spokes |
| Infill | 25% gyroid | Lightweight but rigid |
| Print orientation | Flat (tread face on bed) | Strongest axis is radial |
| Temperature (PLA) | **200-210°C nozzle, 60°C bed** | Standard PLA |
| Cooling fan | **100%** | PLA benefits from maximum cooling |
| Notes | D-shaft bore may need reaming | Print slightly undersized, ream to fit |

### 2.4 Connectors & Brackets (Heat-Set Insert Parts)

Small parts that join extrusions or hold bearings.

| Setting | Value | Rationale |
|---------|-------|-----------|
| Material | PLA (Phase 1) / ASA (Phase 2) | PLA holds heat-set inserts well at 170-180°C |
| Layer height | 0.16mm | Better resolution for insert holes |
| Walls | 4-5 | Maximum wall around inserts |
| Infill | 60-80% | Dense for insert retention |
| Print speed | 35-40 mm/s | Precision over speed |
| Temperature (PLA) | **200-210°C nozzle, 60°C bed** | Standard PLA |
| Cooling fan | **100%** | PLA benefits from maximum cooling |
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
| Pull-out strength (PLA) | 600-1,000N (per CNC Kitchen testing with proper hole sizing) |
| Torque resistance | ~2.5 N·m |

### 3.2 Hole Design for Inserts

| Feature | Dimension | Notes |
|---------|-----------|-------|
| Hole diameter | 4.8mm (general) | Slightly undersized vs insert OD (5.7mm) — plastic flows around knurls |
| Hole diameter (vertical insertion) | 4.2mm | Insert axis perpendicular to layers — tighter hole, knurls grip layer lines |
| Hole diameter (horizontal insertion) | 4.25mm | Insert axis parallel to layers — slightly larger to avoid pushing layers apart |
| Hole depth | 5.5mm | 1mm deeper than insert to allow full seating |
| Wall thickness around hole | ≥2.4mm (3 walls at 0.4mm line width) | Prevents blowout |
| Chamfer at top | 0.5mm × 45° | Guides insert during installation |
| Bottom | Flat (blind hole) | Don't use through-hole unless needed |

### 3.3 Installation Method

| Step | Detail |
|------|--------|
| Tool | Soldering iron with M3 insert tip (or standard conical tip) |
| Temperature | **170-180°C for PLA** (lower than PETG's 220°C to avoid melting too much surrounding material), 230°C for ASA |
| Technique | Place insert on hole, press straight down with iron tip inside insert thread. Let the heat melt the surrounding plastic — do NOT force. Takes 2-3 seconds. |
| Depth | Flush with surface or 0.2mm below |
| Alignment | Press straight — crooked inserts compromise thread engagement |
| Cool time | 10 seconds before handling |
| Quality check | Thread an M3 bolt in/out — should go smooth with no binding |

### 3.4 Insert Orientation vs Print Layers

**Best**: Insert axis perpendicular to print layers (inserted from top or bottom face). The knurls grip into layer lines, maximising pull-out strength.

**Acceptable**: Insert axis parallel to layers (inserted from side). Slightly lower pull-out strength (~70% of perpendicular) because the knurls push layers apart rather than gripping into them.

**Rule**: Where possible, design parts so inserts go in perpendicular to layers. If this conflicts with the best print orientation for strength, prioritise the print orientation and accept slightly lower insert strength (still far exceeds our loads).

**Always print a test insert block first.** A small 30×30×15mm block with 2-3 insert holes lets you validate hole diameter, insertion depth, and pull-out strength before committing to a multi-hour structural print.

### 3.5 Slicer Tip: Local Infill Override

In Cura or PrusaSlicer, use **modifier meshes** to set 100% infill in a cylinder around each insert hole while keeping the rest of the part at normal infill (30-50%). This maximises insert retention without wasting filament on the entire part. Create a cylinder modifier (10mm OD × hole depth) centred on each insert location.

---

## 4. Part Segmentation Strategy

### 4.1 CTC Bizer Build Volume

| Dimension | Value | Usable (with margins) |
|-----------|-------|----------------------|
| X | 225mm | 215mm |
| Y | 145mm | 135mm |
| Z | 150mm | 140mm |

**Note**: The CTC Bizer bed (225x145mm) is narrower than common printers like the Ender 3 (220x220mm). The 145mm Y dimension is the primary constraint — all parts must fit within this. The 150mm Z height is also relatively limited.

### 4.2 Phase 1 Segmentation (0.4 Scale)

Body is 440mm × 260mm × 80mm — exceeds the 225×145mm CTC Bizer bed in both X and Y directions.

| Part | Full Dimension | Segments | Segment Size | Join Method |
|------|---------------|----------|-------------|-------------|
| Body | 440×260×80 | **4 quadrants (FL/FR/RL/RR)** | **220×130×80 each** | M3 bolts + heat-set inserts at seams |
| Top deck | 440×260mm | **4 tiles (FL/FR/RL/RR)** | **220×130mm each** | Clips + alignment features |
| Rocker arm | 180mm long | 2 halves (front + rear) | ~90mm each | M3 bolts through overlap |
| Bogie arm | **180mm** long | 1 piece | Fits in 215mm | No segmentation |
| Diff bar | 300mm rod | 1 piece + rod | Adapters fit easily | Steel rod core |
| Wheels | 80mm dia | 1 piece each | Fits easily | No segmentation |
| Steering brackets | 35×25×40 | 1 piece each | Small | No segmentation |

**Total segments**: 4 (body quadrants) + 4 (top deck tiles) + 4 (rocker halves) + 2 bogies + 3 diff adapters + 6 wheels + 4 steering + 2 fixed mounts + 2 servo mounts + 1 electronics tray + 1 strain relief clip + 1 fuse holder + 1 switch mount = **~26 core parts** (see EA-08 and Phase 1 BOM for complete list with 46 total including hardware)

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

**Design**: One-piece PLA wheel with spoke lightening holes, rim retention lips, and rubber O-ring traction bands (PLA is too rigid for integrated grousers to provide traction; O-rings provide grip on hard surfaces). Optional TPU tire if a compatible printer becomes available.

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
- CTC Bizer cannot print TPU (Bowden-fed). Phase 1 uses rigid PLA wheels with rubber O-ring traction bands instead.
- Phase 2 TPU tire option: 86mm OD, 70mm bore, 32mm width, 48 radial tread ribs (see `cad/scripts/rover_tire.py`)
- Alternative for any phase: use rubber O-rings (70mm ID x 3mm cross-section) in rim grooves for traction

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
| 5 | Install heat-set inserts | Soldering iron at 170-180°C (PLA) / 220°C (PETG) | Before assembly |
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

**4-step spray paint process (best results for PETG panels)**:
1. **Sand**: 220 grit over entire surface for mechanical adhesion
2. **Primer**: Rust-Oleum 2X Ultra Cover Primer — 2 coats, 15min between coats
3. **Color**: 2-3 thin coats of spray paint (any Rust-Oleum 2X color), 10min between coats. Thin coats prevent drips and build even coverage.
4. **Clear coat**: Rust-Oleum Crystal Clear matte or satin — 2 coats, 20min between coats. **This is the primary UV barrier.** Without clear coat, the color will fade and the plastic underneath degrades.
5. Total cost: ~£15-20 for entire rover

**Important notes**:
- XTC-3D epoxy fills layer lines and gives a smooth finish but is NOT UV stable — must apply clear coat over it or it will yellow and crack within months outdoors.
- ASA can be chemically smoothed with MEK (methyl ethyl ketone) but MEK is hazardous (respiratory and skin irritant, flammable). Spray paint + clear coat is a safer alternative that also provides UV protection and colour in one process.

### 7.4 Phase 2 Structural Reinforcement

For high-stress parts at full scale (16.7 kg rover weight):

| Method | Application | Difficulty | When to Use |
|--------|------------|------------|-------------|
| Carbon fiber strips (1mm × 10mm pultruded) | Epoxy-bonded to rocker/bogie arm surfaces | Easy — glue flat strips along arm | Phase 2 rocker arms (bending loads) |
| Fiberglass tape (25mm woven) | Wrapped around pivot joints with epoxy | Moderate — wet layup | Phase 2 pivot bosses (shear loads) |
| M3 threaded rod tensile core | Through-bolt running arm length | Easy — drill and insert | Alternative to aluminium tube core |

**Not needed for Phase 1** — at 1.1 kg total weight, PLA alone is more than adequate.

**Reinforcement details (Phase 2)**:

- **Carbon fiber strips**: Bond 1mm × 10mm pultruded carbon fiber strips to the flat faces of rocker and bogie arms using structural epoxy (e.g. JB Weld or West System). Apply strips to both top and bottom faces for maximum effect. Increases bending stiffness 3-5× compared to bare PETG/ASA. Lightly sand the printed surface and the strip with 120 grit before bonding. Clamp or tape in place for 24hr cure.
- **Fiberglass tape**: Wrap 25mm woven fiberglass tape around pivot joint bosses with epoxy (wet layup). 2-3 wraps provides substantial shear reinforcement at the most stressed points. Sand smooth after cure.
- **Differential bar tensile core**: Run an M3 threaded rod through the full length of the differential bar as a tensile core. The rod carries tension loads while the printed shell handles compression, preventing the bar from snapping under suspension articulation.

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
- ~26 core parts (46 total including hardware)
- ~69 hours total print time
- ~1 kg PLA filament needed

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
| Warping (corners lift from bed) | Uneven cooling, poor adhesion | Glue stick or painter's tape, 60°C bed (PLA), brim on large parts |
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

All filaments absorb moisture from air, degrading print quality (though PLA is less sensitive than PETG/ASA):

| Material | Max moisture | Dry temp | Dry time | Storage |
|----------|-------------|----------|----------|---------|
| PLA | 0.10% | 45°C | 4-6 hours | Vacuum bag + desiccant (less critical than PETG) |
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

*Document EA-11 v2.0 — 2026-03-23 (major rewrite: PLA for Phase 1, CTC Bizer printer, 4-quadrant body, x3g workflow)*
