---
description: Evaluación multidimensional (Código, Infra, Seguridad, UX) de cambios propuestos, garantizando la anticipación de regresiones y la clasificación de riesgo antes de la ejecución técnica.
name: analisis-impacto
trigger: /evol analisis-impacto
---

# /analisis-impacto

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-038 | **Versión:** 2.3.0 | **Nivel:** Diseño Técnico
**Mission:** Evaluación multidimensional (Código, Infra, Seguridad, UX) de cambios propuestos, garantizando la anticipación de regresiones y la clasificación de riesgo antes de la ejecución técnica.

**Orquestador:** Evol-DD Orchestrator (00)
**Asistentes Operativos (Swarm):** Swarm de Diseño (02 Clones)
**Skills Requeridas:** `skill-impacto-details.md`, `skill-dependency-analysis.md`, `skill-code-audit.md`, `skill-risk-assessment.md`
**Cultura:** Cirugía de Precisión · Anticipación · Zero Sorpresas


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

* **Análisis Multi-Dimensión:** El impacto debe evaluarse en código, base de datos, infraestructura y seguridad de forma integrada.
* **Veredicto de Riesgo:** Todo informe debe concluir con una clasificación de riesgo (Bajo a Crítico) para priorizar el testing.
* **Anticipación de Regresiones:** Identificar dependencias circulares o efectos en cadena antes de tocar el código fuente.
* **Trazabilidad de la Evaluación:** Registrar cada hallazgo del análisis en el log NDJSON para auditoría de diseño técnico.
* **Basado en Evidencia:** Usar análisis estático y revisión de la arquitectura (`SAD.md`) para sustentar las conclusiones.

## 2. Evol-DD CORE CONTROL DOMAINS

### 2.1 Impact Governance & Risk Gate
* Approves design changes based on risk assessment results.
* Enforces mandatory mitigations for High/Critical impact changes.

### 2.2 Design Swarm Delegation (Impact)
* **Design Swarm (02):** Executes static analysis, maps side effects, and generates impact reports.
* **Operational Detail:** `skill-impacto-details.md`.

## 3. DOMINIOS DE CONTROL (DETALLE EN SKILLS)

La gestión operativa se delega a skills específicos:

### 3.1 Dimensiones del Análisis Técnico

Delegado a `skill-impacto-details.md > Sección 1`.

- Evaluación integral: Código, Persistencia (DB), Infraestructura y Seguridad.

### 3.2 Metodología de Riesgos

Delegado a `skill-impacto-details.md > Sección 2`.

- Clasificación de severidad (Bajo, Medio, Alto, Crítico) y puntos de control.

### 3.3 Protocolo de Recomendaciones

Delegado a `skill-impacto-details.md > Secciones 3 y 4`.

- Estructura del informe de impacto y plan de mitigación preventiva.

## 4. PROTOCOLO DE ASSETS OBLIGATORIOS

Referencia: `skill-workflow-asset-protocol.md`.

| Activo | Tipo | Origen | Destino/Uso |
| :--- | :--- | :--- | :--- |
| `IMPACT_REPORT` | Markdown | Sistema | `docs/impacto/impacto-[runId].md` |
| `IMPACT_EVENTS` | Log NDJSON | Sistema | `tests/results/impact_${runId}.ndjson` |
| `DEP_GRAPH` | JSON/Dot | Sistema | Mapa de dependencias del cambio |
| `RISK_MATRIX` | Tabla | Sistema | Parte central del informe final |

## 5. FLUJO OPERATIVO (RESUMEN)

1. **Invocación:** El humano lanza `/analisis-impacto` con la descripción del cambio.
2. **Escaneo:** Swarm 02 examina código y referencias mediante análisis estático.
3. **Mapeo:** Análisis de arquitectura (`SAD.md`) y dependencias de base de datos.
4. **Evaluación:** Aplicación de la matriz de riesgos y detección de puntos ciegos.
5. **Cierre:** Generación del informe formal y registro de eventos de diseño.

## 6. RESULTADOS ESPERADOS (NDJSON)

| Evento | Atributos | Propósito |
| :--- | :--- | :--- |
| `impact_analysis_started` | `change_type`, `scope` | Trazabilidad del inicio del análisis de diseño. |
| `side_effect_detected` | `component`, `severity` | Registro de riesgos potenciales identificados. |
| `risk_level_assigned` | `level`, `justification` | Clasificación formal del impacto. |
| `impact_report_ready` | `file_path`, `recommendations` | Notificación de finalización para el orquestador. |

## 7. TEST TIERS (Validación de Análisis)

| Tier | Tipo | Validación |
| :--- | :--- | :--- |
| **Tier 1** | **Estático** | Comprobación de que el informe de impacto cita archivos existentes. |
| **Tier 2** | **Funcional** | El análisis debe incluir al menos una ruta de impacto en la base de datos si aplica. |
| **Tier 3** | **Calidad (Judge)** | LLM revisa si el análisis es "perezoso" o si realmente anticipa fallos complejos. |

## 8. GESTIÓN DE ERRORES (RESUMEN)

- **Ambigüedad en el Cambio:** Detener y pedir clarificación al humano si el alcance no es claro.
- **Alcance Indeterminado:** Marcar como "Requiere Análisis Manual Senior" si la complejidad excede al Swarm.

## 9. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** Ninguno (Fase Creativa).
- **Sucesores:** `FLUJO_001` (New Project), `FLUJO_003` (Fase Requisitos).
- **Skills Vinculadas:** `skill-idea-details`, `skill-prompt-engineering`, `skill-requirements-elicitation`.

---
**Versión:** 2.3.0 | **Fecha:** 2026-03-20
Evol-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.