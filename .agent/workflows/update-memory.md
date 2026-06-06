---
name: update-memory
trigger: /update-memory
description: Revisa y actualiza todos los documentos de memoria persistente (decisiones, convenciones, riesgos).
---

# Update Memory

Este workflow es un gatillo para mantener la **Memoria Persistente** estructurada siempre al día.

## 1. Revisión de Contexto
- El agente **debe** leer el archivo `WORKING-CONTEXT.md` actual y el historial de cambios recientes.
- El agente **debe** revisar el contenido de la carpeta `acuerdos/memoria/`:
  - `acuerdos/memoria/decisiones.md`
  - `acuerdos/memoria/convenciones.md`
  - `acuerdos/memoria/riesgos.md`

## 2. Actualización de Átomos
- Si existen nuevas decisiones arquitectónicas, dependencias, o convenciones adoptadas que no estén registradas, el agente actualizará los átomos correspondientes.
- Si hay riesgos mitigados o nuevos, se actualizará `riesgos.md`.

## 3. Consolidación
- Una vez actualizados los átomos, el agente debe ejecutar `python3 scripts/evol-memory.py memory-split` o notificar al usuario para asegurar que el `MEMORY.md` agregado se regenere.

## Criterios de Salida
1. Los 3 átomos de memoria reflejan el estado real del proyecto.
2. No hay redundancia de información temporal (solo hechos persistentes).
3. El agregado `MEMORY.md` está sincronizado.
