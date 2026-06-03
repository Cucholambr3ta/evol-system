---
name: /evol research
description: Autonomous research (skills, methodologies, frameworks)
trigger: /evol research
category: core
---

# Evol-Researcher

## Mission
Autonomous research on skills, methodologies, frameworks.

## Sources
- GitHub (skills, frameworks, agentic AI)
- Changelogs
- Papers
- Community trends

## Commands
```bash
# Run research
python3 scripts/evol-researcher.py run --scope system
python3 scripts/evol-researcher.py run --scope project --topic "testing"

# List proposals
python3 scripts/evol-researcher.py list

# Apply approved
python3 scripts/evol-researcher.py apply PROPOSAL_ID
```

## Output
- RESEARCH.md with ranked proposals
- Persisted in SQLite (research_proposals table)

## When Invoked
- `/evol research <scope> --topic <topic>`
- Research task