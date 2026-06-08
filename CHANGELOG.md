# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## [Unreleased]

## [0.7.1] - 2026-06-07

### Added
- **Memory v2.0 Integration**: Integrated MemoryV2 into evol-memory.py with 12 new CLI commands:
  - `edms-store`: Verbatim storage
  - `edms-extract`: Entity extraction
  - `edms-link`: Auto-linking
  - `edms-hybrid-search`: Hybrid search (vector + BM25 + graph)
  - `edms-entity`: Get entity by name
  - `edms-entity-relations`: Get entity relations
  - `edms-verify`: Verify item integrity
  - `edms-v2-stats`: v2 memory statistics
  - `edms-reflection`: Run reflection engine
  - `edms-dreaming`: Run dreaming engine
  - `edms-forget`: Run forgetting engine
  - `edms-conflicts`: Detect conflicts

### Changed
- `evol-memory.py`: Integrated MemoryV2 with lazy import, added v2 CLI commands and handlers.
- `.agent/workflows/update-memory.md`: Added v2 integration (verbatim storage, entity extraction, auto-linking, conflict detection).
- `.agent/workflows/cierre-fase.md`: Added v2 integration (verbatim storage of lessons, entity extraction, conflict detection).
- `.agent/workflows/update-context.md`: Added v2 hybrid search, entity context, and evidence contracts.
- `.agent/hooks/scripts/post-edit-memory-index.sh`: Added v2 integration (verbatim storage, entity extraction, auto-linking).

### Fixed
- `evol-memory.py`: Fixed syntax error with duplicate else statement.
- `evol-memory.py`: Fixed `list_all` → `list_items` for v2 command handlers.

## [0.7.0] - 2026-06-07

### Added
- **Memory Architecture v2.0**: Multi-layer memory system with 18 components (~4600 lines, 137 tests, 0 external dependencies).
  - **Phase 1**: VerbatimStore (append-only, SHA-256 dedup), EntityExtractor (8 types, 6 relationships), AutoLinker (zero-LLM, 7 link patterns), EntityStore (temporal validity), MemoryV2 compat layer.
  - **Phase 2**: BM25Retriever (BM25 Okapi stdlib), Evidence contracts, GraphExpander (BFS query expansion), HybridRetriever (RRF fusion).
  - **Phase 3**: ReflectionEngine (patterns, trends, evolutions), DreamingEngine (sprint-aware sessions), ForgettingEngine (TTL-based), ConflictDetector (contradictions, inconsistencies).
  - **Phase 4**: AgentFile format, RelationalIntelligence, MemoryAPI (stdlib HTTP), MigrationTool.
- **52 Discipline Skills**: 9 base + 22 extended + 3 domain advisors + 4 game-inspired + 14 transfer skills covering all *-Driven Development disciplines.
- **Real-time Monitoring**: NDJSON traces, SSE server, state machine, agent loop detection (all stdlib).
- **Code Graph Indexer**: Tree-sitter-based code analysis with separate LadybugDB graph.
- **137 new tests** across 8 test suites.

### Changed
- `README.md`: Updated Memory section to describe v2.0.
- `AGENTS.md`: Added `evol_memory_v2/` to scripts table.
- `docs/arquitectura/ARQUITECTURA.md`: Updated memory system section with v2.0 components and directory structure.

## [0.6.3] - 2026-06-07

### Added
- **Code Graph Indexer**: Tree-sitter-based code analysis with separate LadybugDB graph (`evol_dd_codigo.lbug`). Parses Python and JavaScript/TypeScript to extract symbols (functions, classes, methods), imports, and call relationships.
- **Impact Analysis CLI**: `edms-impact <symbol>` and `edms-trace <entry>` subcommands in `evol-memory.py` for blast radius analysis and execution flow tracing.
- **Compliance Impact Check**: `evol-compliance check-impact` command analyzes changed files and reports risk level with affected symbols.
- **Code Graph CLI**: `evol code-indexer {index|query|graph|impact|trace|stats}` entry point.
- **MemoryStore Code Integration**: New methods `index_code()`, `code_impact()`, `code_trace()`, `code_query()`, `code_stats()` in MemoryStore class.
- **Incremental Indexing**: Git-based change detection (`.evol/.last-code-index-commit`) for efficient partial re-indexing.
- **New Dependencies**: `tree-sitter>=0.23.0`, `tree-sitter-python`, `tree-sitter-javascript`, `tree-sitter-typescript` in optional `[code]` extra.
- **17 new tests** for code indexer, impact analysis, and process tracing.

