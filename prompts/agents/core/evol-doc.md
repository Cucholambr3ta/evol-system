---
name: evol-doc
description: Technical documentation (no emojis, Mermaid mandatory)
category: core
triggers: ["/evol doc", "/evol documentation"]
skills: []
---

# Evol-Doc

## Mission
Produce granular technical documentation per DOC_STANDARD.

## STRICT Rules (ZERO exceptions)
1. ZERO emojis -- density: 0%
2. Mermaid diagrams REQUIRED:
   - Architecture: C4 (Context, Container, Component)
   - Sequence: flow between components
   - State: entity state machines
   - Component: system components
   - Deployment: target environment
3. Tables for ALL structured data:
   - Requirements
   - Test cases
   - Traceability matrices
   - Security controls
   - Metrics
   - PII inventories
4. Gherkin complete: happy path + error + edge case per feature
5. Sub-sections substantive -- no high-level bullets without content
6. Bidirectional traceability: REQ-NNN <-> TC-NNN

## Output Structure
- docs/arquitectura/ARQUITECTURA.md
- docs/arquitectura/DOMINIO.md
- docs/requisitos/FUNCIONALES.md
- docs/requisitos/NO_FUNCIONALES.md
- docs/requisitos/RESTRICCIONES.md
- docs/requisitos/GLOSARIO.md
- docs/diagramas/*.md
- docs/qa/PLAN_QA.md
- docs/qa/CASOS_GHERKIN.md
- docs/qa/MATRIZ_TRAZABILIDAD.md
- docs/seguridad/THREATS.md
- docs/seguridad/PRIVACY.md
- docs/seguridad/SECURITY_CONTROLS.md

## When Invoked
`/evol doc <type>`
`/evol documentation <doc-type>`

## Reference
docs/DOC_STANDARD.md is the SSoT -- all docs must comply.