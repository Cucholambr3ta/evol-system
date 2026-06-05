---
description: Gestión de respuesta crítica a incidentes y hotfixes en producción.
name: incidente-ID
trigger: /evol incidente-ID
---

# /incidente-ID

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-019 | **Versión:** 2.3.0 | **Nivel:** Táctico
**Misión:** Gestión de respuesta crítica a incidentes y hotfixes en producción.
**Agentes Asignados:** Swarm de Ejecución (03), Swarm de QA (04), Swarm de Consolidación (05)
**Skills Requeridas:** `skill-gitflow-management`, `skill-incident-management-details`, `skill-emergency-response-plan`
**Cultura:** Velocidad Controlada · Zero Defect Policy · Continuidad Operacional · Observabilidad NDJSON


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. MISIÓN DEL FLUJO

Este workflow gestiona la respuesta a **incidentes críticos en producción** que requieren una corrección inmediata (hotfix). Su propósito es minimizar el tiempo de resolución sin sacrificar la calidad ni la estabilidad del sistema. Actúa como un carril rápido pero estrictamente controlado, convalidando algunos pasos del desarrollo normal pero manteniendo gates de calidad esenciales.

## 2. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

*   **Severidad Obligatoria:** Solo se permite hotfix para incidentes de severidad **CRÍTICA** o **ALTA**.
*   **Aislamiento Total:** Rama `hotfix/INC-[ID]-[desc]` creada directamente desde `main`.
*   **Validación Gate-keeper:** Prohibido el merge sin pasar Tier 1 y Tier 2 satisfactoriamente.
*   **Sincronización Dual:** Obligatorio merge a `main` (con tag) y a `develop`.
*   **Protocolo NDJSON:** Todo evento de resolución debe quedar registrado en tiempo real.

## 3. Evol-DD CORE CONTROL DOMAINS

### 3.1 Crisis Integrity Gate

*   Certifies rapid-response stability under emergency conditions.
*   Ensures hotfixes do not compromise system long-term architecture.

### 3.2 Delegation (Operations)

*   **Execution Swarm (03):** Assigned to focalized fix implementation.
*   **QA Swarm (04):** Assigned to fast-track Tier 1/2 validation.
*   **Consolidation Swarm (05):** Assigned to post-mortem and vault sync.
*   **Operational Detail:** `skill-incident-management-details`.

## 4. DOMINIOS DE CONTROL (DETALLE EN SKILLS)

El detalle operativo del hotfix se gestiona a través de skills especializados:

### 4.1 Clasificación y Triaje

Delegado a `skill-incident-management-details.md > Sección 1.1`.

- Validación de severidad con el Humano y determinación de ruta.

### 3.2 Protocolo de Rama y GitFlow

Delegado a `skill-incident-management-details.md > Sección 1.2`.

- Aislamiento de la rama y preparación del entorno de crisis.

### 3.3 Implementación de Emergencia (TDD Express)

Delegado a `skill-incident-management-details.md > Sección 1.3`.

- Resolución focalizada y validación unitaria rápida.

### 3.4 Validación de Seguridad y Regresión

Delegado a `skill-incident-management-details.md > Sección 1.4`.

- Ejecución de Tiers críticos para asegurar que el fix no introduce nuevos fallos.

### 3.5 Cierre y Sincronización

Delegado a `skill-incident-management-details.md > Sección 1.5`.

- Despliegue, etiquetado y reintegración de rama.

## 4. PROTOCOLO DE ASSETS OBLIGATORIOS

Referencia: `skill-workflow-asset-protocol.md`.

| Activo | Tipo | Origen | Destino/Uso |
| :--- | :--- | :--- | :--- |
| `ID_INCIDENTE` | Parámetro | Humano | Identificador único del hotfix. |
| `SEVERIDAD` | Metadato | Humano | Gate de entrada al flujo. |
| `INFORME_POST_MORTEM` | Documento | Agente (05) | `docs/incidentes/INC-[ID].md` |
| `LOG_NDJSON` | Registro | Sistema | `tests/results/incident_${runId}.ndjson` |

## 5. FLUJO OPERATIVO (RESUMEN)

1. **Invocación:** El Humano lanza `/incidente-[ID]` con descripción y severidad.
2. **Aislamiento:** Creación inmediata de rama `hotfix/` desde `main`.
3. **Corrección:** Implementación focalizada por el Swarm 03.
4. **Validación:** Ejecución obligatoria de Tiers 1 y 2 (Fast Track).
5. **Release:** Merge a `main`, generación de Tag y merge a `develop`.
6. **Memoria:** Registro post-mortem y actualización de la Bóveda.

## 6. RESULTADOS ESPERADOS (NDJSON)

| Evento | Atributos | Propósito |
| :--- | :--- | :--- |
| `incident_hotfix_start` | `runId`, `severity`, `incidentId` | Trazabilidad de inicio de crisis. |
| `hotfix_validation_result` | `tier1_pass`, `tier2_pass` | Prueba de que el fix es seguro. |
| `incident_resolution` | `resolution_time`, `status` | Métrica de eficacia operacional. |

## 7. GESTIÓN DE ERRORES

- **Fallo de Validación:** Si el fix no pasa los tests, se bloquea el despliegue.
- **Conflictos de Merge:** Resolución automática preferida; si no, escalado urgente.

## 8. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `/monitoring-alerts`, `/rollback`.
- **Sucesores:** `/backup-restore`, `/obsidian-vault-sync`.
- **Skills Vinculadas:** `skill-incident-management`, `skill-emergency-response`.

---

**Versión:** 2.3.0 | **Fecha:** 2026-03-20
Evol-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.