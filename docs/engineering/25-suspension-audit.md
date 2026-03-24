# EA-25: Suspension System — Definitive Mechanical Audit

**Version:** 1.0
**Date:** 2026-03-24
**Status:** AUDIT COMPLETE — Design corrections identified, ready for CAD

---

## 1. Purpose

Exhaustive trace of every mechanical connection from body to each wheel.
Identifies every printed part, hardware item, dimension, and design issue
before CAD scripting begins. Resolves conflicts between existing scripts
and the tube+connector plan.

---

## 2. Critical Design Corrections

### 2A. DESIGN CONFLICT: Monolithic Arms vs Tube+Connector

**Problem:** Two competing designs exist:
- `rocker_arm.py` / `bogie_arm.py` → monolithic printed arms (hollow rectangular tubes)
- `docs/plans/suspension-system-plan.md` → 8mm steel rods with printed connectors

**Resolution: Tube+Connector wins.** Reasons:
1. Steel rods resist bending/tension far better than PLA cross-grain
2. Less print time (~12h connectors vs ~25h monolithic arms)
3. Adjustable tube lengths (cut to fit)
4. Wire routing via connector channels (MrOver-inspired)
5. More NASA-authentic appearance

**Action:** `rocker_arm.py` and `bogie_arm.py` are DEPRECATED for the
suspension system. They may serve as reference for dimensions only.
New connector scripts replace them.

### 2B. DESIGN CORRECTION: Differential Mechanism

**Problem:** The original plan has 3× diff bar adapters (L/C/R), each with
608ZZ bearing seats. This allows each rocker to rotate independently on
the diff bar — defeating the differential coupling.

**Corrected mechanism (diff bar = rocker pivot):**
```
                    ┌─────── BODY ────────┐
                    │                     │
    [L ROCKER HUB]═╪═══ DIFF BAR (8mm) ══╪═[R ROCKER HUB]
       clamped      │   608ZZ    608ZZ    │      clamped
       (grub)       │  bearing  bearing   │      (grub)
                    └─────────────────────┘
```

- The diff bar IS the rocker pivot axis
- Each rocker hub connector CLAMPS rigidly to the diff bar (M3 grub screw)
- The BODY has 608ZZ bearings (in pivot bosses) that the diff bar rotates in
- When left rocker tilts up → bar rotates → right rocker tilts down → body stays level
- **No separate diff bar adapters needed** — `diff_bar_adapter.py` is DEPRECATED

**Bearing count change:** 11 → 8 (no separate diff bar bearings needed)

### 2C. TIRE BORE MISMATCH

**Problem:** `rover_tire.py` has 70mm bore but wheel rim OD is 80mm (seat OD = 75mm).

**Fix:** Update tire bore from 70mm → 75mm (interference fit on 75mm rim seat).

### 2D. PIVOT BORE CLEARANCE

**Problem:** Several scripts use `PIVOT_BORE_R = 0.4cm` (8.0mm diameter) for
8mm shaft pass-through. This is zero clearance — shaft won't fit.

**Note:** This is OK where the shaft sits IN a bearing (bearing provides fit).
For tube sockets in new connector scripts, use **8.2mm bore** (0.2mm clearance),
following MrOver's `tube_rad = 8 + 0.2`.

---

## 3. Complete Mechanical Chain — Body to Each Wheel

### 3A. BODY → DIFF BAR → ROCKER HUB (one per side)

```
BODY (FL+RL quadrants)          BODY (FR+RR quadrants)
  │ pivot boss                    │ pivot boss
  │ [608ZZ bearing]               │ [608ZZ bearing]
  ├─────── 300mm 8mm DIFF BAR ───┤
  │                               │
  [L ROCKER HUB]          [R ROCKER HUB]
  (clamped to bar)         (clamped to bar)
```

