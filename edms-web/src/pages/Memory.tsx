import React, { useState } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { RefreshCw } from 'lucide-react';

export const Memory: React.FC = () => {
  const { t } = useI18n();
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);

  const toggleTooltip = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setActiveTooltip(activeTooltip === id ? null : id);
  };

  return (
    <div onClick={() => setActiveTooltip(null)}>
      <div className="section-header">
        <span className="section-title">{t('nav.memory', 'Memoria')}</span>
      </div>

      <div className="metrics-row reveal-group metrics-row--centered" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', marginBottom: '24px' }}>
        <div className="metric">
          <div className="metric-label">
            <span>{t('mem.totalItems.label', 'Elementos totales')}</span>
            <button className="metric-help" onClick={(e) => toggleTooltip('total', e)}>?</button>
          </div>
          <div className="metric-value">105</div>
          <div className="metric-delta up">{t('mem.totalItems.delta', '+12 hoy')}</div>
          {activeTooltip === 'total' && (
            <div className="metric-tooltip open" style={{ top: 'calc(100% + 4px)', left: '16px', right: '16px' }}>
              Suma de elementos almacenados en todos los cajones de memoria, sin importar su nivel de consolidación actual.
            </div>
          )}
        </div>
        <div className="metric">
          <div className="metric-label">
            <span>{t('mem.drawers.label', 'Cajones')}</span>
            <button className="metric-help" onClick={(e) => toggleTooltip('drawers', e)}>?</button>
          </div>
          <div className="metric-value">63</div>
          <div className="metric-delta">{t('mem.drawers.delta', 'Espacios de nombres')}</div>
          {activeTooltip === 'drawers' && (
            <div className="metric-tooltip open" style={{ top: 'calc(100% + 4px)', left: '16px', right: '16px' }}>
              Espacios de nombres aislados (uno por proyecto, dominio o sprint) que agrupan elementos de memoria relacionados.
            </div>
          )}
        </div>
        <div className="metric">
          <div className="metric-label">
            <span>{t('mem.graphNodes.label', 'Nodos del grafo')}</span>
            <button className="metric-help" onClick={(e) => toggleTooltip('nodes', e)}>?</button>
          </div>
          <div className="metric-value">261</div>
          <div className="metric-delta">{t('mem.graphNodes.delta', '+ relaciones')}</div>
          {activeTooltip === 'nodes' && (
            <div className="metric-tooltip open" style={{ top: 'calc(100% + 4px)', left: '16px', right: '16px' }}>
              Entidades indexadas en el grafo de conocimiento (LadybugDB) y sus relaciones — base del análisis de impacto.
            </div>
          )}
        </div>
        <div className="metric">
          <div className="metric-label">
            <span>{t('mem.vectors.label', 'Vectores')}</span>
            <button className="metric-help" onClick={(e) => toggleTooltip('vectors', e)}>?</button>
          </div>
          <div className="metric-value">2,841</div>
          <div className="metric-delta">ChromaDB</div>
          {activeTooltip === 'vectors' && (
            <div className="metric-tooltip open" style={{ top: 'calc(100% + 4px)', left: '16px', right: '16px' }}>
              Embeddings indexados en ChromaDB para búsqueda semántica de elementos de memoria por similitud.
            </div>
          )}
        </div>
      </div>

      <div className="section-header">
        <span className="section-title">{t('mem.consolidationLevels', 'Niveles de consolidación')}</span>
        <button className="btn btn-ghost" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <RefreshCw size={14} />
          {t('mem.runCompaction', 'Ejecutar compactación')}
        </button>
      </div>

      <div className="card reveal-group" style={{ marginBottom: '24px' }}>
        <div className="card-body">
          <div style={{ display: 'flex', alignItems: 'stretch', gap: '22px', flexWrap: 'wrap', textAlign: 'center' }}>
            {['Crudo', 'Comprimido', 'Memoria', 'Conocimiento', 'Archivado'].map((tier, i) => (
              <div key={tier} style={{ flex: 1, minWidth: '130px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '14px', position: 'relative' }}>
                {i > 0 && <span style={{ position: 'absolute', left: '-15px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }}>→</span>}
                <div style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '6px' }}>{tier}</div>
                <div style={{ fontSize: '22px', fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                  {[38, 24, 21, 18, 4][i]}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '6px' }}>
                  {['decae 1–7d', 'decae 14d', 'decae 30–90d', 'decae 180d', 'sin decaimiento'][i]}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="section-header" style={{ marginTop: '8px' }}>
        <span className="section-title">{t('mem.engine.title', 'Motor de Memoria')}</span>
      </div>

      <div className="reveal-group" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(250px,1fr))', gap: '16px' }}>
          
          <div className="card">
            <div className="card-header">
              <span className="card-title">{t('mem.engine.entities', 'Extracción de Entidades')}</span>
            </div>
            <div className="card-body" style={{ padding: '0 16px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ padding: '8px 0', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
                <div><div style={{ fontSize: '12px', fontWeight: 500 }}>SaaS Platform</div><div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Proyecto · 98%</div></div>
                <span className="badge" style={{ background: 'var(--accent-muted)', color: 'var(--accent)' }}>SPEC.md</span>
              </div>
              <div style={{ padding: '8px 0', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
                <div><div style={{ fontSize: '12px', fontWeight: 500 }}>evol-builder</div><div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Agente · 95%</div></div>
                <span className="badge" style={{ background: 'var(--accent-muted)', color: 'var(--accent)' }}>memoria.md</span>
              </div>
              <div style={{ padding: '8px 0', display: 'flex', justifyContent: 'space-between' }}>
                <div><div style={{ fontSize: '12px', fontWeight: 500 }}>Rate limiting</div><div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Decisión · 92%</div></div>
                <span className="badge" style={{ background: 'var(--accent-muted)', color: 'var(--accent)' }}>ADR-001</span>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">{t('mem.engine.reflections', 'Reflexiones')}</span>
            </div>
            <div className="card-body" style={{ padding: '0 16px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ padding: '10px', background: 'var(--surface-el)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent)' }}>
                <div style={{ fontSize: '10px', color: 'var(--accent)', fontWeight: 500, marginBottom: '4px', textTransform: 'uppercase' }}>patrón</div>
                <div style={{ fontSize: '12px', color: 'var(--text-primary)' }}>Patrón de rate limiting se repite en 3 proyectos</div>
                <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '4px' }}>Basado en 5 elementos · 87%</div>
              </div>
              <div style={{ padding: '10px', background: 'var(--surface-el)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--status-success-fg)' }}>
                <div style={{ fontSize: '10px', color: 'var(--status-success-fg)', fontWeight: 500, marginBottom: '4px', textTransform: 'uppercase' }}>oportunidad</div>
                <div style={{ fontSize: '12px', color: 'var(--text-primary)' }}>Oportunidad de reutilizar módulo de auth</div>
                <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '4px' }}>Basado en 4 elementos · 79%</div>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};
