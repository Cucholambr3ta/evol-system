"""
BM25 retriever with stdlib Python (no external dependencies).

Implements BM25 Okapi algorithm for keyword-based retrieval.
Uses inverted index with term frequency and document frequency.

Part of EDMS Memory v2.0 Phase 2 - Hybrid Retrieval.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

# Spanish/English stop words (minimal set)
_STOP_WORDS = frozenset(
    "a al algo ante antes aquel aquellos aquellas cada con contra "
    "de del desde el ella ellos ellas en entre era esa ese eso "
    "este esto estos estas fue fui ha hay hemos hoy la le les lo "
    "los las más me mi mis muy no nos nuestro nuestra o os otra "
    "otro otros otras para por poco que quien se sin sino sobre "
    "sus su suyos también te tiene todo todos tu tus un una uno "
    "unos ustedes va van vos we what when where which who whom why "
    "how the is are was were be been being have has had do does did "
    "will would shall should may might can could am is are was were "
    "and or but if then else for in on at to from by with as of it "
    "its this that these those i me my we our you your he his she her "
    "they them their es un una uno unos unas".split()
)


def tokenize(text: str) -> list[str]:
    """
    Tokenize text into normalized terms.

    Lowercase, remove punctuation, split on whitespace,
    filter stop words and short tokens (< 2 chars).
    """
    text = text.lower()
    # Remove punctuation and special characters
    text = re.sub(r"[^\w\s]", " ", text)
    # Split on whitespace
    tokens = text.split()
    # Filter stop words and short tokens (only keep tokens >= 3 chars)
    return [t for t in tokens if t not in _STOP_WORDS and len(t) >= 3]


# ---------------------------------------------------------------------------
# BM25 Parameters
# ---------------------------------------------------------------------------

@dataclass
class BM25Params:
    """BM25 tuning parameters."""
    k1: float = 1.5   # Term frequency saturation
    b: float = 0.75    # Document length normalization


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

@dataclass
class Document:
    """Indexed document with metadata."""
    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    tokens: list[str] = field(default_factory=list)
    length: int = 0

    def __post_init__(self):
        self.tokens = tokenize(self.text)
        self.length = len(self.tokens)


# ---------------------------------------------------------------------------
# BM25 Retriever
# ---------------------------------------------------------------------------

class BM25Retriever:
    """
    BM25 Okapi retriever with stdlib Python.

    Features:
    - Inverted index with term frequency
    - Document length normalization
    - TF-IDF scoring
    - Persistence to JSON

    Usage:
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB es una librería de vectores")
        results = retriever.search("ChromaDB vectores", top_k=5)
    """

    def __init__(self, params: BM25Params | None = None):
        self.params = params or BM25Params()

        # Inverted index: term -> {doc_id: term_frequency}
        self._index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Documents: doc_id -> Document
        self._documents: dict[str, Document] = {}

        # Document frequency: term -> number of documents containing it
        self._doc_freq: dict[str, int] = defaultdict(int)

        # Average document length
        self._avg_doc_length: float = 0.0

        # Total documents
        self._total_docs: int = 0

    def add(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """
        Add or update a document in the index.

        Args:
            doc_id: Unique document identifier
            text: Document text content
            metadata: Optional metadata dict
        """
        # Remove old document if exists (for updates)
        if doc_id in self._documents:
            self._remove_document(doc_id)

        # Create document
        doc = Document(id=doc_id, text=text, metadata=metadata or {})
        self._documents[doc_id] = doc

        # Update inverted index
        term_counts = Counter(doc.tokens)
        for term, count in term_counts.items():
            self._index[term][doc_id] = count

        # Update document frequency
        for term in set(doc.tokens):
            self._doc_freq[term] += 1

        # Update statistics
        self._total_docs += 1
        self._update_avg_doc_length()

    def _remove_document(self, doc_id: str) -> None:
        """Remove a document from the index."""
        if doc_id not in self._documents:
            return

        doc = self._documents[doc_id]

        # Remove from inverted index
        term_counts = Counter(doc.tokens)
        for term in term_counts:
            if doc_id in self._index[term]:
                del self._index[term][doc_id]
                if not self._index[term]:
                    del self._index[term]

            # Update document frequency
            if self._doc_freq[term] > 0:
                self._doc_freq[term] -= 1
                if self._doc_freq[term] == 0:
                    del self._doc_freq[term]

        # Remove document
        del self._documents[doc_id]

        # Update statistics
        self._total_docs -= 1
        self._update_avg_doc_length()

    def _update_avg_doc_length(self) -> None:
        """Update average document length."""
        if self._total_docs == 0:
            self._avg_doc_length = 0.0
        else:
            total_length = sum(doc.length for doc in self._documents.values())
            self._avg_doc_length = total_length / self._total_docs

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
        filter_fn: callable | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for documents matching the query.

        Args:
            query: Search query string
            top_k: Maximum number of results
            min_score: Minimum score threshold
            filter_fn: Optional filter function(doc_metadata) -> bool

        Returns:
            List of result dicts with id, score, text, metadata
        """
        if not query.strip():
            return []

        # Tokenize query
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        # Score each document
        scores: list[tuple[str, float]] = []

        for doc_id, doc in self._documents.items():
            # Apply filter
            if filter_fn and not filter_fn(doc.metadata):
                continue

            # Calculate BM25 score
            score = self._score_document(query_tokens, doc)
            if score >= min_score:
                scores.append((doc_id, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Return top_k results (filter out zero scores)
        results = []
        for doc_id, score in scores[:top_k]:
            if score <= 0:
                continue
            doc = self._documents[doc_id]
            results.append({
                "id": doc_id,
                "score": round(score, 4),
                "text": doc.text,
                "metadata": doc.metadata,
            })

        return results

    def _score_document(self, query_tokens: list[str], doc: Document) -> float:
        """
        Calculate BM25 score for a document.

        BM25 formula:
        score(D, Q) = Σ IDF(qi) * (f(qi, D) * (k1 + 1)) / (f(qi, D) + k1 * (1 - b + b * |D| / avgdl))

        Where:
        - IDF(qi) = log((N - n(qi) + 0.5) / (n(qi) + 0.5) + 1)
        - f(qi, D) = term frequency of qi in document D
        - |D| = document length
        - avgdl = average document length
        """
        score = 0.0
        k1 = self.params.k1
        b = self.params.b

        for term in query_tokens:
            if term not in self._index:
                continue

            # Term frequency in this document
            tf = self._index[term].get(doc.id, 0)
            if tf == 0:
                continue

            # Document frequency (number of docs containing term)
            df = self._doc_freq.get(term, 0)

            # IDF (Inverse Document Frequency)
            idf = math.log((self._total_docs - df + 0.5) / (df + 0.5) + 1)

            # BM25 score component
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * doc.length / self._avg_doc_length)
            score += idf * numerator / denominator

        return score

    def get_document(self, doc_id: str) -> Document | None:
        """Get document by ID."""
        return self._documents.get(doc_id)

    def remove_document(self, doc_id: str) -> bool:
        """Remove document by ID. Returns True if removed."""
        if doc_id not in self._documents:
            return False
        self._remove_document(doc_id)
        return True

    def stats(self) -> dict[str, Any]:
        """Get index statistics."""
        return {
            "total_documents": self._total_docs,
            "total_terms": len(self._index),
            "avg_doc_length": round(self._avg_doc_length, 2),
            "index_size_bytes": len(json.dumps(self._index).encode()),
        }

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save index to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "params": {
                "k1": self.params.k1,
                "b": self.params.b,
            },
            "documents": {
                doc_id: {
                    "text": doc.text,
                    "metadata": doc.metadata,
                }
                for doc_id, doc in self._documents.items()
            },
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> BM25Retriever:
        """Load index from JSON file."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())

        # Create retriever with saved params
        params = BM25Params(**data.get("params", {}))
        retriever = cls(params=params)

        # Add documents
        for doc_id, doc_data in data.get("documents", {}).items():
            retriever.add(
                doc_id=doc_id,
                text=doc_data["text"],
                metadata=doc_data.get("metadata", {}),
            )

        return retriever
