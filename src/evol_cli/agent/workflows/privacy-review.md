---
description: Inventario de PII, bases legales y procedimientos GDPR/CCPA. Produce PRIVACY.md.
name: privacy-review
trigger: /evol privacy-review
---
# /privacy-review

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-PRIV | **Versión:** 1.0 | **Agente:** Privacy-Engineer + Compliance-Auditor
**Misión:** Conocer qué PII tratamos, con qué base legal y cómo atendemos los derechos del titular.

## 0. Pre-flight
- Copia `templates/privacy.template.md` a `PRIVACY.md` si no existe.
- Requiere `DOMAIN.md` y `SPEC.md` para identificar entidades con PII.

## 1. Inventario PII
Recorre el modelo de dominio y `events.schema.json`. Lista cada campo personal con:
- Categoría (identificación, contacto, financiero, salud, biométrico…)
- ¿Sensible? (GDPR Art. 9)
- Fuente (form, API, sub-procesador)
- Base legal (consentimiento, contrato, obligación legal, interés legítimo…)
- Retención (con justificación)
- Sub-procesador que lo recibe

## 2. Bases legales
Para cada categoría documenta la base. Para *interés legítimo*, redacta LIA (Legitimate Interest Assessment).

## 3. Derechos del titular (cómo se atienden)
Verifica que existen flujos para:
- Acceso (DSAR) — runbook + endpoint
- Rectificación — UI de perfil
- Borrado — endpoint + cascada en sub-procesadores
- Portabilidad — export JSON
- Oposición — opt-out de marketing y profiling
- Limitación

SLA estándar: 30 días.

## 4. Sub-procesadores
- Lista actualizada con país de procesamiento.
- Mecanismo de transferencia internacional (SCC, adequacy, BCR).
- Acuerdo DPA firmado y archivado.

## 5. Brechas
- Procedimiento de notificación 72h a autoridad.
- Plantilla de comunicación a afectados.
- Plantilla referenciada en `templates/runbook.template.md`.

## 6. Privacy by design checks
- [ ] Minimización: solo se pide PII necesaria para el propósito.
- [ ] Pseudonimización donde sea posible.
- [ ] Encriptación at-rest y in-transit.
- [ ] Logs sin PII (usar IDs).
- [ ] Retención automática (no manual).
- [ ] Consent UI clara y granular donde aplique.

## 7. Cierre
- Versionar `PRIVACY.md`.
- Anotar próxima revisión (6 meses o cambio sustancial).
- Si se detecta brecha, escalar inmediatamente.

---

## Extension: disciplina Compliance-Driven (COMPLIANCE)

> Activacion por profile: `compliance` en `methodologies:`. Ficha:
> [`docs/disciplinas/COMPLIANCE.md`](../../docs/disciplinas/COMPLIANCE.md).

Privacy-review cubre PII (disciplina [PrivacyDD](../../docs/disciplinas/PrivacyDD.md), mapeo directo).
Cuando el profile activa ademas `compliance`, este workflow se extiende a marcos regulatorios completos
(GDPR/HIPAA/PCI-DSS/SOC 2):

- **Entrada adicional:** perfil regulatorio aplicable + `privacy/pii_inventory.json`.
- **Salida adicional:** `compliance/control_mappings.json` (control regulatorio -> implementacion ->
  prueba) + `compliance/audit_logs_spec.json`.
- **Criterio:** cada control aplicable tiene una prueba automatizada; el pipeline falla si un control
  critico no se cumple.
- **Fuentes:** los textos regulatorios y controles se citan con su URL oficial (DOC_STANDARD).
