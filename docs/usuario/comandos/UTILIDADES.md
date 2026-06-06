# Comandos de UTILIDADES

Listado granular de todos los triggers pertenecientes al dominio **UTILIDADES**.

---

### `/evol adr-new`
**Archivo:** `.agent/workflows/adr-new.md`

**Descripción:**
Crea un Architecture Decision Record numerado en docs/adr/. Formato Nygard.

---

### `/evol analisis-impacto`
**Archivo:** `.agent/workflows/analisis-impacto.md`

**Descripción:**
Evaluación multidimensional (Código, Infra, Seguridad, UX) de cambios propuestos, garantizando la anticipación de regresiones y la clasificación de riesgo antes de la ejecución técnica.

---

### `/evol analytics-instrument`
**Archivo:** `.agent/workflows/analytics-instrument.md`

**Descripción:**
Instrumenta product analytics. Define schema de eventos, valida en CI, conecta a CDP/proveedor.

---

### `/evol brainstorm`
**Archivo:** `.agent/workflows/brainstorm.md`

**Descripción:**
Genera muchas ideas sin filtrar para exploración inicial (problem space, root cause). Invoca party mode (Sprint 17). Inspirado en BMAD /brainstorm.

---

### `/evol clarify`
**Archivo:** `.agent/workflows/clarify.md`

**Descripción:**
Detecta ambigüedad (4 niveles severidad) en SPEC/DOMAIN/PLAN y bloquea gate si CRÍTICAS pendientes. Inspirado en Spec-Kit /clarify.

---

### `/evol code-as-tool`
**Archivo:** `.agent/workflows/code-as-tool.md`

**Descripción:**
Pattern Code Execution with MCP. Wrap N tool calls homogéneos en 1 script (98%+ reducción tokens). Stdlib first, output JSON, idempotent.

---

### `/evol crear-skill`
**Archivo:** `.agent/workflows/crear-skill.md`

**Descripción:**
Crea nuevas skills para Evol-DD desde cero con loop iterativo de eval. Mejora skills existentes. Optimiza la descripcion del frontmatter para mejor triggering. Genera evals cuantitativos y cualitativos. Porta la skill a los 7 IDEs via evol-adapt.sh. Usar cuando el usuario quiera crear una skill nueva, mejorar una existente, testear una skill, o necesite que una capacidad este disponible como trigger en Claude Code, Cursor, Windsurf, OpenCode, Antigravity, VSCode Copilot o Codex.

---

### `/evol discovery`
**Archivo:** `.agent/workflows/discovery.md`

**Descripción:**
Research PRE-briefing. Por cada atomo de idea, investiga el tema/proyecto/link para ENTENDER la idea antes de preguntar. Distinto del research post-briefing (que investiga como construir). Discovery = entender que es; research = como construir. Produce acuerdos/discovery/ + sintesis. El briefing arranca despues.

---

### `/evol doc-granular`
**Archivo:** `.agent/workflows/doc-granular.md`

**Descripción:**
Genera documentacion atomica maxima post-briefing. Por cada dominio tecnico crea una CARPETA propia con N documentos atomicos en su interior. 1 carpeta = 1 dominio. 1 doc = 1 subdominio. Sin evaluacion, sin limites. El agente decide cuantas carpetas y cuantos docs segun complejidad real del proyecto.

---

### `/evol evolve`
**Archivo:** `.agent/workflows/evolve.md`

**Descripción:**
Cluster instincts acumulados → propone skills/agents/commands nuevos. Humano aprueba (T6.1) antes de promover.

---

### `/evol generar-flujo`
**Archivo:** `.agent/workflows/generar-flujo.md`

**Descripción:**
Genera workflows Evol-DD personalizados con frontmatter, pasos, agentes y criterios de salida.

---

### `/evol idea`
**Archivo:** `.agent/workflows/idea.md`

**Descripción:**
Decanta la idea cruda del usuario en artefactos atomicos. Cita la solicitud original, preserva el prompt + links entregados, y descompone en una nota atomica por tema/proyecto/mejora a investigar. Paso 0.5 del pipeline — despues de setup-repo, antes de discovery. El input del usuario es el puntapie.

---

### `/evol idea-refine`
**Archivo:** `.agent/workflows/idea-refine.md`

**Descripción:**
Pipeline divergente→convergente (3 fases) para transformar ideas en estado bruto en propuestas accionables con dirección clara, supuestos explícitos y trade-offs declarados. Complementa /brainstorm con convergencia. Usa skill evol-idea-refine.

---

### `/evol mejorar-prompt`
**Archivo:** `.agent/workflows/mejorar-prompt.md`

**Descripción:**
Transform raw or existing prompts into optimized, structured versions compliant with Evol-DD standards. Version 2.2.0 integrates "Meta-Interoperability" (Art. 6) to ensure prompts can call other workflows seamlessly.

---

### `/evol orchestrate`
**Archivo:** `.agent/workflows/orchestrate.md`

**Descripción:**
Multi-agent orchestration runtime (/orchestrate). Ejecuta composition_patterns del registry (sequential/parallel/parallel_then_sync).

---

### `/evol prompt-master`
**Archivo:** `.agent/workflows/prompt-master.md`

**Descripción:**
Genera prompts production-ready para herramientas específicas de IA. Extrae intención en 9 dimensiones, aplica routing por tool conventions, y nunca agrega CoT a modelos de razonamiento nativo. Complementa /mejorar-prompt para targets multi-modelo. Usa skill evol-prompt-master.

---

### `/evol refactor-area`
**Archivo:** `.agent/workflows/refactor-area.md`

**Descripción:**
Refactoriza un área de código con gate: análisis de deuda técnica, plan iterativo, tests verdes.

---

### `/evol research`
**Archivo:** `.agent/workflows/research.md`

**Descripción:**
Investigacion autonoma de mejoras. El agente Researcher descubre nuevas skills de Claude Code, metodologias y changelogs relevantes, y propone mejoras rankeadas en RESEARCH.md. Toda propuesta requiere aprobacion humana.

---

### `/evol skill-template-generator`
**Archivo:** `.agent/workflows/skill-template-generator.md`

**Descripción:**
Implement a template-driven documentation system (gstack pattern) to eliminate divergence between skill implementation (code) and documentation (SKILL.md).

---

### `/evol technical-documentation`
**Archivo:** `.agent/workflows/technical-documentation.md`

**Descripción:**
Ensure project documentation is always synchronized with the source code. Produce high-quality artifacts (Manuals, API Guides, Architecture) by prioritizing "Source Code as Truth" and enforcing a strictly textual, icon-free standard.

---

### `/evol ux-discovery`
**Archivo:** `.agent/workflows/ux-discovery.md`

**Descripción:**
Discovery pre-Fase 1. Valida problema, persona y JTBD antes de invertir en spec. Produce DISCOVERY.md.

---

