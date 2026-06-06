# Riesgos activos

> Atomo de MEMORY. Riesgos vigentes y mitigaciones.

- **[MITIGADO] `docs/evol-dd_Integration_Guide.md` sin rebrand:** Se reescribió la guía por completo aplicando el estricto `DOC_STANDARD`, eliminando el legacy naming e inyectando la nueva filosofía.
- **[MITIGADO] memory/ no existia en bootstrap:** La carpeta `memory/` no era creada por `evol-init.sh`, causando que herramientas como `evol-shield.py` no pudieran verificar sus permisos. Fix aplicado en v0.5.0: `evol-init.sh` la crea con permisos `750`.
- **[MITIGADO] Memoria no se actualizaba en releases:** El flujo `release-close` no existia, dejando `acuerdos/memoria/` desactualizado tras cada release. Fix aplicado en v0.5.0: nuevo subcomando `evol-gitflow.sh release-close --version=X.Y.Z`.
- **Sidecars de disciplinas pueden driftar:** editar una ficha `.md` sin correr `evol-doc-sync.py sync-folder docs/disciplinas` deja el `checksum_md` desincronizado; `validate-disciplinas.py --strict` lo detecta y falla.
- **Commits sin firma GPG en main:** GitHub reporta violaciones de firma en los commits del release v0.5.0. Actualmente bypaseados por reglas del repositorio, pero requieren configurar GPG signing localmente para cumplir la politica de rama protegida en futuros releases.
