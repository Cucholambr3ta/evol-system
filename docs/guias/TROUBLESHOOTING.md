# TROUBLESHOOTING — Errores Conocidos y Soluciones

Esta guia cubre los errores mas frecuentes en Evol-DD, su causa raiz y los pasos de verificacion para confirmar que la solucion fue efectiva. Los errores estan ordenados por subsistema.

---

## Tabla de errores

| # | Error | Subsistema | Severidad |
|---|-------|-----------|-----------|
| 1 | `evol-lessons: invalid choice` al usar `--project` | CLI / Lessons | Media |
| 2 | Hook pre-bash bloquea comandos con `grep` y regex `?` | Hooks | Alta |
| 3 | `evol-adapt.sh` no genera commands para IDE nuevo | Adapters | Media |
| 4 | `evol-doctor` reporta Modo BASE con Memoria Persistente instalado | Doctor / PATH | Media |
| 5 | `validate-registry` falla con "Additional properties not allowed" | Registry | Alta |
| 6 | `evol-memory` en modo mock aunque `EVOL_PROVIDER=anthropic` | Memory / Provider | Media |
| 7 | `git commit` bloqueado por gitflow hook (branch name invalido) | GitFlow / Hooks | Alta |
| 8 | `evol-init --profile lean` falla ("lean requiere evol-global-install.sh") | Init / Profiles | Alta |
| 9 | `evol-agent-lifecycle create` falla ("templates/agent.template.md not found") | Agent Lifecycle | Alta |

---

## Detalles y soluciones

### Error 1 — evol-lessons: invalid choice al usar --project

**Sintoma:**

```
evol-lessons search "query" --project mi-proyecto
error: argument --project: invalid choice
```

**Causa:**

El argparser de `evol-lessons.py` no incluye el flag `--project`. El motor de lecciones opera sobre `lecciones.md` en el directorio de trabajo actual (CWD). No hay soporte para multi-proyecto via flag — el aislamiento se logra por CWD.

**Solucion:**

Cambiar al directorio del proyecto antes de invocar el comando:

```bash
cd /ruta/al/proyecto
evol-lessons search "query"
```

Para busqueda cruzada entre proyectos, usar directamente `grep` sobre multiples `lecciones.md`:

```bash
grep -r "patron de busqueda" */lecciones.md
```

**Verificacion:**

```bash
evol-lessons search "test" && echo "OK"
```

---

### Error 2 — Hook pre-bash bloquea comandos con grep y regex ?

**Sintoma:**

El hook `pre:bash` bloquea comandos que contienen `grep` con expresiones regulares que incluyen `?`, `+`, `{`, `}` sin escapar, o patrones que el hook interpreta como peligrosos.

```
[hook] pre:bash: BLOCKED — pattern matches dangerous command signature
```

**Causa:**

El hook `pre:bash` tiene un sistema de patrones que evalua el comando antes de ejecutarlo. Los regex del hook pueden generar falsos positivos cuando el comando del usuario contiene caracteres que coinciden con los patrones de deteccion de comandos peligrosos. El problema mas comun es usar `grep -P` (Perl regex) con cuantificadores como `?` o `+` sin escapar correctamente en el contexto del hook evaluator.

**Solucion:**

Opcion A — Usar la flag de bypass del hook para ese comando especifico:

```bash
EVOL_HOOK_BYPASS=pre:bash grep -P "patron[?]" archivo
```

Opcion B — Reformular el comando para evitar el patron disparador:

```bash
# En lugar de:
grep -P "api[_-]?key" archivo

# Usar:
grep -E "api[_-]?key" archivo
# o escapar el caracter en la expresion:
grep "api._key" archivo
```

Opcion C — Si es un falso positivo sistematico, reportar el patron en `.agent/hooks/scripts/pre-bash.sh` con el contexto del comando que lo dispara.

**Verificacion:**

```bash
EVOL_HOOK_BYPASS=pre:bash grep "test" README.md && echo "bypass OK"
```

---

### Error 3 — evol-adapt.sh no genera commands para IDE nuevo

**Sintoma:**

Agregar un nuevo target de IDE a `evol-adapt.sh` y ejecutar `bash scripts/evol-adapt.sh all` no genera la carpeta ni los archivos del IDE nuevo.

**Causa:**

`evol-adapt.sh all` itera sobre un array fijo de targets definidos en el script. Si el nuevo IDE no esta en ese array, `all` lo omite silenciosamente. Ademas, la funcion `check_file_exists` bloquea la sobreescritura si ya existe algun archivo previo del target.

**Solucion:**

Paso 1 — Verificar que la funcion del IDE nuevo esta definida en el script:

```bash
grep -n "generate_" scripts/evol-adapt.sh
```

Paso 2 — Verificar que el nuevo target esta en el case/array de `all`:

