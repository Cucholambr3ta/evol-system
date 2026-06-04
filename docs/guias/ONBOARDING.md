# ONBOARDING — Guia de Incorporacion a Evol-DD

Evol-DD es un framework CLI agéntico de desarrollo. Este documento cubre los cinco pasos necesarios para tener un entorno funcional desde cero hasta el primer ciclo de trabajo completo.

---

## Paso 1 — Prerequisitos

### Obligatorios

| Herramienta | Version minima | Verificacion |
|-------------|----------------|-------------|
| Git | 2.30 | `git --version` |
| Python | 3.10 | `python3 --version` |
| Bash | 5.0 | `bash --version` |
| pip | 22.0 | `pip --version` |

Python 3.10 es el minimo porque el framework usa `match`/`case`, `X | Y` en type hints, y `tomllib` de stdlib. Versiones anteriores fallan en importacion silenciosa de `_evol_common.py`.

Git 2.30 es necesario para `git check-ignore -q` que usa `evol-doctor.sh`. Versiones anteriores no soportan la flag `-q` en ese subcomando.

### Opcionales pero recomendados

**MemPalace CLI** habilita el Modo COMPLETO del sistema. Sin él el framework opera en Modo BASE — todas las fases del pipeline funcionan, pero sin indexacion semantica ni recall automatico de contexto.

Instalacion de MemPalace:
```bash
pip install mempalace
mempalace --version
```

**GitNexus** provee analisis de blast radius y grafos de simbolos. Es opt-in obligatorio porque su licencia (PolyForm Noncommercial) es incompatible con uso comercial.

```bash
# Solo proyectos no-comerciales
export EVOL_GITNEXUS=1
npx gitnexus analyze
```

### Verificacion de prerequisitos

```bash
python3 --version   # debe ser 3.10.x o superior
git --version       # debe ser 2.30.x o superior
bash --version      # debe ser 5.x o superior
```

---

## Paso 2 — Instalacion

### Instalacion estandar (recomendada)

```bash
pipx install evol-dd && evol
```

`pipx install evol-dd` instala el framework. `evol` detecta que es la primera
ejecucion y configura automaticamente el trigger `/evol` en los 7 IDEs:
Claude Code, OpenCode, Cursor, Windsurf, VSCode Copilot, Antigravity y Codex.

Desde ese momento, abrir cualquier carpeta en cualquier IDE muestra `/evol`
disponible — sin configuracion adicional por proyecto.

### Instalacion para desarrollo del framework (Opcion B)

### Opcion B: clone + evol-init.sh (desarrollo del framework)

```bash
git clone https://github.com/Cucholambr3ta/evol-system.git evol-dd
cd evol-dd
pip install -e .
bash scripts/evol-init.sh . --profile=developer
evol doctor
```

El flag `-e` instala en modo editable: los cambios en `src/` se reflejan sin reinstalar. `--profile=developer` activa agentes efimeros, hooks, lifecycle, evolution y eval harness.

### Perfiles de instalacion

| Perfil | Extiende | Descripcion |
|--------|----------|-------------|
| `minimal` | — | Nucleo minimo con lecciones y memoria. Para CI o proyectos tiny. |
| `core` | minimal | Estandar para proyectos. Incluye agentes, gate y CI. |
| `developer` | core | Desarrollo activo con agentes efimeros, hooks y eval. |
| `security` | core | Foco en SecDD, shield y hooks estrictos. |
| `research` | core | Evolucion continua, eval harness y observabilidad. |
| `full` | developer | Instalacion completa. Todos los modulos. |
| `lean` | — | Ligero. Requiere global install previo con `evol-global-install.sh`. |

Para ver que modulos incluye cada perfil:
```bash
bash scripts/evol-init.sh . --explain=developer
```

### Instalacion global (maquinas de desarrollo compartidas)

```bash
bash scripts/evol-global-install.sh
```

Esto instala los scripts en `~/.local/bin` y configura el PATH. Necesario para el perfil `lean`.

---

## Paso 3 — Primera sesion

### 1. Leer el manifiesto de operacion

```bash
cat CLAUDE.md
```

`CLAUDE.md` es el manifiesto de operacion del sistema. Define el trigger principal (`/evol`), la tabla de workflows, los scripts disponibles y las anti-reglas del framework. Leerlo una vez es suficiente para entender la arquitectura de comandos.

### 2. Invocar el trigger en Claude Code

Con el proyecto abierto en Claude Code, el trigger `/evol` activa el orquestador principal. No es un comando de shell — es un slash command del IDE que carga el workflow correspondiente desde `.claude/commands/`.

```
/evol
```

El orquestador lee `memoria.md`, detecta el estado actual de la fase, y presenta las opciones de continuacion.

### 3. Verificar que memoria.md fue leida

La Constitucion (Art. 3) requiere leer `memoria.md` al inicio de cada sesion. El sistema lo hace automaticamente al invocar `/evol`, pero puedes verificarlo manualmente:

```bash
cat memoria.md
```

