# 3D Printing Strategy — Mars Rover Garden Robot

> **SUPERSEDED**: This document is outdated. The authoritative 3D printing strategy is now
> **EA-11** (`docs/engineering/11-3d-printing-strategy.md`) and
> **Print Strategy** (`docs/plans/print-strategy.md`).
> Key changes: Printer is CTC Bizer (225x145x150mm, not Ender 3), material is PLA (not PETG),
> body splits into 4 quadrants (not 2 halves). This file is retained for historical reference only.

~~**Printer**: Ender 3 (220x220x250mm build volume)~~
**Printer**: CTC Bizer (225x145x150mm) — see EA-11
**Date**: 2026-03-15 (STALE — see EA-11 updated 2026-03-24)
**Applies to**: ~~Phase 1 (0.4 scale) and Phase 2 (full scale)~~ HISTORICAL ONLY

---

## 1. Chassis Segmentation Strategy

### Phase 1: 0.4 Scale (~440x260mm body)

At 0.4 scale, the full-size 1100x650mm body becomes approximately 440x260mm — too large for a single 220x220mm bed in one axis. The 260mm width fits the bed, but the 440mm length must be split.

**Segmentation plan (body):**

| Segment | Approx Size | Notes |
|---------|-------------|-------|
| Front body half | 220x220mm | Includes front wheel mount points |
| Rear body half | 220x220mm | Includes rear wheel mount points |
| Centre bridge (optional) | ~60x220mm | Only if body exceeds 440mm; may be absorbed into front/rear halves with overlap |

**Split line placement rules:**
- Cut along structural ridges or panel lines, never through thin walls or mounting bosses
- Place splits perpendicular to the longest axis (cut across the 440mm length)
- Offset the split from the centre by 10-20mm so the joint is not at the weakest point (the middle)
- Add alignment features at every split: 2x dowel pin holes (3mm diameter, 6mm deep) plus 2x M3 bolt-through holes
- For segments further than 100mm apart, make one dowel hole a slot (3x5mm) to absorb printer tolerance

**Remaining Phase 1 parts (each fits a single print):**

| Part | Count | Approx Size at 0.4x | Fits Bed? |
|------|-------|---------------------|-----------|
| Rocker arm | 2 | ~180x40x30mm | Yes |
| Bogie arm | 2 | ~120x40x30mm | Yes |
| Wheel | 6 | ~80mm dia x 32mm wide | Yes |
| Differential bar | 1 | ~130x30x30mm | Yes |
| Steering brackets | 4 | ~40x40x30mm | Yes |
| Motor mounts | 6 | ~40x30x25mm | Yes |
| Pivot brackets | 4 | ~35x35x40mm | Yes |

**Total Phase 1: ~15-20 individual prints.**

### Phase 2: Full Scale (1100x650mm body)

The full-scale body must be heavily segmented. Key approach: use a grid pattern of panels screwed to an aluminium extrusion skeleton (2020 profile).

**Body segmentation (top deck, ~1100x650mm):**
- Divide into a grid of ~200x200mm panels (leaving margin for bolt flanges)
- Approximately 5 panels long x 3 panels wide = 15 top panels
- Add 10-15 side panels (~200x150mm each)
- Each panel has M3 bolt holes on flanges that attach to 2020 extrusion

**Structural parts segmentation:**

| Part | Full Size | Segments | Join Method |
|------|-----------|----------|-------------|
| Rocker arm | ~450mm long | 2-3 segments | Aluminium rod core + bolts |
| Bogie arm | ~300mm long | 2 segments | Aluminium rod core + bolts |
| Wheel | 200mm dia | 2 halves (split at mid-plane) | M3 bolts through rim |
| Mast sections | 150mm each | 3-4 sections | Telescoping or bolt-together |
| Arm segments | ~100mm each | Individual links | Bolt + bearing at joints |

**Total Phase 2: ~80-100 individual prints.**

---

## 2. Print Orientation Per Part Type

