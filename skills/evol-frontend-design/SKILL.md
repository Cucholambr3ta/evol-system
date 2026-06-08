---
name: evol-frontend-design
description: >
  Diseno de interfaces frontend production-grade que evitan la estetica generica
  de "AI slop". Fase de design-thinking ANTES de codear, sistema de design tokens,
  y dos perfiles esteticos seleccionables (bold / enterprise-minimal) via
  evol.profile.yml. Usar cuando se construye UI, componentes, paginas, dashboards,
  landing pages, artifacts, wireframes o cualquier salida visual. Sinonimos:
  /frontend-design, disena la UI, construye el dashboard, mejora el diseno,
  build a component, design the page.
origin: evol-dd
inspired_by: anthropics/skills frontend-design (atribucion en NOTICE)
category: growth
when_to_use:
  - Usuario quiere construir UI, componente, pagina, dashboard o landing
  - Usuario quiere refinar o auditar un diseno visual existente
  - Se generan wireframes o artifacts visuales
  - Output visual riesga verse generico/AI-slop
triggers:
  - /frontend-design
  - "disena la ui"
  - "construye el dashboard"
  - "mejora el diseno"
  - "build a component"
  - "design the page"
  - "wireframe"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
evals: evals/evol-frontend-design/
---

# evol-frontend-design

## Proposito

Producir interfaces frontend distintivas y production-grade, evitando la estetica
generica de "AI slop" (morado brillante, gradientes por todas partes, fuentes
genericas, layouts predecibles). Eleva todo output de UI del sistema.

La regla central: **design-thinking ANTES de codear**. No se escribe markup hasta
elegir una direccion estetica clara y un sistema de tokens.

## Reglas hard (NUNCA se violan)

1. **Fase de design-thinking primero.** Antes de cualquier markup, definir:
   proposito (que problema resuelve la interfaz + audiencia), tono (direccion
   estetica concreta), constraints (framework, performance, a11y), diferenciacion
   (que la hace memorable).
2. **Design tokens obligatorios.** Toda la estetica vive en CSS variables
   (`:root` + temas). Cero valores de color/espaciado hardcodeados en componentes.
3. **Perfil estetico declarado.** Leer `aesthetic_profile` de `evol.profile.yml`.
   Si no existe, preguntar al usuario antes de generar (no asumir).
4. **Anti AI-slop checklist** se aplica siempre (ver abajo) — independiente del perfil.
5. **a11y minimo:** contraste WCAG AA, foco visible, semantica HTML correcta.
6. **Coherencia total.** Un solo punto de vista estetico por entregable. No mezclar
   perfiles dentro de la misma UI.

## Perfiles esteticos (aesthetic_profile)

Selector en `evol.profile.yml`. Determina la direccion visual. Default: preguntar.

### Perfil `bold` (directriz original anthropics/frontend-design)

Para landings, marketing, productos con personalidad, artifacts memorables.

- Tipografia distintiva y con caracter. Evitar fuentes genericas (Arial, Roboto).
  Parear display font expresiva con body font refinada.
- Color: comprometerse con una estetica cohesiva. Colores dominantes + acentos
  filosos superan paletas timidas. Usar CSS variables.
- Motion de alto impacto: reveals escalonados al cargar, scroll-triggers, hover
  states. CSS-only en HTML; libreria Motion en React. Para video/animacion
  programatica, delegar en [[evol-remotion]].
- Composicion espacial inesperada: asimetria, overlap, flujo diagonal, romper el
  grid, negative space generoso O densidad controlada.
- Fondos con atmosfera: texturas, gradient mesh, noise, patrones geometricos,
  transparencias en capas, grano.
- Filosofia: "no te contengas". Maximalismo necesita codigo elaborado.

### Perfil `enterprise-minimal` (referencia Linear / Vercel / GitHub Projects)

Para dashboards, plataformas internas, herramientas de productividad, B2B.
Es el perfil de EDMS.

- Paleta oscura monocromatica + UN solo color de accion. Referencia base:
  bg `#0F1115`, surface `#171A21`, surface-elevated `#1D212A`, border `#2A2F3A`,
  text-primary `#F5F7FA`, text-secondary `#9CA3AF`, accent `#4F46E5` (solo
  seleccion / foco / CTA principal).
