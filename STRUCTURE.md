# Mars Rover Garden Robot - Folder Structure

## Quick Navigation

| What you need | Where to find it |
|---------------|-----------------|
| Master design doc | `docs/plans/2026-03-14-mars-rover-design.md` |
| Engineering analyses (EA-00 to EA-30) | `docs/engineering/` |
| Shopping list / BOM | `docs/plans/phase1-shopping-list.md`, `phase1-complete-bom.md` |
| Master todo | `docs/plans/todo-master.md` |
| Assembly guide | `docs/plans/assembly-reference.md` |
| Pre-print checklist | `docs/plans/pre-print-checklist.md` |
| ESP32 firmware | `firmware/esp32/` |
| ROS2 packages (Phase 2) | `software/jetson/` |
| Phone PWA | `software/pwa/` |
| CAD scripts (Fusion 360) | `cad/scripts/` |
| Print-ready STLs | `3d-print/` (by subsystem) |
| Reference CAD models | `cad/reference/`, `cad/reference-wheels/`, `cad/reference-suspension/` |
| Wiring diagrams | `docs/diagrams/` |
| Datasheets | `docs/datasheets/` |
| Research docs | `docs/references/` |
| MCP tool servers | `tools/` |
| CI/CD pipeline | `.github/workflows/ci.yml` |
| Project CLAUDE.md | `CLAUDE.md` |

## Directory Tree

```
Mars Rover Project/
├── firmware/                     # Microcontroller code
│   ├── esp32/                    # ESP32-S3 main firmware (Arduino)
│   │   ├── esp32.ino             # Main program
│   │   ├── config.h              # Pin defs, geometry, timing
│   │   ├── motors.h              # 4-channel L298N control
│   │   ├── steering.h            # Ackermann/point turn/crab walk
│   │   ├── sensors.h             # Battery, encoders, E-stop
│   │   ├── rover_webserver.h     # HTTP + WebSocket server
│   │   ├── uart_nmea.h           # NMEA text protocol
│   │   ├── uart_binary.h         # Binary COBS+CRC protocol
│   │   ├── leds.h                # Status LEDs
│   │   └── ota.h                 # Over-the-air updates
│   └── tests/                    # Host-based firmware tests (pytest)
│
├── software/                     # Higher-level software
│   ├── jetson/                   # ROS2 packages (7 packages, Phase 2)
│   │   ├── rover_bringup/        # Launch files, URDF
│   │   ├── rover_hardware/       # UART bridge node
│   │   ├── rover_navigation/     # Ackermann controller, geofence
│   │   ├── rover_perception/     # YOLO, cameras, depth
│   │   ├── rover_autonomy/       # Behaviour trees
│   │   ├── rover_teleop/         # WebSocket bridge
│   │   └── rover_msgs/           # Custom ROS2 messages
│   └── pwa/                      # Phone control app (Catppuccin Mocha PWA)
│
├── cad/                          # CAD files and tooling
│   ├── scripts/                  # 58 Python CAD scripts (Fusion 360)
│   │   ├── rover_assembly_v2.py  # Current full assembly script
│   │   ├── batch_export_all.py   # STL export driver
│   │   ├── rover_cad_helpers.py  # Shared utility functions
│   │   └── ...                   # Per-component scripts
│   ├── reference/                # Third-party reference designs
│   ├── reference-wheels/         # Curiosity wheel V5 reference files
│   └── reference-suspension/     # Suspension reference model + extracts
│
├── 3d-print/                     # Print-ready exports (organised by subsystem)
│   ├── body/                     # Body quadrants, trays
│   ├── wheels/                   # Wheel variants
│   ├── suspension/               # Rocker arms, bogie arms, pivots
│   ├── steering/                 # Brackets, knuckles
│   ├── drivetrain/               # Wheel mounts
│   ├── calibration/              # Test pieces (bearing, tube socket)
│   ├── hardware/                 # Reference parts (bearings, bolts)
│   ├── reference-suspension/     # Full reference assembly
│   └── screenshots/              # Assembly photos
│
├── docs/                         # All documentation
│   ├── engineering/              # EA-00 to EA-30 (engineering analyses)
│   │   └── wheel-assembly/       # Wheel design breakdown docs
│   ├── plans/                    # Project plans, BOMs, checklists
│   ├── diagrams/                 # Mermaid SVG diagrams
│   ├── datasheets/               # Component datasheets
│   └── references/               # Research and background docs
│
├── tools/                        # MCP tool servers (gitignored, install locally)
│   ├── cadquery-mcp/             # CadQuery parametric CAD
│   ├── kicad-mcp/                # KiCad PCB tools
│   └── math-mcp/                 # SymPy/SciPy math
│
├── scripts/                      # Utility scripts
│   └── backup.bat                # Backup script
│
├── temp/                         # Scratch files (gitignored, safe to clear)
│
├── .claude/                      # Claude Code configuration
│   ├── commands/                 # 18 custom project commands
│   └── launch.json               # Dev server config
│
├── .github/workflows/ci.yml      # CI/CD pipeline
├── CLAUDE.md                     # Project instructions for Claude sessions
├── README.md                     # Public project overview
├── CHANGELOG.md                  # Version history
└── LICENSE                       # Project license
```

## Engineering Analysis Index

EA documents are the authoritative source for design decisions. Each is a self-contained analysis.

| EA | File | Topic |
|----|------|-------|
| 00 | `00-master-handbook.md` | Master index and conventions |
| 01-30 | See CLAUDE.md | Full index in project instructions |

## Housekeeping Rules

1. **temp/ is scratch space** - Gitignored. OK to delete contents periodically. Never commit temp files.
2. **STL exports go in `3d-print/`** - Organised by subsystem (body, wheels, suspension, steering, drivetrain). Never put STLs in `cad/scripts/`.
3. **CAD scripts go in `cad/scripts/`** - One script per component. Use `rover_cad_helpers.py` for shared functions.
4. **Reference models stay in `cad/reference*/`** - Never modify reference files. They're read-only design inputs.
5. **EA docs are append-only** - Don't delete old analyses. Update with addendums or create new EA numbers.
6. **tools/ is gitignored** - Each developer installs MCP servers locally. Don't commit virtual environments.
7. **No temp screenshots in root** - Use `temp/` for scratch screenshots, or delete after use.
8. **Commit messages reference EA numbers** - When a change relates to an engineering analysis, mention it.
9. **Use consistent directory naming** - Lowercase with dashes (e.g., `reference-suspension`, not `reference=suspension`).
10. **Large files (>50 MB)** - Add to `.gitignore`. Keep locally, don't push to GitHub.
