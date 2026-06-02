---
description: Bootstrap de observabilidad. Define SLI/SLO, logs estructurados, métricas, tracing y dashboards.
name: observability-init
trigger: /evol observability-init
---
# /observability-init

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-OBS | **Versión:** 1.0 | **Agente:** SRE + DevOps-Automator
**Misión:** Que el sistema sea diagnosticable en producción sin acceder al código.

## 0. Pre-flight
- Detecta stack en `xdd.profile.yml > stacks.observability`.
- Requiere `FEATURES.md` y servicios críticos identificados.

<!-- CONFIGURAR: Stack de observabilidad. Opciones:                            -->
<!--  - Grafana stack: Loki (logs) + Prometheus (metrics) + Tempo (traces) OSS  -->
<!--  - Datadog: SaaS unificado, mejor DX, caro a escala                        -->
<!--  - New Relic, Honeycomb (eventos), Lightstep                               -->
<!--  - AWS CloudWatch / GCP Cloud Operations / Azure Monitor (cloud-native)    -->

## 1. SLI / SLO por servicio crítico
Para cada servicio (no para "todo el sistema"):
- **SLI**: latencia p95, error rate, availability, throughput.
- **SLO**: objetivo numérico con ventana (ej. 99.9% uptime mensual).
- **Error budget**: 1 - SLO. Política de quema documentada.

## 2. Logs estructurados
- Formato JSON o logfmt (no texto libre).
- Campos obligatorios: `timestamp`, `level`, `service`, `trace_id`, `user_id` (si aplica y sin PII).
- Niveles bien usados: `ERROR` solo para algo que requiere acción humana.
- Correlación con tracing vía `trace_id`.

## 3. Métricas
- Golden signals (USE/RED): latency, traffic, errors, saturation.
- Cardinalidad bajo control (no usar `user_id` como label).
- Business metrics además de técnicas (conversiones, transacciones críticas).

## 4. Tracing distribuido
- OpenTelemetry (estándar agnóstico). Instrumentación auto donde sea posible, manual en spans clave.
- Sampling configurable (head-based en bajo tráfico, tail-based en alto).

## 5. Dashboards y alertas
- Dashboard por servicio + uno overview.
- Alertas SLO-based (multi-window multi-burn-rate), no umbrales caprichosos.
- Cada alerta enlaza a runbook (`templates/runbook.template.md`).

## 6. Higiene
- Logs sin PII (cruzar con `PRIVACY.md`).
- Retención por nivel: hot (7d) → warm (30d) → cold (1y).
- Coste monitorizado (cruzar con `/finops-baseline`).

## 7. Cierre
- Documentar SLOs en `SPEC.md` o `docs/SLO.md`.
- Anotar dashboards principales en `ONBOARDING.md`.
