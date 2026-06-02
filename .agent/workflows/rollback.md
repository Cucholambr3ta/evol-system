---
description: Reversión segura y rápida a estados estables ante fallos críticos.
---

# /rollback

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-022 | **Versión:** 2.3.0 | **Nivel:** Táctico
**Misión:** Reversión segura y rápida a estados estables ante fallos críticos.
**Agentes Asignados:** 03_Ejecutor_Asincrono, 04_Swarm_QA, 05_Gestor_Boveda
**Skills Requeridas:** `skill-gitflow-management`, `skill-rollback-details`, `skill-database-migration`
**Cultura:** Recuperación Rápida · Trazabilidad NDJSON · Zero Downtime


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

* **Activación por Alerta o Comando:** El rollback puede ser manual (`/rollback [version]`) o disparado por monitoreo.
* **Inmutabilidad por Tags:** Solo se permite rollback a versiones con tags de Git válidos.
* **Consistencia de Datos:** Obligatorio ejecutar down migrations o restaurar backup si hubo cambios en BD.
* **Validación Final:** No se cierra el incidente sin pruebas de humo (Smoke Tests) exitosas.
* **Transparencia NDJSON:** Cada paso del proceso debe ser registrado para auditoría post-mortem.

## 2. X-DD CORE CONTROL DOMAINS

### 2.1 Recovery Integrity Gate
* Certifies the system state after a critical failure or failed deployment.
* Ensures the rollback version is consistent and stable.

### 2.2 Delegation (Operations)
* **QA Swarm (04):** Assigned to Smoke Testing and stability validation.
* **Vault Manager (05):** Assigned to incident documentation and NDJSON logging.
* **Operational Detail:** `skill-rollback-details.md`.

## 3. DOMINIOS DE CONTROL (DETALLE EN SKILLS)

La complejidad operativa del rollback se delega a skills específicos:

### 3.1 Validación de Versiones y Esquemas

Delegado a `skill-rollback-details.md > Sección 1.1`.

- Comprobación de existencia de tags y análisis de compatibilidad de BD.

### 3.2 Reversión de Código y Sincronización

Delegado a `skill-rollback-details.md > Sección 1.2`.

- Ejecución de checkouts, resets o reverts según política de Git.

### 3.3 Reversión de Base de Datos (Migrations/Backup)

Delegado a `skill-rollback-details.md > Sección 1.3`.

- Gestión de scripts `down` y coordinación con snapshots de datos.

### 3.4 Re-despliegue de Artefactos Estables

Delegado a `skill-rollback-details.md > Sección 1.4`.

- Despliegue de imágenes previas y restauración de variables de entorno.

### 3.5 Verificación Post-Rollback (Smoke Testing)

Delegado a `skill-rollback-details.md > Sección 1.5`.

- Validación de disponibilidad y flujos críticos tras la reversión.

## 4. PROTOCOLO DE ASSETS OBLIGATORIOS

Referencia: `skill-workflow-asset-protocol.md`.

| Activo | Tipo | Origen | Destino/Uso |
| :--- | :--- | :--- | :--- |
| `INFORME_ROLLBACK` | Documento | Agente (05) | `docs/incidentes/rollback-${fecha}.md` |
| `EVIDENCIA_SMOKE` | Registro | Agente (04) | `tests/results/smoke_${runId}.log` |
| `LOG_NDJSON` | Registro | Sistema | `tests/results/rollback_${runId}.ndjson` |

## 5. FLUJO OPERATIVO (RESUMEN)

1. Invocación: Recepción de comando o alerta con versión objetivo.
2. Validación: Comprobación de que la versión destino existe y es segura.
3. Reversión: Ejecución coordinada de Rollback de Código y BD.
4. Despliegue: Reinicio de servicios con el artefacto de la versión estable.
5. Verificación: Ejecución de Smoke Tests Tier 1/2.
6. Cierre: Generación de informe de incidente y notificación final.

## 6. RESULTADOS ESPERADOS (NDJSON)

| Evento | Atributos | Propósito |
| :--- | :--- | :--- |
| `rollback_start` | `runId`, `target_version` | Trazabilidad del inicio de la emergencia. |
| `reversion_status` | `code_ok`, `db_ok` | Estado de las tareas de restauración. |
| `smoke_test_result` | `pass_rate`, `critical_fail` | Validación de estabilidad post-reversión. |
| `rollback_end` | `final_version`, `status` | Cierre del flujo de recuperación. |

## 7. GESTIÓN DE ERRORES

- Conflicto de Git: Si la reversión automática falla, escalar para intervención manual.
- Fallo de Migración: Priorizar restauración desde backup si las migraciones `down` fallan.

## 8. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `/monitoring-alerts`, `/incidente-ID`.
- **Sucesores:** `/backup-restore`, `/obsidian-vault-sync`.
- **Skills Vinculadas:** `skill-gitflow-management`, `skill-database-migration`.

---

**Versión:** 2.3.0 | **Fecha:** 2026-03-20
X-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.