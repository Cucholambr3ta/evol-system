# Decisiones de Arquitectura

## ADR-001: Arquitectura CLI-first

- Status: Accepted
- Decision: Sistema opera con integración nativa MCP
- Consecuencias: Mayor portabilidad, menor complejidad

---

## ADR-002: Eliminar MCP completamente

- Status: Accepted
- Date: 2026-06-02

### Contexto

X-DD incluia un servidor MCP propio y utilizaba Memoria Persistente en modo MCP para la continuidad de contexto entre sesiones. Esta arquitectura requeria configuracion de red, un proceso servidor persistente, y dependencias de transporte que variaban por entorno. El mantenimiento del servidor MCP introducia superficie de ataque adicional y puntos de fallo que no aportaban valor diferencial en comparacion con alternativas nativas.

### Decision

Evol-DD no utiliza MCP de ningun tipo. Toda integracion con IDEs y herramientas externas se realiza mediante `evol-adapt.sh`, que genera copias reales de la configuracion en los directorios de destino. Memoria Persistente, cuando se usa, opera en modo file-based, no en modo MCP.

### Consecuencias

| Dimension | Impacto |
|-----------|---------|
| Seguridad | Superficie de ataque reducida: sin puerto abierto, sin autenticacion de transporte |
| Configuracion | Sin setup de red. Funciona en entornos air-gapped sin cambios |
| Compatibilidad IDEs | 7 IDEs soportados via copia real generada por adapt.sh (SSoT unico) |
| Memoria Persistente | Sigue disponible como opcion opt-in en modo file-based |
| Complejidad operativa | Elimina proceso servidor, health-checks y reintentos de conexion |

---

## ADR-003: GitFlow como estrategia Git por defecto

- Status: Accepted
- Date: 2026-06-02

### Contexto

X-DD opera con trunk-based development: rama principal unica, commits directos frecuentes y feature flags para ocultar trabajo en progreso. Evol-DD tiene un modelo de releases formales con ciclos de sprint mas largos, changelogs versionados y necesidad de hotfixes paralelos al desarrollo activo. Trunk-based en este contexto generaba colisiones entre trabajo en progreso y preparacion de releases.

### Decision

Evol-DD adopta GitFlow como estrategia Git por defecto con la siguiente estructura de ramas:

| Rama | Proposito | Origen | Merge hacia |
|------|-----------|--------|-------------|
| `main` | Codigo en produccion, tags de release | `release/*`, `hotfix/*` | — |
| `develop` | Integracion continua de features | `main` (inicial) | `release/*` |
| `feature/*` | Desarrollo de una feature o skill | `develop` | `develop` |
| `release/*` | Preparacion de release (freeze, QA) | `develop` | `main` + `develop` |
| `hotfix/*` | Correccion urgente sobre produccion | `main` | `main` + `develop` |

El script `pre-commit-gitflow.sh` verifica que el nombre de rama cumple la convencion y que los mensajes de commit siguen Conventional Commits. PR obligatorio para merge a `develop` y `main`.

### Consecuencias

La estructura de ramas impone disciplina en el ciclo de release pero agrega friction en desarrollo individual. Los sprints cortos (menos de una semana) pueden sentir la sobrecarga de crear rama `release/*`. El hook `pre-commit-gitflow.sh` bloquea commits en ramas mal nombradas, lo que requiere onboarding explicito para contribuidores nuevos. A cambio, el historial de `main` refleja unicamente releases estables y los hotfixes quedan trazados sin contaminar `develop`.

---

## ADR-004: Gate key por proyecto (no global)

- Status: Accepted
- Date: 2026-06-02

### Contexto

La propuesta inicial contemplaba una clave de gate global almacenada en `~/.evol/.gate-key` para simplificar la experiencia de primer uso: el usuario genera la clave una vez y todos sus proyectos la heredan. Esta aproximacion reduce la friccion de setup pero crea un modelo de aislamiento debil: una clave comprometida en un proyecto afecta todos los proyectos del mismo host.

### Decision

La clave de gate reside en `.evol/.gate-key` dentro del directorio del proyecto, no en el home del usuario. El flujo de primer uso es:

