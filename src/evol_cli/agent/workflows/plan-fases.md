---
description: Transformación del PRD en un plano de ejecución multioficio mediante la descomposición en fases lógicas, definición de contratos técnicos (SAD, OpenAPI) y generación de grafos de tareas (DAG) optimizados para el paralelismo.
name: plan-fases
trigger: /evol plan-fases
---

# /plan-fases

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-005 | **Versión:** 3.0.0 | **Nivel:** Diseño Técnico (Execution Plan)
**Mission:** Transformación del PRD en un plano de ejecución mediante Roadmapping GSD y descomposición en Slices atómicos.

**Orquestador:** Orchestrator (00)
**Subagentes:** Architect, Maintainer
**Skills Requeridas:** `skill-gsd-sync`, `skill-project-architect.md`, `skill-technical-documentation.md`
**Duración estimada:** 30-50 minutos
**Cultura:** Contract First · Spec-Driven · Roadmap Excellence


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. MISIÓN DEL FLUJO

Este workflow transforma el PRD aprobado en un **plano de ejecución GSD**. Su objetivo es descomponer el sistema en hitos (Milestones) y Slices, definir los contratos técnicos y generar el `Memoria/gsd/ROADMAP.md` que guiará la ejecución autónoma.

## 2. DIRECTRICES INQUEBRANTABLES

- **Contract First:** Prohibido definir lógica de implementación antes que los contratos de interfaz.
- **DoD Explícito:** Cada tarea en `tasks.yaml` debe tener criterios de aceptación técnicos y medibles.
- **Validación del DAG:** El plan de tareas debe ser validado contra ciclos antes de ser entregado.

## 3. FLUJO OPERATIVO (SINOPSIS)

El detalle técnico y operativo se encuentra en `skill-phase-planning-details.md`.

### 3.1 Fase 1: Arquitectura y Contratos (Architect)

Mapeo de arquitectura técnica basada en el PRD. Definición de esquemas de datos y especificaciones de interfaz.

### 3.2 Fase 2: Generación del ROADMAP.md

Creación del archivo `Memoria/gsd/ROADMAP.md` detallando hitos, riesgos y dependencias. Se utiliza el formato GSD para permitir el rastreo de progreso por Slices.

### 3.3 Fase 3: Inicialización del STATE.md

Creación del `Memoria/gsd/STATE.md` para el seguimiento en tiempo real de la ejecución. Registro de la línea base del proyecto.

## 4. PROTOCOLO DE ACTIVOS

Los activos y entregables deben gestionarse según el estándar en `skill-workflow-asset-protocol.md`. El log de eventos se almacena en `tests/results/plan_fases_${runId}.ndjson`.

## 5. TEST TIERS DE PLANIFICACIÓN

| Tier | Tipo | Qué valida |
| :--- | :--- | :--- |
| **Tier 1** | Estático | Validación del DAG (sin ciclos), validez de OpenAPI. |
| **Tier 2** | Integración | Coherencia entre SAD, PRD y el Grafo de Tareas. |
| **Tier 3** | LLM-Judge | Optimización de la descomposición y paralelismo sugerido. |

## 6. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `/fase-requisitos` (SDD Requisitos).
- **Sucesores:** Ejecución de Slices (Orchestrator).
- **Skills Vinculadas:** `skill-c4-architecture`, `skill-technical-documentation`, `skill-dag-validator`.

---
**Versión:** 3.0.0 | **Fecha:** 2026-04-02
Desarrollado por Evol-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.