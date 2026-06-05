---
name: event-sourcing
trigger: /evol event-sourcing
description: Event Sourcing-Driven Development (ESDD). Disena el event store y la logica de aplicacion de eventos por aggregate, donde el estado se deriva de eventos inmutables. Produce eventsourcing/event_store_schema.json + aggregates con tests de replay. Usar cuando el dominio requiere auditoria completa o reconstruccion de estado historico. Disciplina docs/disciplinas/ESDD.md.
phase: spec
category: architecture
---

# /evol event-sourcing — Event Sourcing-Driven Development (ESDD)

> **Estandar de documentacion:** cumple [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md).
> Disciplina: [`docs/disciplinas/ESDD.md`](../../docs/disciplinas/ESDD.md).

**ID:** FLUJO-ESDD | **Version:** 1.0 | **Agente:** Event-Sourcer (efimero) + Domain
**Mision:** Disenar un event store donde el estado se deriva de eventos inmutables reproducibles.
**Activacion:** solo si `evol.profile.yml` declara `esdd` en `methodologies:`.

## 0. Pre-flight

- Requiere `entities/*.json` (DDD) y `events/*.json` (catalogo de eventos).
- Lee `acuerdos/memoria/MEMORY.md` + lecciones (Art. 3).
- Si faltan entidades/eventos: ABORT -> completar DDD/EDA primero.

## 1. Disenar el event store

`eventsourcing/event_store_schema.json`:
- Estructura del stream (aggregate_id, version, tipo de evento, payload, timestamp).
- Politica de concurrencia optimista (version esperada).
- Estrategia de snapshots y compactacion para performance de replay.

## 2. Definir aggregates

Por cada aggregate con event sourcing, `eventsourcing/aggregates/<aggregate>.md`:
- Eventos que produce/consume.
- Funcion de aplicacion `apply(state, event) -> state'` (deterministica).
- Invariantes que la reproduccion debe preservar.

## 3. Tests de replay

Generar tests que verifiquen: `estado = reduce(eventos)` de forma reproducible. El mismo log
de eventos siempre reconstruye el mismo estado.

## 4. Derecho al olvido sobre eventos inmutables

Documentar la estrategia (crypto-shredding u otra) para cumplir [PrivacyDD](../../docs/disciplinas/PrivacyDD.md)
sin violar la inmutabilidad del log.

## 5. Output + gate (worker -> auditor)

- Sidecar `.json` por doc via `evol-doc-sync`. Fuentes con URL (DOC_STANDARD).
- **Auditor** (Reviewer != worker) rechaza si: replay no deterministico, falta estrategia de
  snapshots, o no se aborda el derecho al olvido.

## 6. Integracion

- Usa los schemas de [EDA](../../docs/disciplinas/EDA.md) para los eventos persistidos.
- Los aggregates son los aggregates de [DDD](../../docs/disciplinas/DDD.md).

---
*X-DD — disciplina ESDD. Ver [docs/disciplinas/ESDD.md](../../docs/disciplinas/ESDD.md).*
