---
name: readme-master
description: >
  Crea, audita y actualiza archivos README.md utilizando la estructura y el nivel de diseño de los repositorios Top 100 de código abierto. Aplica técnicas de Storytelling (DX vs Open Source Ecosystem) y maquetación HTML avanzada (tablas, detalles colapsables, alineación). Activar antes de cualquier acción hacia develop o main, o al crear repositorios.
origin: evol-dd
category: documentation
when_to_use:
  - Antes de realizar una acción de push hacia develop o main.
  - Al inicializar un repositorio o proyecto nuevo.
  - Después de añadir funcionalidades sustanciales que cambien la forma en que se interactúa con el proyecto.
triggers:
  - /evol readme-master
  - "actualiza el readme"
  - "crea la documentación principal"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
---

# Skill: Readme Master

## Propósito
Esta skill genera y actualiza archivos `README.md` inyectando la calidad de diseño visual y las narrativas de los proyectos de software más populares (Top 100). Evita la monotonía del texto plano integrando componentes HTML embebidos, diagramas Mermaid, tablas comparativas y un storytelling adaptado al tipo de repositorio, cumpliendo siempre con el estándar estricto de **Evol-DD** (Cero Emojis).

## Uso
El agente evaluará el código base o la descripción entregada y reconstruirá el archivo `README.md` siguiendo estrictamente esta arquitectura:

### 1. El Estándar Intermedio (Top 100 + Semántica)
Todo `README.md` generado debe contener, en orden estricto:
1. **Hero Visual Atractivo:** Un bloque `<div align="center">` con el `<h1>` principal, y una sola línea hiper-enfocada (Focus Message) describiendo la propuesta de valor.
2. **Badges Coloridos y Estéticos:** Uso de Shields.io con colores temáticos e íconos (`?logo=python&logoColor=white`) para denotar profesionalismo sin caer en la monotonía.
3. **Tabla Comparativa (Problema vs Solución):** Una tabla limpia en HTML que contraste el enfoque tradicional vs el enfoque moderno del proyecto.
4. **Core Features:** Títulos semánticos directos (para que los LLMs y humanos indexen rápido) seguidos de bloques de código Markdown ````bash`` o ````python`` ultracortos.
5. **Arquitectura:** **Obligatorio un diagrama de arquitectura en Mermaid** (````mermaid`) que describa el sistema.
6. **Instalación y Desinstalación:** Bloques de código copiables con pasos de ejecución y un apartado explícito para desinstalar.
7. **Documentación Extendida / FAQ:** Uso de tags `<details>` y `<summary>` para esconder información sin romper el ritmo de lectura.

### 2. Storytelling: Adaptación del Relato
Antes de escribir, el agente inferirá la naturaleza del repositorio:
- **Developer Experience (DX):** Si es un Framework, CLI o Herramienta. La narrativa debe ser agresiva hacia la eficiencia ("Instalar toma 10 segundos, ahorra 3 horas"). Minimizar teoría, maximizar ejemplos copiables de inmediato.
- **Ecosistema Open Source:** Si es una librería comunitaria. Enfocarse en la gobernanza y extender el llamado a colaboradores. Usar cuadros o tablas de contribuidores.
- **Utilitario / Kernel:** Si es una herramienta de bajo nivel. El relato debe ser directo y minimalista.

### 3. Técnicas 2026 de Maquetación HTML
- **Cero Emojis (Regla Evol-DD):** Está terminantemente prohibido usar emojis. Utiliza caracteres Unicode estéticos como `❖`, `►`, `■`.
- **Alineación HTML:** Para el Hero y badges, usar `<div align="center">`.
- **Secciones Colapsables:** Todo bloque de configuración gigante o FAQs deben ir envueltos en `<details><summary><b>► Mostrar Detalle</b></summary><br>... </details>`.

## Ejecución Recursiva
Cuando el usuario solicite la creación o actualización, el agente debe:
1. Buscar los archivos `README.md` a actualizar (ya sea en la raíz, en una subcarpeta específica, o **todos** los READMEs del proyecto si se solicita de forma global).
2. Analizar el código fuente adyacente y **escanear el árbol de directorios locales** (buscando específicamente carpetas como `docs/`, o archivos Markdown hermanos) para entender la misión del proyecto y descubrir automáticamente qué enlaces debe incluir en la sección de "Documentación".
3. Rediseñar y escribir cada archivo `README.md` encontrado, aplicando el estándar estructural, HTML y Markdown de manera proporcional a su contexto local.


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
