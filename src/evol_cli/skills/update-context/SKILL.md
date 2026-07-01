---
name: update-context
description: >
  Sincroniza contexto entre IDEs/maquinas usando archivos de memoria actualizados.
  Usar al cambiar de IDE o maquina para que el agente conozca lo que otro entorno hizo.
  Requiere git pull previo para traer cambios remotos.
category: context
trigger: /update-context
triggers:
  - /update-context
  - "sincronizar contexto"
  - "actualizar contexto"
  - "sync context"
---

# /update-context — Sincronizacion Cross-Environment

> Cuando trabajas en 2+ IDEs/maquinas sobre el mismo proyecto, `/update-context`
> lee todos los archivos de memoria que `/update-memory` actualiza y te inyecta
> el contexto completo usando busqueda hibrida v2 (vector + BM25 + graph).

---

## Protocolo

Al recibir `/update-context`, ejecutar en orden:

### 1. Sync git (obligatorio)

```bash
git pull --ff-only 2>/dev/null || echo "[sync] No hay repo remoto o hay conflictos de merge"
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

Usar busqueda hibrida v2 para contexto relevante:

```bash
# Buscar decisiones recientes
python3 scripts/evol-memory.py edms-hybrid-search "decisiones arquitectonicas" --top-k 5

# Buscar lecciones relevantes
python3 scripts/evol-memory.py edms-hybrid-search "lecciones aprendidas" --top-k 3

# Buscar riesgos activos
python3 scripts/evol-memory.py edms-hybrid-search "riesgos activos" --top-k 3

# Verificar entidades del proyecto
python3 scripts/evol-memory.py edms-entity "proyecto" --type technology
```

Si los comandos v2 no estan disponibles o retornan vacio, continuar con los archivos planos (no es bloqueante).

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
[PROXIMO] <siguiente paso]

[PREFERENCIAS]
- <preferencia 1>
- <preferencia 2>
- <preferencia 3>

[v2 ENTIDADES]
- <entidad 1>: <tipo> (confianza: <confianza>)

[v2 HIBRIDA]
- <resultado 1>: <score>

============================
```

### 5. EDMS Index (opcional)

Almacenar el contexto sincronizado para futuras busquedas:

```bash
python3 scripts/evol-memory.py edms-store "$(cat WORKING-CONTEXT.md)" --tipo contexto
python3 scripts/evol-memory.py edms-extract "$(cat acuerdos/memoria/decisiones.md)"
python3 scripts/evol-memory.py edms-link "$(cat acuerdos/memoria/decisiones.md)"
```

### 6. Confirmar

Al finalizar, informar:
- Cuantos archivos se leyeron
- Si `git pull` trajo cambios nuevos
- Si el contexto esta actualizado o hay drift
- **v2**: Cuantas entidades se extrajeron
- **v2**: Cuantos resultados hibridos se encontraron

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
1. Ejecuta git pull -> "3 archivos actualizados desde remoto"
2. Lee los 8 archivos de memoria
3. Ejecuta busquedas hibridas v2
4. Presenta resumen:
   [RAMA] Branch: feature/edms-ui, Fase: F7, Version: 0.6.3
   [DECISIONES]
   - TUI scaffold completado: 29 archivos
   - Wireframes EDMS aprobados: 9 pantallas
   - ...
   [RIESGOS]
   - VERSION drift: pyproject.toml=0.6.3 vs VERSION=0.6.0
   - ...
   [ESTADO] TUI scaffold completada y smoke-testeada
   [PROXIMO] Validar TUI con usuario
   ...
```
