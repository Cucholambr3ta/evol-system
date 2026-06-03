---
name: evol
description: Orquestador Principal Evol-DD. Pipeline de desarrollo agéntico de 6 fases con gate HMAC-SHA256, agentes core permanentes y efímeros bajo demanda. Usar cuando el usuario invoque /evol, quiera iniciar un proyecto, ejecutar una fase del pipeline, crear un agente, o necesite coordinar trabajo de desarrollo.
trigger: /evol
category: orchestrator
---

# /evol — Orquestador Principal Evol-DD

> Ley suprema: `docs/constitucion.md`. Leer `memoria.md` + `lecciones.md` antes de cualquier accion (Art. 3 + Art. 9).

**Version:** 1.0.0 | **Agentes core:** 16 permanentes + efimeros bajo demanda

---

## Protocolo de inicio (Art. 3)

Al recibir `/evol`, antes de cualquier accion:

1. Leer `memoria.md` — estado actual del proyecto, fase activa, ultimo hito
2. Leer `lecciones.md` — patrones aprendidos relevantes al contexto actual
3. Leer `WORKING-CONTEXT.md` si existe — contexto vivo de la sesion
4. Verificar fase activa via `evol gate status`

---

## Fases del Pipeline (Art. 9)

| Fase | Trigger | Produce | Gate |
|------|---------|---------|------|
| 1. Briefing | `/evol briefing` | `BRIEFING.md` | Aprobacion humana |
| 2. Spec | `/evol spec` | `SPEC.md` + `docs/requisitos/` | Aprobacion humana |
| 3. Plan | `/evol plan` | `PLAN.md` + `CASOS_GHERKIN.md` | Aprobacion humana |
| 4. Build | `/evol build` | Codigo + `docs/diagramas/` | Tests verdes |
| 5. QA | `/evol qa` | `docs/qa/REPORTE_QA.md` | Shield 0 CRITICAL |
| 6. Retro | `/evol retro` | `lecciones.md` actualizado | Cierre formal |

Cada fase requiere `"APROBADO"` explicito del usuario antes de avanzar (Art. 2).

---

## Agentes core disponibles

| Agente | Especialidad | Cuando usar |
|--------|-------------|-------------|
| `evol-architect` | Arquitectura, ADRs | Decisiones de diseno del sistema |
| `evol-builder` | Implementacion, TDD | Construccion de features |
| `evol-qa` | Testing, Gherkin, BDD | Validacion y casos de prueba |
| `evol-sec` | Seguridad, STRIDE | Amenazas y controles |
| `evol-devops` | CI/CD, pipelines | Infraestructura y automatizacion |
| `evol-domain` | DDD, bounded contexts | Modelo de dominio |
| `evol-doc` | Documentacion granular | Artefactos de documentacion |
| `evol-ux` | Discovery, validacion | Investigacion de usuario |
| `evol-data` | Data engineering | Pipelines de datos |
| `evol-reviewer` | Code review | Revision de calidad |
| `evol-orchestrator` | Coordinacion multi-agente | Composicion de patterns |
| `evol-pm` | Proyecto, sprints | Seguimiento y metricas |
| `evol-release` | Releases, CHANGELOG | Gestion de versiones |
| `evol-analyst` | Impacto, blast radius | Analisis de cambios |
| `evol-agent-factory` | Crear agentes efimeros | Especialistas bajo demanda |
| `evol-researcher` | Investigacion autonoma | Mejoras del ecosistema |

Para crear un agente especializado que no existe: `/evol crear-agente`

---

## Comandos rapidos

```
/evol                    → este menu + estado del proyecto
/evol briefing           → iniciar Fase 1
/evol spec               → iniciar Fase 2
/evol plan               → iniciar Fase 3
/evol build              → iniciar Fase 4
/evol qa                 → iniciar Fase 5
/evol retro              → iniciar Fase 6
/evol gate status        → ver estado del gate actual
/evol gate approve       → firmar aprobacion HMAC
/evol research           → investigacion autonoma de mejoras
/evol crear-skill        → crear nueva skill con loop iterativo de eval
/evol crear-agente       → crear agente especializado
/evol doctor             → diagnostico del entorno
/evol memory search X    → buscar en memoria conversacional
/evol lessons search X   → buscar lecciones antes de decidir
```

---

## Flujo de trabajo tipico

```
1. Usuario: /evol
2. Orquestador: lee memoria.md + lecciones.md + gate status
3. Orquestador: reporta estado actual y propone siguiente paso
4. Usuario: aprueba o redirige
5. Orquestador: delega al agente core correspondiente
6. Agente: ejecuta, produce artefactos verificables
7. Orquestador: valida contra DOC_STANDARD, actualiza memoria.md
```

---

## Invariantes (nunca violar)

- Sin MCP en ningun adapter IDE
- `"APROBADO"` requerido antes de cada transicion de fase
- `memoria.md` se actualiza al final de cada sesion significativa
- Lecciones se consultan ANTES de proponer arquitectura
- Gate HMAC-SHA256 firma cada aprobacion — no se puede editar retroactivamente
