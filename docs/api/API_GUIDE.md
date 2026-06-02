# API GUIDE — Referencia CLI de Evol-DD

Evol-DD es un framework CLI-first. No expone una API REST ni un servidor de procesos. Toda la interaccion ocurre a traves de comandos de terminal instalados via pip, scripts bash en `scripts/`, y slash commands del IDE generados por `evol-adapt.sh`. Esta guia cubre los tres niveles de la interfaz.

---

## Entry-points pip

Instalados automaticamente con `pip install evol-dd`. Disponibles en PATH despues de la instalacion.

| Comando | Modulo | Descripcion | Ejemplo |
|---------|--------|-------------|---------|
| `evol` | `evol_cli:main` | Dispatcher principal. Enruta subcomandos al script correspondiente. | `evol doctor` |
| `evol-gate` | `evol_cli:gate` | Gate keeper HMAC-SHA256. Gestiona aprobaciones de fase con cadena de integridad. | `evol-gate approve --phase spec` |
| `evol-eval` | `evol_cli:eval_` | Eval harness con 4 tipos de grader. Valida y ejecuta suites de evaluacion. | `evol-eval run --suite mi-skill` |
| `evol-flow` | `evol_cli:flow` | Ejecuta flujos declarativos YAML con MockProvider o AnthropicProvider. | `evol-flow run flows/ci.yaml` |
| `evol-provider` | `evol_cli:provider` | Puerto LLM hexagonal. MockProvider determinista para tests, AnthropicProvider para produccion. | `evol-provider status` |
| `evol-shield` | `evol_cli:shield` | Auditoria de seguridad estatica del framework. Detecta MCP configs, secrets y refs peligrosas. | `evol-shield audit --ci --no-write` |
| `evol-orchestrate` | `evol_cli:orchestrate` | Runtime multi-agente. Patrones: sequential, parallel, parallel_then_sync. | `evol-orchestrate run plan.yaml` |
| `evol-agent` | `evol_cli:agent` | Ciclo de vida de agentes efimeros: create, invoke, retire, recall, gc. | `evol-agent create --name x --task y` |
| `evol-evolve` | `evol_cli:evolve` | Motor de evolucion. Genera skills desde patrones de instincts con quarantine/pin. | `evol-evolve propose --min-confidence 0.8` |
| `evol-research` | `evol_cli:research` | Investigacion autonoma. Propone mejoras de skills, metodologias y frameworks. | `evol-research propose "async patterns"` |
| `evol-memory` | `evol_cli:memory` | Motor de memoria conversacional (stdlib puro). load, summarize, compact, search, gc. | `evol-memory load` |
| `evol-lessons` | `evol_cli:lessons` | Motor de lecciones aprendidas. add, search, list, suggest-fix, apply-fix. | `evol-lessons search "jwt"` |
| `evol-profile` | `evol_cli:profile` | Gestion de perfiles de instalacion. list, show, explain, init, upgrade, validate. | `evol-profile explain developer` |

---

## Scripts principales

Scripts bash y python en `scripts/`. Ejecutables directamente sin `pip install`, utiles para CI y bootstrapping de proyectos nuevos.

