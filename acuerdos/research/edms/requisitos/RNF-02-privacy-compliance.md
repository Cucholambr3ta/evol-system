# RNF-02 — Privacy Compliance

**Estado:** Aprobado | **Prioridad:** Crítica

## Descripción

Ningún secret debe llegar a ChromaDB o LadybugDB.

## Validación

```python
def test_no_secrets_in_chromadb():
    """Ningún sk-*, ghp_*, o password debe persistirse."""
    text = "API key: sk-123456789012345678901234567890123456789012345678"
    store.index(text, {"tipo": "artefacto"})
    results = store.search("sk-", raw=True)
    assert not any("sk-" in r["text"] for r in results)
```

## Patrones cubiertos

| # | Patrón | Ejemplo |
|---|--------|---------|
| 1 | `sk-*` (48 chars) | OpenAI API key |
| 2 | `ghp_*` (36 chars) | GitHub token |
| 3 | `password[=:\s]+*` | Passwords en config |
| 4 | `<private>.*</private>` | Tags privados |
| 5 | Gate keys (32+ chars) | HMAC keys |
