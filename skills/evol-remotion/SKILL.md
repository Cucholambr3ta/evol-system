---
name: evol-remotion
description: >
  Creacion programatica de motion y video en React con Remotion (useCurrentFrame,
  interpolate, Sequence). Es la capa de diseno dinamico/animado del toolkit de
  diseno de Evol-DD, complementaria a evol-frontend-design (estatica). Usar al
  construir UI con animacion, transiciones, reveals, hero animations, demos de
  producto o video programatico. Sinonimos: /remotion, anima esto, crea un video,
  transicion animada, motion design, demo animada del producto.
origin: evol-dd
inspired_by: remotion-dev/skills (atribucion en NOTICE)
category: growth
when_to_use:
  - Se construye UI con animacion o transiciones no triviales
  - Se necesita video programatico o demo animada del producto
  - Reveals/micro-interacciones que exceden CSS simple
  - Hero animations o motion design en React
triggers:
  - /remotion
  - "anima esto"
  - "crea un video"
  - "transicion animada"
  - "motion design"
  - "demo animada"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
evals: evals/evol-remotion/
---

# evol-remotion

## Proposito

Crear motion y video programatico en React usando Remotion. Es la **capa dinamica**
del toolkit de diseno de Evol-DD: [[evol-frontend-design]] define la estetica y los
tokens (que se ve), `evol-remotion` define el movimiento (como se anima). Las dos
juntas forman el sistema de diseno completo.

Ejemplos: reveals escalonados de paneles, transiciones entre vistas de un dashboard,
animacion del knowledge graph, hero animations de landing, demos de producto en video.

## Reglas hard (NUNCA se violan)

1. **Animacion frame-based, no CSS.** En render de Remotion, CSS transitions/animations
   estan prohibidas — no renderizan correctamente. Usar `useCurrentFrame()` +
   `interpolate()` para toda animacion.
2. **Composicion declarada.** Definir dimensiones, fps y duracion en la metadata de
   la composition.
3. **Timeline con `<Sequence>`.** Manejar delays y duraciones con `<Sequence>`, no
   con timers manuales.
4. **Assets via componentes Remotion.** `<Img>`, `<Video>`, `<Audio>` — no tags HTML
   crudos para media en render.
5. **Coherencia con la estetica.** El motion respeta el `aesthetic_profile` activo
   ([[evol-frontend-design]]): en `enterprise-minimal`, transiciones sobrias 150ms,
   reveals funcionales; en `bold`, motion de alto impacto.

## Capacidades

| Area | Que cubre |
|------|-----------|
| Fundamentos | Scaffolding, `useCurrentFrame()`, `interpolate()`, manejo de assets |
| Media | `<Img>`, `<Video>`, `<Audio>` |
| Timeline | `<Sequence>` para delays y duraciones |
| Config | dimensiones, fps, duracion en metadata de composition |
| Avanzado | captions, 3D, audio visualization, fonts, text animations, transitions, parametrizacion |

## Flujo

1. **Leer perfil estetico** — `aesthetic_profile` de `evol.profile.yml` (define la
   intensidad del motion).
2. **Definir composition** — dimensiones + fps + duracion.
3. **Estructurar timeline** — `<Sequence>` por escena/elemento.
4. **Animar** — `useCurrentFrame()` + `interpolate()` (nunca CSS).
5. **Integrar assets** — componentes Remotion.
6. **Render/preview** — validar que renderiza correcto.

## Integracion Evol-DD

- **Fase 4 (Build):** disponible siempre como capa de motion; se inyecta junto a
  [[evol-frontend-design]] (estatica + motion = toolkit de diseno). No es opt-in.
- Gatillo: se construye UI con animacion, video, demos o transiciones.
- Combinable: un dashboard usa [[evol-frontend-design]] para layout/tokens +
  `evol-remotion` para reveals y transiciones.
- Complementa [[design-system-builder]] (componentes) y [[a11y-audit]] (respetar
  prefers-reduced-motion).

## Agentes que la usan

- `evol-ux` — motion design y prototipos animados
- `evol-builder` — implementa animaciones/video en React

## Limites

- Especifico de React + Remotion. No aplica a stacks sin React.
- No define la estetica estatica (eso es [[evol-frontend-design]]).
- No reemplaza CSS para micro-interacciones triviales fuera de render Remotion.
- Respetar accesibilidad: ofrecer `prefers-reduced-motion` cuando aplique.

## Atribucion

Best-practices basadas en [remotion-dev/skills](https://github.com/remotion-dev/skills)
(remotion = video creation in React). Implementacion nativa Evol-DD: integracion
como capa de motion del toolkit de diseno junto a [[evol-frontend-design]],
respeto del `aesthetic_profile`, e insercion en Fase 4 del pipeline.


## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
