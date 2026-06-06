# Decisiones clave

> Atomo de MEMORY. Decisiones de arquitectura y producto persistentes.

- **Registro de disciplinas 9→31** (2026-06-05, v0.3.2): el sistema integra 31 metodologias *-Driven (9 base + 22 extendidas), heredadas del upgrade X-DD `ultimate-update.md`. Registro canonico en `docs/disciplinas/INDEX.md`. 0 colisiones de ID.
- **Activacion por profile, no global:** cada proyecto declara su subset en `evol.profile.yml` (bloque `methodologies:`); el orquestador inyecta solo esas capas en su fase, resuelve el DAG de dependencias (ej. chaos exige odd_obs+threat_driven), y aplica los criterios como sub-gate. No se inyecta lo no declarado.
- **0 agentes permanentes nuevos:** las disciplinas se ejecutan con los 16 agentes core + efimeros (evol-agent-factory). El core permanente NO crece con el upgrade.
- **3 formas de integracion por disciplina** (campo `executor` en la ficha): mapeo a workflow existente, skill nueva (6 gaps: ux-driven, event-sourcing, api-versioning, iac-driven, debt-budget, use-case-driven), o capa declarativa (regla/sub-gate sin workflow).
- **Erradicación de MemPalace (2026-06-06):** Se retiró MemPalace y todo el "Modo COMPLETO" legacy de X-DD. La memoria queda gobernada por la Standard Library de Python en "Modo BASE" puro, preparándose el terreno para una integración nativa de memoria persistente usando ChromaDB y LadybugDB en futuras iteraciones.
