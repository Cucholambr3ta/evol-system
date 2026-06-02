---
description: Define y prueba el plan de recuperación ante desastres. Produce DR_PLAN.md y log de drills.
name: dr-drill
trigger: /evol dr-drill
---
# /dr-drill

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-DR | **Versión:** 1.0 | **Agente:** SRE + Chaos-Engineer
**Misión:** RTO y RPO conocidos, probados y honrados. DR no es un PDF, es un músculo.

## 0. Pre-flight
- Copia `templates/dr-plan.template.md` a `DR_PLAN.md`.
- Requiere `THREATS.md` para alinear escenarios con amenazas reales.

## 1. Objetivos
Define RTO y RPO **por servicio crítico** (no uno global). Justifica con impacto de negocio.

## 2. Escenarios mínimos
- Caída de región cloud
- Corrupción de datos en BD primaria
- Ransomware / borrado malicioso
- Pérdida de cuenta del proveedor cloud
- Despliegue con regresión crítica

## 3. Backups verificados
Inventario en `DR_PLAN.md` con: recurso, frecuencia, retención, ubicación (cross-region!), encriptación, **última restauración probada**.

> Backup sin restauración probada = no existe.

## 4. Drill calendarizado (mínimo semestral)
Para cada drill:
1. Seleccionar escenario.
2. Ejecutar en entorno aislado (NO producción) con datos sintéticos o congelados.
3. Cronometrar RTO y RPO reales.
4. Documentar hallazgos: qué falló, qué falta automatizar.
5. Actualizar runbooks y `DR_PLAN.md`.

## 5. Chaos engineering (gradual)
- Game days mensuales con failure injection controlado.
- Empezar en staging; promover a prod solo con buy-in y kill switch listo.

## 6. Comunicación
- Status page actualizable bajo presión (probado durante drill).
- Plantillas de comunicación interna y externa pre-redactadas.

## 7. Gated (Art. 2)
`"APROBADO"` antes de:
- Cualquier inyección de fallo en producción.
- Cambios en backups que reduzcan RPO/retención.

## 8. Cierre
- Drill log en `DR_PLAN.md` (fecha, escenario, RTO/RPO reales, hallazgos).
- Mejoras pendientes a `lecciones.md` y backlog.
