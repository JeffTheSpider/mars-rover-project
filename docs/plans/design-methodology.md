# Design Methodology & Process

**Date**: 2026-03-15
**Purpose**: Define the engineering process, quality standards, and management practices governing the Mars rover project across all three build phases.

---

## 1. V-Model Development Process

### 1.1 Overview

The project follows a V-model development lifecycle. The left side of the V represents decomposition (from requirements down to implementation), and the right side represents verification (from unit tests up to acceptance).

```
    Requirements ────────────────────────────────── Acceptance Testing
      (EA-01–06)                                      (EA-21 §5)
         │                                                ▲
         ▼                                                │
    System Design ─────────────────────────── System Testing
      (EA-08,10,13)                               (EA-21 §4)
         │                                            ▲
         ▼                                            │
    Module Design ──────────────────── Integration Testing
      (EA-09,12,15,19)                     (EA-21 §3)
         │                                    ▲
         ▼                                    │
    Implementation ──────────── Unit Testing
      (firmware, ROS2)            (EA-21 §2)
```

### 1.2 EA Document Mapping to V-Model Stages

| V-Model Stage | Engineering Analysis Documents | Purpose |
|---------------|-------------------------------|---------|
| **Requirements** | EA-01 Suspension Analysis | Define what the rover must do |
| | EA-02 Drivetrain Analysis | |
| | EA-03 Power System Analysis | |
| | EA-04 Compute & Sensors | |
| | EA-05 Weight Budget | |
| | EA-06 Cost Breakdown | |
| **System Design** | EA-07 Open Source Review | Define how the rover works at system level |
| | EA-08 Phase 1 Prototype Spec | |
| | EA-10 Ackermann Steering | |
| | EA-11 3D Printing Strategy | |
| | EA-13 ROS2 Architecture | |
| | EA-14 Weatherproofing | |
| | EA-16 PWA App Design | |
| **Module Design** | EA-09 ESP32 GPIO Pin Map | Define individual module interfaces |
| | EA-12 UART Protocol (text) | |
| | EA-15 Safety Systems | |
| | EA-18 Binary UART Protocol | |
| | EA-19 Phase 1 Wiring | |
| **Implementation** | Firmware source code | Build and code |
| | ROS2 node source code | |
| | 3D-printed parts | |
| | Wiring and assembly | |
| **Build & Test** | EA-17 Phase 1 Build Guide | Physical construction |
| | EA-21 Test Procedures | Verification at all levels |

### 1.3 Review Gate Criteria

Before progressing from one V-model stage to the next, a review gate must be passed:

| Gate | From → To | Criteria |
|------|-----------|----------|
| G1 | Requirements → System Design | All EA-01 to EA-06 documents complete. Weight budget closes. Cost within target. No unresolved contradictions between documents. |
| G2 | System Design → Module Design | EA-08, EA-10, EA-13 complete. GPIO allocation finalised (EA-09). 3D print strategy defined (EA-11). No unallocated pins or unresolved interface questions. |
| G3 | Module Design → Implementation | EA-12/EA-18, EA-15, EA-19 complete. All interfaces defined with message formats, pin numbers, wire gauges. Safety systems specified for the target phase. |
| G4 | Implementation → Testing | Firmware compiles without errors. ROS2 packages build. All 3D parts printed and dimensionally verified. Wiring complete per EA-19 checklist. |
| G5 | Testing → Acceptance | All unit tests pass. All integration tests pass. System tests pass within tolerance. Test report completed with evidence. |

---

## 2. Phase Gate Reviews

### 2.1 Phase 0 → Phase 1: Design Review

**Objective**: Confirm that all design documents are complete, consistent, and sufficient to begin building the 0.4-scale prototype.

**Checklist**:

- [ ] All EA documents (EA-01 through EA-19) written and internally consistent
- [ ] Cross-references verified (no EA cites a document that contradicts it)
- [ ] GPIO pin map (EA-09) has no conflicts or double-allocations
- [ ] Weight budget (EA-05) closes at 0.4 scale with margin
- [ ] Cost budget (EA-06) within target ($92 electronics, ~$109 total)
- [ ] UART protocol (EA-12) message catalogue covers all needed commands
- [ ] Safety systems (EA-15) define Phase 1 minimum viable safety
- [ ] Wiring guide (EA-19) is complete with no unconnected signals
- [ ] Build guide (EA-17) is sequenced correctly (no step depends on a later step)
- [ ] Parts list finalised with specific part numbers and sources
- [ ] 3D print settings defined for all parts (EA-11)
- [ ] Test procedures written (EA-21) with pass criteria for Phase 1