```bash
grep -A 20 '"all"' scripts/evol-adapt.sh
```

Paso 3 — Si el target existe pero hay archivos previos bloqueando la generacion:

```bash
# Identificar los archivos bloqueantes
bash scripts/evol-adapt.sh nuevo-ide --dry-run

# Eliminar manualmente los archivos que bloquean
rm -rf .nuevo-ide/commands/

# Regenerar
bash scripts/evol-adapt.sh nuevo-ide
```

**Verificacion:**

```bash
bash scripts/evol-adapt.sh nuevo-ide --dry-run
# debe listar los archivos que generaria sin error
```

---

### Error 4 — evol-doctor reporta Modo BASE con Memoria Persistente instalado

**Sintoma:**

```
[LOW] Dependencies: memoria_persistente not in PATH (optional)
```

A pesar de que `memoria_persistente --version` funciona en la terminal del usuario.

**Causa:**

`evol-doctor.sh` usa `command -v memoria_persistente` para detectar Memoria Persistente. Si memoria_persistente fue instalado en una ubicacion no-standard (por ejemplo `~/.local/bin` en un sistema donde ese directorio no esta en el PATH del entorno que usa el script), el check falla aunque el binario existe.

Esto ocurre frecuentemente cuando:
- El shell del usuario tiene `~/.local/bin` en PATH via `.bashrc` o `.zshrc`, pero el script se ejecuta en un subshell que no carga esos archivos.
- Memoria Persistente fue instalado en un virtualenv que no esta activo al correr `evol-doctor`.
- En CI, el PATH es mas restrictivo que en el entorno interactivo.

**Solucion:**

Opcion A — Activar el entorno donde Memoria Persistente fue instalado antes de correr doctor:

```bash
source ~/.venv/bin/activate
evol doctor
```

Opcion B — Pasar la ruta completa a través de la variable de entorno:

```bash
PATH="$HOME/.local/bin:$PATH" evol doctor
```

Opcion C — Instalar memoria_persistente en el entorno activo al usar el framework:

```bash
pip install memoria_persistente
evol doctor  # ahora debe detectar memoria_persistente
```

**Verificacion:**

```bash
which memoria_persistente          # debe retornar la ruta
evol doctor | grep -i memoria_persistente  # debe decir "detected"
```

---

### Error 5 — validate-registry falla con "Additional properties not allowed"

**Sintoma:**

```
python3 scripts/validate-registry.py --strict
ValidationError: Additional properties are not allowed
  ('custom_field' was unexpected)
```

**Causa:**

`prompts/agents/registry.json` contiene una propiedad en alguna entrada del array `agents` que no esta definida en `schemas/agent-registry.schema.json`. El schema usa `"additionalProperties": false`, lo que significa que cualquier campo fuera del schema declarado es un error de validacion.

Ocurre al agregar un agente manualmente con campos inventados, o al copiar una entrada de un sistema externo (como xdd-*) que tiene propiedades distintas.

**Solucion:**

Paso 1 — Identificar la entrada con el campo invalido:

```bash
python3 -c "
import json
with open('prompts/agents/registry.json') as f:
    reg = json.load(f)
for agent in reg['agents']:
    print(agent.get('id'), list(agent.keys()))
"
```

Paso 2 — Ver que propiedades permite el schema:

```bash
python3 -c "
import json
with open('schemas/agent-registry.schema.json') as f:
    schema = json.load(f)
print(list(schema['items']['properties'].keys()))
"
```

Paso 3 — Eliminar o renombrar el campo invalido en `registry.json`. Los campos estandar son: `id`, `name`, `category`, `description`, `prompt_file`, `capabilities`, `triggers`.

**Verificacion:**

```bash
python3 scripts/validate-registry.py --strict && echo "OK"
```

---

### Error 6 — evol-memory en modo mock aunque EVOL_PROVIDER=anthropic

**Sintoma:**

```bash
export EVOL_PROVIDER=anthropic
evol-memory summarize
[provider] INFO: using mock provider (LLM_API_KEY not set)
```

**Causa:**

`_evol_common.py` usa `get_provider()` que resuelve en este orden: primero verifica `EVOL_PROVIDER`, luego busca `LLM_API_KEY` en el entorno. Si `LLM_API_KEY` no esta definida, el provider cae a `MockProvider` independientemente del valor de `EVOL_PROVIDER`. Esto es comportamiento intencional — el framework no falla en ausencia de credenciales, degrada graciosamente a mock.

**Solucion:**

```bash
export LLM_API_KEY=sk-ant-...
export EVOL_PROVIDER=anthropic
evol-memory summarize
```

Si la key esta en un archivo `.env`:

```bash
source .env
evol-memory summarize
```

Para persistir sin exponer la key en el historial de shell:

