# Profile System

## Overview

Profiles are predefined sets of modules that determine what Evol-DD installs in a project.
Each profile extends from another profile (except `minimal` and `lean`) and adds specific modules.

## Available Profiles

| Profile | Extends | Description |
|---------|---------|-------------|
| `minimal` | — | Core minimum with lessons and memory. For tiny projects or CI-only setups. |
| `core` | minimal | Standard for projects. Default profile. Includes agents, gate, CI and growth engine. |
| `developer` | core | Active development with ephemeral agents, hooks, lifecycle, evolution and eval. |
| `security` | core | Security focus with SecDD, strict hooks, agent shield and eval. |
| `research` | core | Research and continuous evolution with eval harness, observability and lifecycle. |
| `full` | developer | Complete installation. All modules. For maximum capability. |
| `lean` | — | Lightweight. Depends on global install. Minimal footprint. |

## Profile Management CLI

```bash
# List all profiles
evol profile list

# Show current project's profile config
evol profile show

# Show modules for a specific profile
evol profile explain developer

# Initialize new project with profile
evol profile init ./mi-proyecto developer

# Upgrade current project to a profile (additive)
evol profile upgrade full

# Validate current profile against manifests
evol profile validate
```

## Workflow Commands

Agent workflow commands via `/evol-profile`:

- `/evol-profile` — Guided selector
- `/evol-profile list`
- `/evol-profile show`
- `/evol-profile explain developer`
- `/evol-profile init ./mi-proyecto developer`
- `/evol-profile upgrade full`
- `/evol-profile validate`
- `/evol-profile downgrade <profile>` — Blocked unless `--force`

## Module Resolution

Profiles resolve modules hierarchically via the `extends` field:

1. Start from the base profile
2. Recursively resolve parent modules
3. Add current profile's modules

Example: `full` resolves to all modules from `minimal` + `core` + `developer` + `full`'s own modules.

## Manifets

- `manifests/install-profiles.json` — Profile definitions
- `manifests/install-modules.json` — Module definitions

## evol.profile.yml

Installed projects contain `evol.profile.yml` with:

```yaml
profile: developer
modules:
  - core
  - workflows-core
  # ... resolved modules
```