# MANUAL DE USUARIO — Evol-DD

## Que es Evol-DD

Evol-DD es un framework de desarrollo que integra un equipo de agentes especializados directamente en tu entorno de trabajo. En lugar de usar herramientas separadas para planificar, escribir codigo, revisar calidad y documentar, Evol-DD coordina todos esos roles desde un unico punto de entrada: el comando `/evol` dentro de tu IDE.

El sistema aprende de cada proyecto. Cada decision tomada, cada error cometido y cada solucion encontrada se registra y queda disponible para consulta en los proyectos siguientes. Con el tiempo, el sistema no solo ejecuta tareas — las ejecuta mejor porque recuerda como las hizo antes.

Evol-DD no reemplaza al desarrollador. Lo asiste con un equipo que nunca olvida, nunca llega tarde y nunca pierde el hilo del proyecto. El desarrollador mantiene el control total: cada fase importante del trabajo requiere su aprobacion explicita antes de avanzar.

---

## Los cuatro superpoderes del sistema

### 1. Memoria

El sistema mantiene un registro vivo del proyecto llamado `memoria.md`. Cada sesion de trabajo comienza leyendo ese archivo para retomar exactamente donde se dejo. No es necesario re-explicar el contexto, los acuerdos tomados ni los problemas abiertos. La memoria persiste entre sesiones, entre dias y entre miembros del equipo.

Para proyectos que necesitan continuidad semantica profunda, el sistema puede activar MemPalace: un motor de busqueda sobre el codigo y la documentacion del proyecto que permite encontrar patrones, precedentes y decisiones relevantes con una pregunta en lenguaje natural.

### 2. Lecciones

El sistema registra aprendizajes en `lecciones.md` con una estructura especifica: que se intentaba hacer, que salio mal, cual fue la causa raiz y que regla se derivó de eso. Antes de proponer una solucion a un problema, el sistema busca automaticamente si ya existe una leccion relevante. Esto evita repetir errores costosos.

Las lecciones son acumulativas. A medida que el equipo trabaja mas proyectos con Evol-DD, el sistema se vuelve mas preciso en sus propuestas porque tiene mas contexto de lo que funciona y lo que no en el dominio especifico del equipo.

### 3. Agentes

El sistema tiene 16 agentes core permanentes, cada uno especializado en un area: arquitectura, implementacion, calidad, seguridad, operaciones, documentacion, investigacion, entre otros. Cuando un proyecto lo requiere, el sistema puede crear agentes efimeros adicionales, especializados en una tarea concreta, que se retiran cuando terminan su trabajo pero dejan su conocimiento en el sistema.

El orquestador coordina a los agentes: sabe cuando llamar al arquitecto, cuando al especialista en seguridad, y cuando es suficiente con el agente de implementacion solo.

### 4. Skills

Las skills son capacidades reutilizables que el sistema ha aprendido a ejecutar de forma consistente. Una skill puede ser un workflow para crear un contrato de API, un proceso para auditar dependencias, o un procedimiento para hacer onboarding de un desarrollador nuevo. Las skills se crean, se evaluan con casos de prueba y se mejoran iterativamente. Con el tiempo, el catalogo de skills del equipo se convierte en la memoria procesal del sistema.

---

## Ciclo de trabajo tipico

El siguiente ejemplo usa el desarrollo de un sistema de ecommerce para ilustrar cada fase del pipeline.

### Fase 1 — Briefing: definir el problema

El equipo quiere construir un modulo de carrito de compras para su plataforma de ecommerce. En lugar de empezar a codificar directamente, el desarrollador abre Claude Code y escribe:

```
/evol briefing
```

El sistema detecta si el pedido tiene parametros medibles. Si el briefing es vago ("quiero un carrito"), pregunta: cuantos productos puede tener, como se maneja el stock, necesita persistencia de sesion, que pasa cuando un producto se agota. Una vez respondidas esas preguntas, genera `BRIEFING.md` con el objetivo estructurado, los stakeholders identificados y los criterios de exito verificables.

### Fase 2 — Spec: especificar el que

```
/evol spec
```

