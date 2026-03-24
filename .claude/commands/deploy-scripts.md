---
description: Deploy changed CAD scripts from cad/scripts/ to Fusion 360 Scripts directory
argument: optional — specific script name, or "all" to deploy everything
---

# Deploy CAD Scripts to Fusion 360

Copy updated Python scripts from `D:/Mars Rover Project/cad/scripts/` to the Fusion 360 Scripts folder.

## Fusion 360 Scripts Directory
`C:/Users/charl/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts/`

## Convention
- Source: `cad/scripts/snake_case_name.py`
- Target: `Scripts/PascalCaseName/PascalCaseName.py`
- Convert `snake_case` → `PascalCase` for folder and file name

## Steps

1. If `$ARGUMENTS` is a specific script name, deploy just that one. If "all" or empty, deploy all active scripts.

2. **Active scripts** (deploy these): Every `.py` file in `cad/scripts/` EXCEPT:
   - `generate_rover_params.py` (library, not a Fusion script)
   - `batch_export_all.py` (deployed separately as BatchExportAll)
   - `batch_fix_remaining.py` (one-time utility)
   - `rover_assembly.py` (assembly script, not standalone component)
   - `rover_interactive_assembly.py` (assembly script)
   - `suspension_assembly.py` (assembly script)
   - Deprecated: `rocker_arm.py`, `bogie_arm.py`, `diff_bar_adapter.py`
   - Superseded: `rover_wheel.py`, `rover_wheel_v2.py`

3. For each script:
   - Convert filename to PascalCase
   - Create target directory if it doesn't exist
   - Copy the file
   - Report success/failure

4. After deployment, run `ls` on the Fusion Scripts directory to verify.

5. Report: X scripts deployed, any errors, reminder to restart Fusion 360 if it's running.
