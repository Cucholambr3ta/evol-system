---
name: evol-sdd-spec
description: Spec-Driven Development. Genera y refina SPEC.md con REQ-NNN formales, trazabilidad a features, y criterios de aceptación medibles.
category: discipline-base
trigger: /sdd
---

# evol-sdd-spec

## Fase del Pipeline
Todas (transversal)

## Artefacto Clave
`docs/specs/SPEC.md`

## Flujo de Trabajo

### 1. Generar SPEC.md
```bash
# Desde requirements existentes
evol-sdd spec-generate --from=acuerdos/requirements/

# Con trazabilidad a features
evol-sdd spec-generate --features=docs/features/FEATURES.md
```

### 2. Refinar SPEC
```bash
# Agregar REQ-NNN con criterios de aceptación
evol-sdd spec-refine --req=REQ-001 --acceptance="dado/cuando/entonces"

# Validar trazabilidad
evol-sdd spec-validate --trace
```

### 3. Generar Reporte
```bash
evol-sdd spec-report --format=markdown
```

## Formato REQ-NNN

```markdown
## REQ-001: [Título]

**Prioridad:** P0/P1/P2
**Feature:** FEAT-XXX
**Disciplina:** SDD

### Descripción
[Descripción clara y concisa]

### Criterios de Aceptación
- [ ] Dado [contexto], cuando [acción], entonces [resultado]
- [ ] Dado [contexto], cuando [acción], entonces [resultado]

### Categorías de Prueba
- Unit: [qué testear]
- Integration: [qué testear]
- E2E: [qué testear]
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Briefing | Generar REQ-NNN iniciales |
| Spec | Refinar y validar trazabilidad |
| Build | Verificar implementación contra REQ |
| QA | Validar criterios de aceptación |

## Referencia
- `docs/constitucion.md` Art. 9 (Pipeline)
- `docs/disciplinas/SDD.md`


## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
