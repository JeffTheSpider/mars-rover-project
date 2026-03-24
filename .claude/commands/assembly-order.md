---
description: Calculate optimal print and assembly order based on dependencies
allowed-tools: Read, Glob, Grep, Bash(*), Agent
---

# Assembly Order Planner

Calculate the optimal order for printing and assembling Mars Rover Phase 1 parts.

## Data Sources
1. **EA-08 Phase 1 Spec**: Part list and dimensions
2. **EA-17 Build Guide**: Step-by-step assembly (14-day timeline)
3. **EA-11 3D Printing**: Print settings and strategies
4. **CAD Scripts**: `cad/scripts/*/` for part details
5. **Print Log**: `docs/plans/print-log.md` (what's already printed)
6. **BOM**: `docs/plans/phase1-shopping-list.md`

## Steps

### 1. Build Dependency Graph
Map which parts depend on others for assembly:

```
Bearing Test Piece → (validates print settings)
  ↓
Calibration Test Card → (validates tolerances)
  ↓
Wheels (×6) ─────────────────────────────┐
Bogie Arms (×2) ──────┐                  │
Rocker Arms Front (×2)─┤                  │
Rocker Arms Rear (×2) ─┤                  │
                       ├→ Suspension Assembly
Fixed Wheel Mounts (×2)┘                  │
                                          │
Steering Brackets (×4) ──→ Steering Assembly
Servo Mounts (×4) ────────┘               │
                                          │
Diff Bar Adapters (×2) ──→ Drivetrain ────┤
                                          │
Body Quadrants (×4) ─────→ Body Assembly ─┤
Top Deck Tiles (×4) ─────┘               │
Electronics Tray ────────→ Electronics ───┤
                                          │
Strain Relief Clips ─────┐               │
Fuse Holder Bracket ─────┤→ Wiring ──────┤
Switch Mount Plate ──────┘               │
                                          │
                              ROVER COMPLETE
```

### 2. Print Time Estimates
For each part, estimate print time based on:
- Volume and complexity from STL/CAD data
- Suggested settings from EA-11
- CTC Bizer speeds (~40-50mm/s for PLA)
- Total estimated: ~69 hours (from EA-08)

### 3. Optimise Print Order
Consider:
- **Test pieces first** — validate printer settings before committing to real parts
- **Assembly order** — print what you need to assemble first
- **Batch similar settings** — group parts with same layer height/infill
- **Bed utilisation** — can multiple small parts print together?
- **Risk order** — print simple parts first, complex parts after settings are dialled in
- **Already printed** — skip parts that are done (check print log)

### 4. Parallel Tracks
Identify what can happen in parallel:
- While Part X is printing, what assembly/prep can be done?
- Which purchased parts need to arrive before assembly?
- Heat-set insert installation batches

### 5. Output: Recommended Schedule
```
=== Print & Assembly Schedule ===

Day 1: Test & Calibrate
  Print: BearingTestPiece (45min) → test fit
  Print: CalibrationTestCard (30min) → measure
  Prep: Level bed, clean nozzle, test adhesion

Day 2-3: Wheels & Suspension
  Print: 6× RoverWheel (~2h each = 12h total)
  While printing: Sort bearings, prep shafts
  ...

Day X: Final Assembly
  Assemble: [order]
  Wire: [order per EA-23]
  Test: [per EA-21]

Total print time: ~69h
Total assembly time: ~Xh
Critical path: [longest chain]
```

### 6. Generate Checklist
Create a printable checklist at `docs/plans/assembly-checklist.md` if user wants.
