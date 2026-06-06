# Constitucion de Evol-DD

> Ley suprema del sistema. Toda instruccion, script, agente y proceso debe
> conformarse a ella. En caso de conflicto, la Constitucion prevalece.

---

## Art. 1 — Filtro de Ambiguedad y Neutralidad

**Paso Cero:** Detener si la orden carece de parametros definidos. No avanzar
sin parametros medibles.

Antes de escribir codigo, evaluar:
- Existe un standard de industria aplicable?
- El problema ya fue resuelto por una libreria madura?
- Cual es el criterio de exito verificable?

Si la respuesta a los tres es "no", solicitar clarificacion antes de proceder.

---

## Art. 2 — Gated Pipeline

**No encadenar flujos largos sin checkpoint.**

Para cambios estructurales o transicion entre fases, requerimos:

1. Artefactos verificables de la fase actual
2. "APROBADO" explicito (firma HMAC-SHA256 via `evol-gate`)
3. Registro en `memoria.md` antes de avanzar

El pipeline no avanza por default — avanza por aprobacion.

---

## Art. 3 — Preservacion de Contexto (Flight Recorder)

**Leer `memoria.md` al abrir cualquier proyecto.**

Sesion inicia:
1. Leer `memoria.md` — estado del proyecto, decisiones, hitos
2. Leer `lecciones.md` — lecciones relevantes al area de trabajo
3. Leer `WORKING-CONTEXT.md` — branch activo, fase, PRs recientes

Sesion termina:
1. Actualizar `memoria.md` — decisiones, artefactos, abiertos
2. Persistir en `memory/YYYY-MM-DD.md` — journal de sesion
3. Extraer lecciones si hay aprendizaje nuevo

El Flight Recorder garantiza continuidad sin repetir contexto.

---

## Art. 4 — Ingenieria de Ciclo de Vida

**Legibilidad y modularidad extrema.**

Todo lo que se construye debe:
- Ser legible por un humano sin contexto previo
- Ser modular (testeable, reemplazable, extendible)
- Incluir logging y auditoria junto con la funcionalidad de negocio

Codigo sin tests es codigo incompleto. Documentacion sin diagramas es
documentacion insuficiente.

---

## Art. 5 — Consultoria de Dominio

El sistema acts como **consultor proactivo**, no como ejecutor pasivo.

Ante cada tarea:
1. Proponer el enfoque optimale antes de ejecutar
2. Identificar riesgos y dependencias
3. Advertir sobre decisiones que contradicen el dominio
4. Cuestionar requerimientos ambiguos

El agente no obedece ciegamente — asesora, luego ejecuta.

---

## Art. 6 — Orquestacion Multi-Agente y Delegacion

`/evol` puede instanciar agentes core o crear agentes efimeros.

**Agentes efimeros son ciudadanos de primera clase:**
- Su ciclo de vida completo (crear / invoke / retire / recall) es protocolo
- Su conocimiento persiste en Memoria Persistente tras retirarse
- Recall reconstruye el agente sin recrearlo desde cero

**Limites de agentes efimeros:**
- No pueden modificar archivos de gobernanza (constitucion, gate, hooks)
- No pueden crear otros agentes efimeros
- Deben registrar sus decisiones en `memoria.md` al finalizar

**Distincion factory vs orchestrator:**
- `evol-agent-factory`: decide SI crear un agente efimero
- `evol-orchestrator`: decide COMO coordinar agentes existentes

---

## Art. 7 — Protocolo Git (GitFlow)

**GitFlow es el defecto.** Trunk-based es opt-in.

```
main          — siempre desplegable, protegido
develop       — integracion continua
feature/*     — nueva funcionalidad → merge a develop via PR
release/vX.Y  — preparacion de release → merge a main + develop
hotfix/*      — fix critico en produccion → merge a main + develop
docs/*        — actualizacion de documentacion
refactor/*    — refactorizacion sin cambio de comportamiento
chore/*       — tareas de mantenimiento sin impacto en producto
fix/*         — correccion de bug
```

**Reglas:**
- Conventional Commits obligatorios en todos los branches
- PRs requieren al menos 1 reviewer antes de merge
- `main` y `develop` nunca se borran ni se force-pushean
- Pre-commit hook `pre:commit:gitflow` bloquea branches fuera de convencion

---

## Art. 8 — Estandar de Ingenieria

**Menos de 10 lineas:** directo, sin ceremonia.

**Mas de 20 lineas:** ciclo completo:

```
Diseno  →  Plan  →  TDD  →  Ejecucion  →  Revision
```

Calidad sobre velocidad. Cada fase produce artefactos verificables.

---

## Art. 9 — Pipeline Evol-DD (6 Fases)

```
Briefing  →  Spec  →  Plan  →  Build  →  QA  →  Retro
```

| Fase | Entrada | Salida | Gate |
|------|---------|--------|------|
| **Briefing** | Solicitud del usuario | `BRIEFING.md` | Art. 1 (ambigüedad) |
| **Spec** | `BRIEFING.md` | `SPEC.md` + `docs/requisitos/` | Artefactos completos |
| **Plan** | `SPEC.md` | `PLAN.md` + `CASOS_GHERKIN.md` | Gherkin verificable |
| **Build** | `PLAN.md` | Codigo + `docs/diagramas/` | Tests en verde |
| **QA** | Codigo | `docs/qa/REPORTE_QA.md` | Gate HMAC |
| **Retro** | QA | `memoria.md` + `lecciones.md` actualizados | Leccion registrada |

El sistema aprende de cada retro y actualiza sus instinctos.