# Categorias de agentes X-DD

Usar la categoria que mejor describe el DOMINIO de responsabilidad del agente.

| Categoria | Cuando usar | Ejemplos |
|-----------|-------------|---------|
| `academic` | Investigacion, analisis academico, contenido educativo | historian, psychologist, anthropologist |
| `design` | Diseño visual, UX, branding, sistemas de diseño | ui-designer, ux-architect, brand-guardian |
| `engineering` | Desarrollo de software, arquitectura, DevOps, seguridad, testing | backend-architect, code-reviewer, sre |
| `finance` | Analisis financiero, contabilidad, inversiones, FP&A | financial-analyst, bookkeeper |
| `game-development` | Diseño de juegos, nivel, audio, arte tecnico | game-designer, level-designer |
| `marketing` | Contenido, SEO, redes sociales, growth, e-commerce | seo-specialist, content-creator |
| `paid-media` | Publicidad pagada, PPC, programmatica, creatives | ppc-strategist, paid-social |
| `product` | Product management, analytics, roadmap, feedback | product-manager, sprint-prioritizer |
| `project-management` | Gestion de proyecto, operaciones, coordinacion | project-shepherd, studio-operations |
| `sales` | Ventas, CRM, outreach, propuestas, pipeline | sales-coach, deal-strategist |
| `security` | Seguridad ofensiva/defensiva, pentest, compliance | pentest-operator |
| `spatial-computing` | AR/VR/XR, visionOS, interfaces espaciales | xr-developer, spatial-engineer |
| `specialized` | Roles que no encajan en otra categoria | chief-of-staff, mcp-builder, model-qa |
| `strategy` | Estrategia empresarial, nexus, planificacion | nexus-strategy |
| `support` | Soporte, onboarding, documentacion para usuarios | support-responder, end-user-docs |
| `testing` | QA, testing de APIs, accesibilidad, performance | api-tester, accessibility-auditor |

## Regla de decision

Si el agente tiene responsabilidad sobre el SISTEMA X-DD mismo (gobernanza, arquitectura
del framework, seguridad del pipeline) → `specialized` o `engineering`.

Si el agente tiene responsabilidad sobre el DOMINIO DEL PROYECTO del usuario → elegir
la categoria del dominio.

Si duda entre dos categorias → elegir la mas especifica.
