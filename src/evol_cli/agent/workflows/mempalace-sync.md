---
name: mempalace-sync
trigger: /evol mem
description: Sincroniza el proyecto activo con MemPalace. Ejecutar al inicio de sesion para cargar contexto semantico, o al cierre para persistir cambios. Activa Modo COMPLETO — el agente recuerda el proyecto, lecciones y patrones previos sin que el usuario repita contexto. Usar cuando el usuario diga "sincroniza memoria", "indexa MemPalace", "/evol mem", o quiera activar continuidad semantica entre sesiones.
---

# /evol mem — Sincronizacion MemPalace

Sincroniza el proyecto activo con MemPalace para activar Modo COMPLETO.

## Cuándo usar

- Al **iniciar sesion**: cargar contexto de sesiones anteriores
- Al **cerrar sesion**: persistir cambios del sprint
- Cuando el agente no recuerda decisiones previas del proyecto

## Comandos

```bash
# Indexar proyecto actual (MemPalace 3.x)
mempalace mine . --wing evol-dd --mode projects

# Buscar contexto relevante
mempalace search "QUERY" --wing evol-dd

# Ver estado del palace
mempalace status

# Buscar decisiones arquitectonicas previas
mempalace search "arquitectura decision" --wing evol-dd
```

## Flujo de sincronizacion

1. Correr `mempalace mine . --wing evol-dd` en el directorio del proyecto
2. Verificar con `mempalace status` que el wing tiene drawers
3. Buscar contexto relevante con `mempalace search "TEMA"`
4. Registrar en `memoria.md` que la sincronizacion fue exitosa

## Nota sobre LLM local

MemPalace 3.x usa Ollama para indexado semantico completo. Sin Ollama activo,
`mine` corre en modo heuristico — igualmente util. Para semantica completa:
```bash
ollama pull gemma4
```

## Cierre de sesion

Al finalizar trabajo significativo:
```bash
mempalace mine . --wing evol-dd --mode projects
```
Esto persiste el estado del codigo y docs para que la proxima sesion
arranque con contexto completo sin repetir briefing.
