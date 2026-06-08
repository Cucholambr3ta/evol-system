---
name: evol-slo-sla
description: SLO/SLA-Driven Development — SLO definition, error budgets, SLA drafting, burn rate alerts
category: discipline-extended
trigger: /slo-sla
---

# evol-slo-sla

## Fase del Pipeline

**QA (Fase 5) — Verificación y Validación**

Activar cuando se necesita definir o auditar niveles de servicio:
- Definición de SLOs por servicio
- Cálculo de error budgets
- Redacción de SLAs
- Configuración de burn rate alerts

## Artefacto Clave

**`docs/qa/SLO_DEFINITIONS.md`**

```markdown
# SLO Definitions

## Service: api-gateway
| SLI | Target | Window | Error Budget |
|-----|--------|--------|--------------|
| Availability | 99.9% | 30d | 43.2min |
| Latency (p99) | < 500ms | 30d | 0.1% |
| Correctness | 99.99% | 30d | 4.32min |

## Burn Rate Alerts
| SLO | Burn Rate | Window | Severity |
|-----|-----------|--------|----------|
| Availability | 14.4x | 1h | critical |
| Availability | 6x | 6h | warning |

## SLA Summary
- **Availability SLO:** 99.9% monthly
- **Latency SLO:** p99 < 500ms
- **Support Response:** 4h for critical, 24h for high
```

## Flujo de Trabajo

```bash
# 1. Extraer métricas existentes
python3 scripts/slo-sla/extract-slis.py --source . --output docs/qa/SLIS_RAW.md

# 2. Generar definiciones SLO
python3 scripts/slo-sla/generate-slos.py \
  --slis docs/qa/SLIS_RAW.md \
  --output docs/qa/SLO_DEFINITIONS.md \
  --targets "availability=99.9,latency_p99=500,correctness=99.99"

# 3. Calcular error budgets
python3 scripts/slo-sla/calc-budgets.py \
  --slos docs/qa/SLO_DEFINITIONS.md \
  --window 30d \
  --output docs/qa/ERROR_BUDGETS.md

# 4. Generar burn rate alerts
python3 scripts/slo-sla/burn-rate-alerts.py \
  --slos docs/qa/SLO_DEFINITIONS.md \
  --output alerts/slo-burn-rate.yml

# 5. Validar SLA vs SLO alignment
python3 scripts/slo-sla/validate-sla-slo.py \
  --slos docs/qa/SLO_DEFINITIONS.md \
  --sla docs/compliance/SLA.md

# 6. Generar dashboard config
python3 scripts/slo-sla/dashboard.py \
  --slos docs/qa/SLO_DEFINITIONS.md \
  --output dashboards/slo-overview.json
```

### Error Budget Formula

```
Error Budget = (1 - SLO Target) × Time Window
Example: 99.9% SLO over 30d = 0.1% × 30 × 24 × 60 = 43.2 minutes
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | SLI identificados | Métricas clave definidas | No |
| Spec | SLOs propuestos | Targets documentados | Sí |
| Plan | Error budgets calculados | Budgets por SLO | Sí |
| Build | Instrumentación SLIs | Métricas recolectadas | Sí |
| QA | SLOs validados | Burn rate alerts configurados | Sí |
| Retro | Error budget review | Consumo vs presupuesto | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase QA del Pipeline
- **Discipline Doc** — `docs/disciplines/SLO_SLA.md`
- **Google SRE Book** — https://sre.google/sre-book/service-level-objectives/
- **OpenSLO Spec** — https://openslo.com/


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
