---
name: evol-fs-context
description: Filesystem-paradigm context curation. Treat large data as files mounted by agents.
category: context-engineering
trigger: /fs-context
---

# evol-fs-context

## Philosophy
Large data should be treated as files mounted by agents, not passed in context. Filesystem paradigm.

## When to Use
- Data > 50KB that doesn't fit in context
- Log files, datasets, large documents
- Streaming data processing

## Pattern
```
/fs-context mount <path> [--read-only]
/fs-context unmount <path>
/fs-context list
```

## Implementation
- Use file reads with offset/limit for large files
- Stream processing for multi-GB data
- Memory-mapped files for random access
- Virtual filesystem abstraction

## Reference
skills/evol-fs-context/SKILL.md

## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
