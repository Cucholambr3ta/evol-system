import React, { useState } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { X, BarChart2, TrendingUp, Activity, AlertTriangle } from 'lucide-react';

export const Analytics: React.FC = () => {
  const { t } = useI18n();
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);

  const openDrawer = (metric: string) => {
    setSelectedMetric(metric);
  };

  const closeDrawer = () => {
    setSelectedMetric(null);
  };

  const drawerContent: Record<string, { title: string; subtitle: string; icon: React.ReactNode }> = {
    'velocity': { title: 'Velocidad — detalle por proyecto', subtitle: 'Puntos completados por sprint (S23–S28)', icon: <TrendingUp size={24} color="var(--accent)" /> },
    'health': { title: 'Índice de salud — evolución', subtitle: 'Índice semanal por proyecto (S23–S28)', icon: <Activity size={24} color="var(--status-success-fg)" /> },
    'risk': { title: 'Índice de riesgo — evolución', subtitle: 'Nivel de riesgo acumulado global', icon: <AlertTriangle size={24} color="var(--status-warning-fg)" /> },
    'blocked': { title: 'Elementos bloqueados', subtitle: 'Tickets bloqueados acumulados por sprint', icon: <X size={24} color="var(--status-error-fg)" /> },
    'velocity-sprint': { title: 'Velocidad por sprint', subtitle: 'Puntos por sprint — total acumulado 5 proyectos', icon: <BarChart2 size={24} color="var(--accent)" /> },
    'health-trend': { title: 'Tendencia de salud', subtitle: 'Promedio índice salud — últimos 6 sprints', icon: <Activity size={24} color="var(--status-success-fg)" /> },
    'burndown': { title: 'Burndown del sprint 28', subtitle: 'Trabajo restante: real vs ideal', icon: <TrendingUp size={24} color="var(--text-tertiary)" /> },
    'risk-time': { title: 'Riesgo en el tiempo', subtitle: 'Tickets en riesgo — 4 semanas', icon: <AlertTriangle size={24} color="var(--status-warning-fg)" /> }
  };

  return (
    <>
      <div className="section-header">
        <span className="section-title">{t('nav.analytics', 'Analítica')}</span>
      </div>

      <div className="metrics-row reveal-group metrics-row--centered" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', marginBottom: '24px' }}>
        <div className="metric metric-clickable" tabIndex={0} role="button" onClick={() => openDrawer('velocity')}>
          <div className="metric-label">{t('metric.velocity.label', 'Velocidad')}</div>
          <div className="metric-value">38</div>
          <div className="metric-delta up">{t('an.velocity.delta', '+4 vs anterior')}</div>
        </div>
        <div className="metric metric-clickable" tabIndex={0} role="button" onClick={() => openDrawer('health')}>
          <div className="metric-label">{t('metric.health.label', 'Índice de salud')}</div>
          <div className="metric-value">92</div>
          <div className="metric-delta up">{t('metric.health.delta', 'Bueno')}</div>
        </div>
        <div className="metric metric-clickable" tabIndex={0} role="button" onClick={() => openDrawer('risk')}>
          <div className="metric-label">{t('an.riskIndex.label', 'Índice de riesgo')}</div>
          <div className="metric-value">14</div>
          <div className="metric-delta down">{t('an.riskIndex.delta', '2 críticos')}</div>
        </div>
        <div className="metric metric-clickable" tabIndex={0} role="button" onClick={() => openDrawer('blocked')}>
          <div className="metric-label">{t('an.blocked.label', 'Elementos bloqueados')}</div>
          <div className="metric-value">47</div>
          <div className="metric-delta down">{t('an.blocked.delta', 'Requiere atención')}</div>
        </div>
      </div>

      <div className="content-grid reveal-group" style={{ marginBottom: '16px' }}>
        <div className="card chart-clickable" style={{ cursor: 'pointer', transition: 'border-color var(--transition)' }} onClick={() => openDrawer('velocity-sprint')} tabIndex={0}>
          <div className="card-header">
            <span className="card-title">{t('an.velocityChart.title', 'Velocidad por sprint')}</span>
            <span className="section-action">{t('an.last6Sprints', 'Últimos 6 sprints')}</span>
          </div>
          <div className="card-body" style={{ padding: '0 12px 12px', height: '130px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '80px', width: '100%', justifyContent: 'center' }}>
               {[40, 50, 60, 55, 70, 90].map((h, i) => <div key={i} style={{ width: '24px', height: `${h}%`, background: i === 5 ? 'var(--accent)' : 'var(--accent-muted)', borderRadius: '2px 2px 0 0' }}></div>)}
             </div>
          </div>
        </div>

        <div className="card chart-clickable" style={{ cursor: 'pointer', transition: 'border-color var(--transition)' }} onClick={() => openDrawer('health-trend')} tabIndex={0}>
          <div className="card-header">
            <span className="card-title">{t('an.healthTrend.title', 'Tendencia de salud')}</span>
            <span className="section-action">{t('an.last30Days', '30 días')}</span>
          </div>
          <div className="card-body" style={{ padding: '0 12px 12px', height: '130px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <svg width="100%" height="80" viewBox="0 0 200 80" preserveAspectRatio="none">
               <path d="M0,70 L40,65 L80,55 L120,60 L160,40 L200,20 L200,80 L0,80 Z" fill="var(--status-success-bg)" opacity="0.5"/>
               <path d="M0,70 L40,65 L80,55 L120,60 L160,40 L200,20" fill="none" stroke="var(--status-success-fg)" strokeWidth="2"/>
             </svg>
          </div>
        </div>
      </div>

      <div className="content-grid reveal-group" style={{ marginBottom: '32px' }}>
        <div className="card chart-clickable" style={{ cursor: 'pointer', transition: 'border-color var(--transition)' }} onClick={() => openDrawer('burndown')} tabIndex={0}>
          <div className="card-header">
            <span className="card-title">{t('an.burndown.title', 'Burndown del sprint')}</span>
            <span className="section-action">{t('sprint.28', 'Sprint 28')}</span>
          </div>
          <div className="card-body" style={{ padding: '0 12px 12px', height: '130px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="100%" height="80" viewBox="0 0 200 80" preserveAspectRatio="none">
              <path d="M0,10 L200,70" fill="none" stroke="var(--text-tertiary)" strokeWidth="2" strokeDasharray="5,5"/>
              <path d="M0,10 L30,20 L60,25 L90,40 L120,45 L150,65" fill="none" stroke="var(--accent)" strokeWidth="2"/>
            </svg>
          </div>
        </div>

        <div className="card chart-clickable" style={{ cursor: 'pointer', transition: 'border-color var(--transition)' }} onClick={() => openDrawer('risk-time')} tabIndex={0}>
          <div className="card-header">
            <span className="card-title">{t('an.riskOverTime.title', 'Riesgo en el tiempo')}</span>
            <span className="section-action">{t('an.last30Days', '30 días')}</span>
          </div>
          <div className="card-body" style={{ padding: '0 12px 12px', height: '130px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <div style={{ display: 'flex', alignItems: 'flex-end', gap: '16px', height: '80px', width: '100%', justifyContent: 'center' }}>
               {[40, 50, 60, 55].map((h, i) => (
                 <div key={i} style={{ width: '20px', height: `${h}%`, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
                   <div style={{ width: '100%', height: '30%', background: 'var(--status-error-fg)', borderRadius: '2px 2px 0 0' }}></div>
                   <div style={{ width: '100%', height: '70%', background: 'var(--status-warning-fg)' }}></div>
                 </div>
               ))}
             </div>
          </div>
        </div>
      </div>

      <div className={`task-drawer-overlay ${selectedMetric ? 'open' : ''}`} onClick={closeDrawer}>
        <div className="task-drawer" onClick={e => e.stopPropagation()}>
          <div className="task-drawer-header">
            <div>
              <div className="task-drawer-title">{selectedMetric ? drawerContent[selectedMetric]?.title : 'Detalle'}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '4px' }}>{selectedMetric && drawerContent[selectedMetric]?.subtitle}</div>
            </div>
            <button className="icon-btn" aria-label="Cerrar" onClick={closeDrawer}>
              <X size={16} />
            </button>
          </div>
          <div className="task-drawer-body" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', opacity: 0.5 }}>
            {selectedMetric && drawerContent[selectedMetric]?.icon}
            <div style={{ marginTop: '16px', fontSize: '13px' }}>[ Gráfico de análisis interactivo aquí ]</div>
          </div>
        </div>
      </div>
    </>
  );
};
