# lecciones.md — Aprendizajes Acumulados

> Lecciones aprendidas del proyecto. Consultado por agentes antes de proponer
> soluciones (Constitucion Art. 9). Motor: `scripts/evol-lessons.py`.
> Actualizar via `/evol cierre-fase` o `evol-lessons add`.

## Formato

```
### [CATEGORIA] Titulo breve — YYYY-MM-DD
**Contexto:** Que estabamos intentando hacer.
**Problema:** Que fallo o sorprendio.
**Causa raiz:** Por que paso.
**Leccion:** Regla aplicable a futuras decisiones.
**Aplica a:** Ambito donde aplica.
**Fix aplicado:** Que se hizo para resolver. (opcional)
**Mejoras sugeridas:** Propuestas del investigador. (opcional)
**Estado mejoras:** pendiente | en-progreso | aplicado (opcional)
```

Categorias: `ARQUITECTURA` `SEGURIDAD` `DOMINIO` `TESTING` `DEVOPS` `PROCESO` `HERRAMIENTAS`

Comandos rapidos:
- `evol-lessons search QUERY` — buscar antes de decidir
- `evol-lessons add --titulo ... --categoria ... --leccion ...` — añadir
- `evol-lessons suggest-fix "titulo"` — investigador propone mejoras
- `evol-lessons list --pendientes` — ver mejoras pendientes

---

## ARQUITECTURA

### [ARQUITECTURA] Gate key global compromete aislamiento — 2026-06-02
**Contexto:** Diseñando sistema de gates en Evol-DD
**Problema:** Key global compartida entre proyectos elimina invariante de auditoria
**Causa raiz:** Decision de simplificacion de UX sacrifico seguridad
**Leccion:** Gate key por proyecto — evol gate init --from-global como punto de partida
**Aplica a:** Todo proyecto con evol-gate.py

### [ARQUITECTURA] evol-cli debe despachar scripts vía subprocess — 2026-06-02
**Contexto:** entrypoints en `pyproject.toml` apuntaban a funciones que importaban módulos inexistentes
**Problema:** Scripts usaban guiones (`evol-gate.py`) que no son importables como `scripts.evol_gate`
**Causa raiz:** Arquitectura mixta: scripts como CLI standalone y como módulos Python
**Leccion:** Opción A: convertir scripts a módulos Python importables. Opción B (elegida): despachar vía `subprocess.run` a scripts instalados. Nunca mezclar las dos sin contrato claro.
**Aplica a:** CLI packaging, entrypoints

### [ARQUITECTURA] Runtime state no debe indexarse en MemPalace — 2026-06-02
**Contexto:** Indexing de `.evol/`, `dialog/`, `tool_result/` podía exponer secrets
**Problema:** `.evol/.gate-key` entraba a indices semánticos
**Causa raiz:** Indexing con path amplio sin allowlist
**Leccion:** Usar allowlist explícita para indexing. Excluir siempre: `.evol/`, `.xdd/`, `.git/`, `dialog/`, `tool_result/`, `memory/raw/`, `*.key`, `*.pem`, `.env*`. Secret scan antes de indexar.
**Aplica a:** Memory systems, agent indexers

## SEGURIDAD

### [SEGURIDAD] Hooks warning-only no bloquean operaciones peligrosas — 2026-06-02
**Contexto:** Hooks existentes solo warn sobre comandos peligrosos
**Problema:** `rm -rf /`, `curl | sh`, `sudo` no autorizado, force push a ramas protegidas no se bloquean
**Causa raiz:** Hooks diseñados como advisory, no enforcement
**Leccion:** Para governance files y comandos destructivos, convertir hooks en blocking por defecto. Violations deben requerir approval gate explícito.
**Aplica a:** Agent hooks, CI pre-commit

### [SEGURIDAD] Global gate key compromete aislamiento entre proyectos — 2026-06-02
**Contexto:** Gate key compartida globalmente entre todos los proyectos
**Problema:** Un proyecto comprometido afecta la auditoría de todos
**Causa raiz:** Decisión de UX (simplicidad) sacrificó seguridad
**Leccion:** Gate key por proyecto. Usar `evol gate init --from-global` solo como bootstrap inicial, no como operación normal.
**Aplica a:** Security architecture, audit systems

### [SEGURIDAD] evol-shield falsos positivos en docs de seguridad — se escanea a si mismo — 2026-06-02
**Contexto:** Corriendo evol-shield audit --ci antes del release. 34 violations criticas reportadas
**Problema:** El propio evol-shield.py contenia los patrones que buscaba (mcpServers, rm -rf). Docs de seguridad (THREATS.md, PRIVACY.md) mencionan los patrones como referencia
**Causa raiz:** Falta de skip_dirs por regla. La regla no distingue entre 'contener un patron peligroso' y 'documentar ese patron como amenaza'
**Leccion:** Herramientas de audit deben excluirse a si mismas y a docs de seguridad. Añadir skip_dirs por regla, no solo por archivo. Distinguir: docs que describen amenazas vs codigo que las implementa
**Aplica a:** evol-shield.py y cualquier herramienta SAST propia. Regla: siempre skipear scripts/evol-shield.py, docs/seguridad/, tests/
**Fix aplicado:** Añadido skip_dirs por regla a no_mcp_config, no_dangerous_commands, no_evol_dangerous_refs. Excluido el propio shield y docs de seguridad

