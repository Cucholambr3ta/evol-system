# BRIEFING — EDMS: Evol-DD Memory System

> **Objetivo:** Implementar un subsistema de memoria nativa para Evol-DD que permita recuperación híbrida (BM25 + Vector + Graph) con privacy stripping, consolidación en 4 tiers, y knowledge graph consultable via FlowScript.
> **Fecha:** 2026-06-06 | **Estado:** Fase 1 — Infraestructura

---

## 1. Problema actual

Evol-DD tiene memoria fragmentada:
- `evol-memory.py` (351 líneas, solo BM25 stdlib)
- `memoria.md` + `lecciones.md` en raíz del repo
- `acuerdos/memoria/*.md` (3 átomos)
- Sin búsqueda semántica, sin graph, sin consolidación automática

Resultado: el orquestador no puede hacer "por qué se tomó esta decisión" o "qué lecciones aplican a esta disciplina".

## 2. Solución propuesta

**ChromaDB** (vector) + **LadybugDB** (graph/relacional) embebidas en `~/.evol/memory/`, separación por metadata (no DB por proyecto). Fallback a BM25 stdlib si no están instaladas.

### Diferenciadores vs. soluciones existentes

| Feature | Mem0 | agentmemory | Letta | **EDMS** |
|---------|------|-------------|-------|----------|
| Privacy stripping | No | Básico | No | **Completo (11 patrones)** |
| Discipline-aware schema | No | No | No | **31 disciplinas** |
| Knowledge graph causal | No | No | Parcial | **FlowScript (6 queries)** |
| 4-tier consolidation | No | No | Parcial | **Raw→Compressed→Memory→Knowledge** |
| Local-first | Parcial | Sí | No | **Sí, zero cloud** |

## 3. Scope

### Incluido (Fase 1)
- ChromaDB + LadybugDB embebidas
- Privacy stripping (11 patrones regex)
- Metadata schema discipline-aware (31 disciplinas)
- BM25 fallback stdlib
- `evol_memory_store.py` (capa de abstracción)
- `evol-memory.py` extendido (+index, +search, +wake-up, +graph, +bootstrap)

### Incluido (Fase 2)
- RRF fusion (k=60) entre 3 streams
- Composite scoring (vector + recency + importance)
- 12 hooks de lifecycle
- 4-tier consolidation pipeline

### Futuro (no bloqueante)
- Bayesian surprise
- Session replay viewer
- Self-editing memory

## 4. Fuentes

24 repositorios analizados (OpenMemory, agentmemory, Letta/MemGPT, EM-LLM, FlowScript, cognee, mem0, ai-memory, Deja, Cortex, Secure Memory MCP, MemPalace, etc.). Ver `docs/plan-implementacion-edms.md` §18 para lista completa.
