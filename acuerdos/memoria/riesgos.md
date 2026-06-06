# Riesgos activos

> Atomo de MEMORY. Riesgos vigentes y mitigaciones.

- **[MITIGADO] `docs/evol-dd_Integration_Guide.md` sin rebrand:** Se reescribió la guía por completo aplicando el estricto `DOC_STANDARD`, eliminando el legacy naming e inyectando la nueva filosofía.
- **Sidecars de disciplinas pueden driftar:** editar una ficha `.md` sin correr `evol-doc-sync.py sync-folder docs/disciplinas` deja el `checksum_md` desincronizado; `validate-disciplinas.py --strict` lo detecta y falla.
