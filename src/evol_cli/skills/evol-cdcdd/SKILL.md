---
name: evol-cdcdd
description: Change Data Capture-Driven Development. Disena pipelines CDC log-based con transformaciones trazables y SLOs de latencia de replicacion.
category: discipline-extended
trigger: /cdc
---

# evol-cdcdd

## Fase del Pipeline
Plan (Fase 3)

## Artefacto Clave
`docs/plan/CDC_PIPELINE.md`

## Flujo de Trabajo

### 1. Definir fuentes de captura
```bash
# Identificar tablas y columnas a capturar
evol-cdcdd define-sources --schema=migrations/$(ls -t migrations/ | head -1)/up.sql --output=cdc/sources/
```

### 2. Definir transformaciones
```bash
# Escribir transformaciones fuente -> destino
evol-cdcdd transformations --sources=cdc/sources/ --output=cdc/transformations/

# Validar SQL de transformacion
evol-cdcdd validate-sql --dir=cdc/transformations/
```

### 3. Definir destinos y SLOs
```bash
# Configurar destinos de replicacion
evol-cdcdd define-targets --sources=cdc/sources/ --output=cdc/targets/

# Definir SLO de latencia por destino
evol-cdcdd define-slo --targets=cdc/targets/ --max-latency-ms=5000 --output=cdc/targets/slo.json
```

### 4. Generar reporte del pipeline
```bash
# Consolidar pipeline completo
evol-cdcdd report --sources=cdc/sources/ --transformations=cdc/transformations/ --targets=cdc/targets/ --output=docs/plan/CDC_PIPELINE.md
```

## Formato Source

```json
{
  "source_id": "CDC-SRC-001",
  "table": "pedidos",
  "columns": ["id", "usuario_id", "total", "estado", "created_at"],
  "capture_mode": "log-based",
  "plugin": "debezium-postgres",
  "primary_key": "id"
}
```

## Formato Transformation

```sql
-- cdc/transformations/pedidos_to_analytics.sql
-- Transformacion: pedidos operacionales -> analytics

SELECT
  p.id AS order_id,
  p.usuario_id,
  u.email AS user_email,
  p.total,
  p.estado,
  p.created_at,
  CURRENT_TIMESTAMP AS replicated_at
FROM pedidos p
JOIN usuarios u ON p.usuario_id = u.id
WHERE p.created_at >= :cdc_start_offset;
```

## Formato CDC_PIPELINE.md

```markdown
# CDC Pipeline Plan

**Fecha:** 2026-06-07
**Estado:** PLANIFICADO

## Resumen
Pipeline CDC log-based para replicar cambios de `pedidos` hacia data warehouse analytics.

## Sources
| Tabla | Columnas | Modo | Plugin |
|-------|----------|------|--------|
| pedidos | id, usuario_id, total, estado, created_at | log-based | debezium-postgres |

## Transformations
| Source | Transformation | Destino |
|--------|---------------|---------|
| pedidos | pedidos_to_analytics.sql | analytics_orders |

## Targets
| Destino | SLO Latencia | Modo |
|---------|-------------|------|
| analytics_orders | < 5s | streaming |

## Validacion
- [ ] Captura log-based funcional
- [ ] Transformaciones correctas (fidelidad 100%)
- [ ] Latencia dentro del SLO
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Plan | Definir sources, transformaciones y targets |
| Build | Configurar la captura log-based + transformaciones |
| QA | Verificar latencia dentro del SLO |
| Gate | Bloquea si la latencia supera el SLO declarado |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/CDCDD.md`
- [Change Data Capture — Martin Kleppmann](https://www.confluent.io/blog/how-change-data-capture-works-patterns-solutions-implementation/)
- [Debezium](https://github.com/debezium/debezium)