**Parts per side:**
| # | Part | Type | Qty |
|---|------|------|-----|
| 1 | Body pivot boss | Integrated in body_quadrant.py | 1 |
| 2 | 608ZZ bearing | Hardware | 1 |
| 3 | Diff bar (shared) | 300mm × 8mm steel rod | 0.5 |
| 4 | **Rocker hub connector** | NEW printed part | 1 |

### 3B. ROCKER HUB → FRONT WHEEL (steered)

```
[ROCKER HUB]
  │ front tube socket (angled down ~15°)
  │
  ═══ 150mm 8mm STEEL ROD (front arm) ═══
  │
  [FRONT WHEEL CONNECTOR]
  │ steering bracket face
  │ servo mount face
  │
  [STEERING BRACKET]          [SERVO MOUNT]
  │ 608ZZ steering pivot       │ SG90 servo
  │ N20 motor clip             │ horn → bracket
  │
  [WHEEL]
  │ PLA rim + TPU tire
```

**Parts per side:**
| # | Part | Type | Qty |
|---|------|------|-----|
| 5 | Front arm tube | 150mm × 8mm steel rod | 1 |
| 6 | **Front wheel connector** | NEW printed part | 1 |
| 7 | Steering bracket | Existing script | 1 |
| 8 | Servo mount | Existing script | 1 |
| 9 | SG90 servo | Hardware | 1 |
| 10 | N20 motor | Hardware | 1 |
| 11 | Wheel rim | Existing script (needs V3) | 1 |
| 12 | Wheel tire | Existing script (needs bore fix) | 1 |
| 13 | 608ZZ bearing (steering) | Hardware | 1 |

### 3C. ROCKER HUB → BOGIE PIVOT

```
[ROCKER HUB]
  │ rear tube socket (angled down ~20°)
  │
  ═══ 60mm 8mm STEEL ROD (rocker rear arm) ═══
  │
  [BOGIE PIVOT CONNECTOR]
  │ 608ZZ bearing (bogie rotation)
```

**Parts per side:**
| # | Part | Type | Qty |
|---|------|------|-----|
| 14 | Rocker rear arm tube | 60mm × 8mm steel rod | 1 |
| 15 | **Bogie pivot connector** | NEW printed part | 1 |
| 16 | 608ZZ bearing (bogie pivot) | Hardware | 1 |

### 3D. BOGIE PIVOT → MIDDLE WHEEL (fixed, no steering)

```
[BOGIE PIVOT CONNECTOR]
  │ front tube socket
  │
  ═══ 60mm 8mm STEEL ROD (bogie front arm) ═══
  │
  [MIDDLE WHEEL CONNECTOR]
  │ fixed mount face
  │
  [FIXED WHEEL MOUNT]
  │ N20 motor clip (no steering)
  │
  [WHEEL]
```

**Parts per side:**
| # | Part | Type | Qty |
|---|------|------|-----|
| 17 | Bogie front arm tube | 60mm × 8mm steel rod | 1 |
| 18 | **Middle wheel connector** | NEW printed part | 1 |
| 19 | Fixed wheel mount | Existing script | 1 |
| 20 | N20 motor | Hardware | 1 |
| 21 | Wheel rim | Existing script (needs V3) | 1 |
| 22 | Wheel tire | Existing script (needs bore fix) | 1 |

### 3E. BOGIE PIVOT → REAR WHEEL (steered)

```
[BOGIE PIVOT CONNECTOR]
  │ rear tube socket
  │
  ═══ 60mm 8mm STEEL ROD (bogie rear arm) ═══
  │
  [REAR WHEEL CONNECTOR]
  │ steering bracket face
  │ servo mount face
  │
  [STEERING BRACKET]          [SERVO MOUNT]
  │ 608ZZ steering pivot       │ SG90 servo
  │ N20 motor clip
  │
  [WHEEL]
```