| Script | Descripcion | Flags importantes |
|--------|-------------|-------------------|
| `scripts/evol-doctor.sh` | Diagnostico completo del entorno. Verifica perfil, manifiesto, archivos requeridos, permisos, scripts, dependencias y entrypoints. | `--json` para output JSONL maquina-legible |
| `scripts/evol-init.sh` | Bootstrap de proyecto desde templates. Copia modulos segun perfil, genera .gitignore, inicializa git. | `<dest> --profile=<profile>`, `--pip-mode`, `--list-profiles`, `--explain=<profile>`, `--dry-run` |
| `scripts/evol-start.sh` | Arranca el sistema: carga ultima sesion de memoria, verifica estado. | Sin flags adicionales |
| `scripts/evol-global-install.sh` | Instala framework globalmente en `~/.local/bin`. Requerido para perfil `lean`. | Sin flags adicionales |
| `scripts/evol-adapt.sh` | Genera configs de IDE desde SSoT en `.agent/workflows/`. | `<target>` donde target es: `claude-code`, `opencode`, `cursor`, `windsurf`, `vscode-copilot`, `antigravity`, `codex`, `all`. Flags: `--dry-run`, `--trigger=<trigger>` |
| `scripts/evol-brand.sh` | Aplica white-labeling al proyecto desde `evol.profile.yml`. | Sin flags principales |
| `scripts/evol-gate.py` | Gate keeper ejecutable directamente. Mismo que `evol-gate` entry-point. | `init`, `approve --phase <name>`, `validate`, `status`, `transition --from <f> --to <t>` |
| `scripts/evol-shield.py` | Auditoria de seguridad. Mismo que `evol-shield` entry-point. | `audit`, `--ci` (exit 1 en CRITICAL/HIGH), `--no-write`, `--output <file>` |
| `scripts/evol-eval.py` | Eval harness. Mismo que `evol-eval` entry-point. | `validate --suite <name>`, `run --suite <name>`, `run --all`, `report --suite <name>` |
| `scripts/evol-lessons.py` | Motor de lecciones. Mismo que `evol-lessons` entry-point. | `add`, `search <query>`, `list`, `list --pendientes`, `suggest-fix "<titulo>"`, `apply-fix "<titulo>"` |
| `scripts/evol-memory.py` | Motor de memoria. Mismo que `evol-memory` entry-point. | `load`, `summarize [--messages-file <f>]`, `compact`, `search <query>`, `gc` |
| `scripts/evol-agent-lifecycle.py` | Ciclo de vida de agentes efimeros. | `create --name <n> --task <t>`, `invoke <name> <prompt>`, `retire <name>`, `recall <name>`, `gc` |
| `scripts/validate-registry.py` | Valida `prompts/agents/registry.json` contra schema. | `--strict` activa validaciones de referencias cruzadas |
| `scripts/lint-workflows.sh` | Lint de frontmatter YAML de workflows. | Sin flags adicionales |
| `scripts/generate-equipo.sh` | Regenera `docs/equipo.md` desde `prompts/agents/registry.json`. | Sin flags adicionales |
| `scripts/bump-version.py` | Actualiza VERSION, pyproject.toml y CHANGELOG.md. | `<nueva-version>` como argumento posicional |

---

## Variables de entorno

Las variables de entorno controlan el comportamiento del framework en tiempo de ejecucion. Ninguna es obligatoria — el sistema degrada graciosamente cuando no estan definidas.

