# Convenciones

> Atomo de MEMORY. Estandares de codigo y patrones del proyecto.

- **Citacion de fuentes (DOC_STANDARD 1.7):** todo claim producto de investigacion web lleva el link de su fuente. Sin URL = INCOMPLETO. Enforced en discovery/doc-granular/research + las 31 fichas (seccion Fuentes) + `validate-disciplinas.py` (bloquea ficha con `fuentes[]` vacio). El sidecar `.json` captura las URLs via `evol-doc-sync.py` `_extract_sources()`.
- **Labels Mermaid:** salto de linea = `<br/>` (nunca `\n`); todo label con caracteres especiales `() / — ' "` va entre comillas dobles `["..."]`, incluido `subgraph ID["..."]`. El bundle browser de Mermaid es mas estricto que `mmdc` CLI — verificar con el engine del consumidor. Ver `lecciones.md`.
- **Copias reales, nunca symlinks** para `.claude/commands/`, `.github/prompts/`: los IDEs AI-agent no siguen symlinks. SSoT en `.agent/workflows/`; el adapter materializa copias.
- **README.md estandar Top 100 (v0.5.0):** Todo README.md del proyecto (raiz y subdirectorios) debe cumplir el estandar definido en `skills/readme-master/SKILL.md`: HTML centrado, badges Shields.io con iconos, tabla comparativa, Core Features con bloques de codigo, diagrama Mermaid de arquitectura, y seccion de Instalacion/Desinstalacion. La skill opera recursivamente.
- **release-close es obligatorio en todo release (v0.5.0):** El paso `evol-gitflow.sh release-close --version=X.Y.Z` debe ejecutarse ANTES del `git tag`. Es el unico mecanismo que conecta el flujo de release con la actualizacion automatica de `acuerdos/memoria/` y `MEMORY.md`.
