---
description: Onboarding de developer nuevo. Tour del repo, setup verificado y primer PR meaningful en 5 días.
---
# /onboard-dev

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-ONB | **Versión:** 1.0 | **Agente:** Dev-Onboarding-Coach + Codebase-Onboarding-Engineer
**Misión:** Que un dev nuevo sea productivo en ≤ 5 días con cero ambigüedad.

## 0. Pre-flight
- Copia `templates/onboarding.template.md` a `ONBOARDING.md` si no existe.
- Confirma con el dev: rol, experiencia previa con el stack, MemPalace disponible.

## 1. Sub-comandos
El workflow acepta:
- `/onboard-dev tour` — recorrido guiado por la arquitectura.
- `/onboard-dev setup` — verificación de entorno paso a paso.
- `/onboard-dev first-pr` — sugerir un good-first-issue.
- `/onboard-dev day1|week1|month1` — checklist por hito.

## 2. Día 1: setup
Guiar al dev:
```bash
bash ./scripts/xdd-doctor.sh
bash ./scripts/xdd-start.sh
```
Verificar lectura de: `CLAUDE.md`, `memoria.md`, `lecciones.md`, `docs/X-DD_Integration_Guide.md`.

## 3. Tour de arquitectura
El agente recorre:
- `DOMAIN.md` (ubiquitous language — fundamental)
- `SPEC.md` y `FEATURES.md`
- `THREATS.md` y `PRIVACY.md`
- Estructura de carpetas (decisiones, no solo descripción)
- Convenciones de commits, branches, PRs (`docs/constitucion.md` Art. 7)
- Cómo correr tests por nivel (TDD / BDD / E2E)

## 4. Pareo con MemPalace
Demostrar preguntas semánticas útiles:
- "¿cómo manejamos autenticación aquí?"
- "¿qué lecciones hay sobre migraciones?"
- "¿por qué se eligió X stack?"

## 5. Primer PR
Sugerir un cambio acotado (typo en docs, refactor de bajo riesgo, test faltante). Pareo en TDD del primer commit.

## 6. Checklist hitos
- [ ] Día 1: entorno arriba, primer PR trivial.
- [ ] Semana 1: bug fix con pipeline `/xdd-build`.
- [ ] Mes 1: feature completa end-to-end.
- [ ] Mes 2: contribuye a `lecciones.md`.

## 7. Cierre
- Feedback del dev sobre el proceso → mejora de `ONBOARDING.md` y `templates/onboarding.template.md`.
- Lecciones a [[lecciones]].
