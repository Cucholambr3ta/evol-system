/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useEffect } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { X } from 'lucide-react';

const SUB_DETAIL: Record<string, any> = {
  'proj-saas-platform': {
    kicker: 'SaaS Platform', title: 'Detalle del proyecto',
    rows: [
      { name: 'Fase actual', desc: 'Build · Sprint 12' },
      { name: 'Salud', desc: '88 · estable' },
      { name: 'Último gate firmado', desc: 'QA · hace 2 días' }
    ]
  },
  'proj-api-gateway': {
    kicker: 'API Gateway v3', title: 'Detalle del proyecto',
    rows: [
      { name: 'Fase actual', desc: 'QA · retro bloqueado' },
      { name: 'Salud', desc: '74 · atención' },
      { name: 'Último gate firmado', desc: 'Spec · hace 6 días' }
    ]
  },
  'agent-evol-builder': {
    kicker: 'evol-builder', title: 'Detalle del agente',
    rows: [
      { name: 'Estado', desc: 'Ejecutando · SaaS Platform / Sprint 12' },
      { name: 'Tarea actual', desc: 'TASK-512 · Implementar endpoint de exportación' },
      { name: 'Desde', desc: 'hace 24 min' }
    ]
  },
  'agent-evol-qa': {
    kicker: 'evol-qa', title: 'Detalle del agente',
    rows: [
      { name: 'Estado', desc: 'Ejecutando · API Gateway v3' },
      { name: 'Tarea actual', desc: 'Generación de casos Gherkin desde PLAN.md' },
      { name: 'Desde', desc: 'hace 9 min' }
    ]
  },
  'task-512': {
    kicker: 'TASK-512', title: 'Implementar endpoint de exportación',
    rows: [
      { name: 'Proyecto', desc: 'SaaS Platform · Sprint 12' },
      { name: 'Estado', desc: 'En curso · asignada a evol-builder' },
      { name: 'Criterio de aceptación', desc: 'Dado un usuario autenticado, cuando solicita exportar, entonces recibe un archivo CSV firmado' }
    ]
  },
  'task-204': {
    kicker: 'AUTH-204', title: 'SSO corporativo',
    rows: [
      { name: 'Proyecto', desc: 'Auth Domain' },
      { name: 'Estado', desc: 'Bloqueada · proveedor IdP sin respuesta' },
      { name: 'Criterio de aceptación', desc: 'Dado un dominio corporativo configurado, cuando el usuario inicia sesión, entonces se redirige al IdP' }
    ]
  }
};

const METRIC_DETAIL: Record<string, any> = {
  projects: {
    kicker: 'Proyectos', title: 'Proyectos activos',
    rows: [
      { name: 'SaaS Platform', desc: 'Build · Sprint 12 · salud 88', subKey: 'proj-saas-platform' },
      { name: 'API Gateway v3', desc: 'QA · retro bloqueado · salud 74', subKey: 'proj-api-gateway' },
      { name: 'Auth Domain', desc: 'Spec · gate pendiente de firma' },
      { name: 'Payment Domain', desc: 'Briefing · revisión de cumplimiento PCI' },
      { name: 'Analytics Pipeline', desc: 'Retro · cierre cerrado' }
    ]
  },
  agents: {
    kicker: 'Agentes activos', title: 'Agentes en ejecución',
    rows: [
      { name: 'evol-builder', desc: 'Ejecutando · SaaS Platform / Sprint 12', subKey: 'agent-evol-builder' },
      { name: 'evol-qa', desc: 'Ejecutando · API Gateway v3', subKey: 'agent-evol-qa' },
      { name: 'evol-architect', desc: 'Ejecutando · revisión de ADR-0042' },
      { name: 'evol-sec', desc: 'Ejecutando · pruebas STDD en Auth Domain' }
    ]
  },
  gherkin: {
    kicker: 'Casos Gherkin', title: 'Escenarios definidos',
    rows: [
      { name: 'SaaS Platform', desc: '52 escenarios · CASOS_GHERKIN.md' },
      { name: 'API Gateway v3', desc: '38 escenarios · 4 sin automatizar' },
      { name: 'Auth Domain', desc: '46 escenarios · cobertura 100%' },
      { name: 'Payment Domain', desc: '29 escenarios · en redacción' },
      { name: 'Analytics Pipeline', desc: '19 escenarios · cerrados' }
    ]
  },
  tasks: {
    kicker: 'Tareas', title: 'Tareas del portafolio',
    rows: [
      { name: 'TASK-512 · Endpoint de exportación', desc: 'SaaS Platform · en curso', subKey: 'task-512' },
      { name: 'AUTH-204 · SSO corporativo', desc: 'Auth Domain · bloqueada', subKey: 'task-204' },
      { name: 'GW-077 · Rate limiting v2', desc: 'API Gateway v3 · hallazgo QA pendiente' },
      { name: 'AN-033 · Pipeline de eventos', desc: 'Analytics Pipeline · ADR pendiente' }
    ]
  },
  health: {
    kicker: 'Índice de salud', title: 'Salud por proyecto',
    rows: [
      { name: 'SaaS Platform', desc: '88 · estable' },
      { name: 'API Gateway v3', desc: '74 · atención' },
      { name: 'Auth Domain', desc: '81 · estable' },
      { name: 'Payment Domain', desc: '69 · riesgo' },
      { name: 'Analytics Pipeline', desc: '95 · sano' }
    ]
  },
  velocity: {
    kicker: 'Velocidad', title: 'Puntos por sprint (promedio reciente)',
    rows: [
      { name: 'SaaS Platform', desc: '11 pts/sprint' },
      { name: 'API Gateway v3', desc: '7 pts/sprint' },
      { name: 'Auth Domain', desc: '9 pts/sprint' },
      { name: 'Payment Domain', desc: '5 pts/sprint' },
      { name: 'Analytics Pipeline', desc: '6 pts/sprint' }
    ]
  }
};

