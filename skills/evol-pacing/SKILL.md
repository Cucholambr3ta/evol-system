---
name: evol-pacing
description: Controla el timing del pipeline Evol-DD aplicando teoría de pacing, diseño de momentos y ciclos de tensión/resolución.
category: game-inspired
trigger: /pacing
---

# evol-pacing

## Cuándo Usar

Activar esta skill cuando se necesita ajustar el ritmo y timing del pipeline:

- **Pipeline pacing**: ritmo de avance entre fases, cuándo acelerar vs. pausar
- **Moment design**: crear momentos de impacto (breakthroughs, reveals, decisiciones críticas)
- **Tension/resolution**: ciclos de presión y alivio para mantener energía
- **Deadline management**: timing de sprints, releases, milestones
- **Energy management**: distribuir esfuerzo a lo largo del tiempo, evitar burnout
- **Rhythm and flow**: establecer ritmo sostenible de trabajo

**No usar para**: diseño de sistemas de interacción (usar evol-systems-design), optimización de carga (usar evol-balance).

## Conocimiento de Dominio

### Pacing Theory
- **Pacing = ritmo de revelación de información y progress**: no es solo velocidad, es cuándo mostrar qué
- **Slow burn vs. sprint**: momentos de profundidad vs. momentos de velocidad
- **Breathing room**: el espacio entre momentos intensos es tan importante como los momentos mismos
- **Temporal landmarks**: hitos temporales que dan estructura al tiempo

### Moment Design
- **Peak-end rule**: las personas recuerdan el pico emocional y el final, no el promedio
- **Surprise and delight**: momentos inesperados que generan engagement
- **Anticipation**: la anticipación del evento es parte de la experiencia
- **Payoff**: cada setup necesita un payoff, cada promesa necesita cumplimiento

### Tension/Resolution
- **Tension building**: subir la presión gradualmente (deadlines, scope, complejidad)
- **Catharsis**: momento de liberación después de tensión (release, deployment, success)
- **False resolution**: resolución aparente que introduce nueva tensión (scope creep)
- **Sustainable tension**: tensión que motiva sin agotar

### Timing Patterns
- **Pomodoro-like**: ciclos de 25 min trabajo / 5 min descanso
- **Sprint cadence**: 1-2 weeks sprints con retrospective
- **Release cadence**: quarterly releases vs. continuous delivery
- **Seasonal patterns**: productividad varía por día, semana, mes, estación

### Energy Management
- **Ultradian rhythms**: ciclos de 90-120 min de alta energía
- **Decision fatigue**: menos decisiones = mejor calidad de decisiones
- **Context switching cost**: cambiar de tarea tiene costo real
- **Deep work**: bloques de tiempo sin interrupciones para trabajo complejo

## Flujo de Trabajo

1. **Evaluar ritmo actual**: ¿Cómo fluye el pipeline? ¿Dónde hay cuellos de botella?
2. **Identificar momentos clave**: ¿Qué decisiones/entregables son más impactantes?
3. **Diseñar ciclos de tensión**: crear urgencia sin burnout, presión sin agotamiento
4. **Planificar breathing room**: pausas estratégicas entre momentos intensos
5. **Establecer ritmos**: sprint cadence, release cadence, daily rhythms
6. **Monitorear energía**: trackear burnout signs, ajustar ritmo según carga
7. **Crear momentos de payoff**: celebrar logros, marcar hitos, dar closure
8. **Iterar basado en feedback**: ajustar pacing según team energy y velocity

## Integración con Pipeline

- **Briefing (Fase 1)**: establecer ritmo esperado del proyecto, milestones
- **Spec (Fase 2)**: definir momentos críticos de diseño, decisiones clave
- **Plan (Fase 3)**: distribuir esfuerzo a lo largo del tiempo, planificar pausas
- **Build (Fase 4)**: mantener ritmo sostenible, crear momentos de breakthrough
- **QA (Fase 5)**: timing de testing, windows de release, go/no-go decisions
- **Retro (Fase 6)**: evaluar pacing del sprint, ajustar para próximo ciclo

## Referencia

- Constitución Evol-DD: Art. 2 (pipeline con gates - timing de aprobaciones)
- Art. 9: pipeline de 6 fases (ritmo de progreso)
- Agentes relacionados: evol-pm (timing de sprints), evol-release (cadencia de releases), evol-systems-design (diseño de sistemas)
- Jesse Schell - "The Art of Game Design": pacing lenses
- Mihaly Csikszentmihalyi - "Flow": optimal experience requires balance
- Cal Newport - "Deep Work": rhythms for sustained focus


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
