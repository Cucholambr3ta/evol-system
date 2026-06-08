# Evol-DD — Agent Governance Manifest

**Trigger:** `/evol`

---

## Governing Law

`docs/constitucion.md` is the supreme law of this system. Every agent, workflow,
and process must conform to it. In case of conflict between any instruction and the
Constitution, the Constitution prevails.

---

## Core Agents Directory

All 18 core agents are defined in `prompts/agents/core/`. They are permanent and
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
| 17 | `evol-auditor` | Phase auditor: detects gaps, blind spots, missing skills. Logs lessons before retiring. |
| 18 | `evol-compliance-auditor` | Compliance auditor: verifies pipeline phases, detects violations, generates sprint reports. |

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
| `evol_memory_v2/` | Memory Architecture v2.0: verbatim store, entity extraction, auto-linking, BM25 retrieval, hybrid search, reflection, dreaming, forgetting, conflict detection |
| `evol-gitflow.sh` | GitFlow automatizado: `setup --mode=dev\|collab`, `sprint-start`, `sprint-close`, `pre-push` |
| `evol-discipline-check.py` | Valida CONTENIDO por disciplina (SDD/FDD/DDD/BDD/TDD/STDD/SecDD). Activar: `EVOL_DISCIPLINE=1` |
| `evol-lessons.py` | Lessons learned + improvement cycle |
| `evol-eval.py` | Eval harness |
| `evol-shield.py` | Security audit of the framework |
| `evol-flow.py` | Declarative flow gate executor |
| `evol-provider.py` | LLM provider abstraction |
| `evol-adapt.sh` | Generate IDE configs (7 targets) |
| `evol-brand.sh` | Apply custom branding |
| `evol-code-indexer.py` | Tree-sitter code graph indexer (impact, trace, query, incremental) |

---

## Skills Registry (52 Discipline + 18 Core)

### Discipline Skills — Base (9)

| # | Skill | Disciplina | Fase |
|---|-------|------------|------|
| 1 | `evol-sdd-spec` | SDD — Spec-Driven | Todas |
| 2 | `evol-fdd-feature` | FDD — Feature-Driven | 1+3 |
| 3 | `evol-ddd-domain` | DDD — Domain-Driven | 2 |
| 4 | `evol-bdd-behavior` | BDD — Behavior-Driven | 1+5 |
| 5 | `evol-atdd-acceptance` | ATDD — Acceptance Test-Driven | 1+5 |
| 6 | `evol-tdd-unit` | TDD — Test-Driven | 4 |
| 7 | `evol-stdd-security-test` | STDD — Security-Test-Driven | 4 |
| 8 | `evol-secdd-security` | SecDD — Security-Driven | 5 |
| 9 | `evol-threat-model` | Threat-Driven | 2 |

### Discipline Skills — Extended (22)

| # | Skill | Disciplina | Fase |
|---|-------|------------|------|
| 10 | `evol-odd-api` | ODD_API — OpenAPI | 2 |
| 11 | `evol-uxdd-ux` | UXDD — UX | 1 |
| 12 | `evol-a11ydd` | A11yDD — Accessibility | 1+5 |
| 13 | `evol-rdd-refactor` | RDD — Refactoring | 4 |
| 14 | `evol-pdd-perf` | PDD — Performance | 5 |
| 15 | `evol-chaos-resilience` | Chaos — Resiliency | 5 |
| 16 | `evol-mdd-migrate` | MDD — Migration | 3 |
| 17 | `evol-cdcdd` | CDCDD — Change Data Capture | 3 |
| 18 | `evol-esdd-events` | ESDD — Event Sourcing | 2 |
| 19 | `evol-ccdd-contract` | CCDD — Consumer-Driven Contract | 5 |
| 20 | `evol-apivdd` | APIVDD — API Versioning | 3 |
| 21 | `evol-odd-obs` | ODD_Obs — Observability | 5 |
| 22 | `evol-slo-sla` | SLO/SLA-Driven | 5 |
| 23 | `evol-iodd-iac` | IODD — Infrastructure-as-Code | 2 |
| 24 | `evol-pipeline-ci` | Pipeline-Driven | 4 |
| 25 | `evol-compliance-drivers` | Compliance-Driven | 2 |
| 26 | `evol-privacy-drivers` | PrivacyDD — Privacy by Design | 2 |
| 27 | `evol-debt-budget` | DebtBudgetDD — Tech Debt | 3 |
| 28 | `evol-deprecation` | DeprecationDD — Deprecation | 3 |
| 29 | `evol-add-arch` | ADD — Architecture | 2 |
| 30 | `evol-eda` | EDA — Event-Driven | 2 |
| 31 | `evol-udd-usecase` | UDD — Use-Case | 1 |

