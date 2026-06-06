# Casos Gherkin — Evol-DD

## Reglas de Escritura (DOC_STANDARD)

| Regla | Limite | Razon |
|-------|--------|-------|
| Max escenarios por feature | 8 | Split si mas |
| Max pasos por escenario | 5 | Legibilidad |
| Vocabulario | DOMAIN.md exclusively | Ubiquitous Language |
| Escenario referencia REQ-NNN | Requerido | Trazabilidad |
| Examples incluye | normal, limite inf, limite sup, invalido | Cobertura borde |

---

## FEAT-001: Bootstrap de Proyecto

**Prioridad:** ALTA | **REQ:** REQ-001, REQ-002, REQ-003

### Happy Path

```gherkin
Scenario: Bootstrap exitoso con perfil core
  Given directorio vacio "/tmp/test-evol"
  And git instalado en sistema
  And python3 version 3.10+ disponible
  When ejecuto "bash scripts/evol-init.sh /tmp/test-evol --profile=core"
  Then directorio contiene ".git/"
  And archivo "memoria.md" existe en directorio
  And archivo ".gitignore" existe con 3 categorias
  And archivo "evol.profile.yml" existe con profile "core"
  And archivo "lecciones.md" existe
  And mensaje "[evol-init] Bootstrap complete" mostrado  # REQ-001

Scenario: Bootstrap idempotente
  Given proyecto ya inicializado en "/tmp/test-evol"
  And archivos memoria.md, lecciones.md existen
  When ejecuto "bash scripts/evol-init.sh /tmp/test-evol --profile=core"
  Then no hay errores
  And archivos previos intactos
  And mensaje indicando re-ejecucion  # REQ-002

Scenario: Listar perfiles disponibles
  When ejecuto "bash scripts/evol-init.sh --list-profiles"
  Then salida incluye: minimal, core, developer, security, research, full, lean
  And descripcion de cada perfil mostrada
```

### Error Cases

```gherkin
Scenario: Directorio destino no especificado
  Given sin argumentos
  When ejecuto "bash scripts/evol-init.sh"
  Then mensaje de uso mostrado: "Usage: evol-init.sh <destination> [--profile=<profile>]"
  And exit code 1

Scenario: Perfil inexistente
  Given perfil "xyz-inexistente" no existe
  When ejecuto "bash scripts/evol-init.sh /tmp/test --profile=xyz-inexistente"
  Then mensaje de error: "Unknown profile"
  And lista de perfiles disponibles mostrada
  And exit code 1

Scenario: Git no instalado
  Given git no disponible en PATH
  When ejecuto "bash scripts/evol-doctor.sh"
  Then mensaje "[ERROR] git not found"
  And exit code no 0
```

### Edge Cases

```gherkin
Scenario Outline: Bootstrap con perfil <perfil>
  Given perfil "<perfil>"
  When ejecuto "bash scripts/evol-init.sh /tmp/test --profile=<perfil>"
  Then resultado "<resultado>"

  Examples:
    | perfil    | resultado |
    | minimal   | exito     |
    | core      | exito     |
    | developer | exito     |
    | security  | exito     |
    | research  | exito     |
    | full      | exito     |
    | lean      | error si no global install |
    | empty     | error     |
    | INVALID   | error     |
```

---

## FEAT-002: Ciclo de Vida de Agente Efimero

**Prioridad:** ALTA | **REQ:** REQ-004, REQ-005, REQ-006, REQ-007, REQ-008

### Happy Path

