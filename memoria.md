# memoria.md — Flight Recorder del Proyecto

> Bitácora viva del proyecto. **Lectura obligatoria** al inicio de cada sesión (Constitución Art. 3).
> Toda sesión termina actualizando este archivo vía `/cierre-fase`.

## Identidad del Proyecto
- **Nombre:** Evol-DD
- **Dominio:** Framework de desarrollo agéntico
- **Stack:** Python, Bash, CLI
- **Fecha de inicio:** 2026-06-02
- **Repositorio:** https://github.com/Cucholambr3ta/evol-system.git

## Estado Actual
- **Fase Evol-DD:** PUBLICADO EN PYPI — v0.5.0 activa en produccion
- **Ultimo hito:** Integrada skill readme-master, diseño Top 100 y hooks recursivos pre-push.
- **Proximo paso:** Construir memoria persistente nativa (ChromaDB + LadybugDB).
- **PyPI:** https://pypi.org/project/evol-dd/
- **Versiones publicadas:** 0.1.0 → 0.3.3 (update-memory) → 0.4.0 → 0.5.0 (readme-master)

## Decisiones Arquitectónicas Clave
- 2026-06-02: Sprint 0 Bootstrap — xdd-init.sh legacy mode
- 2026-06-02: 11 sprints completados en una sesion
- 2026-06-02: Remote configurado a https://github.com/Cucholambr3ta/evol-system.git
- 2026-06-02: GitFlow violado — todo en un commit, corregido post-hoc con branches
- 2026-06-02: Lecciones registradas sobre GitFlow y orquestador
- 2026-06-02: Fix 002 — Migración estricta evol vs xdd (no shims legacy)
- 2026-06-02: Fix 005 — Opcion A: scripts como ejecutables con subprocess dispatch
- 2026-06-02: Fix 009 — CI sin masks (`|| true` eliminados), gates reales activos
- 2026-06-02: Fix 011 — Eval harness con 4 grader types implementados
- 2026-06-02: Fix 022 — Manifesto `agent.yaml` como SSoT de capacidades
- 2026-06-02: Publicacion PyPI v0.1.0 — primer release publico
- 2026-06-02: Fix empaquetado pipx — pyproject.toml migracion setuptools → hatchling + force-include data dirs
- 2026-06-02: Fix evol-adapt.sh — soporte real --dest, 0 archivos generados en OpenCode corregido
- 2026-06-02: evol-install-global — trigger /evol global en 7 IDEs (Claude Code, OpenCode, Cursor, Windsurf, VSCode Copilot, Antigravity, Codex)
- 2026-06-02: Docs completas — 22 archivos vacios poblados con contenido real
- 2026-06-02: Auditoria arquitectonica pre-implementacion — 8 ADRs, 15 casos borde, DOC_STANDARD

## Riesgos Activos
- Feedback externo pendiente: comportamiento en equipos sin todos los IDEs instalados
- evol-update apply no testeado en produccion con pipx upgrade real
- Antigravity ~/.gemini/skills/ path puede variar segun version del IDE

## Historial de versiones PyPI
| Version | Fecha | Que incluye |
|---------|-------|-------------|
| 0.1.0 | 2026-06-02 | Release inicial |
| 0.1.1 | 2026-06-02 | Fix evol-adapt.sh --dest + OpenCode triggers |
| 0.1.2 | 2026-06-02 | evol-install-global para Claude Code + OpenCode |
| 0.1.3 | 2026-06-02 | evol-install-global cubre 7 IDEs simultaneamente |
| 0.1.4 | 2026-06-03 | Auto-install global en primera ejecucion (first-run marker) |
| 0.1.6 | 2026-06-03 | Fix packaging: data dirs en src/evol_cli/ (force-include fallaba en PyPI) |
| 0.1.7 | 2026-06-03 | Workflow evol.md orquestador principal (trigger /evol) |
| 0.1.8 | 2026-06-03 | VSCode tasks.json global (Copilot sin slash global) + OpenCode 2 dirs |
| 0.1.9 | 2026-06-03 | evol-start.sh compatible Memoria Persistente 3.x (mine API) |
| 0.2.0 | 2026-06-03 | evol.md + memoria_persistente-sync (/evol mem) frontmatter limpio |
| 0.2.1 | 2026-06-03 | Security nativa: evol-scan/validate/patch/crash |
| 0.2.2 | 2026-06-03 | 4 community skills (grill/fact-check/idea-refine/prompt-master) |
| 0.2.3 | 2026-06-03 | grill-me ENFORCED en gate del plan (marker SHA + 7 tests) |
| 0.2.7 | 2026-06-04 | E5-E8: sprint-close, historias, gitflow, discipline-check (69 tests) |
| 0.3.0 | 2026-06-05 | setup-repo, security-inventory, briefing idea.md, sprint eval |
| 0.3.2 | 2026-06-05 | 31 disciplinas, rebrand x-dd→evol-dd, .gitignore limpio |

