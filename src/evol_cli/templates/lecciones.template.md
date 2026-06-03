# lecciones.md — Aprendizajes Acumulados

> Lecciones aprendidas del proyecto. Indexado por MemPalace. Consultado por agentes antes de proponer soluciones para evitar repetir errores (Constitución Art. 9).
> Actualizado vía `/cierre-fase` al final de cada fase.

## Formato
Cada lección sigue la estructura:
```
### [CATEGORÍA] Título breve — YYYY-MM-DD
**Contexto:** Qué estábamos intentando hacer.
**Problema:** Qué falló o sorprendió.
**Causa raíz:** Por qué pasó.
**Lección:** Regla aplicable a futuras decisiones.
**Aplica a:** Ámbito (módulo X, todo el proyecto, stack Y…).
**Fix aplicado:** Qué se hizo para resolver. (opcional)
**Mejoras sugeridas:** Propuestas del investigador para evolución futura. (opcional)
**Estado mejoras:** pendiente | en-progreso | aplicado (opcional)
```

Categorías sugeridas: `ARQUITECTURA`, `SEGURIDAD`, `DOMINIO`, `TESTING`, `DEVOPS`, `PROCESO`, `HERRAMIENTAS`.

Motor nativo disponible en `scripts/evol-lessons.py`:
- `evol-lessons add` — añadir lección con deduplicación fuzzy
- `evol-lessons suggest-fix "titulo"` — investigador propone mejoras
- `evol-lessons apply-fix "titulo" --fix "descripcion"` — marcar mejoras aplicadas
- `evol-lessons search QUERY` — buscar antes de decidir (Art. 9)
- `evol-lessons list --pendientes` — lecciones con mejoras pendientes
- `evol-lessons stats` — total, por categoría, mejoras pendientes/aplicadas

---

## Lecciones

_(vacío — añadir entradas vía `/cierre-fase`)_
