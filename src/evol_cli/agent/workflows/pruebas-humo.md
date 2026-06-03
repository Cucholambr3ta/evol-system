---
description: Workflow X-DD
name: pruebas-humo
trigger: /evol pruebas-humo
---

# /pruebas-humo

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-037 | **Versión:** 2.3.0 (NDJSON & Tiered Testing) | **Nivel:** Operativo
**Orquestador:** X-DD Orchestrator (00)
**Asistentes Operativos (Swarm):** Swarm de QA (04 Clones)
**Skills Requeridas:** `skill-smoke-test-details.md`, `skill-browser-automation.md`, `skill-containerization-docker.md`
**Entorno:** Sandbox Docker aislado (o entorno de staging)
**Cultura:** Verificación Rápida · Confianza Básica · Zero Regressions


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

* **Conjunto Mínimo Vital:** Las pruebas deben cubrir solo el "Happy Path" crítico (login, pago, carga inicial).
* **Límite de Tiempo:** La suite completa no debe exceder los **5 minutos**. Rapidez sobre exhaustividad.
* **Resultado Binario (Fail-Fast):** El resultado es PASS o FAIL. Si un test crítico falla, se aborta el despliegue/promoción inmediatamente.
* **Automatización Total:** Ejecución sin intervención humana en entornos aislados.
* **Evidencia NDJSON:** Cada paso de la prueba de humo debe ser observable y trazable mediante registros asíncronos.

## 2. X-DD CORE CONTROL DOMAINS

### 2.1 Stability Assurance Gate
* Ensures post-deployment integrity before broader exposure.
* Automatically triggers rollbacks (if configured) upon smoke test failure.

### 2.2 QA Swarm Delegation (Smoke)
* **QA Swarm (04):** Executes automated scripts, validates entrypoints, and performs visual/AI sanity checks.
* **Operational Detail:** `skill-smoke-test-details.md`.

## 3. DOMINIOS DE CONTROL (DETALLE EN SKILLS)

La gestión operativa se delega a skills específicos:

### 3.1 Estructura del Manifiesto

Delegado a `skill-smoke-test-details.md > Sección 1`.

- Definición de `smoke-manifest.json` y configuración de timeouts.

### 3.2 Ejecución por Tiers

Delegado a `skill-smoke-test-details.md > Sección 2`.

- Niveles de validación: Tier 1 (Conectividad), Tier 2 (Funciones Vitales), Tier 3 (Visual/AI).

### 3.3 Lógica de Reintentos y Aborto

Delegado a `skill-smoke-test-details.md > Sección 3`.

- Protocolo de Fail-Fast y reintentos automáticos ante errores transitorios.

## 4. PROTOCOLO DE ASSETS OBLIGATORIOS

Referencia: `skill-workflow-asset-protocol.md`.

| Activo | Tipo | Origen | Destino/Uso |
| :--- | :--- | :--- | :--- |
| `SMOKE_MANIFEST` | JSON | Sistema | `tests/smoke-manifest.json` |
| `SMOKE_REPORT` | Markdown | Sistema | `docs/auditorias/smoke-[runId].md` |
| `SMOKE_EVENTS` | Log NDJSON | Sistema | `tests/results/smoke_${runId}.ndjson` |
| `VISUAL_ASSERT` | Imagen | Sistema | Capturas de pantalla para Tier 3 |

## 5. FLUJO OPERATIVO (RESUMEN)

1. **Invocación:** El sistema lanza `/pruebas-humo` tras un despliegue.
2. **Preparación:** QA (04) valida accesibilidad de la URL y carga el manifiesto.
3. **Ejecución:** Proceso secuencial de Tiers 1-3 con lógica de aborto temprano.
4. **Validación Visual:** Uso de LLM para confirmar estabilidad visual básica.
5. **Cierre:** Generación de reporte y notificación de estado de salud.

## 6. RESULTADOS ESPERADOS (NDJSON)

| Evento | Atributos | Propósito |
| :--- | :--- | :--- |
| `smoke_suite_started` | `target_url`, `env` | Inicio de la validación post-despliegue. |
| `tier_validation_completed` | `tier_level`, `status` | Trazabilidad del progreso por niveles. |
| `critical_test_failed` | `test_id`, `error_msg` | Alerta inmediata de regresión mayor. |
| `smoke_summary` | `passed_count`, `total_time` | Resumen ejecutivo para el orquestador. |

## 7. TEST TIERS (Validación de Humo)

| Tier | Tipo | Validación |
| :--- | :--- | :--- |
| **Tier 1** | **Conectividad** | HTTP 200 en entrypoints y salud de DB/Cache. |
| **Tier 2** | **Funcional** | Ejecución de scripts Playwright en rutas críticas. |
| **Tier 3** | **Calidad (Judge)** | LLM analiza si hay "glitches" o "broken layouts" evidentes. |

## 8. GESTIÓN DE ERRORES (RESUMEN)

- **Entorno Inalcanzable:** Reintentar 3 veces; si falla persistente, marcar FAIL de infraestructura.
- **Fallo Crítico:** Detener flujo, revertir despliegue (si aplica) y alertar al humano.

---

**Versión:** 2.3.0 | **Fecha:** 2026-03-20
X-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.