---
name: evol-idea-refine
description: Refinamiento de ideas brutas en conceptos accionables. Pipeline divergente→convergente en 3 fases (Expandir / Evaluar / Afilar). Produce one-pager Markdown con dirección recomendada y lista explícita de "No Hacemos". Inspirado en addyosmani/agent-skills idea-refine.
origin: evol-dd
inspired_by: addyosmani/agent-skills idea-refine (MIT, atribución en NOTICE)
when_to_use: Cuando una idea está en estado bruto y necesita claridad antes de spec. Complementa /brainstorm (divergente) con convergencia accionable. Trigger: "refina esta idea", "help me refine", "ideate on", "trabaja mi idea".
triggers:
  - "refina esta idea"
  - "help me refine"
  - "ideate on"
  - "trabaja mi idea"
  - "afina esto"
  - "desarrolla este concepto"
evals: evals/evol-idea-refine/
---

# evol-idea-refine

Skill de refinamiento de ideas: transforma conceptos vagos en propuestas
accionables con dirección clara, supuestos explícitos y trade-offs declarados.

## Filosofía

- "La simplicidad es la máxima sofisticación." — Steve Jobs
- Empieza con UX, trabaja hacia atrás hasta la tecnología.
- Dile no a 1,000 cosas. La lista "No Hacemos" es tan valiosa como la dirección.
- Sé honesto, no complaciente. Empuja hacia atrás en ideas débiles.

**Diferencia con `/brainstorm`:** `/brainstorm` es puramente divergente, genera
sin filtrar. `evol-idea-refine` cierra el loop: converge hacia una dirección
accionable y hace los trade-offs explícitos.

## Anti-patterns bloqueados

- No generar 20+ ideas superficiales. 5-8 consideradas > muchas shallow.
- No saltarse "¿para quién es esto?".
- No producir plan sin surfacear supuestos.
- No ser yes-machine. Empujar hacia atrás si la idea es débil.
- No ignorar restricciones del codebase (explorar con Glob/Grep/Read si aplica).

## Pipeline de 3 fases

---

### Fase 1 — Entender y Expandir (Divergente)

**1.1 Reformulación como "How Might We"**
Convierte la idea en un problema bien formulado:
> "¿Cómo podríamos [acción] para [persona] de manera que [resultado]?"

**1.2 Preguntas de enfoque (3-5 max)**
Hacer en orden, una a la vez:
1. ¿Para quién específicamente es esto? (persona concreta)
2. ¿Qué aspecto exitoso concreto y medible?
3. ¿Cuáles son las restricciones no negociables?
4. ¿Qué se ha intentado antes? ¿Por qué no funcionó?
5. ¿Por qué ahora y no antes?

**1.3 Variaciones (5-8 ideas)**
Explorar con lentes diferentes:

| Lente | Pregunta guía |
|-------|---------------|
| Inversión | ¿Qué pasa si hacemos lo opuesto? |
| Sin restricciones | ¿Cómo sería sin limitaciones técnicas/presupuesto? |
| Cambio de audiencia | ¿Y si es para un usuario completamente diferente? |
| Combinación | ¿Con qué otra herramienta/concepto se combina? |
| Simplificación | ¿Cuál es la versión más simple que funciona? |
| 10x | ¿Cómo sería si fuera 10 veces más impactante? |
| Experto | ¿Cómo lo haría [experto en el dominio]? |

Si hay codebase: explorar con Glob/Grep/Read antes de inventar.

---

### Fase 2 — Evaluar y Converger

**2.1 Clustering**
Agrupa las variaciones en 2-3 direcciones distintas (no 7 iguales con distinto nombre).

**2.2 Stress-test por dirección**

| Criterio | Pregunta |
|----------|---------|
| Valor usuario | ¿Painkiller o vitamina? ¿Cuánto dolor alivia? |
| Factibilidad | ¿Costo técnico y de recursos? ¿Qué dependencias? |
| Diferenciación | ¿Genuinamente diferente o variación de algo existente? |

**2.3 Supuestos ocultos (obligatorio)**
Para la dirección favorita:
- ¿Qué estamos apostando que es verdad?
- ¿Qué podría matar esto?
- ¿Qué estamos eligiendo ignorar conscientemente?

---

### Fase 3 — Afilar y Entregar

Produce un **one-pager Markdown** con estructura fija:

```markdown
# Idea Refinement — <título idea>
**Fecha:** <ISO date> | **Autor:** <context> | **Estado:** DRAFT

## Problema
<"How Might We" statement + 1 párrafo de contexto>

## Dirección recomendada
<qué hacemos y por qué esta dirección>

## Supuestos a validar
- [ ] <supuesto 1 — método de validación>
- [ ] <supuesto 2 — método de validación>
- [ ] <supuesto 3 — método de validación>

## MVP scope
<qué entra en la primera iteración — lo mínimo que valida la hipótesis>

## No hacemos (y por qué)
| Qué | Por qué no |
|-----|-----------|
| <feature tentador> | <trade-off explícito> |
| <otra cosa> | <razón honesta> |

## Próximos pasos
1. <acción concreta siguiente>
2. <quién valida qué supuesto>
```

**La lista "No Hacemos" es la parte más valiosa.** Trade-offs implícitos son deuda cognitiva.

## Almacenamiento opcional

Al finalizar, ofrecer guardar en:
```
docs/ideas/<idea-slug>.md
```

## Integración Evol-DD

- Invocada por `/ux-discovery` como paso de convergencia post-discovery.
- Invocada por `/brainstorm` al final de sesión divergente.
- Invocada por `/fase-requisitos` para refinar features antes de spec.
- Invocada por `/plan-fases` cuando hay ambigüedad en scope.

## Agentes que la usan

- `evol-pm` — refina features y prioridades de producto
- `evol-ux` — procesa feedback de usuarios en ideas refinadas
- `evol-architect` — convierte ideas en decisiones técnicas accionables

## Atribución
Concepto inspirado en [addyosmani/agent-skills idea-refine](https://github.com/addyosmani/agent-skills/tree/main/skills/idea-refine) (MIT).
Implementación nativa Evol-DD: pipeline 3 fases integrado al gated pipeline,
one-pager compatible con DOC_STANDARD.md, integración con /brainstorm y /ux-discovery.


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
