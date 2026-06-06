# WORKING-CONTEXT.md — Estado Vivo del Proyecto

> Estado operativo actual. Se sobreescribe en cada cambio de sprint o hito.
> El hook `session:start:context-load` carga este archivo al iniciar sesion.

## Estado actual

- **Branch:** `feature/edms-memory-system`
- **Fase Evol-DD:** F6+ — Compliance Auditor + EDMS + Orchestration
- **Version:** `0.4.0-dev`
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git

## Hitos recientes

| Commit | Descripcion |
|--------|-------------|
| `408ce01` | fix(critical): implement orchestrate.py + missing audit templates |
| `270862e` | feat(compliance): add compliance auditor — agent #18 + 3-layer enforcement |
| `a20228b` | fix(core): update all references from 16 to 17 core agents |

## Proximo paso

1. ~~Implement evol-orchestrate.py~~ (Completado).
2. ~~Add compliance auditor (agent #18)~~ (Completado).
3. **Merge a develop** cuando se cierre el sprint actual.

## Resumen del sistema

| Componente | Cantidad | Ubicacion |
|------------|----------|-----------|
| Workflows | 71 | `.agent/hooks/scripts/` + `.agent/workflows/` |
| Agentes core | 18 | `prompts/agents/core/` |
| Scripts evol-* | 26 | `scripts/` |
| Skills | 9 | `skills/` |
| Hooks registrados | 19 | `.agent/hooks/hooks.json` |
| Audit templates | 6 | `templates/audit/` |

## Notas de arquitectura vigentes

- Gate HMAC-SHA256 por proyecto (`.evol/.gate-key` gitignored)
- GitFlow enforced via pre-commit-gitflow.sh
- Compliance auditor: 3 capas (hooks + workflow + sprint-end)
- Orchestration engine: 5 patterns built-in, SQLite recording
- 18 core agents (registry.json)
