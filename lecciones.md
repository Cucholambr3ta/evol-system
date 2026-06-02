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

### [PROCESO] Cierre de fase sin gates pre-validacion — 2026-06-02
**Contexto:** Ejecutamos /cierre-fase sin haber inicializado evol-gate ni modificado lecciones.md ni memoria.md en la sesion.
**Problema:** Gate check fallo ("Gate not initialized"), lecciones.md no tuvo nuevas entries, memoria.md no fue actualizada con cierre final.
**Causa raiz:** El cierre se ejecuto automaticamente por workflow sin verificar precondiciones. Falta validacion de pre-flight en el workflow.
**Leccion:** El workflow /cierre-fase debe verificar precondiciones ANTES de ejecutar: gate init si no existe, lecciones actualizadas, memoria actualizada. No ejecutar cierre si checks fallan — abortar con mensaje claro.
**Aplica a:** Todo proyecto con pipeline gated — verificar precondiciones antes de cerrar, no despues.
**Fix aplicado:** Ejecutamos evol-gate.py init manualmente, actualizamos memoria.md con cierre final, lecciones.md con nueva entrada.
**Mejoras sugeridas:** Modificar workflow /cierre-fase para incluir pre-flight checks blockantes (gate init, lecciones diff, memoria diff).
**Estado mejoras:** pendiente
**Contexto:** El piloto multi-IDE genero lecciones sobre orquestador-y-delegacion, pero esas lecciones no se aplicaron al construir Evol-DD.
**Problema:** Misma categoria de error repetida: lecciones aprendidas en un proyecto no se transfieren al siguiente.
**Causa raiz:** El sistema de lecciones no se consulto antes de comenzar el proyecto. El orquestador no leyó lecciones.md antes de iniciar Sprint 0.
**Leccion:** Protocolo obligatorio: al inicio de cada proyecto, ejecutar `lecciones suggest <dominio>` para recuperar prevenciones relevantes antes de comenzar arquitectura.
**Aplica a:** Todo proyecto nuevo.
**Mejoras sugeridas:** Integrar `lecciones suggest` en el hook `session:start:context-load`.
**Estado mejoras:** pendiente
