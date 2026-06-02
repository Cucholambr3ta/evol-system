---
description: Diseña pipeline de datos con contratos, SLAs, DLQ y data quality checks.
---
# /data-pipeline

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-DATA | **Versión:** 1.0 | **Agente:** Data-Engineer + Software-Architect
**Misión:** Datos confiables, trazables y con calidad medida — no "logs convertidos en tablas".

## 0. Pre-flight
- Aplica si `xdd.profile.yml > capabilities.data_pipeline: true` o si el dominio tiene ETL/streaming.

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
