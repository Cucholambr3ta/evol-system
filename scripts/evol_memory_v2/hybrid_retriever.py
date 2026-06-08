"""
Hybrid retriever for EDMS Memory v2.0.

Combines vector search, BM25 keyword search, and graph-based expansion
using Reciprocal Rank Fusion (RRF) for optimal retrieval.

Part of EDMS Memory v2.0 Phase 2 - Hybrid Retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .bm25_retriever import BM25Retriever
from .evidence import EvidenceBuilder, EvidenceContract
from .graph_expander import GraphExpander


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
    ):
        """
        Initialize hybrid retriever.

        Args:
            k: RRF constant (higher = less weight to top ranks)
            use_vector: Enable vector search (requires ChromaDB)
            use_bm25: Enable BM25 keyword search
            use_graph: Enable graph-based query expansion
        """
        self.k = k
        self.use_vector = use_vector
        self.use_bm25 = use_bm25
        self.use_graph = use_graph

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
            },
        }
