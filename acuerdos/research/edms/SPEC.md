# SPEC — EDMS: Evol-DD Memory System

> **Fecha:** 2026-06-06 | **Estado:** Aprobado
> **Plan de implementación:** `docs/plan-implementacion-edms.md` (720 líneas)

---

## Requisitos Funcionales

### RF-01 — ChromaDB Index

- **Descripción:** Indexar texto verbatim + metadata en ChromaDB con colección `evol_memory`
- **Entrada:** texto + dict metadata (proyecto, sprint, fase, tipo, disciplinas[], etc.)
- **Salida:** ID de drawer insertado
- **Pre-condición:** ChromaDB instalado (`pip install -e ".[memory]"`)
- **Post-condición:** Drawer searchable por vector cosine
- **Archivos:** `scripts/evol_memory_store.py`, `scripts/evol-memory.py` (subcomando `index`)
- **Tests:** `tests/test_memory_store.py::test_chromadb_index_and_search`

### RF-02 — ChromaDB Search

- **Descripción:** Buscar drawers por query de texto con filtro metadata
- **Entrada:** query string + filtros opcionales (proyecto, fase, tipo, disciplinas[])
- **Salida:** lista de resultados ordenados por distance
- **Archivos:** `scripts/evol_memory_store.py`, `scripts/evol-memory.py` (subcomando `search`)
- **Tests:** `tests/test_memory_store.py::test_chromadb_index_and_search`

### RF-03 — LadybugDB Graph

- **Descripción:** Crear nodos (Proyecto, Sprint, Artefacto, Disciplina, Decision, Leccion, Riesgo, Handoff) y relaciones (DEFINE, Produce, AFECTA, APLICA_A, CAUSA, SOLUCIONA, PREVIENE, BLOQUEA, HABILITA)
- **Entrada:** tipo de nodo + propiedades, par de nodos + tipo de relación
- **Salida:** nodo/relación creado, traversal result
- **Archivos:** `scripts/evol_memory_store.py`, `scripts/evol-memory.py` (subcomando `graph`)
- **Tests:** `tests/test_memory_store.py::test_ladybugdb_graph_creation`

### RF-04 — RRF Fusion

- **Descripción:** Reciprocal Rank Fusion (k=60) entre 3 streams: BM25 + Vector + Graph
- **Entrada:** 3 rankings (cada uno es lista ordenada de IDs)
- **Salida:** ranking fusionado ordenado por score RRF
- **Archivos:** `scripts/evol_memory_store.py`
- **Tests:** `tests/test_memory_store.py::test_rrf_fusion`

### RF-05 — Privacy Stripping

- **Descripción:** Eliminar API keys, tokens, passwords, PII antes de indexar. 11 patrones regex.
- **Entrada:** texto crudo
- **Salida:** texto sin secrets (REDACTED)
- **Archivos:** `scripts/evol_memory_store.py`
- **Tests:** `tests/test_memory_store.py::test_privacy_strip`

### RF-06 — Wake-up Context

- **Descripción:** Generar contexto compacto (~170 tokens) para nueva sesión desde EDMS
- **Entrada:** proyecto + sprint actual
- **Salida:** string con resumen de memoria relevante
- **Archivos:** `scripts/evol_memory_store.py`, `scripts/evol-memory.py` (subcomando `wake-up`)
- **Tests:** `tests/test_memory_store.py::test_wake_up_context`

### RF-07 — Bootstrap de Historia

- **Descripción:** Importar `acuerdos/`, `lecciones/`, `memoria.md` existentes al EDMS
- **Entrada:** directorio del proyecto
- **Salida:** draws indexados en ChromaDB + nodos en LadybugDB
- **Archivos:** `scripts/evol-memory.py` (subcomando `bootstrap`)
- **Tests:** `tests/test_memory_store.py::test_bootstrap`

### RF-08 — Composite Scoring

- **Descripción:** Score compuesto post-RRF: 50% vector + 30% recency + 20% importance
- **Entrada:** item + query_time
- **Salida:** float score
- **Archivos:** `scripts/evol_memory_store.py`
- **Tests:** `tests/test_memory_store.py::test_composite_scoring`

---

## Requisitos No Funcionales

### RNF-01 — Fallback stdlib

- **Descripción:** Sin ChromaDB/LadybugDB instaladas, BM25 stdlib sigue funcionando
- **Validación:** Desinstalar chromadb, ejecutar `evol-memory search "test"`, verificar resultado
- **Archivos:** `scripts/evol_memory_store.py` (try/except import)

### RNF-02 — Privacy compliance

- **Descripción:** Ningún secret debe llegar a ChromaDB o LadybugDB
- **Validación:** Test con 11 patrones de secrets, verificar que todos son REDACTED
- **Archivos:** `scripts/evol_memory_store.py::privacy_strip`

### RNF-03 — Discipline-aware schema

- **Descripción:** Campo `disciplinas[]` multi-value en metadata. 31 disciplinas como filtro.
- **Validación:** Indexar con `disciplinas: ["sec-driven", "ddd"]`, buscar con filtro `disciplinas=sec-driven`
- **Archivos:** `scripts/evol_memory_store.py`

---

## Archivos a Crear

| Archivo | Descripción |
|---------|-------------|
| `scripts/evol_memory_store.py` | Capa de abstracción ChromaDB + LadybugDB |
| `scripts/post-edit-memory-index.sh` | Hook de indexación automática post-edit |
| `scripts/session-end-handoff.sh` | Hook de handoff al final de sesión |
| `scripts/post-tool-failure-capture.sh` | Hook de captura de errores → lecciones |
| `~/.evol/memory/config.json` | Configuración global de memoria |
| `tests/test_memory_store.py` | Tests unitarios del store |
| `tests/test_memory_hooks.py` | Tests de hooks de memoria |

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `scripts/evol-memory.py` | +index, +search, +wake-up, +graph, +bootstrap |
| `scripts/_evol_common.py` | Actualizar `find_memory_db()` |
| `pyproject.toml` | `[project.optional-dependencies] memory` |
| `.agent/hooks/hooks.json` | +4 hooks |
| `.agent/hooks/scripts/session-start-context-load.sh` | +wake-up EDMS |
