---
description: Fast consistency check — scan for stale counts across all project files
---

# Quick Audit — Stale Count Scanner

Rapid grep-based scan for common stale values across the project. Much faster than a full 6-agent audit.

## Checks to Run (all via grep)

1. **Bearing count**: Grep for `\b8\b.*bearing|bearing.*\b8\b|8x 608|8× 608` — should all be 9
2. **STL count**: Grep for `\b29\b.*STL|STL.*\b29\b|29 exports|30 exports` — should be 28
3. **EA doc count**: Grep for `EA-00.*EA-2[0-6]|2[2-7] engineering` — should reference EA-00 to EA-27 (28 docs)
4. **CI range**: Grep for `seq.*0 2[0-6]` — should be `seq 0 27`
5. **Deprecated parts**: Grep for `RockerArm|BogieArm|DiffBarAdapter|DifferentialLink` in active files (not changelogs/deprecation notes)
6. **Stale printer**: Grep for `Ender 3|PETG` in Phase 1 context — should be CTC Bizer / PLA
7. **Rod count**: Grep for `1m rod|1 rod|1x.*rod` — should be 2x 1m rods
8. **Stale component dims**: Grep for `69.{0,5}mm.*ESP|ESP.*69|37mm.*motor|motor.*37mm|70.{0,5}35.{0,5}18.*lipo` — should be ESP32 63mm, N20 24mm, LiPo 86×34×19mm
9. **Script count**: Grep for `33 CAD|33 script` — should be 45 total (23 active part scripts + 4 deprecated + 6 reference + 2 superseded + 1 shared module + 9 utilities)

## Output Format

For each check, report:
- PASS: No stale references found
- WARN: X stale references found in Y files (list them)

## Exclusions
- Skip `CHANGELOG.md` (historical records)
- Skip `audit-report-*.md` (historical snapshots)
- Skip `.git/` directory
- Skip `cad/reference/` (third-party code)
