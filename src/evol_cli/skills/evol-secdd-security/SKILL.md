---
name: evol-secdd-security
description: Security-Driven Development. Ejecuta SAST, DAST y secrets scanning para verificar seguridad en runtime y generar QA_REPORT.md.
category: discipline-base
trigger: /secdd
---

# evol-secdd-security

## Fase del Pipeline
QA (Fase 5)

## Artefacto Clave
`.evol/qa/QA_REPORT.md`

## Flujo de Trabajo

### 1. Ejecutar SAST (Analisis Estatico)
```bash
# Semgrep — analisis de codigo fuente
npx semgrep --config=auto src/
npx semgrep --config=p/owasp-top-ten src/
npx semgrep --config=p/jwt src/

# Gitleaks — deteccion de secretos
gitleaks detect --source=. --verbose
gitleaks detect --source=. --log-opts="--all"

# npm audit — analisis de dependencias
npm audit --audit-level=high
```

### 2. Ejecutar DAST (Analisis Dinamico) en staging
```bash
# OWASP ZAP — baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t $STAGING_URL

# Nuclei — templates de vulnerabilidades
nuclei -u $STAGING_URL -t cves/ -t vulnerabilities/ -t exposures/
```

### 3. Ejecutar SCA (Analisis de Composicion)
```bash
# Trivy — escaneo de contenedores
docker run aquasec/trivy image [nombre-imagen]:latest

# Verificar CVEs en dependencias
npm audit --json --output=tests/results/npm-audit.json
```

### 4. Generar QA_REPORT.md
```bash
# Compilar resultados de todas las herramientas
evol-secdd compile --sast=tests/results/semgrep.json --dast=tests/results/zap.json --output=.evol/qa/QA_REPORT.md

# Validar estructura del reporte
evol-secdd validate --report=.evol/qa/QA_REPORT.md
```

### 5. Verificar criterios de aprobacion
```bash
# Verificar que no hay hallazgos criticos/altos
evol-secdd check --report=.evol/qa/QA_REPORT.md --block-on=critical,high

# Generar resumen para gate de Fase 5
evol-secdd gate-report --report=.evol/qa/QA_REPORT.md --output=.evol/qa/secdd-gate.json
```

## Formato QA_REPORT.md

```markdown
# QA Report — Security

**Fecha:** 2026-06-04
**Estado:** APROBADO / RECHAZADO

## Resumen Ejecutivo
[Estado general y hallazgos criticos]

## Resultados SAST
| Herramienta | Hallazgos criticos | Hallazgos altos | Hallazgos medios |
|-------------|-------------------|-----------------|------------------|
| Semgrep | 0 | 0 | 3 |

## Resultados Secrets
| Herramienta | Secretos detectados |
|-------------|---------------------|
| Gitleaks | 0 |

## Resultados SCA
| Herramienta | CVEs criticos | CVEs altos |
|-------------|--------------|------------|
| npm audit | 0 | 0 |

## Resultados DAST
| Herramienta | Hallazgos criticos | Hallazgos altos |
|-------------|-------------------|-----------------|
| OWASP ZAP | 0 | 0 |
| Nuclei | 0 | 0 |

## Hallazgos Abiertos
| ID | Herramienta | Severidad | Descripcion | Estado | Owner |
|----|-------------|-----------|-------------|--------|-------|
| SEC-001 | Semgrep | MEDIO | Uso de eval() en parser | ABIERTO | Builder |

## Hallazgos Aceptados
| ID | Razon | Aprobado por | Fecha |
|----|-------|-------------|-------|
| SEC-002 | Falso positivo en test helper | SecOps | 2026-06-04 |
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Build | STDD implementa controles de seguridad |
| QA | SecDD verifica controles en runtime con SAST/DAST |
| Gate | Bloquea si QA_REPORT.md tiene hallazgos criticos/altos |
| Release | Requisito para release a produccion |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/disciplinas/SecDD.md`
- [OWASP SAMM — Software Assurance Maturity Model](https://owaspsamm.org/)
- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)
