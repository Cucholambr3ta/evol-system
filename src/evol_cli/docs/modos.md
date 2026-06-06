# Modos de Operación

## Modo COMPLETO

Memoria Persistente instalado y activo (CLI only).

Aporta:
- Indexación semántica del codebase
- Continuidad automática entre sesiones
- Pattern-extraction para evol-evolve
- Recall completo de agentes efímeros

## Modo BASE

Sin Memoria Persistente. Pipeline completo funcional.

Lo que se pierde:
- Continuidad semántica (suplir con memoria.md)
- Búsqueda RAG
- Pattern-extraction automático
- Recall semántico

## Modo Memoria Conversacional (opt-in)

Sistema nativo, stdlib Python, sin dependencias.

Activar: `EVOL_MEMORY=1`

Estructura:
- AGENT_MEMORY.md (long-term)
- memory/YYYY-MM-DD.md (journal diario)
- dialog/ (gitignored)
- tool_result/ (gitignored, TTL 3 días)

## Detección

```bash
bash scripts/evol-doctor.sh  # COMPLETO o BASE
bash scripts/evol-doctor.sh --json  # JSON con mode
```