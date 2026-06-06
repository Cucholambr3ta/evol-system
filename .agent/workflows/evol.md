---
name: evol
trigger: /evol
description: Orquestador Principal Evol-DD. Pipeline de desarrollo agéntico de 6 fases con gate HMAC-SHA256, agentes core permanentes y efímeros bajo demanda. Usar cuando el usuario invoque /evol, quiera iniciar un proyecto, ejecutar una fase del pipeline, crear un agente, o necesite coordinar trabajo de desarrollo.
skills:
  - evol-compact
  - evol-talk-compact
  - evol-skill-manager
---

# /evol — Orquestador Principal Evol-DD

> Ley suprema: `docs/constitucion.md`. Leer `memoria.md` + `lecciones.md` antes de cualquier accion (Art. 3 + Art. 9).

**Version:** 1.0.0 | **Agentes core:** 17 permanentes + auditor de cumplimiento + efimeros bajo demanda

---

## Protocolo de inicio (Art. 3)

Al recibir `/evol`, antes de cualquier accion:

1. Leer `memoria.md` — estado actual del proyecto, fase activa, ultimo hito
2. Leer `lecciones.md` — patrones aprendidos relevantes al contexto actual
3. Leer `WORKING-CONTEXT.md` si existe — contexto vivo de la sesion
4. Verificar fase activa via `evol gate status`
5. Resolver dinamicamente los perfiles requeridos para la accion solicitada comparando `manifests/workflow-profiles.json` con `evol.profile.yml`. Si el perfil instalado es inferior, escalar automaticamente via `evol-init.sh --profile=<perfil> --upgrade` y configurar la variable `EVOL_HOOK_PROFILE` correspondiente.

---

## Pre-flight del Orquestador — Routing de Input

Al recibir `/evol` con un input del usuario, el orquestador DEBE:

### 1. Detectar tipo de input

| Tipo de input | Workflow a ejecutar | Ruta de salida |
|---------------|--------------------|----|
| Idea vaga ("quiero hacer X", "necesito un sistema para Y") | `/evol idea` + `/evol discovery` | `acuerdos/idea/` + `acuerdos/discovery/` |
| Prompt de investigacion con links/referencias | `/evol doc-granular` (PASO 1: investiga) | `acuerdos/research/<dominio>/<nombre>/` |
| "Implementar feature X" | Verificar fase actual del pipeline | Segun fase (ver tabla abajo) |
| "Cerrar sprint" | `/evol retro` | `acuerdos/memoria/` + `acuerdos/lecciones/` |
| "Actualizar memoria" | `/update-memory` | `acuerdos/memoria/` atomos + MEMORY.md |
| Comando de fase (`/evol briefing`, `/evol build`, etc.) | Workflow correspondiente | Segun fase |

### 2. Verificar prerrequisitos de la fase

Si el usuario solicita una fase especifica, verificar que los artefactos de la fase anterior existen:

| Fase solicitada | Prerrequisito | ABORT si falta |
|----------------|---------------|----------------|
| Briefing | `acuerdos/discovery/INDEX.md` | "Ejecutar `/evol idea` + `/evol discovery` primero" |
| Spec (doc-granular) | `acuerdos/idea/` con 14 atomos | "Ejecutar `/evol briefing` primero" |
| Plan (historias) | `acuerdos/proyecto/INDEX.md` | "Ejecutar `/evol doc-granular` primero" |
| Build | Historias de usuario en `acuerdos/historia-usuario-N/` | "Ejecutar `/evol historias` primero" |
| QA | Codigo implementado | "Ejecutar `/evol build` primero" |
| Retro | QA completado | "Ejecutar `/evol qa` primero" |

### 3. Si el input no matchea ningun workflow

ABORT con mensaje: "Input no reconocido. Usar `/evol idea` para iniciar un proyecto, o `/evol briefing` si ya tienes idea + discovery."


---

## Fases del Pipeline (Art. 9)

