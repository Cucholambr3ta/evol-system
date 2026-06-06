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
| `2cdaca0` | docs(edms-ui): add stack reference for UI development |
| `174cfd0` | Merge feature/edms-memory-system into develop — EDMS + Compliance + Orchestration + Installer v0.6.0 |
| `b6b288c` | feat(edms): add edms-compact, cross-platform installer, graph dependency |

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
- EDMS: ChromaDB + NetworkX + stdlib fallback (auto-detect venv)
- 4-tier consolidation: raw→compressed→memory→knowledge→archived
- Optional deps: `memory` (chromadb), `graph` (networkx), `full` (both)
- Cross-platform installer: `install.sh` (curl|bash)
