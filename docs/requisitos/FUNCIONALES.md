# Requisitos Funcionales — Evol-DD

## Resumen

Este documento especifica los requisitos funcionales del framework Evol-DD organizados por feature.

## Convenciones

| Campo | Formato |
|-------|---------|
| ID | REQ-NNN (tres digitos) |
| Prioridad | ALTA / MEDIA / BAJA |
| Status | PENDIENTE / EN PROGRESO / IMPLEMENTADO / VALIDADO |
| Trazabilidad | REQ-NNN ↔ TC-NNN via MATRIZ_TRAZABILIDAD.md |

---

## REQ-001: Bootstrap de Proyecto

**Feature:** FEAT-001
**Prioridad:** ALTA
**Responsable:** evol-devops

### Descripcion

El sistema debe permitir bootstrap de nuevos proyectos con perfil configurable.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-001-01 | `evol-init.sh <path> --profile=core` crea directorio .git/ | Funcional | Test CP-001 |
| CA-001-02 | Archivo memoria.md creado desde template | Funcional | Test CP-001 |
| CA-001-03 | Archivo .gitignore generado con 3 categorias | Funcional | Review |
| CA-001-04 | Archivo evol.profile.yml creado con profile especificado | Funcional | Test CP-001 |
| CA-001-05 | Idempotencia: re-ejecutar no causa errores ni modifica archivos previos | Funcional | Test CP-001 |
| CA-001-06 | `evol-init.sh --list-profiles` lista todos los perfiles disponibles | Funcional | Test CP-001 |
| CA-001-07 | Perfil inexistente muestra error claro | Funcional | Test CP-001 |

### Dependencias

- REQ-015 (templates)
- REQ-016 (profiles)

---

## REQ-002: Ciclo de Vida de Agentes Efimeros

**Feature:** FEAT-002
**Prioridad:** ALTA
**Responsable:** evol-agent-factory

### Descripcion

El sistema debe permitir crear, invocar, retirar y recuperar agentes efimeros.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-002-01 | `create --name X --task Y --expires-after Z` genera archivo .md desde template | Funcional | Test CP-002 |
| CA-002-02 | Registry actualizado con entrada ephemeral=true | Funcional | Test CP-002 |
| CA-002-03 | Memoria Persistente indexado tras create (si disponible) | Funcional | Test CP-002 |
| CA-002-04 | `invoke X` incrementa sessions_used en 1 | Funcional | Test CP-002 |
| CA-002-05 | `retire X` elimina .md y archiva snapshot JSON | Funcional | Test CP-002 |
| CA-002-06 | Snapshot incluye prompt_sha256 calculado | Funcional | Review code |
| CA-002-07 | Snapshot incluye invocation_log con timestamps | Funcional | Review snapshot |
| CA-002-08 | `recall X` reconstruye .md desde snapshot | Funcional | Test CP-002 |
| CA-002-09 | Recall verifica SHA-256; falla si mismatch (excepto --force) | Funcional | Test CP-002 |
| CA-002-10 | Recall completo indica JSON + semantic; basico indica solo JSON | Funcional | Test CP-002 |
| CA-002-11 | `gc` retira agentes vencidos automaticamente | Funcional | Test CP-002 |
| CA-002-12 | `list --all/--ephemeral/--retired` filtra correctamente | Funcional | Test CP-002 |

### Edge Cases

| Escenario | Comportamiento esperado |
|-----------|------------------------|
| Duplicar nombre | Error claro, archivo no modificado |
| Agent no existe para invoke | Mensaje "Agent not found", exit 1 |
| Snapshot corrupto | Error con SHA esperado vs calculado, hint --force |
| Recall sin snapshot | Error "Snapshot not found" |

### Dependencias

- REQ-015 (templates)
- REQ-003 (registry)
- REQ-012 (Memoria Persistente integration)

---

## REQ-003: Registro de Agentes (Registry)

**Feature:** FEAT-002
**Prioridad:** ALTA
**Responsable:** evol-agent-factory

### Descripcion

