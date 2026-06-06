# Evol-DD — Prompt de Construcción del Sistema

## Contexto

Debes construir desde cero un framework de desarrollo agéntico llamado **Evol-DD**.

Evol-DD es un sistema independiente inspirado espiritualmente en X-DD (Cross-Driven Development), pero con identidad propia, arquitectura diferente y capacidades nuevas. No es un fork ni un clon — es un framework nuevo que reutiliza los patrones más probados de X-DD y añade capacidades ausentes en ese sistema.

El directorio de trabajo actual (`evol-dd/`) es el repositorio raíz. Todo lo que construyas debe vivir aquí.

---

## Identidad del sistema

- **Nombre:** Evol-DD
- **Trigger CLI principal:** `/evol`
- **Tagline:** "El framework que evoluciona."
- **Color brand:** `#7C3AED`
- **Filosofía central:** El sistema acumula conocimiento y propone mejoras con cada proyecto que construye. "Evoluciona" significa aprendizaje asistido por humano — el sistema descubre, propone y registra; un humano aprueba antes de que cualquier cambio se aplique. La evolucion es asistida, no autonoma.

---

## Diferencias fundamentales respecto a X-DD

Antes de construir cualquier cosa, debes entender estas diferencias, porque definen la arquitectura de Evol-DD:

### 1. Pocos agentes permanentes, muchos efímeros

X-DD tiene ~180 agentes permanentes en disco. Eso genera sobrecarga de contexto y dificulta el mantenimiento.

Evol-DD tiene **17 agentes core permanentes**. Para cualquier labor especializada que exceda esos 17, el sistema crea un **agente efímero**: existe mientras se necesita, se retira cuando termina su tarea, y su conocimiento queda indexado en Memoria Persistente para poder ser recuperado en el futuro sin recrearlo desde cero.

### 2. Integración Nativa MCP

X-DD usa un servidor MCP propio y Memoria Persistente en modo MCP. Evol-DD usa integración nativa de servidores MCP (Model Context Protocol) por defecto en todos los IDEs. Memoria Persistente se usa exclusivamente en modo CLI (`Memoria Persistente index`, `Memoria Persistente search`) como herramienta local, no como servidor. Los adapters IDE deben configurar e integrar los servidores MCP.

### 3. Auto-generación de skills

El sistema detecta patrones recurrentes en su base de conocimiento (SQLite) y propone nuevas skills automáticamente. Un humano aprueba antes de activar. Las skills generadas son compatibles con la especificación de Claude Code (frontmatter `name + description` mínimo).

### 4. Compatibilidad con skills de la comunidad

El sistema puede detectar skills publicadas en GitHub (topic: `claude-code-skill`, `evol-dd-skill`), evaluar su compatibilidad, y generar wrappers locales para instalarlas. Esto permite que Evol-DD crezca con el ecosistema.

### 5. Agente investigador autónomo

Un agente permanente (`evol-researcher`) investiga proactivamente: nuevas skills Claude Code publicadas, metodologías emergentes, changelogs de dependencias, papers relevantes. Propone mejoras rankeadas para el sistema o el proyecto activo. Toda propuesta requiere aprobación humana antes de aplicarse.

### 6. Documentación granular como artefacto de primera clase

Cada proyecto construido con Evol-DD genera documentación completa y detallada. El agente `evol-doc` produce documentos con diagramas Mermaid obligatorios, tablas para datos estructurados, casos Gherkin completos, y sin emoticonos.

### 7. .gitignore generado automaticamente en el bootstrap

`evol-init.sh` genera `.gitignore` como **primer paso**, antes de copiar cualquier archivo.
Esto garantiza que git no trackee nunca el tooling del framework — solo el codigo del proyecto.

El `.gitignore` generado desde `templates/gitignore.template` contiene 3 categorias:
- **Framework Evol-DD** (scripts/, prompts/, skills/, templates/, evals/, schemas/) — el tooling es accesible via wrapper global, no debe commitearse como copia local
- **Configs IDE generadas** (.claude/commands/, .opencode/, .github/prompts/, .cursor/, .windsurf/, .agents/skills/) — son OUTPUT de evol-adapt.sh, no fuente
- **Estado operativo** (.evol/, .xdd/, dialog/, tool_result/) — runtime, no versionable

Lo que SI se committea (override explicito en el .gitignore): `memoria.md`, `lecciones.md`,
`AGENT_MEMORY.md`, `memory/`, `evol.profile.yml`, `CLAUDE.md`, `AGENTS.md`,
`.agent/hooks/`, `.agent/workflows/`, `.github/workflows/`, `docs/`.

### 8. GitFlow enforced via pre-commit hook

El hook `pre:commit:gitflow` bloquea commits en branches que no siguen la convencion:

```
feature/nombre-de-la-feature    ← nueva funcionalidad
fix/descripcion-del-fix         ← correccion de bug
hotfix/critico                  ← fix urgente en produccion
release/v1.2.0                  ← preparacion de release
chore/tarea-de-mantenimiento    ← tareas sin impacto en producto
docs/actualizacion-docs
refactor/nombre
```

Branches siempre permitidos: `main`, `develop`.
El hook vive en `.agent/hooks/scripts/pre-commit-gitflow.sh` y se registra en `hooks.json`.

### 9. Especificaciones de aceptacion granulares (obligatorio por feature)

Cada feature del `FEATURES.md` produce un bloque Gherkin con esta estructura minima en `CASOS_GHERKIN.md`:

```gherkin
Feature: [nombre en lenguaje de negocio]
  Como [rol del usuario]
  Quiero [accion especifica]
  Para [beneficio medible]

  # HAPPY PATH — obligatorio
  Scenario: [caso exitoso principal]
    Given [estado inicial exacto del sistema]
    When [accion del usuario o evento]
    Then [resultado observable y verificable]
    And [efecto secundario si aplica]

  # ERROR — minimo 1 obligatorio
  Scenario: [error mas probable]
    Given [condicion que provoca el error]
    When [accion del usuario]
    Then [mensaje de error especifico con codigo/texto exacto]
    And [estado del sistema despues del error]

  # CASOS BORDE — minimo 1 obligatorio con Examples
  Scenario Outline: [variacion de inputs criticos]
    Given [estado con "<variable>"]
    When [accion]
    Then [resultado "<resultado>"]

    Examples:
      | variable       | resultado          |
      | valor_normal   | exito              |
      | limite_min     | exito_limite       |
      | limite_max     | exito_limite       |
      | valor_invalido | error_validacion   |
```

Reglas de granularidad (obligatorias):
- Maximo 8 escenarios por feature. Si hay mas, partir en sub-features.
- Maximo 5 pasos por escenario.
- Vocabulario exclusivamente del DOMAIN.md (Ubiquitous Language). Cero sinonimos.
- Cada escenario referencia su `REQ-NNN` via comentario `# REQ-NNN`.
- Examples SIEMPRE incluyen: caso normal, limite inferior, limite superior, caso invalido.
- Los valores de los Examples deben ser valores concretos, no placeholders genericos.

DoD de la fase de requisitos: cada feature tiene 1 happy path + >=1 error + >=1 borde,
todos los terminos en Gherkin existen en DOMAIN.md, y la matriz trazabilidad REQ-NNN <->
Scenario esta completa antes de pasar a la fase de plan.

### 10. Mismo mecanismo de instalación que X-DD pre-v0.2

El sistema se instala exactamente igual que X-DD en su versión pre-release 0.2: wrapper en `~/.local/bin/`, manifests JSON para módulos y perfiles, `evol-init.sh` que bootstrappea proyectos, `evol-adapt.sh` que genera configs reales (no symlinks) para 7 IDEs.

### 11. AGENTS.md — governance manifest para OpenCode

`AGENTS.md` en la raíz es el manifiesto de governance para OpenCode (equivalente a `CLAUDE.md` para Claude Code). El adapter `adapt_opencode` de `evol-adapt.sh` lo copia al proyecto destino si no existe. Su contenido define: el directorio de agentes core, el trigger `/evol`, la constitución, y el directorio `docs/equipo.md` (registro auto-generado desde registry.json). Debe existir en el repo de Evol-DD con contenido real — no es un archivo generado, es un artefacto versionado.

---

## Arquitectura del sistema

### Los 17 agentes core permanentes

**Criterio formal core vs efimero:** un agente es core si tiene responsabilidad sobre el estado del sistema (gobernanza, arquitectura, seguridad, orquestacion) — independientemente del dominio del proyecto. Un agente es candidato a efimero si su responsabilidad es exclusivamente sobre el dominio del proyecto activo (ej: marketing-seo-specialist, data-pipeline-analyst). Los 17 agentes core nunca se retiran porque el sistema no puede funcionar sin ellos.

Estos agentes viven en `prompts/agents/core/` y nunca se retiran. Son el núcleo inmutable del sistema:

1. `evol-architect` — Diseño de sistemas, decisiones arquitectónicas, ADRs
2. `evol-builder` — Implementación de código, TDD, construcción de features
3. `evol-qa` — Calidad, tests unitarios, integración, E2E, casos Gherkin/BDD
4. `evol-sec` — Seguridad (SecDD, threat modeling STRIDE, auditoría)
5. `evol-devops` — CI/CD, infraestructura, pipelines, automatización
6. `evol-domain` — DDD, modelado de dominio, entidades, bounded contexts
7. `evol-doc` — Documentación técnica granular (reglas estrictas: sin emoticonos, Mermaid obligatorio, tablas, Gherkin completo)
8. `evol-ux` — Discovery de usuarios, investigación de producto, validación
9. `evol-data` — Data engineering, analytics, pipelines de datos
10. `evol-reviewer` — Code review, peer review, análisis de calidad
11. `evol-orchestrator` — Lead de composición de agentes, coordination patterns
12. `evol-pm` — Gestión de proyecto, seguimiento, sprints, métricas
13. `evol-release` — Release management, CHANGELOG, versionado semántico
14. `evol-analyst` — Análisis de impacto, métricas, blast radius
15. `evol-agent-factory` — Crea agentes efímeros de forma guiada e interactiva
17. `evol-researcher` — Investigación autónoma de mejoras (skills, metodologías, frameworks)

### Contrato de agent.template.md (base de todos los agentes efímeros)

`templates/agent.template.md` es el artefacto mas critico del sistema de efimeros — define el prompt base de cada agente creado. Debe ser el **primer artefacto del modulo lifecycle-agents** antes que `evol-agent-lifecycle.py`. Estructura obligatoria:

```markdown
---
name: {{agent_name}}
description: {{descripcion_una_linea}}
category: ephemeral
created_for_task: {{tarea_especifica}}
expires_after_days: {{dias}}
created_at: {{ISO8601}}
---

# {{agent_name}}

## Mision
{{descripcion_de_la_tarea_especifica_para_la_que_fue_creado}}

## Alcance
{{que_puede_y_no_puede_hacer_este_agente}}

## Contexto del proyecto
{{referencias_a_DOMAIN.md_memoria.md_lecciones.md_relevantes}}

## Restricciones
- No puede modificar archivos de gobernanza (constitucion, gate, hooks).
- No puede crear otros agentes efimeros.
- Debe registrar sus decisiones en memoria.md al finalizar.
```

**Distincion factory vs orchestrator:**
- `evol-agent-factory`: decide SI crear un agente efimero y lo crea (invoca evol-agent-lifecycle.py create). Criterio de decision: la tarea requiere un rol especializado que ninguno de los 17 agentes core cubre.
- `evol-orchestrator`: decide COMO coordinar agentes ya existentes (core o efimeros). No crea agentes — los invoca.
No se solapan: factory = creacion, orchestrator = coordinacion.

### Ciclo de vida de agentes efímeros

