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

| Pantalla | Wireframe | Descripción |
|----------|-----------|-------------|
| Global View | `acuerdos/design/wireframes/edms-global.html` | Knowledge graph, memory health, sectors |
| Project Board | `acuerdos/design/wireframes/edms-project-board.html` | Gantt, Kanban, metrics |
| Navigation Flow | `acuerdos/design/wireframes/edms-navigation-flow.html` | User flow diagram |

## Bloqueante

- [ ] Diseños finales de pantallas (aprobación del usuario)
- [ ] Definición de endpoints exactos (POST bodies, respuestas)
- [ ] Autenticación (si aplica)
