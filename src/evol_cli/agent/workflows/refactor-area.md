---
description: Workflow X-DD
name: refactor-area
trigger: /evol refactor-area
---

# /refactor-area

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-012 | **Versión:** 2.3.0 | **Nivel:** Táctico
**Orquestador:** X-DD Orchestrator (00)
**Subagentes:** Swarm de Ejecución (03), Swarm de QA (04), Swarm de Consolidación (05)


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES

* **Ámbito Definido**: Prohibido refactorizar fuera del área especificada en el comando.
* **Zero Regressions**: Las pruebas existentes (Tier 1 y 2) deben pasar al 100% en todo momento.
* **Métricas de Valor**: Todo refactor debe demostrar mejora cuantitativa (complejidad, cobertura o rendimiento).
* **Source Integrity**: Mantener la paridad de funcionalidad y contratos de API.

## 2. X-DD CORE CONTROL DOMAINS

| Dominio | Responsabilidad | Control de Calidad |
| :--- | :--- | :--- |
| **Arquitectura** | Orchestrator (00) | Validación de alineación con SAD y patrones X-DD. |
| **Ejecución** | Swarm 03 | Implementación atómica y pruebas de caracterización. |
| **Validación** | Swarm 04 | Testing Tiered (1-3) y validación de métricas delta. |
| **Consolidación** | Swarm 05 | Registro en memoria institucional y actualización de docs. |

## 3. OPERATIONAL FLOW

El detalle operativo se delega a la skill especializada para mantener la agilidad del workflow.

### 3.1 Caracterización y Línea Base

* **Referencia:** `skill-refactoring-details.md > Sección 1.1`
* Escritura de tests de caracterización si la cobertura es insuficiente.
* Medición de métricas pre-refactor (NDJSON).

### 3.2 Refactorización Incremental

* **Referencia:** `skill-refactoring-details.md > Sección 1.2`
* Aplicación de patrones de refactoring (Martin Fowler).
* Validación unitaria continua.

### 3.3 Validación y Cierre

* **Referencia:** `skill-refactoring-details.md > Sección 1.3`
* Ejecución de Tier 2 (Integration) y Tier 3 (LLM Audit).
* Cálculo de mejora delta y reporte final.

## 4. ASSET LOG & NDJSON

El registro de activos se rige por el estándar: `skill-workflow-asset-protocol.md`.

* **Informe de Refactor**: `docs/refactors/refactor-[area].md`
* **Métricas Comparativas**: `tests/results/metrics-refactor.ndjson`
* **Log de Evidencias**: `tests/results/refactor_${runId}.ndjson`

## 5. RECOVERY & ERRORS

| Incidente | Acción Orchestrator |
| :--- | :--- |
| **Regresión Detectada** | Reversión inmediata al commit previo estable. |
| **Métricas Negativas** | Bloqueo de merge; requiere análisis de impacto técnico. |
| **Ruptura de Contrato** | Parada de emergencia; el refactor no debe alterar la API. |

---
**Versión:** 2.3.0 | **Estado:** Operativo
X-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.