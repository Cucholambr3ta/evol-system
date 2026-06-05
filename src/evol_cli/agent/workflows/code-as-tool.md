---
name: code-as-tool
title: "/code-as-tool — Reduce N MCP tool calls a 1 code execution"
description: Pattern Code Execution with MCP. Wrap N tool calls homogéneos en 1 script (98%+ reducción tokens). Stdlib first, output JSON, idempotent.
phase: any
category: context-engineering
ssot: true
inputs:
  - Lista de N tool calls que serían independientes
outputs:
  - Script (Python/Bash/JS) que ejecuta los N calls + retorna summary structured
inspired_by: "ai-boost: Code Execution with MCP (98.7% token reduction)"
adr: docs/adr/0024-compaction-skill.md
trigger: /evol code-as-tool
---

# /code-as-tool — Reducir token overhead de N tool calls

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.

## Propósito

Cada MCP tool call gasta tokens en:
- Definition del tool (system prompt)
- Args serialization (JSON)
- Tool call event en transcript
- Tool result inline

Para N=10 calls similares, overhead es ~10x. Pattern: **un solo script** que ejecuta los N calls y retorna summary.

## Cuándo invocar

- Batch operations (analyze 50 files, query 10 endpoints, scan 100 PRs)
- ETL-style workflows
- Tasks con tool calls homogéneos en loop
- Cuando context budget warning aparece

## Procedimiento

### Anti-pattern (alto overhead)
```
Agent → MCP tool: read_file(file1) → 800 tokens result
Agent → MCP tool: read_file(file2) → 800 tokens result
... (50 veces)
→ 40k+ tokens en context post-batch
```

### Pattern (code-as-tool)
```python
# Agent escribe + ejecuta:
import os, json
results = []
for f in os.listdir("src/"):
    if f.endswith(".py"):
        with open(f"src/{f}") as fp:
            content = fp.read()
        # Solo guardamos summary, no full content
        results.append({
            "file": f,
            "lines": len(content.splitlines()),
            "has_todo": "TODO" in content,
        })
print(json.dumps({"total": len(results), "with_todos":
                  sum(1 for r in results if r["has_todo"])}))
```

→ 200 tokens en context (vs 40k). 99% reducción.

## Reglas

1. **Output structured.** Siempre JSON, nunca prose. Agent parsea fácil.
2. **No leaks.** Si script lee secrets, redact antes de print.
3. **Stdlib first.** Evitar deps que el sandbox no tenga.
4. **Idempotent.** Re-ejecución debe dar mismo resultado.
5. **Error handling.** Captura exceptions, retornar `{"errors": [...]}` no crash.

## Boundaries

- ❌ NO usar para tool calls con side effects que requieren confirmación humana entre cada uno (deploy, transfer, etc.)
- ❌ NO usar si la lógica de cada call depende del result del previo de forma compleja (usar sequential entonces)
- ✅ SÍ usar para read-only batch
- ✅ SÍ usar para ETL/análisis
- ✅ SÍ usar para "summarize N items"

## Output expected

Script ejecutable + `STDOUT JSON` con summary. Agent puede pedir scripts adicionales para drill-down si necesario.

## Referencias
- [ADR-0023 Context budget policy](../../docs/adr/0023-context-budget-policy.md)
- [skills/evol-fs-context](../../skills/evol-fs-context/SKILL.md)
- Code Execution with MCP pattern: ai-boost/awesome-harness-engineering
