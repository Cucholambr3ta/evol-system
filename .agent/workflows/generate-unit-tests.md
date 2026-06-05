---
description: Automatically generate unit tests with mocks for existing code modules, aiming for a minimum 80% coverage and strict adherence to architectural contracts.
name: generate-unit-tests
trigger: /evol generate-unit-tests
---

# /generate-unit-tests

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-000 | **Versión:** 2.3.0
**Mission:** Automatically generate unit tests with mocks for existing code modules, aiming for a minimum 80% coverage and strict adherence to architectural contracts.


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/generate-unit-tests`
**Version:** 2.1.2 (2026-03-17)
**Status:** ACTIVE

---

## 1. STRATEGIC DIRECTIVES

- **Contract-Based Testing:** Tests must validate behavior against `SAD.md` and `PRD.md`.
- **Inverse TDD:** Use these tests as a safety net before any refactoring.
- **Coverage Mandatory (Art. 6.3):** Minimum 80% coverage goal.
- **ReadOnly Production:** Agents cannot modify the production source code during this flow.
- **Zero Context Rot:** Temporary generator agents are destroyed post-execution.
- **Human Gate:** Plan approval is mandatory before mass generation.

## 2. Evol-DD CORE CONTROL DOMAINS

### 2.1 Quality Gate (Governance)
- Approves the test generation plan.
- Validates the coverage report and accuracy of detected bugs.
- Authorizes committing the generated tests to the repository.

### 2.2 Delegation (Operations)
- **Primary:** `03_Ejecutor_Asincrono` (Generator Mode).
- **Secondary:** `04_Swarm_QA` (Coverage & Consistency Validation).
- **Technical Detail:** `skill-unit-test-details`.

## 3. ASSET PROTOCOL

- **Input:** Target module path, `SAD.md`, `PRD.md`, Framework config.
- **Output:** Generated test files, `test_generation_report.md`, and NDJSON traces.

## 4. OPERATIONAL FLOW

| Phase | Actor | Action | Standard |
| :--- | :--- | :--- | :--- |
| **I. Analysis** | Orchestrator | Scans module, extracts contracts and interfaces. | `skill-unit-test-details` |
| **II. Planning** | Orchestrator | Presents test plan and scenarios to Human. | **Gate: Approval** |
| **III. Generation** | Subagent | Creates test files with mocks. | English Naming |
| **IV. Execution** | Subagent | Runs the suite and calculates coverage. | Tiered Testing |
| **V. Refinement** | Subagent | Fixes failing tests or improves coverage. | SLI Thresholds |
| **VI. Reporting** | Orchestrator | Delivers final report and requests commit auth. | NDJSON Schema |

## 5. RECOVERY & ERRORS (NDJSON)

- **[ERR-001]:** Missing target module -> Terminate and notify.
- **[ERR-002]:** Missing test framework -> Provide installation instructions.
- **[ERR-003]:** Unstable tests -> Max 3 retries for automated fixes.

## 6. METRICS & OBSERVABILITY (SLIs)

- **Coverage Success:** Final coverage vs. 80% target.
- **Generation Time:** End-to-end latency per module.
- **Bug Discovery:** Number of production bugs uncovered by new tests.

---
**Next Step:** See `skill-unit-test-details.md` for mocking strategies and test matrices.


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.