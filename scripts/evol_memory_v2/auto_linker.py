#!/usr/bin/env python3
"""auto_linker.py — Zero-LLM Relationship Builder for Evol-DD Memory v2.0.

Creates relationships between memory items on every write using regex patterns.
Zero token cost — deterministic and repeatable.

Inspired by GBrain's zero-LLM auto-link:
"Every `put_page` runs `extractEntityRefs` on the markdown body. Zero LLM tokens."

Usage:
    from evol_memory_v2.auto_linker import AutoLinker
    linker = AutoLinker()
    links = linker.link("Decidimos usar ChromaDB para vector search y LadybugDB para grafo")
    # Returns: [
    #   {"from_text": "ChromaDB", "to_text": "vector search", "relation": "PARA", "confidence": 0.8},
    #   {"from_text": "LadybugDB", "to_text": "grafo", "relation": "PARA", "confidence": 0.8},
    # ]
"""

import re
from typing import Any

from .extractor import EntityExtractor


# ── Link Patterns ─────────────────────────────────────────────────────────

LINK_PATTERNS = {
    "PARA": [
        r"(.+?)\s+para\s+(.+?)(?:\.|,|$)",
        r"(.+?)\s+for\s+(.+?)(?:\.|,|$)",
    ],
    "CON": [
        r"(.+?)\s+con\s+(.+?)(?:\.|,|$)",
        r"(.+?)\s+with\s+(.+?)(?:\.|,|$)",
    ],
    "USANDO": [
        r"(.+?)\s+usando\s+(.+?)(?:\.|,|$)",
        r"(.+?)\s+using\s+(.+?)(?:\.|,|$)",
    ],
    "BASADO_EN": [
        r"(.+?)\s+basado\s+en\s+(.+?)(?:\.|,|$)",
        r"(.+?)\s+inspirado\s+en\s+(.+?)(?:\.|,|$)",
    ],
    "SEPARADO_DE": [
        r"(.+?)\s+separado\s+(?:de|del)\s+(.+?)(?:\.|,|$)",
        r"(.+?)\s+separate\s+(?:from)\s+(.+?)(?:\.|,|$)",
    ],
    "DEPENDE_DE": [
        r"(.+?)\s+depende\s+de\s+(.+?)(?:\.|,|$)",
        r"(.+?)\s+requires?\s+(.+?)(?:\.|,|$)",
    ],
    "COMPLEMENTA": [
        r"(.+?)\s+complementa?\s+(.+?)(?:\.|,|$)",
        r"(.+?)\s+completes?\s+(.+?)(?:\.|,|$)",
    ],
}

# ── Semantic Proximity ─────────────────────────────────────────────────────

# Technologies that commonly work together
TECH_AFFINITY = {
    "chromadb": ["vector", "embedding", "search", "retrieval", "hnsw"],
    "ladybugdb": ["graph", "cypher", "relationship", "node", "edge"],
    "tree-sitter": ["ast", "parse", "code", "symbol", "language"],
    "python": ["pip", "venv", "package", "module"],
    "typescript": ["npm", "node", "package", "module"],
    "docker": ["container", "image", "deploy", "kubernetes"],
    "git": ["commit", "branch", "merge", "repository"],
}


