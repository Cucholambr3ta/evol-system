---
name: evol-atdd-acceptance
description: Acceptance Test-Driven Development. Genera stubs de acceptance tests que fallan por diseno y bloquean merge hasta implementacion completa.
category: discipline-base
trigger: /atdd
---

# evol-atdd-acceptance

## Fase del Pipeline
Briefing + QA (Fase 1+5)

## Artefacto Clave
`tests/acceptance/*.acceptance.test.ts`

## Flujo de Trabajo

### 1. Generar stubs de acceptance tests
```bash
# Desde criterios de aceptacion en FEATURES.md
evol-atdd stub --from=docs/features/FEATURES.md --output=tests/acceptance/

# Para un feature especifico
evol-atdd stub --feature=FEAT-001 --output=tests/acceptance/
```

### 2. Validar estructura de stubs
```bash
# Verificar que stubs fallan por diseno
evol-atdd verify-stubs --expect=failing --output=tests/results/stub-status.json

# Contar stubs vs criterios de aceptacion
evol-atdd coverage --features=docs/features/FEATURES.md --stubs=tests/acceptance/
```

### 3. Ejecutar acceptance tests
```bash
# Ejecutar suite de acceptance tests
npx playwright test tests/acceptance/

# Ejecutar un test especifico
npx playwright test tests/acceptance/feat-001-exportar-pdf.acceptance.test.ts

# Generar reporte
npx playwright test tests/acceptance/ --reporter=json --output=tests/results/acceptance-results.json
```

### 4. Validar contra el pipeline CI
```bash
# Verificar que los tests bloquean merge si fallan
evol-atdd ci-check --results=tests/results/acceptance-results.json --block-on=failure

# Generar reporte para gate de Fase 5
evol-atdd gate-report --results=tests/results/acceptance-results.json --output=.evol/qa/acceptance-gate.json
```

## Formato Acceptance Test

```typescript
// tests/acceptance/feat-001-exportar-pdf.acceptance.test.ts
// ATDD Stub — FEAT-001: Exportar reporte PDF del periodo de facturacion
// Estado: FAILING BY DESIGN — implementacion pendiente en Fase 4
// REQ: REQ-001 (SPEC.md)

import { test, expect } from '@playwright/test';
import { loginAs } from '../helpers/auth';
import { crearPeriodoConClientes } from '../helpers/billing';

test.describe('FEAT-001: Exportar reporte PDF', () => {

  test('REQ-001 — Operador puede exportar PDF de periodo vigente', async ({ page }) => {
    await loginAs(page, 'operador-admin');
    await crearPeriodoConClientes('2026-05', 3);
    
    await page.goto('/reportes');
    await page.click('[data-testid="exportar-pdf-2026-05"]');
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('[data-testid="confirmar-exportar"]'),
    ]);
    
    expect(download.suggestedFilename()).toMatch(/reporte-2026-05\.pdf/);
  });

  test('REQ-001-ERR1 — Rechaza exportacion sin datos', async ({ page }) => {
    await loginAs(page, 'operador-admin');
    const response = await page.request.get('/api/reportes/2026-03/pdf');
    expect(response.status()).toBe(404);
  });

});
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Briefing | Escribir stubs de acceptance tests (FAILING BY DESIGN) |
| Build | Implementar feature hasta que stubs pasen |
| QA | Ejecutar suite completa; 100% passing en Tier 2 |
| Gate | Bloquea merge si algun acceptance test falla |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 8 (Mandato de testing)
- `docs/disciplinas/ATDD.md`
- [ATDD by Example — Markus Gartner (2012)](https://www.oreilly.com/library/view/atdd-by-example/9780132542883/)


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
