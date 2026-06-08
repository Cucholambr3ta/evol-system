---
name: crear-skill
description: >
  Crea nuevas skills para Evol-DD desde cero con loop iterativo de eval.
  Mejora skills existentes. Optimiza la descripcion del frontmatter para mejor
  triggering. Genera evals cuantitativos y cualitativos. Porta la skill a los 7
  IDEs via evol-adapt.sh. Usar cuando el usuario quiera crear una skill nueva,
  mejorar una existente, testear una skill, o necesite que una capacidad este
  disponible como trigger en Claude Code, Cursor, Windsurf, OpenCode, Antigravity,
  VSCode Copilot o Codex. Sinonimos: /crear-skill, crear skill, nueva skill,
  quiero una skill para, hazme una skill.
origin: evol-dd
category: growth
when_to_use:
  - Usuario quiere crear una skill nueva
  - Usuario quiere mejorar una skill existente
  - Usuario quiere testear una skill
  - Necesita una capacidad disponible como trigger en IDE
triggers:
  - /crear-skill
  - "crear skill"
  - "nueva skill"
  - "quiero una skill"
  - "hazme una skill"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
---

# crear-skill

## Proposito

Loop completo de creacion iterativa de skills con eval cuantitativo/cualitativo
y portabilidad a 7 IDEs. Patron inspirado en anthropics/skills/skill-creator (Apache-2.0).

El sistema no puede crecer sin este mecanismo. Cada proyecto puede generar skills
especificas que luego se comparten en el registry global.

## Uso

```
/crear-skill
```

El agente abre un workflow guiado con 8 pasos:

1. **Capturar intencion** — entrevista al usuario
2. **Estructura** — crea directorio `skills/<nombre>/`
3. **Draft** — escribe SKILL.md con frontmatter
4. **Casos de prueba** — genera 2-3 prompts realistas
5. **Loop eval** — runs paralelos with-skill vs baseline
6. **Optimizar description** — recall/precision >= 0.85
7. **Portar a 7 IDEs** — `bash scripts/evol-adapt.sh all`
8. **Registro** — actualiza catalogo + memoria.md

## Estructura de skill

```
skills/<nombre>/
├── SKILL.md              (requerido)
├── references/           (opcional)
├── scripts/              (opcional)
└── evals/                (si output es verificable)
    ├── evals.json
    └── cases.jsonl
```

## Formato SKILL.md

```yaml
---
name: nombre-kebab-case
description: > Descripcion que determina triggering
origin: evol-dd
category: context-engineering | quality-gate | security | compression | research | lifecycle | growth
when_to_use:
  - caso de uso 1
triggers:
  - /trigger-principal
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
---

# Nombre de la Skill

## Proposito

## Uso

## Referencias
```

## Principios

- Explicar el POR QUE, no solo el QUE
- Evitar SIEMPRE/NUNCA en mayusculas
- Mantener SKILL.md bajo 500 lineas
- Description "un poco agresiva" — mejor overtrigger que undertrigger

## CSO — Claude Search Optimization (description que dispara, no que resume)

La `description` del frontmatter es lo unico que el agente lee para decidir si
carga la skill. Optimizarla para **triggering**, no para resumir el workflow.

- Describe CONDICIONES de activacion ("usar cuando el usuario quiera X"), no el
  procedimiento interno. Si la description detalla el workflow, el agente puede
  seguir la description en vez de leer el SKILL.md completo.
- Tercera persona, orientada a gatillos. Incluir sinonimos y triggers naturales.
- Maximo util ~1024 caracteres; concision > exhaustividad.

Inspirado en obra/superpowers (writing-skills).

## RED-GREEN-REFACTOR (escribir skills es TDD aplicado a procesos)

Ninguna skill se da por buena sin un test que falle primero. El loop de eval
(paso 5) se formaliza asi:

1. **RED** — correr 2-3 escenarios de presion SIN la skill; documentar las
   racionalizaciones/errores exactos que comete el baseline.
2. **GREEN** — escribir la skill minima que resuelve esos fallos especificos.
3. **REFACTOR** — re-testear; identificar nuevas racionalizaciones; agregar
   contras explicitas; repetir hasta que sea a prueba de balas.

Inspirado en obra/superpowers (writing-skills): "no skill deploys without a
failing test first".

## Criterio de calidad

- Test primero (RED): baseline documentado antes de escribir la skill
- Benchmark iter-1: with-skill supera baseline en >= 30pp (GREEN)
- Description CSO: recall >= 0.85, precision >= 0.85 (condiciones, no workflow)
- 0 emojis en body, seccion `## Limites` presente

## Limites

- No crea agentes (usar `crear-agente` para eso)
- No modifica skills core del sistema
- No genera MCP servers
