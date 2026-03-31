# WHL-04: Wheel Assembly — Master Document

**Assembly**: Curiosity V5 Wheel (Tread + Hub + 6x Spoke)
**Assembly .f3d**: `cad/reference-wheels/CuriosityWheelV5_Assembly.f3d`
**Baseline .f3d**: `cad/reference-wheels/CuriosityWheelV5_Approved_Baseline.f3d`
**Date**: 2026-03-27
**Status**: Design analysis complete — assembly method TBD

---

## 1. Assembly Overview

The Curiosity V5 wheel consists of three part types assembled into a single rotating unit:

| Part | Qty | Document | Description |
|------|-----|----------|-------------|
| Tread | 1 | WHL-01 | Outer cylindrical drum with chevron grousers |
| Hub | 1 | WHL-02 | Central disc with axle bore and bolt holes |
| Spoke | 6 | WHL-03 | S-curve flexures connecting hub to tread |

### 1.1 Full-Scale Dimensions

| Parameter | Value |
|-----------|-------|
| Overall OD | 500.0 mm |
| Overall width | 404.0 mm |
| Total mass (real rover) | ~7.9 kg aluminium + titanium |
| Total mass (0.4x PLA est.) | ~40-60g at 20% infill |

### 1.2 Assembly Files

| File | Purpose |
|------|---------|
| `CuriosityWheelV5_Approved_Baseline.f3d` | Parametric source — all 3 part types with full design history |
| `CuriosityWheelV5_Assembly.f3d` | Assembly — 8 components (Tread + Hub + 6x Spoke) correctly positioned |
| `components/Tread.f3d` | Individual part .f3d |
| `components/Hub.f3d` | Individual part .f3d |
| `components/Spoke.f3d` | Individual part .f3d (one copy; pattern 6x in assembly) |

## 2. How the Real Curiosity Wheel is Assembled

Understanding the real assembly is essential for designing a practical printed version.

### 2.1 Real Rover Assembly Sequence (Ref-1, Ref-2, Ref-3)

1. **Tread ring machined** from single 7075-T7351 aluminium billet — includes outer skin, chevron grousers, internal stiffening ring, and edge rims (all one piece)
2. **Hub disc machined** separately — central bore, reinforcing ribs, bolt bosses
3. **Six titanium spokes formed/machined** individually — bent to S-curve compound profile
4. **Spokes bolted to hub first** — 2x M5 SHCS per spoke at hub-end flanges (r = 80.3 mm)
5. **Hub+spoke subassembly inserted into tread ring** — spoke tips positioned against inner bore surface and stiffening ring
6. **Spoke tips bolted to tread stiffening ring** — 2x M5 SHCS per spoke at tread-end flanges (r = 227-229 mm)
7. **Total fasteners per wheel**: 24x M5 SHCS (4 per spoke) + hub bore fasteners

### 2.2 Key Real-Rover Design Features

| Feature | Detail | Relevance to Our Build |
|---------|--------|----------------------|
| Stiffening ring inside tread | Provides threaded bosses for spoke bolts | We have no internal structure — tread wall is solid |
| Titanium spoke flex | Spokes act as springs, absorbing impacts | PLA is rigid — no flex behaviour |
| Machined bearing surfaces | Spoke flanges mate precisely to hub bosses | FDM surfaces are rough — tolerance is ~0.2-0.4 mm |
| 24x M5 SHCS | Positive mechanical attachment | At 0.4x this becomes M2 territory — very small |
| Splined hub bore | Locks to drive actuator | We use 608ZZ bearing + 8mm axle |

## 3. Interface Analysis

### 3.1 Spoke-to-Tread Interface

```
CROSS-SECTION (radial direction, not to scale):

    Tread outer surface (grousers)
    ================================
    |        Tread wall            |
    |   r=250  ←  39.6mm  → r=210 |
    |                              |
    |   ┌──── Spoke tip ────┐     |
    |   │  extends to r=224 │     |
    |   │  2x SHCS here     │     |
    |   └───────────────────┘     |
    |        Inner bore            |
    ================================
             r = 210.4 mm
```

- **Overlap**: 13.7 mm (spoke tip at r=224 into tread wall starting at r=210.4)
- **Contact type**: Radial bearing surface (spoke tip presses outward against tread)
- **Fastening (real)**: 2x M5 SHCS through spoke flange into stiffening ring
- **No alignment features**: Tread inner bore is smooth — no slots, channels, or keyways
- **Angular location**: Determined solely by bolt hole positions in stiffening ring

### 3.2 Spoke-to-Hub Interface

```
HUB DISC (viewed from spoke side):

         ┌─────────────────────┐
        /   Spoke root flange   \
       /     r = 73.5 mm         \
      │   ┌─ Hub boss ─┐          │
      │   │  2x SHCS    │         │
      │   │  r = 80.3   │         │
      │   └─────────────┘         │
       \     Hub OD = 87.5       /
        \_______________________/
```

- **Overlap**: 14.0 mm (hub edge at r=87.5 over spoke root at r=73.5)
- **Contact type**: Axial bearing surface (spoke root flange lies flat on hub face)
- **Fastening (real)**: 2x M5 SHCS through spoke flange into hub boss
- **Alignment**: Hub has raised bosses that locate spoke roots

