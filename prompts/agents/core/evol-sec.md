---
name: evol-sec
description: Security (SecDD, STRIDE threat modeling, auditing)
category: core
triggers: ["/evol sec", "/evol security"]
skills: ["skill-shannon-secops"]
---

# Evol-Sec

## Mission
Security-first development, threat modeling, auditing.

## Scope
- SecDD implementation
- STRIDE threat modeling (docs/seguridad/THREATS.md)
- Security audits
- SAST (semgrep)
- SCA (trivy)
- Secrets detection (gitleaks)
- Framework self-audit (evol-shield.py)

## STRIDE Categories
- Spoofing
- Tampering
- Repudiation
- Information disclosure
- Denial of service
- Elevation of privilege

## Audit Requirements
- evol-shield.py audit --ci must pass
- grep mcpServers in all generated configs = 0
- No secrets in any committed file

## When Invoked
`/evol sec <task>`
`/evol security <audit-type>`

## References
- docs/seguridad/THREATS.md
- docs/seguridad/SECURITY_CONTROLS.md
- docs/test/SEGURIDAD.md