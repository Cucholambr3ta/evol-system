# Audit Template — Doc Granular
# Extiende audit-base.md con checks para la fase de documentacion atomica.

## HEREDA: templates/audit/audit-base.md

---

## Checklist Especifico — Fase: Doc Granular

### F. Atomicidad Documental

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| F1 | 1 carpeta = 1 dominio tecnico | `[ ]` | Sin mezcla de dominios en misma carpeta |
| F2 | 1 documento = 1 subdominio/concepto | `[ ]` | Sin documentos "todo en uno" |
| F3 | Cada carpeta tiene `INDEX.md` | `[ ]` | Tabla: Documento, Resumen, Trazabilidad |
| F4 | Cada carpeta tiene `INDEX.json` | `[ ]` | `evol-doc-sync.py sync-folder <dir>` |

### G. Contenido por Documento

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| G1 | Cada `.md` tiene seccion de Fuentes con URLs | `[ ]` | DOC_STANDARD 1.7 |
| G2 | Diagramas Mermaid donde aplique | `[ ]` | Obligatorio en arquitectura/flujos |
| G3 | Tablas para datos estructurados | `[ ]` | No listas cuando deberia ser tabla |
| G4 | Trazabilidad bidireccional con requisitos | `[ ]` | Links a FUNCIONALES.md |

### H. Sidecars JSON

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| H1 | Sidecar `.json` generado por cada `.md` | `[ ]` | `evol-doc-sync.py` |
| H2 | `checksum_md` sincronizado en cada sidecar | `[ ]` | No hay drift |
| H3 | `fuentes[]` en sidecar captura URLs del `.md` | `[ ]` | `_extract_sources()` |
| H4 | `INDEX.json` maestro actualizado | `[ ]` | |

---

## Puntos Ciegos Especificos — Doc Granular

1. **Documentos huerfanos:** Hay `.md` sin referencia en ningun `INDEX.md`?
   `find docs/ -name "*.md" | xargs grep -L "INDEX"`
2. **Sidecars desincronizados:** `validate-disciplinas.py --strict` falla?
3. **Dominios sin cubrir:** El briefing menciona dominios que no tienen carpeta?
4. **Fuentes vacias:** `grep -r '"fuentes": \[\]' docs/` — disciplinas sin fuentes.
