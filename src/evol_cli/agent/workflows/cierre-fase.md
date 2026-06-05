---
description: Ejecucion del cierre formal de una fase de desarrollo y actualizacion de la Memoria Viva de Evol-DD.
name: cierre-fase
trigger: /evol cierre-fase
---
# /evol cierre-fase

**ID:** FLUJO-CIERRE | **Version:** 1.4 | **Agente:** Architect & QA-Reviewer
**Mision:** Certificar el exito de la fase y asegurar la persistencia del conocimiento (Learning Loop).

## 0. CHECKS BLOQUEANTES

Ejecuta ANTES de pasar a Seccion 1:

1. **Gate keeper criptografico:**

   ```bash
   python3 scripts/evol-gate.py approve --phase=<fase-actual>
   ```

   Si falla: ABORT cierre. Reporta motivo. NO continuar sin resolver.

2. **Sprint number identificado:** determina el numero de sprint actual.

3. **Verificar que exista `acuerdos/lecciones/sprint-NN.md` o preparar su creacion (Seccion 2).**

4. **Verificar que exista `acuerdos/memoria/sprint-NN.md` o preparar su creacion (Seccion 3).**

## 1. DESTILACION DE LOGROS

- Resume los hitos alcanzados en la fase actual.
- Verifica contra el Plan de Implementacion que todo este marcado como `[x]`.

## 2. BUCLE DE APRENDIZAJE (POST-MORTEM)

- Identifica cualquier error, bloqueo o gotcha tecnico ocurrido.
- **Registro obligatorio en `acuerdos/lecciones/sprint-NN.md`** (formato canonico):

  ```
  ### [CATEGORIA] Titulo breve — YYYY-MM-DD
  **Contexto:** Que estabamos intentando hacer.
  **Problema:** Que fallo o sorprendio.
  **Causa raiz:** Por que paso.
  **Leccion:** Regla aplicable a futuras decisiones.
  **Aplica a:** Ambito.
  ```

  Categorias: ARQUITECTURA, SEGURIDAD, DOMINIO, TESTING, DEVOPS, PROCESO, HERRAMIENTAS.

- Si el sprint es nuevo: crear con `evol-memory --project=. sprint-close --sprint=NN`.
- Si ya existe: append directo con las lecciones del sprint.
- **Backward compat:** tambien appendear a `lecciones.md` root.

## 3. ACTUALIZACION DE MANIFIESTOS

- **`acuerdos/memoria/sprint-NN.md`** — log del sprint (hitos, bloqueos, proxima sesion):

  ```bash
  evol-memory --project=. sprint-close --sprint=NN
  # Luego editar acuerdos/memoria/sprint-NN.md con el contenido real
  ```

- **`acuerdos/memoria/` atomos** — editar decisiones.md / convenciones.md / riesgos.md (NO MEMORY.md, es agregado generado).
- **`acuerdos/lecciones/INDEX.md`** — actualizado automaticamente por sprint-close.
- **`memoria.md` root** — mantener por backward compat: appendear resumen del sprint.

## 4. CERTIFICACION DE CALIDAD

Reporte rapido:

- Drift detectado: Si/No
- Tests pasando: Si/No (ejecutar `python3 -m pytest -q`)
- Shield 0 CRITICAL: Si/No (ejecutar `python3 scripts/evol-shield.py audit --ci`)

## 5. SELLO DE CIERRE — GATE APPROVE OBLIGATORIO

```bash
python3 scripts/evol-gate.py approve --phase=<fase>
```

- Si gate approve falla: ABORT cierre, NO sello verbal.
- Termina con timestamp + estatus final + commit message sugerido.

---

*Driven by Evol-DD Learning Loop — Inc E5*
