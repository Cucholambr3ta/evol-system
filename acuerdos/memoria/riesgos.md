# Riesgos activos

> Atomo de MEMORY. Riesgos vigentes y mitigaciones.

- **`docs/X-DD_Integration_Guide.md` sin rebrand:** el guide heredado conserva 16 referencias "X-DD" en vez de "Evol-DD". El conteo de disciplinas (31) ya esta corregido, pero el branding completo del guide queda pendiente de port.
- **Sidecars de disciplinas pueden driftar:** editar una ficha `.md` sin correr `evol-doc-sync.py sync-folder docs/disciplinas` deja el `checksum_md` desincronizado; `validate-disciplinas.py --strict` lo detecta y falla.
