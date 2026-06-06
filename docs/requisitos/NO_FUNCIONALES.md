# Requisitos No Funcionales — Evol-DD

## Resumen

Este documento especifica los requisitos no funcionales del framework Evol-DD.

## Convenciones

| Campo | Formato |
|-------|---------|
| ID | NFR-NNN (tres digitos) |
| Categoria | RENDIMIENTO / DISPONIBILIDAD / SEGURIDAD / PORTABILIDAD / MANTENIBILIDAD / OBSERVABILIDAD |
| Metrica | Parametro medible |
| Umbral | Valor objetivo |
| Prioridad | ALTA / MEDIA / BAJA |

---

## NFR-001: Rendimiento — Tiempo de Inicializacion

| Campo | Valor |
|-------|-------|
| ID | NFR-001 |
| Categoria | RENDIMIENTO |
| Metrica | Tiempo de ejecucion de `evol-doctor.sh` |
| Umbral | < 5 segundos |
| Prioridad | MEDIA |
| Validacion | Manual |

### Descripcion

El comando de diagnostico debe ejecutarse en menos de 5 segundos para mantener productividad del desarrollador.

### Criterio

```
time bash scripts/evol-doctor.sh
# Real: < 5s
```

### Dependencias

- Ninguna (script stdlib)

---

## NFR-002: Rendimiento — Tiempo de Bootstrap

| Campo | Valor |
|-------|-------|
| ID | NFR-002 |
| Categoria | RENDIMIENTO |
| Metrica | Tiempo de ejecucion de `evol-init.sh` para bootstrap |
| Umbral | < 30 segundos |
| Prioridad | ALTA |
| Validacion | CI |

### Descripcion

El bootstrap de un nuevo proyecto debe completarse en menos de 30 segundos para no obstaculizar flujos de trabajo rapidos.

### Criterio

```
time bash scripts/evol-init.sh /tmp/test --profile=core
# Real: < 30s
```

---

## NFR-003: Disponibilidad — Modo BASE

| Campo | Valor |
|-------|-------|
| ID | NFR-003 |
| Categoria | DISPONIBILIDAD |
| Metrica | Porcentaje de features disponibles sin Memoria Persistente |
| Umbral | 100% de features core |
| Prioridad | ALTA |
| Validacion | Test |

### Descripcion

El sistema debe funcionar completamente sin Memoria Persistente. El Modo BASE debe tener todas las features del Modo COMPLETO excepto busqueda semantica y recall semantico.

### Features disponibles en Modo BASE

| Feature | Modo COMPLETO | Modo BASE |
|---------|--------------|-----------|
| Scripts | Si | Si |
| 16 Core Agents | Si | Si |
| Agent Lifecycle | Si | Si |
| Gate Keeper | Si | Si |
| Pipeline 6 fases | Si | Si |
| memoria.md | Si | Si |
| lecciones.md | Si | Si |
| evol-memory.py | Si | Si |
| evol-lessons.py | Si | Si |
| evol-evolve.py | Si | Si |
| evol-researcher.py | Si | Si |
| Busqueda RAG | Si | No |
| Recall semantico | Si | No (JSON only) |
| Pattern-extraction auto | Si | Manual |

### Validacion

```bash
# Sin Memoria Persistente
PATH="" bash scripts/evol-doctor.sh
# Output: [BASE]
# Exit: 0
```

---

## NFR-004: Seguridad — Con MCP

| Campo | Valor |
|-------|-------|
| ID | NFR-004 |
| Categoria | SEGURIDAD |
| Metrica | Numero de referencias a mcpServers/mcp.json en configs generadas |
| Umbral | 0 |
| Prioridad | CRITICAL |
| Validacion | CI |

### Descripcion

Ningun archivo de configuracion generado por evol-adapt.sh debe contener referencias a servidores MCP. Zero tolerance.

### Criterio

```bash
grep -rn 'mcpServers\|mcp\.json\|xdd-mcp-server\|evol-mcp-server' \
  .claude/ .opencode/ .cursor/ .windsurf/ \
  --include='*.md' --include='*.json' --include='*.yml' \
  | wc -l
# Resultado: 0
```

### Excepciones


- Archivos .md en prompts/agents/ NO son configs generadas

---

## NFR-005: Seguridad — Sin Secrets

| Campo | Valor |
|-------|-------|
| ID | NFR-005 |
| Categoria | SEGURIDAD |
| Metrica | Numero de secrets hardcoded detectados |
| Umbral | 0 |
| Prioridad | CRITICAL |
| Validacion | CI (gitleaks) |

### Descripcion

Ningun secret (API keys, passwords, tokens) debe estar hardcoded en el codigo.

