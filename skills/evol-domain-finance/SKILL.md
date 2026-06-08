---
name: evol-domain-finance
description: Asesor de dominio para construir software financiero y contable. Aporta conocimiento en GAAP/IFRS, cálculo de impuestos, reportes financieros y reconciliación.
category: domain-advisor
trigger: /domain-finance
---

# evol-domain-finance

## Cuándo Usar

Activar esta skill cuando el sistema Evol-DD necesita construir o auditar software en el dominio financiero y contable:

- **Contabilidad y libros**: ledger doble entrada, chart of accounts, journal entries, balance sheet, income statement, cash flow
- **Cálculo de impuestos**: IVA, ISR, retenciones, impuestos por jurisdicción, cálculos automáticos
- **Reportes financieros**: estados financieros GAAP/IFRS, reportes fiscales, auditoría
- **Reconciliación**: bancaria, entre cuentas, cross-system matching
- **Pagos y transferencias**: ACH, wire transfers, SEPA, pagos recurrentes
- **Presupuestos y forecasting**: budgeting, variance analysis, proyecciones
- **Compliance**: SOX, anti-money laundering (AML), KYC

**No usar para**: e-commerce y ventas (usar evol-domain-sales), analytics de marketing (usar evol-domain-marketing).

## Conocimiento de Dominio

### Contabilidad
- **Double-entry bookkeeping**: cada transacción tiene debito y crédito, el balance siempre cuadra
- **Chart of Accounts**: estructura jerárquica de cuentas (assets, liabilities, equity, revenue, expenses)
- **Journal Entries**: asientos contables con débitos y créditos
- **Accrual vs. Cash basis**: cuándo reconocer ingresos/gastos
- **Close process**: monthly/quarterly/yearly close, adjusting entries

### Impuestos
- **IVA/VAT**: cálculo por jurisdicción, input vs. output tax, declaraciones
- **ISR/Income Tax**: retenciones, pagos provisionales, declaración anual
- ** withholding taxes**: retenciones en fuente, tratados tributarios
- **Sales tax**: Nexus, economic nexus, marketplace facilitator laws

### Estados Financieros
- **Balance Sheet**: assets = liabilities + equity
- **Income Statement**: revenue - expenses = net income
- **Cash Flow Statement**: operating, investing, financing activities
- **Equity Statement**: cambios en equity, retained earnings

### Reconciliación
- **Bank reconciliation**: matching entre ledger y estado bancario
- **Inter-company reconciliation**: transacciones entre entidades
- **Subledger reconciliation**: AP/AR subledgers vs. GL
- **Automated matching**: rules-based, fuzzy matching, threshold-based

### Compliance y Regulación
- **SOX**: controles internos, segregación de duties, audit trail
- **AML/KYC**: due diligence, suspicious activity reports
- **IFRS vs. GAAP**: diferencias clave, convergencia
- **Data retention**: requerimientos legales de retención de datos financieros

## Flujo de Trabajo

1. **Identificar el alcance financiero**: ¿Qué tipo de software? (contabilidad, pagos, reporting, compliance)
2. **Mapear el modelo contable**: chart of accounts, reglas de negocio, monedas
3. **Diseñar el ledger**: double-entry, audit trail, inmutabilidad de registros
4. **Planificar cálculos de impuestos**: jurisdicciones, tasas, excepciones, edge cases
5. **Definir reportes**: estados financieros, reportes fiscales, dashboards
6. **Implementar reconciliación**: matching rules, manejo de diferencias, alertas
7. **Testear con datos contables**: balance debe cuadrar siempre, edge cases de cierre
8. **Verificar compliance**: audit trail, controles, segregación de duties

## Integración con Pipeline

- **Briefing (Fase 1)**: identificar necesidades contables y regulatorias del cliente
- **Spec (Fase 2)**: documentar chart of accounts, reglas fiscales, requerimientos de compliance
- **Plan (Fase 3)**: estimar complejidad contable, dependencias regulatorias
- **Build (Fase 4)**: implementar con TDD, ledger inmutable, audit trail completo
- **QA (Fase 5)**: testear balance cuadrado, reconciliación, edge cases de cierre
- **Retro (Fase 6)**: revisar accuracy contable, identificar mejoras en automatización

## Referencia

- Constitución Evol-DD: Art. 5 (consultoría de dominio proactiva)
- Art. 9: pipeline de 6 fases
- Agentes relacionados: evol-domain (modelado de dominio), evol-sec (seguridad financiera), evol-auditor (auditoría)
- FASB Accounting Standards: https://www.fasb.org
- IFRS Foundation: https://www.ifrs.org


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
