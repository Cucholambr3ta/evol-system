---
name: /evol doc
description: Technical documentation (no emojis, Mermaid mandatory)
trigger: /evol doc
category: core
---

# Evol-Doc

## Mission
Produce granular technical documentation per DOC_STANDARD.

## Rules
1. ZERO emojis — density: 0%
2. Mermaid diagrams REQUIRED: C4, sequence, state, component, deployment
3. Tables for structured data
4. Gherkin complete: happy path + error + edge case per feature
5. Sub-sections substantive — no high-level bullets without content
6. Bidirectional traceability: REQ-NNN <-> TC-NNN

## Output
- docs/arquitectura/*.md
- docs/requisitos/*.md
- docs/diagramas/*.md
- docs/qa/*.md
- docs/seguridad/*.md

## When Invoked
- `/evol doc <type>`
- Documentation requested

## Reference
docs/DOC_STANDARD.md is the SSoT — all docs must comply.