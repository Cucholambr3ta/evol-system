# WORKING-CONTEXT.md — Estado Vivo del Proyecto

> Estado operativo actual. Se sobreescribe en cada cambio de sprint o hito.
> El hook `session:start:context-load` carga este archivo al iniciar sesion.

## Estado actual

- **Branch:** `feature/edms-ui`
- **Fase Evol-DD:** F7 — EDMS UI Dashboard
- **Version:** `0.6.0`
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git

## Hitos recientes

| Commit | Descripcion |
|--------|-------------|
| `b8d80d9` | docs(memoria): sync acuerdos post-publish — PyPI 0.6.0, fix duplicates, new risks |
| `588cf17` | docs(memoria): update acuerdos — decisions, risks, conventions post-v0.6.0 |
| `58ea5c5` | docs(context): update WORKING-CONTEXT.md to v0.6.0 — EDMS complete, feature/edms-ui branch |
| `2cdaca0` | docs(edms-ui): add stack reference for UI development |
| `174cfd0` | Merge feature/edms-memory-system into develop — EDMS + Compliance + Orchestration + Installer v0.6.0 |

## Proximo paso

1. ~~Implement EDMS Phases 1-6~~ (Completado — v0.6.0).
2. ~~Cross-platform installer~~ (Completado — install.sh).
3. **Aprobación de wireframes** para EDMS UI dashboard.
4. **Implement UI** con React 19 + FastAPI (cuando wireframes estén aprobados).

## Resumen del sistema

| Componente | Cantidad | Ubicacion |
|------------|----------|-----------|
| Workflows | 71 | `.agent/hooks/scripts/` + `.agent/workflows/` |
| Agentes core | 18 | `prompts/agents/core/` |
| Scripts evol-* | 26+ | `scripts/` |
| Skills | 9 | `skills/` |
| Hooks registrados | 19 | `.agent/hooks/hooks.json` |
| Audit templates | 6 | `templates/audit/` |
| Tests | 41 | `tests/` |
| EDMS items | 105 | ChromaDB (63 drawers) + local index (98) + graph (261) |

## Notas de arquitectura vigentes

- Gate HMAC-SHA256 por proyecto (`.evol/.gate-key` gitignored)
- GitFlow enforced via pre-commit-gitflow.sh
- Compliance auditor: 3 capas (hooks + workflow + sprint-end)
- Orchestration engine: 5 patterns built-in, SQLite recording
- 18 core agents (registry.json)
- EDMS: ChromaDB + LadybugDB + stdlib fallback (auto-detect venv)
- 4-tier consolidation: raw→compressed→memory→knowledge→archived
- Optional deps: `memory` (chromadb), `graph` (ladybug + networkx), `full` (all)
- Cross-platform installer: `install.sh` (curl|bash)
