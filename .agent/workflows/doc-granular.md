---
name: doc-granular
trigger: /evol doc-granular
description: Genera documentacion granular automatica post-briefing. Por cada dominio tecnico identificado en acuerdos/idea/ genera un documento exhaustivo via pipeline worker-auditor. Sin evaluacion — si es un dominio tecnico del proyecto, tiene doc. Cero deuda tecnica. Invocado automaticamente por /xdd briefing al cerrar, o manualmente para regenerar.
phase: spec
category: documentation
---

# /evol doc-granular — Documentacion granular automatica

> **Principio (cero deuda tecnica):** Sin evaluacion. Cada dominio tecnico del
> proyecto tiene su documento. No hay "esto es obvio", "el agente ya sabe" ni
> "no merece un doc separado". Si existe como dominio, se documenta.
>
> **Pipeline worker → auditor:** quien escribe NO aprueba. El auditor identifica
> gaps, refuerza consistencia cross-doc e itera hasta cerrar. Es el patron de
> cero confianza aplicado a documentacion.

## 0. Pre-flight

1. Verificar que `acuerdos/idea/` tiene los 14 artefactos del briefing cerrado.
2. Leer `memoria.md` + `lecciones.md` (Art. 3).
3. Registrar inicio en `memoria.md`.

Si `acuerdos/idea/` esta vacio o incompleto: detener y ejecutar `/xdd briefing` primero.

---

## 1. IDENTIFICACION DE DOMINIOS

El agente lee TODOS los artefactos de `acuerdos/idea/`:
- `producto.md`, `usuarios.md`, `plataformas.md`, `stack.md`, `arquitectura.md`
- `integraciones.md`, `auth.md`, `seguridad.md`, `calidad.md`, `datos-privacidad.md`
- `observabilidad.md`, `cicd.md`, `operaciones.md`, `proceso.md`

Y los wireframes de `acuerdos/wireframes/*.html` + tokens de `acuerdos/design/`.

A partir de esa lectura identifica **todos** los dominios tecnicos del proyecto.
Criterio: ¿hay suficiente complejidad tecnica para que un sub-agente necesite
este doc como referencia de trabajo independiente?

Ejemplos de dominios para un proyecto tipico:
- DB: schemas completos, relaciones, indices, migraciones
- API: contratos, endpoints, schemas request/response, errores
- Autenticacion: flujos, tokens, sesiones, refresh
- State machines: estados, transiciones, guards por entidad
- Algoritmos: logica de negocio no trivial
- Seguridad: STRIDE, controles, AgentShield
- Observabilidad: logs, metricas, alertas, spans
- UI: componentes, estados, responsive, a11y
- Testing: estrategia, fixtures, mocks, cobertura
- CI/CD: pipelines, ambientes, despliegue
- Migracion de datos: si aplica
- Performance: benchmarks, SLOs, caching
- ...y todos los dominios especificos del proyecto

**No hay limite de documentos.** Un proyecto simple genera 15-20.
Uno complejo genera 50-100. El numero lo determina el proyecto, no el agente.

Producir: `acuerdos/proyecto/INDEX.md` con el listado de documentos a generar
(numerados, titulo, proposito de una linea).

---

## 2. PIPELINE WORKER → AUDITOR

Por cada documento del INDEX, ejecutar en paralelo (evol-orchestrate parallel_then_sync):

### PASO 1 — INVESTIGA (worker: specialized-researcher)

```
Tarea: investigar el dominio "<nombre>" para el proyecto "<nombre-proyecto>"
Contexto: leer acuerdos/idea/<artefactos-relevantes>.md
Output: acuerdos/research/<dominio>/investigacion.md
  - Mejores practicas del dominio
  - Patrones recomendados para el stack del proyecto
  - Riesgos conocidos y como mitigarlos
  - Referencias (links, RFCs, documentacion oficial)
```

### PASO 2 — VALIDA CLAIMS (worker: fact-check)

Ejecutar `/xdd fact-check` sobre `acuerdos/research/<dominio>/investigacion.md`.
Si algun claim tiene veredicto FALSO o ENGAÑOSO: marcar y excluir del documento.
Output: `acuerdos/research/<dominio>/investigacion-validada.md`

### PASO 3 — ESCRIBE (worker: engineering-technical-writer)

Con base en:
- `acuerdos/research/<dominio>/investigacion-validada.md`
- Artefactos de briefing relevantes
- Wireframes HTML si el dominio tiene componentes UI
- DOC_STANDARD.md (Mermaid obligatorio, tablas, Gherkin, 0 emojis)

