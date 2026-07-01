import React, { useState } from 'react';

export const Projects: React.FC = () => {
  const [selectedProject, setSelectedProject] = useState('saas-platform');
  const [selectedSprint, setSelectedSprint] = useState('28');

  return (
    <>
      {/* Metrics row */}
      <div className="metrics-row reveal-group metrics-row--centered" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', marginBottom: '20px' }}>
        <div className="metric metric-clickable" tabIndex={0} role="button">
          <div className="metric-label">Índice de riesgo<button className="metric-help" type="button">?</button></div>
          <div className="metric-value">14</div>
          <div className="metric-delta down">2 críticos</div>
        </div>
        <div className="metric metric-clickable" tabIndex={0} role="button">
          <div className="metric-label">Elementos bloqueados<button className="metric-help" type="button">?</button></div>
          <div className="metric-value">47</div>
          <div className="metric-delta down">Requiere atención</div>
        </div>
        <div className="metric metric-clickable" tabIndex={0} role="button">
          <div className="metric-label">En revisión<button className="metric-help" type="button">?</button></div>
          <div className="metric-value">23</div>
          <div className="metric-delta">Esta iteración</div>
        </div>
        <div className="metric metric-clickable" tabIndex={0} role="button">
          <div className="metric-label">Completadas<button className="metric-help" type="button">?</button></div>
          <div className="metric-value">312</div>
          <div className="metric-delta up">+28 esta semana</div>
        </div>
      </div>

      {/* Pipeline gateado */}
      <div className="section-header">
        <span className="section-title">Posición en el Gated Pipeline</span>
        <span className="section-action">6 fases · gate HMAC-SHA256 obligatorio entre cada una</span>
      </div>
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="gantt-wrapper">
          <table className="gantt-table">
            <thead>
              <tr>
                <th style={{ minWidth: '160px' }}>Proyecto</th>
                <th className="month"><span className="gantt-phase-head"><span>Briefing</span></span></th>
                <th className="month"><span className="gantt-phase-head"><span>Spec</span></span></th>
                <th className="month"><span className="gantt-phase-head"><span>Plan</span></span></th>
                <th className="month"><span className="gantt-phase-head"><span>Build</span></span></th>
                <th className="month"><span className="gantt-phase-head"><span>QA</span></span></th>
                <th className="month"><span className="gantt-phase-head"><span>Retro</span></span></th>
              </tr>
            </thead>
            <tbody>
              <tr className="gantt-row">
                <td className="gantt-label">
                  SaaS Platform<br/><span className="gantt-phase">Gate Build → QA: en curso</span>
                </td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar" style={{ width: '84%' }}></div></td>
                <td className="gantt-cell"></td>
                <td className="gantt-cell"></td>
              </tr>
              <tr className="gantt-row">
                <td className="gantt-label">
                  API Gateway v3<br/><span className="gantt-phase">Gate QA → Retro: bloqueado</span>
                </td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar warning" style={{ width: '61%' }}></div></td>
                <td className="gantt-cell"></td>
              </tr>
              <tr className="gantt-row">
                <td className="gantt-label">
                  Auth Domain<br/><span className="gantt-phase">Gate Spec → Plan: pendiente</span>
                </td>
                <td className="gantt-cell"><div className="gantt-bar success" style={{ width: '100%' }}></div></td>
                <td className="gantt-cell"><div className="gantt-bar muted" style={{ width: '32%' }}></div></td>
                <td className="gantt-cell"></td>
                <td className="gantt-cell"></td>
                <td className="gantt-cell"></td>
                <td className="gantt-cell"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Selector de proyecto */}
      <div className="section-header">
        <div className="board-header">
          <span className="section-title">Proyecto seleccionado</span>
          <select className="project-select" value={selectedProject} onChange={e => setSelectedProject(e.target.value)}>
            <option value="saas-platform">SaaS Platform</option>
            <option value="api-gateway">API Gateway v3</option>
            <option value="auth-domain">Auth Domain</option>
            <option value="analytics-pipeline">Analytics Pipeline</option>
          </select>
        </div>
        <span className="section-action">GitFlow + sprint activo se filtran por este proyecto</span>
      </div>

      {/* GitFlow branch history */}
      <div className="section-header">
        <span className="section-title">GitFlow — Historial de ramas</span>
        <span className="section-action">SaaS Platform · últimos 12 commits</span>
      </div>
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="gitflow-wrapper">
          <div className="gitflow-tree-col">
            <svg className="gitflow-graph" viewBox="0 0 230 220" preserveAspectRatio="xMidYMid meet">
              <line className="gf-lane main" x1="36"  y1="14" x2="36"  y2="216"/>
              <line className="gf-lane develop" x1="76"  y1="34" x2="76"  y2="196"/>
              <line className="gf-lane feature" x1="116" y1="74" x2="116" y2="136"/>
              <line className="gf-lane release" x1="156" y1="114" x2="156" y2="176"/>
              <path className="gf-merge" d="M116,134 C116,150 76,150 76,164"/>
              <path className="gf-merge" d="M76,76 C76,90 116,90 116,104"/>
              <path className="gf-merge" d="M76,116 C76,130 156,130 156,144"/>
              <path className="gf-merge accent" d="M156,174 C156,190 36,190 36,204"/>
              <path className="gf-merge accent" d="M76,166 C76,180 36,180 36,194"/>
              
              <circle className="gf-dot main" cx="36" cy="24"  r="4"/>
              <circle className="gf-dot main" cx="36" cy="194" r="4"/>
              <circle className="gf-dot main accent" cx="36" cy="204" r="5"/>
              <circle className="gf-dot develop" cx="76" cy="44"  r="4"/>
              <circle className="gf-dot develop" cx="76" cy="76"  r="4"/>
              <circle className="gf-dot develop" cx="76" cy="116" r="4"/>
              <circle className="gf-dot develop" cx="76" cy="146" r="4"/>
              <circle className="gf-dot develop accent" cx="76" cy="166" r="5"/>
              <circle className="gf-dot feature" cx="116" cy="84"  r="4"/>
              <circle className="gf-dot feature" cx="116" cy="106" r="4"/>
              <circle className="gf-dot feature" cx="116" cy="124" r="4"/>
              <circle className="gf-dot feature accent" cx="116" cy="134" r="5"/>
              <circle className="gf-dot release" cx="156" cy="124" r="4"/>
              <circle className="gf-dot release" cx="156" cy="156" r="4"/>
              <circle className="gf-dot release accent" cx="156" cy="174" r="5"/>
            </svg>
            <div className="gf-branch-legend">
              <span className="gf-branch-item"><span className="gf-dot-sm main"></span>main</span>
              <span className="gf-branch-item"><span className="gf-dot-sm develop"></span>develop</span>
              <span className="gf-branch-item"><span className="gf-dot-sm feature"></span>feature/*</span>
              <span className="gf-branch-item"><span className="gf-dot-sm release"></span>release/*</span>
            </div>
          </div>
          <div className="gitflow-log">
            <div className="gf-entry main"><span className="gf-dot-sm main"></span><div><div className="gf-msg">Merge release/v0.6.0 a main</div><div className="gf-meta"><span className="gf-sha">58ea5c5</span> · main · hace 2h</div></div></div>
            <div className="gf-entry release"><span className="gf-dot-sm release"></span><div><div className="gf-msg">release: bump VERSION to 0.6.0</div><div className="gf-meta"><span className="gf-sha">b6b288c</span> · release/v0.6.0 · hace 4h</div></div></div>
            <div className="gf-entry develop"><span className="gf-dot-sm develop"></span><div><div className="gf-msg">Merge feature/edms-memory-system a develop</div><div className="gf-meta"><span className="gf-sha">174cfd0</span> · develop · hace 6h</div></div></div>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="section-header">
        <div className="board-header">
          <span className="section-title">Sprint generado por el pipeline — {selectedProject}</span>
          <select className="project-select" value={selectedSprint} onChange={e => setSelectedSprint(e.target.value)}>
            <option value="28">Sprint 28</option>
            <option value="27">Sprint 27</option>
          </select>
        </div>
        <span className="section-action">Generado en Fase Plan a partir de PLAN.md · 10 tareas</span>
      </div>

      <div className="kanban-wrapper">
        <div className="kanban-board reveal-group">
          
          <div className="kanban-column">
            <div className="kanban-col-header">
              <div className="kanban-col-title"><span>Definidas en Plan</span><span className="col-count">3</span></div>
            </div>
            <div className="kanban-cards">
              <div className="kanban-card">
                <div className="card-id">API-88</div>
                <div className="card-title">Definir estrategia de límite de tasa</div>
                <div className="card-meta">
                  <div className="card-tags"><span className="card-tag">SDD</span><span className="card-tag">DDD</span></div>
                  <span className="badge neutral">PLAN.md</span>
                </div>
              </div>
            </div>
          </div>

          <div className="kanban-column">
            <div className="kanban-col-header">
              <div className="kanban-col-title"><span>En construcción</span><span className="col-count">2</span></div>
            </div>
            <div className="kanban-cards">
              <div className="kanban-card">
                <div className="card-id">AUTH-102</div>
                <div className="card-title">Refactorizar clase UserValidator</div>
                <div className="card-meta">
                  <div className="card-tags"><span className="card-tag">DDD</span><span className="card-tag">TDD</span></div>
                  <span className="badge accent">Fase Build</span>
                </div>
              </div>
            </div>
          </div>

          <div className="kanban-column">
            <div className="kanban-col-header">
              <div className="kanban-col-title"><span>En revisión — gate QA</span><span className="col-count">3</span></div>
            </div>
            <div className="kanban-cards">
              <div className="kanban-card">
                <div className="card-id">AUTH-98</div>
                <div className="card-title">Implementar flujo OAuth2</div>
                <div className="card-meta">
                  <div className="card-tags"><span className="card-tag">SDD</span><span className="card-tag">SecDD</span></div>
                  <span className="badge accent">Gate: en curso</span>
                </div>
              </div>
            </div>
          </div>

          <div className="kanban-column">
            <div className="kanban-col-header">
              <div className="kanban-col-title"><span>Cerradas — Retro</span><span className="col-count">2</span></div>
            </div>
            <div className="kanban-cards">
              <div className="kanban-card done">
                <div className="card-id">DB-12</div>
                <div className="card-title">Migración de esquema</div>
                <div className="card-meta">
                  <div className="card-tags"><span className="card-tag">DDD</span><span className="card-tag">IaC-Driven</span></div>
                  <span className="badge success">Gate: firmado</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </>
  );
};
