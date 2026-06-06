# RF-02 — ChromaDB Search

**Estado:** Aprobado | **Prioridad:** Alta | **Esfuerzo:** Medio

## Descripción

Buscar drawers por query de texto con filtro metadata.

## Criterios de aceptación

- [ ] `evol-memory.py search "gate HMAC" --proyecto=evol-dd` retorna resultados ordenados por distance
- [ ] Filtros: `--fase`, `--tipo`, `--disciplinas`, `--sprint`
- [ ] Resultados incluyen: text, metadata, distance
- [ ] Fallback a BM25 stdlib si ChromaDB no disponible

## Dependencias

- RF-01 (ChromaDB Index)

## Archivos

- `scripts/evol_memory_store.py` → `MemoryStore.search()`
- `scripts/evol-memory.py` → subcomando `search`
- `tests/test_memory_store.py::test_chromadb_index_and_search`
