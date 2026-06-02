# lecciones.md — Aprendizajes Acumulados

> Lecciones aprendidas del proyecto. Consultado por agentes antes de proponer
> soluciones (Constitucion Art. 9). Motor: `scripts/evol-lessons.py`.
> Actualizar via `/evol cierre-fase` o `evol-lessons add`.

## Formato

```
### [CATEGORIA] Titulo breve — YYYY-MM-DD
**Contexto:** Que estabamos intentando hacer.
**Problema:** Que fallo o sorprendio.
**Causa raiz:** Por que paso.
**Leccion:** Regla aplicable a futuras decisiones.
**Aplica a:** Ambito donde aplica.
**Fix aplicado:** Que se hizo para resolver. (opcional)
**Mejoras sugeridas:** Propuestas del investigador. (opcional)
**Estado mejoras:** pendiente | en-progreso | aplicado (opcional)
```

Categorias: `ARQUITECTURA` `SEGURIDAD` `DOMINIO` `TESTING` `DEVOPS` `PROCESO` `HERRAMIENTAS`

Comandos rapidos:
- `evol-lessons search QUERY` — buscar antes de decidir
- `evol-lessons add --titulo ... --categoria ... --leccion ...` — añadir
- `evol-lessons suggest-fix "titulo"` — investigador propone mejoras
- `evol-lessons list --pendientes` — ver mejoras pendientes

---

## ARQUITECTURA

### [ARQUITECTURA] Gate key global compromete aislamiento — 2026-06-02
**Contexto:** Diseñando sistema de gates en Evol-DD
**Problema:** Key global compartida entre proyectos elimina invariante de auditoria
**Causa raiz:** Decision de simplificacion de UX sacrifico seguridad
**Leccion:** Gate key por proyecto — evol gate init --from-global como punto de partida
**Aplica a:** Todo proyecto con evol-gate.py

## SEGURIDAD

_(vacio)_

## DOMINIO

_(vacio)_

## TESTING

_(vacio)_

## DEVOPS

_(vacio)_

## PROCESO

_(vacio)_

## HERRAMIENTAS

_(vacio)_

