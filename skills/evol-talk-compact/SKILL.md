---
name: evol-talk-compact
description: Compresion de output del orquestador Evol-DD. 3 niveles. Ahorro tokens ~50-75%.
category: compression
trigger: /compact-talk
---

# evol-talk-compact

## Philosophy
Orquestador output compression inspired by caveman (juliusbrussee/caveman, MIT).

## Levels
- **light**: Remove redundant headers, keep technical precision
- **medium**: Fragment sentences, drop articles/fillers
- **aggressive**: Keep only technical terms + action verbs

## Example Transformations
| Original | Compacted |
|----------|-----------|
| "The answer is 4." | "4" |
| "Based on the information provided, the answer is..." | "[info provided] → ..." |
| "I will now execute the following command..." | "Exec: ..." |

## When to Use
- Orchestrator verbose output
- Multi-agent coordination logs
- CI/CD pipeline output

## Reference
skills/evol-talk-compact/SKILL.md


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
