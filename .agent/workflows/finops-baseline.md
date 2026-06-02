---
description: Establece presupuesto cloud, alertas, tagging y checklist mensual de rightsizing. Produce BUDGET.md.
---
# /finops-baseline

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-FINOPS | **Versión:** 1.0 | **Agente:** FinOps-Architect
**Misión:** Cero sorpresas en factura cloud. Gobierno de costos como ciudadano de primera clase.

## 0. Pre-flight
- Copia `templates/budget.template.md` a `BUDGET.md`.
- Detecta proveedor cloud en `xdd.profile.yml > stacks.cloud`.

## 1. Categorías y cap
Define cap mensual por categoría: compute, storage, egress, observabilidad, IA/LLMs, terceros.

## 2. Tagging obligatorio
Todo recurso cloud DEBE tener: `env`, `service`, `owner`, `cost-center`.
CI/Terraform rechaza recursos sin tags.

## 3. Alertas
<!-- CONFIGURAR: Mecanismo de alertas por proveedor.                          -->
<!--  - AWS: Budgets + Cost Anomaly Detection                                   -->
<!--  - GCP: Billing Budgets + Recommender                                      -->
<!--  - Azure: Cost Management + Advisor                                        -->
<!--  - Multi-cloud: Vantage, CloudHealth, Infracost                            -->

Configurar:
- 50% cap → notificación
- 80% cap → warning + revisión
- 100% cap → escalamiento + freeze de gasto no esencial

## 4. Checklist rightsizing mensual
- [ ] VMs sub-utilizadas (<20% CPU 30d)
- [ ] Storage no accedido > 90 días → tier frío
- [ ] Snapshots vencidos
- [ ] Recursos huérfanos (sin tags / sin propietario)
- [ ] Reservas/savings plans expirados o sub-utilizados
- [ ] Egress inter-región evitable

## 5. Cuotas IA
Cap diario de tokens por modelo y owner. Alertas si se acerca al cap.

## 6. Pre-deploy
Estimación de costo de nuevos recursos (Infracost en CI) antes de merge.

## 7. Cierre
Log de optimizaciones aplicadas y ahorro estimado en `BUDGET.md`. Lecciones a [[lecciones]].
