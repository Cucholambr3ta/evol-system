# RF-03 — LadybugDB Graph

**Estado:** Aprobado | **Prioridad:** Alta | **Esfuerzo:** Alto

## Descripción

Crear nodos (Proyecto, Sprint, Artefacto, Disciplina, Decision, Leccion, Riesgo, Handoff) y relaciones en LadybugDB.

## Criterios de aceptación

- [ ] `evol-memory.py graph add-node Proyecto --props='{"name":"evol-dd"}'` crea nodo
- [ ] `evol-memory.py graph add-relation evol-dd DEFINE DDD` crea relación
- [ ] `evol-memory.py graph traverse evol-dd` retorna subgrafo conectado
- [ ] 8 tipos de nodos soportados
- [ ] 9 tipos de relaciones soportadas
- [ ] Fallback a dict en memoria si LadybugDB no disponible

## Dependencias

- LadybugDB instalado (`pip install -e ".[memory]"`)

## Archivos

- `scripts/evol_memory_store.py` → `MemoryStore.graph_*()`
- `scripts/evol-memory.py` → subcomando `graph`
- `tests/test_memory_store.py::test_ladybugdb_graph_creation`
