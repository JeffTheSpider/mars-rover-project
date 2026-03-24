---
description: Fast consistency check — scan for stale counts across all project files
---

# Quick Audit — Stale Count Scanner

Rapid grep-based scan for common stale values across the project. Much faster than a full 6-agent audit.

## Checks to Run (all via grep)

1. **Bearing count**: Grep for `\b8\b.*bearing|bearing.*\b8\b|8x 608|8× 608` — should all be 9
2. **STL count**: Grep for `\b30\b.*STL|STL.*\b30\b|30 exports` — should be 28
3. **EA doc count**: Grep for `EA-00.*EA-24|EA-00.*EA-25|25 engineering|26 engineering|22 engineering` — should reference EA-00 to EA-26 (27 docs)
4. **CI range**: Grep for `seq.*0 25|seq.*0 24` — should be `seq 0 26`
5. **Deprecated parts**: Grep for `RockerArm|BogieArm|DiffBarAdapter` in active files (not changelogs)
6. **Stale printer**: Grep for `Ender 3|PETG` in Phase 1 context — should be CTC Bizer / PLA
7. **Rod count**: Grep for `1m rod|1 rod|1x.*rod` — should be 2x 1m rods

## Output Format

For each check, report:
- PASS: No stale references found
- WARN: X stale references found in Y files (list them)

## Exclusions
- Skip `CHANGELOG.md` (historical records)
- Skip `audit-report-*.md` (historical snapshots)
- Skip `.git/` directory
- Skip `cad/reference/` (third-party code)
