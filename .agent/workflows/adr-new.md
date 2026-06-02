---
description: Crea un Architecture Decision Record numerado en docs/adr/. Formato Nygard.
---
# /adr-new

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-ADR | **Versión:** 1.0 | **Agente:** Software-Architect
**Misión:** Toda decisión arquitectónica significativa queda capturada con su contexto, alternativas y consecuencias.

## 0. Pre-flight
- Crea `docs/adr/` si no existe.
- Calcula el próximo número (`NNNN` = max existente + 1, 4 dígitos).

## 1. Cuándo usar
Crear ADR cuando:
- La decisión es difícil de revertir (elección de stack, lenguaje, BD principal).
- Afecta múltiples componentes o equipos.
- Resuelve un trade-off no obvio.
- Reemplaza una decisión previa.

NO crear ADR para:
- Decisiones tácticas reversibles (nombre de variable, lib de fechas).
- Implementación específica sin alternativas razonables.

## 2. Generación
Copia `templates/adr.template.md` a `docs/adr/NNNN-<slug-kebab-case>.md` y guía al usuario en rellenar:
- Contexto (¿qué problema, qué restricciones?)
- Decisión (imperativa, 1-3 frases)
- Alternativas consideradas (con pro/contra/por qué descartadas)
- Consecuencias (positivas, negativas, neutras)
- Plan de revisión (cuándo y bajo qué señales revisitar)

## 3. Estados
- `Propuesto` — en discusión.
- `Aceptado` — vigente.
- `Reemplazado por ADR-XXXX` — superseded (mantener original, no borrar).
- `Deprecado` — ya no aplica pero se conserva por trazabilidad.

## 4. Vinculación
- Si reemplaza ADR previo: actualizar el ADR antiguo a "Reemplazado por ADR-NNNN".
- Si está relacionado con DOMAIN.md, SPEC.md, THREATS.md: enlazar.
- Indexar en `docs/adr/README.md` (índice cronológico).

## 5. Cierre
- Commit con prefijo `docs(adr): NNNN <título>`.
- MemPalace indexa.
- Notificar a equipo si decisión impacta a otros componentes.
