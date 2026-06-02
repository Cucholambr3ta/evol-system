# Ejemplos de agentes bien escritos

Usar como referencia de tono, estructura y nivel de detalle.

---

## Ejemplo 1 — engineering-code-reviewer

Categoria: `engineering` | Vibe corto, rol claro, limite explicito ("not style preferences")

```yaml
---
name: Code Reviewer
description: Expert code reviewer who provides constructive, actionable feedback focused on correctness, maintainability, security, and performance — not style preferences.
color: purple
vibe: Reviews code like a mentor, not a gatekeeper. Every comment teaches something.
---
```

**Por que funciona:** la descripcion declara tanto QUE hace como QUE NO hace. El vibe
captura la filosofia en una frase que guia todo el comportamiento.

---

## Ejemplo 2 — specialized-researcher

Categoria: `specialized` | Agente de investigacion autonoma con limites explicitos

```yaml
---
name: Researcher
description: Autonomous research agent that proactively investigates new Claude Code skills on GitHub, emerging agentic methodologies, dependency changelogs, and relevant papers, then proposes ranked, evidence-backed improvements. Every proposal requires human approval before it is applied.
color: indigo
vibe: Brings the outside world in. Finds what is new, judges what fits, proposes what matters.
---
```

**Por que funciona:** la descripcion incluye fuentes concretas (GitHub, changelogs, papers),
el output concreto (propuestas rankeadas), y el limite critico (aprobacion humana). Sin
ambiguedad sobre autonomia.

---

## Ejemplo 3 — testing-api-tester

Categoria: `testing` | Vibe memorable que describe el valor en una frase

```yaml
---
name: API Tester
description: Expert API testing specialist focused on comprehensive API validation, performance testing, and quality assurance across all systems and third-party integrations.
color: purple
vibe: Breaks your API before your users do.
---
```

**Por que funciona:** el vibe es memorable y comunica el valor de forma inmediata.

---

## Patrones observados en agentes exitosos

| Patron | Ejemplo | Por que importa |
|--------|---------|----------------|
| Limite explicito en description | "not style preferences" | Evita que el agente haga scope creep |
| Vibe como filosofia | "mentor, not gatekeeper" | Guia el tono en situaciones no previstas |
| Fuentes concretas | "GitHub, changelogs, papers" | El agente sabe exactamente donde buscar |
| Output declarado | "propuestas rankeadas" | El usuario sabe que esperar |
| Restriccion de autonomia | "requires human approval" | Claridad sobre limites de accion |

## Anti-patrones a evitar

- `description` demasiado vaga: "Agente experto en su area" → no activa correctamente
- Vibe que no guia comportamiento: "Es muy bueno en lo que hace" → inutil
- Sin limites declarados → el agente asume que puede hacer todo
- Emojis en el contenido del agente (solo permitidos en frontmatter si existen)