Redactar `acuerdos/proyecto/NN-<DOMINIO>.md` con granularidad extrema:
- Vision general del dominio en el proyecto
- Diagrama Mermaid de la arquitectura del dominio
- Schemas completos (SQL, TypeScript, Zod, JSON Schema segun aplique)
- Algoritmos y logica de negocio no trivial (pseudocodigo o codigo real)
- Casos borde y como se manejan
- Contratos de integracion con otros dominios
- Test cases (escenarios Gherkin)
- Glosario del dominio

### PASO 4 — AUDITA (auditor: engineering-reviewer)

El auditor NO es quien escribio el documento (separacion de privilegios — reusa
enforcement de evol-gate set-author + segregacion del Inc 1).

El auditor verifica:
1. **Completitud**: ¿hay gaps obvios? ¿falta alguna seccion critica?
2. **Consistencia cross-doc**: ¿contradice algun otro documento ya aprobado?
3. **Alineacion con briefing**: ¿refleja exactamente lo acordado en acuerdos/idea/?
4. **Granularidad**: ¿esta suficientemente detallado para que un sub-agente
   pueda trabajar a partir de el sin hacer preguntas?
5. **DOC_STANDARD**: Mermaid presente, tablas para datos estructurados, 0 emojis

Si hay gaps: el auditor los lista → el writer los cierra → el auditor re-verifica.
Iterar hasta que el auditor aprueba (max 3 iteraciones; si no cierra, escalar).

Registrar en evol-gate:
```bash
evol-gate.py set-author --phase spec --author "engineering-technical-writer"
# El auditor aprueba (no el writer):
evol-gate.py approve --phase spec --approver "engineering-reviewer"
```

### PASO 5 — INDEXA (post-sync)

Una vez que TODOS los documentos estan aprobados:

Generar `acuerdos/proyecto/INDEX.md` definitivo:

```markdown
# INDEX — Documentacion del Proyecto

> Generado automaticamente post-briefing. Trazabilidad bidireccional.
> Cada documento esta auditado (worker != auditor).

## Documentos generados

| # | Documento | Dominio | Briefing relacionado | Estado |
|---|-----------|---------|---------------------|--------|
| 01 | 01-DB-SCHEMAS.md | Base de datos | stack.md, arquitectura.md | Aprobado |
| 02 | 02-API-CONTRATOS.md | API REST | arquitectura.md, integraciones.md | Aprobado |
| ... | ... | ... | ... | ... |

## Trazabilidad

Por cada documento: que artefactos del briefing lo originaron.
Por cada artefacto del briefing: en que documentos esta materializado.
```

---

## 3. ORQUESTACION

Usar `evol-orchestrate.py` con pattern `parallel_then_sync`:
- **Paralelo:** pasos 1-4 por cada dominio simultaneamente
- **Sync:** paso 5 (INDEX) espera a que todos los documentos esten aprobados

```python
# Esquema de orquestacion
{
  "pattern": "parallel_then_sync",
  "parallel_tasks": [
    {"agent": "specialized-researcher", "task": "investigar <dominio>"},
    # ... un task por dominio
  ],
  "sync_task": {
    "agent": "engineering-technical-writer",
    "task": "generar INDEX.md con trazabilidad bidireccional"
  }
}
```

---

## 4. GATE DE CIERRE

El doc-granular cierra cuando:

```
[ ] acuerdos/proyecto/INDEX.md existe con todos los documentos listados
[ ] Cada NN-<DOMINIO>.md tiene firma de aprobacion (auditor != writer)
[ ] 0 gaps abiertos en ningun documento
[ ] INDEX tiene trazabilidad bidireccional completa
```

Verificacion:
```bash
ls acuerdos/proyecto/*.md | wc -l   # N+1 (N docs + INDEX)
evol-gate.py status                  # todas las aprobaciones registradas
```

Al cerrar: registrar en `memoria.md` el numero de documentos generados y
la proxima etapa (historias de usuario + sprints).

---

## 5. POST-FLIGHT — HISTORIAS DE USUARIO

Con la documentacion granular completa, el siguiente paso es:

```
/xdd historias
```

El agente lee `acuerdos/proyecto/` + `acuerdos/wireframes/` y genera:
- `acuerdos/historia-usuario-N/` por cada historia identificada
- Cada historia: propuesta + requisitos-escenarios + escenario-tecnico + checklist-tareas
- `acuerdos/sprint.md`: plan de sprints con estimaciones

---

## Agentes delegados

| Agente | Rol |
|--------|-----|
| `specialized-researcher` | Investiga cada dominio (PASO 1) |
| `engineering-technical-writer` | Escribe cada documento (PASO 3) |
| `engineering-reviewer` | Audita cada documento — NUNCA el mismo que escribio (PASO 4) |
| `product-manager` | Audita alineacion con briefing en documentos de producto |
