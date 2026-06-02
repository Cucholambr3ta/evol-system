---
name: crear-agente
description: >
  Crea nuevos agentes Evol-DD desde cero (permanentes o efimeros): genera el .md del agente
  con identidad, mision, reglas y limites; registra en registry.json; crea
  agent.template.md si no existe. Usar SOLO cuando el usuario quiera CREAR un agente
  nuevo — "crear agente", "crea un agente para X", "nuevo agente que haga Y", "añadir
  especialista en Z", "necesito un agente que sepa de X", o cuando una tarea requiera
  un rol ausente del sistema. También activar con "quiero un agente que sea experto en X",
  "agente para [dominio]", "necesito alguien que sepa de X". NO usar para: listar agentes,
  crear skills (usar /crear-skill), crear workflows, o preguntas generales sobre el
  sistema. Soporta agentes permanentes (prompts/agents/<categoria>/)
  y agentes efimeros (van a prompts/agents/ephemeral/, tienen fecha de expiracion).
origin: evol-dd
category: lifecycle
when_to_use:
  - El usuario quiere un agente especializado que no existe en el registry
  - Una tarea requiere expertise que ningun agente core cubre
  - El usuario dice "crea un agente para X" o variantes
  - Se detecta un patron recurrente que justifica un agente dedicado
triggers:
  - /crear-agente
  - "crear agente"
  - "nuevo agente"
  - "necesito un agente"
  - "agente para"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
---

# Crear Agente Evol-DD

Skill para crear agentes Evol-DD con identidad, mision y reglas bien definidas. Genera el
archivo `.md` del agente, lo registra en `registry.json`, y opcionalmente crea
`templates/agent.template.md` como base para futuros agentes efimeros.

## Proceso

### 1. Entrevistar al usuario

Antes de escribir nada, hacer estas preguntas (las que no esten claras del contexto):

- **Que hace este agente?** (1-2 lineas — su responsabilidad principal)
- **Que NO hace?** (limites explícitos — evitar scope creep)
- **Es permanente o efimero?**
  - Permanente: experto de dominio que el sistema siempre necesita
  - Efimero: especialista para una tarea concreta, se retira al terminar
- **Que categoria corresponde?**
  Ver referencias/categorias.md para la lista valida
- **Tiene un tono o personalidad especifica?** (tecnico, colaborativo, directo, educativo)
- **Con que otros agentes o skills trabaja?**

Si el usuario da suficiente contexto, extraer respuestas del historial sin preguntar todo.

### 2. Verificar si ya existe

Antes de crear, buscar en el registry:

```bash
python3 scripts/validate-registry.py --strict
grep -i "<nombre-candidato>" prompts/agents/registry.json
```

Si existe uno similar, mostrarlo al usuario y preguntar si prefiere mejorar el existente
o crear uno nuevo con diferente enfoque.

### 3. Crear el archivo .md del agente

**Destino segun tipo:**
- Permanente: `prompts/agents/<categoria>/<categoria>-<nombre>.md`
- Efimero: `prompts/agents/ephemeral/<timestamp>-<nombre>.md`

**Formato obligatorio:**

```markdown
---
name: Nombre del Agente
description: Una linea precisa que describe que hace y cuando usarlo.
color: <color-hex-o-nombre>
vibe: Una frase que captura la personalidad y enfoque del agente.
---

# [Nombre del Agente]

Parrafo de apertura: quien es, que hace, por que importa su rol.

## Mision principal

[Descripcion detallada de la responsabilidad central. Explicar el POR QUE,
no solo el QUE. El agente debe entender el razonamiento para ir mas alla
de instrucciones literales.]

## Reglas criticas

[Maximo 6 reglas. Solo las que realmente importan. Explicar cada una con
razonamiento, no con SIEMPRE/NUNCA en mayusculas.]

1. [Regla con razon]
2. [Regla con razon]

## Como trabajar

[Patron de trabajo tipico: como recibe una tarea, como la procesa,
que produce, como comunica resultados.]

## Limites

[Que NO hace este agente. Ser explicito sobre lo que esta fuera de scope.]
```

**Principios de escritura del agente:**
- Explicar el POR QUE detrás de cada instruccion — los LLMs son inteligentes y funcionan
  mejor con razonamiento que con reglas rigidas
- Evitar SIEMPRE/NUNCA en mayusculas — reformular con explicacion del razonamiento
- El tono debe ser coherente con la personalidad declarada en `vibe:`
- Usar segunda persona ("Eres X", "Tu rol es Y") para identidad fuerte
- `## Limites` es OBLIGATORIA — declara explícitamente qué NO hace el agente. Sin esta
  sección el agente asume que puede hacer todo, lo que genera scope creep.
- NO duplicar nombres de sección. Cada `##` debe aparecer exactamente una vez. Revisar
  el draft antes de guardar y eliminar duplicados.

### 4. Registrar en registry.json

Añadir entry al final del array `agents`:

```json
{
  "id": "<categoria>-<nombre-kebab>",
  "name": "<Nombre Legible>",
  "category": "<categoria>",
  "description": "<descripcion una linea>",
  "color": "<color>",
  "vibe": "<personalidad>",
  "prompt_file": "prompts/agents/<categoria>/<archivo>.md",
  "ide_compat": ["claude-code", "opencode", "cursor", "windsurf", "vscode-copilot", "antigravity", "codex"],
  "skills": [],
  "constraints": [],
  "triggers": [],
  "fallback_agent": null
}
```

Para agentes **efimeros**, añadir campos adicionales:
```json
{
  ...campos_base...,
  "ephemeral": true,
  "created_for_task": "<descripcion de la tarea>",
  "expires_after_days": 30,
  "created_at": "<ISO8601>"
}
```

### 5. Validar

```bash
python3 scripts/validate-registry.py --strict
```

Debe reportar: `✓ schema OK (N+1 agents)`. Si falla, corregir antes de continuar.

### 6. Crear agent.template.md si no existe

Si `templates/agent.template.md` no existe, crearlo como base para futuros agentes
efimeros. Ver referencias/agent-template-spec.md para el formato completo.

### 7. Reportar al usuario

```
Agente creado: [Nombre]
Archivo: prompts/agents/<categoria>/<archivo>.md
Registry: registry.json actualizado (N+1 agentes)
Tipo: permanente | efimero (expira en N dias)

Para invocar este agente en el sistema:
  /evol → mencionar el agente por nombre
  O via composition_pattern si necesita coordinacion con otros agentes
```

## Referencias

- `references/categorias.md` — lista de categorias validas y cuando usar cada una
- `references/agent-template-spec.md` — spec completa del formato de agente efimero
- `references/ejemplos.md` — ejemplos de agentes bien escritos del registry
