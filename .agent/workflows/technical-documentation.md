---
description: Ensure project documentation is always synchronized with the source code. Produce high-quality artifacts (Manuals, API Guides, Architecture) by prioritizing "Source Code as Truth" and enforcing a strictly textual, icon-free standard.
name: technical-documentation
trigger: /evol technical-documentation
---

# /technical-documentation

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-007 | **Versión:** 2.3.0
**Mission:** Ensure project documentation is always synchronized with the source code. Produce high-quality artifacts (Manuals, API Guides, Architecture) by prioritizing "Source Code as Truth" and enforcing a strictly textual, icon-free standard.


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/technical-documentation`
**Version:** 2.2.0
**Status:** ACTIVE

## 6. CONEXIONES DE INTEROPERABILIDAD (ART. 6)
- **Predecesores**: `/audit-planificador`
- **Sucesores**: `/qa-review`, `/vincular-obsidian`
- **Skills Vinculadas**: `skill-technical-documentation`, `skill-drawio-diagram-generator`, `skill-software-architect-gsd`, `skill-humanizer-gsd`

---

## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

- **Template-as-Source:** Metadata editing must occur in `.tmpl` files. Manual editing of final `.md` files is strictly prohibited.
- **CI Freshness Check:** Mandatory `gen-docs --dry-run` + `git diff --exit-code` verification in every PR.
- **No Iconography Policy:** Absolute prohibition of emojis, icons, or non-textual symbols in final artifacts. Documentation must remain strictly textual, professional, and technical.
- **Pure Text Standard:** Enforce a 0% emoji density. Any non-ASCII symbols must be validated as purely technical or mathematical notation.
- **NDJSON Quality Traces:** Documentation quality scores and generation logs must be recorded with a unique `runId`.

## 2. Evol-DD CORE CONTROL DOMAINS

### 2.1 Quality Gate (Governance)

- Orchestrates the extraction of technical metadata from source code.
- Enforces the "Git Freshness" standard and "No Iconography" policy.
- Validates the resolution of all technical placeholders.

### 2.2 Delegation (Operations)

- **Architecture Swarm (02):** Assigned as "Technical Designer" to generate core documentation.
- **Analysis Swarm (01):** Specialized skill for metadata extraction and context mapping.
- **Consolidation Swarm (05):** Assigned as "Vault Manager" for Obsidian synchronization.
- **Operational Detail:** `skill-technical-documentation-details`.

## 3. ASSET PROTOCOL (NDJSON)

- **Input:** Source Code, PRD.md, SAD.md, skill templates.
- **Output:** SKILL.md, user_manual.md, api_guide.md, NDJSON documentation traces.

## 4. OPERATIONAL FLOW

| Phase | Actor | Action | Standard |
| :--- | :--- | :--- | :--- |
| **I. Knowledge Extraction** | Orchestrator | Scans `/src/` to update metadata maps. | Art. 1 (Const.) |
| **II. Document Generation** | Subagente 02 | Generación de las 13 secciones de ingeniería (S01-S13) y diagramas UML/C4. Aplicación de "No Iconography". | `skill-technical-documentation-details`, `skill-drawio-diagram-generator`, `skill-software-architect-gsd` |
| **III. Humanizer Pass** | Humanizer Agent | Revisión y filtrado de los 25 patrones Anti-AI para asegurar tono profesional/experto. | `skill-humanizer-gsd` |
| **IV. CI Check** | Orchestrator | Verifies "Git Freshness", absence of icons and documentation traceability (RTM). | Tier 1 Testing |
| **V. Vault Sync** | Subagente 05 | Synchronizes final documents with Obsidian. | skill-obsidian-manager |
| **VI. Teardown** | Orchestrator | Context destruction and artifact archival. | Art. 7.3 (Const.) |

## 5. RECOVERY & ERRORS (NDJSON)

- **[ERR-001]:** Placeholder Resolution Failure -> Block commit and issue repair task.
- **[ERR-002]:** Iconography Detected -> Reject document and trigger sanitization swarm.
- **[ERR-003]:** Obsidian Sync Error -> Exponential backoff x3 followed by local cache.

## 6. METRICS & OBSERVABILITY (SLIs)

- **Doc Freshness Index:** % of code changes reflected in docs within 1 cycle.
- **Iconography Density:** Must be exactly 0%.
- **Link Integrity:** % of non-broken internal documentation links.

---
**Next Step:** See `skill-technical-documentation-details.md` for generation architecture, placeholders, and test tiers.


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.