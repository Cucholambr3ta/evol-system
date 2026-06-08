---
name: evol-mdd-migrate
description: Migration-Driven Development. Genera migraciones de esquema versionadas con up/down reversibles y migracion de datos explicita.
category: discipline-extended
trigger: /mdd
---

# evol-mdd-migrate

## Fase del Pipeline
Plan (Fase 3)

## Artefacto Clave
`docs/plan/MIGRATION.md`

## Flujo de Trabajo

### 1. Detectar cambios de esquema
```bash
# Comparar modelo actual vs nuevo
evol-mdd diff --current=entities/current.json --new=entities/new.json --output=migrations/proposed_changes.json
```

### 2. Generar migraciones up/down
```bash
# Generar par up/down desde el cambio de modelo
evol-mdd generate --changes=migrations/proposed_changes.json --output=migrations/$(date +%Y%m%d%H%M%S)/

# Verificar que el directorio tiene up.sql + down.sql
ls migrations/$(date +%Y%m%d%H%M%S)/
```

### 3. Generar migracion de datos si aplica
```bash
# Detectar si el cambio requiere migracion de datos
evol-mdd needs-data-migration --changes=migrations/proposed_changes.json

# Generar data_migration.md cuando aplica
evol-mdd data-migration --changes=migrations/proposed_changes.json --output=migrations/$(date +%Y%m%d%H%M%S)/data_migration.md
```

### 4. Verificar reversibilidad
```bash
# Ejecutar up -> down -> up en entorno de prueba
evol-mdd verify-reversible --migration=migrations/$(date +%Y%m%d%H%M%S)/ --db=test

# Generar reporte de migracion
evol-mdd report --migration=migrations/$(date +%Y%m%d%H%M%S)/ --output=docs/plan/MIGRATION.md
```

## Formato up.sql

```sql
-- MIGRATION: 20260607_add_user_role
-- Up: Agregar campo role a la tabla usuarios

ALTER TABLE usuarios ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL;
CREATE INDEX idx_usuarios_role ON usuarios(role);

-- Data migration: asignar role basado en existencia de permisos
UPDATE usuarios SET role = 'admin' WHERE id IN (
  SELECT DISTINCT usuario_id FROM permisos WHERE nivel = 'admin'
);
```

## Formato down.sql

```sql
-- MIGRATION: 20260607_add_user_role
-- Down: Revertir agregado de campo role

DROP INDEX IF EXISTS idx_usuarios_role;
ALTER TABLE usuarios DROP COLUMN IF EXISTS role;
```

## Formato MIGRATION.md

```markdown
# Migration Plan

**Fecha:** 2026-06-07
**Migracion:** 20260607_add_user_role

## Cambio de Esquema
Agregar campo `role` (VARCHAR 20, default 'user') a tabla `usuarios`.

## Migracion de Datos
Asignar `role = 'admin'` a usuarios con permisos de nivel admin existentes.

## Reversibilidad
El down.sql elimina la columna y el indice. La migracion de datos no es reversible
(sin historial de valores anteriores).

## Verificacion
- [ ] up.sql ejecuta sin errores
- [ ] down.sql revierte completamente
- [ ] up -> down -> up es idempotente
- [ ] Datos preservados correctamente
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Plan | Generar migraciones up/down desde el cambio de modelo |
| Build | Aplicar migracion en entornos no productivos |
| QA | Verificar rollback y migracion de datos |
| Gate | Bloquea si la migracion no es reversible |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/MDD.md`
- [Evolutionary Database Design — Martin Fowler](https://martinfowler.com/articles/evodb.html)
- [Flyway](https://github.com/flyway/flyway)
