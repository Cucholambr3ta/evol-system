# RNF-01 — Fallback stdlib

**Estado:** Aprobado | **Prioridad:** Alta

## Descripción

Sin ChromaDB/LadybugDB instaladas, BM25 stdlib sigue funcionando.

## Validación

```bash
pip uninstall chromadb ladybugdb
evol-memory search "gate HMAC" --proyecto=evol-dd
# Debe retornar resultados via BM25 stdlib, sin error
```

## Implementación

```python
# evol_memory_store.py
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
```
