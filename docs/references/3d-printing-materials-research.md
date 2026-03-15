# 3D Printing Materials & Techniques Research

**Date**: 2026-03-15
**Source**: Research agent — CNC Kitchen data, community sources

## CNC Kitchen Prusament Test Data (Quantitative)

| Property | PLA | PETG | ASA | ABS |
|---|---|---|---|---|
| Static strength (horizontal) | 73 kg | 55 kg | 57 kg | ~53 kg |
| Layer adhesion (vertical, % of horiz.) | 40 kg (55%) | 25 kg (46%) | 17 kg (29%) | ~15 kg (~28%) |
| Stiffness (bending modulus) | 3,300 MPa | 1,900 MPa | 2,300 MPa | 2,100 MPa |
| Impact strength (IZOD) | 5 kJ/m2 | 8.6 kJ/m2 | 18 kJ/m2 | ~16 kJ/m2 |
| Heat deflection | ~60C | ~80C | ~110C | ~100C |
| UV resistance | Poor | Moderate | Excellent (10x ABS) | Poor |

## Heat-Set Insert Data (CNC Kitchen Testing)

- M3 insert pull-out in PETG: **800-1200N** (80-120 kg) with proper hole sizing and 4+ walls
- Even weakest orientation (side-inserted, 2 walls): >200N
- CNC Kitchen M3 x 5.7mm Standard inserts: most widely tested/documented
- Recommended hole: 4.2mm (vertical), 4.25mm (horizontal), 4.1mm (45-degree)
- **Note**: EA-11 specifies 4.8mm for 5.7mm OD inserts — actual hole size depends on specific insert brand. Always print a test block first.

## Phase 2 Reinforcement Options

| Method | Application | Difficulty |
|---|---|---|
| Carbon fiber strips (1mm x 10mm pultruded) | Epoxy-bonded to rocker/bogie arms — massively increases bending stiffness | Easy |
| Fiberglass tape (25mm woven) | Wrapped around pivot joints with epoxy — increases shear strength | Moderate |
| M3 threaded rod | Through-arm tensile core | Easy |

## UV Protection Layered Approach

1. Sand with 220 grit
2. Spray primer: Rust-Oleum 2X Ultra Cover Primer
3. Spray paint: 2-3 thin coats Rust-Oleum 2X Ultra Cover
4. Clear coat: Rust-Oleum Crystal Clear matte/satin, 2 coats (primary UV barrier)
- Total cost: ~15-20 GBP

**XTC-3D note**: Self-leveling epoxy fills layer lines but is NOT UV stable — must apply clear coat over it.

**ASA smoothing**: MEK (methyl ethyl ketone) works but hazardous. Spray paint + clear coat achieves better results with less risk.

## Slicer Tips

- Use modifier meshes in Cura/PrusaSlicer to set 100% infill in cylinders around insert holes while keeping rest at 50%
- Tree supports (Cura) produce less scarring on ASA than linear supports
- 0.2mm support interface gap for clean removal

## Sources

- [CNC Kitchen: Comparing PLA, PETG & ASA](https://www.cnckitchen.com/blog/comparing-pla-petg-amp-asa-feat-prusament)
- [CNC Kitchen: Heat-Set Insert Tips & Tricks](https://www.cnckitchen.com/blog/tipps-amp-tricks-fr-gewindeeinstze-im-3d-druck-3awey)
- [Filamentive: UV Resistant Filament UK Guide 2025](https://www.filamentive.com/outdoor-3d-printing-2025-uv-resistant-filament-uk-guide/)
- [Polymaker Wiki: Print Orientation Affects Strength](https://wiki.polymaker.com/the-basics/fun-3d-printing-facts/print-orientation-affects-strength)
- [Wevolver: ASA vs PETG Comparison](https://www.wevolver.com/article/asa-vs-petg-a-comprehensive-comparison-and-guide)
- [3DPUT: PLA vs PETG vs ASA Strength Testing](https://3dput.com/pla-vs-petg-vs-asa-which-filament-is-actually-strongest/)
