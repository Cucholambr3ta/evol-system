---
description: Operacionalización del Artículo 1 (Filtro de Ambigüedad) mediante elicitación de alta resolución, categorización técnica y validación de interoperabilidad para la generación de PRDs profundos.
name: fase-requisitos
trigger: /evol fase-requisitos
---

# /fase-requisitos

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-003 | **Versión:** 3.0.0 | **Nivel:** Operativo (SDD Enabled)
**Mission:** Operacionalización del Artículo 1 (Filtro de Ambigüedad) mediante elicitación de alta resolución y SDD (Spec-Driven Development).

**Orquestador:** Orchestrator (00)
**Subagentes:** Architect, Domain-Expert
**Skills Requeridas:** `skill-gsd-sync`, `skill-requirements-elicitation.md`, `skill-project-architect.md`
**Duración estimada:** 20-40 minutos
**Cultura:** Ambiguity Filter · Spec-Driven · GSD Logic


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. MISIÓN DEL FLUJO

Este workflow operacionaliza el **Artículo 1 (Filtro de Ambigüedad)** de la Constitución con un enfoque de **Spec-Driven Development (SDD)**. Su objetivo es destilar la visión del usuario en un **Documento de Requisitos del Producto (PRD)** detallado y cuestionarios GSD que eliminen la ambigüedad antes de planificar fases.

## 2. DIRECTRICES INQUEBRANTABLES

- **Protocolo Paso Cero:** Prohibido redactar el PRD si existen dudas en áreas críticas (Frontend, Backend, Seguridad, Infraestructura).
- **Categorización Mandataria:** Los requisitos agrupados por áreas de especialidad técnica.
- **Auditoría de Interoperabilidad:** Cada requisito validado contra workflows existentes (Fit-Audit).
- **Gherkin Completo Obligatorio:** Cada feature tiene TODOS sus criterios de aceptacion en formato Gherkin. No se acepta "criterio" sin su bloque Feature/Scenario.

## 2.1 ESPECIFICACIONES DE ACEPTACION GRANULARES (OBLIGATORIO)

Cada feature del FEATURES.md produce un bloque Gherkin con esta estructura minima:

```gherkin
Feature: [nombre de la feature en lenguaje de negocio]
  Como [rol del usuario]
  Quiero [accion]
  Para [beneficio]

  # HAPPY PATH — obligatorio
  Scenario: [descripcion del caso exitoso principal]
    Given [estado inicial del sistema]
    When [accion del usuario o evento]
    Then [resultado observable esperado]
    And [efecto secundario si aplica]

  # ESCENARIOS DE ERROR — minimo 1 obligatorio
  Scenario: [descripcion del error mas probable]
    Given [condicion que provoca el error]
    When [accion del usuario]
    Then [mensaje de error especifico]
    And [estado del sistema tras el error]

  # CASOS BORDE — minimo 1 obligatorio
  Scenario Outline: [variacion de inputs]
    Given [estado con "<variable>"]
    When [accion]
    Then [resultado para "<resultado>"]

    Examples:
      | variable | resultado |
      | <valor1> | <esperado1> |
      | <valor2> | <esperado2> |
      | <limite> | <esperado_limite> |
```

**Reglas de granularidad:**
- Maximo 8 escenarios por feature (si mas, el feature esta mal acotado — partir en sub-features)
- Maximo 5 pasos por escenario (Given/When/Then/And)
- Vocabulario exclusivamente del DOMAIN.md (Ubiquitous Language)
- Cada escenario referencia su REQ-NNN de trazabilidad en un comentario `# REQ-NNN`
- Los valores de Examples deben incluir: caso normal, caso limite inferior, caso limite superior, caso invalido

**Criterio de DoD de esta fase:**
- Cada feature tiene bloque Gherkin con 1 happy path + >=1 error + >=1 borde
- Todos los terminos en Gherkin existen en DOMAIN.md
- Matriz trazabilidad REQ-NNN <-> Scenario completa

## 3. FLUJO OPERATIVO (SINOPSIS)

El detalle técnico y operativo se encuentra en `skill-requirements-phase-details.md`.

### 3.1 Fase 1: Elicitación de Alta Resolución (Questionnaire GSD)

X-DD-Core inicia el cuestionario iterativo basado en GSD 1.0. Se generan preguntas hasta que el modelo mental del usuario sea < 5% ambiguo. Se investigan áreas críticas: Frontend, Backend, Seguridad e Infraestructura.

### 3.2 Fase 2: Auditoría y Sincronización

Validación de requisitos contra `Memoria/gsd/PROJECT.md`. Sincronización de contexto para asegurar que no hay conflictos de arquitectura.

### 3.3 Fase 3: Generación de PRD y REQUIREMENTS.md

Estructuración del PRD oficial y el archivo `Memoria/gsd/REQUIREMENTS.md`. X-DD-Core audita la trazabilidad y deposita los activos en `Memoria/`.

## 4. PROTOCOLO DE ACTIVOS

Los activos y entregables deben gestionarse según el estándar en `skill-workflow-asset-protocol.md`. El log de eventos se almacena en `tests/results/fase_requisitos_${runId}.ndjson`.

## 5. TEST TIERS DE REQUISITOS

| Tier | Tipo | Qué valida |
| :--- | :--- | :--- |
| **Tier 1** | Estático | Cumplimiento del Art. 1 (No ambigüedad), IDs únicos, MoSCoW. |
| **Tier 2** | Funcional | Consistencia interna entre requisitos y criterios de aceptación Gherkin. |
| **Tier 3** | LLM-Judge | Calidad semántica, alineación con la visión del usuario y KPIs. |

## 6. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `/x-dd` (Init Meta).
- **Sucesores:** `/plan-fases` (Roadmapping).
- **Skills Vinculadas:** `skill-requirements-elicitation`, `skill-prd-writing`, `skill-bdi-mental-states`.

---
**Versión:** 3.0.0 | **Fecha:** 2026-04-02
Desarrollado por X-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.