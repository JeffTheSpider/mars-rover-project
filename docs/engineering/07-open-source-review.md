# Engineering Analysis 07: Open Source Rover Project Review

**Document**: EA-07
**Date**: 2026-03-15
**Purpose**: Evaluate existing open-source Mars rover designs to identify the best baseline for Charlie's rover, avoiding reinventing proven solutions.

---

## 1. Projects Evaluated

Three major open-source rover projects were analysed:

| Project | Organisation | Year | Community Size | Active? |
|---------|-------------|------|----------------|---------|
| JPL Open Source Rover (OSR) | NASA JPL | 2018 | Large (1.8k+ GitHub stars) | Yes |
| Sawppy | Roger Cheng (individual) | 2018 | Medium (400+ stars) | Yes |
| ExoMy | ESA Planetary Robotics Lab | 2020 | Medium (300+ stars) | Archived (community fork active) |

---

## 2. NASA JPL Open Source Rover

### Overview
Scaled-down version of the actual Mars rover design, created by NASA's Jet Propulsion Laboratory as an educational outreach project. Uses Consumer Off-The-Shelf (COTS) parts exclusively.

### Technical Specifications

| Parameter | Value |
|-----------|-------|
| Dimensions | ~60cm L x 45cm W x 40cm H (approx.) |
| Weight | ~11 kg |
| Wheels | 6, individually driven |
| Suspension | Rocker-bogie with differential pivot bar |
| Steering | 4-corner Ackermann steering |
| Motors | 10 total (6 drive + 4 steering) |
| Controller | Raspberry Pi |
| Motor control | RoboClaw 2x7A motor controllers |
| Frame | Custom machined aluminium + COTS brackets |
| Communication | WiFi (gamepad via Raspberry Pi) |

### Strengths
- **Authentic NASA design** — directly derived from flight rover geometry
- **Excellent documentation** — step-by-step build guide with photos
- **Proven mechanical design** — hundreds of successful builds worldwide
- **6-wheel Ackermann steering** — mathematically correct steering geometry
- **ROS2 support** — community-contributed ROS2 packages available
- **Readthedocs documentation** — comprehensive online build guide

### Weaknesses
- **Cost: ~$2,500-3,000** — significantly over our budget
- **Build time: ~200 person-hours** — substantial commitment
- **Custom machining required** — drill press and Dremel minimum, some parts need precise machining
- **RoboClaw motor controllers** — expensive (~$80 each, need 5)
- **Heavy aluminium construction** — not easily modified or lightened
- **No 3D printing focus** — designed around machined metal and COTS brackets

### Relevance to Our Project
The JPL OSR provides the gold standard reference geometry for rocker-bogie proportions and steering kinematics. However, its cost and metal-first construction approach don't align with our phased 3D-print-to-metal strategy. We should study its geometry ratios and steering math but not directly follow its build process.

---

## 3. Sawppy Rover

### Overview
Created by Roger Cheng as a cost-reduced alternative to the JPL OSR. Uses 15x15mm aluminium extrusion for structure with 3D printed joints. Specifically designed for individual hobbyists.

### Technical Specifications

| Parameter | Value |
|-----------|-------|
| Dimensions | ~52cm L x 38cm W x 30cm H |
| Weight | ~5-7 kg (estimated) |
| Wheels | 6, individually driven |
| Suspension | Rocker-bogie with differential pivot |
| Steering | 4-corner steering (simplified) |
| Motors | 10x LewanSoul LX-16A serial bus servos |
| Controller | Various (Arduino, ESP32, Raspberry Pi) |
| Frame | 15x15mm Misumi HFS3 aluminium extrusion + 3D printed connectors |
| Communication | WiFi/Serial depending on controller |
| Fasteners | M3 heat-set inserts into 3D printed parts |

### Strengths
- **Cost: <$500** — fits our Phase 1 budget perfectly
- **3D print friendly** — designed around printed connectors on extrusion
- **Modular extrusion frame** — easy to modify, extend, and strengthen
- **Excellent documentation** — detailed build logs and design rationale
- **Heat-set inserts** — robust threaded connections in printed plastic
- **Multiple controller options** — documented with Arduino, ESP32, and Pi
- **Active community** — ongoing development, multiple forks and variants
- **Well-documented design decisions** — Roger explains every trade-off

### Weaknesses
- **Serial bus servos** — LX-16A servos lack torque for a heavier rover
- **Smaller scale** — designed as a desk/demo rover, not full-size utility
- **No payload capacity** — structure designed for self-weight only
- **Limited sensor integration** — no camera, LIDAR, or autonomy by default
- **No weatherproofing** — indoor/fair-weather use only
- **15x15mm extrusion** — too small for our 25-35kg rover (need 2020 minimum)

### Relevance to Our Project
Sawppy's construction method (aluminium extrusion skeleton + 3D printed connectors with heat-set inserts) is directly applicable to our Phase 2 design. The M3 heat-set insert approach is proven for rover-scale loads. However, we need to scale up the extrusion (15x15 → 2020 or 2040), use stronger motors, and add significant payload capacity.

---

## 4. ExoMy Rover

### Overview
Created by ESA's Planetary Robotics Laboratory as an educational platform. Designed to be almost entirely 3D printed, with a focus on accessibility and low cost.

### Technical Specifications

| Parameter | Value |
|-----------|-------|
| Dimensions | ~30cm L x 25cm W x 42cm H |
| Weight | ~2.5 kg |
| Wheels | 6, individually driven |
| Suspension | Triple bogie (simplified rocker-bogie variant) |
| Steering | 6-wheel steering (all wheels steerable) |
| Motors | 12x hobby servos (6 drive + 6 steering) |
| Controller | Raspberry Pi |
| Frame | Almost entirely 3D printed (PLA) |
| Communication | WiFi (web interface) |
| Print time | ~2 weeks of continuous printing |