## DOMINIO

_(vacio)_

## TESTING

_(vacio)_

## DEVOPS

### [DEVOPS] .gitignore no debe ignorar directorios fuente críticos — 2026-06-02
**Contexto:** Corrigiendo integrity del repo para que clones contengan código ejecutable
**Problema:** Directorios fuente como `scripts/`, `src/`, `templates/` estaban en `.gitignore`
**Causa raiz:** Template generado para proyectos destino se usó incorrectamente en el repo fuente
**Leccion:** El `.gitignore` del repo fuente debe ignorar solo runtime state (`.evol/`, `.cache/`, `__pycache__/`). Los source dirs siempre se trackean.
**Aplica a:** Cualquier framework distribuible

### [DEVOPS] Dependencias no declaradas rompen packaging en CI — 2026-06-02
**Contexto:** `validate-registry.py` importa `jsonschema` pero no estaba en `pyproject.toml`
**Problema:** `pip install -e .` no instala deps reales; CI falla silenciosamente
**Causa raiz:** Dependencies agregadas directamente a scripts sin actualizar manifest de package
**Leccion:** Cada import en scripts Python debe tener corresponding entry en `dependencies` de `pyproject.toml`. Dependency audit como gate.
**Aplica a:** Python packaging, CI

### [DEVOPS] CI masks (`|| true`) ocultan fallos reales y rompen gates — 2026-06-02
**Contexto:** CI usaba `|| true` para hacer pasar comandos que fallaban
**Problema:** Test fallidos, shield findings, doctor errors no rompen CI
**Causa raiz:** Debug residual o miedo a fallos en primer CI run
**Leccion:** Eliminar todo `|| true`, `|| echo`, `set +e` que convierten fallo en éxito. CI debe fallar ruidosamente ante errores reales.
**Aplica a:** CI/CD, release gates

### [DEVOPS] Evals stubs rompen quality gates — 2026-06-02
**Contexto:** `evol-eval.py` era stub sin implementación real
**Problema:** `evals/*/cases.jsonl` y `grader.yaml` no se ejecutaban; no había quality gate agental
**Causa raiz:** Evals implementados como placeholders después de código principal
**Leccion:** Eval harness es gate crítico. Implementar desde Sprint 0, no post-hoc.
**Aplica a:** Quality assurance, agentic systems

### [DEVOPS] Registry validation debe ser strict por defecto — 2026-06-02
**Contexto:** `validate-registry.py` con `--strict` era la única forma de detectar inconsistencias
**Problema:** Entradas de test (`test-agent`), campos inconsistentes (`retired: false` + `retired_at` presente) pasaban sin `--strict`
**Causa raiz:** Validation diseñada para ser laxa por defecto
**Leccion:** Strict validation debe ser default. Lax mode debe ser explícito y documentado.
**Aplica a:** Agent registry, metadata validation

### [DEVOPS] Version debe tener single source of truth — 2026-06-02
**Contexto:** Version duplicada en `VERSION`, `pyproject.toml`, `src/evol_cli/__init__.py`
**Problema:** Desincronización entre archivos; release tags inconsistentes
**Causa raiz:** Copy-paste de version entre archivos manualmente
**Leccion:** Un archivo canonical para version (ej: `VERSION`). Otros lo consumen vía script. Tag coincide con contenido de `VERSION`.
**Aplica a:** Release management, versioning

### [DEVOPS] Skills supply chain sin quarantine permite instalar código malicioso — 2026-06-02
**Contexto:** `evol-evolve.py` copiaba skills sin validación ni scanning
**Problema:** Skills con secretos o malware podían instalarse directamente a `.claude/skills/`
**Causa raiz:** Trust sin verificación en supply chain
**Leccion:** Descargar a quarantine temporal → validar schema/frontmatter → secret scan → semgrep si aplica → pin SHA para remotos → registrar hash → instalar solo si todos checks pasan.
**Aplica a:** Skill management, agentic tool supply chain

### [DEVOPS] pyproject.toml data-files va a /usr/share/, no al wheel — 2026-06-02
**Contexto:** Intentando empaquetar scripts/, manifests/, templates/ dentro del wheel de evol-dd
**Problema:** setuptools data-files instala en /usr/share/ del sistema. evol --version reportaba 0.1.0-dev stale y evol init --list-profiles fallaba sin manifests
**Causa raiz:** Confusion entre data-files (para el sistema operativo) y package-data/force-include (para dentro del wheel)
**Leccion:** Usar hatchling con force-include para empaquetar data dirs dentro del wheel. Verificar con zipfile que el wheel contiene los dirs antes de publicar
**Aplica a:** Todo framework Python con data dirs (scripts/, manifests/, templates/) que necesite funcionar en instalacion pipx/wheel sin repo local
**Fix aplicado:** Migrado setuptools → hatchling. force-include: scripts→evol_cli/scripts, manifests→evol_cli/manifests, templates→evol_cli/templates, VERSION→evol_cli/VERSION. _data_dir() con logica 3 niveles.

