---
name: evol-update-project
trigger: /evol-update-project
description: Orquesta la actualización de un proyecto existente a la nueva versión de Evol-DD, garantizando la preservación de mejoras locales, previniendo regresiones y resolviendo conflictos de manera inteligente.
---

# /evol-update-project — Actualización Segura de Proyecto

> Inyecta la actualización del core de Evol-DD al proyecto actual, resolviendo conflictos y protegiendo las personalizaciones locales.

**Cuándo usar:**
Después de haber actualizado el core con `/evol-update`, cuando requieras que tu proyecto local herede las nuevas disciplinas, workflows y estructuras sin perder tu trabajo local.

---

## Fases de Ejecución del Agente

### Fase 1: Análisis de Impacto y Prevención de Conflictos
Antes de ejecutar cualquier comando de actualización, **DEBES** analizar el estado local:
1. **Identificar modificaciones locales**:
   - Comprueba si el usuario ha modificado o mejorado localmente workflows (`.agent/workflows/`), skills (`.agents/skills/`), o plantillas (`templates/`). 
   - Utiliza comandos como `git status` o `git log --oneline -- <rutas>` para identificar si existen "skills ya mejoradas" u overrides locales.
2. **Detección de dependencias**: Revisa si el `evol.profile.yml` tiene módulos personalizados que la actualización pueda afectar.

### Fase 2: Reporte de Actualización (User Review)
Presenta al usuario un reporte estructurado y claro indicando:
- **Riesgos de Sobreescritura (Conflictos)**: Lista explícita de archivos locales modificados que la herramienta de actualización podría sobrescribir.
- **Plan de Mitigación propuesto**: 
  - Si hay un workflow/skill local mejorado, propone hacer un backup de la versión local en una ruta temporal (`.evol/backups/`).
  - Indica claramente qué partes de la actualización conviene aplicar tal cual, y cuáles requerirán un *merge* manual posterior.
- **Pide explícitamente aprobación** ("¿Procedo a realizar el backup e inyectar la actualización en el proyecto?").

### Fase 3: Ejecución y Consolidación
Una vez que el usuario **APRUEBA** el reporte:
1. Ejecuta backups preventivos de las skills/workflows en conflicto.
2. Ejecuta la propagación oficial:
   ```bash
   evol update apply
   ```
   *(Esto aplicará las plantillas actualizadas y correrá `evol-init.sh --upgrade` para actualizar las carpetas base y fusionar `evol.profile.yml` inteligentemente).*
3. **Restauración Inteligente**: Si hubo backups, compara las diferencias (`diff`) entre la versión recién descargada y el backup local. Integra las mejoras locales del usuario con la nueva versión.
4. Ejecuta `/evol doctor` para asegurar que el entorno del proyecto quede 100% estable.