---

## Bitácora de Sesiones

### Sesión 2026-06-06 — Fix Rebrand Residual, MemPalace Removal & v0.3.3

- **Meta:** Limpiar menciones residuales de X-DD, erradicar MemPalace, estructurar memoria atómica y hacer release.
- **Hitos:**
  - Sustituciones aplicadas a docs (residuales) y preservación de documentos históricos.
  - Erradicación de MemPalace de los scripts core y templates, preparación para ChromaDB/LadybugDB.
  - Generación de comandos atómicos en `docs/usuario/comandos/`.
  - Workflow `/update-memory` creado.
- **QA:** Grep validado; menciones restantes a X-DD son estrictamente contextuales/comparativas.
- **Estado:** Branch main = v0.5.0, develop = main. PyPI activo.
- **Próxima sesión:** Diseño e implementación de Memoria Persistente nativa.
### Sesión 2026-06-05 — Rebrand x-dd→evol-dd + .gitignore + release v0.3.2

- **Meta:** Limpieza completa de namespace x-dd en todo el codebase, corrección de gaps en .gitignore, y release v0.3.2 en PyPI.
- **Hitos:**
  - Rebrand funcional: `evol-scan.py` scanner names `xdd-heuristic/xdd-sca` → `evol-heuristic/evol-sca`; temp path `/tmp/xdd-gitleaks.json` → `/tmp/evol-gitleaks.json`.
  - `evol-discipline-check.py`: removidos 6 fallback `.xdd/` de los bloques candidates.
  - 45 workflows (SSoT + mirrors): `xdd.profile.yml`, `xdd-orchestrate.py`, `xdd-state.py`, `xdd-gate.py`, `xdd-researcher`, `X-DD CORE CONTROL DOMAINS`, `X-DD System`, `X-DD Orchestrator`, `Constitución X-DD`, `/x-dd`, `/xdd-build`, footers disciplinas, link muerto `xdd-fs-context → evol-fs-context`.
  - 9 frontmatter descriptions `"Workflow X-DD"` → descripciones reales.
  - `skills/crear-skill/SKILL.md`: `origin: x-dd` → `origin: evol-dd` (ambas copias).
  - `.gitignore`: fix negación `.github/prompts/` (era anulada por `!.github/`); agregados `.vscode/` y `dudas.md`.
  - VERSION + pyproject.toml: `0.3.1` → `0.3.2`.
  - Commit `971c91c`: 110 archivos, 723 inserciones.
  - Push develop → origin; rama `main` creada y pusheada.
  - Tag `v0.3.2` en main; build wheel (scripts=68, agent=206, manifests=6, skills=64); publicado en PyPI.
  - `/evol` reinstalado globalmente en 7 IDEs con `evol-install-global`.
- **QA:** 104 pytest OK. 7/7 verificaciones OK. Mirrors idénticos.
- **Estado:** Branch main = v0.3.2, develop = main. PyPI activo.
- **Próxima sesión:** Construir evol-agent en otro PC con /evol.