- Semantica de color minima: normal=gris, seleccionado=indigo, warning=ambar,
  error=rojo, success=verde. Nada mas. Prohibido un color por nodo/categoria.
- Tipografia: Geist (preferida) o Inter. Escala: 32/24/20/16/14/13/12. Nada < 12px.
- Densidad de informacion alta, ruido visual bajo. Bordes invisibles o sutiles,
  sombras minimas, hover elegante. Sin barras de colores ni sparklines decorativos.
- Motion sobrio: transiciones 150ms, micro-interacciones discretas. Reveals
  funcionales (no decorativos) via [[evol-remotion]] cuando aporten claridad.
- Iconografia monocromatica: Lucide / Heroicons / Phosphor. SVG inline. Cero emojis.
- Glassmorphism: NO. Sin `backdrop-filter: blur()` por todas partes. Solo
  `rgba(255,255,255,0.03)` en overlays especificos.
- Metricas ejecutivas, no tecnicas: Health Score, Velocity, Risk Score, Blocked
  Items (no Nodes/Edges/Drawer Count).
- Frase guia: "Linear + Vercel + GitHub Projects: enterprise oscuro, minimalista,
  monocromatico, enfocado en densidad de informacion."

## Anti AI-slop checklist (todos los perfiles)

Antes de entregar, verificar y corregir:

- [ ] Sin morado/RGB brillante por defecto ni gradientes gratuitos
- [ ] Sin layout generico de "AI dashboard 2023" (cajas con bordes pesados, un color por seccion)
- [ ] Tipografia elegida con intencion (no la default del framework)
- [ ] Color via tokens, no hardcodeado
- [ ] Cero emojis como iconos (usar SVG)
- [ ] Direccion estetica unica y coherente, no "todo a la vez"
- [ ] Cada decision visual justificable (por que ese color/peso/espaciado)

## Flujo (8 pasos)

1. **Leer perfil** — `aesthetic_profile` de `evol.profile.yml`; si falta, preguntar.
2. **Design-thinking** — proposito + tono + constraints + diferenciacion (registrar).
3. **Tokens** — definir CSS variables del sistema (color, tipo, espaciado, radios).
4. **Estructura** — layout + jerarquia + densidad acorde al perfil.
5. **Componentes** — markup semantico + tokens; sin valores magicos.
6. **Motion** — transiciones/reveals acorde al perfil; delegar video a [[evol-remotion]].
7. **Anti-slop pass** — correr el checklist; corregir.
8. **Registro** — documentar el por que del diseno (decisiones esteticas).

## Integracion Evol-DD

- **Fase 4 (Build):** se inyecta automaticamente al construir UI, junto a
  [[evol-remotion]] (estatica + motion = toolkit de diseno).
- **Transversal:** gatillo cuando el usuario pide "disena / componente / dashboard
  / landing / wireframe".
- Complementa [[design-system-builder]] (tokens + Storybook + componentes atomicos)
  y [[a11y-audit]] (verificacion WCAG).
- El perfil EDMS es `enterprise-minimal`.

## Agentes que la usan

- `evol-ux` — discovery y validacion de direccion visual
- `evol-builder` — construye UI con tokens
- `evol-reviewer` — corre el anti-slop checklist en review

## Limites

- No reemplaza [[design-system-builder]] (ese genera el design system completo con
  Storybook); esta skill define la direccion estetica + tokens base.
- No genera video/animacion programatica (eso es [[evol-remotion]]).
- No audita accesibilidad en profundidad (eso es [[a11y-audit]]).
- No decide el perfil estetico por el usuario si no esta declarado: pregunta.

## Atribucion

Concepto inspirado en [anthropics/skills frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
(directriz "bold/anti-AI-slop"). Implementacion nativa Evol-DD: doble perfil
seleccionable por `aesthetic_profile`, perfil `enterprise-minimal` propio
(Linear/Vercel/GitHub Projects), integracion con design tokens, [[evol-remotion]]
y el pipeline de 6 fases.


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
