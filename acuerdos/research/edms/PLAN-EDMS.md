# PLAN-EDMS.md — Plan de Implementación: Evol-DD Memory System

> **Objetivo:** Diseñar e implementar el subsistema de Memoria Nativa de Evol-DD usando ChromaDB (vector) + LadybugDB (graph/relacional), integrado al pipeline de 6 fases.
> **Base de investigación:** 24 repositorios de referencia analizados (OpenMemory, agentmemory, Letta/MemGPT, EM-LLM, FlowScript, cognee, mem0, ai-memory, Deja, Cortex, etc.)
> **Versión:** 1.0.0 | **Fecha:** 2026-06-06

---

## 1. Arquitectura

### 1.1 Ubicación y estructura

```
~/.evol/memory/                          # 1 memoria GLOBAL (no per-project)
├── chromadb/                            # ChromaDB: busqueda semántica
│   └── evol_memory/                    # 1 coleccion con multi-tenancy por metadata
│       ├── doc: "texto verbatim"
│       │   meta: {proyecto, sprint, fase, tipo, sector, disciplinas[], agente, ...}
│       └── doc: "resumen comprimido"
│           meta: {proyecto, sprint, tipo: "resumen", ...}
├── ladybugdb/                           # LadybugDB: grafo relacional + knowledge graph
│   └── evol_graph/
│       ├── nodos: Proyecto, Sprint, Artefacto, Disciplina, Decision, Leccion, Riesgo
│       └── relaciones: DEFINE, Produce, AFECTA, APLICA_A, CAUSA, SOLUCIONA, PREVIENE, BLOQUEA, HABILITA
├── config.json                          # configuracion global
└── locks/                               # concurrencia
```

### 1.2 Proyectos no tienen DB propia

Los proyectos guardan artefactos verbatim en `.evol/drawers/` (source of truth) y un indice local `.evol/memory/index.json`. La separación entre proyectos es por **metadata** en la DB global, no por DB separada.

### 1.3 Fallback stdlib

Si ChromaDB o LadybugDB no están instalados, todo sigue funcionando con BM25 stdlib (como ahora). Zero dependencias obligatorias.

---

## 2. 15 Mejoras Investigadas

### Grupo A — Core (implementar obligatorio)

| # | Mejora | Fuente | Esfuerzo |
|---|--------|--------|----------|
| 1 | **RRF Fusion** — Reciprocal Rank Fusion (k=60) entre 3 streams: BM25 + Vector + Graph | agentmemory, Obsidian MCP | Medio |
| 4 | **Composite Scoring** — salience + recency + importance, decay adaptativo por tipo | OpenMemory, mem0, EM-LLM | Medio |
| 7 | **Privacy Stripping** — eliminar API keys, secrets, PII antes de indexar | Secure Memory MCP, agentmemory | Bajo |
| 11 | **12 Hooks de Lifecycle** — mapear hooks de agentpipeline a las 6 fases | agentmemory | Medio |
| 15 | **Discipline-Aware Schema** — metadata con campo `disciplinas[]` multi-value | Ninguno (Evol-DD unique) | Bajo |

### Grupo B — Diferenciador (Fase 2)

| # | Mejora | Fuente | Esfuerzo |
|---|--------|--------|----------|
| 2 | **4-Tier Consolidation** — raw → compressed → memory → knowledge | agentmemory, ai-memory, Letta | Alto |
| 5 | **Causal Chains** — relaciones CAUSA, SOLUCIONA, PREVIENE, BLOQUEA, HABILITA en KG | FlowScript, Letta, cognee | Alto |
| 6 | **Handoff entre sesiones** — markers + prose digest al final de sesión | ai-memory, Deja, Cortex | Medio |
| 13 | **Team Memory Namespaces** — AGENT_ID tagging, scope shared/private | agentmemory | Bajo |
| 14 | **Bootstrap de Historia** — importar acuerdos/, lecciones/, memoria.md existentes | ai-memory, basic-memory | Bajo |

### Grupo C — Futuro (no bloqueante)