### Changed
- `pyproject.toml`: Version bumped to 0.6.3. Added `[code]` optional dependency group.
- `evol_cli/__init__.py`: Added `code-indexer` entry point and `code_indexer()` function.
- `evol-memory.py`: Added `edms-impact`, `edms-trace`, `edms-code-query`, `edms-code-stats`, `edms-code-index` subcommands.
- `evol-compliance.py`: Added `check-impact` command for pre-commit impact analysis.
- `AGENTS.md`: Added `evol-code-indexer.py` to scripts table.
- `README.md`: Added Code Graph Indexer section with usage examples.
- `docs/arquitectura/ARQUITECTURA.md`: Added Code Graph Indexer component (Section 5).
- `docs/operaciones/UPGRADE_GUIDE.md`: Added `[code]` dependency installation instructions.
- `docs/edms-ui-STACK.md`: Added Code Graph API routes (pending implementation).

### Added
- `docs/adr/ADR-0009-code-graph-indexer.md`: Architecture decision record for code graph indexer.
- `skills/code-indexer/SKILL.md`: User-facing skill documentation for code graph tools.
- `.agent/workflows/code-indexer.md`: Workflow documentation for code graph indexer.
- `scripts/evol_traces.py`: Added `emit_code_index()`, `emit_code_impact()`, `emit_code_trace()` dedicated emitters.

## [0.6.0] - 2026-06-06

