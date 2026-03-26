# CAD Dimensions Reference — Phase 1 (0.4 Scale)

All dimensions verified in Fusion 360 on 2026-03-26. Every script produces a single body.

## Shared Constants (rover_cad_helpers.py)

| Constant | Value (mm) | Purpose |
|----------|-----------|---------|
| BEARING_OD | 22.15 | 608ZZ outer diameter |
| BEARING_DEPTH | 7.2 | 608ZZ radial depth |
| BEARING_BORE | 8.1 | 608ZZ inner bore |
| TUBE_BORE | 8.2 | Arm tube socket bore |
| TUBE_DEPTH | 15 | Tube socket depth |
| TUBE_WALL | 4 | Minimum tube socket wall |
| INSERT_BORE | 4.8 | M3 heat-set insert bore |
| INSERT_DEPTH | 5.5 | M3 heat-set insert depth |
| GRUB_M3 | 1.6 | M3 grub screw bore radius |
| N20_W | 12.2 | N20 motor pocket width |
| N20_H | 10.2 | N20 motor pocket height |
| N20_D | 25 | N20 motor pocket depth |
| N20_SHAFT_EXIT | 2.0 | Shaft exit hole radius (4mm dia) |
| SG90_W | 22.4 | SG90 servo pocket width |
| SG90_D | 12.2 | SG90 servo pocket depth |
| SG90_POCKET_DEPTH | 12 | SG90 pocket insertion depth |
| FILLET_STD | 0.5 | Standard external fillet |
| CHAMFER_STD | 0.3 | Standard entry chamfer |
| CORNER_R | 2.0 | Rounded-rect corner radius |

---

## Calibration (2 scripts)

### bearing_test_piece.py
- **Verified size:** 32.8 x 32.8 x 12.0 mm
- **Features:** 3x 608ZZ bearing seats (22.15mm x 7.2mm deep), 3mm base
- **Qty:** 1 (test only) | **EA:** EA-11, EA-25

### tube_socket_test.py
- **Verified size:** 58.9 x 20.3 x 19.0 mm
- **Features:** 3x tube sockets (8.1/8.2/8.3mm bore variants), 15mm deep
- **Qty:** 1 (test only) | **EA:** EA-25

---

## Wheels (2 scripts)

### rover_wheel_v3.py
- **Verified size:** 86.0 x 86.0 x 52.0 mm
- **Body:** OD 80mm, width 44mm, 5 spokes
- **Hub:** 3.1mm D-shaft bore, M3 grub screw
- **Traction:** O-ring grooves
- **Qty:** 6 | **EA:** EA-11, EA-25