**Parts per side:**
| # | Part | Type | Qty |
|---|------|------|-----|
| 23 | Bogie rear arm tube | 60mm × 8mm steel rod | 1 |
| 24 | **Rear wheel connector** | NEW printed part | 1 |
| 25 | Steering bracket | Existing script | 1 |
| 26 | Servo mount | Existing script | 1 |
| 27 | SG90 servo | Hardware | 1 |
| 28 | N20 motor | Hardware | 1 |
| 29 | Wheel rim | Existing script (needs V3) | 1 |
| 30 | Wheel tire | Existing script (needs bore fix) | 1 |
| 31 | 608ZZ bearing (steering) | Hardware | 1 |

---

## 4. Complete Parts Inventory (Both Sides)

### 4A. NEW Printed Parts (to design)

| Part | Qty | Est. Size (mm) | Key Features |
|------|-----|-----------------|--------------|
| **Rocker hub connector** | 2 | 45×40×35 | Clamps to diff bar (8.0mm bore + M3 grub), 2× tube sockets (8.2mm bore × 15mm deep, front angled ~15° down, rear angled ~20° down), 2× wire channels (8×6mm) |
| **Front wheel connector** | 2 | 35×30×30 | 1× tube socket, steering bracket mount face (2× M3 heat-set), servo mount face (2× M3 heat-set), wire exit hole (10×8mm) |
| **Bogie pivot connector** | 2 | 45×35×30 | 608ZZ bearing seat (22.15×7.2mm), 3× tube sockets (one from rocker, two to wheels), wire channel Y-split (8×6mm in, 2× 6×4mm out) |
| **Middle wheel connector** | 2 | 30×25×25 | 1× tube socket, fixed mount face (2× M3 heat-set), wire exit hole (8×6mm) |
| **Rear wheel connector** | 2 | 35×30×30 | Same as front wheel connector (mirrored) |
| **Cable clips** | 12 | 12×8×5 | Snap-fit onto 8mm rod, 5×3mm wire channel, printed in pairs |

**Total new printed parts: 22** (10 connectors + 12 cable clips)

### 4B. EXISTING Printed Parts (to use/update)

| Part | Qty | Script | Changes Needed |
|------|-----|--------|----------------|
| Steering bracket | 4 | `steering_bracket.py` | None — dimensions verified correct |
| Servo mount | 4 | `servo_mount.py` | None — dimensions verified correct |
| Fixed wheel mount | 2 | `fixed_wheel_mount.py` | None — dimensions verified correct |
| Wheel rim | 6 | `rover_wheel.py` → `rover_wheel_v3.py` | **REDESIGN** — 5-spoke jakkra-style, 75mm seat OD |
| Wheel tire | 6 | `rover_tire.py` | **FIX** bore 70mm → 75mm |
| Body quadrant | 4 | `body_quadrant.py` | Verify pivot boss dimensions match diff bar design |

**Total existing printed parts: 26** (10 brackets + 6 rims + 6 tires + 4 body)

### 4C. DEPRECATED Printed Parts (no longer needed)

| Part | Script | Reason |
|------|--------|--------|
| Rocker arm (front/rear halves) | `rocker_arm.py` | Replaced by tubes + connectors |
| Bogie arm | `bogie_arm.py` | Replaced by tubes + connectors |
| Diff bar adapter (×3) | `diff_bar_adapter.py` | Diff bar goes directly through body bearings |

### 4D. Hardware (Buy)

| Item | Qty | Specification | Source |
|------|-----|--------------|--------|
| 608ZZ bearings | 8 | 8×22×7mm | eBay/Amazon |
| 8mm steel rod | 2m total | Mild steel, smooth | Hardware shop |
| N20 geared motors | 6 | 100RPM 6V | AliExpress |
| SG90 micro servos | 4 | 180° | AliExpress |
| M3×8 socket head cap screws | 30 | For heat-set inserts | eBay |
| M3×5.7 heat-set inserts | 30 | Brass, 4.8mm OD | CNC Kitchen / eBay |
| M3 grub screws (set screws) | 18 | M3×4mm | eBay |
| M2×8 self-tapping screws | 8 | For servo mount M2 holes | eBay |
| 3mm steel dowel pins | 8 | 15mm long, body alignment | Hardware shop |
| 2S LiPo 2200mAh | 1 | 7.4V, XT60 | Hobby shop |
| L298N motor driver | 2 | Dual H-bridge | AliExpress |

