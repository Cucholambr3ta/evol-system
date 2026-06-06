# Audit Template — Agent Creation
# Extiende audit-base.md con checks especificos de creacion de agentes.

## HEREDA: templates/audit/audit-base.md

---

## Checklist Especifico — Fase: Agent Creation

### F. Definicion del Agente

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| F1 | Archivo `.md` del agente creado en `prompts/agents/core/` o `prompts/agents/ephemeral/` | `[ ]` | |
| F2 | Frontmatter tiene: name, category, mission, triggers | `[ ]` | Todos los campos obligatorios |
| F3 | Agente tiene triggers claros (cuando invocarlo) | `[ ]` | Minimo 1 trigger |
| F4 | Descripcion es concreta (no vaga ni generica) | `[ ]` | |

### G. Registro

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| G1 | Agente registrado en `prompts/agents/registry.json` | `[ ]` | |
| G2 | ID es secuencial (no duplicado) | `[ ]` | |
| G3 | Campo `category` correcto (core o ephemeral) | `[ ]` | |
| G4 | Campo `file` apunta al archivo correcto | `[ ]` | Path relativo a `prompts/agents/` |
| G5 | `validate-registry.py --strict` pasa | `[ ]` | |

### H. Integracion

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| H1 | Agente referenciado en `AGENTS.md` (si es core) | `[ ]` | Tabla de agentes actualizada |
| H2 | Agente referenciado en `evol.md` (si es core) | `[ ]` | Seccion "Agentes core disponibles" |
| H3 | Skills asociadas declaradas en frontmatter | `[ ]` | Campo `skills` en registry |
| H4 | Workflow asociado existe en `.agent/workflows/` | `[ ]` | Si el agente tiene workflow propio |

### I. Efimero (solo si category=ephemeral)

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| I1 | `expires_after_days` definido | `[ ]` | Default: 1 dia |
| I2 | Creado via `evol-agent-lifecycle.py create` | `[ ]` | No manual |
| I3 | Snapshot de retiro registrado | `[ ]` | En `.evol/agents/retired/` |

---

## Puntos Ciegos Especificos — Agent Creation

1. **Agente sin triggers:** El agente existe pero nadie puede invocarlo?
2. **Registro desincronizado:** Archivo existe pero no esta en registry.json?
3. **Agente efimero sin expiracion:** Podria acumularse indefinidamente?
4. **Skills faltantes:** Agente necesita skills que no declara?
5. **Workflow huerfano:** Workflow existe pero no apunta a ningun agente?
6. **Duplicado funcional:** Nuevo agente hace lo mismo que uno existente?
