# RF-05 — Privacy Stripping

**Estado:** Aprobado | **Prioridad:** Crítica | **Esfuerzo:** Bajo

## Descripción

Eliminar API keys, tokens, passwords, PII antes de indexar. 11 patrones regex.

## Criterios de aceptación

- [ ] `privacy_strip(text)` elimina: sk-*, ghp_*, passwords, <private>, gate keys (32+ chars)
- [ ] Reemplaza por `[REDACTED_*]`
- [ ] Se ejecuta ANTES de cualquier insert en ChromaDB/LadybugDB
- [ ] 11 patrones cubiertos (ver plan §6)
- [ ] Test con cada patrón individual

## Dependencias

- Ninguna

## Archivos

- `scripts/evol_memory_store.py` → `privacy_strip()`
- `tests/test_memory_store.py::test_privacy_strip`