El sistema debe mantener un registro unificado de todos los agentes.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-003-01 | registry.json existe en prompts/agents/ | Funcional | Test |
| CA-003-02 | Schema registry.schema.json valida entrada | Funcional | validate-registry.py |
| CA-003-03 | 18 agentes core registrados con category=core | Funcional | Test |
| CA-003-04 | Agentes efimeros registrados con ephemeral=true | Funcional | Test CP-002 |
| CA-003-05 | No IDs duplicados | Funcional | validate-registry.py --strict |
| CA-003-06 | Todos los campos requeridos presentes | Funcional | JSON Schema validation |

---

## REQ-004: Gate Keeper HMAC-SHA256

**Feature:** FEAT-003
**Prioridad:** ALTA
**Responsable:** evol-sec

### Descripcion

El sistema debe implementar gates HMAC-SHA256 para cambios estructurales.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-004-01 | `gate init` crea .evol/.gate-key con clave 32 bytes | Funcional | Test CP-003 |
| CA-004-02 | Archivo .gate-key con permisos 0600 | Funcional | Review |
| CA-004-03 | Archivo .evol/ en .gitignore | Funcional | Review .gitignore |
| CA-004-04 | `gate approve --phase X` calcula signature HMAC-SHA256 | Funcional | Test CP-003 |
| CA-004-05 | Log en .evol/.gate-log.jsonl con timestamp, phase, approver, signature | Funcional | Review log |
| CA-004-06 | `gate validate` retorna "Gate active" si existe | Funcional | Test CP-003 |
| CA-004-07 | `gate validate` falla si gate no existe | Funcional | Test CP-003 |
| CA-004-08 | `gate transition --from X --to Y` registra transicion | Funcional | Test CP-003 |
| CA-004-09 | `gate status` muestra historial de aprobaciones | Funcional | Test CP-003 |

### Dependencias

- Ninguna (base del sistema)

---

## REQ-005: Pipeline de 6 Fases

**Feature:** FEAT-004
**Prioridad:** ALTA
**Responsable:** evol-pm

### Descripcion

El sistema debe implementar el pipeline de 6 fases con gates de aprobacion.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-005-01 | Fase inicial en memoria.md es "1-Briefing" | Funcional | Test |
| CA-005-02 | Transicion requiere "APROBADO" del gate | Funcional | Test CP-004 |
| CA-005-03 | Fase cambia en memoria.md tras aprobacion | Funcional | Test CP-004 |
| CA-005-04 | Transicion backwards bloqueada | Funcional | Test CP-004 |
| CA-005-05 | Cierre de sesion actualiza memoria.md con hitos | Funcional | Test CP-004 |

### Fases

| # | Fase | Artefactos obligatorios |
|---|------|-------------------------|
| 1 | Briefing | REQ-NNN, restricciones |
| 2 | Spec | SPEC.md, DOMAIN.md, Gherkin |
| 3 | Plan | tasks, ADRs |
| 4 | Build | codigo, tests |
| 5 | QA | CASOS_GHERKIN.md, reportes |
| 6 | Retro | lecciones.md, memoria.md |

### Dependencias

- REQ-004 (gate)
- REQ-010 (memoria.md)

---

## REQ-006: 16 Agentes Core

**Feature:** FEAT-004
**Prioridad:** ALTA
**Responsable:** evol-orchestrator

### Descripcion

El sistema debe incluir 18 agentes core permanentes.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-006-01 | Archivo existe para cada agente en prompts/agents/core/ | Funcional | Test |
| CA-006-02 | Frontmatter completo: name, description, category, triggers | Funcional | Review |
| CA-006-03 |evol-orchestrator delega segun dominio | Funcional | Review |
| CA-006-04 | evol-doc cumple DOC_STANDARD (cero emojis, Mermaid, tablas) | Funcional | Review |
| CA-006-05 | evol-sec implementa STRIDE threat modeling | Funcional | Review THREATS.md |
| CA-006-06 |evol-qa produce Gherkin completo por feature | Funcional | Review CASOS_GHERKIN.md |

### Tabla de Agentes

