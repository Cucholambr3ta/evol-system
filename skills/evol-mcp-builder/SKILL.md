---
name: evol-mcp-builder
description: Construye herramientas de integración para agentes using MCP protocol. Diseña tools, patterns de integración y arquitectura de agentes.
category: transfer
trigger: /mcp-builder
---

# evol-mcp-builder

## Cuándo Usar

Activar esta skill cuando se necesita construir o integrar herramientas para agentes:

- **MCP protocol**: Model Context Protocol, tool definitions, resource exposure
- **Tool design**: diseñar tools que sean useful, composable, safe
- **Agent integration**: conectar agentes con external systems
- **Resource management**: exposición de archivos, databases, APIs como resources
- **Security**: sandboxing, permission models, rate limiting
- **Testing**: testear tools y agent integrations

**No usar para**: arquitectura de agentes Evol-DD (usar evol-architect), optimización de rendimiento (usar evol-balance).

## Conocimiento de Dominio

### MCP Protocol
- **Tools**: funciones que el LLM puede llamar (name, description, parameters, handler)
- **Resources**: datos que el LLM puede leer (files, DB records, API responses)
- **Prompts**: templates de prompts que el LLM puede usar
- **Sampling**: permitir al LLM solicitar completions a otros modelos

### Tool Design
- **Single responsibility**: cada tool hace una cosa bien
- **Clear naming**: nombres descriptivos, no abbreviations
- **Comprehensive description**: qué hace, cuándo usarla, qué devuelve
- **Parameter validation**: schemas claros, defaults sensatos
- **Error handling**: errores informativos, no stack traces
- **Idempotency**: same input = same output, safe to retry

### Agent Integration Patterns
- **Tool composition**: combinar tools para workflows complejos
- **Resource mounting**: exponer datos como resources
- **Prompt templates**: prompts reutilizables con variables
- **Middleware**: logging, auth, rate limiting entre tool y handler
- **Caching**: cache results para tools expensive

### Security
- **Sandboxing**: limitar qué puede hacer cada tool
- **Permission model**: ACLs por tool, por resource
- **Input validation**: sanitizar todo input antes de usar
- **Rate limiting**: prevenir abuse
- **Audit logging**: track qué tools se usan y cómo
- **Secret management**: nunca exponer secrets en tool outputs

### Testing
- **Unit tests**: testear handlers con mocks
- **Integration tests**: testear tools con real backends
- **Contract tests**: verify tool schema matches implementation
- **E2E tests**: testear full agent + tool flow
- **Chaos testing**: testear con failures y edge cases

## Flujo de Trabajo

1. **Identificar necesidad**: ¿Qué tool se necesita? ¿Qué problem resuelve?
2. **Diseñar tool schema**: name, description, parameters, return type
3. **Implementar handler**: lógica del tool, validación, error handling
4. **Exponer via MCP**: register tool, define resources, setup server
5. **Segurar**: sandboxing, permissions, input validation
6. **Testear**: unit, integration, contract, E2E tests
7. **Documentar**: usage examples, error cases, limitations
8. **Iterar**: collect feedback, improve based on actual usage

## Integración con Pipeline

- **Briefing (Fase 1)**: identificar qué tools se necesitan para el proyecto
- **Spec (Fase 2)**: documentar tool schemas, security requirements
- **Plan (Fase 3)**: estimar esfuerzo de implementación, dependencias
- **Build (Fase 4)**: implementar tools con TDD, testing completo
- **QA (Fase 5)**: testear tools, integration, security
- **Retro (Fase 6)**: analizar uso de tools, identificar mejoras

## Referencia

- Constitución Evol-DD: Art. 6 (orquestación multi-agente)
- Agentes relacionados: evol-architect (arquitectura), evol-devops (deployment), evol-sec (security)
- MCP Specification: https://spec.modelcontextprotocol.io
- Anthropic MCP Documentation: https://docs.anthropic.com/en/docs/agents-and-tools/mcp
- Tool Design Patterns: https://github.com/modelcontextprotocol


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
