#!/usr/bin/env python3
"""extractor.py — ADD-Only Rule-Based Entity Extraction for Evol-DD Memory v2.0.

Extracts entities from text using regex patterns and dictionaries.
No LLM calls — deterministic, zero-token cost.

Inspired by Mem0's single-pass ADD-only extraction and GBrain's zero-LLM auto-link.

Usage:
    from evol_memory_v2.extractor import EntityExtractor
    extractor = EntityExtractor()
    entities = extractor.extract("Decidimos usar ChromaDB para el vector store")
    # Returns: [{"text": "ChromaDB", "type": "technology", "start": 22, "end": 31}]
"""

import re
from typing import Any


# ── Entity Type Patterns ──────────────────────────────────────────────────

ENTITY_PATTERNS = {
    "technology": [
        # Databases
        r"\b(ChromaDB|LadybugDB|PostgreSQL|Postgres|SQLite|Neo4j|Qdrant|Milvus|Pinecone|Redis|Elasticsearch)\b",
        r"\b(PGLite|pgvector|FAISS|Weaviate)\b",
        # Languages & Frameworks
        r"\b(Python|TypeScript|JavaScript|Rust|Go|Java|React|Vue|Django|FastAPI|Flask|Express)\b",
        r"\b(Tree-sitter|LangChain|LlamaIndex|CrewAI|AutoGen)\b",
        # Tools
        r"\b(ChromaDB|Git|Docker|Kubernetes|Terraform|Ansible|GitHub|GitLab|Jira)\b",
        r"\b(Claude|GPT|LLM|OpenAI|Anthropic|Google|Ollama|LiteLLM)\b",
        # Protocols
        r"\b(MCP|REST|GraphQL|WebSocket|OAuth|JWT|HMAC|SSH|HTTPS)\b",
    ],
    "project": [
        r"\b(Evol-DD|evol-dd|EDMS|EDMS v2|MemPalace|GitNexus|GBrain|Mem0|Letta|Supermemory)\b",
        r"\b([A-Z][a-z]+(?:-[A-Z][a-z]+)+)\b",  # CamelCase with hyphens
    ],
    "concept": [
        r"\b(vector store|knowledge graph|retrieval|embedding|chunking|indexing)\b",
        r"\b(verbatim|ADD-only|auto-link|dream cycle|forgetting|consolidation)\b",
        r"\b(rollback|deployment|pipeline|workflow|orchestration)\b",
        r"\b(security|compliance|governance|audit|privacy)\b",
        r"\b(TDD|BDD|SDD|DDD|FDD|ATDD|SecDD|STDD|RDD)\b",
    ],
    "discipline": [
        r"\b(SDD|FDD|DDD|BDD|ATDD|TDD|STDD|SecDD|RDD|PDD|A11yDD|UXDD|IODD|CDCDD|CCDD|ESDD|APIVDD|ODD|SLO|SLA|EDA|UDD)\b",
    ],
    "agent": [
        r"\b(evol-architect|evol-builder|evol-qa|evol-sec|evol-devops|evol-domain|evol-doc)\b",
        r"\b(evol-ux|evol-data|evol-reviewer|evol-orchestrator|evol-pm|evol-release|evol-analyst)\b",
        r"\b(evol-agent-factory|evol-researcher|evol-auditor|evol-compliance-auditor)\b",
    ],
    "person": [
        # Common Spanish names pattern
        r"\b([A-Z][áéíóúñ][a-z]+(?:\s[A-Z][áéíóúñ][a-z]+)*)\b",
    ],
    "file": [
        r"\b[\w/\\.-]+\.(py|js|ts|tsx|jsx|md|json|yaml|yml|toml|sh)\b",
    ],
    "metric": [
        r"\b(\d+(?:\.\d+)?%)\b",  # Percentages
        r"\b(\d+(?:\.\d+)?x)\b",  # Multipliers
        r"\b(p\d+|p95|p99)\b",  # Latency percentiles
    ],
    "date": [
        r"\b(\d{4}-\d{2}-\d{2})\b",  # ISO dates
        r"\b(Q[1-4]\s?\d{4})\b",  # Quarters
        r"\b(\d{4}-W\d{2})\b",  # ISO weeks
    ],
}

# ── Relationship Patterns ──────────────────────────────────────────────────