### 4E. Rod Cutting Plan

From 2× 1m 8mm steel rods:

| Rod | Qty | Length | Purpose | Total |
|-----|-----|--------|---------|-------|
| Diff bar | 1 | 300mm | Body width + overhang | 300mm |
| Rocker front arm | 2 | 150mm | Hub to front wheel | 300mm |
| Rocker rear arm | 2 | 60mm | Hub to bogie pivot | 120mm |
| Bogie front arm | 2 | 60mm | Bogie to middle wheel | 120mm |
| Bogie rear arm | 2 | 60mm | Bogie to rear wheel | 120mm |
| **Total** | **9** | | | **960mm** |

960mm from 2000mm = 1040mm spare. Plenty of room for errors.

---

## 5. Dimension Audit Matrix

### 5A. Hardware Fitments (must match across ALL scripts)

| Dimension | Value | Tolerance | Scripts Using |
|-----------|-------|-----------|---------------|
| 608ZZ bearing seat dia | 22.15mm | ±0.05mm | steering_bracket, body_quadrant, bogie pivot connector (NEW) |
| 608ZZ bearing seat depth | 7.2mm | ±0.05mm | Same as above |
| 608ZZ bearing entry chamfer | 0.3mm × 45° | Cosmetic | Same as above |
| N20 motor clip width | 12.2mm | ±0.1mm | steering_bracket, fixed_wheel_mount |
| N20 motor clip height | 10.2mm | ±0.1mm | Same as above |
| N20 motor clip depth | 25mm | ±0.5mm | Same as above |
| N20 shaft exit hole | 4mm dia | ±0.2mm | Same as above |
| SG90 servo pocket | 22.4×12.2×12mm | ±0.1mm | servo_mount |
| SG90 tab pocket width | 32.4mm | ±0.2mm | servo_mount |
| Heat-set insert bore | 4.8mm dia | ±0.05mm | All mount points |
| Heat-set insert depth | 5.5mm | ±0.1mm | All mount points |
| M3 bolt clearance hole | 3.2mm dia | ±0.1mm | All bolt holes |
| Tube socket bore | 8.2mm dia | NEW | All connectors |
| Tube socket depth | 15mm | NEW | All connectors |
| M3 grub screw hole | 3.0mm dia × 6mm | NEW | All tube sockets |
| Diff bar clamp bore | 8.0mm dia | ±0.05mm | Rocker hub connector (press-fit) |
| Wire channel (main) | 8×6mm rect | ±0.5mm | All connectors |
| Wire channel (split) | 6×4mm rect | ±0.5mm | Bogie pivot connector |

### 5B. Cross-Script Consistency Check

| Parameter | steering_bracket | fixed_wheel_mount | servo_mount | body_quadrant | NEW connectors |
|-----------|-----------------|-------------------|-------------|---------------|----------------|
| BEARING_SEAT_R | 1.1075cm ✓ | N/A | N/A | 1.1075cm ✓ | 1.1075cm |
| BEARING_SEAT_DEPTH | 0.72cm ✓ | N/A | N/A | 0.72cm ✓ | 0.72cm |
| N20 MOTOR_W | 1.22cm ✓ | 1.22cm ✓ | N/A | N/A | N/A |
| N20 MOTOR_H | 1.02cm ✓ | 1.02cm ✓ | N/A | N/A | N/A |
| INSERT_BORE | 0.48cm ✓ | 0.48cm ✓ | 0.48cm ✓ | 0.48cm ✓ | 0.48cm |
| INSERT_DEPTH | 0.55cm ✓ | 0.55cm ✓ | 0.55cm ✓ | 0.55cm ✓ | 0.55cm |

