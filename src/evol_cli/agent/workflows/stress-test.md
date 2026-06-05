---
description: Subject the system to extreme load conditions to determine its breaking point and validate non-functional requirements (SLA/SLOs) within an isolated sandbox.
name: stress-test
trigger: /evol stress-test
---

# /stress-test

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-000 | **Versión:** 2.3.0
**Mission:** Subject the system to extreme load conditions to determine its breaking point and validate non-functional requirements (SLA/SLOs) within an isolated sandbox.


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/stress-test`
**Version:** 2.1.2 (2026-03-17)
**Status:** ACTIVE

---

## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

* **Total Isolation:** Execution MUST be restricted to ephemeral Docker sandboxes; never in production or shared environments.
* **Gradual Loading:** Tests must start at 10% theoretical load and scale progressively.
* **Zero Regression Policy:** Stress testing must not corrupt data integrity or persistent state.
* **NDJSON Accountability:** All performance metrics must be logged with high-resolution traceability.

## 2. Evol-DD CORE CONTROL DOMAINS

### 2.1 Performance & Reliability Gate

* Validates that the "Breaking Point" is above the required SLA.
* Certifies resource efficiency (CPU/RAM/IO) under peak load conditions.

### 2.2 Delegation (Operations)

* **QA Swarm (04):** Assigned to load generation, monitoring instrumentation, and bottleneck analysis.
* **Consolidation Swarm (05):** Assigned to performance reporting and NDJSON log sealing.
* **Operational Detail:** `skill-stress-testing-details`.

## 3. ASSET PROTOCOL (NDJSON)

* **Input:** Target Topology, Load Profiles, SLA Requirements, Sandbox Config.
* **Output:** Stress Test Report, Performance Dashboards, `stress_metrics.ndjson`.

## 4. OPERATIONAL FLOW

| Phase | Actor | Action | Standard |
| :--- | :--- | :--- | :--- |
| **I. Sandbox Setup** | Subagente 04 | Ephemeral cluster deployment and architecture freezing. | `skill-stress-testing-details` |
| **II. Instrumentation** | Subagente 04 | Activation of monitoring stacks (Prometheus/Grafana). | Real-time Observability |
| **III. Load Execution** | Subagente 04 | Progressive Scaling, Soak Test, and Spike Test. | Load Profile Standard |
| **IV. Analysis** | Orchestrator | Bottleneck identification and Breaking Point certification. | SLA Compliance |
| **V. Sync & Cierre** | Subagente 05 | Report archival and environment teardown. | Asset Protocol |

## 5. RECOVERY & ERRORS (NDJSON)

* **[ERR-014-01]:** Breaking Point < SLA -> FAIL. Block deployment and trigger optimization audit.
* **[ERR-014-02]:** Sandbox Instability -> Restart environment and verify Docker daemon logs.
* **[ERR-014-03]:** Memory Leak Detected -> Document trace and generate refactoring ticket (Swarm 03).

## 6. METRICS & OBSERVABILITY (SLIs)

* **Throughput Capacity:** Max requests per second before latency degradation.
* **Error Rate under Load:** % of failed requests at 95% load capacity.
* **Recovery Time:** Duration to return to baseline latency after stress cessation.

---
**Next Step:** See `skill-stress-testing-details.md` for specific K6/Locust scripts and sandbox templates.


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.