### Strengths
- **Cost: ~500** — within budget
- **Almost entirely 3D printed** — minimal non-printed parts
- **6-wheel steering** — all wheels steerable, maximum manoeuvrability
- **Triple bogie suspension** — simplified but functional suspension
- **ESA pedigree** — designed by actual planetary robotics engineers
- **ROS support** — designed with ROS integration in mind
- **Customisable face** — fun aesthetic touches (smiley face, hat)
- **Step-by-step wiki** — detailed assembly guide

### Weaknesses
- **Very small scale** — only 42cm tall, toy-sized
- **PLA structure** — brittle, poor outdoor durability
- **Hobby servos** — very low torque, not suitable for scaling up
- **No payload capacity** — structural PLA can't support additional weight
- **Triple bogie** — simpler than true rocker-bogie, less obstacle climbing ability
- **Archived repository** — original ESA repo archived, community fork continues
- **No differential bar** — uses a simpler linkage than true rocker-bogie

### Relevance to Our Project
ExoMy demonstrates that a functional rover can be almost entirely 3D printed, validating our Phase 1 approach. Its 6-wheel steering concept (all wheels steerable) is interesting but adds complexity and cost (12 motors vs 10). The triple bogie is simpler than true rocker-bogie — worth considering if the full rocker-bogie proves too complex at scale.

---

## 5. Comparison Matrix

| Criterion | Weight | JPL OSR | Sawppy | ExoMy |
|-----------|--------|---------|--------|-------|
| **Cost** | 20% | 2/10 ($2,500+) | 8/10 (<$500) | 7/10 (~$500) |
| **3D Print Suitability** | 15% | 3/10 (metal-first) | 7/10 (hybrid) | 9/10 (almost all printed) |
| **Scalability to Our Size** | 20% | 7/10 (proven at scale) | 6/10 (needs scaling up) | 3/10 (toy scale, not designed to scale) |
| **Suspension Quality** | 15% | 10/10 (authentic NASA) | 8/10 (faithful reproduction) | 5/10 (simplified triple bogie) |
| **Documentation** | 10% | 9/10 (professional) | 8/10 (excellent blog) | 7/10 (wiki format) |
| **Payload Capacity** | 10% | 6/10 (rigid but heavy) | 4/10 (light duty) | 2/10 (self-weight only) |
| **Community / Ecosystem** | 10% | 8/10 (NASA backing) | 7/10 (active individual) | 5/10 (archived, forks) |
| **Weighted Score** | 100% | **5.65** | **6.65** | **5.10** |

---

## 6. Decision & Recommendation

### Recommended Approach: Sawppy-Inspired Hybrid

**Base our design on Sawppy's construction philosophy, with JPL OSR's geometry ratios and our own custom scaling.**

Rationale:

1. **Construction method from Sawppy**: Aluminium extrusion skeleton (scaled up to 2020/2040) with 3D printed connectors using M3 heat-set inserts. This is proven, modular, and scales well.

2. **Suspension geometry from JPL OSR**: Use JPL's authentic rocker-bogie proportions and differential bar design. Their geometry is derived from actual Mars rover data.

3. **All-printed Phase 1 from ExoMy**: Phase 1 prototype can be almost entirely 3D printed (like ExoMy), validating the design before committing to extrusion.

4. **Custom scaling and features**: None of these projects include our feature set (fridge, solar, arms, AI, etc.), so the body, payload bay, and electronics integration will be entirely custom.

### What We Borrow from Each

| From JPL OSR | From Sawppy | From ExoMy |
|-------------|-------------|------------|
| Rocker-bogie geometry ratios | Extrusion + 3D print construction | All-printed prototype approach |
| Differential bar angles | M3 heat-set insert joints | 6-wheel steering option (evaluated) |
| Ackermann steering math | Bill of materials philosophy | ROS integration patterns |
| Wheel cleat/grouser design | Cost-reduction strategies | Customisable aesthetics |

### What We Design Custom

- Body frame sized for coffee table dimensions (1100x650mm)
- Payload bay (electronics, fridge, batteries)
- Solar panel folding mechanism
- Robotic arm mounts and kinematics
- Camera mast with pan-tilt
- Weatherproofing (Phase 3)
- All software (ROS2 + PWA + ESP32 firmware)

---

## 7. References

- [NASA JPL Open Source Rover — GitHub](https://github.com/nasa-jpl/open-source-rover)
- [JPL OSR Build Documentation](https://open-source-rover.readthedocs.io/en/stable/)
- [NASA Robotics Alliance — Build an Open Source Rover](https://robotics.nasa.gov/build-an-open-source-rover/)
- [Sawppy the Rover — GitHub](https://github.com/Roger-random/Sawppy_Rover)
- [Sawppy — Hackaday.io](https://hackaday.io/project/158208-sawppy-the-rover)
- [ExoMy — ESA GitHub](https://github.com/esa-prl/ExoMy)
- [ESA — 3D Print Your Own Mars Rover with ExoMy](https://www.esa.int/Enabling_Support/Space_Engineering_Technology/3D_print_your_own_Mars_rover_with_ExoMy)
- [ExoMy: An Open Source 3D Printed Rover for Education — ResearchGate](https://www.researchgate.net/publication/345162193_ExoMy_An_Open_Source_3D_Printed_Rover_for_Education)

---

*Document EA-07 v1.0 — 2026-03-15*