```gherkin
Scenario: Crear agente efimero
  Given agent "test-agent" no existe en registry
  And directorio prompts/agents/ephemeral/ existe
  When ejecuto "python3 scripts/evol-agent-lifecycle.py create --name test-agent --task 'Prueba de agente' --expires-after 7"
  Then archivo "prompts/agents/ephemeral/*-test-agent.md" creado desde templates/agent.template.md
  And registry actualizado con entrada para "test-agent"
  And campo "ephemeral": true en registry
  And campo "expires_after_days": 7 en registry
  And mensaje "Agent created: test-agent (expires in 7 days)" mostrado
  And Memoria Persistente indexado (si disponible)  # REQ-004

Scenario: Invocar agente
  Given agente "test-agent" existe y no esta retired
  When ejecuto "python3 scripts/evol-agent-lifecycle.py invoke test-agent"
  Then sessions_used incrementa en 1
  And mensaje "Agent invoked: test-agent" mostrado
  And mensaje "Sessions used: N" mostrado  # REQ-005

Scenario: Retirar agente con snapshot
  Given agente "test-agent" existe
  When ejecuto "python3 scripts/evol-agent-lifecycle.py retire test-agent"
  Then archivo .md eliminado de prompts/agents/ephemeral/
  And directorio .evol/agents/retired/ existe
  And archivo ".evol/agents/retired/test-agent.json" creado
  And campo "prompt" presente en snapshot
  And campo "prompt_sha256" calculado y presente en snapshot
  And campo "invocation_log" presente con timestamp y task
  And campo "sessions_used" igual al contador final
  And registry marca "retired": true
  And registry limpia "prompt_file"  # REQ-006

Scenario: Recuperar agente (recall completo)
  Given agente "test-agent" retired con snapshot
  And Memoria Persistente activo con indice previo
  When ejecuto "python3 scripts/evol-agent-lifecycle.py recall test-agent"
  Then archivo .md reconstruido en prompts/agents/ephemeral/
  And archivo identical al original (SHA-256 match)
  And registry marca "retired": false
  And registry marca "recalled": true
  And registro "recalled_at" con timestamp
  And Memoria Persistente re-indexado
  And mensaje "Recall type: COMPLETO (JSON + semantic)" mostrado  # REQ-007

Scenario: Garbage collection de agentes vencidos
  Given agentes vencidos existen (created_at + expires < now)
  When ejecuto "python3 scripts/evol-agent-lifecycle.py gc"
  Then agentes vencidos retirada automaticamente
  And contador de agentes collectados mostrado
  And registry actualizado  # REQ-008

Scenario: Listar agentes por filtro
  Given agentes de diferentes tipos existen
  When ejecuto "python3 scripts/evol-agent-lifecycle.py list --all"
  Then todos los agentes listados con nombre, categoria, estado
  When ejecuto "python3 scripts/evol-agent-lifecycle.py list --ephemeral"
  Then solo agentes con category "ephemeral" listados
  When ejecuto "python3 scripts/evol-agent-lifecycle.py list --retired"
  Then solo agentes con retired=true listados
```

### Error Cases

```gherkin
Scenario: Agent no existe para invoke
  Given agent "no-existe" no existe en registry
  When ejecuto "python3 scripts/evol-agent-lifecycle.py invoke no-existe"
  Then mensaje "Agent not found: no-existe"
  And exit code 1

Scenario: Snapshot corrupto en recall (SHA mismatch)
  Given snapshot ".evol/agents/retired/test-agent.json" existe
  And campo "prompt_sha256" no coincide con contenido real
  When ejecuto "python3 scripts/evol-agent-lifecycle.py recall test-agent"
  Then mensaje "Snapshot integrity check FAILED"
  And mensaje mostrando SHA esperado y calculado
  And hint "Use --force to override"
  And exit code 1

Scenario: Recall sin snapshot existente
  Given snapshot ".evol/agents/retired/no-existe.json" no existe
  When ejecuto "python3 scripts/evol-agent-lifecycle.py recall no-existe"
  Then mensaje "Snapshot not found: .evol/agents/retired/no-existe.json"
  And exit code 1

Scenario: Duplicar nombre de agente
  Given agente "test-agent" ya existe
  When ejecuto "python3 scripts/evol-agent-lifecycle.py create --name test-agent --task otra"
  Then mensaje de error por nombre duplicado
  And archivo existente no modificado
```

### Edge Cases

```gherkin
Scenario Outline: GC con expiration <dias> dias
  Given creo agente con expires_after=<dias>
  And dia actual es dia 0
  When Espero <dias+1> dias
  And ejecuto "python3 scripts/evol-agent-lifecycle.py gc"
  Then resultado "<resultado>"

  Examples:
    | dias | resultado        | nota              |
    | 0    | expirado        | inmediato         |
    | 1    | expirado        | dia siguiente     |
    | 30   | NO expirado     | dentro de plazo   |
    | 365  | NO expirado     | maximo razonable   |

Scenario: Recall con --force para snapshot corrupto
  Given snapshot corrupto existe
  When ejecuto "python3 scripts/evol-agent-lifecycle.py recall test-agent --force"
  Then agente reconstruido sin verificar SHA
  And warning mostrado sobre perdida de verificacion
  And mensaje indicando uso de --force
```

