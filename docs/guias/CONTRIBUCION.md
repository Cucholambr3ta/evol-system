# CONTRIBUCION — Guia de Contribucion a Evol-DD

Esta guia define el proceso completo para contribuir al framework: desde la creacion de una branch hasta el merge al trunk. Cubre GitFlow, conventional commits, requisitos de PR, y los tres tipos principales de contribucion: workflows, agentes core y skills.

---

## Flujo GitFlow

Evol-DD usa GitFlow como protocolo por defecto (Art. 7 de la Constitucion). Trunk-based es opt-in para proyectos que lo requieran explicitamente.

### Estructura de branches

```
main          — siempre desplegable, protegido, nunca force-push
develop       — integracion continua, rama de trabajo principal
feature/*     — nueva funcionalidad → merge a develop via PR
release/vX.Y  — preparacion de release → merge a main + develop
hotfix/*      — fix critico desde main → merge a main + develop
docs/*        — actualizacion de documentacion
refactor/*    — refactorizacion sin cambio de comportamiento
chore/*       — tareas de mantenimiento sin impacto en producto
fix/*         — correccion de bug
```

`main` y `develop` nunca se borran ni se force-pushean. El pre-commit hook `pre:commit:gitflow` bloquea commits en branches que no siguen la convencion.

### Comandos completos

**Nueva feature:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/nombre-descriptivo

# ... trabajo ...

git add <archivos>
git commit -m "feat(scope): descripcion breve"
git push origin feature/nombre-descriptivo

# Abrir PR: feature/nombre-descriptivo → develop
```

**Hotfix critico:**
```bash
git checkout main
git pull origin main
git checkout -b hotfix/descripcion-breve

# ... fix ...

git commit -m "fix(scope): descripcion del fix"
git push origin hotfix/descripcion-breve

# PR 1: hotfix/descripcion-breve → main
# PR 2: hotfix/descripcion-breve → develop
```

**Release:**
```bash
git checkout develop
git pull origin develop
git checkout -b release/v0.2.0

# Actualizar VERSION, CHANGELOG.md
python3 scripts/bump-version.py 0.2.0

git commit -m "chore(release): bump to 0.2.0"
git push origin release/v0.2.0

# PR 1: release/v0.2.0 → main (con tag vX.Y.Z)
# PR 2: release/v0.2.0 → develop
```

---

## Conventional Commits

Todos los commits deben seguir la especificacion Conventional Commits. El hook `pre:commit:gitflow` verifica el formato antes de aceptar el commit.

### Formato

```
<tipo>(<scope>): <descripcion breve en imperativo>

[body opcional: contexto del cambio]