RELATIONSHIP_PATTERNS = {
    "DECIDE": [
        r"decid(?:imos|iste?|ió|aron)\s+(?:usar|utilizar|implementar|crear|agregar|eliminar|cambiar|actualizar|mejorar)\s+(.+?)(?:\.|,|$)",
        r"decisión\s+(?:de|para|sobre)\s+(.+?)(?:\.|,|$)",
    ],
    "MENCIONA": [
        r"(?:us(?:ar?|o|amos|ando|é|aste?|ió|aron)|utiliz(?:ar?|o|amos|ando|é|aste?|ió|aron))\s+(.+?)(?:\.|,|para|$)",
        r"(?:con|usando|mediante)\s+(.+?)(?:\.|,|$)",
    ],
    "DEPENDE_DE": [
        r"depend(?:e|emos|ía)\s+de\s+(.+?)(?:\.|,|$)",
        r"(?:requiere?|necesita?|necesitamos)\s+(.+?)(?:\.|,|$)",
    ],
    "INSPIRA_EN": [
        r"inspir(?:ado|ada|ación)\s+en\s+(.+?)(?:\.|,|$)",
        r"(?:bas(?:ado|ada)|inspir(?:ado|ada))\s+en\s+(.+?)(?:\.|,|$)",
    ],
    "IMPLEMENTA": [
        r"implement(?:a(?:mos|ste?)?|ó|aron)\s+(.+?)(?:\.|,|$)",
        r"(?:implement(?:ado|ación)|hecho)\s+(.+?)(?:\.|,|$)",
    ],
}


class EntityExtractor:
    """Rule-based entity extractor with zero LLM cost.

    Extracts entities and relationships from text using regex patterns
    and heuristic scoring. Deterministic and repeatable.
    """

    def __init__(self, custom_patterns: dict[str, list[str]] | None = None):
        """Initialize extractor.

        Args:
            custom_patterns: Additional entity patterns to merge with defaults
        """
        self._patterns = {**ENTITY_PATTERNS}
        if custom_patterns:
            for etype, patterns in custom_patterns.items():
                if etype in self._patterns:
                    self._patterns[etype].extend(patterns)
                else:
                    self._patterns[etype] = patterns

        # Pre-compile patterns
        self._compiled = {}
        for etype, patterns in self._patterns.items():
            self._compiled[etype] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

        # Compile relationship patterns
        self._rel_compiled = {}
        for rtype, patterns in RELATIONSHIP_PATTERNS.items():
            self._rel_compiled[rtype] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def extract(self, text: str) -> list[dict[str, Any]]:
        """Extract entities from text.

        Args:
            text: Input text to extract from

        Returns:
            List of entity dicts with keys: text, type, start, end, confidence
        """
        if not text:
            return []

        entities = []
        seen = set()

        for etype, patterns in self._compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    entity_text = match.group(1) if match.lastindex else match.group(0)
                    entity_text = entity_text.strip()

                    # Dedup by (text, type)
                    key = (entity_text.lower(), etype)
                    if key in seen:
                        continue
                    seen.add(key)

                    # Skip very short entities
                    if len(entity_text) < 2:
                        continue

                    # Score confidence
                    confidence = self._score_entity(entity_text, etype, text)

                    entities.append({
                        "text": entity_text,
                        "type": etype,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": confidence,
                    })

        return entities

    def extract_relationships(self, text: str) -> list[dict[str, Any]]:
        """Extract relationships from text.

        Args:
            text: Input text

        Returns:
            List of relationship dicts with keys: type, subject, object, confidence
        """
        if not text:
            return []

        relationships = []

        for rtype, patterns in self._rel_compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    object_text = match.group(1) if match.lastindex else match.group(0)
                    object_text = object_text.strip()

                    if len(object_text) < 2:
                        continue

                    relationships.append({
                        "type": rtype,
                        "object": object_text,
                        "confidence": 0.7,  # Base confidence for regex matches
                        "span": text[match.start():match.end()],
                    })

        return relationships

    def extract_all(self, text: str) -> dict[str, Any]:
        """Extract both entities and relationships.

        Args:
            text: Input text

        Returns:
            Dict with 'entities' and 'relationships' lists
        """
        return {
            "entities": self.extract(text),
            "relationships": self.extract_relationships(text),
        }

    def _score_entity(
        self, entity_text: str, entity_type: str, context: str
    ) -> float:
        """Score entity confidence based on heuristics.

        Args:
            entity_text: Entity text
            entity_type: Entity type
            context: Full text context

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.5  # Base score

        # Boost for known technologies
        if entity_type == "technology":
            known_techs = {
                "chromadb", "ladybugdb", "postgres", "sqlite", "python",
                "typescript", "rust", "docker", "git", "claude", "gpt",
            }
            if entity_text.lower() in known_techs:
                score += 0.3

        # Boost for known disciplines
        if entity_type == "discipline":
            known_disciplines = {"sdd", "fdd", "ddd", "bdd", "tdd", "secdd", "rdd"}
            if entity_text.lower() in known_disciplines:
                score += 0.3

        # Boost for known agents
        if entity_type == "agent":
            if entity_text.startswith("evol-"):
                score += 0.3

        # Boost for entities that appear multiple times
        count = context.lower().count(entity_text.lower())
        if count > 1:
            score += min(0.2, count * 0.05)

        # Boost for capitalized entities (proper nouns)
        if entity_text[0].isupper():
            score += 0.1

        return min(1.0, score)

    def get_entity_types(self) -> list[str]:
        """Get all supported entity types."""
        return list(self._patterns.keys())

    def get_relationship_types(self) -> list[str]:
        """Get all supported relationship types."""
        return list(RELATIONSHIP_PATTERNS.keys())