**Exit criteria**: All items checked. Any open issues documented with planned resolution.

### 2.2 Phase 1 → Phase 2: Prototype Validation

**Objective**: Confirm that the 0.4-scale prototype meets all acceptance criteria and that lessons learned are captured for full-scale design.

**Checklist**:

- [ ] All Phase 1 acceptance tests pass (EA-21 Section 5.1)
- [ ] Straight-line accuracy < 200mm over 5m
- [ ] Turn radius within 20% of calculated
- [ ] 40mm obstacle traversal confirmed
- [ ] Battery runtime > 15 minutes at 50% speed
- [ ] E-stop response < 50ms
- [ ] WiFi range > 10m
- [ ] All unit tests pass
- [ ] Issues log complete (every failure documented with root cause and fix)
- [ ] Lessons-learned document written
- [ ] Phase 2 parts list drafted based on prototype experience
- [ ] Phase 2 design changes identified (e.g., motor driver upgrade to Cytron MDD10A, add PCA9685, add Jetson)
- [ ] Phase 2 EA amendments or new EAs planned

**Exit criteria**: All Phase 1 acceptance tests pass. Issues log reviewed. Phase 2 scope defined.

### 2.3 Phase 2 → Phase 3: Full-Scale Validation

**Objective**: Confirm that the full-scale 3D-printed rover meets performance targets before committing to metal fabrication.

**Checklist**:

- [ ] All Phase 2 acceptance tests pass (EA-21 Section 5.2)
- [ ] UART communication stable at 50Hz for 60+ seconds
- [ ] ROS2 navigation reaches goals within tolerance
- [ ] SLAM map quality verified
- [ ] Obstacle avoidance functional (LIDAR + depth camera)
- [ ] Human detection stops rover appropriately
- [ ] Geofence enforcement tested
- [ ] Full-scale 3D-printed structure handles rover weight without failure
- [ ] Metal fabrication drawings prepared from validated CAD
- [ ] Structural analysis (FEA) completed for metal parts
- [ ] Supplier quotes obtained for metal fabrication
- [ ] Phase 3 budget approved

**Exit criteria**: All Phase 2 tests pass. Metal design validated by analysis. Budget approved.

---

## 3. Configuration Management

### 3.1 Git Branching Strategy

```
main ──────────────────────────────────────────────────────
  │                                      ▲
  ├── feature/motor-control ─────────────┤  (merge via PR)
  │                                      │
  ├── feature/uart-protocol ─────────────┤
  │                                      │
  ├── feature/steering-modes ────────────┤
  │                                      │
  ├── fix/encoder-drift ─────────────────┤
  │                                      │
  └── docs/ea-21-test-procedures ────────┘
```

| Branch Type | Naming Convention | Merges Into | Review Required |
|-------------|-------------------|-------------|-----------------|
| Main | `main` | — | Protected. All tests must pass. |
| Feature | `feature/<description>` | `main` | Self-review (solo project). Compile-test before merge. |
| Bug fix | `fix/<description>` | `main` | Self-review. Include test that reproduces the bug. |
| Documentation | `docs/<description>` | `main` | No compile needed. Review for accuracy. |
| Experiment | `experiment/<description>` | Discard or promote to feature | No review. May be deleted. |

**Solo project note**: Since this is a personal project, pull requests are optional but recommended for significant changes. At minimum, ensure `main` always compiles and passes tests.

### 3.2 Version Numbering

#### Firmware Versioning

Format: `vMAJOR.MINOR.PATCH`

| Component | When to Increment | Example |
|-----------|-------------------|---------|
| MAJOR | Phase change (new hardware platform) | v0.x.x → v1.0.0 (Phase 1 → Phase 2) |
| MINOR | New feature added | v0.1.0 → v0.2.0 (added steering modes) |
| PATCH | Bug fix or tuning | v0.2.0 → v0.2.1 (fixed servo trim) |

