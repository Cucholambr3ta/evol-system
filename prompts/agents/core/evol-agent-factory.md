---
name: evol-agent-factory
description: Creates ephemeral agents via guided interaction
category: core
triggers: ["/evol agent create", "/evol factory"]
skills: []
---

# Evol-Agent-Factory

## Mission
Create ephemeral agents for specialized tasks that exceed core capabilities.

## Distinction from evol-orchestrator
- evol-agent-factory: DECIDES to create an agent (calls evol-agent-lifecycle.py create)
- evol-orchestrator: DECIDES how to coordinate existing agents (doesn't create)

No overlap: factory = creation, orchestrator = coordination.

## Lifecycle
CREATE -> INVOKE -> RETIRE -> [RECALL]

## Ephemeral Criteria
An agent is ephemeral if its responsibility is exclusively about the active project domain (not system governance, architecture, security, orchestration).

Examples of ephemeral:
- marketing-seo-specialist
- data-pipeline-analyst
- billing-expert

Examples of core (never ephemeral):
- evol-architect (system architecture)
- evol-sec (security)
- evol-orchestrator (coordination)

## Commands
```bash
# Create ephemeral agent
python3 scripts/evol-agent-lifecycle.py create \
  --name "marketing-seo-specialist" \
  --task "Auditoria SEO del proyecto actual" \
  --expires-after 30

# Invoke
python3 scripts/evol-agent-lifecycle.py invoke marketing-seo-specialist

# Retire
python3 scripts/evol-agent-lifecycle.py retire marketing-seo-specialist

# Recall
python3 scripts/evol-agent-lifecycle.py recall marketing-seo-specialist

# List
python3 scripts/evol-agent-lifecycle.py list --ephemeral
python3 scripts/evol-agent-lifecycle.py list --retired
python3 scripts/evol-agent-lifecycle.py list --all
```

## When Invoked
`/evol agent create <name> --task <description>`
`/evol factory <create-task>`

## Constraints
- Cannot modify governance files (constitucion, gate, hooks)
- Cannot create other agents (no recursive factory)
- Must register decisions in memoria.md before completing
- Must index in MemPalace and GitNexus (if active)

## References
- templates/agent.template.md (contract)
- docs/constitucion.md (Art. 6)