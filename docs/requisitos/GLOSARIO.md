# Glosario — Evol-DD

## Resumen

Este documento define el vocabulario unificado (Ubiquitous Language) del dominio de Evol-DD. Todos los artefactos deben usar estos terminos consistentemente.

---

## Terminos Core

### Agent (Agente)

**Definicion:** Unidad de procesamiento autonomous con responsabilidad especifica. Puede ser core (permanente) o ephemeral (temporal).

**Contexto:** Todos los agentes viven en `prompts/agents/`. Los core en `core/`, los efimeros en `ephemeral/`.

**Sinonimos:** - (no usar sinonimos)

**Antónimos:** - (no usar antónimos)

**Ejemplo:** "evol-builder es un agent que implementa codigo siguiendo TDD."

---

### Agent Core

**Definicion:** Agente permanente con responsabilidad sobre el estado del sistema (gobernanza, arquitectura, seguridad, orquestacion).

**Contexto:** Los 18 agentes core nunca se retiran. Son el nucleo inmutable.

**Criterio:** Un agente es core si tiene responsabilidad sobre estado del sistema — independientemente del dominio del proyecto.

**Ejemplo:** "evol-orchestrator es un agent core porque orquesta a otros agentes."

---

### Agent Ephemeral

**Definicion:** Agente dinamico creado para tarea especializada. Existe mientras se necesita, se retira cuando termina, y su conocimiento queda indexado.

**Ciclo:** CREATE → INVOKE → RETIRE → [RECALL]

**Ejemplo:** "marketing-seo-specialist es un agent ephemeral porque su responsabilidad es exclusivamente sobre el dominio del proyecto activo."

---

### Agent Lifecycle (Ciclo de vida de agente)

**Definicion:** CREAR → INVOCAR → RETIRAR → [RECUPERAR]

**CREATE:** Genera .md desde template, registra en registry.json, indexa Memoria Persistente.

**INVOKE:** Marca sesion, incrementa sessions_used.

**RETIRE:** Elimina .md, archiva snapshot JSON con SHA-256, Memoria Persistente retiene.

**RECALL:** Reconstruye .md desde snapshot, re-registra, re-indexa.

---

### Agent Factory

**Definicion:** Agente core responsable de crear agentes efimeros. No se solapa con orquestador (factory = creacion, orchestrator = coordinacion).

**Script:** `evol-agent-lifecycle.py`

**Trigger:** `/evol agent create <name> --task <description>`

---

### Agente Orquestador

**Definicion:** Agente core que coordina la composicion de agentes y delega tareas.

**Criterio de delegacion:**

| Dominio | Agente |
|---------|--------|
| Estrategia/Priorizacion | evol-pm |
| Arquitectura | evol-architect |
| Logica de dominio | evol-domain |
| Feature/UI | evol-builder |
| Calidad | evol-qa |
| Seguridad | evol-sec |
| DevOps | evol-devops |

**Patterns:** sequential, parallel, parallel_then_sync, party

---

### Artifact (Artefacto)

**Definicion:** Archivo generado por el sistema o proceso de desarrollo.

**Ejemplos:** memoria.md, lecciones.md, SPEC.md, CASOS_GHERKIN.md, ARQUITECTURA.md

**Categoria:** Versionable (git) o Runtime (gitignored)

---

### Boot (Bootstrap)

**Definicion:** Proceso de inicializacion de un nuevo proyecto con Evol-DD.

**Script:** `evol-init.sh`

**Perfiles:** minimal, core, developer, security, research, full, lean

---

### Branch (Rama)

**Definicion:** Linea de desarrollo en Git.

**Convenciones GitFlow:**