### Domain Advisor Skills (3)

| # | Skill | Dominio | Uso |
|---|-------|---------|-----|
| 32 | `evol-domain-sales` | Ventas/E-commerce | Software de ventas |
| 33 | `evol-domain-finance` | Finanzas/Contabilidad | Software financiero |
| 34 | `evol-domain-marketing` | Marketing/Analytics | Software de marketing |

### Game-Inspired Skills (4)

| # | Skill | Concepto | Aplicación |
|---|-------|----------|------------|
| 35 | `evol-systems-design` | Systems Design | Interacciones agent-workflow |
| 36 | `evol-pacing` | Pacing | Timing del pipeline |
| 37 | `evol-narrative-docs` | Narrative | Documentación con storytelling |
| 38 | `evol-balance` | Balance | Carga y optimización |

### Transfer Skills (14)

| # | Skill | Fuente | Aplicación |
|---|-------|--------|------------|
| 39 | `evol-dx-advocate` | Developer Advocate | DX, community |
| 40 | `evol-mcp-builder` | MCP Builder | Agent tools |
| 41 | `evol-discovery` | Discovery Coach | User research |
| 42 | `evol-growth-experiment` | Growth Hacker | A/B testing |
| 43 | `evol-seo-technical` | SEO Specialist | Technical SEO |
| 44 | `evol-observability` | Tracking Specialist | Telemetry |
| 45 | `evol-cost-analysis` | Financial Analyst | Cost modeling |
| 46 | `evol-workflow-design` | Workflow Architect | Process automation |
| 47 | `evol-code-archaeology` | Historian | Technical debt |
| 48 | `evol-cognitive-ux` | Psychologist | Cognitive UX |
| 49 | `evol-ethnography` | Anthropologist | Deep user research |
| 50 | `evol-change-mgmt` | Change Management | Adoption |
| 51 | `evol-governance` | Automation Governance | Policy-as-code |
| 52 | `evol-team-dynamics` | Org Psychologist | Team performance |

### Core Skills (18)

| # | Skill | Categoría |
|---|-------|-----------|
| 53 | `agent-eval` | Eval & Testing |
| 54 | `code-indexer` | Code Analysis |
| 55 | `crear-agente` | Agent Lifecycle |
| 56 | `crear-skill` | Skill Lifecycle |
| 57 | `evol-ai-review` | Quality Gate |
| 58 | `evol-compact` | Context Engineering |
| 59 | `evol-context7` | Documentation |
| 60 | `evol-fact-check` | Research |
| 61 | `evol-frontend-design` | UI Design |
| 62 | `evol-fs-context` | Context Engineering |
| 63 | `evol-grill-me` | Planning |
| 64 | `evol-idea-refine` | Planning |
| 65 | `evol-prompt-master` | Prompt Engineering |
| 66 | `evol-remotion` | Motion Design |
| 67 | `evol-sandbox` | Execution |
| 68 | `evol-skill-manager` | Skill Lifecycle |
| 69 | `evol-talk-compact` | Context Engineering |
| 70 | `readme-master` | Documentation |

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
persists in Memoria Persistente for future recall without rebuilding
from scratch.

Ephemeral agents cannot modify governance files (constitution, gate, hooks) and
must register their decisions in `memoria.md` before completing.
