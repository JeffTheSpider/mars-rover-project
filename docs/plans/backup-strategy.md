# Backup Strategy

## Overview

The Mars Rover project is backed up to 3 locations:

| Location | Path | Type |
|----------|------|------|
| Primary (working copy) | `D:\Mars Rover Project\` | SSD (Samsung 990 PRO) |
| Local backup | `C:\Backups\Mars Rover Project\` | NVMe boot drive |
| External backup | `E:\Backup\Mars Rover Project\` | 8TB Seagate Barracuda HDD |

## Backup Method

**Robocopy mirror** (`/MIR`) — creates an exact copy, deleting files from the destination that no longer exist in the source.

Excludes: `.git`, `__pycache__`, `node_modules`

### Manual Backup Command

Create a `.bat` file and run via `cmd.exe` (Git Bash mangles the `/MIR` flag):

```bat
@echo off
robocopy "D:\Mars Rover Project" "C:\Backups\Mars Rover Project" /MIR /XD .git __pycache__ node_modules /NFL /NDL /NJH /NJS /NC /NS
robocopy "D:\Mars Rover Project" "E:\Backup\Mars Rover Project" /MIR /XD .git __pycache__ node_modules /NFL /NDL /NJH /NJS /NC /NS
echo Backup complete.
```

Save as `D:\Mars Rover Project\tools\backup.bat` and run:
```bash
cmd.exe //c "D:\\Mars Rover Project\\tools\\backup.bat"
```

### Git Bash Workaround

Robocopy flags like `/MIR` get mangled by Git Bash's POSIX path conversion. Always run robocopy via a `.bat` file executed through `cmd.exe //c`, never directly in Git Bash.

## Backup Schedule

- **After every commit session** — run backup manually
- **Before any destructive operation** — branch deletion, force push, file restructuring
- **Weekly** — as part of Charlie's existing Sunday 10am backup script (`D:\Pc Upgrades\weekly-backup.ps1`)

## What's Backed Up

- All source code (firmware, ROS2, PWA)
- All engineering documents (EA-00 through EA-21)
- All planning documents (design doc, shopping list, todo)
- CAD scripts and parameters
- Reference research documents
- Datasheets directory

## What's NOT Backed Up

- `.git` directory (git history lives only on D: drive — push to GitHub for offsite)
- `__pycache__` and `node_modules` (regeneratable)
- Build artifacts (regeneratable via compile)

## Recovery

To restore from backup:
```bash
# From C: drive
robocopy "C:\Backups\Mars Rover Project" "D:\Mars Rover Project" /MIR /XD .git

# From E: drive
robocopy "E:\Backup\Mars Rover Project" "D:\Mars Rover Project" /MIR /XD .git
```

Note: Exclude `.git` when restoring to preserve the working git repository on D:.

## Verification

After backup, verify latest files are present:
```bash
ls -la "C:/Backups/Mars Rover Project/docs/engineering/00-master-handbook.md"
ls -la "E:/Backup/Mars Rover Project/docs/engineering/00-master-handbook.md"
```
