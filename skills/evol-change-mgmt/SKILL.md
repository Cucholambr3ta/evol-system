---
name: evol-change-mgmt
description: Gestión del cambio tecnológico y adopción. Aplica ADKAR/Kotter, alineación de stakeholders y estrategias de adopción.
category: transfer
trigger: /change-mgmt
---

# evol-change-mgmt

## Cuándo Usar

Activar esta skill cuando se necesita gestionar el cambio tecnológico:

- **Technology adoption**: adoptar nuevas herramientas, frameworks, procesos
- **Stakeholder alignment**: alinear a todos los stakeholders en el cambio
- **Resistance management**: manejar resistencia al cambio
- **Communication planning**: comunicar el cambio efectivamente
- **Training and enablement**: capacitar al equipo para el cambio
- **Cultural change**: cambiar la cultura organizacional

**No usar para**: gestión de proyectos (usar evol-pm), governance de código (usar evol-governance).

## Conocimiento de Dominio

### ADKAR Model
- **Awareness**: entender por qué el cambio es necesario
- **Desire**: querer participar y apoyar el cambio
- **Knowledge**: saber cómo cambiar
- **Ability**: poder implementar el cambio
- **Reinforcement**: mantener el cambio, recaer

### Kotter's 8 Steps
1. **Create urgency**: make the case for change
2. **Form powerful coalition**: build a guiding coalition
3. **Create vision**: develop a clear vision
4. **Communicate vision**: communicate the vision widely
5. **Empower action**: remove obstacles, enable risk-taking
6. **Create quick wins**: plan for visible, short-term wins
7. **Build on gains**: use credibility from wins to tackle bigger changes
8. **Anchor in culture**: make change stick in organizational culture

### Resistance Management
- **Identify resistance**: who resists, why, how strongly
- **Root causes**: fear, lack of understanding, past failures, loss of control
- **Strategies**: education, involvement, facilitation, negotiation, coercion
- **Engage resistors**: listen, understand, address concerns
- **Champions**: empower early adopters to influence others

### Communication Planning
- **Audience segmentation**: different messages for different groups
- **Channel selection**: email, meetings, Slack, workshops
- **Timing**: when to communicate, how often
- **Feedback loops**: two-way communication, questions, concerns
- **Transparency**: be honest about what's changing and why

### Adoption Strategies
- **Pilot programs**: test with small group before broad rollout
- **Training**: workshops, documentation, pair programming
- **Incentives**: rewards for adoption, recognition
- **Gamification**: make adoption engaging and fun
- **Support**: dedicated help during transition period

## Flujo de Trabajo

1. **Assess readiness**: how ready is the organization for change?
2. **Identify stakeholders**: who will be affected, who decides, who influences
3. **Build case for change**: urgency, business case, vision
4. **Develop communication plan**: messages, channels, timing
5. **Address resistance**: identify, understand, mitigate
6. **Execute change**: pilot, train, rollout, support
7. **Monitor adoption**: track usage, gather feedback, adjust
8. **Reinforce**: celebrate wins, anchor in culture, prevent backsliding

## Integración con Pipeline

- **Briefing (Fase 1)**: understand change context, stakeholder landscape
- **Spec (Fase 2)**: document adoption requirements, training needs
- **Plan (Fase 3)**: develop change management plan, communication strategy
- **Build (Fase 4)**: implement with adoption in mind, pilot early
- **QA (Fase 5)**: test adoption with real users, gather feedback
- **Retro (Fase 6)**: evaluate adoption success, lessons for next change

## Referencia
- Constitución Evol-DD: Art. 6 (multi-agent coordination - human change)
- Agentes relacionados: evol-pm (project management), evol-ux (user adoption), evol-team-dynamics (team culture)
- Prosci ADKAR Model: https://www.prosci.com/methodology/adkar
- John Kotter - "Leading Change": the 8-step process
- Everett Rogers - "Diffusion of Innovations": adoption lifecycle
- William Bridges - "Managing Transitions": people side of change


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