El agente de arquitectura y el agente de dominio leen el briefing y generan la especificacion tecnica. Esto incluye los requisitos funcionales (el carrito permite agregar, quitar y actualizar cantidades), los no funcionales (respuesta menor a 200ms, consistencia eventual aceptable), y las restricciones (no se puede agregar un producto sin stock mayor a cero).

El resultado es `SPEC.md` mas los documentos de requisitos en `docs/requisitos/`. Nada avanza hasta que el desarrollador revisa y aprueba:

```bash
evol-gate approve --phase spec
```

### Fase 3 — Plan: descomponer el como

```
/evol plan
```

El agente de proyecto descompone la spec en features concretas con criterios Gherkin. Por ejemplo: "Dado que el usuario tiene un producto en el carrito, cuando actualiza la cantidad a cero, entonces el producto se elimina del carrito". Estos casos son la definicion de done verificable.

El resultado es `PLAN.md` con las features priorizadas y `docs/qa/CASOS_GHERKIN.md` con los escenarios de prueba.

### Fase 4 — Build: implementar

```
/evol build
```

El agente de implementacion escribe el codigo guiado por los casos Gherkin. Usa TDD: primero los tests, luego la implementacion que los hace pasar. El agente de arquitectura supervisa que las decisiones de diseño sean coherentes con el dominio.

Al terminar, los tests deben estar en verde:

```bash
pytest tests/
```

### Fase 5 — QA: verificar calidad

```
/evol qa
```

El agente de calidad revisa los casos implementados contra los casos planificados, mide la cobertura, identifica gaps y genera el reporte en `docs/qa/REPORTE_QA.md`. El gate de QA firma el cierre cuando la calidad es aceptable.

### Fase 6 — Retro: aprender

```
/evol retro
```

El sistema actualiza `memoria.md` con las decisiones tomadas, los artefactos producidos y los proximos pasos. Si hubo algun aprendizaje significativo — por ejemplo, que la estrategia de persistencia de sesion elegida tiene problemas con usuarios anonimos — el desarrollador lo registra en `lecciones.md`. La proxima vez que el sistema trabaje con sesiones de usuario, encontrara esa leccion.

---

## Como hablar con el sistema

Los comandos del sistema son slash commands del IDE. Se escriben directamente en el chat de Claude Code.

```
/evol                    — retoma el estado del proyecto y presenta opciones
/evol briefing           — inicia el ciclo con un nuevo briefing
/evol spec               — genera especificacion desde el briefing activo
/evol plan               — genera plan desde la spec activa
/evol build              — implementa desde el plan activo
/evol qa                 — genera reporte de calidad
/evol retro              — cierra la fase y actualiza memoria
/evol research           — pide al sistema que investigue un tema
/evol gate status        — muestra el estado de aprobaciones de las fases
```

Para tareas especificas que no son parte del pipeline principal:

```
/evol doc                — genera o actualiza la documentacion del proyecto
/evol gate approve       — firma la aprobacion de la fase actual
```

El sistema puede recibir instrucciones en lenguaje natural. Si escribes "quiero agregar autenticacion OAuth al modulo de usuarios", el sistema lo interpreta, busca lecciones relevantes sobre autenticacion, y propone el enfoque antes de ejecutar.

---

## Como leer la memoria al inicio de sesion

Al abrir el proyecto en Claude Code, el primer comando siempre es:

```
/evol
```

Esto activa el orquestador que lee `memoria.md` automaticamente. El archivo tiene una estructura fija:

- **Identidad del proyecto**: nombre, dominio, stack, fecha de inicio.
- **Estado actual**: fase activa, ultimo hito, proximo paso.
- **Decisiones arquitectonicas clave**: lista de decisiones con fecha y razonamiento.
- **Riesgos activos**: lo que podria salir mal y requiere atencion.
- **Bitacora de sesiones**: registro cronologico de cada sesion de trabajo.

Si se quiere leer directamente sin pasar por el orquestador:

```bash
cat memoria.md
```

La regla es simple: si `memoria.md` no ha sido leido, el sistema no tiene contexto del proyecto y sus propuestas pueden ser contradictorias con decisiones ya tomadas.

---

