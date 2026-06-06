# Catalogo de Skills de Evol-DD

Este catalogo de skills representa la memoria procedal y de razonamiento de Evol-DD. Una skill es una capacidad especializada y reutilizable que los agentes y flujos del sistema pueden invocar para resolver tareas concretas.

## Indice de Categorias

- N/A
- Compression
- Context Engineering
- Documentation
- Growth
- Lifecycle
- Quality Gate
- Security

---

## Tabla General de Skills

| Nombre | Categoria | Trigger Principal | Descripcion |
|--------|-----------|-------------------|-------------|
| [agent-eval](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/agent-eval/SKILL.md) | quality-gate | `/eval` | Eval-harness para skills/agents/workflows Evol-DD. 4 grader types. Suite por skill. |
| [crear-agente](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-agente/SKILL.md) | lifecycle | `/crear-agente` |  |
| [crear-skill](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-skill/SKILL.md) | growth | `/crear-skill` | Crea nuevas skills para Evol-DD desde cero con loop iterativo de eval. Mejora skills existentes. Optimiza la descripcion del frontmatter para mejor triggering. Genera evals cuantitativos y cualitativos. Porta la skill a los 7 IDEs via evol-adapt.sh. Usar cuando el usuario quiera crear una skill nueva, mejorar una existente, testear una skill, o necesite que una capacidad este disponible como trigger en Claude Code, Cursor, Windsurf, OpenCode, Antigravity, |
| [evol-ai-review](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-ai-review/SKILL.md) | quality-gate | `/ai-review` | Quality gate review using AI for nuanced assessment. |
| [evol-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-compact/SKILL.md) | context-engineering | `/compact` | Provider-agnostic context compaction. Reduce tokens preserving semantics. |
| [evol-fact-check](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fact-check/SKILL.md) | N/A | `fact-check` | Verificación de claims y detección de desinformación con pipeline de 11 pasos (SIFT + CRAAP + MFS scoring). Produce Fact-Check Card con veredicto, score de manipulación y componente educativo. Inspirado en petar-nauka/fact-check-skill. |
| [evol-fs-context](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fs-context/SKILL.md) | context-engineering | `/fs-context` | Filesystem-paradigm context curation. Treat large data as files mounted by agents. |
| [evol-grill-me](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-grill-me/SKILL.md) | N/A | `grill me` | Interrogatorio implacable de planes y diseños hasta alcanzar comprensión compartida. Recorre cada rama del árbol de decisiones resolviendo dependencias una a una. Inspirado en mattpocock/skills grill-me (MIT). |
| [evol-idea-refine](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-idea-refine/SKILL.md) | N/A | `refina esta idea` | Refinamiento de ideas brutas en conceptos accionables. Pipeline divergente→convergente en 3 fases (Expandir / Evaluar / Afilar). Produce one-pager Markdown con dirección recomendada y lista explícita de "No Hacemos". Inspirado en addyosmani/agent-skills idea-refine. |
| [evol-prompt-master](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-prompt-master/SKILL.md) | N/A | `escribe un prompt para` | Generación de prompts optimizados para 30+ herramientas de IA. Extracción de intención en 9 dimensiones, routing por tool-specific conventions, reglas hard sobre cuándo NO agregar CoT. Complementa /mejorar-prompt (Evol-DD workflows) con soporte multi-modelo y agentic tools. Inspirado en nidhinjs/prompt-master. |
| [evol-sandbox](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-sandbox/SKILL.md) | security | `/sandbox` | Provider-agnostic sandbox skill. Backends E2B, Daytona, Microsandbox, local docker, none. |
| [evol-skill-manager](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-skill-manager/SKILL.md) | lifecycle | `/skill` | Lifecycle management for skills (install, update, rollback, validate). |
| [evol-talk-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-talk-compact/SKILL.md) | compression | `/compact-talk` | Compresion de output del orquestador Evol-DD. 3 niveles. Ahorro tokens ~50-75%. |
| [readme-master](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/readme-master/SKILL.md) | documentation | `/evol readme-master` | Crea, audita y actualiza archivos README.md utilizando la estructura y el nivel de diseño de los repositorios Top 100 de código abierto. Aplica técnicas de Storytelling (DX vs Open Source Ecosystem) y maquetación HTML avanzada (tablas, detalles colapsables, alineación). Activar antes de cualquier acción hacia develop o main, o al crear repositorios. |

