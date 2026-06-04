---
name: prompt-master
trigger: /evol prompt-master
title: "/prompt-master — Generación de prompts optimizados para 30+ herramientas de IA"
description: Genera prompts production-ready para herramientas específicas de IA. Extrae intención en 9 dimensiones, aplica routing por tool conventions, y nunca agrega CoT a modelos de razonamiento nativo. Complementa /mejorar-prompt para targets multi-modelo. Usa skill evol-prompt-master.
phase: any
category: productivity
ssot: true
inputs:
  - Idea de prompt + herramienta objetivo
  - Opcional: prompt existente a mejorar/adaptar
outputs:
  - Prompt copiable listo para pegar + target + optimización aplicada
skill: skills/evol-prompt-master/SKILL.md
inspired_by: nidhinjs/prompt-master
---

# /prompt-master — Prompts optimizados por herramienta

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, secciones mínimas y trazabilidad bidireccional.

## Propósito

Generar prompts production-ready para cualquier herramienta de IA respetando
las convenciones específicas de cada tool: cuándo usar CoT, cuándo no, cómo
estructurar prompts para modelos de razonamiento nativo, cómo acotar scope
en agentes con acceso al sistema.

**Diferencia con `/mejorar-prompt`:** `/mejorar-prompt` optimiza prompts de workflows
Evol-DD internos (agentes, skills, workflows del framework). `/prompt-master` se enfoca
en prompts para herramientas externas multi-modelo (Claude API, Cursor, Gemini, etc.).

**Activación condicional:** Este workflow se activa SOLO cuando el usuario pide
explícitamente escribir, arreglar, optimizar o adaptar un prompt. NO para conversación
general, coding directo ni escritura de documentos.

## Cuándo invocar

- "Escribe un prompt para [tool]"
- "Mejora este prompt para [tool]"
- "Adapta este prompt de Claude a Cursor"
- "Fix this prompt — está fallando en o3"
- Cuando `/evolve` propone una skill para un IDE externo y necesita prompt optimizado

## Procedimiento

### 0. Pre-flight
- Confirmar tool objetivo. Si ambiguo: preguntar antes de generar.
- Máx 3 preguntas clarificadoras total antes de entregar.

### 1. Extracción de intención (9 dimensiones)

| Dimensión | ¿Siempre? |
|-----------|-----------|
| Task | Siempre |
| Target tool | Siempre |
| Output format | Siempre |
| Constraints | Si complejo |
| Input del modelo | Si aplica |
| Context/historial | Si lo hay |
| Audience | Si user-facing |
| Success criteria | Si complejo |
| Examples | Si formato crítico |

### 2. Routing por tool

Aplicar `skill/evol-prompt-master` — convenciones por categoría:

**Modelos de conversación:**
```
Claude 4.x    → XML tags + explícito sobre output
ChatGPT/GPT-5 → Denso y compacto + contrato de output
Gemini 2.x    → Aprovechar ventana larga + citar solo confirmado
Qwen 2.5      → Instruction following + JSON output preferido
Ollama/Llama  → Corto y simple + role explícito
```

**Modelos de razonamiento (NUNCA CoT):**
```
o3 / o4-mini        → Instrucciones CORTAS. Sin CoT.
DeepSeek-R1         → Instrucciones limpias. Sin CoT.
Qwen3-thinking      → Sin CoT. Output estructurado sí.
```

**Coding agents / IDEs:**
```
Claude Code         → Estado + target + acciones + forbidden + stop conditions
Cursor/Windsurf     → Rutas de archivo + scope + "Done when:"
Devin/SWE-agent     → Estado + target + forbidden actions explícito
Bolt/v0             → Componente + constraints UI + "Done when:"
```

**Imagen / Video:**
```
Midjourney          → Descriptores, pesos ::N, --ar, --style
DALL-E 3            → Prosa descriptiva + estilo artístico
Stable Diffusion    → Positive + negative separados
Sora/Runway         → Lenguaje cinematográfico: cámara + luz + movimiento
```

### 3. Diagnóstico silencioso

Antes de entregar, verificar y corregir:

```
Fallas task:    verbo vago / dos tareas / sin success criteria / scope creep
Fallas contexto: riesgo alucinación / falta historial
Fallas formato:  sin output format / longitud implícita / sin role
Fallas scope:    sin estado inicial/target / filesystem sin restricción (agentic)
Fallas razonamiento: CoT en modelo de razonamiento / contradicciones
```

### 4. Output (formato lock)

```
[PROMPT LISTO PARA PEGAR]
<bloque copiable completo>

🎯 Target: <tool>
💡 <una línea: optimización principal aplicada>
⚙️ Setup: <1-2 líneas SOLO si requiere configuración especial>
```

**Aviso agentic** (si aplica — tool con acceso real al sistema):
> Aviso: Este prompt es para un agente con acceso al sistema.
> Revisar scope locks, forbidden actions y stop conditions antes de pegar.

## Integración con otros workflows

- **Complementa `/mejorar-prompt`** — este workflow para targets externos; /mejorar-prompt para internos Evol-DD.
- **Invocado desde `/evolve`** cuando se propone skill para IDE externo.
- **Invocado desde `/mejorar-prompt`** cuando el target es multi-modelo externo.
- **Invoca `/fact-check`** si el prompt incluye claims sobre comportamiento de modelos.

## Agentes delegados

| Agente | Rol |
|--------|-----|
| `evol-researcher` | Genera prompts para investigación en tools específicas |
| `evol-builder` | Construye prompts para pipelines multi-modelo y producción |
| Agente 18 (Prompt Engineer) | Delegado interno de `/mejorar-prompt` para casos complejos |

## POST-FLIGHT
- No genera artefactos persistentes por defecto (output es el prompt copiable).
- Si el usuario guarda el prompt en `/prompts/`: registrar en `memoria.md`.
