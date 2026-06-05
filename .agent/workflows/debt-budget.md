---
name: debt-budget
trigger: /evol debt-budget
description: Technical Debt Budgeting (DebtBudgetDD). Asigna un presupuesto explicito de deuda tecnica y mide la deuda generada y pagada por iteracion en un ledger. Produce debt/budget.json + debt/ledger.json + debt/forecast.md. Alerta y prioriza pago cuando se excede el limite. Usar en proyectos a largo plazo o legacy con deuda acumulada. Disciplina docs/disciplinas/DebtBudgetDD.md.
phase: plan
category: maintenance
---

# /evol debt-budget — Technical Debt Budgeting (DebtBudgetDD)

> **Estandar de documentacion:** cumple [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md).
> Disciplina: [`docs/disciplinas/DebtBudgetDD.md`](../../docs/disciplinas/DebtBudgetDD.md).

**ID:** FLUJO-DEBT | **Version:** 1.0 | **Agente:** Debt-Accountant (efimero) + PM
**Mision:** Hacer visible y presupuestada la deuda tecnica; bloquear features si se excede el limite.
**Activacion:** solo si `evol.profile.yml` declara `debtbudgetdd` en `methodologies:`.

## 0. Pre-flight

- Lee `debt/debt_items.json` (items detectados por linters/revisiones) si existe.
- Lee `acuerdos/memoria/MEMORY.md` + lecciones (Art. 3).

## 1. Definir el presupuesto

`debt/budget.json`: limite de deuda permitido (por iteracion y total). Politica explicita
(ej. 20% del tiempo de cada sprint a pago de deuda).

## 2. Mantener el ledger

`debt/ledger.json`: por iteracion, deuda **anadida** (nuevos items, atajos justificados) y
deuda **pagada** (refactorings, items cerrados). Saldo acumulado.

## 3. Forecast

`debt/forecast.md`: proyeccion del saldo de deuda + plan de pago. Identifica el momento en que
el saldo cruzaria el limite si no se actua.

## 4. Alerta y bloqueo

Cuando el ledger supera el `budget`, emitir alerta y **priorizar pago de deuda sobre nuevas
features** en el plan. El sub-gate de iteracion lo refleja.

## 5. Output + gate (worker -> auditor)

- Sidecar `.json` via `evol-doc-sync`. Fuentes con URL (DOC_STANDARD).
- **Auditor** (Reviewer != worker) verifica que cada PR declara su impacto en deuda y que el
  ledger se actualizo.

## 6. Integracion

- [RDD](../../docs/disciplinas/RDD.md) paga deuda del ledger.
- [DeprecationDD](../../docs/disciplinas/DeprecationDD.md): el codigo deprecado vivo es deuda.
- [A11yDD](../../docs/disciplinas/A11yDD.md): los issues `#a11y` pendientes entran al ledger.

---
*X-DD — disciplina DebtBudgetDD. Ver [docs/disciplinas/DebtBudgetDD.md](../../docs/disciplinas/DebtBudgetDD.md).*
