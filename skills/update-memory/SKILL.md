---
name: update-memory
description: >
  Revisa y actualiza todos los documentos de memoria persistente (decisiones, convenciones, riesgos) con Memory v2.0.
  Ejecutar despues de cambios significativos o al final de sesion.
category: memory
trigger: /update-memory
triggers:
  - /update-memory
  - "actualizar memoria"
  - "sincronizar memoria"
---

# /update-memory — Actualizacion de Memoria Persistente

> Gatillo global para mantener **todo el ecosistema de Memoria Persistente** estructurado y actualizado usando Memory v2.0.

## 1. Revision de Contexto

### 0. Sync git (obligatorio antes de leer)
```bash
git pull --ff-only 2>/dev/null || echo "[sync] Conflicto de merge — resolver ANTES de continuar con update-memory"
```
Si hay conflictos de merge, **detenerse** y pedir resolucion al usuario. No continuar con pasos 1-4 hasta que el repo este limpio.

### 1. Leer estado actual
El agente **debe** leer el estado actual del repositorio, los ultimos cambios en codigo, los commits recientes y los siguientes documentos de memoria:
- `WORKING-CONTEXT.md` (estado activo de desarrollo).
- `acuerdos/memoria/` (`decisiones.md`, `convenciones.md`, `riesgos.md`).
- `lecciones.md` (errores recientes o aprendizajes).
- `AGENT_MEMORY.md` (comportamiento y estilo del usuario).
- `memoria.md` (bitacora y flight recorder).

## 2. Actualizacion de Capas de Memoria
El agente procedera a actualizar sistematicamente las capas:

### A. Memoria Estructural (Atomos)
- Si existen nuevas decisiones arquitectonicas, dependencias, o convenciones adoptadas que no esten registradas, el agente actualizara `acuerdos/memoria/decisiones.md` y `convenciones.md`.
- Si hay riesgos mitigados o nuevos, se actualizara `acuerdos/memoria/riesgos.md`.

### B. Aprendizajes y Errores
- Extraer lecciones recientes de las interacciones, herramientas o bloqueos y anadirlas al archivo `lecciones.md` siguiendo el formato estandar de categorias.

### C. Preferencias del Agente/Usuario
- Anotar cualquier nuevo patron de interaccion, preferencia de codigo o regla descubierta en el archivo `AGENT_MEMORY.md`.

### D. Bitacora del Proyecto
- Registrar el estado actual de alto nivel, la fase de desarrollo y las tareas completadas en `memoria.md` para mantener el *flight recorder* actualizado.

## 3. Memory v2.0 Integration
Una vez actualizados los atomos, ejecutar los siguientes comandos v2:

### 3.1 Verbatim Storage
```bash
# Almacenar atomos actualizados en verbatim store
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/convenciones.md)" --tipo convencion
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/riesgos.md)" --tipo riesgo
```

### 3.2 Entity Extraction
```bash
# Extraer entidades de los atomos
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

## 4. Consolidacion
- Una vez actualizados los atomos de la Memoria Estructural, el agente debe ejecutar `python3 scripts/evol-memory.py memory-split` para asegurar que el `MEMORY.md` agregado se regenere.
- Verificar integridad con `python3 scripts/evol-memory.py edms-verify`.

## Criterios de Salida
1. Los 3 atomos de memoria en `acuerdos/memoria/` reflejan el estado real del proyecto.
2. El agregado `MEMORY.md` esta sincronizado.
3. Nuevas lecciones han sido indexadas en `lecciones.md`.
4. La bitacora `memoria.md` y el estado `AGENT_MEMORY.md` estan al dia.
5. **v2**: Atomos almacenados en verbatim store.
6. **v2**: Entidades extraidas y relaciones creadas.
7. **v2**: Sin conflictos detectados.

---

## Relacion con otros comandos

| Comando | Quando usar |
|---------|-------------|
| `/update-memory` | Actualizar la memoria del proyecto (atomos, lecciones, MEMORY.md) |
| `/update-context` | Sincronizar contexto desde archivos actualizados por otro entorno |
| `session:start:context-load` | Hook automatico al iniciar sesion (ligero, ~170 tokens) |
