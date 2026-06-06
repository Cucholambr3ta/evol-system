# Casos de Borde

## Tabla de casos

| ID | Escenario | Precondicion | Input | Resultado esperado | Prioridad |
|----|-----------|--------------|-------|--------------------|-----------|
| CB-001 | Manifest invalido al hacer evol-init (profile inexistente) | Binario evol-init disponible, sin evol.profile.yml previo | `evol-init --profile perfil_inexistente` | Error claro con lista de profiles disponibles, sin crear directorio parcial | CRITICA |
| CB-002 | IDE no detectado en bootstrap (PATH vacio) | evol-adapt.sh ejecutable, PATH={} | `evol-adapt.sh` sin IDEs en PATH | Warning por cada IDE no detectado, continua con los detectados, exit 0 si al menos uno funciono | ALTA |
| CB-003 | Agente efimero vencido al intentar invocar | AGENT.md con `expires_after_days` ya expirado en fecha de ejecucion | Invocacion del agente por nombre | Error con fecha de expiracion, sugerencia de `recall` o `crear-agente` nuevo | CRITICA |
| CB-004 | Recall con Memoria Persistente no disponible (solo snapshot JSON) | Memoria Persistente offline, snapshot `memoria_persistente-snapshot.json` presente | `evol-memory recall --agent nombre` | Carga desde snapshot JSON local, warning de datos potencialmente desactualizados | CRITICA |
| CB-005 | Gate key no existe al hacer transition (primera vez) | Proyecto nuevo, sin `.evol/.gate-key` | `evol-gate.py transition fase1 fase2` | Error explicito con instruccion de ejecutar `evol-gate.py init` primero | ALTA |
| CB-006 | Registry.json corrupto (JSON invalido) al validate-registry | `registry.json` con syntax error (coma extra, llave sin cerrar) | `validate-registry.py --strict` | Exit 1 con linea exacta del error de parseo, sin intentar validacion parcial | ALTA |
| CB-007 | Leccion duplicada en evol-lessons (similaridad Jaccard > 0.70) | lecciones.md con al menos una leccion existente | `evol-lessons add "Evitar commits directos a main"` con leccion similar ya presente | Rechazo con ID de la leccion similar, valor Jaccard calculado y texto de la colision | CRITICA |
| CB-008 | evol-memory con EVOL_MEMORY=1 pero sin LLM_API_KEY (mock fallback) | Variable EVOL_MEMORY=1 en entorno, LLM_API_KEY ausente | Operacion de resumen en evol-memory.py | Fallback a resumen heuristico local, warning en stderr, sin crash, AGENT_MEMORY.md generado | CRITICA |
| CB-009 | Skill con frontmatter sin 'description' al evol-adapt.sh codex | SKILL.md existente con campos obligatorios faltantes | `evol-adapt.sh codex` | Skill omitida del output codex, warning con path y campo faltante, resto de skills procesadas | MEDIA |
| CB-010 | evol-evolve clustering con menos de 3 instincts disponibles | state.db con 0-2 instincts registrados | `evol-evolve cluster` | Warning de corpus insuficiente para clustering significativo, sugerencia de minimo de instincts | MEDIA |
| CB-011 | evol-researcher con rate limit de GitHub API (60 req/h) | Token GitHub ausente o limite alcanzado | Busqueda de patrones en GitHub via evol-researcher | Fallback a resultados cacheados si existen, error descriptivo con tiempo estimado de reset | ALTA |
| CB-012 | evol-adapt.sh con directorio destino inexistente | IDE configurado en evol.profile.yml con path no creado | `evol-adapt.sh vscode` con destino `~/.vscode/nonexistent/` | Creacion del directorio con mkdir -p antes de copiar, o error si permisos insuficientes | MEDIA |
| CB-013 | evol-gate approve con aprobador == autor (mismo usuario) | Fase pendiente de aprobacion, `git config user.email` igual al del autor del artefacto | `evol-gate.py approve fase2` por el mismo autor | Rechazo con mensaje de separacion de roles, identidad de autor y aprobador mostradas | ALTA |
| CB-014 | evol-lessons suggest-fix sin EVOL_PROVIDER=anthropic (mock) | EVOL_PROVIDER ausente o distinto de anthropic | `evol-lessons suggest-fix CB-007` | Sugestion generica de mock con flag `[mock]` en output, sin crash, estado leccion no cambia a fix-proposed | MEDIA |
| CB-015 | evol-init --profile lean sin wrapper global instalado | evol-dd clonado localmente, sin instalacion global en PATH | `evol-init --profile lean` ejecutado desde directorio del proyecto | Detecta ausencia de wrapper global, ejecuta desde ruta relativa `./scripts/evol-init.sh`, warning de instalacion recomendada | CRITICA |

