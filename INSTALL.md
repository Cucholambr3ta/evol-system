# Instalacion

## Requisitos

- Python 3.10+
- pipx (recomendado) o pip
- Git

## Instalacion

```bash
pipx install evol-dd && evol
```

El segundo comando (`evol`) detecta que es la primera ejecucion y configura
automaticamente el trigger `/evol` en los 7 IDEs: Claude Code, OpenCode,
Cursor, Windsurf, VSCode Copilot, Antigravity y Codex.

Desde ese momento, abrir cualquier carpeta en cualquier IDE muestra `/evol`
disponible sin configuracion adicional.

### Si no tienes pipx

```bash
# Ubuntu / Debian / Linux Mint
sudo apt install pipx && pipx ensurepath && source ~/.bashrc

# macOS
brew install pipx && pipx ensurepath

# Windows (PowerShell)
python -m pip install --user pipx && python -m pipx ensurepath
```

Luego:
```bash
pipx install evol-dd && evol
```

## Bootstrap de proyecto (opcional)

```bash
evol init /path/to/project --profile core
```

## Perfiles

| Perfil | Descripción |
|--------|-------------|
| minimal | Nucleo mínimo con lecciones y memoria |
| core | Estándar para proyectos |
| developer | Desarrollo activo con agentes efímeros |
| security | Enfoque SecDD |
| research | Investigación y evolución |
| full | Instalación completa |
| lean | Ligthweight, requiere global install |

## Modos de operación

- **COMPLETO**: Memoria Persistente activo, búsqueda semántica
- **BASE**: Sin Memoria Persistente, funciona completamente

## Actualizacion

```bash
pipx upgrade evol-dd && evol
```

Al detectar una nueva version, `evol` reinstala los triggers actualizados
en todos los IDEs automaticamente.

### Modo avanzado (propagar a proyectos existentes)

```bash
# Verificar si hay actualizacion disponible
evol update check

# Actualizar paquete + propagar workflows al proyecto activo
evol update apply

### Modo legacy (scripts copiados localmente)

Si instalaste con `evol-init.sh --legacy`, los scripts están copiados en tu proyecto:

```bash
# Apuntar al repo fuente actualizado
export EVOL_SOURCE_DIR=/ruta/al/repo/evol-dd

# Verificar qué hay disponible
evol update check

# Aplicar: copia scripts evol-*, propaga workflows, regenera IDE
evol update apply --project /tu-proyecto
```

### Verificar versión activa

```bash
evol --version           # versión del paquete instalado
evol update status       # versión + modo de instalación + fuente
evol doctor --version    # versión del doctor (debe coincidir)
```

### Anti-bug de empaquetado

El paquete incluye todos los data dirs (`manifests/`, `templates/`, `.agent/workflows/`,
`docs/`, `VERSION`) para que `evol --version` y `evol init --list-profiles` funcionen
correctamente en instalaciones pipx/wheel sin repositorio local clonado.