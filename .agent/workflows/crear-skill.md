---
description: Crea nuevas skills para Evol-DD desde cero con loop iterativo de eval. Mejora skills existentes. Optimiza la descripcion del frontmatter para mejor triggering. Genera evals cuantitativos y cualitativos. Porta la skill a los 7 IDEs via evol-adapt.sh. Usar cuando el usuario quiera crear una skill nueva, mejorar una existente, testear una skill, o necesite que una capacidad este disponible como trigger en Claude Code, Cursor, Windsurf, OpenCode, Antigravity, VSCode Copilot o Codex.
---

# /crear-skill

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, Mermaid obligatorio,
> tablas, Gherkin donde aplique, secciones minimas, trazabilidad bidireccional.

**ID:** FLUJO-SKILL | **Version:** 1.0.0 | **Agente:** evol-architect + evol-qa
**Mision:** Loop completo de creacion iterativa de skills con eval cuantitativo/cualitativo
y portabilidad a 7 IDEs. Patron inspirado en anthropics/skills/skill-creator (Apache-2.0).

---

## 0. PRE-FLIGHT

- Leer `memoria.md` y `lecciones.md` antes de empezar (Art. 3 + Art. 9).
- Si el usuario ya tiene una skill parcial, saltar directamente al paso de eval.
- Si el usuario dice "vibe conmigo" o "sin evals", omitir las fases de benchmark.

---

## 1. CAPTURAR INTENCION

Antes de escribir nada, entender al usuario. Si la conversacion actual ya contiene un
flujo de trabajo que el usuario quiere capturar, extraer del historial: herramientas
usadas, secuencia de pasos, correcciones hechas, formatos de entrada/salida observados.

Preguntas obligatorias:

1. Que debe hacer esta skill? (descripcion en 1-2 lineas)
2. Cuando debe dispararse? (frases del usuario que la activan)
3. Cual es el formato de salida esperado?
4. Necesita archivos de referencia, scripts, o recursos externos?
5. La salida es verificable objetivamente (codigo, datos, transformaciones) o subjetiva (estilo, diseño)?

Si la salida es objetivamente verificable → crear evals con assertions.
Si es subjetiva → eval cualitativo sin assertions numericas.

Investigar antes de escribir: revisar skills existentes en `skills/` para no duplicar,
buscar patrones similares en `lecciones.md`.

---

## 2. ESTRUCTURA DE UNA SKILL Evol-DD

Toda skill vive en `skills/<nombre>/` con esta estructura:

```
skills/<nombre>/
├── SKILL.md              (requerido — frontmatter + instrucciones)
├── references/           (opcional — docs cargados como contexto)
│   └── *.md
├── scripts/              (opcional — scripts ejecutables reutilizables)
│   └── *.py / *.sh
└── evals/                (requerido si skill tiene outputs verificables)
    ├── evals.json        (prompts de prueba + assertions)
    └── cases.jsonl       (formato evol-eval.py)
```

### Formato del SKILL.md

```yaml
---
name: nombre-kebab-case
description: >
  Descripcion que determina el triggering. Incluir: QUE hace + CUANDO usar.
  Ser especifico sobre contextos de activacion. Listar frases tipicas del usuario.
  Evitar "undertriggering" — si el usuario menciona X o Y, usar esta skill.
origin: evol-dd
category: context-engineering | quality-gate | security | compression | research | lifecycle
when_to_use:
  - caso de uso 1
  - caso de uso 2
triggers:
  - /trigger-principal
  - "frase de activacion"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
---

# Nombre de la Skill

## Proposito
[Por que existe esta skill. El problema que resuelve.]

## Uso
[Como invocarla. Que input espera. Que output produce.]

## Referencias
[Links a archivos en references/ si aplica]
```

### Principios de escritura

- Explicar el POR QUE, no solo el QUE. Los modelos son inteligentes — entender el razonamiento
  produce mejor comportamiento que instrucciones rigidas.
- Evitar SIEMPRE/NUNCA en mayusculas. Si te encuentras escribiendolo, reformular con razonamiento.
- Mantener SKILL.md bajo 500 lineas. Si se excede, mover contenido a `references/`.
- Hacer la descripcion del frontmatter "un poco agresiva" — el undertriggering es el error
  mas comun. Si el usuario menciona el tema aunque sea de pasada, la skill debe activarse.

