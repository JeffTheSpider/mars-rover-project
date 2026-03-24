---
description: Full firmware validation — compile, test, lint, check constants
allowed-tools: Bash(arduino-cli:*), Bash(python*), Bash(cd*), Bash(grep*), Read, Glob, Grep
---

# Firmware Validation Pipeline

Run the complete firmware validation pipeline in one go.

## Context
- Firmware: `D:/Mars Rover Project/firmware/esp32/`
- Tests: `D:/Mars Rover Project/firmware/tests/`
- Board: `esp32:esp32:esp32s3`
- Expected: 42 tests passing, clean compile, no lint errors

## Pipeline Steps

### 1. Compile Firmware
```bash
cd "D:/Mars Rover Project" && arduino-cli compile --fqbn esp32:esp32:esp32s3 firmware/esp32/esp32.ino
```
- Expected: ~1045KB flash (79%), ~53KB RAM (16%)
- **FAIL** if compile errors
- **WARN** if flash >90% or RAM >80%

### 2. Run Unit Tests
```bash
cd "D:/Mars Rover Project" && python -m pytest firmware/tests/ -v --tb=short
```
- Expected: 42 tests, all passing
- **FAIL** if any test fails
- Report: passed/failed/skipped counts

### 3. Lint Check
```bash
cd "D:/Mars Rover Project" && python -m flake8 firmware/tests/ --max-line-length=120 --statistics
```
- **WARN** on any lint issues (don't fail the pipeline)
- Report: issue count by type

### 4. Stale Constants Check
Verify key constants haven't drifted from engineering documents:
- `config.h`: Check BOGIE_LENGTH matches EA-01 (180mm)
- `config.h`: Check DIFF_BAR_LENGTH matches EA-01 (300mm)
- `config.h`: Check WHEEL_DIAMETER matches EA-08
- `config.h`: Check BATTERY_* thresholds match EA-03/EA-15
- `config.h`: Check PIN_* definitions match EA-09 GPIO map
- Cross-reference at least 5 constants against their EA source docs

### 5. Version Check
- Read firmware version from `config.h` or `esp32.ino`
- Compare against CHANGELOG.md
- **WARN** if version hasn't been bumped since last change

### 6. Summary
```
=== Firmware Validation Report ===
Compile:    PASS/FAIL (flash: XX%, RAM: XX%)
Tests:      PASS/FAIL (42/42 passed)
Lint:       PASS/WARN (X issues)
Constants:  PASS/WARN (X stale values found)
Version:    X.Y.Z (matches CHANGELOG: YES/NO)
Overall:    GO / NO-GO
```
