---
name: briefing
trigger: /evol briefing
description: Briefing como arbol de preguntas bloqueante (16 dimensiones). NO cierra hasta que todas las ramas estan respondidas, el design system aprobado y cada pantalla tiene su HTML aprobado. Produce acuerdos/ con toda la base para documentacion granular automatica. Cero deuda tecnica — cero asunciones — el agente nunca decide por el usuario. Usar al inicio de cualquier proyecto de software nuevo.
phase: briefing
category: planning
---

# /evol briefing — Arbol de preguntas bloqueante

> **Principio:** Cero deuda tecnica = cero asunciones. El briefing NO cierra hasta
> que las 16 dimensiones esten completamente respondidas, el design system aprobado
> y cada pantalla tenga su HTML aprobado por el usuario.
> El agente hace UNA pregunta a la vez. Espera respuesta antes de avanzar.
> Nunca asume. Nunca inventa. Nunca salta dimensiones.

## 0. Pre-flight

Antes de comenzar:

1. Leer `memoria.md` + `lecciones.md` (Art. 3).
2. Crear estructura de trabajo:

```
acuerdos/
  idea/              ← archivo original del usuario + idea.md
  research/          ← investigacion por dominio (post-briefing)
  design/            ← tokens aprobados (colores, tipografias, assets)
  wireframes/        ← <pantalla>.html aprobados
  proyecto/          ← N docs granulares (generados post-briefing)
  memoria/           ← memoria por sprint
  lecciones/         ← lecciones por sprint
```

3. Guardar en `acuerdos/idea/idea.md` la solicitud original del usuario (citar textual).
4. Registrar inicio en `memoria.md`.

---

## 1. DIMENSIONES DEL BRIEFING

El arbol tiene 16 dimensiones. Cada dimension es bloqueante:
no se avanza a la siguiente hasta tener respuesta completa en la actual.

---

### DIMENSION 01 — IDENTIDAD DEL PRODUCTO

Preguntas (una a la vez, en este orden):
1. ¿Cuál es el nombre del producto?
2. ¿Qué problema resuelve? (respuesta en una frase medible, no un adjetivo)
3. ¿Para quién exactamente? (persona, rol, contexto de uso — no "usuarios en general")
4. ¿Cómo resuelve ese problema hoy sin este software? (workaround actual)
5. ¿Qué hace este software que el workaround no puede hacer?
6. ¿Por qué construirlo ahora y no antes?
7. ¿Cuál es el criterio de éxito cuantificable de v1.0? (métrica concreta)
8. ¿Qué incluye v1.0? (lista explícita)
9. ¿Qué queda explícitamente FUERA de v1.0? (lista explícita — sin esto hay scope creep)

Artefacto: `acuerdos/idea/producto.md`

---

### DIMENSION 02 — USUARIOS

1. ¿Cuántos tipos de usuario tiene el sistema?
2. Por cada tipo: nombre del rol, qué puede hacer, qué no puede hacer
3. ¿Hay usuarios anónimos (sin autenticación)?
4. ¿Hay jerarquía de roles? (admin > moderador > usuario > viewer)
5. ¿Multi-tenant? (múltiples organizaciones aisladas) o ¿single-tenant?
6. ¿En qué idioma(s) usarán el producto? ¿Hay idioma prioritario?
7. ¿Hay requerimiento de accesibilidad? (WCAG AA, AAA, o ninguno)

Artefacto: `acuerdos/idea/usuarios.md`

---

### DIMENSION 03 — PLATAFORMAS

1. ¿Dónde vivirá el producto? (web / mobile iOS / mobile Android / desktop / CLI / API / combinación)
2. Por cada plataforma: ¿navegadores mínimos? ¿versiones OS mínimas?
3. ¿Debe ser instalable? (PWA, app store, instalador)
4. ¿Necesita funcionar offline? ¿Con qué capacidad?
5. ¿Dispositivos específicos? (tablet, TV, wearable, quiosco)
6. ¿Tamaño de pantalla mínimo soportado?

Artefacto: `acuerdos/idea/plataformas.md`

---

### DIMENSION 04 — STACK TECNOLOGICO

1. ¿Tiene stack tecnológico ya definido o el agente propone?
   - Si ya definido: listar frontend, backend, base de datos, infraestructura
   - Si el agente propone: genera 2 opciones con justificación → usuario elige