```bash
# En .env (gitignored):
LLM_API_KEY=sk-ant-tu-key-aqui
EVOL_PROVIDER=anthropic

# Al inicio de sesion:
source .env
```

**Verificacion:**

```bash
python3 -c "
import os
os.environ['LLM_API_KEY'] = os.environ.get('LLM_API_KEY', '')
from evol_cli import get_provider_name
print(get_provider_name())
"
# debe imprimir "anthropic" no "mock"
```

---

### Error 7 — git commit bloqueado por gitflow hook (branch name invalido)

**Sintoma:**

```
[pre-commit] ERROR: branch 'mi-cambio' does not follow GitFlow convention
Commit blocked. Rename branch to: feature/mi-cambio, fix/mi-cambio, etc.
```

**Causa:**

El hook `pre:commit:gitflow` (registrado en `.agent/hooks/scripts/`) verifica que el nombre del branch activo sigue el patron de GitFlow antes de aceptar cada commit. Los branches que no tienen el prefijo `feature/`, `fix/`, `hotfix/`, `release/`, `docs/`, `refactor/`, `chore/` son rechazados.

**Solucion:**

Renombrar el branch activo al formato correcto:

```bash
# Ver el branch actual
git branch --show-current

# Renombrar (git rename local)
git branch -m mi-cambio feature/mi-cambio

# Verificar
git branch --show-current  # debe mostrar feature/mi-cambio

# Intentar el commit nuevamente
git commit -m "feat(scope): descripcion"
```

Si el branch ya tiene un remote tracking, actualizar la referencia remota despues del rename:

```bash
git push origin -u feature/mi-cambio
git push origin --delete mi-cambio  # eliminar el branch viejo del remote
```

**Verificacion:**

```bash
git branch --show-current  # debe mostrar el nombre con prefijo valido
git commit --dry-run       # no debe mostrar el error del hook
```

---

### Error 8 — evol-init --profile lean falla ("lean requiere evol-global-install.sh")

**Sintoma:**

```bash
bash scripts/evol-init.sh ./proyecto --profile=lean
[error] Profile 'lean' requires global framework installation.
Run: bash scripts/evol-global-install.sh
```

**Causa:**

El perfil `lean` no copia scripts al proyecto destino — asume que el framework esta instalado globalmente en el sistema (via `evol-global-install.sh` que instala en `~/.local/bin`). Si el global install no se ha ejecutado, el perfil `lean` falla porque los scripts que el proyecto necesita no estan disponibles en PATH.

A diferencia de `minimal` y `core` que son autocontenidos, `lean` es una referencia ligera al framework global.

**Solucion:**

Ejecutar el global install primero:

```bash
bash scripts/evol-global-install.sh

# Verificar que los scripts quedaron en PATH
which evol-doctor
which evol-lessons

# Luego inicializar el proyecto con lean
bash scripts/evol-init.sh ./proyecto --profile=lean
```

Si no se quiere usar global install, cambiar a un perfil autocontenido:

```bash
bash scripts/evol-init.sh ./proyecto --profile=minimal
```

**Verificacion:**

```bash
which evol-doctor && echo "global install OK"
bash scripts/evol-init.sh ./proyecto --profile=lean --dry-run
```

---

### Error 9 — evol-agent-lifecycle create falla ("templates/agent.template.md not found")

**Sintoma:**

```bash
evol-agent create --name "specialist" --task "tarea especifica"
[ERROR] Template not found: templates/agent.template.md
```

**Causa:**

`evol-agent-lifecycle.py` busca el template en dos ubicaciones: primero en `templates/agent.template.md` relativo al CWD, luego en `<EVOL_DATA_DIR>/templates/agent.template.md`. Si el comando se ejecuta fuera de la raiz del proyecto framework, o si `EVOL_DATA_DIR` no apunta al directorio correcto, el template no se encuentra.

**Solucion:**

Opcion A — Ejecutar el comando desde la raiz del proyecto:

```bash
cd /ruta/al/proyecto-evol-dd
evol-agent create --name "specialist" --task "tarea"
```

Opcion B — Definir `EVOL_DATA_DIR` apuntando al directorio que contiene `templates/`:

```bash
export EVOL_DATA_DIR=/ruta/al/proyecto-evol-dd
evol-agent create --name "specialist" --task "tarea"
```

Opcion C — Si el template no existe en el proyecto (instalacion incompleta):

```bash
# Verificar si el template existe
ls templates/agent.template.md

# Si no existe, re-inicializar con el perfil adecuado
bash scripts/evol-init.sh . --profile=developer
```

**Verificacion:**

```bash
ls templates/agent.template.md && echo "template OK"
evol-agent create --name "test-agent" --task "test task" --dry-run 2>/dev/null || \
  evol-agent create --name "test-agent" --task "test task"
```

---

