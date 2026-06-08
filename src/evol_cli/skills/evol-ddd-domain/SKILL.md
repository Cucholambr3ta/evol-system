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
