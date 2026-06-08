---
name: evol-udd-usecase
description: UDD — Use-Case-Driven Development, use case modeling, user story mapping, scenario analysis
category: discipline-extended
trigger: /udd-usecase
---

# evol-udd-usecase

## Fase del Pipeline

**Briefing (Fase 1) — Análisis de Requisitos**

Activar cuando se necesita modelar casos de uso:
- Use case modeling (UML)
- User story mapping
- Scenario analysis
- Acceptance criteria definition

## Artefacto Clave

**`docs/usecases/USE_CASES.md`**

```markdown
# Use Cases

## Actors
| Actor | Role | Description |
|-------|------|-------------|
| Customer | Primary | Places orders and manages account |
| Admin | Secondary | Manages products and orders |
| System | Supporting | Payment processing, notifications |

## Use Cases
| ID | Name | Actor(s) | Priority | Status |
|----|------|----------|----------|--------|
| UC-001 | Place Order | Customer | High | Implemented |
| UC-002 | Process Payment | System | High | Implemented |
| UC-003 | Manage Inventory | Admin | Medium | In Progress |

## Use Case: Place Order (UC-001)
### Main Flow
1. Customer adds items to cart
2. Customer proceeds to checkout
3. System displays order summary
4. Customer confirms order
5. System creates order
6. System sends confirmation email

### Alternate Flows
- 3a. Cart is empty → Display message
- 4a. Payment fails → Show error, retry
- 5a. Item out of stock → Notify customer

### Acceptance Criteria
- [ ] Cart supports up to 50 items
- [ ] Checkout completes in < 3 steps
- [ ] Order confirmation shown within 2s

## User Story Map
```
Backbone: Place Order → Process Payment → Fulfill Order → Deliver
Tasks: Add to cart → Checkout → Pay → Confirm → Ship → Track
```

## Scenario Matrix
| Scenario | Preconditions | Steps | Expected Result |
|----------|---------------|-------|-----------------|
| Happy path | Items in stock | 1-6 | Order confirmed |
| Payment failure | Invalid card | 1-4, 4a | Error shown |
| Out of stock | Item unavailable | 1-5, 5a | Notification sent |
```

## Flujo de Trabajo

```bash
# 1. Capturar requisitos
python3 scripts/udd/capture-requirements.py \
  --source docs/briefing/ \
  --output docs/usecases/REQUIREMENTS_RAW.md

# 2. Identificar actores
python3 scripts/udd/identify-actors.py \
  --requirements docs/usecases/REQUIREMENTS_RAW.md \
  --output docs/usecases/ACTORS.md

# 3. Generar use cases
python3 scripts/udd/generate-usecases.py \
  --actors docs/usecases/ACTORS.md \
  --requirements docs/usecases/REQUIREMENTS_RAW.md \
  --output docs/usecases/USE_CASES.md

# 4. Crear user story map
python3 scripts/udd/story-map.py \
  --usecases docs/usecases/USE_CASES.md \
  --output docs/usecases/STORY_MAP.md

# 5. Definir acceptance criteria
python3 scripts/udd/acceptance-criteria.py \
  --usecases docs/usecases/USE_CASES.md \
  --output docs/usecases/ACCEPTANCE_CRITERIA.md

# 6. Generar scenario matrix
python3 scripts/udd/scenario-matrix.py \
  --usecases docs/usecases/USE_CASES.md \
  --output docs/usecases/SCENARIO_MATRIX.md
```

### User Story Format

```markdown
## User Story: UC-001-01
**As a** Customer
**I want to** add items to my shopping cart
**So that** I can purchase multiple items in one order

### Acceptance Criteria
- Given I am on the product page
  When I click "Add to Cart"
  Then the item is added to my cart
  And the cart count increases by 1

### Definition of Done
- [ ] Code complete
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] UI reviewed
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Use cases defined | Use cases principales documentados | Sí |
| Spec | Use case details | Flujos y escenarios completos | Sí |
| Plan | Story mapping | User stories priorizadas | No |
| Build | Acceptance criteria | Criteria verificables | Sí |
| QA | Scenario testing | Escenarios validados | Sí |
| Retro | Use case review | Cobertura evaluada | No |

## Referencia

- **Constitución Art. 1** — Filtro de ambigüedad
- **Constitución Art. 9** — Fase Briefing del Pipeline
- **Discipline Doc** — `docs/disciplines/UDD_UseCase.md`
- **Use Case Modeling** — https://www.uml-diagrams.org/use-case-diagram.html
- **User Story Mapping** — https://www.jeffpatton.com/resources/
