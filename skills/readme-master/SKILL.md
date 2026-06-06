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

### 1. El Estándar 2026 (Minimalista y AI-Friendly)
Todo `README.md` generado debe contener, en orden estricto:
1. **Banner Adaptativo:** Un bloque HTML `<picture>` en el `<div align="center">` que soporte cambio automático entre tema claro y oscuro (mediante `prefers-color-scheme`).
2. **Hero Minimalista y Focus Hook:** Inmediatamente después del banner, el `<h1>` y **una sola línea** hiper-enfocada (Focus Message) describiendo la propuesta de valor sin ruido visual.
3. **Badges Monocromáticos:** Uso de Shields.io con el estilo `style=flat-square` y un color corporativo uniforme (ej. `#1e293b`) para denotar profesionalismo.
4. **Tabla Comparativa (Problema vs Solución):** Una tabla limpia en HTML que contraste el enfoque tradicional vs el enfoque moderno del proyecto.
5. **Core Features (AI-Friendly Snippets):** Títulos semánticos directos (para que los LLMs indexen rápido) seguidos de bloques de código Markdown ````bash`` o ````python`` ultracortos.
6. **Arquitectura:** **Obligatorio un diagrama de arquitectura en Mermaid** (````mermaid`) que describa el sistema.
7. **Instalación & Quick Start.**
8. **Documentación Extendida / FAQ:** Uso de tags `<details>` y `<summary>` para esconder información sin romper el minimalismo.

### 2. Storytelling: Adaptación del Relato
Antes de escribir, el agente inferirá la naturaleza del repositorio:
- **Developer Experience (DX):** Si es un Framework, CLI o Herramienta. La narrativa debe ser agresiva hacia la eficiencia ("Instalar toma 10 segundos, ahorra 3 horas"). Minimizar teoría, maximizar ejemplos copiables de inmediato.
- **Ecosistema Open Source:** Si es una librería comunitaria. Enfocarse en la gobernanza y extender el llamado a colaboradores. Usar cuadros o tablas de contribuidores.
- **Utilitario / Kernel:** Si es una herramienta de bajo nivel. El relato debe ser directo y minimalista.

### 3. Técnicas 2026 de Maquetación HTML
- **Cero Emojis (Regla Evol-DD):** Está terminantemente prohibido usar emojis. Utiliza caracteres Unicode estéticos como `❖`, `►`, `■`.
- **Alineación HTML:** Para el Hero y badges, usar `<div align="center">`.
- **Secciones Colapsables:** Todo bloque de configuración gigante o FAQs deben ir envueltos en `<details><summary><b>► Mostrar Detalle</b></summary><br>... </details>`.

## Ejecución
Cuando el usuario solicite la creación o actualización, primero analiza el `package.json`, `pyproject.toml`, o los archivos fuente clave para extraer la misión real del proyecto. Luego rediseña y escribe el archivo `README.md` en la raíz con el nuevo estilo en HTML y Markdown.
