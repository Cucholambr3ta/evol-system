# EDMS UI — Stack Técnico

**Branch:** `feature/edms-ui`
**Estado:** Pendiente diseños de pantallas

## Stack

| Capa | Tecnología | Versión |
|------|-----------|---------|
| **Frontend** | React | 19.x |
| **Styling** | Tailwind CSS | 4.x |
| **Backend API** | FastAPI | 0.115+ |
| **Graph DB** | NetworkX | 3.x |
| **Vector DB** | ChromaDB | 1.5.x |
| **State** | SQLite | stdlib |

## API Endpoints (diseño preliminar)

```
GET  /api/v1/edms/stats              → Tier stats, memory health
GET  /api/v1/edms/search?q=...       → Vector search results
GET  /api/v1/edms/graph              → Knowledge graph nodes + relations
GET  /api/v1/edms/decisions          → Decisiones recientes
GET  /api/v1/edms/lessons            → Lecciones pendientes/aplicadas
GET  /api/v1/edms/health             → Memory health metrics
POST /api/v1/edms/index              → Indexar nuevo item
POST /api/v1/edms/compact            → Ejecutar compactación
GET  /api/v1/compliance/report       → Sprint compliance report
```

## Pantallas (wireframes de referencia)

Wireframes activos: perfil `enterprise-minimal` (Linear/Vercel/GitHub Projects),
generados con la skill `evol-frontend-design` + capa de motion `evol-remotion`.
Viven en `acuerdos/design/wireframes/propuesta/`. Design tokens en `propuesta/styles.css`.

| Pantalla | Wireframe | Descripción |
|----------|-----------|-------------|
| Dashboard | `acuerdos/design/wireframes/propuesta/index.html` | Métricas ejecutivas, proyectos, milestones, activity |
| Project Board | `acuerdos/design/wireframes/propuesta/edms-project-board.html` | Gantt monocromático, Kanban estilo Linear, metrics |
| Knowledge Graph | `acuerdos/design/wireframes/propuesta/edms-navigation-flow.html` | Grafo canvas + node detail panel |
| Search / Global | `acuerdos/design/wireframes/propuesta/edms-global.html` | Búsqueda con highlight, filter chips, activity |

Sistema de diseño:

- `aesthetic_profile: enterprise-minimal` (en `evol.profile.yml`)
- Paleta dark-first `#0F1115` + acento único `#4F46E5`; light theme persistente (localStorage)
- Tipografía Geist/Inter; iconografía SVG monocromática (sin emojis)
- Motion CSS sobrio: reveals escalonados (IntersectionObserver), transiciones 150-180ms,
  `prefers-reduced-motion` respetado. Remotion-ready para la migración a React 19.

## Bloqueante

- [ ] Diseños finales de pantallas (aprobación del usuario)
- [ ] Definición de endpoints exactos (POST bodies, respuestas)
- [ ] Autenticación (si aplica)

## Code Graph API Routes (pendiente de implementar)

El dashboard necesita endpoints para exponer el code graph indexer:

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/api/v1/code/stats` | GET | Estadisticas del code graph (nodes, relations, last index) |
| `/api/v1/code/impact/<symbol>` | GET | Analisis de impacto de un simbolo |
| `/api/v1/code/trace/<entry>` | GET | Trazado de ejecucion desde un punto de entrada |
| `/api/v1/code/query/<pattern>` | GET | Busqueda de simbolos por patron |
| `/api/v1/code/index` | POST | Trigger indexacion completa |
| `/api/v1/code/index/incremental` | POST | Trigger indexacion incremental |

**Nota:** Estos endpoints requieren `evol_code_indexer.py` y estan disponibles solo cuando `[code]` esta instalado.
