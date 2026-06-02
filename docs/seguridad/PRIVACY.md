# Politica de Privacidad — Evol-DD

Revision: 2026-06-02
Alcance: framework Evol-DD y todos los proyectos creados con `evol-init.sh`

---

## Principio general

Evol-DD es un framework CLI-first de operacion local. Por diseno arquitectonico, no existe servidor central, telemetria automatica ni sincronizacion en la nube. Todo dato permanece en el filesystem del usuario salvo configuracion explicita de proveedores externos.

---

## Inventario de datos personales y sensibles

| Categoria                    | Descripcion                                                                          | Ubicacion                              | Versionado en git  | Gitignored |
|------------------------------|--------------------------------------------------------------------------------------|----------------------------------------|--------------------|------------|
| Prompts de agentes           | Instrucciones de sistema de cada agente definido por el usuario                      | `skills/<nombre>/SKILL.md`, `registry.json` | Si                 | No         |
| Memoria conversacional       | Contexto acumulado de sesiones anteriores del proyecto                               | `AGENT_MEMORY.md` (raiz proyecto)      | Opcional           | No por defecto |
| Memoria local extendida      | Chunks indexados por el motor ReMe                                                   | `memory/` (raiz proyecto)              | Opcional           | Recomendado gitignorear |
| Instincts (aprendizaje)      | Patrones derivados de lecciones aprendidas, almacenados como filas SQLite            | `~/.evol/state.db`                     | No (global)        | N/A (fuera del repo) |
| Research proposals           | Propuestas de evolucion del framework generadas por `evol-researcher.py`             | `~/.evol/state.db` (tabla proposals)   | No (global)        | N/A |
| Snapshots de agentes retirados | Dump del prompt final + metadatos al momento de retirar un agente efimero          | `.evol/agents/retired/<nombre>.json`   | Opcional           | Recomendado gitignorear |
| Dialogos de sesion           | Transcripciones parciales o buffers de sesion activa                                 | `dialog/` (raiz proyecto)              | No                 | Si (TTL 3 dias) |
| Tool results                 | Salidas de herramientas durante ejecucion                                            | `tool_result/` (raiz proyecto)         | No                 | Si (TTL 3 dias) |
| Gate key del proyecto        | Clave HMAC-SHA256 local del proyecto                                                 | `.evol/.gate-key`                      | No                 | Si (obligatorio) |

---

## Transmision de datos a terceros

### Por defecto: ninguna

Con la configuracion por defecto (`EVOL_PROVIDER=mock`), el framework usa `MockProvider` determinista. Ningun dato es enviado fuera del filesystem local.

### Con EVOL_PROVIDER=anthropic

Cuando el usuario configura `EVOL_PROVIDER=anthropic`, los prompts de agentes y el contexto de sesion se envian a la API de Anthropic para inferencia. Aplica la politica de privacidad de Anthropic (https://www.anthropic.com/privacy). El usuario es responsable de no incluir datos personales de terceros en los prompts.

### Con GITHUB_TOKEN configurado

Cuando el usuario configura `GITHUB_TOKEN`, el script `evol-researcher.py` consulta la API publica de GitHub. Solo se accede a metadata publica de repositorios: nombre, descripcion, numero de estrellas, topics, licencia. No se transmiten datos del usuario ni del proyecto hacia GitHub mas alla del token de autenticacion en el header de la request.

---

## Datos de terceros procesados por el framework

| Fuente      | Datos accedidos                                      | Finalidad                              | Almacenamiento local                        |
|-------------|------------------------------------------------------|----------------------------------------|---------------------------------------------|
| GitHub API  | Nombre de repo, descripcion, stars, topics, licencia | Generar research proposals de mejora   | `~/.evol/state.db` tabla `research_proposals` |

No se procesa ningun otro dato de terceros.

---

## Retencion y ciclo de vida

| Dato                         | Retencion por defecto          | Eliminacion manual                                         |
|------------------------------|--------------------------------|------------------------------------------------------------|
| Prompts de agentes           | Indefinida (versionada en git) | `git rm skills/<nombre>/SKILL.md`                          |
| AGENT_MEMORY.md              | Indefinida                     | `rm AGENT_MEMORY.md` o reemplazar con version vacia       |
| memory/ chunks               | Indefinida                     | `rm -rf memory/`                                           |
| ~/.evol/state.db instincts   | Indefinida                     | `python scripts/evol-state.py prune --older-than <dias>`  |
| ~/.evol/state.db proposals   | Indefinida                     | `python scripts/evol-researcher.py prune`                  |
| dialog/                      | 3 dias (TTL evol-memory gc)    | `python scripts/evol-memory.py gc` o `rm -rf dialog/`     |
| tool_result/                 | 3 dias (TTL evol-memory gc)    | `python scripts/evol-memory.py gc` o `rm -rf tool_result/`|
| Snapshots retired            | Indefinida si commiteados      | `git rm .evol/agents/retired/<nombre>.json`                |
| .evol/.gate-key              | Indefinida (local, gitignored) | `rm .evol/.gate-key` + regenerar con `evol gate init`     |

---

## Derechos del usuario

Dado que todos los datos son locales, el usuario tiene control total:

- **Acceso:** todos los datos son archivos en el filesystem o una base SQLite legible con cualquier cliente SQLite.
- **Rectificacion:** editar directamente los archivos o usar los scripts de gestion (`evol-state.py`, `evol-lessons.py`, `evol-memory.py`).
- **Eliminacion completa:** borrar `~/.evol/` elimina todo el estado global. Borrar `.evol/` en el proyecto elimina el estado del proyecto. Borrar los archivos de memoria elimina el contexto conversacional.
- **Portabilidad:** el formato es Markdown plano, JSON y SQLite; todos son estandares abiertos legibles sin dependencia de Evol-DD.

---

## Contacto

Para consultas sobre privacidad relacionadas con este framework, contactar al mantenedor del proyecto en el repositorio de Evol-DD.
