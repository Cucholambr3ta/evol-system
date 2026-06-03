---
description: Workflow X-DD
name: deploy-prod
trigger: /evol deploy-prod
---

# /deploy-prod

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-018 | **Versión:** 2.3.0 (Art. 6 Interoperabilidad) | **Nivel:** Táctico
**Orquestador:** X-DD Orchestrator (00)
**Skills Requeridas:** `skill-gitflow-management.md`, `skill-deployment-details.md`, `skill-workflow-asset-protocol.md`

**Entorno:** Producción / Main Branch
**Cultura:** Velocidad Controlada · Zero Defect Policy · Continuidad Operacional · Observabilidad NDJSON


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

*   **Protocolo de Verificación P0**: Prohibición de despliegue sin validación exitosa de Tier 1 y 2.
*   **Inmutabilidad**: Prohibición de cambios manuales en `prod`. Todo cambio debe provenir de Git.
*   **Veredicto NDJSON**: Registro atómico obligatorio en `logs/deploy/${runId}.ndjson`.

## 2. X-DD CORE CONTROL DOMAINS

### 2.1 Production Integrity Gate
*   Certifies security, performance, and stability before production release.
*   Ensures compliance with the Asset Protocol (Version Sealing).

### 2.2 Delegation (Operations)
*   **Ops Swarm (06):** Assigned to environment preparation, secret injection, and infrastructure sync.
*   **Orchestrator (00):** Final approval gate and log certification.
*   **Operational Detail:** `skill-deployment-details`.
- **Protección de `main`**: Solo fusiones mediante PR protegida. Prohibido commit directo.
- **Memoria Viva**: Actualización obligatoria de `claude.md` y Obsidian tras el despliegue.

## 3. ARTÍCULO 6: INTEROPERABILIDAD

El despliegue es el evento culminante de la cadena de valor:

* **Conector `CICD-AUTH` (`FLUJO-008`)**: El despliegue a producción requiere la certificación previa del setup de CI/CD para garantizar la integridad del entorno.
* **Conector `DOC-FINAL` (`FLUJO-007`)**: Gatilla la generación final de manuales de usuario y guías de API basados en la versión estable desplegada.
* **Conector `INCIDENT-LOG` (`FLUJO-019`)**: En caso de fallo post-deploy, activa automáticamente el protocolo de respuesta ante incidentes.

## 4. PROTOCOLO OPERATIVO (DELEGACIÓN)

El detalle operativo del despliegue se gestiona a través de skills especializados:

### 4.1 Verificación de Gates
Delegado a `skill-deployment-details.md > Sección 1.1`.

### 4.2 Determinación de Versión (SemVer)
Delegado a `skill-deployment-details.md > Sección 1.2`.

### 4.3 Generación de Release Notes
Delegado a `skill-deployment-details.md > Sección 1.3`.

### 4.4 Sincronización GitFlow
Delegado a `skill-deployment-details.md > Sección 1.4`.

### 4.5 Consolidación de Memoria
Delegado a `skill-deployment-details.md > Sección 1.5`.

## 5. ACTIVOS Y ENTREGABLES

| Activo | Destino | Tipo |
| :--- | :--- | :--- |
| Release Notes | `CHANGELOG.md` y GitHub Releases | Doc |
| Tag de Versión | Repositorio (vX.Y.Z) | Tag |
| Memoria Actualizada | `claude.md` y Vault Obsidian | Memory |
| Evidencias NDJSON | `tests/results/deployment_${runId}.ndjson` | Audit Log |

## 6. TEST TIERS (DEPLOYMENT)

| Tier | Tipo | Herramienta | Validación |
| :--- | :--- | :--- | :--- |
| **Tier 1** | Estático | SemVer Check | Formato de versión y existencia de Changelog. |
| **Tier 2** | Integración | Git Remote | Verificación de existencia del tag en remoto. |
| **Tier 3** | Calidad (Judge) | LLM-as-judge | Claridad y completitud de las Release Notes. |

## 7. GESTIÓN DE ERRORES

| Error | Acción |
| :--- | :--- |
| Gates no superados | **ABORT**. No se permite el despliegue. |
| Conflicto en Merge | El humano debe resolver manualmente; reintentar. |
| Fallo en Push | Verificar permisos y estado de red; reintentar. |

---
**Versión:** 2.3.0 | **Fecha:** 2026-03-20
X-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.