# WORKING-CONTEXT.md — Estado Vivo del Proyecto

> Estado operativo actual. Se sobreescribe en cada cambio de sprint o hito.
> El hook `session:start:context-load` carga este archivo al iniciar sesion.

## Estado actual

- **Branch:** `feature/update-memory`
- **Fase Evol-DD:** F6-Retro — Update memory and prepare release
- **Version:** `0.3.3`
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git

## Hitos recientes

| Commit | Descripcion |
|--------|-------------|
| `369e27d` | feat: add /update-memory workflow to maintain persistent memory |
| `61f746d` | refactor: remove memoria_persistente dependencies in preparation for persistent memory |
| `e03d5f3` | docs(memoria): migrate monolithic MEMORY to atomic structure |

## Proximo paso

1. ~~Borrar Memoria Persistente y toda su estructura.~~ (Completado).
2. **Merge & Release v0.3.3**: Mergear cambios a develop, hacer el tag de release de v0.3.3 y subir a PyPI.

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
- GitFlow enforced via pre-commit-gitflow.sh
- Motor memoria nativo: `EVOL_MEMORY=1` activa `evol-memory.py`
- Motor lecciones: siempre activo, `evol-lessons.py` en core
- Schema registry.json: 22 propiedades incluyendo ciclo de vida efimeros
