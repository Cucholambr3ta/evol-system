---
name: evol-add-arch
description: ADD — Architecture-Driven Development, ADR generation, architecture fitness functions, trade-off analysis
category: discipline-extended
trigger: /add-arch
---

# evol-add-arch

## Fase del Pipeline

**Spec (Fase 2) — Especificación y Diseño**

Activar cuando se necesita documentar decisiones arquitectónicas:
- ADR (Architecture Decision Records) generation
- Architecture fitness functions
- Trade-off analysis
- Architectural runway tracking

## Artefacto Clave

**`docs/adr/ADR-NNN.md`**

```markdown
# ADR-001: Use Event-Driven Architecture

## Status
Accepted

## Date
2026-06-07

## Context
We need to build a system that handles 10k orders/day with real-time inventory updates.
Current synchronous architecture creates bottlenecks during peak hours.

## Decision
We will use event-driven architecture with:
- Kafka for event streaming
- CQRS for read/write separation
- Saga pattern for distributed transactions

## Consequences
### Positive
- Better scalability and fault tolerance
- Real-time inventory updates
- Decoupled services

### Negative
- Increased operational complexity
- Eventual consistency challenges
- Need for event schema management

## Alternatives Considered
| Alternative | Pros | Cons |
|-------------|------|------|
| REST APIs | Simple, well-known | Tight coupling, sync bottleneck |
| Message Queue | Decentralized | No event replay |

## Architecture Fitness Functions
- [ ] Latency p99 < 500ms
- [ ] Event processing lag < 1s
- [ ] System availability > 99.9%
```

## Flujo de Trabajo

```bash
# 1. Detectar decisiones arquitectónicas
python3 scripts/adr/detect.py \
  --source . \
  --output docs/adr/ADR_CANDIDATES.md

# 2. Generar ADR
python3 scripts/adr/generate.py \
  --title "Use Event-Driven Architecture" \
  --context "High throughput requirements" \
  --output docs/adr/ADR-001.md

# 3. Analizar trade-offs
python3 scripts/adr/trade-off.py \
  --adr docs/adr/ADR-001.md \
  --output docs/adr/TRADE_OFF_ANALYSIS.md

# 4. Definir fitness functions
python3 scripts/adr/fitness-functions.py \
  --adr docs/adr/ADR-001.md \
  --output docs/adr/FITNESS_FUNCTIONS.md

# 5. Validar consistencia de ADRs
python3 scripts/adr/validate.py \
  --adr-dir docs/adr/ \
  --output docs/adr/CONSISTENCY_REPORT.md

# 6. Generar diagrama de decisiones
python3 scripts/adr/visualize.py \
  --adr-dir docs/adr/ \
  --output docs/adr/DECISION_GRAPH.md
```

### ADR Template

```markdown
# ADR-{NNN}: {Title}

## Status
{Proposed | Accepted | Deprecated | Superseded by ADR-{NNN}}

## Date
{YYYY-MM-DD}

## Context
{What is the issue that we're seeing that motivates this decision?}

## Decision
{What is the change that we're proposing and/or doing?}

## Consequences
### Positive
{What becomes easier or more supported?}

### Negative
{What becomes harder?}

## Alternatives Considered
{What other options were evaluated?}
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Architecture context | Contexto arquitectónico definido | No |
| Spec | ADRs generated | ADRs creados para decisiones clave | Sí |
| Plan | Trade-offs analyzed | Trade-offs documentados | Sí |
| Build | Fitness functions | Fitness functions monitoreados | Sí |
| QA | Architecture validated | Consistencia verificada | Sí |
| Retro | ADR review | Decisiones revisadas | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Spec del Pipeline
- **Discipline Doc** — `docs/disciplines/ADD_Arch.md`
- **ADR Template** — https://github.com/joelparkerhenderson/architecture-decision-record
- **Fitness Functions** — https://www.thoughtworks.com/radar/techniques/fitness-functions