## 4. Assembly Feasibility for 3D Printing

### 4.1 The Core Problem

The GrabCAD model was designed for CNC-machined metal parts with bolted joints. For 3D printed PLA at 0.4x scale:

1. **No alignment features** — spokes have no positive location on either tread or hub
2. **No fastener access** — M5 bolts become M2 at 0.4x; the screw positions are buried inside the tread wall
3. **Overlap geometry** — spoke tips extend INTO the tread wall; they cannot simply be placed against the surface
4. **PLA bonding** — CA glue on PLA-to-PLA is moderately strong but has no shear resistance without mechanical interlock
5. **Assembly sequence** — cannot insert 6 spokes + hub into the tread ring simultaneously without fixturing

### 4.2 Printing Strategy Options

#### Option A: Single-Piece Print (RECOMMENDED for Phase 1)
Print the entire wheel as one STL — hub, spokes, and tread combined into a single body.

| Pro | Con |
|-----|-----|
| No assembly required | Cannot replace individual parts |
| Strongest structure (integral PLA) | Must reprint entire wheel if one part breaks |
| No alignment issues | Large print — may need splitting for bed fit |
| Proven approach (Sawppy, OSR) | No spoke compliance (rigid PLA) |
| Simplest workflow | Single material only |

**Implementation**: Combine all bodies in Fusion 360, export as single STL, scale to 0.4x.

This is how every successful hobbyist Mars rover wheel has been made (Ref-4, Ref-5). At 0.4x scale, the structural arguments for separate parts do not apply — the whole wheel weighs ~40-60g and carries ~200g of rover load. A single-piece PLA print is more than strong enough.

#### Option B: Two-Piece (Hub+Spokes Combined, Tread Separate)
Print hub and spokes as one piece. Tread is separate and slides over the spoke assembly.

| Pro | Con |
|-----|-----|
| Can use TPU tread (future) | Requires spoke tips to seat into tread |
| Replaceable tread | Needs alignment method (pins/slots) |
| Hub+spoke is one print | Tread must slide over curved spokes |

**Implementation**: Requires modifying the tread inner surface to add 6 slots/pockets matching the spoke tip profiles. Also requires the tread to be wider than the spoke assembly to slide on axially.

**Feasibility**: Moderate — the spoke tips are compound-curved, making slot geometry complex. The 13.7mm overlap must become a designed slot, not a vague overlap zone.

#### Option C: Three-Piece (All Separate)
Print tread, hub, and 6 spokes individually. Assemble with adhesive + pins.

| Pro | Con |
|-----|-----|
| Individual part replacement | Complex assembly with 8 parts per wheel |
| Each part fits CTC Bizer easily | Weak joints (PLA glue bond only) |
| Can optimise print orientation per part | No alignment features in current design |
| True to original construction method | Requires jig/fixture for alignment |

**Implementation**: Requires designing:
- 6 pockets on hub face matching spoke root flange profiles
- 6 pockets on tread inner surface matching spoke tip profiles
- Alignment pins or keyways at each joint
- Assembly jig to hold all parts during bonding

**Feasibility**: High effort. The spoke-to-tread interface is the hardest problem — there are no visible marks on the tread inner surface indicating where each spoke goes. An assembly jig that clocks all 6 spokes at 60-degree intervals while bonding to the tread would be required.

#### Option D: Hybrid (Modified Single-Piece Wheel + Bolt-On Hub)
Print the tread + spokes as one piece. Hub is separate and bolts on via the existing 6x 6mm bolt holes.

| Pro | Con |
|-----|-----|
| Hub is replaceable/serviceable | Spoke-tread interface is still integral |
| Hub can be adapted for different axle types | Bolt hole alignment is critical |
| Natural separation point (bolts already designed) | Small bolts (M2.4 at 0.4x) |
| Existing bolt pattern provides positive location | — |

**Implementation**: In Fusion 360, combine Tread + 6 Spokes into one body. Keep Hub separate. Add matching bolt holes. Scale to 0.4x. Print as 2 parts per wheel.

**Feasibility**: Good. This follows the real rover's design intent — the hub IS the separable component. The 6 bolt holes provide perfect alignment. Hub can be designed with appropriate axle bore for our 608ZZ + 8mm setup.

### 4.3 Recommendation

**Phase 1**: Start with **Option A (single-piece)** for the first prints. This is proven, fast, and eliminates all assembly risk. Focus on getting a rolling rover, not on part serviceability.

**Phase 1.5**: If the single-piece wheel works, try **Option D (tread+spokes integral, hub bolt-on)** as an upgrade. This gives us a serviceable axle interface without the complexity of all-separate parts.

**Phase 2**: At full scale with stronger materials (PETG/ASA), **Option C (all separate)** becomes viable with designed joints and proper fasteners.

## 5. Assembly Sequence (for Option A — Single Piece)

