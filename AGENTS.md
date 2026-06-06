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
| `evol-memory.py` | Conversational memory engine + `sprint-close --sprint=NN` (acuerdos/memoria + lecciones por sprint) |
| `evol-gitflow.sh` | GitFlow automatizado: `setup --mode=dev\|collab`, `sprint-start`, `sprint-close`, `pre-push` |
| `evol-discipline-check.py` | Valida CONTENIDO por disciplina (SDD/FDD/DDD/BDD/TDD/STDD/SecDD). Activar: `EVOL_DISCIPLINE=1` |
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
persists in Memoria Persistente and GitNexus (if active) for future recall without rebuilding
from scratch.

Ephemeral agents cannot modify governance files (constitution, gate, hooks) and
must register their decisions in `memoria.md` before completing.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **evol-system** (2219 symbols, 2798 relationships, 77 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/evol-system/context` | Codebase overview, check index freshness |
| `gitnexus://repo/evol-system/clusters` | All functional areas |
| `gitnexus://repo/evol-system/processes` | All execution flows |
| `gitnexus://repo/evol-system/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
