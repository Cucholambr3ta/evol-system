---
name: evol-profile
description: Workflow evol-profile
trigger: /evol evol-profile
---

# Workflow: /evol-profile

Profile management workflow for Evol-DD projects.

## Triggers

- `/evol-profile` — Guided selector showing available profiles and current project profile
- `/evol-profile list` — List all profiles from install-profiles.json
- `/evol-profile show` — Show current project's evol.profile.yml
- `/evol-profile explain <profile>` — Show modules for a profile
- `/evol-profile init <path> <profile>` — Initialize project at path with profile
- `/evol-profile upgrade <profile>` — Add modules from profile (doesn't remove existing)
- `/evol-profile validate` — Validate evol.profile.yml against manifests
- `/evol-profile downgrade <profile>` — Blocked by default; requires --force

## CLI Integration

```bash
evol profile list
evol profile show
evol profile explain developer
evol profile init ./mi-proyecto developer
evol profile upgrade full
evol profile validate
```
