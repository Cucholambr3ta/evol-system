---
name: evol-odd-api
description: OpenAPI-Driven Development. Genera y valida el contrato OpenAPI 3.1 desde SPEC.md, garantizando spec-first y sin breaking changes no planificados.
category: discipline-extended
trigger: /odd-api
---

# evol-odd-api

## Fase del Pipeline
Spec (Fase 2)

## Artefacto Clave
`api/openapi.yaml`

## Flujo de Trabajo

### 1. Derivar contrato desde SPEC.md + DOMAIN.md
```bash
# Leer REQ-NNN y dominio para generar schemas
evol-odd-api derive --spec=docs/specs/SPEC.md --domain=docs/specs/DOMAIN.md --output=api/openapi.yaml
```

### 2. Validar especificacion OpenAPI
```bash
# Validar sintaxis y estructura
npx @redocly/cli lint api/openapi.yaml

# Validar contra el estandar OpenAPI 3.1
npx openapi-spec-validator api/openapi.yaml
```

### 3. Detectar breaking changes contra version anterior
```bash
# Diff entre version actual y anterior del contrato
evol-odd-api breaking-check --current=api/openapi.yaml --previous=api/openapi_v1.yaml

# Reporte de cambios para el gate
evol-odd-api diff-report --current=api/openapi.yaml --previous=api/openapi_v1.yaml --output=.evol/odd-api/diff.json
```

### 4. Generar fragmentos reutilizables
```bash
# Extraer schemas comunes para ahorrar tokens en LLMs
evol-odd-api fragment --input=api/openapi.yaml --output=api/fragments/
```

### 5. Generar stubs de servidor y cliente
```bash
# Generar stubs desde el contrato
evol-odd-api stubs --input=api/openapi.yaml --output=src/api/stubs/ --lang=typescript
```

## Formato Contrato OpenAPI

```yaml
openapi: "3.1.0"
info:
  title: "[Proyecto] API"
  version: "1.0.0"
  description: "Contrato generado desde SPEC.md"
paths:
  /usuarios/{id}:
    get:
      operationId: getUsuario
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: "Usuario encontrado"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Usuario"
              examples:
                default:
                  value:
                    id: "usr_001"
                    nombre: "Ana Garcia"
components:
  schemas:
    Usuario:
      type: object
      required: [id, nombre]
      properties:
        id:
          type: string
        nombre:
          type: string
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Spec | Derivar openapi.yaml desde REQ-NNN; validar schema |
| Plan | Tareas del plan referencian operaciones del contrato |
| Build | Implementar endpoints contra el contrato; generar stubs |
| QA | Verificar conformidad servidor vs contrato |
| Gate | Bloquea si el contrato es invalido o tiene breaking changes sin plan |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/ODD_API.md`
- [OpenAPI Specification 3.1](https://spec.openapis.org/oas/latest.html)
- [OpenAPI-Driven Development — Stoplight](https://stoplight.io/openapi/guides/openapi-driven-development)


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
