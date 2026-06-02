# Instalación

## Requisitos

- Python 3.10+
- Git
- (Opcional) MemPalace CLI para Modo COMPLETO

## Instalación global

```bash
bash scripts/evol-global-install.sh
```

## Bootstrap de proyecto

```bash
bash scripts/evol-init.sh /path/to/project --profile=core
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

- **COMPLETO**: MemPalace activo, búsqueda semántica
- **BASE**: Sin MemPalace, funciona completamente

## Actualización

Evol-DD tiene dos modos de actualización según cómo fue instalado.

### Modo pip (recomendado)

```bash
# 1. Verificar si hay actualización disponible
evol update check

# 2. Aplicar la actualización (detecta pipx o pip automáticamente)
evol update apply

# 3. Para actualizar solo el paquete sin propagar al proyecto
pipx upgrade evol-dd
# o
pip install --upgrade evol-dd
```

`evol update apply` hace tres cosas automáticamente:
- Actualiza el paquete pip/pipx a la última versión
- Propaga los workflows SSoT actualizados al proyecto activo (`.agent/workflows/`)
- Regenera las configs IDE (`evol-adapt.sh all`)

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