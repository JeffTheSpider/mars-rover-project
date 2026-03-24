# CTC Bizer 3D Printer — Setup & Operation Guide

## Printer Specifications

| Spec | Value |
|------|-------|
| Model | CTC 3D Bizer (MakerBot Replicator 1 Dual clone) |
| Build volume | 225 × 145 × 150mm |
| Extruders | Dual (use LEFT only for this project) |
| Nozzle diameter | 0.4mm |
| Firmware | MakerBot/Sailfish |
| File format | x3g (NOT standard gcode) |
| Heated bed | Yes (aluminium) |
| Connectivity | SD card only |

---

## Initial Setup (First Use After Long Storage)

### 1. Mechanical Checks

- [ ] Check all belt tension (X and Y). Belts stretch over time — should be firm, not slack.
- [ ] Check that both Z-axis threaded rods turn freely
- [ ] Verify X carriage slides smoothly on rods
- [ ] Check all 4 bed levelling thumbscrews turn freely
- [ ] Inspect extruder gears for PLA dust buildup — clean with compressed air
- [ ] Ensure filament guide tubes are clear

### 2. Right Nozzle — Park or Remove

The CTC Bizer has dual nozzles. For single-extruder printing (our case):

**Option A (Recommended):** Remove right nozzle assembly entirely
- Prevents catching on prints
- Reduces carriage weight (faster acceleration)

**Option B:** Park the right nozzle
- Raise it 1-2mm above the left nozzle using the set screw
- Ensure it cannot snag on printed parts

### 3. Bed Levelling

1. Home all axes
2. Move nozzle to front-left corner
3. Place sheet of paper between nozzle and bed
4. Adjust thumbscrew until paper slides with slight resistance
5. Repeat for front-right, rear-right, rear-left
6. Re-check front-left (adjusting corners affects others)
7. Check centre last
8. Repeat full cycle until all 5 points are consistent

**Tip**: Use a 0.1mm feeler gauge instead of paper for more consistent results.

### 4. Nozzle Cleaning (After Storage)

1. Heat nozzle to 220°C
2. Push nylon filament through (cold pull material)
3. Let cool to 90°C
4. Pull nylon sharply — should bring old debris
5. Repeat 3-5 times until pull comes out clean
6. Switch to PLA, purge 50mm

---

## GPX Workflow — gcode to x3g Conversion

The CTC Bizer runs x3g files, not standard gcode. Use GPX to convert.

### Command

```bash
gpx -m cr1d input.gcode output.x3g
```

- `-m cr1d`: Machine profile for CTC Bizer (Replicator 1 Dual)
- GPX location: `C:\Users\charl\bin\gpx.exe`
- GPX version: 2.6.8

### Full Slicer Workflow

```
Fusion 360 → Export STL
     ↓
Cura → Open STL → Slice → Save as .gcode
     ↓
Terminal:  gpx -m cr1d part_name.gcode part_name.x3g
     ↓
Copy .x3g to SD card (FAT32)
     ↓
Insert SD → CTC Bizer menu → Print from SD → Select file
```

### SD Card Notes

- **Format**: FAT32 (not exFAT or NTFS)
- **Filenames**: Keep under 31 characters, no spaces (use underscores)
- **Root directory**: Place x3g files in root, not subfolders
- **Card size**: 2-8GB recommended (16GB+ may not be recognized)

---

## Temperature Settings (PLA)

| Parameter | Value |
|-----------|-------|
| Nozzle temperature | 200-210°C |
| Bed temperature | 60°C |
| First layer nozzle | 210°C (slightly higher for adhesion) |
| First layer bed | 65°C |
| Heat-set insert install | 170-180°C (soldering iron tip) |

### Temperature Tuning

If you see:
- **Stringing** between parts → Lower temp 5°C, increase retraction
- **Poor layer adhesion** → Raise temp 5°C
- **Warping/lifting** → Raise bed temp 5°C, add brim, use glue stick
- **Elephant foot** (first layer too squished) → Raise Z offset slightly

---

## Retraction Settings

The CTC Bizer likely has a **direct drive** extruder:

| Setting | Value |
|---------|-------|
| Retraction distance | 1-2mm |
| Retraction speed | 25mm/s |
| Z-hop | 0.2mm (optional, helps with zits) |
| Combing | Within infill |
| Wipe | Enabled |

**Note**: If using a Bowden tube setup, increase retraction to 4-6mm.

---

## Print Speed Guidelines

The CTC Bizer is slower than modern printers. Conservative speeds recommended:

| Feature | Speed (mm/s) |
|---------|-------------|
| Perimeters (outer) | 30-35 |
| Perimeters (inner) | 40-45 |
| Infill | 45-50 |
| First layer | 20-25 |
| Travel | 80-100 |
| Bearing seats | 25-30 |
| Support | 40 |

**Expect 10-20% longer print times** compared to Ender 3 / Prusa estimates.

---

## Bed Adhesion

### For Small Parts (< 80mm footprint)
- Heated bed at 60°C
- Clean bed with IPA
- No brim needed (skirt only)

### For Medium Parts (80-150mm footprint)
- Heated bed at 60°C
- 5mm brim, 3 lines
- Painter's tape OR thin glue stick layer

### For Large Parts (body quadrants, 220×130mm)
- Heated bed at 65°C
- 8mm brim, 5 lines
- Glue stick applied fresh before each print
- Close any drafts/enclosures if possible
- Consider raft for extremely warpy parts (adds ~30min)

---

## Cooling Fan

The CTC Bizer's stock part cooling may be inadequate:

- **Check**: Does your CTC Bizer have an active part cooling fan?
- **If yes**: Set to 100% after layer 3 for PLA
- **If no**: Reduce print speed by 20%, add external desk fan pointed at print
- **Bridge test**: Print a simple bridge test to assess cooling capability

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Print not sticking | Bed too low / dirty | Re-level, clean with IPA, apply glue stick |
| Stringing between parts | Temp too high / retraction low | Lower nozzle 5°C, increase retraction |
| Layer separation | Temp too low / draft | Raise nozzle 5°C, eliminate drafts |
| Nozzle clog | Old filament debris | Cold pull with nylon at 90°C |
| X/Y shift mid-print | Loose belt | Tighten X/Y belts |
| Z wobble | Bent threaded rod / loose coupling | Check Z couplers, straighten rod |
| Clicking extruder | Nozzle clog / too fast | Clean nozzle, reduce speed |
| First layer too squished | Z too low | Raise bed screws slightly |
| Warping on large parts | Bed adhesion / temperature | Brim + glue stick + 65°C bed |

---

## Maintenance Schedule

| Frequency | Task |
|-----------|------|
| Every print | Clean bed with IPA, check first layer |
| Every 5 prints | Check belt tension, clean extruder gear |
| Every 10 prints | Lubricate Z rods (light machine oil) |
| Monthly | Cold pull, check all screws, re-level bed |
| Before long storage | Run filament out, cold pull, cover printer |
