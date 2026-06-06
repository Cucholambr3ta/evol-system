# RF-08 — Composite Scoring

**Estado:** Aprobado | **Prioridad:** Media | **Esfuerzo:** Medio

## Descripción

Score compuesto post-RRF: 50% vector + 30% recency + 20% importance.

## Criterios de aceptación

- [ ] `composite_score(item, query_time)` retorna float
- [ ] Vector score: `item["chroma_distance"]`
- [ ] Recency score: `1.0 / (1 + days_since(item["fecha"]))`
- [ ] Importance score: `item.get("importance", 0.5)`
- [ ] Decay adaptativo por tipo (ver plan §5.4)

## Dependencias

- RF-04

## Archivos

- `scripts/evol_memory_store.py` → `composite_score()`
- `tests/test_memory_store.py::test_composite_scoring`
