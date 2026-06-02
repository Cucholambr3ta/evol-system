---
name: evol-ai-review
description: Quality gate review using AI for nuanced assessment.
category: quality-gate
trigger: /ai-review
---

# evol-ai-review

## Philosophy
AI-as-judge for quality gates. Supplement static checks with LLM reasoning.

## Tiers
1. **Static** (automated): grep, lint, schema validation
2. **Functional** (automated): test execution, contract testing
3. **AI Judge** (LLM): nuanced quality assessment

## When to Use
- Complex refactoring decisions
- Architecture trade-off evaluation
- Security vulnerability severity
- Documentation quality

## Commands
```
/ai-review --type=security <target>
/ai-review --type=quality <target>
/ai-review --type=architecture <target>
```

## Integration
- Run after static checks pass
- Input: code + context
- Output: assessment + confidence score

## Reference
skills/evol-ai-review/SKILL.md