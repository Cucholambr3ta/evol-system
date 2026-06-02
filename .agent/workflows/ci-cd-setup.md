---
description: Automate the configuration of the CI/CD pipeline, establishing a continuous delivery environment that ensures code quality, security, and visual compliance. In version 2.2.0, it enforces "Deployment Interoperability" (Art. 6) to ensure cross-environment synchronization.
---

# /ci-cd-setup

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-000 | **Versión:** 2.3.0
**Mission:** Automate the configuration of the CI/CD pipeline, establishing a continuous delivery environment that ensures code quality, security, and visual compliance. In version 2.2.0, it enforces "Deployment Interoperability" (Art. 6) to ensure cross-environment synchronization.


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/ci-cd-setup`
**Version:** 2.2.0 (2026-03-20)
**Status:** ACTIVE

---

## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

- **Gated Deployment:** Merge to `main` is prohibited without a full PASS from the Tiered Testing system.
- **Security Check Mandatory:** The pipeline MUST fail if critical vulnerabilities are detected (Art. 6).
- **Coverage Minimum:** Automated validation that unit/integration coverage is >= 80%.
- **NDJSON Accountability:** All pipeline configuration events and validation results must be logged with a unique `runId`.

## 2. ZENITH CONTROL DOMAINS

### 2.1 Quality Gate (Infrastructure)
- Defines the QA Tiers and environment isolation rules.
- Manages the lifecycle of CI/CD secrets and branch protection policies.
- Validates the overall health and readiness of the deployment pipeline.

### 2.2 Delegation (Operations)
- **Design Swarm (02):** Assigned to design the pipeline structure and YAML workflows.
- **QA Swarm (04):** Assigned to validate the pipeline via smoke tests and compliance checks.
- **Operational Detail:** `skill-cicd-setup-details`.

## 3. ARTÍCULO 6: INTEROPERABILIDAD

La automatización del pipeline es el motor de la entrega continua:

* **Conector `TASK-PIPELINE` (`FLUJO-055`)**: El CI/CD se activa automáticamente al final de la fase de validación del pipeline core.
* **Conector `DEPLOY-SYNC` (`FLUJO-018`)**: Provee la infraestructura validada necesaria para el despliegue final en producción.
* **Conector `SEC-AUDIT` (`FLUJO-015`)**: Consume reglas de seguridad dinámicas para integrarlas como "Breaking Gates" en el CI.

## 4. ASSET PROTOCOL (NDJSON)

- **Input:** Infrastructure requirements, security policies, environment secrets.
- **Output:** CI/CD YAML workflows, Environment Config, NDJSON infrastructure traces.

## 5. OPERATIONAL FLOW

| Phase | Actor | Action | Standard |
| :--- | :--- | :--- | :--- |
| **I. Pipeline Design** | Subagente 02 | Configures Tiers in `.planning/config.json`. | Art. 6.3 (Const.) |
| **II. Env Provisioning** | Zenith | Creates Staging/Prod environments and keys. | `skill-cicd-setup-details` |
| **III. Pipeline Validation** | Subagente 04 | Executes smoke tests and security scan. | Tiered Testing |
| **IV. Handover** | Zenith | Formal availability certification and logging. | Asset Protocol |
| **V. Teardown** | Zenith | ephemeral context destruction. | Art. 7.3 (Const.) |

## 6. RECOVERY & ERRORS (NDJSON)

- **[ERR-001]:** Secret Propagation Failure -> Trigger secure rotation and retry.
- **[ERR-002]:** Runner Dependency Missing -> Issue infrastructure update task.
- **[ERR-003]:** Compliance Violation -> Block pipeline activation and alert Zenith.

## 7. METRICS & OBSERVABILITY (SLIs)

- **Pipeline Availability:** % of time the CI/CD pipeline is in a healthy state.
- **Setup Latency:** Time from Phase 1 start to full certification.
- **Gate Fidelity:** Ratio of blocked vs. bypassed compliance checks.

---
**Next Step:** See `skill-cicd-setup-details.md` for specific QA tiers, YAML structures, and NDJSON schemas.


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.