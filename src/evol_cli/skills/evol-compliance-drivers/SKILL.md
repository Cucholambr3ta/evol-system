---
name: evol-compliance-drivers
description: Compliance-Driven Development — SOC 2, ISO 27001, HIPAA, regulatory compliance
category: discipline-extended
trigger: /compliance-drivers
---

# evol-compliance-drivers

## Fase del Pipeline

**Spec (Fase 2) — Especificación y Diseño**

Activar cuando se necesita cumplimiento regulatorio:
- SOC 2 Type II controls
- ISO 27001 Annex A controls
- HIPAA safeguards
- Regulatory compliance mapping

## Artefacto Clave

**`docs/compliance/COMPLIANCE_REPORT.md`**

```markdown
# Compliance Report

## Framework: SOC 2 Type II

### Control Mapping
| Control | Category | Status | Evidence | Owner |
|---------|----------|--------|----------|-------|
| CC6.1 | Logical Access | Implemented | IAM policies | Security |
| CC6.8 | Malware | Implemented | Endpoint protection | IT |
| CC7.1 | Monitoring | Implemented | SIEM alerts | SOC |

### Gaps Identified
| Gap | Risk Level | Remediation | Target Date |
|-----|------------|-------------|-------------|
| No MFA on admin accounts | High | Enable MFA | 2026-07-01 |

### Evidence Collection
- Access logs: `/var/log/auth.log`
- Change logs: GitHub audit trail
- Monitoring: Datadog dashboards
```

## Flujo de Trabajo

```bash
# 1. Identificar framework aplicable
python3 scripts/compliance/identify-framework.py \
  --industry fintech \
  --region eu \
  --output docs/compliance/APPLICABLE_FRAMEWORKS.md

# 2. Generar mapeo de controles
python3 scripts/compliance/map-controls.py \
  --framework soc2 \
  --source . \
  --output docs/compliance/CONTROL_MAP.md

# 3. Ejecutar assessment
python3 scripts/compliance/assess.py \
  --framework soc2 \
  --source . \
  --output docs/compliance/COMPLIANCE_REPORT.md

# 4. Validar evidencia
python3 scripts/compliance/validate-evidence.py \
  --report docs/compliance/COMPLIANCE_REPORT.md \
  --output docs/compliance/EVIDENCE_STATUS.md

# 5. Generar remediation plan
python3 scripts/compliance/remediation.py \
  --report docs/compliance/COMPLIANCE_REPORT.md \
  --output docs/compliance/REMEDIATION_PLAN.md

# 6. Dashboard de compliance
python3 scripts/compliance/dashboard.py \
  --report docs/compliance/COMPLIANCE_REPORT.md \
  --output dashboards/compliance-overview.json
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Compliance requirements | Frameworks identificados | No |
| Spec | Control mapping | Controles mapeados | Sí |
| Plan | Gap remediation | Plan de remediación | No |
| Build | Controls implemented | Controles en código | Sí |
| QA | Evidence collection | Evidencia verificada | Sí |
| Retro | Compliance status | Estado documentado | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Spec del Pipeline
- **Discipline Doc** — `docs/disciplines/Compliance_Drivers.md`
- **SOC 2 Trust Principles** — https://us.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report
- **ISO 27001 Controls** — https://www.iso.org/iso-27001-information-security.html