export const Dashboard: React.FC = () => {
  const { t } = useI18n();

  const [activeMetricKey, setActiveMetricKey] = useState<string | null>(null);
  const [activeSubKey, setActiveSubKey] = useState<string | null>(null);
  const [activityData, setActivityData] = useState<number[]>(Array.from({ length: 24 }, () => Math.floor(Math.random() * 80) + 20));

  useEffect(() => {
    const interval = setInterval(() => {
      setActivityData(prev => {
        const newData = [...prev.slice(1), Math.floor(Math.random() * 80) + 20];
        return newData;
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const activeMetric = activeMetricKey ? METRIC_DETAIL[activeMetricKey] : null;
  const activeSub = activeSubKey ? SUB_DETAIL[activeSubKey] : null;

  const handleRowClick = (subKey?: string) => {
    if (subKey) {
      setActiveSubKey(subKey);
    }
  };

  return (
    <>
      <div className="metrics-row reveal-group metrics-row--centered">
        {['projects', 'agents', 'gherkin', 'tasks', 'health', 'velocity'].map(key => {
          const labels: Record<string, string> = {
            projects: 'Proyectos', agents: 'Agentes activos', gherkin: 'Casos Gherkin', 
            tasks: 'Tareas', health: 'Índice de salud', velocity: 'Velocidad'
          };
          const vals: Record<string, string> = {
            projects: '24', agents: '18', gherkin: '184', tasks: '921', health: '92', velocity: '38'
          };
          const deltas: Record<string, string> = {
            projects: '+2 este mes', agents: 'En ejecución', gherkin: '+12 este sprint', 
            tasks: '47 bloqueadas', health: 'Bueno', velocity: 'pts / sprint'
          };
          const ups = ['projects', 'gherkin', 'health'];
          return (
            <div key={key} className="metric metric-clickable" tabIndex={0} role="button" onClick={() => setActiveMetricKey(key)}>
              <div className="metric-label">
                <span>{t(`metric.${key}.label`, labels[key])}</span>
                <button className="metric-help" type="button" aria-label="?" onClick={(e) => { e.stopPropagation(); }}>?</button>
              </div>
              <div className="metric-value">{vals[key]}</div>
              <div className={`metric-delta ${ups.includes(key) ? 'up' : ''}`}>{t(`metric.${key}.delta`, deltas[key])}</div>
            </div>
          );
        })}
      </div>

      <div className="card reveal-group" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <span className="card-title" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            Sistema en vivo
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontSize: '11px', fontWeight: 400, color: 'var(--status-success-fg)' }}>
              <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--status-success-fg)' }}></span>
              En vivo
            </span>
          </span>
        </div>
        <div className="card-body" style={{ padding: '8px 16px 16px' }}>
          <div className="live-kpi-grid">
            <div style={{ background: 'var(--surface-el)', borderRadius: 'var(--radius-sm)', padding: '8px 10px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Agentes</div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#4F46E5' }}>18</div>
              <div style={{ fontSize: '10px', color: 'var(--status-success-fg)' }}>activos</div>
            </div>
            <div style={{ background: 'var(--surface-el)', borderRadius: 'var(--radius-sm)', padding: '8px 10px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Tareas</div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#22c55e' }}>921</div>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>47 bloq.</div>
            </div>
            <div style={{ background: 'var(--surface-el)', borderRadius: 'var(--radius-sm)', padding: '8px 10px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Entidades</div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#06B6D4' }}>847</div>
              <div style={{ fontSize: '10px', color: 'var(--status-success-fg)' }}>+23 hoy</div>
            </div>
            <div style={{ background: 'var(--surface-el)', borderRadius: 'var(--radius-sm)', padding: '8px 10px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginBottom: '2px' }}>Gates</div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#D97706' }}>7</div>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>pendientes</div>
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
              Seguimiento en tiempo real
            </div>
            <div style={{ display: 'flex', gap: '3px', alignItems: 'flex-end', height: '48px' }}>
              {activityData.map((val, i) => (
                <div 
                  key={i} 
                  style={{ 
                    flex: 1, 
                    background: '#6d28d9', 
                    borderRadius: '2px', 
                    height: `${val}%`, 
                    minHeight: '2px',
                    opacity: 0.5 + (val / 200),
                    transition: 'height 0.4s ease-out, opacity 0.4s ease-out'
                  }} 
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="content-grid reveal-group">
        <div>
          <div className="card">
            <div className="card-header">
              <span className="card-title">{t('projects.title', 'Proyectos activos')}</span>
              <a className="section-action" href="/projects">{t('common.viewAll', 'Ver todo')}</a>
            </div>
            <div className="project-list">
              <div className="project-row header">
                <span>{t('table.project', 'Proyecto')}</span>
                <span>{t('table.phase', 'Fase')}</span>
                <span>{t('table.progress', 'Progreso')}</span>
                <span>{t('table.status', 'Estado')}</span>
              </div>
              <div className="project-row">
                <span className="project-name">SaaS Platform</span>
                <span className="project-phase">{t('phase.build', 'Construcción')}</span>
                <div className="progress-cell">
                  <div className="progress-bar"><div className="progress-fill" style={{ width: '84%' }}></div></div>
                  <span className="progress-pct">84%</span>
                </div>
                <span className="badge success">{t('status.inProgress', 'En curso')}</span>
              </div>
              <div className="project-row">
                <span className="project-name">API Gateway v3</span>
                <span className="project-phase">{t('phase.qa', 'QA')}</span>
                <div className="progress-cell">
                  <div className="progress-bar"><div className="progress-fill" style={{ width: '61%' }}></div></div>
                  <span className="progress-pct">61%</span>
                </div>
                <span className="badge warning">{t('status.atRisk', 'En riesgo')}</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="card">
            <div className="card-header">
              <span className="card-title">{t('gates.title', 'Próximos gates')}</span>
            </div>
            <div className="milestone-list">
              <div className="milestone-item">
                <span className="milestone-name">{t('gate.saas', 'SaaS Platform → gate QA')}</span>
                <span className="milestone-date">{t('sprint.28', 'Sprint 28')}</span>
              </div>
              <div className="milestone-item">
                <span className="milestone-name">{t('gate.apigw', 'API Gateway v3 → gate Build')}</span>
                <span className="milestone-date">{t('sprint.29', 'Sprint 29')}</span>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="card-header">
              <span className="card-title">{t('activity.pipeline.title', 'Actividad')}</span>
              <span className="section-action">{t('time.min3ago', 'hace 3 min')}</span>
            </div>
            <div className="activity-feed">
              <div className="activity-item">
                <div className="activity-dot"></div>
                <div className="activity-text">
                  <span dangerouslySetInnerHTML={{ __html: t('act.pipe.1', '<strong>evol-qa</strong> movió <a href="#">TSK-208</a> a En revisión gate QA') }}></span>
                </div>
                <div className="activity-time">{t('time.3m', '3m')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Metric Drawer */}
      <div className={`task-drawer-overlay ${activeMetricKey ? 'open' : ''}`} onClick={() => setActiveMetricKey(null)}>
        <div className="task-drawer" onClick={(e) => e.stopPropagation()}>
          <div className="task-drawer-header">
            <div>
              <div className="task-drawer-id">{activeMetric?.kicker || '—'}</div>
              <div className="task-drawer-title">{activeMetric?.title || '—'}</div>
            </div>
            <button className="icon-btn" onClick={() => setActiveMetricKey(null)}>
              <X size={16} />
            </button>
          </div>
          <div className="task-drawer-body">
            <div className="td-section">
              {activeMetric?.rows.map((row: any, i: number) => (
                <div key={i} className={`mcp-row ${row.subKey ? 'clickable' : ''}`} onClick={() => handleRowClick(row.subKey)}>
                  <div className="mcp-row-main">
                    <div className="mcp-row-name">{row.name}</div>
                    <div className="mcp-row-desc">{row.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Sub Metric Drawer */}
      <div className={`task-drawer-overlay ${activeSubKey ? 'open' : ''}`} onClick={() => setActiveSubKey(null)} style={{ zIndex: 1200 }}>
        <div className="task-drawer" onClick={(e) => e.stopPropagation()}>
          <div className="task-drawer-header">
            <div>
              <div className="task-drawer-id">{activeSub?.kicker || '—'}</div>
              <div className="task-drawer-title">{activeSub?.title || '—'}</div>
            </div>
            <button className="icon-btn" onClick={() => setActiveSubKey(null)}>
              <X size={16} />
            </button>
          </div>
          <div className="task-drawer-body">
            <div className="td-section">
              {activeSub?.rows.map((row: any, i: number) => (
                <div key={i} className="mcp-row">
                  <div className="mcp-row-main">
                    <div className="mcp-row-name">{row.name}</div>
                    <div className="mcp-row-desc">{row.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