| Branch | Uso |
|--------|-----|
| main | Produccion, siempre desplegable |
| develop | Integracion continua |
| feature/* | Nueva funcionalidad |
| fix/* | Correccion de bug |
| hotfix/* | Fix urgente en produccion |
| release/* | Preparacion de release |
| chore/* | Tareas sin impacto producto |
| docs/* | Documentacion |
| refactor/* | Refactoring |

---

### Cache (Caché)

**Definicion:** Almacenamiento temporal para mejorar rendimiento.

**TTL:** 3 dias por defecto para tool_result/.

**Ubicacion:** tool_result/, dialog/

**Gitignored:** Si

---

### Commit

**Definicion:** Unidad de cambio en Git.

**Formato:** Conventional Commits

```
<tipo>(<alcance>): <descripcion>

<tipo>: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert
<alcance>: opcional, modulo afectado
<descripcion>: max 50 caracteres, imperativo
```

---

### Configuration (Configuracion)

**Archivos:**

- `evol.config.yml` — Configuracion del sistema
- `evol.profile.yml` — Perfil del proyecto
- `AGENTS.md` — Governance manifest
- `CLAUDE.md` — Operation manifest

---

### Context (Contexto)

**Definicion:** Informacion disponible para el agente en el momento de ejecucion.

**Jerarquia de precedencia:**

1. memoria.md (verdad del proyecto)
2. AGENT_MEMORY.md + memory/ (sesion)
3. Memoria Persistente (busqueda semantica)

---

### Delegate (Delegar)

**Definicion:** Accion del orquestador de asignar tarea a agente especializado.

**Protocolo:** El orquestador nunca escribe codigo directamente. Siempre delega.

---

### DOC_STANDARD

**Definicion:** Estandar de documentacion de Evol-DD. SSoT en `docs/DOC_STANDARD.md`.

**Reglas:**

1. Cero emojis
2. Mermaid obligatorio
3. Tablas para datos estructurados
4. Gherkin completo
5. Profundidad substantiva
6. Trazabilidad bidireccional

---

### Domain (Dominio)

**Definicion:** Area de conocimiento o responsabilidad.

**Bounded Contexts en Evol-DD:**

- BC-1: Framework Core (agentes, memoria, pipeline)
- BC-2: Project Bootstrap (instalacion, perfiles)
- BC-3: Quality Assurance (testing, evaluacion)
- BC-4: Memory & Learning (memorias, lecciones)

---

### Ephemeral

Ver "Agent Ephemeral"

---

### Evolution (Evolucion)

**Definicion:** Proceso de auto-generacion de skills desde instinct patterns.

**Script:** `evol-evolve.py`

**Comandos:** run, approve, invalidate, rollback

---

### Feature

**Definicion:** Unidad de funcionalidad con criterios de aceptacion.

**Estructura Gherkin:**

- Happy path (1 obligatorio)
- Error case (>=1 obligatorio)
- Edge case with Examples (>=1 obligatorio)
- Max 8 escenarios por feature

---

### Flight Recorder

**Definicion:** Protocolo de memoria que graba hitos de sesion.

**Archivos:** memoria.md, lessons.md

**Trigger:** `/evol cierre` al final de sesion

---

### Gate (Puerta)

**Definicion:** Checkpoint HMAC-SHA256 para cambios estructurales.

**Ubicacion:** `.evol/.gate-key`

**Log:** `.evol/.gate-log.jsonl`

**Comandos:** init, approve, validate, transition, status

---

### GitFlow

**Definicion:** Estrategia de branching con main + develop + feature/*.

**Obligatorio por Constitucion Art. 7.**

---

### Gherkin

**Definicion:** Lenguaje de especificacion en formato Given/When/Then.

**Usage:** Casos de prueba en `docs/qa/CASOS_GHERKIN.md`

**Vocabulary:** Solo terminos de DOMAIN.md

---

### Hook

**Definicion:** Script que se ejecuta en respuesta a un evento.

**Eventos:**

- PreToolUse: Antes de usar herramienta
- PostToolUse: Despues de usar herramienta
- SessionStart: Al iniciar sesion
- Stop: Al cerrar sesion

**Perfiles:** minimal, standard, strict

---

### Instinct

**Definicion:** Patron detectado con confianza > threshold.

**Almacenamiento:** SQLite evol-state.db (tabla instincts)

**Uso:** Base para auto-evolucion de skills.

---

### Mode (Modo)

**Definicion:** Configuracion de operacion segun disponibilidad de componentes.

| Modo | Memoria Persistente | Features |
|------|-----------|----------|
| COMPLETO | CLI activo | Todas |
| BASE | No disponible | Core, sin RAG |

---

### Pipeline

**Definicion:** Flujo de 6 fases con gates de aprobacion.

**Fases:**

1. Briefing
2. Spec
3. Plan
4. Build
5. QA
6. Retro

---

### Profile (Perfil)

**Definicion:** Configuracion predefinida de modulos para instalacion.

**Perfiles:** minimal, core, developer, security, research, full, lean

---

### Registry

**Definicion:** Registro unificado de agentes en `prompts/agents/registry.json`.

**Schema:** `prompts/agents/registry.schema.json`

---

### Research (Investigacion)

**Definicion:** Proceso de buscar y proponer mejoras automaticamente.

**Script:** `evol-researcher.py`

**Fuentes:** GitHub (skills, frameworks), changelogs, papers

---

### Recall

**Definicion:** Recuperacion de agente retired desde snapshot.

**Tipos:**

- COMPLETO: JSON + contexto semantico (Memoria Persistente activo)
- BASICO: Solo JSON (Memoria Persistente no activo)

---

### Skill

**Definicion:** Capacidad especializada activable por trigger.

**Ubicacion:** `skills/<nombre>/SKILL.md`

**Categorias:** context-engineering, compression, quality-gate, security, lifecycle

---

### Snapshot

**Definicion:** Archivo JSON archivado de agente retired.

**Ubicacion:** `.evol/agents/retired/<name>.json`

**Contenido:** prompt, prompt_sha256, invocation_log, sessions_used

---

### Trigger

**Definicion:** Palabra clave para activar workflow o agente.

**Formatos:** `/evol <comando>`, slash commands IDE

---

### Ubiquitous Language

**Definicion:** Vocabulario unificado del dominio. Todos los documentos usan los mismos terminos.

**Referencia:** Este glosario

**Regla:** Cero sinonimos en Gherkin y documentacion

---

## Acronimos

| Acronimo | Significado |
|----------|-------------|
| ADR | Architectural Decision Record |
| CI | Continuous Integration |
| DDD | Domain-Driven Design |
| DoD | Definition of Done |
| E2E | End-to-End |
| NFR | Non-Functional Requirement |
| REQ | Requirement |
| SAST | Static Application Security Testing |
| SCA | Software Composition Analysis |
| SecDD | Security-Driven Development |
| SSoT | Single Source of Truth |
| TDD | Test-Driven Development |

---

## Terminos Deprecados

| Termino | Reemplazar por | Razon |
|---------|---------------|-------|
| xdd-* | evol-* | Diferenciacion de X-DD |
| MCP | MCP Nativo | MCP First-Class |
| agent | core o ephemeral | Claridad |

---

## Extension del Glosario

Para agregar nuevos terminos:

1. Definir termino y definicion
2. Verificar que no exista sinonimo
3. Agregar a este documento
4. Asegurar uso consistente en todos los artefactos