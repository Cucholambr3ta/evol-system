---
description: Investigacion autonoma de mejoras. El agente Researcher descubre nuevas skills de Claude Code, metodologias y changelogs relevantes, y propone mejoras rankeadas en RESEARCH.md. Toda propuesta requiere aprobacion humana.
name: research
trigger: /evol research
---
# /research

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-RESEARCH | **Version:** 1.0 | **Agente:** Researcher (specialized-researcher)
**Mision:** Mantener X-DD y el proyecto activo en evolucion continua mediante investigacion
proactiva del ecosistema, proponiendo mejoras rankeadas con aprobacion humana (Art. 2).

## 0. Pre-flight
- Registro obligatorio en `memoria.md` (Art. 4 Constitucion).
- Leer `lecciones.md` antes de proponer (evitar repetir descartes previos).

## 1. Alcance

| Scope | Que investiga | Salida |
| :--- | :--- | :--- |
| `system` | Mejoras al framework X-DD: skills, agentes, workflows, scripts | Propuestas para el repo X-DD |
| `project` | Mejoras al proyecto activo: librerias, metodologias, herramientas del stack | Propuestas para el proyecto |

## 2. Flujo operativo

| Fase | Accion | Herramienta |
| :--- | :--- | :--- |
| I. Descubrir | Investiga GitHub (topics claude-code-skill), changelogs, papers | `xdd-researcher run --scope <scope>` |
| II. Evaluar | Compatibilidad + colision + impacto (0.0-1.0) por hallazgo | Agente Researcher |
| III. Proponer | Genera `RESEARCH.md` + persiste en `research_proposals` (SQLite) | `xdd-researcher.py` |
| IV. Revisar | Usuario revisa propuestas rankeadas | `xdd-researcher list` |
| V. Aprobar | Usuario aprueba las relevantes (Art. 2) | `xdd-researcher apply <ID>` |
| VI. Implementar | Otro agente (builder/architect) implementa lo aprobado | Pipeline X-DD |

## 3. Comandos

```
xdd-researcher run --scope system            # mejoras al framework
xdd-researcher run --scope project --topic testing
xdd-researcher list --status proposed
xdd-researcher apply rp_<id> --by <usuario>
```

## 4. Limites (Constitucion Art. 2)

- El Researcher NUNCA implementa una propuesta por su cuenta.
- Solo actua dentro del scope declarado.
- Verifica licencia antes de proponer cualquier dependencia externa.
- El comando `run` es offline/determinista por defecto (sin red en CI).

## 5. Artefacto de salida

`RESEARCH.md` en la raiz del proyecto, cumpliendo `docs/DOC_STANDARD.md`:
tabla de propuestas rankeadas + detalle por propuesta + siguientes pasos.

## 6. Conexiones de interoperabilidad (Art. 6)
- **Predecesores:** `/cierre-fase` (retro detecta necesidad de investigar)
- **Sucesores:** `/evolve` (skills auto-generadas), `/adr-new` (decision sobre adopcion)
- **Estado SQLite:** tabla `research_proposals` en `~/.xdd/state.db`
