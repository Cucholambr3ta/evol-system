---
name: evol-qa
description: Quality, tests unitarios, integracion, E2E, Gherkin/BDD cases
category: core
triggers: ["/evol qa", "/evol test"]
skills: ["agent-eval", "evol-ai-review"]
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
- skills/code-indexer/SKILL.md (code graph tools)

## Code Graph Awareness

When designing test plans, use the code graph indexer to:

1. **Identify test targets**: Find all functions/classes in modified files
   ```bash
   python3 scripts/evol_code_indexer.py query <ModifiedFile>
   ```

2. **Coverage gaps**: Check which callers lack test coverage
   ```bash
   python3 scripts/evol_code_indexer.py impact <FunctionName> --depth=2
   ```

3. **Regression risk**: High blast radius symbols need additional test cases
   ```bash
   python3 scripts/evol_compliance.py check-impact --json
   ```

Prioritize test cases for symbols with blast radius > 5 at depth-1.