---
name: evol
trigger: /evol
description: Orquestador Principal Evol-DD. Pipeline de desarrollo agéntico de 6 fases con gate HMAC-SHA256, agentes core permanentes y efímeros bajo demanda. Usar cuando el usuario invoque /evol, quiera iniciar un proyecto, ejecutar una fase del pipeline, crear un agente, o necesite coordinar trabajo de desarrollo.
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

## Inyeccion de disciplinas por profile

El sistema integra **31 disciplinas *-Driven** (9 base + 22 extendidas). Registro:
[`docs/disciplinas/INDEX.md`](../../docs/disciplinas/INDEX.md) — cada ficha declara su fase y su
`executor` (workflow que la ejecuta).

Al iniciar una fase, el orquestador:

1. Lee `evol.profile.yml` -> bloque `methodologies:` (las disciplinas activas del proyecto).
2. Por cada disciplina cuya **fase** coincide con la fase actual, inyecta su capa: invoca su
   `executor` (workflow mapeado, skill nueva, o aplica la regla declarativa), genera sus artefactos
   I/O y aplica sus criterios de exito como **sub-gate** de la fase.
3. Resuelve el **DAG de dependencias** entre disciplinas antes de inyectar (ej. `chaos` exige
   `odd_obs`+`threat_driven`; `slodriven` exige `odd_obs`+`pdd`).
4. NO inyecta disciplinas que el profile no declara — activacion estricta por caso de uso.

Las 6 disciplinas sin cobertura previa tienen skill propia: `/evol ux-driven`, `/evol event-sourcing`,
`/evol api-versioning`, `/evol iac-driven`, `/evol debt-budget`, `/evol use-case-driven`.

> **Regla de fuentes (DOC_STANDARD 1.7):** todo documento producto de investigacion web cita el
> link de su fuente. El validador `validate-disciplinas.py` bloquea fichas sin `fuentes[]`.

---

## Skills de razonamiento — integracion automatica en el pipeline

Estas skills no son fases; son herramientas de razonamiento que el orquestador
**invoca automaticamente** en el punto del pipeline donde aportan valor. El agente
las dispara sin que el usuario las pida explicitamente cuando se cumple el gatillo.

| Skill | Punto de inserción automatico | Gatillo |
|-------|-------------------------------|---------|
| `/evol idea-refine` | **Antes de Fase 1 (Briefing)** | Usuario llega con idea bruta/vaga → converger a one-pager accionable antes de abrir briefing |
| `/evol grill-me` | **Antes del gate de Fase 3 (Plan)** | Antes de firmar HMAC del PLAN.md → interrogar supuestos y dependencias del plan |
| `/evol fact-check` | **Fase 2 (Spec) y Fase 5 (QA)** | Cuando SPEC.md cita un benchmark/claim externo, o QA evalua un advisory/CVE → verificar antes de aceptar como verdad |
| `/evol prompt-master` | **Transversal (Fase 4 Build)** | Al construir prompts de agentes/skills o integrar tools de IA externas → optimizar por tool |

**Regla de invocacion automatica (orquestador):**

1. **idea-refine** — Si en el Protocolo de inicio el usuario describe una idea sin
   alcance claro (no hay BRIEFING.md y la peticion es vaga), el orquestador propone
   correr `/evol idea-refine` ANTES de `/evol briefing`. El one-pager resultante
   alimenta el Briefing.

2. **grill-me** — En la transicion Fase 3 → gate, ANTES de pedir `"APROBADO"` del
   plan, el orquestador corre `/evol grill-me` sobre PLAN.md. Solo tras resolver los
   supuestos en riesgo se ofrece firmar el gate HMAC. Un plan no interrogado no se firma.
   **ENFORCED:** `evol-gate approve --phase plan` falla (exit 1) sin el marker
   `.evol/.grill-done-plan` (SHA del PLAN.md). No es solo guia — el gate lo bloquea
   criptograficamente. Override explicito: `EVOL_SKIP_GRILL=1`. Ver workflow grill-me.

3. **fact-check** — Durante Spec/QA, si un agente detecta un claim externo (benchmark,
   "X es mas rapido que Y", CVE, advisory), el orquestador dispara `/evol fact-check`
   sobre ese claim antes de incorporarlo. Veredicto FALSO/ENGAÑOSO → bloquea el uso
   del claim y registra en `lecciones.md` la fuente no confiable.

4. **prompt-master** — En Build, cuando se construyen prompts para agentes/skills del
   producto o se integra una herramienta de IA externa, el orquestador invoca
   `/evol prompt-master` para optimizar el prompt segun las convenciones de la tool.

Estas reglas hacen el pipeline **autodefensivo**: converge ideas antes de specificar
(idea-refine), no firma planes sin interrogar (grill-me), no acepta claims sin
verificar (fact-check), y no genera prompts subóptimos (prompt-master).

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
/evol-update             → actualizar el core global (pipx) y ver novedades
/evol-update-project     → inyectar actualización del core al proyecto local
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
