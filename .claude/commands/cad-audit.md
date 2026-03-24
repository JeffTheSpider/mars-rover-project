---
description: Re-run engineering audit checks on CAD scripts for fitment, wall thickness, and consistency
argument-hint: [script name or "all"]
allowed-tools: Read, Glob, Grep, Bash(*), Agent
---

# CAD Script Engineering Audit

Re-run engineering audit checks on Fusion 360 CAD scripts to verify hardware fitments, wall thicknesses, and dimensional consistency.

## Target: $ARGUMENTS

If "all" or empty, audit all scripts in `cad/scripts/`. Otherwise audit the specified script.

## Reference Standards (from Engineering Audit)

### Hardware Fitments (must be identical across ALL scripts)
| Component | Dimension | Tolerance |
|-----------|-----------|-----------|
| 608ZZ bearing seat | 22.15mm bore × 7.2mm deep | ±0.05mm |
| N20 motor clip | 12.2 × 10.2 × 25mm | ±0.1mm |
| SG90 servo pocket | 22.4 × 12.2 × 12mm | ±0.1mm |
| Heat-set insert hole | 4.8mm bore × 5.5mm deep | ±0.05mm |
| 8mm shaft bore | 8.1mm (0.1mm clearance) | ±0.05mm |
| M3 bolt clearance | 3.2mm | ±0.1mm |
| M3 bolt head recess | 5.8mm × 3.2mm | ±0.1mm |

### Minimum Wall Thicknesses (PLA on CTC Bizer)
| Part Type | Minimum | Recommended |
|-----------|---------|-------------|
| Structural (suspension, steering) | 2.5mm | 3.0mm |
| Body panels | 3.0mm | 4.0mm |
| Motor/servo mounts | 2.5mm | 3.0mm |
| Electronics tray | 2.0mm | 2.5mm |

### Key Dimensions (from EA-08)
- Bogie arm length: 180mm (was 120mm — verify no stale refs)
- Diff bar rod: 300mm (was 200mm — verify no stale refs)
- Wheel diameter: per EA-08 Phase 1 spec
- All parts symmetric: no mirrored STLs needed

## Audit Checks

### 1. Parse Script
- Read the target CAD script(s) from `cad/scripts/`
- Extract all dimensional parameters (look for UPPERCASE constants)
- Extract hardware fitment dimensions

### 2. Fitment Check
- Compare every bearing seat, motor clip, servo pocket, insert hole against reference table
- Flag any deviation outside tolerance

### 3. Wall Thickness Check
- Find WALL parameter(s) in each script
- Compare against minimum for that part type
- Flag any below minimum

### 4. Stale Value Check
- Search for old values: 120 (bogie), 200 (diff bar), "Ender", "PETG", "halves"
- These were all corrected in the audit — flag if any reappear

### 5. Cross-Script Consistency
- Shared dimensions (bearing seats, insert holes) must be identical across all scripts
- If auditing "all", build a consistency matrix

### 6. DFM Notes
- Check print orientation assumptions
- Verify no overhang >45° without support markers
- Check parts fit CTC Bizer bed (225 × 145 × 150mm)

### 7. Report
```
=== CAD Audit: [Script Name] ===
Fitments:     X/Y within tolerance
Wall thickness: PASS/WARN (min found: Xmm)
Stale values:  PASS/FAIL (X found)
Consistency:   PASS/FAIL (X mismatches)
Bed fit:       PASS/FAIL
Overall:       PASS / NEEDS ATTENTION
```