1. `evol-gate.py init` genera una clave aleatoria y la escribe en `.evol/.gate-key`.
2. Opcionalmente, `--from-global` copia la clave global como punto de partida, pero la convierte en una copia local independiente.
3. `.evol/.gate-key` se agrega automaticamente a `.gitignore` del proyecto.

### Consecuencias

| Dimension | Impacto |
|-----------|---------|
| Aislamiento | Leak en un proyecto no propaga a otros proyectos del mismo usuario |
| UX primer uso | Requiere `evol-gate.py init` explicito por proyecto |
| CI/CD | La clave debe inyectarse como secret por proyecto en el pipeline |
| Rotacion | Rotar la clave de un proyecto no afecta los demas |
| Backup | El usuario es responsable de respaldar `.evol/.gate-key` fuera del repo |

La clave global en `~/.evol/.gate-key` sigue siendo valida como conveniencia de arranque rapido, pero nunca como fuente de verdad operativa.

---

## ADR-005: 16 agentes core permanentes + efimeros ilimitados

- Status: Accepted
- Date: 2026-06-02

### Contexto

X-DD define 180 agentes permanentes con responsabilidades granulares. En la practica, cargar el directorio completo de agentes en cada sesion genera sobrecarga de contexto: el orquestador debe evaluar relevancia de 180 candidatos antes de delegar, y la mayoria de las sesiones usa menos de 10 agentes distintos. La granularidad maxima no se traduce en calidad de respuesta si el contexto del LLM se satura con descriptores de agentes no relevantes.

### Decision

Evol-DD mantiene exactamente 16 agentes core con caracter permanente. Su criterio de permanencia es responsabilidad sobre el SISTEMA (orquestacion, gate, memoria, lecciones, seguridad, QA, etc.), no sobre dominios de negocio especificos. Los agentes de dominio son efimeros: se crean con `crear-agente`, tienen un ciclo de vida formal (create / active / retired / recalled) y expiran segun `expires_after_days` en su AGENT.md.

| Estado | Descripcion |
|--------|-------------|
| `create` | Definicion escrita, aun no activo en sesion |
| `active` | Disponible para invocacion en sesion actual |
| `retired` | Fuera de rotacion activa, conocimiento en Memoria Persistente |
| `recalled` | Reactivado desde Memoria Persistente para una sesion especifica |

### Consecuencias

El contexto de sesion se mantiene limpio. La transicion `retired → recalled` requiere que Memoria Persistente haya persistido el conocimiento del agente antes del retire; si Memoria Persistente no estaba activo, la informacion se pierde. El numero 16 es un limite de gobierno, no tecnico: no hay verificacion automatica que impida crear mas de 16 agentes con ciclo de vida `active` simultaneamente; la disciplina es responsabilidad del equipo.

---

## ADR-006: Motor de memoria conversacional nativo

- Status: Accepted
- Date: 2026-06-02

### Contexto

X-DD depende de Memoria Persistente (MIT) para la continuidad de contexto entre sesiones. Memoria Persistente es una dependencia externa con su propio modelo de instalacion y configuracion. En entornos con restricciones de red o en onboardings rapidos, la ausencia de Memoria Persistente dejaba al sistema sin ningun mecanismo de continuidad, forzando al usuario a reconstruir contexto manualmente al inicio de cada sesion.

### Decision

`evol-memory.py` es el motor nativo de memoria conversacional de Evol-DD. Opera exclusivamente con stdlib de Python (sin dependencias externas) y persiste el estado en dos artefactos editables:

| Artefacto | Contenido |
|-----------|-----------|
| `AGENT_MEMORY.md` | Resumen estructurado del contexto activo (hechos, decisiones, entidades) |
| `journals/YYYY-MM-DD.md` | Log diario append-only de interacciones |

La busqueda sobre el historial usa BM25 implementado sobre texto plano. La integracion con LLM es opcional: con `EVOL_MEMORY=1` y `LLM_API_KEY` presente, el motor usa el LLM para resumir; sin API key, cae a modo mock con resumen heuristico.

### Consecuencias

