---
name: evol-deprecation
description: DeprecationDD — Deprecation timelines, migration guides, breaking changes
category: discipline-extended
trigger: /deprecation
---

# evol-deprecation

## Fase del Pipeline

**Plan (Fase 3) — Planificación y Presupuesto**

Activar cuando se necesita gestionar deprecaciones:
- Deprecation timelines
- Migration guides
- Breaking changes management
- Backward compatibility planning

## Artefacto Clave

**`docs/plan/DEPRECATION_PLAN.md`**

```markdown
# Deprecation Plan

## Active Deprecations
| Component | Deprecated In | Remove In | Replacement | Status |
|-----------|---------------|-----------|-------------|--------|
| /api/v1/users | v2.3.0 | v3.0.0 | /api/v2/users | Migration 80% |
| legacy-auth | v2.4.0 | v3.0.0 | oauth2 | In Progress |

## Breaking Changes Timeline
| Version | Breaking Changes | Migration Effort |
|---------|------------------|------------------|
| v3.0.0 | 5 endpoints removed, 2 renamed | Medium |
| v3.1.0 | Config format change | Low |

## Migration Guides
| From | To | Guide | Status |
|------|-----|-------|--------|
| /api/v1/* | /api/v2/* | docs/migration/v1-to-v2.md | Complete |
| basic-auth | oauth2 | docs/migration/auth.md | Draft |

## Breaking Changes Checklist
- [ ] CHANGELOG updated
- [ ] Migration guide published
- [ ] Deprecation warnings in code
- [ ] Support window communicated
- [ ] Monitoring for usage of deprecated APIs
```

## Flujo de Trabajo

```bash
# 1. Detectar deprecaciones pendientes
python3 scripts/deprecation/detect.py \
  --source . \
  --output docs/plan/DEPRECATION_CANDIDATES.md

# 2. Analizar usage de APIs deprecated
python3 scripts/deprecation/analyze-usage.py \
  --apis docs/plan/DEPRECATION_CANDIDATES.md \
  --logs /var/log/api-access.log \
  --output docs/plan/USAGE_REPORT.md

# 3. Generar timeline
python3 scripts/deprecation/generate-timeline.py \
  --candidates docs/plan/DEPRECATION_CANDIDATES.md \
  --output docs/plan/DEPRECATION_PLAN.md

# 4. Crear migration guides
python3 scripts/deprecation/migration-guide.py \
  --from-version 2.x \
  --to-version 3.0 \
  --output docs/migration/v2-to-v3.md

# 5. Agregar deprecation warnings
python3 scripts/deprecation/add-warnings.py \
  --source src/ \
  --deprecations docs/plan/DEPRECATION_PLAN.md

# 6. Validar backward compatibility
python3 scripts/deprecation/validate-compat.py \
  --source src/ \
  --output docs/plan/COMPAT_REPORT.md
```

### Deprecation Warning Pattern

```python
import warnings

def deprecated_endpoint():
    warnings.warn(
        "This endpoint is deprecated since v2.3.0. "
        "Use /api/v2/users instead. "
        "Will be removed in v3.0.0.",
        DeprecationWarning,
        stacklevel=2
    )
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Deprecation awareness | Componentes deprecated conocidos | No |
| Spec | Deprecation design | Nuevos componentes no deprecated | Sí |
| Plan | Deprecation plan | Timeline documentado | Sí |
| Build | Warning injection | Deprecation warnings activos | Sí |
| QA | Migration tested | Migration guides validados | Sí |
| Retro | Deprecation status | Uso de deprecated monitoreado | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Plan del Pipeline
- **Discipline Doc** — `docs/disciplines/DeprecationDD.md`
- **Semantic Versioning** — https://semver.org/
- **API Deprecation Best Practices** — https://blog.developer.atlassian.com/api-deprecation/


## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
