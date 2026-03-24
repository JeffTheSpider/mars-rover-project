# Fusion 360 MCP Setup Guide

## Prerequisites

1. **Install Fusion 360** (free for personal/hobby use):
   - Go to https://www.autodesk.com/products/fusion-360/personal
   - Create an Autodesk account (or sign in)
   - Download and install Fusion 360
   - Launch it once to complete setup

## MCP Server Installation

### Option A: ClaudeFusion360MCP (Recommended)

Best Claude integration with skill files for 3D spatial understanding.

```bash
# Clone the repo
git clone https://github.com/rahayesj/ClaudeFusion360MCP.git

# Follow the repo's install instructions for the Fusion 360 add-in
# Typically: copy the add-in folder to Fusion 360's Scripts & Add-Ins directory
```

Fusion 360 add-in directory (Windows):
```
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\
```

### Option B: fusion-mcp-server (Joe Spencer)

Lighter weight, exposes Fusion API tools directly.

```bash
git clone https://github.com/Joe-Spencer/fusion-mcp-server.git
```

## Claude Code MCP Configuration

Add to `~/.claude/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "fusion360": {
      "command": "python",
      "args": ["path/to/fusion-mcp-server/server.py"],
      "env": {}
    }
  }
}
```

The exact config depends on which MCP server is chosen — check the repo's README for the correct command and args.

## What Claude Can Do With Fusion 360 MCP

- Create parametric sketches (lines, circles, rectangles, arcs, splines)
- Extrude, revolve, sweep, loft operations
- Apply fillets, chamfers, shells, patterns
- Build multi-component assemblies with joints
- Set parameters and dimensions programmatically
- Export to STL (for 3D printing), STEP, 3MF
- Read existing design data (components, parameters, features)

## Rover CAD Plan

Once connected, Claude will use the dimensions from EA-08 to create:

1. **Chassis body** (440x260mm base plate, segmented for CTC Bizer 225x145mm bed)
2. **Rocker arms** (2x, with 608ZZ bearing mounts)
3. **Bogie arms** (2x, with wheel mounts)
4. **Differential bar** (connects left/right rockers)
5. **Wheel hubs** (6x, 80mm diameter)
6. **Steering brackets** (4x, servo mount + wheel pivot)
7. **Motor mounts** (6x, for N20 motors)
8. **Electronics enclosure** (ESP32 + L298N mount)
9. **Battery tray** (2S LiPo holder)

All parts designed for PLA printing on CTC Bizer (225x145mm bed). Phase 2 upgrade to PETG/ASA printer.
Parametric dimensions linked to EA-08 constants for easy scaling.