### Criterio

```bash
gitleaks detect --no-git
# Resultado: 0 secrets
```

### Contramedidas

- evol-shield.py ejecuta gitleaks en audit
- CI bloquea merge si gitleaks encuentra secrets
- Patternos detectados: api_key=, password=, token= con valores de longitud > 20

---

## NFR-006: Portabilidad — Rutas Relativas

| Campo | Valor |
|-------|-------|
| ID | NFR-006 |
| Categoria | PORTABILIDAD |
| Metrica | Porcentaje de archivos con rutas relativas |
| Umbral | 100% |
| Prioridad | ALTA |
| Validacion | Review |

### Descripcion

Todos los archivos generados deben usar rutas relativas. Ninguna ruta absoluta del host.

### Criterio

```bash
# Verificar scripts
grep -rn '/home/' scripts/ .agent/
# Resultado: 0 (excepto excepciones documentadas)

# Verificar configs
grep -rn '/home/' .claude/ .opencode/ .cursor/
# Resultado: 0
```

### Excepciones documentadas

- `EVOL_STATE_DB = os.path.expanduser("~/.evol/state.db")` en _evol_common.py
- Rutas en tests de integracion que explicitan /tmp/

---

## NFR-007: Mantenibilidad — Max Lineas Funcion

| Campo | Valor |
|-------|-------|
| ID | NFR-007 |
| Categoria | MANTENIBILIDAD |
| Metrica | Numero de funciones con mas de 10 lineas (sin comments) |
| Umbral | 0 en scripts nuevos |
| Prioridad | MEDIA |
| Validacion | CI (pylint, custom) |

### Descripcion

Funciones pequenas y enfocadas: max 10 lineas de logica (sin comments, sin blank lines).

### Regla

- < 10 lineas: directo
- >= 10 lineas: requiere ciclo Design-Plan-TDD-Review

### Criterio

```python
# En evol-*.py:
def small_function():
    line1
    line2
    line3  # max 9 lineas de codigo
```

---

## NFR-008: Observabilidad — Traces NDJSON

| Campo | Valor |
|-------|-------|
| ID | NFR-008 |
| Categoria | OBSERVABILIDAD |
| Metrica | Archivos de trace en .evol/traces/ |
| Umbral | Sesiones grabadas en NDJSON |
| Prioridad | MEDIA |
| Validacion | Test |

### Descripcion

El sistema debe grabar traces de sesion en formato NDJSON para replay y debugging.

### Formato

```json
{"timestamp":"2026-06-02T10:00:00Z","event":"session_start","agent":"orchestrator"}
{"timestamp":"2026-06-02T10:00:01Z","event":"delegate","to":"architect","task":"design"}
{"timestamp":"2026-06-02T10:05:00Z","event":"delegate","to":"builder","task":"implement"}
{"timestamp":"2026-06-02T10:30:00Z","event":"session_end","duration":1800}
```

### Ubicacion

- `.evol/traces/<session-id>.jsonl`
- Gitignored (runtime, no versionable)

---

## NFR-009: Disponibilidad — Modo Memory (opt-in)

| Campo | Valor |
|-------|-------|
| ID | NFR-009 |
| Categoria | DISPONIBILIDAD |
| Metrica | Sistema funciona con EVOL_MEMORY=1 sin dependencias externas |
| Umbral | 100% |
| Prioridad | MEDIA |
| Validacion | Test |

### Descripcion

El sistema de memoria conversacional (evol-memory.py) debe funcionar con stdlib Python puro, sin dependencias externas.

### Dependencias разрешены

- sqlite3 (stdlib)
- os, sys, json, datetime, pathlib (stdlib)

### Dependencias NO разрешены

- No external packages (no pip install)

---

## NFR-010: Seguridad — Supply Chain Scan

| Campo | Valor |
|-------|-------|
| ID | NFR-010 |
| Categoria | SEGURIDAD |
| Metrica | Skills instaladas tienen scan de seguridad |
| Umbral | 100% de skills externas |
| Prioridad | HIGH |
| Validacion | CI |

### Descripcion

Toda skill instalada via evol-evolve.py install-skill debe pasar scan de supply-chain.

### Criterio

```bash
# Antes de install-skill
gitleaks detect --no-git <skill-dir>
semgrep --config auto <skill-dir>

# Si alguno falla: BLOCK install
```

### Contramedida

- evol-evolve.py install-skill ejecuta gitleaks + semgrep antes de copiar
- Si scan falla: error con motivo especifico
- Skills con scan_skipped: true si herramientas no instaladas

---

## NFR-011: Rendimiento — Gate Validation