| # | Mejora | Fuente | Esfuerzo |
|---|--------|--------|----------|
| 3 | **5-Sector Classification** — episódica, semántica, procedural, reflexiva, emocional | OpenMemory, cognee | Bajo |
| 8 | **Citation Provenance** — source_file, source_line, source_sha en metadata | agentmemory, cognee | Bajo |
| 9 | **Bayesian Surprise** — filtro de sorpresa para eventos memorables | EM-LLM | Alto |
| 10 | **Session Replay Viewer** — dashboard en tiempo real + timeline | agentmemory, ai-memory | Alto |
| 12 | **Self-Editing Memory** — agentes core pueden modificar su memoria durante ejecución | Letta, context-llemur | Medio |

---

## 3. Schema de Metadata (Discipline-Aware)

Cada drawer en ChromaDB lleva esta metadata:

```json
{
  "proyecto": "evol-dd",
  "sprint": "05",
  "fase": "Spec",
  "tipo": "decision|leccion|convencion|riesgo|artefacto|resumen|handoff",
  "sector": "episodica|semantica|procedural|reflexiva|emocional",
  "disciplinas": ["sec-driven", "ddd"],
  "disciplina_primary": "sec-driven",
  "agente": "evol-architect",
  "scope": "shared|private",
  "source_file": "acuerdos/memoria/decisiones.md",
  "source_line": 5,
  "source_sha": "abc123...",
  "importance": 0.8,
  "surprise_score": 0.3,
  "fecha": "2026-06-05",
  "indexed_at": "2026-06-05T14:30:00"
}
```

### Mapeo tipo → sector de memoria

| Tipo | Sector | Ejemplo |
|------|--------|---------|
| `decision` | reflexiva | "Decidimos usar gate HMAC-SHA256" |
| `leccion` | reflexiva | "Hooks warning-only no bloquean" |
| `convencion` | semantica | "Labels Mermaid: salto = br" |
| `riesgo` | emocional | "CRITICAL: blocking issue en build" |
| `artefacto` | procedural | spec.md, plan.md, tests/ |
| `resumen` | semantica | Resumen de sprint comprimido |
| `handoff` | episodica | Estado pendiente para siguiente sesión |

### Mapeo fase → tipo predominante

| Fase Pipeline | Tipo que produce | Sector |
|---------------|-----------------|--------|
| Briefing (F1) | artefacto | episódica |
| Spec (F2) | artefacto | semántica |
| Plan (F3) | decision | reflexiva |
| Build (F4) | artefacto | procedural |
| QA (F5) | leccion | reflexiva |
| Retro (F6) | leccion + resumen | reflexiva |

---

## 4. Knowledge Graph (LadybugDB)

### 4.1 Nodos

```
(:Proyecto {name, repo_url, fecha_inicio})
(:Sprint {number, fecha_inicio, fecha_cierre, status})
(:Artefacto {path, tipo, sha256, fecha})
(:Disciplina {name, category, fase})
(:Decision {text, fecha, agente, importance})
(:Leccion {text, categoria, causa_raiz, fix, fecha})
(:Riesgo {text, severity, status, fecha})
(:Handoff {timestamp, prose_digest, pending_count})
```

### 4.2 Relaciones

```
(:Proyecto)-[:DEFINE]->(:Disciplina)
(:Proyecto)-[:TIENE]->(:Sprint)
(:Sprint)-[:Produce]->(:Artefacto)
(:Sprint)-[:Genera]->(:Decision)
(:Sprint)-[:Genera]->(:Leccion)
(:Sprint)-[:Cierra]->(:Handoff)

(:Decision)-[:AFECTA]->(:Disciplina)
(:Decision)-[:CAUSA]->(:Problema)
(:Leccion)-[:APLICA_A]->(:Disciplina)
(:Leccion)-[:SOLUCIONA]->(:Problema)
(:Leccion)-[:PREVIENE]->(:Riesgo)
(:Riesgo)-[:BLOQUEA]->(:Artefacto)
(:Mejora)-[:HABILITA]->(:Disciplina)
```

### 4.3 Queries FlowScript (6 tipos)

