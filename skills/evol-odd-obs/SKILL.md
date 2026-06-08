---
name: evol-odd-obs
description: Observability-Driven Development — logging, metrics, tracing, alerting design, OpenTelemetry instrumentation
category: discipline-extended
trigger: /odd-obs
---

# evol-odd-obs

## Fase del Pipeline

**QA (Fase 5) — Verificación y Validación**

Activar cuando se necesita diseñar o auditar la observabilidad de un sistema:
- Instrumentación OpenTelemetry (traces, metrics, logs)
- Diseño de alerting y reglas de notificación
- Validación de cobertura observabilidad vs requisitos

## Artefacto Clave

**`docs/observability/CONFIG.md`**

```markdown
# Observability Configuration

## Services
| Service | Traces | Metrics | Logs | Sampling |
|---------|--------|---------|------|----------|
| api-gateway | OTLP | Prometheus | structured | 10% |
| order-svc | OTLP | Prometheus | structured | 100% |

## Alert Rules
| Alert | Condition | Severity | Channel |
|-------|-----------|----------|---------|
| HighErrorRate | error_rate > 5% for 5m | critical | pagerduty |
| LatencyP99 | p99 > 2s for 10m | warning | slack |

## OpenTelemetry Config
- Endpoint: otel-collector:4317
- Protocol: gRPC
- Resource attributes: service.name, service.version, deployment.environment
```

## Flujo de Trabajo

```bash
# 1. Analizar observabilidad existente
grep -r "otel\|opentelemetry\|prometheus\|jaeger" --include="*.yaml" --include="*.yml" --include="*.tf" .

# 2. Generar CONFIG.md desde código
python3 scripts/odd-obs/generate.py --output docs/observability/CONFIG.md

# 3. Validar instrumentación
python3 scripts/odd-obs/validate.py --config docs/observability/CONFIG.md --source .

# 4. Verificar cobertura de spans
python3 scripts/odd-obs/span-coverage.py --threshold 80

# 5. Ejecutar lint de reglas de alerta
python3 scripts/odd-obs/lint-alerts.py --rules docs/observability/CONFIG.md

# 6. Generar reporte de gaps
python3 scripts/odd-obs/gaps.py --config docs/observability/CONFIG.md --output docs/observability/GAPS.md
```

### Ejemplo de Instrumentación

```yaml
# Trace instrumentation pattern
otel:
  service_name: order-service
  exporter:
    endpoint: http://otel-collector:4317
    protocol: grpc
  sampling:
    strategy: parentbased_traceidratio
    ratio: 0.1
  attributes:
    - service.version
    - deployment.environment
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Observabilidad requerida | Identificar servicios críticos | No |
| Spec | Diseño ODD | CONFIG.md definido | Sí |
| Plan | Cobertura planificada | ≥80% servicios instrumentados | Sí |
| Build | Instrumentación completa | Traces + Metrics + Logs configurados | Sí |
| QA | Validación observabilidad | Alertas activas, dashboards existentes | Sí |
| Retro | Lecciones ODD | Mejoras documentadas | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase QA del Pipeline
- **Discipline Doc** — `docs/disciplines/ODD_Obs.md`
- **OpenTelemetry Spec** — https://opentelemetry.io/docs/specs/
- **Grafana Best Practices** — https://grafana.com/docs/grafana/latest/best-practices/


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
