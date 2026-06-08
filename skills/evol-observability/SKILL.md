---
name: evol-observability
description: Telemetry y analytics para sistemas distribuidos. Logging, métricas, tracing, dashboards y OpenTelemetry.
category: transfer
trigger: /observability
---

# evol-observability

## Cuándo Usar

Activar esta skill cuando se necesita observabilidad en el software:

- **Logging**: structured logs, log levels, correlation IDs
- **Metrics**: counters, gauges, histograms, SLIs/SLOs/SLAs
- **Distributed tracing**: traces, spans, service maps
- **Dashboards**: Grafana, DataDog, visualization best practices
- **Alerting**: alert rules, escalation, on-call rotations
- **OpenTelemetry**: vendor-neutral instrumentation

**No usar para**: analytics de negocio (usar evol-data), performance testing (usar evol-balance).

## Conocimiento de Dominio

### Three Pillars of Observability
- **Logs**: discrete events with context (what happened)
- **Metrics**: numerical measurements over time (how much/how fast)
- **Traces**: request flow through distributed systems (where time is spent)

### Structured Logging
- **JSON format**: parseable, searchable, consistent
- **Log levels**: ERROR > WARN > INFO > DEBUG > TRACE
- **Correlation IDs**: trace requests across services
- **Context enrichment**: add user ID, request ID, service name
- **Sensitive data**: never log passwords, tokens, PII

### Metrics
- **Counters**: monotonically increasing (requests, errors)
- **Gauges**: can go up and down (memory, queue size)
- **Histograms**: distribution of values (latency, request size)
- **SLIs**: Service Level Indicators (availability, latency, throughput)
- **SLOs**: Service Level Objectives (target SLIs)
- **SLAs**: Service Level Agreements (business commitments)

### Distributed Tracing
- **Spans**: units of work within a trace
- **Trace context**: propagated across service boundaries
- **Service maps**: visual representation of dependencies
- **Latency analysis**: where time is spent, bottlenecks

### OpenTelemetry
- **Vendor-neutral**: instrument once, export anywhere
- **Auto-instrumentation**: libraries for common frameworks
- **Context propagation**: W3C Trace Context standard
- **Collector**: receive, process, export telemetry

### Alerting
- **Alert on symptoms**: what users experience, not causes
- **Multi-window multi-burn-rate**: SLO-based alerting
- **Escalation**: who gets paged, when, how
- **Runbooks**: what to do when alert fires

## Flujo de Trabajo

1. **Define observability goals**: what do we need to know? what questions answer?
2. **Instrument code**: add logs, metrics, traces to critical paths
3. **Setup collection**: OpenTelemetry collector, log aggregation
4. **Create dashboards**: service health, business metrics, SLIs
5. **Configure alerts**: SLO-based, actionable, with runbooks
6. **Test observability**: verify logs appear, metrics are correct, traces flow
7. **Train team**: how to use dashboards, respond to alerts, debug with traces
8. **Iterate**: add more instrumentation as needed, refine alerts

## Integración con Pipeline

- **Briefing (Fase 1)**: understand what needs to be observable, SLIs/SLOs
- **Spec (Fase 2)**: document observability requirements, dashboard specs
- **Plan (Fase 3)**: plan instrumentation effort, tool selection
- **Build (Fase 4)**: instrument code, setup collection, create dashboards
- **QA (Fase 5)**: verify observability works, alerts fire correctly
- **Retro (Fase 6)**: review observability effectiveness, add missing telemetry

## Referencia

- Constitución Evol-DD: Art. 4 (logging, monitoring)
- Agentes relacionados: evol-devops (infrastructure), evol-sec (security monitoring), evol-data (analytics)
- Charity Majors - "Observability Engineering"
- OpenTelemetry: https://opentelemetry.io
- SLO methodology: https://sre.google/sre-book/service-level-objectives
- Grafana: https://grafana.com


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