| Variable | Tipo | Defecto | Descripcion |
|----------|------|---------|-------------|
| `EVOL_MEMORY` | flag (`1`/`0`) | no definida | Activa el motor de memoria conversacional nativo. Cuando es `1`, los hooks `SessionStart` y `Stop` ejecutan `evol-memory load` y `evol-memory summarize` automaticamente. |
| `EVOL_PROVIDER` | string | `mock` | Proveedor LLM. Valores: `mock` (determinista, sin red), `anthropic`. Requiere `LLM_API_KEY` cuando se usa `anthropic`. |
| `LLM_API_KEY` | string | no definida | API key del proveedor LLM. Requerida cuando `EVOL_PROVIDER=anthropic`. Si no esta definida, el sistema usa `MockProvider` independientemente de `EVOL_PROVIDER`. |
| `EVOL_GITNEXUS` | flag (`1`/`0`) | no definida | Activa la integracion con GitNexus para code intelligence. Solo para proyectos no-comerciales (licencia PolyForm-NC). |
| `EVOL_HOOK_PROFILE` | string | `default` | Perfil de hooks activo. Controla que hooks se ejecutan y con que severidad. Valores tipicos: `default`, `strict`, `ci`. |
| `EVOL_HOOK_BYPASS` | string | no definida | Nombre del hook a omitir para el comando actual. Ejemplo: `EVOL_HOOK_BYPASS=pre:bash`. Solo para uso en depuracion — no usar en produccion. |
| `EVOL_DATA_DIR` | path | directorio del script | Directorio raiz del framework. Usado por scripts para resolver rutas a `templates/`, `schemas/`, `prompts/`. Cuando no esta definida, los scripts resuelven la ruta relativa al `$0`. |
| `EVOL_HOME` | path | `~/.evol` | Directorio de datos globales del usuario. Contiene `state.db` (instincts SQLite) y archivos de configuracion global. |
| `EVOL_STATE_DB` | path | `~/.evol/state.db` | Ruta explicita a la base de datos SQLite de instincts. Sobreescribe `EVOL_HOME` para el archivo de state. Util para aislar entornos en CI. |
| `EVOL_TRIGGER` | string | `evol` | Trigger word usado por `evol-adapt.sh` al generar los slash commands de los IDEs. Permite white-labeling del trigger. |
| `EVOL_MEMORY_COMPACT_THRESHOLD` | integer | `90000` | Numero de caracteres acumulados en journales antes de que `evol-memory compact` se ejecute. |
| `EVOL_MEMORY_COMPACT_RESERVE` | integer | `10000` | Caracteres reservados para el resumen generado por compact. |
| `EVOL_MEMORY_TOOL_TTL_DAYS` | integer | `3` | Dias de retencion de archivos en `tool_result/`. `evol-memory gc` elimina los que superan este TTL. |

---

## Flujo completo: crear agente efimero end-to-end

Este ejemplo muestra todos los comandos involucrados en el ciclo de vida completo de un agente efimero, desde la creacion hasta el recall posterior.

### Prerequisitos

```bash
# Verificar que el template existe
ls templates/agent.template.md

# Verificar que el registry es valido
python3 scripts/validate-registry.py --strict
```

### Creacion

```bash
evol-agent create \
  --name "api-contract-auditor" \
  --task "Auditar contratos OpenAPI del proyecto para detectar breaking changes entre v1 y v2" \
  --expires-after 14
```

El agente queda registrado en `prompts/agents/registry.json` con categoria `ephemeral` y su archivo en `prompts/agents/ephemeral/<timestamp>-api-contract-auditor.md`.

### Invocacion

```bash
evol-agent invoke api-contract-auditor \
  "Comparar docs/api/v1/openapi.yaml con docs/api/v2/openapi.yaml e identificar breaking changes"
```

O desde Claude Code:

```
/evol [invocar api-contract-auditor para comparar v1 y v2 de la API]
```

### Cierre de tarea

Al terminar, el agente debe registrar sus decisiones en `memoria.md`. Luego se retira:

```bash
evol-agent retire api-contract-auditor
```

El archivo del agente se mueve a `.evol/agents/retired/`. El registro en `registry.json` se marca como retirado.

### Recall posterior

Meses despues, si se necesita el mismo agente para una nueva version:

```bash
evol-agent recall api-contract-auditor
```

El sistema reconstruye el agente con el contexto original mas las lecciones aprendidas desde su retiro.

### Limpieza de agentes vencidos

```bash
evol-agent gc
# Elimina agentes efimeros cuyo expires_after_days fue superado
```

---

## Flujo completo: crear skill end-to-end

Las skills son capacidades reutilizables con casos de prueba propios. Este es el flujo desde el draft hasta que la skill esta en produccion.

### Paso 1 — Generar el draft inicial

Desde Claude Code:

```
/crear-skill
```

El workflow interactivo hace preguntas sobre la skill y genera:

```
skills/
  nombre-skill/
    SKILL.md
evals/
  nombre-skill/
    cases.jsonl
    grader.yaml
```

### Paso 2 — Validar la estructura

```bash
python3 scripts/evol-eval.py validate --suite nombre-skill
```

