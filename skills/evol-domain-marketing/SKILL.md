---
name: evol-domain-marketing
description: Asesor de dominio para construir software de marketing y analytics. Aporta conocimiento en SEO, estrategia de contenido, funnels de conversión, A/B testing y analytics.
category: domain-advisor
trigger: /domain-marketing
---

# evol-domain-marketing

## Cuándo Usar

Activar esta skill cuando el sistema Evol-DD necesita construir o auditar software en el dominio de marketing y analytics:

- **SEO y búsqueda**: keyword research, on-page SEO, technical SEO, link building, core web vitals
- **Content strategy**: calendar editorial, content pillars, distribution channels, content scoring
- **Conversion funnels**: funnel design, drop-off analysis, CRO (conversion rate optimization)
- **A/B testing**: experiment design, statistical significance, feature flags, multivariate testing
- **Analytics**: event tracking, attribution modeling, dashboards, cohort analysis
- **Email marketing**: automation flows, segmentation, deliverability, personalization
- **Social media**: scheduling, engagement tracking, sentiment analysis
- **Paid advertising**: campaign management, bid strategies, ROAS optimization

**No usar para**: e-commerce (usar evol-domain-sales), software contable (usar evol-domain-finance).

## Conocimiento de Dominio

### SEO
- **On-page**: title tags, meta descriptions, heading structure, internal linking, schema markup
- **Technical SEO**: crawlability, indexability, site speed, mobile-first, canonical tags
- **Core Web Vitals**: LCP, FID/INP, CLS - métricas de experiencia
- **Keyword research**: search intent, keyword difficulty, long-tail opportunities
- **Link building**: strategies, toxicity analysis, disavow

### Content Strategy
- **Content pillars**: temas centrales, clusters de contenido
- **Editorial calendar**: planificación, producción, distribución
- **Content scoring**: evaluación de calidad, SEO optimization, readability
- **Distribution**: owned, earned, paid channels
- **Repurposing**: adaptar contenido a múltiples formatos y canales

### Conversion Funnels
- **TOFU/MOFU/BOFU**: awareness, consideration, decision stages
- **Micro-conversions**: eventos que preceden a la conversión principal
- **Drop-off analysis**: dónde se pierden usuarios, causas, fixes
- **Landing page optimization**: above the fold, social proof, CTA design

### A/B Testing
- **Hypothesis-driven**: H0/H1, variables independientes, métricas de éxito
- **Statistical significance**: p-value, confidence intervals, sample size
- **Feature flags**: gradual rollouts, kill switches, percentage-based
- **Multivariate testing**: testing múltiples variables simultáneamente

### Analytics
- **Event tracking**: event taxonomy, custom dimensions, user properties
- **Attribution modeling**: last-click, linear, time-decay, data-driven
- **Cohort analysis**: retention curves, behavioral cohorts
- **Dashboards**: KPIs, metrics that matter, avoid vanity metrics

## Flujo de Trabajo

1. **Identificar objetivos de marketing**: ¿Qué se quiere lograr? (tráfico, leads, conversiones, retención)
2. **Mapear el funnel actual**: customer journey, touchpoints, métricas actuales
3. **Diseñar la estrategia SEO**: keyword research, technical audit, content plan
4. **Planificar experiments**: hipótesis, métricas, duración, sample size
5. **Implementar tracking**: event taxonomy, attribution, dashboards
6. **Crear contenido**: content calendar, SEO optimization, distribution
7. **Ejecutar y medir**: A/B tests, analyze results, iterate
8. **Optimizar continuamente**: CRO, funnel improvements, personalization

## Integración con Pipeline

- **Briefing (Fase 1)**: identificar objetivos de marketing y KPIs
- **Spec (Fase 2)**: documentar funnel, métricas, herramientas de analytics necesarias
- **Plan (Fase 3)**: estimar esfuerzo de SEO, contenido, integraciones de analytics
- **Build (Fase 4)**: implementar tracking, dashboards, herramientas de contenido
- **QA (Fase 5)**: testear tracking de eventos, accuracy de analytics, funnel completo
- **Retro (Fase 6)**: analizar métricas de marketing, identificar opportunities de optimización

## Referencia

- Constitución Evol-DD: Art. 5 (consultoría de dominio proactiva)
- Art. 9: pipeline de 6 fases
- Agentes relacionados: evol-ux (user research), evol-data (analytics pipelines), evol-doc (documentación de métricas)
- Google Search Central: https://developers.google.com/search
- CXL Institute: https://cxl.com/institute


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
