---
name: /evol evolve
description: Auto-generate skills, sync community
trigger: /evol evolve
category: core
---

# Evol-Evolve

## Mission
Auto-generate skills from instinct patterns, sync community skills.

## Commands
```bash
# Status
python3 scripts/evol-evolve.py status

# Generate proposals (dry-run)
python3 scripts/evol-evolve.py run --dry-run

# Generate proposals (requires approval)
python3 scripts/evol-evolve.py run
python3 scripts/evol-evolve.py approve CLUSTER_ID

# Invalidate anti-pattern
python3 scripts/evol-evolve.py invalidate INSTINCT_ID --reason "..."

# Rollback auto-generated skill
python3 scripts/evol-evolve.py rollback SKILL_NAME

# Sync community skills
python3 scripts/evol-evolve.py sync-community --dry-run

# Install community skill
python3 scripts/evol-evolve.py install-skill SKILL_NAME
```

## When Invoked
- `/evol evolve <action>`
- Skill generation needed