```cypher
-- WHY: Por que se tomó esta decision?
MATCH (d:Decision)-[:CAUSA]->(p) WHERE d.text CONTAINS 'gate HMAC' RETURN p

-- TENSIONS: Que lecciones conflictan?
MATCH (l1:Leccion)-[:APLICA_A]->(d:Disciplina)<-[:APLICA_A]-(l2:Leccion)
WHERE l1.categoria != l2.categoria AND l1.text <> l2.text
RETURN l1, l2

-- BLOCKED: Que bloquea progreso?
MATCH (r:Riesgo)-[:BLOQUEA]->(a:Artefacto) WHERE r.status = 'activo' RETURN r, a

-- WHATIF: Que pasaria si...? (simulacion sobre subgrafo)
MATCH path = (d:Decision)-[:CAUSA*1..3]->(consequence) RETURN path

-- ALTERNATIVES: Que alternativas se consideraron?
MATCH (d:Decision)-[:DESCARTA]->(alternativa) RETURN alternativa

-- COUNTERFACTUAL: Escenarios alternativos
MATCH (d:Decision)-[:GENERA]->(scenario {type: 'counterfactual'}) RETURN scenario
```

---

## 5. Retrieval Híbrido (RRF + Composite Scoring)

### 5.1 Tres streams de búsqueda

```
Stream 1: BM25 keyword   → LadybugDB full-text search (o stdlib fallback)
Stream 2: Vector cosine  → ChromaDB query_embeddings con filtro metadata
Stream 3: Graph traversal → LadybugDB BFS sobre knowledge graph
```

### 5.2 Reciprocal Rank Fusion (k=60)

```python
def reciprocal_rank_fusion(rankings, k=60):
    """Fusiona multiples rankings con RRF. k=60 es el estandar."""
    scores = {}
    for stream_name, ranking in rankings.items():
        for rank, item_id in enumerate(ranking, 1):
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])
```

### 5.3 Composite Scoring

```python
def composite_score(item, query_time):
    """Score compuesto post-RRF: vector + recency + importance."""
    vector_score = item.get("chroma_distance", 0.5)
    recency_score = 1.0 / (1 + days_since(item["fecha"]))
    importance_score = item.get("importance", 0.5)
    
    return (
        0.5 * vector_score +
        0.3 * recency_score +
        0.2 * importance_score
    )
```

### 5.4 Decay adaptativo por tipo

| Tipo | Half-life | Razon |
|------|-----------|-------|
| `decision` | 90 dias | Decisiones persisten meses |
| `leccion` | 30 dias | Lecciones relevantes semanas |
| `artefacto` | 14 dias | Artefactos se obsoletan rapido |
| `convencion` | 180 dias | Convenciones son duraderas |
| `riesgo` | 7 dias | Riesgos se resuelven o escalan |
| `handoff` | 1 dia | Handoff expira en siguiente sesion |
| `resumen` | 60 dias | Resumenes tienen vida media |

---

## 6. Privacy Stripping (antes de indexar)

```python
def privacy_strip(text):
    """Elimina secrets y PII antes de indexar. CRITICO."""
    import re
    # API keys
    text = re.sub(r'sk-[a-zA-Z0-9]{48}', '[REDACTED_API_KEY]', text)
    text = re.sub(r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]', text)
    # Passwords
    text = re.sub(r'(?i)password["\s:=]+\S+', 'password=[REDACTED]', text)
    # Private tags
    text = re.sub(r'<private>.*?</private>', '[REDACTED_PRIVATE]', text, flags=re.DOTALL)
    # Gate keys (32+ chars)
    text = re.sub(r'[\w-]{32,}', '[REDACTED_POSSIBLE_KEY]', text)
    return text
```

---

## 7. 12 Hooks de Lifecycle

### 7.1 Hooks existentes (actuales en hooks.json)

| Hook | Evento | Fase | Modificar |
|------|--------|------|-----------|
| `session:start:context-load` | SessionStart | Fase 1 | Si — agregar wake-up EDMS |
| `pre:bash:dangerous-command` | PreToolUse | Transversal | No |
| `pre:write:doc-file-warning` | PreToolUse | Transversal | No |
| `post:bash:pr-logger` | PostToolUse | Transversal | No |
| `post:write:auto-organize` | PostToolUse | Transversal | No |
| `stop:git-check` | Stop | Fase 5 | No |
| `pre:edit:config-protection` | PreToolUse | Transversal | No |
| `pre:tool:temporal-awareness` | PreToolUse | Transversal | No |
| `stop:pattern-extraction` | Stop | Fase 6 | No |
| `pre:build:security-scan` | PreToolUse | Fase 4 | No |

