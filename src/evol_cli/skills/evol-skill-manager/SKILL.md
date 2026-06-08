---
name: evol-skill-manager
description: Lifecycle management for skills (install, update, rollback, validate).
category: lifecycle
trigger: /skill
---

# evol-skill-manager

## Mission
Manage skill lifecycle: install, update, rollback, validate.

## Commands
```bash
# List installed skills
/evol skill list

# Install from GitHub
/evol skill install <repo-url>

# Update to latest
/evol skill update <skill-name>

# Rollback to previous
/evol skill rollback <skill-name> --version=<version>

# Validate
/evol skill validate <skill-name>

# Remove
/evol skill remove <skill-name>
```

## Lifecycle
1. **Install**: Validate frontmatter, scan supply-chain, copy to skills/
2. **Update**: Pin by commit SHA (not branch/tag), scan again
3. **Rollback**: Restore from skills/<name>/.retired/
4. **Validate**: Ensure SKILL.md + eval suite exist

## Supply-Chain
- gitleaks: detect secrets
- semgrep: detect dangerous patterns
- Block install if either fails

## Reference
scripts/evol-evolve.py (sync-community, install-skill)
skills/evol-skill-manager/SKILL.md

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
