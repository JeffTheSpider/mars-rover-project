---
name: rover-orchestrator
description: Meta-skill that prompts proactive use of all installed plugins, project commands, and MCP tools for every task. Activates on all engineering, firmware, CAD, printing, and project management tasks.
---

# Rover Orchestrator — Proactive Skill Usage

You have an extensive toolkit for the Mars Rover project. **Before starting any task, check this list and use the most relevant tools.** Do not rely on memory alone — consult this skill.

## Decision Matrix: Which Tools to Use

### When writing or modifying CODE (firmware, ROS2, PWA):
1. **Before**: Read relevant EA docs for specs/constraints
2. **During**: Use `security-guidance` hook (automatic), follow `code-simplifier` suggestions
3. **After**: Run `/firmware-validate` (if ESP32), use `code-simplifier` auto-skill, consider `/commit`
4. **Review**: Launch `pr-review-toolkit` agents or `/coderabbit:review`

### When working on CAD/3D PRINTING:
1. **Design**: Check `cad/reference/SKILL.md` for Fusion 360 rules (cm units, Z-negation)
2. **Dimensions**: Use `/tolerance-calc` for mating parts, cross-ref EA-08 and hardware fitments
3. **Audit**: Run `/cad-audit` after any script changes
4. **Export**: Run `/fusion-export` when scripts are updated
5. **Pre-print**: Always run `/preflight <part>` before printing
6. **Post-print**: Log with `/print-log <part>`

### When PLANNING or MANAGING the project:
1. **Status**: Run `/bom-check` or `/project-dashboard` for current state
2. **Planning**: Use `/assembly-order` for print/build sequence
3. **Brainstorming**: Use `/brainstorm` (superpowers) for open-ended exploration
4. **Feature work**: Use `/feature-dev` for structured development
5. **Big tasks**: Use `/ralph-loop` for autonomous extended work
6. **Plans**: Use `/write-plan` then `/execute-plan` (superpowers)

### When DEBUGGING or INVESTIGATING:
1. **Firmware**: `/firmware-validate` first, then `systematic-debugging` skill (superpowers)
2. **Wiring**: `/wiring-check` to cross-reference all sources
3. **Mechanical**: `/tolerance-calc` for fit issues, `/cad-audit` for dimension errors
4. **Root cause**: Use superpowers `root-cause-tracing` skill

### When starting or ending a SESSION:
1. **Start**: Read `docs/plans/session-handoff.md` (if exists) and memory files
2. **End**: Run `/session-handoff` to save context, run `tools/backup.bat`
3. **CLAUDE.md**: Run `/revise-claude-md` if significant learnings this session

### When doing CALCULATIONS:
1. **Math**: Use the `math` MCP server (SymPy/SciPy) for engineering calculations
2. **Tolerances**: Use `/tolerance-calc` for fit calculations
3. **Electrical**: Use math MCP for voltage dividers, current, power calcs
4. **Structural**: Use math MCP for stress, moment, deflection calcs

### When creating DOCUMENTATION or DIAGRAMS:
1. **Diagrams**: Use `mermaid` MCP for flowcharts, wiring, architecture
2. **Docs**: Follow EA-XX numbering convention for engineering analyses
3. **Quality**: Use `claude-md-management` for CLAUDE.md maintenance

## MCP Tools — Don't Forget These Exist
- **fusion360 → python**: Run arbitrary Python — great for data processing, file ops
- **fusion360 → system**: Windows UI automation (screenshots, clicks) — for Fusion 360 control
- **fusion360 → terminal**: Serial, SSH, BLE, WebSocket — for ESP32 comms
- **fusion360 → context7**: Pull library documentation mid-conversation
- **3dprint**: STL analysis, slicing, dimension checking
- **math**: Any engineering calculation (don't do it by hand!)
- **jlcpcb**: Component lookup for parts ordering
- **github**: PR management, issues, code search

## Key Reminder
Charlie wants ALL plugins and skills used proactively. Don't wait to be asked — if a skill is relevant, use it. When in doubt, run `/skill-guide` to see the full list.
