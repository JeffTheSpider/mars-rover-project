---
description: Log a 3D print attempt with settings, results, and lessons learned
argument-hint: <part name> [--result success|fail|partial]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(date*)
---

# Print Log

Log a 3D print attempt to build a database of what works on the CTC Bizer.

## Arguments: $ARGUMENTS

## Steps

### 1. Identify Part
- Match argument to a known part in `3d-print/**/*.stl`
- If not found, ask user to specify the part name and STL path
- Pull part dimensions and script info from `cad/scripts/` if available

### 2. Gather Print Details
Ask the user (using AskUserQuestion) for:

**Required:**
- Result: Success / Fail / Partial
- Print time (actual, not estimated)
- Any issues encountered

**Settings (if user knows them):**
- Layer height (default: 0.2mm)
- Infill % and pattern
- Nozzle temp / bed temp
- Support used? (yes/no/type)
- Adhesion (brim/raft/skirt/none)
- Speed

**Optional:**
- Photo path (if they took one)
- Weight of finished part
- Notes on fit/assembly test

### 3. Write Log Entry
Append to `docs/plans/print-log.md` (create if doesn't exist):

```markdown
## [Part Name] — [DATE] — [RESULT]

| Setting | Value |
|---------|-------|
| STL | `path/to/file.stl` |
| Layer height | 0.2mm |
| Infill | 30% grid |
| Nozzle temp | 200°C |
| Bed temp | 60°C |
| Supports | No |
| Adhesion | Brim 8mm |
| Print time | 2h 15m |
| Weight | 23g |

### Result
[Success/Fail/Partial] — [description]

### Issues
- [issue 1]
- [issue 2]

### Lessons Learned
- [what to do differently next time]

---
```

### 4. Update Statistics
At the top of the print-log file, maintain running stats:
```markdown
# Print Log — Mars Rover Project

## Statistics
- Total prints: X
- Successful: X (X%)
- Failed: X
- Total print time: Xh
- Total filament: Xg
- Parts completed: [list]
- Parts remaining: [list]
```

### 5. Cross-Reference
- Update the BOM status if a part was successfully printed
- Note if the part needs reprinting (bad fit, wrong settings)
- Suggest settings adjustments based on failure patterns
