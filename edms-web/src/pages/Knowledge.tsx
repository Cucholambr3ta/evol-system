import React, { useState } from 'react';
import { ChevronDown, Search } from 'lucide-react';

const GRAPH_DATA = [
  {
    id: 'saas-platform',
    name: 'SaaS Platform',
    children: [
      { id: 'api-gateway', name: 'API Gateway', leaves: ['Rate Limiting', 'Auth Middleware', 'Swagger Spec'], type: 'Dominio', phase: 'QA', tasks: '14 abiertas', agent: 'evol-builder', updated: 'Hoy' },
      { id: 'auth-domain', name: 'Auth Domain', leaves: ['OAuth2 Flow', 'JWT Strategy', 'Session Store'], type: 'Dominio', phase: 'Plan', tasks: '3 abiertas', agent: 'evol-architect', updated: 'Ayer' },
      { id: 'payment-domain', name: 'Payment Domain', leaves: ['Stripe Integration', 'Webhooks'], type: 'Servicio', phase: 'Build', tasks: '8 abiertas', agent: 'evol-builder', updated: 'Hoy' },
      { id: 'analitica', name: 'Analítica', leaves: ['Event Schema', 'Retention Policy'], type: 'Data', phase: 'Spec', tasks: '5 abiertas', agent: 'evol-data', updated: 'Hace 2 días' }
    ]
  },
  {
    id: 'api-gw-v3',
    name: 'API Gateway v3',
    children: [
      { id: 'routing-layer', name: 'Routing Layer', leaves: ['Path Matching', 'Load Balancing'], type: 'Core', phase: 'Build', tasks: '2 abiertas', agent: 'evol-builder', updated: 'Hoy' }
    ]
  }
];

export const Knowledge: React.FC = () => {
  const [filter, setFilter] = useState('');
  const [expandedProjects, setExpandedProjects] = useState<Record<string, boolean>>({'saas-platform': true});
  const [selectedNode, setSelectedNode] = useState(GRAPH_DATA[0].children[0]);

  const toggleProject = (id: string) => {
    setExpandedProjects(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="graph-layout reveal-group">
      {/* Graph canvas */}
      <div className="graph-canvas">
        <div className="graph-search">
          <Search size={14} />
          <input 
            type="text" 
            placeholder="Filtrar nodos..." 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>

        <div className="graph-tree">
          {GRAPH_DATA.map(project => {
            const isExpanded = !!expandedProjects[project.id];
            const visibleChildren = project.children.filter(c => 
              c.name.toLowerCase().includes(filter.toLowerCase()) || 
              c.leaves.some(l => l.toLowerCase().includes(filter.toLowerCase()))
            );

            if (filter && visibleChildren.length === 0 && !project.name.toLowerCase().includes(filter.toLowerCase())) {
              return null;
            }

            return (
              <div key={project.id} className={`graph-project ${isExpanded ? 'expanded' : ''}`}>
                <div className="graph-root" onClick={() => toggleProject(project.id)} style={{ cursor: 'pointer' }}>
                  <ChevronDown size={14} className="graph-root-caret" style={{ transform: isExpanded ? 'none' : 'rotate(-90deg)' }} />
                  <div className="graph-root-dot"></div>
                  {project.name}
                </div>
                {isExpanded && (
                  <div className="graph-children">
                    {visibleChildren.map(child => (
                      <React.Fragment key={child.id}>
                        <div 
                          className={`graph-node-row ${selectedNode.id === child.id ? 'selected' : ''}`}
                          onClick={() => setSelectedNode(child)}
                          style={{ cursor: 'pointer' }}
                        >
                          {child.name}
                        </div>
                        <div className="graph-grandchildren">
                          {child.leaves.map((leaf, idx) => (
                            <div key={idx} className="graph-leaf">{leaf}</div>
                          ))}
                        </div>
                      </React.Fragment>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Node detail panel */}
      <div className="node-detail">
        <div className="detail-card">
          <div className="detail-header">
            <div className="detail-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>{selectedNode.name}</span>
            </div>
            <div className="detail-sub">Nodo seleccionado</div>
          </div>
          <div className="detail-body">
            <div className="detail-row">
              <span className="detail-row-label">Tipo</span>
              <span className="detail-row-value">{selectedNode.type}</span>
            </div>
            <div className="detail-row">
              <span className="detail-row-label">Fase</span>
              <span className={`detail-row-value badge ${selectedNode.phase === 'QA' ? 'warning' : 'neutral'}`}>{selectedNode.phase}</span>
            </div>
            <div className="detail-row">
              <span className="detail-row-label">Tareas</span>
              <span className="detail-row-value">{selectedNode.tasks}</span>
            </div>
            <div className="detail-row">
              <span className="detail-row-label">Agente asignado</span>
              <span className="detail-row-value">{selectedNode.agent}</span>
            </div>
            <div className="detail-row">
              <span className="detail-row-label">Actualizado</span>
              <span className="detail-row-value">{selectedNode.updated}</span>
            </div>
          </div>
        </div>

        <div className="detail-card">
          <div className="detail-header">
            <span className="detail-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>Relaciones</span>
            </span>
          </div>
          <div className="relations-list">
            <div className="relation-item">
              <span className="relation-arrow">--&gt;</span>
              <span className="relation-name">Microservices</span>
              <span className="relation-type">depende de</span>
            </div>
            <div className="relation-item">
              <span className="relation-arrow">--&gt;</span>
              <span className="relation-name">{selectedNode.leaves[0]}</span>
              <span className="relation-type">posee</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
