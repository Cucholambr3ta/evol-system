---
description: Gestión de migraciones de BD en Fase 4. Genera migración up/down, seed y verifica rollback.
name: db-migrate
trigger: /evol db-migrate
---
# /db-migrate

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-DB-MIG | **Versión:** 1.0 | **Agente:** Database-Optimizer + Senior-Developer
**Misión:** Toda evolución de schema atraviesa migración versionada, reversible y probada.

## 0. Pre-flight
- Verifica `migrations/` (crea si no existe).
- Verifica que la migración pendiente derive de un cambio en `DOMAIN.md` aprobado.

## 1. Tipo de cambio
Clasifica:
- **Aditivo seguro** (nueva tabla, nueva columna nullable, nuevo índice CONCURRENTLY)
- **Riesgoso** (NOT NULL en columna existente con datos, rename, drop, cambio de tipo)
- **Datos** (backfill, transformación)

Para `Riesgoso` y `Datos` → split en múltiples migraciones (expand → migrate → contract).

## 2. Generación
<!-- CONFIGURAR: Herramienta de migraciones. Opciones:                          -->
<!--  - Prisma Migrate, Drizzle Kit, TypeORM (Node)                              -->
<!--  - Alembic (Python), Flyway, Liquibase (JVM)                                -->
<!--  - sqlx-cli, refinery (Rust), Goose, golang-migrate (Go)                    -->
<!--  - dbmate, sqitch (agnóstico)                                               -->

Crea:
- `migrations/NNNN_<descripcion>.up.sql` (o equivalente)
- `migrations/NNNN_<descripcion>.down.sql`
- `seeds/<NNNN_descripcion>.seed.sql` si aplica

## 3. Seguridad y bloqueos
- Sin `ACCESS EXCLUSIVE LOCK` en horas pico (Postgres: usar `CONCURRENTLY`, `NOT VALID` + `VALIDATE`).
- Backfills en lotes con cooldown.
- Timeout de migración configurado.

## 4. Verificación obligatoria
```bash
# 1. Aplica en BD efímera (Docker/sqlite/test container)
# 2. Verifica que down revierte limpio
# 3. Carga seed
# 4. Corre tests de integración
```
Si rollback falla → bloquea merge.

## 5. Gated (Art. 2)
Antes de migrar producción: `"APROBADO"` con confirmación de:
- Backup reciente y restorable.
- Ventana de mantenimiento o online migration validada.
- Runbook de rollback listo.

## 6. Cierre
- Documenta migración en `CHANGELOG.md`.
- Si afecta PII, dispara `/privacy-review`.
- Si afecta performance, dispara `/perf-budget`.
