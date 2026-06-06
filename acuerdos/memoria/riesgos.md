# Riesgos activos

> Atomo de MEMORY. Riesgos vigentes y mitigaciones.

- **[MITIGADO] `docs/evol-dd_Integration_Guide.md` sin rebrand:** Se reescribió la guía por completo aplicando el estricto `DOC_STANDARD`, eliminando el legacy naming e inyectando la nueva filosofía.
- **[MITIGADO] memory/ no existia en bootstrap:** La carpeta `memory/` no era creada por `evol-init.sh`, causando que herramientas como `evol-shield.py` no pudieran verificar sus permisos. Fix aplicado en v0.5.0: `evol-init.sh` la crea con permisos `750`.
- **[MITIGADO] Memoria no se actualizaba en releases:** El flujo `release-close` no existia, dejando `acuerdos/memoria/` desactualizado tras cada release. Fix aplicado en v0.5.0: nuevo subcomando `evol-gitflow.sh release-close --version=X.Y.Z`.
- **[MITIGADO] Sidecars de disciplinas y documentación pueden driftar:** Se automatizó por completo la sincronización de sidecars y la regeneración de catálogos en `cmd_sprint_close` y `cmd_release_close` dentro de `evol-gitflow.sh` (sprint anterior y fusionado en `develop`).
- **Commits sin firma GPG en main:** GitHub reporta violaciones de firma en los commits del release v0.5.0. Actualmente bypaseados por reglas del repositorio, pero requieren configurar GPG signing localmente para cumplir la politica de rama protegida en futuros releases.
- **[MITIGADO] EDMS no implementado:** Completado v0.6.0: 6 fases, ChromaDB + NetworkX activos en `.venv/`, 41 tests passing. Grafo con 261 entries, 105 items bootstrapped, 63 drawers. Fallback stdlib permanece disponible para proyectos sin dependencias opcionales.
- **[MITIGADO] Dependencia en ChromaDB/NetworkX:** Ambas son dependencias opcionales. `pip install evol-dd` funciona sin ellas. Fallback BM25 stdlib con búsqueda local por keywords. Auto-detect venv en `evol_memory_store.py` maneja instalación transparente.