---

## 3. ESCRIBIR LA SKILL (DRAFT)

1. Escribir `skills/<nombre>/SKILL.md` basado en la entrevista.
2. Si hay scripts reutilizables que todos los runs van a necesitar, escribirlos en
   `scripts/` ahora — mejor que cada invocacion los regenere.
3. Presentar el draft al usuario: "Aqui esta el borrador. Revisalo y dime si hay algo
   que cambiar antes de correr los tests."

---

## 4. CASOS DE PRUEBA

Crear 2-3 prompts realistas — lo que un usuario real escribiria. Guardar en
`skills/<nombre>/evals/evals.json`:

```json
{
  "skill_name": "<nombre>",
  "evals": [
    {
      "id": 1,
      "prompt": "Prompt realista del usuario con contexto especifico",
      "expected_output": "Descripcion del resultado esperado",
      "assertions": []
    }
  ]
}
```

Mostrar al usuario: "Aqui estan los casos de prueba que voy a correr. ¿Los apruebas
o quieres añadir alguno?"

Tambien generar `skills/<nombre>/evals/cases.jsonl` para `evol-eval.py`:

```jsonl
{"id": "eval-1", "prompt": "...", "expected": "..."}
```

---

## 5. LOOP DE EVAL ITERATIVO

Este es el ciclo central. No interrumpir a la mitad.

### 5.1 Lanzar runs en paralelo (WITH-skill vs baseline)

Para cada caso de prueba, lanzar DOS subagentes en el mismo turno:

**Run WITH-skill:**
```
Ejecuta esta tarea usando la skill:
- Skill: skills/<nombre>/SKILL.md
- Tarea: <prompt del eval>
- Guardar outputs en: skills/<nombre>/evals/workspace/iter-<N>/eval-<id>/with_skill/
```

**Run BASELINE** (sin skill o con version anterior):
```
Ejecuta esta tarea SIN skill:
- Tarea: <mismo prompt>
- Guardar outputs en: skills/<nombre>/evals/workspace/iter-<N>/eval-<id>/baseline/
```

Guardar metadata por eval:
```json
{
  "eval_id": 1,
  "eval_name": "nombre-descriptivo",
  "prompt": "...",
  "assertions": []
}
```

### 5.2 Mientras corren los runs: escribir assertions

No esperar — usar el tiempo productivamente. Redactar assertions verificables
objetivamente y explicarselas al usuario:

```json
{
  "assertion_id": "assert-1",
  "description": "El output contiene un diagrama Mermaid",
  "check": "grep '```mermaid' output.md",
  "type": "contains"
}
```

Las assertions deben tener nombres descriptivos — alguien que vea los resultados
debe entender inmediatamente que verifica cada una.
Skills subjetivas (estilo de escritura, diseño visual) → eval cualitativo sin assertions.

### 5.3 Cuando terminen los runs: evaluar + mostrar resultados

1. Evaluar cada assertion contra los outputs (o usar `evol-eval.py` si disponible).
2. Generar tabla comparativa:

| Eval | Con skill | Sin skill | Delta |
|------|-----------|-----------|-------|
| eval-1 | pass 3/3 | pass 1/3 | +2 assertions |
| eval-2 | ... | ... | ... |

3. Mostrar outputs concretos al usuario para revision cualitativa.
4. Preguntar: "¿Que te parece? ¿Hay algo que cambiar?"

### 5.4 Iterar segun feedback

Al recibir feedback del usuario:

1. Generalizar desde el feedback — no hacer cambios hiper-especificos para los ejemplos.
   Pensar: "¿Por que el usuario quiere esto? ¿Que principio general mejora?"
2. Mantener la skill lean — quitar lo que no aporta.
3. Reescribir `SKILL.md` con los cambios.
4. Relanzar todos los runs en un nuevo `iter-<N+1>/`.
5. Comparar con la iteracion anterior.

Continuar hasta que:
- El usuario diga que esta satisfecho
- Todos los evals pasan
- No hay mejora significativa entre iteraciones

---

## 6. OPTIMIZAR LA DESCRIPCION (TRIGGERING)

El campo `description:` en el frontmatter es el mecanismo primario de activacion.
Una descripcion mal escrita hace que la skill no se active cuando deberia.

### 6.1 Generar 20 eval queries de triggering

Mix de should-trigger y should-not-trigger. Guardar en
`skills/<nombre>/evals/trigger_evals.json`:

```json
[
  {"query": "prompt realista con contexto especifico", "should_trigger": true},
  {"query": "prompt que parece similar pero no deberia activarla", "should_trigger": false}
]
```

**Para should-trigger (10):** diferentes fraseos del mismo intent — formal, casual,
abreviado, con typos, sin nombrar la skill explicitamente pero claramente necesitandola.

**Para should-not-trigger (10):** near-misses criticos — queries que comparten keywords
pero necesitan algo diferente. Evitar negativos obvios (son inutil para el test).

Presentar al usuario para revision antes de correr.

### 6.2 Probar description actual

Para cada query, verificar si la skill se activa. Calcular:
- Recall: % should-trigger que activa correctamente
- Precision: % de activaciones que son correctas

### 6.3 Iterar description hasta recall >= 0.85 y precision >= 0.85

Reescribir el campo `description:` siendo mas especifico sobre contextos de activacion.
Recordar: listar frases explicitas del usuario que deben activarla.

---

## 7. PORTAR A 7 IDEs

Una vez la skill esta lista, portarla a todos los IDEs con `evol-adapt.sh`:

```bash
# Verificar primero (sin escribir)
bash scripts/evol-adapt.sh all --dest=. --dry-run