---

## FEAT-003: Gate Keeper HMAC-SHA256

**Prioridad:** ALTA | **REQ:** REQ-009, REQ-010, REQ-011

### Happy Path

```gherkin
Scenario: Inicializar gate
  Given directorio .evol/ no existe
  When ejecuto "python3 scripts/evol-gate.py init"
  Then directorio .evol/ creado
  And archivo ".evol/.gate-key" creado con clave de 32 bytes aleatorios
  And archivo .evol/.gate-key con permisos 0600 (chmod 600)
  And archivo ".evol/.gate-log.jsonl" creado (vacio)
  And archivo .evol/ en .gitignore
  And mensaje "Gate initialized" mostrado  # REQ-009

Scenario: Aprobar fase con signature HMAC
  Given gate inicializado
  And fase "spec" es proxima
  When ejecuto "python3 scripts/evol-gate.py approve --phase spec --approver human"
  Then entrada en .evol/.gate-log.jsonl con timestamp ISO8601
  And entrada contiene: timestamp, phase, approver, signature
  And signature calculada con HMAC-SHA256 de "phase:approver:timestamp"
  And mensaje "APROBADO: spec by human" mostrado

Scenario: Verificar gate activo
  Given gate inicializado previamente
  When ejecuto "python3 scripts/evol-gate.py validate"
  Then mensaje "Gate active"
  And exit code 0  # REQ-010

Scenario: Ver historial de aprobaciones
  Given gate tiene entradas previas
  When ejecuto "python3 scripts/evol-gate.py status"
  Then todas las entradas mostradas con formato "[timestamp] phase approved by approver"

Scenario: Transicion entre fases
  Given fase actual "plan" y proxima "build"
  When ejecuto "python3 scripts/evol-gate.py transition --from plan --to build"
  Then entrada log: "plan -> build"
  And mensaje "Transition: plan -> build" mostrado
```

### Error Cases

```gherkin
Scenario: Validar gate no inicializado
  Given directorio .evol/ no existe
  When ejecuto "python3 scripts/evol-gate.py validate"
  Then mensaje "Gate not initialized. Run: evol-gate init"
  And exit code 1

Scenario: Approve sin gate inicializado
  Given gate no existe
  When ejecuto "python3 scripts/evol-gate.py approve --phase spec"
  Then mensaje de error
  And exit code 1
```

---

## FEAT-004: Pipeline de 6 Fases

**Prioridad:** ALTA | **REQ:** REQ-012, REQ-013, REQ-014

### Happy Path

```gherkin
Scenario: Transicion entre fases con APROBADO
  Given fase actual "build" en memoria.md
  And gate inicializado
  When solicito transicion a fase "qa"
  Then gate solicita "APROBADO" explicitamente
  When confirmo "APROBADO" al gate
  Then fase en memoria.md cambia a "5-QA"
  And entrada de transicion en gate log
  And hitos registrados en memoria.md

Scenario: Verificar estado actual en memoria.md
  Given fase "spec" activa
  When leo memoria.md
  Then campo "Fase Evol-DD activa" muestra "2-Spec"
  And proximo paso en campo "Proximo paso" disponible

Scenario: Pipeline completo de 6 fases
  Given fase "briefing" activa
  When ejecuto las 6 fases con APROBADO en cada transicion:
    | from    | to    |
    | briefing | spec   |
    | spec    | plan   |
    | plan    | build  |
    | build   | qa     |
    | qa      | retro  |
  Then todas las fases completadas secuencialmente
  And memoria.md actualizada con hitos de cada fase
  And lecciones.md actualizada con aprendizajes

Scenario: Cierre de sesion con Flight Recorder
  Given sesion de trabajo terminada
  When ejecuto workflow "/evol cierre"
  Then memoria.md actualizada con sesion actual
  And lecciones.md evaluada para aprendizaje
  And GC de agentes vencidos ejecutado
  And hook stop:git-check verificado
```

### Error Cases

