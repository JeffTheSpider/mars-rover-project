---
description: Load all context for a new session — memory files, handoff, project status
---

# Session Start — Context Loader

Load all persistent context at the start of a new session.

## Steps (in order)

1. **Read memory files**:
   - `~/.claude/projects/D--Mars-Rover-Project/memory/MEMORY.md`
   - `~/.claude/projects/D--Mars-Rover-Project/memory/suspension-design.md`
   - `~/.claude/projects/D--Mars-Rover-Project/memory/engineering-audit.md`
   - `~/.claude/projects/D--Mars-Rover-Project/memory/mcp-servers.md`

2. **Check for session handoff**:
   - Read `docs/plans/session-handoff.md` if it exists
   - Report what was left in progress

3. **Git status**: Run `git log --oneline -10` and `git status --short` to see recent changes

4. **Check GitHub**: Use `mcp__github__list_issues` for any open issues on `JeffTheSpider/mars-rover-project`

5. **Quick audit**: Run the stale count scanner (same checks as `/quick-audit`)

6. **Report a session brief**:
   ```
   SESSION START — Mars Rover Project
   ===================================
   Last commit: [hash] [message]
   Branch: [branch]
   Open issues: X
   Stale references: X (run /quick-audit for details)

   FROM LAST SESSION:
   [handoff summary or "No handoff file found"]

   SUGGESTED NEXT STEPS:
   [Based on project status and handoff]
   ```
