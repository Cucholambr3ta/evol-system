"""
Graph-based query expander for EDMS Memory v2.0.

Expands queries using knowledge graph relationships to improve recall.
Traverses graph to find related terms and concepts.

Part of EDMS Memory v2.0 Phase 2 - Hybrid Retrieval.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GraphNode:
    """Node in the knowledge graph."""
    id: str
    name: str
    type: str  # "technology", "concept", "discipline", "agent", etc.
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Edge in the knowledge graph."""
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)


class GraphExpander:
    """
    Graph-based query expander.

    Expands search queries using knowledge graph relationships.
    Traverses graph to find related terms and concepts.

    Usage:
        expander = GraphExpander()
        expander.add_node("ChromaDB", "technology")
        expander.add_edge("ChromaDB", "vector search", "ENABLES")

        expanded = expander.expand("ChromaDB")
        # Returns: ["ChromaDB", "vector search", ...]
    """

    def __init__(self, max_depth: int = 2, max_expansions: int = 10):
        self.max_depth = max_depth
        self.max_expansions = max_expansions

        # Adjacency list: node_id -> [(target_id, relation, weight)]
        self._adjacency: dict[str, list[tuple[str, str, float]]] = defaultdict(list)

        # Reverse adjacency: target_id -> [(source_id, relation, weight)]
        self._reverse: dict[str, list[tuple[str, str, float]]] = defaultdict(list)

        # Nodes: node_id -> GraphNode
        self._nodes: dict[str, GraphNode] = {}

        # Name -> ID mapping (case-insensitive)
        self._name_to_id: dict[str, str] = {}

    def add_node(
        self,
        name: str,
        node_type: str = "concept",
        properties: dict[str, Any] | None = None,
    ) -> str:
        """
        Add a node to the graph.

        Args:
            name: Node name (e.g., "ChromaDB")
            node_type: Node type (e.g., "technology")
            properties: Optional properties

        Returns:
            Node ID
        """
        node_id = name.lower().replace(" ", "_")
        node = GraphNode(
            id=node_id,
            name=name,
            type=node_type,
            properties=properties or {},
        )
        self._nodes[node_id] = node
        self._name_to_id[name.lower()] = node_id
        return node_id

    def add_edge(
        self,
        source_name: str,
        target_name: str,
        relation: str,
        weight: float = 1.0,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """
        Add an edge to the graph.

        Args:
            source_name: Source node name
            target_name: Target node name
            relation: Edge relation (e.g., "ENABLES", "USES")
            weight: Edge weight (default 1.0)
            properties: Optional properties
        """
        source_id = self._name_to_id.get(source_name.lower(), source_name.lower().replace(" ", "_"))
        target_id = self._name_to_id.get(target_name.lower(), target_name.lower().replace(" ", "_"))

        # Add nodes if they don't exist
        if source_id not in self._nodes:
            self.add_node(source_name)
        if target_id not in self._nodes:
            self.add_node(target_name)

        # Add edges (bidirectional)
        self._adjacency[source_id].append((target_id, relation, weight))
        self._reverse[target_id].append((source_id, relation, weight))

    def expand(self, query: str) -> list[str]:
        """
        Expand a query using graph relationships.

        Args:
            query: Search query to expand

        Returns:
            List of expanded terms (original + related)
        """
        # Find starting nodes that match the query
        starting_nodes = self._find_matching_nodes(query)
        if not starting_nodes:
            return [query]

        # BFS to find related terms
        expanded = set()
        queue = [(node_id, 0) for node_id in starting_nodes]
        visited = set()

        while queue and len(expanded) < self.max_expansions:
            node_id, depth = queue.pop(0)

            if node_id in visited:
                continue
            visited.add(node_id)

            # Add node name to expanded set
            if node_id in self._nodes:
                expanded.add(self._nodes[node_id].name.lower())

            # Stop if max depth reached
            if depth >= self.max_depth:
                continue

            # Traverse outgoing edges
            for target_id, relation, weight in self._adjacency.get(node_id, []):
                if target_id not in visited:
                    queue.append((target_id, depth + 1))

            # Traverse incoming edges
            for source_id, relation, weight in self._reverse.get(node_id, []):
                if source_id not in visited:
                    queue.append((source_id, depth + 1))

        # Combine original query with expanded terms
        original_terms = query.lower().split()
        all_terms = list(expanded) + original_terms

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for term in all_terms:
            if term not in seen:
                seen.add(term)
                result.append(term)

        return result

    def _find_matching_nodes(self, query: str) -> list[str]:
        """Find nodes matching the query."""
        matching = []
        query_lower = query.lower()

        # Exact name match
        if query_lower in self._name_to_id:
            matching.append(self._name_to_id[query_lower])

        # Partial match (substring)
        for name, node_id in self._name_to_id.items():
            if query_lower in name or name in query_lower:
                if node_id not in matching:
                    matching.append(node_id)

        return matching

    def get_related(self, node_name: str) -> list[tuple[str, str, float]]:
        """
        Get all related nodes for a given node.

        Args:
            node_name: Name of the node

        Returns:
            List of (related_name, relation, weight) tuples
        """
        node_id = self._name_to_id.get(node_name.lower(), node_name.lower().replace(" ", "_"))
        if node_id not in self._adjacency:
            return []

        related = []
        for target_id, relation, weight in self._adjacency[node_id]:
            if target_id in self._nodes:
                related.append((self._nodes[target_id].name, relation, weight))

        return related

    def get_node(self, name: str) -> GraphNode | None:
        """Get node by name."""
        node_id = self._name_to_id.get(name.lower())
        return self._nodes.get(node_id)

    def stats(self) -> dict[str, Any]:
        """Get graph statistics."""
        return {
            "nodes": len(self._nodes),
            "edges": sum(len(edges) for edges in self._adjacency.values()),
            "node_types": self._count_node_types(),
            "relation_types": self._count_relation_types(),
        }

    def _count_node_types(self) -> dict[str, int]:
        """Count nodes by type."""
        counts = defaultdict(int)
        for node in self._nodes.values():
            counts[node.type] += 1
        return dict(counts)

    def _count_relation_types(self) -> dict[str, int]:
        """Count edges by relation type."""
        counts = defaultdict(int)
        for edges in self._adjacency.values():
            for _, relation, _ in edges:
                counts[relation] += 1
        return dict(counts)

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save graph to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.type,
                    "properties": node.properties,
                }
                for node in self._nodes.values()
            ],
            "edges": [],
        }

        # Collect unique edges
        seen_edges = set()
        for source_id, edges in self._adjacency.items():
            for target_id, relation, weight in edges:
                edge_key = (source_id, target_id, relation)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    data["edges"].append({
                        "source": source_id,
                        "target": target_id,
                        "relation": relation,
                        "weight": weight,
                    })

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> GraphExpander:
        """Load graph from JSON file."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        expander = cls()

        # Load nodes
        for node_data in data.get("nodes", []):
            expander.add_node(
                name=node_data["name"],
                node_type=node_data.get("type", "concept"),
                properties=node_data.get("properties", {}),
            )

        # Load edges
        for edge_data in data.get("edges", []):
            # Get source and target names from node IDs
            source_node = expander._nodes.get(edge_data["source"])
            target_node = expander._nodes.get(edge_data["target"])

            source_name = source_node.name if source_node else ""
            target_name = target_node.name if target_node else ""

            if source_name and target_name:
                expander.add_edge(
                    source_name=source_name,
                    target_name=target_name,
                    relation=edge_data.get("relation", "RELATED_TO"),
                    weight=edge_data.get("weight", 1.0),
                )

        return expander