| Campo | Valor |
|-------|-------|
| ID | NFR-011 |
| Categoria | RENDIMIENTO |
| Metrica | Tiempo de validacion de gate |
| Umbral | < 1 segundo |
| Prioridad | MEDIA |
| Validacion | Test |

### Descripcion

La validacion de gate (HMAC-SHA256) debe ser rapida para no obstaculizar flujo de trabajo.

### Criterio

```bash
time python3 scripts/evol-gate.py validate
# Real: < 1s
```

---

## NFR-012: Escalabilidad — Max Agentes Concurrentes

| Campo | Valor |
|-------|-------|
| ID | NFR-012 |
| Categoria | RENDIMIENTO |
| Metrica | Max workers en orquestacion paralela |
| Umbral | 5 |
| Prioridad | MEDIA |
| Validacion | Code review |

### Descripcion

El orquestador no debe exceder 5 workers en paralelo para evitar resource contention.

### Implementacion

```python
ThreadPoolExecutor(max_workers=5)
```

---

## NFR-013: Compatibilidad — Python Version

| Campo | Valor |
|-------|-------|
| ID | NFR-013 |
| Categoria | PORTABILIDAD |
| Metrica | Python version soportada |
| Umbral | 3.10, 3.11, 3.12 |
| Prioridad | ALTA |
| Validacion | CI matrix |

### Descripcion

El sistema debe funcionar en Python 3.10, 3.11 y 3.12.

### Criterio

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

---

## NFR-014: Compatibilidad — IDEs Soportados

| Campo | Valor |
|-------|-------|
| ID | NFR-014 |
| Categoria | PORTABILIDAD |
| Metrica | IDEs con configs generadas |
| Umbral | 7 IDEs |
| Prioridad | ALTA |
| Validacion | Test |

### IDEs

| IDE | Mecanismo | Generado por |
|-----|-----------|--------------|
| claude-code | Slash commands | evol-adapt.sh |
| opencode | Slash commands | evol-adapt.sh |
| cursor | @-mention | evol-adapt.sh |
| windsurf | Slash natives | evol-adapt.sh |
| vscode-copilot | Slash /chat | evol-adapt.sh |
| antigravity | Skills locales | evol-adapt.sh |
| codex | Skills globales | evol-adapt.sh |

---

## NFR-015: Seguridad — GitFlow Enforcement

| Campo | Valor |
|-------|-------|
| ID | NFR-015 |
| Categoria | SEGURIDAD |
| Metrica | Commits fuera de convencion bloqueados |
| Umbral | 100% |
| Prioridad | HIGH |
| Validacion | CI |

### Descripcion

El pre-commit hook debe bloquear commits en branches que no siguen convencion.

### Criterio

```bash
git commit -m "fix: something" -b feature/test
# Resultado: bloqueado si branch no sigue feature/*, fix/*, etc
```

### Branches permitidos

- main
- develop
- feature/*
- fix/*
- hotfix/*
- release/*
- chore/*
- docs/*
- refactor/*

---

## Matriz Resumen

| ID | Categoria | Metrica | Umbral | Prioridad | Validacion |
|----|-----------|---------|--------|-----------|------------|
| NFR-001 | RENDIMIENTO | doctor time | < 5s | MEDIA | Manual |
| NFR-002 | RENDIMIENTO | init time | < 30s | ALTA | CI |
| NFR-003 | DISPONIBILIDAD | features sin Memoria Persistente | 100% | ALTA | Test |
| NFR-004 | SEGURIDAD | refs MCP | 0 | CRITICAL | CI |
| NFR-005 | SEGURIDAD | secrets | 0 | CRITICAL | CI |
| NFR-006 | PORTABILIDAD | rutas relativas | 100% | ALTA | Review |
| NFR-007 | MANTENIBILIDAD | lineas/funcion | <= 10 | MEDIA | CI |
| NFR-008 | OBSERVABILIDAD | traces NDJSON | Sesiones | MEDIA | Test |
| NFR-009 | DISPONIBILIDAD | memory stdlib | 100% | MEDIA | Test |
| NFR-010 | SEGURIDAD | supply scan | 100% | HIGH | CI |
| NFR-011 | RENDIMIENTO | gate validate | < 1s | MEDIA | Test |
| NFR-012 | RENDIMIENTO | max workers | 5 | MEDIA | Review |
| NFR-013 | PORTABILIDAD | python version | 3.10-3.12 | ALTA | CI |
| NFR-014 | PORTABILIDAD | IDEs soportados | 7 | ALTA | Test |
| NFR-015 | SEGURIDAD | gitflow blocks | 100% | HIGH | CI |

**Total: 15 requisitos no funcionales**