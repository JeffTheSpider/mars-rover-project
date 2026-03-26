# Rocker-Bogie Suspension Design Research

**Date:** 2026-03-26
**Purpose:** Find open-source rocker-bogie designs to study and adapt components from.

---

## Our Current Suspension Specs

- 0.4 scale (body 440×260mm)
- 608ZZ bearings × 9 (2 rocker + 2 bogie + 1 diff pivot + 4 steering)
- 8mm steel rods as suspension arms, inserted into printed connectors
- Tube socket: 8.2mm bore, 15mm depth, M3 grub screw retention
- Through-bar differential mechanism (300mm 8mm steel rod)
- Track width 280mm, wheelbase 360mm
- N20 motors (12×10×24mm), SG90 servos

---

## Complete Suspension Systems Compared

### 1. Sawppy Rover ★★★ (MOST RELEVANT)
- **URL:** https://github.com/Roger-random/Sawppy_Rover
- **License:** MIT
- **Format:** Onshape + 23 STL files
- **Architecture:** 8mm steel shafts + 15mm aluminium extrusions + 608ZZ bearings (30!)
- **Differential:** Through-bar with turnbuckle ball joints (M3) connecting to rockers
- **Connectors:** Bolt clamp around 15mm extrusion, set screws in heat-set inserts
- **Key dimensions:** Diff bar 300mm, rocker pivot 84mm, bogie pivot 66.5mm, steering shaft 61mm, wheel axle 50mm

**CRITICAL LESSONS:**
1. **Diff bar BENT under load** — needed printed DiffBrace (upper + lower clamp). Our 8mm bar may have same issue.
2. **Heat-set insert variability** — different manufacturers = different bore sizes = widespread build failures. We must validate 4.8mm × 5.5mm spec with test print.
3. **E-clip shaft retention** as alternative to grub screws (more secure)
4. **Hex wrench shaft** variant prevents rotation (clever)

### 2. jakkra Mars-Rover ★★★
- **URL:** https://github.com/jakkra/Mars-Rover
- **License:** MIT
- **Format:** Fusion 360 .f3z/.f3d (directly importable!)
- **Architecture:** 25mm PVC pipes + 608ZZ + SKF 6005 bearings
- **Motors:** 12V 60RPM DC motors, MG996R servos
- **Value:** Import .f3z as reference overlay in our Fusion 360 assembly

### 3. NASA-JPL Open Source Rover ★★☆
- **URL:** https://github.com/nasa-jpl/open-source-rover
- **License:** Apache 2.0
- **Format:** Onshape
- **Architecture:** goRail aluminium extrusions, flanged bearings (8×14×5mm, NOT 608ZZ)
- **Differential:** Pivot bar + 45° brackets + turnbuckles
- **Value:** Best documentation of any project. Study geometry ratios and bogie joint spacing.
- **Key technique:** Asymmetric spacers (4mm + 6mm) on bogie pivot prevent lateral flex

### 4. ESA ExoMy ★☆☆
- **URL:** https://github.com/esa-prl/ExoMy
- **License:** GPL-3.0
- **Architecture:** Triple-bogie (NOT rocker-bogie), fully 3D-printed, servo-direct-drive
- **Value:** Different suspension philosophy. Study their 3 steering modes (same as ours).

### 5. HowToMechatronics Perseverance ★★☆
- **URL:** https://howtomechatronics.com/projects/diy-mars-perseverance-rover-replica-with-arduino/
- **License:** Paid STL ($3), personal use only
- **Architecture:** 20mm aluminium profiles, M8 bolt pivots, rod-end ball joints
- **Key technique:** Rod-end ball joints on differential — elegant, adjustable
- **Key dimension:** 20mm gap between diff link and rod end = level chassis

---

## Differential Mechanism Comparison

