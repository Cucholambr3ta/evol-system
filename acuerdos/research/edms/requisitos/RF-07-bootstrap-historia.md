# RF-07 — Bootstrap de Historia

**Estado:** Aprobado | **Prioridad:** Media | **Esfuerzo:** Medio

## Descripción

Importar `acuerdos/`, `lecciones/`, `memoria.md` existentes al EDMS.

## Criterios de aceptación

- [ ] `evol-memory.py bootstrap --proyecto=evol-dd` escanea acuerdos/**/*.md
- [ ] Cada archivo → drawer en ChromaDB con metadata auto-detectada
- [ ] Extracto de relaciones → nodos en LadybugDB
- [ ] Idempotente (no duplica si se corre 2 veces)
- [ ] Muestra stats: archivos procesados, drawers insertados, nodos creados

## Dependencias

- RF-01, RF-03

## Archivos

- `scripts/evol-memory.py` → subcomando `bootstrap`
- `tests/test_memory_store.py::test_bootstrap`
