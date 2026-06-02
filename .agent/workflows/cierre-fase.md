---
description: Ejecución del cierre formal de una fase de desarrollo y actualización de la Memoria Viva de X-DD.
---
# /cierre-fase

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-CIERRE | **Versión:** 1.3 | **Agente:** Architect & QA-Reviewer
**Misión:** Certificar el éxito de la fase y asegurar la persistencia del conocimiento (Learning Loop).

## 0. CHECKS BLOQUEANTES (Sprint 28 / ADR-0038 + Sprint 31 / ADR-0041)

> **Lección retroactiva:** en proyecto piloto multi-IDE, cierre se ejecutó "APROBADO" verbal sin gate criptográfico ni update de `lecciones.md`. Ahora son **gates bloqueantes**.

Ejecuta ANTES de pasar a Sección 1:

1. **Gate keeper criptográfico:**
   ```
   python3 scripts/xdd-gate.py validate --phase=<fase-actual>
   ```
   Si exit code != 0 → **ABORT cierre**. Reporta motivo al usuario (artefacto faltante / checksum mismatch / firma inválida). NO continúes sin resolver.

2. **lecciones.md modificado en esta sesión:**
   ```
   git diff --name-only HEAD | grep -q "^lecciones\.md$" || git status --short | grep -q "lecciones\.md"
   ```
   Si NO → **bloquea cierre**. Mensaje: "Cierre rechazado: lecciones.md no actualizado. Registra al menos 1 entry de aprendizaje (ver Sección 2) antes de continuar."

3. **memoria.md modificado en esta sesión:** misma verificación. Bloquea cierre si NO.

## 1. DESTILACIÓN DE LOGROS
- Resume los hitos alcanzados en la fase actual.
- Verifica contra el **Plan de Implementación** que todo esté marcado como `[x]`.

## 2. BUCLE DE APRENDIZAJE (POST-MORTEM)
- Identifica cualquier error, bloqueo o "gotcha" técnico que ocurrió durante el desarrollo.
- **Registro obligatorio**: Añade al menos 1 entry a `lecciones.md` con formato canónico (CATEGORÍA / Contexto / Problema / Causa raíz / Lección / Aplica a).
- **Evolución**: Si la solución es reutilizable, propón al usuario crear una nueva skill en `.agent/skills/` o `skills/<name>/SKILL.md` (SSoT).

## 3. ACTUALIZACIÓN DE MANIFIESTOS
- Actualiza `memoria.md` con el log de la sesión (Sección "Bitácora de Sesiones" con timestamp + hitos + bloqueos + próxima sesión).
- Actualiza `CLAUDE.md` con el nuevo "Estado Actual" y "Próximo Hito".

## 4. CERTIFICACIÓN DE CALIDAD
- Genera un reporte rápido de QA:
  - ¿Drift detectado? (Sí/No)
  - ¿Tests pasando? (Sí/No)
  - ¿Estética premium validada? (Sí/No)

## 5. AUTO-ORGANIZE (Sprint 31 / ADR-0041)

Ejecuta antes del sello de cierre:

```bash
bash scripts/xdd-organize.sh apply
```

Acciones automáticas:
- Mueve `SPEC.md`/`DOMAIN.md`/`THREATS.md`/`DISCOVERY.md`/`PLAN.md` root → `docs/`
- Mueve `ADR-*.md` root → `docs/adr/`
- Mueve `*-research-*.md` / `*-inspiration-*.md` → `docs/research/`
- Añade a `.gitignore`: caches (`node_modules/`, `__pycache__/`, `.venv/`), binarios (`*.log`, `*.tmp`, `*.bak`), IDE state (`.idea/`, `.DS_Store`), secretos (`.env`, `*.pem`, `*.key`)
- WARN si secretos ya tracked en git (SecDD violation)

Opt-out: `XDD_NO_ORGANIZE=1`. Manual review: `bash scripts/xdd-organize.sh check`.

## 6. SELLO DE CIERRE — GATE APPROVE OBLIGATORIO (Sprint 28)
- Ejecuta `python3 scripts/xdd-gate.py approve --phase=<fase>` con firma HMAC-SHA256.
  - Genera `.xdd/<fase>/.signature` (firma criptográfica del cierre).
  - Marca `.xdd/<fase>/.status` = APROBADO.
- Si gate approve falla → ABORT cierre, NO sello verbal.
- Archiva planes completados de `/docs/plans` a `/docs/plans/archive/` (opcional).
- Termina con timestamp + estatus final del proyecto + commit message sugerido al usuario.

---
*Driven by X-DD Learning Loop — Sprint 28 / ADR-0038 + Sprint 31 / ADR-0041*
