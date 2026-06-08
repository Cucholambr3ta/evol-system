---
name: update-memory
trigger: /update-memory
description: Revisa y actualiza todos los documentos de memoria persistente (decisiones, convenciones, riesgos) con Memory v2.0.
---

# Update Memory

Este workflow es un gatillo global para mantener **todo el ecosistema de Memoria Persistente** estructurado y actualizado usando Memory v2.0.

## 1. Revisión de Contexto
El agente **debe** leer el estado actual del repositorio, los últimos cambios en código, los commits recientes y los siguientes documentos de memoria:
- `WORKING-CONTEXT.md` (estado activo de desarrollo).
- `acuerdos/memoria/` (`decisiones.md`, `convenciones.md`, `riesgos.md`).
- `lecciones.md` (errores recientes o aprendizajes).
- `AGENT_MEMORY.md` (comportamiento y estilo del usuario).
- `memoria.md` (bitácora y flight recorder).

## 2. Actualización de Capas de Memoria
El agente procederá a actualizar sistemáticamente las capas:

### A. Memoria Estructural (Átomos)
- Si existen nuevas decisiones arquitectónicas, dependencias, o convenciones adoptadas que no estén registradas, el agente actualizará `acuerdos/memoria/decisiones.md` y `convenciones.md`.
- Si hay riesgos mitigados o nuevos, se actualizará `acuerdos/memoria/riesgos.md`.

### B. Aprendizajes y Errores
- Extraer lecciones recientes de las interacciones, herramientas o bloqueos y añadirlas al archivo `lecciones.md` siguiendo el formato estándar de categorías.

### C. Preferencias del Agente/Usuario
- Anotar cualquier nuevo patrón de interacción, preferencia de código o regla descubierta en el archivo `AGENT_MEMORY.md`.

### D. Bitácora del Proyecto
- Registrar el estado actual de alto nivel, la fase de desarrollo y las tareas completadas en `memoria.md` para mantener el *flight recorder* actualizado.

## 3. Memory v2.0 Integration
Una vez actualizados los átomos, ejecutar los siguientes comandos v2:

### 3.1 Verbatim Storage
```bash
# Almacenar átomos actualizados en verbatim store
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/convenciones.md)" --tipo convencion
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/riesgos.md)" --tipo riesgo
```

### 3.2 Entity Extraction
```bash
# Extraer entidades de los átomos
python3 scripts/evol-memory.py edms-extract "$(cat acuerdos/memoria/decisiones.md)"
python3 scripts/evol-memory.py edms-extract "$(cat acuerdos/memoria/convenciones.md)"
python3 scripts/evol-memory.py edms-extract "$(cat acuerdos/memoria/riesgos.md)"
```

### 3.3 Auto-Linking
```bash
# Crear relaciones entre entidades
python3 scripts/evol-memory.py edms-link "$(cat acuerdos/memoria/decisiones.md)"
python3 scripts/evol-memory.py edms-link "$(cat acuerdos/memoria/convenciones.md)"
```

### 3.4 Conflict Detection
```bash
# Detectar contradicciones en la memoria
python3 scripts/evol-memory.py edms-conflicts
```

## 4. Consolidación
- Una vez actualizados los átomos de la Memoria Estructural, el agente debe ejecutar `python3 scripts/evol-memory.py memory-split` para asegurar que el `MEMORY.md` agregado se regenere.
- Verificar integridad con `python3 scripts/evol-memory.py edms-verify`.

## Criterios de Salida
1. Los 3 átomos de memoria en `acuerdos/memoria/` reflejan el estado real del proyecto.
2. El agregado `MEMORY.md` está sincronizado.
3. Nuevas lecciones han sido indexadas en `lecciones.md`.
4. La bitácora `memoria.md` y el estado `AGENT_MEMORY.md` están al día.
5. **v2**: Átomos almacenados en verbatim store.
6. **v2**: Entidades extraídas y relaciones creadas.
7. **v2**: Sin conflictos detectados.