Print orientation is critical — FDM parts are weakest between layers (Z-axis). Orient parts so the primary load direction is along the X/Y plane (within layers), not across layers (Z-axis).

### Orientation Guide

| Part | Orientation | Reasoning |
|------|------------|-----------|
| **Wheels** | Outer face flat on bed | Spokes print as continuous perimeters; no supports needed; hub detail faces up |
| **Rocker arms** | Flat side down (long axis along X) | Bending loads run along printed layers, maximising strength; pivot holes print vertically (strongest) |
| **Bogie arms** | Same as rocker arms | Same load pattern — bending along the arm length |
| **Body panels** | Flat face down | Panels are essentially plates; print flat for dimensional accuracy and smooth outer face |
| **Differential bar** | Long axis along X, flat on bed | Torsional loads along the bar; minimise layer-crossing stress |
| **Steering brackets** | Bolt face down | Puts the bearing bore vertical (roundest) and load path along layers |
| **Motor mounts** | Motor face down | Shaft hole prints vertically (circular accuracy); mounting flange on top |
| **Pivot brackets** | Bearing bore vertical | Bearing seats need circular accuracy; vertical bores print rounder than horizontal |

### Key Orientation Rules

1. **Bearing and shaft bores should be vertical** — horizontal holes print as ovals with layer stepping; vertical holes are round
2. **Load-bearing arms print flat** — bending loads along the printed layers, not across them
3. **Thin panels print flat** — best dimensional accuracy, smoothest face against bed
4. **If a part has a flat face and a detailed face, put the flat face down** — bed surface gives the smoothest finish

---

## 3. Joint and Connection Methods

### Between Segments of the Same Part

**For structural parts (rocker/bogie arms, chassis halves):**

1. **Bolt-through with alignment pins** (primary method):
   - 2x M3 dowel pin holes (3.0mm diameter, 6mm deep) for alignment
   - 2-4x M3 bolt-through holes (3.2mm clearance hole + heat-set insert on receiving side)
   - Apply thin layer of cyanoacrylate (super glue) or epoxy on the mating face after test-fit
   - Bolts provide clamping force; pins provide alignment; adhesive prevents shear

2. **Tongue-and-groove** (for panel-to-panel):
   - 2mm deep tongue, 2.1mm groove (0.1mm clearance)
   - Run the tongue along the full edge for maximum shear area
   - Combine with 2x M3 bolts at the ends

3. **Dovetail** (for parts that must be disassembled):
   - Print dovetail at 60-degree angle, 3mm depth
   - Slide-together joint with a retaining M3 bolt
   - Good for body panels on the extrusion skeleton

### Between Different Parts

**For pivot joints (rocker-to-bogie, rocker-to-body):**
- 608ZZ bearing (8mm bore, 22mm OD, 7mm thick) pressed into printed housing
- 8mm steel shaft through bearing
- Retaining clip or M8 nut on shaft end
- Design the bearing pocket 21.9mm ID (0.1mm interference fit for press-in)

**For body panels to extrusion:**
- M3 T-nuts in 2020 extrusion channel
- M3 bolt through panel flange into T-nut
- Panels are removable for electronics access

---

## 4. Material Selection

### Summary Table

| Component | Material | Why |
|-----------|----------|-----|
| Rocker arms | PETG | High bending loads, outdoor UV, impact resistance |
| Bogie arms | PETG | Same as rocker — structural, outdoor |
| Differential bar | PETG | Torsional load, must not snap |
| Chassis body segments | PETG | Structural, outdoor exposure |
| Steering brackets | PETG | High stress at servo attachment |
| Motor mounts | PETG | Vibration, heat from motors |
| Pivot brackets | PETG | Bearing press-fit, structural |
| Body panels (cosmetic) | PLA or PETG | Low stress; PLA fine for Phase 1 prototype, PETG for Phase 2 outdoor |
| Wheel hubs/spokes | PETG | Torsional stress from motor, impact from terrain |
| Wheel tyres/treads | TPU 95A | Flexible, grip, shock absorption |
| Cable clips, covers | PLA | Non-structural, fast print |
| Camera mounts | PLA or PETG | Low stress; PETG if outdoors long-term |

