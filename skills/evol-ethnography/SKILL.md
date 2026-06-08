---
name: evol-ethnography
description: Deep user research con métodos etnográficos. Observa patrones culturales, analiza comportamiento y descubre necesidades no articuladas.
category: transfer
trigger: /ethnography
---

# evol-ethnography

## Cuándo Usar

Activar esta skill cuando se necesita entender usuarios a nivel profundo:

- **Ethnographic observation**: observar usuarios en su contexto natural
- **Cultural patterns**: entender normas, valores, comportamientos culturales
- **Behavioral analysis**: lo que los usuarios hacen vs. lo que dicen
- **Unarticulated needs**: necesidades que los usuarios no saben expresar
- **Contextual inquiry**: entender trabajo/vida en contexto
- **Journey mapping**: mapear experiencias completas

**No usar para**: user interviews generales (usar evol-discovery), usability testing (usar evol-qa), A/B testing (usar evol-growth-experiment).

## Conocimiento de Dominio

### Ethnographic Methods
- **Participant observation**: observar participando
- **Contextual inquiry**: entrevistar en el contexto del usuario
- **Diary studies**: usuarios documentan su experiencia
- **Cultural probes**: artifacts que guían la auto-observación
- **Photo studies**: fotos como data de comportamiento

### Behavioral Analysis
- **Do-say gap**: diferencia entre lo que hacen y lo que dicen
- **Workarounds**: soluciones informales a problemas formales
- **Shadowing**: seguir al usuario en su día a día
- **Task analysis**: descomponer tareas en pasos detallados
- **Affinity diagramming**: agrupar observaciones en themes

### Cultural Patterns
- **Material culture**: objetos que revelan valores
- **Social practices**: rituales, rutinas, costumbres
- **Communication patterns**: cómo comunican, qué canal, qué tono
- **Power dynamics**: quién decide, quién influye, quién ejecuta

### Research Design
- **Research questions**: qué queremos descubrir
- **Sampling**: a quién observar, cuántos, dónde
- **Duration**: cuánto observar para capturar patrones
- **Ethics**: consentimiento, privacidad, anonimización
- **Triangulation**: múltiples fuentes para validar findings

### Synthesis
- **Affinity mapping**: agrupar observaciones en themes
- **Empathy maps**: qué piensan, sienten, dicen, hacen
- **Persona development**: arquetipos basados en data real
- **Journey mapping**: experiencia a lo largo del tiempo
- **Insight synthesis**: connecting dots entre observaciones

## Flujo de Trabajo

1. **Definir research questions**: qué queremos descubrir
2. **Diseñar study**: métodos, sampling, duración, ética
3. **Reclutar participantes**: representativos del target
4. **Conducir fieldwork**: observar, entrevistar, documentar
5. **Documentar observations**: notas, fotos, recordings, artifacts
6. **Sintetizar findings**: affinity mapping, pattern identification
7. **Crear deliverables**: personas, journey maps, insight reports
8. **Compartir learnings**: presentar a equipo, stakeholder, documentar

## Integración con Pipeline

- **Briefing (Fase 1)**: ethnographic insights informan el brief
- **Spec (Fase 2)**: user needs y behaviors informan specs
- **Plan (Fase 3)**: cultural patterns informan design decisions
- **Build (Fase 4)**: behavioral insights guían implementation
- **QA (Fase 5)**: validate against real user behavior
- **Retro (Fase 6)**: learnings para próximos proyectos

## Referencia

- Constitución Evol-DD: Art. 5 (consultoría de dominio proactiva - deep user understanding)
- Agentes relacionados: evol-ux (user experience), evol-discovery (user research), evol-cognitive-ux (cognitive patterns)
- Jeanette Blomberg - "Ethnographic Field Methods"
- Tony Salvador - "Ethnographic Praxis in Industry"
- IDEO: human-centered design methodology
- Nielsen Norman Group: UX research methods


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
