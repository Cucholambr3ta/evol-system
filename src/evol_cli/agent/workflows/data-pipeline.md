---
description: Diseña pipeline de datos con contratos, SLAs, DLQ y data quality checks.
name: data-pipeline
trigger: /evol data-pipeline
---
# /data-pipeline

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-DATA | **Versión:** 1.0 | **Agente:** Data-Engineer + Software-Architect
**Misión:** Datos confiables, trazables y con calidad medida — no "logs convertidos en tablas".

## 0. Pre-flight
- Aplica si `evol.profile.yml > capabilities.data_pipeline: true` o si el dominio tiene ETL/streaming.

## 1. Contratos de datos
- Schema versionado (Avro, Protobuf, JSON Schema) por dataset.
- Contract testing entre productor y consumidor.
- Cambios breaking → procedimiento (deprecación, migración, sunset).

## 2. SLAs por dataset
Para cada dataset crítico:
- **Freshness** (latencia máxima desde origen)
- **Completeness** (porcentaje de registros esperados)
- **Accuracy** (validaciones de negocio aprobadas)
- **Availability** (uptime del pipeline)

## 3. Calidad
<!-- CONFIGURAR: Herramientas data quality.                                    -->
<!--  - Great Expectations, Soda Core, dbt tests                                -->
<!--  - Deequ (JVM)                                                             -->

Tests por dataset: not null en columnas clave, unicidad, rangos, joins consistentes.

## 4. Resiliencia
- **Dead Letter Queue** para registros no procesables (sin perderlos).
- **Idempotencia** de jobs (re-run seguro).
- **Backfill** documentado y probado.
- **Watermarks** para late-arriving data.

## 5. Lineage y catálogo
- Lineage automatizado (dbt, OpenLineage, DataHub).
- Catálogo navegable con dueño por dataset.

## 6. PII en pipelines
- Cruzar con `PRIVACY.md`: minimización, pseudonimización en bronze/silver, accesos auditados a gold.
- Borrado por DSAR llega hasta el warehouse.

## 7. Costo
- Cruzar con `/finops-baseline`: presupuesto por pipeline/dataset.
- Particiones y compresión revisadas.

## 8. Cierre
- Documentar pipeline en `docs/data/<dataset>.md`.
- Lineage publicado.
- Lecciones a [[lecciones]].

---

## Extension: disciplinas EDA y CDCDD

> Activacion por profile: `eda` y/o `cdcdd` en `methodologies:`. Fichas:
> [`docs/disciplinas/EDA.md`](../../docs/disciplinas/EDA.md) y
> [`docs/disciplinas/CDCDD.md`](../../docs/disciplinas/CDCDD.md).

Cuando el profile activa estas disciplinas, este workflow se extiende:

### EDA — Event-Driven Architecture
- **Salida adicional:** `eda/schemas/*.avsc` (Avro/Protobuf versionados), `eda/topics/*.json`,
  `eda/producers/*.json` (mapeo productor -> evento -> consumidores).
- **Criterio:** todo evento con schema evolutivo + politica de compatibilidad declarada.

### CDCDD — Change Data Capture
- **Entrada adicional:** `migrations/*/up.sql` (esquema fuente) + `events/*.json`.
- **Salida adicional:** `cdc/sources/*.json`, `cdc/transformations/*.sql`, `cdc/targets/*.json`.
- **Criterio:** latencia de replicacion dentro del SLO; captura log-based donde la BD lo soporte.

**Fuentes:** toda decision de schema/replicacion basada en investigacion web cita su URL (DOC_STANDARD).
