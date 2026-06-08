---
name: evol-fdd-feature
description: Feature-Driven Development. Descompone features en FEATURES.md con priorización RICE/MoSCoW, story mapping, y criterios de aceptación.
category: discipline-base
trigger: /fdd
---

# evol-fdd-feature

## Fase del Pipeline
Fase 1 (Briefing) + Fase 3 (Plan)

## Artefacto Clave
`docs/features/FEATURES.md`

## Flujo de Trabajo

### 1. Generar FEATURES.md
```bash
evol-fdd features-generate --from=acuerdos/idea/
```

### 2. Priorizar con RICE/MoSCoW
```bash
evol-fdd features-prioritize --method=RICE
# Returns: Reach, Impact, Confidence, Effort score
```

### 3. Story Mapping
```bash
evol-fdd story-map --features=docs/features/FEATURES.md
```

### 4. Validar
```bash
evol-fdd features-validate --check=dependencies
```

## Formato FEATURE

```markdown
## FEAT-001: [Nombre]

**Prioridad:** Must/Should/Could/Won't
**RICE Score:** [R×I×C]/E
**Fases:** 1, 3

### User Story
Como [rol], quiero [acción] para [beneficio].

### Criterios de Aceptación
- [ ] Dado/ Cuando/ Entonces

### Dependencias
- REQUIERE: FEAT-002
- BLOQUEA: FEAT-003
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Briefing | Generar features iniciales, priorizar |
| Spec | Conectar features con REQ-NNN |
| Plan | Organizar por features verticales |
| Build | Implementar por feature |


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
