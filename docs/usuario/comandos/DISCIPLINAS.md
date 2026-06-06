# Comandos de DISCIPLINAS

Listado granular de todos los triggers pertenecientes al dominio **DISCIPLINAS**.

---

### `/evol api-contract`
**Archivo:** `.agent/workflows/api-contract.md`

**Descripción:**
Define el contrato API (OpenAPI/AsyncAPI/GraphQL SDL) en Fase 2. Genera openapi.yaml + stubs Pact.

---

### `/evol api-versioning`
**Archivo:** `.agent/workflows/api-versioning.md`

**Descripción:**
API Versioning-Driven Development (APIVDD). Define la estrategia de versionado y las politicas de deprecacion ANTES de implementar cambios en la API. Detecta breaking changes, genera deprecation_schedule y guias de migracion. Usar en APIs publicas con multiples versiones conviviendo o consumidores externos. Disciplina docs/disciplinas/APIVDD.md.

---

### `/evol data-pipeline`
**Archivo:** `.agent/workflows/data-pipeline.md`

**Descripción:**
Diseña pipeline de datos con contratos, SLAs, DLQ y data quality checks.

---

### `/evol debt-budget`
**Archivo:** `.agent/workflows/debt-budget.md`

**Descripción:**
Technical Debt Budgeting (DebtBudgetDD). Asigna un presupuesto explicito de deuda tecnica y mide la deuda generada y pagada por iteracion en un ledger. Produce debt/budget.json + debt/ledger.json + debt/forecast.md. Alerta y prioriza pago cuando se excede el limite. Usar en proyectos a largo plazo o legacy con deuda acumulada. Disciplina docs/disciplinas/DebtBudgetDD.md.

---

### `/evol design-system-builder`
**Archivo:** `.agent/workflows/design-system-builder.md`

**Descripción:**
Construye o audita un design system: tokens, componentes atómicos, Storybook y accesibilidad.

---

### `/evol event-sourcing`
**Archivo:** `.agent/workflows/event-sourcing.md`

**Descripción:**
Event Sourcing-Driven Development (ESDD). Disena el event store y la logica de aplicacion de eventos por aggregate, donde el estado se deriva de eventos inmutables. Produce eventsourcing/event_store_schema.json + aggregates con tests de replay. Usar cuando el dominio requiere auditoria completa o reconstruccion de estado historico. Disciplina docs/disciplinas/ESDD.md.

---

### `/evol feature-flag`
**Archivo:** `.agent/workflows/feature-flag.md`

**Descripción:**
Crea, gobierna y retira feature flags. Mantiene FLAGS.md como inventario único.

---

### `/evol finops-baseline`
**Archivo:** `.agent/workflows/finops-baseline.md`

**Descripción:**
Establece presupuesto cloud, alertas, tagging y checklist mensual de rightsizing. Produce BUDGET.md.

---

### `/evol i18n-setup`
**Archivo:** `.agent/workflows/i18n-setup.md`

**Descripción:**
Configura internacionalización del proyecto. Extracción, locales, RTL, formato de fechas/números.

---

### `/evol iac-driven`
**Archivo:** `.agent/workflows/iac-driven.md`

**Descripción:**
Infrastructure-as-Code-Driven Development (IODD). Especifica los recursos de infraestructura como codigo declarativo desde la fase de spec. Produce infra/main.tf (modulos) + dependencies_graph.json, recreable desde cero y sin recursos manuales en consola. Usar en proyectos cloud o con infraestructura automatizada. Disciplina docs/disciplinas/IODD.md.

---

### `/evol observability-init`
**Archivo:** `.agent/workflows/observability-init.md`

**Descripción:**
Bootstrap de observabilidad. Define SLI/SLO, logs estructurados, métricas, tracing y dashboards.

---

### `/evol project-architecture-gsd`
**Archivo:** `.agent/workflows/project-architecture-gsd.md`

**Descripción:**
Genera arquitectura física del proyecto tras gate spec. Scaffolding, ADRs y estructura técnica.

---

### `/evol use-case-driven`
**Archivo:** `.agent/workflows/use-case-driven.md`

**Descripción:**
Use-Case-Driven Development (UDD). Modela los casos de uso como unidad de diseno y planificacion por encima de las features (actor, objetivo, flujo principal y alternativos). Produce usecases/usecase.json + diagram.puml + test_scenarios.feature por caso de uso. Usar en aplicaciones transaccionales o modernizacion de legacy. Disciplina docs/disciplinas/UDD.md.

---

### `/evol ux-driven`
**Archivo:** `.agent/workflows/ux-driven.md`

**Descripción:**
UX-Driven Development (UXDD). Especifica flujos de usuario, mensajes de UI y microinteracciones ANTES del codigo frontend. Produce ux/user_journeys, ux/ui_messages y ux/microinteractions desde el catalogo de features y los wireframes del briefing. Usar cuando el proyecto tiene UI compleja y la experiencia es diferenciadora. Disciplina docs/disciplinas/UXDD.md.

---