| ID | Nombre | Mission |
|----|--------|---------|
| 1 | evol-architect | Diseno sistemas, ADRs |
| 2 | evol-builder | Implementacion, TDD |
| 3 | evol-qa | Tests, Gherkin/BDD |
| 4 | evol-sec | SecDD, STRIDE |
| 5 | evol-devops | CI/CD, infra |
| 6 | evol-domain | DDD, modelado |
| 7 | evol-doc | Documentacion granular |
| 8 | evol-ux | User research |
| 9 | evol-data | Data engineering |
| 10 | evol-reviewer | Code review |
| 11 | evol-orchestrator | Composicion agentes |
| 12 | evol-pm | Gestion proyecto |
| 13 | evol-release | Release, semver |
| 14 | evol-analyst | Impacto, metricas |
| 15 | evol-agent-factory | Crear efimeros |
| 16 | evol-researcher | Investigacion autonoma |

---

## REQ-007: Sistema de Memoria

**Feature:** FEAT-005
**Prioridad:** MEDIA
**Responsable:** evol-orchestrator

### Descripcion

El sistema debe implementar jerarquia de memorias con precedencia clara.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-007-01 | memoria.md es truth del proyecto y nunca sobreescrito por otro | Funcional | Review |
| CA-007-02 | AGENT_MEMORY.md complementa memoria.md sin reemplazarlo | Funcional | Review |
| CA-007-03 | Memoria Persistente para busqueda semantica; no reemplaza memoria.md | Funcional | Review |
| CA-007-04 | Precedencia: memoria.md > AGENT_MEMORY.md > Memoria Persistente | Funcional | Review constitucion.md |
| CA-007-05 | evol-memory.py load/show/summarize/compact/search/gc/stats | Funcional | Test CP-005 |
| CA-007-06 | evol-lessons.py add/search/list/stats/gc/suggest-fix/apply-fix | Funcional | Test CP-006 |

### Dependencias

- REQ-008 (Memoria Persistente CLI, opt-in)
- REQ-009 (lecciones.md)

---

## REQ-008: Hooks Event-Driven

**Feature:** FEAT-006
**Prioridad:** MEDIA
**Responsable:** evol-devops

### Descripcion

El sistema debe implementar hooks bash event-driven con integración MCP.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-008-01 | hooks.json define 3 perfiles: minimal, standard, strict | Funcional | Review |
| CA-008-02 | pre:bash:dangerous-command bloquea rm -rf/, --force, chmod 777, curl\|sh | Funcional | Test |
| CA-008-03 | post:edit:memoria_persistente-index re-indexa async | Funcional | Review hook |
| CA-008-04 | session:start:context-load carga memoria.md y WORKING-CONTEXT.md | Funcional | Review hook |
| CA-008-05 | stop:git-check advierte cambios sin commit | Funcional | Review hook |
| CA-008-06 | pre:commit:gitflow valida branch naming | Funcional | Review hook |
| CA-008-07 | Exit 0 = permitir, Exit 2 = bloquear PreToolUse | Funcional | Test |

### Hooks por Perfil

| Hook ID | Minimal | Standard | Strict |
|---------|---------|----------|--------|
| pre:bash:dangerous-command | - | X | X |
| pre:edit:config-protection | - | - | X |
| pre:write:doc-file-warning | - | X | X |
| post:edit:memoria_persistente-index | X | X | X |
| session:start:context-load | - | X | X |
| stop:git-check | - | X | X |

---

## REQ-009: Auto-Evolucion de Skills

**Feature:** FEAT-007
**Prioridad:** MEDIA
**Responsable:** evol-researcher

### Descripcion

El sistema debe auto-detectar patrones y proponer skills.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-009-01 | evol-evolve.py status muestra instinct candidates | Funcional | Test |
| CA-009-02 | evol-evolve.py run genera propuestas de clusters | Funcional | Test |
| CA-009-03 | evol-evolve.py approve activa skill e indexa | Funcional | Test |
| CA-009-04 | evol-evolve.py invalidate marca anti-patron (confidence=0) | Funcional | Test |
| CA-009-05 | evol-evolve.py rollback mueve skill a .retired/ | Funcional | Test |
| CA-009-06 | evol-evolve.py sync-community --dry-run lista GitHub skills | Funcional | Test |
| CA-009-07 | evol-evolve.py install-skill con supply-chain scan | Funcional | Test |
| CA-009-08 | evol-researcher.py run genera RESEARCH.md | Funcional | Test |
| CA-009-09 | evol-researcher.py list muestra proposals pendientes | Funcional | Test |
| CA-009-10 | evol-researcher.py apply aplica proposal aprobada | Funcional | Test |

