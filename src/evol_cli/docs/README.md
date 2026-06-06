# Documentacion — Evol-DD

Indice del directorio `docs/`. Cada subdirectorio cubre un area especifica del sistema.

## Estructura

| Directorio / Archivo | Contenido |
|----------------------|-----------|
| `constitucion.md` | Ley suprema del sistema. 9 articulos de gobernanza. |
| `DOC_STANDARD.md` | Estandar: sin emojis, Mermaid obligatorio, Gherkin, trazabilidad. |
| `modos.md` | Modos de operacion: Base, Completo, Memoria conversacional. |
| `GATE.md` | Gate keeper HMAC-SHA256: arquitectura, comandos, fail-closed. |
| `CONFIG.md` | Referencia de evol.config.yml y evol.profile.yml. |
| `IDE_SETUP.md` | Setup de los 7 IDEs soportados por evol-adapt.sh. |

| `RETROFIT_GUIDE.md` | Migracion desde X-DD: tabla de equivalencias xdd-* vs evol-*. |
| `evol-dd_Integration_Guide.md` | Relacion Evol-DD / X-DD: diferencias clave. |
| `equipo.md` | Directorio de agentes auto-generado desde registry.json. |
| `arquitectura/` | ARQUITECTURA.md (C4), DOMINIO.md (DDD), DECISIONES.md (ADRs). |
| `requisitos/` | FUNCIONALES.md, NO_FUNCIONALES.md, RESTRICCIONES.md, GLOSARIO.md. |
| `qa/` | PLAN_QA.md, CASOS_GHERKIN.md, CASOS_BORDE.md, REPORTE_QA.md. |
| `seguridad/` | THREATS.md (STRIDE), SECURITY_CONTROLS.md, PRIVACY.md. |
| `diagramas/` | Diagramas Mermaid: componentes, despliegue, flujo-datos. |
| `operaciones/` | RUNBOOK.md, MONITORING.md, DR_PLAN.md, RELEASE_PROCESS.md. |
| `guias/` | ONBOARDING.md, CONTRIBUCION.md, TROUBLESHOOTING.md. |
| `usuario/` | MANUAL_USUARIO.md, FAQ.md. |
| `api/` | API_GUIDE.md — referencia CLI: entry-points y variables de entorno. |

## Lectura recomendada por rol

**Nuevo desarrollador:** constitucion.md → guias/ONBOARDING.md → arquitectura/ARQUITECTURA.md → guias/CONTRIBUCION.md

**Operador:** modos.md → GATE.md → operaciones/RUNBOOK.md → operaciones/MONITORING.md

**Revisor de seguridad:** seguridad/THREATS.md → seguridad/SECURITY_CONTROLS.md → GATE.md

**Usuario final:** usuario/MANUAL_USUARIO.md → usuario/FAQ.md → modos.md