---

## Detalle por Categoria

### N/A

- **[evol-fact-check](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fact-check/SKILL.md)**: Verificación de claims y detección de desinformación con pipeline de 11 pasos (SIFT + CRAAP + MFS scoring). Produce Fact-Check Card con veredicto, score de manipulación y componente educativo. Inspirado en petar-nauka/fact-check-skill.
- **[evol-grill-me](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-grill-me/SKILL.md)**: Interrogatorio implacable de planes y diseños hasta alcanzar comprensión compartida. Recorre cada rama del árbol de decisiones resolviendo dependencias una a una. Inspirado en mattpocock/skills grill-me (MIT).
- **[evol-idea-refine](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-idea-refine/SKILL.md)**: Refinamiento de ideas brutas en conceptos accionables. Pipeline divergente→convergente en 3 fases (Expandir / Evaluar / Afilar). Produce one-pager Markdown con dirección recomendada y lista explícita de "No Hacemos". Inspirado en addyosmani/agent-skills idea-refine.
- **[evol-prompt-master](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-prompt-master/SKILL.md)**: Generación de prompts optimizados para 30+ herramientas de IA. Extracción de intención en 9 dimensiones, routing por tool-specific conventions, reglas hard sobre cuándo NO agregar CoT. Complementa /mejorar-prompt (Evol-DD workflows) con soporte multi-modelo y agentic tools. Inspirado en nidhinjs/prompt-master.

### Compression

- **[evol-talk-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-talk-compact/SKILL.md)**: Compresion de output del orquestador Evol-DD. 3 niveles. Ahorro tokens ~50-75%.

### Context Engineering

- **[evol-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-compact/SKILL.md)**: Provider-agnostic context compaction. Reduce tokens preserving semantics.
- **[evol-fs-context](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fs-context/SKILL.md)**: Filesystem-paradigm context curation. Treat large data as files mounted by agents.

### Documentation

- **[readme-master](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/readme-master/SKILL.md)**: Crea, audita y actualiza archivos README.md utilizando la estructura y el nivel de diseño de los repositorios Top 100 de código abierto. Aplica técnicas de Storytelling (DX vs Open Source Ecosystem) y maquetación HTML avanzada (tablas, detalles colapsables, alineación). Activar antes de cualquier acción hacia develop o main, o al crear repositorios.

### Growth

- **[crear-skill](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-skill/SKILL.md)**: Crea nuevas skills para Evol-DD desde cero con loop iterativo de eval. Mejora skills existentes. Optimiza la descripcion del frontmatter para mejor triggering. Genera evals cuantitativos y cualitativos. Porta la skill a los 7 IDEs via evol-adapt.sh. Usar cuando el usuario quiera crear una skill nueva, mejorar una existente, testear una skill, o necesite que una capacidad este disponible como trigger en Claude Code, Cursor, Windsurf, OpenCode, Antigravity,

### Lifecycle

- **[crear-agente](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-agente/SKILL.md)**: 
- **[evol-skill-manager](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-skill-manager/SKILL.md)**: Lifecycle management for skills (install, update, rollback, validate).

### Quality Gate

- **[agent-eval](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/agent-eval/SKILL.md)**: Eval-harness para skills/agents/workflows Evol-DD. 4 grader types. Suite por skill.
- **[evol-ai-review](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-ai-review/SKILL.md)**: Quality gate review using AI for nuanced assessment.

### Security

- **[evol-sandbox](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-sandbox/SKILL.md)**: Provider-agnostic sandbox skill. Backends E2B, Daytona, Microsandbox, local docker, none.

