---
name: evol-compact
description: Provider-agnostic context compaction. Reduce tokens preserving semantics.
category: context-engineering
trigger: /compact
---

# evol-compact

## Philosophy
Context compaction must preserve semantic meaning while reducing token count.

## Strategies
1. Remove redundant examples
2. Merge similar instructions
3. Compress technical terms
4. Keep decision-critical context
5. Preserve error cases

## When to Use
- Context approaching token limit
- Large codebase navigation
- Long conversation history

## Commands
```
/compact --level=light   # 20-30% reduction
/compact --level=medium  # 40-50% reduction
/compact --level=aggressive # 60-75% reduction
```

## Reference
skills/evol-compact/SKILL.md