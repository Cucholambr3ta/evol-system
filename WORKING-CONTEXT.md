# WORKING-CONTEXT.md — Estado Vivo del Proyecto

> Estado operativo actual. Se sobreescribe en cada cambio de sprint o hito.
> El hook `session:start:context-load` carga este archivo al iniciar sesion.

## Estado actual

- **Branch:** `feature/edms-ui`
- **Fase Evol-DD:** F7 — EDMS UI Dashboard (Web PWA descartada por perdida de foco, TUI es la prioridad actual)
- **Version:** `0.6.3` (pyproject.toml) / `0.6.0` (VERSION — drift pendiente)
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git

## Hitos recientes

| Commit | Descripcion |
|--------|-------------|
| (sin commit) | fix(update-memory): add git pull as Step 0 for multi-agent safety |
| (sin commit) | feat(skills): add update-memory + update-context to package CATALOG |
| `d0d19b6` | fix(skill): enforce attributionLogo:false by default in code generation |

## Proximo paso

1. ~~Implement EDMS Phases 1-6~~ (Completado — v0.6.0).
2. ~~Cross-platform installer~~ (Completado — install.sh).
3. ~~Real-time monitoring (Phases 1-2)~~ (Completado — evol_traces + evol_sse_server + state machine + loop detector).
4. ~~Aprobación de wireframes~~ (Completado — 9 pantallas aprobadas).
5. ~~Implement TUI~~ (Completado — scaffold 29 archivos en `scripts/evol_tui/`).
6. **Auditar TUI** — verificar la interfaz Textual TUI contra los wireframes aprobados.
7. **Sincronizar VERSION** — resolver discrepancia pyproject.toml=0.6.3 vs VERSION=0.6.0.
8. **Commit Backend** — stagear módulos TUI, evol_memory_v2, sse_server, etc.

## Resumen del sistema

| Componente | Cantidad | Ubicacion |
|------------|----------|-----------|
| Workflows | 72 | `.agent/hooks/scripts/` + `.agent/workflows/` |
| Agentes core | 18 | `prompts/agents/core/` |
| Scripts evol-* | 30+ | `scripts/` |
| Skills (catálogo) | 82 | `skills/CATALOG.json` (70 core + 12 extra) |
| Skills local-only | 1 | `~/.agents/skills/` (revision-release) |
| Hooks registrados | 19 | `.agent/hooks/hooks.json` |
| Audit templates | 6 | `templates/audit/` |
| Tests | 52 | `tests/` |
| EDMS items | 105+ | ChromaDB (63+ drawers) + local index (98+) + graph (261+) |
| EDMS v2 components | 18 | `scripts/evol_memory_v2/` (~4600 L, 137 tests) |
| Real-time modules | 4 | evol_traces, evol_sse_server, evol_state_machine, evol_loop_detector |
| Code indexer | 1 | evol_code_indexer (Tree-sitter) |
| Wireframes EDMS | 9 | `acuerdos/design/wireframes/propuesta/` (ALL APPROVED) |
| npm wrappers | 15 | `bin/evol*.js` |
| EDMS Web PWA | 34 | `edms-web/src/` (React 19 + ThreeJS + PWA) |

## Notas de arquitectura vigentes

- Gate HMAC-SHA256 por proyecto (`.evol/.gate-key` gitignored)
- GitFlow enforced via pre-commit-gitflow.sh
- Compliance auditor: 3 capas (hooks + workflow + sprint-end)
- Orchestration engine: 5 patterns built-in, SQLite recording
- 18 core agents (registry.json)
- EDMS: ChromaDB + LadybugDB + stdlib fallback (auto-detect venv)
- 4-tier consolidation: raw→compressed→memory→knowledge→archived
- Optional deps: `memory` (chromadb), `graph` (ladybug + networkx), `full` (all)
- Expanded indexing: artefacto, agente_def, skill_def graph nodes (P0+P1+P2)
- Bootstrap: 9 phases (acuerdos, legacy, git, disciplines, sprints, root docs, agents, skills)
- Real-time monitoring: NDJSON traces + SSE server + state machine + loop detection (all stdlib)
- Cross-platform installer: `install.sh` (curl|bash)
- Cross-env sync: `/update-context` workflow (read-only, no EDMS re-index)
- Code graph: Tree-sitter mandatory, separate LadybugDB (evol_dd_codigo.lbug)
- Optional deps: + `code` (tree-sitter + grammars), `full` (all including code)
- npm installation: `package.json` + 15 wrappers in `bin/`, `PYTHONPATH=scripts`
- Local-only skills: NOT in evol-dd releases (revision-release, update-context, update-memory)
- v2 persistence hooks: session-start dreaming, session-end reflection+forgetting+conflicts
- EDMS memory integration in all 70 skills (edms-store, edms-extract, edms-link, edms-conflicts)
- attributionLogo: false by default in code generation skills
- Wireframes: 9 HTML screens ALL APPROVED
- TUI: delegated to external agent (Textual + netext), audit pending
- VERSION drift: pyproject.toml=0.6.3 vs VERSION=0.6.0 (needs sync)