```gherkin
Scenario: Transicion sin APROBADO
  Given fase "spec"
  When solicito transicion sin confirmar APROBADO
  Then transicion bloqueada por gate
  And mensaje "APROBADO requerido para transicion de fase"
  And fase permanece en "spec"

Scenario: Fase invalida
  Given gate inicializado
  When ejecuto "python3 scripts/evol-gate.py approve --phase fase-inexistente"
  Then mensaje de error con lista de fases validas
  And log no modificado

Scenario: Transicion backwards
  Given fase "qa"
  When solicito transicion a "plan" (hacia atras)
  Then transicion bloqueada
  And mensaje "Solo se permite transicion forward"
```

### Edge Cases

```gherkin
Scenario Outline: Pipeline con <fase> como inicial
  Given fase inicial "<fase>"
  When verifico estado en memoria.md
  Then fase activa coincide con "<fase>"

  Examples:
    | fase     | nota              |
    | briefing | inicio del pipeline |
    | spec     | post-briefing     |
    | build    | post-plan         |

Scenario: Sesion multiple en mismo dia
  Given dia "2026-06-02"
  And sesion 1 completada con hitos en memoria.md
  When inicio sesion 2
  Then journal memory/2026-06-02.md tiene entrada para sesion 2
  And no sobreescribe entrada de sesion 1
  And contexto de sesion anterior cargado
```

---

## FEAT-005: Memoria Conversacional

**Prioridad:** MEDIA | **REQ:** REQ-015, REQ-016, REQ-017

### Happy Path

```gherkin
Scenario: Cargar memoria al iniciar sesion
  Given AGENT_MEMORY.md existe con contenido previo
  And journal de ayer "memory/YYYY-MM-DD.md" existe
  When ejecuto "python3 scripts/evol-memory.py load"
  Then seccion "=== Memory Load ===" mostrada
  Then contenido AGENT_MEMORY.md mostrado
  Then contenido journal de ayer mostrado
  Then seccion "===================" mostrada  # REQ-015

Scenario: Persistir sesion en journal
  Given sesion terminada con archivo session.jsonl
  And archivo contiene mensajes en formato JSON
  When ejecuto "python3 scripts/evol-memory.py summarize --messages session.jsonl"
  Then archivo "memory/YYYY-MM-DD.md" actualizado o creado
  And entrada de sesion con timestamp en formato "## Sesion YYYY-MM-DDTHH:MM:SS"
  And seccion "### Factual Memory" con hechos objetivos
  And seccion "### Reflections & Logic" con estrategias  # REQ-016

Scenario: Buscar en memoria
  Given conversas previas en AGENT_MEMORY.md y journals
  When ejecuto "python3 scripts/evol-memory.py search 'palabra clave'"
  Then resultados mostrados con source y snippet
  And resultados ordenados por relevancia

Scenario: GC de tool results vencidos
  Given directorio tool_result/ con archivos
  And archivos con antiguedad mayor a TTL (3 dias por defecto)
  When ejecuto "python3 scripts/evol-memory.py gc --days 3"
  Then archivos vencidos eliminados
  And contador de archivos eliminados mostrado
  And archivos no vencidos intactos  # REQ-017

Scenario: Stats del sistema de memoria
  When ejecuto "python3 scripts/evol-memory.py stats"
  Then numero de journals mostrado
  Then tamano de AGENT_MEMORY.md mostrado
  Then numero de archivos dialog y tool_result mostrado
```

### Edge Cases

```gherkin
Scenario Outline: Compactar historial con <tokens> tokens
  Given historial de mensajes con <tokens> tokens totales
  When ejecuto "python3 scripts/evol-memory.py compact --messages session.jsonl"
  Then resultado "<resultado>"

  Examples:
    | tokens  | resultado        | accion                  |
    | 50000  | sin compactar    | bajo umbral             |
    | 90000  | sin compactar    | exactamente en umbral  |
    | 95000  | compactar        | sobre umbral           |
    | 150000 | compactar        | muy sobre umbral       |

Scenario: Load sin archivos previos
  Given AGENT_MEMORY.md no existe
  And journals no existen
  When ejecuto "python3 scripts/evol-memory.py load"
  Then solo estructura "=== Memory Load ===" y "===================" mostrada
  And sin errores
```

---

## FEAT-006: Sistema de Lecciones Aprendidas

**Prioridad:** MEDIA | **REQ:** REQ-018, REQ-019, REQ-020

### Happy Path

