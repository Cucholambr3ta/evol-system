# RF-04 — RRF Fusion

**Estado:** Aprobado | **Prioridad:** Alta | **Esfuerzo:** Medio

## Descripción

Reciprocal Rank Fusion (k=60) entre 3 streams: BM25 + Vector + Graph.

## Criterios de aceptación

- [ ] Función `reciprocal_rank_fusion(rankings, k=60)` retorna ranking fusionado
- [ ] k=60 (estándar)
- [ ] Score de cada item: sum(1/(k+rank)) por cada stream
- [ ] Integrado en `MemoryStore.search()` como paso post-retrieval

## Dependencias

- RF-01, RF-02, RF-03

## Archivos

- `scripts/evol_memory_store.py` → `reciprocal_rank_fusion()`
- `tests/test_memory_store.py::test_rrf_fusion`
