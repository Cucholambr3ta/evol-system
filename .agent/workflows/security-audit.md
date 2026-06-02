---
description: Perform an exhaustive security audit (SAST/DAST/SCA) simulating controlled attacks in an isolated sandbox to identify and mitigate vulnerabilities before exploitation.
---

# /security-audit

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-000 | **Versión:** 2.2.0
**Mission:** Perform an exhaustive security audit (SAST/DAST/SCA) simulating controlled attacks in an isolated sandbox to identify and mitigate vulnerabilities before exploitation.


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/security-audit`
**Version:** 2.1.2 (2026-03-17)
**Status:** ACTIVE

---

## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

* **Isolated Hacking:** Execution MUST be restricted to sterile Docker sandboxes; zero access to production data or credentials.
* **PII Masking:** Any data used for testing must be anonymized or synthetic.
* **NDJSON Veracity:** Atomic recording of every vulnerability trace is mandatory.
* **Zero Trust Validation:** Semantic validation (Tier 3) of complex attack vectors (Logic Flaws, Prompt Injection).

## 2. X-DD CORE CONTROL DOMAINS

### 2.1 Security & Compliance Gate

* Certifies that the system is free of "Critical" and "High" vulnerabilities.
* Validates adherence to X-DD Secure Coding Standards and OWASP Top 10.

### 2.2 Delegation (Operations)

* **Security Swarm (04):** Assigned to vulnerability scanning, automated penetration testing, and risk assessment.
* **Consolidation Swarm (05):** Assigned to final security reporting and asset sealing.
* **Operational Detail:** `skill-security-audit-details`.

## 3. ASSET PROTOCOL (NDJSON)

* **Input:** Source Code Repository, Container Images, Network Topology, Compliance Requirements.
* **Output:** Confidential Security Report, Remediation Backlog, `vulnerability_traces.ndjson`.

## 4. OPERATIONAL FLOW

| Phase | Actor | Action | Standard |
| :--- | :--- | :--- | :--- |
| **I. Sandbox Prep** | Subagente 04 | Deployment of sterile Docker environment and PII masking. | `skill-security-audit-details` |
| **II. Static Analysis** | Subagente 04 | SAST, SCA, and Secret Scanning execution. | Secure Coding Tier 1 |
| **III. Dynamic Analysis** | Subagente 04 | DAST (OWASP ZAP) and fuzzing in active environment. | Hacking Ethics Tier 2 |
| **IV. Red Teaming** | X-DD | Semantic validation of complex vulnerabilities and logic flaws. Link to `FLUJO_062_advanced-agentic-pentesting` using **Shannon AI (Gemini)** for automated POC. | `skill-autonomous-exploitation` |
| **V. Reporting** | Subagente 05 | Severity classification and confidential report archival. | Asset Protocol |

## 5. RECOVERY & ERRORS (NDJSON)

* **[ERR-015-01]:** Critical Vulnerability Found -> FAIL. Block deployment and initiate immediate remediation audit.
* **[ERR-015-02]:** Sandbox Contamination -> Reset environment and verify isolation layer integrity.
* **[ERR-015-03]:** Scanning Timeout -> Adjust depth or allocate more resources; document restricted scope.

## 6. METRICS & OBSERVABILITY (SLIs)

* **Vulnerability Density:** Number of findings per 1k lines of code.
* **Mean Time to Detection (MTTD):** Duration of the audit cycle.
* **Scan Coverage:** % of codebase and dependencies analyzed by the toolkit.
* **Mandato Art. 6:** Las brechas detectadas deben actualizar el backlog de seguridad en `proyecto/interop/`.

## 7. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `FLUJO_010` (QA Review), `FLUJO_056` (Quality Validation).
- **Sucesores:** `FLUJO_062` (Advanced Pentesting), `FLUJO_028` (Cumplimiento).
- **Skills Vinculadas:** `skill-security-auditor`, `skill-agentic-sast-reasoning`, `skill-autonomous-exploitation`.

---
**Next Step:** Consult `skill-security-audit-details.md` for specific tool configurations (Semgrep, Snyk, ZAP, Shannon).


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.