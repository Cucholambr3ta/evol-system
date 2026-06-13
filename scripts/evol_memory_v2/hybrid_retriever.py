"""
Hybrid retriever for EDMS Memory v2.0.

Combines vector search, BM25 keyword search, and graph-based expansion
using Reciprocal Rank Fusion (RRF) for optimal retrieval.

Part of EDMS Memory v2.0 Phase 2 - Hybrid Retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .bm25_retriever import BM25Retriever
from .evidence import EvidenceBuilder, EvidenceContract
from .graph_expander import GraphExpander

# Default half-life (days) per atom type for temporal decay.
# Architectural decisions decay slowly; volatile state (branch, version) fast.
# Used only when temporal_decay > 0. Falls back to DEFAULT_HALF_LIFE_DAYS.
DEFAULT_HALF_LIFE_DAYS = 90.0
HALF_LIFE_BY_TIPO: dict[str, float] = {
    "decision": 365.0,
    "convencion": 365.0,
    "leccion": 180.0,
    "artefacto": 120.0,
    "riesgo": 60.0,
    "prediction": 30.0,
    "resumen": 30.0,
    "handoff": 14.0,
}


def _parse_timestamp(value: Any) -> datetime | None:
    """Parse an ISO-8601 timestamp into an aware datetime, or None.

    Tolerates missing values, epoch floats/ints, and trailing 'Z'.
    """
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str):
        text = value.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    return None


def _temporal_weight(
    created_at: Any,
    half_life_days: float,
    *,
    now: datetime | None = None,
) -> float:
    """Exponential recency weight in (0, 1].

    weight = 0.5 ** (age_days / half_life_days)

    A fresh item scores ~1.0; one half-life old scores 0.5; etc. Missing or
    unparseable timestamps return 1.0 (no penalty — neutral). half_life_days
    <= 0 disables decay (returns 1.0).
    """
    if half_life_days <= 0:
        return 1.0
    ts = _parse_timestamp(created_at)
    if ts is None:
        return 1.0
    reference = now or datetime.now(timezone.utc)
    age_days = (reference - ts).total_seconds() / 86400.0
    if age_days <= 0:
        return 1.0
    return float(0.5 ** (age_days / half_life_days))


@dataclass
class RetrievalResult:
    """A single retrieval result with evidence."""
    id: str
    score: float
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    evidence: EvidenceContract | None = None
    retrieval_sources: list[str] = field(default_factory=list)


class HybridRetriever:
    """
    Hybrid retriever combining vector, BM25, and graph search.

    Uses Reciprocal Rank Fusion (RRF) to combine results from
    multiple retrieval sources into a single ranked list.

    RRF formula: score(d) = Σ 1 / (k + rank_i(d))
    where k is a constant (typically 60) and rank_i is the rank in source i.

    Usage:
        retriever = HybridRetriever()
        retriever.add_document("doc1", "ChromaDB es una librería de vectores")
        results = retriever.search("ChromaDB vectores", top_k=5)
    """

    def __init__(
        self,
        k: int = 60,
        use_vector: bool = True,
        use_bm25: bool = True,
        use_graph: bool = True,
        temporal_decay: float = 0.0,
        half_life_by_tipo: dict[str, float] | None = None,
    ):
        """
        Initialize hybrid retriever.

        Args:
            k: RRF constant (higher = less weight to top ranks)
            use_vector: Enable vector search (requires ChromaDB)
            use_bm25: Enable BM25 keyword search
            use_graph: Enable graph-based query expansion
            temporal_decay: Strength of recency weighting in [0, 1].
                0.0 (default) disables it — fully backward-compatible. At 1.0
                the recency weight multiplies the RRF score directly; values
                in between blend toward 1.0 (no penalty).
            half_life_by_tipo: Optional override of per-tipo half-lives (days).
                Merged over HALF_LIFE_BY_TIPO defaults.
        """
        self.k = k
        self.use_vector = use_vector
        self.use_bm25 = use_bm25
        self.use_graph = use_graph
        self.temporal_decay = max(0.0, min(1.0, temporal_decay))
        self.half_life_by_tipo = dict(HALF_LIFE_BY_TIPO)
        if half_life_by_tipo:
            self.half_life_by_tipo.update(half_life_by_tipo)

        # BM25 retriever (always available)
        self._bm25 = BM25Retriever()

        # Graph expander
        self._graph = GraphExpander(max_depth=2, max_expansions=10)

        # Vector store reference (optional)
        self._vector_store = None

        # Document store: id -> {text, metadata}
        self._documents: dict[str, dict[str, Any]] = {}

    def set_vector_store(self, store: Any) -> None:
        """
        Set the vector store for semantic search.

        Args:
            store: Vector store instance with search() method
        """
        self._vector_store = store

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a document to all retrieval sources.

        Args:
            doc_id: Unique document ID
            text: Document text
            metadata: Optional metadata
        """
        metadata = metadata or {}

        # Store document
        self._documents[doc_id] = {"text": text, "metadata": metadata}

        # Add to BM25
        if self.use_bm25:
            self._bm25.add(doc_id, text, metadata)

        # Extract entities and add to graph
        if self.use_graph:
            self._add_to_graph(doc_id, text, metadata)

    def _add_to_graph(self, doc_id: str, text: str, metadata: dict[str, Any]) -> None:
        """Extract entities from text and add to graph."""
        # Simple entity extraction (could use EntityExtractor from Phase 1)
        words = text.lower().split()

        # Add significant words as nodes
        for word in words:
            if len(word) > 3:  # Skip short words
                node_type = metadata.get("tipo", "concept")
                self._graph.add_node(word, node_type)

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
        include_evidence: bool = True,
    ) -> list[RetrievalResult]:
        """
        Search using hybrid retrieval.

        Args:
            query: Search query
            top_k: Maximum results
            min_score: Minimum score threshold
            include_evidence: Include evidence contracts

        Returns:
            List of RetrievalResult with fused scores
        """
        # Expand query using graph
        expanded_terms = query
        if self.use_graph and query.strip():
            expanded_terms = " ".join(self._graph.expand(query))

        # Collect results from each source
        all_results: dict[str, dict[str, list[tuple[str, float]]]] = {
            doc_id: {"sources": [], "texts": [], "scores": []}
            for doc_id in self._documents
        }

        # BM25 search
        if self.use_bm25 and query.strip():
            bm25_results = self._bm25.search(expanded_terms, top_k=top_k * 2)
            for rank, result in enumerate(bm25_results, 1):
                doc_id = result["id"]
                if doc_id in all_results:
                    all_results[doc_id]["sources"].append("bm25")
                    all_results[doc_id]["scores"].append(("bm25", rank, result["score"]))

        # Vector search (if available)
        if self.use_vector and self._vector_store:
            vector_results = self._vector_store.search(expanded_terms, top_k=top_k * 2)
            for rank, result in enumerate(vector_results, 1):
                doc_id = result["id"]
                if doc_id in all_results:
                    all_results[doc_id]["sources"].append("vector")
                    all_results[doc_id]["scores"].append(("vector", rank, result["score"]))

        # Calculate RRF scores
        rrf_scores: list[tuple[str, float, list[str]]] = []

        for doc_id, data in all_results.items():
            if not data["sources"]:
                continue

            # Calculate RRF score
            rrf_score = 0.0
            for source, rank, original_score in data["scores"]:
                rrf_score += 1.0 / (self.k + rank)

            # Apply temporal recency weighting (no-op when temporal_decay == 0)
            if self.temporal_decay > 0:
                rrf_score *= self._recency_multiplier(
                    self._documents.get(doc_id, {}).get("metadata", {})
                )

            # Collect source names
            sources = list(set(data["sources"]))

            if rrf_score >= min_score:
                rrf_scores.append((doc_id, rrf_score, sources))

        # Sort by RRF score
        rrf_scores.sort(key=lambda x: x[1], reverse=True)

        # Build results
        results = []
        for doc_id, rrf_score, sources in rrf_scores[:top_k]:
            doc = self._documents.get(doc_id, {})

            # Create evidence contract
            evidence = None
            if include_evidence:
                evidence = self._create_evidence(
                    doc_id, rrf_score, sources, doc.get("metadata", {})
                )

            result = RetrievalResult(
                id=doc_id,
                score=rrf_score,
                text=doc.get("text", ""),
                metadata=doc.get("metadata", {}),
                evidence=evidence,
                retrieval_sources=sources,
            )
            results.append(result)

        return results

    def _recency_multiplier(self, metadata: dict[str, Any]) -> float:
        """Blend the raw exponential recency weight by temporal_decay.

        decay == 0 -> 1.0 (no effect); decay == 1 -> raw weight; in between,
        linearly interpolate toward 1.0 so older items are only partially
        penalized. Half-life is chosen by the atom's ``tipo``.
        """
        tipo = metadata.get("tipo", "")
        half_life = self.half_life_by_tipo.get(tipo, DEFAULT_HALF_LIFE_DAYS)
        created = metadata.get("created_at") or metadata.get("updated_at")
        raw = _temporal_weight(created, half_life)
        return (1.0 - self.temporal_decay) + self.temporal_decay * raw

    def _create_evidence(
        self,
        doc_id: str,
        score: float,
        sources: list[str],
        metadata: dict[str, Any],
    ) -> EvidenceContract:
        """Create evidence contract for a result."""
        builder = EvidenceBuilder()

        # Set item ID first
        builder.for_item(doc_id)

        # Add sources
        for source in sources:
            builder.with_source(source, doc_id, confidence=score)

        # Add reasoning
        reasoning = f"Retrieved via {', '.join(sources)} with RRF score {score:.3f}"
        builder.with_reasoning(reasoning)

        # Add confidence
        builder.with_confidence(min(score * 10, 1.0))  # Normalize to [0, 1]

        # Add metadata
        if "tier" in metadata:
            builder.with_metadata("tier", metadata["tier"])
        if "tipo" in metadata:
            builder.with_metadata("tipo", metadata["tipo"])

        return builder.build()

    def stats(self) -> dict[str, Any]:
        """Get retriever statistics."""
        return {
            "documents": len(self._documents),
            "bm25": self._bm25.stats() if self.use_bm25 else None,
            "graph": self._graph.stats() if self.use_graph else None,
            "vector_store": "connected" if self._vector_store else "disconnected",
            "config": {
                "k": self.k,
                "use_vector": self.use_vector,
                "use_bm25": self.use_bm25,
                "use_graph": self.use_graph,
                "temporal_decay": self.temporal_decay,
            },
        }
