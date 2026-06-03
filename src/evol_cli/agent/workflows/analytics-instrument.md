---
description: Instrumenta product analytics. Define schema de eventos, valida en CI, conecta a CDP/proveedor.
name: analytics-instrument
trigger: /evol analytics-instrument
---
# /analytics-instrument

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-ANALYTICS | **Versión:** 1.0 | **Agente:** Product-Analytics-Architect
**Misión:** Que cada decisión de producto se base en datos, no en opiniones.

## 0. Pre-flight
- Copia `templates/events.schema.template.json` a `events.schema.json` si no existe.
- Verifica stack en `xdd.profile.yml > stacks.analytics`.

<!-- CONFIGURAR: Stack analytics. Opciones:                                  -->
<!--  - PostHog (OSS, autohospedable o cloud)                                 -->
<!--  - Segment / RudderStack (CDP — abstrae proveedores)                     -->
<!--  - Amplitude / Mixpanel (analytics producto SaaS)                        -->

## 1. Plan de tracking
Por cada feature de `FEATURES.md`, define eventos clave que respondan:
- ¿Se descubre? (impression, view)
- ¿Se intenta? (started, opened)
- ¿Se completa? (completed, succeeded)
- ¿Se abandona? (abandoned, error)

Anti-patrón: trackear todo. Regla: cada evento debe responder una pregunta de producto declarada.

## 2. Esquema (events.schema.json)
- Naming: `snake_case`, formato `object_action` (`checkout_started`, no `startedCheckout`).
- Propiedades comunes en `context` (app_version, platform, locale).
- Propiedades específicas validadas con sub-schema.
- Versionar el schema (`$id` + semver).

## 3. Identificación
- `user_id`: ID estable post-login (UUID, no email).
- `anonymous_id`: persistente pre-login (cookie/localStorage).
- Cuando hay login, `alias()` para unificar histórico.
- Nunca incluir PII en propiedades (email, nombre) salvo trait explícito por user.

## 4. Implementación
- Wrapper local `track(event, props)` que valida contra `events.schema.json` en dev.
- Tests CI rechazan PRs con `track()` que no encajen en schema.
- Eventos críticos también emitidos a logs estructurados (auditoría).

## 5. Privacidad
Cruzar con `PRIVACY.md`:
- Consent management (no track antes de consent en jurisdicciones requeridas).
- Endpoint de borrado (DSAR) afecta también al proveedor de analytics.

## 6. Cierre
- Documenta dashboards iniciales esperados (funnel principal, retención, activación).
- Snapshot del schema → ADR si cambios mayores.
