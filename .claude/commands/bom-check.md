---
description: Cross-reference BOM against CAD scripts, STL exports, and parts ordering status
allowed-tools: Read, Glob, Grep, Bash(*), Agent
---

# BOM Cross-Reference Check

Cross-reference the Phase 1 Bill of Materials against what's been designed, exported, printed, and ordered.

## Data Sources
1. **Phase 1 Shopping List**: `docs/plans/phase1-shopping-list.md`
2. **EA-08 Phase 1 Spec**: `docs/engineering/EA-08-phase1-spec.md` (24 parts, dimensions)
3. **CAD Scripts**: `cad/scripts/*/` (what's been designed)
4. **STL Exports**: `3d-print/**/*.stl` (what's been exported)
5. **Print Log**: `docs/plans/print-log.md` (what's been printed — if exists)
6. **Master Todo**: `docs/plans/todo-master.md`

## Steps

### 1. Load BOM
- Read the Phase 1 shopping list and EA-08
- Build a complete parts list with: name, quantity, source (printed/bought), dimensions, status

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

### 4. Dimensional Consistency
Spot-check key dimensions across sources:
- 608ZZ bearing seats: 22.15mm bore × 7.2mm deep (check CAD scripts)
- N20 motor clips: 12.2 × 10.2 × 25mm
- SG90 servo pockets: 22.4 × 12.2 × 12mm
- Heat-set inserts: 4.8mm bore × 5.5mm deep
- Diff bar rod: 300mm (was incorrectly 200mm — verify swept)

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
Printed parts:  X/Y designed | X/Y exported | X/Y printed
Purchased parts: X/Y ordered | X/Y received
Gaps found: [list]
Next actions: [prioritised list]
```