---

## Escenarios Gherkin

### CB-001: Manifest invalido al hacer evol-init (profile inexistente)

```gherkin
Feature: Inicializacion de proyecto con profile invalido

  Background:
    Given el binario evol-init esta disponible en PATH
    And no existe evol.profile.yml en el directorio actual
    And los profiles validos son: "default", "lean", "enterprise"

  Scenario: Profile inexistente produce error con lista de alternativas
    When el usuario ejecuta "evol-init --profile perfil_inexistente"
    Then el proceso termina con exit code 1
    And stderr contiene "Profile 'perfil_inexistente' no existe"
    And stderr contiene la lista de profiles disponibles: "default, lean, enterprise"
    And no se crea ningun directorio ".evol" en el filesystem
    And no se escribe ningun archivo parcial

  Scenario: Error no deja artefactos parciales en disco
    Given el directorio ".evol" no existe antes de la ejecucion
    When el usuario ejecuta "evol-init --profile perfil_inexistente"
    Then el directorio ".evol" no existe despues de la ejecucion

  Scenario: La lista de profiles en el error es siempre actualizada
    Given existe un profile personalizado "custom-lean" en el directorio de profiles
    When el usuario ejecuta "evol-init --profile inexistente"
    Then stderr contiene "custom-lean" en la lista de profiles disponibles
```

---

### CB-004: Recall con Memoria Persistente no disponible (solo snapshot JSON)

```gherkin
Feature: Recall de agente cuando Memoria Persistente no esta disponible

  Background:
    Given el archivo "memoria_persistente-snapshot.json" existe en ".evol/memory/"
    And el snapshot contiene datos del agente "evol-researcher" con fecha "2026-05-01"
    And Memoria Persistente no esta disponible (proceso no corre, puerto cerrado)

  Scenario: Recall carga desde snapshot local con advertencia
    When el usuario ejecuta "evol-memory recall --agent evol-researcher"
    Then el proceso termina con exit code 0
    And stdout contiene los datos del agente cargados desde el snapshot
    And stderr contiene "Memoria Persistente no disponible: usando snapshot local"
    And stderr contiene la fecha del snapshot "2026-05-01"
    And se indica que los datos pueden estar desactualizados

  Scenario: Recall falla correctamente si tampoco existe snapshot
    Given el archivo "memoria_persistente-snapshot.json" no existe
    When el usuario ejecuta "evol-memory recall --agent evol-researcher"
    Then el proceso termina con exit code 1
    And stderr contiene "Sin fuente de datos disponible para recall"
    And stderr sugiere ejecutar "evol-memory snapshot" cuando Memoria Persistente este disponible

  Scenario: Los datos cargados desde snapshot son de solo lectura
    When el usuario ejecuta "evol-memory recall --agent evol-researcher"
    Then AGENT_MEMORY.md se carga con flag "[snapshot-readonly]" en el header
    And cualquier intento de write sobre esos datos produce un warning explicito
```

---

### CB-007: Leccion duplicada en evol-lessons (similaridad Jaccard > 0.70)

```gherkin
Feature: Deduplicacion fuzzy de lecciones por similitud Jaccard

  Background:
    Given lecciones.md contiene la leccion ID "L-042":
      """
      No hacer commits directos a la rama main. Usar feature branches y PR obligatorio.
      """
    And el umbral de deduplicacion es EVOL_JACCARD_THRESHOLD=0.70

  Scenario: Leccion con similitud sobre umbral es rechazada
    When el usuario ejecuta:
      """
      evol-lessons add "Evitar push directo a main, siempre trabajar en feature branches con pull request"
      """
    Then el proceso termina con exit code 2
    And stderr contiene "Leccion similar detectada: L-042"
    And stderr contiene el valor Jaccard calculado (mayor o igual a 0.70)
    And stderr muestra el texto de la leccion existente L-042
    And lecciones.md no es modificado

  Scenario: Leccion con similitud bajo umbral es aceptada
    When el usuario ejecuta:
      """
      evol-lessons add "Los hotfixes deben derivarse de main y mergearse a main y develop"
      """
    Then el proceso termina con exit code 0
    And la nueva leccion es agregada a lecciones.md con un ID nuevo
    And la similitud con otras lecciones existentes es menor a 0.70

  Scenario: El umbral es configurable por variable de entorno
    Given EVOL_JACCARD_THRESHOLD=0.50
    When el usuario ejecuta una leccion con similitud Jaccard de 0.65 respecto a L-042
    Then el proceso termina con exit code 2
    And la leccion es rechazada por superar el umbral de 0.50

  Scenario: El reporte de colision incluye suficiente informacion para decidir
    When una leccion nueva es rechazada por similitud
    Then stderr contiene: ID de la leccion en colision, valor Jaccard, texto completo de la existente
    And stderr sugiere usar "evol-lessons update L-042" si la intencion era enriquecer la existente
```

