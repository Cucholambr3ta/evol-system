---
name: evol-grill-me
description: Interrogatorio implacable de planes y diseños hasta alcanzar comprensión compartida. Recorre cada rama del árbol de decisiones resolviendo dependencias una a una. Inspirado en mattpocock/skills grill-me (MIT).
origin: evol-dd
inspired_by: mattpocock/skills grill-me (MIT, atribución en NOTICE)
when_to_use: Cuando hay un plan, diseño o decisión técnica que necesita ser stress-testeado antes de comprometer recursos. Trigger: "grill me", "interrógate mi plan", "stress-test esto", "ponme a prueba".
triggers:
  - "grill me"
  - "interrógate mi plan"
  - "stress-test"
  - "ponme a prueba"
  - "cuestioname"
  - "drill me"
evals: evals/evol-grill-me/
---

# evol-grill-me

Skill de interrogatorio técnico implacable. Recorre el árbol de decisiones
de cualquier plan o diseño, rama por rama, hasta que no quedan supuestos
sin validar ni dependencias sin resolver.

## Filosofía

Un plan no interrogado es un riesgo oculto. Esta skill materializa el
principio de "Ambigüedad Cero" (Art. 1 Constitución Evol-DD) aplicado a
diseños y planes, no solo a specs.

**Diferencia con `/clarify`:** `/clarify` detecta ambigüedad en artefactos
existentes (SPEC, PLAN). `evol-grill-me` interroga activamente el razonamiento
detrás de decisiones, explorando ramas no escritas del árbol de decisiones.

## Activación

```
"grill me sobre [plan/diseño/decisión]"
"interrógate mi arquitectura"
"stress-test mi propuesta"
"ponme a prueba sobre [X]"
```

## Protocolo de interrogatorio

### Fase 1 — Mapeo del árbol
1. Identifica el plan/diseño objetivo.
2. Mapea las ramas principales de decisión (máx 5 por nivel).
3. Detecta dependencias entre ramas.
4. Si el contexto permite explorar el codebase, hazlo antes de preguntar.

### Fase 2 — Interrogatorio sistemático
Reglas estrictas:
- **Una pregunta a la vez.** Nunca bundle de preguntas.
- **Para cada pregunta:** provee tu respuesta recomendada antes de esperar la del usuario.
- **Resuelve dependencias en orden:** primero las ramas que desbloquean otras.
- **Explora codebase** si la respuesta puede derivarse de él (usa Read/Grep/Glob).
- **No aceptes "depende" sin especificar** de qué depende exactamente.

### Fase 3 — Síntesis
Al agotar el árbol de decisiones:
1. Lista supuestos validados vs supuestos aún en riesgo.
2. Identifica el camino crítico de dependencias.
3. Produce `GRILL_REPORT.md` si el usuario lo solicita.

## Estructura de preguntas

Para cada nodo del árbol de decisiones:

```
[Rama: <nombre>]
Pregunta: <pregunta específica y accionable>
Mi respuesta recomendada: <respuesta con razonamiento>
Tu respuesta: ?
```

## Áreas de interrogación estándar

| Área | Preguntas clave |
|------|----------------|
| **Supuestos** | ¿Qué asumimos que es verdad? ¿Qué pasa si es falso? |
| **Dependencias** | ¿Qué debe existir/pasar antes de que esto funcione? |
| **Casos borde** | ¿Qué pasa con X=0, X=null, concurrencia, fallo parcial? |
| **Escalabilidad** | ¿Funciona con 10x la carga esperada? ¿Y con 0.1x? |
| **Reversibilidad** | ¿Qué tan difícil es deshacer esta decisión? |
| **Alternativas** | ¿Por qué esta opción y no Y o Z? |
| **Métricas** | ¿Cómo sabemos que funcionó? ¿Qué mide el éxito? |

## Integración Evol-DD

- Invocada por `/clarify` cuando detecta plan sin stress-test.
- Invocada por `/brainstorm` antes de convergencia.
- Invocada por `/project-architecture-gsd` en fase de diseño.
- Invocada por `/plan-fases` antes de aprobación de plan.

## Agentes que la usan

- `evol-researcher` — interroga supuestos de investigación
- `evol-pm` — stress-test de features y prioridades
- `evol-architect` — valida decisiones arquitectónicas

## Output opcional

```bash
# Genera reporte formal post-interrogatorio
GRILL_REPORT.md:
  - Plan original
  - Árbol de decisiones explorado
  - Supuestos validados
  - Riesgos residuales
  - Decisiones finales tomadas
```

## Atribución
Concepto inspirado en [mattpocock/skills grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) (MIT).
Implementación nativa Evol-DD con integración al pipeline gated y árbol de decisiones explícito.
