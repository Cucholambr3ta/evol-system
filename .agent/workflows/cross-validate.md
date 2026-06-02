---
name: cross-validate
title: "/cross-validate — Verificar consistencia entre artefactos"
description: Detecta drift entre pares de artefactos (MISSING/CONFLICT/ORPHAN). Bloquea gate si MISSING o CONFLICT. Inspirado en Spec-Kit /cross-validate.
phase: any
category: planning
ssot: true
inputs:
  - 2+ artefactos relacionados (SPEC.md ↔ DOMAIN.md, PLAN.md ↔ FEATURES.md, etc.)
outputs:
  - REPORT.md de inconsistencias detectadas + sugerencias
inspired_by: Spec-Kit /cross-validate (MIT)
adr: docs/adr/0014-sdd-parity-clarify-cross-validate-constitution.md
---

# /cross-validate — Consistencia entre artefactos

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.

## Propósito
Detectar drift, contradicciones y omisiones entre artefactos relacionados que deberían ser coherentes. Ejemplos típicos:
- SPEC.md menciona "OAuth login" pero THREATS.md no modela auth threats
- PLAN.md tiene 5 features pero FEATURES.md sólo 3
- DOMAIN.md define entidad `Order` pero `openapi.yaml` no la expone
- `events.schema.json` define eventos no referenciados en `PLAN.md`

## Cuándo invocar
- Pre-gate de cualquier fase que tenga artefactos relacionados
- Cuando se modifica un artefacto: validar que sus relacionados siguen consistentes
- Auditoría periódica del repo (post-merge en CI opcional)

## Procedimiento

1. **Definir par(es) de artefactos** a comparar. Pares comunes:
   - SPEC.md ↔ DOMAIN.md (entidades del dominio)
   - SPEC.md ↔ THREATS.md (amenazas por feature)
   - SPEC.md ↔ FEATURES.md (catálogo FDD)
   - PLAN.md ↔ FEATURES.md (plan implementa todas las features)
   - DOMAIN.md ↔ openapi.yaml (entidades expuestas)
   - PLAN.md ↔ events.schema.json (eventos del plan)
   - FLAGS.md ↔ src/ (flags declarados existen en código)
   - PRIVACY.md ↔ DOMAIN.md (PII fields del dominio)

2. **Detectar 3 tipos de drift:**
   - **MISSING:** A menciona X, B no contiene X
   - **CONFLICT:** A y B contienen X con valores incompatibles
   - **ORPHAN:** B contiene X, A no lo menciona

3. **Generar REPORT.md** con findings:
   ```
   ## Cross-Validation Report — <fecha>
   **Pares analizados:** SPEC.md ↔ DOMAIN.md

   ### MISSING (N findings)
   - SPEC.md L42 menciona entidad "Order" — DOMAIN.md no la define
   - SPEC.md L78 menciona "discount rules" — DOMAIN.md no las modela

   ### CONFLICT (M findings)
   - SPEC.md L15: "User has 0..1 Address" vs DOMAIN.md L9: "User has 1..N Address"

   ### ORPHAN (K findings)
   - DOMAIN.md L100 define entidad "Coupon" — SPEC.md no la menciona
   ```

4. **Bloquear gate** si hay findings MISSING o CONFLICT (configurable con `--allow-orphans`).

5. **Proponer fix** al humano: editar artefacto A, editar artefacto B, o aceptar drift con justificación documentada.

## Exit codes
- 0 = todos los pares consistentes
- 1 = al menos 1 MISSING o CONFLICT detectado
- 2 = error de ejecución (artefacto no encontrado, parse error)

## Referencias
- ADR-0014 SDD parity
- Spec-Kit /cross-validate inspiración
- Constitución X-DD Art. 6 (Trazabilidad bidireccional)
