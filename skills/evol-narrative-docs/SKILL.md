---
name: evol-narrative-docs
description: Documentación con storytelling técnico. Aplica estructura narrativa, decisiones branching y technical storytelling para crear docs que se lean y se entiendan.
category: game-inspired
trigger: /narrative-docs
---

# evol-narrative-docs

## Cuándo Usar

Activar esta skill cuando se necesita crear documentación que sea engaging y comprensible:

- **Technical storytelling**: convertir specs secas en narrativas que enganchan
- **Decision records**: ADRs con contexto narrativo, no solo dry facts
- **Architecture docs**: documentación que cuente la historia del sistema
- **Onboarding guides**: guías que guíen al developer a través de una journey
- **Postmortems**: historias de incidentes con lessons learned narrativas
- **Release notes**: changelogs que cuenten qué cambió y por qué importa

**No usar para**: documentación puramente referencial (usar evol-doc), documentación de dominio (usar evol-domain).

## Conocimiento de Dominio

### Narrative Structure
- **Three-act structure**: setup → confrontation → resolution
- **Hero's journey**: el developer como héroe que supera obstáculos
- **In medias res**: empezar en el medio de la acción, luego flashbacks
- **Non-linear narratives**: branches, choose-your-own-adventure para docs

### Technical Storytelling
- **Problem → Solution → Result**: la estructura más efectiva para tech docs
- **Before/After**: mostrar el estado antes y después del cambio
- **Case studies**: historias reales de implementación
- **Metaphor and analogy**: hacer lo complejo familiar

### Decision Records
- **Context**: qué estaba pasando, por qué se necesitó decidir
- **Options**: qué alternativas se consideraron
- **Decision**: qué se decidió y por qué
- **Consequences**: qué impacto tuvo la decisión

### Writing Patterns
- **BLUF (Bottom Line Up Front)**: dar la respuesta primero, contexto después
- **Pyramid principle**: estructura jerárquica de información
- **Show, don't tell**: usar ejemplos en vez de descripciones abstractas
- **Scannable content**: headings, bullets, bold key phrases

### Engagement Mechanics
- **Curiosity gaps**: plantear preguntas que el lector quiera responder
- **Progressive disclosure**: información en capas, no todo de golpe
- **Concrete examples**: ejemplos específicos > descripciones generales
- **Visual anchoring**: diagrams, code blocks, tables para romper texto

## Flujo de Trabajo

1. **Identificar audiencia**: ¿Para quién es la documentación? (developer, PM, stakeholder)
2. **Definir el arco narrativo**: ¿Cuál es la historia? (problema → solución → resultado)
3. **Estructurar con BLUF**: respuesta/decisión primero, contexto después
4. **Crear curiosity gaps**: plantear preguntas que enganchen al lector
5. **Agregar ejemplos concretos**: code snippets, diagrams, before/after
6. **Iterar con progressive disclosure**: información en capas
7. **Testear con usuario real**: ¿Se entiende? ¿Se usa? ¿Es engaging?
8. **Mantener viva**: update docs como se updatea código

## Integración con Pipeline

- **Briefing (Fase 1)**: documentar la historia del proyecto, el "por qué"
- **Spec (Fase 2)**: ADRs narrativos, decision records con contexto
- **Plan (Fase 3)**: documentar el plan como narrative, no solo tasks
- **Build (Fase 4)**: inline docs que cuenten la historia del código
- **QA (Fase 5)**: test results como case studies, no solo pass/fail
- **Retro (Fase 6)**: postmortems narrativos, lessons learned como stories

## Referencia

- Constitución Evol-DD: Art. 4 (readabilidad, modularidad)
- Art. 7 (docs como parte del producto)
- Agentes relacionados: evol-doc (technical writing), evol-ux (user-centered docs), evol-architect (architecture docs)
- Michael Wolfe - "Writing on Medium": storytelling patterns
- Julie Zhuo - "The Making of a Manager": communication as storytelling
- Google Technical Writing Course: https://developers.google.com/tech-writing


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
