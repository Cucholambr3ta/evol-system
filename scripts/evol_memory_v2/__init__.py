"""evol_memory_v2 — Memory Architecture v2.0 for Evol-DD.

Inspired by: MemPalace (verbatim), GBrain (auto-link), Mem0 (ADD-only),
Letta (progressive disclosure), Supermemory (forgetting), GitNexus (precomputed).

Components:
    - store: Verbatim storage with SHA-256 integrity
    - extractor: ADD-only rule-based entity extraction
    - auto_linker: Zero-LLM relationship builder
    - entity_store: Centralized entity storage with merge
    - compat: Compatibility layer over EDMS v1
"""

__version__ = "2.0.0"