---

### CB-008: evol-memory con EVOL_MEMORY=1 pero sin LLM_API_KEY (mock fallback)

```gherkin
Feature: Fallback a resumen heuristico cuando LLM_API_KEY no esta disponible

  Background:
    Given la variable de entorno EVOL_MEMORY=1 esta configurada
    And la variable LLM_API_KEY no esta configurada en el entorno
    And existen entradas en el journal de hoy para resumir

  Scenario: Resumen heuristico se genera sin crash
    When evol-memory.py ejecuta una operacion de resumen de sesion
    Then el proceso termina con exit code 0
    And AGENT_MEMORY.md es generado o actualizado con resumen heuristico
    And stderr contiene "LLM_API_KEY no disponible: usando resumen heuristico"
    And el resumen en AGENT_MEMORY.md esta marcado con "[mock-summary]"

  Scenario: El resumen heuristico contiene al menos entidades y hechos extraidos
    When evol-memory.py genera resumen en modo mock
    Then AGENT_MEMORY.md contiene una seccion "Entidades detectadas"
    And AGENT_MEMORY.md contiene una seccion "Hechos del dia"
    And las secciones tienen contenido derivado del journal, no texto placeholder

  Scenario: La operacion de busqueda no se ve afectada por la ausencia de LLM_API_KEY
    When el usuario ejecuta "evol-memory search 'gate key'"
    Then el proceso termina con exit code 0
    And los resultados de busqueda BM25 se devuelven normalmente
    And no se muestra warning relacionado con LLM_API_KEY para operaciones de busqueda

  Scenario: Con LLM_API_KEY presente el comportamiento cambia
    Given LLM_API_KEY="sk-test-key" configurado en el entorno
    When evol-memory.py ejecuta una operacion de resumen
    Then el intento usa el LLM para resumir
    And el resumen en AGENT_MEMORY.md no contiene la marca "[mock-summary]"
```

---

### CB-015: evol-init --profile lean sin wrapper global instalado

```gherkin
Feature: Bootstrap de proyecto sin instalacion global del wrapper

  Background:
    Given el repositorio evol-dd esta clonado en el directorio actual
    And el script "./scripts/evol-init.sh" existe en el repositorio
    And el comando "evol-init" no esta disponible en PATH del sistema

  Scenario: evol-init relativo funciona cuando el global no esta instalado
    When el usuario ejecuta "./scripts/evol-init.sh --profile lean" desde el directorio del proyecto
    Then el proceso termina con exit code 0
    And el directorio ".evol" es creado con la estructura del profile "lean"
    And "evol.profile.yml" es generado con profile=lean
    And stderr contiene "Wrapper global no instalado. Ejecutando desde ruta relativa."
    And stderr contiene instruccion para instalar el wrapper global

  Scenario: El warning de instalacion incluye el comando exacto para instalar
    When el usuario ejecuta evol-init desde ruta relativa sin wrapper global
    Then stderr contiene un comando de instalacion ejecutable, como:
      """
      Para instalar globalmente: ./scripts/install.sh o pip install -e .
      """

  Scenario: La ausencia del wrapper global no impide el bootstrap completo
    Given el comando "evol-init" no esta en PATH
    When el usuario ejecuta "./scripts/evol-init.sh --profile lean"
    Then todos los artefactos del profile lean son creados correctamente
    And el proyecto queda en estado operativo para continuar con evol-gate.py init

  Scenario: El profile lean genera exactamente los artefactos minimos esperados
    When el bootstrap con profile lean completa correctamente
    Then existen los archivos: ".evol/", "evol.profile.yml", "memoria.md", "lecciones.md"
    And no existen artefactos de profiles mas complejos como "DISCOVERY.md" o "THREATS.md"
```
