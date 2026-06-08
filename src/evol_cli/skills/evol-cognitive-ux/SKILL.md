---
name: evol-cognitive-ux
description: Cognitive UX: carga cognitiva, modelos mentales y diseño de comportamiento para crear interfaces intuitivas.
category: transfer
trigger: /cognitive-ux
---

# evol-cognitive-ux

## Cuándo Usar

Activar esta skill cuando se necesita optimizar la experiencia cognitiva del usuario:

- **Cognitive load**: reducir carga cognitiva, gestionar atención
- **Mental models**: alinear diseño con expectativas del usuario
- **Behavior design**: diseñar para que los usuarios hagan lo que queremos
- **Decision fatigue**: simplificar decisiones, reducir opciones
- **Memory limitations**: diseñar para olvido, no para memoria
- **Attention management**: capturar y mantener atención

**No usar para**: UX research general (usar evol-ux), usability testing (usar evol-qa), A/B testing (usar evol-growth-experiment).

## Conocimiento de Dominio

### Cognitive Load Theory
- **Intrinsic load**: complejidad inherente de la tarea
- **Extraneous load**: complejidad innecesaria del diseño
- **Germane load**: esfuerzo para aprender y internalizar
- **Goal**: minimizar extraneous, optimizar intrinsic, maximizar germane

### Mental Models
- **User expectations**: qué creen que pasará basado en experiencia previa
- **Conceptual models**: representación mental del sistema
- **Gulf of execution**: diferencia entre intención y acción
- **Gulf of evaluation**: diferencia entre sistema y comprensión

### Behavior Design
- **BJ Fogg model**: Behavior = Motivation + Ability + Trigger
- **Habit loop**: cue → routine → reward
- **Variable reward**: unpredictability mantiene engagement
- **Social proof**:其他人的行为 guía el nuestro
- **Loss aversion**: miedo a perder > deseo de ganar

### Decision Making
- **Choice overload**: demasiadas opciones paralizan
- **Default effect**: el default es lo que la mayoría elige
- **Anchoring**: primera información afecta decisiones posteriores
- **Satisficing vs. maximizing**: primero que funcione vs. la mejor opción

### Memory and Attention
- **Miller's Law**: 7±2 items in working memory
- **Serial position effect**: recuerdas primero y último
- **Change blindness**: no notas cambios graduales
- **Inattentional blindness**: no ves lo que no esperas

### Gestalt Principles
- **Proximity**: cosas cerca se perciben como grupo
- **Similarity**: cosas similares se perciben como grupo
- **Continuity**: percibimos líneas continuas, no segments
- **Closure**: completamos formas incompletas

## Flujo de Trabajo

1. **Audit cognitive load**: ¿Cuánto tiene que pensar el usuario?
2. **Map mental models**: ¿Qué espera el usuario? ¿Cómo cree que funciona?
3. **Identify decision points**: ¿Dónde el usuario tiene que decidir?
4. **Simplify choices**: reducir opciones, usar defaults, guiar decisión
5. **Align with mental models**: diseñar para que coincida con expectativas
6. **Reduce memory load**: mostrar info relevante, no depender de memoria
7. **Test with users**: observar dónde se confunden, dónde dudan
8. **Iterate**: mejorar basado en observación real

## Integración con Pipeline

- **Briefing (Fase 1)**: understand user mental models, decision points
- **Spec (Fase 2)**: document cognitive requirements, behavior goals
- **Plan (Fase 3)**: design for cognitive load, decision architecture
- **Build (Fase 4)**: implement with cognitive principles, behavior design
- **QA (Fase 5)**: test cognitive load, mental model alignment
- **Retro (Fase 6)**: analyze user behavior, identify cognitive improvements

## Referencia

- Constitución Evol-DD: Art. 5 (consultoría de dominio proactiva - user needs)
- Agentes relacionados: evol-ux (user experience), evol-growth-experiment (behavior design), evol-ethnography (user research)
- Don Norman - "The Design of Everyday Things": mental models, affordances
- Steve Krug - "Don't Make Me Think": cognitive simplicity
- BJ Fogg - "Tiny Habits": behavior design model
- Daniel Kahneman - "Thinking, Fast and Slow": cognitive biases