[footer opcional: BREAKING CHANGE, closes #123]
```

### Tipos obligatorios

| Tipo | Cuando usar | Impacto en CHANGELOG |
|------|-------------|---------------------|
| `feat` | Nueva funcionalidad visible para el usuario | Si |
| `fix` | Correccion de bug | Si |
| `docs` | Solo cambios en documentacion | No |
| `chore` | Mantenimiento sin impacto en producto (deps, build) | No |
| `test` | Agregar o corregir tests | No |
| `refactor` | Refactorizacion sin cambio de comportamiento | No |
| `perf` | Mejora de rendimiento | Si |
| `ci` | Cambios en la configuracion de CI/CD | No |
| `style` | Formato de codigo (espacios, punto y coma) | No |
| `revert` | Revertir un commit previo | Si |

### Ejemplos correctos

```bash
git commit -m "feat(agent): add recall command to evol-agent-lifecycle"
git commit -m "fix(gate): prevent timing attack in signature comparison"
git commit -m "docs(onboarding): add ephemeral agent creation example"
git commit -m "refactor(lessons): extract jaccard_similarity to common utils"
git commit -m "test(gate): add negative test for tampered log entry"
git commit -m "chore(deps): pin jsonschema to 4.17.x"
```

### Breaking changes

```bash
git commit -m "feat(gate)!: change payload schema to include nonce

BREAKING CHANGE: existing gate logs are incompatible with new schema.
Run evol-gate migrate before upgrading."
```

---

## Requisitos de PR

Todo PR debe pasar los siguientes checks antes del merge. Estos son gates reales en CI, no recomendaciones.

### 1. pytest verde

```bash
pytest tests/ -v
```

El suite incluye tests unitarios en `tests/test_*.py` y tests de integracion en `tests/*.bats`. Todos deben pasar. No se aceptan `|| true` ni tests con `skip` no justificado.

### 2. lint-workflows.sh sin errores

```bash
bash scripts/lint-workflows.sh
```

Verifica que todos los workflows en `.agent/workflows/` tienen frontmatter YAML valido y estan registrados en el catalogo. Exit code 0 es el unico resultado aceptable.

### 3. validate-registry.py --strict OK

```bash
python3 scripts/validate-registry.py --strict
```

Valida que `prompts/agents/registry.json` cumple el schema JSON, que todos los `id` son unicos, que los `prompt_file` referenciados existen, y que no hay propiedades no permitidas por el schema. `--strict` activa todas las validaciones incluyendo referencias cruzadas.

### 4. evol-doctor sin HIGH ni CRITICAL

```bash
evol doctor
```

Si el output termina en `[FAIL]`, el PR no puede hacer merge. Resolver todos los checks `CRITICAL` y `HIGH` antes de abrir el PR.

### 5. evol-shield sin regresiones

```bash
python3 scripts/evol-shield.py audit --ci --no-write
```

En modo `--ci` el shield retorna exit code 1 si encuentra violaciones de severidad CRITICAL o HIGH. `--no-write` evita modificar archivos durante el CI run.

---

## Como añadir un workflow

Los workflows son el SSoT de los comandos del framework. Se definen una vez y se generan para todos los IDEs.

### Estructura de un workflow

```
.agent/workflows/
  nombre-workflow.md    # SSoT — el unico archivo a editar manualmente
```

Cada workflow es un archivo Markdown con frontmatter YAML obligatorio:

```yaml
---
name: nombre-workflow
description: Descripcion de una linea
trigger: /evol nombre-workflow
phase: build
produces:
  - ARTEFACTO.md
requires:
  - SPEC.md
---
```

Despues del frontmatter va el cuerpo del workflow: instrucciones para el agente, pasos, criterios de salida, y referencias a artefactos.

### Pasos para agregar un workflow

```bash
# 1. Crear el archivo SSoT
vim .agent/workflows/mi-workflow.md

# 2. Verificar que el frontmatter es valido
bash scripts/lint-workflows.sh

# 3. Regenerar los adapters para todos los IDEs
bash scripts/evol-adapt.sh all

# Esto genera:
#   .claude/commands/mi-workflow.md    (Claude Code)
#   .opencode/commands/mi-workflow.md  (OpenCode)
#   .cursor/rules/mi-workflow.md       (Cursor)
#   etc.
```

Nunca editar los archivos generados en `.claude/commands/`, `.opencode/`, `.cursor/`, etc. directamente. Son outputs de `evol-adapt.sh`. Los cambios se pierden en el proximo `evol-adapt.sh all`.

### Targets de evol-adapt.sh

```bash
bash scripts/evol-adapt.sh claude-code    # solo Claude Code
bash scripts/evol-adapt.sh opencode       # solo OpenCode
bash scripts/evol-adapt.sh cursor         # solo Cursor
bash scripts/evol-adapt.sh windsurf       # solo Windsurf
bash scripts/evol-adapt.sh vscode-copilot # solo VSCode Copilot
bash scripts/evol-adapt.sh antigravity    # solo Antigravity
bash scripts/evol-adapt.sh codex          # solo Codex
bash scripts/evol-adapt.sh all            # todos (recomendado)
bash scripts/evol-adapt.sh all --dry-run  # ver sin generar
```

---

## Como añadir un agente core

Los 16 agentes core son permanentes. Anadir uno aumenta a 17. Esta operacion es infrecuente y requiere deliberacion.

### Crear el archivo del agente

Los agentes core viven en `prompts/agents/core/`. El archivo sigue el formato:

```markdown
# Nombre del Agente

## Mision
Una oracion que define el proposito unico del agente.

## Reglas de Operacion
1. Regla operativa especifica.
2. Otra regla.

## Limites
- No puede hacer X.
- No puede hacer Y.

## Contexto de Trabajo
Que archivos lee. Que artefactos produce.

## Activacion
Como se invoca este agente. Que señal lo activa.
```

### Registrar en registry.json

```bash
# Editar prompts/agents/registry.json
# Agregar entrada al array "agents":
{
  "id": "evol-nombre",
  "name": "evol-nombre",
  "category": "core",
  "description": "Descripcion de una linea",
  "prompt_file": "prompts/agents/core/nombre.md",
  "capabilities": ["lista", "de", "capacidades"],
  "triggers": ["/evol nombre"]
}

# Validar que el schema es correcto
python3 scripts/validate-registry.py --strict

# Regenerar equipo.md
bash scripts/generate-equipo.sh
```

### Verificar

```bash
python3 scripts/validate-registry.py --strict
cat docs/equipo.md  # debe reflejar el nuevo agente
evol doctor         # no debe reportar HIGH ni CRITICAL
```

---

## Como añadir una skill

Las skills son capacidades reutilizables que extienden el sistema. El flujo de creacion pasa por un loop iterativo: draft, evals, optimize, adapt.

### Loop de creacion

```bash
# Paso 1: Draft inicial
# En Claude Code:
/crear-skill

# El workflow genera:
#   skills/nombre-skill/SKILL.md
#   evals/nombre-skill/cases.jsonl
#   evals/nombre-skill/grader.yaml

# Paso 2: Ejecutar evals
python3 scripts/evol-eval.py run --suite nombre-skill

# Paso 3: Revisar resultados y optimizar
python3 scripts/evol-eval.py report --suite nombre-skill

# Paso 4: Cuando los evals pasan, regenerar adapters
bash scripts/evol-adapt.sh all
```

### Estructura de una skill

```
skills/
  nombre-skill/
    SKILL.md          # definicion de la skill
evals/
  nombre-skill/
    cases.jsonl       # casos de prueba (required)
    grader.yaml       # criterios de evaluacion (required)
```

`SKILL.md` define: nombre, descripcion, cuando usar, pasos de ejecucion, y criterios de exito. `cases.jsonl` contiene al menos: happy path, error case y edge case. `grader.yaml` define el tipo de grader: `structural`, `behavioral`, `output_match` o `pass_at_k`.

### Verificar antes del PR

```bash
python3 scripts/evol-eval.py validate --suite nombre-skill
python3 scripts/evol-eval.py run --suite nombre-skill
python3 scripts/evol-shield.py audit --ci --no-write  # no debe detectar refs a internals
```

---

## Code Review Checklist

Segun DOC_STANDARD.md, todo PR que modifique documentacion debe cumplir:

### Cero emojis

```bash
grep -rP "[\x{1F000}-\x{1FAFF}]" docs/
# debe retornar 0 resultados
```

### Mermaid donde aplique

Documentos en `docs/arquitectura/` requieren diagramas Mermaid (C4, secuencia, estado o componentes). Documentos en `docs/diagramas/` son exclusivamente Mermaid.

```bash
grep -L '```mermaid' docs/arquitectura/*.md
# debe retornar 0 archivos
```

### Tablas para datos estructurados

Requisitos, casos de prueba, matrices de trazabilidad, controles de seguridad y metricas deben usar tablas Markdown, no listas de bullets sin estructura.

### Profundidad sustantiva

Cada seccion debe tener sub-secciones con contenido real. Los bullets sin desarrollo no son documentacion — son indices. Expandir con contexto, ejemplos y razonamiento.

### Trazabilidad bidireccional

Si el PR toca requisitos o casos de prueba, verificar que la matriz en `docs/qa/MATRIZ_TRAZABILIDAD.md` refleja las nuevas relaciones REQ-NNN <-> TC-NNN en ambas direcciones.

### Checklist de PR minimo

```
[ ] pytest tests/                           pasa sin errores
[ ] bash scripts/lint-workflows.sh          retorna 0
[ ] python3 scripts/validate-registry.py    retorna 0 con --strict
[ ] evol doctor                             sin HIGH ni CRITICAL
[ ] evol-shield audit --ci --no-write       sin CRITICAL ni HIGH
[ ] zero emojis en documentacion modificada
[ ] mermaid presente si el doc es arquitectura
[ ] memoria.md actualizada si hay decision arquitectonica
[ ] lecciones.md actualizada si hay aprendizaje nuevo
[ ] Conventional Commit en todos los commits del branch
```
