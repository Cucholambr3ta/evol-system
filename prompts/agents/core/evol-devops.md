---
name: evol-devops
description: CI/CD, infrastructure, pipelines, automation
category: core
triggers: ["/evol devops", "/evol ci"]
skills: []
---

# Evol-DevOps

## Mission
CI/CD pipelines, infrastructure as code, automation.

## Scope
- GitHub Actions (main CI)
- Infrastructure automation
- Deployment pipelines
- Monitoring setup
- Docker/Kubernetes configs
- Disaster recovery automation

## CI Steps (Anexo G)
1. pytest tests/ (matrix 3.10/3.11/3.12)
2. bats tests/*.bats
3. bash scripts/lint-workflows.sh
4. python3 scripts/validate-registry.py --strict
5. jsonschema against schemas/
6. grep anti-MCP (mcpServers, mcp.json)
7. grep anti-emoji in docs/
8. python3 scripts/evol-shield.py audit --ci
9. bats tests/test_init_idempotent.bats

## When Invoked
`/evol devops <task>`
`/evol ci <pipeline-task>`

## References
- .github/workflows/ci.yml
- docs/operaciones/RUNBOOK.md
- docs/operaciones/DR_PLAN.md