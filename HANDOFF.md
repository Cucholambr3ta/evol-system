# HANDOFF.md — Continuidad Cross-Hardware

> Generado 2026-07-01 para retomar desarrollo en otro equipo. Snapshot exacto del
> estado del repo al momento del último push desde este hardware.

## Identidad

- **Proyecto:** Evol-DD — framework de desarrollo agéntico (CLI + orquestación multi-agente + EDMS memory system)
- **Repo:** https://github.com/Cucholambr3ta/evol-system.git
- **Branch activo:** `feature/edms-ui`
- **Version:** `0.6.3` (pyproject.toml) — drift conocido vs `VERSION`=0.6.0 (pendiente sync)
- **PyPI:** https://pypi.org/project/evol-dd/ (últ. publicada: 0.6.0)

## Cómo retomar en el otro equipo

```bash
git clone https://github.com/Cucholambr3ta/evol-system.git
cd evol-system
git checkout feature/edms-ui
git pull origin feature/edms-ui
```

Leer en este orden (Constitución Art. 3 — Flight Recorder):
1. `docs/constitucion.md` — ley suprema del proyecto
2. `memoria.md` — bitácora viva, decisiones/artefactos/próximos pasos
3. `WORKING-CONTEXT.md` — estado operativo, se sobreescribe por sprint
4. Este archivo (`HANDOFF.md`) — snapshot de la sesión de corte

Si el otro entorno tiene su propio agente activo, usar skill `update-context`
(local, no se publica en releases) para sincronizar lo que hizo este entorno.

## Qué hay hecho (resumen funcional)

### CLI core
- `evol-init`, `evol-start`, `evol-doctor`, `evol-gate` (HMAC-SHA256), `evol-state` (SQLite)
- `evol-orchestrate` — runtime multi-agente, 5 patrones built-in
- `evol-agent` — lifecycle de agentes efímeros (crear/invocar/retirar/recall)
- `evol-memory` — EDMS completo (ver abajo)
- `evol-gitflow` — GitFlow automatizado (setup/sprint-start/sprint-close/pre-push/status)
- `evol-discipline-check` — valida contenido por disciplina (31 metodologías X-DD)
- `evol-adapt` — genera configs para 7 IDEs desde SSoT (`.agent/workflows/`)
- ~30 scripts `evol-*` en `scripts/`, 15 wrappers npm en `bin/`

### EDMS (Evol Distributed Memory System) — pieza central
- **Fases 1-6 completas.** Arquitectura: ChromaDB + LadybugDB + fallback stdlib (auto-detect venv)
- 4-tier consolidation: raw → compressed → memory → knowledge → archived
- **Memory v2 (5 gaps implementados, investigación vs 20 sistemas externos — "elagente vs EDMS"):**
  - `forecasting.py` — memorias predictivas
  - `thought.py` — captura de pensamiento
  - `user_model.py` — modelo dialéctico de usuario (inspirado en Honcho)
  - Señal temporal de recencia en retrieval
  - `dreaming_log` auditable
  - Subcomandos nuevos: `edms-dream-log`, `edms-predictions`, `edms-thought(s)`, `edms-user-model`
  - Investigación completa en `acuerdos/research/memory-v2-gaps/`
- Code graph: Tree-sitter obligatorio, LadybugDB separada (`evol_dd_codigo.lbug`)
  - Estado actual del grafo: 4837 nodos, 22938 relaciones (Symbol 3924, File 489, Module 424; CALLS 12636, CONTAINS 4816, EXPORTS 4326, IMPORTS 1158, EXTENDS 2)
- Real-time monitoring (stdlib puro): `evol_traces.py` (NDJSON) + `evol_sse_server.py` + `evol_state_machine.py` + `evol_loop_detector.py`
- Nuevo: `evol_memory_stack.py`, `evol_contradictions.py`, `evol_code_indexer.py` (Tree-sitter)

### UI / Frontend
- **TUI** (prioridad actual): `scripts/evol_tui/` — scaffold de 68 archivos, Textual + netext. **Auditoría pendiente** contra los 9 wireframes aprobados en `acuerdos/design/wireframes/propuesta/`.
- **Web PWA** (`edms-web/`): React 19 + ThreeJS + PWA, 34 archivos en `src/`. **Descartada por pérdida de foco** — TUI es la prioridad. No borrar, queda como referencia/backup.

