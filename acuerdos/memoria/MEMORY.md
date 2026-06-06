# MEMORY.md — Hechos persistentes del proyecto

> GENERADO automaticamente desde los atomos (decisiones/convenciones/riesgos).
> NO editar este archivo: editar el atomo correspondiente y regenerar via
> `evol-memory sprint-close` o `evol-memory memory-split`.

# Decisiones clave

> Atomo de MEMORY. Decisiones de arquitectura y producto persistentes.

- **Registro de disciplinas 9→31** (2026-06-05, v0.3.2): el sistema integra 31 metodologias *-Driven (9 base + 22 extendidas), heredadas del upgrade X-DD `ultimate-update.md`. Registro canonico en `docs/disciplinas/INDEX.md`. 0 colisiones de ID.
- **Activacion por profile, no global:** cada proyecto declara su subset en `evol.profile.yml` (bloque `methodologies:`); el orquestador inyecta solo esas capas en su fase, resuelve el DAG de dependencias (ej. chaos exige odd_obs+threat_driven), y aplica los criterios como sub-gate. No se inyecta lo no declarado.
- **0 agentes permanentes nuevos:** las disciplinas se ejecutan con los 16 agentes core + efimeros (evol-agent-factory). El core permanente NO crece con el upgrade.
- **3 formas de integracion por disciplina** (campo `executor` en la ficha): mapeo a workflow existente, skill nueva (6 gaps: ux-driven, event-sourcing, api-versioning, iac-driven, debt-budget, use-case-driven), o capa declarativa (regla/sub-gate sin workflow).
- **Erradicación de MemPalace (2026-06-06):** Se retiró MemPalace y todo el "Modo COMPLETO" legacy de X-DD. La memoria queda gobernada por la Standard Library de Python en "Modo BASE" puro, preparándose el terreno para una integración nativa de memoria persistente usando ChromaDB y LadybugDB en futuras iteraciones.

# Convenciones

> Atomo de MEMORY. Estandares de codigo y patrones del proyecto.

- **Citacion de fuentes (DOC_STANDARD 1.7):** todo claim producto de investigacion web lleva el link de su fuente. Sin URL = INCOMPLETO. Enforced en discovery/doc-granular/research + las 31 fichas (seccion Fuentes) + `validate-disciplinas.py` (bloquea ficha con `fuentes[]` vacio). El sidecar `.json` captura las URLs via `evol-doc-sync.py` `_extract_sources()`.
- **Labels Mermaid:** salto de linea = `<br/>` (nunca `\n`); todo label con caracteres especiales `() / — ' "` va entre comillas dobles `["..."]`, incluido `subgraph ID["..."]`. El bundle browser de Mermaid es mas estricto que `mmdc` CLI — verificar con el engine del consumidor. Ver `lecciones.md`.
- **Copias reales, nunca symlinks** para `.claude/commands/`, `.github/prompts/`: los IDEs AI-agent no siguen symlinks. SSoT en `.agent/workflows/`; el adapter materializa copias.

# Riesgos activos

> Atomo de MEMORY. Riesgos vigentes y mitigaciones.

- **`docs/X-DD_Integration_Guide.md` sin rebrand:** el guide heredado conserva 16 referencias "X-DD" en vez de "Evol-DD". El conteo de disciplinas (31) ya esta corregido, pero el branding completo del guide queda pendiente de port.
- **Sidecars de disciplinas pueden driftar:** editar una ficha `.md` sin correr `evol-doc-sync.py sync-folder docs/disciplinas` deja el `checksum_md` desincronizado; `validate-disciplinas.py --strict` lo detecta y falla.

