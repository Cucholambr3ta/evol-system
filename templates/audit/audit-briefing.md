# Audit Template — Briefing
# Extiende audit-base.md con checks especificos de la fase Briefing.

## HEREDA: templates/audit/audit-base.md

---

## Checklist Especifico — Fase: Briefing

### F. Atomos de Idea

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| F1 | `acuerdos/idea/INDEX.md` existe y tiene los 14 atomos | `[ ]` | Checklist de atomos completos |
| F2 | Cada atomo tiene su sidecar `.json` | `[ ]` | `evol-doc-sync.py sync-folder acuerdos/idea/` |
| F3 | Ningun atomo contiene emojis | `[ ]` | DOC_STANDARD sin emojis |

### G. Discovery

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| G1 | `acuerdos/discovery/` tiene al menos 1 tema investigado | `[ ]` | Fuentes citadas |
| G2 | Investigacion tiene fuentes con URLs reales | `[ ]` | DOC_STANDARD 1.7 |
| G3 | Hallazgos son accionables (no solo resumen) | `[ ]` | Cada hallazgo → implicacion |

### H. Diseño

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| H1 | Wireframes o prototipos existen si aplica | `[ ]` | `acuerdos/design/` |
| H2 | Diagrama de arquitectura de alto nivel existe | `[ ]` | Mermaid o аналогичный |
| H3 | Decisiones de diseño registradas en `acuerdos/memoria/decisiones.md` | `[ ]` | |

### I. Validacion

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| I1 | Briefing aprobado por usuario antes de avanzar a Spec | `[ ]` | Gate HMAC o confirmacion explicita |
| I2 | Alcance definido (que SÍ y que NO se hace) | `[ ]` | En el briefing o en documento aparte |

---

## Puntos Ciegos Especificos — Briefing

1. **Atomos faltantes:** El INDEX.md declara 14 atomos pero faltan archivos?
2. **Discovery sin fuentes:** Investigacion basada en opiniones, no en fuentes verificables?
3. **Briefing vago:** El briefing no define criterios de exito medibles?
4. **Decisiones no registradas:** Se tomaron decisiones de diseño que no estan en `decisiones.md`?
5. **Scope creep detectado:** El briefing incluye features que no estaban en la idea original?
