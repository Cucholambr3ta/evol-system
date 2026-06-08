---
name: evol-systems-design
description: Diseña interacciones agent-workflow aplicando principios de game design: feedback loops, sistemas de progresión, balance y mecánicas de engagement.
category: game-inspired
trigger: /systems-design
---

# evol-systems-design

## Cuándo Usar

Activar esta skill cuando se necesita diseñar o evaluar sistemas de interacción entre agentes y workflows:

- **Feedback loops**: loops de refuerzo positivo/negativo, emergence, unintended consequences
- **Sistemas de progresión**: niveles de agente, unlock de skills, progression trees
- **Balance de agentes**: capacidad vs. carga, distribución equitativa, evitar cuellos de botella
- **Mecánicas de engagement**: motivación intrínseca, variedad, sensación de progreso
- **Arquitectura de reglas**: constraints, boundaries, decision trees para agentes
- **Flow states**: diseñar para que los agentes mantengan flow (challenge = skill level)

**No usar para**: optimización de rendimiento técnico (usar evol-balance), documentación narrativa (usar evol-narrative-docs).

## Conocimiento de Dominio

### Feedback Loops
- **Positive feedback loops**: refuerzan comportamiento (más uso → más datos → mejor servicio → más uso)
- **Negative feedback loops**: estabilizan el sistema (load balancing, auto-scaling)
- **Delay loops**: efectos diferidos que causan oscilaciones (stock → demanda → stock)
- **Emergence**: comportamientos no diseñados que emergen de interacciones simples

### Progression Systems
- **Linear progression**: niveles 1→2→3, claro y predecible
- **Branching progression**: árbol de habilidades, choice matters
- **Prestige systems**: reset con beneficios, replayability
- **Unlock systems**: contenido que se desbloquea con achievement

### Balance
- **Power budget**: cada agente tiene un "presupuesto" de capacidad
- **Rock-paper-scissors**: agentes complementarios, no competidores
- **Diminishing returns**: más de lo mismo no siempre es mejor
- **Skill ceiling**: límite de cuánto puede mejorar un agente con práctica

### Engagement Mechanics
- **Intrinsic motivation**: mastery, autonomy, purpose (Daniel Pink)
- **Flow channel**: balance entre challenge y skill (Csikszentmihalyi)
- **Loss aversion**: miedo a perder es más fuerte que deseo de ganar
- **Variable reward**: unpredictability mantiene engagement (slot machine effect)

### Decision Architecture
- **Choice architecture**: cómo se presentan las opciones afecta la decisión
- **Default effects**: el default es lo que la mayoría elige
- **Nudge theory**: cambios sutiles que guían comportamiento
- **Choice overload**: demasiadas opciones paralizan

## Flujo de Trabajo

1. **Mapear el sistema actual**: ¿Qué agentes existen? ¿Cómo interactúan? ¿Qué loops existen?
2. **Identificar feedback loops**: positivos (refuerzo), negativos (estabilización), delay (oscilaciones)
3. **Diseñar progresión**: niveles, unlocks, progression trees para agentes
4. **Evaluar balance**: distribución de carga, power budget, complementariedad
5. **Definir mecánicas de engagement**: flow states, motivación, variedad
6. **Prototipar reglas**: decision trees, constraints, boundaries
7. **Simular comportamiento**: ejecutar el sistema y observar emergence
8. **Iterar basado en datos**: métricas de engagement, balance, unintended consequences

## Integración con Pipeline

- **Briefing (Fase 1)**: entender el sistema de agentes y sus objetivos
- **Spec (Fase 2)**: documentar arquitectura de reglas, feedback loops, progression
- **Plan (Fase 3)**: diseñar sistema de balance, métricas de engagement
- **Build (Fase 4)**: implementar reglas, progression, métricas de sistema
- **QA (Fase 5)**: testear balance, simular edge cases, medir engagement
- **Retro (Fase 6)**: analizar emergence, unintended consequences, iterar diseño

## Referencia

- Constitución Evol-DD: Art. 6 (orquestación multi-agente)
- Art. 2: pipeline con gates (feedback loops de control)
- Agentes relacionados: evol-orchestrator (composición), evol-balance (optimización), evol-pacing (timing)
- Jesse Schell - "The Art of Game Design": lenses para diseñar sistemas
- Will Wright - "SimCity": emergence en sistemas complejos
- Dan Cook - "Chemical Courage": game design patterns for emergent gameplay


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
