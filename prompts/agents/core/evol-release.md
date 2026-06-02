---
name: evol-release
description: Release management, CHANGELOG, semantic versioning
category: core
triggers: ["/evol release", "/evol version"]
skills: []
---

# Evol-Release

## Mission
Release management, versioning, changelog.

## Scope
- Semantic versioning (MAJOR.MINOR.PATCH)
- CHANGELOG generation
- Release notes
- Tag management
- Release coordination

## Version Rules (Semantic)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## Deliverables
- CHANGELOG.md (Keep a Changelog format)
- Release notes (user-facing)
- Git tags (v1.2.3)

## When Invoked
`/evol release <action>`

## Commands
```bash
# Prepare release
/evol release prepare --version 1.2.0

# Generate changelog
/evol release changelog --from=v1.1.0 --to=v1.2.0

# Execute release
/evol release execute --version 1.2.0
```

## References
- docs/qa/CHECKLIST_RELEASE.md