### Why PETG for Structural Parts

1. **Impact resistance**: PETG has roughly double the impact strength of PLA. A rover hitting a rock or curb needs parts that deform rather than shatter. PLA fails catastrophically (brittle fracture); PETG yields and flexes.

2. **Layer adhesion**: PETG achieves significantly stronger inter-layer bonding than PLA. Since FDM parts are weakest between layers, this directly improves the weakest axis of every printed part.

3. **Outdoor durability**: PETG handles UV exposure, rain, and temperature swings (up to ~70C glass transition vs PLA's ~55C). A rover sitting in summer sun will not soften or deform in PETG. PLA will warp above 50-55C, which a dark-coloured part in direct sunlight can easily reach.

4. **Chemical resistance**: PETG resists oils, greases, and cleaning products that might contact a garden robot.

5. **Flexibility over brittleness**: PETG's lower tensile strength (40-50 MPa vs PLA's 50-60 MPa) is misleading — PETG absorbs far more energy before failure. For a robot that encounters unpredictable loads, toughness matters more than peak tensile strength.

### When to Use PLA

- Phase 1 prototype test prints (fast iteration, will be reprinted in PETG once validated)
- Non-structural cosmetic pieces (decorative grousers, logos, bezels)
- Quick jigs and test fixtures during development
- Any part that will never see outdoor sun exposure

### TPU for Wheel Treads

- Shore hardness 95A (standard TPU filament)
- Provides grip on grass, gravel, and pavement
- Absorbs shock from terrain impacts
- Print as a separate tyre that press-fits over the PETG hub/spoke wheel
- 95A is stiff enough to hold shape but flexible enough for traction

---

## 5. Print Settings Per Component Type

### Structural Parts (rocker, bogie, brackets, chassis segments)

| Setting | Value | Reasoning |
|---------|-------|-----------|
| Material | PETG |  |
| Nozzle temp | 230-240C | Ender 3 Bowden limit ~245C; stay below to prevent PTFE tube degradation |
| Bed temp | 75-85C | PETG adheres well at 80C; use painter's tape or PEI sheet to prevent glass fusion |
| Layer height | 0.2mm | Balance of strength and speed; 0.2mm gives good layer bonding |
| Perimeters (walls) | 4 | 4 x 0.4mm nozzle = 1.6mm wall thickness; walls contribute ~28% of part strength; 4 walls at stress points |
| Top/bottom layers | 5 | 5 x 0.2mm = 1.0mm solid top/bottom |
| Infill | 30-40% gyroid | Gyroid is isotropic (equal strength in all directions); 30% for arms, 40% for pivot brackets |
| Print speed | 40-50mm/s | Slower for PETG to prevent stringing; structural parts benefit from slower speed |
| Retraction | 5-6mm at 35-40mm/s | Bowden tube PETG settings; reduce stringing |
| Cooling fan | 30-50% | PETG needs less cooling than PLA; too much cooling weakens layer bonds |
| First layer speed | 20mm/s | Slow first layer for adhesion |
| Bed adhesion | Brim (5mm) | PETG on painter's tape or PEI; brim prevents corner lift |

### Body Panels (cosmetic, low-stress)

| Setting | Value | Reasoning |
|---------|-------|-----------|
| Material | PETG (outdoor) or PLA (Phase 1 only) |  |
| Layer height | 0.2mm | Good surface finish |
| Perimeters | 3 | 3 x 0.4mm = 1.2mm; adequate for panels |
| Top/bottom layers | 4 | 4 x 0.2mm = 0.8mm |
| Infill | 15-20% gyroid | Panels are low-stress; save material and time |
| Print speed | 50-60mm/s | Can print faster since panels are not structural |

### Wheels (hub + spokes in PETG)