## Como revisar lecciones antes de tomar una decision

Antes de elegir una tecnologia, un patron de diseño o un enfoque de implementacion, consultar primero si el sistema ya tiene una leccion sobre ese tema:

```bash
evol-lessons search "autenticacion JWT"
evol-lessons search "migracion de base de datos"
evol-lessons search "rate limiting"
```

El motor de busqueda usa similitud de Jaccard sobre los textos de las lecciones. Retorna las lecciones relevantes con su categoria, contexto, problema original y la regla derivada.

Si hay una leccion que aplica, el sistema la presenta antes de proponer una solucion. El desarrollador decide si seguir la leccion o desviarse conscientemente — en cuyo caso conviene registrar una nueva leccion con el razonamiento de la desviacion.

Para ver todas las lecciones de una categoria:

```bash
evol-lessons list --categoria ARQUITECTURA
evol-lessons list --categoria SEGURIDAD
```

Para ver las mejoras pendientes de aplicar:

```bash
evol-lessons list --pendientes
```

---

## Como crear un agente especializado para una tarea

Cuando el equipo necesita capacidades que ningun agente core cubre completamente, se puede crear un agente efimero. Los agentes efimeros son especialistas temporales para una tarea concreta.

Ejemplo: el equipo necesita migrar una base de datos de PostgreSQL 13 a 15. Ningun agente core esta especializado en esta tarea especifica. Se crea un agente efimero:

```bash
evol-agent create \
  --name "postgres-migration" \
  --task "Disenar e implementar migracion de PostgreSQL 13 a 15 con zero-downtime usando logical replication"
```

El sistema genera el agente con el contexto de la tarea. Para usarlo desde Claude Code:

```
/evol [invocar postgres-migration]
```

O desde la linea de comandos:

```bash
evol-agent invoke postgres-migration \
  "Revisar el plan de migracion en docs/migracion-pg15.md"
```

Cuando la tarea termina, el agente se retira pero su conocimiento queda disponible para recall futuro:

```bash
evol-agent retire postgres-migration
# Meses despues, si se necesita de nuevo:
evol-agent recall postgres-migration
```

Los agentes efimeros tienen restricciones: no pueden modificar archivos de gobernanza del sistema y deben registrar sus decisiones en `memoria.md` al finalizar.

---

## Glosario de terminos clave

| Termino | Significado en Evol-DD |
|---------|----------------------|
| **Pipeline** | La secuencia de seis fases de desarrollo: Briefing, Spec, Plan, Build, QA, Retro. Cada fase produce artefactos verificables y requiere aprobacion para avanzar. |
| **Gate** | Punto de control entre fases. Requiere firma HMAC-SHA256 del aprobador. Garantiza que no se avanza sin revision humana explicita. |
| **Memoria** | Archivo `memoria.md` que actua como flight recorder del proyecto. Se lee al inicio de cada sesion y se actualiza al cierre. |
| **Leccion** | Aprendizaje registrado en `lecciones.md` con estructura: contexto, problema, causa raiz y regla derivada. Consultado antes de proponer soluciones. |
| **Agente core** | Uno de los 16 especialistas permanentes del sistema. Nunca se retiran. Cubren: arquitectura, implementacion, calidad, seguridad, operaciones, documentacion, dominio, UX, datos, revision, orquestacion, PM, release, analisis, factory y research. |
| **Agente efimero** | Especialista temporal creado para una tarea concreta. Se retira al terminar pero su conocimiento persiste para recall. |
| **Skill** | Capacidad reutilizable del sistema definida como workflow con casos de prueba propios. Se crean, evaluan y mejoran iterativamente. |
| **Modo COMPLETO** | Estado del sistema cuando MemPalace esta instalado y activo. Habilita indexacion semantica, recall automatico y extraccion de patrones. |
| **Modo BASE** | Estado del sistema sin MemPalace. El pipeline completo funciona. La continuidad semantica se maneja manualmente via `memoria.md`. |
| **Perfil** | Conjunto predefinido de modulos que determina las capacidades instaladas en el proyecto. Los perfiles van de `minimal` a `full`, con opciones especializadas como `security` y `research`. |