Phase mapping:
- Phase 1 firmware: v0.x.x
- Phase 2 firmware: v1.x.x
- Phase 3 firmware: v2.x.x

#### Software Versioning (ROS2 packages)

Same `vMAJOR.MINOR.PATCH` convention. Tracked in `package.xml` version field.

#### Document Versioning

Format: `vMAJOR.MINOR` in the document footer.

| Component | When to Increment |
|-----------|-------------------|
| MAJOR | Structural rewrite or new phase |
| MINOR | Content updates, corrections, additions |

Example: `EA-12 v1.0` → `EA-12 v1.1` (added error code 10) → `EA-12 v2.0` (Phase 2 rewrite).

### 3.3 Change Request Process

For significant design changes (anything that affects multiple EA documents):

1. **Identify**: Describe the proposed change and its motivation
2. **Impact analysis**: List every EA document, firmware module, or hardware component affected
3. **Update**: Revise all affected documents and code
4. **Verify**: Re-run affected tests from EA-21
5. **Record**: Add a change log entry to the affected documents

For minor changes (typo fixes, single-document updates): edit directly, update document version.

---

## 4. Risk Management

### 4.1 Risk Register Format

Each risk is tracked with:

| Field | Description |
|-------|-------------|
| Risk ID | Unique identifier (R-xxx) |
| Description | What could go wrong |
| Likelihood | 1 (rare) to 5 (almost certain) |
| Impact | 1 (negligible) to 5 (project-ending) |
| Risk Score | Likelihood x Impact (1-25) |
| Mitigation | Actions to reduce likelihood or impact |
| Owner | Who is responsible for monitoring |
| Status | Open / Mitigated / Closed |

### 4.2 Top 10 Project Risks

| ID | Description | L | I | Score | Mitigation |
|----|-------------|---|---|-------|------------|
| R-01 | 3D-printed parts too weak for full-scale loads | 3 | 4 | 12 | Phase 1 validates geometry at 0.4 scale. Phase 2 uses thicker walls and higher infill. Phase 3 uses metal. FEA analysis before metal fabrication. |
| R-02 | L298N motor driver insufficient for N20 motors | 2 | 3 | 6 | Phase 1 uses L298N (adequate for 6V N20 motors). Phase 2 upgrades to Cytron MDD10A. Test motor current draw in Phase 1 to validate. |
| R-03 | ESP32-S3 GPIO conflicts with PSRAM (N16R8) | 3 | 5 | 15 | GPIO 26-37 clearly marked as reserved in EA-09. Wiring guide (EA-19) explicitly warns against these pins. Physical tape over reserved pin headers. |
| R-04 | Battery fire or thermal runaway | 1 | 5 | 5 | Use quality LiPo cells with built-in BMS. Never charge unattended. Store in LiPo-safe bag. Undervoltage cutoff in firmware prevents deep discharge. |
| R-05 | WiFi range too short for outdoor use | 3 | 2 | 6 | Phase 1 accepts 10-15m range. Phase 2 adds external antenna. Phase 3 adds 4G backup. Geofence prevents rover from driving out of range. |
| R-06 | Servo power insufficient (L298N 5V regulator) | 4 | 2 | 8 | Phase 1: only 1-2 servos move simultaneously in normal use. If brownout occurs, add dedicated 5V 3A buck converter (~$3). Phase 2 uses dedicated BEC. |
| R-07 | Encoder wires break at suspension pivots | 3 | 2 | 6 | Allow 50mm slack at every pivot. Use strain relief (hot glue at entry points). Route through arm tubes. Phase 2 uses flexible ribbon cable. |
| R-08 | UART communication errors under EMI from motors | 2 | 3 | 6 | Motor noise suppression caps (100nF per motor, EA-17). Short UART wires (<300mm). Text protocol self-recovers from errors (EA-12). Phase 2 binary protocol adds CRC-16. |
| R-09 | Jetson Orin Nano thermal throttling outdoors | 3 | 3 | 9 | Phase 2: add heatsink + fan. Monitor temperature via ROS2 node. Throttle AI workload at 80 degrees C. Consider passive cooling in Phase 3 metal body. |
| R-10 | Scope creep delays Phase 1 completion | 4 | 3 | 12 | Phase 1 deliberately minimal (ESP32 standalone, no Jetson, no AI). Strict feature freeze after design review. Defer all nice-to-haves to Phase 2. Track progress in todo-master.md. |