| Setting | Value | Reasoning |
|---------|-------|-----------|
| Material | PETG |  |
| Layer height | 0.2mm |  |
| Perimeters | 4 | Spokes need strength; 4 walls on thin spoke cross-sections |
| Top/bottom layers | 5 |  |
| Infill | 40% gyroid | Wheels take impact loads; higher infill for toughness |
| Print speed | 40mm/s | Accuracy matters for hub bore and spoke geometry |
| Orientation | Outer face on bed | Spokes print as continuous perimeters; hub detail faces up |

### TPU Tyres

| Setting | Value | Reasoning |
|---------|-------|-----------|
| Material | TPU 95A |  |
| Nozzle temp | 220-230C | Typical for 95A TPU |
| Bed temp | 50-60C | Light adhesion; TPU sticks well |
| Layer height | 0.2mm |  |
| Perimeters | 3-4 | Tyre walls need flexibility + durability |
| Infill | 20% gyroid or 15% grid | Low infill for flex; gyroid distributes stress |
| Print speed | 20-25mm/s | TPU must print slowly on Bowden extruder; faster = jams |
| Retraction | Minimal or disabled | TPU compresses in Bowden tube; retraction causes jams |
| Cooling fan | 50-100% | TPU benefits from cooling to hold shape |
| Note | Bowden Ender 3 can struggle with TPU. Print very slowly. Consider a direct-drive mod if doing many TPU prints. |

---

## 6. Infill Pattern Analysis

### Why Gyroid

Gyroid is the recommended infill pattern for this project because:

1. **Isotropic strength** — equal strength in all directions (X, Y, and Z). A rover experiences loads from all angles (impacts, bending, torsion). Grid infill is strong top-to-bottom but weak at 45 degrees. Gyroid has no weak axis.

2. **Good strength-to-weight ratio** — at 30% density, gyroid provides excellent structural performance without wasting material.

3. **No sharp corners** — gyroid's smooth curves distribute stress and avoid stress concentration points that grid/rectilinear patterns create at every intersection.

4. **Prints reliably** — continuous extrusion paths without the frequent direction changes of honeycomb, leading to fewer printing artifacts.

### When to Use Alternatives

| Pattern | Use Case |
|---------|----------|
| Gyroid | Default for everything (structural + cosmetic) |
| Grid/Rectilinear | When you need maximum top-down compressive strength only (electronics tray) |
| Honeycomb | When you need crush resistance (fridge housing) |
| Lightning | Non-structural parts with large flat tops that just need support for the top surface |

### Infill Percentage Guide

| Stress Level | Infill % | Example Parts |
|-------------|----------|---------------|
| High stress | 40-50% | Pivot brackets, wheel hubs, steering knuckles |
| Medium stress | 25-35% | Rocker/bogie arms, chassis segments, motor mounts |
| Low stress | 15-20% | Body panels, covers, cable clips, decorative |

---

## 7. Reinforcement Strategies

### Heat-Set Inserts (M3 Brass)

Heat-set inserts provide reusable, strong threaded connections in printed parts. They melt into the plastic using a soldering iron and bond mechanically with knurled outer surfaces.

**Design rules for M3 inserts:**

| Parameter | Value |
|-----------|-------|
| Pilot hole diameter | 4.0mm (for standard M3 x 5mm OD inserts) |
| Hole depth | Insert length x 1.5 (e.g., 5mm insert = 7.5mm hole) |
| Wall thickness around insert | Minimum 2mm on all sides |
| Soldering iron temp (PETG) | 240-250C |
| Install method | Press straight down with soldering iron tip; do not wobble |
| Insert type | M3 x 5.7mm OD x 4.6mm length (CNC Kitchen recommended) |

**Placement strategy:**
- Every segment-to-segment joint: 2-4 inserts per joint face
- Every bracket-to-arm connection
- Every panel-to-extrusion flange point
- Motor mount holes (so motors can be swapped without re-threading)
- At least 3 perimeters of wall surrounding each insert for pull-out resistance

