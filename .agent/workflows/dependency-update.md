---
description: Mantenimiento proactivo de dependencias y mitigación de vulnerabilidades en la cadena de suministro.
name: dependency-update
trigger: /evol dependency-update
---

# /dependency-update

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-026 | **Versión:** 2.3.0 | **Nivel:** Táctico
**Misión:** Mantenimiento proactivo de dependencias y mitigación de vulnerabilidades en la cadena de suministro.
**Agentes Asignados:** X-DD Orchestrator (00), Swarm de Ejecución (03), 12_Dependency_Manager
**Skills Requeridas:** `skill-software-composition-analysis`, `skill-dependency-update-details`, `skill-patch-management`
**Cultura:** Mantenimiento Proactivo · Seguridad · Zero Vulnerabilidades Conocidas


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

* **Seguridad Primero:** Las actualizaciones que resuelven vulnerabilidades críticas tienen prioridad absoluta sobre cualquier otra tarea.
* **Validación Aislada:** Todas las actualizaciones deben realizarse en ramas independientes (`deps/*`) para evitar la contaminación de `develop`.
* **Inmutabilidad del Lockfile:** Prohibido modificar archivos de bloqueo manualmente; siempre utilizar los comandos del gestor de paquetes oficial.
* **Evidencia Técnica:** Cada actualización debe estar respaldada por un reporte de validación en formato NDJSON.
* **Zero Context Rot:** El entorno de trabajo debe ser saneado tras la fusión exitosa del Pull Request.

## 2. X-DD CORE CONTROL DOMAINS

### 2.1 Supply Chain Integrity Gate
* Certifies that third-party code additions do not introduce backdoors or license conflicts.
* Enforces strict tiered validation for critical dependency updates.

### 2.2 Operational Swarm Delegation
* **Execution Swarm (03):** Assigned to automated patch application and build verification.
* **Dependency Manager (12):** Assigned to vulnerability triage and security auditing.
* **Operational Detail:** `skill-dependency-update-details.md`.

## 3. DOMINIOS DE CONTROL (DETALLE EN SKILLS)

La gestión técnica de dependencias se delega a skills específicos:

### 3.1 Escaneo y Registro de Vulnerabilidades

Delegado a `skill-dependency-update-details.md > Sección 1`.

- Uso de herramientas de auditoría (Audit Swarm) y registro de hallazgos en NDJSON.

### 3.2 Estrategia de Priorización y Tiers

Delegado a `skill-dependency-update-details.md > Sección 2`.

- Clasificación semántica de actualizaciones y niveles de validación (Tier 1-3).

### 3.3 Flujo Secuencial y Resolución

Delegado a `skill-dependency-update-details.md > Sección 3 y 4`.

- Pasos operativos desde la invocación hasta el Pull Request y manejo de conflictos de lockfiles.

## 4. PROTOCOLO DE ASSETS OBLIGATORIOS

Referencia: `skill-workflow-asset-protocol.md`.

| Activo | Tipo | Origen | Destino/Uso |
| :--- | :--- | :--- | :--- |
| `DEP_BRANCH` | Rama Git | Sistema | `deps/update-YYYYMMDD` |
| `SCAN_NDJSON` | Registro | Sistema | `tests/results/scan_[runId].ndjson` |
| `VALIDATION_LOG` | Registro | Sistema | `tests/results/dep_update_[runId].ndjson` |
| `DEP_REPORT` | Informe MD | Agente (12) | `knowledge/Proyectos/[Project]/Dependencies.md` |

## 5. FLUJO OPERATIVO (RESUMEN)

1. **Auditoría:** Escaneo masivo de dependencias para detectar versiones obsoletas y vulnerabilidades.
2. **Evaluación:** Clasificación de cambios según impacto (Patch, Minor, Major).
3. **Actualización:** Aplicación de cambios en ramas aisladas y regeneración de lockfiles.
4. **Verificación:** Ejecución de suites de prueba Tiered para detectar regresiones funcionales.
5. **Gobernanza:** Creación de Pull Request y solicitud de `/qa-review` automatizada.
6. **Cierre:** Fusión de cambios y archivado de logs de auditoría.

## 6. RESULTADOS ESPERADOS (NDJSON)

| Evento | Atributos | Propósito |
| :--- | :--- | :--- |
| `dep_scan_start` | `runId`, `package_manager` | Inicio del proceso de auditoría. |
| `vuln_detected` | `package`, `severity`, `cve` | Notificación de riesgos de seguridad. |
| `update_completed` | `package`, `from`, `to`, `status` | Trazabilidad del proceso de cambio. |
| `dep_validation_end` | `test_tier`, `pass_rate` | Confirmación de estabilidad post-cambio. |

## 7. TEST TIERS (Validación de Auditoría)

| Tier | Tipo | Validación |
| :--- | :--- | :--- |
| **Tier 1** | **Estático** | Validación de integridad de lockfiles y sintaxis de manifiestos. |
| **Tier 2** | **Funcional** | Ejecución de regresiones y suites unitarias/integración. |
| **Tier 3** | **Calidad (Judge)** | Análisis por LLM de los changelogs para prever impactos arquitectónicos. |

## 8. GESTIÓN DE ERRORES (RESUMEN)

- **Conflicto de Árbol:** Intentar purga de caché y reinstalación limpia del ecosistema.
- **Fallo de Regresión:** Revertir la dependencia conflictiva y reportar el incidente de inmediato.

## 9. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `/security-audit`, `/qa-review`.
- **Sucesores:** `/ci-cd-setup`, `/monitoring-alerts`.
- **Skills Vinculadas:** `skill-software-composition-analysis`, `skill-patch-management`.

---

**Versión:** 2.3.0 | **Fecha:** 2026-03-20
X-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.

---

## Extension: disciplina Deprecation-Driven (DeprecationDD)

> Activacion por profile: `deprecationdd` en `methodologies:`. Ficha:
> [`docs/disciplinas/DeprecationDD.md`](../../docs/disciplinas/DeprecationDD.md).

Dependency-update gestiona la actualizacion de dependencias. Cuando el profile activa `deprecationdd`,
se extiende a la **politica de sunset del codigo propio deprecado**:

- **Entrada adicional:** `api_versions/deprecation_schedule.json` (desde [APIVDD](../../docs/disciplinas/APIVDD.md)).
- **Salida adicional:** `deprecations/*/sunset_policy.json` (fecha tope + reemplazo) +
  `deprecations/logs/usage_metrics.json` (uso del codigo deprecado).
- **Criterio:** no hay llamadas a codigo obsoleto despues de su fecha de sunset; cerca del sunset se
  generan PRs automaticos de eliminacion.
- **Integracion:** el codigo deprecado vivo se contabiliza como deuda en
  [DebtBudgetDD](../../docs/disciplinas/DebtBudgetDD.md).
- **Fuentes:** las politicas basadas en estandares (RFC 8594, etc.) citan su URL (DOC_STANDARD).