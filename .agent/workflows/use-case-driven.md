---
name: use-case-driven
trigger: /evol use-case-driven
description: Use-Case-Driven Development (UDD). Modela los casos de uso como unidad de diseno y planificacion por encima de las features (actor, objetivo, flujo principal y alternativos). Produce usecases/usecase.json + diagram.puml + test_scenarios.feature por caso de uso. Usar en aplicaciones transaccionales o modernizacion de legacy. Disciplina docs/disciplinas/UDD.md.
phase: briefing
category: requirements
---

# /evol use-case-driven — Use-Case-Driven Development (UDD)

> **Estandar de documentacion:** cumple [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md).
> Disciplina: [`docs/disciplinas/UDD.md`](../../docs/disciplinas/UDD.md).

**ID:** FLUJO-UDD | **Version:** 1.0 | **Agente:** UseCase-Discoverer (efimero) + Product-Manager
**Mision:** Modelar la interaccion actor-sistema completa como unidad de diseno, por encima de la feature.
**Activacion:** solo si `evol.profile.yml` declara `udd` en `methodologies:`.

## 0. Pre-flight

- Requiere `docs/specs/SPEC.md` y `docs/features/FEATURES.md`.
- Lee `acuerdos/memoria/MEMORY.md` + lecciones (Art. 3).
- Si falta SPEC/FEATURES: ABORT -> completar Spec/FDD primero.

## 1. Extraer casos de uso

Por cada interaccion transaccional, `usecases/<caso>/usecase.json`:
- Actor + objetivo.
- Precondiciones y postcondiciones.
- Flujo principal (pasos numerados).
- Flujos alternativos y de excepcion.

## 2. Diagrama de secuencia

`usecases/<caso>/diagram.puml`: secuencia actor-sistema-dependencias del flujo principal.

## 3. Derivar escenarios BDD

`usecases/<caso>/test_scenarios.feature`: un escenario [BDD](../../docs/disciplinas/BDD.md) por
flujo (principal + cada alternativo/excepcion), con vocabulario del DOMAIN.md.

## 4. Trazabilidad

Mapear caso de uso -> REQ-NNN ([SDD](../../docs/disciplinas/SDD.md)) -> features ([FDD](../../docs/disciplinas/FDD.md)).
Cada caso de uso es trazable del objetivo del actor hasta el codigo y sus tests.

## 5. Output + gate (worker -> auditor)

- Sidecar `.json` via `evol-doc-sync`. Fuentes con URL (DOC_STANDARD).
- **Auditor** (Reviewer != worker) rechaza si: faltan flujos alternativos, no hay diagrama, o
  los escenarios no cubren todos los flujos.

## 6. Integracion

- Agrupa features de [FDD](../../docs/disciplinas/FDD.md) en interacciones completas.
- Los [UXDD](../../docs/disciplinas/UXDD.md) journeys enmarcan los casos de uso con UI.

---
*X-DD — disciplina UDD. Ver [docs/disciplinas/UDD.md](../../docs/disciplinas/UDD.md).*