1. Open `CuriosityWheelV5_Approved_Baseline.f3d` in Fusion 360
2. Combine all bodies (Tread Body1 + Hub Body1 + 6x Spoke Body1) using Combine → Join
3. Delete/hide minor bodies (Body40, Body69, etc.) and all screw occurrences
4. Export combined body as STL
5. Scale to 0.4x using `scale_stl` MCP tool or Cura scale function
6. Verify bed fit: 200mm OD x 162mm width → requires segmenting or 0.3x scale
7. Slice in Cura → GPX → x3g → print

## 6. Assembly Sequence (for Option D — Integral Tread+Spokes, Bolt-On Hub)

1. In Fusion 360: Combine Tread Body1 + 6x Spoke Body1 (NOT Hub)
2. Add 6x bolt holes to spoke root flanges matching hub bolt pattern (73mm BCD, 6mm dia)
3. Export tread+spoke body as STL; export hub as separate STL
4. Scale both to 0.4x
5. Print both parts
6. Install heat-set inserts into hub bolt holes (M2.4 at 0.4x, or design for M3 with adjusted BCD)
7. Bolt tread+spoke assembly to hub with 6x button head screws
8. Install 608ZZ bearing into hub bore, insert 8mm axle

## 7. Open Questions

| # | Question | Impact | Notes |
|---|----------|--------|-------|
| 1 | Single-piece or bolt-on hub? | Determines all downstream work | Recommend single-piece for Phase 1 first prints |
| 2 | Scale factor — 0.4x or 0.3x? | 0.4x tread doesn't fit CTC Bizer bed | 0.3x = 150mm OD, fits bed standing up |
| 3 | Print orientation for single-piece? | Quality vs support material | Spoke-side down likely best |
| 4 | How to integrate our 608ZZ + 8mm axle with 52mm hub bore? | Adapter sleeve needed | Could print adapter or modify hub bore |
| 5 | Retain decorative detail or simplify for FDM? | Print quality at small scale | Rivet details won't print at 0.4x |
| 6 | Spoke tip modification for Option D? | Bolt holes in spoke flanges | Only needed if going bolt-on hub route |

## 8. Comparison with Hobbyist Rover Wheels

| Project | Wheel Approach | Scale | Material | Ref |
|---------|---------------|-------|----------|-----|
| **Sawppy** | Single-piece print (integral) | ~0.4x | PLA/PETG | Ref-4 |
| **JPL Open Source Rover** | Commodity wheels + Sonic Hub adapter | N/A | Rubber + aluminium | Ref-6 |
| **OpenPerseverance** | 4-piece (Tire + Rim + 2x Holder) | ~0.3x | PLA | Ref-7 |
| **Mars Rovers Studio** | CNC aluminium spokes, bolted | 1:2 | Aluminium | Ref-3 |
| **HowToMechatronics** | 3D printed + bolted | ~0.3x | PLA + bolts | Ref-8 |
| **Our V5** | TBD (Options A-D above) | 0.4x | PLA (Phase 1) | This document |

## 9. References

| ID | Source | Content |
|----|--------|---------|
| Ref-1 | [NASA "Reinventing the Wheel"](https://www3.nasa.gov/specials/wheels/) | Official wheel anatomy and assembly |
| Ref-2 | [Planetary Society: Diagram of a Curiosity Wheel](https://www.planetary.org/space-images/diagram-of-a-curiosity-wheel) | Cross-section with stiffening ring |
| Ref-3 | [Mars Rovers Studio: Building and Testing](https://buymarsrovers.com/building-and-testing-the-wheel-skeleton-of-the-mars-perseverance-rover-replica.html) | 1:2 replica assembly sequence |
| Ref-4 | [Sawppy: Rover Wheel Design for 3D Printing](https://newscrewdriver.com/2018/05/10/sawppy-feet-1-0-rover-wheel-design-for-3d-printing/) | Single-piece FDM wheel philosophy |
| Ref-5 | [Micro Sawppy Beta 3 Wheel](https://newscrewdriver.com/2021/01/30/micro-sawppy-beta-3-wheel/) | Simplified small-scale approach |
| Ref-6 | [JPL Open Source Rover: Wheel Assembly](https://open-source-rover.readthedocs.io/en/stable/mechanical/wheel_assembly/index.html) | Multi-bolt hub for torque resistance |
| Ref-7 | OpenPerseverance project | 4-piece wheel design |
| Ref-8 | [HowToMechatronics: DIY Mars Perseverance](https://howtomechatronics.com/projects/diy-mars-perseverance-rover-replica-with-arduino/) | Printed + bolted approach |
| Ref-9 | [NASA 3D-DIC Paper (IEEE 2023)](https://ntrs.nasa.gov/api/citations/20220015213) | Flexure characterisation methodology |
| Ref-10 | [Emily Lakdawalla: Curiosity Wheel Damage](https://www.planetary.org/articles/08190630-curiosity-wheel-damage) | Stiffening ring role in structural integrity |
| Ref-11 | `docs/engineering/bolt-on-wheel-mounting-design.md` | Our 4x M3 BCD wheel-to-connector design |
| Ref-12 | EA-11 (3D Printing) | CTC Bizer specs, PLA settings, bed dimensions |
