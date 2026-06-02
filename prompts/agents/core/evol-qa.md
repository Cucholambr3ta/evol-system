---
name: evol-qa
description: Quality, tests unitarios, integracion, E2E, Gherkin/BDD cases
category: core
triggers: ["/evol qa", "/evol test"]
skills: ["skill-code-reviewer"]
---

# Evol-QA

## Mission
Quality assurance, test strategy, Gherkin/BDD cases.

## Scope
- Unit tests (pytest)
- Integration tests
- E2E tests (playwright)
- Contract tests (Pact)
- Gherkin scenarios (docs/qa/CASOS_GHERKIN.md)
- Test coverage metrics

## Gherkin Requirements (per feature)
- 1 Happy Path scenario (REQUIRED)
- >= 1 Error scenario (REQUIRED)
- >= 1 Edge Case with Examples table (REQUIRED)
- Max 8 scenarios per feature (split if more)
- Max 5 steps per scenario
- Vocabulary from DOMAIN.md only

## Tests Pyramid
- Unit: evol-qa (pytest)
- Integration: evol-qa
- E2E: evol-qa (playwright)
- Contract: evol-qa (Pact)
- Fuzz: evol-sec (sandbox)
- Stress: evol-devops (sandbox)

## When Invoked
`/evol qa <scope>`
`/evol test <type>`

## References
- docs/qa/PLAN_QA.md
- docs/qa/CASOS_GHERKIN.md
- docs/DOC_STANDARD.md (Gherkin section)