---
description: List all available skills, commands, plugins, and MCP tools with usage examples
allowed-tools: Read, Glob, Grep
---

# Skill Guide — Mars Rover Project

Show all available tools, skills, and commands for this project.

## Display the following reference to the user:

---

### Project Commands (18 total — type `/command-name`)

| Command | What it does |
|---------|-------------|
| `/session-start` | Load all context at the start of a new session |
| `/session-handoff` | Save structured handoff for seamless next-session pickup |
| `/quick-audit` | Fast stale-count scan across all files (bearings, STLs, EAs) |
| `/cad-audit [name\|all]` | Re-run engineering audit on CAD scripts for fitment and consistency |
| `/deploy-scripts [name\|all]` | Copy CAD scripts to Fusion 360 Scripts directory |
| `/fusion-export` | Run BatchExportAll in Fusion 360 to re-export all 28 STLs |
| `/stl-check <part>` | Validate STL — dimensions, manifold, bed fit, print estimate |
| `/preflight <part>` | Pre-print checklist — verify STL, bed fit, filament, Cura/GPX |
| `/print-log <part>` | Log a print attempt with settings and results |
| `/tolerance-calc <feature> <dim>` | Calculate fit tolerances for PLA on CTC Bizer |
| `/rod-cutting` | Calculate 8mm steel rod cutting plan from parametric dimensions |
| `/assembly-order` | Optimal print and assembly sequence with timeline |
| `/bom-check` | Cross-reference BOM against CAD, STL, print, and order status |
| `/firmware-validate` | Full pipeline: compile + 42 tests + lint + stale constant check |
| `/wiring-check` | Cross-check wiring diagrams vs firmware pins vs EA docs |
| `/esp32-deploy` | Compile firmware and generate/run upload command |
| `/project-dashboard` | Generate interactive HTML status dashboard |
| `/skill-guide` | This guide |

### Installed Plugin Commands

| Command | Plugin | What it does |
|---------|--------|-------------|
| `/commit` | commit-commands | Create a git commit from current changes |
| `/commit-push-pr` | commit-commands | Commit, push, and create a PR in one go |
| `/clean-gone` | commit-commands | Clean up local branches deleted on remote |
| `/feature-dev <desc>` | feature-dev | 7-phase guided feature development |
| `/brainstorm` | superpowers | Structured brainstorming session |
| `/write-plan` | superpowers | Create an implementation plan |
| `/execute-plan` | superpowers | Execute a previously written plan |
| `/ralph-loop "task"` | ralph-loop | Autonomous loop — Claude keeps working until done |
| `/cancel-ralph` | ralph-loop | Stop the Ralph loop |
| `/hookify <rule>` | hookify | Create hook rules to prevent unwanted behaviours |
| `/hookify:list` | hookify | List all hookify rules |
| `/hookify:configure` | hookify | Enable/disable hookify rules |
| `/revise-claude-md` | claude-md-management | Update CLAUDE.md with session learnings |
| `/coderabbit:review` | coderabbit | Run CodeRabbit AI code review |
| `/simplify` | code-simplifier | Simplify and refine recently changed code |

### Auto-Skills (trigger automatically)

| Skill | When it activates |
|-------|------------------|
| orchestrator | Every task — prompts proactive use of all 18 commands + MCP tools |
| code-simplifier | After writing/editing code |
| frontend-design | When building web UI components |
| security-guidance | When editing files (hook checks for vulnerabilities) |
| engineering (standup, architecture, etc.) | When discussing engineering workflows |
| design (critique, UX, accessibility) | When discussing design |
| productivity (tasks, memory) | When managing tasks and context |
| operations (process, vendor, compliance) | When discussing operations |
| superpowers (debugging, TDD, verification) | 14 auto-skills for various dev workflows |

### MCP Servers (10 configured)

| Server | Key Tools |
|--------|-----------|
| fusion360 | python, system (UI automation), terminal (serial/SSH), context7 (docs), sqlite |
| 3dprint | get_stl_info, slice, scale, rotate, visualize, print_3mf |
| github | Issues, PRs, code search, repository management |
| mermaid | Generate diagrams (SVG/PNG/PDF) |
| math | SymPy/SciPy calculations, unit conversion |
| kicad | PCB/schematic tools (needs KiCad) |
| cadquery | Parametric CAD modelling |
| jlcpcb | Component search and BOM |
| text-to-model | 64 Fusion 360 CAD tools (disabled — enable when F360 running) |

### Quick Reference

```
Session:         /session-start (begin) → /session-handoff (end)
Audit:           /quick-audit → /cad-audit → /wiring-check → /bom-check
Print workflow:  /stl-check → /preflight → print → /print-log
CAD workflow:    edit script → /deploy-scripts → /fusion-export
Dev workflow:    /feature-dev → /firmware-validate → /esp32-deploy → /commit
Planning:        /assembly-order → /rod-cutting → /tolerance-calc
Status:          /project-dashboard → /bom-check
```

---