### 7.2 Hooks nuevos (agregar)

| Hook | Evento | Fase | Sector | Que captura |
|------|--------|------|--------|-------------|
| `post:edit:memory-index` | PostToolUse (edit) | Fase 4 | Procedural | Cada edit en drawers/ → ChromaDB |
| `session:end:handoff` | SessionEnd | Fase 6 | Episódica | Handoff marker para siguiente sesión |
| `post:tool:failure-capture` | PostToolUse (failure) | Fase 4 | Reflexiva | Errores → lecciones candidatas |
| `pre:compact:compress` | PreCompact | Fase 4 | Semántica | Compresión de observaciones raw |

### 7.3 Mapeo hooks → pipeline

```
Fase 1 (Briefing):
  └── session:start:context-load → wake-up EDMS (~170 tokens)

Fase 2 (Spec):
  └── (sin hooks nuevos — spec se escribe manualmente)

Fase 3 (Plan):
  └── (grill-me enforced via gate HMAC)

Fase 4 (Build):
  ├── post:edit:memory-index → indexa drawers/ en ChromaDB
  ├── post:tool:failure-capture → errores como lecciones
  └── pre:compact:compress → compresión de raw observations

Fase 5 (QA):
  └── stop:git-check (existente)

Fase 6 (Retro):
  ├── stop:pattern-extraction (existente)
  └── session:end:handoff → handoff para siguiente sesión
```

---

## 8. 4-Tier Consolidation Pipeline

```
Tier 1: RAW OBSERVATIONS (Fase 4 Build)
  │  Hooks capturan cada edit, tool call, error
  │  Almacenamiento: ChromaDB (drawer raw)
  │
  ▼
Tier 2: COMPRESSED OBSERVATIONS (Fase 5 QA)
  │  PreCompact: LLM resume observations en chunks semánticos
  │  Almacenamiento: ChromaDB (drawer compressed)
  │
  ▼
Tier 3: MEMORIES (Fase 6 Retro)
  │  Consolidation: decisions, lessons, conventions extraídas
  │  Almacenamiento: ChromaDB (drawer memory) + LadybugDB (nodos)
  │
  ▼
Tier 4: CONSOLIDATED KNOWLEDGE (Post-Retro)
  │  Entity extraction + relationship mapping
  │  Almacenamiento: LadybugDB (knowledge graph)
  │  Queryable via FlowScript (why/tensions/blocked/whatIf)
```

### Políticas de consolidación

| De | A | Trigger | Metodo |
|----|---|---------|--------|
| Raw → Compressed | Fase 5 QA | PreCompact o manual | LLM summarization |
| Compressed → Memory | Fase 6 Retro | sprint-close | Entity extraction |
| Memory → Knowledge | Post-Retro | manual o auto | Relationship mapping |

---

## 9. Handoff entre Sesiones

### 9.1 Estructura del handoff

```json
{
  "timestamp": "2026-06-06T14:30:00",
  "project": "evol-dd",
  "sprint": "05",
  "pending_decisions": [
    {"text": "ChromaDB vs Qdrant", "context": "Spec fase"}
  ],
  "active_blockers": [
    {"text": "LadybugDB Python bindings inestables", "severity": "HIGH"}
  ],
  "recent_lessons": [
    {"text": "Mermaid labels requieren comillas dobles", "categoria": "HERRAMIENTAS"}
  ],
  "prose_digest": "Sprint 5 completado. Gate HMAC aprobado. Pendiente: implementar EDMS con ChromaDB+LadybugDB. Bloqueo: bindings Python de Ladybug."
}
```

### 9.2 Flujo de handoff

```
Fin de sesión:
  1. session:end:handoff hook genera handoff JSON
  2. Indexa en ChromaDB como drawer tipo "handoff" sector "episódica"
  3. Guarda marker en .evol/handoff-{fecha}.json
  4. Genera prose_digest (~170 tokens) via LLM

Inicio de sesión:
  1. session:start:context-load lee handoff anterior
  2. Inyecta prose_digest al agente
  3. Si hay pending_decisions → alerta al usuario
  4. Si hay active_blockers → sugiere resolver antes de avanzar
```