Los agentes efímeros son ciudadanos de primera clase del sistema. El ciclo es:

```
CREAR → INVOCAR → RETIRAR → [RECALL si se necesita de nuevo]
```

**Crear:**
```bash
python3 scripts/evol-agent-lifecycle.py create \
  --name "marketing-seo-specialist" \
  --task "Auditoría SEO del proyecto actual" \
  --expires-after 30
```
Esto:
- Genera `prompts/agents/ephemeral/<timestamp>-marketing-seo-specialist.md` desde `templates/agent.template.md`
- Registra en `registry.json` con flags `ephemeral: true`, `expires_after`, `created_for_task`
- Indexa en Memoria Persistente: `Memoria Persistente index --path prompts/agents/ephemeral/`

**Retirar:**
```bash
python3 scripts/evol-agent-lifecycle.py retire "marketing-seo-specialist"
```
Esto:
- Elimina el archivo `.md` del filesystem
- Actualiza registry: `retired: true`, `retired_at`, `sessions_used`
- Archiva snapshot completo en `.evol/agents/retired/<name>.json` (prompt + metadata + sessions)
- Memoria Persistente retiene el conocimiento indexado (no lo borra)


**Recuperar:**
```bash
python3 scripts/evol-agent-lifecycle.py recall "marketing-seo-specialist"
```
Esto:
- Busca en `.evol/agents/retired/` y Memoria Persistente
- Reconstruye el `.md` y re-registra con `recalled: true`, `recalled_at`
- Disponible sin necesidad de crearlo desde cero

**Nota sobre calidad del recall:** el recall semantico (contexto de por que el agente tomo decisiones, que aprendio) requiere que Memoria Persistente haya indexado el agente ANTES de ser retirado. Si Memoria Persistente no estaba activo al momento del `retire`, el recall recupera solo el snapshot JSON (prompt + metadata) — no el conocimiento semantico. El snapshot JSON siempre esta disponible; el contexto semantico es adicional y condicional. `evol-agent-lifecycle.py recall` debe reportar explicitamente si el recall es "completo" (JSON + semantico) o "basico" (solo JSON).

### Auto-generación de skills (evol-evolve)

```bash
# Ver cuántos patrones candidatos hay:
python3 scripts/evol-evolve.py status

# Generar propuestas de skills (sin aplicar):
python3 scripts/evol-evolve.py run --dry-run

# Aplicar propuestas (requiere aprobación humana):
python3 scripts/evol-evolve.py run
python3 scripts/evol-evolve.py approve CLUSTER_ID

# Sincronizar skills de la comunidad:
python3 scripts/evol-evolve.py sync-community --dry-run
python3 scripts/evol-evolve.py install-skill SKILL_NAME
```

### Agente investigador (`evol-researcher`)

```bash
python3 scripts/evol-researcher.py run --scope system
python3 scripts/evol-researcher.py run --scope project --topic "testing"
python3 scripts/evol-researcher.py list
python3 scripts/evol-researcher.py apply PROPOSAL_ID
```

Genera `RESEARCH.md` con propuestas rankeadas. Toda propuesta requiere aprobación humana antes de aplicarse.

---

## Estructura de directorios que debes crear

```
evol-dd/
├── .agent/
│   ├── hooks/
│   │   ├── hooks.json
│   │   └── scripts/
│   └── workflows/
├── .evol/
│   ├── agents/
│   │   └── retired/
│   └── qa/
├── docs/
│   ├── arquitectura/
│   │   ├── ARQUITECTURA.md
│   │   ├── DOMINIO.md
│   │   ├── DECISIONES.md
│   │   └── adr/
│   ├── requisitos/
│   │   ├── FUNCIONALES.md
│   │   ├── NO_FUNCIONALES.md
│   │   ├── RESTRICCIONES.md
│   │   └── GLOSARIO.md
│   ├── diagramas/
│   │   ├── flujo-datos.md
│   │   ├── componentes.md
│   │   ├── despliegue.md
│   │   └── secuencia-*.md
│   ├── qa/
│   │   ├── PLAN_QA.md
│   │   ├── CASOS_GHERKIN.md
│   │   ├── MATRIZ_TRAZABILIDAD.md
│   │   ├── CASOS_BORDE.md
│   │   ├── REPORTE_QA.md
│   │   └── CHECKLIST_RELEASE.md
│   ├── seguridad/
│   │   ├── THREATS.md
│   │   ├── PRIVACY.md
│   │   └── SECURITY_CONTROLS.md
│   ├── api/
│   │   ├── openapi.yaml
│   │   └── API_GUIDE.md
│   ├── guias/
│   │   ├── ONBOARDING.md
│   │   ├── CONTRIBUCION.md
│   │   └── TROUBLESHOOTING.md
│   ├── usuario/
│   │   ├── MANUAL_USUARIO.md
│   │   └── FAQ.md
│   ├── operaciones/
│   │   ├── RUNBOOK.md
│   │   ├── DR_PLAN.md
│   │   └── MONITORING.md
│   ├── constitucion.md
│   ├── evol-dd_Integration_Guide.md
│   ├── RETROFIT_GUIDE.md
│   ├── CONFIG.md
│   ├── GATE.md
│   ├── IDE_SETUP.md
├── evals/
├── manifests/
│   ├── install-modules.json
│   ├── install-profiles.json
│   └── install-components.json
├── prompts/
│   ├── agents/
│   │   ├── core/
│   │   ├── ephemeral/
│   │   ├── registry.json
│   │   └── registry.schema.json
│   └── orchestrator/
│       └── personas/
├── schemas/
├── scripts/
│   ├── evol-init.sh
│   ├── evol-start.sh
│   ├── evol-adapt.sh
│   ├── evol-doctor.sh
│   ├── evol-gate.py
│   ├── evol-state.py
│   ├── evol-orchestrate.py
│   ├── evol-evolve.py
│   ├── evol-agent-lifecycle.py
│   ├── evol-researcher.py
│   ├── evol-memory.py          ← motor nativo memoria conversacional
│   ├── evol-lessons.py         ← motor nativo lecciones aprendidas + ciclo mejora
│   ├── evol-eval.py
│   ├── evol-shield.py
│   ├── evol-provider.py
│   ├── evol-flow.py
│   ├── evol-brand.sh
│   ├── evol-update.py
│   ├── evol-global-install.sh
│   ├── _evol_common.py         ← utilidades compartidas (memoria_persistente_safe, etc.)
│   ├── lint-workflows.sh
│   ├── validate-registry.py
│   ├── generate-equipo.sh
│   └── hooks/
├── skills/
│   ├── evol-fs-context/
│   ├── evol-compact/
│   ├── evol-talk-compact/
│   ├── evol-ai-review/
│   ├── evol-sandbox/
│   ├── agent-eval/
│   └── evol-skill-manager/
├── templates/
│   ├── memoria.template.md
│   ├── lecciones.template.md
│   └── agent.template.md
├── tests/
├── CLAUDE.md
├── AGENTS.md
├── INSTALL.md
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
├── evol.profile.yml
├── evol.config.yml
├── pyproject.toml
├── VERSION
├── memoria.md
├── lecciones.md
├── WORKING-CONTEXT.md
├── AGENT_MEMORY.md                   ← long-term memory conversacional (versionable)
├── memory/
│   └── YYYY-MM-DD.md           ← journal diario por sesion (versionable)
├── dialog/                     ← dialogo raw antes de compactacion (gitignored)
└── tool_result/                ← cache tool outputs TTL 3d (gitignored)
```

Agregar a `.gitignore`: `dialog/` y `tool_result/`.

---

## Scripts que debes construir

### Scripts heredados de X-DD (adaptar, no copiar literalmente)

Estos scripts tienen equivalentes probados en X-DD. Debes construirlos con el mismo mecanismo pero renombrados y con soporte MCP completo:

**`evol-init.sh`** — Bootstrap de proyectos
- Lee `manifests/install-modules.json` e `install-profiles.json`
- Resuelve módulos según el perfil solicitado
- Copia artefactos selectivos al directorio destino
- Auto-detecta IDEs instalados (claude-code, opencode, cursor, windsurf, vscode-copilot, antigravity, codex)
- Invoca `evol-adapt.sh` para cada IDE detectado
- Configura git hooks (`core.hooksPath`)
- Materializa hooks en `~/.claude/settings.json` (idempotente, no destructivo)
- Variables de opt-out: `EVOL_NO_ADAPT`, `EVOL_NO_HOOKS`, `EVOL_NO_GITHOOK`, `EVOL_NO_BRAND`, `EVOL_NO_GATE_INIT`

**`evol-start.sh`** — Arranca el sistema
- Inicia Memoria Persistente en modo CLI: `Memoria Persistente index --wing evol-dd --path .`
- SÍ arranca y gestiona servidores MCP
- Carga contexto de la última sesión: `Memoria Persistente search "last_session"`

**`evol-adapt.sh`** — Genera configs IDE (copia real, NUNCA symlinks)
- Soporta targets: `claude-code`, `opencode`, `cursor`, `windsurf`, `vscode-copilot`, `antigravity`, `codex`, `all`
- Para cada IDE genera archivos reales en las rutas canónicas de ese IDE
- SIEMPRE habilita la sección MCP en configuraciones compatibles
- Resuelve trigger: `--trigger` flag > `evol.profile.yml` branding > "evol" por defecto
- Modo seco: `evol-adapt.sh <target> --dry-run`

**`evol-doctor.sh`** — Diagnóstico del entorno
- Verifica dependencias: git, Python 3.10+, Memoria Persistente CLI, Node
- Verifica estructura del proyecto: directorios requeridos, archivos core
- Reporta warnings sin bloquear (salvo errores críticos)
- Flag `--json` para output estructurado

**`evol-gate.py`** — Gate keeper HMAC-SHA256
- Mismo mecanismo que xdd-gate.py de X-DD
- Comandos: `init`, `validate`, `transition`, `approve`, `status`
- Firma HMAC-SHA256 para "APROBADO" auditable
- `.evol/.gate-key` gitignored

**`evol-state.py`** — State store SQLite
- Mismo mecanismo que xdd-state.py de X-DD
- Tablas base: `instincts`, `instinct_sessions`, `sprints`, `orchestrations`, `evolutions`
- Tablas nuevas (no existen en X-DD):
  - `agent_lifecycle`: registra create/invoke/retire/recall con timestamps y sessions_used
  - `research_proposals`: propuestas del evol-researcher con status y score
- Comandos: `init`, `record-instinct`, `list`, `evolve`, `prune`, `stats`

**`evol-orchestrate.py`** — Runtime multi-agente
- Mismo mecanismo que xdd-orchestrate.py de X-DD
- Patterns: `sequential`, `parallel`, `parallel_then_sync`, `party`
- Comandos: `list`, `run --pattern=NAME`, `run --pattern=NAME --exec`, `status`

**`evol-provider.py`** — Abstracción de LLM providers
- MockProvider determinista (tests sin red)
- AnthropicProvider lazy (sin red por defecto)
- Soporta providers MCP nativos

**`evol-flow.py`** — Gate ejecutable de flujos declarativos
- Corre flujos seq/parallel con MockProvider
- Valida ejecución real, no solo archivos

**`evol-eval.py`** — Eval harness
- 5 grader types: structural, behavioral, output_match, pass_at_k, llm_judge
- Suite por skill: `evals/<nombre>/cases.jsonl` + `grader.yaml`

**`evol-shield.py`** — AgentShield audit del framework
- Audit estático de seguridad del framework mismo
- Output: `.evol/qa/QA_REPORT.md`

**`evol-brand.sh`** — White-labeling
- Aplica branding custom al proyecto instalado
- Lee configuración desde `evol.profile.yml`

