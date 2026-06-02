---
name: evol-researcher
description: Autonomous research (skills, methodologies, frameworks)
category: core
triggers: ["/evol research", "/evol researcher"]
skills: []
---

# Evol-Researcher

## Mission
Autonomous research on skills, methodologies, frameworks. Propose improvements ranked by impact.

## Sources
- GitHub (skills, frameworks, agentic AI)
- Changelogs of dependencies
- Papers (arXiv, etc.)
- Community trends

## Commands
```bash
# Run system-wide research
python3 scripts/evol-researcher.py run --scope system

# Run project-specific research
python3 scripts/evol-researcher.py run --scope project --topic "testing"

# List pending proposals
python3 scripts/evol-researcher.py list

# Apply approved proposal
python3 scripts/evol-researcher.py apply PROPOSAL_ID
```

## Output
- RESEARCH.md with ranked proposals
- Proposals persisted in SQLite (research_proposals table)
- Every proposal requires human approval before applying

## Failure Contract (MANDATORY)
| Scenario | Behavior |
|----------|----------|
| GitHub timeout | Warning + continue with cache; no cache -> exit 0 "sin conexion" |
| Rate-limit 403/429 | Report limit + reset time; use cache; don't crash |
| LLM unavailable (mock mode) | Fall to mock; proposals marked "[mock -- requiere LLM real]" |
| Skill fails supply-chain scan | Block install + report specific reason; other proposals unaffected |
| gitleaks/semgrep not installed | Warning "scan omitted"; flag scan_skipped: true in proposal |

## When Invoked
`/evol research <scope> --topic <topic>`
`/evol researcher <task>`

## Constraints
- All proposals require human approval
- Research does not modify anything -- only proposes
- Integration with evol-lessons: suggest-fix chain

## References
- docs/constitucion.md (Art. 9: evolution)