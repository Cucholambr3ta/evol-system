---
name: evol-code-archaeology
description: Análisis de deuda técnica y evolución de sistemas. Excava código legacy, identifica patrones de deuda y planifica modernización.
category: transfer
trigger: /code-archaeology
---

# evol-code-archaeology

## Cuándo Usar

Activar esta skill cuando se necesita analizar código legacy o deuda técnica:

- **Code archaeology**: entender código que nadie documentó
- **Technical debt identification**: encontrar y clasificar deuda técnica
- **System evolution**: entender cómo evolucionó el sistema
- **Dependency analysis**: mapear dependencias, identificar riesgos
- **Refactoring planning**: planificar modernización incremental
- **Legacy migration**: estrategias para migrar sistemas legacy

**No usar para**: arquitectura de nuevos sistemas (usar evol-architect), documentación técnica (usar evol-doc).

## Conocimiento de Dominio

### Code Archaeology
- **Git archaeology**: blame, log, bisect para entender historia
- **Dead code detection**: código que no se ejecuta
- **Dependency graphs**: visualizar dependencias entre módulos
- **Call chains**: entender flujos de ejecución
- **Data flow**: seguir datos a través del sistema

### Technical Debt Taxonomy
- **Code smells**: duplicated code, long methods, large classes
- **Architecture smells**: circular dependencies, god modules
- **Test debt**: missing tests, flaky tests, low coverage
- **Documentation debt**: missing docs, outdated docs
- **Dependency debt**: outdated deps, known vulnerabilities
- **Infrastructure debt**: manual processes, snowflake servers

### System Evolution
- **Conway's Law**: system structure mirrors org structure
- **Accidental complexity**: complexity that doesn't add value
- **Intentional complexity**: necessary complexity for the domain
- **Evolution stages**: prototype → growth → maturity → decline
- **Strangler fig pattern**: gradually replace legacy

### Refactoring Patterns
- **Extract method/module/class**: break down large units
- **Rename**: improve naming for clarity
- **Move method**: place behavior where it belongs
- **Replace conditional with polymorphism**: OOP patterns
- **Introduce parameter object**: reduce parameter lists
- **Decouple**: reduce coupling between modules

### Migration Strategies
- **Strangler fig**: new system grows around old, old system shrinks
- **Branch by abstraction**: abstract interface, implement new behind it
- **Feature toggle**: new behavior behind flag, gradual migration
- **Data migration**: dual-write, backfill, validate, switch
- **Big bang**: replace all at once (high risk, sometimes necessary)

## Flujo de Trabajo

1. **Survey the codebase**: high-level structure, entry points, main flows
2. **Analyze git history**: who wrote what, why, when, how it evolved
3. **Identify debt**: code smells, architecture smells, missing tests
4. **Map dependencies**: what depends on what, circular deps, hot spots
5. **Classify debt**: by type, severity, impact on development velocity
6. **Plan remediation**: prioritize by impact × effort
7. **Execute incrementally**: refactor in small steps, test after each
8. **Prevent new debt**: coding standards, review, automated checks

## Integración con Pipeline

- **Briefing (Fase 1)**: understand legacy system, business context
- **Spec (Fase 2)**: document current architecture, debt inventory
- **Plan (Fase 3)**: prioritize debt remediation, plan migration
- **Build (Fase 4)**: refactor incrementally, maintain tests
- **QA (Fase 5)**: verify refactoring didn't break anything
- **Retro (Fase 6)**: measure improvement, identify next debt to address

## Referencia

- Constitución Evol-DD: Art. 4 (readability, modularity, lifecycle engineering)
- Agentes relacionados: evol-architect (architecture), evol-reviewer (code review), evol-sec (security debt)
- Martin Fowler - "Refactoring": the definitive guide
- Michael Feathers - "Working Effectively with Legacy Code"
- Ward Cunningham - "The Wyckoff Methodology": debt metaphor origin
- Sourcetrail: code visualization and exploration tool
