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
Esta skill genera y actualiza archivos `README.md` inyectando la calidad de diseño y las narrativas de los proyectos de software más populares (Top 100). Evita la monotonía del texto plano integrando componentes HTML embebidos, diagramas Mermaid, tablas comparativas y un storytelling adaptado al tipo de repositorio, todo cumpliendo rigurosamente con el estándar estricto de **Evol-DD** (Cero Emojis).

## Uso
El agente evaluará el código base o la descripción entregada y reconstruirá el archivo `README.md` siguiendo estrictamente esta arquitectura:

### 1. La Estructura Estándar (El Esqueleto)
Todo `README.md` generado debe contener, en orden estricto:
1. **Cabecera (Header):** Título alineado al centro usando HTML (`<h1 align="center">`).
2. **Badges Dinámicos:** Alineados bajo la cabecera. Incluir Shields.io estáticos o dinámicos para CI/CD, Versión, Licencia y Stack Principal.
3. **Pitch Corto:** Un párrafo de 1 a 3 líneas describiendo concisamente el valor del proyecto.
4. **Tabla de Contenidos (TOC):** Solo generada si el archivo supera las 5 secciones.
5. **Demostración Visual / Arquitectura:** Si no hay GIF/Screenshot disponible, **debe generarse un bloque de diagrama de arquitectura en Mermaid** (````mermaid`) que describa el flujo principal del código evaluado.
6. **Características (Features):** Lista de viñetas claras enfocadas en el dolor que solucionan.
7. **Quick Start / Instalación:** Bloques de código copiables con pasos de ejecución `< 5 minutos`.
8. **Documentación Extendida / FAQ:** Uso de tags `<details>` y `<summary>` para esconder información densa o FAQs sin romper el ritmo de lectura.
9. **Contributing & Comunidad:** Guía corta de cómo aportar.
10. **Licencia:** Mención legal.

### 2. Storytelling: Adaptación del Relato
Antes de escribir, el agente inferirá la naturaleza del repositorio:
- **Developer Experience (DX):** Si es un Framework, CLI o Herramienta. La narrativa debe ser agresiva hacia la eficiencia ("Instalar toma 10 segundos, ahorra 3 horas"). Minimizar teoría, maximizar ejemplos copiables. Usar diseño corporativo/estilizado.
- **Ecosistema Open Source:** Si es una librería comunitaria. Enfocarse en la gobernanza y extender el llamado a colaboradores. Usar cuadros o tablas de contribuidores (All-Contributors format).
- **Utilitario / Kernel:** Si es una herramienta de bajo nivel. El relato debe ser directo, áspero y minimalista. Sin banners, pura especificación y rendimiento.

### 3. Técnicas de Maquetación HTML (Nivel Top 100)
- **Cero Emojis (Regla Evol-DD):** Está terminantemente prohibido usar emojis (🚀, 📦, 🛠️) en el documento generado. Utiliza viñetas estándar (`-`), símbolos matemáticos o HTML simple.
- **Alineación HTML:** Para títulos y badges usar `<p align="center">`.
- **Secciones Colapsables:** Todo bloque de código complejo de configuración, logs enormes o FAQs debe ir envuelto en `<details><summary>Mostrar Configuración Avanzada</summary> ... </details>`.
- **Tablas de Arquitectura:** Genera tablas en Markdown para dependencias, stack tecnológico y comparativas funcionales.

## Ejecución
Cuando el usuario solicite la creación o actualización, primero analiza el `package.json`, `pyproject.toml`, o los archivos fuente clave para extraer la misión real del proyecto y reflejarla fielmente. Finalmente, escribe o sobrescribe el archivo `README.md` en la raíz.
