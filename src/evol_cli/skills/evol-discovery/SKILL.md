---
name: evol-discovery
description: User research con SPIN questioning, gap analysis y requirements gathering. Descubre qué necesita el usuario antes de construir.
category: transfer
trigger: /discovery
---

# evol-discovery

## Cuándo Usar

Activar esta skill cuando se necesita descubrir requisitos reales del usuario:

- **SPIN questioning**: Situation, Problem, Implication, Need-payoff questions
- **Gap analysis**: brecha entre estado actual y estado deseado
- **Requirements gathering**: elicitar requisitos funcionales y no funcionales
- **User interviews**: techniques para entrevistas efectivas
- **Observation**: watch users work, no solo what they say
- **Stakeholder mapping**: identificar quién decide, quién influye

**No usar para**: validación de soluciones (usar evol-ux), testing de usabilidad (usar evol-qa).

## Conocimiento de Dominio

### SPIN Questioning
- **Situation questions**: entender el contexto actual, facts
- **Problem questions**: discover pains, dissatisfactions, difficulties
- **Implication questions**: make problems feel urgent and important
- **Need-payoff questions**: help them see value of solving the problem

### Gap Analysis
- **Current state**: cómo funciona hoy (processes, tools, pain points)
- **Desired state**: cómo quiere funcionar (goals, aspirations)
- **Gap**: distance between current and desired
- **Root cause**: why the gap exists, not just symptoms

### Requirements Gathering
- **Functional requirements**: what the system should do
- **Non-functional requirements**: performance, security, scalability
- **Constraints**: budget, timeline, technology, regulations
- **Assumptions**: things we believe but haven't validated
- **Dependencies**: what we need from others

### Interview Techniques
- **Open-ended questions**: "Tell me about..." not "Do you like..."
- **Active listening**: reflect, paraphrase, ask follow-ups
- **Silence**: let them think, don't fill every pause
- **Probing**: "Why?" "Can you give an example?" "How often?"
- **Documenting**: take notes, record (with permission), transcribe

### Stakeholder Mapping
- **Decision makers**: who approves budget and scope
- **Influencers**: who shapes opinions of decision makers
- **Users**: who will actually use the solution
- **Blocked**: who needs to be consulted or informed
- **RACI matrix**: Responsible, Accountable, Consulted, Informed

## Flujo de Trabajo

1. **Identificar stakeholders**: who to talk to, who decides, who uses
2. **Preparar entrevistas**: research context, prepare questions
3. **Conducir entrevistas**: SPIN questioning, active listening, observation
4. **Analizar findings**: patterns, themes, root causes
5. **Mapear gaps**: current state → desired state → gap analysis
6. **Documentar requirements**: functional, non-functional, constraints
7. **Validar con stakeholders**: confirm understanding, resolve conflicts
8. **Entregar brief**: resumen ejecutivo con key findings and recommendations

## Integración con Pipeline

- **Briefing (Fase 1)**: discovery es el input principal del briefing
- **Spec (Fase 2)**: requirements se traducen en specs
- **Plan (Fase 3)**: constraints y dependencies informan el plan
- **Build (Fase 4)**: requirements son el source of truth
- **QA (Fase 5)**: validation contra requirements originales
- **Retro (Fase 6)**: evaluar si se cumplieron los objectives del discovery

## Referencia

- Constitución Evol-DD: Art. 5 (consultoría de dominio proactiva)
- Agentes relacionados: evol-ux (user experience), evol-domain (domain knowledge), evol-pm (requirements management)
- Neil Rackham - "SPIN Selling": the original SPIN framework
- Marty Cagan - "Inspired": product discovery techniques
- Teresa Torres - "Continuous Discovery Habits": ongoing discovery practices