---

## 10. Team Memory (Namespaces)

### 10.1 AGENT_ID tagging

Cada drawer lleva `agente` en metadata:

```json
{"agente": "evol-architect", "scope": "shared"}
{"agente": "evol-builder", "scope": "shared"}
{"agente": "ephemeral-audit-sec-abc123", "scope": "private"}
```

### 10.2 Reglas de scope

| Scope | Quien puede leer | Quien puede escribir | Ejemplo |
|-------|-----------------|---------------------|---------|
| `shared` | Todos los agentes del proyecto | Todos los agentes | Decisiones, lecciones |
| `private` | Solo el agente que creó | Solo el agente que creó | Borradores, drafts |

### 10.3 Lifecycle de agente efímero

```
Crear → Registrar en registry.json + crear drawer private
Invoke → Buscar en shared + private del agente
Retire → Migrar private a shared → cleanup drawer private → indexar lecciones en LadybugDB
Recall → Buscar en shared + lecciones del agente en LadybugDB
```

---

## 11. Bootstrap de Historia

### 11.1 Comando

```bash
evol-memory bootstrap --project evol-dd
```

### 11.2 Flujo

```
1. Lee acuerdos/memoria/*.md (decisiones, convenciones, riesgos)
   → indexa cada sección como drawer tipo atomo
   → crea nodos :Decision/:Convencion/:Riesgo en LadybugDB

2. Lee acuerdos/lecciones/*.md
   → indexa cada lección como drawer tipo "leccion"
   → crea nodos :Leccion en LadybugDB

3. Lee memoria.md
   → indexa como drawer tipo "decision" (historico)
   → crea relaciones en LadybugDB

4. Lee lecciones.md
   → indexa cada lección como drawer tipo "leccion"
   → crea relaciones :APLICA_A con disciplinas

5. Lee .evol/drawers/**/*.md (si existe)
   → indexa como drawers tipo "artefacto"

6. Reporta: X drawers indexados, Y nodos creados, Z relaciones
```

---

## 12. Flujo de Datos Completo

### 12.1 Indexar artefacto

```
evol-memory index --file spec.md --project evol-dd --sprint 05 --phase Spec

1. Lee archivo verbatim desde .evol/drawers/sprint-05/spec.md
2. privacy_strip(texto) → elimina secrets
3. Calcula surprise_score vs memoria existente
4. ChromaDB: upsert con embedding + metadata completa
5. LadybugDB: crear nodo (:Artefacto) + relacion (:Sprint)-[:Produce]->(:Artefacto)
6. Actualiza .evol/memory/index.json (indice local del proyecto)
```

### 12.2 Buscar memoria

```
evol-memory search "gate HMAC" --project evol-dd --limit 5

1. Stream 1: BM25 keyword → LadybugDB full-text (o stdlib fallback)
2. Stream 2: ChromaDB vector query con filtro {proyecto: "evol-dd"}
3. Stream 3: LadybugDB graph traversal sobre nodos relacionados
4. RRF fusion (k=60) de los 3 rankings
5. Composite scoring: vector + recency + importance
6. Retornar top-N con citation provenance
```

### 12.3 Contexto para nueva sesión (wake-up)

```
evol-memory wake-up --project evol-dd --sprint 05

1. ChromaDB: drawers recientes (últimas 24h) del proyecto + sprint
2. LadybugDB: cargar grafo del sprint (decisiones, lecciones, disciplinas)
3. Handoff anterior (si existe)
4. Generar contexto ~170 tokens
5. Inyectar al agente via SessionStart hook
```

### 12.4 Cross-project query

```
evol-memory search "disciplinas" --all-projects --discipline ddd

1. ChromaDB: sin filtro de proyecto, con filtro {disciplinas: "ddd"}
2. LadybugDB: (:Leccion)-[:APLICA_A]->(:Disciplina {name: "DDD"})
3. Fusionar + rankear por relevancia cross-project
```

---

## 13. Archivos a Crear/Modificar

### 13.1 Archivos nuevos

