---
description: Discovery pre-Fase 1. Valida problema, persona y JTBD antes de invertir en spec. Produce DISCOVERY.md.
name: ux-discovery
trigger: /evol ux-discovery
---
# /ux-discovery

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-UX-DISC | **Versión:** 1.0 | **Agente:** UX-Researcher + Product-Manager
**Misión:** Asegurar que existe un problema real con persona y JTBD claros antes de gastar tokens en `/fase-requisitos`.

## 0. Pre-flight
- Lee `memoria.md`, `lecciones.md`, y `evol.profile.yml` si existe.
- Si ya hay `DISCOVERY.md`, ofrece **actualizar** vs **crear nuevo**.

## 1. Entrada
Pide al usuario, en este orden:
1. **Problema percibido** en 1 frase.
2. **Para quién** (persona inicial).
3. **Evidencia** disponible (entrevistas, datos, tickets). Si no hay, marca riesgo.

Si falta cualquiera de los tres → **Filtro de Ambigüedad (Art. 1)**: solicita aclaración antes de continuar.

## 2. Estructuración (basada en `templates/discovery.template.md`)
Construye `DISCOVERY.md` en la raíz del proyecto siguiendo la plantilla:
- Problema + dolor (1-10) + evidencia
- Persona primaria
- Jobs To Be Done ("Cuando X, quiero Y, para Z")
- Alternativas existentes y por qué no resuelven
- Hipótesis de solución (Si → Esperamos → Medido por)
- Supuestos a validar (con método)
- Out of scope
- Próximo paso

## 3. Validación crítica
Antes de cerrar, evalúa con el usuario:
- ¿Cuántos clientes/usuarios han verbalizado este dolor? (n < 5 = riesgo alto)
- ¿Existe ya una solución que el usuario rechazó? (si no, sospecha de demanda baja)
- ¿La hipótesis es falsable y medible?

## 4. Decisión gated (Art. 2)
Solicita `"APROBADO"` para uno de:
- (a) Validar supuestos antes de `/fase-requisitos`.
- (b) Saltar a `/fase-requisitos` con riesgo declarado y trazado en `memoria.md`.

## 5. Cierre
- Escribe `DISCOVERY.md`.
- Indexa con MemPalace (PostToolUse hook lo hará).
- Anota decisión y riesgo en `memoria.md`.