### Aluminium Tube/Rod Inserts

For rocker and bogie arms that span long distances and experience bending loads, a printed shell around an aluminium core is far stronger than solid plastic.

**Design approach:**

| Tube Type | OD | ID | Use |
|-----------|----|----|-----|
| 8mm aluminium rod (solid) | 8mm | N/A | Axle shafts, pivot pins |
| 10mm aluminium tube | 10mm | 8mm | Light arm reinforcement (Phase 1) |
| 12mm aluminium tube | 12mm | 10mm | Rocker arm core (Phase 2) |
| 16mm aluminium tube | 16mm | 14mm | Heavy structural members (Phase 2) |

**Channel design rules:**
- Print the arm as a hollow tube with a channel for the aluminium insert
- Channel internal diameter = tube OD + 0.3mm clearance (e.g., 12.3mm for 12mm tube)
- Add 1-2 grub screw holes (M3) through the printed wall to lock the tube in place
- The tube should extend the full length of the arm, protruding at each end into the pivot bracket
- For rocker arms in Phase 2 (450mm long, split into 2-3 segments): the aluminium tube runs through all segments, unifying them into one rigid assembly

**Where to use metal vs printed structure:**

| Location | Phase 1 (0.4x) | Phase 2 (1.0x) |
|----------|----------------|-----------------|
| Rocker arms | Printed only (short enough at 180mm) | 12mm aluminium tube core |
| Bogie arms | Printed only (180mm) | 10mm aluminium tube core |
| Differential bar | Printed only | 8mm steel rod |
| Wheel axles | 4mm steel shaft | 8mm steel shaft |
| Pivot pins | M3 bolts | 8mm steel shaft + 608 bearings |
| Body frame | Printed segments bolted together | 2020 aluminium extrusion skeleton |

### Bolt-Through Connection Design

For any joint that must be strong and optionally disassemblable:

1. **Clearance hole**: 3.2mm for M3 bolt (bolt passes through freely)
2. **Heat-set insert on receiving side**: 4.0mm pilot hole, insert melted in
3. **Washer under bolt head**: Distributes load, prevents bolt head pulling through plastic
4. **Minimum wall thickness**: 5mm around bolt holes for load-bearing connections
5. **Boss design**: Add a cylindrical boss (8mm OD, 5mm tall) around each bolt hole to increase local wall thickness
6. **Avoid edge bolts**: Keep bolt holes at least 6mm from any part edge

---

## 8. Wheel Design for FDM

### Spoke Patterns That Print Without Support

The wheel prints outer face flat on the bed. This means spokes must be designed so they can be printed layer-by-layer without overhangs exceeding 45 degrees.

**Recommended spoke patterns:**

1. **Straight radial spokes (simplest):**
   - 6-8 spokes radiating from hub to rim
   - Each spoke is a rectangular cross-section (~4mm wide x 6mm tall)
   - Prints perfectly flat with no supports
   - Adequate for Phase 1 (small, light rover)

2. **Curved/swept spokes (NASA aesthetic):**
   - Spokes curve in one direction (like a turbine)
   - Still prints flat without support since the curvature is in the X/Y plane
   - Looks more like the real Curiosity/Perseverance wheels
   - Better at absorbing lateral impacts than straight spokes

3. **Web/lattice pattern:**
   - Thin web connecting hub to rim with cutout holes
   - Prints as a nearly solid disc with weight-saving holes
   - Very strong but heavier than spokes
   - Good for Phase 2 where wheels are 200mm and take more load

**Key spoke design rules:**
- Minimum spoke width: 3mm (with 0.4mm nozzle, this gives 7-8 perimeters across the spoke)
- Spoke height (Z in print orientation): 6-10mm for Phase 1, 15-20mm for Phase 2
- Hub wall thickness: 3mm minimum around motor shaft bore
- Rim width should match tyre width minus 2mm on each side (tyre lips wrap over rim edges)

### Motor Hub Attachment Methods

