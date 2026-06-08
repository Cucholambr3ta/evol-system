---
name: evol-rdd-refactor
description: Refactoring-Driven Development. Detecta code smells, aplica patrones de refactoring con red de tests, y verifica que la cobertura no baja.
category: discipline-extended
trigger: /rdd
---

# evol-rdd-refactor

## Fase del Pipeline
Build (Fase 4)

## Artefacto Clave
`refactoring/sessions/*.md`

## Flujo de Trabajo

### 1. Detectar code smells y priorizar
```bash
# Analizar complejidad ciclomatica
npx complexity-report src/ --format=json --output=.evol/complexity.json

# Detectar code smells con plato
npx plato -r -d -x node_modules src/ -e .evol/plato/

# Identificar deuda tecnica priorizada
evol-rdd debt-items --complexity=.evol/complexity.json --output=debt/debt_items.json
```

### 2. Ejecutar tests antes del refactoring (red de seguridad)
```bash
# Suite completa antes de tocar codigo
npx vitest run tests/ --reporter=json --output=refactoring/before_metrics.json

# Guardar metricas base
evol-rdd snapshot-metrics --input=refactoring/before_metrics.json --output=refactoring/before_snapshot.json
```

### 3. Ejecutar sesion de refactoring
```bash
# Planificar sesion desde deuda priorizada
evol-rdd plan-session --debt=debt/debt_items.json --output=refactoring/sessions/SESSION-$(date +%Y%m%d).md

# Ejecutar refactoring guiado
evol-rdd refactor --target=src/facturacion/ --pattern=extract-method
```

### 4. Verificar post-refactoring
```bash
# Suite completa despues del refactoring
npx vitest run tests/ --reporter=json --output=refactoring/after_metrics.json

# Comparar metricas before/after
evol-rdd compare --before=refactoring/before_snapshot.json --after=refactoring/after_metrics.json --output=refactoring/comparison.json

# Verificar que la cobertura no bajo
evol-rdd check-coverage --comparison=refactoring/comparison.json --block-on=coverage-decrease
```

## Formato Sesion de Refactoring

```markdown
# Sesion de Refactoring — SESSION-20260607

**Fecha:** 2026-06-07
**Target:** `src/facturacion/calcular-total.ts`
**Debt Item:** DEBT-003

## Code Smell Detectado
Metodo `calcularTotal` con complejidad ciclomatica = 18 (umbral: 10)

## Refactoring Aplicado
Extract Method: Separar logica de descuentos en `aplicarDescuentos()`

## Metricas
| Metrica | Antes | Despues | Delta |
|---------|-------|---------|-------|
| Complejidad ciclomatica | 18 | 6 | -66% |
| Cobertura de tests | 87% | 87% | 0% |

## Tests
- [x] Todos los tests pasan antes del refactoring
- [x] Todos los tests pasan despues del refactoring
- [x] Cobertura estable o mayor
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Build | Planificar y ejecutar sesiones de refactoring |
| QA | Verificar que las metricas mejoraron |
| Retro | Registrar la deuda pagada en el ledger |
| Gate | Bloquea si la cobertura bajo tras el refactoring |

## Referencia
- `docs/constitucion.md` Art. 8 (Mandato TDD)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/RDD.md`
- [Refactoring — Martin Fowler](https://refactoring.com/)
- [Refactoring Catalog — refactoring.com](https://refactoring.com/catalog/)


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
