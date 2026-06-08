---
name: evol-sandbox
description: Provider-agnostic sandbox skill. Backends E2B, Daytona, Microsandbox, local docker, none.
category: security
trigger: /sandbox
---

# evol-sandbox

## Philosophy
Sandbox execution for untrusted code. Multiple backend support with graceful fallback.

## Backends
- **E2B**: cloud sandbox (requires API key)
- **Daytona**: cloud sandbox (requires credentials)
- **Microsandbox**: lightweight local isolation
- **local-docker**: docker-based isolation
- **none**: no sandbox (insecure, requires explicit flag)

## When to Use
- Running untrusted code
- Security testing (fuzzing, penetration testing)
- Contract test execution
- Stress testing

## Commands
```
/sandbox exec --backend=<backend> <command>
/sandbox list
/sandbox status
/sandbox health
```

## Security Rules
- Never execute untrusted code outside sandbox
- Scan with evol-shield before sandbox execution
- Log all sandbox executions

## Reference
skills/evol-sandbox/SKILL.md

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
