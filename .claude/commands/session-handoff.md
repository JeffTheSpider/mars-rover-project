---
description: Save structured session handoff for seamless next-session pickup
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git*)
---

# Session Handoff

Save a structured handoff file capturing everything about the current session so the next session can pick up seamlessly.

## Steps

### 1. Gather Session Context
Analyse the current conversation to extract:

**What was done this session:**
- Files created or modified (check `git status` and `git diff --stat`)
- Tasks completed
- Decisions made and their rationale
- Problems encountered and how they were solved

**What's in progress:**
- Partially completed work
- Open questions waiting for answers
- Tools/processes that were started but not finished

**What's next:**
- Immediate next steps (specific and actionable)
- Blockers that need resolving
- Things to remember for next time

### 2. Check Project State
- Run `git status` to see uncommitted changes
- Check if there are modified files that should be committed
- Check memory files for consistency with current session work
- Note any running processes, servers, or tools that were set up

### 3. Write Handoff File
Create/update `docs/plans/session-handoff.md`:

```markdown
# Session Handoff — [DATE]

## Session Summary
[2-3 sentence overview of what was accomplished]

## Completed This Session
- [ ] Item 1 (files: x, y, z)
- [ ] Item 2

## In Progress
- [ ] Item with details on current state

## Next Steps (Priority Order)
1. **[First thing to do]** — context and details
2. **[Second thing]** — context
3. **[Third thing]** — context

## Decisions Made
- Decision: [what] — Rationale: [why]

## Open Questions
- Question needing answer

## Uncommitted Changes
[git status output]

## Memory Files Updated
- [list any memory files that were updated]

## Environment State
- [any servers running, tools configured, etc.]
```

### 4. Update Memory
- Update MEMORY.md if any significant new patterns or decisions were made
- Keep memory concise — session-specific details go in handoff, not memory

### 5. Backup Reminder
Remind to run backup:
```bash
cd "D:/Mars Rover Project" && tools/backup.bat
```

### 6. Confirm
Show the handoff summary to the user for review.
