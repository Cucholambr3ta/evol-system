# Code Graph Indexer — Evol-DD

**Objetivo:** Indexar el codebase usando Tree-sitter para construir un grafo de código estructurado. Soporta indexación completa, incremental (git diff), análisis de impacto y trazado de procesos.

---

## Stack Tecnológico

| Capa | Componente | Versión |
|------|-----------|---------|
| Parser | Tree-sitter | >= 0.23.0 |
| Gramáticas | tree-sitter-python, tree-sitter-javascript, tree-sitter-typescript | Latest |
| Graph DB | LadybugDB (instancia separada) | 0.17.1 |
| Fallback | JSON local (`code_graph.json`) | N/A |

---

## Flujo de Ejecución

### 1. Indexación Completa del Proyecto

```bash
python3 scripts/evol_code_indexer.py index
```

**Proceso:**
1. Escanea archivos `.py`, `.js`, `.ts`, `.tsx` en el proyecto
2. Parsea cada archivo con Tree-sitter (gramática apropiada por extensión)
3. Extrae nodos: File, Module, Symbol (Function/Class/Method), Test
4. Extrae relaciones: IMPORTS, CALLS, EXTENDS, CONTAINS, EXPORTS
5. Almacena en LadybugDB (`evol_dd_codigo.lbug`) o fallback JSON
6. Actualiza marker de commit: `.evol/.last-code-index-commit`

**Resultado:**
```
📊 Code Graph Index: 85 files, 958 symbols, 9641 relations
```

### 2. Indexación Incremental (Git Diff)

```bash
python3 scripts/evol_code_indexer.py incremental
```

**Proceso:**
1. Lee marker: `git rev-parse $(cat .evol/.last-code-index-commit)..HEAD`
2. Obtiene archivos modificados: `git diff --name-only $LAST_COMMIT..HEAD`
3. Re-parsea solo archivos modificados con Tree-sitter
4. Actualiza relaciones afectadas en LadybugDB
5. Actualiza marker de commit

**Resultado:**
```
📊 Incremental: 5 files changed, 12 symbols updated, 47 relations refreshed
```

### 3. Análisis de Impacto

```bash
python3 scripts/evol_code_indexer.py impact <SymbolName> --depth=3
```

**Proceso:**
1. Busca símbolo en el grafo (query exacto o parcial)
2. Traversa relaciones CALLS hacia atrás (quién llama a este símbolo)
3. Retorna impacto por profundidad:
   - **Depth-1**: Llamadores directos (afectados inmediatamente)
   - **Depth-2**: Llamadores de llamadores (afectados indirectamente)
   - **Depth-3**: Impacto transitivo más profundo

**Resultado:**
```
Impacto de 'MemoryStore': 54 símbolos afectados
  Depth-1: 28 símbolos (evol_memory_store.py:150, evol_memory.py:89, ...)
  Depth-2: 21 símbolos (evol-orchestrate.py:234, ...)
  Depth-3: 5 símbolos (scripts/evol-start.sh:67, ...)
```

### 4. Trazado de Procesos

```bash
python3 scripts/evol_code_indexer.py trace <EntryPoint> --max-depth=5
```

**Proceso:**
1. Busca punto de entrada (función o método)
2. Traversa relaciones CALLS hacia adelante (qué llama este símbolo)
3. Retorna cadena de ejecución completa
4. Detecta ciclos y los marca

**Resultado:**
```
Trace de 'session_start':
  session_start()
    → load_config()
    → wake_up()
      → edms_wake_up()
        → get_context()
    → run_hooks()
```

### 5. Consulta de Símbolos

```bash
python3 scripts/evol_code_indexer.py query <Pattern>
```

**Proceso:**
1. Búsqueda parcial en nombres de símbolos
2. Filtra por tipo (Function, Class, Method, Module)
3. Retorna lista de coincidencias con ubicación

### 6. Estadísticas del Grafo

```bash
python3 scripts/evol_code_indexer.py stats
```

**Resultado:**
```
📊 Code Graph Stats:
  Nodes: 958 (Files: 85, Symbols: 873)
  Relations: 9641 (CALLS: 9201, CONTAINS: 1043, EXPORTS: 958, IMPORTS: 440)
  Last index: commit abc1234 (2 hours ago)
  Languages: Python (156), JavaScript (89), TypeScript (43)
```

---

## Integración con EDMS

### Vía Orchestrator

```bash
edms-code-index          # Indexación completa
edms-code-impact <Sym>   # Análisis de impacto
edms-code-trace <Entry>  # Trazado de procesos
edms-code-query <Pat>    # Búsqueda de símbolos
edms-code-stats          # Estadísticas
```

### Vía Bootstrap

El `edms_bootstrap()` step 10 ejecuta indexación incremental automáticamente:

```bash
python3 scripts/evol_memory_store.py code-index
```

### Vía Hooks

- **post-commit**: `post-commit-code-index.sh` ejecuta indexación incremental después de cada commit
- **session-start**: `session-start-context-load.sh` muestra estadísticas del code graph

---

## Almacenamiento

### LadybugDB (`evol_dd_codigo.lbug`)

**Tablas:**
```sql
CREATE TABLE CodeNode (
    name STRING PRIMARY KEY,
    type STRING,  -- File, Module, Symbol, Test, Commit, Branch
    properties STRING  -- JSON codificado en base64
);

CREATE TABLE CodeRel (
    FROM CodeNode,
    TO CodeNode,
    relation STRING,  -- IMPORTS, CALLS, EXTENDS, CONTAINS, EXPORTS, TESTS, MODIFIES, BLAME
    metadata STRING  -- JSON
);
```

### Fallback JSON (`.evol/memory/code_graph.json`)

Cuando LadybugDB no está disponible, el code graph se almacena como JSON local con la misma estructura de nodos y relaciones.

---

## Métricas de Éxito

| Métrica | Target |
|---------|--------|
| Archivos indexados | 100% de `.py`, `.js`, `.ts`, `.tsx` |
| Símbolos extraídos | > 500 por proyecto mediano |
| Tiempo indexación incremental | < 5s para < 10 archivos |
| Tiempo análisis impacto | < 2s para depth=3 |
| Precisión trazado | 100% de relaciones CALLS |
