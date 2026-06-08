---
name: agent-eval
description: Eval-harness para skills/agents/workflows Evol-DD. 4 grader types. Suite por skill.
category: quality-gate
trigger: /eval
---

# agent-eval

## Philosophy
Eval harness for skills/agents/workflows. Suite per skill with cases.jsonl + grader.yaml.

## Grader Types

### structural
Verify file structure, presence of required elements.

### behavioral
Verify script behavior: exit codes, output format.

### output_match
Exact output matching for deterministic outputs.

### pass_at_k
Pass@k sampling: run k times, succeed if any pass.

### llm_judge
LLM as judge for nuanced evaluation.

## Suite Structure
```
evals/<skill-name>/
  cases.jsonl    # Test cases (one JSON per line)
  grader.yaml    # Grader configuration
```

## Commands
```
/eval run --suite=<skill-name>
/eval list
/eval report <run-id>
```

## Integration
- Runs in CI to gate merges
- Can run locally: evol eval run --suite=NAME
- Results persisted in evol-state.db

## Reference
skills/agent-eval/SKILL.md


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