### Contrato de Fallo

| Caso | Comportamiento |
|------|----------------|
| GitHub timeout | Warning + continue con cache; sin cache exit 0 "sin conexion" |
| Rate-limit 403/429 | Reportar limite + reset time; usar cache |
| LLM unavailable | Mock provider; stubs "[mock — requiere LLM real]" |
| Skill falla scan | Bloquear install, reportar motivo |
| gitleaks/semgrep ausente | Warning "scan omitido", flag scan_skipped: true |

---

## REQ-010: Evaluacion y Calidad

**Feature:** FEAT-008
**Prioridad:** MEDIA
**Responsable:** evol-qa

### Descripcion

El sistema debe implementar eval harness para skills.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-010-01 | evol-eval.py run --suite=NAME ejecuta suite | Funcional | Test |
| CA-010-02 | 5 grader types: structural, behavioral, output_match, pass_at_k, llm_judge | Funcional | Review |
| CA-010-03 | evol-eval.py list muestra suites disponibles | Funcional | Test |
| CA-010-04 | evol-shield.py audit detecta violaciones | Funcional | Test |
| CA-010-05 | evol-shield.py audit --ci falla con exit 1 en CRITICAL | Funcional | Test |
| CA-010-06 | Integración-MCP: MCP config habilitado en artefactos = 1 | Funcional | CI |
| CA-010-07 | Anti-Emoji: grep emojis en docs/ = 0 | Funcional | CI |

### Graders

| Grader | Uso |
|--------|-----|
| structural | Verificar estructura archivos |
| behavioral | Verificar comportamiento script |
| output_match | Match exacto output |
| pass_at_k | Pass@k sampling |
| llm_judge | LLM como judge |

---

## REQ-011: Instalacion y Perfiles

**Feature:** FEAT-009
**Prioridad:** ALTA
**Responsable:** evol-devops

### Descripcion

El sistema debe soportar multiple perfiles de instalacion.

### Criterios de Aceptacion

| ID | Criterio | Tipo | Validacion |
|----|----------|------|------------|
| CA-011-01 | Perfil minimal instalable | Funcional | Test |
| CA-011-02 | Perfil core instalable (DEFAULT) | Funcional | Test |
| CA-011-03 | Perfil developer instalable | Funcional | Test |
| CA-011-04 | Perfil full instalable | Funcional | Test |
| CA-011-05 | Perfil lean falla si no hay global install | Funcional | Test |
| CA-011-06 | manifestos install-modules.json y install-profiles.json validos | Funcional | CI |
| CA-011-07 | evol-doctor.sh detecta modo COMPLETO vs BASE | Funcional | Test |

---

## Matriz de Trazabilidad

| REQ | FEAT | Prioridad | Status | CP |
|-----|------|-----------|--------|-----|
| REQ-001 | FEAT-001 | ALTA | IMPLEMENTADO | CP-001 |
| REQ-002 | FEAT-002 | ALTA | IMPLEMENTADO | CP-002 |
| REQ-003 | FEAT-002 | ALTA | IMPLEMENTADO | CP-002 |
| REQ-004 | FEAT-003 | ALTA | IMPLEMENTADO | CP-003 |
| REQ-005 | FEAT-004 | ALTA | IMPLEMENTADO | CP-004 |
| REQ-006 | FEAT-004 | ALTA | IMPLEMENTADO | - |
| REQ-007 | FEAT-005 | MEDIA | IMPLEMENTADO | CP-005 |
| REQ-008 | FEAT-006 | MEDIA | IMPLEMENTADO | - |
| REQ-009 | FEAT-007 | MEDIA | IMPLEMENTADO | CP-008 |
| REQ-010 | FEAT-008 | MEDIA | IMPLEMENTADO | - |
| REQ-011 | FEAT-009 | ALTA | IMPLEMENTADO | - |

**Total: 11 requisitos funcionales**