2. Frontend: framework, lenguaje, bundler
3. Backend: lenguaje, framework, runtime
4. Base de datos: tipo (relacional/documental/grafo/vector), motor específico
5. Infraestructura: cloud provider, on-premise, local, serverless
6. Package manager, ¿monorepo o repos separados?
7. ¿Versiones mínimas de dependencias críticas?

Artefacto: `acuerdos/idea/stack.md`

---

### DIMENSION 05 — ARQUITECTURA

1. ¿Monolito / microservicios / modular monolith?
2. ¿Tipo de API? (REST / GraphQL / gRPC / eventos / combinación)
3. ¿Comunicación síncrona / asíncrona / ambas?
4. ¿Event sourcing requerido?
5. ¿Patrones de resiliencia? (circuit breaker, retry, fallback, timeout)
6. ¿Límites de latencia aceptables por operación crítica?
7. ¿Volumen de datos esperado? ¿Proyección de crecimiento a 1 año?
8. ¿Concurrencia máxima esperada?
9. ¿Caché requerido? ¿Dónde?

Artefacto: `acuerdos/idea/arquitectura.md`

---

### DIMENSION 06 — INTEGRACIONES EXTERNAS

1. ¿Qué APIs externas consume el sistema?
2. ¿Qué servicios de terceros? (pagos, email, SMS, storage, mapas, IA)
3. ¿Webhooks? ¿Entrantes, salientes o ambos?
4. ¿Importación o exportación de datos? ¿En qué formatos?
5. ¿Hay migración desde un sistema existente? ¿Qué datos y qué volumen?
6. ¿Límites de rate de APIs externas críticas?

Artefacto: `acuerdos/idea/integraciones.md`

---

### DIMENSION 07 — AUTENTICACION Y AUTORIZACION

1. ¿Cómo se autentica el usuario? (email/password, OAuth, SSO, magic link, biometría, sin auth)
2. ¿Proveedores OAuth? (Google, GitHub, Microsoft, Apple...)
3. ¿MFA requerido? ¿Obligatorio u opcional?
4. ¿Modelo de permisos? (RBAC / ABAC / ACL / combinación)
5. ¿Duración de sesión? ¿Revocación de sesiones activas?
6. ¿API keys para integraciones máquina-a-máquina?
7. ¿Recuperación de cuenta? ¿Cómo?

Artefacto: `acuerdos/idea/auth.md`

---

### DIMENSION 08 — SEGURIDAD

1. ¿El sistema maneja datos sensibles o PII?
2. ¿Regulaciones a cumplir? (GDPR, HIPAA, PCI-DSS, SOC2, CCPA, ninguna)
3. ¿Cifrado en tránsito (TLS) y en reposo requerido?
4. ¿Auditoría de acciones requerida? ¿Qué acciones? ¿Por cuánto tiempo?
5. ¿Política de retención de datos?
6. ¿Penetration testing antes de producción?
7. ¿Gestión de secretos? (vault, variables de entorno, keychain del SO)
8. ¿Política de contraseñas?

Artefacto: `acuerdos/idea/seguridad.md`

---

### DIMENSION 09 — CALIDAD Y TESTING

1. ¿Cobertura mínima de tests requerida? (%)
2. ¿Qué tipos de test son obligatorios? (unit / integration / e2e / performance / security / visual regression)
3. ¿Framework de testing por capa? (o el agente propone según el stack)
4. ¿Tests de regresión visual? ¿Con qué herramienta?
5. ¿Performance benchmarks? ¿Cuáles son los umbrales?
6. ¿Definition of Done para una feature? (lista de condiciones)
7. ¿Code review requerido antes de merge?

Artefacto: `acuerdos/idea/calidad.md`

---

### DIMENSION 10 — DATOS Y PRIVACIDAD

1. ¿Qué datos genera y almacena el sistema? (inventario)
2. ¿Cuáles son PII (datos personales identificables)?
3. ¿Base legal para procesar cada PII? (consentimiento, contrato, interés legítimo)
4. ¿Derecho de supresión requerido? ¿En qué plazo?
5. ¿Qué se registra en logs? ¿Por cuánto tiempo?
6. ¿Backups: frecuencia, retención, punto de recuperación máximo (RPO)?
7. ¿Datos de terceros que el sistema procesa?

