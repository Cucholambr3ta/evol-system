---
name: evol-privacy-drivers
description: PrivacyDD — Privacy by Design, GDPR, data minimization, privacy impact assessment
category: discipline-extended
trigger: /privacy-drivers
---

# evol-privacy-drivers

## Fase del Pipeline

**Spec (Fase 2) — Especificación y Diseño**

Activar cuando se necesita privacidad y protección de datos:
- GDPR compliance
- Data minimization principles
- Privacy Impact Assessment (PIA)
- Data flow mapping

## Artefacto Clave

**`docs/compliance/PRIVACY_REVIEW.md`**

```markdown
# Privacy Review

## Data Processing Inventory
| Data Type | Purpose | Legal Basis | Retention | Location |
|-----------|---------|-------------|-----------|----------|
| Email | Authentication | Consent | 2 years | EU |
| IP Address | Security | Legitimate interest | 30 days | EU |
| Payment | Transaction | Contract | 7 years | EU |

## Data Flow Map
```
User → API Gateway → Auth Service → Database
         ↓
      Analytics (anonymized)
         ↓
      Third Party (Stripe)
```

## Privacy Impact Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data breach | Low | High | Encryption at rest + transit |
| Unauthorized access | Medium | High | RBAC + MFA |

## GDPR Compliance
- [ ] Right to access implemented
- [ ] Right to erasure implemented
- [ ] Data portability supported
- [ ] Consent management active
```

## Flujo de Trabajo

```bash
# 1. Descubrir datos personales
python3 scripts/privacy/discover-data.py \
  --source . \
  --output docs/compliance/DATA_INVENTORY.md

# 2. Mapear flujos de datos
python3 scripts/privacy/map-dataflows.py \
  --source . \
  --output docs/compliance/DATA_FLOW_MAP.md

# 3. Generar PIA
python3 scripts/privacy/generate-pia.py \
  --inventory docs/compliance/DATA_INVENTORY.md \
  --output docs/compliance/PRIVACY_REVIEW.md

# 4. Validar GDPR compliance
python3 scripts/privacy/validate-gdpr.py \
  --pia docs/compliance/PRIVACY_REVIEW.md \
  --output docs/compliance/GDPR_CHECKLIST.md

# 5. Detectar PII en código
python3 scripts/privacy/detect-pii.py \
  --source src/ \
  --output docs/compliance/PII_DETECTION.md

# 6. Generar reporte de privacidad
python3 scripts/privacy/privacy-report.py \
  --pia docs/compliance/PRIVACY_REVIEW.md \
  --output docs/compliance/PRIVACY_REPORT.md
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Privacy requirements | Datos personales identificados | No |
| Spec | PIA completada | PIA documentada | Sí |
| Plan | Minimización | Datos mínimos definidos | No |
| Build | Privacy controls | Encriptación + anonimización | Sí |
| QA | Privacy validation | PII scanning pass | Sí |
| Retro | Privacy review | Lessons documentadas | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Spec del Pipeline
- **Discipline Doc** — `docs/disciplines/PrivacyDD.md`
- **GDPR Text** — https://gdpr-info.eu/
- **Privacy by Design** — https://www.privacybydesign.ca/
