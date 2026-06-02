# Matriz de Trazabilidad — Requisitos vs Pruebas

## Estado de Implementacion

| Codigo | Descripcion | Test/Prueba | Script/Workflow | Estado |
|--------|-------------|-------------|-----------------|--------|
| REQ-001 | Bootstrap genera proyecto con `.git` | CP-001 | `scripts/evol-init.sh` | Roadmap |
| REQ-002 | Bootstrap idempotente | CP-001 | `tests/test_init_idempotent.bats` | Ejecutado |
| REQ-003 | Perfiles disponibles y validos | CP-001 | `scripts/evol-init.sh --list-profiles` | Roadmap |
| REQ-004 | Crear agente efimero con registro | CP-002 | `scripts/evol-agent-lifecycle.py create` | Implementado |
| REQ-005 | Invocar agente incrementa contador | CP-002 | `scripts/evol-agent-lifecycle.py invoke` | Implementado |
| REQ-006 | Retirar agente crea snapshot SHA-256 | CP-002 | `scripts/evol-agent-lifecycle.py retire` | Implementado |
| REQ-007 | Recuperar agente desde snapshot | CP-002 | `scripts/evol-agent-lifecycle.py recall` | Implementado |
| REQ-008 | Gate inicializa con permisos 0600 | CP-003 | `scripts/evol-gate.py init` | Implementado |
| REQ-009 | Gate firma HMAC-SHA256 | CP-003 | `scripts/evol-gate.py approve` | Implementado |
| REQ-010 | Gate valida cadena y falla en log alterado | CP-003, CP-004 | `scripts/evol-gate.py validate` | Ejecutado |
| REQ-011 | Transicion entre fases requiere APROBADO | CP-004 | `scripts/evol-gate.py transition` | Implementado |
| REQ-012 | memoria.md refleja fase actual | CP-004 | workflow `cierre-fase.md` | Roadmap |
| REQ-013 | Cargar memoria al inicio de sesion | CP-005 | `scripts/evol-memory.py load` | Roadmap |
| REQ-014 | Persistir sesion en journal | CP-005 | `scripts/evol-memory.py summarize` | Roadmap |
| REQ-015 | GC de tool_result vencidos | CP-005 | `scripts/evol-memory.py gc` | Roadmap |
| REQ-016 | Anadir leccion con deduplicacion | CP-006 | `scripts/evol-lessons.py add` | Roadmap |
| REQ-017 | Buscar lecciones con score | CP-006 | `scripts/evol-lessons.py search` | Roadmap |
| REQ-018 | Sugerir y aplicar fixes de lecciones | CP-006 | `scripts/evol-lessons.py suggest-fix` | Roadmap |

## Estados

| Estado | Significado |
|--------|-------------|
| **Roadmap** | Planificado, no implementado aun |
| **Implementado** | Codigo existe, puede no tener test ejecutado |
| **Ejecutado** | Tiene test automatizado pasando en CI |

## Cobertura Actual

| Categoria | Total | Roadmap | Implementado | Ejecutado |
|-----------|-------|---------|--------------|-----------|
| Bootstrap | 3 | 2 | 1 | 1 |
| Agentes Efimeros | 4 | 0 | 4 | 0 |
| Gate Keeper | 3 | 0 | 3 | 2 |
| Pipeline | 2 | 1 | 1 | 0 |
| Memoria | 3 | 3 | 0 | 0 |
| Lecciones | 3 | 3 | 0 | 0 |
| **Total** | **18** | **9** | **9** | **3** |

## Gates de Calidad

| Gate | Criterio | Bloquea |
|------|----------|---------|
| G1 | `pytest tests/` 100%% pass | SI |
| G2 | `bats tests/*.bats` 100%% pass | SI |
| G3 | `bash scripts/lint-workflows.sh` OK | SI |
| G4 | `python3 scripts/validate-registry.py --strict` OK | SI |
| G5 | jsonschema contra schemas/ OK | SI |
| G6 | grep mcpServers en artefactos = 0 | SI |
| G7 | grep emojis en docs/ = 0 | SI |
| G8 | `python3 scripts/evol-shield.py audit --ci` OK | SI |
| G9 | `bats tests/test_init_idempotent.bats` OK | SI |

## Requisitos No Funcionales

| ID | Descripcion | Estado |
|----|-------------|--------|
| NFR-001 | `evol-doctor.sh` completa en < 5s | Implementado |
| NFR-002 | `evol-init.sh --profile=full` completa en < 30s | Implementado |
| NFR-003 | Modo BASE funcional sin MemPalace | Implementado |
| NFR-004 | Sin MCP en configs generadas | Implementado (G6) |
| NFR-005 | Sin hardcoded secrets | Implementado (G8) |
| NFR-006 | Rutas relativas en todos los archivos | Roadmap |
| NFR-007 | Max 10 lineas por funcion | Implementado (lint) |
| NFR-008 | Traces en .evol/traces/ | Roadmap |

## Artefactos de Trazabilidad

| Artefacto | Ubicacion | Productor | Consumidor |
|-----------|-----------|-----------|------------|
| ARQUITECTURA.md | docs/arquitectura/ | evol-architect | Todos |
| DOMAIN.md | docs/arquitectura/ | evol-domain | evol-builder, evol-qa |
| FUNCIONALES.md | docs/requisitos/ | evol-pm | evol-builder, evol-qa |
| GLOSARIO.md | docs/requisitos/ | evol-domain | Todos |
| CASOS_GHERKIN.md | docs/qa/ | evol-qa | evol-builder (TDD) |
| MATRIZ_TRAZABILIDAD.md | docs/qa/ | evol-qa | evol-pm, evol-release |
| memoria.md | raiz | Todos (cierre-fase) | Todos (session-start) |
| lecciones.md | raiz | Todos | evol-researcher |