`memoria.md` contiene: identidad del proyecto, estado actual de fase, decisiones arquitectonicas clave, riesgos activos, y bitacora de sesiones. Si el archivo esta vacio o es la primera sesion, el orquestador lo inicializa.

### 4. Verificar modo de operacion

```bash
evol doctor
```

La ultima linea del output indica el modo: `[PASS]` significa que todos los checks criticos pasaron. Si ves `[FAIL]`, revisa las lineas marcadas con `[CRITICAL]` o `[HIGH]`.

Para ver el modo en JSON (util para scripts):
```bash
evol doctor --json | grep mempalace_mode
```

---

## Paso 4 — Comandos esenciales

### evol doctor

Diagnostica el entorno completo: perfil, manifiesto, archivos requeridos, permisos, scripts ejecutables, dependencias, entrypoints y artefactos legacy.

```bash
evol doctor              # output humano con colores
evol doctor --json       # output JSONL, una linea por check
```

Checks que ejecuta: `Profile`, `Manifest`, `RequiredFiles`, `Scripts`, `Permissions`, `SourceTracking`, `MemPalace`, `Entrypoints`, `Dependencies`, `LegacyArtifacts`.

### evol profile

Gestiona los perfiles de instalacion del proyecto.

```bash
evol profile list                          # lista perfiles disponibles
evol profile show                          # muestra perfil activo del proyecto
evol profile explain developer             # detalla modulos del perfil developer
evol profile init ./nuevo-proyecto core    # inicializa un proyecto nuevo
evol profile upgrade full                  # actualiza al perfil full
evol profile validate                      # verifica integridad del perfil activo
```

### evol-lessons

Motor de lecciones aprendidas. Siempre activo (no requiere variable de entorno).

```bash
# Antes de tomar una decision tecnica, busca si ya fue aprendida:
evol-lessons search "gitflow branch naming"

# Despues de un incidente o decision, registra la leccion:
evol-lessons add \
  --titulo "Gate key por proyecto no global" \
  --categoria ARQUITECTURA \
  --leccion "Usar evol gate init --from-global como punto de partida" \
  --problema "Key global elimina invariante de auditoria" \
  --causa "Simplificacion de UX sacrifico seguridad"

# Ver mejoras pendientes:
evol-lessons list --pendientes

# Proponer mejoras para una leccion existente:
evol-lessons suggest-fix "Gate key por proyecto no global"
```

### evol-memory

Motor de memoria conversacional. Requiere `EVOL_MEMORY=1`.

```bash
EVOL_MEMORY=1 evol-memory load          # carga contexto al inicio de sesion
EVOL_MEMORY=1 evol-memory summarize     # persiste sesion al journal
EVOL_MEMORY=1 evol-memory compact       # compacta cuando supera 90000 tokens
EVOL_MEMORY=1 evol-memory search QUERY  # busqueda en journales
EVOL_MEMORY=1 evol-memory gc            # elimina tool_results viejos (TTL 3 dias)
```

### evol-gate

Gate keeper con firmas HMAC-SHA256. Requerido para transiciones de fase.

```bash
evol-gate init                            # inicializa key + log en .evol/
evol-gate approve --phase briefing        # firma la aprobacion de la fase
evol-gate validate                        # verifica integridad de la cadena
evol-gate status                          # muestra el log con verificacion
evol-gate transition --from spec --to plan  # registra transicion firmada
```

### Comandos /evol en Claude Code

Estos no son comandos de shell. Se ejecutan dentro de Claude Code:

```
/evol               # orquestador principal, lee memoria.md
/evol briefing      # genera BRIEFING.md (Fase 1)
/evol spec          # genera SPEC.md + docs/requisitos/ (Fase 2)
/evol plan          # genera PLAN.md + CASOS_GHERKIN.md (Fase 3)
/evol build         # implementa codigo + docs/diagramas/ (Fase 4)
/evol qa            # genera docs/qa/REPORTE_QA.md (Fase 5)
/evol retro         # actualiza memoria.md + lecciones.md (Fase 6)
/evol research      # propone mejoras autonomas (continuo)
/evol gate status   # muestra estado de aprobaciones
/evol doc           # genera set completo de documentacion
```

---

## Paso 5 — Flujo de trabajo tipico

El pipeline de Evol-DD tiene seis fases. Cada fase produce artefactos verificables y requiere aprobacion explicita antes de avanzar.

### Briefing

El usuario describe el objetivo. El sistema detecta ambiguedad (Art. 1) y solicita clarificacion si el pedido no tiene parametros medibles.

```
/evol briefing
```

Salida: `BRIEFING.md` con objetivo, stakeholders, criterios de exito y riesgos iniciales.

### Spec

Expande el briefing a especificacion tecnica. Genera documentos de requisitos funcionales, no funcionales y restricciones.

```
/evol spec
```

Salida: `SPEC.md`, `docs/requisitos/FUNCIONALES.md`, `docs/requisitos/NO_FUNCIONALES.md`, `docs/requisitos/RESTRICCIONES.md`.

Gate de Spec requiere aprobacion explicita:
```bash
evol-gate approve --phase spec
```

### Plan

