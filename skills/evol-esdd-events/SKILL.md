---
name: evol-esdd-events
description: Event Sourcing-Driven Development. Disena event stores, aggregates con funciones de aplicacion, y tests de replay deterministico.
category: discipline-extended
trigger: /esdd
---

# evol-esdd-events

## Fase del Pipeline
Spec (Fase 2)

## Artefacto Clave
`docs/specs/EVENT_MODEL.md`

## Flujo de Trabajo

### 1. Identificar entidades candidatas a event sourcing
```bash
# Analizar entidades con necesidad de auditoria completa
evol-esdd candidates --entities=entities/ --output=eventsourcing/candidates.json
```

### 2. Disenar event store schema
```bash
# Generar esquema del event store
evol-esdd design-schema --candidates=eventsourcing/candidates.json --output=eventsourcing/event_store_schema.json
```

### 3. Definir aggregates y funciones de aplicacion
```bash
# Generar documentacion de aggregates
evol-esdd define-aggregates --schema=eventsourcing/event_store_schema.json --events=events/ --output=eventsourcing/aggregates/
```

### 4. Generar tests de replay
```bash
# Generar tests que verifican reconstruccion deterministica
evol-esdd replay-tests --aggregates=eventsourcing/aggregates/ --output=tests/eventsourcing/

# Ejecutar tests de replay
npx vitest run tests/eventsourcing/
```

### 5. Generar reporte del modelo de eventos
```bash
evol-esdd report --schema=eventsourcing/event_store_schema.json --aggregates=eventsourcing/aggregates/ --output=docs/specs/EVENT_MODEL.md
```

## Formato Event Store Schema

```json
{
  "streams": {
    "Pedido": {
      "aggregate_root": "Pedido",
      "events": [
        "PedidoCreado",
        "PedidoConfirmado",
        "PedidoEnviado",
        "PedidoEntregado",
        "PedidoCancelado"
      ],
      "snapshot_policy": {
        "every_n_events": 100
      }
    }
  }
}
```

## Formato Aggregate

```markdown
# Aggregate — Pedido

## Funcion de Aplicacion

El estado de Pedido se construye aplicando eventos en orden:

1. **PedidoCreado** -> Estado: CREADO, items: [...], total: X
2. **PedidoConfirmado** -> Estado: CONFIRMADO, confirmado_en: timestamp
3. **PedidoEnviado** -> Estado: ENVIADO, tracking_number: "XXX"
4. **PedidoEntregado** -> Estado: ENTREGADO, entregado_en: timestamp

## Reglas de Negocio
- Un pedido solo puede confirmarse si esta en estado CREADO
- Un pedido cancelado no puede recibir mas eventos
- El total se recalcula solo al crear el pedido

## Tests de Replay
- [ ] Replay de PedidoCreado -> PedidoConfirmado -> PedidoEnviado produce estado correcto
- [ ] Replay de PedidoCreado -> PedidoCancelado produce estado CANCELADO
- [ ] Replay deterministico: mismo orden de eventos = mismo estado final
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Spec | Disenar event store + aggregates + reglas de aplicacion |
| Build | Implementar el event store y las proyecciones |
| QA | Tests de replay: estado deterministico desde eventos |
| Retro | Revisar snapshots y politicas de compactacion |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/ESDD.md`
- [Event Sourcing — Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Getting Started with Event Sourcing — AxonIQ](https://axoniq.io/resources/getting-started-with-event-sourcing)


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