**Result: All existing scripts are dimensionally consistent. ✓**

### 5C. Suspension Geometry (0.4x Scale)

| Dimension | Value | Source |
|-----------|-------|--------|
| Body length (Y) | 440mm | body_quadrant.py |
| Body width (X) | 260mm | body_quadrant.py |
| Body height (Z) | 80mm | body_quadrant.py |
| Rocker front arm | 150mm tube + 2×15mm socket = 180mm span | Plan |
| Rocker rear arm | 60mm tube + 2×15mm socket = 90mm span | Plan |
| Bogie front arm | 60mm tube + 2×15mm socket = 90mm span | Plan |
| Bogie rear arm | 60mm tube + 2×15mm socket = 90mm span | Plan |
| Diff bar | 300mm rod | Plan |
| Wheel diameter | 80mm rim / 86mm with tire | rover_wheel.py / rover_tire.py |
| Wheel width | 32mm | rover_wheel.py |
| Rocker pivot height | ~80mm (body top) | body_quadrant.py |
| Bogie pivot position | 90mm behind rocker pivot | rocker_arm.py geometry |
| Front wheel position | 180mm ahead of rocker pivot | rocker_arm.py geometry |

### 5D. Sawppy Cross-Reference

| Our Part | Our Dim | Sawppy Equivalent | Sawppy Dim | Ratio |
|----------|---------|-------------------|------------|-------|
| Wheel | 80mm dia | Wheel.stl | 124mm dia | 0.65× |
| Rocker span | 270mm | Rocker.stl | 98mm (partial) | N/A |
| Bogie span | 180mm | Bogie-Body + Bogie-Wheels | 147mm total | 1.22× |
| Diff bar | 300mm | DiffBrace.stl | 240mm | 1.25× |
| Steering knuckle | 35×30×40mm | Steering Knuckle.stl | 97×40×110mm | Smaller (SG90 vs LX-16A) |

---

## 6. Wire Routing Audit

### 6A. Wire Count Per Segment

| Segment | Wires | Details |
|---------|-------|---------|
| Body → Rocker hub | 12 | 2× motor power (front) + 3× servo signal (front) + 2× motor (mid) + 2× motor (rear) + 3× servo (rear) |
| Rocker front arm | 5 | 2× motor power + 3× servo signal (front wheel) |
| Rocker rear arm | 7 | 2× motor (mid) + 2× motor (rear) + 3× servo (rear) |
| Bogie → middle wheel | 2 | Motor power only (no steering) |
| Bogie → rear wheel | 5 | 2× motor power + 3× servo signal |

### 6B. Wire Channel Sizing

| Channel | Size | Capacity | Location |
|---------|------|----------|----------|
| Main (rocker hub) | 10×8mm | 12 wires (AWG 22-26) | Through body wall to rocker hub |
| Front arm | 8×6mm | 5 wires | Along 150mm front tube |
| Rear arm | 8×6mm | 7 wires (tight) | Along 60mm rear tube |
| Bogie front | 6×4mm | 2 wires | Along 60mm bogie front tube |
| Bogie rear | 6×4mm | 5 wires (tight — upgrade to 8×6mm) | Along 60mm bogie rear tube |

**Issue:** Bogie rear channel needs 5 wires in 6×4mm — too tight.
**Fix:** Use 8×6mm for ALL channels. Standardise on one size.

### 6C. Wire Routing Method

Wires run **externally** along 8mm solid steel rods (not through them).
Cable clips snap-fit onto the rods and hold wires against them.
Wires enter/exit through rectangular channels in the connectors.

```
  ┌────────────── 8mm steel rod ──────────────┐
  │  [clip]  ── wires ──  [clip]  ── wires ── │
  │                                            │
[CONNECTOR]                            [CONNECTOR]
  wire channel ──→                  ←── wire channel
```

