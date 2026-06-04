---
name: evol-historias
trigger: /evol historias
description: Genera historias de usuario completas post-doc-granular. Lee acuerdos/proyecto/ + acuerdos/wireframes/ e identifica TODAS las historias (HU/HT/HS). Por cada una crea 4 artefactos via pipeline worker-auditor. Genera acuerdos/sprint.md con plan de sprints. Sin evaluacion — si es una historia identificable, se documenta completa.
phase: plan
category: planning
---

# /evol historias — Historias de usuario + plan de sprints

> **Principio (cero deuda tecnica):** Sin evaluacion. Cada funcionalidad identificable
> tiene su historia completa. Si existe como unidad de valor entregable, tiene historia.
>
> **Pipeline worker → auditor:** quien escribe NO aprueba. El auditor verifica
> completitud, alineacion con briefing y granularidad del checklist (minimo 50 tareas).
> Toda deficiencia se registra en acuerdos/lecciones/sprint-00.md.

## 0. Pre-flight

1. Verificar que `acuerdos/proyecto/INDEX.md` existe (doc-granular completo).
2. Verificar que `acuerdos/wireframes/` tiene al menos 1 HTML aprobado.
3. Leer `acuerdos/memoria/MEMORY.md` + journal mas reciente en `acuerdos/memoria/`.
4. Si falta doc-granular: detener y ejecutar `/evol doc-granular` primero.

---

## 1. IDENTIFICACION DE HISTORIAS

El agente lee TODOS los artefactos de `acuerdos/proyecto/` + `acuerdos/wireframes/*.html`.

**Tipos de historia:**
- `HU` — Historia de usuario (funcionalidad para el usuario final)
- `HT` — Historia tecnica (infraestructura, setup, configuracion)
- `HS` — Historia de seguridad (controles STDD, amenazas STRIDE)

Producir borrador en `acuerdos/sprint.md` con listado inicial (numeradas, tipo, titulo, estimacion).

---

## 2. PIPELINE WORKER → AUDITOR POR HISTORIA

Por cada historia:

### PASO 1 — ESCRIBE 4 ARTEFACTOS (worker: engineering-technical-writer + product-manager)

#### `acuerdos/historia-usuario-N/propuesta.md`

```markdown
# HU-N: <Titulo>

## Descripcion
Como <tipo de usuario>, quiero <accion> para <beneficio>.

## Valor de negocio
<Por que importa. Que pasa si no se implementa.>

## Criterio de exito
<Condicion medible y verificable.>

## Alcance
- Incluye: <lista>
- Excluye: <lista>

## Dependencias
- Requiere: <HU-X, HT-Y>
- Bloquea: <HU-A>
```

#### `acuerdos/historia-usuario-N/requisitos-escenarios.md`

Gherkin completo. Minimo por historia:
- 1 escenario happy path
- 2+ escenarios de error
- 1+ escenario borde
- Escenarios de seguridad si la historia toca auth/datos/API

#### `acuerdos/historia-usuario-N/escenario-tecnico.md`

Incluye: stack involucrado, componentes, diagrama Mermaid, esquemas de datos, patrones, integraciones, consideraciones de seguridad STRIDE.

#### `acuerdos/historia-usuario-N/checklist-tareas.md`

**Minimo 50 tareas atomicas.** Estructura obligatoria:

```markdown
# Checklist — HU-N

## Setup y preparacion
- [ ] <tarea>

## Backend
- [ ] <tarea>

## Frontend / UI (si aplica)
- [ ] <tarea>

## Tests unitarios (TDD — tests primero)
- [ ] Escribir test que falla para <componente>
- [ ] Implementar minimo codigo para pasar test

## Tests BDD
- [ ] Implementar escenario Gherkin: <scenario>

## Tests de seguridad (STDD)
- [ ] Escribir test de seguridad para amenaza <STRIDE-REF>

## Observabilidad
- [ ] Log estructurado en <punto critico>

## Documentacion
- [ ] Actualizar acuerdos/proyecto/<dominio>.md

## Revision y cierre
- [ ] Code review por engineering-code-reviewer
- [ ] Shield audit 0 CRITICAL
- [ ] Todos los escenarios Gherkin verdes
- [ ] PR lista para merge
```

### PASO 2 — AUDITA (auditor: engineering-code-reviewer + product-manager)

Verifica:
1. Completitud de propuesta (AS, valor, criterio, alcance, dependencias)
2. Gherkin: happy path + errores + bordes
3. Diagrama Mermaid presente en escenario-tecnico
4. Checklist >= 50 tareas — si < 50: rechaza, writer amplia
5. Cobertura STDD — si historia toca auth/datos/API y no hay tareas STDD: rechaza
6. Alineacion con briefing en acuerdos/idea/

Cada gap → registrar en `acuerdos/lecciones/sprint-00.md`:

```bash
evol-memory --project=. sprint-close --sprint=00
# Append: gap encontrado, historia afectada, correccion aplicada
```

Gate de historia aprobada:

```bash
python3 scripts/evol-gate.py approve --phase plan --approver "engineering-code-reviewer"
```

---

## 3. PLAN DE SPRINTS — `acuerdos/sprint.md`

Una vez que TODAS las historias estan aprobadas, generar:

```markdown
# Plan de Sprints — <Nombre Proyecto>

> Cada sprint = 1 branch feature/sprint-NN-<titulo>.
> Regla: 1 PR mergeada a develop antes de iniciar siguiente sprint.

## Resumen

| Total historias | Total puntos | Sprints propuestos | Velocidad asumida |
|---|---|---|---|
| N | NNN SP | N | N SP/sprint |

## Sprints

### Sprint 01 — <titulo>
**Objetivo:** <capacidad disponible al cerrar>
**Historias:** HT-01 (N SP), HU-02 (N SP)
**Definition of Done:**
- Tests verdes (unit + integration + security)
- Shield 0 CRITICAL
- PR mergeada a develop
```

Criterios de organizacion:
- HT primero, HS distribuidas (nunca al final)
- Dependencias respetadas
- Ultimo sprint: hardening + observabilidad + docs

---

## 4. GATE DE CIERRE

```
[ ] acuerdos/sprint.md con todos los sprints definidos
[ ] Cada acuerdos/historia-usuario-N/ tiene 4 artefactos completos
[ ] Cada historia: firma auditor != writer
[ ] checklist-tareas.md >= 50 tareas
[ ] 0 gaps abiertos
```

Al cerrar: registrar en `acuerdos/memoria/sprint-00.md` el numero de historias y plan de sprints.

---

## Agentes delegados

| Agente | Rol |
|--------|-----|
| `product-manager` | Identifica historias, escribe propuesta.md |
| `engineering-technical-writer` | Escribe requisitos-escenarios, escenario-tecnico, checklist |
| `engineering-code-reviewer` | Audita (NUNCA el mismo que escribio) |
| `project-manager-senior` | Organiza sprints en sprint.md |