| Method | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **D-shaft flat** | Simple, cheap motors have D-shafts | Weak in torque; plastic D-bore rounds out | Phase 1 only (low torque) |
| **Hex bore** | Strong torque transfer; self-centering | Requires hex shaft or adapter | Good for Phase 2 |
| **Set screw (grub screw)** | Easy to assemble/disassemble | Single point contact; can slip | Backup retention only |
| **Keyed shaft** | Very strong, no slipping | Requires machined keyway | Phase 3 metal only |
| **Clamping hub** | Very strong; split clamp + bolt | Requires thicker hub wall | Best for Phase 2 PETG |

**Recommended approach:**
- **Phase 1**: D-shaft bore printed into hub (motor shaft is 3mm D-shape on N20 gearmotors). Add an M3 set screw through the hub wall as backup retention. Print the D-flat with 0.1mm extra clearance.
- **Phase 2**: Hex coupler. Use a brass or aluminium hex coupler between the motor shaft and the wheel hub. The coupler press-fits or screws into the hub. This transfers torque through the hex geometry rather than relying on plastic alone.

### TPU Tyre Design

**Construction:**
- Print the tyre as a separate ring in TPU
- Internal diameter of tyre = outer diameter of PETG wheel rim (interference fit, -0.3mm)
- Tyre cross-section: crescent or C-shape with 2-3mm wall thickness
- Add small lips on the inner edges that hook under the rim edge (retaining feature)

**Tread/grouser pattern:**
- Chevron pattern (V-shapes pointing in the direction of travel) for traction on loose surfaces
- Grouser height: 2-3mm for Phase 1, 4-5mm for Phase 2
- Grouser width: 3mm
- Spacing: 8-10mm between grousers
- For the Mars aesthetic: add small rectangular cleats in a pattern inspired by Curiosity's wheels

**Assembly:**
- Stretch the TPU tyre over the PETG wheel using clamps or an arbor press
- The interference fit holds the tyre in place
- For extra security: add 2-3 small M2 screws through the tyre sidewall into the rim
- Alternative: print the tyre with through-holes and use small bolts to mechanically lock to the hub

**TPU tyre dimensions (Phase 1):**
- Wheel rim OD: ~76mm
- Tyre ID: 75.7mm (0.3mm interference)
- Tyre OD: ~80mm (overall wheel diameter target)
- Tyre width: 32mm (matches wheel width)
- Grouser height: 2mm

**TPU tyre dimensions (Phase 2):**
- Wheel rim OD: ~190mm
- Tyre ID: 189.5mm (0.5mm interference)
- Tyre OD: ~200mm (overall wheel diameter target)
- Tyre width: 80mm
- Grouser height: 4-5mm

---

## 9. Time and Filament Estimates

These are rough estimates based on the print settings described above. Actual values depend on your specific slicer settings, printer speed calibration, and part geometry. Always slice the actual STL files for accurate numbers.

### Phase 1 (0.4 Scale Prototype)

| Part Category | Count | Est. Print Time Each | Est. Filament Each | Total Time | Total Filament |
|---------------|-------|---------------------|-------------------|------------|----------------|
| Chassis body segments | 2-3 | 6-8 hours | 60-80g | 16-24 hrs | 160-240g |
| Rocker arms | 2 | 2-3 hours | 25-35g | 4-6 hrs | 50-70g |
| Bogie arms | 2 | 1.5-2 hours | 15-25g | 3-4 hrs | 30-50g |
| Wheels (PETG hub+spokes) | 6 | 1.5-2 hours | 20-30g | 9-12 hrs | 120-180g |
| TPU tyres | 6 | 1-1.5 hours | 10-15g | 6-9 hrs | 60-90g |
| Differential bar | 1 | 1-1.5 hours | 15-20g | 1-1.5 hrs | 15-20g |
| Steering brackets | 4 | 0.5-1 hour | 8-12g | 2-4 hrs | 32-48g |
| Motor mounts | 6 | 0.5-1 hour | 8-12g | 3-6 hrs | 48-72g |
| Pivot brackets + misc | 6 | 0.5-1 hour | 8-12g | 3-6 hrs | 48-72g |
| **Phase 1 Total** | **~35 prints** | | | **~47-73 hrs** | **~560-840g** |

