---
description: Workflow X-DD — Sincronización del Palacio de la Memoria
---

# /mempalace-sync

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-059 | **Versión:** 3.0.0 | **Nivel:** Operativo
**Módulo Core:** `skill-mempalace-manager`

## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio de la fecha y hora en `memoria.md` (Art. 3 de la Constitución).

## 1. MISIÓN DEL FLUJO
Sincronizar de forma bidireccional el código fuente, la documentación Loci, las lecciones y las lecciones aprendidas del workspace con la base de datos de grafos local-first de **MemPalace**, asegurando que los agentes locales y el contenedor Nous-Hermes tengan un mapa mental exacto y actualizado en tiempo real.

## 2. DIRECTRICES INQUEBRANTABLES
- **Actualización Activa:** Ejecutar este workflow antes de cerrar cualquier sesión de desarrollo importante.
- **Validación Semántica:** Verificar que los perfiles Markdown no contengan wikilinks rotos o formatos de Obsidian obsoletos.
- **Higiene de Grafos:** Asegurarse de que el comando de minado no indexe directorios basura (como `node_modules`, `.git`, `.venv`, etc.).

## 3. FLUJO OPERATIVO DETALLADO
1. **Poda de Logs:** Opcionalmente limpiar archivos de log pesados utilizando `.agent/scripts/optimize_context.ps1`.
2. **Minado de Loci (`mempalace mine`):** Ejecutar el comando para re-analizar el código y las notas semánticas:
   ```bash
   mempalace mine "$PWD"
   ```
3. **Validación de Relaciones:** Ejecutar una consulta RAG simple de prueba para verificar que el indexador responde correctamente.
4. **Cierre de Vuelo:** Registrar el volumen de memoria semántica actualizado en `memoria.md`.

## 4. OBSERVABILIDAD (REGISTRO SEMÁNTICO)
Cada sincronización exitosa debe loggear un evento con formato:
```json
{
  "timestamp": "ISO-8601",
  "event": "mempalace_sync_completed",
  "data": {
    "workspace": "x-dd-integration",
    "loci_mined": "success"
  }
}
```

---
**Versión:** 3.0.0 | **Fecha:** 2026-05-17
X-DD System