class AutoLinker:
    """Zero-LLM relationship builder.

    Creates relationships between entities using regex patterns and
    semantic proximity. Runs on every write at near-zero cost.
    """

    def __init__(self, entity_extractor: EntityExtractor | None = None):
        """Initialize linker.

        Args:
            entity_extractor: Optional pre-configured extractor
        """
        self._extractor = entity_extractor or EntityExtractor()

        # Pre-compile link patterns
        self._compiled = {}
        for rtype, patterns in LINK_PATTERNS.items():
            self._compiled[rtype] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def link(self, text: str) -> list[dict[str, Any]]:
        """Extract relationships from text using patterns.

        Args:
            text: Input text

        Returns:
            List of link dicts with keys: from_text, to_text, relation, confidence
        """
        if not text:
            return []

        links = []
        seen = set()

        # Pattern-based extraction
        for rtype, patterns in self._compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    from_text = match.group(1).strip()
                    to_text = match.group(2).strip()

                    # Skip very short or very long entities
                    if len(from_text) < 2 or len(to_text) < 2:
                        continue
                    if len(from_text) > 100 or len(to_text) > 100:
                        continue

                    # Dedup
                    key = (from_text.lower(), to_text.lower(), rtype)
                    if key in seen:
                        continue
                    seen.add(key)

                    confidence = self._score_link(from_text, to_text, rtype, text)

                    links.append({
                        "from_text": from_text,
                        "to_text": to_text,
                        "relation": rtype,
                        "confidence": confidence,
                        "source": "pattern",
                    })

        # Entity-based proximity links
        entities = self._extractor.extract(text)
        proximity_links = self._find_proximity_links(entities, text)

        for link in proximity_links:
            key = (
                link["from_text"].lower(),
                link["to_text"].lower(),
                link["relation"],
            )
            if key not in seen:
                seen.add(key)
                links.append(link)

        return links

    def link_entities(
        self, entities: list[dict], text: str
    ) -> list[dict[str, Any]]:
        """Create links between extracted entities.

        Args:
            entities: List of entity dicts from EntityExtractor
            text: Original text context

        Returns:
            List of link dicts
        """
        links = []
        seen = set()

        # Co-occurrence links (entities in same sentence)
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence_entities = [
                e for e in entities
                if e["text"].lower() in sentence.lower()
            ]

            # Create links between co-occurring entities
            for i, e1 in enumerate(sentence_entities):
                for e2 in sentence_entities[i + 1:]:
                    key = (e1["text"].lower(), e2["text"].lower())
                    if key in seen:
                        continue
                    seen.add(key)

                    relation = self._infer_relation(e1, e2, sentence)
                    confidence = min(e1.get("confidence", 0.5), e2.get("confidence", 0.5))
                    confidence *= 0.8  # Discount for indirect relation

                    links.append({
                        "from_text": e1["text"],
                        "to_text": e2["text"],
                        "relation": relation,
                        "confidence": confidence,
                        "source": "co-occurrence",
                    })

        return links

    def _find_proximity_links(
        self, entities: list[dict], text: str
    ) -> list[dict[str, Any]]:
        """Find links based on entity proximity and semantic affinity."""
        links = []

        for i, e1 in enumerate(entities):
            for e2 in entities[i + 1:]:
                # Check if entities are close in text
                distance = abs(e1.get("start", 0) - e2.get("start", 0))
                if distance > 200:  # Too far apart
                    continue

                # Check semantic affinity
                affinity = self._check_affinity(e1["text"], e2["text"])
                if affinity > 0:
                    relation = self._infer_relation(e1, e2, text)
                    links.append({
                        "from_text": e1["text"],
                        "to_text": e2["text"],
                        "relation": relation,
                        "confidence": affinity * 0.6,  # Discount for proximity-based
                        "source": "proximity",
                    })

        return links

    def _check_affinity(self, text1: str, text2: str) -> float:
        """Check semantic affinity between two texts."""
        t1 = text1.lower()
        t2 = text2.lower()

        # Check TECH_AFFINITY
        for tech, keywords in TECH_AFFINITY.items():
            if tech in t1:
                if any(kw in t2 for kw in keywords):
                    return 0.7
            if tech in t2:
                if any(kw in t1 for kw in keywords):
                    return 0.7

        # Check if one contains the other
        if t1 in t2 or t2 in t1:
            return 0.5

        return 0.0

    def _infer_relation(self, e1: dict, e2: dict, context: str) -> str:
        """Infer relationship type between two entities."""
        context_lower = context.lower()
        e1_lower = e1["text"].lower()
        e2_lower = e2["text"].lower()

        # Check context for relationship hints
        if "para" in context_lower or "for" in context_lower:
            return "PARA"
        if "con" in context_lower or "with" in context_lower:
            return "CON"
        if "usando" in context_lower or "using" in context_lower:
            return "USANDO"
        if "inspirado" in context_lower or "basado" in context_lower:
            return "BASADO_EN"
        if "separado" in context_lower or "separate" in context_lower:
            return "SEPARADO_DE"
        if "depende" in context_lower or "requires" in context_lower:
            return "DEPENDE_DE"

        # Default: RELACIONA (generic relationship)
        return "RELACIONA"

    def _score_link(
        self, from_text: str, to_text: str, relation: str, context: str
    ) -> float:
        """Score link confidence."""
        score = 0.5  # Base

        # Boost for explicit relationship words
        explicit_words = {
            "PARA": ["para", "for"],
            "CON": ["con", "with"],
            "USANDO": ["usando", "using"],
        }
        if relation in explicit_words:
            if any(w in context.lower() for w in explicit_words[relation]):
                score += 0.3

        # Boost for known entities
        if any(t in from_text.lower() for t in ["chromadb", "ladybugdb", "python"]):
            score += 0.1
        if any(t in to_text.lower() for t in ["vector", "graph", "search"]):
            score += 0.1

        return min(1.0, score)

    def get_relation_types(self) -> list[str]:
        """Get all supported relationship types."""
        return list(LINK_PATTERNS.keys())
