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
4. **EA-25 Suspension Audit**: Tube+connector approach, parts list
5. **EA-26 Suspension Design Package**: Differential mechanism, full geometry
6. **CAD Scripts**: `cad/scripts/` for part details
7. **Print Log**: `docs/plans/print-log.md` (what's already printed)
8. **BOM**: `docs/plans/phase1-shopping-list.md`

## Steps

### 1. Build Dependency Graph
Map which parts depend on others for assembly:

```
Bearing Test Piece → (validates print settings)
  ↓
Tube Socket Test → (validates rod fit and grub screw)
  ↓
Calibration Test Card → (validates tolerances)
  ↓
Wheels V3 (×6) ─────────────────────────────┐
RockerHubConnector (×2) ────┐               │
BogiePivotConnector (×2) ───┤               │
FrontWheelConnector (×4) ───┤               │
MiddleWheelConnector (×2) ──┤→ Suspension   │
DifferentialPivotHousing ───┤  Assembly     │
SteeringHornLink (×4) ─────┤               │
SteeringKnuckle (×4) ───────┤               │
CableClip (×8-12) ──────────┘               │
                                             │
SteeringBracket (×4) ──→ Steering Assembly  │
ServoMount (×4) ────────┘                   │
FixedWheelMount (×2) ──┘                    │
                                             │
Body Quadrants (×4) ─────→ Body Assembly ───┤
Top Deck Tiles (×4) ────┘                   │
Electronics Tray ────────→ Electronics ─────┤
                                             │
Strain Relief Clips ─────┐                  │
Fuse Holder Bracket ─────┤→ Wiring ────────┤
Switch Mount Plate ──────┘                  │
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
- Steel rod cutting (2× 1m rods → per `/rod-cutting` plan)

### 5. Output: Recommended Schedule
```
=== Print & Assembly Schedule ===

Day 1: Test & Calibrate
  Print: BearingTestPiece (45min) → test fit
  Print: TubeSocketTest (30min) → test rod fit
  Print: CalibrationTestCard (30min) → measure
  Prep: Level bed, clean nozzle, test adhesion

Day 2-3: Wheels & Connectors
  Print: 6× RoverWheelV3 (~2h each = 12h total)
  Print: 2× RockerHubConnector, 2× BogiePivotConnector
  While printing: Cut steel rods, sort bearings

Day 4-5: Suspension Connectors
  Print: 4× FrontWheelConnector, 2× MiddleWheelConnector
  Print: 1× DiffPivotHousing, 2× DiffLink, 4× SteeringKnuckle
  Print: 8-12× CableClip
  While printing: Install heat-set inserts in completed parts

Day 6-7: Steering & Mounts
  Print: 4× SteeringBracket, 4× ServoMount, 2× FixedWheelMount
  Assemble: Suspension (rods + connectors + bearings)

Day 8-10: Body & Electronics
  Print: 4× BodyQuadrant (~4h each)
  Print: 4× TopDeckTile, 1× ElectronicsTray
  While printing: Wire harness prep

Day 11-12: Small Parts & Wiring
  Print: StrainReliefClips, FuseHolderBracket, SwitchMountPlate
  Assemble: Body, mount electronics, wire harness

Day 13-14: Integration & Test
  Final assembly per EA-17
  Test per EA-21

Total print time: ~69h
Total assembly time: ~8-12h
Critical path: Wheels → Suspension → Body → Integration
```

### 6. Generate Checklist
Create a printable checklist at `docs/plans/assembly-checklist.md` if user wants.
