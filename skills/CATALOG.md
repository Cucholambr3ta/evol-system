# Catalogo de Skills de Evol-DD

Este catalogo de skills representa la memoria procedal y de razonamiento de Evol-DD. Una skill es una capacidad especializada y reutilizable que los agentes y flujos del sistema pueden invocar para resolver tareas concretas.

## Indice de Categorias

- Context Engineering (Ingenieria de Contexto)
- Quality Gate (Puertas de Calidad)
- Growth (Crecimiento del Sistema)
- Compression (Compresion de Datos y Tokens)
- Security (Seguridad)
- Lifecycle (Ciclo de Vida)
- Research (Investigacion)
- Documentation (Documentacion)

---

## Tabla General de Skills

| Nombre | Categoria | Trigger Principal | Descripcion |
|--------|-----------|-------------------|-------------|
| [agent-eval](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/agent-eval/SKILL.md) | quality-gate | `/eval` | Eval-harness para skills/agents/workflows de Evol-DD. |
| [crear-agente](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-agente/SKILL.md) | growth | `/crear-agente` | Crea nuevos agentes permanentes o efimeros desde cero. |
| [crear-skill](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-skill/SKILL.md) | growth | `/crear-skill` | Crea nuevas skills desde cero con loop iterativo de evaluacion. |
| [evol-ai-review](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-ai-review/SKILL.md) | quality-gate | `/ai-review` | Calidad de codigo y evaluacion matizada mediante IA como juez. |
| [evol-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-compact/SKILL.md) | context-engineering | `/compact` | Compresion de contexto independiente del proveedor de LLM. |
| [evol-fact-check](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fact-check/SKILL.md) | research | `fact-check` | Pipeline de 11 pasos (SIFT + CRAAP + MFS) para verificar afirmaciones. |
| [evol-fs-context](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fs-context/SKILL.md) | context-engineering | `/fs-context` | Paradigma de sistema de archivos para manejar grandes volumenes de datos. |
| [evol-grill-me](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-grill-me/SKILL.md) | research | `grill me` | Interrogatorio tecnico exhaustivo y validacion de supuestos. |
| [evol-idea-refine](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-idea-refine/SKILL.md) | research | `refina esta idea` | Refinamiento divergente-convergente para convertir ideas en propuestas. |
| [evol-prompt-master](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-prompt-master/SKILL.md) | productivity | `escribe un prompt para` | Optimizacion de prompts para mas de 30 herramientas de IA externas. |
| [evol-sandbox](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-sandbox/SKILL.md) | security | `/sandbox` | Entornos de ejecucion aislados (E2B, Daytona, Docker, etc.). |
| [evol-skill-manager](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-skill-manager/SKILL.md) | lifecycle | `/skill` | Gestion del ciclo de vida de las skills (instalacion, rollbacks). |
| [evol-talk-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-talk-compact/SKILL.md) | compression | `/compact-talk` | Compresion y ahorro de tokens en la comunicacion del orquestador. |
| [readme-master](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/readme-master/SKILL.md) | documentation | `/evol readme-master` | Auditoria y creacion de README.md de alta calidad visual. |

---

## Detalle por Categoria

### Context Engineering

- **[evol-fs-context](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fs-context/SKILL.md)**: Evita saturar el contexto de la conversacion montando archivos extensos en memoria o procesandolos en streams de datos.
- **[evol-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-compact/SKILL.md)**: Aplica tecnicas sistematicas de reduccion de tokens de conversacion eliminando redundancias y compactando texto sin perder semantica.

### Quality Gate

- **[agent-eval](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/agent-eval/SKILL.md)**: Harness de evaluacion continua para asegurar el comportamiento correcto de agentes y flujos. Soporta grading estructural, conductual e IA.
- **[evol-ai-review](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-ai-review/SKILL.md)**: Evaluacion de alto nivel por parte de un LLM que actua como juez para auditar decisiones de diseño y codigo.

### Growth

- **[crear-agente](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-agente/SKILL.md)**: Agiliza la creacion de nuevos agentes core o efimeros, asegurando el cumplimiento de la estructura definida en prompts y su registro automatico.
- **[crear-skill](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/crear-skill/SKILL.md)**: Proporciona un loop completo de creacion, evaluacion contra benchmarks y distribucion de skills para multiples IDEs.

### Research

- **[evol-fact-check](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-fact-check/SKILL.md)**: Metodologia rigurosa para auditar claims y documentacion externa a fin de evitar la integracion de desinformacion.
- **[evol-grill-me](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-grill-me/SKILL.md)**: Stress-testing de planes y decisiones tecnicas que fuerza al agente a validar supuestos ocultos.
- **[evol-idea-refine](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-idea-refine/SKILL.md)**: Estructuracion de ideas abstractas en documentos "one-pager" claros con foco en que no hacer.

### Security

- **[evol-sandbox](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-sandbox/SKILL.md)**: Provisionamiento y ejecucion de comandos e implementaciones en entornos seguros y aislados para proteger la maquina anfitriona.

### Lifecycle

- **[evol-skill-manager](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-skill-manager/SKILL.md)**: Gestiona la instalacion, actualizacion, desinstalacion y rollback de skills dentro de la arquitectura del framework.

### Compression

- **[evol-talk-compact](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/evol-talk-compact/SKILL.md)**: Modulo especifico para compactar el output enviado a traves de logs y chats del orquestador central, optimizando costos.

### Documentation

- **[readme-master](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/readme-master/SKILL.md)**: Sincroniza la documentacion del proyecto principal y del framework con estandares visuales de la comunidad de codigo abierto.
