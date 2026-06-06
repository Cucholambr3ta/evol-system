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

### 1. La Estructura Estándar (El Esqueleto Top 100)
Todo `README.md` generado debe contener, en orden estricto:
1. **Hero (Cabecera Visual):** Un bloque `<div align="center">` con el `<h1>` principal, un `<p>` resaltado con el pitch de 2 líneas, y un `<p>` secundario que aloje *Badges de Shields.io* estéticos. Es obligatorio añadir soporte visual a los badges (ej. `?logo=python&logoColor=white`).
2. **Tabla Comparativa (Problema vs Solución):** Una tabla en HTML (`<table>...</table>`) que contraste cómo la industria resuelve el dolor y cómo lo soluciona este proyecto de manera magistral.
3. **Módulos de Código (El "Aha! Moment"):** Debajo de la tabla, inyectar directamente la demostración del flujo clave en bloques Markdown ````bash`` o ````python`` (fragmentos ultracortos).
4. **Tabla de Contenidos (TOC):** Solo generada si el archivo supera las 5 secciones.
5. **Arquitectura:** **Debe generarse un bloque de diagrama de arquitectura en Mermaid** (````mermaid`) que describa el flujo principal.
6. **Instalación & Quick Start:** Bloques de código copiables con pasos de ejecución `< 5 minutos`.
7. **Documentación Extendida / FAQ:** Uso de tags `<details>` y `<summary>` para esconder información densa o FAQs sin romper el ritmo de lectura.
8. **Contributing & Licencia.**

### 2. Storytelling: Adaptación del Relato
Antes de escribir, el agente inferirá la naturaleza del repositorio:
- **Developer Experience (DX):** Si es un Framework, CLI o Herramienta. La narrativa debe ser agresiva hacia la eficiencia ("Instalar toma 10 segundos, ahorra 3 horas"). Minimizar teoría, maximizar ejemplos copiables de inmediato.
- **Ecosistema Open Source:** Si es una librería comunitaria. Enfocarse en la gobernanza y extender el llamado a colaboradores. Usar cuadros o tablas de contribuidores.
- **Utilitario / Kernel:** Si es una herramienta de bajo nivel. El relato debe ser directo y minimalista.

### 3. Técnicas de Maquetación HTML (Nivel Top 100)
- **Cero Emojis (Regla Evol-DD):** Está terminantemente prohibido usar emojis (🚀, 📦, 🛠️). Utiliza caracteres Unicode estéticos como `❖`, `►`, `■` o viñetas estándar (`-`).
- **Alineación HTML:** Para el Hero y badges, usar obligatoriamente `<div align="center">`.
- **Secciones Colapsables:** Todo bloque de configuración gigante, logs enormes o listados aburridos deben ir envueltos en `<details><summary><b>► Mostrar Detalle</b></summary><br>... </details>`.

## Ejecución
Cuando el usuario solicite la creación o actualización, primero analiza el `package.json`, `pyproject.toml`, o los archivos fuente clave para extraer la misión real del proyecto. Luego rediseña y escribe el archivo `README.md` en la raíz con el nuevo estilo en HTML y Markdown.
