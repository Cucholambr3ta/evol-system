---
name: evol-sec
description: Security (SecDD, STRIDE threat modeling, auditing)
category: core
triggers: ["/evol sec", "/evol security"]
skills: ["evol-sandbox"]
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
- skills/code-indexer/SKILL.md (code graph tools)

## Code Graph Awareness

When performing security audits, use the code graph indexer to:

1. **Trace sensitive data flow**: Follow how user input reaches security-sensitive functions
   ```bash
   python3 scripts/evol_code_indexer.py trace <EntryPoint> --max-depth=5
   ```

2. **Identify attack surface**: Find all public API endpoints and their callers
   ```bash
   python3 scripts/evol_code_indexer.py query <PublicFunction>
   ```

3. **Impact of vulnerability**: Determine blast radius if a function is compromised
   ```bash
   python3 scripts/evol_code_indexer.py impact <VulnerableFunction> --depth=3
   ```

Flag any function with depth-1 callers > 10 as high-risk for vulnerability propagation.