Descompone la spec en features FDD con casos Gherkin verificables.

```
/evol plan
```

Salida: `PLAN.md`, `docs/qa/CASOS_GHERKIN.md`.

### Historias de usuario (post-Plan)

Genera historias completas a partir de la documentacion granular y los wireframes.

```
/evol historias
```

Salida por historia: `acuerdos/historia-usuario-N/propuesta.md`, `requisitos-escenarios.md` (Gherkin), `escenario-tecnico.md` (Mermaid), `checklist-tareas.md` (>=50 tareas atomicas via pipeline worker-auditor).

Artefacto global: `acuerdos/sprint.md` con plan de sprints, estimaciones y DoD.

### Sprint (ciclo completo)

Ejecuta un sprint completo: equipo dinamico por componentes tecnicos, TDD estricto, auditor permanente, evaluacion pre-push y GitFlow.

```
/evol sprint --sprint=NN
```

Flujo: `sprint-start` → checklist atomico (worker+auditor) → Gherkin verde → eval pre-push → `sprint-close` → PR a develop → leer lecciones.

```bash
bash scripts/evol-gitflow.sh sprint-start --sprint=01 --title=auth
# ... implementar ...
bash scripts/evol-gitflow.sh sprint-close --sprint=01
```

### Build

Implementa el codigo guiado por TDD. Los tests deben ser verdes antes de cerrar la fase.

```
/evol build
```

Salida: Codigo en `src/`, diagramas en `docs/diagramas/`.

Verificacion obligatoria antes de gate:
```bash
pytest tests/
bash scripts/lint-workflows.sh
python3 scripts/validate-registry.py --strict
```

### QA

Genera el reporte de calidad con casos ejecutados, cobertura y gaps.

```
/evol qa
```

Salida: `docs/qa/REPORTE_QA.md`.

Gate de QA firma el cierre:
```bash
evol-gate approve --phase qa
```

### Retro

Actualiza la memoria del proyecto y extrae lecciones para el sistema de aprendizaje continuo.

```
/evol retro
```

Salida: `memoria.md` actualizado, `lecciones.md` con nuevas entradas.

---

## Crear el primer agente efimero

Los agentes efimeros son especialistas temporales creados para una tarea especifica. Se retiran cuando la tarea termina pero su conocimiento persiste.

```bash
# Crear agente especializado en migracion de base de datos
evol-agent create \
  --name "db-migration-specialist" \
  --task "Disenar e implementar migracion de PostgreSQL 13 a 15 con zero-downtime"

# Invocar el agente para una tarea concreta
evol-agent invoke db-migration-specialist \
  "Revisar script de migracion en migrations/v2_upgrade.sql"

# Retirar cuando la tarea termina (conocimiento persiste en MemPalace)
evol-agent retire db-migration-specialist

# Recall posterior sin recrear desde cero
evol-agent recall db-migration-specialist
```

Los archivos de agentes efimeros se generan en `prompts/agents/ephemeral/` con el template de `templates/agent.template.md`. El registro se actualiza en `prompts/agents/registry.json`.

Restricciones de agentes efimeros (Art. 6 de la Constitucion):
- No pueden modificar archivos de gobernanza (`docs/constitucion.md`, `.evol/.gate-key`, hooks).
- No pueden crear otros agentes efimeros.
- Deben registrar sus decisiones en `memoria.md` al finalizar.

---

## Añadir la primera leccion

```bash
evol-lessons add \
  --titulo "Descripcion breve de lo aprendido" \
  --categoria PROCESO \
  --problema "Que fallo o sorprendio" \
  --causa "Por que paso" \
  --leccion "Regla aplicable a futuras decisiones" \
  --aplica "Ambito donde aplica"
```

Categorias validas: `ARQUITECTURA`, `SEGURIDAD`, `DOMINIO`, `TESTING`, `DEVOPS`, `PROCESO`, `HERRAMIENTAS`.

El sistema aplica deduplicacion por similitud de Jaccard (umbral 0.7) para evitar entradas duplicadas.

---

## Activar memoria conversacional

```bash
# Sesion con memoria activa
EVOL_MEMORY=1 evol-memory load

# Al terminar la sesion, persistir:
EVOL_MEMORY=1 evol-memory summarize

# Para activar de forma persistente en el proyecto:
echo 'EVOL_MEMORY=1' >> .env
```

La memoria conversacional usa stdlib Python puro sin dependencias externas. Almacena:
- `AGENT_MEMORY.md` — memoria de largo plazo del agente
- `memory/YYYY-MM-DD.md` — journal diario de sesion
- `dialog/` — mensajes en crudo (gitignored)
- `tool_result/` — resultados de herramientas (gitignored, TTL 3 dias)

---

## Mantener el sistema actualizado

```bash
pipx upgrade evol-dd && evol
```

Al detectar una nueva version instalada, `evol` reinstala los triggers
actualizados en todos los IDEs automaticamente.

Para propagar actualizaciones a un proyecto especifico:
```bash
evol update apply   # actualiza paquete + propaga workflows al proyecto activo
```
