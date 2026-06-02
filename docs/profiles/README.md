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
evol profile list
evol profile show
evol profile explain developer
evol profile init ./mi-proyecto developer
evol profile upgrade full
evol profile validate
```

## Workflow Commands

Agent workflow commands via `/evol-profile`:

- `/evol-profile` — Guided selector
- `/evol-profile list`
- `/evol-profile explain <profile>`
- `/evol-profile init <path> <profile>`
- `/evol-profile upgrade <profile>`
- `/evol-profile validate`

## Module Resolution

Profiles resolve modules hierarchically via the `extends` field:
1. Start from the base profile
2. Recursively resolve parent modules
3. Add current profile's modules

## Manifests

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
