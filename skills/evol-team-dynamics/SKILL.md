---
name: evol-team-dynamics
description: Dinámica de equipos y rendimiento colaborativo. Analiza patrones de colaboración, diseñar cultura y optimizar trabajo en equipo.
category: transfer
trigger: /team-dynamics
---

# evol-team-dynamics

## Cuándo Usar

Activar esta skill cuando se necesita mejorar el rendimiento del equipo:

- **Team dynamics**: entender cómo trabaja el equipo, qué funciona, qué no
- **Collaboration patterns**: patrones de comunicación,.review, pairing
- **Culture engineering**: diseñar la cultura del equipo intencionalmente
- **Conflict resolution**: manejar desacuerdos constructivamente
- **Psychological safety**: crear ambiente donde sea seguro take risks
- **Team health**: medir y mejorar la salud del equipo

**No usar para**: gestión de proyectos (usar evol-pm), gestión del cambio (usar evol-change-mgmt), orquestación de agentes (usar evol-orchestrator).

## Conocimiento de Dominio

### Team Dynamics
- **Tuckman model**: forming → storming → norming → performing
- **Lencioni's 5 dysfunctions**: absence of trust, fear of conflict, lack of commitment, avoidance of accountability, inattention to results
- **Psychological safety**: Amy Edmondson's research on safe teams
- **Dunbar's number**: cognitive limits on team size (5, 15, 50, 150)

### Collaboration Patterns
- **Pair programming**: two people, one code, real-time review
- **Mob programming**: whole team, one code, collective ownership
- **Code review**: asynchronous quality and knowledge sharing
- **Architecture Decision Records**: document decisions for future reference
- **Tech talks**: knowledge sharing sessions

### Culture Engineering
- **Values definition**: what we believe and how we behave
- **Norms**: unwritten rules that govern behavior
- **Rituals**: recurring practices that reinforce culture
- **Stories**: narratives that embody culture
- **Artifacts**: visible manifestations of culture

### Conflict Resolution
- **Interest-based resolution**: focus on interests, not positions
- **Thomas-Kilmann modes**: competing, collaborating, compromising, avoiding, accommodating
- **Nonviolent communication**: observations, feelings, needs, requests
- **Mediation**: neutral third party facilitates resolution

### Psychological Safety
- **Speak up**: team members feel safe to voice opinions
- **Take risks**: safe to try new things and fail
- **Ask questions**: safe to say "I don't know"
- **Challenge authority**: safe to disagree with leadership
- **Admit mistakes**: safe to own failures

### Team Health Metrics
- **eNPS**: employee Net Promoter Score
- **Engagement surveys**: regular pulse checks
- **Velocity stability**: consistent delivery over time
- **Defect rates**: quality as team health indicator
- **Turnover**: people leaving as signal of problems

## Flujo de Trabajo

1. **Assess current state**: how does the team work today?
2. **Identify dynamics**: what patterns exist? what works? what doesn't?
3. **Measure health**: surveys, metrics, observation
4. **Identify improvements**: where to focus for maximum impact
5. **Design interventions**: specific actions to improve dynamics
6. **Implement changes**: pilot, measure, iterate
7. **Build psychological safety**: trust, respect, openness
8. **Sustain improvements**: rituals, norms, continuous feedback

## Integración con Pipeline

- **Briefing (Fase 1)**: understand team context, dynamics, constraints
- **Spec (Fase 2)**: document team requirements, collaboration needs
- **Plan (Fase 3)**: design team structure, communication patterns
- **Build (Fase 4)**: implement collaboration practices, tools
- **QA (Fase 5)**: verify team dynamics support quality delivery
- **Retro (Fase 6)**: team retrospective as continuous improvement

## Referencia

- Constitución Evol-DD: Art. 6 (multi-agent coordination parallels human teams)
- Agentes relacionados: evol-pm (project management), evol-change-mgmt (change adoption), evol-ux (user-centered team)
- Amy Edmondson - "The Fearless Organization": psychological safety
- Patrick Lencioni - "The Five Dysfunctions of a Team"
- Bruce Tuckman - "Developmental Sequence in Small Groups"
- Netflix Culture Deck: culture of freedom and responsibility
- Google Project Aristotle: psychological safety as #1 factor


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
