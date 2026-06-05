---
description: Transform raw or existing prompts into optimized, structured versions compliant with Evol-DD standards. Version 2.2.0 integrates "Meta-Interoperability" (Art. 6) to ensure prompts can call other workflows seamlessly.
name: mejorar-prompt
trigger: /evol mejorar-prompt
---

# /mejorar-prompt

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-000 | **Versión:** 2.3.0
**Mission:** Transform raw or existing prompts into optimized, structured versions compliant with Evol-DD standards. Version 2.2.0 integrates "Meta-Interoperability" (Art. 6) to ensure prompts can call other workflows seamlessly.


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/mejorar-prompt`
**Version:** 2.2.0 (2026-03-20)
**Status:** ACTIVE

---

## 1. STRATEGIC DIRECTIVES

- **Prompt as Code:** Treat every prompt as a technical contract with defined inputs, logic, and outputs.
- **Structural Integrity:** Mandatory inclusion of all constitutional sections (Metadata, Mission, Flow, NDJSON, Art. 6).
- **Ambiguity Filter:** Apply Article 1 (Zero Vagueness) before any rewriting process.
- **Zero Context Rot:** Destroy the prompt-engineer agent after task completion; persist only the optimized artifact.
- **Tiered Validation:** Every optimization must pass a Tier 3 (LLM-as-judge) quality assessment.

## 2. Evol-DD CORE CONTROL DOMAINS

### 2.1 Quality Gate (Governance)
- Identifies the prompt type (Agent, Workflow, Skill) and selects the appropriate template.
- Enforces the inclusion of the NDJSON observability protocol and Article 6 connections.

### 2.2 Delegation (Operations)
- **Prompt Engineer (18):** `18_Prompt_Engineer` (or Orchestrator).
- **Structural Analysis:** `skill-structural-analysis`.
- **Operational Detail:** `skill-mejorar-prompt-details`.

## 3. ARTÍCULO 6: INTEROPERABILIDAD

La optimización de prompts es la base del razonamiento sistémico:

* **Conector `SKILL-ORCH` (`CAPABILITY-ORCHESTRATOR`)**: Todo nuevo prompt de skill debe integrarse en la lógica de descubrimiento y orquestación global.
- **Conector `FLOW-INTEG` (`FLUJO-072`)**: Los prompts de nuevos workflows deben incluir los contratos de entrada/salida para su integración en el índice maestro.
* **Conector `KNOW-MAP` (`FLUJO-059`)**: Los cambios en la lógica de los prompts se documentan en el Vault para mantener la memoria operativa.

## 4. ASSET PROTOCOL

- **Input:** Raw prompt text or file, Type metadata.
- **Output:** Optimized Prompt file, NDJSON optimization traces.

## 5. OPERATIONAL FLOW

| Phase | Actor | Action | Standard |
| :--- | :--- | :--- | :--- |
| **I. Identification** | Orchestrator | Classifies prompt and applies Ambiguity Filter. | Article 1 (Const.) |
| **II. Optimization** | Agente 18| Applies template v2.2.0 and technical rewriting.| `skill-mejorar-prompt-details`|
| **III. Validation** | Orchestrator/QA | Executes Tier 1 (Syntax) and Tier 3 (Semantic). | Tiered Testing |
| **IV. Consolidate** | Orchestrator | Records in NDJSON and saves file in `/prompts/`. | NDJSON Protocol |
| **V. Closure** | Orchestrator | Notifies Human and destroys temporary context. | Article 7.3 (Const.) |

## 6. RECOVERY & ERRORS (NDJSON)

- **[ERR-001]:** High Ambiguity found -> Invoke Clarification Protocol (Art. 1).
- **[ERR-002]:** Unknown Prompt Type -> Apply Generic Template v2.2.0.
- **[ERR-003]:** Tier 3 Failure < 0.9 Clarity -> Automatic retry with temperature adjustment.

## 7. METRICS & OBSERVABILITY (SLIs)

- **Clarity Delta:** Qualitative and quantitative increase in Clarity Index.
- **Adherence Rate:** Percentage of mandatory sections successfully included.
- **Optimization Time:** Latency from raw input to final production-ready prompt.

---
**Next Step:** See `skill-mejorar-prompt-details.md` for template taxonomies, structural rules, and QA thresholds.


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.