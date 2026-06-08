---
name: evol-cost-analysis
description: Cost modeling y ROI analysis para proyectos de software. Análisis de costos, optimización financiera y modelado financiero.
category: transfer
trigger: /cost-analysis
---

# evol-cost-analysis

## Cuándo Usar

Activar esta skill cuando se necesita analizar costos y ROI de software:

- **ROI analysis**: retorno de inversión de features, proyectos, herramientas
- **Cost modeling**: estimar costos de infra, desarrollo, operación
- **Cost optimization**: reducir costos sin sacrificar calidad
- **Financial modeling**: proyecciones, scenarios, break-even analysis
- **Build vs. buy**: decidir entre construir internamente o comprar
- **Cloud cost management**: AWS/GCP/Azure cost optimization

**No usar para**: software contable/financiero (usar evol-domain-finance), análisis de presupuesto de proyecto (usar evol-pm).

## Conocimiento de Dominio

### ROI Analysis
- **ROI formula**: (Gain - Cost) / Cost × 100%
- **Payback period**: cuánto tiempo para recuperar la inversión
- **NPV (Net Present Value)**: valor presente de flujos futuros
- **IRR (Internal Rate of Return)**: tasa de retorno implícita
- **Intangibles**: brand value, developer productivity, time-to-market

### Cost Modeling
- **Infrastructure costs**: compute, storage, network, databases
- **Development costs**: salaries, contractors, tools, licenses
- **Operational costs**: monitoring, support, maintenance, updates
- **Opportunity costs**: what we're not building
- **Hidden costs**: technical debt, context switching, onboarding

### Cost Optimization
- **Right-sizing**: matching resources to actual needs
- **Reserved instances**: commit for discount (1yr, 3yr)
- **Spot instances**: use spare capacity for non-critical workloads
- **Auto-scaling**: scale down when not needed
- **Caching**: reduce compute and database costs
- **Serverless**: pay per execution, not per hour

### Financial Modeling
- **Scenario analysis**: best case, worst case, most likely
- **Sensitivity analysis**: which variables matter most
- **Monte Carlo simulation**: probabilistic outcomes
- **Break-even analysis**: when costs = revenue
- **Unit economics**: cost per user, cost per transaction

### Build vs. Buy
- **Build**: more control, more expensive, longer time-to-market
- **Buy**: less control, faster, may not fit perfectly
- **Total Cost of Ownership**: purchase + maintenance + integration + opportunity cost
- **Core vs. context**: build what's core, buy what's context

## Flujo de Trabajo

1. **Identificar costs**: enumerate all costs (infra, dev, ops, hidden)
2. **Estimate ROI**: gain vs. cost, payback period, NPV
3. **Model scenarios**: best/worst/most likely cases
4. **Analyze build vs. buy**: for each major component
5. **Identify optimization opportunities**: right-sizing, reserved, caching
6. **Create financial model**: projections, break-even, sensitivity
7. **Validate assumptions**: check estimates against reality
8. **Present recommendations**: clear ROI, trade-offs, next steps

## Integración con Pipeline

- **Briefing (Fase 1)**: understand budget constraints, business case
- **Spec (Fase 2)**: document cost requirements, ROI targets
- **Plan (Fase 3)**: estimate project costs, identify cost optimization
- **Build (Fase 4)**: implement cost-efficiently, monitor costs
- **QA (Fase 5)**: verify cost estimates, test cost optimization
- **Retro (Fase 6)**: actual vs. estimated costs, lessons for next project

## Referencia

- Constitución Evol-DD: Art. 8 (engineering standards - cost efficiency)
- Agentes relacionados: evol-devops (infrastructure costs), evol-pm (budget management), evol-domain-finance (financial modeling)
- AWS Well-Architected Framework: Cost Optimization pillar
- Google Cloud Architecture Framework: Cost optimization
- Tom DeMarco - "Controlling Software Projects": measurement and estimation