El motor funciona sin Memoria Persistente, lo que elimina la dependencia critica para continuidad basica. Los archivos son Markdown editables, por lo que un humano puede corregir o enriquecer el contexto directamente. La busqueda BM25 es efectiva para corpus pequenos (menos de 500 entradas); para corpus grandes, la precision decrece respecto a embeddings. Memoria Persistente sigue siendo la opcion recomendada para proyectos con historial extenso o equipos grandes.

---

## ADR-007: Motor de lecciones con ciclo de mejora continua

- Status: Accepted
- Date: 2026-06-02

### Contexto

En X-DD, `lecciones.md` era un archivo Markdown gestionado manualmente. No existia motor que verificara duplicados, sugiriera mejoras a lecciones existentes, ni rastreara el estado de aplicacion de cada leccion. El resultado era un archivo que crecia sin depuracion: lecciones obsoletas, repetidas con distintas palabras, o con propuestas de solucion que nunca se verificaban como aplicadas.

### Decision

`evol-lessons.py` implementa un motor de lecciones con las siguientes operaciones:

| Operacion | Descripcion |
|-----------|-------------|
| `add` | Agrega leccion nueva con dedup fuzzy Jaccard (umbral 0.70) |
| `suggest-fix` | El investigador propone una mejora a una leccion existente |
| `apply-fix` | Marca la mejora como aplicada y actualiza el texto de la leccion |
| `search` | Busqueda BM25 sobre el corpus de lecciones |
| `extract` | Extrae lecciones candidatas desde un artefacto (SPEC.md, QA_REPORT, etc.) |

El estado de cada leccion (`open`, `fix-proposed`, `fix-applied`) se persiste en frontmatter YAML dentro de `lecciones.md`.

### Consecuencias

Las lecciones pasan de ser un artefacto pasivo a tener ciclo de vida gestionado. La deduplicacion por Jaccard previene el crecimiento sin control pero puede rechazar lecciones legitimamente distintas con vocabulario similar; el umbral 0.70 es ajustable via `EVOL_JACCARD_THRESHOLD`. La operacion `suggest-fix` requiere `EVOL_PROVIDER=anthropic` para generar propuestas de calidad; en modo mock produce sugerencias genericas. El investigador que propone la mejora no puede ser el mismo que la aplica (separacion de roles, alineada con ADR-004).

---

## ADR-008: Growth engine como capacidad core (crear-skill + crear-agente)

- Status: Accepted
- Date: 2026-06-02

### Contexto

En X-DD, crear una skill o un agente nuevo requeria conocimiento manual del formato de frontmatter, la estructura de directorios esperada, los campos obligatorios del SKILL.md o AGENT.md, y la actualizacion manual del registry. El proceso no estaba documentado de forma ejecutable: existian plantillas pero no habia un flujo guiado con validacion, evals automaticos ni integracion con los 7 IDEs.

### Decision

Evol-DD eleva la capacidad de auto-expansion a capacidad core del sistema mediante dos skills nativas:

| Skill | Ruta | Responsabilidad |
|-------|------|-----------------|
| `crear-skill` | `skills/crear-skill/` | Loop iterativo: spec → scaffold → eval → iterate → promote |
| `crear-agente` | `skills/crear-agente/` | Define AGENT.md, asigna ciclo de vida, registra en registry.json |

El loop de `crear-skill` incluye evals automaticos al finalizar cada iteracion. Una skill no se promueve a `active` hasta pasar el umbral de eval definido en `grader.yaml`. La integracion con `evol-adapt.sh` es automatica al promover: la skill queda disponible en los 7 IDEs configurados.

### Consecuencias

El sistema puede expandirse desde dentro sin intervencion manual en el registro o en las plantillas. El loop iterativo con evals introduce latencia en la creacion de skills nuevas (cada iteracion requiere correr el eval-harness), pero garantiza calidad minima antes de la promocion. El riesgo principal es la creacion de skills redundantes: sin una etapa de busqueda previa en el registry, dos sesiones paralelas pueden crear skills solapadas. `crear-skill` incluye una busqueda de similitud sobre `registry.json` como primer paso del loop para mitigar este riesgo.