| Archivo | Descripcion |
|---------|-------------|
| `scripts/evol_memory_store.py` | Capa de abstraccion ChromaDB + LadybugDB |
| `scripts/post-edit-memory-index.sh` | Hook de indexacion automatica post-edit |
| `scripts/session-end-handoff.sh` | Hook de handoff al final de sesion |
| `scripts/post-tool-failure-capture.sh` | Hook de captura de errores → lecciones |
| `~/.evol/memory/config.json` | Configuracion global de memoria |
| `~/.evol/memory/.gitignore` | Ignorar archivos de DB |
| `tests/test_memory_store.py` | Tests unitarios del store |
| `tests/test_memory_hooks.py` | Tests de hooks de memoria |

### 13.2 Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `scripts/evol-memory.py` | Agregar subcomandos: index, search, wake-up, graph, bootstrap, stats --global |
| `scripts/_evol_common.py` | Actualizar `find_memory_db()` para buscar ChromaDB + LadybugDB |
| `pyproject.toml` | Agregar `[project.optional-dependencies] memory` con chromadb + ladybugdb |
| `.agent/hooks/hooks.json` | Agregar 4 hooks nuevos |
| `.agent/hooks/scripts/session-start-context-load.sh` | Agregar wake-up EDMS con fallback |

---

## 14. Dependencias

### 14.1 pyproject.toml

```toml
[project.optional-dependencies]
memory = [
    "chromadb>=0.4.0",
    "ladybugdb>=0.1.0",
]
```

### 14.2 Instalacion

```bash
# Con memoria (requiere ChromaDB + LadybugDB)
pip install -e ".[memory]"

# Sin memoria (solo BM25 stdlib, como ahora)
pip install -e .
```

---

## 15. Tests

### 15.1 Suite de tests

```python
# tests/test_memory_store.py

def test_chromadb_index_and_search():
    """Indexa y busca en ChromaDB."""
    store = MemoryStore()
    store.index("Decidimos usar gate HMAC", {
        "proyecto": "evol-dd", "sprint": "05", "tipo": "decision"
    })
    results = store.search("gate HMAC", project="evol-dd")
    assert len(results) > 0
    assert "HMAC" in results[0]["text"]

def test_ladybugdb_graph_creation():
    """Crea nodos y relaciones en LadybugDB."""
    store = MemoryStore()
    store.graph_add_node("Proyecto", {"name": "evol-dd"})
    store.graph_add_node("Disciplina", {"name": "DDD"})
    store.graph_add_relation("evol-dd", "DEFINE", "DDD")
    result = store.graph_traverse("evol-dd")
    assert "DDD" in result

def test_wake_up_context():
    """Genera contexto para nueva sesion."""
    store = MemoryStore()
    context = store.get_context("evol-dd", sprint="05")
    assert len(context) < 200  # ~170 tokens
    assert "evol-dd" in context

def test_rrf_fusion():
    """RRF fusion de 3 rankings."""
    r1 = ["a", "b", "c"]
    r2 = ["b", "a", "d"]
    r3 = ["c", "a", "b"]
    result = reciprocal_rank_fusion({"bm25": r1, "vector": r2, "graph": r3})
    assert result[0][0] in ["a", "b"]  # Top items

def test_privacy_strip():
    """Elimina secrets antes de indexar."""
    text = "API key: sk-123456789012345678901234567890123456789012345678"
    result = privacy_strip(text)
    assert "sk-" not in result
    assert "REDACTED" in result

def test_composite_scoring():
    """Score compuesto prioriza recencia + importancia."""
    # ... test con items de diferentes fechas/importancias

def test_fallback_stdlib():
    """Fallback cuando ChromaDB/LadybugDB no estan instalados."""
    # Mock import failures
    # Verificar que BM25 keyword search funciona
    pass
```

### 15.2 Verificacion

```bash
# 1. Instalar dependencias
pip install -e ".[memory]"

# 2. Inicializar memoria
evol-memory init

# 3. Bootstrap de historia existente
evol-memory bootstrap --project evol-dd

# 4. Indexar artefacto de prueba
evol-memory index --file acuerdos/memoria/decisiones.md \
    --project evol-dd --sprint 27 --type decision

# 5. Buscar
evol-memory search "gate HMAC" --project evol-dd

# 6. Wake-up
evol-memory wake-up --project evol-dd --sprint 27

# 7. Grafo
evol-memory graph show --project evol-dd

# 8. Stats
evol-memory stats --global

# 9. Ejecutar tests
pytest tests/test_memory_store.py tests/test_memory_hooks.py -v

# 10. Shield audit
evol-shield audit --ci --no-write
```

