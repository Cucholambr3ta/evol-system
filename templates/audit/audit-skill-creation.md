# Audit Template — Skill Creation
# Extiende audit-base.md con checks para la creacion de una nueva skill.

## HEREDA: templates/audit/audit-base.md

---

## Checklist Especifico — Fase: Creacion de Skill

### F. Estructura de la Skill

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| F1 | Carpeta en `skills/<nombre>/` | `[ ]` | Nombre en kebab-case |
| F2 | `SKILL.md` con frontmatter valido | `[ ]` | name, description, triggers |
| F3 | Descripcion del frontmatter activa el triggering correcto | `[ ]` | Clara y especifica |
| F4 | Sin emojis en ningun archivo de la skill | `[ ]` | |

### G. Evaluaciones

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| G1 | `evals/evals.json` creado con >= 3 casos | `[ ]` | |
| G2 | `evals/cases.jsonl` con casos de prueba | `[ ]` | |
| G3 | Loop eval ejecutado (score >= 0.7) | `[ ]` | |

### H. Sincronizacion

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| H1 | Copiada a `src/evol_cli/skills/<nombre>/` | `[ ]` | Mirror obligatorio |
| H2 | `evol-adapt.sh` ejecutado para portar a 7 IDEs | `[ ]` | |
| H3 | `validate-registry.py` no reporta la skill como faltante | `[ ]` | |

---

## Puntos Ciegos Especificos — Skill Creation

1. **Skill duplicada:** Ya existe una skill similar? Verificar `skills/` antes de crear.
2. **Triggering vago:** La descripcion del frontmatter es suficientemente especifica para activarse sin ambiguedad?
3. **Sin casos negativos:** Los evals incluyen casos donde la skill NO deberia activarse?
4. **Mirror olvidado:** `src/evol_cli/skills/` tiene la copia actualizada?