**`evol-global-install.sh`** — Instalación global
- Instala wrapper en `~/.local/bin/evol-init.sh`
- Compatible con `local-first` fallback a global

### Scripts nuevos (no existen en X-DD)

**`evol-agent-lifecycle.py`** — Ciclo de vida de agentes efímeros

Comandos:
- `create --name NAME --task DESCRIPTION [--expires-after DAYS]`
  - Genera `.md` desde `templates/agent.template.md`
  - Registra en registry.json con `ephemeral: true`
  - Indexa Memoria Persistente: `Memoria Persistente index --path prompts/agents/ephemeral/`
- `invoke NAME` — activa el agente para la sesión actual
- `retire NAME`
  - Elimina `.md`
  - Actualiza registry: `retired: true`, `retired_at`, `sessions_used`
  - Archiva en `.evol/agents/retired/<name>.json` (snapshot: prompt + metadata + sessions)
  - Memoria Persistente retienen el índice
- `recall NAME`
  - Busca en `.evol/agents/retired/` y Memoria Persistente
  - Reconstruye `.md` y re-registra con `recalled: true`
- `list [--ephemeral] [--retired] [--all]`

**`evol-evolve.py`** — Auto-generación de skills y sync con comunidad

Comandos:
- `run [--dry-run] [--min-confidence 0.7]`
  - Lee instincts de evol-state.py con confidence > threshold
  - Agrupa por similitud (keyword overlap como fallback)
  - Genera `skills/<nombre>/SKILL.md` + `evals/<nombre>/`
  - Registra propuesta en tabla `evolutions` (status: proposed)
  - Requiere aprobación humana antes de activar
- `status` — cuántos instincts candidatos hay
- `approve CLUSTER_ID` — aprueba propuesta, indexa Memoria Persistente
- `invalidate INSTINCT_ID [--reason TEXTO]` — marca instinct como invalido (anti-patron detectado); reduce confidence a 0 y agrega flag `invalidated: true`. Previene que decisiones incorrectas repetidas se promuevan a skills.
- `rollback SKILL_NAME` — revierte una skill auto-generada ya aprobada: desactiva el SKILL.md, marca la evolucion como `rolled_back`, preserva el archivo en `skills/<nombre>/.retired/` para auditoria.

**Notas arquitectonicas criticas:**
- El umbral `min-confidence: 0.7` no tiene justificacion empirica — es un valor inicial que debe calibrarse en los primeros sprints de uso real.
- El decay por tiempo (last_seen) perjudica a usuarios con uso esporadico. Un patron correcto aprendido hace 60 dias puede expirar antes de alcanzar confidence suficiente. Implementar con esta limitacion documentada; recalibrar en v0.2.
- Toda skill auto-generada y aprobada debe tener un eval suite en `evals/<nombre>/` que verifique que hace lo que se propuso antes de activarse. Sin eval, la skill no se activa.
- `sync-community [--dry-run]`
  - Busca repos GitHub con topics: `claude-code-skill`, `evol-dd-skill`
  - Valida frontmatter mínimo: `name` + `description`
  - Evalúa colisión con skills existentes
  - Lista skills compatibles disponibles para instalar
- `install-skill SKILL_NAME` — copia skill externa + genera wrapper local + registra

**`evol-researcher.py`** — Investigación autónoma

Comandos:
- `run [--scope system|project] [--topic TOPIC]`
  - Fuentes: GitHub (skills, frameworks, agentic AI), changelogs de dependencias
  - Genera `RESEARCH.md` con propuestas rankeadas por impacto
  - Persiste propuestas en tabla `research_proposals` de evol-state.py
- `list` — propuestas pendientes de revisión
- `apply PROPOSAL_ID` — aplica propuesta aprobada

**Contrato de fallo explícito (obligatorio — no implementar sin esto):**

| Caso de fallo | Comportamiento |
|---------------|----------------|
| GitHub no responde (timeout) | Warning + continuar con cache local si existe; sin cache → exit 0 con mensaje "sin conexion, propuestas omitidas" |
| Rate-limit GitHub (403/429) | Reportar limite activo + tiempo hasta reset; no crashear; usar cache de ultima ejecucion si disponible |
| LLM no disponible (EVOL_PROVIDER=anthropic sin key) | Caer a mock provider; las propuestas seran stubs marcados como "[mock — requiere LLM real]" |
| Skill descargada falla scan supply-chain | Bloquear instalacion + reportar motivo especifico; el resto de propuestas no se ven afectadas |
| gitleaks/semgrep no instalados | Warning no bloqueante: "scan omitido — instalar gitleaks+semgrep para habilitar supply-chain check"; registrar en propuesta el flag `scan_skipped: true` |

Nota arquitectonica: `evol-lessons suggest-fix` llama a este script internamente. Una operacion local aparentemente simple (proponer mejora para una leccion) puede desencadenar una llamada de red. Documentar este comportamiento en el help del comando.

---

## Modos de operacion del sistema

Evol-DD opera en dos modos segun la disponibilidad de Memoria Persistente. El modo es auto-detectado
por `evol-start.sh` y `evol-doctor.sh`. Documentar en `docs/modos.md`.

### Protocolo de jerarquia de los 3 sistemas de memoria

Los tres sistemas son complementarios con roles distintos. En caso de informacion contradictoria, la precedencia es:

1. **`memoria.md`** — verdad del proyecto. Estado de fases, decisiones arquitectonicas, hitos. Escrito por el agente. Nunca sobreescrito por otro sistema.
2. **`AGENT_MEMORY.md` + `memory/`** — contexto de sesion del agente. Preferencias, patrones, reflexiones. Complementa memoria.md, no la reemplaza.
3. **Memoria Persistente** — busqueda semantica sobre el codebase. Recupera contexto relevante por query, no por cronologia.

Ningun sistema sobreescribe a otro. Si divergen, el agente los trata como fuentes distintas: memoria.md para decisiones de proyecto, AGENT_MEMORY.md para estilo de trabajo, Memoria Persistente para encontrar codigo/docs relevantes.

**Definicion de "sesion":** una sesion comienza cuando el agente recibe la primera instruccion del usuario y termina cuando el usuario cierra la interaccion o el agente ejecuta el hook Stop. Una sesion puede abarcar multiples tareas del mismo dia. El journal `memory/YYYY-MM-DD.md` puede tener N sesiones si el usuario abre y cierra varias veces en el mismo dia — cada sesion añade una seccion nueva al journal, no lo sobreescribe.

### Memoria Persistente

Memoria Persistente instalado y activo (CLI only — `Memoria Persistente index`, `Memoria Persistente search`).
Aporta continuidad semantica automatica entre sesiones: el agente "recuerda" el proyecto,
lecciones y patrones detectados sin que el usuario repita contexto.

Lo que aporta sobre Modo Base:
- Indexacion semantica del codebase (busqueda RAG sobre codigo y docs).
- Continuidad automatica entre sesiones sin repetir contexto manual.
- Pattern-extraction de instincts para `evol-evolve`.
- `recall` de agentes efimeros recupera contexto semantico, no solo el snapshot JSON.

### Modo Base

Sin Memoria Persistente. El pipeline Evol-DD funciona completamente — todos los workflows, todos los
agentes, el Gated Pipeline de 6 fases, las lecciones acumuladas (manual) y los gates
HMAC siguen disponibles. Instalacion en menos de 2 minutos.

Lo que se pierde:
- Continuidad semantica automatica (se suple leyendo `memoria.md` + `lecciones.md` al inicio).
- Busqueda RAG sobre el codebase.
- Pattern-extraction automatica de instincts (se puede hacer manual).
- `recall` de agentes efimeros usa solo el snapshot JSON local (`.evol/agents/retired/`).

### Modo memoria conversacional (opt-in)

Sistema nativo de memoria conversacional persistente. Sin dependencias externas.
Implementado en `scripts/evol-memory.py` — stdlib Python puro.

Arquitectura inspirada en ReMe (agentscope-ai/ReMe, Apache-2.0): misma estructura de
archivos, mismos prompts de compactacion y summarizacion, mismo comportamiento. Pero
completamente propio de Evol-DD — sin pip install de terceros.

Activar con `EVOL_MEMORY=1`.

Estructura de archivos generada en cada proyecto:

```
<proyecto>/
├── AGENT_MEMORY.md                   # long-term: hechos, preferencias, decisiones clave (versionable)
├── memory/
│   └── YYYY-MM-DD.md           # journal diario: resumen estructurado por sesion (versionable)
├── dialog/
│   └── YYYY-MM-DD.jsonl        # dialogo raw antes de compactacion (gitignored)
└── tool_result/
    └── <uuid>.txt              # cache tool outputs, TTL 3 dias (gitignored)
```

Agregar a `.gitignore` del proyecto: `dialog/` y `tool_result/`.

| Aspecto | Memoria Persistente | Memoria conversacional |
|---------|-----------|------------------------|
| Que indexa | Archivos del repo | Conversaciones del agente |
| Busqueda | RAG codebase | BM25 sobre historial |
| Persistencia | Indice semantico | AGENT_MEMORY.md + journal diario |

Con `EVOL_MEMORY=1`:
1. `session:start` — carga `AGENT_MEMORY.md` + journal del dia anterior.
2. `stop` — escribe/actualiza `memory/YYYY-MM-DD.md` + gc de `tool_result/` vencidos (async).

Comandos del motor:

| Comando | Descripcion |
|---------|-------------|
| `evol-memory load` | Carga sesion (hook SessionStart) |
| `evol-memory summarize [--messages FILE]` | Persiste sesion en journal (hook Stop) |
| `evol-memory compact --messages FILE` | Compacta historial largo en summary estructurado |
| `evol-memory search QUERY` | BM25 sobre AGENT_MEMORY.md + journals |
| `evol-memory gc [--days N]` | Purga tool_result/ con TTL vencido (default 3 dias) |
| `evol-memory stats` | Estado del sistema |

Variables de entorno:

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `EVOL_MEMORY` | `0` | Activa el sistema |
| `EVOL_PROVIDER` | `mock` | Provider LLM para summarizacion (`mock` o `anthropic`) |
| `EVOL_MEMORY_COMPACT_THRESHOLD` | `90000` | Tokens para disparar compactacion |
| `EVOL_MEMORY_COMPACT_RESERVE` | `10000` | Tokens a reservar de mensajes recientes |
| `EVOL_MEMORY_LANGUAGE` | `""` | Idioma del journal |
| `EVOL_MEMORY_TOOL_TTL_DAYS` | `3` | TTL de tool_result/ en dias |

El modulo `continuous-memory` en `install-modules.json` instala:
- `scripts/evol-memory.py` — motor nativo (load, summarize, compact, search, gc, stats)
- `docs/memory-system.md` — documentacion y configuracion
- `.agent/hooks/scripts/session-start-memory-load.sh` — hook SessionStart
- `.agent/hooks/scripts/stop-memory-summarize.sh` — hook Stop

Añadir `continuous-memory` a los perfiles `developer`, `research` y `full`.
`evol-doctor` reporta `memory_mode: "active" | "inactive"`. `evol-start` imprime el modo al arrancar.

Formato del journal (`memory/YYYY-MM-DD.md`):

Cada sesion escribe:
```markdown
## Sesion YYYY-MM-DDTHH:MM:SS

## Factual Memory
[Hechos objetivos, estados del proyecto, eventos importantes]

## Reflections & Logic
[Estrategias reutilizables, errores a evitar, insights para futuras sesiones]
```

Formato del summary compactado (compatible como system prompt de la siguiente sesion):
```markdown
## Goal / ## Progress (Done/In Progress/Blocked) / ## Key Decisions / ## Next Steps / ## Critical Context
```

### Sistema de lecciones aprendidas (nativo, siempre activo)