### Sesión 2026-06-05 — Herencia upgrade 31 metodologías (Lote F, v0.3.2) + merge develop + fix Mermaid
- **Meta:** Heredar el upgrade X-DD (22 metodologías → registro de disciplinas 9→31) a Evol-DD con branding evol, mergear a develop, arreglar render Mermaid.
- **Hitos (commit feature `42c50f1`, merge `fe27101`):**
  - `docs/disciplinas/` 9→31 fichas con branding evol (9 base in-situ + 22 copiadas con rebrand). Sección Fuentes + sidecars `fuentes[]` (116 URLs). `evol-doc-sync.py` con `_extract_sources()`.
  - 6 skills `/evol` (ux-driven, event-sourcing, api-versioning, iac-driven, debt-budget, use-case-driven).
  - 4 workflows extendidos (dr-drill, data-pipeline, privacy-review, dependency-update); `evol.profile.yml` `methodologies:`; `evol.md` inyección por profile + DAG; DOC_STANDARD 1.7; `validate-disciplinas.py`.
  - CHANGELOG v0.3.2.
- **Fix Mermaid (2 commits develop):** `b611b05` (\n→<br/> 7 fichas base + INDEX), `22b8eb4` (comillas simples en labels). Mismo bug que X-DD; las fichas evol lo heredaron.
- **QA:** validate-disciplinas 31/31 strict; lint 87 OK; sin drift post-resync.
- **Agentes permanentes:** 0 nuevos — sigue en 16 + efímeros (evol-agent-factory).
- **Estado:** develop con 5+ commits sin pushear. Lección Mermaid en lecciones.md root + acuerdos/lecciones/sprint-27.md.
- **Próxima sesión:** push develop; release v0.3.2; revisar dev-docs por mismo patrón Mermaid.

### Sesión Fixes — 2026-06-02 (post-auditoría)
- **Meta:** Aplicar 21 fixes de auditoría full, estabilizar proyecto para release
- **Archivos modificados:**
  - `.gitignore`, `templates/gitignore.template` (Fix 001)
  - `evol.profile.yml`, `AGENTS.md`, `CLAUDE.md`, `docs/constitucion.md` (Fix 002)
  - `scripts/evol-init.sh`, `manifests/*.json` (Fix 003, Fix 014)
  - `scripts/evol-global-install.sh` (Fix 004)
  - `scripts/*.py`, `pyproject.toml` entrypoints (Fix 005)
  - `scripts/evol-gate.py` payload/sign verifying (Fix 006)
  - `memoria_persistente.yaml`, `evol.config.yml`, hooks (Fix 007, Fix 008)
  - `.github/workflows/ci.yml` (Fix 009)
  - `tests/*.py`, `tests/*.bats` (Fix 010)
  - `scripts/evol-eval.py` (Fix 011)
  - `prompts/agents/registry.json`, `scripts/generate-equipo.sh` (Fix 012)
  - `pyproject.toml` deps (Fix 013)
  - `scripts/evol-doctor.sh` blocking mode (Fix 014)
  - `scripts/evol-shield.py` CI mode, flags (Fix 015)
  - `scripts/evol-evolve.py` quarantine/pin (Fix 016)
  - `scripts/evol-brand.sh` sanitized (Fix 017)
  - `scripts/evol-adapt.sh` sanitized (Fix 018)
  - `CHANGELOG.md`, `VERSION`, `main` branch (Fix 019)
  - 12+ docs actualizados con datos reales (Fix 020)
  - Runtime permissions hardened (Fix 021)
  - `agent.yaml` manifesto (Fix 022)
- **Decisiones:**
  - Fix 002: Migración estricta evol vs xdd (no shims legacy)
  - Fix 005: Opción A — scripts como ejecutables con subprocess dispatch
  - Fix 009: CI sin masks (`|| true` eliminados), gates reales activos
  - Fix 011: Eval harness con 4 grader types (structural, behavioral, output_match, pass_at_k)
  - Fix 022: Manifesto `agent.yaml` como SSoT de capacidades
- **Tests ejecutados:**
  - `pytest tests/`, `bats tests/*.bats`
  - `evol-doctor.sh`, `evol-shield.py audit --ci --no-write`
  - `validate-registry.py --strict`
  - `evol-eval.py validate --all && evol-eval.py run --all`
  - `git ls-files scripts src tests evals schemas prompts templates`
- **Bloqueos:**
  - Ninguno crítico — todos resueltos
- **Próxima sesión:** Release v0.1.0-dev

---

