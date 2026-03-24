---
description: Cross-reference BOM against CAD scripts, STL exports, and parts ordering status
allowed-tools: Read, Glob, Grep, Bash(*), Agent
---

# BOM Cross-Reference Check

Cross-reference the Phase 1 Bill of Materials against what's been designed, exported, printed, and ordered.

## Data Sources
1. **Phase 1 Shopping List**: `docs/plans/phase1-shopping-list.md`
2. **EA-08 Phase 1 Spec**: `docs/engineering/08-phase1-prototype-spec.md` (base parts list)
3. **EA-25 Suspension Audit**: `docs/engineering/25-suspension-audit.md` (tube+connector parts)
4. **EA-26 Suspension Design**: `docs/engineering/26-suspension-design-package.md` (differential mechanism)
5. **CAD Scripts**: `cad/scripts/` (what's been designed)
6. **STL Exports**: `3d-print/**/*.stl` (what's been exported)
7. **Print Log**: `docs/plans/print-log.md` (what's been printed — if exists)
8. **Master Todo**: `docs/plans/todo-master.md`

## Steps

### 1. Load BOM
- Read the Phase 1 shopping list, EA-08, EA-25, and EA-26
- Build a complete parts list with: name, quantity, source (printed/bought), dimensions, status
- Note: Parts list was redesigned in EA-25/EA-26 — use these as authoritative

### 2. Printed Parts Status
For each 3D printed part in the BOM:

| Part | CAD Script? | STL Exported? | Printed? | Notes |
|------|------------|---------------|----------|-------|
| Check `cad/scripts/` for matching script | Check `3d-print/` for matching STL | Check print log if exists | |

### 3. Purchased Parts Status
For each bought part (bearings, motors, electronics, hardware):
- Cross-reference against shopping list
- Check if ordered (look for notes in todo or shopping list)
- Flag anything missing or unclear
- Key quantities: 9× 608ZZ bearings, 2× 1m steel rods, 6× N20 motors, 4× SG90 servos

### 4. Dimensional Consistency
Spot-check key dimensions across sources:
- 608ZZ bearing seats: 22.15mm bore x 7.2mm deep (check CAD scripts)
- N20 motor clips: 12.2 x 10.2 x 25mm
- SG90 servo pockets: 22.4 x 12.2 x 12mm
- Heat-set inserts: 4.8mm bore x 5.5mm deep
- Diff bar rod: 400mm total (200mm half-span, EA-26)
- Tube sockets: 8.2mm bore for 8mm rods

### 5. Gap Analysis
Identify:
- Parts in BOM but no CAD script yet
- CAD scripts with no STL export
- STL exports not yet printed
- Purchased parts not yet ordered
- Any quantity mismatches (e.g., need 6 wheels but only 1 script)

### 6. Summary Report
```
=== Mars Rover Phase 1 BOM Status ===
Printed parts:  X/28 designed | X/28 exported | X/28 printed
Purchased parts: X/Y ordered | X/Y received
Bearings: X/12 on hand (9 needed + 3 spares)
Steel rods: X/2 on hand (2× 1m, 8mm dia)
Gaps found: [list]
Next actions: [prioritised list]
```
