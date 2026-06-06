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

        # Auto-update graph based on metadata
        self._auto_update_graph(clean_text, meta)

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

    # ── 4-Tier Consolidation ──────────────────────────────────────────────

    def consolidate_tier(self, from_tier: str, to_tier: str, project: str,
                         max_items: int = 50) -> int:
        """Consolidate drawers from one tier to the next.

        Tiers: raw -> compressed -> memory -> knowledge

        Returns:
            Number of items consolidated
        """
        # Find items from source tier
        results = self.search(
            "",
            project=project,
            n_results=max_items,
        )

        # Filter by tier (using 'tipo' field with tier prefix)
        source_items = [r for r in results if r['metadata'].get('tipo', '').startswith(from_tier)]

        if not source_items:
            return 0

        consolidated = 0
        for item in source_items:
            meta = item['metadata'].copy()
            meta['tipo'] = to_tier
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
        idx_file = self.memory_dir / 'local_index.json'
        if not idx_file.exists():
            return 0

        with open(idx_file) as f:
            idx = json.load(f)

        now = datetime.now()
        decayed = 0

        for item in idx:
            meta = item.get('metadata', {})
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

            # Mark as decayed if older than 2x half-life
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
        stats = {'raw': 0, 'compressed': 0, 'memory': 0, 'knowledge': 0, 'total': 0}

        idx_file = self.memory_dir / 'local_index.json'
        if not idx_file.exists():
            return stats

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
