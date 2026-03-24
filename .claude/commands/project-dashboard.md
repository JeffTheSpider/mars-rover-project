---
description: Generate an interactive HTML dashboard showing full project status
allowed-tools: Read, Write, Glob, Grep, Bash(*)
---

# Project Dashboard

Generate an interactive HTML dashboard showing the complete Mars Rover project status at a glance. Uses the playground plugin style — single self-contained HTML file.

## Steps

### 1. Gather Data
Read all status sources:
- `CLAUDE.md` — project status section
- `docs/plans/todo-master.md` — master task list
- `docs/plans/phase1-shopping-list.md` — parts ordering status
- `docs/plans/print-log.md` — print status (if exists)
- `cad/scripts/` — list all CAD scripts
- `3d-print/**/*.stl` — list all exported STLs
- `firmware/esp32/config.h` — firmware version
- `docs/engineering/` — list all EA docs
- `git log --oneline -20` — recent activity

### 2. Generate Dashboard HTML
Create `docs/dashboard.html` — a single self-contained HTML file with:

**Design:**
- Catppuccin Mocha colour scheme (matching the PWA)
- Mars red accent (#f38ba8)
- Responsive grid layout
- No external dependencies (inline CSS/JS)

**Sections:**

**Header:**
- Project name, Phase 1 status, firmware version
- Last updated timestamp

**Progress Ring:**
- Overall completion % (calculated from subsystem statuses)

**Subsystem Cards (grid):**
Each card shows status (not started / in progress / complete):
- CAD Design: X/29 active scripts (34 total, 3 deprecated, 2 superseded)
- STL Export: X/28 files exported
- 3D Printing: X/28 parts to print (suspension redesign EA-25/EA-26)
- Electronics: ordered/received/assembled
- Firmware: version, compile status, test results
- Wiring: harness built yes/no
- Software: PWA, ROS2 status
- Documentation: X/27 EA docs

**Parts Table:**
Sortable table of all Phase 1 parts:
- Name, CAD?, STL?, Printed?, Assembly group, Notes

**Timeline:**
Visual progress against EA-17's 14-day build plan

**Recent Activity:**
Last 10 git commits

**Print Stats:**
From print log: success rate, total hours, filament used

### 3. Auto-Refresh Data
Include a JS function that can regenerate data from a JSON object, so the dashboard can be updated by just changing the data.

### 4. Save and Open
- Save to `docs/dashboard.html`
- Tell user they can open it in a browser
- Optionally open it: `start docs/dashboard.html` (Windows)
