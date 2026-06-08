---
name: evol-tdd-unit
description: Test-Driven Development. Aplica ciclo Rojo-Verde-Refactor para toda logica de negocio con mandato constitucional (Art. 8).
category: discipline-base
trigger: /tdd
---

# evol-tdd-unit

## Fase del Pipeline
Build (Fase 4)

## Artefacto Clave
`tests/unit/*.test.ts`

## Flujo de Trabajo

### 1. Identificar logica de negocio para TDD
```bash
# Analizar codigo fuente para identificar funciones que requieren TDD
evol-tdd analyze --src=src/ --output=.evol/tdd-candidates.json

# Filtrar por tipo de codigo (logica de negocio vs scaffolding)
evol-tdd filter --candidates=.evol/tdd-candidates.json --type=business-logic
```

### 2. Escribir test que falla (ROJO)
```bash
# Generar stub de test unitario
evol-tdd stub --function=calcularTotalPeriodo --output=tests/unit/facturacion/calcular-total.test.ts

# Ejecutar para confirmar fallo
npx vitest run tests/unit/facturacion/calcular-total.test.ts
```

### 3. Implementar codigo minimo (VERDE)
```bash
# Ejecutar test mientras se implementa
npx vitest watch tests/unit/facturacion/calcular-total.test.ts

# Confirmar que el test pasa
npx vitest run tests/unit/facturacion/calcular-total.test.ts
```

### 4. Refactorizar sin romper tests
```bash
# Ejecutar todos los tests para verificar que no se rompieron
npx vitest run tests/unit/

# Verificar cobertura
npx vitest --coverage
```

### 5. Ejecutar suite completa
```bash
# Ejecutar todos los tests unitarios
npx vitest run tests/unit/

# Generar reporte de cobertura
npx vitest --coverage --reporter=json --output=tests/results/coverage.json
```

## Formato Test Unitario

```typescript
// tests/unit/facturacion/calcular-total.test.ts
// REQ: REQ-001 (SPEC.md) — Calcular total del periodo de facturacion
// FEAT: FEAT-001 (FEATURES.md)
// Autor: Builder | Revisor: Reviewer

import { describe, it, expect } from 'vitest';
import { calcularTotalPeriodo } from '../../../src/facturacion/calcular-total';

describe('calcularTotalPeriodo', () => {

  it('retorna la suma de subtotales de N lineas', () => {
    const lineas = [{ subtotal: 100 }, { subtotal: 250 }, { subtotal: 75 }];
    expect(calcularTotalPeriodo(lineas)).toBe(425);
  });

  it('retorna 0 para un array vacio de lineas', () => {
    expect(calcularTotalPeriodo([])).toBe(0);
  });

  it('lanza DomainError si el total resulta negativo', () => {
    const lineas = [{ subtotal: -100 }];
    expect(() => calcularTotalPeriodo(lineas)).toThrow('DomainError');
  });

});
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Build | Ejecutar ciclo TDD para toda logica de negocio |
| QA | Tier 1 ejecuta tests unitarios; 100% passing |
| Gate | Bloquea si hay logica de negocio sin test previo (Art. 8) |

## Referencia
- `docs/constitucion.md` Art. 8 (Mandato TDD)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/TDD.md`
- [Test-Driven Development: By Example — Kent Beck (2002)](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
