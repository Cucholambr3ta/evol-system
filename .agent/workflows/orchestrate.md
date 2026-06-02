---
description: Multi-agent orchestration runtime (/orchestrate). Ejecuta composition_patterns del registry (sequential/parallel/parallel_then_sync).
---
# /orchestrate

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-ORCH | **Versión:** 1.0 | **Agente:** Architect (lead)
**Misión:** Coordinar varios agentes especializados según patterns predefinidos.

## 0. Pre-condición
```bash
test -f scripts/xdd-orchestrate.py
test -f prompts/agents/registry.json
```

## 1. Listar patterns disponibles
```bash
python3 scripts/xdd-orchestrate.py list
```

Patterns v0.1.0 (definidos en registry.json):
- **security_review** (sequential): code-reviewer → security-engineer → threat-detection-engineer
- **feature_squad** (parallel_then_sync): product-manager + backend-architect + ui-designer + test-analyzer → sync@spec_approval
- **release_train** (sequential): studio-producer → contract-testing → devops → docs

## 2. Dry-run
```bash
python3 scripts/xdd-orchestrate.py run --pattern=security_review --json
```
Muestra qué agents se invocarían y en qué orden. No ejecuta nada.

## 3. Execute (cuando hay confianza)
```bash
python3 scripts/xdd-orchestrate.py run --pattern=security_review --exec --json
```
Modo execute valida que los prompts existan. Las invocaciones LLM reales las
hace tu orquestador (Claude Code/OpenCode) cuando recibe la tool call vía
MCP server (Sprint 6).

## 4. Post-condición
- Cada step queda registrado en el report JSON
- Sprint 12+ integrará con eval-harness para gates entre steps

## Comandos auxiliares
- `/multi-plan` — placeholder (Sprint 12 wraps orchestrate run --pattern=feature_squad)
- `/multi-execute` — placeholder (Sprint 12)
- `/loop-start` / `/loop-status` — futuro (post v0.1.0)