**Phase 1 filament summary:**
- PETG: ~500-750g (roughly 1 spool)
- TPU: ~60-90g (fraction of a spool)
- Total: approximately 1 spool PETG + partial spool TPU
- Allow 20-30% extra for failed prints and test pieces: **~1 kg PETG + 0.25 kg TPU**

### Phase 2 (Full Scale)

| Part Category | Count | Est. Print Time Each | Est. Filament Each | Total Time | Total Filament |
|---------------|-------|---------------------|-------------------|------------|----------------|
| Top deck panels | 15-20 | 3-5 hours | 40-60g | 60-100 hrs | 700-1200g |
| Side panels | 10-12 | 2-4 hours | 30-50g | 24-48 hrs | 360-600g |
| Electronics bay panels | 6-8 | 2-3 hours | 25-40g | 14-24 hrs | 175-320g |
| Rocker arms (segmented) | 6-8 | 3-5 hours | 50-80g | 24-40 hrs | 400-640g |
| Bogie arms (segmented) | 4 | 2-4 hours | 40-60g | 8-16 hrs | 160-240g |
| Wheels (PETG, 2 halves each) | 12 | 3-5 hours | 50-80g | 36-60 hrs | 600-960g |
| TPU tyres | 6 | 3-4 hours | 40-60g | 18-24 hrs | 240-360g |
| Mast sections | 3-4 | 2-3 hours | 30-50g | 6-12 hrs | 120-200g |
| Arm segments | 12 | 1-2 hours | 15-25g | 12-24 hrs | 180-300g |
| Fridge housing | 4 | 3-5 hours | 50-70g | 12-20 hrs | 200-280g |
| Camera mounts + misc | 10-15 | 0.5-1 hour | 5-15g | 5-15 hrs | 75-225g |
| **Phase 2 Total** | **~90-110 prints** | | | **~220-380 hrs** | **~3.2-5.3 kg** |

**Phase 2 filament summary:**
- PETG: ~3.0-5.0 kg (3-5 spools)
- TPU: ~240-360g (roughly 0.5 spool)
- Total: approximately 4-5 spools PETG + 0.5 spool TPU
- Allow 20% extra for failures: **~4-6 kg PETG + 0.5 kg TPU**

### Print Time Reality Check

At an average of 6-8 hours of Ender 3 printing per day (practical limit with setup, bed cleaning, and overnight prints):

| Phase | Total Hours | Calendar Days | Approx Calendar Time |
|-------|-------------|---------------|---------------------|
| Phase 1 | 50-75 hrs | 7-12 days | 1.5-2 weeks |
| Phase 2 | 220-380 hrs | 30-55 days | 5-8 weeks |

These align with community experience: ExoMy (a smaller rover) takes about 2 weeks of printing for structural parts using 1.5 kg of filament. Sawppy (closer in size to Phase 1) uses about 3 kg / 3 spools.

---

## 10. Ender 3 Specific Tips

### PETG on Ender 3

1. **Use painter's tape or PEI sheet** — PETG bonds aggressively to bare glass beds. It can rip chunks of glass off when removing prints. Blue painter's tape or a PEI spring steel sheet prevents this.
2. **Bowden tube limit** — the stock PTFE Bowden tube degrades above 240C. Stay at 230-235C for longevity. If you print a lot of PETG, consider upgrading to a Capricorn tube (rated to 260C) or an all-metal hotend.
3. **Z-offset** — PETG needs slightly more Z-offset than PLA. If the first layer is too squished, PETG will stick permanently to the bed surface.
4. **Stringing** — PETG strings more than PLA. Use 5-6mm retraction at 35-40mm/s, travel speed 150mm/s, and enable "wipe" in your slicer.
5. **Cooling** — PETG prints best with the part cooling fan at 30-50%. Too much cooling causes layer adhesion failure. Too little causes drooping on overhangs.
6. **Bed levelling** — critical for large parts. Level the bed before every print session. Consider installing a BLTouch/CRTouch for auto bed levelling if printing many large parts.