### Sesión Sprint Completo — 2026-06-02
- **Meta:** Construir Evol-DD completo (11 sprints)
- **Hitos:**
  - S0: Identity + Base Legal (AGENTS.md, CLAUDE.md, constitucion.md, .gitignore, templates)
  - S1: 5 scripts infraestructura (_evol_common, state, provider, gate, flow)
  - S2: 4 scripts bootstrap (doctor, init, start, global-install)
  - S3: evol-adapt.sh + 19 workflows SSoT
  - S4: 16 agentes core + registry.json + equipo.md
  - S5: 7 skills + 7 eval suites
  - S6: 11 hooks + hooks.json
  - S7: evol-agent-lifecycle.py (create/invoke/retire/recall/gc)
  - S8: evol-memory.py + evol-lessons.py
  - S9: evol-evolve.py + evol-researcher.py
  - S10: evol-eval.py + evol-shield.py
  - S11: pyproject.toml + CI + README + docs finales
  - Docs granular completo reescrito (ARQUITECTURA, DOMINIO, PLAN_QA, CASOS_GHERKIN, THREATS, FUNCIONALES, NO_FUNCIONALES, RESTRICCIONES, GLOSARIO)
  - 12 feature branches creadas y mergeadas a develop
- **Decisiones:**
  - 23 scripts, 16 core agents, 19 workflows, 7 skills, 28 docs archivos
  - Doctor reporta 0 errores, Memoria Persistente en modo COMPLETO
  - GitFlow violado inicial, corregido con branches post-hoc
- **Bloqueos:**
  - Ninguno — todos resueltos
- **Próxima sesión:** Release v0.1.0-dev y primer merge a main

### Sesión Fix 025 — Release Cleanup + Final Docs — 2026-06-02
- **Meta:** Limpieza profunda + revisión final de docs para release
- **Hitos:**
  - Clasificados todos los archivos del repo (source/generated/runtime/local-memory/qa-evidence/delete-safe)
  - Eliminados archivos de prueba/ephemeral: `test-agent.md`, `evol-profile.md`
  - Eliminados artefactos corruptos o accidentales: `"El framework que evoluciona."` (branding test), `PYEOF` (stderr artifact)
  - Eliminados logs de hooks bloqueados: `.hook-blocked.log`
  - Eliminados archivos de memoria de usuario: `AGENT_MEMORY.md` (no es parte del release)
  - Verificado `.gitignore` cubre outputs sin ignorar source crítico (con `!` rules para dirs fuente)
  - Actualizado `memoria.md` con sesión Fix 025
  - Verificado `docs/equipo.md` sincronizado con registry (16 core, 0 ephemeral actuales)
  - Verificado `lecciones.md` con aprendizaje de gate key
  - Verificado `docs/qa/REPORTE_QA.md` distingue planificado/implementado/ejecutado/pendiente
  - Verificado `README.md` y `INSTALL.md` sin TBD ni refs xdd- legacy
  - Verificado `CHECKLIST_RELEASE.md` con comandos ejecutables reales
- **Decisiones:**
  - Archivos JSON corruptos de pruebas de branding no son parte del release
  - `AGENT_MEMORY.md` es memoria del usuario, no del framework
  - Test ephemeral agents (test-agent) no tracked ni versionado
- **Bloqueos:**
  - Ninguno
- **Proxima sesion:** Merge a develop, crear release branch, tag v0.1.0

### Sesion Release + Publicacion PyPI — 2026-06-02
- **Meta:** Publicar Evol-DD en PyPI y dejar disponible globalmente en 7 IDEs
- **Hitos:**
  - Migracion setuptools → hatchling (pyproject.toml) + force-include data dirs en wheel
  - evol_cli/__init__.py: _data_dir() con logica 3 niveles, EVOL_DATA_DIR inyectado a bash
  - 22 archivos de documentacion vacios poblados con contenido real y especifico
  - evol-update.py implementado (check/apply/status, pip-mode + legacy-mode)
  - evol-adapt.sh reescrito: soporte real --dest, todos los IDEs reciben configs
  - Gates pre-release: 15 tests verdes, lint 69 workflows OK, shield 0 CRITICAL
  - Publicacion: v0.1.0 en PyPI, luego patches 0.1.1/0.1.2/0.1.3
  - evol-install-global: copia /evol a ~/.claude/commands/, ~/.config/opencode/command/,
    ~/.cursor/rules/, ~/.codeium/workflows/, ~/.config/Code/User/prompts/,
    ~/.gemini/skills/, ~/.codex/skills/ — disponible globalmente en cualquier carpeta
