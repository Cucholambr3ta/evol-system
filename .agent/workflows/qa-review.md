---
name: /evol qa-review
description: Quality gate review tier 1
trigger: /evol qa-review
category: core
---

# Evol-QA-Review (Tier 1 Gate)

## Mission
Static quality gate before artifacts are accepted.

## Checks
1. grep emoji in docs/ → must be 0
2. Mermaid block present in structural docs
3. Tables present for structured data
4. REQ-NNN traceability present

## Commands
```bash
# Verify all docs
grep -rP "[\x{1F000}-\x{1FAFF}]" docs/ && echo "FAIL: emojis found"
grep -L "```mermaid" docs/arquitectura/*.md && echo "FAIL: missing diagram"
```

## When Invoked
- `/evol qa-review`
- Before phase transition

## Gate Behavior
- FAIL: reject with specific violations
- PASS: approve for next phase