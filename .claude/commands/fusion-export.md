---
description: Run BatchExportAll in Fusion 360 to re-export all STL files
allowed-tools: Bash(*), Read, Glob, Grep
---

# Fusion 360 BatchExportAll Automation

Automate running the BatchExportAll script in Fusion 360 to re-export all rover STL files.

## Context
- BatchExportAll script produces **29 STL files** (4 body quadrants, 4 top deck tiles, 5 suspension connectors, 1 cable clip, 1 tube test piece, plus individual parts)
- Scripts are at `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\BatchExportAll\`
- Repo copies at `cad/scripts/BatchExportAll/`
- STL output dirs: `3d-print/{calibration,wheels,suspension,steering,drivetrain,body,gcode}`

## Steps

### 1. Pre-Export Check
- Verify Fusion 360 is running (use `tasklist | grep -i fusion` or the system MCP `list_windows`)
- Check if any CAD scripts have been modified since last export:
  - Compare timestamps of `cad/scripts/*/` against `3d-print/**/*.stl`
  - List which scripts have changes that need re-export

### 2. Run BatchExportAll
Use the Fusion 360 UI automation tools:
```powershell
# Use the search_and_run_script.ps1 helper
powershell -ExecutionPolicy Bypass -File "D:\Mars Rover Project\tools\search_and_run_script.ps1" -ScriptName "BatchExportAll"
```

If the PowerShell script is unavailable, use the system MCP tools:
1. `list_windows` to find Fusion 360
2. Open Scripts dialog (Shift+S or Tools → Scripts)
3. `click_at_screen_coordinates` to search field
4. Type "BatchExportAll"
5. Click the result to run it

### 3. Wait and Monitor
- Wait for export to complete (watch for messageBox dialog with OK button)
- Use `tools/click_ok_dialog.ps1` to dismiss completion dialogs
- Typical export time: 2-5 minutes for all 29 parts

### 4. Verify Exports
After completion, verify all expected STL files exist and are recent:
```
Expected STL files (29 total):
- 3d-print/calibration/calibration_test_card.stl
- 3d-print/calibration/bearing_test_piece.stl
- 3d-print/calibration/tube_socket_test.stl
- 3d-print/wheels/rover_wheel_v3.stl
- 3d-print/wheels/rover_tire.stl
- 3d-print/suspension/rocker_hub_connector.stl
- 3d-print/suspension/bogie_pivot_connector.stl
- 3d-print/suspension/front_wheel_connector.stl
- 3d-print/suspension/middle_wheel_connector.stl
- 3d-print/suspension/cable_clip.stl
- 3d-print/suspension/differential_pivot_housing.stl
- 3d-print/steering/steering_horn_link.stl
- 3d-print/steering/steering_bracket.stl
- 3d-print/steering/steering_knuckle.stl
- 3d-print/steering/fixed_wheel_mount.stl
- 3d-print/steering/servo_mount.stl
- 3d-print/body/body_quadrant_fl.stl
- 3d-print/body/body_quadrant_fr.stl
- 3d-print/body/body_quadrant_rl.stl
- 3d-print/body/body_quadrant_rr.stl
- 3d-print/body/top_deck_fl.stl
- 3d-print/body/top_deck_fr.stl
- 3d-print/body/top_deck_rl.stl
- 3d-print/body/top_deck_rr.stl
- 3d-print/body/electronics_tray.stl
- 3d-print/body/strain_relief_clip.stl
- 3d-print/body/fuse_holder_bracket.stl
- 3d-print/body/switch_mount_plate.stl
- 3d-print/body/battery_tray.stl
```
- Check file sizes (should be >1KB, warn if suspiciously small)
- Check timestamps (should all be within last 10 minutes)
- Report any missing files

### 5. Summary
Report: X/29 STL files exported successfully, any failures, total export size.
