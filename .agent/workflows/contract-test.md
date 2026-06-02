---
description: Tests de contrato consumer-driven (Pact) en Fase 5. Verifica compatibilidad entre servicios.
---
# /contract-test

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-CDC | **Versión:** 1.0 | **Agente:** Contract-Testing-Engineer + API-Tester
**Misión:** Detectar rupturas de contrato API antes del deploy, no en producción.

## 0. Pre-flight
- Requiere `openapi.yaml` (o equivalente) generado por `/api-contract`.
- Identifica consumidores conocidos del API.

## 1. Estrategia
- **Consumer-Driven Contracts (Pact)** para APIs internas con consumidores conocidos.
- **Schema contract** (Spectral + openapi-diff) para APIs públicas/desconocidas.
- Ambas estrategias coexisten.

<!-- CONFIGURAR: Stack. Opciones:                                              -->
<!--  - Pact Foundation (Pact Broker / PactFlow)                                -->
<!--  - Spring Cloud Contract (JVM)                                             -->
<!--  - Dredd (OpenAPI runtime verification)                                    -->
<!--  - Hoverfly / Wiremock (simulación)                                        -->

## 2. Consumidor
Cada cliente del API publica sus expectativas:
- Test que define request esperado y response mínimo aceptable.
- Genera artefacto Pact (`*.pact.json`).
- Publica a broker en CI con `consumer` + `provider` + `version` + `branch`.

## 3. Proveedor
- En CI del proveedor, `can-i-deploy` consulta el broker.
- Si hay contratos rotos para entornos relevantes → bloquea merge/deploy.
- Tras deploy, `record-deployment` marca el entorno.

## 4. Versionado de contratos
- Tag con git SHA y branch.
- Política WIP en branches, verificación estricta en `main`/`release/*`.

## 5. Falsos positivos
- Cambios aditivos (nuevo campo opcional) → no rompe contratos correctamente diseñados.
- Si rompe, revisar consumidores demasiado estrictos (anti-patrón).

## 6. Cierre
- Resultado a `qa-review` Tier 2.
- Si hay ruptura intencional → coordinar con consumidores, plan de migración, deprecación.
