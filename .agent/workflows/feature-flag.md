---
description: Crea, gobierna y retira feature flags. Mantiene FLAGS.md como inventario único.
name: feature-flag
trigger: /evol feature-flag
---
# /feature-flag

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-FLAGS | **Versión:** 1.0 | **Agente:** Feature-Flag-Manager
**Misión:** Desacoplar deploy de release y permitir kill switches sin riesgo.

## 0. Pre-flight
- Crea `FLAGS.md` desde `templates/flags.template.md` si no existe.
- Verifica stack elegido en `xdd.profile.yml > stacks.feature_flags`.

<!-- CONFIGURAR: Stack de feature flags. Opciones:                          -->
<!--  - LaunchDarkly: SaaS, mejor DX, pago por seat                          -->
<!--  - Unleash: OSS auto-hospedable                                         -->
<!--  - Flagsmith: híbrido                                                   -->
<!--  - GrowthBook: foco en experimentación                                  -->

## 1. Tipo de flag
Selecciona y nombra con prefijo:
- `release_*` — desacoplar deploy de release. Vida corta.
- `exp_*` — A/B test. Vida corta (hasta análisis).
- `perm_*` — entitlement por plan/rol. Vida larga.
- `kill_*` — switch de degradación. Vida larga.

## 2. Definición
Para cada flag captura: key, tipo, owner, audiencia inicial, default (OFF en prod salvo kill), métrica de éxito, fecha objetivo de retiro.

## 3. Implementación
- Usa wrapper local (`isEnabled(key, ctx)`) — nunca llames al SDK del proveedor en cada uso.
- Default seguro si el SDK no responde (fail-closed para release, fail-open para kill).
- Tests con flag en ambos estados.

## 4. Gobernanza
- Cada flag se añade a `FLAGS.md` en el commit que la introduce.
- Retiro automático sugerido si flag > 90 días al 100% o al 0%.
- Linter de CI rechaza flags sin owner o sin fecha de retiro.

## 5. Experimentos (exp_*)
- Hipótesis declarada antes de empezar (Si X → esperamos Y, métrica Z).
- Cálculo de tamaño muestral mínimo.
- Stop rule: análisis cuando se alcance n; no peek prematuro.
- Resultados a `lecciones.md` y a [[adr-new]].

## 6. Gated (Art. 2)
`"APROBADO"` antes de:
- Rollout > 25% en producción.
- Cambio de default en kill switches.

## 7. Cierre
Actualiza `FLAGS.md`, indexa con MemPalace.
