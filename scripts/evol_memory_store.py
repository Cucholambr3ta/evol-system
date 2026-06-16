#!/usr/bin/env python3
"""evol_memory_store.py — ChromaDB + LadybugDB abstraction layer for Evol-DD.

Provides MemoryStore class that wraps ChromaDB (vector) and LadybugDB (graph)
with automatic fallback to stdlib BM25 when dependencies are not installed.

Usage:
    from evol_memory_store import MemoryStore
    store = MemoryStore()
    store.index("Decidimos usar gate HMAC", {"tipo": "decision", ...})
    results = store.search("gate HMAC", project="evol-dd")
"""

import base64
import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# ── Trace emitter (optional, fails silently) ─────────────────────────────
try:
    from evol_traces import (
        emit_edms_index, emit_edms_search,
        emit_graph_node, emit_graph_relation,
    )
    _TRACES_AVAILABLE = True
except ImportError:
    _TRACES_AVAILABLE = False

    def emit_edms_index(*a, **kw): pass
    def emit_edms_search(*a, **kw): pass
    def emit_graph_node(*a, **kw): pass
    def emit_graph_relation(*a, **kw): pass

# ── Auto-detect project venv ───────────────────────────────────────────────────
_VENV_PYTHON = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python3"
if _VENV_PYTHON.exists() and sys.executable != str(_VENV_PYTHON):
    try:
        import chromadb  # noqa: F401
    except ImportError:
        os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON)] + sys.argv)

# ── Optional imports with fallback ─────────────────────────────────────────────

logger = logging.getLogger("evol.memory.store")

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import ladybug as lb
    LADYBUG_AVAILABLE = True
except ImportError:
    LADYBUG_AVAILABLE = False


# ── Privacy stripping ─────────────────────────────────────────────────────────

_PRIVACY_PATTERNS = [
    (re.compile(r'sk-[a-zA-Z0-9]{48}'), '[REDACTED_API_KEY]'),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), '[REDACTED_GITHUB_TOKEN]'),
    (re.compile(r'(?i)password["\s:=]+\S+'), 'password=[REDACTED]'),
    (re.compile(r'<private>.*?</private>', re.DOTALL), '[REDACTED_PRIVATE]'),
    (re.compile(r'[\w-]{32,}'), '[REDACTED_POSSIBLE_KEY]'),
]


def privacy_strip(text: str) -> str:
    """Elimina secrets y PII antes de indexar. CRITICO."""
    for pattern, replacement in _PRIVACY_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _parse_ladybug_metadata(s: str) -> dict:
    """Parse LadybugDB's non-JSON metadata format: {key: value, key2: value2}"""
    if not s or s.strip() == '':
        return {}
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
    result = {}
    for match in re.finditer(r'(\w+)\s*:\s*([^,}]+)', s):
        key = match.group(1).strip()
        val = match.group(2).strip()
        if val == 'null' or val == 'None':
            result[key] = None
        elif val.startswith('"') and val.endswith('"'):
            result[key] = val[1:-1]
        elif val.replace('.', '', 1).replace('-', '', 1).isdigit():
            result[key] = float(val) if '.' in val else int(val)
        else:
            result[key] = val
    return result


# ── Frontmatter / Section helpers ──────────────────────────────────────────────


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content.

    Returns dict with frontmatter fields, or empty dict if none found.
    """
    if not content.startswith('---'):
        return {}
    end = content.find('---', 3)
    if end == -1:
        return {}
    yaml_text = content[3:end].strip()
    result = {}
    for line in yaml_text.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if value.startswith('[') and value.endswith(']'):
                # Parse simple YAML list
                items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',') if v.strip()]
                result[key] = items
            else:
                result[key] = value.strip('"').strip("'")
    return result


def extract_section(content: str, header: str) -> str:
    """Extract a section from markdown by heading text.

    Returns the section content (without the heading), or empty string.
    """
    lines = content.split('\n')
    in_section = False
    section_lines = []
    header_level = 0
    for line in lines:
        if line.strip().startswith('#') and header.lower() in line.lower():
            in_section = True
            header_level = len(line) - len(line.lstrip('#'))
            continue
        if in_section:
            if line.strip().startswith('#') and (len(line) - len(line.lstrip('#'))) <= header_level:
                break
            section_lines.append(line)
    return '\n'.join(section_lines).strip()


# ── RRF Fusion ────────────────────────────────────────────────────────────────


def reciprocal_rank_fusion(rankings: dict[str, list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Fusiona multiples rankings con Reciprocal Rank Fusion.

    Args:
        rankings: dict mapping stream_name -> list of item IDs (ordered by rank)
        k: parameter (default 60, standard)

    Returns:
        List of (item_id, score) sorted by score descending
    """
    scores: dict[str, float] = {}
    for stream_name, ranking in rankings.items():
        for rank, item_id in enumerate(ranking, 1):
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# ── Composite scoring ─────────────────────────────────────────────────────────

_HALF_LIFE_DAYS = {
    'decision': 90,
    'leccion': 30,
    'artefacto': 14,
    'convencion': 180,
    'riesgo': 7,
    'handoff': 1,
    'resumen': 60,
}


def composite_score(item: dict, query_time: datetime | None = None) -> float:
    """Score compuesto post-RRF: 50% vector + 30% recency + 20% importance.

    Args:
        item: dict with chroma_distance, fecha, importance, tipo
        query_time: datetime for recency calculation (default: now)

    Returns:
        Float score between 0 and 1
    """
    if query_time is None:
        query_time = datetime.now()

    vector_score = item.get('chroma_distance', 0.5)
    importance_score = item.get('importance', 0.5)

    fecha_str = item.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.fromisoformat(fecha_str)
            days = (query_time - fecha).total_seconds() / 86400
        except (ValueError, TypeError):
            days = 30
    else:
        days = 30

    tipo = item.get('tipo', 'artefacto')
    half_life = _HALF_LIFE_DAYS.get(tipo, 30)
    recency_score = max(0, 1.0 / (1 + days / half_life))

    return 0.5 * vector_score + 0.3 * recency_score + 0.2 * importance_score


# ── MemoryStore ───────────────────────────────────────────────────────────────


