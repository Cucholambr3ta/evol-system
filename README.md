# Evol-DD — El framework que evoluciona

> Framework de desarrollo agéntico con 16 agentes core, agentes efímeros, y auto-mejora asistida.

## Quick Start

```bash
# Clone
git clone https://github.com/Cucholambr3ta/evol-system.git
cd evol-system

# Bootstrap project
bash scripts/evol-init.sh /path/to/project --profile=core

# Start
bash scripts/evol-start.sh

# Doctor check
bash scripts/evol-doctor.sh
```

## Core Concepts

- **16 Agentes Core**: Permanentes, responsables del estado del sistema
- **Agentes Efímeros**: Creados para tareas especializadas, archivados en MemPalace
- **Auto-Evolución**: El sistema detecta patrones y propone skills automáticas
- **Gated Pipeline**: 6 fases con checkpoint de aprobación

## Trigger

```
/evol <comando>
```

## Scripts

| Script | Función |
|--------|---------|
| evol-init.sh | Bootstrap de proyectos |
| evol-doctor.sh | Diagnóstico del entorno |
| evol-gate.py | Gate keeper HMAC-SHA256 |
| evol-state.py | State store SQLite |
| evol-agent-lifecycle.py | Gestión de agentes efímeros |
| evol-evolve.py | Auto-generación de skills |
| evol-researcher.py | Investigación autónoma |
| evol-memory.py | Memoria conversacional |
| evol-lessons.py | Lecciones aprendidas |
| evol-shield.py | Auditoría de seguridad |
| evol-eval.py | Eval harness |

## Documentation

- [docs/constitucion.md](docs/constitucion.md) — Ley suprema
- [AGENTS.md](AGENTS.md) — Governance manifest
- [CLAUDE.md](CLAUDE.md) — Operation manifest
- [docs/DOC_STANDARD.md](docs/DOC_STANDARD.md) — Estándar de documentación

## License

MIT