---

## 7. Print Feasibility Audit

### CTC Bizer bed: 225 × 145 × 150mm

| Part | X (mm) | Y (mm) | Z (mm) | Fits? | Orientation |
|------|--------|--------|--------|-------|-------------|
| Rocker hub connector | 45 | 40 | 35 | ✓ | Flat |
| Front wheel connector | 35 | 30 | 30 | ✓ | Flat |
| Bogie pivot connector | 45 | 35 | 30 | ✓ | Flat |
| Middle wheel connector | 30 | 25 | 25 | ✓ | Flat |
| Rear wheel connector | 35 | 30 | 30 | ✓ | Flat |
| Cable clip (×2 on bed) | 24 | 8 | 5 | ✓ | Flat |
| Steering bracket | 35 | 30 | 40 | ✓ | Flat |
| Servo mount | 40 | 18 | 25 | ✓ | Flat |
| Fixed wheel mount | 25 | 25 | 30 | ✓ | Flat |
| Wheel rim | 80 | 80 | 32 | ✓ | Hub down |
| Wheel tire (TPU) | 86 | 86 | 32 | ✓** | **CTC can't print TPU** |
| Body quadrant | 220 | 130 | 80 | ✓ (tight) | Open face up |

**Issue:** CTC Bizer cannot print TPU (all-metal hot end and direct drive required).
**Workaround:** Use PLA wheels with O-ring grooves for Phase 1 traction.
Order TPU tires from a print service, or defer to Phase 2 printer.
The wheel script already has `USE_TPU_TIRE` toggle with O-ring groove fallback.

### Estimated Print Times (connectors only)

| Part | Qty | Est. Time Each | Total |
|------|-----|---------------|-------|
| Rocker hub connector | 2 | 2.5h | 5h |
| Front wheel connector | 2 | 1.5h | 3h |
| Bogie pivot connector | 2 | 2h | 4h |
| Middle wheel connector | 2 | 1h | 2h |
| Rear wheel connector | 2 | 1.5h | 3h |
| Cable clips | 12 | 0.25h | 3h |
| **Connector subtotal** | **22** | | **20h** |
| Steering bracket | 4 | 1.5h | 6h |
| Servo mount | 4 | 1h | 4h |
| Fixed wheel mount | 2 | 1h | 2h |
| Wheel rim | 6 | 2h | 12h |
| Body quadrant | 4 | 6h | 24h |
| **Grand total** | **42** | | **~68h** |

---

## 8. Hardware Compatibility Check

### 8A. N20 Motor → Steering Bracket / Fixed Mount

| Check | Value | Pass? |
|-------|-------|-------|
| Motor body: 12×10×25mm → Clip: 12.2×10.2×25mm | 0.2mm clearance all sides | ✓ |
| Shaft: 3mm D-shaft → Wheel bore: 3.1mm D | 0.1mm clearance | ✓ |
| M2 grub screw retention on wheel hub | 2mm bore × 5mm deep | ✓ |
| Zip-tie slot on fixed mount | 3.5×2mm | ✓ |

### 8B. SG90 Servo → Servo Mount

| Check | Value | Pass? |
|-------|-------|-------|
| Servo body: 22.2×12.0×11.8mm → Pocket: 22.4×12.2×12mm | 0.2mm clearance | ✓ |
| Tab-to-tab: 32.2mm → Pocket: 32.4mm | 0.2mm clearance | ✓ |
| M2 mounting holes: 2.0mm → Mount: 2.4mm | 0.4mm clearance | ✓ |
| Horn slot: ±35° sweep → 12mm dia slot | ✓ (verified) | ✓ |

### 8C. 608ZZ Bearing → All Seats

| Check | Value | Pass? |
|-------|-------|-------|
| Bearing OD: 22mm → Seat: 22.15mm | 0.15mm clearance (press/snug fit) | ✓ |
| Bearing width: 7mm → Seat depth: 7.2mm | 0.2mm clearance | ✓ |
| Bearing ID: 8mm → Rod: 8mm | Zero clearance (bearing provides rotation) | ✓ |