### Added
- **EDMS Phase 1-5**: MemoryStore abstraction layer with ChromaDB (vector search) + JSON fallback, 26 CLI subcommands, lifecycle hooks, 4-tier consolidation pipeline, FlowScript queries (why/tensions/blocked/whatIf/alternatives), team memory namespaces.
- **EDMS Phase 6**: `edms-compact` command with LLM summarization + extractive fallback (Jaccard dedup + key sentence extraction). Compacts raw observations into compressed tier.
- **Compliance Auditor (Agent #18)**: 3-layer enforcement (hooks + workflow + sprint-end), phase compliance tracking, lesson verification, sprint compliance reports.
- **Orchestration Engine**: 5 built-in patterns (security_review, feature_squad, release_train, briefing_squad, brainstorm_party), SQLite recording, dry-run mode.
- **Cross-platform installer**: `curl | bash` installer (`install.sh`) with auto Python/pipx detection, OS-adaptive package manager support, optional IDE trigger installation.
- **18 core agents** with compliance auditor workflow and audit templates (briefing, agent-creation).
- **31 tests** across 4 test suites (memory_store, memory, compliance, lessons).
- **NetworkX** as optional graph database dependency (replaces JSON-only in-memory graph).

### Changed
- `pyproject.toml`: Added `[project.optional-dependencies]` for `memory` (chromadb), `graph` (networkx), and `full` (both).
- All hooks now support 3 profiles: minimal (1 hook), standard (11 hooks), strict (7 hooks).
- EDMS auto-detects project venv and re-executes with correct Python if chromadb is missing.

### Fixed
- `consolidate_tier()` now filters by `tier` field instead of `tipo` prefix.
- `get_tier_stats()` counts by actual `tier` field.
- `decay_old_items()` operates on `tier` field, skips archived items.
- `evol-compliance.py`: lesson_tracking table auto-created on first use.
- Orphan hooks (`session-start-reme-load.sh`, `stop-reme-summary.sh`) now have correct permissions.

## [0.5.0] - 2026-06-06

### Added
- Nueva skill `/evol readme-master` para estandarizar visualmente (Top 100, Minimalismo, AI-Friendly) y semánticamente la documentación de los `README.md`.
- Integración automática en el pre-push hook (`evol-gitflow.sh`) para asegurar que todos los archivos `README.md` (root y subcarpetas) del repositorio cumplan el estándar antes de mezclarse.
- Ejecución recursiva de la skill `readme-master`, con escaneo dinámico del árbol de directorios para mapear y auto-referenciar documentos cercanos (ej. `docs/`).

## [0.4.0] - 2026-06-06

### Added
- Integración nativa de **MCP (Model Context Protocol)** por defecto, abandonando la política opt-in y anti-MCP. Ahora `evol.config.yml` habilita los servidores automáticamente.
- Script `evol-mcp.sh` (módulo `mcp-manager`) como gestor oficial de configuraciones MCP del proyecto. Comandos: `add`, `remove`, `list`, `status`.

### Removed
- **GitNexus:** Se eliminó por completo el soporte, referencias, skills exclusivas (`.claude/skills/gitnexus/`), bloques de contexto forzados en `AGENTS.md` y `CLAUDE.md`, así como la documentación `gitnexus-optin.md` debido a la migración de estrategia en favor del uso de integraciones estándar de MCP.

### Changed
- `evol-shield.py` ya no bloquea la inclusión de configuraciones `mcpServers` en entornos IDE (regla `no_mcp_config` eliminada).
- `evol-init.sh` no requiere bandera `--mcp` para el scaffolding de configuraciones.

## [0.3.2] - 2026-06-05

### Added
- Registro de disciplinas extendido de **9 a 31 metodologias** en `docs/disciplinas/` (herencia
  del upgrade X-DD `ultimate-update.md`). 22 fichas nuevas con paridad de profundidad (proposito,
  cuando aplicar, artefactos I/O, pipeline Mermaid, integracion, criterios, DoD, agentes, Fuentes):
  ODD_API, UXDD, A11yDD, RDD, PDD, Chaos, MDD, CDCDD, ESDD, CCDD, APIVDD, ODD_Obs, SLO/SLA, IODD,
  Pipeline-Driven, Compliance, PrivacyDD, DebtBudgetDD, DeprecationDD, ADD, EDA, UDD.
- Seccion **Fuentes** en las 9 fichas base con respaldo canonico verificable (Dan North/BDD,
  Kent Beck/TDD, Eric Evans/DDD, STRIDE/Microsoft, OWASP, etc.). Sidecars con `fuentes[]` (116 URLs).
- 6 skills nuevas para disciplinas sin cobertura: `/evol ux-driven`, `/evol event-sourcing`,
  `/evol api-versioning`, `/evol iac-driven`, `/evol debt-budget`, `/evol use-case-driven`.
- `scripts/validate-disciplinas.py`: valida que cada ficha tenga `fuentes[]` no-vacio (regla
  DOC_STANDARD 1.7); `--strict` valida drift de sidecar.
- `evol.profile.yml`: bloque `methodologies:` (31 disciplinas, activacion por caso de uso).
- `evol.md`: seccion "Inyeccion de disciplinas por profile" (lee methodologies, inyecta por fase,
  resuelve DAG de dependencias).

### Changed
- `evol-doc-sync.py`: nuevo extractor `_extract_sources()` captura URLs de la seccion Fuentes en
  el sidecar `fuentes[]`.
- DOC_STANDARD: nueva regla **1.7 Citacion de fuentes de investigacion web** (claim sin link =
  INCOMPLETO) + campo `fuentes[]` en el contrato del sidecar.
- 4 workflows extendidos con disciplinas (activacion por profile): dr-drill (Chaos), data-pipeline
  (EDA + CDCDD), privacy-review (Compliance), dependency-update (DeprecationDD).
- discovery/doc-granular/research: regla de fuentes OBLIGATORIA en el paso de escritura.

### Fixed
- **Rebrand x-dd → evol-dd** (namespace cleanup completo):
  - `evol-scan.py`: scanner names `xdd-heuristic`/`xdd-sca` → `evol-heuristic`/`evol-sca`;
    temp path `/tmp/xdd-gitleaks.json` → `/tmp/evol-gitleaks.json`.
  - `evol-discipline-check.py`: removidos 6 fallback paths `.xdd/` de cada bloque `candidates`.
  - 45 workflows en `.agent/workflows/` + mirrors `src/evol_cli/agent/workflows/`: sustituidos
    `xdd.profile.yml`, `xdd-orchestrate.py`, `xdd-state.py`, `xdd-gate.py`, `xdd-researcher`,
    `X-DD CORE CONTROL DOMAINS`, `X-DD System`, `X-DD Orchestrator`, `Constitución X-DD`,
    `/x-dd`, `/xdd-build`, footers `*X-DD — disciplina`, link muerto `skills/xdd-fs-context`.
  - 9 frontmatter descriptions reemplazadas de `"Workflow X-DD"` por descripciones reales.
  - `skills/crear-skill/SKILL.md`: `origin: x-dd` → `origin: evol-dd`.
- `.gitignore`: fix negacion para `.github/prompts/` (la negacion `!.github/` en L73 la
  re-incluia); agregados `.vscode/` y `dudas.md`.

## [0.3.0] - 2026-06-05

### Added
- `/evol setup-repo`: paso 0 antes del briefing. Pregunta ubicacion (existente/crear nube/local)
  + modo (dev/collab). `evol-gitflow.sh setup --create` (gh repo create autonomo, private default),
  `--local` (solo local). ADR-0003.
- `evol-security-inventory.py`: arsenal seguridad por componente. Nativas (scan/shield/crash/
  patch/validate/STRIDE/fuzz, sin instalar) + externas auto-discovery (semgrep/gitleaks/trivy/
  nuclei/zap). SIN Shannon (AGPL) — exploit-verify manual. `--readme` documenta todo antes de instalar.
- `.agent/workflows/briefing.md`: idea.md como puntapie con prompt de investigacion (tabla de
  links/temas a investigar que alimenta la fase research).
- evol-sprint.md seccion 5.5: evalua desempeno de subagentes ANTES del gitflow (evol-eval.py),
  bloquea si score bajo. Suite evals/subagent-performance/.

### Changed
- evol-historias.md: checklist STDD por componente (invoca security-inventory).
- doc-granular.md: clarifica grupo 4-roles por documento en paralelo.

## [0.2.9] - 2026-06-04

### Added
- `evol-doc-sync.py`: motor JSON/MD de ahorro de tokens. Genera sidecar .json compacto
  desde cada .md (fuente de verdad). INDEX.json por carpeta + maestro. Ahorro ~95% navegando.
- `evol-openapi-merge.py`: mergea fragments OpenAPI por recurso en raiz valida (stdlib+pyyaml).
- `evol-discipline-check.py`: check_json_sidecar + check_atomic_folder + 8 wrappers + CLI `folder`.
- `evol-memory.py`: MEMORY.md -> 3 atomos (decisiones/convenciones/riesgos) + agregado generado
  + subcomando `memory-split` para migrar monolitico legacy.
- `evol-init.sh`: esqueleto atomico idempotente (sprints/, features/, domain/, privacy/,
  openapi/fragments/ + 3 atomos MEMORY + UBIQUITOUS_LANGUAGE.md).
- DOC_STANDARD seccion 7: contrato JSON/MD + regla de consumo obligatoria.

### Changed
- Workflows evol-historias/evol-sprint/cierre-fase: sprint.md -> acuerdos/sprints/,
  MEMORY.md -> atomos. Lectura via INDEX.json (ahorro tokens).

## [0.2.7] - 2026-06-04

### Added
- `evol-memory sprint-close --sprint=NN`: crea `acuerdos/memoria/sprint-NN.md` + `acuerdos/lecciones/sprint-NN.md` + `INDEX.md` idempotente (INC E5)
- `evol-init.sh`: genera `acuerdos/memoria/MEMORY.md` (hechos persistentes) + `acuerdos/lecciones/INDEX.md` en bootstrap (INC E5)
- Workflow `evol-historias.md` (`/evol historias`): historias con 4 artefactos cada una via pipeline worker-auditor; checklist >=50 tareas; genera `acuerdos/sprint.md` (INC E6)
- Workflow `evol-sprint.md` (`/evol sprint`): ciclo completo de sprint — equipo dinamico por componente tecnico, auditor permanente, eval pre-push, GitFlow (INC E6)
- `evol-gitflow.sh`: GitFlow automatizado — `setup --mode=dev|collab`, `sprint-start`, `sprint-close`, `pre-push` (gitignore + gitleaks), `status` (INC E7)
- `evol-discipline-check.py`: valida CONTENIDO por disciplina (SDD/FDD/DDD/Threat-Driven/BDD/TDD/STDD/SecDD). Activar con `EVOL_DISCIPLINE=1` (INC E8)
- `evol-gate.py approve()`: llama `_check_discipline()` cuando `EVOL_DISCIPLINE=1` (INC E8)

### Changed
- `cierre-fase.md` v1.4: usa `evol-memory sprint-close` en lugar de append monolitico (INC E5)
- `evol-memory.py`: `--project` va ANTES del subcomando (argparse global)

### Fixed
- `acuerdos/memoria/` y `acuerdos/lecciones/` incluyen `MEMORY.md` + `INDEX.md` desde bootstrap

## [0.1.0] - 2026-06-02

### Added
- Framework core with CLI entrypoints (gate, eval, flow, provider, shield, orchestrate, agent, evolve, research, memory, lessons)
- GitFlow branching strategy with develop/main/release process
- HMAC-signed gate protocol for approval workflow
- Memoria Persistente memory integration for agent context persistence
- Agent registry with 18 core agents and ephemeral agent lifecycle
- Eval harness with structural, behavioral, output_match, pass_at_k graders
- Security shield with secret detection and config auditing
- Skills supply chain with quarantine, pinning, and secret scanning
- Shell/Bash hooks for pre/post operations (edit, bash, write)
- Security hooks: dangerous command blocking, config protection, auto-organize
- Doctor diagnostic tool with JSON output and exit codes
- Brand adapter for trigger-based IDE configuration generation
- Agent lifecycle management (create, invoke, retire, recall)
- Workflow orchestration (sequential, parallel, party patterns)
- State management with SQLite and JSON-based gate log
- Release checklist with real gates and commands
- Tag strategy with semver and Conventional Commits enforcement

### Changed
- Security-hardened evol-brand.sh with YAML parsing and JSON serialization
- Security-hardened evol-adapt.sh with strict trigger validation

### Fixed
- Source gitignore tracking scripts, prompts, skills, templates, evals, schemas, src, tests, .github
- evol-init.sh with profile manifest system (minimal, core, developer, security, research, full, lean)
- evol-naming strict mode with all xdd references migrated to evol
- Gate HMAC chain with payload persistence and verify-on-read
- Memoria Persistente safe indexing with explicit allowlist (no `.evol/`, `.xdd/`, `.git/`, dialog/, tool_result/)
- Security hooks with structured JSON input and real blocking for dangerous commands
- CI as real gate without `|| true` masks, running pytest, shield, doctor, registry validation
- Hermetic tests using EVOL_HOME, EVOL_STATE_DB, EVOL_PROJECT_DIR overrides with tmp_path fixtures
- Eval harness with list, validate, run, report commands
- Registry validation with strict schema checking (retired consistency, unique IDs, skill references)
- Python dependencies in pyproject.toml with jsonschema as actual dependency
- Doctor blocking mode with --json output and CRITICAL/HIGH exit codes
- Security shield with --ci, --output, --no-write, --format flags and gitleaks/semgrep integration
- Skills supply chain with quarantine, SHA pin enforcement, and secret scanning
- evol-brand.sh sanitized with YAML parser and JSON serializer
- evol-adapt.sh sanitized with TRIGGER regex `[A-Za-z0-9_-]+` and realpath validation