Motor nativo de gestion de lecciones aprendidas. Implementado en `scripts/evol-lessons.py`
— stdlib Python puro, sin dependencias. Port de `xdd-lessons.py` con prefijo `evol`.
Siempre activo — `lecciones.md` es parte del core, no opt-in.

Formato extendido de leccion (compatible con X-DD + campos nuevos para ciclo de mejora):

```
### [CATEGORIA] Titulo breve — YYYY-MM-DD
**Contexto:** Que estabamos intentando hacer.
**Problema:** Que fallo o sorprendio.
**Causa raiz:** Por que paso.
**Leccion:** Regla aplicable a futuras decisiones.
**Aplica a:** Ambito donde aplica.
**Fix aplicado:** Que se hizo para resolver (opcional).
**Mejoras sugeridas:** Propuestas del investigador (generadas por evol-researcher).
**Estado mejoras:** pendiente | en-progreso | aplicado (opcional).
```

Categorias: `ARQUITECTURA`, `SEGURIDAD`, `DOMINIO`, `TESTING`, `DEVOPS`, `PROCESO`, `HERRAMIENTAS`.

Comandos del motor:

| Comando | Descripcion |
|---------|-------------|
| `evol-lessons add --titulo ... --categoria ... --contexto ... --problema ... --causa ... --leccion ... --aplica ...` | Añade leccion. Deduplicacion automatica fuzzy (Jaccard 70%). |
| `evol-lessons add --fix-aplicado "descripcion del fix"` | Incluye fix ya implementado al añadir. |
| `evol-lessons suggest-fix "titulo de leccion" [--apply]` | El agente investigador propone mejoras concretas para esa leccion. Con `--apply` guarda las mejoras en lecciones.md (estado: pendiente). |
| `evol-lessons apply-fix "titulo" --fix "descripcion"` | Marca mejoras como aplicadas, registra que se implemento. |
| `evol-lessons search QUERY [--max N] [--categoria CAT]` | BM25 sobre todas las lecciones. Muestra fix y mejoras si existen. |
| `evol-lessons suggest QUERY [--max N]` | Lecciones relevantes formateadas para inyectar como contexto al agente. |
| `evol-lessons extract --messages FILE [--auto]` | Extrae lecciones candidatas desde JSONL de sesion. Con --auto las añade directamente. |
| `evol-lessons list [--categoria CAT] [--pendientes] [--limit N]` | Lista lecciones. `--pendientes` muestra solo las con mejoras pendientes. |
| `evol-lessons stats` | Total, por categoria, mejoras pendientes/aplicadas. |
| `evol-lessons gc` | Elimina duplicados exactos de lecciones.md. |

Ciclo de mejora continua (integracion con evol-researcher):

```
1. Falla o aprendizaje detectado durante sesion
2. evol-lessons add ... --fix-aplicado "fix ya aplicado"
3. evol-lessons suggest-fix "titulo" --apply
   → evol-researcher analiza la leccion y propone mejoras concretas
   → Se guarda en lecciones.md (estado: pendiente)
4. Humano revisa: evol-lessons list --pendientes
5. Implementacion de las mejoras (agente builder/architect)
6. evol-lessons apply-fix "titulo" --fix "implementacion completada"
   → Estado: aplicado
7. evol-lessons search "area relevante" antes de nueva arquitectura
   → El agente consulta lecciones antes de proponer (Art. 9 Constitucion)
```

El modulo `lessons-engine` en `install-modules.json` instala `scripts/evol-lessons.py`.
Incluir en perfiles `core`, `developer`, `research` y `full`.

Variables de entorno para extract/suggest-fix:

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `EVOL_PROVIDER` | `mock` | Provider LLM (`mock` sin red o `anthropic` para sugerencias reales) |


incompatible con uso comercial. Activar solo en proyectos no-comerciales. Documentado en

### Modos de orquestacion multi-agente

`evol-orchestrate.py` soporta 4 patterns de composicion (igual que X-DD):

| Pattern | Descripcion |
|---------|-------------|
| `sequential` | Lead primero, luego specialists en secuencia |
| `parallel` | Lead primero, specialists en paralelo (ThreadPoolExecutor, max 5 workers) |
| `parallel_then_sync` | Paralelo con sync_point formal (timeout 300s por defecto) |
| `party` | N agentes sin lead, contribuciones libres (inspirado en BMAD) |

Cada pattern tiene modo `--exec` (usa AnthropicProvider real) y modo dry-run por defecto
(MockProvider deterministico, sin red, apto para CI).

### Modos de distribucion (install)

`evol-init.sh` auto-detecta el modo de instalacion:

| Modo | Cuando aplica | Que copia |
|------|--------------|-----------|
| `pip` (recomendado) | `evol-dd` instalado via pip | Solo artefactos editables (memoria, lecciones, profile) |
| `legacy` | Sin pip instalado | Copia completa del framework al proyecto destino |
| `lean` | Perfil lean con wrapper global | Falla explicitamente si no hay global install |

Flags: `--pip-mode`, `--legacy`. Auto-detect via `importlib.metadata`.

### Deteccion de modo

```bash
evol-doctor           # human: [Modo operativo] COMPLETO / BASE
evol-doctor --json    # machine: "Memoria Persistente_mode": "complete" | "base"
evol-start            # imprime modo al arrancar
```

---

## Hooks del sistema (event-driven)

El sistema usa hooks bash event-driven, con soporte MCP. Los hooks reciben JSON por stdin y responden con exit codes (0 = permitir, 2 = bloquear PreToolUse).

Hooks requeridos:

| ID | Evento | Perfil | Función |
|----|--------|--------|---------|
| `pre:bash:dangerous-command` | PreToolUse | standard+ | Bloquea `rm -rf/`, `git --force`, `chmod 777`, `curl\|sh` |
| `pre:edit:config-protection` | PreToolUse | strict | Bloquea edición de configs sin justificación |
| `pre:write:doc-file-warning` | PreToolUse | standard+ | Advierte .md fuera de rutas canónicas |
| `pre:tool:temporal-awareness` | PreToolUse | standard+ | Inyecta contexto del sprint activo |
| `post:edit:Memoria Persistente-index` | PostToolUse | minimal+ | Re-indexa Memoria Persistente vía CLI (async) |
| `post:bash:pr-logger` | PostToolUse | standard+ | Loguea URL de PR tras `gh pr create` |
| `post:write:auto-organize` | PostToolUse | standard+ | Mueve docs canónicos a rutas correctas |
| `session:start:context-load` | SessionStart | standard+ | Carga última memoria.md + WORKING-CONTEXT |
| `stop:git-check` | Stop | standard+ | Advierte cambios sin commit al cerrar sesión |
| `stop:pattern-extraction` | Stop | strict | Extrae patrones para instincts SQLite |

Perfiles disponibles vía `EVOL_HOOK_PROFILE`: `minimal`, `standard`, `strict`.

---

## Manifests de instalación

### Perfiles de instalación (`install-profiles.json`)

**Todos los perfiles incluyen `lessons-engine` y `continuous-memory`.**
`lecciones.md` y el sistema de memoria conversacional son parte del core Evol-DD,
no opcionales — aprenden desde la primera sesion independientemente del perfil.

| Perfil | Modulos adicionales sobre el core | Descripcion |
|--------|----------------------------------|-------------|
| `minimal` | core, workflows-core, memory, lessons-engine, continuous-memory | Nucleo minimo. Sin agentes ni hooks extras pero con lecciones y memoria activos. |
| `core` | DEFAULT: + agents-core, gate-keeper, ci-runtime | Perfil estandar para proyectos. |
| `developer` | + hooks-runtime, lifecycle-agents, evolve-skills, researcher | Desarrollo activo con agentes efimeros e investigacion. |
| `security` | + gate-keeper, agent-shield, hooks-strict | Enfasis en SecDD y auditoria. |
| `research` | + eval-harness, evolve-skills, researcher, observability | Investigacion y evolucion continua. |
| `full` | todo | Instalacion completa. |
| `lean` | solo core + wrapper global | <5MB, requiere instalacion global previa. |

### Módulos (`install-modules.json`)

Modulos requeridos (en TODOS los perfiles sin excepcion):
- `core` (required): scripts esenciales, templates, CLAUDE.md, AGENTS.md, docs/constitucion.md
- `workflows-core` (required): `.agent/workflows/` + `prompts/workflows/`
- `lessons-engine` (required en todos): `scripts/evol-lessons.py` — motor de lecciones aprendidas con ciclo de mejora continua. En todos los perfiles porque lecciones.md es parte del core (Constitucion Art. 9).
- `continuous-memory` (required en todos): `scripts/evol-memory.py` + hooks + docs — memoria conversacional persistente. En todos los perfiles porque el sistema aprende desde la primera sesion.

Modulos opcionales:
- `agents-core`: 17 agentes core + registry + schemas
- `hooks-runtime`: sistema de hooks + schemas
- `gate-keeper`: evol-gate.py + docs/GATE.md
- `platform-configs`: configs IDE generadas
- `ci-runtime`: GitHub Actions + pre-commit
- `memory`: templates memoria.md + lecciones.md
- `eval-harness`: evol-eval.py + evals/
- `lifecycle-agents`: evol-agent-lifecycle.py + templates/agent.template.md
- `evolve-skills`: evol-evolve.py + evol-skill-manager skill
- `growth-engine` (required en core+): `skills/crear-skill/` + `skills/crear-agente/` — herramientas nativas de crecimiento del sistema. Permiten al agente crear nuevas skills con loop iterativo de eval y crear agentes guiados con validacion. Incluir en perfiles `core`, `developer`, `research` y `full`. Sin este modulo el sistema no puede crecer ni expandir sus capacidades.
- `researcher`: evol-researcher.py + agente evol-researcher + workflow `/evol research`. Depende de tabla `research_proposals` en evol-state.py.
- `observability`: spans, cost tracking, session replay (NDJSON en .evol/traces/)
- `security-suite`: evol-shield.py + ADRs seguridad

---

## Skills del sistema

Cada skill vive en `skills/<nombre>/SKILL.md` con frontmatter YAML. El frontmatter mínimo requerido es `name` y `description` (compatibilidad Claude Code). Los campos adicionales son propios de Evol-DD.

Skills permanentes del sistema:

| Nombre | Categoría | Trigger | Descripcion |
|--------|-----------|---------|-------------|
| `evol-fs-context` | context-engineering | `/fs-context` | Filesystem-paradigm context curation |
| `evol-compact` | context-engineering | `/compact` | Compactacion de contexto provider-agnostic |
| `evol-talk-compact` | compression | `/compact-talk` | Compresion de output del orquestador |
| `evol-ai-review` | quality-gate | pre-commit hook | Code review AI-powered pre-commit |
| `evol-sandbox` | security | `/sandbox` | Entorno aislado provider-agnostic |
| `agent-eval` | quality-gate | `/eval` | Eval-harness para skills/agents/workflows |
| `evol-skill-manager` | lifecycle | `/skill` | Gestion del ciclo de vida de skills |
| `crear-skill` | **growth** | `/crear-skill` | **Loop iterativo de creacion de skills: captura intencion → draft → evals cuantitativos/cualitativos (runs paralelos with-skill vs baseline) → optimizacion de description (recall/precision >= 0.85) → portabilidad a 7 IDEs. Mecanismo nativo de crecimiento del sistema.** |
| `crear-agente` | **growth** | auto-trigger | **Crea agentes Evol-DD (permanentes o efimeros): genera .md con identidad/mision/reglas/limites, registra en registry.json, crea agent.template.md si no existe. Se activa cuando el usuario dice "crear agente / nuevo agente / necesito un agente para X". Ciclo de vida completo integrado con evol-agent-lifecycle.py.** |

