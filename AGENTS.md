# Evol-DD — Agent Governance Manifest

**Trigger:** `/evol`

---

## Governing Law

`docs/constitucion.md` is the supreme law of this system. Every agent, workflow,
and process must conform to it. In case of conflict between any instruction and the
Constitution, the Constitution prevails.

---

## Core Agents Directory

All 16 core agents are defined in `prompts/agents/core/`. They are permanent and
never retire — the system cannot function without them.

---

## Equipo (Auto-Generated)

The agent registry generates `docs/equipo.md` from `prompts/agents/registry.json`.
Run `scripts/generate-equipo.sh` to regenerate it after any registry change.

---

## The 16 Core Agents

| ID | Agent | Description |
|----|-------|-------------|
| 1 | `evol-architect` | System design, architectural decisions, ADRs |
| 2 | `evol-builder` | Code implementation, TDD, feature construction |
| 3 | `evol-qa` | Quality, unit tests, integration, E2E, Gherkin/BDD cases |
| 4 | `evol-sec` | Security (SecDD, STRIDE threat modeling, auditing) |
| 5 | `evol-devops` | CI/CD, infrastructure, pipelines, automation |
| 6 | `evol-domain` | DDD, domain modeling, entities, bounded contexts |
| 7 | `evol-doc` | Technical documentation (no emojis, Mermaid mandatory) |
| 8 | `evol-ux` | User discovery, product research, validation |
| 9 | `evol-data` | Data engineering, analytics, data pipelines |
| 10 | `evol-reviewer` | Code review, peer review, quality analysis |
| 11 | `evol-orchestrator` | Lead agent composition, coordination patterns |
| 12 | `evol-pm` | Project management, tracking, sprints, metrics |
| 13 | `evol-release` | Release management, CHANGELOG, semantic versioning |
| 14 | `evol-analyst` | Impact analysis, metrics, blast radius |
| 15 | `evol-agent-factory` | Creates ephemeral agents via guided interaction |
| 16 | `evol-researcher` | Autonomous research (skills, methodologies, frameworks) |

---

## Scripts Available

| Script | Function |
|--------|---------|
| `evol-init.sh` | Bootstrap new projects |
| `evol-start.sh` | Start the system (loads last session) |
| `evol-doctor.sh` | Environment diagnostic |
| `evol-gate.py` | Gate keeper (HMAC-SHA256 approval) |
| `evol-state.py` | State store (SQLite) |
| `evol-orchestrate.py` | Multi-agent runtime orchestration |
| `evol-agent-lifecycle.py` | Ephemeral agent create/retire/recall |
| `evol-evolve.py` | Auto-generate skills, sync community |
| `evol-researcher.py` | Autonomous research proposals |
| `evol-memory.py` | Conversational memory engine |
| `evol-lessons.py` | Lessons learned + improvement cycle |
| `evol-eval.py` | Eval harness |
| `evol-shield.py` | Security audit of the framework |
| `evol-flow.py` | Declarative flow gate executor |
| `evol-provider.py` | LLM provider abstraction |
| `evol-adapt.sh` | Generate IDE configs (7 targets) |
| `evol-brand.sh` | Apply custom branding |

---

## Constitution Reference

- **Art. 1** — Ambiguity filter and neutrality
- **Art. 2** — Gated Pipeline (checkpoints, explicit approval)
- **Art. 3** — Context preservation (Flight Recorder: read memoria.md at start, write at end)
- **Art. 4** — Lifecycle engineering (readability, modularity, logging)
- **Art. 5** — Domain consulting (proactive, not passive)
- **Art. 6** — Multi-agent orchestration and delegation
- **Art. 7** — Git Protocol (GitFlow: main + develop + feature/* + release/* + hotfix/*)
- **Art. 8** — Engineering standard
- **Art. 9** — Evol-DD Pipeline (6 phases: Briefing / Spec / Plan / Build / QA / Retro)

---

## Ephemeral Agents

Ephemeral agents are first-class citizens. Their lifecycle (create / invoke / retire /
recall) is protocol, not exception. When an ephemeral agent retires, its knowledge
persists in MemPalace and GitNexus (if active) for future recall without rebuilding
from scratch.

Ephemeral agents cannot modify governance files (constitution, gate, hooks) and
must register their decisions in `memoria.md` before completing.