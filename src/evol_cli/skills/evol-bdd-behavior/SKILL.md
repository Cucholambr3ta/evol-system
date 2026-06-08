---
name: evol-bdd-behavior
description: Behavior-Driven Development. Convierte criterios de aceptacion en especificaciones Gherkin ejecutables con escenarios de tres tiers.
category: discipline-base
trigger: /bdd
---

# evol-bdd-behavior

## Fase del Pipeline
Briefing + QA (Fase 1+5)

## Artefacto Clave
`tests/features/*.feature`

## Flujo de Trabajo

### 1. Generar archivos .feature skeleton
```bash
# Desde criterios de aceptacion en FEATURES.md
evol-bdd generate --from=docs/features/FEATURES.md --output=tests/features/

# Por epica especifica
evol-bdd generate --epic=EPIC-001 --output=tests/features/
```

### 2. Escribir escenarios Gherkin
```bash
# Validar sintaxis Gherkin
evol-bdd validate --file=tests/features/feature-001.feature

# Verificar vocabulario contra DOMAIN.md
evol-bdd check-vocab --file=tests/features/feature-001.feature --domain=docs/specs/DOMAIN.md
```

### 3. Implementar step definitions
```bash
# Generar steps stub
evol-bdd stub-steps --feature=tests/features/feature-001.feature --output=tests/steps/

# Verificar que todos los steps tienen implementacion
evol-bdd dry-run --features=tests/features/
```

### 4. Ejecutar suite BDD
```bash
# Ejecutar todos los tests BDD
npx playwright test --grep @bdd

# Ejecutar un feature especifico
npx playwright test tests/features/feature-001*

# Generar reporte HTML
npx playwright test --reporter=html
```

### 5. Validar cobertura de escenarios
```bash
# Verificar estructura de tres tiers
evol-bdd check-tiers --features=tests/features/

# Contar escenarios por tier
evol-bdd count --features=tests/features/ --output=tests/results/bdd-coverage.json
```

## Formato Gherkin

```gherkin
Feature: Exportar reporte PDF
  Como operador administrador
  Quiero exportar el reporte de facturacion en PDF
  Para entregarlo a los clientes

  Background:
    Given el operador esta autenticado con rol "administrador"

  @happy-path
  Scenario: Exportar reporte de periodo vigente
    Given existe un Periodo de Facturacion del "2026-05-01" al "2026-05-31"
    When el operador solicita exportar el reporte del periodo "2026-05"
    Then el sistema genera un PDF con los totales
    And el PDF incluye la fecha de generacion

  @error
  Scenario: Rechazar exportacion sin datos
    Given no existen clientes en el Periodo de Facturacion "2026-03"
    When el operador solicita exportar el reporte del periodo "2026-03"
    Then el sistema muestra el error "No hay datos para el periodo seleccionado"

  @edge
  Scenario: Exportar reporte con un solo cliente
    Given existe exactamente 1 cliente en el Periodo de Facturacion "2026-05"
    When el operador solicita exportar el reporte del periodo "2026-05"
    Then el sistema genera un PDF con los datos del unico cliente
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Briefing | Crear archivos .feature skeleton por epica |
| Spec | Verificar vocabulario Gherkin contra DOMAIN.md |
| Build | Implementar step definitions |
| QA | Ejecutar suite completa; 100% passing en Tier 2 |

## Referencia
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/BDD.md`
- [Gherkin Reference — Cucumber](https://cucumber.io/docs/gherkin/reference/)
- [Introducing BDD — Dan North (2006)](https://dannorth.net/introducing-bdd/)