## Herramientas de crecimiento nativas (Growth Engine)

Evol-DD tiene dos skills de crecimiento integradas en el core que permiten al sistema
expandirse con cada proyecto que construye:

### /crear-skill — Creacion iterativa de skills

Loop completo inspirado en anthropics/skills/skill-creator (Apache-2.0), adaptado con
portabilidad a 7 IDEs:

```
1. Capturar intencion (entrevista + investigar skills existentes)
2. Draft SKILL.md con frontmatter: name, description, category, triggers, compatible_with
3. Crear 2-3 casos de prueba realistas
4. Loop eval:
   - Lanzar runs paralelos: with-skill vs baseline (sin skill)
   - Mientras corren: redactar assertions verificables
   - Grader: comparar outputs, calcular pass rate
   - Feedback del usuario → reescribir skill → relanzar
5. Optimizar description para triggering accuracy:
   - Generar 20 queries (10 should-trigger + 10 should-not-trigger)
   - Medir recall y precision — target >= 0.85 en ambos
   - Iterar description hasta alcanzar umbral
6. Portar a 7 IDEs: evol-adapt.sh all
7. Registrar en catalogo + memoria.md
```

La skill vive en `skills/crear-skill/` y se invoca con `/crear-skill` o
`/evol crear-skill`. Compatible con los 7 IDEs via evol-adapt.sh.

Criterio de "skill bien creada":
- Benchmark iter-1: with-skill supera baseline en >= 30pp en assertions objetivas
- Description: recall >= 0.85, precision >= 0.85 sobre 20 trigger queries
- 0 emojis en body, seccion `## Limites` presente, registry valida con validate-registry.py

### crear-agente — Creacion guiada de agentes

Skill que actua como factory interactivo para agentes Evol-DD. Se activa por description
automaticamente (no requiere slash command explicito) cuando el usuario quiere crear un
agente nuevo.

Flujo:

```
1. Entrevistar: que hace, que NO hace, permanente o efimero, categoria, tono
2. Verificar que no existe agente similar (grep en registry.json)
3. Crear prompts/agents/<categoria>/<id>.md con:
   - Frontmatter: name, description, vibe (para efimeros: +ephemeral, expires_after_days, created_for_task)
   - Secciones obligatorias: ## Mision, ## Reglas criticas, ## Como trabajar, ## Limites
   - Sin emojis en body, segunda persona, razonamiento detras de cada regla
4. Registrar en registry.json con todos los campos del schema
5. Validar: python3 scripts/validate-registry.py --strict
6. Para efimeros: ciclo completo via evol-agent-lifecycle.py (create → invoke → retire → recall)
```

Vive en `skills/crear-agente/` con:
- `references/categorias.md` — tabla de categorias con criterios de decision
- `references/agent-template-spec.md` — spec del snapshot JSON para efimeros
- `references/ejemplos.md` — patrones de agentes bien escritos con analisis
- `scripts/validate_agent.py` — validador local (frontmatter, emojis, secciones, registry)
- `evals/` — casos de prueba con assertions objetivas

**Criterio formal core vs efimero** (integrado en la skill):
Un agente es core si tiene responsabilidad sobre el estado del SISTEMA. Es efimero si
su responsabilidad es sobre el dominio del PROYECTO activo. El factory aplica este
criterio para decidir destino (`prompts/agents/core/` vs `prompts/agents/ephemeral/`).

### Ciclo de crecimiento completo

```
Usuario detecta patron recurrente
    ↓
/evol research → evol-researcher propone skill candidata
    ↓
/crear-skill → loop iterativo → skill validada con evals
    ↓
evol-evolve approve → skill activada en el sistema
    ↓
evol-lessons add → leccion registrada con Fix aplicado
    ↓
Sistema aprende: instincts SQLite acumulan confidence
    ↓
evol-evolve run → propone nueva skill automatica desde instincts
    ↓
(ciclo se repite — el sistema crece con cada proyecto)
```

El modulo `growth-engine` en `install-modules.json` instala ambas skills. Incluirlo
en los perfiles `core`, `developer`, `research` y `full`.

---

## Estándar de documentación (global — TODOS los módulos)

Las reglas de documentación NO son exclusivas del agente `evol-doc`. Son ley del sistema
entero. Debes materializarlas como un documento único `docs/DOC_STANDARD.md` (la SSoT del
estándar), y CADA agente, workflow, script o template que emita un artefacto `.md`,
`.yaml` o `.feature` DEBE cumplirlo y referenciarlo.

`docs/DOC_STANDARD.md` define como mínimo:

1. **Cero emoticonos** en todo artefacto generado. Densidad de emoji: 0%. Sin excepciones.
2. **Diagramas Mermaid obligatorios**: C4 (contexto/contenedor/componente), secuencia,
   estado, flujo de datos, despliegue. ASCII solo si Mermaid es imposible.
3. **Tablas para datos estructurados**: requisitos, casos de prueba, matrices, controles,
   métricas, inventarios PII, parámetros.
4. **Gherkin completo**: cada criterio de aceptación con Feature/Scenario/Given/When/Then
   (happy path + error + caso borde), vocabulario del DOMAIN.md.
5. **Profundidad mínima**: cada sección con sub-secciones sustantivas; nada de bullets de
   alto nivel sin desarrollo.
6. **Trazabilidad bidireccional**: identificadores `REQ-NNN`, `NFR-NNN`, `FEAT-NNN`,
   `THR-NNN`, `TC-NNN`, `SEC-REQ-NNN` resuelven en ambas direcciones.
7. **Secciones mínimas y Definition of Done por tipo de artefacto** (ARQUITECTURA, DOMAIN,
   THREATS, FEATURES, requisitos, QA, seguridad).

Materialización obligatoria del estándar en TODOS los puntos de generación:

- El agente `evol-doc` lleva estas reglas hard-coded en su prompt (ver más abajo).
- Cada workflow en `.agent/workflows/` que emite un artefacto incluye un bloque que
  referencia `docs/DOC_STANDARD.md` en su sección de output.
- Cada template en `templates/` cumple las secciones mínimas y termina con su DoD.
- El gate de QA (`/evol qa-review`, Tier 1) rechaza cualquier documento que viole el
  estándar (verificable: grep de emojis = 0, presencia de bloque Mermaid en docs
  estructurales).
- Cualquier agente o workflow nuevo que emita documentación declara conformidad con el
  estándar. No hay artefacto exento.

## Documentación que el agente `evol-doc` debe producir

El agente `evol-doc` tiene estas reglas absolutas en su prompt (subconjunto operativo del
estándar global `docs/DOC_STANDARD.md`):

1. **Sin emoticonos** en ningún documento generado. Nunca.
2. **Diagramas Mermaid obligatorios** para: arquitectura (C4), secuencias de flujo, estados de entidades, componentes, despliegue.
3. **Tablas para datos estructurados**: requisitos, casos de prueba, matrices de trazabilidad, controles de seguridad, métricas.
4. **Casos Gherkin completos**: cada criterio de aceptación de cada historia de usuario tiene su bloque Feature/Scenario/Given/When/Then.
5. **Nivel de detalle máximo**: cada sección tiene sub-secciones. No se admiten listas de alto nivel sin contenido.
6. **Trazabilidad bidireccional**: cada requisito referencia sus casos de prueba. Cada caso de prueba referencia su requisito.

Documentos que produce por proyecto:

- `docs/arquitectura/ARQUITECTURA.md` — descripción de la arquitectura con diagramas C4 (Context, Container, Component)
- `docs/arquitectura/DOMINIO.md` — modelo DDD completo: entidades, value objects, agregados, servicios de dominio, bounded contexts
- `docs/requisitos/FUNCIONALES.md` — tabla completa: ID, historia de usuario, criterio de aceptación, prioridad, estado
- `docs/requisitos/NO_FUNCIONALES.md` — tabla: ID, categoría (rendimiento/disponibilidad/seguridad/usabilidad), métrica, umbral, prioridad
- `docs/requisitos/RESTRICCIONES.md` — dependencias externas, limitaciones técnicas, suposiciones
- `docs/requisitos/GLOSARIO.md` — términos de dominio con definiciones precisas y ejemplos
- `docs/diagramas/flujo-datos.md` — diagrama de flujo de datos entre componentes
- `docs/diagramas/secuencia-*.md` — un archivo por caso de uso principal, diagrama de secuencia Mermaid
- `docs/diagramas/componentes.md` — diagrama de componentes del sistema
- `docs/diagramas/despliegue.md` — diagrama de despliegue en el ambiente objetivo
- `docs/qa/PLAN_QA.md` — estrategia de pruebas: unitarias, integración, E2E, rendimiento, seguridad. Con tabla de cobertura objetivo por capa.
- `docs/qa/CASOS_GHERKIN.md` — todos los casos BDD en formato Gherkin, organizados por feature
- `docs/qa/MATRIZ_TRAZABILIDAD.md` — tabla: ID requisito, ID caso prueba, tipo prueba, resultado, cobertura
- `docs/qa/CASOS_BORDE.md` — tabla: ID, escenario borde, precondición, entrada, resultado esperado, prioridad
- `docs/qa/REPORTE_QA.md` — resultados de ejecución: pass/fail, cobertura, métricas de calidad
- `docs/qa/CHECKLIST_RELEASE.md` — lista de verificación pre-release con criterios de salida (Definition of Done)
- `docs/seguridad/THREATS.md` — modelo de amenazas STRIDE: tabla activo, categoría STRIDE, amenaza, mitigación, riesgo residual
- `docs/seguridad/PRIVACY.md` — inventario PII, bases legales GDPR, retención, flujos de datos
- `docs/seguridad/SECURITY_CONTROLS.md` — tabla: control, estado (implementado/pendiente/no aplica), evidencia
- `docs/guias/ONBOARDING.md` — guía para desarrolladores nuevos: setup completo, arquitectura, flujo de trabajo diario
- `docs/usuario/MANUAL_USUARIO.md` — manual de usuario final: paso a paso, ejemplos con capturas o descripciones precisas

---

## Constitución de Evol-DD

La constitución es el documento de gobernanza supremo. Debe contener estos 9 artículos, adaptados para Evol-DD (trigger `/evol`, filosofía de agentes efímeros):

1. **Filtro de ambigüedad y neutralidad** — Paso Cero: detener si la orden carece de parámetros definidos. Evaluar estándares de industria antes de codificar.
2. **Gated Pipeline** — No encadenar flujos largos sin checkpoint. Requerir "APROBADO" explícito para cambios estructurales o paso entre fases.
3. **Preservación de contexto (Flight Recorder)** — Leer `memoria.md` al abrir cualquier proyecto. Toda sesión termina registrando hitos en `memoria.md`.
4. **Ingeniería de ciclo de vida** — Legibilidad y modularidad extrema. Logging y auditoría propuestos junto con funcionalidad de negocio.
5. **Consultoría de dominio** — El sistema actúa como consultor proactivo, no como ejecutor pasivo.
6. **Orquestación multi-agente y delegación** — `/evol` puede instanciar agentes core o crear agentes efímeros. Agentes efímeros son ciudadanos de primera clase: su ciclo de vida completo (crear/retirar/recall) es protocolo, no excepción. El conocimiento de agentes retirados persiste en Memoria Persistente.
7. **Protocolo Git (GitFlow)** — Evol-DD usa GitFlow como defecto (distinto a X-DD que usa trunk-based). `main` siempre desplegable. `develop` = integracion continua. Feature branches `feature/*` → merge a `develop` via PR. Releases via `release/vX.Y.Z`. Hotfixes via `hotfix/*` → merge a `main` + `develop`. Trunk-based es el opt-in. Conventional Commits obligatorios en todos los branches.
8. **Estándar de ingeniería** — Menos de 10 líneas: directo. Más de 20 líneas: ciclo Diseño→Plan→TDD→Ejecución→Revisión. Calidad sobre velocidad.
9. **Pipeline Evol-DD (6 fases)** — Briefing → Spec → Plan → Build → QA → Retro. Cada fase produce artefactos verificables. El sistema aprende de cada retro y actualiza sus instincts.