Artefacto: `acuerdos/idea/datos-privacidad.md`

---

### DIMENSION 11 — OBSERVABILIDAD

1. ¿Logging estructurado requerido? ¿Nivel mínimo? (debug/info/warn/error)
2. ¿Métricas y alertas? ¿En qué plataforma? (Datadog, Grafana, CloudWatch...)
3. ¿Tracing distribuido? ¿OpenTelemetry?
4. ¿Dashboard de salud del sistema?
5. ¿SLIs y SLOs definidos? ¿Cuáles?
6. ¿Quién recibe alertas críticas? ¿Por qué canal? (email, Slack, PagerDuty)
7. ¿Costos cloud: monitoreo y alertas de presupuesto?

Artefacto: `acuerdos/idea/observabilidad.md`

---

### DIMENSION 12 — CI/CD Y DESPLIEGUE

1. ¿Plataforma CI/CD? (GitHub Actions, GitLab CI, Jenkins, CircleCI...)
2. ¿Ambientes requeridos? (dev / staging / prod — o más)
3. ¿Estrategia de despliegue? (blue-green / canary / rolling / recreate)
4. ¿Feature flags? ¿Con qué herramienta?
5. ¿Auto-rollback ante fallo de despliegue?
6. ¿Proceso de release? (semver, CHANGELOG automático, aprobación manual)
7. ¿Contenedores? ¿Docker, Kubernetes, u otro?

Artefacto: `acuerdos/idea/cicd.md`

---

### DIMENSION 13 — OPERACIONES Y DR

1. ¿SLA de disponibilidad requerido? (99% / 99.9% / 99.99% / best effort)
2. ¿RTO máximo? (Recovery Time Objective — cuánto tiempo sin servicio es aceptable)
3. ¿RPO máximo? (Recovery Point Objective — cuánta pérdida de datos es aceptable)
4. ¿Plan de DR documentado requerido?
5. ¿Runbook de incidentes?
6. ¿Escalado automático requerido? ¿Vertical, horizontal o ambos?
7. ¿Mantenimiento programado? ¿Ventana de mantenimiento?

Artefacto: `acuerdos/idea/operaciones.md`

---

### DIMENSION 14 — COLABORACION Y PROCESO

1. ¿Solo dev o equipo? ¿Cuántas personas?
2. ¿Repositorio nuevo o existente? (URL si existe)
3. ¿GitFlow estricto o trunk-based?
4. ¿PRs requieren aprobación? ¿De quién? ¿Cuántos reviewers?
5. ¿Conventional commits requerido?
6. ¿Documentación vive en el repo o en sistema externo?
7. ¿Licencia del software?
8. ¿Gestión de tareas? (GitHub Issues, Linear, Jira, Notion...)

Artefacto: `acuerdos/idea/proceso.md`

---

### DIMENSION 15 — DESIGN SYSTEM

Esta dimension produce los tokens que se aplican en los wireframes (Dimension 16).
Completar ANTES de los wireframes.

#### 15.1 Paleta de colores
"¿Tienes colores definidos o genero una propuesta?"
- Si tiene: solicitar hex codes para primario, secundario, acento, fondo, texto, error, éxito, advertencia
- Si genera: proponer 3 opciones de paleta completa → usuario elige → itera hasta aprobar

#### 15.2 Tipografias
"¿Tienes fuentes definidas o propongo?"
- Si tiene: nombre de fuentes para heading, body, monospace + escala tipográfica
- Si propone: recomendar par de fuentes (heading + body) según el estilo → itera hasta aprobar

#### 15.3 Estilo visual general
Elegir uno: flat / material / neumorphic / glassmorphism / brutalist / custom
→ Define border-radius, sombras y densidad de la UI

#### 15.4 Spacing y grid
Sistema base: 4px / 8px / 16px base (o custom)
Grid: columnas (12, 16, custom), gutter, margin lateral

#### 15.5 Modo oscuro / claro
Opciones: solo claro / solo oscuro / ambos con toggle / sistema del SO

#### 15.6 Responsive
Mobile-first / desktop-first / ambos con breakpoints definidos

#### 15.7 Componentes base
Acordar estilo visual de: botones, inputs, cards, modales, tablas, navegación, alertas

