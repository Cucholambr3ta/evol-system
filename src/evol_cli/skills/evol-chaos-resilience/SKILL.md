---
name: evol-chaos-resilience
description: Chaos / Resiliency-Driven Development. Ejecuta experimentos de chaos con inyeccion de fallos controlada para validar recuperacion automatica del sistema.
category: discipline-extended
trigger: /chaos
---

# evol-chaos-resilience

## Fase del Pipeline
QA (Fase 5)

## Artefacto Clave
`docs/qa/CHAOS_REPORT.md`

## Flujo de Trabajo

### 1. Formular hipotesis desde amenazas
```bash
# Leer amenazas de tipo DoS desde STRIDE
evol-chaos hypothesis --threats=docs/specs/THREATS.md --output=chaos/hypothesis/

# Generar plan de experimentos
evol-chaos plan --hypothesis=chaos/hypothesis/ --output=chaos/experiments/
```

### 2. Configurar sandbox aislado
```bash
# Preparar entorno de staging para chaos
evol-chaos setup-sandbox --env=staging --output=chaos/sandbox_config.json

# Verificar que produccion NO esta expuesta
evol-chaos verify-isolation --config=chaos/sandbox_config.json
```

### 3. Ejecutar experimentos de inyeccion de fallo
```bash
# Inyectar latencia de red
evol-chaos inject --type=network-latency --duration=60s --target=api-service

# Inyectar fallo de dependencia
evol-chaos inject --type=dependency-failure --target=database-service

# Inyectar consumption de recursos
evol-chaos inject --type=cpu-stress --duration=120s --target=api-service
```

### 4. Medir tiempo de recuperacion
```bash
# Monitorear metricas durante el experimento
evol-chaos monitor --experiment=chaos/experiments/EXP-001.json --output=chaos/results/EXP-001_metrics.json

# Generar reporte
evol-chaos report --results=chaos/results/ --hypothesis=chaos/hypothesis/ --output=docs/qa/CHAOS_REPORT.md
```

## Formato Hipotesis

```markdown
# Hipotesis de Resiliencia — HYP-001

**Amenaza:** THREAT-003 (DoS via saturacion de DB)
**Estado estable:** Latencia p95 < 100ms, error rate < 0.1%
**Fallo inyectado:** Latencia de 500ms en queries a la BD
**Resultado esperado:** Sistema se recupera en < 2 min tras cesar el fallo
**Blast radius:** 100% de requests afectados durante el fallo
```

## Formato CHAOS_REPORT.md

```markdown
# Chaos Report

**Fecha:** 2026-06-07
**Estado:** APROBADO / RECHAZADO

## Resumen Ejecutivo
[N experimentos ejecutados, N pasaron, N fallaron]

## Experimentos
| ID | Amenaza | Fallo | Recuperacion | SLO | Estado |
|----|---------|-------|--------------|-----|--------|
| EXP-001 | DoS DB | Latencia 500ms | 1m 23s | < 2min | PASS |
| EXP-002 | Dependencia caida | Timeout 30s | No recupero | < 2min | FAIL |

## Hallazgos
[Lecciones aprendidas y mejoras sugeridas]

## Plan de Accion
| Mejora | Owner | Prioridad |
|--------|-------|-----------|
| Agregar circuit breaker a DB pool | Builder | P1 |
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Spec | Identificar amenazas de disponibilidad (STRIDE DoS) |
| QA | Ejecutar experimentos en sandbox aislado |
| Retro | Registrar hallazgos y mejorar la resiliencia |
| Gate | Bloquea si hay experimentos que requieren intervencion manual |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/CHAOS.md`
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [Chaos Mesh](https://github.com/chaos-mesh/chaos-mesh)
- [Chaos Engineering Overview — Microsoft](https://learn.microsoft.com/en-us/azure/chaos-studio/chaos-engineering-overview)
