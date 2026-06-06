# Comandos de PIPELINE

Listado granular de todos los triggers pertenecientes al dominio **PIPELINE**.

---

### `/evol`
**Archivo:** `.agent/workflows/evol.md`

**Descripción:**
Orquestador Principal Evol-DD. Pipeline de desarrollo agéntico de 6 fases con gate HMAC-SHA256, agentes core permanentes y efímeros bajo demanda. Usar cuando el usuario invoque /evol, quiera iniciar un proyecto, ejecutar una fase del pipeline, crear un agente, o necesite coordinar trabajo de desarrollo.

---

### `/evol briefing`
**Archivo:** `.agent/workflows/briefing.md`

**Descripción:**
Briefing como arbol de preguntas bloqueante (16 dimensiones). NO cierra hasta que todas las ramas estan respondidas, el design system aprobado y cada pantalla tiene su HTML aprobado. Produce acuerdos/ con toda la base para documentacion granular automatica. Cero deuda tecnica — cero asunciones — el agente nunca decide por el usuario. Usar al inicio de cualquier proyecto de software nuevo.

---

### `/evol cierre-fase`
**Archivo:** `.agent/workflows/cierre-fase.md`

**Descripción:**
Ejecucion del cierre formal de una fase de desarrollo y actualizacion de la Memoria Viva de Evol-DD.

---

### `/evol fase-requisitos`
**Archivo:** `.agent/workflows/fase-requisitos.md`

**Descripción:**
Operacionalización del Artículo 1 (Filtro de Ambigüedad) mediante elicitación de alta resolución, categorización técnica y validación de interoperabilidad para la generación de PRDs profundos.

---

### `/evol plan-fases`
**Archivo:** `.agent/workflows/plan-fases.md`

**Descripción:**
Transformación del PRD en un plano de ejecución multioficio mediante la descomposición en fases lógicas, definición de contratos técnicos (SAD, OpenAPI) y generación de grafos de tareas (DAG) optimizados para el paralelismo.

---

### `/evol setup-repo`
**Archivo:** `.agent/workflows/setup-repo.md`

**Descripción:**
Configuracion inicial del repositorio — lo PRIMERO antes del briefing. Pregunta una a una: repo existente / crear en nube / solo local, y dev / colaborativo. Configura GitFlow main-develop con el modo correcto. Es el paso 0 del pipeline Evol-DD.

---

### `/evol sprint`
**Archivo:** `.agent/workflows/evol-sprint.md`

**Descripción:**
Orquestador del ciclo completo de un sprint en Evol-DD. Lee la historia asignada, crea equipo dinamico de subagentes segun componentes tecnicos, ejecuta el checklist atomico con auditor anti-alucinacion, evalua pre-push, cierra con GitFlow. Invocar con --sprint=NN o el agente determina el proximo sprint pendiente.

---

