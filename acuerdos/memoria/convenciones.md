# Convenciones

> Atomo de MEMORY. Estandares de codigo y patrones del proyecto.

- **Citacion de fuentes (DOC_STANDARD 1.7):** todo claim producto de investigacion web lleva el link de su fuente. Sin URL = INCOMPLETO. Enforced en discovery/doc-granular/research + las 31 fichas (seccion Fuentes) + `validate-disciplinas.py` (bloquea ficha con `fuentes[]` vacio). El sidecar `.json` captura las URLs via `evol-doc-sync.py` `_extract_sources()`.
- **Labels Mermaid:** salto de linea = `<br/>` (nunca `\n`); todo label con caracteres especiales `() / — ' "` va entre comillas dobles `["..."]`, incluido `subgraph ID["..."]`. El bundle browser de Mermaid es mas estricto que `mmdc` CLI — verificar con el engine del consumidor. Ver `lecciones.md`.
- **Copias reales, nunca symlinks** para `.claude/commands/`, `.github/prompts/`: los IDEs AI-agent no siguen symlinks. SSoT en `.agent/workflows/`; el adapter materializa copias.
