# Audit Template — Sprint
# Extiende audit-base.md con checks especificos del ciclo de sprint.

## HEREDA: templates/audit/audit-base.md

---

## Checklist Especifico — Fase: Sprint

### F. Historias y Checklist

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| F1 | Todas las historias del sprint tienen 4 artefactos | `[ ]` | propuesta, requisitos, escenario-tecnico, checklist-tareas |
| F2 | Todos los checks de `checklist-tareas.md` estan en `[x]` | `[ ]` | Ningun `[ ]` pendiente |
| F3 | Tests TDD escritos ANTES de la implementacion | `[ ]` | Orden Rojo→Verde→Refactor |

### G. Calidad del Codigo

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| G1 | `pytest tests/ -v` 100% verde | `[ ]` | |
| G2 | Cobertura de tests >= 80% | `[ ]` | |
| G3 | `evol-shield.py audit --ci` 0 CRITICAL | `[ ]` | |
| G4 | Escenarios Gherkin ejecutados y verdes | `[ ]` | |

### H. Subagentes

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| H1 | Equipo dinamico registrado en `acuerdos/memoria/sprint-NN.md` | `[ ]` | |
| H2 | Audit pass-rate de workers >= 70% | `[ ]` | Desde lecciones del sprint |
| H3 | `evol-eval.py run subagent-performance` con score OK | `[ ]` | |

### I. Cierre

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| I1 | `evol-gitflow.sh sprint-close --sprint=NN` ejecutado | `[ ]` | |
| I2 | `acuerdos/lecciones/sprint-NN.md` creado con lecciones reales | `[ ]` | |
| I3 | `evol-gate.py approve --phase build` aprobado | `[ ]` | |

---

## Puntos Ciegos Especificos — Sprint

1. **Tareas sin test:** Hay implementaciones sin test unitario asociado?
2. **Lecciones vacias:** `acuerdos/lecciones/sprint-NN.md` tiene contenido real o esta en blanco?
3. **Skills no propuestas:** El auditor detecto SKILL_MISSING pero no se propuso la skill?
4. **JSON sidecars:** Documentos nuevos en `acuerdos/historia-usuario-N/` tienen su `.json`?
5. **Workers sin retire:** Subagentes efimeros del sprint fueron retirados?
