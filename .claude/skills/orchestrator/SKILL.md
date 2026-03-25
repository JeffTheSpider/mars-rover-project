---
name: rover-orchestrator
description: Meta-skill that prompts proactive use of all installed plugins, project commands, and MCP tools for every task. Activates on all engineering, firmware, CAD, printing, and project management tasks.
---

# Rover Orchestrator — Proactive Skill Usage

You have an extensive toolkit for the Mars Rover project. **Before starting any task, check this list and use the most relevant tools.** Do not rely on memory alone — consult this skill.

## Quick Reference: 18 Project Commands

| Command | When to Use |
|---------|-------------|
| `/session-start` | Beginning of every new session |
| `/session-handoff` | End of every session |
| `/quick-audit` | After any batch of changes — fast stale count scan |
| `/cad-audit [name]` | After modifying any CAD script |
| `/stl-check <part>` | Before printing — validates STL dimensions and bed fit |
| `/preflight <part>` | Full pre-print checklist (settings, filament, GPX) |
| `/print-log <part>` | After every print attempt (success or fail) |
| `/deploy-scripts` | After editing CAD scripts — copies to Fusion 360 |
| `/fusion-export` | Re-export all STLs via BatchExportAll |
| `/rod-cutting` | Calculate steel rod cutting plan from params |
| `/tolerance-calc` | PLA fit calculator for mating parts |
| `/assembly-order` | Optimal print and assembly sequence |
| `/bom-check` | Cross-ref BOM vs CAD vs STL vs ordered |
| `/firmware-validate` | Compile + 42 tests + lint + stale constants |
| `/wiring-check` | Cross-check wiring vs firmware vs EA docs |
| `/esp32-deploy` | Compile + upload command generation |
| `/project-dashboard` | Interactive HTML status dashboard |
| `/skill-guide` | Master reference of ALL tools |

## Decision Matrix: Which Tools to Use

### CAD/3D PRINTING (current phase):
1. **Edit script** → `/deploy-scripts` → `/cad-audit`
2. **Export STLs** → `/fusion-export` in Fusion 360
3. **Before print** → `/stl-check <part>` → `/preflight <part>`
4. **After print** → `/print-log <part>` with settings + results
5. **Fit issues** → `/tolerance-calc` for CTC Bizer PLA
6. **Rod cuts** → `/rod-cutting` for steel rod plan

### CODE (firmware, ROS2, PWA):
1. **Before**: Read relevant EA docs for specs
2. **After ESP32**: `/firmware-validate` (compile + 42 tests)
3. **Upload**: `/esp32-deploy` for command generation
4. **Commit**: Use the `/commit` command (commit-commands plugin)
5. **Review**: Launch PR review agents

### PLANNING/MANAGEMENT:
1. **Status**: `/project-dashboard` or `/bom-check`
2. **Sequence**: `/assembly-order` for print/build order
3. **Session end**: `/session-handoff` + `tools/backup.bat`
4. **Session start**: `/session-start`

### CALCULATIONS:
1. **Engineering math**: `math` MCP server (SymPy/SciPy) — NEVER do manual arithmetic
2. **Tolerances**: `/tolerance-calc`
3. **Rod plans**: `/rod-cutting`

### DIAGRAMS:
1. **Mermaid**: `mermaid` MCP for flowcharts, wiring, architecture
2. **Docs**: Follow EA-XX numbering (currently EA-00 through EA-27)

## MCP Servers Available (10)
| Server | Key Tools |
|--------|-----------|
| **fusion360** | python, system (UI automation), terminal (serial/SSH), context7 (docs), sqlite |
| **3dprint** | get_stl_info, scale/rotate/translate, visualize, slice, print |
| **github** | Issues, PRs, code search, branches |
| **mermaid** | Diagram preview + save (SVG/PNG/PDF) |
| **math** | SymPy algebra, calculus, unit conversion |
| **kicad** | PCB/schematic tools (Phase 2) |
| **cadquery** | Parametric CAD (Python CSG) |
| **text-to-model** | 64 Fusion 360 CAD tools (disabled, enable when needed) |
| **jlcpcb** | Component search + BOM for ordering |

## Key Reminders
- Charlie wants ALL plugins and skills used proactively
- Run `tools/backup.bat` after significant work
- 9 bearings (not 8 or 11), 28 STLs, 28 EA docs (EA-00 through EA-27)
- CTC Bizer: 225×145×150mm bed, PLA only, x3g via GPX
- Fusion 360 API: values in cm (mm/10), Z negated on XZ/YZ planes
