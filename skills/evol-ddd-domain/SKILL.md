---
name: evol-ddd-domain
description: Domain-Driven Design. Modela el dominio del negocio con Ubiquitous Language, Bounded Contexts, Aggregates y Domain Events en DOMAIN.md.
category: discipline-base
trigger: /ddd
---

# evol-ddd-domain

## Fase del Pipeline
Spec (Fase 2)

## Artefacto Clave
`docs/specs/DOMAIN.md`

## Flujo de Trabajo

### 1. Identificar Bounded Contexts
```bash
# Analizar el modelo de negocio para identificar limites
evol-ddd identify-contexts --from=docs/features/FEATURES.md

# Generar diagrama de bounded contexts
evol-ddd context-map --output=docs/specs/context-map.mermaid
```

### 2. Definir Ubiquitous Language
```bash
# Crear glosario de terminos del negocio
evol-ddd ubiquitous-language --export=domain

# Validar coherencia del vocabulario
evol-ddd validate-vocab --against=docs/specs/SPEC.md
```

### 3. Modelar Core Aggregates
```bash
# Identificar aggregates y sus invariantes
evol-ddd model-aggregates --from=domain-events

# Generar diagrama de clases
evol-ddd class-diagram --output=docs/specs/class-diagram.mermaid
```

### 4. Documentar Domain Events
```bash
# Catalogar eventos de dominio
evol-ddd catalog-events --emitters=aggregates

# Validar dependencias entre eventos
evol-ddd validate-events --check-dependencies
```

### 5. Generar DOMAIN.md
```bash
# Compilar artefacto final
evol-ddd compile --output=docs/specs/DOMAIN.md

# Validar contra DOC_STANDARD v2.0
evol-ddd validate --standard=DOC_STANDARD
```

## Formato DOMAIN.md

```markdown
## Ubiquitous Language
| Termino | Definicion precisa | Sinonimos prohibidos | Contexto |
|---------|--------------------|---------------------|----------|
| Periodo de Facturacion | Intervalo de tiempo por el que se calcula el cargo | "mes", "ciclo" | Facturacion |

## Bounded Contexts
[Descripcion narrativa + diagrama Mermaid flowchart]

## Context Map
[Diagrama Mermaid con tipos de relacion]

## Core Aggregates
| Aggregate Root | Invariantes | Entidades | Value Objects | Repository |
|----------------|-------------|-----------|---------------|------------|
| `Factura` | El total nunca puede ser negativo | `LineaFactura` | `Monto` | `FacturaRepository` |

## Domain Events
| Evento | Emisor | Consumidores | Payload | Efecto |
|--------|--------|-------------|---------|--------|
| `FacturaEmitida` | `Factura` | `Notificaciones` | `{facturaId, total}` | Notifica al cliente |
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Spec | Identificar Bounded Contexts y Ubiquitous Language |
| Spec | Modelar Core Aggregates y Domain Events |
| Build | Verificar que el código usa el vocabulario del dominio |
| QA | Tier 3 verifica coherencia semantica con DOMAIN.md |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/DDD.md`
- Referencia canonica: [Domain-Driven Design — Eric Evans (2003)](https://www.domainlanguage.com/ddd/)


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
