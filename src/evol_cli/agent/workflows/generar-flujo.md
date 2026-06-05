---
description: Genera workflows Evol-DD personalizados con frontmatter, pasos, agentes y criterios de salida.
name: generar-flujo
trigger: /evol generar-flujo
---

# /generar-flujo

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.

**ID:** S-GENERADOR-FLUJOS | **Versión:** 2.3.0 | **Nivel:** Sistema / Investigación
**Mission:** Estandarizar y automatizar la creación de nuevos flujos de trabajo en el ecosistema, asegurando el cumplimiento de la nomenclatura establecida en el Artículo 10 y la estructura de metadatos de Antigravity.

**Orquestador:** Orchestrator (ID: 00)
**Asistentes Operativos (Swarm):** Swarm de Arquitectura (01)
**Skills Requeridas:** `skill-identity-context.md`, `skill-project-architect.md`
**MCPs Obligatorios:** `core`
**Entorno:** Local Hub
**Cultura:** Investigación · Aislamiento · Mejora Continua


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

- **Consulta de Categoría (Art. 10.2)**: Es obligatorio preguntar al usuario si el flujo es `General` o de `Sistema` antes de su creación.
- **Continuidad Numérica**: Los flujos generales deben mantener la numeración correlativa `FLUJO_XXX`.
- **Estructura Densa .gemini**: Todo archivo generado debe incluir el bloque completo de metadatos (Mission, Orquestador, etc.).
- **Privacidad S_**: Los flujos `S_` están excluidos de las actualizaciones públicas por el Artículo 10.3.

## 2. Evol-DD CORE CONTROL DOMAINS

### 2.1 Governance & Taxonomy
- Orchestrator aprueba la asignación de IDs de sistema `S-` para evitar colisiones con el índice global.

## 3. FLUJO OPERATIVO (RESUMEN)

1. **Definición**: Captura de slug y categoría mediante el orquestador.
2. **Generación**: Ejecución de \`scripts/create_workflow.sh\` con el template alineado.
3. **Registro**: Alta en \`CORE_REGISTRY.md\` y sincronización con el Vault.

## 4. PROTOCOLO DE ASSETS OBLIGATORIOS

Referencia: \`skill-workflow-asset-protocol.md\`.

| Activo | Tipo | Origen | Destino/Uso |
| :--- | :--- | :--- | :--- |
| \`NEW_WORKFLOW\` | Markdown | Sistema | \`workflows/\` o \`global_workflows/\` |
| \`GEN_LOG\` | Log NDJSON | Sistema | \`tests/results/gen_workflow_\${runId}.ndjson\` |

## 5. RESULTADOS ESPERADOS (NDJSON)

| Evento | Atributos | Propósito |
| :--- | :--- | :--- |
| \`workflow_generated\` | \`workflow_id\`, \`category\` | Registro de creación de capacidad. |

## 6. GESTIÓN DE ERRORES (RESUMEN)

- **Colisión de IDs**: Orchestrator detiene la operación si el ID ya existe en el registro.
- **Error de Script**: Reportar fallo en la generación del archivo y revertir cambios en el registro.

## 7. TEST TIERS (Validación)

| Tier | Tipo | Validación |
| :--- | :--- | :--- |
| **Tier 1** | **Estático** | Verificación de que el archivo .md se creó correctamente. |
| **Tier 2** | **Funcional** | El nuevo workflow es detectable por el sistema. |
| **Tier 3** | **Calidad (Judge)** | LLM valida que la Mission del nuevo flujo sea coherente con su slug. |

## 8. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** [/evol]
- **Sucesores:** [Workflow Creado], [/quality_validation]
- **Skills Vinculadas:** \`skill-identity-context\`, \`skill-project-architect\`

---
**Versión:** 2.3.0 | **Fecha:** 2026-03-20
Desarrollado por Evol-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.