---
name: evol-compact
description: Provider-agnostic context compaction. Reduce tokens preserving semantics.
category: context-engineering
trigger: /compact
---

# evol-compact

## Philosophy
Context compaction must preserve semantic meaning while reducing token count.

## Strategies
1. Remove redundant examples
2. Merge similar instructions
3. Compress technical terms
4. Keep decision-critical context
5. Preserve error cases

## When to Use
- Context approaching token limit
- Large codebase navigation
- Long conversation history

## Commands
```
/compact --level=light   # 20-30% reduction
/compact --level=medium  # 40-50% reduction
/compact --level=aggressive # 60-75% reduction
```

## Reference
skills/evol-compact/SKILL.md

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
