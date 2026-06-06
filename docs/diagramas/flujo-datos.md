# Flujo de datos — Evol-DD

Diagramas de secuencia para los cuatro flujos principales del sistema.

## Flujo 1: Bootstrap de proyecto nuevo

```mermaid
sequenceDiagram
    actor Usuario
    participant Init as evol-init.sh
    participant Manifests as manifests/
    participant FS as Filesystem proyecto
    participant Gate as evol-gate.py
    participant State as ~/.evol/state.db

    Usuario->>Init: evol init /proyecto --profile core
    Init->>Manifests: leer install-profiles.json
    Manifests-->>Init: modulos del perfil core
    Init->>Manifests: leer install-modules.json
    Manifests-->>Init: rutas de componentes por modulo
    Init->>FS: crear .evol/ (0700)
    Init->>Gate: init (generar .gate-key)
    Gate->>FS: escribir .evol/.gate-key (0600)
    Gate->>FS: escribir .evol/.gate-log.jsonl (genesis hash)
    Gate-->>Init: gate inicializado
    Init->>FS: copiar templates/ al proyecto
    Init->>FS: crear prompts/agents/core/ (18 agentes)
    Init->>FS: crear skills/ (segun perfil)
    Init->>FS: crear .agent/workflows/ y hooks/
    Init->>FS: crear AGENT_MEMORY.md desde template
    Init->>FS: crear memoria.md y lecciones.md
    Init->>State: init_db() — crear tablas si no existen
    State-->>Init: schema listo
    Init-->>Usuario: proyecto inicializado con perfil core
```

## Flujo 2: Sesion de trabajo con memoria activa

```mermaid
sequenceDiagram
    participant Hook as SessionStart Hook
    participant Memory as evol-memory.py
    participant AgentMem as AGENT_MEMORY.md
    participant Journal as memory/YYYY-MM-DD.md
    participant Dialog as memory/dialog/
    participant LLM as evol-provider.py
    actor Agente as Agente / Claude Code
    participant StopHook as Stop Hook

    Hook->>Memory: load
    Memory->>AgentMem: leer hechos long-term
    AgentMem-->>Memory: contenido long-term
    Memory->>Journal: buscar journal de ayer
    Journal-->>Memory: resumen sesion anterior (si existe)
    Memory->>Dialog: verificar historial reciente
    Dialog-->>Memory: mensajes previos (si existen)
    Memory->>Agente: imprimir contexto cargado (=== Memory Load ===)

    Agente->>Agente: ejecuta tarea (multiples turnos)

    Agente->>StopHook: sesion terminada
    StopHook->>Memory: summarize(messages_file)
    Memory->>LLM: resumir sesion si hay mensajes
    LLM-->>Memory: resumen estructurado
    Memory->>Journal: escribir entrada YYYY-MM-DD.md
    Memory->>AgentMem: actualizar hechos facticos si cambiaron
    Memory->>Dialog: limpiar entradas con TTL expirado (EVOL_MEMORY_TOOL_TTL_DAYS)
    Memory-->>StopHook: persistencia completada
```

## Flujo 3: Ciclo de vida de agente efimero

```mermaid
sequenceDiagram
    actor Usuario
    participant Factory as evol-agent-factory (agente core)
    participant Lifecycle as evol-agent-lifecycle.py
    participant Template as templates/agent.template.md
    participant Registry as prompts/agents/registry.json
    participant EphDir as prompts/agents/ephemeral/
    participant State as evol-state.py

    Usuario->>Factory: solicitar agente especializado para tarea X
    Factory->>Lifecycle: create --name X --task "descripcion" --expires 30
    Lifecycle->>Template: leer agent.template.md
    Template-->>Lifecycle: contenido plantilla
    Lifecycle->>Lifecycle: sustituir variables (name, task, expires, sha256)
    Lifecycle->>EphDir: escribir YYYYMMDDHHMMSS-X.md
    Lifecycle->>Registry: registrar {id, name, category:ephemeral, prompt_file}
    Registry-->>Lifecycle: confirmacion
    Lifecycle->>State: registrar sesion de creacion
    Lifecycle-->>Factory: agente creado en {filepath}
    Factory-->>Usuario: agente disponible como {id}

    note over Usuario,State: ... agente trabaja durante su TTL de 30 dias ...

    Usuario->>Lifecycle: prune (limpiar expirados)
    Lifecycle->>Registry: leer todos los agentes ephemeral
    Registry-->>Lifecycle: lista con created_at y expires_after_days
    Lifecycle->>Lifecycle: calcular expirados (created_at + TTL < hoy)
    Lifecycle->>EphDir: mover archivos expirados a .evol/agents/retired/
    Lifecycle->>Registry: eliminar entradas expiradas
    Lifecycle-->>Usuario: N agentes retirados, registry actualizado
```

## Flujo 4: Creacion de skill nueva (/crear-skill)

```mermaid
sequenceDiagram
    actor Usuario
    participant Skill as crear-skill workflow
    participant Entrevista as Entrevista interactiva
    participant SkillDir as skills/<nombre>/
    participant EvalDir as evals/<nombre>/
    participant Evolve as evol-evolve.py
    participant Adapt as evol-adapt.sh
    participant State as ~/.evol/state.db

    Usuario->>Skill: /crear-skill
    Skill->>Entrevista: preguntar intencion y casos de uso
    Entrevista-->>Usuario: que capacidad necesitas?
    Usuario-->>Entrevista: descripcion del objetivo
    Entrevista->>Usuario: cuales son los triggers naturales?
    Usuario-->>Entrevista: sinonimos y frases trigger
    Entrevista->>Usuario: con que IDEs debe ser compatible?
    Usuario-->>Entrevista: lista de IDEs (claude-code, cursor, etc.)

    Skill->>SkillDir: crear skills/<nombre>/SKILL.md (frontmatter + body)
    Skill->>SkillDir: crear skills/<nombre>/hooks/ (SessionStart, Stop si aplica)
    Skill->>SkillDir: crear skills/<nombre>/workflows/ (flujos declarativos)
    Skill->>EvalDir: crear evals/<nombre>/cases.jsonl (casos de prueba)
    Skill->>EvalDir: crear evals/<nombre>/grader.yaml (criterios)

    Skill->>Evolve: evol-evolve.py --dry-run (verificar coherencia)
    Evolve->>State: leer instincts relacionados
    State-->>Evolve: patrones similares (si existen)
    Evolve-->>Skill: reporte de coherencia

    Skill->>Adapt: evol-adapt.sh (portar a 7 IDEs)
    Adapt->>SkillDir: generar symlinks y configs por IDE
    Adapt-->>Skill: skill disponible en claude-code, cursor, windsurf, opencode, vscode-copilot, antigravity, codex

    Skill->>State: registrar instinct de nueva skill (confidence 0.5)
    Skill-->>Usuario: skill <nombre> lista y registrada en skills/
```
