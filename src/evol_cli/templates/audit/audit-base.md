# Audit Template — Base
# Todas las fases heredan este template. Cada fase extiende con su checklist especifico.

## Contexto de Auditoria

**Fase auditada:** {{FASE}}
**Timestamp:** {{ISO8601}}
**Auditor:** evol-auditor-{{FASE}}-{{TIMESTAMP}}
**Version del sistema:** {{VERSION}}

---

## Checklist Universal (todas las fases)

El auditor verifica estos items en CUALQUIER flujo antes de los checks especificos de fase.

### A. Contratos de Documentacion

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| A1 | Todo `.md` nuevo tiene su sidecar `.json` generado | `[ ]` | `evol-doc-sync.py sync-folder <dir>` |
| A2 | Ningun documento nuevo contiene emojis | `[ ]` | `grep -rE "[\\x{1F300}-\\x{1F9FF}]"` |
| A3 | Cada seccion de documentacion tiene Fuentes con URLs | `[ ]` | DOC_STANDARD 1.7 |
| A4 | Diagramas Mermaid usan `<br/>` no `\n` en labels | `[ ]` | Ver lecciones.md |

### B. Memoria Persistente

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| B1 | `acuerdos/memoria/decisiones.md` refleja decisiones de esta fase | `[ ]` | |
| B2 | `acuerdos/memoria/convenciones.md` refleja nuevas convenciones | `[ ]` | |
| B3 | `acuerdos/memoria/riesgos.md` tiene riesgos mitigados/nuevos | `[ ]` | |
| B4 | `MEMORY.md` agregado regenerado via `memory-split` | `[ ]` | |
| B5 | `lecciones.md` tiene lecciones de esta sesion | `[ ]` | |

### C. Directorios de Runtime

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| C1 | `memory/` existe con permisos `750` | `[ ]` | Creado por `evol-init.sh` |
| C2 | `.evol/` existe con `.gate-key` y `.gate-log.jsonl` | `[ ]` | |
| C3 | `acuerdos/auditoria/` existe para historial | `[ ]` | |

### D. Skills y Capacidades

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| D1 | No hay tareas repetitivas sin skill asociada | `[ ]` | SKILL_MISSING si aplica |
| D2 | Skills nuevas tienen eval en `evals/` | `[ ]` | |
| D3 | Skills nuevas sincronizadas a `src/evol_cli/skills/` | `[ ]` | |

### E. GitFlow y Versionamiento

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| E1 | Commits siguen Conventional Commits | `[ ]` | `feat:`, `fix:`, `docs:`, etc. |
| E2 | `VERSION` y `pyproject.toml` sincronizados | `[ ]` | |
| E3 | `CHANGELOG.md` actualizado antes del tag | `[ ]` | |

---

## Puntos Ciegos Sugeridos (revisar en cada auditoria)

El auditor SIEMPRE verifica estos puntos ciegos comunes del sistema:

1. **JSON sidecars:** Se generaron documentos `.md` sin su sidecar `.json`?
   Comando: `find <dir> -name "*.md" | while read f; do [ ! -f "${f%.md}.json" ] && echo "FALTANTE: $f"; done`

2. **Skills faltantes:** Hay acciones repetidas manualmente que deberian ser skills?
   Patron: Si una accion se ejecuta >2 veces en una sesion, proponer skill.

3. **Memoria desactualizada:** El estado de `acuerdos/memoria/` refleja la realidad post-fase?

4. **Lecciones no registradas:** Hubo bloqueos, conflictos o bugs? Estan en `lecciones.md`?

5. **Docs sin INDEX.json:** Carpetas nuevas sin su `INDEX.json` de tokens.

---

## Formato de Hallazgo

```markdown
### [TIPO] Titulo del hallazgo

**Tipo:** GAP | BLIND_SPOT | SKILL_MISSING | OK
**Severidad:** CRITICAL | HIGH | MEDIUM | LOW
**Contexto:** Donde ocurre (archivo, fase, comando).
**Descripcion:** Que falla o que falta exactamente.
**Accion sugerida:** Comando o paso concreto para resolverlo.
**Leccion generada:** Si/No — texto de la leccion.
```

---

## Resumen Ejecutivo (al final)

```markdown
## Resumen Auditoria {{FASE}} — {{ISO8601}}

- Items auditados: N
- OK: N | GAP: N | BLIND_SPOT: N | SKILL_MISSING: N
- Skills propuestas: [lista]
- Lecciones registradas: N
- Estado general: APROBADO | OBSERVACIONES | BLOQUEADO
```