| Type | Project | Our Compatibility | Notes |
|------|---------|-------------------|-------|
| **Through-bar + turnbuckle** | Sawppy | HIGH — same bar, different links | Bar bends! Need brace. |
| **Through-bar direct coupling** | Our design | Current approach | Simplest, but must prevent bending |
| **Rod-end ball joints** | HowToMechatronics | Possible upgrade | More robust, adjustable |
| **45° bracket + turnbuckle** | JPL OSR | LOW — aluminium extrusion based | Study geometry only |
| **Bevel gear** | Real Spirit/Opportunity | LOW — complex to print | Phase 3 maybe |
| **Magnetic pivot** | Morethan3D | NO — not robust for outdoor | Creative but impractical |
| **No differential** | Fishbone Mini Rover | Fallback only | Body tilts uncontrolled |

---

## Connector Design Comparison

| Approach | Project | Tube/Rod | Retention | Our Assessment |
|----------|---------|----------|-----------|---------------|
| **Extrusion bolt clamp** | Sawppy | 15mm Al extrusion | M3 bolts + channel nuts | Different from ours, very strong |
| **Socket + grub screw** | Our design | 8mm steel rod | M3 grub in heat-set insert | Good compromise, validate with test print |
| **PVC pipe + screw** | jakkra | 25mm PVC | Screw-through | Too large for 0.4 scale |
| **Bolt-through pivot** | Fishbone/ROVER-X | M3/M5 screw | Nylon lock nut | Too simple, will wear |
| **Set screw + E-clip** | Sawppy (shafts) | 8mm shaft | Set screw + E-clip groove | Consider as alternative to grub screw |

---

## Steering Knuckle Comparison

| Design | Bearings | Shaft | Servo Linkage | Our Assessment |
|--------|----------|-------|---------------|---------------|
| **Sawppy** | 2× 608ZZ (top+bottom) | 8mm | Direct servo on shaft | More robust than ours (dual bearing) |
| **jakkra** | 608ZZ + SKF 6005 | PVC | Servo arm direct | Two different bearing types |
| **JPL OSR** | Flanged 8×14×5mm | goRail | Servo through bracket | Different bearing class |
| **Our design** | 1× 608ZZ | 8mm | Horn link 4-bar (EA-27) | Unique linkage, consider dual bearing |

**Note:** Sawppy uses TWO 608ZZ bearings per steering pivot (top + bottom). We use ONE. Consider whether we need dual bearings for robustness.

---

## Parts We Should Adapt From Other Projects

1. **Sawppy DiffBrace** — Add printed brace around our diff bar (it WILL bend)
2. **JPL OSR asymmetric spacers** — Prevent lateral flex on bogie pivot
3. **Sawppy E-clip retention** — Alternative to grub screws (more secure)
4. **jakkra .f3z import** — Visual reference overlay in our Fusion 360 assembly
5. **Sawppy shaft proportions** — Cross-reference our rod lengths

## Parts We Should NOT Adapt

1. Sawppy extrusion clamps (different structural approach)
2. ExoMy triple-bogie (different suspension type)
3. JPL OSR aluminium construction (too expensive)
4. Magnetic bearings (not robust)

---

## Key Sources

- Sawppy GitHub: https://github.com/Roger-random/Sawppy_Rover
- Sawppy Diff Bar Brace: https://newscrewdriver.com/2018/06/01/differential-bar-brace-completes-mechanical-assembly-of-sawppy-rover/
- Sawppy Heat-Set Issues: https://newscrewdriver.com/2020/11/25/sawppy-issue-heat-set-insert-shaft-coupling/
- Sawppy Suspension Geometry: https://newscrewdriver.com/2018/05/24/copying-curiosity-rover-suspension-geometry-for-sawppy-the-rover/
- jakkra Mars-Rover: https://github.com/jakkra/Mars-Rover
- JPL OSR Docs: https://open-source-rover.readthedocs.io/en/latest/mechanical/rocker_bogie/
- HowToMechatronics: https://howtomechatronics.com/projects/diy-mars-perseverance-rover-replica-with-arduino/
- ExoMy: https://github.com/esa-prl/ExoMy
- Fishbone Mini Rover: https://www.printables.com/model/164147
- ROVER-X: https://hackaday.io/project/170953-rover-x
- Rover-One (Fusion 360): https://github.com/chetanborse1999/Rover-One