| Fase | Trigger | Produce (ruta real) | Gate |
|------|---------|---------------------|------|
| 0.5. Idea | `/evol idea` | `acuerdos/idea/<atomos>.md` + `INDEX.md` | Art. 1 (ambiguedad) |
| 0.7. Discovery | `/evol discovery` | `acuerdos/discovery/<tema>/investigacion.md` | Fuentes citadas |
| 1. Briefing | `/evol briefing` | `acuerdos/idea/` (14 atomos) + `acuerdos/design/` + `acuerdos/wireframes/` | 14 atomos + design aprobado |
| 2. Spec | `/evol doc-granular` | `acuerdos/proyecto/<dominio>/<subdominio>.md` + `acuerdos/research/` | Worker != auditor, 80+ lineas |
| 3. Plan | `/evol historias` | `acuerdos/historia-usuario-N/` + `acuerdos/sprints/INDEX.md` | Gherkin verificable |
| 4. Build | `/evol build` | Codigo + `acuerdos/memoria/sprint-NN.md` | Tests en verde |
| 5. QA | `/evol qa` | `docs/qa/REPORTE_QA.md` + `acuerdos/memoria/sprint-NN.md` | Shield 0 CRITICAL |
| 6. Retro | `/evol retro` | `acuerdos/memoria/sprint-NN.md` + `acuerdos/lecciones/sprint-NN.md` + `memoria.md` + `lecciones.md` | Leccion registrada |

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

Para ver el catalogo completo de skills disponibles en el sistema y sus triggers de activacion, consulte el [Catalogo de Skills](file:///home/alejandro/Documentos/Desarrollos/personal/evol-dd/skills/CATALOG.md).

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

## Auditor de Cumplimiento (Capa 2 — enforcement semantico)

El orquestador tiene un **auditor de cumplimiento** que verifica el pipeline
en tiempo real. Opera en 3 capas:

- **Capa 1 (mecanica):** Hooks en `.agent/hooks/scripts/` ejecutan validaciones
  antes y después de cada fase. El LLM lee su output.
- **Capa 2 (semantica):** Esta sección. El orquestador DEBE ejecutar los
  comandos de compliance antes de cada transición.
- **Capa 3 (reporte):** Al cierre de sprint, se genera un reporte de cumplimiento.

### Regla obligatoria por fase

Al **INICIAR** cada fase, el orquestador DEBE ejecutar:

```bash
python3 scripts/evol-compliance.py check --fase=<NUM> [--sprint=NN]
```

| Resultado | Accion del orquestador |
|-----------|----------------------|
| **PASS** | Continuar normalmente |
| **WARN** | Mostrar warnings al usuario, continuar si confirma |
| **BLOCK** | NO avanzar. Mostrar razon. Requiere resolucion explicita |

Al **FINALIZAR** cada fase, el orquestador DEBE ejecutar:

```bash
python3 scripts/evol-compliance.py record --fase=<NUM> [--sprint=NN] --agent=<AGENT>
```

### Verificacion de lecciones

Antes de cada fase, verificar lecciones pendientes:

```bash
python3 scripts/evol-compliance.py check-lessons --fase=<NUM>
```

Si hay lecciones pendientes relevantes, el orquestador DEBE:
1. Mostrarlas al usuario
2. Recordarlas al agente que ejecuta la fase
3. Verificar al finalizar si se aplicaron

### Al cierre de sprint

```bash
python3 scripts/evol-lessons.py verify-applied --sprint=NN
python3 scripts/evol-compliance.py report --sprint=NN
```

Esto genera `acuerdos/auditoria/compliance-sprint-NN.md` y actualiza
el estado de lecciones en `lecciones.md`.

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
/evol compliance-audit   → auditoria de cumplimiento del sprint
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

- Integración MCP en los adapters IDE
- `"APROBADO"` requerido antes de cada transicion de fase
- `memoria.md` se actualiza al final de cada sesion significativa
- Lecciones se consultan ANTES de proponer arquitectura
- Gate HMAC-SHA256 firma cada aprobacion — no se puede editar retroactivamente
