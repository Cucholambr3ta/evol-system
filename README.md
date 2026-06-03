# Evol-DD

> El framework de desarrollo agéntico que aprende con cada proyecto que construye.

[![PyPI](https://img.shields.io/pypi/v/evol-dd)](https://pypi.org/project/evol-dd/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitFlow](https://img.shields.io/badge/branching-GitFlow-orange)](docs/constitucion.md)

---

## Por que Evol-DD

La mayoria de frameworks de IA tienen 180+ agentes permanentes en disco, dependen de
servidores MCP, y olvidan todo lo que aprendieron en la sesion anterior.

Evol-DD es diferente en cuatro puntos concretos:

| Problema comun | Solucion Evol-DD |
|----------------|-----------------|
| Agentes: demasiados, todo permanente | 16 agentes core + efimeros bajo demanda |
| Sin memoria entre sesiones | AGENT_MEMORY.md + journals diarios nativos |
| Errores que se repiten | Motor de lecciones con ciclo de mejora continua |
| Skills que no crecen | Loop iterativo de creacion con evals y 7 IDEs |

---

## Memoria que persiste

El agente recuerda lo que hiciste la semana pasada. Sin repetir contexto.

```bash
# Al iniciar sesion, el agente carga automaticamente:
EVOL_MEMORY=1 bash scripts/evol-start.sh
# → AGENT_MEMORY.md (long-term: preferencias, patrones, decisiones clave)
# → memory/2026-06-02.md (journal del dia anterior)

# Buscar en el historial de sesiones pasadas:
python3 scripts/evol-memory.py search "decision sobre base de datos"
```

La memoria vive en tu repo, en archivos Markdown que puedes leer y editar.
No hay servidor, no hay API key requerida para el modo basico.

---

## Lecciones que se acumulan

Cada error se convierte en regla. Cada regla se mejora con el investigador.

```bash
# Registrar una leccion tras resolver un bug
python3 scripts/evol-lessons.py add \
  --titulo "Gate key comprometida afecta todos los proyectos" \
  --categoria SEGURIDAD \
  --contexto "Key global compartida entre proyectos" \
  --problema "Un leak compromete todos los proyectos del usuario" \
  --leccion "Gate key debe ser por proyecto, --from-global solo como inicio" \
  --aplica "Todo proyecto con evol-gate.py"

# El investigador propone como mejorar esa leccion
python3 scripts/evol-lessons.py suggest-fix "Gate key comprometida" --apply

# Antes de tomar una decision arquitectonica, consultar lecciones relevantes
python3 scripts/evol-lessons.py search "seguridad autenticacion"
```

---

## Agentes precisos, efimeros

Crea un especialista para la tarea. Retiralo al terminar. Recuperalo cuando vuelvas a necesitarlo.

```bash
# Crear agente especializado para una auditoria legal
python3 scripts/evol-agent-lifecycle.py create \
  --name "legal-saas-reviewer" \
  --task "Revisar contratos SaaS con cliente enterprise" \
  --expires-after 7

# El agente existe, hace su trabajo, y se retira
python3 scripts/evol-agent-lifecycle.py retire "legal-saas-reviewer"
# → Archivado en .evol/agents/retired/ con SHA-256 de integridad
# → MemPalace retiene el conocimiento semantico

# Semanas despues, recuperarlo exactamente igual
python3 scripts/evol-agent-lifecycle.py recall "legal-saas-reviewer"
```

16 agentes core permanentes (architect, builder, qa, sec, devops, domain, doc, ux,
data, reviewer, orchestrator, pm, release, analyst, agent-factory, researcher).
Para todo lo demas: efimeros.

---

## Skills que crecen con el ecosistema

Una skill creada hoy, disponible en Claude Code, Cursor, Windsurf y 4 IDEs mas.

```bash
# Loop iterativo: captura intencion → draft → evals paralelos → optimizar triggering
/evol crear-skill

# El sistema detecta patrones recurrentes y propone skills automaticas
python3 scripts/evol-evolve.py run --dry-run
# → Propone: "skill-sql-optimizer" basada en 8 sesiones con el mismo patron

# Sincronizar con skills de la comunidad
python3 scripts/evol-evolve.py sync-community --dry-run

# Portar a los 7 IDEs con un comando
bash scripts/evol-adapt.sh all --dest=. --trigger=evol
```

---

## Prerequisitos

Evol-DD requiere **Python 3.10+** y **pipx** (recomendado) o pip.

### Verificar que tienes lo necesario

```bash
python3 --version   # debe ser 3.10 o superior
pipx --version      # recomendado para instalar CLIs
# o
pip --version       # alternativa
```

### Instalar pipx si no lo tienes

```bash
# Ubuntu / Debian / Linux Mint
sudo apt install pipx
pipx ensurepath
source ~/.bashrc    # recargar PATH

# macOS (con Homebrew)
brew install pipx
pipx ensurepath

# Windows (PowerShell)
python -m pip install --user pipx
python -m pipx ensurepath

# Verificar
pipx --version
```

### Instalar Python 3.10+ si no lo tienes

```bash
# Ubuntu / Debian
sudo apt install python3 python3-pip python3-full

# macOS
brew install python

# Windows
# Descargar desde https://python.org/downloads
# Marcar "Add Python to PATH" durante la instalacion
```

---

## Instalacion

```bash
# Opcion A — pipx (recomendado: instala en entorno aislado, sin conflictos)
pipx install evol-dd

# Opcion B — pip en entorno virtual
python3 -m venv ~/.venvs/evol-dd
source ~/.venvs/evol-dd/bin/activate   # Linux/macOS
# ~/.venvs/evol-dd/Scripts/activate    # Windows
pip install evol-dd

# Verificar instalacion
evol --version
# → evol-dd 0.1.0
```

---

## Quick Start

```bash
# 1. Verificar entorno
evol doctor

# 2. Bootstrap tu proyecto (elige el perfil segun tu caso)
evol init /path/to/project --profile core

# Perfiles disponibles:
#   minimal    — solo nucleo + workflows + memoria
#   core       — DEFAULT: + agentes + gate + CI (recomendado para empezar)
#   developer  — + hooks + agentes efimeros + investigador
#   security   — + SecDD + AgentShield
#   research   — + eval harness + evolution engine
#   full       — todo incluido
#   lean       — <5MB, requiere instalacion global previa

# 3. Generar configs para tu IDE
evol adapt claude-code --dest=/path/to/project   # Claude Code
evol adapt all --dest=/path/to/project           # todos los IDEs

# 4. Activar en Claude Code: invocar /evol en el chat
# 5. Primera sesion
evol start
```

O clonar el repo directamente (modo legacy, sin pip):

```bash
git clone https://github.com/Cucholambr3ta/evol-system.git
cd evol-system
bash scripts/evol-init.sh /path/to/project --profile core
```

---

## Caracteristicas

| Capacidad | Detalle |
|-----------|---------|
| Sin MCP | CLI nativo. Sin servidor, sin configuracion de red. |
| Memoria nativa | AGENT_MEMORY.md + journals. BM25 search sobre historial. |
| Lecciones + ciclo de mejora | evol-lessons.py con suggest-fix via investigador. |
| Agentes efimeros | create/retire/recall con SHA-256 de integridad. |
| Growth engine | /crear-skill + /crear-agente con evals iterativos. |
| 7 IDEs | claude-code, opencode, cursor, windsurf, vscode-copilot, antigravity, codex. |
| GitFlow enforced | pre-commit hook bloquea branches sin convencion. |
| Gate HMAC-SHA256 | "APROBADO" auditable y firmado por proyecto. |
| Stdlib-first | Cero dependencias externas requeridas para el core. |

---

## Documentacion

| Documento | Para que |
|-----------|---------|
| [docs/constitucion.md](docs/constitucion.md) | 9 articulos de gobernanza — ley suprema |
| [AGENTS.md](AGENTS.md) | Los 16 agentes core con roles y limites |
| [CLAUDE.md](CLAUDE.md) | Manifiesto de operacion para Claude Code |
| [docs/modos.md](docs/modos.md) | Modo Base vs Completo vs Memoria vs GitNexus |
| [docs/guias/ONBOARDING.md](docs/guias/ONBOARDING.md) | Primeros pasos detallados |
| [docs/arquitectura/ARQUITECTURA.md](docs/arquitectura/ARQUITECTURA.md) | Arquitectura completa con diagramas C4 |
| [INSTALL.md](INSTALL.md) | Perfiles de instalacion (minimal, core, developer, full) |

---

## License

MIT — ver [LICENSE](LICENSE)
