---
name: evol-pdd-perf
description: Performance-Driven Development. Define SLOs de rendimiento, ejecuta pruebas de carga con k6, y bloquea si se superan los umbrales de latencia/throughput.
category: discipline-extended
trigger: /pdd
---

# evol-pdd-perf

## Fase del Pipeline
QA (Fase 5)

## Artefacto Clave
`docs/qa/PERF_REPORT.md`

## Flujo de Trabajo

### 1. Definir SLOs de rendimiento
```bash
# Derivar SLOs desde NFR de SPEC.md
evol-pdd define-slos --spec=docs/specs/SPEC.md --output=performance/slos/

# Generar escenarios de carga k6
evol-pdd generate-scenarios --slos=performance/slos/ --output=performance/load_test_scenarios/
```

### 2. Ejecutar pruebas de carga
```bash
# Prueba baseline (trafico normal)
k6 run --out json=performance/results/baseline.json performance/load_test_scenarios/baseline.js

# Prueba de pico (trafico maximo)
k6 run --out json=performance/results/spike.json performance/load_test_scenarios/spike.js

# Prueba de estres (carga creciente)
k6 run --out json=performance/results/stress.json performance/load_test_scenarios/stress.js
```

### 3. Analizar resultados contra umbrales
```bash
# Comparar resultados vs SLOs
evol-pdd compare --results=performance/results/ --slos=performance/slos/ --output=performance/comparison.json

# Generar reporte consolidado
evol-pdd report --comparison=performance/comparison.json --output=docs/qa/PERF_REPORT.md
```

### 4. Verificar Core Web Vitals (frontend)
```bash
# Lighthouse Performance
npx lighthouse http://localhost:3000 --only-categories=performance --output=json --output-path=performance/lighthouse-perf.json

# Extraer CWV
evol-pdd core-web-vitals --report=performance/lighthouse-perf.json --output=performance/cwv.json
```

## Formato SLO

```json
{
  "endpoint": "GET /api/usuarios",
  "latencia": {
    "p50": 50,
    "p95": 100,
    "p99": 250,
    "unit": "ms"
  },
  "throughput": {
    "min": 1000,
    "target": 5000,
    "unit": "req/s"
  },
  "disponibilidad": 0.999
}
```

## Formato PERF_REPORT.md

```markdown
# Performance Report

**Fecha:** 2026-06-07
**Estado:** APROBADO / RECHAZADO

## Resumen Ejecutivo
[Estado general vs SLOs]

## Resultados por Endpoint
| Endpoint | p50 | p95 | p99 | SLO p95 | Estado |
|----------|-----|-----|-----|---------|--------|
| GET /api/usuarios | 32ms | 87ms | 180ms | 100ms | PASS |
| POST /api/pedidos | 45ms | 110ms | 230ms | 100ms | FAIL |

## Core Web Vitals
| Metrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| LCP | 1.2s | 2.5s | PASS |
| FID | 45ms | 100ms | PASS |
| CLS | 0.05 | 0.1 | PASS |
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Spec | Definir SLOs de rendimiento |
| Build | Etiquetar escenarios `@performance` |
| QA | Ejecutar pruebas de carga; comparar con umbrales |
| Gate | Bloquea si las pruebas superan los umbrales |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/PDD.md`
- [k6 — Grafana](https://github.com/grafana/k6)
- [SLOs and Performance Testing — Gatling](https://gatling.io/blog/slo-load-testing/)


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
