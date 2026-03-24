# Mars Rover CAD Design Phase — Handover Document

**Date**: 2026-03-22
**From**: Previous Claude Code session (Revamp w Claude workspace)
**To**: New Claude Code session (Mars Rover Project workspace, Fusion 360 MCP connected)

---

## What's Been Done

### Full Project Audit (119 fixes across 2 projects)
- Two-pass code audit covering Clock, Lamp, Hub, Rover Firmware, ROS2, PWA, and Docs
- All fixes committed: `b20e2ef`, `3a0388e` (pass 1), `9d80789`, `6b511c1` (pass 2)

### Design Phase Prep (this session)
- Fusion 360 installed and MCP-Link connected via `mcp-proxy.exe`
- Shopping list updated for Charlie's CTC Bizer printer (PLA, 225×145mm bed)
- EA-08 updated: 24 parts, 4-segment body, 69hr print time, PLA
- EA-20 updated: 4-quadrant body split, alignment features, Fusion 360 assembly structure
- CLAUDE.md updated with printer specs and CAD workflow
- Parameter script ready: `cad/scripts/generate_rover_params.py`

### Commits from this session
- `dbb8e39` — Update docs for CTC printer: PLA, 150x200mm bed, 4-segment body
- `8edf1ec` — Update CLAUDE.md: CTC printer specs, CAD workflow, PLA Phase 1

---

## Charlie's Setup

### 3D Printer
- **Model**: CTC 3D Bizer (MakerBot Replicator 1 Dual clone)
- **Bed size**: 225×145mm (body needs 4 quadrants to fit)
- **Material**: PLA only (no PETG, no TPU)
- **Heat-set inserts**: 170-180°C for PLA (lower than PETG)

### CAD Tool
- **Fusion 360 Personal** — installed and running
- **MCP-Link add-in** — loaded in Fusion 360 (v1.2.72, Aura Friday)
- **MCP connection**: Working via `.mcp.json` using `mcp-proxy.exe` stdio bridge
- The MCP gives you direct Fusion 360 API access — you can create sketches, extrude bodies, build assemblies, export STLs

### Key Reference Documents
- `docs/engineering/08-phase1-prototype-spec.md` — ALL dimensions for every part (v1.1)
- `docs/engineering/20-cad-preparation-guide.md` — Assembly structure, design checklist, Fusion 360 workflow
- `docs/engineering/11-3d-printing-strategy.md` — Print settings, segmentation, heat-set inserts
- `docs/engineering/01-suspension-analysis.md` — Rocker-bogie geometry, bearing locations
- `docs/engineering/10-ackermann-steering.md` — Steering bracket geometry, servo mounting
- `docs/plans/phase1-shopping-list.md` — Components list (£145 core)
- `cad/scripts/generate_rover_params.py` — Parametric dimensions (all measurements in mm)

---

## What Needs To Be Done Now

### CAD Design — Part Order (from EA-20)
Design each part in Fusion 360 using dimensions from EA-08:

| # | Part | Key Dimensions (0.4 scale, mm) | Count |
|---|------|-------------------------------|-------|
| 1 | Bearing test piece | 22.15mm bore, 608ZZ press-fit | 1 |
| 2 | Wheels | 80mm dia, 32mm width, 3.1mm D-shaft, 12 grousers, O-ring grooves | 6 |
| 3 | Bogie arms | 180mm long, 15×12mm tube, bearing bosses both ends | 2 |
| 4 | Rocker arms | 180mm long, 20×15mm tube, bearing bosses, differential mount | 2 |
| 5 | Differential adapters | Connects 8mm rod to rocker arms | 3 |
| 6 | Steering brackets | 35×25×40mm, 608ZZ pivot, servo horn mount, ±35° range | 4 |
| 7 | Fixed wheel mounts | Middle wheels, no steering, bearing + motor mount | 2 |
| 8 | Motor mounts | N20 snap-fit clip, 12.2×10.2mm inner | 6 |
| 9 | Body segments | 4 quadrants (~220×130mm each), 3mm walls, alignment tabs | 4 |
| 10 | Electronics tray | ESP32 (69×25mm) + 2× L298N (43×43mm) + LiPo tray | 1 |
| 11 | Deck cover | Top panel, ventilation slots | 1 |

### After CAD
1. Export STLs to `3d-print/` directory
2. Review shopping list — order parts
3. Start printing (bearing test piece first for calibration)

---

## Critical Design Constraints

- **All parts must fit 225×145mm bed** (CTC Bizer)
- **PLA material** — design wall thickness ≥3mm for structural, 2mm for non-structural
- **608ZZ bearings**: 8mm ID, 22mm OD, 7mm width — bore holes at 22.15mm for press-fit in PLA
- **M3 heat-set inserts**: 4.8mm hole diameter, 5.5mm depth, 170-180°C insertion
- **Body splits at X=0 and Y=+20mm** into 4 quadrants with alignment features (dowel pins + tongue-and-groove + interlocking tabs)
- **12× M3x12 body join bolts** (6 per seam axis)
- **Wheels**: Rigid PLA with circumferential grooves for 70mm ID × 3mm rubber O-rings (no TPU)
- **N20 motors**: 12mm diameter, 10mm flat width, 3.1mm D-shaft

---

## Charlie's Preferences (from memory)
- Wants thorough, dissertation-grade engineering work
- Prefers efficiency and optimization
- Comfortable with code but this is his first Fusion 360 project
- Wants all plugins/skills used proactively
- Holiday just ended — back at PC, ready to work

---

## How To Start

In this session, you have the Fusion 360 MCP. Start by:

1. Run `generate_rover_params.py` to get all dimensions
2. Create a new Fusion 360 document called "Mars Rover Phase 1"
3. Design the bearing test piece first (simplest part, validates 608ZZ fit)
4. Then wheels, then work through the part order above

Use `execute_python` via the MCP to run Fusion API code directly. You have full access to `adsk.core`, `adsk.fusion`, sketches, extrusions, fillets, assemblies, and STL export.

Good luck! 🚀