---

## 16. Orden de Ejecucion

```
Fase 1: Infraestructura
├── 1.1 Crear evol_memory_store.py (ChromaDB + LadybugDB + fallback)
├── 1.2 Crear ~/.evol/memory/config.json
├── 1.3 Actualizar pyproject.toml (+optional deps)
├── 1.4 Actualizar _evol_common.py (find_memory_db)
└── 1.5 Privacy stripping integrado

Fase 2: CLI
├── 2.1 Extender evol-memory.py (+index, +search, +wake-up, +graph, +bootstrap)
├── 2.2 RRF fusion en search
├── 2.3 Composite scoring
└── 2.4 Discipline-aware metadata

Fase 3: Hooks
├── 3.1 Crear post-edit-memory-index.sh
├── 3.2 Crear session-end-handoff.sh
├── 3.3 Crear post-tool-failure-capture.sh
├── 3.4 Actualizar hooks.json (4 hooks nuevos)
└── 3.5 Actualizar session-start-context-load.sh (wake-up EDMS)

Fase 4: Consolidation
├── 4.1 4-tier pipeline (raw → compressed → memory → knowledge)
├── 4.2 PreCompact compression
└── 4.3 Decay adaptativo por tipo

Fase 5: Knowledge Graph
├── 5.1 Causal chains en LadybugDB
├── 5.2 FlowScript queries (why/tensions/blocked/whatIf)
├── 5.3 Entity extraction
└── 5.4 Team memory namespaces

Fase 6: Observabilidad
├── 6.1 Stats globales
├── 6.2 Memory health dashboard
└── 6.3 Session replay (futuro)
```

---

## 17. Invariantes

- **Local-first, zero cloud, zero subscriptions** — ChromaDB + LadybugDB embebidas
- **Fallback stdlib** — Sin ChromaDB/LadybugDB, BM25 sigue funcionando
- **Privacy first** — Secrets se eliminan ANTES de indexar
- **Verbatim storage** — Nunca resumir originales; summaries en tier separado
- **Metadata filtering** — Separación por proyecto via metadata, no DB separada
- **Discipline-aware** — 31 disciplinas como filtro de metadata
- **Gate HMAC** — Cada aprobación firmada criptográficamente
- **Constitution prevalece** — En conflicto, constitución Art. 1-9 manda

---

## 18. Fuentes

| # | Repositorio | URL | Mejora referenciada |
|---|-------------|-----|---------------------|
| 1 | agentmemory | https://github.com/rohitg00/agentmemory | #1, #7, #8, #11, #13 |
| 2 | OpenMemory | https://github.com/openmemoryteam/openmemory | #3, #4 |
| 3 | Letta/MemGPT | https://github.com/letta-ai/letta | #2, #12 |
| 4 | EM-LLM | https://github.com/em-llm/em-llm | #9 |
| 5 | FlowScript | https://github.com/flowscript/flowscript | #5 |
| 6 | cognee | https://github.com/topoteretes/cognee | #3, #8 |
| 7 | mem0 | https://github.com/mem0ai/mem0 | #4 |
| 8 | ai-memory | https://github.com/akitaonrails/ai-memory | #6, #10, #14 |
| 9 | Deja | https://github.com/deja-ai/deja | #6, #12 |
| 10 | Cortex | https://github.com/cortex-system/cortex | #6 |
| 11 | context-llemur | https://github.com/context-llemur/context-llemur | #12 |
| 12 | Secure Memory MCP | https://github.com/secure-memory-mcp/secure-memory-mcp | #7 |
| 13 | Obsidian MCP | https://github.com/obsidian-mcp/obsidian-mcp | #1 |
| 14 | MemPalace | https://github.com/memory-palace/mcp-memory-palace | Arquitectura base |
| 15 | ChromaDB | https://github.com/chroma-core/chroma | Stack base |
| 16 | LadybugDB | https://github.com/LadybugDB/ladybug | Stack base |