### 8D. 8mm Steel Rod → Tube Sockets

| Check | Value | Pass? |
|-------|-------|-------|
| Rod OD: 8mm → Socket bore: 8.2mm | 0.2mm clearance (slide fit) | ✓ |
| Socket depth: 15mm | Good engagement | ✓ |
| M3 grub screw retention | 3mm bore through socket wall | ✓ |
| Wall around socket: 4mm minimum | Adequate for PLA 60% infill | ✓ |

---

## 9. New CAD Scripts Required

### Priority Order (build dependency)

| # | Script Name | Complexity | Dependencies |
|---|-------------|-----------|--------------|
| 1 | `rover_wheel_v3.py` | HIGH | None — can validate immediately |
| 2 | `rover_tire.py` (update) | LOW | Wheel V3 (for bore match) |
| 3 | `cable_clip.py` | LOW | None |
| 4 | `bogie_pivot_connector.py` | HIGH | None |
| 5 | `middle_wheel_connector.py` | MEDIUM | Fixed wheel mount dims |
| 6 | `front_wheel_connector.py` | MEDIUM | Steering bracket dims |
| 7 | `rear_wheel_connector.py` | MEDIUM | Same as front (mirror) |
| 8 | `rocker_hub_connector.py` | HIGHEST | All other connectors (defines tube angles) |
| 9 | `suspension_assembly.py` | HIGH | All above |

### Key Design Parameters for Each Script

**All connectors share:**
```python
TUBE_SOCKET_BORE_R = 0.41    # 8.2mm dia (0.2mm clearance on 8mm rod)
TUBE_SOCKET_DEPTH = 1.5      # 15mm engagement
GRUB_HOLE_R = 0.15           # 3mm dia M3 grub screw
GRUB_HOLE_DEPTH = 0.6        # 6mm (through wall)
WIRE_CHANNEL_W = 0.8         # 8mm wide
WIRE_CHANNEL_H = 0.6         # 6mm tall
WALL = 0.4                   # 4mm minimum
BEARING_SEAT_R = 1.1075      # 22.15mm dia (608ZZ)
BEARING_SEAT_DEPTH = 0.72    # 7.2mm
INSERT_BORE_R = 0.24         # 4.8mm dia (heat-set)
INSERT_DEPTH = 0.55          # 5.5mm
```

---

## 10. Stale Value Check

| Value | Expected | Search Pattern | Status |
|-------|----------|---------------|--------|
| Bogie length | 180mm | "120" in suspension scripts | ✓ Clean |
| Diff bar | 300mm | "200" in diff scripts | ✓ Clean |
| Printer | CTC Bizer | "Ender" | ✓ Clean |
| Material | PLA (Phase 1) | "PETG" in Phase 1 context | ✓ Clean |
| Bearings | 8 total | "11 bearings" | **UPDATE** suspension plan |
| Body | 4 quadrants | "halves" | ✓ Clean |

---

## 11. Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| PLA connectors crack at tube sockets | HIGH | Medium | 4mm walls, 60% infill, 5 perimeters. Fallback: aluminium tube clamps |
| 8mm rod doesn't fit tube socket | MEDIUM | Low | Print test socket first (bearing test piece approach) |
| Diff bar slips in rocker hub | HIGH | Medium | M3 grub screw + thread-lock. Fallback: D-shaft flat on rod end |
| Wire bundles too thick for channels | MEDIUM | Medium | Standardised 8×6mm channels. Use thinner wire (AWG 26) |
| CTC Bizer can't print TPU tire | LOW | Certain | Use O-ring grooves on PLA rim. Order TPU from service |
| Body pivot boss too thin for bearing | MEDIUM | Low | Boss wall: 3.9mm around bearing — marginal. Monitor |
| Tube angles wrong at rocker hub | HIGH | Medium | Compute from geometry, verify in assembly script first |