### Skills
- 82 skills en catálogo (`skills/CATALOG.json`: 70 core + 12 extra), portadas a 7 IDEs
- 2 skills **local-only** (NO van a releases de evol-dd): `update-context`, `update-memory` — sirven justo para el caso de cambiar de hardware/IDE
- Última agregada: `evol-minimal` (anti-over-engineering, inspirada en ponytail) — decision ladder, niveles lite/full/ultra/off, cablea a code-review/evol-shield/debt-budget/evol-eval

### Tests
- 24 archivos `test_*.py` en `tests/` (incluye nuevos: code_indexer, contradictions, impact, memory_stack, memory_v2 fases 2 y 4)
- Última cifra reportada en memoria.md: 247 tests verdes (+50 vs baseline)

## Decisiones arquitectónicas clave (no derivables del código)

- **TUI > Web PWA**: se descartó la PWA por foco disperso; toda la energía UI va a la TUI (Textual). No es un fallback técnico, es decisión de producto/tiempo.
- **EDMS Memory v2 stdlib-first**: LLM es opcional, se activa solo con `EVOL_MEMORY_LLM`. Motivo: no forzar dependencia pesada para funcionalidad base.
- **evol-minimal NO clona ponytail**: se reusaron capacidades ya existentes en Evol-DD (code-review, evol-shield, debt-budget, evol-eval) en vez de duplicar — regla "Zero Duplicados" de la Constitución.
- **Skills local-only**: `update-context`/`update-memory` existen precisamente para el escenario de "seguir en otro hardware" — están diseñadas para no ir en el paquete público porque son de sincronización de sesión, no de producto.

## Bugs / deuda conocida (pendiente, no resuelta)

1. **`edms-conflicts` roto**: `VerbatimStore` no iterable. Ver `lecciones.md` entrada 2026-06-08.
2. **VERSION drift**: `pyproject.toml`=0.6.3 vs `VERSION`/`src/evol_cli/VERSION`=0.6.0. Hay que decidir cuál es la fuente de verdad y sincronizar el resto.
3. **`edms-predictions` / `edms-user-model` no cableados al wake-up del orquestador** `/evol` — hoy son comandos manuales, no se auto-inyectan en el arranque de sesión.
4. **TUI sin auditar** contra wireframes — scaffold generado por agente externo, falta verificación punto por punto.

## Próximos pasos (orden sugerido)

1. Auditar TUI (`scripts/evol_tui/`) vs los 9 wireframes aprobados.
2. Sincronizar VERSION en los 3 lugares (`pyproject.toml`, `VERSION`, `src/evol_cli/VERSION`).
3. Cablear `edms-predictions` + `edms-user-model` en el wake-up del orquestador.
4. Corregir `edms-conflicts` (bug VerbatimStore).
5. Evaluar si `edms-web/` se archiva definitivamente o se retoma — está huérfana desde el pivot a TUI.

## Estructura de memoria del proyecto (para el otro agente/hardware)

| Archivo | Rol |
|---|---|
| `memoria.md` | Flight recorder — lectura obligatoria al inicio de sesión |
| `lecciones.md` | Lecciones cross-proyecto (bugs, causas raíz) |
| `WORKING-CONTEXT.md` | Estado operativo vivo, se sobreescribe por sprint/hito |
| `AGENT_MEMORY.md` | Memoria del agente (estilo, convenciones de trabajo) |
| `acuerdos/memoria/*.{md,json}` | Decisiones, convenciones, riesgos — versión estructurada |
| `acuerdos/research/memory-v2-gaps/` | Investigación que fundamenta EDMS Memory v2 |
| Este archivo | Snapshot puntual de corte de hardware — no se actualiza, se reemplaza si se repite el escenario |

## Todo commiteado y pusheado

Al momento de generar este archivo, **no queda ningún cambio local sin subir**:
todo lo modificado y todo lo nuevo (sin excepción, incluyendo `edms-web/`,
`scripts/evol_tui/`, skills locales, tests nuevos) fue agregado, commiteado y
pusheado a `origin/feature/edms-ui` antes de cerrar esta sesión.
