import React, { useState, useMemo } from 'react';
import { Search, X, FileText, Database, Box, PlayCircle, BookOpen } from 'lucide-react';

const ALL_ITEMS = [
  { id: 's1',  type: 'tareas',    source: 'pipeline', location: 'edms-project-board.html', title: 'Implementar flujo de inicio de sesión OAuth2', context: 'AUTH-98 · Auth Domain · En progreso', badge: 'P0', badgeClass: 'neutral', icon: 'task' },
  { id: 's2',  type: 'memoria',   source: 'chroma',   location: 'edms-navigation-flow.html', title: 'Flujo OAuth2 — Nodo de conocimiento', context: 'Auth Domain · cajón: auth-domain · 12 vectores', badge: 'Conocimiento', badgeClass: 'accent', icon: 'memory' },
  { id: 's3',  type: 'agentes',   source: 'pipeline', location: 'edms-agents.html', title: 'evol-sec — modelo de amenazas OAuth2', context: 'Agente · evol-sec · última actividad hace 2h', badge: 'Activo', badgeClass: 'success', icon: 'agent' },
  { id: 's4',  type: 'historias', source: 'pipeline', location: 'edms-project-board.html', title: 'SaaS Platform — historia OAuth2', context: 'STORY-44 · SaaS Platform · fase Plan', badge: 'Abierto', badgeClass: 'neutral', icon: 'story' },
  { id: 's5',  type: 'memoria',   source: 'ladybug',  location: 'edms-memory.html', title: 'Lección: CSRF en parámetro state de OAuth2', context: 'lecciones.md · Seguridad · 2026-06-03', badge: '', badgeClass: '', icon: 'memory' },
  { id: 's6',  type: 'tareas',    source: 'pipeline', location: 'edms-project-board.html', title: 'Configurar JWT refresh token endpoint', context: 'AUTH-102 · Auth Domain · Por hacer', badge: 'P1', badgeClass: 'neutral', icon: 'task' },
  { id: 's7',  type: 'proyectos', source: 'pipeline', location: 'edms-project-board.html', title: 'SaaS Platform v2 — API Gateway', context: 'Proyecto · 12 features · Fase Build', badge: 'Activo', badgeClass: 'success', icon: 'project' },
  { id: 's8',  type: 'proyectos', source: 'pipeline', location: 'edms-project-board.html', title: 'Auth Domain — sistema de autenticación', context: 'Proyecto · 8 features · Fase QA', badge: 'QA', badgeClass: 'accent', icon: 'project' },
];

const ICONS: Record<string, React.ReactNode> = {
  task: <PlayCircle size={13} />,
  memory: <Database size={13} />,
  agent: <Box size={13} />,
  story: <BookOpen size={13} />,
  project: <FileText size={13} />
};

const TYPE_LABELS: Record<string, string> = { tareas: 'Tarea', memoria: 'Memoria', agentes: 'Agente', historias: 'Historia', proyectos: 'Proyecto' };
const SOURCE_LABELS: Record<string, string> = { pipeline: 'Pipeline EVOL-DD', chroma: 'ChromaDB', ladybug: 'LadybugDB' };

export const GlobalSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [selectedItem, setSelectedItem] = useState<typeof ALL_ITEMS[0] | null>(null);

  const normalize = (s: string) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  const results = useMemo(() => {
    const q = normalize(query.trim());
    return ALL_ITEMS.filter(item => {
      const matchesFilter = filter === 'all' || item.type === filter;
      if (!matchesFilter) return false;
      if (!q) return true;
      return normalize(item.title).includes(q) || normalize(item.context).includes(q);
    });
  }, [query, filter]);

  const highlight = (text: string, q: string) => {
    if (!q.trim()) return text;
    const parts = text.split(new RegExp(`(${q.trim()})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === q.trim().toLowerCase() ? <mark key={i}>{part}</mark> : part
    );
  };

  return (
    <>
      {/* Search input */}
      <div className="search-full" style={{ marginBottom: '16px' }}>
        <Search size={16} />
        <input 
          type="text" 
          placeholder="Buscar proyectos, tareas, agentes, memoria..." 
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <span className="search-kbd">↵ para buscar</span>
      </div>

      {/* Filters */}
      <div className="filter-row" style={{ marginBottom: '24px' }}>
        {['all', 'proyectos', 'tareas', 'memoria', 'agentes', 'historias'].map(f => (
          <span 
            key={f}
            className={`filter-chip ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'all' ? 'Todo' : f.charAt(0).toUpperCase() + f.slice(1)}
          </span>
        ))}
      </div>

      {/* Results */}
      <div className="content-grid reveal-group">
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <div className="card-header">
            <span className="card-title">
              {query.trim() ? `Resultados para "${query.trim()}"` : 'Todos los resultados'}
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span className="section-action">{results.length} coincidencias</span>
            </div>
          </div>
          <div className="results-list">
            {results.length === 0 ? (
              <div className="td-note" style={{ padding: '24px 16px', textAlign: 'center' }}>
                Sin resultados.
              </div>
            ) : (
              results.map(item => (
                <div 
                  key={item.id} 
                  className="result-item" 
                  onClick={() => setSelectedItem(item)}
                  style={{ display: 'flex', alignItems: 'flex-start', gap: '14px', padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)', cursor: 'pointer' }}
                >
                  <div className="result-icon" style={{ width: '28px', height: '28px', borderRadius: '4px', background: 'var(--surface-el)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    {ICONS[item.icon]}
                  </div>
                  <div className="result-body" style={{ flex: 1, minWidth: 0 }}>
                    <div className="result-title" style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '2px' }}>
                      {highlight(item.title, query)}
                    </div>
                    <div className="result-context" style={{ fontSize: '12px', color: 'var(--text-tertiary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.context}
                    </div>
                  </div>
                  <div className="result-meta" style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                    <span className="result-type" style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                      {TYPE_LABELS[item.type]}
                    </span>
                    {item.badge && (
                      <span className={`badge ${item.badgeClass}`}>{item.badge}</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Result detail drawer */}
      {selectedItem && (
        <div className="task-drawer-overlay open" onClick={() => setSelectedItem(null)}>
          <div className="task-drawer" onClick={e => e.stopPropagation()}>
            <div className="task-drawer-header">
              <div>
                <div className="task-drawer-id">{selectedItem.context}</div>
                <div className="task-drawer-title">{selectedItem.title}</div>
              </div>
              <button className="icon-btn" onClick={() => setSelectedItem(null)} title="Cerrar">
                <X size={16} />
              </button>
            </div>
            <div className="task-drawer-body">
              <div className="td-section">
                <div className="td-section-title">Contexto</div>
                <div className="detail-row">
                  <span className="detail-row-label">Fuente</span>
                  <span className="detail-row-value">{SOURCE_LABELS[selectedItem.source]}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-row-label">Tipo</span>
                  <span className="detail-row-value">{TYPE_LABELS[selectedItem.type]}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-row-label">Ubicación</span>
                  <span className="detail-row-value">{selectedItem.location}</span>
                </div>
              </div>
              <div className="td-section">
                <div className="td-section-title">Contenido</div>
                <div className="doc-drawer-text">
                  <h3>{selectedItem.title}</h3>
                  <p>{selectedItem.context}</p>
                  <p><strong>Nota:</strong> Contenido de muestra — implementación final cargará el documento real desde la fuente indexada.</p>
                </div>
              </div>
              <div className="td-section">
                <a className="btn btn-ghost" href="#">Mostrar documento</a>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
