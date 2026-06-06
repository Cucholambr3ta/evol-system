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
- **Erradicación de GitNexus (2026-06-06):** Se eliminó GitNexus del framework completo (docs, configs, workflows). 17 archivos modificados, -435 lineas. Referencias residuales en `evol-agent-lifecycle.py` y `evol-evolve.py` protegidas por env var `EVOL_GITNEXUS=1` (inactivas por defecto). Razon: licencia PolyForm NC incompatible con uso comercial + requiere MCP.
- **Arquitectura EDMS: ChromaDB + LadybugDB global (2026-06-06):** Memoria nativa se implementa con ChromaDB (vector semántico) + LadybugDB (graph/relacional) en una DB global `~/.evol/memory/` (no per-project). Separación por metadata, no por DB. 15 mejoras investigadas (24 repos analizados: OpenMemory, agentmemory, Letta, EM-LLM, FlowScript, cognee, mem0, ai-memory, Deja, Cortex). Plan atómico en `docs/plan-implementacion-edms.md`.
- **Discipline-aware schema como diferenciador único (2026-06-06):** El schema de metadata de EDMS incluye `disciplinas[]` como multi-value filter — ningún otro framework de memoria maneja 31 disciplinas *-Driven como filtro de memoria. Habilita queries como "qué decisiones afectan SEGURIDAD?" o "qué lecciones de DDD hay?".
- **RRF fusion + composite scoring (2026-06-06):** Retrieval híbrido usa Reciprocal Rank Fusion (k=60) para fuscionar 3 streams (BM25 + Vector + Graph) con composite scoring (salience + recency + importance). Decay adaptativo por tipo de memoria. Referencia: agentmemory (95.2% R@5).
- **Auditoría e Higienización de Documentación (2026-06-06):** Se eliminaron emojis residuales (como `👉` en `MANUAL_USUARIO.md`) logrando un 0% de densidad de emojis en todo el repositorio. Se sincronizaron los 66 documentos y 14 dominios mediante `evol-doc-sync.py sync-all docs/` y `sync-folder` recursivo para corregir todos los drifts detectados.
- **Paridad y Espejo de Documentación en CLI (2026-06-06):** Se copiaron y sincronizaron los 11 archivos de documentación `.md` de raíz y sus sidecars `.json` en `src/evol_cli/docs/` para garantizar la paridad del paquete CLI distribuible.

# Convenciones

> Atomo de MEMORY. Estandares de codigo y patrones del proyecto.

- **Citacion de fuentes (DOC_STANDARD 1.7):** todo claim producto de investigacion web lleva el link de su fuente. Sin URL = INCOMPLETO. Enforced en discovery/doc-granular/research + las 31 fichas (seccion Fuentes) + `validate-disciplinas.py` (bloquea ficha con `fuentes[]` vacio). El sidecar `.json` captura las URLs via `evol-doc-sync.py` `_extract_sources()`.
- **Labels Mermaid:** salto de linea = `<br/>` (nunca `\n`); todo label con caracteres especiales `() / — ' "` va entre comillas dobles `["..."]`, incluido `subgraph ID["..."]`. El bundle browser de Mermaid es mas estricto que `mmdc` CLI — verificar con el engine del consumidor. Ver `lecciones.md`.
- **Copias reales, nunca symlinks** para `.claude/commands/`, `.github/prompts/`: los IDEs AI-agent no siguen symlinks. SSoT en `.agent/workflows/`; el adapter materializa copias.
- **README.md estandar Top 100 (v0.5.0):** Todo README.md del proyecto (raiz y subdirectorios) debe cumplir el estandar definido en `skills/readme-master/SKILL.md`: HTML centrado, badges Shields.io con iconos, tabla comparativa, Core Features con bloques de codigo, diagrama Mermaid de arquitectura, y seccion de Instalacion/Desinstalacion. La skill opera recursivamente.
- **release-close es obligatorio en todo release (v0.5.0):** El paso `evol-gitflow.sh release-close --version=X.Y.Z` debe ejecutarse ANTES del `git tag`. Es el unico mecanismo que conecta el flujo de release con la actualizacion automatica de `acuerdos/memoria/` y `MEMORY.md`.
- **Planes de implementacion atomicos (2026-06-06):** Los planes de implementacion se guardan como archivos markdown atomicos en `docs/plan-*.md`, no en memoria.md ni en AGENTS.md. Un solo archivo por plan, con todas las secciones (arquitectura, schema, hooks, tests, fuentes). Referencia: `docs/plan-implementacion-edms.md` (720 lineas, 18 secciones).
- **Research-first antes de implementar (2026-06-06):** Antes de implementar un subsistema complejo, investigar al menos 10 repositorios de referencia y documentar mejoras en un plan atomico. El plan se aprueba ANTES de escribir codigo. Evita reimplementar lo que ya existe y captura patrones de la industria.
- **Privacy stripping obligatorio antes de indexar (2026-06-06):** Todo texto que entre a ChromaDB o LadybugDB debe pasar por `privacy_strip()` primero. Eliminar API keys, tokens, passwords, private tags. Nunca indexar secrets. Referencia: Secure Memory MCP (84 tests de seguridad).
- **Sincronización recursiva de documentación (2026-06-06):** Al realizar operaciones de sincronización de sidecars JSON, se debe correr `sync-folder` explícitamente en directorios anidados de segundo nivel (como `docs/arquitectura/adr/` y `docs/usuario/comandos/`), ya que la llamada a `sync-all` predeterminada no los escanea de forma recursiva profunda.

# Riesgos activos

> Atomo de MEMORY. Riesgos vigentes y mitigaciones.

- **[MITIGADO] `docs/evol-dd_Integration_Guide.md` sin rebrand:** Se reescribió la guía por completo aplicando el estricto `DOC_STANDARD`, eliminando el legacy naming e inyectando la nueva filosofía.
- **[MITIGADO] memory/ no existia en bootstrap:** La carpeta `memory/` no era creada por `evol-init.sh`, causando que herramientas como `evol-shield.py` no pudieran verificar sus permisos. Fix aplicado en v0.5.0: `evol-init.sh` la crea con permisos `750`.
- **[MITIGADO] Memoria no se actualizaba en releases:** El flujo `release-close` no existia, dejando `acuerdos/memoria/` desactualizado tras cada release. Fix aplicado en v0.5.0: nuevo subcomando `evol-gitflow.sh release-close --version=X.Y.Z`.
- **[MITIGADO] Sidecars de disciplinas y documentación pueden driftar:** Se automatizó por completo la sincronización de sidecars y la regeneración de catálogos en `cmd_sprint_close` y `cmd_release_close` dentro de `evol-gitflow.sh` (sprint anterior y fusionado en `develop`).
- **Commits sin firma GPG en main:** GitHub reporta violaciones de firma en los commits del release v0.5.0. Actualmente bypaseados por reglas del repositorio, pero requieren configurar GPG signing localmente para cumplir la politica de rama protegida en futuros releases.
- **EDMS no implementado:** El plan de implementacion esta completo (docs/plan-implementacion-edms.md) pero cero codigo escrito. ChromaDB y LadybugDB no instalados. La memoria sigue en modo stdlib BM25. Riesgo: si el proyecto crece sin memoria persistente, el contexto entre sesiones se pierde y los agentes no aprenden de fallos previos.
- **Dependencia en ChromaDB/LadybugDB:** Ambas son dependencias opcionales. Si no se instalan, el fallback es BM25 stdlib que no tiene vector search ni graph traversal. Las 15 mejoras del plan (RRF, consolidation, causal chains) no estan disponibles sin ellas.

