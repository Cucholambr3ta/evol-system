---
name: update-context
trigger: /update-context
description: Sincroniza contexto desde archivos de memoria actualizados por /update-memory con Memory v2.0. Usar al cambiar de IDE o maquina para que el agente conozca lo que otro entorno hizo.
---

# /update-context — Sincronizacion Cross-Environment con Memory v2.0

> Cuando trabajas en 2+ IDEs/maquinas sobre el mismo proyecto, `/update-context`
> lee todos los archivos de memoria que `/update-memory` actualiza y te inyecta
> el contexto completo usando **búsqueda híbrida v2** (vector + BM25 + graph).

---

## Protocolo

Al recibir `/update-context`, ejecutar en orden:

### 1. Sync git (opcional)

```bash
git pull --ff-only 2>/dev/null || echo "[sync] No hay repo remoto o hay cambios locales"
```

Si hay conflictos de merge, informar al usuario y pedir resolucion antes de continuar.

### 2. Leer archivos de memoria

Leer los siguientes archivos y extraer los puntos clave de cada uno:

| Archivo | Que extraer |
|---------|-------------|
| `acuerdos/memoria/decisiones.md` | Ultimas 5 decisiones arquitectonicas |
| `acuerdos/memoria/convenciones.md` | Convenciones activas (no todas, solo las relevantes) |
| `acuerdos/memoria/riesgos.md` | Riesgos activos (no mitigados) |
| `acuerdos/memoria/MEMORY.md` | Agregado de atomos (resumen general) |
| `lecciones.md` | Ultimas 3 lecciones relevantes |
| `memoria.md` | Estado actual del proyecto, fase, ultimo hito |
| `AGENT_MEMORY.md` | Preferencias del agente/usuario |
| `WORKING-CONTEXT.md` | Branch activo, fase, proximo paso |

### 3. Memory v2.0: Hybrid Search

Usar búsqueda híbrida v2 para contexto relevante:

```bash
# Buscar decisiones recientes
python3 scripts/evol-memory.py edms-hybrid-search "decisiones arquitectónicas" --top-k 5

# Buscar lecciones relevantes
python3 scripts/evol-memory.py edms-hybrid-search "lecciones aprendidas" --top-k 3

# Buscar riesgos activos
python3 scripts/evol-memory.py edms-hybrid-search "riesgos activos" --top-k 3

# Verificar entidades del proyecto
python3 scripts/evol-memory.py edms-entity "proyecto" --type technology
```

### 4. Presentar resumen estructurado

Despues de leer todos los archivos, presentar un resumen estructurado:

```
=== Contexto Sincronizado (v2) ===

[RAMA] Branch: <branch>, Fase: <fase>, Version: <version>

[DECISIONES]
- <decision 1>
- <decision 2>
- <decision 3>
- <decision 4>
- <decision 5>

[CONVENCIONES]
- <convencion 1>
- <convencion 2>
- <convencion 3>

[RIESGOS]
- <riesgo activo 1>
- <riesgo activo 2>

[LECCIONES]
- <leccion 1>
- <leccion 2>
- <leccion 3>

[ESTADO] <ultimo hito>
[PROXIMO] <siguiente paso>

[PREFERENCIAS]
- <preferencia 1>
- <preferencia 2>
- <preferencia 3>

[v2 ENTIDADES]
- <entidad 1>: <tipo> (confianza: <confianza>)
- <entidad 2>: <tipo> (confianza: <confianza>)

[v2 HÍBRIDA]
- <resultado 1>: <score>
- <resultado 2>: <score>

============================
```

### 5. Confirmar

Al finalizar, informar:
- Cuantos archivos se leyeron
- Si `git pull` trajo cambios nuevos
- Si el contexto esta actualizado o hay drift
- **v2**: Cuantas entidades se extrajeron
- **v2**: Cuantos resultados híbridos se encontraron

---

## Relacion con otros comandos

| Comando | Quando usar |
|---------|-------------|
| `/update-memory` | Actualizar la memoria del proyecto (atomos, lecciones, MEMORY.md) |
| `/update-context` | Sincronizar contexto desde archivos actualizados por otro entorno |
| `session:start:context-load` | Hook automatico al iniciar sesion (ligero, ~170 tokens) |

---

## Ejemplo de uso

```
Usuario: /update-context

Agente:
1. Ejecuta git pull → "3 archivos actualizados desde remoto"
2. Lee los 8 archivos de memoria
3. Ejecuta búsquedas híbridas v2
4. Presenta resumen:
   [RAMA] Branch: feature/edms-ui, Fase: F7, Version: 0.6.1
   [DECISIONES]
   - Real-time monitoring: NDJSON traces + SSE
   - EDMS como fuente de contexto activo
   - ...
   [RIESGOS]
   - LadybugDB como dependencia nueva
   - Real-time monitoring adds complexity
   ...
   [ESTADO] Real-time monitoring Phases 1-2 completadas
   [PROXIMO] Aprobacion de wireframes para EDMS UI
   ...
   [v2 ENTIDADES]
   - ChromaDB: technology (confianza: 0.95)
   - LadybugDB: technology (confianza: 0.90)
   ...
   [v2 HÍBRIDA]
   - Real-time monitoring: 0.92
   - EDMS UI: 0.88
   ...
```
