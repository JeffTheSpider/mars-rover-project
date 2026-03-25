# Open-Source CAD Model Reference

Reference catalogue of existing 3D-printable models and open-source designs relevant to the Mars Rover project. Curated for adaptation — not direct use. Every part should be re-modelled in Fusion 360 to match our parametric dimensions, but these provide geometry inspiration, proven mechanisms, and fitment validation.

**Last updated:** 2026-03-25

---

## Top Picks (Highest Relevance)

| Model | Why | Source | License | Format |
|-------|-----|--------|---------|--------|
| **jakkra Mars-Rover** | Fusion 360 .f3z file, rocker-bogie, 3D-printed, most directly importable | [GitHub](https://github.com/jakkra/Mars-Rover) | MIT | Fusion 360 (.f3z) |
| **Sawppy** | Tube+connector approach matches ours, 608ZZ+8mm shaft, mature design | [GitHub](https://github.com/Roger-random/Sawppy_Rover) | MIT | Onshape (free) |
| **JPL Open Source Rover** | Official NASA/JPL design, excellent docs, proven at scale | [GitHub](https://github.com/nasa-jpl/open-source-rover) | Apache 2.0 | Onshape |
| **EEZYbotARM MK2** | 4-bar linkage arm, MG996R servos, exactly matches EA-24 concept | [Thingiverse](https://www.thingiverse.com/thing:1454048) | CC BY-NC | STL + STEP |
| **GrabCAD Rocker-Bogie** | Full rocker-bogie assembly, reference geometry | [GrabCAD](https://grabcad.com/library/rover-with-rocker-bogie-wheel-1) | Public | STEP/STL |

---

## 1. Complete Rover Designs

### 1.1 jakkra Mars-Rover ★★★
- **Source:** [github.com/jakkra/Mars-Rover](https://github.com/jakkra/Mars-Rover)
- **License:** MIT
- **Format:** Fusion 360 .f3z (directly importable!)
- **Features:** Rocker-bogie, 6 wheels, 3D printed, ESP32-based
- **Relevance:** Closest to our project. Can import directly into Fusion 360 as reference assembly.
- **Key differences:** Different scale, different motor choice, no differential bar mechanism

### 1.2 Sawppy Rover ★★★
- **Source:** [github.com/Roger-random/Sawppy_Rover](https://github.com/Roger-random/Sawppy_Rover) (483 stars)
- **License:** MIT
- **Format:** Onshape (free to view/copy)
- **Features:** 8mm steel rods + 3D printed connectors (same approach as ours), 608ZZ bearings, rocker-bogie
- **Relevance:** Our tube+connector architecture is directly inspired by Sawppy. Use for connector geometry reference.
- **Key parts to study:** Rod clamps, bearing seats, wheel hubs, differential mechanism

### 1.3 JPL Open Source Rover ★★☆
- **Source:** [github.com/nasa-jpl/open-source-rover](https://github.com/nasa-jpl/open-source-rover) (9.2k stars)
- **License:** Apache 2.0
- **Format:** Onshape
- **Features:** Aluminium extrusion + custom brackets, full rocker-bogie, ROS2 support
- **Relevance:** Excellent engineering documentation. Too large and expensive for Phase 1 but good reference for Phase 2/3 aluminium upgrade.

### 1.4 ExoMy ★★☆
- **Source:** [github.com/esa-prl/ExoMy](https://github.com/esa-prl/ExoMy)
- **License:** GPL-3.0
- **Format:** STEP files
- **Features:** ESA-inspired, fully 3D printed, Raspberry Pi, rocker-bogie
- **Relevance:** Compact design, good for small-scale reference. Different suspension approach.

### 1.5 OpenPerseverance ★☆☆
- **Source:** [printables.com/model/639451](https://www.printables.com/model/639451-open-perseverance)
- **License:** CC0 (public domain)
- **Format:** STL
- **Features:** Perseverance replica, detailed body panels
- **Relevance:** Cosmetic/body panel reference only. Different scale and mechanism.

### 1.6 HowToMechatronics Mars Rover ★★☆
- **Source:** [howtomechatronics.com](https://howtomechatronics.com/projects/diy-mars-perseverance-rover-replica/)
- **Format:** STEP + SolidWorks
- **Features:** Full build tutorial, NEMA17 motors, detailed wiring
- **Relevance:** Good build documentation reference. Different motor class but similar structure.

### 1.7 Watney Rover ★☆☆
- **Source:** [GitHub](https://github.com/nicholasgasior/watney)
- **License:** MIT
- **Features:** WebRTC video streaming, simple 4-wheel design
- **Relevance:** Software reference for camera streaming only.

---

## 2. Suspension & Wheels

### 2.1 Sawppy Wheel Hub ★★★
- **Source:** Sawppy Onshape
- **Features:** 608ZZ bearing seat, 8mm shaft, printed spokes, rubber band traction
- **Relevance:** Very close to our wheel design. Study spoke geometry and bearing seat tolerances.

### 2.2 Sawppy Rocker/Bogie Connectors ★★★
- **Source:** Sawppy Onshape
- **Features:** Tube clamp connectors for 8mm rods, snap/bolt retention
- **Relevance:** Direct reference for our tube socket design (8.2mm bore, 15mm depth).

### 2.3 GrabCAD Rocker-Bogie Assembly ★★☆
- **Source:** [GrabCAD](https://grabcad.com/library/rover-with-rocker-bogie-wheel-1)
- **Features:** Complete rocker-bogie with differential bar
- **Relevance:** Reference geometry for rocker-bogie linkage ratios and pivot placement.

### 2.4 EQM Mars Rover Wheels ★★☆
- **Source:** Thingiverse / GrabCAD
- **Features:** Curiosity-style grousered wheels, various sizes
- **Relevance:** Aesthetic reference for Phase 2 wheel design. Our Phase 1 uses simpler O-ring traction bands.

### 2.5 Parametric 608ZZ Bearing Mount ★★☆
- **Source:** Various (Thingiverse, Printables)
- **Features:** Adjustable bearing press-fit tolerance
- **Relevance:** Tolerance calibration for our 22.15mm bearing seats on CTC Bizer.

---

## 3. Steering & Motor Mounts

### 3.1 Sawppy Steering Knuckle ★★★
- **Source:** Sawppy Onshape
- **Features:** 608ZZ bearing + 8mm shaft, servo-driven steering
- **Relevance:** Closest match to our steering knuckle design. Study the servo linkage geometry.

### 3.2 EQM Mars Rover Steering (SG90) ★★☆
- **Source:** GrabCAD / Thingiverse
- **Features:** SG90 servos for steering actuation
- **Relevance:** SG90 mounting bracket reference for Phase 1.

### 3.3 Ackermann Steering Linkage ★★☆
- **Source:** Various GrabCAD models
- **Features:** 4-bar linkage Ackermann geometry
- **Relevance:** Validate our horn link 4-bar approach (EA-27). Compare linkage geometry.

### 3.4 N20 Motor Mount (Improved) ★★★
- **Source:** Thingiverse / Printables
- **Features:** N20 micro gearmotor mount with M2 bolt retention
- **Relevance:** Direct reference for our motor clip design (12.2×10.2×25mm envelope).
- **Key detail:** Some designs use M2 bolts through motor face holes rather than friction clips — worth evaluating.

### 3.5 L298N Mounting Bracket ★★☆
- **Source:** Thingiverse
- **Features:** 43×43mm PCB mount with standoffs, M3 holes
- **Relevance:** Reference for electronics tray L298N mounting. Our L298N module has 4× M3 mounting holes on 37mm spacing.

---

## 4. Robotic Arms (Phase 2)

### 4.1 EEZYbotARM MK2 ★★★
- **Source:** [Thingiverse](https://www.thingiverse.com/thing:1454048)
- **License:** CC BY-NC
- **Features:** 3-DOF + gripper, MG996R servos, 4-bar parallel linkage, 300mm reach
- **Relevance:** **Top pick for Phase 2 arm.** 4-bar linkage matches EA-24 concept. MG996R servos match our Phase 2 spec. Extensively tested by community.
- **Adaptation needed:** Scale to rover mount points, redesign base for 360° rotation, add ESP32/ROS2 control

### 4.2 RC Rover+Arm 6DOF ★★☆
- **Source:** MakerWorld
- **Features:** 6-DOF arm on rover platform, MG996R servos
- **Relevance:** Shows integrated rover+arm approach. Study the arm base mounting to chassis.

### 4.3 Easy Robot Arm (Fusion 360) ★★☆
- **Source:** GrabCAD
- **Format:** Fusion 360
- **Features:** 3-DOF, designed in Fusion 360
- **Relevance:** Directly importable as reference. Study joint design.

### 4.4 3-DOF Servo Arm ★★☆
- **Source:** Various (Thingiverse, Printables)
- **Features:** 3-DOF, SG90/MG996R, exact EA-24 match in concept
- **Relevance:** Validates our 3-DOF + gripper approach for Phase 2.

### 4.5 ElRobot ★☆☆
- **Source:** [elrobot.dev](https://elrobot.dev/)
- **Features:** 7-DOF, AI-ready, $220 BOM, Feb 2026 release
- **Relevance:** Aspirational — much more complex than EA-24 scope but shows what's possible.

### 4.6 LittleBot Gripper ★★☆
- **Source:** Thingiverse / Printables
- **Features:** SG90-driven parallel gripper, compact
- **Relevance:** Phase 1 arm mount prep gripper reference. Small enough for 0.4 scale testing.

### 4.7 Thor / BCN3D Moveo / AR2 ★☆☆
- **Source:** Various GitHub repos
- **Features:** Full 6-axis industrial-style arms
- **Relevance:** Phase 3 reference only. Too large/complex for Phase 1-2.

---

## 5. Electronics Enclosures & Mounts

### 5.1 ESP32-S3-DevKitC-1 Case ★★★
- **Source:** Thingiverse / Printables
- **Features:** Snap-fit case for ESP32-S3 DevKitC-1 (exact board match)
- **Relevance:** Direct use or adaptation for our electronics tray. Verify dimensions against our 62.7×25.4mm PCB spec.

### 5.2 L298N Snap-Fit Case ★★★
- **Source:** Thingiverse
- **Features:** Enclosure for L298N module with ventilation for heatsink, wire routing slots
- **Relevance:** Protect L298N modules in electronics tray. CTC Bizer printable.

### 5.3 Jetson Orin Nano Super Case ★★☆
- **Source:** Thingiverse / Printables
- **Features:** Ventilated case for Jetson module
- **Relevance:** Phase 2. Keep for later.

### 5.4 2S LiPo Battery Case ★★☆
- **Source:** Various
- **Features:** Battery holders with strap retention
- **Relevance:** Adapt for our 86×34×19mm LiPo in electronics tray. Anti-vibration padding.

### 5.5 Parametric IP65 Enclosure ★☆☆
- **Source:** Thingiverse
- **Features:** Customisable weatherproof box with cable glands
- **Relevance:** Phase 3 weatherproofing reference (EA-14).

---

## 6. Sensors & Camera Mounts

### 6.1 SG90 Pan-Tilt Mount ★★★
- **Source:** Thingiverse / Printables (many variants)
- **Features:** 2-axis camera mount using 2× SG90 servos
- **Relevance:** Mast camera mount for Phase 1/2. We have SG90s in our BOM.

### 6.2 OAK-D Lite Camera Mount ★★☆
- **Source:** Luxonis GitHub / Thingiverse
- **Features:** Mounting bracket for OAK-D Lite stereo depth camera
- **Relevance:** Phase 2 depth camera mount. Keep for later.

### 6.3 RPLidar A1 Case ★★☆
- **Source:** Thingiverse
- **Features:** Protective housing with mounting holes
- **Relevance:** Phase 2 LIDAR mount. Keep for later.

### 6.4 BNO055 IMU Housing ★☆☆
- **Source:** Various
- **Features:** Vibration-dampened IMU mount
- **Relevance:** Phase 2. Important for accurate EKF localisation — vibration isolation matters.

### 6.5 GPS Antenna Mount ★☆☆
- **Source:** Various
- **Features:** Ground plane + elevated mount
- **Relevance:** Phase 2 GPS. Mount needs clear sky view.

---

## 7. Accessories & Utility

### 7.1 Solar Panel Bracket ★☆☆
- **Source:** Various (Thingiverse, GrabCAD)
- **Features:** Adjustable angle brackets for solar panels
- **Relevance:** Phase 2 solar charging (100W 2S2P panels).

### 7.2 Cable Management Clips ★★☆
- **Source:** FRC (FIRST Robotics) designs, Thingiverse
- **Features:** Wire routing clips, cable chain, strain relief
- **Relevance:** Wire harness routing (EA-23 describes 58-wire harness). Print a few test clips.

### 7.3 Heat-Set Insert Jig ★★☆
- **Source:** Thingiverse / Printables
- **Features:** Alignment jig for pressing heat-set inserts straight
- **Relevance:** We use M3 heat-set inserts throughout. CTC Bizer PLA at 170-180°C.

---

## 8. Design Adaptation Notes

### What to Import vs. What to Redesign

**Import as reference bodies (don't print directly):**
- jakkra .f3z file — import as external reference in Fusion 360 assembly
- Sawppy connectors — screenshot geometry, re-model to our parameters
- EEZYbotARM — study linkage ratios, re-model for our servo/mount specs

**Print directly (or with minor scaling):**
- ESP32-S3 case (verify dimensions first)
- L298N case (verify heatsink clearance)
- SG90 pan-tilt (standard SG90 dimensions)
- Cable management clips

**Study and redesign from scratch:**
- Steering knuckles (our horn link 4-bar is unique — EA-27)
- Wheel hubs (our specific spoke/O-ring design)
- Suspension connectors (our parametric dimensions differ)
- Robotic arm (must match rover mount points and control system)

### CTC Bizer Constraints
All downloaded models must be checked against our printer limits:
- Max print volume: 225 × 145 × 150 mm
- PLA only (no PETG, TPU, ABS)
- Single extruder (left only)
- x3g format via GPX conversion
- Use `/stl-check <file>` to verify bed fit before printing

### Licensing Summary
| License | Can Modify? | Commercial? | Must Share? |
|---------|-------------|-------------|-------------|
| MIT | Yes | Yes | No |
| Apache 2.0 | Yes | Yes | No (patent clause) |
| CC0 | Yes | Yes | No |
| CC BY | Yes | Yes | No (attribution) |
| CC BY-SA | Yes | Yes | Yes (same license) |
| CC BY-NC | Yes | **No** | No |
| GPL-3.0 | Yes | Yes | Yes (source code) |

Our project is currently private. If we open-source, avoid CC BY-NC parts (EEZYbotARM MK2) — redesign from scratch using the linkage concept.

---

## Action Items

1. **Import jakkra .f3z into Fusion 360** — Use as overlay reference for our assembly
2. **Study Sawppy connectors in Onshape** — Compare tube socket geometry to our 8.2mm bore / 15mm depth
3. **Download ESP32-S3 + L298N cases** — Test print for electronics tray fit
4. **Download SG90 pan-tilt** — Prototype mast camera mount
5. **Bookmark EEZYbotARM MK2** — Phase 2 arm starting point (redesign for licensing)
6. **Print heat-set insert jig** — Useful for all M3 insert installations
7. **Print cable management clips** — Start wire harness routing practice
