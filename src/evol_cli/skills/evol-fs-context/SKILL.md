---
name: evol-fs-context
description: Filesystem-paradigm context curation. Treat large data as files mounted by agents.
category: context-engineering
trigger: /fs-context
---

# evol-fs-context

## Philosophy
Large data should be treated as files mounted by agents, not passed in context. Filesystem paradigm.

## When to Use
- Data > 50KB that doesn't fit in context
- Log files, datasets, large documents
- Streaming data processing

## Pattern
```
/fs-context mount <path> [--read-only]
/fs-context unmount <path>
/fs-context list
```

## Implementation
- Use file reads with offset/limit for large files
- Stream processing for multi-GB data
- Memory-mapped files for random access
- Virtual filesystem abstraction

## Reference
skills/evol-fs-context/SKILL.md