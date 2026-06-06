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

import hashlib
import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# ── Optional imports with fallback ─────────────────────────────────────────────

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import ladybugdb
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
            memory_dir = os.path.expanduser('~/.evol/memory')
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
        ladybug_path = str(self.memory_dir / 'ladybugdb')
        self._ladybug_client = ladybugdb.Client(path=ladybug_path)

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

        if CHROMA_AVAILABLE and self._chroma_collection:
            doc_id = hashlib.sha256(clean_text.encode()).hexdigest()[:16]
            self._chroma_collection.upsert(
                ids=[doc_id],
                documents=[clean_text],
                metadatas=[meta]
            )
            return doc_id

        # Fallback: write to local JSON index
        return self._index_local(clean_text, meta)

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
            where = filters if filters else None
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
            return out

        # Fallback: local JSON search (BM25-like keyword match)
        return self._search_local(clean_query, filters, n_results)

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
            self._ladybug_client.add_node(node_type, properties)
            return node_id

        # Fallback: in-memory dict
        key = f"{node_type}:{node_id}"
        self._graph[key] = {'type': node_type, 'properties': properties}
        self._save_graph()
        return node_id

    def graph_add_relation(self, source_id: str, relation_type: str, target_id: str) -> bool:
        """Add a relation between two nodes.

        Returns:
            True if successful
        """
        if LADYBUG_AVAILABLE:
            self._ladybug_client.add_relation(source_id, relation_type, target_id)
            return True

        # Fallback: in-memory dict
        rel_key = f"{source_id}->{target_id}"
        if rel_key not in self._graph:
            self._graph[rel_key] = {'type': relation_type}
            self._save_graph()
        return True

    def graph_traverse(self, node_id: str, depth: int = 2) -> dict:
        """Traverse graph from a node.

        Returns:
            Subgraph as dict with nodes and relations
        """
        if LADYBUG_AVAILABLE:
            return self._ladybug_client.traverse(node_id, depth)

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

        context = '\n'.join(parts)
        # Truncate to ~170 tokens (~800 chars)
        if len(context) > 800:
            context = context[:797] + '...'
        return context
