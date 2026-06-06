# Comandos de CALIDAD_SEGURIDAD

Listado granular de todos los triggers pertenecientes al dominio **CALIDAD_SEGURIDAD**.

---

### `/evol a11y-audit`
**Archivo:** `.agent/workflows/a11y-audit.md`

**Descripción:**
Auditoría de accesibilidad WCAG 2.1 AA. Automatizada en CI + revisión humana de flujos críticos.

---

### `/evol advanced-agentic-pentesting`
**Archivo:** `.agent/workflows/advanced-agentic-pentesting.md`

**Descripción:**
Workflow advanced-agentic-pentesting

---

### `/evol contract-test`
**Archivo:** `.agent/workflows/contract-test.md`

**Descripción:**
Tests de contrato consumer-driven (Pact) en Fase 5. Verifica compatibilidad entre servicios.

---

### `/evol cross-validate`
**Archivo:** `.agent/workflows/cross-validate.md`

**Descripción:**
Detecta drift entre pares de artefactos (MISSING/CONFLICT/ORPHAN). Bloquea gate si MISSING o CONFLICT. Inspirado en Spec-Kit /cross-validate.

---

### `/evol fact-check`
**Archivo:** `.agent/workflows/fact-check.md`

**Descripción:**
Pipeline de 11 pasos (SIFT + CRAAP + MFS scoring) para verificar claims externos antes de incorporarlos al proyecto. Produce Fact-Check Report con veredicto auditado. Usa skill evol-fact-check.

---

### `/evol generate-unit-tests`
**Archivo:** `.agent/workflows/generate-unit-tests.md`

**Descripción:**
Automatically generate unit tests with mocks for existing code modules, aiming for a minimum 80% coverage and strict adherence to architectural contracts.

---

### `/evol grill-me`
**Archivo:** `.agent/workflows/grill-me.md`

**Descripción:**
Stress-test de planes, diseños o decisiones técnicas mediante interrogatorio sistemático rama a rama. Usa skill evol-grill-me. Complementa /clarify y /brainstorm.

---

### `/evol ml-eval`
**Archivo:** `.agent/workflows/ml-eval.md`

**Descripción:**
Evaluación sistemática de modelos ML/LLM. Datasets dorados, métricas, drift detection, A/B.

---

### `/evol perf-budget`
**Archivo:** `.agent/workflows/perf-budget.md`

**Descripción:**
Establece y verifica presupuestos de performance (CWV, bundle size, latencias) en CI.

---

### `/evol privacy-review`
**Archivo:** `.agent/workflows/privacy-review.md`

**Descripción:**
Inventario de PII, bases legales y procedimientos GDPR/CCPA. Produce PRIVACY.md.

---

### `/evol pruebas-fuzz`
**Archivo:** `.agent/workflows/pruebas-fuzz.md`

**Descripción:**
Ejecución de pruebas destructivas mediante inyección de datos malformados en sandboxes aislados, garantizando la robustez y seguridad ante entradas inesperadas.

---

### `/evol pruebas-humo`
**Archivo:** `.agent/workflows/pruebas-humo.md`

**Descripción:**
Smoke tests post-deploy para paths críticos. Detecta regresiones en menos de 5 minutos.

---

### `/evol qa-review`
**Archivo:** `.agent/workflows/qa-review.md`

**Descripción:**
Ejecución de revisión por pares concurrente y validación estratificada (Tiers 1-3) para garantizar la excelencia técnica y estética antes de la entrega.

---

### `/evol security-audit`
**Archivo:** `.agent/workflows/security-audit.md`

**Descripción:**
Perform an exhaustive security audit (SAST/DAST/SCA) simulating controlled attacks in an isolated sandbox to identify and mitigate vulnerabilities before exploitation.

---

### `/evol stress-test`
**Archivo:** `.agent/workflows/stress-test.md`

**Descripción:**
Subject the system to extreme load conditions to determine its breaking point and validate non-functional requirements (SLA/SLOs) within an isolated sandbox.

---

