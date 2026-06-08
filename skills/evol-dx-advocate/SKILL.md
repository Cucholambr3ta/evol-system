---
name: evol-dx-advocate
description: Developer experience advocate. Optimiza DX, construye comunidades y mejora el onboarding de developers.
category: transfer
trigger: /dx
---

# evol-dx-advocate

## Cuándo Usar

Activar esta skill cuando se necesita mejorar la experiencia de desarrollo:

- **DX optimization**: hacer que el framework/herramienta sea placer de usar
- **Community building**: crear y mantener comunidad de developers
- **Developer onboarding**: reducir time-to-first-contribution
- **API design**: APIs que sean intuitivas y hard de usar mal
- **Error messages**: errores claros, accionables, con links a docs
- **Tooling**: CLIs, IDEs, debuggers que faciliten el trabajo

**No usar para**: UX de usuarios finales (usar evol-ux), documentación técnica pura (usar evol-doc).

## Conocimiento de Dominio

### DX Principles
- **Delight over efficiency**: el developer debe disfrutar usándolo
- **Convention over configuration**: defaults sensibles, escape hatches cuando se necesite
- **Progressive complexity**: empezar simple, complejizar cuando se necesite
- **Fail fast, fail clear**: errores tempranos con mensajes claros

### Community Building
- **Contributing guide**: cómo contribuir, reglas claras
- **Code of conduct**: ambiente seguro y inclusivo
- **Issue templates**: facilitar reportes de bugs y features
- **PR templates**: checklist para PRs
- **Discussion forums**: GitHub Discussions, Discord, etc.
- **Office hours**: tiempo regular para preguntas y feedback

### Onboarding
- **Time to first commit**: métrica clave de DX
- **Quickstart guide**: de cero a funcionando en <5 min
- **Interactive tutorials**: learn by doing, no solo reading
- **Example projects**: starter templates, reference implementations
- **Sandbox environments**: playgrounds donde experimentar sin riesgo

### API Design
- **Consistency**: naming conventions, patterns consistentes
- **Discoverability**: APIs que se puedan descubrir IntelliSense
- **Minimal surprise**: el comportamiento debe ser predecible
- **Backward compatibility**: no romper contratos existentes
- **Good defaults**: configuración que funcione sin configurar

### Error Handling
- **Error messages as documentation**: cada error es una mini-doc
- **Actionable errors**: decir qué hacer, no solo qué pasó
- **Context in errors**: incluir relevant context (file, line, value)
- **Suggested fixes**: "Did you mean...?" patterns

## Flujo de Trabajo

1. **Evaluar DX actual**: time-to-first-commit, developer surveys, pain points
2. **Identificar friction points**: dónde los developers se frustran
3. **Mejorar onboarding**: quickstart, tutorials, examples
4. **Optimizar APIs**: consistencia, discoverability, error messages
5. **Construir comunidad**: contributing guide, templates, forums
6. **Crear tooling**: CLIs, generators, scaffolding
7. **Medir y iterar**: track DX metrics, collect feedback, improve
8. **Documentar DX patterns**: playbooks para futuro

## Integración con Pipeline

- **Briefing (Fase 1)**: entender audiencia de developers, sus pain points
- **Spec (Fase 2)**: documentar DX requirements, API design principles
- **Plan (Fase 3)**: planificar community building, onboarding materials
- **Build (Fase 4)**: implementar DX improvements, tooling, templates
- **QA (Fase 5)**: testear con developer real, medir time-to-first-contribution
- **Retro (Fase 6)**: analizar DX metrics, identificar próximas mejoras

## Referencia

- Constitución Evol-DD: Art. 4 (readabilidad, modularidad)
- Agentes relacionados: evol-ux (user experience), evol-doc (documentación), evol-builder (implementation)
- Kelsey Hightower - "Developer Experience" talks
- Abigail Sine - "Designing for Developer Experience"
- The DX Docs: https://thedocs.io


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
