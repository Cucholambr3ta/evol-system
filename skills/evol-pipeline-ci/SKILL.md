---
name: evol-pipeline-ci
description: Pipeline-Driven Development — CI/CD pipeline design, workflow optimization, parallel execution
category: discipline-extended
trigger: /pipeline-ci
---

# evol-pipeline-ci

## Fase del Pipeline

**Build (Fase 4) — Construcción e Integración**

Activar cuando se necesita diseñar o optimizar pipelines CI/CD:
- Diseño de workflows (GitHub Actions, GitLab CI)
- Optimización de ejecución paralela
- Caching y artifact management
- Gate de calidad automatizado

## Artefacto Clave

**`.github/workflows/` or `.gitlab-ci.yml`**

```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make lint

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test-unit

  test-integration:
    needs: [lint]
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
    steps:
      - uses: actions/checkout@v4
      - run: make test-integration

  build:
    needs: [test-unit, test-integration]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make docker-build
```

## Flujo de Trabajo

```bash
# 1. Analizar pipelines existentes
ls -la .github/workflows/ .gitlab-ci.yml Jenkinsfile 2>/dev/null

# 2. Generar pipeline base
python3 scripts/pipeline-ci/generate.py \
  --type github-actions \
  --language python \
  --output .github/workflows/ci.yml

# 3. Optimizar ejecución
python3 scripts/pipeline-ci/optimize.py \
  --file .github/workflows/ci.yml \
  --output .github/workflows/ci-optimized.yml

# 4. Validar sintaxis
actionlint .github/workflows/*.yml

# 5. Analizar tiempos de ejecución
python3 scripts/pipeline-ci/analyze-duration.py \
  --file .github/workflows/ci.yml \
  --output docs/ci/DURATION_REPORT.md

# 6. Generar cache strategy
python3 scripts/pipeline-ci/cache-strategy.py \
  --file .github/workflows/ci.yml \
  --output docs/ci/CACHE_STRATEGY.md
```

### Parallel Execution Pattern

```yaml
# Parallel jobs
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]
  
  test-unit:
    runs-on: ubuntu-latest
    steps: [...]
  
  security-scan:
    runs-on: ubuntu-latest
    steps: [...]
  
  build:
    needs: [lint, test-unit, security-scan]
    steps: [...]
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | CI requirements | Pipelines necesarios identificados | No |
| Spec | Pipeline design | Workflows definidos | Sí |
| Plan | Optimización | Jobs paralelos planificados | Sí |
| Build | Pipeline ejecutable | CI passing | Sí |
| QA | Quality gates | Lint, test, security pass | Sí |
| Retro | Pipeline metrics | Tiempos y costos analizados | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Build del Pipeline
- **Discipline Doc** — `docs/disciplines/Pipeline_CI.md`
- **GitHub Actions Docs** — https://docs.github.com/en/actions
- **GitLab CI Docs** — https://docs.gitlab.com/ee/ci/


## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
