---
name: evol-ai-review
description: Quality gate review using AI for nuanced assessment.
category: quality-gate
trigger: /ai-review
---

# evol-ai-review

## Philosophy
AI-as-judge for quality gates. Supplement static checks with LLM reasoning.

## Tiers
1. **Static** (automated): grep, lint, schema validation
2. **Functional** (automated): test execution, contract testing
3. **AI Judge** (LLM): nuanced quality assessment

## When to Use
- Complex refactoring decisions
- Architecture trade-off evaluation
- Security vulnerability severity
- Documentation quality

## Commands
```
/ai-review --type=security <target>
/ai-review --type=quality <target>
/ai-review --type=architecture <target>
```

## Integration
- Run after static checks pass
- Input: code + context
- Output: assessment + confidence score

## Reference
skills/evol-ai-review/SKILL.md

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