---

## 12. Action Items

### Immediate (before CAD design)
1. ✅ Complete this audit document
2. Update suspension plan with corrected bearing count (11 → 8)
3. Update suspension plan with corrected differential mechanism
4. Update `rover_tire.py` bore: 70mm → 75mm
5. Create test socket piece (like bearing test piece) for 8mm rod fit validation

### CAD Design Phase (in order)
6. Write `rover_wheel_v3.py` — 5-spoke jakkra-style, 75mm seat
7. Write `cable_clip.py` — snap-fit on 8mm rod
8. Write `bogie_pivot_connector.py` — most important connector after hub
9. Write `middle_wheel_connector.py`
10. Write `front_wheel_connector.py` / `rear_wheel_connector.py`
11. Write `rocker_hub_connector.py` — last (needs all tube angles)
12. Write `suspension_assembly.py` — validates all geometry

### Deprecation
13. Mark `rocker_arm.py` as deprecated (add header comment)
14. Mark `bogie_arm.py` as deprecated
15. Mark `diff_bar_adapter.py` as deprecated

### Documentation
16. Update `docs/plans/suspension-system-plan.md` to match this audit
17. Update memory files with corrected design
18. Back up after each major milestone

---

## Appendix A: Connector Tube Angle Geometry

The rocker hub connector must direct tubes at the correct angles.
These angles determine the suspension geometry.

```
             ┌── Diff bar axis (horizontal, perpendicular to body side)
             │
     ┌───────┼───────┐  ROCKER HUB CONNECTOR
     │       │       │
  rear ←─────┤────→ front
  tube   20° │  15°  tube
  (down)     │      (down)
             │
        body side wall
```

### Angle Computation (to be verified in assembly script)

Given:
- Body top surface: Z = 80mm above ground reference
- Rocker pivot: at body side, Z ≈ 70mm (10mm below top)
- Front wheel center: Z ≈ 43mm (half of 86mm tire), Y = +180mm ahead
- Bogie pivot: Z ≈ 55mm, Y = -90mm behind

Front arm angle below horizontal:
- ΔZ = 70 - 43 = 27mm drop over ΔY = 180mm
- angle = atan(27/180) ≈ 8.5° below horizontal

Rear arm angle below horizontal:
- ΔZ = 70 - 55 = 15mm drop over ΔY = 90mm
- angle = atan(15/90) ≈ 9.5° below horizontal

**Note:** These are approximate. Final angles will be computed from the
full kinematic model in the assembly script. The suspension must allow
±20° of rocker travel for obstacle climbing.

---

## Appendix B: Design Comparison Summary

| Feature | Our Phase 1 | Sawppy V1 | Papaya Mini | MrOver |
|---------|------------|-----------|-------------|--------|
| Scale | 0.4× | ~0.3× | ~0.3× | ~0.5× |
| Frame | 8mm steel rod | 8mm steel rod | Metal/printed | Carbon fibre tube |
| Connectors | Printed PLA | Printed PLA clips | Printed PLA | Printed (OpenSCAD) |
| Bearings | 608ZZ (8 total) | 608ZZ | M3 bolts | 608ZZ + thrust |
| Drive motors | N20 100RPM (6×) | LX-16A smart servo | N20 (6×) | DC geared |
| Steering | SG90 (4×) | LX-16A smart servo | SG90 (4×) | Servo |
| Wheels | 80mm PLA + TPU | 124mm PLA | ~80mm PLA + TPU | 150mm PLA |
| Diff mechanism | Bar = pivot (1 rod) | 5-part linkage | 3-part bar | Bar + clamps |
| Wire routing | External + clips | External | External | Through-hole joints |
| Body | 4-quadrant PLA | Beam frame | Printed | Printed |

---

*EA-25 v1.0 — Audit complete. Ready for CAD design phase.*
