# lecciones.md — Aprendizajes Acumulados

> Lecciones aprendidas del proyecto. Indexado por MemPalace. Consultado por agentes antes de proponer soluciones para evitar repetir errores (Constitución Art. 9).
> Actualizado vía `/cierre-fase` al final de cada fase.

## Formato
Cada lección sigue la estructura:
```
### [CATEGORÍA] Título breve — YYYY-MM-DD
**Contexto:** Qué estábamos intentando hacer.
**Problema:** Qué falló o sorprendió.
**Causa raíz:** Por qué pasó.
**Lección:** Regla aplicable a futuras decisiones.
**Aplica a:** Ámbito (módulo X, todo el proyecto, stack Y…).
```

Categorías sugeridas: `ARQUITECTURA`, `SEGURIDAD`, `DOMINIO`, `TESTING`, `DEVOPS`, `PROCESO`, `HERRAMIENTAS`.

---

## Lecciones

### [PROCESO] GitFlow violado — todo en un commit — 2026-06-02
**Contexto:** Construccion de Evol-DD en una sesion continua. 11 sprints ejecutados sin crear branches intermedias.
**Problema:** Todo el codigo commiteado a `develop` en un solo commit de 87 archivos. No hubo PRs por sprint, no hubo review entre fases, no hubo rollback granular.
**Causa raiz:** El orquestador ejecuto sprints secuencialmente sin aplicar GitFlow. La leccion aprendida del piloto multi-IDE no fue aplicada: "orquestador no delega" se corrigio, pero "orquestador no crea branches" se ignoro.
**Leccion:** GitFlow no es opcional aunque el proyecto sea rapido. Cada sprint debe producir una branch `feature/sN-nombre`, PR a `develop`, y merge. Esto permite:
- Review granular por feature
- Rollback de un sprint especifico sin afectar otros
- Historial traceable de decisiones
- CI/CD paralelo en lugar de secuencial
**Aplica a:** Todo proyecto Evol-DD — incluyendo piloto multi-IDE, proyectos rapidos, prototipos. GitFlow es obligatorio por Constitucion Art. 7.
**Fix aplicado:** Branches creadas post-hoc: feature/s0-identity, feature/s1-scripts, ..., feature/s11-ci. Todas pushadas a origin.
**Mejoras sugeridas:** El orquestador `/evol` debe verificar branch activa antes de comenzar sprint. Si no existe `feature/sN-*` desde develop, crear antes de cualquier modificacion de codigo.
**Estado mejoras:** pendiente

---

### [PROCESO] Orquestador no genera specs directamente — 2026-06-02
**Contexto:** Leccion aprendida del piloto multi-IDE. El orquestador genero SPEC.md sin delegar al Architect.
**Problema:** El orquestador escribio codigo y specs directamente, violando su rol de coordinador.
**Causa raiz:** Cuando el equipo es pequeno (1 persona), hay tentacion de "hacer directamente" en lugar de delegar.
**Leccion:** El orquestador siempre delega. Si no hay subagente disponible para una tarea, crear un agente efimero primero. Nunca escribir codigo directamente — solo coordinar.
**Aplica a:** Todo proyecto con orquestador Evol-DD.
**Fix aplicado:** Protocolo de delegacion reforzado.
**Estado mejoras:** aplicado

---

### [PROCESO] Prevenciones del piloto multi-IDE no aplicada a Evol-DD — 2026-06-02
**Contexto:** El piloto multi-IDE genero lecciones sobre orquestador-y-delegacion, pero esas lecciones no se aplicaron al construir Evol-DD.
**Problema:** Misma categoria de error repetida: lecciones aprendidas en un proyecto no se transfieren al siguiente.
**Causa raiz:** El sistema de lecciones no se consulto antes de comenzar el proyecto. El orquestador no leyó lecciones.md antes de iniciar Sprint 0.
**Leccion:** Protocolo obligatorio: al inicio de cada proyecto, ejecutar `lecciones suggest <dominio>` para recuperar prevenciones relevantes antes de comenzar arquitectura.
**Aplica a:** Todo proyecto nuevo.
**Mejoras sugeridas:** Integrar `lecciones suggest` en el hook `session:start:context-load`.
**Estado mejoras:** pendiente
