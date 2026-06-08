---
name: evol-eda
description: EDA — Event-Driven Architecture, event choreography, saga patterns, event mesh design
category: discipline-extended
trigger: /eda
---

# evol-eda

## Fase del Pipeline

**Spec (Fase 2) — Especificación y Diseño**

Activar cuando se necesita diseñar arquitectura orientada a eventos:
- Event choreography design
- Saga patterns (choreography vs orchestration)
- Event mesh topology
- Event schema management

## Artefacto Clave

**`docs/specs/EVENT_MODEL.md`**

```markdown
# Event Model

## Event Types
| Event | Producer | Consumers | Schema |
|-------|----------|-----------|--------|
| OrderCreated | order-svc | inventory-svc, notification-svc | avro |
| InventoryUpdated | inventory-svc | order-svc | avro |
| PaymentProcessed | payment-svc | order-svc, notification-svc | avro |

## Event Flow
```
OrderCreated → inventory-svc → InventoryUpdated
     ↓
payment-svc → PaymentProcessed → notification-svc
```

## Saga Pattern: Order Processing
| Step | Service | Event | Compensation |
|------|---------|-------|--------------|
| 1 | order-svc | OrderCreated | CancelOrder |
| 2 | inventory-svc | InventoryReserved | ReleaseInventory |
| 3 | payment-svc | PaymentProcessed | RefundPayment |
| 4 | notification-svc | OrderConfirmed | - |

## Event Schema Registry
| Event | Version | Format | Location |
|-------|---------|--------|----------|
| OrderCreated | v1 | Avro | schema-registry |
| PaymentProcessed | v2 | Avro | schema-registry |
```

## Flujo de Trabajo

```bash
# 1. Descubrir eventos existentes
python3 scripts/eda/discover-events.py \
  --source . \
  --output docs/specs/EVENTS_RAW.md

# 2. Generar modelo de eventos
python3 scripts/eda/generate-model.py \
  --events docs/specs/EVENTS_RAW.md \
  --output docs/specs/EVENT_MODEL.md

# 3. Diseñar sagas
python3 scripts/eda/design-sagas.py \
  --model docs/specs/EVENT_MODEL.md \
  --output docs/specs/SAGA_DESIGN.md

# 4. Validar consistencia
python3 scripts/eda/validate.py \
  --model docs/specs/EVENT_MODEL.md \
  --output docs/specs/CONSISTENCY_REPORT.md

# 5. Generar event mesh topology
python3 scripts/eda/mesh-topology.py \
  --model docs/specs/EVENT_MODEL.md \
  --output docs/specs/EVENT_MESH.md

# 6. Schema registry validation
python3 scripts/eda/validate-schemas.py \
  --model docs/specs/EVENT_MODEL.md \
  --output docs/specs/SCHEMA_STATUS.md
```

### Event Schema Example

```avro
{
  "namespace": "com.example.events",
  "type": "record",
  "name": "OrderCreated",
  "fields": [
    {"name": "orderId", "type": "string"},
    {"name": "userId", "type": "string"},
    {"name": "items", "type": {"type": "array", "items": "string"}},
    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"}
  ]
}
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Event requirements | Eventos necesarios identificados | No |
| Spec | Event model | Modelo de eventos definido | Sí |
| Plan | Saga design | Sagas diseñadas | No |
| Build | Event implementation | Producers/Consumers funcionando | Sí |
| QA | Event validation | Eventos procesados correctamente | Sí |
| Retro | Event review | Performance y consistencia evaluadas | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Spec del Pipeline
- **Discipline Doc** — `docs/disciplines/EDA.md`
- **Event Modeling** — https://eventmodeling.org/
- **Saga Pattern** — https://microservices.io/patterns/data/saga.html
