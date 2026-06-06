# RF-01 — ChromaDB Index

**Estado:** Aprobado | **Prioridad:** Alta | **Esfuerzo:** Medio

## Descripción

Indexar texto verbatim + metadata en ChromaDB con colección `evol_memory`.

## Criterios de aceptación

- [ ] `evol_memory_store.py` crea colección `evol_memory` si no existe
- [ ] `evol-memory.py index "texto" --proyecto=evol-dd --sprint=05 --tipo=decision --disciplinas=sec-driven,ddd` inserta drawer
- [ ] Metadata completa: proyecto, sprint, fase, tipo, sector, disciplinas[], agente, scope, source_file, importance, fecha, indexed_at
- [ ] Privacy stripping se ejecuta ANTES de insertar
- [ ] Devuelve ID de drawer insertado

## Dependencias

- ChromaDB instalado (`pip install -e ".[memory]"`)
- `scripts/evol_memory_store.py` (capa de abstracción)

## Archivos

- `scripts/evol_memory_store.py` → `MemoryStore.index()`
- `scripts/evol-memory.py` → subcomando `index`
- `tests/test_memory_store.py::test_chromadb_index_and_search`