#### 15.8 Iconos
"¿Usas una biblioteca (Lucide, Phosphor, Heroicons...) o iconos personalizados?"
Si personalizados: acordar estilo (outlined / filled / duo-tone) y origen (usuario aporta / agente genera specs)

#### 15.9 Imagenes e ilustraciones
"¿Necesitas imágenes o ilustraciones personalizadas?"
Si sí: acordar estilo (fotografia / ilustracion vectorial / isometrico / 3D) y origen

#### 15.10 Animaciones
Ninguna / sutiles (200-300ms) / expresivas / micro-interacciones específicas

Artefactos:
- `acuerdos/design/tokens.md` (paleta, tipografias, spacing, breakpoints)
- `acuerdos/design/components.md` (estilo de componentes base)
- `acuerdos/design/assets.md` (inventario de iconos, imagenes, ilustraciones)

---

### DIMENSION 16 — PANTALLAS Y FLUJOS

Solo se ejecuta con el design system (D15) completamente aprobado.

#### 16.1 Mapa de pantallas
"¿Cuáles son todas las pantallas del producto?"
→ Listar con el usuario hasta que la lista este completa y aprobada

#### 16.2 Mapa de navegacion
¿Desde qué pantalla se llega a cada una?
→ Genera diagrama Mermaid del flujo de navegacion
→ Usuario aprueba el mapa

#### 16.3 Por cada pantalla (iterativo, una a la vez)

Para `<nombre-pantalla>`:
1. ¿Qué rol(es) la ven?
2. ¿Cuál es el objetivo principal del usuario en esta pantalla?
3. ¿Qué datos muestra?
4. ¿Qué acciones puede hacer el usuario?
5. ¿Qué estados tiene? (vacio / cargando / error / exito / sin permisos)
6. ¿Tiene formularios? ¿Qué campos y validaciones?
7. "¿Tienes un template HTML base o genero uno?"
   - Si tiene: usuario pega el HTML → revisar y ajustar con tokens del D15
   - Si genera: crear HTML completo con tokens reales (colores, fuentes, spacing)
8. Iterar el HTML hasta que el usuario aprueba
9. Guardar como `acuerdos/wireframes/<nombre-pantalla>.html`

Repetir para cada pantalla de la lista.

---

## 2. GATE DE CIERRE

El briefing cierra SOLO cuando:

```
[ ] D01-D14: todas las preguntas respondidas (14 artefactos en acuerdos/idea/)
[ ] D15: design system aprobado (3 artefactos en acuerdos/design/)
[ ] D16: TODAS las pantallas tienen HTML aprobado en acuerdos/wireframes/
```

Verificacion antes de cerrar:
```bash
# Contar artefactos generados
ls acuerdos/idea/*.md | wc -l       # debe ser 14
ls acuerdos/design/*.md | wc -l     # debe ser 3
ls acuerdos/wireframes/*.html | wc -l  # debe ser N (una por pantalla acordada)
```

Una vez cerrado, registrar en `memoria.md`:
- Fecha de cierre del briefing
- N pantallas acordadas
- Stack tecnologico elegido
- Proxima etapa: generacion automatica de documentacion granular

---

## 3. POST-FLIGHT (documentacion automatica)

Con el briefing cerrado, el agente inicia automaticamente:

1. Analiza los 14 artefactos de `acuerdos/idea/`
2. Identifica TODOS los dominios tecnicos del proyecto
3. Por cada dominio → genera su documento en `acuerdos/proyecto/` (sin evaluar si "merece" uno)
4. Cada documento sigue el flujo worker → auditor (ver `/evol doc-granular`)
5. Al completar: genera `acuerdos/proyecto/INDEX.md` con trazabilidad bidireccional

Ver workflow `/evol doc-granular` para el detalle del paso 3-5.

---

## Agentes delegados

| Agente | Rol |
|--------|-----|
| `product-manager` | Dimensiones 01-02 (producto + usuarios) |
| `engineering-software-architect` | Dimensiones 04-05 (stack + arquitectura) |
| `engineering-security-engineer` | Dimensiones 07-08-10 (auth + seguridad + privacidad) |
| `engineering-devops` | Dimensiones 11-12-13 (observabilidad + CI/CD + DR) |
| `design-system-builder` | Dimension 15 (design system completo) |
| `engineering-technical-writer` | Artefactos finales de cada dimension |