```gherkin
Scenario: Anadir leccion nueva
  Given leccion no existe previamente
  When ejecuto "python3 scripts/evol-lessons.py add --titulo 'GitFlow violado' --categoria PROCESO --contexto 'Construccion' --problema 'Todo en un commit' --causa 'No crear branches' --leccion 'GitFlow obligatorio' --aplica 'Todo proyecto'"
  Then leccion guardada en lecciones.md
  And deduplicacion fuzzy aplicada (Jaccard 70%)
  And mensaje "Lesson added: GitFlow violado" mostrado  # REQ-018

Scenario: Anadir leccion con fix ya aplicado
  Given fix ya implementado para problema
  When ejecuto "python3 scripts/evol-lessons.py add --fix-aplicado 'Branches creadas post-hoc'"
  Then leccion creada con campo "Fix aplicado" preenchido
  And campo "Estado mejoras" pendiente

Scenario: Buscar lecciones
  Given lecciones existentes sobre PROCESO y ARQUITECTURA
  When ejecuto "python3 scripts/evol-lessons.py search 'Git'"
  Then lecciones relevantes mostradas con titulo, categoria, score
  And sinonimos controlados

Scenario: Listar solo lecciones pendientes
  When ejecuto "python3 scripts/evol-lessons.py list --pendientes"
  Then solo lecciones con "Estado mejoras: pendiente" listadas
  And lecciones aplicadas filtradas

Scenario: Suggest fix con LLM
  Given leccion "GitFlow violado" existe
  When ejecuto "python3 scripts/evol-lessons.py suggest-fix 'GitFlow violado'"
  Then mejoras propuestas por evol-researcher.py mostradas
  And mejoras guardadas en lecciones.md si --apply usado  # REQ-019

Scenario: Apply fix
  Given leccion con mejoras pendientes
  When ejecuto "python3 scripts/evol-lessons.py apply-fix 'GitFlow violado' --fix 'Orquestador crea branch antes de cada sprint'"
  Then campo "Estado mejoras" cambia a "aplicado"
  And campo "Mejoras sugeridas" preserve contenido previo

Scenario: Stats de lecciones
  When ejecuto "python3 scripts/evol-lessons.py stats"
  Then total de lecciones mostrado
  Then desglose por categoria mostrado
  Then numero de pendientes y aplicadas mostrado  # REQ-020

Scenario: GC para eliminar duplicados exactos
  Given lecciones con duplicados exactos
  When ejecuto "python3 scripts/evol-lessons.py gc"
  Then duplicados exactos eliminados
  And mensaje "Removed N duplicates" mostrado
```

### Error Cases

```gherkin
Scenario: Categoria invalida
  Given categoria "INVALIDA" no existe
  When ejecuto "python3 scripts/evol-lessons.py add --categoria INVALIDA ..."
  Then mensaje de error con categorias validas
  And exit code 1

Scenario: Leccion no existe para suggest-fix
  Given leccion "inexistente" no existe
  When ejecuto "python3 scripts/evol-lessons.py suggest-fix 'inexistente'"
  Then mensaje "Lesson not found: inexistente"
```

---

## FEAT-007: IDE Adapters y Adaptacion

**Prioridad:** MEDIA | **REQ:** REQ-021, REQ-022

### Happy Path

```gherkin
Scenario: Generate configs para IDE especifico
  Given workflow en .agent/workflows/ existen
  When ejecuto "bash scripts/evol-adapt.sh claude-code"
  Then directorio .claude/commands/ creado
  And archivos .md copiados desde workflows

Scenario: Generate todos los IDEs
  Given workflows definidos
  When ejecuto "bash scripts/evol-adapt.sh all"
  Then configs generados para los 7 IDEs:
    | IDE | Directorio |
    | claude-code | .claude/commands/ |
    | opencode | .opencode/command/ |
    | cursor | .cursor/rules/ |
    | windsurf | .windsurf/workflows/ |
    | vscode-copilot | .github/prompts/ |
    | antigravity | .agents/skills/ |
    | codex | ~/.codex/skills/ |
  And mensaje "Generation complete" mostrado

Scenario: Dry-run de adaptacion
  Given workflows existentes
  When ejecuto "bash scripts/evol-adapt.sh all --dry-run"
  Then lista de archivos a generar mostrada
  And sin archivos creados
  # REQ-021

Scenario: Adapt con trigger custom
  Given trigger "custom-trigger" especificado
  When ejecuto "bash scripts/evol-adapt.sh all --trigger=custom-trigger"
  Then archivos generados referencian "custom-trigger"
  And trigger por defecto no afectado
```

