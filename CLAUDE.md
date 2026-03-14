# Mars Rover Garden Robot - Project Instructions

## Overview
Mars rover-inspired outdoor robot for garden and park use. Rocker-bogie suspension, 6 wheels, AI vision, robotic arms, solar power, coffee table mode.

## Project Location
- Root: `D:\Mars Rover Project\`
- Design doc: `docs/plans/2026-03-14-mars-rover-design.md`
- CAD files: `cad/` (Fusion 360, to be created)
- Firmware: `firmware/esp32/` (ESP32-S3 motor controller)
- Software: `software/jetson/` (ROS2, AI, web server)
- App: `software/pwa/` (Phone control app)
- 3D print files: `3d-print/` (STL exports from Fusion 360)

## Key Specs
- Size: 1100mm x 650mm x 1050mm (driving) / 450mm (coffee table)
- Weight: 25-35kg (metal version)
- Suspension: Rocker-bogie (6 wheels, 4 steered)
- Power: 6S LiPo 20Ah (444Wh) + 100W solar
- Compute: Jetson Orin Nano (AI) + ESP32-S3 (motors/sensors)
- Budget: ~1,500-2,000

## Build Phases
1. **Phase 1** (0.4 scale): PLA/PETG prototype, ESP32 only, basic driving
2. **Phase 2** (full scale): 3D printed + aluminium extrusion, all electronics
3. **Phase 3** (full scale): Machined metal, weatherproof, production quality

## Development Environment
- OS: Windows 11
- CAD: Fusion 360
- 3D Printer: Ender 3 (220x220x250mm)
- Firmware: Arduino/PlatformIO (ESP32-S3)
- Jetson: Ubuntu + ROS2 Humble
- Phone app: PWA (HTML/CSS/JS)

## Conventions
- ESP32 firmware follows same patterns as Clock/Lamp projects (single translation unit, .h includes, non-blocking state machines)
- Phone PWA follows Hub patterns (Catppuccin Mocha, WebSocket, service worker)
- All measurements in millimetres unless stated
- Document all design decisions in design doc
