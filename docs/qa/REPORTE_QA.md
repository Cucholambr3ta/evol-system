# Reporte QA — Evol-DD

## Resumen General

| Categoria | Total | Pendiente | Implementado | Ejecutado |
|-----------|-------|-----------|--------------|-----------|
| Requisitos funcionales | 18 | 9 | 9 | 3 |
| Gates de calidad | 9 | 0 | 9 | 9 |
| Scripts del sistema | 25 | 0 | 25 | 9 |
| Agentes core | 16 | 0 | 16 | 0 |
| Workflows | 21 | 0 | 21 | 0 |
| Skills | 9 | 0 | 9 | 1 |
| Eval suites | 7 | 0 | 7 | 0 |
| Casos de prueba | 6 | 0 | 6 | 2 |

## 1. Requisitos Funcionales

### Planificado (18 total)

- REQ-001 a REQ-018 (docs/qa/PLAN_QA.md, CP-001 a CP-006)
- NFR-001 a NFR-008

### Implementado (9)

| ID | Descripcion | Evidencia |
|----|-------------|-----------|
| REQ-002 | Bootstrap idempotente | `tests/test_init_idempotent.bats` |
| REQ-004 | Crear agente efimero | `scripts/evol-agent-lifecycle.py create` |
| REQ-005 | Invocar agente | `scripts/evol-agent-lifecycle.py invoke` |
| REQ-006 | Retirar agente con snapshot SHA-256 | `scripts/evol-agent-lifecycle.py retire` |
| REQ-007 | Recuperar agente desde snapshot | `scripts/evol-agent-lifecycle.py recall` |
| REQ-008 | Gate inicializa con permisos 0600 | `scripts/evol-gate.py init` |
| REQ-009 | Gate firma HMAC-SHA256 | `scripts/evol-gate.py approve` |
| REQ-010 | Gate valida cadena | `scripts/evol-gate.py validate`, `tests/test_gate.py` |
| REQ-011 | Transicion entre fases | `scripts/evol-gate.py transition` |

### Ejecutado en CI (3)

| ID | Test | Resultado |
|----|------|-----------|
| REQ-002 | `bats tests/test_init_idempotent.bats` | PASS |
| REQ-010 | `pytest tests/test_gate.py` | PASS |
| REQ-009 | smoke test en CI | PASS |

### Pendiente (9 roadmap)

- REQ-001, REQ-003 (bootstrap generate)
- REQ-012 (memoria.md fase actual)
- REQ-013 a REQ-018 (memory + lessons)
- NFR-006 (rutas relativas)
- NFR-008 (traces NDJSON)

## 2. Gates de Calidad

Todos los 9 gates estan implementados y ejecutados en CI (`.github/workflows/ci.yml`).

| Gate | Herramienta | Resultado |
|------|-------------|-----------|
| G1-Tests-Python | `pytest tests/` | 3 tests pass |
| G2-Tests-Shell | `bats tests/*.bats` | 2 suites pass |
| G3-Workflows-Lint | `bash scripts/lint-workflows.sh` | OK |
| G4-Registry-Validate | `python3 scripts/validate-registry.py --strict` | OK |
| G5-Manifests-Validate | jsonschema | OK |
| G6-Integración-MCP | grep mcpServers | MCP listo |
| G7-Anti-Emoji | grep emojis | MCP listo |
| G8-Shield-Audit | `python3 scripts/evol-shield.py audit --ci` | OK |
| G9-Init-Idempotent | `bats tests/test_init_idempotent.bats` | PASS |

## 3. Scripts del Sistema

### Implementados (25 scripts)

```
evol-brand.sh, evol-adapt.sh, evol-evolve.py, evol-shield.py, evol-eval.py,
_generate_equipo.py, generate-equipo.sh, validate-registry.py, evol-doctor.sh,
evol-state.py, _evol_common.py, evol-global-install.sh, evol-gate.py, evol-init.sh,
evol-update.py, lint-workflows.sh, evol-lessons.py, evol-researcher.py,
evol-orchestrate.py, evol-agent-lifecycle.py, evol-flow.py, evol-memory.py,
evol-start.sh, evol-provider.py
```

### Ejecutados en CI (9)

`evol-gate.py`, `evol-eval.py`, `evol-shield.py`, `validate-registry.py`, `lint-workflows.sh`, `generate-equipo.sh`, `evol-doctor.sh`, `evol-init.sh`, `evol-brand.sh`

### Sin cobertura CI automatizada (16)

`evol-state.py`, `evol-update.py`, `evol-lessons.py`, `evol-researcher.py`, `evol-orchestrate.py`, `evol-agent-lifecycle.py`, `evol-flow.py`, `evol-memory.py`, `evol-provider.py`, `evol-global-install.sh`, `evol-start.sh`, `_generate_equipo.py`, `_evol_common.py`, `test_gate.py` (pytest), `test_adapt_trigger_sanitization.bats`, `test_init_idempotent.bats`

## 4. Agentes Core

17 agentes core implementados en `prompts/agents/core/`. Registrados en `prompts/agents/registry.json`.
`docs/equipo.md` generado automaticamente via `scripts/generate-equipo.sh`.

## 5. Workflows

21 workflows en `.agent/workflows/`: architect, builder, qa, sec, devops, domain, doc, ux, data, reviewer, orchestrator, pm, release, analyst, agent-factory, researcher, cierrefase, crear-skill, evolve, qa-review, agent-factory.

## 6. Skills

9 skills en `skills/`: evol-skill-manager, crear-agente, agent-eval, evol-talk-compact, crear-skill, evol-compact, evol-sandbox, evol-fs-context, evol-ai-review.
Solo `agent-eval` tiene eval suite.

## 7. Eval Suites

7 suites en `evals/`: evol-talk-compact, evol-skill-manager, evol-ai-review, evol-fs-context, evol-sandbox, evol-compact, agent-eval.
Ninguna ejecutada en CI como gate (Fix 011 pendiente de implementacion).

## 8. Hallazgos Conocidos

| ID | Severidad | Descripcion | Archivo |
|----|-----------|-------------|---------|
| H-001 | HIGH | `index_paths` incluye `.evol` (secretos podrian indexarse) | `evol.config.yml` |
| H-002 | CRITICAL | `.gitignore` ignora `scripts/` y `src/` del framework | `.gitignore` |
| H-003 | HIGH | `evol-eval.py` stub - no ejecuta evals como gate | `scripts/evol-eval.py` |
| H-004 | CRITICAL | CI tiene `|| true` que oculta fallos | `.github/workflows/ci.yml` |

## 9. Caminos de Prueba

| Feature | CP | Happy Path | Error Path |
|---------|----|-----------|------------|
| Bootstrap | CP-001 | init exitoso, idempotente | perfil invalido, sin git |
| Agentes Efimeros | CP-002 | create/invoke/retire/recall | agente inexistente, snapshot corrupto |
| Gate Keeper | CP-003 | init/approve/validate/transition | sin init, log alterado |
| Pipeline | CP-004 | 6 fases con APROBADO | transicion sin APROBADO, fase invalida |
| Memoria | CP-005 | load/summarize/search/gc | pendiente implementacion |
| Lecciones | CP-006 | add/search/suggest-fix/apply-fix | pendiente implementacion |

## 10. Criterios de Release

Antes de release deben estar:

1. Todos los G1-G9 passando en CI
2. Ningun hallazgo CRITICAL o HIGH abierto
3. Rama `main` y `develop` creadas
4. `CHANGELOG.md` actualizado
5. Version tag creado
6. `docs/equipo.md` sincronizado con registry