class MemoryStore:
    """Abstraction layer for ChromaDB + LadybugDB with stdlib fallback."""

    def __init__(self, memory_dir: str | None = None):
        if memory_dir is None:
            memory_dir = os.environ.get('EVOL_MEMORY_DIR', os.path.expanduser('~/.evol/memory'))
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self._chroma_client = None
        self._chroma_collection = None
        self._graph: dict[str, dict] = {}  # fallback graph (nodes + relations)

        if CHROMA_AVAILABLE:
            self._init_chroma()
        if LADYBUG_AVAILABLE:
            self._init_ladybug()
        else:
            self._load_graph()

    def _init_chroma(self):
        chroma_path = str(self.memory_dir / 'chromadb')
        self._chroma_client = chromadb.PersistentClient(path=chroma_path)
        self._chroma_collection = self._chroma_client.get_or_create_collection(
            name='evol_memory',
            metadata={"hnsw:space": "cosine"}
        )

    def _init_ladybug(self):
        ladybug_path = str(self.memory_dir / 'ladybug.lbug')
        self._lbug_db = lb.Database(ladybug_path)
        self._lbug_conn = lb.Connection(self._lbug_db)
        # Create schema if not exists
        self._lbug_conn.execute(
            "CREATE NODE TABLE IF NOT EXISTS MemoryNode("
            "name STRING PRIMARY KEY, type STRING, properties STRING)"
        )
        self._lbug_conn.execute(
            "CREATE REL TABLE IF NOT EXISTS MemoryRel("
            "FROM MemoryNode TO MemoryNode, relation STRING, "
            "metadata STRING)"
        )
        # Migrate older DBs whose MemoryRel predates the metadata column.
        self._rel_has_metadata = self._ensure_rel_metadata_column()

    def _rel_columns(self) -> list[str]:
        """Return MemoryRel column names via schema introspection.

        Uses LadybugDB's table_info() call. Returns [] if it cannot be read.
        """
        try:
            res = self._lbug_conn.execute(
                "CALL table_info('MemoryRel') RETURN *"
            )
            cols: list[str] = []
            while res.has_next():
                row = res.get_next()
                # row layout: [property_id, name, type, default, ...]
                if len(row) > 1:
                    cols.append(row[1])
            return cols
        except Exception as exc:
            logger.warning("Could not introspect MemoryRel schema: %s", exc)
            return []

    def _ensure_rel_metadata_column(self) -> bool:
        """Ensure MemoryRel has a `metadata` column. Returns True if present.

        For freshly created tables the column already exists. For older DBs it
        is added via ALTER TABLE (LadybugDB syntax: ``ADD <name> <type>``, no
        COLUMN keyword). If introspection cannot confirm/repair the schema we
        log a warning and report False so callers degrade gracefully instead
        of crashing on a missing property.
        """
        cols = self._rel_columns()
        if not cols:
            # Introspection failed: assume the CREATE ... metadata STRING above
            # took effect, but warn so a real schema problem is visible.
            logger.warning(
                "MemoryRel schema unreadable; assuming metadata column present"
            )
            return True
        if "metadata" in cols:
            return True
        try:
            self._lbug_conn.execute(
                "ALTER TABLE MemoryRel ADD metadata STRING"
            )
            logger.info("Migrated MemoryRel: added missing 'metadata' column")
            return "metadata" in self._rel_columns()
        except Exception as exc:
            logger.warning(
                "Could not add 'metadata' column to MemoryRel (%s); "
                "relations will be stored without metadata", exc
            )
            return False

    def _load_graph(self):
        """Load graph from disk (fallback when LadybugDB not available)."""
        graph_file = self.memory_dir / 'graph.json'
        if graph_file.exists():
            with open(graph_file) as f:
                self._graph = json.load(f)

    def _save_graph(self):
        """Save graph to disk (fallback when LadybugDB not available)."""
        graph_file = self.memory_dir / 'graph.json'
        with open(graph_file, 'w') as f:
            json.dump(self._graph, f, indent=2, ensure_ascii=False)

    # ── Index ─────────────────────────────────────────────────────────────

    def index(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """Index text with metadata into ChromaDB (after privacy strip).

        Returns:
            ID of inserted drawer
        """
        clean_text = privacy_strip(text)
        meta = metadata or {}

        if 'fecha' not in meta:
            meta['fecha'] = datetime.now().strftime('%Y-%m-%d')
        meta['indexed_at'] = datetime.now().isoformat()

        # Ensure tier field exists
        if 'tier' not in meta:
            meta['tier'] = 'raw'

        # Ensure importance field exists
        if 'importance' not in meta:
            meta['importance'] = 0.5

        # Content hash for change detection
        meta['content_hash'] = hashlib.sha256(clean_text.encode()).hexdigest()[:16]

        # Auto-update graph based on metadata
        self._auto_update_graph(clean_text, meta)

        if CHROMA_AVAILABLE and self._chroma_collection:
            doc_id = hashlib.sha256(clean_text.encode()).hexdigest()[:16]
            self._chroma_collection.upsert(
                ids=[doc_id],
                documents=[clean_text],
                metadatas=[meta]
            )
            emit_edms_index(
                project=meta.get('proyecto', ''),
                tipo=meta.get('tipo', 'unknown'),
                doc_id=doc_id,
                agent=meta.get('agente', ''),
            )
            return doc_id

        # Fallback: write to local JSON index
        doc_id = self._index_local(clean_text, meta)
        emit_edms_index(
            project=meta.get('proyecto', ''),
            tipo=meta.get('tipo', 'unknown'),
            doc_id=doc_id,
            agent=meta.get('agente', ''),
        )
        return doc_id

    def _auto_update_graph(self, text: str, meta: dict):
        """Auto-update knowledge graph based on indexed content metadata."""
        proyecto = meta.get('proyecto', 'unknown')
        tipo = meta.get('tipo', 'artefacto')
        fase = meta.get('fase', '')
        sprint = meta.get('sprint')
        disciplinas = meta.get('disciplinas', [])
        agente = meta.get('agente')

        # Ensure project node exists
        self.graph_add_node("Proyecto", {"name": proyecto})

        # Add discipline nodes and relations
        if isinstance(disciplinas, str):
            disciplinas = [d.strip() for d in disciplinas.split(',')]
        for disc in disciplinas:
            if disc:
                self.graph_add_node("Disciplina", {"name": disc})
                self.graph_add_relation(proyecto, "DEFINE", disc)

        # Add sprint node and relation
        if sprint:
            sprint_id = f"sprint-{sprint}"
            self.graph_add_node("Sprint", {"number": sprint, "status": "active"})
            self.graph_add_relation(proyecto, "TIENE", sprint_id)

        # Add entity based on tipo
        entity_id = hashlib.sha256(text.encode()).hexdigest()[:12]

        if tipo == 'decision':
            self.graph_add_node("Decision", {
                "text": text[:200],
                "fecha": meta.get('fecha', ''),
                "agente": agente or 'unknown',
            })
            self.graph_add_relation(proyecto, "Genera", entity_id)
            if sprint:
                self.graph_add_relation(f"sprint-{sprint}", "Genera", entity_id)
            for disc in disciplinas:
                if disc:
                    self.graph_add_relation(entity_id, "AFECTA", disc)

        elif tipo == 'leccion':
            self.graph_add_node("Leccion", {
                "text": text[:200],
                "categoria": fase,
                "agente": agente or 'unknown',
            })
            self.graph_add_relation(proyecto, "Genera", entity_id)
            if sprint:
                self.graph_add_relation(f"sprint-{sprint}", "Genera", entity_id)
            for disc in disciplinas:
                if disc:
                    self.graph_add_relation(entity_id, "APLICA_A", disc)

        elif tipo == 'riesgo':
            self.graph_add_node("Riesgo", {
                "text": text[:200],
                "status": meta.get('status', 'activo'),
            })
            self.graph_add_relation(proyecto, "Genera", entity_id)

        elif tipo == 'handoff':
            self.graph_add_node("Handoff", {
                "timestamp": datetime.now().isoformat(),
                "prose_digest": text[:200],
            })
            if sprint:
                self.graph_add_relation(f"sprint-{sprint}", "Cierra", entity_id)

        elif tipo == 'artefacto':
            source_file = meta.get('source_file', '')
            self.graph_add_node("Artefacto", {
                "name": text[:80],
                "text": text[:200],
                "source_file": source_file,
                "fase": fase,
                "importance": meta.get('importance', 0.5),
            })
            self.graph_add_relation(proyecto, "GENERADO_POR", entity_id)
            if sprint:
                self.graph_add_relation(f"sprint-{sprint}", "GENERADO_POR", entity_id)
            if source_file:
                self.graph_add_node("File", {"name": source_file})
                self.graph_add_relation(entity_id, "REFERENCIA", source_file)
            for disc in disciplinas:
                if disc:
                    self.graph_add_relation(entity_id, "DEFINE", disc)

        elif tipo == 'agente_def':
            agent_name = meta.get('agent_name', text[:80])
            self.graph_add_node("AgenteDef", {
                "name": agent_name,
                "capabilities": meta.get('agent_capabilities', ''),
            })
            self.graph_add_relation(proyecto, "TIENE_AGENTE", agent_name)

        elif tipo == 'skill_def':
            skill_name = meta.get('skill_name', text[:80])
            self.graph_add_node("SkillDef", {
                "name": skill_name,
                "trigger": meta.get('skill_trigger', ''),
            })
            self.graph_add_relation(proyecto, "TIENE_SKILL", skill_name)

    def _index_local(self, text: str, meta: dict) -> str:
        idx_file = self.memory_dir / 'local_index.json'
        idx = []
        if idx_file.exists():
            with open(idx_file) as f:
                idx = json.load(f)

        doc_id = hashlib.sha256(text.encode()).hexdigest()[:16]
        idx.append({'id': doc_id, 'text': text, 'metadata': meta})

        with open(idx_file, 'w') as f:
            json.dump(idx, f, indent=2, ensure_ascii=False)
        return doc_id

    # ── Search ────────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        project: str | None = None,
        phase: str | None = None,
        tipo: str | None = None,
        disciplinas: str | None = None,
        sprint: str | None = None,
        n_results: int = 10,
    ) -> list[dict]:
        """Search drawers by query with optional metadata filters.

        Returns:
            List of dicts with keys: id, text, metadata, distance
        """
        clean_query = privacy_strip(query)
        filters = {}
        if project:
            filters['proyecto'] = project
        if phase:
            filters['fase'] = phase
        if tipo:
            filters['tipo'] = tipo
        if disciplinas:
            filters['disciplinas'] = disciplinas
        if sprint:
            filters['sprint'] = sprint

        if CHROMA_AVAILABLE and self._chroma_collection:
            if len(filters) == 1:
                where = filters
            elif len(filters) > 1:
                where = {"$and": [{k: v} for k, v in filters.items()]}
            else:
                where = None
            results = self._chroma_collection.query(
                query_texts=[clean_query],
                n_results=n_results,
                where=where
            )
            out = []
            if results and results['ids']:
                for i, doc_id in enumerate(results['ids'][0]):
                    out.append({
                        'id': doc_id,
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                    })
            emit_edms_search(project=project or '', query=query, result_count=len(out))
            return out

        # Fallback: local JSON search (BM25-like keyword match)
        out = self._search_local(clean_query, filters, n_results)
        emit_edms_search(project=project or '', query=query, result_count=len(out))
        return out

    def _search_local(self, query: str, filters: dict, n_results: int) -> list[dict]:
        idx_file = self.memory_dir / 'local_index.json'
        if not idx_file.exists():
            return []

        with open(idx_file) as f:
            idx = json.load(f)

        query_words = set(query.lower().split())
        scored = []
        for item in idx:
            meta = item.get('metadata', {})
            if filters:
                skip = False
                for k, v in filters.items():
                    item_val = meta.get(k)
                    if isinstance(item_val, list):
                        if v not in item_val:
                            skip = True
                            break
                    elif item_val != v:
                        skip = True
                        break
                if skip:
                    continue

            text_lower = item['text'].lower()
            hits = sum(1 for w in query_words if w in text_lower)
            if hits > 0:
                scored.append({
                    'id': item['id'],
                    'text': item['text'],
                    'metadata': meta,
                    'distance': 1.0 - (hits / len(query_words)) if query_words else 1.0,
                })

        scored.sort(key=lambda x: x['distance'])
        return scored[:n_results]

    # ── Graph ─────────────────────────────────────────────────────────────

    def graph_add_node(self, node_type: str, properties: dict) -> str:
        """Add a node to the knowledge graph.

        Returns:
            Node ID
        """
        node_id = properties.get('name', hashlib.sha256(json.dumps(properties).encode()).hexdigest()[:12])

        if LADYBUG_AVAILABLE:
            props_json = json.dumps(properties, ensure_ascii=False)
            props_b64 = base64.b64encode(props_json.encode()).decode()
            self._lbug_conn.execute(
                "MERGE (n:MemoryNode {name: $name}) "
                "SET n.type = $type, n.properties = $props",
                parameters={"name": node_id, "type": node_type, "props": props_b64}
            )
            emit_graph_node(
                project=properties.get('name', ''),
                node_type=node_type,
                node_name=node_id,
                action="created",
            )
            return node_id

        # Fallback: in-memory dict
        key = f"{node_type}:{node_id}"
        self._graph[key] = {'type': node_type, 'properties': properties}
        self._save_graph()
        emit_graph_node(
            project=properties.get('name', ''),
            node_type=node_type,
            node_name=node_id,
            action="created",
        )
        return node_id

    def graph_add_relation(self, source_id: str, relation_type: str, target_id: str,
                           valid_from: str = None, valid_to: str = None,
                           confidence: float = 1.0) -> bool:
        """Add a relation between two nodes with optional temporal validity.

        Args:
            source_id: Source node name
            relation_type: Relation type (e.g. 'DEFINE', 'REFERENCIA')
            target_id: Target node name
            valid_from: ISO date when this relation became valid (default: now)
            valid_to: ISO date when this relation stopped being valid (None = still active)
            confidence: Confidence score 0.0-1.0 (default: 1.0)

        Returns:
            True if successful
        """
        if not valid_from:
            valid_from = datetime.now().isoformat()

        # Build metadata JSON
        metadata = json.dumps({
            "valid_from": valid_from,
            "valid_to": valid_to,
            "confidence": confidence
        }, ensure_ascii=False)

        if LADYBUG_AVAILABLE:
            # Degrade gracefully when the active schema lacks the metadata
            # column (older DB that could not be migrated): create the relation
            # without metadata rather than crashing with "Cannot find property
            # metadata". getattr guard covers stores created before migration.
            if getattr(self, "_rel_has_metadata", True):
                self._lbug_conn.execute(
                    "MATCH (a:MemoryNode), (b:MemoryNode) "
                    "WHERE a.name = $src AND b.name = $tgt "
                    "CREATE (a)-[:MemoryRel {relation: $rel, metadata: $meta}]->(b)",
                    parameters={
                        "src": source_id, "tgt": target_id, "rel": relation_type,
                        "meta": metadata
                    }
                )
            else:
                logger.warning(
                    "MemoryRel has no metadata column; storing relation "
                    "%s -[%s]-> %s without metadata", source_id, relation_type,
                    target_id
                )
                self._lbug_conn.execute(
                    "MATCH (a:MemoryNode), (b:MemoryNode) "
                    "WHERE a.name = $src AND b.name = $tgt "
                    "CREATE (a)-[:MemoryRel {relation: $rel}]->(b)",
                    parameters={
                        "src": source_id, "tgt": target_id, "rel": relation_type
                    }
                )
            emit_graph_relation(
                project='',
                source=source_id,
                relation=relation_type,
                target=target_id,
            )
            return True

        # Fallback: in-memory dict
        rel_key = f"{source_id}->{target_id}"
        if rel_key not in self._graph:
            self._graph[rel_key] = {
                'type': relation_type,
                'valid_from': valid_from,
                'valid_to': valid_to,
                'confidence': confidence,
            }
            self._save_graph()
            emit_graph_relation(
                project='',
                source=source_id,
                relation=relation_type,
                target=target_id,
            )
        return True

    def graph_query_temporal(self, node_name: str = None, as_of: str = None) -> list:
        """Query relations with temporal filtering.

        Args:
            node_name: Filter by node name (optional, None = all)
            as_of: ISO date to query "what was valid at this time?" (None = current)

        Returns:
            List of dicts with source, relation, target, valid_from, valid_to, confidence
        """
        if LADYBUG_AVAILABLE:
            # Load invalidations if they exist
            invalidations = {}
            invalidations_file = self.memory_dir / 'invalidations.json'
            if invalidations_file.exists():
                with open(invalidations_file) as f:
                    invalidations = json.load(f)

            if node_name:
                result = self._lbug_conn.execute(
                    "MATCH (a:MemoryNode)-[r:MemoryRel]->(b:MemoryNode) "
                    "WHERE a.name = $name "
                    "RETURN a.name, r.relation, b.name, r.metadata",
                    parameters={"name": node_name}
                )
            else:
                result = self._lbug_conn.execute(
                    "MATCH (a:MemoryNode)-[r:MemoryRel]->(b:MemoryNode) "
                    "RETURN a.name, r.relation, b.name, r.metadata"
                )
            relations = []
            for row in result:
                meta = {}
                if row[3]:
                    try:
                        meta = json.loads(row[3])
                    except Exception:
                        meta = _parse_ladybug_metadata(row[3])
                vf = meta.get('valid_from')
                vt = meta.get('valid_to')
                cf = meta.get('confidence', 1.0)
                
                # Check if relation was invalidated
                rel_key = f"{row[0]}->{row[1]}->{row[2]}"
                if rel_key in invalidations:
                    vt = invalidations[rel_key]
                
                # Filter by time
                if as_of:
                    if vf and vf > as_of:
                        continue
                    if vt and vt <= as_of:
                        continue
                else:
                    # For current queries, skip relations that ended in the past
                    if vt and vt < datetime.now().isoformat():
                        continue
                relations.append({
                    "source": row[0], "relation": row[1], "target": row[2],
                    "valid_from": vf, "valid_to": vt, "confidence": cf
                })
            return relations

        # Fallback: in-memory dict
        relations = []
        for key, val in self._graph.items():
            src, tgt = key.split("->", 1)
            vf = val.get('valid_from')
            vt = val.get('valid_to')
            # Filter by node
            if node_name and src != node_name and tgt != node_name:
                continue
            # Filter by time
            if as_of:
                if vf and vf > as_of:
                    continue
                if vt and vt <= as_of:
                    continue
            else:
                if vt:  # Skip invalidated relations
                    continue
            relations.append({
                "source": src, "relation": val.get('type'), "target": tgt,
                "valid_from": vf, "valid_to": vt,
                "confidence": val.get('confidence', 1.0)
            })
        return relations

    def graph_invalidate(self, source_id: str, relation_type: str, target_id: str,
                         ended: str = None) -> bool:
        """Invalidate a relation (mark as ended).

        Args:
            source_id: Source node name
            relation_type: Relation type to invalidate
            target_id: Target node name
            ended: ISO date when it ended (default: now)

        Returns:
            True if the relation was found and invalidated
        """
        if not ended:
            ended = datetime.now().isoformat()

        if LADYBUG_AVAILABLE:
            # First, get the current metadata
            result = self._lbug_conn.execute(
                "MATCH (a:MemoryNode)-[r:MemoryRel]->(b:MemoryNode) "
                "WHERE a.name = $src AND r.relation = $rel AND b.name = $tgt "
                "RETURN r.metadata",
                parameters={"src": source_id, "rel": relation_type, "tgt": target_id}
            )
            rows = list(result)
            if not rows:
                return False
            
            # Update metadata with valid_to
            meta_str = rows[0][0] if rows[0][0] else "{}"
            try:
                meta = json.loads(meta_str)
            except Exception:
                meta = _parse_ladybug_metadata(meta_str)
            meta['valid_to'] = ended
            
            # Store invalidation in a separate JSON file (LadybugDB doesn't support UPDATE on relations)
            invalidations_file = self.memory_dir / 'invalidations.json'
            invalidations = {}
            if invalidations_file.exists():
                with open(invalidations_file) as f:
                    invalidations = json.load(f)
            rel_key = f"{source_id}->{relation_type}->{target_id}"
            invalidations[rel_key] = ended
            with open(invalidations_file, 'w') as f:
                json.dump(invalidations, f, indent=2)
            
            return True

        # Fallback: in-memory dict
        rel_key = f"{source_id}->{target_id}"
        if rel_key in self._graph and self._graph[rel_key].get('type') == relation_type:
            self._graph[rel_key]['valid_to'] = ended
            self._save_graph()
            return True
        return False

    def graph_timeline(self, node_name: str) -> list:
        """Get chronological timeline of all relations for a node.

        Args:
            node_name: Node to get timeline for

        Returns:
            List of dicts sorted by valid_from, with status (active/ended)
        """
        if LADYBUG_AVAILABLE:
            result = self._lbug_conn.execute(
                "MATCH (a:MemoryNode)-[r:MemoryRel]->(b:MemoryNode) "
                "WHERE a.name = $name OR b.name = $name "
                "RETURN a.name, r.relation, b.name, r.metadata "
                "ORDER BY r.metadata",
                parameters={"name": node_name}
            )
            timeline = []
            for row in result:
                meta = {}
                if row[3]:
                    try:
                        meta = json.loads(row[3])
                    except Exception:
                        meta = _parse_ladybug_metadata(row[3])
                vf = meta.get('valid_from')
                vt = meta.get('valid_to')
                cf = meta.get('confidence', 1.0)
                status = "active" if not vt else "ended"
                timeline.append({
                    "source": row[0], "relation": row[1], "target": row[2],
                    "valid_from": vf, "valid_to": vt,
                    "confidence": cf, "status": status
                })
            return timeline

        # Fallback: in-memory dict
        events = []
        for key, val in self._graph.items():
            src, tgt = key.split("->", 1)
            if src == node_name or tgt == node_name:
                status = "active" if not val.get('valid_to') else "ended"
                events.append({
                    "source": src, "relation": val.get('type'), "target": tgt,
                    "valid_from": val.get('valid_from'), "valid_to": val.get('valid_to'),
                    "confidence": val.get('confidence', 1.0), "status": status
                })
        events.sort(key=lambda x: x.get('valid_from') or '')
        return events

    def graph_traverse(self, node_id: str, depth: int = 2) -> dict:
        """Traverse graph from a node.

        Returns:
            Subgraph as dict with nodes and relations
        """
        if LADYBUG_AVAILABLE:
            result = self._lbug_conn.execute(
                "MATCH (n:MemoryNode)-[r:MemoryRel*1.." + str(depth) + "]-(m:MemoryNode) "
                "WHERE n.name = $start "
                "RETURN DISTINCT m.name, m.type, m.properties",
                parameters={"start": node_id}
            )
            nodes = []
            for row in result:
                props = {}
                if row[2]:
                    try:
                        props = json.loads(base64.b64decode(row[2]).decode())
                    except Exception:
                        props = {}
                nodes.append({
                    'name': row[0],
                    'type': row[1],
                    'properties': props
                })
            # Also get direct relations
            rel_result = self._lbug_conn.execute(
                "MATCH (a:MemoryNode)-[r:MemoryRel]->(b:MemoryNode) "
                "WHERE a.name = $start "
                "RETURN a.name, r.relation, b.name",
                parameters={"start": node_id}
            )
            relations = []
            for row in rel_result:
                relations.append({
                    'source': row[0],
                    'type': row[1],
                    'target': row[2]
                })
            return {'nodes': nodes, 'relations': relations}

        # Fallback: in-memory traversal
        visited = set()
        nodes = []
        relations = []

        def _traverse(nid: str, d: int):
            if d <= 0 or nid in visited:
                return
            visited.add(nid)
            for key, val in self._graph.items():
                if key.startswith(f"{nid}->"):
                    target = key.split('->')[1]
                    relations.append({'source': nid, 'type': val['type'], 'target': target})
                    _traverse(target, d - 1)

        _traverse(node_id, depth)
        for n in nodes:
            pass  # collect node details
        return {'nodes': nodes, 'relations': relations}

    def _backfill_graph(self):
        """One-time: create graph nodes for existing artefacto records that lack them."""
        if not (CHROMA_AVAILABLE and self._chroma_collection):
            return
        results = self._chroma_collection.get(
            where={"tipo": "artefacto"},
            include=["metadatas", "documents"]
        )
        if not results or not results['ids']:
            return
        count = 0
        for doc_id, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            if doc and meta:
                self._auto_update_graph(doc, meta)
                count += 1
        return count

    # ── Wake-up context ───────────────────────────────────────────────────

    def get_context(self, project: str, sprint: str | None = None) -> str:
        """Generate compact context (~170 tokens) for new session.

        Returns:
            String with relevant memory summary
        """
        parts = []
        parts.append(f"Proyecto: {project}")

        # Recent decisions
        decisions = self.search("", project=project, tipo='decision', n_results=3)
        if decisions:
            parts.append("Decisiones recientes:")
            for d in decisions:
                parts.append(f"  - {d['text'][:80]}")

        # Active risks
        risks = self.search("", project=project, tipo='riesgo', n_results=2)
        if risks:
            parts.append("Riesgos activos:")
            for r in risks:
                parts.append(f"  - {r['text'][:80]}")

        # Recent lessons
        lessons = self.search("", project=project, tipo='leccion', n_results=2)
        if lessons:
            parts.append("Lecciones:")
            for l in lessons:
                parts.append(f"  - {l['text'][:80]}")

        # Code graph stats (~50 tokens)
        try:
            from evol_code_indexer import CodeGraph
            code_graph = CodeGraph(self.memory_dir)
            code_stats = code_graph.stats()
            if code_stats.get('total_nodes', 0) > 0:
                parts.append(f"Code Graph: {code_stats['total_nodes']} nodes, "
                           f"{code_stats['total_relations']} relations")
        except Exception:
            pass  # Code graph not available

        context = '\n'.join(parts)
        # Truncate to ~170 tokens (~800 chars)
        if len(context) > 800:
            context = context[:797] + '...'
        return context

    # ── 4-Tier Consolidation ──────────────────────────────────────────────

    def consolidate_tier(self, from_tier: str, to_tier: str, project: str,
                         max_items: int = 50) -> int:
        """Consolidate drawers from one tier to the next.

        Tiers: raw -> compressed -> memory -> knowledge

        Returns:
            Number of items consolidated
        """
        if CHROMA_AVAILABLE and self._chroma_collection:
            where_filter = {"$and": [
                {"tier": from_tier},
                {"proyecto": project}
            ]}
            results = self._chroma_collection.get(
                where=where_filter,
                limit=max_items
            )
            source_items = []
            if results and results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    source_items.append({
                        'id': doc_id,
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {},
                    })
        else:
            results = self.search("", project=project, n_results=max_items)
            source_items = [r for r in results if r['metadata'].get('tier') == from_tier]

        if not source_items:
            return 0

        consolidated = 0
        for item in source_items:
            meta = item['metadata'].copy()
            meta['tier'] = to_tier
            meta['consolidated_from'] = from_tier
            meta['consolidated_at'] = datetime.now().isoformat()

            # For knowledge tier, add to graph
            if to_tier == 'knowledge':
                self._add_to_knowledge_graph(item['text'], meta)

            self.index(item['text'], meta)
            consolidated += 1

        return consolidated

    def _add_to_knowledge_graph(self, text: str, meta: dict):
        """Extract entities and add to knowledge graph."""
        # Simple entity extraction (can be enhanced with LLM)
        proyecto = meta.get('proyecto', 'unknown')
        tipo = meta.get('tipo', 'artefacto')

        # Add project node if not exists
        self.graph_add_node("Proyecto", {"name": proyecto})

        # Add entity based on tipo
        if tipo == 'decision':
            entity_id = hashlib.sha256(text.encode()).hexdigest()[:12]
            self.graph_add_node("Decision", {"text": text[:200], "fecha": meta.get('fecha', '')})
            self.graph_add_relation(proyecto, "Genera", entity_id)
        elif tipo == 'leccion':
            entity_id = hashlib.sha256(text.encode()).hexdigest()[:12]
            self.graph_add_node("Leccion", {"text": text[:200], "categoria": meta.get('fase', '')})
            self.graph_add_relation(proyecto, "Genera", entity_id)

    def decay_old_items(self, days_threshold: int = 30) -> int:
        """Mark old items as decayed based on half-life per type.

        Returns:
            Number of items decayed
        """
        if CHROMA_AVAILABLE and self._chroma_collection:
            results = self._chroma_collection.get(limit=10000)
            if not results or not results['ids']:
                return 0

            now = datetime.now()
            decayed = 0
            for i, doc_id in enumerate(results['ids']):
                meta = results['metadatas'][i]
                # Skip already archived/decayed items
                if meta.get('tier') == 'archived' or meta.get('decayed'):
                    continue
                fecha_str = meta.get('fecha')
                if not fecha_str:
                    continue
                try:
                    fecha = datetime.fromisoformat(fecha_str)
                    days_old = (now - fecha).days
                except (ValueError, TypeError):
                    continue

                tipo = meta.get('tipo', 'artefacto')
                half_life = _HALF_LIFE_DAYS.get(tipo, 30)

                if days_old > half_life * 2:
                    meta['decayed'] = True
                    meta['decayed_at'] = now.isoformat()
                    self._chroma_collection.update(
                        ids=[doc_id],
                        metadatas=[meta]
                    )
                    decayed += 1

            return decayed

        # Fallback: local JSON index
        idx_file = self.memory_dir / 'local_index.json'
        if not idx_file.exists():
            return 0

        with open(idx_file) as f:
            idx = json.load(f)

        now = datetime.now()
        decayed = 0

        for item in idx:
            meta = item.get('metadata', {})
            if meta.get('tier') == 'archived' or meta.get('decayed'):
                continue
            fecha_str = meta.get('fecha')
            if not fecha_str:
                continue

            try:
                fecha = datetime.fromisoformat(fecha_str)
                days_old = (now - fecha).days
            except (ValueError, TypeError):
                continue

            tipo = meta.get('tipo', 'artefacto')
            half_life = _HALF_LIFE_DAYS.get(tipo, 30)

            if days_old > half_life * 2:
                meta['decayed'] = True
                meta['decayed_at'] = now.isoformat()
                decayed += 1

        if decayed > 0:
            with open(idx_file, 'w') as f:
                json.dump(idx, f, indent=2, ensure_ascii=False)

        return decayed

    def get_tier_stats(self, project: str) -> dict:
        """Get statistics per tier.

        Returns:
            Dict with tier counts
        """
        stats = {'raw': 0, 'compressed': 0, 'memory': 0, 'knowledge': 0, 'archived': 0, 'total': 0}

        if CHROMA_AVAILABLE and self._chroma_collection:
            where_filter = {"proyecto": project}
            results = self._chroma_collection.get(where=where_filter, limit=10000)
            if results and results['metadatas']:
                for meta in results['metadatas']:
                    tier = meta.get('tier', 'raw')
                    if tier in stats:
                        stats[tier] += 1
                    stats['total'] += 1
            return stats

        idx_file = self.memory_dir / 'local_index.json'
        if not idx_file.exists():
            return stats

        with open(idx_file) as f:
            idx = json.load(f)

        for item in idx:
            meta = item.get('metadata', {})
            if meta.get('proyecto') != project:
                continue

            tier = meta.get('tier', 'raw')
            if tier in stats:
                stats[tier] += 1
            stats['total'] += 1

        return stats

    # ── Compaction (LLM + extractive fallback) ─────────────────────────────

    @staticmethod
    def _jaccard_similarity(s1: str, s2: str) -> float:
        """Jaccard similarity between two strings."""
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        if not set1 or not set2:
            return 0.0
        return len(set1 & set2) / len(set1 | set2)

    @staticmethod
    def _extract_key_sentence(text: str) -> str:
        """Extract the most informative sentence from a text."""
        import re as _re
        sentences = _re.split(r'[.!?]\s+', text.strip())
        if not sentences:
            return text[:200]

        HIGH_VALUE = [
            'decidimos', 'decisión', 'decision', 'lesson', 'lección', 'riesgo',
            'problema', 'causa', 'solución', 'implementar', 'configurar',
            'instalar', 'bug', 'fix', 'error', 'bloquea', 'critical',
        ]

        scored = []
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            score = sum(1 for kw in HIGH_VALUE if kw in s.lower())
            scored.append((score, s))

        if not scored:
            return text[:200]

        best = max(scored, key=lambda x: x[0])
        return best[1][:300]

    def compact_extractive(self, items: list[dict], threshold: float = 0.7) -> list[dict]:
        """Extractive compression: dedup by Jaccard + key sentence extraction.

        Args:
            items: list of dicts with 'text' and 'metadata' keys
            threshold: Jaccard similarity threshold for dedup (0-1)

        Returns:
            List of compressed items with tier='compressed'
        """
        if not items:
            return []

        # Step 1: Dedup by Jaccard similarity (keep most recent)
        unique = [items[0]]
        for item in items[1:]:
            text = item['text']
            is_dup = False
            for existing in unique:
                sim = self._jaccard_similarity(text, existing['text'])
                if sim > threshold:
                    # Keep the more recent one
                    if item.get('metadata', {}).get('indexed_at', '') > existing.get('metadata', {}).get('indexed_at', ''):
                        unique.remove(existing)
                        unique.append(item)
                    is_dup = True
                    break
            if not is_dup:
                unique.append(item)

        # Step 2: Key sentence extraction
        compressed = []
        for item in unique:
            summary = self._extract_key_sentence(item['text'])
            meta = item.get('metadata', {}).copy()
            meta['tier'] = 'compressed'
            meta['compact_method'] = 'extractive'
            meta['compact_at'] = datetime.now().isoformat()
            meta['original_id'] = item.get('id', '')
            compressed.append({'text': summary, 'metadata': meta})

        return compressed

    def compact_tier(self, project: str, max_items: int = 50,
                     provider=None, force: str | None = None) -> dict:
        """Compact raw items into compressed tier.

        Args:
            project: project name to filter
            max_items: max items to compact in one run
            provider: LLM provider (from evol-provider.py). None = auto-detect.
            force: 'llm' or 'extractive' to force a method. None = auto.

        Returns:
            dict with stats: {method, before, after, compacted, skipped}
        """
        # Get raw items
        if CHROMA_AVAILABLE and self._chroma_collection:
            where_filter = {"$and": [
                {"tier": "raw"},
                {"proyecto": project}
            ]}
            results = self._chroma_collection.get(where=where_filter, limit=max_items)
            raw_items = []
            if results and results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    raw_items.append({
                        'id': doc_id,
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {},
                    })
        else:
            raw_items = self.search("", project=project, n_results=max_items)
            raw_items = [r for r in raw_items if r['metadata'].get('tier') == 'raw']

        if not raw_items:
            return {'method': 'none', 'before': 0, 'after': 0, 'compacted': 0, 'skipped': 0}

        # Decide method
        use_llm = False
        if force == 'llm':
            use_llm = True
        elif force == 'extractive':
            use_llm = False
        elif provider is not None:
            use_llm = getattr(provider, '__class__', type).__name__ != 'MockProvider'
        # Default: extractive (safe fallback)

        if use_llm:
            compressed = self._compact_with_llm(raw_items, provider, project)
        else:
            compressed = self.compact_extractive(raw_items)

        # Index compressed items first
        for c in compressed:
            self.index(c['text'], c['metadata'])

        # Archive originals that were replaced (different text = new doc_id)
        compacted = 0
        for item in raw_items:
            if CHROMA_AVAILABLE and self._chroma_collection:
                compressed_text = None
                for c in compressed:
                    if c.get('metadata', {}).get('original_id') == item['id']:
                        compressed_text = c['text']
                        break

                if compressed_text and compressed_text != item['text']:
                    # Text changed → archive original (new doc_id was created)
                    meta = item['metadata'].copy()
                    meta['tier'] = 'archived'
                    meta['archived_at'] = datetime.now().isoformat()
                    self._chroma_collection.update(
                        ids=[item['id']],
                        metadatas=[meta]
                    )
                else:
                    # Text unchanged → just update tier to compressed
                    meta = item['metadata'].copy()
                    meta['tier'] = 'compressed'
                    meta['compact_method'] = 'extractive'
                    meta['compact_at'] = datetime.now().isoformat()
                    self._chroma_collection.update(
                        ids=[item['id']],
                        metadatas=[meta]
                    )
            compacted += 1

        return {
            'method': 'llm' if use_llm else 'extractive',
            'before': len(raw_items),
            'after': len(compressed),
            'compacted': compacted,
            'skipped': len(raw_items) - compacted,
        }

    def _compact_with_llm(self, items: list[dict], provider, project: str) -> list[dict]:
        """LLM-based compaction: summarize batches of raw items."""
        BATCH_SIZE = 10
        all_compressed = []

        for i in range(0, len(items), BATCH_SIZE):
            batch = items[i:i + BATCH_SIZE]

            # Build prompt
            observations = []
            for idx, item in enumerate(batch):
                observations.append(f"[{idx + 1}] {item['text'][:500]}")

            prompt = (
                "Eres un motor de compresión de memoria técnica de un proyecto de software.\n"
                "Recibe observaciones raw de un proyecto. Comprime cada batch en un resumen conciso que preserve:\n"
                "- Decisiones clave (qué se decidió y por qué)\n"
                "- Hechos relevantes (qué existe, qué cambió)\n"
                "- Lecciones aprendidas\n"
                "- Riesgos activos\n\n"
                "NO incluyas metadata irrelevante (hashes, timestamps exactos) ni texto duplicado.\n"
                "Output: un solo párrafo por batch, máximo 300 caracteres.\n\n"
                "Observaciones:\n" + "\n".join(observations)
            )

            try:
                result = provider.complete(prompt, max_tokens=300)
                summary = result.get('content', '') if isinstance(result, dict) else str(result)
            except Exception:
                # Fallback to extractive for this batch
                compressed = self.compact_extractive(batch)
                all_compressed.extend(compressed)
                continue

            meta = batch[0]['metadata'].copy()
            meta['tier'] = 'compressed'
            meta['compact_method'] = 'llm'
            meta['compact_at'] = datetime.now().isoformat()
            meta['batch_size'] = len(batch)
            all_compressed.append({'text': summary[:500], 'metadata': meta})

        return all_compressed

    # ── FlowScript Queries (6 types) ──────────────────────────────────────

    def query_why(self, decision_text: str) -> list[dict]:
        """WHY: Por que se tomo esta decision? Find causes."""
        results = self.search(decision_text, tipo='decision', n_results=5)
        causes = []
        for r in results:
            # Look for related causes in graph
            node_id = hashlib.sha256(r['text'].encode()).hexdigest()[:12]
            traversal = self.graph_traverse(node_id, depth=2)
            for rel in traversal.get('relations', []):
                if rel['type'] in ('CAUSA', 'AFECTA'):
                    causes.append({'decision': r['text'][:100], 'cause': rel})
        return causes

    def query_tensions(self) -> list[dict]:
        """TENSIONS: Que lecciones conflictan entre si?"""
        lessons = self.search("", tipo='leccion', n_results=20)
        tensions = []
        for i, l1 in enumerate(lessons):
            for l2 in lessons[i+1:]:
                # Simple conflict detection: different categories, same topic
                cat1 = l1['metadata'].get('fase', '')
                cat2 = l2['metadata'].get('fase', '')
                if cat1 != cat2:
                    words1 = set(l1['text'].lower().split())
                    words2 = set(l2['text'].lower().split())
                    common = words1 & words2
                    if len(common) > 3:  # Significant overlap
                        tensions.append({
                            'lesson1': l1['text'][:100],
                            'lesson2': l2['text'][:100],
                            'common_words': list(common)[:5]
                        })
        return tensions

    def query_blocked(self) -> list[dict]:
        """BLOCKED: Que riesgos bloquean progreso?"""
        risks = self.search("", tipo='riesgo', n_results=10)
        blocked = []
        for r in risks:
            if r['metadata'].get('status', 'activo') == 'activo':
                blocked.append({
                    'risk': r['text'][:100],
                    'metadata': r['metadata']
                })
        return blocked

    def query_whatif(self, scenario: str) -> list[dict]:
        """WHATIF: Que pasaria si...? Simulate over subgraph."""
        # Find related decisions
        decisions = self.search(scenario, tipo='decision', n_results=3)
        scenarios = []
        for d in decisions:
            node_id = hashlib.sha256(d['text'].encode()).hexdigest()[:12]
            traversal = self.graph_traverse(node_id, depth=3)
            scenarios.append({
                'decision': d['text'][:100],
                'consequences': [rel for rel in traversal.get('relations', [])]
            })
        return scenarios

    def query_alternatives(self, decision_text: str) -> list[dict]:
        """ALTERNATIVES: Que alternativas se consideraron?"""
        results = self.search(decision_text, tipo='decision', n_results=5)
        alternatives = []
        for r in results:
            # Look for DESCARTA relations
            node_id = hashlib.sha256(r['text'].encode()).hexdigest()[:12]
            traversal = self.graph_traverse(node_id, depth=2)
            for rel in traversal.get('relations', []):
                if rel['type'] == 'DESCARTA':
                    alternatives.append({
                        'chosen': r['text'][:100],
                        'alternative': rel
                    })
        return alternatives

    # ── Team Memory Namespaces ────────────────────────────────────────────

    def index_agent(self, text: str, agent_id: str, scope: str = 'shared',
                    metadata: dict | None = None) -> str:
        """Index text with agent-specific namespace.

        Args:
            text: Text to index
            agent_id: Agent identifier (e.g., 'evol-architect')
            scope: 'shared' (visible to all) or 'private' (agent-only)
            metadata: Additional metadata

        Returns:
            Document ID
        """
        meta = metadata or {}
        meta['agente'] = agent_id
        meta['scope'] = scope
        return self.index(text, meta)

    def search_agent(self, query: str, agent_id: str | None = None,
                     scope: str | None = None, **kwargs) -> list[dict]:
        """Search with agent namespace filtering.

        Args:
            query: Search query
            agent_id: Filter by agent (None = all agents)
            scope: Filter by scope (shared/private)
            **kwargs: Additional search filters

        Returns:
            List of matching drawers
        """
        if agent_id:
            kwargs['agent'] = agent_id
        return self.search(query, **kwargs)

    def get_agent_context(self, agent_id: str, project: str) -> str:
        """Get context specific to an agent.

        Returns:
            String with agent-relevant memory
        """
        parts = [f"Agente: {agent_id}"]

        # Agent's own memories
        agent_memories = self.search_agent("", agent_id=agent_id, n_results=5)
        if agent_memories:
            parts.append("Memorias propias:")
            for m in agent_memories:
                parts.append(f"  - {m['text'][:80]}")

        # Shared memories relevant to agent
        shared = self.search_agent("", scope='shared', n_results=5)
        if shared:
            parts.append("Memorias compartidas:")
            for s in shared:
                parts.append(f"  - {s['text'][:80]}")

        context = '\n'.join(parts)
        if len(context) > 800:
            context = context[:797] + '...'
        return context

    # ── Code Graph Integration ──────────────────────────────────────────────

    def get_code_graph(self):
        """Get the CodeGraph instance for code indexing.

        Returns:
            CodeGraph instance or None if not available
        """
        try:
            from evol_code_indexer import CodeGraph
            return CodeGraph(self.memory_dir)
        except ImportError:
            return None

    def index_code(self, project_root: str, incremental: bool = True) -> dict:
        """Index code files into the code graph.

        Args:
            project_root: Root directory of the project
            incremental: If True, only index changed files

        Returns:
            Stats dict
        """
        from pathlib import Path
        graph = self.get_code_graph()
        if not graph:
            return {"error": "evol_code_indexer not available"}

        from evol_code_indexer import index_project
        return index_project(Path(project_root), incremental=incremental, graph=graph)

    def code_impact(self, symbol: str, max_depth: int = 3) -> dict:
        """Analyze impact of changing a symbol.

        Args:
            symbol: Symbol name to analyze
            max_depth: Maximum depth for impact analysis

        Returns:
            Impact analysis dict
        """
        graph = self.get_code_graph()
        if not graph:
            return {"error": "evol_code_indexer not available"}
        return graph.get_impact(symbol, max_depth=max_depth)

    def code_trace(self, entry_point: str, max_depth: int = 5) -> dict:
        """Trace execution flow from an entry point.

        Args:
            entry_point: Entry point symbol
            max_depth: Maximum depth for trace

        Returns:
            Trace dict
        """
        graph = self.get_code_graph()
        if not graph:
            return {"error": "evol_code_indexer not available"}
        return graph.get_trace(entry_point, max_depth=max_depth)

    def code_query(self, symbol: str) -> list[dict]:
        """Query information about a code symbol.

        Args:
            symbol: Symbol name to query

        Returns:
            List of matching results
        """
        graph = self.get_code_graph()
        if not graph:
            return []
        return graph.query_symbol(symbol)

    def code_stats(self) -> dict:
        """Get code graph statistics.

        Returns:
            Stats dict
        """
        graph = self.get_code_graph()
        if not graph:
            return {"error": "evol_code_indexer not available"}
        return graph.stats()

        with open(idx_file) as f:
            idx = json.load(f)

        for item in idx:
            meta = item.get('metadata', {})
            if meta.get('proyecto') != project:
                continue

            tipo = meta.get('tipo', 'artefacto')
            for tier in stats:
                if tipo.startswith(tier):
                    stats[tier] += 1
                    stats['total'] += 1
                    break

        return stats