# Aplicar a todos los IDEs
bash scripts/evol-adapt.sh all --dest=.
```

La skill en `skills/<nombre>/` es automaticamente:
- Copiada a `~/.codex/skills/<nombre>/` para **Codex**
- Copiada a `.agents/skills/<nombre>/` para **Antigravity**
- Disponible via slash commands en **Claude Code**, **OpenCode**, **Windsurf**, **VSCode Copilot**
- Disponible via @-mention en **Cursor**

Verificar que no hay MCP generado:
```bash
grep -r "mcpServers" .claude/ .opencode/ .cursor/ 2>/dev/null | wc -l
# Debe ser 0
```

---

## 8. REGISTRO Y CIERRE

1. Actualizar `prompts/workflows/03_workflows_catalog.md` con la nueva skill.
2. Si la skill fue auto-generada desde instincts: registrar en `evol-state.py`:
   ```bash
   python3 scripts/evol-state.py --db ~/.evol-dd/state.db record-instinct \
     --category HERRAMIENTAS \
     --pattern "skill <nombre> creada via /crear-skill" \
     --context "caso de uso: <descripcion>"
   ```
3. Actualizar `memoria.md` con el hito.
4. Si la skill es suficientemente util para el sistema: abrir PR via GitFlow
   (`feature/skill-<nombre>`).

---

## CONEXIONES DE INTEROPERABILIDAD (Art. 6)

- **Predecesores:** `/orchestrate` (orquestador), `/fase-requisitos` (si la skill resuelve un requisito)
- **Sucesores:** `/evolve` (si la skill se genera desde instincts), `/technical-documentation` (documentar la skill)
- **Scripts vinculados:** `evol-eval.py` (eval harness), `evol-adapt.sh` (portabilidad IDE), `evol-state.py` (registro)
- **Skills relacionadas:** `agent-eval` (eval de agentes), `evol-skill-manager` (gestion de skills)

---

## RECUPERACION DE ERRORES

| Error | Causa probable | Solucion |
|-------|---------------|----------|
| Skill no se activa en Claude Code | Description muy vaga | Ir a paso 6 (optimizar triggering) |
| Skill no aparece en Codex | No se corrio evol-adapt.sh codex | `bash scripts/evol-adapt.sh codex --dest=.` |
| Eval falla sin razon clara | Prompt de eval muy ambiguo | Reescribir el prompt del eval con mas contexto |
| Assertions siempre pasan (con y sin skill) | Assertions no discriminan | Disenar assertions mas especificas sobre el valor que añade la skill |
| SKILL.md > 500 lineas | Skill sobrediseñada | Mover secciones a `references/`; mantener SKILL.md como indice |
