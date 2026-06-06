# WORKING-CONTEXT.md — Estado Vivo del Proyecto

> Estado operativo actual. Se sobreescribe en cada cambio de sprint o hito.
> El hook `session:start:context-load` carga este archivo al iniciar sesion.

## Estado actual

- **Branch:** `main`
- **Fase Evol-DD:** F6-Retro — Fixes post-release
- **Version:** `0.3.2`
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git

## Hitos recientes

| Commit | Descripcion |
|--------|-------------|
| `feb4fd3` | docs(memoria): actualizar estado v0.3.2 + historial PyPI + bitacora rebrand |
| `971c91c` | fix(rebrand): x-dd → evol-dd namespace cleanup + .gitignore + bump v0.3.2 |
| `65cc0da` | docs(disciplinas): actualizar conteo 9->31 + constitucion Art.9 + MEMORY.md |

## Proximo paso

1. Construir `evol-agent` en otro PC con `/evol` (spec enriquecida lista).
2. Monitorear feedback externo y bugs tras el lanzamiento v0.3.2.

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
