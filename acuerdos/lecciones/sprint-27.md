# Lecciones Sprint 27 — 2026-06-04

> Formato: CATEGORIA / Contexto / Problema / Causa raiz / Leccion / Aplica a.

### [DEVOPS] Versiones PyPI no se pueden reutilizar — bump preventivo antes de publicar
**Contexto:** Al intentar publicar evol-dd 0.2.4, PyPI rechazó con "File already exists".
**Problema:** La versión 0.2.4 ya existía de una sesión anterior. PyPI es inmutable.
**Causa raiz:** El tracking de versiones publicadas no estaba en memoria persistente.
**Leccion:** Antes de publicar: verificar última versión en PyPI con `pip index versions evol-dd`. Registrar la última versión publicada en MEMORY.md del proyecto para evitar colisiones.
**Aplica a:** Todo ciclo de publicación PyPI en evol-dd y proyectos distribuidos.

### [ARQUITECTURA] Herencia X-DD → Evol-DD: adaptar paths (.evol/ vs .xdd/) y env vars (EVOL_ vs XDD_)
**Contexto:** Port de los validadores discipline-check y gitflow de X-DD a Evol-DD.
**Problema:** Los paths hardcoded (.xdd/briefing/, .xdd/spec/) y las env vars (XDD_DISCIPLINE) no funcionan en evol-dd que usa .evol/ y EVOL_ prefix.
**Causa raiz:** X-DD y Evol-DD tienen namespaces distintos por diseño (evol- vs xdd-). La herencia no es copia directa.
**Leccion:** Al portar de X-DD a Evol-DD: (1) buscar artefactos en .evol/ primero, luego fallback a paths alternativos; (2) todas las env vars usan EVOL_ prefix; (3) scripts llaman evol-* no xdd-*. Mantener lista de diferencias en MEMORY.md del proyecto evol-dd.
**Aplica a:** Cualquier port futuro X-DD → Evol-DD.
