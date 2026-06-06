---
name: evol-compliance-auditor-workflow
trigger: /evol compliance-audit
description: Workflow del auditor de cumplimiento. Verifica fases del pipeline, detecta violaciones, genera reportes de sprint. Se ejecuta al final de cada sprint o bajo demanda.
---

# evol-compliance-auditor-workflow

> Este workflow instancia el agente `evol-compliance-auditor` como observador
> del pipeline. No reemplaza al orquestador — lo audita.

## Fase 0 — Instantiación

```bash
python3 scripts/evol-agent-lifecycle.py create \
  --name "evol-compliance-audit-${FASE}-${TIMESTAMP}" \
  --task "Auditoria de cumplimiento fase ${FASE}" \
  --expires-after 1
```

## Fase 1 — Contexto

1. Leer `memoria.md` — estado actual del proyecto
2. Leer `lecciones.md` — lecciones acumuladas
3. Leer `acuerdos/memoria/MEMORY.md` — memoria consolidada
4. Ejecutar `python3 scripts/evol-compliance.py check-lessons` — lecciones pendientes por fase
5. Ejecutar `python3 scripts/evol-state.py stats` — estado del sistema

## Fase 2 — Verificación por fase

Para cada fase del pipeline que se haya ejecutado en el sprint:

```bash
python3 scripts/evol-compliance.py check --fase=<NUM> --sprint=<SPRINT>
```

Registrar resultado:
- PASS: fase OK
- WARN: advertencias (gate no firmado, lecciones pendientes)
- BLOCK: violaciones criticas (artifacts faltantes, seguridad)

## Fase 3 — Verificación de lecciones

```bash
python3 scripts/evol-lessons.py verify-applied --sprint=<SPRINT>
```

Para cada lección pendiente:
1. Buscar evidencia de aplicación en artefactos del sprint
2. Si se encontró evidencia → marcar como aplicada
3. Si no se encontró → verificar si la situación se repitió (VIOLATION)

## Fase 4 — Reporte

```bash
python3 scripts/evol-compliance.py report --sprint=<SPRINT>
```

Esto genera:
- `acuerdos/auditoria/compliance-sprint-<SPRINT>.md`
- Resumen de violaciones
- Estado de lecciones (aplicadas vs pendientes)
- Score de cumplimiento

## Fase 5 — Registro de lecciones

Para cada VIOLATION detectada, crear lección:

```bash
python3 scripts/evol-lessons.py add \
  --titulo "<titulo>" \
  --categoria "PROCESO" \
  --contexto "Auditoria de cumplimiento sprint <SPRINT>" \
  --problema "<descripcion de la violacion>" \
  --causa "<por que ocurrio>" \
  --leccion "<regla para evitarlo>" \
  --aplica "Pipeline Evol-DD, fase <FASE>"
```

## Fase 6 — Actualización de memoria

Si se detectaron nuevas convenciones:

```bash
# Agregar a acuerdos/memoria/convenciones.md
```

Si se detectaron nuevos riesgos:

```bash
# Agregar a acuerdos/memoria/riesgos.md
```

## Fase 7 — Retiro

```bash
python3 scripts/evol-agent-lifecycle.py retire "evol-compliance-audit-${FASE}-${TIMESTAMP}"
```

## Reglas de enforcement

| Severidad | Acción | Override |
|-----------|--------|----------|
| CRITICAL | Bloquea fase | `EVOL_SKIP_COMPLIANCE=1` (requiere confirmación) |
| WARNING | Muestra warning | Usuario confirma para continuar |
| INFO | Solo registra | No interfiere |

## Output

- `acuerdos/auditoria/compliance-sprint-<SPRINT>.md` — reporte completo
- `acuerdos/lecciones/sprint-<SPRINT>.md` — enriquecido
- `~/.evol/state.db` — tablas phase_compliance, violation_log, lesson_tracking actualizadas