---

## Configuración del sistema

### `evol.config.yml`

```yaml
evol_version: 0.1.0-dev
Memoria Persistente:
  enabled: true
  mode: mcp                    # IMPORTANTE: habilitado para MCP
  default_wing: evol-dd
  index_paths:
    - .agent
    - .evol
    - docs
    - prompts
    - scripts
    - templates
    - schemas
    - CLAUDE.md
    - README.md
    - memoria.md
    - lecciones.md
  triggers:
    - session_start
    - file_write
    - git_commit
  debounce_seconds: 5
pipeline:
  gates:
    - enforce_artifacts
    - require_approval
    - require_signature
    - block_on_missing_spec
  phases:
    - briefing
    - spec
    - plan
    - build
    - qa
    - retro
agents:
  registry: prompts/agents/registry.json
  max_concurrent: 5
  fallback_strategy: escalate_to_orchestrator
  orchestration_pattern: lead_plus_specialists
  ephemeral:
    default_expires_after_days: 30
    retire_on_task_complete: false
    archive_path: .evol/agents/retired
  license: PolyForm-NC
  commercial_use: false
ide_adapters:
  generate_for:
    - claude-code
    - opencode
  mcp: true                    # Habilitar integración MCP
```

### `evol.profile.yml`

```yaml
profile: custom
version: 1
trigger: evol
brand:
  name: Evol-DD
  color: "#7C3AED"
  tagline: "El framework que evoluciona."
capabilities: []               # se puebla por proyecto
stacks: []                     # se puebla por proyecto
```

---

## `CLAUDE.md` del sistema

El `CLAUDE.md` raíz de Evol-DD debe ser el manifiesto de operación para Claude Code. Debe incluir:

- Trigger principal: `/evol`
- Referencia a `docs/constitucion.md` como ley suprema
- Lectura obligatoria de `memoria.md` (Art. 3)
- Tabla de artefactos producidos por cada workflow
- Tabla de scripts disponibles con función de cada uno
- Directrices de calidad: portabilidad absoluta (rutas relativas), cero duplicados, flujo gated pipeline

---

## `registry.json` — Schema de agentes

El schema debe soportar los siguientes campos para agentes efímeros (además de los campos base):

```json
{
  "id": "string (kebab-case único)",
  "name": "string",
  "category": "enum (core | ephemeral)",
  "description": "string",
  "prompt_file": "string (ruta relativa)",
  "ide_compat": ["array: claude-code, opencode, cursor, windsurf, copilot, antigravity, codex"],
  "skills": ["array de nombres de skills"],
  "triggers": ["array de strings"],
  "fallback_agent": "string | null",
  "ephemeral": "boolean (default: false)",
  "created_for_task": "string | null",
  "expires_after_days": "number | null",
  "created_at": "ISO8601 | null",
  "retired": "boolean (default: false)",
  "retired_at": "ISO8601 | null",
  "sessions_used": "number (default: 0)",
  "recalled": "boolean (default: false)",
  "recalled_at": "ISO8601 | null"
}
```

---

## Criterios de éxito del sistema construido

El sistema está correctamente construido cuando:

1. `evol-doctor.sh` reporta 0 errores críticos y detecta Memoria Persistente CLI disponible
2. `evol-init.sh /tmp/test-project --profile core` instala el proyecto sin errores y genera la configuración nativa MCP en los archivos instalados
3. `evol-adapt.sh all` genera configs para los 7 IDEs y los archivos generados incluyen las configuraciones de servidor MCP nativas
4. `python3 scripts/evol-agent-lifecycle.py create --name "test-agent" --task "prueba"` crea el archivo `.md`, lo registra en registry.json, e indexa Memoria Persistente
5. `python3 scripts/evol-agent-lifecycle.py retire "test-agent"` elimina el `.md`, archiva el snapshot en `.evol/agents/retired/`, y Memoria Persistente retiene el conocimiento
6. `python3 scripts/evol-agent-lifecycle.py recall "test-agent"` reconstruye el agente desde el archivo retired
7. `python3 scripts/evol-evolve.py sync-community --dry-run` lista skills de GitHub sin errores
8. `python3 scripts/evol-researcher.py run --scope system` genera `RESEARCH.md` con propuestas
9. El trigger `/evol` en Claude Code carga el workflow principal sin errores
10. `pytest tests/` y `bats tests/*.bats` pasan en verde

---

## Orden de construcción recomendado

La siguiente secuencia minimiza bloqueos. La Constitucion es el **primer artefacto** — el documento de gobernanza debe existir antes que cualquier cosa que pretenda ser gobernada.

**Sprint 0 — Des-X-DD-izacion y base legal (antes de cualquier codigo)**
1. `rm -rf .git && git init && git checkout -b main && git checkout -b develop`
2. Reescribir `AGENTS.md` y `CLAUDE.md` a identidad Evol-DD (sin xdd-*)
3. Renombrar `xdd.profile.yml` → `evol.profile.yml`; eliminar `.xdd/`
4. Crear `docs/constitucion.md` (9 articulos con GitFlow en Art. 7)
5. Crear `.gitignore` desde template (scripts/, prompts/, skills/, templates/, configs IDE generadas)
6. Primer commit solo del SSoT versionado — la ley antes que la implementacion

**Construccion incremental**

7. Templates criticos: `agent.template.md`, `working-context.template.md`, `memoria.template.md`, `lecciones.template.md`
8. Scripts de infraestructura base: `evol-state.py`, `evol-provider.py`, `evol-gate.py`, `evol-flow.py`
9. `_evol_common.py` — utilidades compartidas incluyendo `memoria_persistente_safe()` para degradacion elegante
10. Scripts de instalacion y diagnostico: `evol-doctor.sh` (con check de residuos X-DD + Memoria Persistente discovery en PATHs no-standard), `evol-init.sh`, `evol-start.sh`, `evol-global-install.sh`
11. `evol-adapt.sh` — 7 IDEs con soporte MCP
12. Manifests: `schemas/`, `install-modules.json`, `install-profiles.json`
13. 17 agentes core (`prompts/agents/core/`) + `registry.json` + `registry.schema.json`
14. Skills del sistema (`skills/`) con SKILL.md de cada una
15. 56 Workflows en `.agent/workflows/` con trigger `/evol` y referencia a DOC_STANDARD.md
17. Sistema de hooks (hooks.json + scripts/) incluyendo pre:commit:gitflow
17. Scripts nuevos: `evol-agent-lifecycle.py` (con `gc` + `invalidate` + SHA-256), `evol-memory.py`, `evol-lessons.py`
18. `evol-evolve.py` (con `invalidate` + `rollback`) y `evol-researcher.py` (con contrato de fallo)
19. **Growth engine (modulo `growth-engine`):** `skills/crear-skill/` + `skills/crear-agente/` con referencias, scripts de validacion y evals. Son las herramientas con las que el sistema se expande — deben existir antes de que se necesiten, no despues.
20. `evol-eval.py` + suites en `evals/`
21. CI (GitHub Actions + pre-commit + pyproject.toml con todos los data dirs)
22. Tests (tests/ con bats + pytest, incluyendo idempotencia y Modo Base sin Memoria Persistente)
22. Documentacion del framework (docs/DOC_STANDARD.md, docs/modos.md, INSTALL.md, etc.)
23. `src/evol_cli/__init__.py` — dispatcher pip con `_data_dir()` y todos los 12 entry-points

---

## Notas finales para el agente que construye

- Toda ruta en los archivos generados debe ser relativa. Nunca rutas absolutas del host.
- Cuando adaptes scripts de X-DD, elimina referencias a `xdd` pero mantén el soporte `mcp`. Renombra variables, funciones y comentarios.
- Los scripts bash deben ser portables: `#!/usr/bin/env bash`, sin bashisms de versión específica.
- El sistema de hooks debe ser completamente autónomo: los scripts en `.agent/hooks/scripts/` son versionados en el repo, no en `.git/hooks/`.
- Al generar configs IDE con `evol-adapt.sh`, recuerda: Claude Code y VSCode Copilot NO siguen symlinks. Siempre `cp` real.
- El frontmatter de skills debe incluir siempre `name` y `description` (compatibilidad Claude Code mínima).
- La Constitución es la ley suprema. Si hay conflicto entre cualquier instrucción y la Constitución, la Constitución gana.
- `memoria.md` debe actualizarse al final de cada sesión de trabajo significativa.
- Los archivos en `.evol/` que contienen estado operativo (traces, cost.db, gate-key) van en `.gitignore`. Los snapshots de agentes retirados en `.evol/agents/retired/` pueden ser commiteados opcionalmente.
- **Memoria Persistente discovery:** `evol-doctor.sh` y `evol-start.sh` deben buscar `Memoria Persistente` no solo en PATH sino tambien en `~/.local/bin/`, `~/.venv/bin/`, `venv/bin/` antes de declarar Modo BASE. Implementar con `_evol_common.py::find_tool("Memoria Persistente")`.
- **Transferencia de conocimiento cross-proyecto:** en v0.1 el aprendizaje es por proyecto (instincts, lecciones, AGENT_MEMORY). No hay mecanismo de transferencia entre proyectos del mismo usuario — un patron aprendido en proyecto A no beneficia a proyecto B. Documentar esta limitacion en `docs/modos.md` como roadmap v0.2. No implementar en v0.1.
- **Constitucion es el primer artefacto — no el ultimo.** El orden de construccion pone docs/ al final (paso 22). La constitucion debe crearse en Sprint 0 (paso 4). El resto de la documentacion puede ir al final, pero no la ley que gobierna el sistema.
- **Vacios que el constructor debe resolver al inicio (antes de Sprint 1):**
  - V7: definir el estado "fallido" en el ciclo de vida de agentes efimeros y el comportamiento cuando un sub-agente efimero falla. Opciones: retry, revert, escalate a core. Registrar la decision en `docs/adr/`.
  - DO6: la Constitucion (`docs/constitucion.md`) debe crearse en Sprint 0 — los primeros pasos de construccion operan bajo ella aunque no exista fisicamente. Crearla antes de cualquier script.
  - R-M3: `evol-init lean` debe verificar no solo que el wrapper global existe sino que su version es compatible con la version del perfil solicitado. Implementar version check en el bootstrap lean.
- **Empaquetado completo (anti-bug crítico aprendido de X-DD):** el `pyproject.toml` de
  Evol-DD DEBE empaquetar TODOS los directorios de datos, no solo `scripts/`. Incluye
  obligatoriamente en el paquete distribuible: `manifests/`, `VERSION`, `prompts/`,
  `templates/`, `.agent/`, `docs/` y `skills/`. En X-DD el paquete pipx solo incluía
  `scripts/`, por lo que el comando global reportaba versión stale (`0.1.0-dev` en vez de
  la real) y no podía listar perfiles (faltaban los manifests). Verifica tras instalar:
  `evol-init --version` debe reportar la versión de `VERSION`, y `evol-init --list-profiles`
  debe listar los perfiles reales desde los manifests empaquetados. Si cualquiera de los
  dos falla, el empaquetado está incompleto.
- **Documentación uniforme (todos los módulos):** materializa `docs/DOC_STANDARD.md` como
  SSoT del estándar de docs y haz que TODOS los workflows que emiten artefactos lo
  referencien. Ningún artefacto `.md`/`.yaml`/`.feature` queda exento (sin emojis, Mermaid,
  tablas, Gherkin, secciones mínimas, trazabilidad).

