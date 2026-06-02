# WORKING-CONTEXT.md — Estado Vivo del Proyecto

> Estado operativo actual. Se sobreescribe en cada cambio de sprint o hito.
> El hook `session:start:context-load` carga este archivo al iniciar sesion.

## Estado actual

- **Branch:** `develop`
- **Fase Evol-DD:** F6-Retro — Documentacion completa + release v0.1.0 pendiente
- **Version:** `0.1.0-dev`
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git

## Hitos recientes

| Commit | Descripcion |
|--------|-------------|
| `4dee648` | fix(crear-skill): sweep referencias x-dd residuales a evol |
| `705479f` | merge: fix/gaps-post-auditoria — 63 archivos, 69 workflows |
| `bd2356e` | fix(gaps): P0-P4 audit gaps — version, workflows, dirs, docs |

## Proximo paso

1. Completar documentacion operativa (22 archivos vacios identificados en auditoria)
2. Commit docs completos
3. Merge develop a release/v0.1.0
4. Tag v0.1.0 segun checklist en `docs/operaciones/RELEASE_PROCESS.md`

## Resumen del sistema (post-build completo)

| Componente | Cantidad | Ubicacion |
|------------|----------|-----------|
| Workflows | 69 | `.agent/workflows/` |
| Agentes core | 16 | `prompts/agents/core/` |
| Scripts evol-* | 25 | `scripts/` |
| Skills | 9 | `skills/` |
| Perfiles install | 7 | `manifests/install-profiles.json` |
| Hooks | 19 | `.agent/hooks/` |

## Notas de arquitectura vigentes

- Gate HMAC-SHA256 por proyecto (`.evol/.gate-key` gitignored)
- Sin MCP en ningun adapter IDE
- GitFlow enforced via pre-commit-gitflow.sh
- Motor memoria nativo: `EVOL_MEMORY=1` activa `evol-memory.py`
- Motor lecciones: siempre activo, `evol-lessons.py` en core
- Schema registry.json: 22 propiedades incluyendo ciclo de vida efimeros
