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