## PROCESO

### [PROCESO] Docs deben reflejar implementacion real, no aspiración — 2026-06-02
**Contexto:** Docs contenían placeholders TBD y claims sin respaldo de código
**Problema:** Documentación ahead of implementation crea falsas expectativas
**Causa raiz:** Docs escritas en paralelo sin validación contra código
**Leccion:** Cada claim en docs release-critical debe tener script, test o workflow que lo verifique. Placeholders TBD rompen gates hasta que se resuelven.
**Aplica a:** Technical documentation, release readiness

### [PROCESO] 53 de 69 workflows sin name/trigger en frontmatter — lint falla silencioso — 2026-06-02
**Contexto:** Corriendo lint-workflows.sh antes del release. 104 warnings reportados
**Problema:** Los workflows heredados de X-DD tenian description en frontmatter pero sin name ni trigger. Lint reportaba warnings que no bloqueaban el build
**Causa raiz:** Al adaptar los 69 workflows de X-DD a Evol-DD solo se cambiaron referencias /xdd → /evol pero no se completaron los campos de frontmatter requeridos
**Leccion:** Al heredar workflows de otro sistema, verificar que el schema de frontmatter este completo. Lint warnings no bloquean build pero indican deuda tecnica real. Corregir antes de publicar.
**Aplica a:** Cualquier migracion de workflows entre sistemas. El lint debe ser gate bloqueante, no informativo
**Fix aplicado:** Script Python corrigio 53 workflows: añadio name (slug del filename) y trigger (/evol <slug>) a cada uno

## HERRAMIENTAS

### [HERRAMIENTAS] YAML parsing con grep/cut/tr es frágil y vulnerable a inyección — 2026-06-02
**Contexto:** `evol-brand.sh` usaba `grep | cut | tr` para parsear YAML
**Problema:** Valores con `/`, `&`, comillas o espacios rompen sed/json output
**Causa raiz:** Bash string processing no escala para structured data
**Leccion:** Parsear YAML/JSON con parsers dedicados (Python `yaml`/`json` modules). Nunca interpolations raw en sed sin escaping.
**Aplica a:** Bash scripts que procesan config estructurada

### [HERRAMIENTAS] Validación de input con regex débil permite path traversal — 2026-06-02
**Contexto:** `evol-adapt.sh` aceptaba TRIGGER sin validación estricta
**Problema:** `../x` o `a/b` podían influir rutas de salida
**Causa raiz:** Input del usuario pasado directamente a path sin sanitization
**Leccion:** Validar inputs con regex estricta (`^[A-Za-z0-9_-]+$`). Verificar `realpath` final queda dentro de directorio permitido.
**Aplica a:** Any script that builds paths from user input

### [HERRAMIENTAS] evol-adapt.sh hardcodeaba REPO_ROOT — ignoraba --dest completamente — 2026-06-02
**Contexto:** Intentando que evol adapt opencode generara commands en el proyecto del usuario
**Problema:** Todas las funciones generate_*() usaban REPO_ROOT hardcodeado. validate_output_path() bloqueaba cualquier path externo. Resultado: 0 archivos generados en proyectos externos
**Causa raiz:** Script escrito asumiendo que siempre se corre desde el repo del framework, no desde un proyecto consumidor
**Leccion:** Adapters IDE deben recibir DEST como argumento explícito. Nunca hardcodear el directorio de origen como destino. Testear siempre con --dest=/tmp/test-dir externo al repo
**Aplica a:** Todo script de generacion de configs IDE en frameworks distribuibles
**Fix aplicado:** Reescrito evol-adapt.sh: DEST variable con default PWD, todas las generate_*() reciben dest como argumento, eliminados validate_output_path y check_file_exists

### [HERRAMIENTAS] Triggers IDE no globales — /evol invisible en carpetas sin bootstrap — 2026-06-02
**Contexto:** Usuario instalo evol-dd via pipx en otro equipo y el trigger /evol no aparecia en Claude Code ni OpenCode al abrir una carpeta vacia
**Problema:** evol adapt all genera configs POR PROYECTO en dirs locales (.claude/commands/, .opencode/command/). Sin bootstrap del proyecto, el IDE no ve el trigger
**Causa raiz:** Arquitectura correcta para triggers por-proyecto pero erronea para triggers globales. Comparar con /anmax: vive en ~/.claude/commands/ global
**Leccion:** Para que un trigger sea global (disponible en CUALQUIER carpeta), debe copiarse a los dirs globales de cada IDE: ~/.claude/commands/, ~/.config/opencode/command/, ~/.cursor/rules/, ~/.codeium/workflows/, ~/.config/Code/User/prompts/, ~/.gemini/skills/, ~/.codex/skills/. Un solo comando post-instalacion debe hacer todo esto
**Aplica a:** Todo framework distribuible via pip que quiera que su trigger sea global. El flujo correcto es: pip install → un comando de setup global → listo en todos los IDEs
**Fix aplicado:** evol-install-global (entry-point pip): copia /evol a dirs globales de 7 IDEs en un solo comando