### TPU on Ender 3 (Bowden)

1. **Very slow** — 20-25mm/s maximum. The Bowden tube compresses TPU.
2. **Disable retraction** or use 0.5-1mm retraction max.
3. **Direct-drive conversion** recommended if doing extensive TPU printing (Micro Swiss, Creality Sprite, or printed direct-drive adapter).
4. **Dry filament** — TPU absorbs moisture rapidly. Store in a sealed bag with desiccant. Print from a dry box if possible.

### General Ender 3 Best Practices for This Project

- **Calibrate e-steps and flow rate** before starting structural prints
- **Print a temperature tower** for your specific PETG brand
- **Use OctoPrint or similar** for remote monitoring (your rover project will involve hundreds of hours of printing)
- **Keep spare nozzles** — printing this much filament will wear nozzles; swap every 1-2 kg
- **Bed adhesion failures** waste the most time. Invest in proper bed surface preparation.

---

## 11. Reference Projects

These open-source rover builds informed this strategy:

- **Sawppy** (Roger Cheng): Quarter-scale Curiosity/Perseverance replica using 15mm aluminium extrusion + 3D printed connectors. ~3 kg filament total. PLA prototype reprinted in PETG. 3 perimeters, 0.3mm layers, 0.4mm nozzle. Wheels print outer-face-down, no supports.
- **ExoMy** (ESA): Fully 3D-printed Mars rover. 1.5 kg PLA, 0.15mm layers, 20% infill, 0.4mm nozzle. ~2 weeks print time. 392x300x420mm final size, 2.5 kg total weight. Designed to minimise support material.
- **JPL Open Source Rover**: Full-scale design using primarily COTS (off-the-shelf) parts with minimal 3D printing. Community has added 3D printed parts for customisation.
- **HowToMechatronics Perseverance Replica**: Arduino-based, 3D printed chassis with detailed cosmetic accuracy.

### Source Links

- [Sawppy the Rover - Hackaday.io](https://hackaday.io/project/158208-sawppy-the-rover)
- [Sawppy GitHub (STLs + docs)](https://github.com/Roger-random/Sawppy_Rover)
- [ExoMy - ESA](https://www.esa.int/Enabling_Support/Space_Engineering_Technology/3D_print_your_own_Mars_rover_with_ExoMy)
- [ExoMy GitHub (3D printing wiki)](https://github.com/esa-prl/ExoMy/wiki/3D-Printing)
- [JPL Open Source Rover](https://github.com/nasa-jpl/open-source-rover)
- [DIY Mars Perseverance Replica](https://howtomechatronics.com/projects/diy-mars-perseverance-rover-replica-with-arduino/)
- [PETG vs PLA Strength Comparison - Ultimaker](https://ultimaker.com/learn/petg-vs-pla-vs-abs-3d-printing-strength-comparison/)
- [Heat-Set Insert Best Practices - CNC Kitchen](https://www.cnckitchen.com/blog/tipps-amp-tricks-fr-gewindeeinstze-im-3d-druck-3awey)
- [How To Split and Join Large 3D Prints - DigiKey](https://www.digikey.com/en/maker/blogs/2024/how-to-split-and-join-large-3d-prints)
- [Infill Patterns - Prusa Knowledge Base](https://help.prusa3d.com/article/infill-patterns_177130)
- [Ender 3 PETG Settings - Creality](https://www.creality.com/blog/how-to-get-perfect-petg-prints-on-ender-3-correct-settings-first)
- [Mastering Infill Patterns - Ultimaker](https://ultimaker.com/learn/mastering-3d-printing-infill-patterns-from-gyroid-to-lightning/)
