# Especificacion de agent.template.md

Este template es la base de todos los agentes efimeros creados via `evol-agent-lifecycle.py`
o manualmente. Debe existir en `templates/agent.template.md`.

## Campos del frontmatter

| Campo | Requerido | Descripcion |
|-------|-----------|-------------|
| `name` | Si | Nombre legible del agente |
| `description` | Si | Una linea: que hace y cuando usarlo |
| `category` | Si | Siempre `ephemeral` para efimeros |
| `created_for_task` | Si (efimeros) | Descripcion de la tarea especifica |
| `expires_after_days` | Si (efimeros) | Dias hasta que el GC lo retire (default: 30) |
| `created_at` | Si (efimeros) | ISO8601 timestamp de creacion |
| `color` | No | Color para identificacion visual |
| `vibe` | No | Personalidad en una frase |

## Template completo

```markdown
---
name: {{agent_name}}
description: {{descripcion_una_linea}}
category: ephemeral
created_for_task: {{tarea_especifica}}
expires_after_days: {{dias}}
created_at: {{ISO8601}}
---

# {{agent_name}}

## Mision
{{descripcion_detallada_de_la_tarea_para_la_que_fue_creado}}

## Alcance
Lo que puede hacer:
- {{capacidad_1}}
- {{capacidad_2}}

Lo que NO puede hacer:
- No puede modificar archivos de gobernanza (constitucion, gate, hooks).
- No puede crear otros agentes efimeros.
- No puede aprobar sus propias propuestas (Art. 2 — aprobacion humana requerida).

## Contexto del proyecto
Referencias relevantes para esta tarea:
- Ver `memoria.md` para estado actual del proyecto.
- Ver `lecciones.md` seccion {{categoria_relevante}} para patrones aplicables.
- {{referencias_adicionales_si_aplica}}

## Como reportar
Al finalizar la tarea, actualizar `memoria.md` con:
- Que se hizo
- Decisiones tomadas y por que
- Que queda pendiente (si aplica)
```

## Campos del snapshot (retired)

Cuando el agente se retira via `evol-agent-lifecycle.py retire`, el snapshot JSON en
`.evol/agents/retired/<name>.json` incluye:

```json
{
  "name": "nombre-del-agente",
  "prompt": "<contenido completo del .md>",
  "prompt_sha256": "<sha256 del prompt para verificacion en recall>",
  "metadata": {
    "created_for_task": "...",
    "expires_after_days": 30,
    "created_at": "ISO8601",
    "retired_at": "ISO8601",
    "sessions_used": 3
  },
  "invocation_log": [
    {"timestamp": "ISO8601", "task": "descripcion de la invocacion"}
  ]
}
```