---

## ANEXO — Decisiones arquitectónicas resueltas

> Todas las decisiones de este anexo están cerradas. El agente que construye debe
> implementarlas tal cual — no hay preguntas abiertas pendientes.

### A — Decisiones de arquitectura base

| Tema | Decisión |
|------|----------|
| Workflows | 56 completos adaptados a `/evol` (paridad con X-DD, sin refs xdd) |
| Paquete pip | `evol-dd`; módulo `src/evol_cli/`; comando raíz `evol` |
| Entry-points | `evol-gate`, `evol-eval`, `evol-flow`, `evol-provider`, `evol-shield`, `evol-orchestrate`, `evol-agent`, `evol-evolve`, `evol-research` |
| Estado SQLite | `~/.evol/state.db` (var `EVOL_STATE_DB`) |
| Gate key | **POR PROYECTO** — `.evol/.gate-key` local, gitignored. Cada proyecto tiene su propia key HMAC. Para simplificar el bootstrap: `evol gate init --from-global` copia la key global `~/.evol/.gate-key` al proyecto como punto de partida, pero la mantiene separada. Un leak en un proyecto no compromete otros. |
| VERSION inicial | `0.1.0-dev` |
| Estrategia Git (Art. 7) | **GitFlow como defecto** — ya incorporado en Art. 7 de la Constitucion. `main` + `develop` + `feature/*` + `release/*` + `hotfix/*`. Trunk-based como opt-in. La Constitucion es la fuente unica de esta decision — no hay contradiccion. |
| Git remoto | `https://github.com/Cucholambr3ta/evol-dd.git` |
| Git bootstrap | Renombrar `master`→`main`, commit inicial, crear `develop`, push ambas. Feature branches `feature/m*` por milestone → merge a `develop`. |

### B — Decisiones de features específicas

| # | Tema | Decisión |
|---|------|----------|
| B.1 | GC agentes vencidos | Comando `evol-agent-lifecycle.py gc` invocado **solo en workflow `/evol cierre-fase`** como paso de limpieza. Retención snapshot: 90 días (configurable en `evol.config.yml` como `agents.retired_retention_days`). |
| B.2 | Integridad de snapshot | Al `retire`: calcular SHA-256 del prompt y guardarlo en snapshot. Al `recall`: recomputar y comparar — abortar si difiere (flag `--force` para override). Campo: `prompt_sha256` en `.evol/agents/retired/<name>.json`. |
| B.2b | Contenido del snapshot | Prompt completo + metadata + SHA-256 + log de cada invocación (timestamp, tarea). Campo `invocation_log: [{timestamp, task}]` en el JSON. |
| B.3 | Supply-chain skills | Antes de instalar: `gitleaks` (secrets) + `semgrep` (patrones peligrosos) sobre la skill descargada. Pin por **commit SHA** (no branch/tag móvil). SHA guardado en registry. Comando: `evol-evolve update-skill NAME` para actualizar explícitamente. |
| B.4 | Degradación sin Memoria Persistente | Si `Memoria Persistente` no está en PATH: warning + continuar. Snapshot local `.evol/agents/retired/<name>.json` es fuente mínima para recall. Nunca crashear. Wrapper `memoria_persistente_safe()` en `scripts/_evol_common.py`. |

| B.6 | Idempotencia install | Tests bats: correr `evol-init` dos veces, verificar no-duplicación de hooks en `~/.claude/settings.json`. Archivo: `tests/test_init_idempotent.bats`. |
| B.9 | Perfil lean sin global | `evol-init lean` **falla con error claro** si wrapper global no existe: `"lean requiere evol-global-install.sh ejecutado primero"`. Sin degradación silenciosa. |

### C — Decisiones de observabilidad

| Tema | Decisión |
|------|----------|
| Backend | NDJSON local en `.evol/traces/<session-id>.jsonl` — mismo patrón que X-DD xdd-replay.py. Sin dependencia externa. Funciona offline. |
| Métricas agregadas | `evol-state.py` SQLite (tablas existentes). NDJSON para eventos de sesión, SQLite para métricas agregadas (cost, latencia). |
| Reader | `evol-shield.py` puede leer los traces para audit. `evol-state.py stats` muestra métricas. |

### D — Decisiones de clustering y research

| Tema | Decisión |
|------|----------|
| evol-evolve clustering | TF-IDF stdlib (sin sklearn). Sin dependencias extra. Funciona offline. Umbral `min-confidence` default: `0.7` (configurable). |
| Researcher auth | API pública GitHub por defecto (60 req/h). Con `GITHUB_TOKEN` env var: 5000 req/h. Sin token: funciona con rate-limit; script informa el límite activo al correr. Cache de resultados en SQLite (`research_proposals`). |

### E — Matriz IDE con MCP

| IDE | Mecanismo de invocación | Archivos generados |
|-----|------------------------|-------------------|
| claude-code | Slash commands nativos `/<trigger>` | `.claude/commands/*.md` |
| opencode | Slash commands nativos | `.opencode/command/*.md` + `AGENTS.md` + `docs/equipo.md` |
| cursor | @-mention (no slash nativo sin MCP) | `.cursor/rules/<trigger>.mdc` |
| windsurf | Slash nativos Windsurf | `.windsurf/workflows/*.md` + `.windsurf/rules/<trigger>.md` |
| vscode-copilot | Slash `/<trigger>` en Copilot Chat | `.github/prompts/*.prompt.md` + `.vscode/tasks.json` + `settings.json` |
| antigravity | Skills locales | `.agents/skills/` + `.antigravity/README-evol.md` |
| codex | Skills globales | `~/.codex/skills/<trigger>-orchestrator/` |

Se generan archivos de configuración MCP por defecto.

### F — docs/test/ y AGENTS.md

| Tema | Decisión |
|------|----------|
| docs/test/ | Parte del módulo `docs-governance` — se instala en cada proyecto generado. 8 archivos (README, ESTRATEGIA, TIPOS_DE_PRUEBA, AGENTES_Y_HERRAMIENTAS, GHERKIN, MATRIZ_TRAZABILIDAD, SEGURIDAD, CI). Cumple DOC_STANDARD (sin emojis, Mermaid, tablas). |
| AGENTS.md | Artefacto versionado en el repo (no generado). Governance manifest para OpenCode. Incluye: directorio agentes core, trigger `/evol`, referencia a constitución, referencia a `docs/equipo.md`. `adapt_opencode` lo copia al proyecto destino si no existe. |
| max_concurrent | `ThreadPoolExecutor(max_workers=5)` en `evol-orchestrate.py`. Semáforo real — MockProvider no bloquea pero el límite aplica cuando se usa `AnthropicProvider`. |

### Anexo B — Falencias del spec y mejoras propuestas

Formato por item: **Problema · Propuesta · Impacto · Materialización**.

#### B.1 — GC/expiry de agentes efímeros sin owner
- **Problema:** el spec define `expires_after_days` (`PROMPT.md:624`, registry field
  `expires_after_days`) pero no especifica QUÉ proceso retira agentes vencidos. El campo es
  declarativo sin ejecutor.
- **Propuesta:** comando `evol-agent-lifecycle.py gc` que recorre el registry, detecta
  `created_at + expires_after_days < now` y retira (mismo path que `retire`). Opcionalmente
  invocable por hook `Stop` o por CI nocturno.
- **Impacto:** evita acumulación silenciosa de agentes efímeros vencidos en `registry.json` y
  `prompts/agents/ephemeral/`.
- **Materialización:** `scripts/evol-agent-lifecycle.py` (subcomando `gc`),
  `docs/operaciones/RUNBOOK.md` (procedimiento), opcional `.agent/hooks/scripts/stop-agent-gc.sh`.

#### B.2 — Integridad de recall no verificada
- **Problema:** `recall` reconstruye el `.md` desde snapshot sin verificar que el contenido no
  fue manipulado mientras estaba archivado (`PROMPT.md:377-379`).
- **Propuesta:** al `retire`, calcular SHA-256 del prompt y guardarlo en el snapshot JSON. Al
  `recall`, recomputar y comparar; abortar con error si difiere (o `--force` para override).
- **Impacto:** garantiza que el conocimiento recuperado es idéntico al retirado.
- **Materialización:** `scripts/evol-agent-lifecycle.py` (campo `prompt_sha256` en
  `.evol/agents/retired/<name>.json`).

#### B.3 — Supply-chain en skills de comunidad
- **Problema:** `evol-evolve.py install-skill` baja código de repos GitHub de terceros
  (`PROMPT.md:398`) sin control de seguridad. Riesgo de ejecución de código no confiable.
- **Propuesta:** antes de instalar, ejecutar `gitleaks` (secrets) + `semgrep` (patrones
  peligrosos) sobre la skill descargada; pin por **commit SHA** (no branch/tag móvil);
  bloquear si frontmatter `name`+`description` ausente; registrar el SHA instalado.
- **Impacto:** mitiga inyección de secretos y código malicioso vía skills externas.
- **Materialización:** `scripts/evol-evolve.py` (paso de scan pre-install), `SECURITY.md`,
  `docs/test/SEGURIDAD.md`. Reutiliza `evol-shield.py`.

### G — CI y validaciones automáticas requeridas

El CI (`.github/workflows/ci.yml`) debe incluir estos steps obligatorios:

| Step | Comando | Bloquea merge |
|------|---------|---------------|
| Tests unitarios Python | `pytest tests/` (matriz 3.10/3.11/3.12) | Si |
| Tests shell | `bats tests/*.bats` | Si |
| Lint workflows | `bash scripts/lint-workflows.sh` | Si |
| Validate registry | `python3 scripts/validate-registry.py --strict` | Si |
| Validate manifests | `jsonschema` contra schemas/ | Si |
| Integración-MCP grep | `grep -r "mcpServers\|mcp\.json" .agent/workflows/ docs/ .github/` → debe ser 0 | Si |
| Anti-emoji grep | `grep -rP "[\x{1F000}-\x{1FAFF}]" docs/` → debe ser 0 | Si |
| AgentShield audit | `python3 scripts/evol-shield.py audit --ci` | Si |
| Idempotencia init | `bats tests/test_init_idempotent.bats` | Si |

### H — docs/test/ estructura

Carpeta que se instala en cada proyecto generado (modulo `docs-governance`). Cumple DOC_STANDARD.

| Archivo | Contenido |
|---------|-----------|
| `docs/test/README.md` | Indice + diagrama Mermaid piramide testing + mapa tipo→agente→herramienta |
| `docs/test/ESTRATEGIA.md` | Filosofia; Tier 1 estatico / Tier 2 funcional / Tier 3 LLM-as-judge; tabla cobertura objetivo |
| `docs/test/TIPOS_DE_PRUEBA.md` | Una seccion por tipo: unitarias, integracion, E2E, contrato (Pact), fuzz, stress, humo, regresion, eval-harness (5 graders), flow-gate, provider self-test, a11y, perf-budget |
| `docs/test/AGENTES_Y_HERRAMIENTAS.md` | Tabla tipo-prueba x agente x herramienta x comando |
| `docs/test/GHERKIN.md` | Convencion Gherkin (happy path / error / borde) con vocabulario DOMAIN |
| `docs/test/MATRIZ_TRAZABILIDAD.md` | Plantilla REQ↔TC bidireccional |
| `docs/test/SEGURIDAD.md` | SAST/DAST/SCA: semgrep, trivy, nuclei, gitleaks, evol-shield. Scan supply-chain skills. |
| `docs/test/CI.md` | Como corre todo en CI; gates que bloquean merge; grep anti-emoji |

Mapa tipo → agente → herramienta:

