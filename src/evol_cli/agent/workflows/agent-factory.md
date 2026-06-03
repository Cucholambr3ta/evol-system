---
name: /evol agent create
description: Creates ephemeral agents via guided interaction
trigger: /evol agent create
category: core
---

# Evol-Agent-Factory

## Mission
Create ephemeral agents for specialized tasks.

## Lifecycle
CREATE -> INVOKE -> RETIRE -> [RECALL]

## Commands
```bash
# Create
python3 scripts/evol-agent-lifecycle.py create \
  --name "specialist-name" \
  --task "Task description" \
  --expires-after 30

# Invoke
python3 scripts/evol-agent-lifecycle.py invoke specialist-name

# Retire
python3 scripts/evol-agent-lifecycle.py retire specialist-name

# Recall
python3 scripts/evol-agent-lifecycle.py recall specialist-name
```

## When Invoked
- `/evol agent create <name> --task <desc>`
- Ephemeral agent needed

## Constraints
- Cannot modify governance files
- Cannot create other agents
- Must register decisions in memoria.md