Verifica que `cases.jsonl` tiene el formato correcto y que `grader.yaml` referencia un tipo de grader valido (`structural`, `behavioral`, `output_match`, `pass_at_k`).

### Paso 3 — Ejecutar los evals

```bash
python3 scripts/evol-eval.py run --suite nombre-skill
```

Ejecuta los casos contra la definicion de la skill usando `MockProvider` (por defecto). Para evals contra el LLM real:

```bash
EVOL_PROVIDER=anthropic LLM_API_KEY=$LLM_API_KEY \
  python3 scripts/evol-eval.py run --suite nombre-skill
```

### Paso 4 — Revisar el reporte

```bash
python3 scripts/evol-eval.py report --suite nombre-skill
```

El reporte muestra: casos pasados, casos fallidos, score por tipo de grader y recomendaciones de mejora.

### Paso 5 — Auditoria de seguridad

```bash
python3 scripts/evol-shield.py audit --ci --no-write
```

Verifica que la skill no referencia internals del framework (`.evol/`, `.gate-key`, `state.db`). Las skills tienen acceso restringido al scope publico del sistema.

### Paso 6 — Regenerar adapters

```bash
bash scripts/evol-adapt.sh all
```

Si la skill incluye un workflow asociado en `.agent/workflows/`, `evol-adapt.sh all` lo distribuye a todos los IDEs configurados.

### Paso 7 — Commit

```bash
git add skills/nombre-skill/ evals/nombre-skill/
git commit -m "feat(skills): add nombre-skill capability"
```

---

## Exit codes y comportamiento de error

| Comando | Exit 0 | Exit 1 | Exit 2 |
|---------|--------|--------|--------|
| `evol doctor` | Todos los checks CRITICAL y HIGH pasaron | Al menos un check CRITICAL o HIGH fallo | — |
| `evol-gate validate` | Cadena HMAC integra | Tamper detectado o log vacio | — |
| `evol-gate approve` | Aprobacion registrada y firmada | Key no inicializada o error de escritura | — |
| `evol-shield audit --ci` | Sin violaciones CRITICAL ni HIGH | Al menos una violacion CRITICAL o HIGH | — |
| `evol-eval run` | Todos los casos pasaron | Al menos un caso fallo | Error de configuracion o suite no encontrada |
| `python3 scripts/validate-registry.py --strict` | Registry valido | Violacion de schema | Error de archivo no encontrado |
| `bash scripts/lint-workflows.sh` | Todos los workflows validos | Al menos un workflow con frontmatter invalido | — |

### Errores de configuracion comunes

Todos los scripts de Python importan `_evol_common.py`. Si el import falla con `ModuleNotFoundError`, el script no fue ejecutado desde la raiz del proyecto ni con `EVOL_DATA_DIR` configurado:

```bash
# Forma incorrecta (desde directorio arbitrario):
python3 /ruta/al/proyecto/scripts/evol-eval.py run --suite x
# ModuleNotFoundError: No module named '_evol_common'

# Forma correcta:
cd /ruta/al/proyecto
python3 scripts/evol-eval.py run --suite x

# O con PYTHONPATH:
PYTHONPATH=/ruta/al/proyecto/scripts python3 /ruta/al/proyecto/scripts/evol-eval.py run --suite x
```

### Modo fail-closed del gate

El gate opera en modo fail-closed: en ausencia de informacion, falla con exit 1. Esto es intencional. Si el gate-key no existe, si el log esta vacio, o si la cadena esta rota, el gate no adivina — bloquea.

```bash
evol-gate validate
# Exit 1 si:
#   - .evol/.gate-key no existe
#   - .evol/.gate-log.jsonl no existe o esta vacio
#   - Cualquier entrada falla verificacion HMAC
#   - previous_hash de una entrada no coincide con hash de la anterior
```

Para reinicializar el gate en un proyecto nuevo:

```bash
evol-gate init
# Crea .evol/.gate-key (permisos 0600) y .evol/.gate-log.jsonl vacio
```
