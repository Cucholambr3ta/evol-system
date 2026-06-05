---
name: ux-driven
trigger: /evol ux-driven
description: UX-Driven Development (UXDD). Especifica flujos de usuario, mensajes de UI y microinteracciones ANTES del codigo frontend. Produce ux/user_journeys, ux/ui_messages y ux/microinteractions desde el catalogo de features y los wireframes del briefing. Usar cuando el proyecto tiene UI compleja y la experiencia es diferenciadora. Disciplina docs/disciplinas/UXDD.md.
phase: briefing
category: design
---

# /evol ux-driven — UX-Driven Development (UXDD)

> **Estandar de documentacion:** Todo artefacto cumple [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md):
> sin emojis, Mermaid donde haya flujo, tablas, trazabilidad bidireccional. Disciplina:
> [`docs/disciplinas/UXDD.md`](../../docs/disciplinas/UXDD.md).

**ID:** FLUJO-UXDD | **Version:** 1.0 | **Agente:** UX-Designer (efimero) + Product-Manager
**Mision:** Disenar la experiencia (flujos, mensajes, microinteracciones) como artefacto antes del codigo.
**Activacion:** solo si `evol.profile.yml` declara `uxdd` en `methodologies:`.

## 0. Pre-flight

- Requiere `docs/features/FEATURES.md` (FDD) y `acuerdos/wireframes/*.html` del briefing.
- Lee `acuerdos/memoria/MEMORY.md` + lecciones (Art. 3).
- Si falta FEATURES.md o wireframes: ABORT -> completar `/evol briefing` primero.

## 1. Construir user journeys

Por cada flujo principal del producto, generar `ux/user_journeys/<flujo>.json`:
- Pasos del flujo (estados del sistema + accion del usuario).
- Estado emocional esperado por paso (frustracion/confianza/duda).
- Puntos de friccion y como se resuelven.

## 2. Redactar mensajes de UI

`ux/ui_messages/<area>.md` — todos los mensajes (exito, error, vacio, carga):
- **Sin jerga tecnica** (no exponer codigos de error crudos ni stacktraces).
- Un solo origen por mensaje (no duplicar strings).

## 3. Especificar microinteracciones

`ux/microinteractions/<componente>.yaml` — feedback de UI (hover, loading, transiciones,
validacion inline) para los componentes criticos.

## 4. Output + sidecar

Generar el `.json` sidecar con `evol-doc-sync` por cada doc. Toda investigacion de patrones UX
referenciada (Nielsen Norman, etc.) cita su URL (DOC_STANDARD — regla de fuentes).

## 5. Gate (worker -> auditor)

- **Worker** (UX-Designer) escribe; **auditor** (Reviewer != worker) valida:
  - Todo flujo principal tiene journey.
  - 0 jerga tecnica en mensajes de error.
  - 0 strings duplicados.
- El gate de Fase 1 no cierra hasta que el auditor aprueba.

## 6. Integracion

- Alimenta [A11yDD](../../docs/disciplinas/A11yDD.md) (los componentes reciben criterios WCAG).
- Los escenarios [BDD](../../docs/disciplinas/BDD.md) incluyen pasos de UX observables.

---
*X-DD — disciplina UXDD. Ver [docs/disciplinas/UXDD.md](../../docs/disciplinas/UXDD.md).*
