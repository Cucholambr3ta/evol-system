---
description: Establece y verifica presupuestos de performance (CWV, bundle size, latencias) en CI.
name: perf-budget
trigger: /evol perf-budget
---
# /perf-budget

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-PERF | **Versión:** 1.0 | **Agente:** Performance-Benchmarker + Frontend-Developer
**Misión:** Performance como contrato. Regresiones bloquean merge, no se discuten.

## 0. Pre-flight
- Identifica tipo de proyecto (web, mobile, backend) en `xdd.profile.yml`.

## 1. Presupuestos por dominio

### Web (Core Web Vitals)
- **LCP** ≤ 2.5s (p75 real users)
- **INP** ≤ 200ms (p75)
- **CLS** ≤ 0.1 (p75)
- **TTFB** ≤ 800ms
- **JS bundle inicial**: <CONFIGURAR: ej. ≤ 170 KB gzip>
- **CSS crítico**: ≤ 14 KB inline

### Backend
- **p95 latencia** por endpoint crítico (cap por endpoint, no global)
- **Error rate** ≤ 0.1%
- **Throughput** objetivo bajo carga representativa

### Mobile
- **App launch time** (cold) ≤ 2s
- **Crash-free users** ≥ 99.5%
- **Binary size** ≤ <CONFIGURAR>

## 2. Medición
<!-- CONFIGURAR: Herramientas.                                                 -->
<!--  - Web: Lighthouse CI, WebPageTest, Calibre, SpeedCurve, RUM (PostHog)     -->
<!--  - Bundle: bundlewatch, size-limit, statoscope                             -->
<!--  - Backend: k6, Gatling, Locust, autocannon                                -->
<!--  - Mobile: Firebase Perf, Sentry Performance, native profilers             -->

## 3. CI gate
- Cada PR ejecuta benchmark contra presupuesto.
- Regresión > X% en métrica crítica → bloquea merge.
- Resultados publicados como comment del PR.

## 4. RUM (Real User Monitoring)
- Producción mide CWV reales (no solo lab).
- Cruzar con `/observability-init`.
- Alertas si percentiles se degradan.

## 5. Gobernanza
- Owner por presupuesto.
- Revisión trimestral de caps (subir/bajar según evidencia).
- Excepciones documentadas con fecha de re-evaluación.

## 6. Cierre
- Presupuestos versionados en `perf.budget.json` o equivalente.
- Hallazgos críticos → ADR vía `/adr-new`.
