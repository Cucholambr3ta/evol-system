# Agent Memory

> Estilo de trabajo del agente. Leido al inicio de cada sesion (Constitucion Art. 3).

## Preferencias de comunicacion

- Lenguaje: espanol
- Tono: profesional, directo
- Formato: markdown sin emojis

## Contexto operativo

- Framework: Evol-DD
- GitFlow: main + develop + feature/*
- Docs: DOC_STANDARD.md — Mermaid obligatorio, 0 emojis, trazabilidad REQ-NNN

## Metodologia

- Diseño antes de codigo
- Tests antes de features
- Commits pequenos y frecuente
- Gates en CI: pytest, shell, security, eval

## Preferencias descubiertas

- Quiere planes atomicos (un solo markdown por plan), no dispersion en multiples archivos
- Quiere research-first: investigar repos de referencia antes de implementar
- Quiere resultado de investigacion como plan accionable, no solo analisis
- Quiere que los planes incluyan: arquitectura, schema, hooks, tests, fuentes, orden de ejecucion
- Trabaja en español, respuestas cortas y directas
- No emojis en archivos del proyecto
- Quiere una consistencia rigurosa en la documentación (0% drift en sidecars JSON) y validación inmediata contra el estándar en cada iteración.
- Quiere tracking en tiempo real del estado del proyecto (Active/Paused/Error)
- Quiere detección inmediata de loops de agente para evitar sobreconsumo de tokens
- Prefiere stdlib Python sobre dependencias externas cuando es posible
- Wireframes se diseñan como HTML estático, no como prototipos interactivos
- Quiere que el monitoreo sea visible en interfaces gráficas (dashboard HTML + SSE)


## Notas

- Framework: Evol-DD
- GitFlow: main + develop + feature/*
- Docs: DOC_STANDARD.md — Mermaid obligatorio, 0 emojis, trazabilidad REQ-NNN- Antes de ejecutar un plan retomado tras compactación, grep identificadores clave en archivos objetivo — puede ya estar implementado en sesión previa (evitar duplicados)
- Delegar tareas grandes/arquitectónicas a subagentes con prompt completo y autocontenido (no fragmentado en pasos separados)
