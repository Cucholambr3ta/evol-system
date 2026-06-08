---
name: evol-context7
description: >
  Inyeccion de documentacion version-specific y actualizada de librerias/frameworks
  al contexto del agente via Context7 (MCP server o CLI ctx7). Elimina APIs
  alucinadas, ejemplos obsoletos y respuestas genericas cuando se trabaja con
  versiones nuevas fuera del knowledge cutoff. Usar al fijar contratos de
  dependencias (Spec) o al escribir codigo contra una libreria (Build). Sinonimos:
  /context7, use context7, docs actualizadas de, documentacion de la libreria,
  como se usa la API de.
origin: evol-dd
inspired_by: upstash/context7 (atribucion en NOTICE)
category: research
when_to_use:
  - Se fija una dependencia con version especifica en Spec
  - Se escribe codigo contra una libreria/framework en Build
  - El agente sospecha que su conocimiento de una API esta obsoleto
  - El usuario pide docs actualizadas de una libreria
triggers:
  - /context7
  - "use context7"
  - "docs actualizadas de"
  - "documentacion de la libreria"
  - "como se usa la api de"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
evals: evals/evol-context7/
---

# evol-context7

## Proposito

Traer documentacion actualizada y version-specific de librerias al contexto, en
lugar de confiar en el conocimiento del modelo (que tiene cutoff y aluciona APIs).
Critico para EDMS UI: React 19, Tailwind 4, FastAPI 0.115+ son versiones nuevas
posteriores al cutoff del modelo.

Context7 es un servicio externo de Upstash. Esta skill **documenta como integrarlo
y cuando invocarlo** — no lo reimplementa.

## Dos modos de integracion

Evol-DD adopto MCP nativo (v0.6.0). Modo preferido: MCP server.

### Modo MCP (preferido)

Registrar el server una vez via el gestor oficial:

```bash
bash scripts/evol-mcp.sh add context7 npx @upstash/context7-mcp
bash scripts/evol-mcp.sh status   # verificar
bash scripts/evol-mcp.sh list     # listar servers
```

Uso en prompt: agregar `use context7` a la peticion. Ej:
`"Como configuro middleware en Next.js 15? use context7"`. El server inyecta la
doc matching automaticamente.

### Modo CLI (fallback, sin MCP)

Si el IDE no soporta MCP o se prefiere CLI:

```bash
npx -y @upstash/context7-mcp   # o instalar ctx7 CLI
```

Invocar `ctx7` con library-id + version para recuperar docs puntuales.

## Reglas hard

1. **No alucinar versiones.** Si se trabaja con una version posterior al cutoff,
   consultar Context7 antes de escribir codigo contra esa API.
2. **Citar la fuente** de la doc recuperada (DOC_STANDARD 1.7 — toda info externa
   lleva su origen).
3. **No indexar secrets.** Lo recuperado es doc publica; no pegar tokens/keys.
4. **Verificar antes de aceptar.** Si un claim de la doc parece dudoso, pasar por
   [[evol-fact-check]].

## Integracion Evol-DD

- **Fase 2 (Spec):** al fijar el contrato de dependencias y sus versiones.
- **Fase 4 (Build):** al escribir codigo contra una libreria con version especifica.
- Gatillo automatico: el agente detecta una dependencia con version pinneada que
  excede su knowledge cutoff.
- Complementa [[evol-fact-check]] (verificacion de claims) y [[api-contract]].

## Agentes que la usan

- `evol-builder` — codigo contra libs actualizadas
- `evol-architect` — decisiones de stack con versiones reales
- `evol-researcher` — investigacion de APIs

## Limites

- Depende de un servicio externo (Upstash Context7). Sin red, no funciona.
- No reemplaza la doc oficial del proyecto; complementa con doc de terceros.
- No es memoria persistente (eso es EDMS / [[mempalace-sync]]).
- No reimplementa Context7 — solo integra el server/CLI.

## Atribucion

Integracion de [upstash/context7](https://github.com/upstash/context7) (MIT).
Servicio externo, no reimplementado. Evol-DD aporta: registro via `evol-mcp.sh`,
reglas de citacion (DOC_STANDARD), e integracion en fases Spec/Build del pipeline.
