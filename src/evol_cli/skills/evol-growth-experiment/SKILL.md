---
name: evol-growth-experiment
description: A/B testing y experimentation frameworks para optimización de conversión. Diseña experiments, mide resultados itera basado en datos.
category: transfer
trigger: /growth
---

# evol-growth-experiment

## Cuándo Usar

Activar esta skill cuando se necesita diseñar y ejecutar experiments de crecimiento:

- **Experiment design**: hipótesis, variables, métricas, sample size
- **A/B testing**: split tests, multivariate testing, feature flags
- **Conversion optimization**: CRO, funnel optimization, drop-off analysis
- **Metrics definition**: north star metric, input metrics, guardrail metrics
- **Statistical analysis**: significance, confidence intervals, bayesian analysis
- **Growth loops**: self-reinforcing loops de crecimiento

**No usar para**: analytics generales (usar evol-data), SEO technical (usar evol-seo-technical).

## Conocimiento de Dominio

### Experiment Design
- **Hypothesis format**: "We believe [action] will result in [outcome] because [reasoning]"
- **Variables**: independent (what we change), dependent (what we measure), controlled (what we keep same)
- **Sample size**: calculado basado en MDE, baseline conversion, significance level
- **Duration**: mínimo 1-2 business cycles, no stopping early

### A/B Testing
- **Split testing**: users randomly assigned to A or B
- **Multivariate testing**: multiple variations simultaneously
- **Feature flags**: gradual rollouts, kill switches
- **Cuped**: variance reduction using pre-experiment data
- **Bayesian analysis**: probability of being best, not just p<0.05

### Conversion Optimization
- **North star metric**: single metric that captures product value
- **Input metrics**: controllable metrics that drive north star
- **Guardrail metrics**: metrics we don't want to hurt
- **Micro-conversions**: small steps toward main conversion
- **Drop-off analysis**: where users leave, why, how to fix

### Growth Loops
- **Acquisition → Activation → Revenue → Referral**: classic growth loop
- **Viral loops**: users bring users (K-factor > 1)
- **Content loops**: users create content that attracts more users
- **Paid loops**: spend money → get users → get revenue → spend more

### Statistical Rigor
- **Minimum Detectable Effect (MDE)**: smallest effect we care about
- **Statistical significance**: p-value threshold (typically 0.05)
- **Practical significance**: is the effect size meaningful?
- **Multiple comparisons**: Bonferroni correction, false discovery rate
- **Peeking problem**: don't stop experiments early based on results

## Flujo de Trabajo

1. **Identificar oportunidad**: dónde hay potencial de mejora, qué metric mover
2. **Formular hipótesis**: qué creemos que pasará y por qué
3. **Diseñar experiment**: variables, sample size, duration, success criteria
4. **Implementar**: feature flags, tracking, variations
5. **Ejecutar**: run experiment, don't touch, monitor guardrails
6. **Analizar resultados**: statistical significance, practical significance
7. **Decidir**: ship winner, iterate, or kill experiment
8. **Documentar learnings**: what we learned, what we'll try next

## Integración con Pipeline

- **Briefing (Fase 1)**: identify growth opportunities, define north star
- **Spec (Fase 2)**: document experiment design, metrics, success criteria
- **Plan (Fase 3)**: prioritize experiments by impact × confidence
- **Build (Fase 4)**: implement feature flags, tracking, variations
- **QA (Fase 5)**: test experiment setup, verify tracking accuracy
- **Retro (Fase 6)**: analyze results, document learnings, plan next experiments

## Referencia

- Constitución Evol-DD: Art. 9 (pipeline con iteración)
- Agentes relacionados: evol-data (analytics), evol-ux (user behavior), evol-marketing (marketing metrics)
- Ronny Kohavi - "Trustworthy Online Controlled Experiments": the A/B testing bible
- Reforge - growth frameworks and loops
- experimentation.dev: community of practice
