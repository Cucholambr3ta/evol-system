---
name: evol-debt-budget
description: DebtBudgetDD — Tech debt inventory, prioritization, remediation planning
category: discipline-extended
trigger: /debt-budget
---

# evol-debt-budget

## Fase del Pipeline

**Plan (Fase 3) — Planificación y Presupuesto**

Activar cuando se necesita gestionar deuda técnica:
- Inventario de deuda técnica
- Priorización (impacto vs esfuerzo)
- Plan de remediación
- Presupuesto de deuda por sprint

## Artefacto Clave

**`docs/plan/DEBT_BUDGET.md`**

```markdown
# Tech Debt Budget

## Debt Inventory
| ID | Category | Severity | Effort | Impact | File(s) |
|----|----------|----------|--------|--------|---------|
| TD-001 | Architecture | High | 5d | High | src/legacy/ |
| TD-002 | Dependencies | Medium | 2d | Medium | package.json |
| TD-003 | Code Quality | Low | 1d | Low | src/utils/ |

## Sprint Budget
| Sprint | Capacity | Allocated | Remaining |
|--------|----------|-----------|-----------|
| Sprint 12 | 40h | 12h (30%) | 28h |
| Sprint 13 | 40h | 8h (20%) | 32h |

## Remediation Plan
| Quarter | Target Debt | Est. Hours | Owner |
|---------|-------------|------------|-------|
| Q3 2026 | TD-001, TD-002 | 40h | Team A |
| Q4 2026 | TD-003, TD-004 | 20h | Team B |

## Debt Trends
- Total debt: 45h → 38h (↓16%)
- New debt added: 8h
- Debt resolved: 15h
```

## Flujo de Trabajo

```bash
# 1. Descubrir deuda técnica
python3 scripts/debt/discover.py \
  --source . \
  --output docs/plan/DEBT_RAW.md

# 2. Clasificar deuda
python3 scripts/debt/classify.py \
  --input docs/plan/DEBT_RAW.md \
  --output docs/plan/DEBT_CLASSIFIED.md

# 3. Priorizar por impacto
python3 scripts/debt/prioritize.py \
  --input docs/plan/DEBT_CLASSIFIED.md \
  --output docs/plan/DEBT_PRIORITIZED.md

# 4. Generar presupuesto
python3 scripts/debt/budget.py \
  --input docs/plan/DEBT_PRIORITIZED.md \
  --capacity 40h \
  --ratio 0.25 \
  --output docs/plan/DEBT_BUDGET.md

# 5. Generar plan de remediación
python3 scripts/debt/remediation-plan.py \
  --input docs/plan/DEBT_PRIORITIZED.md \
  --output docs/plan/REMEDIATION_PLAN.md

# 6. Reporte de tendencias
python3 scripts/debt/trends.py \
  --history docs/plan/DEBT_HISTORY.json \
  --output docs/plan/DEBT_TRENDS.md
```

### Debt Classification

```
Categories: Architecture, Dependencies, Code Quality, Testing, Documentation
Severity: Critical (blocks features), High (impacts velocity), Medium (technical risk), Low (cosmetic)
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Debt awareness | Deuda conocida identificada | No |
| Spec | Debt impact | Impacto en diseño evaluado | No |
| Plan | Debt budget | Presupuesto definido (20-30%) | Sí |
| Build | Debt tracking | Deuda nueva registrada | Sí |
| QA | Debt validation | Deuda remediada verificada | Sí |
| Retro | Debt trends | Tendencias actualizadas | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Plan del Pipeline
- **Discipline Doc** — `docs/disciplines/DebtBudgetDD.md`
- **Martin Fowler Tech Debt** — https://martinfowler.com/bliki/TechnicalDebt.html
- **Tech Debt Quadrant** — https://martinfowler.com/bliki/TechnicalDebtQuadrant.html


## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
