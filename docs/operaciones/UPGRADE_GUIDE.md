# Upgrade Guide

Esta guía documenta el proceso de actualización de Evol-DD. Existen tres escenarios dependiendo del estado actual de tu proyecto y del framework.

## Escenario A: Proyectos Existentes (Upgrade Regular)

Si ya tienes un proyecto inicializado con Evol-DD y quieres heredar las nuevas características, disciplinas y scripts del framework actualizado, el proceso es:

1. **Actualizar el paquete global de Evol-DD:**
   ```bash
   pipx upgrade evol-dd
   # o si usaste pip: pip install --upgrade evol-dd
   ```

2. **Propagar la actualización al proyecto:**
   Navega a la carpeta de tu proyecto y ejecuta:
   ```bash
   evol update apply
   ```

**¿Qué ocurre bajo el capó?**
- Se copian las nuevas plantillas (templates) y los workflows (SSoT) al directorio `.agent/`.
- Se ejecuta `evol-init.sh --upgrade` automáticamente. Esto significa que:
  - Se crearán estructuras de carpetas base faltantes (ej. `acuerdos/` en migraciones desde la v0.2.x a la v0.3.x).
  - Se añadirán nuevos módulos al archivo `evol.profile.yml` correspondientes a tu perfil, sin sobrescribir o eliminar configuraciones previas que ya tuvieras.
  - Se copiarán scripts nuevos o actualizados, preservando los archivos locales que hayas modificado.
- Se regeneran las configuraciones del IDE (Claude Code, Cursor, Windsurf, OpenCode, etc.) mediante `evol-adapt.sh all`.

> **Vía Agentes:** Puedes orquestar todo este flujo pidiéndole al agente que ejecute `/evol-update` (para actualizar el core global y ver las novedades) y luego `/evol-update-project` (para que el agente prevenga conflictos, resguarde tus mejoras locales e inyecte la actualización al proyecto).

## Escenario B: Proyectos Nuevos (Fresh Init)

Si estás empezando un proyecto desde cero con la versión más reciente del framework:

1. Crea el directorio y ejecuta:
   ```bash
   evol-init.sh . --profile=developer
   # (Puedes usar minimal, core, security, research, full, lean o custom)
   ```
2. Este comando creará toda la estructura de cero, instalará los módulos del perfil, y creará un archivo `evol.profile.yml` limpio.

## Escenario C: Re-Inicialización Forzada (Upgrade Manual)

Si por algún motivo necesitas forzar la re-inicialización o actualización del perfil de un proyecto (por ejemplo, cambiaste el perfil de `lean` a `full`), puedes usar explícitamente el flag `--upgrade`:

```bash
evol-init.sh . --profile=full --upgrade
```

**Comportamiento de `--upgrade`:**
- **No destructivo:** No sobrescribirá tu `.gitignore` ni los archivos que ya existan en el disco.
- **Merge de perfil:** Agregará los módulos nuevos del perfil a `evol.profile.yml` sin borrar la lista anterior.
- Instalará todas las carpetas, flujos y archivos que falten.

## Migración desde X-DD

Si vienes de la versión anterior del framework (X-DD) y estás haciendo la transición a Evol-DD, consulta la [RETROFIT_GUIDE.md](../RETROFIT_GUIDE.md) para los pasos específicos de migración de estado y variables de entorno.