### rover_tire.py
- **Verified size:** 86.0 x 86.0 x 44.0 mm
- **Body:** OD 86mm, ID 75mm, width 44mm
- **Features:** 48 tread ribs
- **Qty:** 6 (TPU, friend's printer) | **EA:** EA-11

---

## Steering (4 scripts)

### steering_bracket.py
- **Verified size:** 35.0 x 30.0 x 30.0 mm
- **Features:** 608ZZ seat (top), 8.1mm pivot bore, 2x M3 through-holes (16mm spacing)
- **Hard stops:** ±35°
- **Mates with:** steering_knuckle (bearing pivot), front/rear wheel connector (M3 bolts)
- **Qty:** 4 | **EA:** EA-25, EA-27

### steering_knuckle.py
- **Verified size:** 39.0 x 34.6 x 41.5 mm
- **Features:** 608ZZ seat (top), N20 pocket (12.2x10.2x25mm), 4mm axle bore
- **Steering arm:** 15mm extension + hard stop tab
- **Mates with:** steering_bracket (bearing), servo_mount (horn link), wheel (N20 shaft)
- **Qty:** 4 | **EA:** EA-25, EA-27

### steering_horn_link.py
- **Verified size:** 28.0 x 8.0 x 5.0 mm
- **Features:** 20mm c/c hole spacing, 2x M2 pin holes, M2 washer counterbores (2.8mm)
- **Mates with:** SG90 horn (M2 pin) + steering_knuckle arm (M2 pin)
- **Qty:** 4 | **EA:** EA-27, EA-10

### servo_mount.py
- **Verified size:** 40.0 x 18.0 x 25.0 mm
- **Features:** SG90 pocket (22.4x12.2x12mm), 2x M2 servo holes (27.5mm), 2x M3 mount
- **Horn slot offset:** 5.1mm from centre
- **Mates with:** front_wheel_connector side face (M3 bolts)
- **Qty:** 4 | **EA:** EA-27

---

## Drivetrain (1 script)

### fixed_wheel_mount.py
- **Verified size:** 25.0 x 25.0 x 30.0 mm
- **Features:** N20 pocket (horizontal), 3.1mm shaft exit, 2x M3 through-holes (16mm)
- **Extras:** Zip-tie slot, 2x diagonal gussets
- **Mates with:** middle_wheel_connector bottom face (M3 bolts into inserts)
- **Qty:** 2 (ML/MR) | **EA:** EA-25, EA-26

---

## Suspension (7 scripts)

### front_wheel_connector.py
- **Verified size:** 35.0 x 30.0 x 30.0 mm
- **Tube socket:** 8.2mm x 15mm deep (side face), M3 grub
- **Mount faces:** 2x M3 inserts steering (20mm, front), 2x M3 inserts servo (20mm, side)
- **Wire exit:** 10x8mm (motor + servo wires)
- **Mates with:** steering_bracket (front), servo_mount (side), 8mm rod (top)
- **Qty:** 4 (FL/FR/RL/RR) | **EA:** EA-25, EA-27

### middle_wheel_connector.py
- **Verified size:** 30.0 x 25.0 x 25.0 mm (smallest connector)
- **Tube socket:** 8.2mm x 15mm deep (side face), M3 grub
- **Mount face:** 2x M3 inserts (16mm, bottom)
- **Wire exit:** 8x6mm (motor only)
- **Mates with:** fixed_wheel_mount (bottom), 8mm rod (top)
- **Qty:** 2 (ML/MR) | **EA:** EA-25

### rocker_hub_connector.py
- **Verified size:** 45.0 x 40.0 x 35.0 mm
- **Diff bar bore:** 8.0mm press-fit + M3 grub
- **Tube sockets:** 2x (8.2mm x 15mm, front/rear)
- **Wire channels:** 2x (8x6mm)
- **Mates with:** diff bar (press-fit), bogie_pivot (8mm rods), front_wheel (8mm rod)
- **Qty:** 2 (L/R) | **EA:** EA-25, EA-26

### bogie_pivot_connector.py
- **Verified size:** 44.5 x 30.1 x 45.0 mm (cylindrical revolve)
- **608ZZ seat:** top face (22.15x7.2mm), 8.1mm pivot bore
- **Tube sockets:** 3x (8.2x15mm) — up, front-down, rear-down @ 70° spread
- **Wire channel:** 8x6mm (centre)
- **Mates with:** rocker (bearing pivot), middle_wheel (8mm rod), rear_wheel (8mm rod)
- **Qty:** 2 (L/R) | **EA:** EA-25, EA-26

### differential_pivot_housing.py
- **Verified size:** 30.0 x 30.0 x 23.0 mm
- **608ZZ seat:** 22.15x7.2mm, 8.1mm bore
- **Mount:** 4x M3 inserts (32mm PCD, 45° cross-pattern)
- **Hard stops:** ±25° rotation limit
- **Mates with:** body_quadrant (RL/RR seam), diff bar (bearing pivot)
- **Qty:** 1 | **EA:** EA-25, EA-26

### differential_link.py
- **Verified size:** 20.0 x 85.0 x 6.0 mm
- **Features:** Connecting link between diff pivot and rocker hubs
- **Qty:** 2 | **EA:** EA-26

### cable_clip.py
- **Verified size:** 11.3 x 15.8 x 5.0 mm
- **Rod bore:** 8.3mm (friction fit on 8mm rod)
- **Wire channel:** 5x3mm, locating ridge 1.5mm
- **Qty:** 12 (3 per arm rod x 4) | **EA:** EA-25, EA-23

---

## Body (4 scripts)

### body_quadrant.py
- **Verified size:** 130.5 x 225.5 x 120.0 mm (one quadrant)
- **Full rover body:** 440 x 260 x 120 mm (4 quadrants assembled)
- **Walls:** 4mm, ribs 2mm, corner radius 2mm
- **Features:** Rocker pivot bosses (RL/RR: 608ZZ seats), vent slots, cable channels
- **Alignment:** 3mm dowel pin holes + M3 seam inserts
- **Cosmetic:** LED underglow (5mm), headlight (20mm recess), taillight (15mm recess)
- **Kill switch:** RR quadrant, 15mm bore
- **Qty:** 4 (FL/FR/RL/RR) | **EA:** EA-08, EA-11, EA-29

### top_deck.py
- **Verified size:** 133.0 x 223.0 x 10.0 mm (one tile)
- **Features:** Snap clips (6x10mm), stiffening ribs (2mm), solar grid texture
- **Accessories:** Phone mount (FR: 4x M3), camera mast (RL: 4x M3), antenna dish (RR)
- **Qty:** 4 (FL/FR/RL/RR) | **EA:** EA-11, EA-20

### electronics_tray.py
- **Verified size:** 120.0 x 180.0 x 18.0 mm
- **Features:** ESP32 edge-clip posts, 8x M2 L298N standoffs, LiPo cradle (88x36mm)
- **Extras:** Breadboard pocket (49x37mm), 6x wire U-channels, USB-C access (12x6mm)
- **Mount:** 4x M3 body mounts (150mm spacing)
- **Qty:** 1 | **EA:** EA-09, EA-11, EA-19

### battery_tray.py
- **Verified size:** 94.0 x 42.0 x 23.0 mm
- **Interior:** 88x36x20mm (fits 86x34x19mm 2S LiPo)
- **Features:** 4x strap slots, XT60 access (16x10mm), JST-XH exit (8x5mm)
- **Mount:** 4x M3 corner holes (50mm pattern)
- **Qty:** 1 | **EA:** EA-03, EA-11

---

## Accessories (3 scripts)

### strain_relief_clip.py
- **Verified size:** 18.0 x 10.0 x 11.5 mm
- **Features:** U-channel (6x5mm), entry ramps, snap tabs (1.5mm)
- **Mount:** 2x M3 holes (10mm spacing)
- **Qty:** 8-12 | **EA:** EA-19, EA-23

### fuse_holder_bracket.py
- **Verified size:** 19.0 x 40.0 x 13.5 mm
- **Features:** Fuse channel (8x6mm for 8x35mm fuse), retention lips
- **Mount:** 4x M3 holes
- **Qty:** 1 | **EA:** EA-03, EA-15

### switch_mount.py
- **Verified size:** 30.0 x 30.0 x 5.0 mm
- **Features:** Toggle bore 15mm, entry chamfer, 2x M3 diagonal holes with counterbores
- **Qty:** 1 | **EA:** EA-15, EA-22

---

## Assembly Interface Matrix

| Connection | Fasteners | Spacing |
|-----------|-----------|---------|
| steering_bracket ↔ front_wheel_connector | M3 bolts into inserts | 20mm |
| servo_mount ↔ front_wheel_connector | M3 bolts into inserts | 20mm |
| fixed_wheel_mount ↔ middle_wheel_connector | M3 bolts into inserts | 16mm |
| steering_horn_link ↔ SG90 horn + knuckle arm | M2x10 + washer + nyloc | 20mm c/c |
| rocker_hub ↔ diff bar | 8.0mm press-fit + M3 grub | N/A |
| All tube sockets ↔ 8mm rods | 8.2mm bore + M3 grub | 15mm deep |
| differential_pivot ↔ body_quadrant | M3 inserts | 32mm PCD |
| electronics_tray ↔ body_quadrant | M3 through-holes | 150mm |
| top_deck ↔ body_quadrant | Snap clips | No fasteners |
| cable_clip ↔ 8mm rods | Friction C-clip | N/A |

## Print Summary

| Category | Parts | Total Qty | Est. Print Time |
|----------|-------|-----------|-----------------|
| Calibration | 2 | 2 | 20 min |
| Wheels | 2 | 12 | 540 min |
| Steering | 4 | 16 | 264 min |
| Drivetrain | 1 | 2 | 60 min |
| Suspension | 7 | 25 | 420 min |
| Body | 4 | 10 | 1035 min |
| Accessories | 3 | 12 | 40 min |
| **Total** | **23 types** | **79 pieces** | **~40 hrs** |

All parts fit CTC Bizer bed (225x145x150mm). Body quadrant is the largest at 130.5x225.5mm — fits with ~0.5mm clearance on the long axis.