### Error Cases

```gherkin
Scenario: IDE invalido
  Given target "unknown-ide" no existe
  When ejecuto "bash scripts/evol-adapt.sh unknown-ide"
  Then mensaje "Unknown target: unknown-ide"
  And usage mostrado

Scenario: Sin permisos de escritura
  Given directorio protegido
  When ejecuto "bash scripts/evol-adapt.sh claude-code"
  Then mensaje de error "Permission denied"
```

### Edge Cases

```gherkin
Scenario: Integración-MCP verification
  Given configs generados
  When ejecuto grep en configs generados
  Then 0 referencias a "mcpServers" encontradas
  Then 0 referencias a "mcp.json" encontradas  # REQ-022

Scenario: Generar sin workflows
  Given .agent/workflows/ vacio
  When ejecuto "bash scripts/evol-adapt.sh claude-code"
  Then mensaje de warning "No workflows found"
  And directorios creados vacios
```

---

## FEAT-008: Auto-Evolucion de Skills

**Prioridad:** MEDIA | **REQ:** REQ-023, REQ-024, REQ-025

### Happy Path

```gherkin
Scenario: Status de instincts
  Given instincts en base de datos
  When ejecuto "python3 scripts/evol-evolve.py status"
  Then numero de instinct candidates mostrado
  Then top patterns listados con confidence  # REQ-023

Scenario: Generar propuestas de skills (dry-run)
  Given instincts con confidence > 0.7
  When ejecuto "python3 scripts/evol-evolve.py run --dry-run"
  Then clusters propuestos listados
  Then sin skills creadas todavia

Scenario: Generar y aprobar propuesta
  Given instincts suficientes para clustering
  When ejecuto "python3 scripts/evol-evolve.py run"
  Then skills creadas en skills/
  Then eval suites creadas en evals/
  Then entrada en tabla evolutions con status "proposed"
  When ejecuto "python3 scripts/evol-evolve.py approve cluster-1"
  Then skill activada
  Then Memoria Persistente indexado  # REQ-024

Scenario: Invalidar anti-patron
  Given instinct existe
  When ejecuto "python3 scripts/evol-evolve.py invalidate 1 --reason 'Anti-pattern detectado'"
  Then confidence ajustada a 0
  Then campo invalidated=true
  Then razon almacenada

Scenario: Rollback de skill auto-generada
  Given skill auto-generada existe
  When ejecuto "python3 scripts/evol-evolve.py rollback mi-skill"
  Then skill movida a skills/.retired/
  Then evolutions marcada como "rolled_back"
```

### Edge Cases

```gherkin
Scenario: Sync community sin conexion
  Given GitHub no disponible
  When ejecuto "python3 scripts/evol-evolve.py sync-community --dry-run"
  Then warning "sin conexion, propuestas omitidas"
  Then exit code 0

Scenario: Instalar skill sin supply-chain scan
  Given gitleaks no instalado
  When ejecuto "python3 scripts/evol-evolve.py install-skill nueva-skill"
  Then warning "scan omitido — instalar gitleaks+semgrep"
  Then skill instalada con flag scan_skipped=true
```

---

## Matriz de Trazabilidad Completa

| Feature | Escenarios | REQs | CP |
|---------|------------|------|-----|
| FEAT-001 | 6 | REQ-001, REQ-002, REQ-003 | CP-001 |
| FEAT-002 | 13 | REQ-004, REQ-005, REQ-006, REQ-007, REQ-008 | CP-002 |
| FEAT-003 | 6 | REQ-009, REQ-010, REQ-011 | CP-003 |
| FEAT-004 | 5 | REQ-012, REQ-013, REQ-014 | CP-004 |
| FEAT-005 | 6 | REQ-015, REQ-016, REQ-017 | CP-005 |
| FEAT-006 | 8 | REQ-018, REQ-019, REQ-020 | CP-006 |
| FEAT-007 | 6 | REQ-021, REQ-022 | CP-007 |
| FEAT-008 | 6 | REQ-023, REQ-024, REQ-025 | CP-008 |

**Total: 56 escenarios Gherkin cubriendo 25 requisitos**