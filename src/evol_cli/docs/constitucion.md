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

| Fase | Trigger | Entrada | Salida (ruta real) | Gate |
|------|---------|---------|-------------------|------|
| **0.5. Idea** | `/evol idea` | Solicitud del usuario | `acuerdos/idea/<atomos>.md` + `acuerdos/idea/INDEX.md` | Art. 1 (ambiguedad) |
| **0.7. Discovery** | `/evol discovery` | `acuerdos/idea/INDEX.md` | `acuerdos/discovery/<tema>/investigacion.md` + `investigacion-validada.md` | Fuentes citadas |
| **1. Briefing** | `/evol briefing` | `acuerdos/discovery/INDEX.md` | `acuerdos/idea/` (14 atomos D01-D14) + `acuerdos/design/` (3 tokens) + `acuerdos/wireframes/` (N html) | 14 atomos + design aprobado |
| **2. Spec** | `/evol doc-granular` | `acuerdos/idea/` completo | `acuerdos/proyecto/<dominio>/<subdominio>.md` + `acuerdos/research/<dominio>/` | Worker != auditor, 80+ lineas, Mermaid, Gherkin |
| **3. Plan** | `/evol historias` | `acuerdos/proyecto/INDEX.md` + `acuerdos/wireframes/` | `acuerdos/historia-usuario-N/` (4 artefactos) + `acuerdos/sprints/INDEX.md` | Gherkin verificable |
| **4. Build** | `/evol build` | Historias de usuario | Codigo + `acuerdos/memoria/sprint-NN.md` | Tests en verde |
| **5. QA** | `/evol qa` | Codigo | `docs/qa/REPORTE_QA.md` + `acuerdos/memoria/sprint-NN.md` | Shield 0 CRITICAL |
| **6. Retro** | `/evol retro` | QA | `acuerdos/memoria/sprint-NN.md` + `acuerdos/lecciones/sprint-NN.md` + `memoria.md` + `lecciones.md` | Leccion registrada |

### Mapeo: Input del usuario → Workflow → Ruta de salida

| Tipo de input | Workflow a ejecutar | Ruta de salida |
|---------------|--------------------|----|
| Idea vaga ("quiero hacer X") | `/evol idea` + `/evol discovery` | `acuerdos/idea/` + `acuerdos/discovery/` |
| Prompt de investigacion con links | `/evol doc-granular` (PASO 1) | `acuerdos/research/<dominio>/<nombre>/` |
| "Implementar feature X" | Verificar fase actual del pipeline | Segun fase |
| "Cerrar sprint" | `/evol retro` | `acuerdos/memoria/` + `acuerdos/lecciones/` |
| "Actualizar memoria" | `/update-memory` | `acuerdos/memoria/` atomos + MEMORY.md |

El sistema integra **31 disciplinas *-Driven Development*** (9 base + 22 extendidas activables por
caso de uso) como capas sobre estas 6 fases. El registro canonico, con la fase, el ejecutor y las
fuentes de respaldo de cada disciplina, reside en [`docs/disciplinas/INDEX.md`](./disciplinas/INDEX.md).
Cada proyecto declara en `evol.profile.yml` (bloque `methodologies:`) el subconjunto que aplica; el
orquestador inyecta solo esas capas en su fase correspondiente. Toda ficha de disciplina y todo
documento producto de investigacion web cita el link de su fuente (DOC_STANDARD 1.7).

El sistema aprende de cada retro y actualiza sus instinctos.