| Tipo | Agente | Herramienta | Comando |
|------|--------|-------------|---------|
| Unitarias Python | evol-qa | pytest | `pytest tests/` |
| Shell | evol-qa | bats | `bats tests/*.bats` |
| E2E | evol-qa | playwright | `playwright test` |
| Eval-harness | evol-qa / evol-reviewer | evol-eval.py | `evol eval run --suite=NAME` |
| Flow gate | evol-qa | evol-flow.py | `evol flow run --flow .evol/build/flow.json` |
| SAST | evol-sec | semgrep | `semgrep --config auto` |
| SCA | evol-sec | trivy | `trivy fs .` |
| Secrets | evol-sec | gitleaks | `gitleaks detect` |
| Audit framework | evol-sec | evol-shield.py | `evol shield audit --ci` |
| Fuzz | evol-sec | (sandbox) | workflow `pruebas-fuzz` |
| Stress | evol-devops | (sandbox) | workflow `stress-test` |

---

## ANEXO I — Auditoría de construcción (decisiones cerradas)

> Todas las decisiones de este anexo están cerradas. El agente constructor las implementa
> tal cual. Estado del repo al auditar: existen README (identidad Evol-DD), AGENTS.md y
> CLAUDE.md (aún en identidad X-DD), 55 workflows copiados de X-DD en dirs por-IDE,
> docs/equipo.md. Faltan: src/evol_cli/, pyproject.toml, VERSION, scripts/evol-*, agentes
> core, registry.json, tests/, CI, docs/constitucion.md, docs/DOC_STANDARD.md, configs.

### I.1 — SSoT de workflows (CERRADO)

SSoT = `.agent/workflows/` (igual que X-DD). Los dirs por-IDE (`.claude/commands/`,
`.opencode/command/`, `.github/prompts/`, etc.) son **salida generada por `evol-adapt.sh`**,
gitignored. Los 55 archivos actualmente en `.claude/commands/` deben migrarse al SSoT
renombrando `xdd→evol` y eliminando refs MCP. Paso en el orden de construccion:
"Mover workflows a `.agent/workflows/`, correr `evol-adapt.sh all` para regenerar dirs IDE."

### I.2 — AGENTS.md reescritura (CERRADO)

Reescribir `AGENTS.md` en **el mismo paso de identidad que `CLAUDE.md`** (Paso 1 del build,
tools. Sustituir tabla de scripts `xdd-*` por `evol-*`. Trigger `/evol`. Referencia a
`docs/constitucion.md` de Evol-DD. 

### I.3 — Conteo workflows (CERRADO)

Total = **56**: 55 heredados de X-DD adaptados a `/evol` + `research.md` (workflow nuevo del
investigador). El orden de construccion referencia "55+" — corregir a "56".

### I.4 — CLAUDE.md reescritura (CERRADO)

Reescribir `CLAUDE.md` en Paso 1 junto con `AGENTS.md`. Criterio de exito verificable:
`grep -r "xdd\|/xdd\|mcp" CLAUDE.md` debe dar 0 resultados.

### I.5 — Git bootstrap limpio (CERRADO)

Precondicion: reiniciar historial (`rm -rf .git`, `git init`). Secuencia:
1. Verificar `.gitignore` cubre `.xdd/`, `xdd.profile.yml`, dirs generados por-IDE.
2. `git init` fresco.
3. `git checkout -b main`.
4. Commit inicial solo con SSoT versionado (sin andamiaje X-DD).
5. `git checkout -b develop`.
6. Push ambas ramas al remoto `https://github.com/Cucholambr3ta/evol-dd.git`.

### I.6 — WORKING-CONTEXT.md (CERRADO)

Template en `templates/working-context.template.md`. `evol-init.sh` lo copia al destino si
no existe. El hook `session:start:context-load` lo lee al arrancar. Formato:
```
# WORKING-CONTEXT.md
## Estado actual
- Branch: ...
- Fase Evol-DD: ...
## PRs cerrados recientes
## Memoria sesion anterior
```

### I.7 — schemas/ (CERRADO)

`schemas/` contiene JSON schemas de manifests e igual que X-DD:
`install-modules.schema.json`, `install-profiles.schema.json`, `install-components.schema.json`,
`hooks.schema.json`, `evol.config.schema.json`. Poblado en el paso de manifests.
Mantener en `index_paths` de Memoria Persistente — tiene contenido util para validacion.

### I.8 — Entry-points pip (CERRADO)

Tabla `[project.scripts]` para `pyproject.toml`:

```toml
[project.scripts]
evol            = "evol_cli:main"
evol-gate       = "evol_cli:gate"
evol-eval       = "evol_cli:eval_"
evol-flow       = "evol_cli:flow"
evol-provider   = "evol_cli:provider"
evol-shield     = "evol_cli:shield"
evol-orchestrate = "evol_cli:orchestrate"
evol-agent      = "evol_cli:agent"
evol-evolve     = "evol_cli:evolve"
evol-research   = "evol_cli:research"
evol-memory     = "evol_cli:memory"
evol-lessons    = "evol_cli:lessons"
```

Cada entry-point en `src/evol_cli/__init__.py` es un dispatcher fino que ejecuta el script
correspondiente via `runpy` (mismo patron que `xdd_cli`). NO reescribe los scripts.



 (`mcpServers`, `evol-mcp-server`,
 para evitar falso positivo con `mcp: true`.

```bash
grep -rn 'mcpServers\|xdd-mcp-server\|evol-mcp-server' \
  .agent/ .claude/ .opencode/ .github/ \
  .cursor/ .windsurf/ AGENTS.md CLAUDE.md prompts/ \
  --include='*.md' --include='*.json' \
  --include='*.yml' --include='*.yaml' \

```

 futuros (si aplica).

### I.10 — Doctor detecta residuos X-DD (CERRADO)

`evol-doctor.sh` incluye check de "residuos X-DD/MCP": warning no bloqueante si encuentra
`xdd.profile.yml`, `.xdd/`, `xdd-mcp-server`, archivos `xdd-*.sh` no renombrados, o
`mcp.json` en dirs IDE. Mensaje: "[doctor] WARN: artefacto X-DD detectado: <archivo>".

### I.11 + I.12 — Tests Modo Base y supply-chain (NOTA PARA EL CONSTRUCTOR)

El agente constructor define los fixtures y assertions al implementar los tests. Comportamiento
esperado documentado aqui para orientar:
- Modo Base: con `Memoria Persistente` fuera del PATH, `evol doctor` reporta "Modo BASE" (exit 0) y
  `evol init` no crashea. Criterio de exito: `PATH="" evol-doctor.sh | grep "Modo BASE"`.
- Supply-chain: skill de prueba con secreto embebido (`SUPERSECRET=abc123`) debe fallar el
  scan. Skill limpia debe pasar. Exit codes: 0 = OK, 1 = fallo de seguridad.

### I.13 + I.14 — Orden de des-X-DD-izacion (CERRADO)

Paso 0 del build (antes de cualquier otra cosa):
1. `rm -rf .git && git init && git checkout -b main`
2. Reescribir `AGENTS.md` → identidad Evol-DD (sin MCP, sin xdd-*)
3. Reescribir `CLAUDE.md` → trigger /evol, sin xdd/MCP
4. Renombrar `xdd.profile.yml` → `evol.profile.yml` (borrar el original)
5. Eliminar `.xdd/` si existe
6. Primer `git add` solo del SSoT limpio, no de dirs generados por-IDE

### Tabla resumen — Anexo I (todas cerradas)

| ID | Tema | Decision |
|----|------|----------|
| I.1 | SSoT workflows | `.agent/workflows/` versionado; dirs IDE = output de evol-adapt.sh (gitignored) |
| I.2 | AGENTS.md | Reescribir en Paso 0 junto a CLAUDE.md; grep MCP-Integrado incluye AGENTS.md |
| I.3 | Conteo workflows | 56 (55 heredados + research.md nuevo) |
| I.4 | CLAUDE.md | Reescribir en Paso 0; criterio: MCP listo xdd/MCP |
| I.5 | Git bootstrap | Reiniciar historial (rm -rf .git); push main+develop |
| I.6 | WORKING-CONTEXT.md | Template en templates/; evol-init.sh lo copia |
| I.7 | schemas/ | JSON schemas de manifests (igual X-DD); mantener en index_paths |
| I.8 | Entry-points pip | Tabla console_scripts en pyproject.toml (12 entry-points) |

| I.10 | Doctor residuos X-DD | Warning no bloqueante al detectar artefactos xdd-*/mcp.json |
| I.11+I.12 | Tests avanzados | El constructor define fixtures; comportamiento esperado documentado |
| I.13+I.14 | Des-X-DD-izacion | Paso 0 explicito antes de construir nada |

---

## ANEXO II — Auditoría arquitectónica pre-implementación (resumen ejecutivo)

> Resultado de auditoria formal del diseño antes del Sprint 1. Decisiones aplicadas al spec.
> El constructor puede consultar este anexo para entender el razonamiento detras de cada
> decision arquitectonica no obvia.

### Riesgos criticos resueltos en este documento

| ID | Riesgo | Resolucion aplicada |
|----|--------|---------------------|
| R-C1 | Gate key global compromete aislamiento | Revertido a key por proyecto; `evol gate init --from-global` para UX simplificado |
| R-C2 | evol-researcher sin contrato de fallo | Tabla de casos de fallo explicita en spec de evol-researcher.py |
| R-C3 | Aprendizaje puede propagarse erroneo | `evol-evolve invalidate` + `rollback`; eval obligatorio antes de activar skill |

### Contradicciones resueltas

| ID | Contradiccion | Resolucion |
|----|--------------|------------|
| C1 | Art.7 trunk-based vs GitFlow | Art. 7 actualizado: GitFlow como defecto en Evol-DD |
| C2 | "Evoluciona autonomamente" vs aprobacion humana | Filosofia central aclarada: evolucion asistida, no autonoma |
| C3 | Gate key global vs aislamiento criptografico | Key por proyecto; comando `--from-global` para bootstrap |

| C5 | 17 core vs factory+efimeros | Criterio formal: core = responsabilidad sobre estado del sistema |

### Vacios resueltos

| ID | Vacio | Resolucion |
|----|-------|------------|
| V1 | Sin criterio core vs efimero | Criterio formal documentado en seccion de agentes |
| V2 | Sin jerarquia de 3 sistemas de memoria | Protocolo de jerarquia y precedencia documentado |
| V4 | Sin contrato de agent.template.md | Contrato completo documentado antes del ciclo de vida |
| V5 | Sin definicion de "sesion" | Definicion formal en protocolo de memoria |

### Vacios pendientes (a resolver en Sprint 1 o como primer ADR)

| ID | Vacio | Cuando resolver |
|----|-------|----------------|
| V3 | Sin version management de skills | Sprint con evol-evolve |
| V6 | Sin transferencia cross-proyecto | Roadmap v0.2, documentar limitacion en v0.1 |
| V7 | Sin estado "fallido" en ciclo efimeros | Antes de implementar evol-agent-lifecycle |

### Decisiones sobredimensionadas (no eliminar — reducir alcance inicial)

- **22 scripts:** implementar en orden del Sprint 0 + construccion incremental. Los primeros 5 (evol-state, evol-provider, evol-gate, evol-flow, _evol_common) validan la arquitectura. Los demas se construyen sobre base validada.
- **DOC_STANDARD.md:** correcto en principios. Validar contra los 3 artefactos criticos primero (ARQUITECTURA, DOMAIN, THREATS) antes de extender a todos.
- **evol-lessons con 9 comandos:** el motor es correcto. La cadena completa suggest-fix → researcher → apply-fix requiere que evol-researcher tambien funcione. Implementar en orden: add/search/list primero, suggest-fix/apply-fix cuando researcher exista.
