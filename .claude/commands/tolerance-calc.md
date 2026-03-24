---
description: Calculate fit tolerances for mating parts on CTC Bizer PLA
argument-hint: <part1> <part2> or <feature> <nominal_dim_mm>
allowed-tools: Read, Glob, Grep, Bash(python*)
---

# Tolerance Calculator

Calculate interference/clearance fits for PLA parts printed on the CTC Bizer.

## Arguments: $ARGUMENTS

## CTC Bizer PLA Tolerances (Empirical Baseline)

These are starting values — update from print log data as we learn more:

| Feature Type | Typical Deviation | Compensation |
|-------------|-------------------|--------------|
| Hole (circular) | Shrinks 0.1-0.2mm | Add +0.15mm to radius |
| Shaft (circular) | Grows 0.05-0.15mm | Subtract -0.1mm from radius |
| Slot (rectangular) | Shrinks 0.1-0.15mm per axis | Add +0.1mm per side |
| Boss (rectangular) | Grows 0.05-0.1mm per axis | Subtract -0.1mm per side |
| Layer height (Z) | ±0.05mm per 10mm | Usually accurate |
| First layer | Elephant foot +0.2-0.4mm | Chamfer first layer or tune first layer offset |

### Fit Types
| Fit | Gap | Use Case |
|-----|-----|----------|
| Press/Interference | -0.05 to -0.15mm | Bearings in seats, permanent assemblies |
| Transition | 0.0 to +0.05mm | Snug fit, light press |
| Sliding | +0.1 to +0.2mm | Shafts in bearings, moving parts |
| Clearance | +0.2 to +0.5mm | Easy assembly, bolt through-holes |
| Loose | +0.5mm+ | Cable routing, decorative |

### Project-Specific Fits
| Mating Pair | Nominal | Fit Type | Designed Gap |
|------------|---------|----------|-------------|
| 608ZZ OD (22mm) → bearing seat | 22.15mm bore | Press fit | +0.15mm |
| 608ZZ width (7mm) → seat depth | 7.2mm deep | Clearance | +0.2mm |
| 8mm shaft → 608ZZ ID (8mm) | 8.1mm bore | Sliding | +0.1mm |
| N20 motor (12×10×24mm) → clip | 12.2×10.2×25mm | Clearance | +0.2mm |
| SG90 body (22.2×12×11.8mm) → pocket | 22.4×12.2×12mm | Clearance | +0.2mm |
| M3 bolt (3mm) → through-hole | 3.2mm | Clearance | +0.2mm |
| Heat-set M3 insert (4.6mm) → hole | 4.8mm bore | Press (melted) | +0.2mm |

## Calculation

### 1. Identify Mating Parts
Parse the arguments to determine:
- What two features are mating
- The nominal dimension(s)
- The desired fit type (ask if not specified)

### 2. Calculate
For each dimension:
```
Designed dimension = Nominal + Fit gap + Printer compensation

Where:
- Fit gap = from fit type table above
- Printer compensation = from feature type table above
  (holes get larger compensation than shafts)
```

### 3. Validate Against Existing Scripts
If the parts have CAD scripts:
- Check what dimensions are currently used
- Compare against calculated ideal
- Flag if current values are outside recommended range

### 4. Report
```
=== Tolerance Calculation ===
Feature: [description]
Nominal: XX.Xmm
Fit type: [press/sliding/clearance]
Fit gap: +X.Xmm
Printer compensation: +X.Xmm
→ Recommended design dimension: XX.Xmm
→ Currently in CAD: XX.Xmm [OK / ADJUST]

Print tip: [orientation advice for best accuracy on this feature]
```

### 5. Learn from Print Log
If `docs/plans/print-log.md` exists, check for relevant data:
- Did we print this part before?
- What was the actual fit?
- Should we adjust the baseline tolerances?
