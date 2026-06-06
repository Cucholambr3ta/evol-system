# RF-06 — Wake-up Context

**Estado:** Aprobado | **Prioridad:** Alta | **Esfuerzo:** Medio

## Descripción

Generar contexto compacto (~170 tokens) para nueva sesión desde EDMS.

## Criterios de aceptación

- [ ] `evol-memory.py wake-up --proyecto=evol-dd --sprint=05` genera string <200 tokens
- [ ] Incluye: sprint actual, decisiones recientes, lecciones aplicables, riesgos activos
- [ ] Integrado en `session-start-context-load.sh` (hook existente)
- [ ] Fallback a BM25 si EDMS no disponible

## Dependencias

- RF-01, RF-03

## Archivos

- `scripts/evol_memory_store.py` → `MemoryStore.get_context()`
- `scripts/evol-memory.py` → subcomando `wake-up`
- `tests/test_memory_store.py::test_wake_up_context`