- **Bugs encontrados y corregidos:**
  - evol-adapt.sh hardcodeaba REPO_ROOT → 0 archivos en proyectos externos
  - pyproject.toml data-files iba a /usr/share/ no al wheel → fix con hatchling force-include
  - evol-shield.py falsos positivos en docs de seguridad → skip_dirs por regla
  - Workflows sin frontmatter name/trigger (53 de 69) → fix masivo
  - evol-lessons.py ignoraba estructura ## CATEGORIA en lecciones.md → fix insert-by-section
- **Version final:** 0.1.3 en PyPI

### Sesion Megasprint — 2026-06-03 (install global + security + skills + enforcement)
- **Meta:** Trigger global real en 7 IDEs, security nativa, community skills, enforcement de gate
- **Hitos (0.1.3 → 0.2.3):**
  - install_global() cubre los 7 IDEs en un comando + _first_run_check() auto-trigger
    post `pipx install evol-dd && evol` (marker versionado ~/.evol/.global-installed-VERSION)
  - Fix empaquetado definitivo: data dirs DENTRO de src/evol_cli/ (force-include fallaba
    en sdist de PyPI). Verificado con zipfile antes de publicar
  - VSCode Copilot: tasks.json global (no soporta slash commands globales) — limitacion del IDE
  - Memoria Persistente 3.x: evol-start.sh usa `mine <dir> --wing` (API cambio de `index`)
  - Security nativa portada desde X-DD: evol-scan/validate/patch/crash (sin deps externas,
    inspirado en RAPTOR MIT). Agente offsec + guidance tiers + hook pre-build
  - 4 community skills nativas: grill-me, fact-check, idea-refine, prompt-master
    (atribucion en NOTICE). Integradas al pipeline 6 fases en evol.md
  - grill-me ENFORCED: gate del plan bloquea (exit 1) sin marker SHA del PLAN.md.
    7 tests. Escape hatch EVOL_SKIP_GRILL=1
- **Entregable paralelo:** evol-agent-specification.md enriquecida (2355→2615 lineas):
  Seccion 0 guia construccion con Evol-DD, mapeo 5 graders, L0-L5 MVP, Nexus MVP,
  event types, seccion de Riesgos y Falencias. Modelo hibrido: Evol-DD construye,
  producto autoref. Listo para /evol en otro PC
- **Bugs corregidos:** symlinks conflictivos pipx editable, OpenCode lee 2 dirs +
  frontmatter minimal, falta workflow evol.md orquestador principal
- **Lecciones nuevas:** 5 (trigger global multi-IDE, first-run sin post-install hook,
  force-include sdist, gate enforcement con SHA, OpenCode 2 dirs)
- **QA:** 14 tests gate verdes, lint 74 workflows OK, shield 0 CRITICAL (4 HIGH preexistentes)
- **Version final:** 0.2.3 en PyPI
- **Proxima sesion:** Construir evol-agent con /evol en otro equipo

### Sesion 2026-06-04 — INC E5-E8: herencia X-DD Inc 5-9 a Evol-DD (feature/evol-inc5-9)
- **Meta:** Portar los 5 incrementos completados en X-DD (sprint-close, historias, gitflow, sprint, discipline-check) a Evol-DD con namespace evol-.
- **Hitos:**
  - E5: evol-memory.py sprint-close + evol-init.sh MEMORY.md/INDEX.md + cierre-fase v1.4
  - E6: evol-historias.md + evol-sprint.md (workflows portados)
  - E7: evol-gitflow.sh (setup dev/collab, sprint-start/close, pre-push, 15 bats)
  - E8: evol-discipline-check.py (8 disciplinas, 21 tests) + integrado en evol-gate.py
- **QA:** 54 pytest + 15 bats = 69 tests verdes
- **Version:** 0.2.7 publicada en PyPI (0.2.4 ya existia de sesion anterior)
- **Proxima sesion:** Merge feature/evol-inc5-9 a develop; merge feature/sprint-memoria-lecciones en X-DD
