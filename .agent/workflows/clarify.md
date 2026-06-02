---
name: clarify
title: "/clarify — Detectar y resolver ambigüedad antes de avanzar"
description: Detecta ambigüedad (4 niveles severidad) en SPEC/DOMAIN/PLAN y bloquea gate si CRÍTICAS pendientes. Inspirado en Spec-Kit /clarify.
phase: any
category: planning
ssot: true
inputs:
  - SPEC.md o DISCOVERY.md o PLAN.md vigente (cualquier artefacto fase actual)
outputs:
  - Lista de preguntas categorizadas por severidad
  - Respuestas registradas en CLARIFICATIONS.md (append-only)
inspired_by: Spec-Kit /clarify (MIT)
adr: docs/adr/0014-sdd-parity-clarify-cross-validate-constitution.md
trigger: /evol clarify
---

# /clarify — Detectar ambigüedad y resolver

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.

## Propósito
Identificar términos vagos, supuestos no declarados, criterios de aceptación faltantes, dependencias implícitas. **Bloquea avance de fase si encuentra ambigüedad crítica** (alineado con principio "Ambigüedad Cero" del Art. 7).

## Cuándo invocar
- Pre-gate de Spec (Fase 2): antes de firmar SPEC/DOMAIN/THREATS
- Pre-gate de Plan (Fase 3): antes de firmar PLAN.md
- Cualquier sesión que el agente detecte palabras como "etc", "tbd", "ver luego", "asumiendo que"

## Procedimiento

1. **Cargar artefacto vigente** de la fase actual (SPEC.md, DISCOVERY.md, PLAN.md, según fase).

2. **Detectar ambigüedad** clasificada por severidad:
   - **CRÍTICA** (bloquea fase): criterio de aceptación faltante, comportamiento de error no definido, autoridad de decisión no asignada, threat sin mitigación
   - **ALTA** (requiere respuesta antes del próximo gate): performance budget no declarado, capacidad escala no especificada, edge case sin trat
   - **MEDIA** (registrar en backlog): convención de naming, refactor pendiente, optimización
   - **BAJA** (informativo): comment a añadir, docstring incompleta

3. **Generar preguntas** en formato:
   ```
   [SEV] Q-NNN: <pregunta>
     Contexto: <cita literal del artefacto>
     Posibles respuestas (3-5 opciones):
       a) ...
       b) ...
       c) ...
   ```

4. **Esperar respuestas** del humano. Cada respuesta se registra en `CLARIFICATIONS.md`:
   ```
   ## Q-NNN — <fecha>
   **Pregunta:** ...
   **Respuesta:** opción <X> + comentarios
   **Decisión por:** <nombre humano>
   **Impacto en artefactos:** <archivos a editar>
   ```

5. **Editar artefactos** afectados con las respuestas (no inferir, citar respuesta).

6. **Re-ejecutar** /clarify hasta que no queden ambigüedades CRÍTICAS pendientes.

## Comportamiento

- Si quedan ambigüedades **CRÍTICAS** sin respuesta → exit code 1 (bloquea gate)
- Si quedan **ALTAS** sin respuesta → exit code 0 + warning (gate permitido con flag --allow-high)
- MEDIA y BAJA → siempre exit code 0

## Ejemplo

```
[CRÍTICA] Q-001: "El sistema debe ser rápido" en SPEC.md L42.
  Contexto: "La búsqueda debe ser rápida y eficiente."
  Posibles respuestas:
    a) p99 latency < 100ms
    b) p99 latency < 500ms
    c) Sin SLA específico (no recomendado)
    d) Solo asintótico O(log n)

[ALTA] Q-002: Comportamiento si usuario busca con query vacío
  Contexto: "Permite búsqueda por texto libre."
  Posibles respuestas:
    a) Retornar todos los resultados (paginados)
    b) Retornar error 400
    c) Retornar resultados más recientes (default ordering)
```

## Referencias
- ADR-0014 SDD parity
- Spec-Kit /clarify inspiración
- Constitución X-DD Art. 7 (Ambigüedad Cero)
