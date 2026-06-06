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


## Notas

- Framework: Evol-DD
- GitFlow: main + develop + feature/*
- Docs: DOC_STANDARD.md — Mermaid obligatorio, 0 emojis, trazabilidad REQ-NNN