---
name: evol-update
trigger: /evol-update
description: Actualiza el core global de Evol-DD a la última versión y genera un reporte de novedades.
---

# /evol-update — Actualización Global (Core)

> Actualiza la instalación global del framework Evol-DD (vía pip/pipx) y genera un reporte de los cambios antes de aplicarlos a los proyectos.

**Cuándo usar:**
Para descargar e instalar la versión más reciente del framework a nivel sistema.

---

## Fases de Ejecución del Agente

### Fase 1: Instalación de la Actualización
Ejecuta el siguiente comando para actualizar el framework globalmente y regenerar los triggers en el IDE:
```bash
pipx upgrade evol-dd && evol
```
*(Nota: si el usuario utiliza `pip` global, ajusta a `pip install --upgrade evol-dd && evol`).*

### Fase 2: Reporte de Actualización (Core)
Una vez que el comando haya finalizado:
1. Revisa la salida del comando para determinar a qué versión se actualizó.
2. Lee el archivo `CHANGELOG.md` del código fuente (o las notas del release) para resumirle al usuario cuáles son las nuevas features, mejoras y fixes de esta versión.
3. Genera un reporte corto destacando las novedades.

### Fase 3: Llamado a la Acción
Indica explícitamente al usuario que el sistema global ha sido actualizado, pero que su proyecto local aún necesita heredar estos cambios.
- Sugiere al usuario ejecutar el comando:
  **`/evol-update-project`**
  Para inyectar estas actualizaciones de forma segura en el proyecto actual.