### 4.3 Risk Review Schedule

| Event | Frequency | Action |
|-------|-----------|--------|
| Quick risk check | Every build session | Scan top 5 risks. Note any new risks encountered. |
| Full risk review | At each phase gate | Review all risks. Update scores. Add new risks from lessons learned. Close mitigated risks. |
| Post-incident review | After any failure or unexpected behaviour | Add new risk if the failure was not already tracked. Document root cause and update mitigation. |

---

## 5. Quality Standards

### 5.1 Code Review Checklist

Before merging firmware or ROS2 code:

**Functionality**
- [ ] Code compiles without warnings (`-Wall -Wextra`)
- [ ] New feature works as intended (manual test)
- [ ] Edge cases handled (zero values, max values, negative values)
- [ ] No unintended side effects on existing features

**Safety**
- [ ] No blocking calls in main loop (no `delay()`, no `while(true)` without yield)
- [ ] Watchdog feed present in all loop paths
- [ ] Motor commands bounded to safe range (-100 to +100)
- [ ] Servo angles clamped to physical limits
- [ ] Error conditions handled (sensor timeout, communication failure)

**Code Quality**
- [ ] Functions are short and single-purpose
- [ ] Variable names are descriptive
- [ ] Magic numbers replaced with named constants
- [ ] Comments explain "why" not "what"
- [ ] No dead code or commented-out blocks left in

**ESP32 Specific**
- [ ] No float math in time-critical loops (use integer or lookup tables)
- [ ] String concatenation avoided in logging (use `snprintf` with char buffer)
- [ ] EEPROM writes debounced (no rapid repeated writes)
- [ ] WiFi reconnect uses exponential backoff
- [ ] PWM values within 0-255 range (8-bit) or 0-65535 (16-bit LEDC)

**ROS2 Specific**
- [ ] Node shuts down cleanly (no orphan processes)
- [ ] Topics use correct message types from rover_msgs
- [ ] QoS settings appropriate (reliable for commands, best-effort for sensor streams)
- [ ] Launch file updated if new node added
- [ ] Parameters documented in config YAML

### 5.2 CAD Review Checklist

Before exporting STL for printing:

- [ ] All dimensions match EA-08 specification (within 0.1mm)
- [ ] Bearing bores sized correctly (22mm for 608ZZ, with 0.1mm tolerance adjustment)
- [ ] Heat-set insert holes sized correctly (5.0mm for 5.7mm OD inserts)
- [ ] Wall thickness meets minimum (3mm structural, 2mm cosmetic)
- [ ] No unsupported overhangs > 45 degrees (or supports added in slicer)
- [ ] Bolt holes have clearance (3.4mm for M3 through-holes, 8.4mm for M8)
- [ ] Parts fit on print bed (225mm x 145mm for CTC Bizer)
- [ ] Mating surfaces aligned (front/rear body halves, arm joints)
- [ ] Cable routing channels present where needed
- [ ] Part labelled (L/R, top/bottom) in the model or with a flat for marking

### 5.3 3D Print Quality Acceptance Criteria

After each print:

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Dimensional accuracy | Callipers on critical dimensions | Within 0.3mm of CAD model |
| Layer adhesion | Flex test (try to peel layers apart) | No delamination under moderate hand pressure |
| Surface finish | Visual inspection | No significant stringing, blobs, or underextrusion |
| Bearing fit | Insert 608ZZ bearing by hand | Press fit: firm push, no hammer needed. Not loose. |
| Heat-set insert fit | Insert with soldering iron at 220 degrees C | Insert sits flush, knurls grip plastic, no excessive melt-through |
| Bolt hole alignment | Pass M3 or M8 bolt through | Bolt passes through without forcing. Threads engage nut on other side. |
| Structural integrity | Hold part, apply moderate twist | No cracking, no flex beyond 1mm under hand force |
| Weight | Kitchen scale | Within 20% of slicer-estimated weight |

