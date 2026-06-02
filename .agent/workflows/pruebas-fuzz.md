---
description: Ejecución de pruebas destructivas mediante inyección de datos malformados en sandboxes aislados, garantizando la robustez y seguridad ante entradas inesperadas.
name: pruebas-fuzz
trigger: /evol pruebas-fuzz
---

# /pruebas-fuzz

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-033 | **Versión:** 2.3.0 | **Nivel:** Operativo
**Mission:** Ejecución de pruebas destructivas mediante inyección de datos malformados en sandboxes aislados, garantizando la robustez y seguridad ante entradas inesperadas.
**Orquestador:** X-DD Orchestrator (00)
**Asistentes Operativos (Swarm):** Swarm de QA (04 Clones)
**Skills Requeridas:** `skill-fuzz-test-details.md`, `skill-fuzzing.md`, `skill-containerization-docker.md`, `skill-advanced-evaluation.md`
**Entorno:** Sandbox Docker Aislado
**Cultura:** Pruebas Destructivas · Robustez · Zero Defects Ocultos


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

*   **Aislamiento Total:** Prohibido ejecutar fuzzing fuera del sandbox Docker. El daño colateral debe ser cero.
*   **Inyección Basada en Contrato:** Los payloads deben alinearse con los esquemas definidos en `docs/contratos_tecnicos/` para maximizar la cobertura.
*   **Reproducibilidad Mandatoria:** Un crash sin `testcase` reproducible es un falso positivo. Registre siempre la semilla (seed).
*   **Validación Multi-Tier:** Basada en Tiers 1-3 con juicio de IA para explotabilidad.
*   **Observabilidad NDJSON:** Cada crash detectado debe generar un evento atómico con traza completa.

## 2. X-DD CORE CONTROL DOMAINS

### 2.1 Robustness Assurance Gate
*   Ensures the system can handle malformed inputs without critical failure or security breach.
*   Blocks deployment if high-exploitability crashes are detected.

### 2.2 QA Swarm Delegation (Fuzzing)
*   **QA Swarm (04):** Tasks include dictionary selection, payload mutation, and crash reproduction analysis.
*   **Operational Detail:** `skill-fuzz-test-details.md`.

## 3. DOMINIOS DE CONTROL (DETALLE EN SKILLS)

La ejecución técnica se delega a skills especializados:

### 3.1 Diccionarios y Estrategias de Ataque

Delegado a `skill-fuzz-test-details.md > Sección 1`.

-   Selección de payloads según tecnología (API, Binario, Protocolo).

### 3.2 Gestión de Sandbox y Aislamiento

Delegado a `skill-fuzz-test-details.md > Sección 2`.

-   Configuración de límites de CPU, memoria y red en contenedores efímeros.

### 3.3 Reproducción y Análisis Semántico

Delegado a `skill-fuzz-test-details.md > Secciones 3 y 4`.

-   Protocolo de minimización de crashes y juicio de explotabilidad (Juicio de Orchestrator).

## 4. PROTOCOLO DE ASSETS OBLIGATORIOS

Referencia: `skill-workflow-asset-protocol.md`.

| Activo | Tipo | Origen | Destino/Uso |
| :--- | :--- | :--- | :--- |
| `API_CONTRACTS` | JSON/YAML | Docs | Guía para la mutación de campos |
| `TEST_VARS` | Env | Orchestrator | Configuración del sandbox Docker |
| `FUZZ_CRASH_REPORT` | NDJSON | Fuzz_Engineer | `tests/results/fuzz_${runId}.ndjson` |
| `AUDIT_REPORT` | Markdown | Fuzz_Engineer | `docs/auditorias/fuzzing_[fecha].md` |

## 5. FLUJO OPERATIVO (RESUMEN)

1.  **Preparación:** Despliegue de la aplicación en el sandbox Docker aislado.
2.  **Configuración:** Selección de herramientas (`AFL`, `wfuzz`, `Burp`) y diccionarios.
3.  **Ejecución:** Bombardeo de entradas monitorizando el estado del proceso/servicio.
4.  **Análisis:** Clasificación de crashes, minimización de inputs y juicio de impacto.
5.  **Reporte:** Documentación de vulnerabilidades y recomendaciones de parcheo.

## 6. RESULTADOS ESPERADOS (NDJSON)

| Evento | Atributos | Propósito |
| :--- | :--- | :--- |
| `fuzz_session_started` | `target_url`, `tool`, `dictionary` | Registro de inicio de campaña. |
| `crash_detected` | `input_vector`, `signal`, `traceback` | Trazabilidad de fallo crítico. |
| `exploitability_score` | `cvss_score`, `impact_desc` | Evaluación semántica de la gravedad. |
| `fuzz_session_ended` | `total_requests`, `crashes_found` | Resumen estadístico de la prueba. |

## 7. TEST TIERS (Validación de Robustez)

| Tier | Tipo | Validación |
| :--- | :--- | :--- |
| **Tier 1** | **Estático** | Revisión de diccionarios para asegurar que cubren el stack tecnológico actual. |
| **Tier 2** | **Funcional** | Ejecución del fuzzing; el éxito es "No detectar crashes críticos en X tiempo/peticiones". |
| **Tier 3** | **Calidad (Judge)** | LLM analiza los logs de los crashes para descartar ruidos y priorizar remedios. |

## 8. GESTIÓN DE ERRORES (RESUMEN)

-   **Sandbox Caído:** Reintento automático de levantado (2 veces); si persiste, abortar flujo.
-   **Falsos Positivos:** El Swarm de QA debe verificar manualmente cada hallazgo de Tier 2 antes del reporte final.

## 9. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

-   **Predecesores:** `FLUJO_015` (Security Audit), `FLUJO_071` (Secure Isolation).
-   **Sucesores:** `FLUJO_062` (Advanced Pentesting), `FLUJO_056` (Quality Validation).
-   **Skills Vinculadas:** `skill-fuzzing`, `skill-agentic-sast-reasoning`.

---
**Versión:** 2.3.0 | **Fecha:** 2026-03-20
Desarrollado por el X-DD SecOps


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.