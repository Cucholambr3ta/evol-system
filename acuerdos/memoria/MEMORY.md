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
- **Erradicación de Memoria Persistente (2026-06-06):** Se retiró Memoria Persistente y todo el "Modo COMPLETO" legacy de X-DD. La memoria queda gobernada por la Standard Library de Python en "Modo BASE" puro, preparándose el terreno para una integración nativa de memoria persistente usando ChromaDB y LadybugDB en futuras iteraciones.
- **Skill readme-master como gate de calidad documental (2026-06-06, v0.5.0):** La skill `/evol readme-master` es el estándar oficial para cualquier archivo README.md del proyecto. Opera recursivamente sobre todos los subdirectorios y es activada automáticamente por el hook `pre-push` de `evol-gitflow.sh`. Los READMEs deben seguir el patrón Top 100 (HTML grid, Mermaid obligatorio, badges, sin emojis).
- **memory/ como directorio de runtime local (2026-06-06, v0.5.0):** La carpeta `memory/` (con `memory/raw/`) es un directorio de runtime local, ignorado por git por diseño. Debe ser creada por `evol-init.sh` en el bootstrap con permisos `750`. Nunca se versiona.
- **release-close como gate de memoria (2026-06-06, v0.5.0):** Todo release debe invocar `evol-gitflow.sh release-close --version=X.Y.Z` ANTES del tag git. Este comando dispara la actualización de `acuerdos/memoria/` y la sincronización de `MEMORY.md`. Sin este paso, la memoria persistente queda desactualizada respecto al estado real del repositorio.

# Convenciones

> Atomo de MEMORY. Estandares de codigo y patrones del proyecto.

- **Citacion de fuentes (DOC_STANDARD 1.7):** todo claim producto de investigacion web lleva el link de su fuente. Sin URL = INCOMPLETO. Enforced en discovery/doc-granular/research + las 31 fichas (seccion Fuentes) + `validate-disciplinas.py` (bloquea ficha con `fuentes[]` vacio). El sidecar `.json` captura las URLs via `evol-doc-sync.py` `_extract_sources()`.
- **Labels Mermaid:** salto de linea = `<br/>` (nunca `\n`); todo label con caracteres especiales `() / — ' "` va entre comillas dobles `["..."]`, incluido `subgraph ID["..."]`. El bundle browser de Mermaid es mas estricto que `mmdc` CLI — verificar con el engine del consumidor. Ver `lecciones.md`.
- **Copias reales, nunca symlinks** para `.claude/commands/`, `.github/prompts/`: los IDEs AI-agent no siguen symlinks. SSoT en `.agent/workflows/`; el adapter materializa copias.
- **README.md estandar Top 100 (v0.5.0):** Todo README.md del proyecto (raiz y subdirectorios) debe cumplir el estandar definido en `skills/readme-master/SKILL.md`: HTML centrado, badges Shields.io con iconos, tabla comparativa, Core Features con bloques de codigo, diagrama Mermaid de arquitectura, y seccion de Instalacion/Desinstalacion. La skill opera recursivamente.
- **release-close es obligatorio en todo release (v0.5.0):** El paso `evol-gitflow.sh release-close --version=X.Y.Z` debe ejecutarse ANTES del `git tag`. Es el unico mecanismo que conecta el flujo de release con la actualizacion automatica de `acuerdos/memoria/` y `MEMORY.md`.

# Riesgos activos

> Atomo de MEMORY. Riesgos vigentes y mitigaciones.

- **[MITIGADO] `docs/evol-dd_Integration_Guide.md` sin rebrand:** Se reescribió la guía por completo aplicando el estricto `DOC_STANDARD`, eliminando el legacy naming e inyectando la nueva filosofía.
- **[MITIGADO] memory/ no existia en bootstrap:** La carpeta `memory/` no era creada por `evol-init.sh`, causando que herramientas como `evol-shield.py` no pudieran verificar sus permisos. Fix aplicado en v0.5.0: `evol-init.sh` la crea con permisos `750`.
- **[MITIGADO] Memoria no se actualizaba en releases:** El flujo `release-close` no existia, dejando `acuerdos/memoria/` desactualizado tras cada release. Fix aplicado en v0.5.0: nuevo subcomando `evol-gitflow.sh release-close --version=X.Y.Z`.
- **Sidecars de disciplinas pueden driftar:** editar una ficha `.md` sin correr `evol-doc-sync.py sync-folder docs/disciplinas` deja el `checksum_md` desincronizado; `validate-disciplinas.py --strict` lo detecta y falla.
- **Commits sin firma GPG en main:** GitHub reporta violaciones de firma en los commits del release v0.5.0. Actualmente bypaseados por reglas del repositorio, pero requieren configurar GPG signing localmente para cumplir la politica de rama protegida en futuros releases.