### 5.4 Electrical Assembly Checklist

Before closing the rover body:

**Power System**
- [ ] Battery polarity verified with multimeter
- [ ] Fuse installed and rated correctly (20A)
- [ ] Kill switch functional (toggles power)
- [ ] No short circuits (continuity test: positive to negative shows open)
- [ ] L298N VCC voltage correct (7.4-8.4V)
- [ ] L298N 5V output voltage correct (4.8-5.2V)
- [ ] ESP32 VIN voltage correct (4.8-5.2V)

**Signal Wiring**
- [ ] Every wire labelled with GPIO number
- [ ] No wires on reserved GPIOs (26-37)
- [ ] All grounds connected to common bus
- [ ] Voltage divider resistor values verified (10k and 4.7k)
- [ ] ADC pin voltage within safe range (< 3.3V at max battery voltage)
- [ ] Servo signal wires on correct GPIOs (1, 2, 41, 42)
- [ ] Motor direction wires on correct GPIOs (per EA-19)
- [ ] Motor PWM wires on correct GPIOs (4, 7, 8, 11)

**Mechanical**
- [ ] All solder joints heat-shrunk
- [ ] Wire slack at all pivot points (50mm minimum)
- [ ] Strain relief at pivot entry/exit points
- [ ] No bare wire touching chassis or other bare wire
- [ ] Wires routed through internal channels (not external)
- [ ] No wires near sharp edges or pinch points

---

## 6. Documentation Standards

### 6.1 EA Document Format and Numbering

All engineering analysis documents follow a consistent format:

**Numbering**: `EA-XX` where XX is a sequential number (01, 02, ..., 21).

**Header block** (every document):
```
# Engineering Analysis XX: <Title>

**Document**: EA-XX
**Date**: YYYY-MM-DD
**Purpose**: One-sentence description of what this document covers.
**Depends on**: List of EA documents this one references.
```

**Footer** (every document):
```
*Document EA-XX vM.N — YYYY-MM-DD*
```

**Structure conventions**:
- Use numbered sections (## 1. Section, ### 1.1 Subsection)
- Tables for structured data (specifications, pin maps, comparisons)
- Code blocks for firmware snippets, protocol examples, and ASCII diagrams
- Explicit units on all numerical values (mm, V, A, Hz, ms, kg, degrees)
- Cross-references to other EAs by number (e.g., "see EA-10 Section 5")

### 6.2 Drawing and Diagram Standards

| Diagram Type | Tool | Format | Location |
|-------------|------|--------|----------|
| ASCII wiring diagrams | Text editor | Embedded in EA documents | In-document |
| CAD models | Fusion 360 | .f3d (native) + .step (interchange) | `/cad/` directory |
| STL files for printing | Exported from Fusion 360 | .stl (binary) | `/cad/stl/` directory |
| Circuit schematics (future) | KiCad | .kicad_sch | `/electrical/` directory |
| ROS2 node graphs | Text (ASCII) or draw.io | Embedded or .png | In-document or `/docs/diagrams/` |
| System block diagrams | Text (ASCII) or draw.io | Embedded or .png | In-document |

**ASCII diagram conventions** (used throughout EAs):
- Use box-drawing characters or `+---+` for boxes
- Use `-->` or `▶` for data flow direction
- Label all connections
- Include a legend if symbols are ambiguous

### 6.3 Test Report Format

Test reports follow the template defined in EA-21 Section 6.1:

```
Test ID:        <from EA-21>
Date:           YYYY-MM-DD
Tester:         <name>
Firmware:       <version>
Hardware rev:   <phase and revision>
Result:         PASS / FAIL
Measured value: <quantitative result>
Notes:          <observations, anomalies>
Follow-up:      <actions if failed>
```

Store test reports in `/docs/test-reports/phase-N/` as markdown files, one file per test session. Include photos or video links where applicable.

### 6.4 Document Change Log

Major documents should include a change log at the bottom (before the footer):

```markdown
## Change Log

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial release |
| v1.1 | 2026-04-01 | Added error code 10 (PCA9685 failure) |
| v2.0 | 2026-06-15 | Phase 2 rewrite: binary protocol, CRC-16 |
```

---

*Design Methodology v1.0 — 2026-03-15*
