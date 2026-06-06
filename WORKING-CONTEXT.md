# WORKING-CONTEXT.md — Estado Vivo del Proyecto

> Estado operativo actual. Se sobreescribe en cada cambio de sprint o hito.
> El hook `session:start:context-load` carga este archivo al iniciar sesion.

## Estado actual

- **Branch:** `feature/upgrade-gaps`
- **Fase Evol-DD:** F6-Retro — Fixes post-release
- **Version:** `0.3.2` (en transición a `0.3.3`)
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git

## Hitos recientes

| Commit | Descripcion |
|--------|-------------|
| `3fd7bf9` | feat: implement evol-update and evol-update-project workflows and fix upgrade gaps |
| `feb4fd3` | docs(memoria): actualizar estado v0.3.2 + historial PyPI + bitacora rebrand |
| `971c91c` | fix(rebrand): x-dd → evol-dd namespace cleanup + .gitignore + bump v0.3.2 |

## Proximo paso

1. ~~Construir `evol-agent` en otro PC con `/evol`~~ (Despriorizado / Cerrado).
2. **Resolver Advertencia [HIGH]**: Excluir explícitamente `.evol/` de la indexación de Memoria Persistente en la configuración.
3. **Merge & Release v0.3.3**: Mergear `feature/upgrade-gaps` a develop y lanzar nueva versión a PyPI con los workflows de actualización.

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
