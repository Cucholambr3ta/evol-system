---
name: brainstorm
title: "/brainstorm — Exploración divergente sin convergencia forzada"
description: Genera muchas ideas sin filtrar para exploración inicial (problem space, root cause). Invoca party mode (Sprint 17). Inspirado en BMAD /brainstorm.
phase: briefing
category: planning
ssot: true
inputs:
  - Problema o pregunta abierta
  - Opcional: contexto previo (DISCOVERY.md, SPEC.md draft)
outputs:
  - BRAINSTORM_<timestamp>.md con ideas categorizadas
inspired_by: BMAD /brainstorm (NOASSERT)
adr: docs/adr/0017-web-bundles-distribution.md
trigger: /evol brainstorm
---

# /brainstorm — Exploración divergente

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.

## Propósito
Generar **muchas ideas sin filtrar** sobre un problema abierto. Optimizado para fase exploratoria (Briefing) cuando todavía no hay SPEC firme.

**Anti-pattern bloqueado:** convergencia prematura. Brainstorm **no produce decisión**, sólo opciones.

## Cuándo invocar
- Pre-Briefing: explorar el problem space
- Mid-Spec: cuando un tradeoff de diseño tiene 5+ caminos posibles
- Retro: explorar root causes de un incidente

## Procedimiento

1. **Definir el prompt brainstorming:**
   - "¿Cómo podríamos resolver X?"
   - "¿Qué arquitecturas servirían Y?"
   - "¿Por qué pudo haber pasado Z?"

2. **Invocar party mode** del orchestrator (Sprint 17, ADR-0016):
   ```bash
   python3 scripts/xdd-orchestrate.py run --pattern=brainstorm_party --exec
   ```

3. **Capturar ideas** sin filtrar en `BRAINSTORM_<ts>.md`:
   ```markdown
   # Brainstorm — <fecha> — <prompt>

   ## Ideas raw (orden de aparición)
   - Idea 1: <descripción>
   - Idea 2: <descripción>
   - ...

   ## Categorizadas

   ### Categoría A — <nombre>
   - Idea X
   - Idea Y

   ### Categoría B — <nombre>
   - Idea Z

   ## Ideas wild (low likelihood, alto impacto si funciona)
   - ...

   ## Ideas safe (high likelihood, bajo riesgo)
   - ...
   ```

4. **NO decidir aquí.** La decisión se toma en `/clarify` + ADR posterior.

## Reglas

- ✅ Cantidad sobre calidad inicialmente
- ✅ Build on top: agregar a ideas existentes
- ✅ Permite ideas wild explícitamente
- ❌ No vetar ideas
- ❌ No optimizar redacción
- ❌ No convergir hasta que la sesión termine

## Output expected

Document append-only `BRAINSTORM_<ts>.md` con mínimo 15 ideas. Si <15, sesión incompleta — re-invocar con prompt variado.

## Referencias
- ADR-0016 Party Mode
- ADR-0017 Web bundles
- BMAD /brainstorm (inspiración)
