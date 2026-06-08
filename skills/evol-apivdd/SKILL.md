---
name: evol-apivdd
description: API Versioning-Driven Development. Detecta breaking changes, genera calendarios de deprecacion, y planes de migracion entre versiones de API.
category: discipline-extended
trigger: /apivdd
---

# evol-apivdd

## Fase del Pipeline
Plan (Fase 3)

## Artefacto Clave
`docs/plan/API_VERSIONING.md`

## Flujo de Trabajo

### 1. Detectar breaking changes entre versiones
```bash
# Comparar contratos versionados
evol-apivdd detect --current=api/openapi.yaml --previous=api/openapi_v1.yaml --output=api_versions/breaking_changes/

# Generar reporte de cambios
evol-apivdd diff --current=api/openapi.yaml --previous=api/openapi_v1.yaml --output=api_versions/diff_report.json
```

### 2. Generar calendario de deprecacion
```bash
# Generar schedule desde breaking changes
evol-apivdd deprecation-schedule --breaking=api_versions/breaking_changes/ --output=api_versions/deprecation_schedule.json

# Calcular fecha minima de deprecation (min 90 dias)
evol-apivdd validate-schedule --schedule=api_versions/deprecation_schedule.json --min-days=90
```

### 3. Generar guias de migracion
```bash
# Para cada breaking change, generar guia de migracion
evol-apivdd migration-guide --breaking=api_versions/breaking_changes/ --output=api_versions/breaking_changes/

# Ejemplo: breaking change en nombre de campo
# Antes: { "usuario_id": "usr_001" }
# Despues: { "userId": "usr_001" }
```

### 4. Generar reporte de versioning
```bash
evol-apivdd report --breaking=api_versions/breaking_changes/ --schedule=api_versions/deprecation_schedule.json --output=docs/plan/API_VERSIONING.md
```

## Formato Breaking Change

```markdown
# Breaking Change — BC-001

**Tipo:** Renombrado de campo
**Endpoint:** GET /api/usuarios
**Campo:** `usuario_id` -> `userId`
**Impacto:** Todos los consumidores que usan `usuario_id`

## Impacto en Consumidores
- Frontend: requiere cambio en 3 componentes
- Movil: requiere cambio en 2 pantallas

## Plan de Migracion
1. Publicar nueva version v2 con campo `userId`
2. Mantener `usuario_id` deprecated por 90 dias
3. Headers `Deprecation: true` y `Sunset: 2026-09-05`
4. Eliminar campo en v3
```

## Formato deprecation_schedule.json

```json
{
  "version_from": "v1",
  "version_to": "v2",
  "breaking_changes": [
    {
      "id": "BC-001",
      "description": "Renombrado usuario_id -> userId",
      "deprecation_date": "2026-06-07",
      "sunset_date": "2026-09-05",
      "migration_guide": "api_versions/breaking_changes/BC-001.md"
    }
  ],
  "headers": {
    "Deprecation": "true",
    "Sunset": "Sat, 05 Sep 2026 00:00:00 GMT",
    "Link": "<https://docs.api.com/migration/v2>; rel=\"successor-version\""
  }
}
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Plan | Definir estrategia de versionado + calendario de deprecacion |
| Build | Implementar versiones conviviendo + headers de deprecacion |
| QA | Verificar que ningun breaking change carece de plan |
| Gate | Bloquea si hay breaking change sin plan de migracion |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/APIVDD.md`
- [Semantic Versioning 2.0.0](https://semver.org/)
- [RFC 8594 — The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594)
- [API Versioning Strategies — API7](https://api7.ai/blog/api-versioning-strategies)


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
