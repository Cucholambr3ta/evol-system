---
description: Implement a template-driven documentation system (gstack pattern) to eliminate divergence between skill implementation (code) and documentation (SKILL.md).
name: skill-template-generator
trigger: /evol skill-template-generator
---

# /skill-template-generator

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-000 | **Versión:** 2.3.0
**Mission:** Implement a template-driven documentation system (gstack pattern) to eliminate divergence between skill implementation (code) and documentation (SKILL.md).


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/skill-template-generator`
**Version:** 2.2.0
**Status:** ACTIVE

---

## 1. STRATEGIC DIRECTIVES

- **Code as Single Source of Truth:** Documentation is an automated structural consequence of the code.
- **Template-First:** `SKILL.md` is a generated artifact; manual edits are prohibited.
- **CI Freshness Gate:** PRs are blocked if documentation is out of sync with code (enforced via `--validate-only`).
- **Fail-Fast Resolution:** Generation must abort if placeholders cannot be resolved from `metadata.json`.
- **Zero Drift:** Maintain 100% alignment between command signatures and documentation.

## 2. X-DD CORE CONTROL DOMAINS

### 2.1 Quality Gate (Governance)
- Validates that all new skills provide a valid `SKILL.md.tmpl` and `metadata.json`.
- Enforces documentation quality via Tier 3 (LLM-as-judge) during releases.
- Monitors "Skill Freshness" metrics across the ecosystem.

### 2.2 Delegation (Operations)
- **Technical Design/Docs:** `02_Disenador_Tecnico`.
- **Vault/Storage Gate:** `05_Gestor_Boveda`.
- **Operational Detail:** `skill-template-details`.

## 3. ASSET PROTOCOL

- **Input:** `SKILL.md.tmpl`, `metadata.json`, `fixtures/*.json`.
- **Output:** Generated `SKILL.md`, NDJSON traces, Freshness reports.

## 4. OPERATIONAL FLOW

| Phase | Actor | Action | Standard |
| :--- | :--- | :--- | :--- |
| **I. Creation** | Agente 02 | Scaffolds directory and template structure. | `skill-template-details` |
| **II. Sync** | Agente 02 | Executes `gen-skill-docs` to update `.md` y aplica el filtro `skill-humanizer-gsd`. | Template Logic |
| **III. Validation** | Agente 04 | Runs Tier 1 (Syntax) and Tier 2 (Semantic) + Calidad de Ingeniería (S01-S13). | Tiered Testing |
| **IV. Audit** | Agente 02 | Global validation of all skills (freshness report).| `skill-template-details` |
| **V. Closure** | Orchestrator | Records resultados en `tests/results/` y sincroniza con el Vault. | NDJSON / Obsidian |

## 5. RECOVERY & ERRORS (NDJSON)

- **[ERR-001]:** Placeholder Resolution Failure -> Identify missing key in `metadata.json`.
- **[ERR-002]:** `metadata.json` Schema Violation -> Validate against official skill schema.
- **[ERR-003]:** Documentation Drift in CI -> Run local sync and commit results.

## 6. METRICS & OBSERVABILITY (SLIs)

- **Generation Latency:** Time to sync all skill docs.
- **Drift Frequency:** Number of PRs blocked by documentation stale state.
- **Tier 3 Quality Score:** Average LLM evaluation of generated content (Target: > 4/5).
- **Mandato Art. 6:** Toda nueva skill debe declarar sus conexiones en el Grafo Maestro.

## 7. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `FLUJO_072` (Integración Capacidades).
- **Sucesores:** `FLUJO_007` (Technical Documentation).
- **Skills Vinculadas:** `skill-template-details`, `skill-capability-orchestrator`.

---
**Next Step:** See `skill-template-details.md` for directory mapping, placeholder resolution, and script usage.


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.