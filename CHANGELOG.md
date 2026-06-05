# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## [Unreleased]

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
- MemPalace memory integration for agent context persistence
- Agent registry with 16 core agents and ephemeral agent lifecycle
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
- MemPalace safe indexing with explicit allowlist (no `.evol/`, `.xdd/`, `.git/`, dialog/, tool_result/)
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