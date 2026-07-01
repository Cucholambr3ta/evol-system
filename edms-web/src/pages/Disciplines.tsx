import React, { useState } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { X } from 'lucide-react';

const DISCIPLINES = [
  {
    id: 'SDD', name: 'SDD — Spec-Driven Development', type: 'base',
    phase: 'Todas (transversal)', artifact: 'docs/specs/SPEC.md', skill: 'evol-sdd-spec',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Exige que toda iteración de desarrollo comience con una especificación aprobada, no con código. El código es consecuencia de la spec, no su origen. SDD actúa como columna vertebral del pipeline: ninguna fase avanza sin un artefacto de especificación que haya superado el gate correspondiente. Elimina el drift entre lo que se pidió, lo que se diseñó y lo que se construyó.',
    doD: ['Spec aprobada con HMAC antes de escribir código', 'Artefacto SPEC.md versionado en el repositorio', 'Gate superado con firma del solicitante'],
    file: 'SDD.md'
  },
  {
    id: 'FDD', name: 'FDD — Feature-Driven Development', type: 'base',
    phase: 'Fase 1 + Fase 3', artifact: 'docs/features/FEATURES.md', skill: 'evol-fdd-feature',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Organiza el desarrollo en torno a features atómicas con valor de negocio. Cada feature tiene un identificador único, descripción, criterios de aceptación y estimación. El catálogo FEATURES.md es la fuente de verdad para el plan de sprints.',
    doD: ['FEATURES.md con catálogo completo de features', 'Cada feature tiene ID, descripción y criterios', 'Plan de sprints derivado del catálogo'],
    file: 'FDD.md'
  },
  {
    id: 'DDD', name: 'DDD — Domain-Driven Design', type: 'base',
    phase: 'Fase 2', artifact: 'docs/specs/DOMAIN.md', skill: 'evol-ddd-domain',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Modela el dominio del problema antes de diseñar la solución técnica. Define Bounded Contexts, entidades, value objects, aggregates y el ubiquitous language. DOMAIN.md captura el modelo de dominio aprobado que guía la arquitectura.',
    doD: ['DOMAIN.md con mapa de bounded contexts', 'Ubiquitous language documentado', 'Aggregates y entidades definidos'],
    file: 'DDD.md'
  },
  {
    id: 'BDD', name: 'BDD — Behavior-Driven Development', type: 'base',
    phase: 'Fase 1 + Fase 5', artifact: 'tests/features/*.feature', skill: 'evol-bdd-behavior',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Convierte los criterios de aceptación del negocio en especificaciones ejecutables en lenguaje Gherkin (Given/When/Then). Los escenarios son legibles por el negocio y ejecutables como suite de tests. Integra con Playwright y Cucumber.',
    doD: ['Escenarios Gherkin para todos los criterios de aceptación', 'Suite de tests ejecutable en CI', 'Cobertura de happy path + edge cases'],
    file: 'BDD.md'
  },
  {
    id: 'ATDD', name: 'ATDD — Acceptance Test-Driven Development', type: 'base',
    phase: 'Fase 1 + Fase 5', artifact: 'tests/acceptance/*.acceptance.test.ts', skill: 'evol-atdd-acceptance',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Los tests de aceptación se escriben ANTES del código, junto con el equipo y el solicitante. Define el criterio de Done técnico: el sistema está listo cuando todos los tests de aceptación pasan. Complementa BDD con tests a nivel de integración.',
    doD: ['Tests de aceptación escritos antes del código', 'Todos los tests de aceptación pasan en CI', 'Revisados y aprobados por el solicitante'],
    file: 'ATDD.md'
  },
  {
    id: 'TDD', name: 'TDD — Test-Driven Development', type: 'base',
    phase: 'Fase 4', artifact: 'tests/unit/*.test.ts', skill: 'evol-tdd-unit',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Invierte el orden natural: se escribe primero el test que describe el comportamiento deseado, luego el código mínimo para que pase, luego se refactoriza. El ciclo Rojo-Verde-Refactor garantiza cobertura por diseño, no por auditoría posterior.',
    doD: ['Cobertura de tests ≥80% en código nuevo', 'Ciclo Red-Green-Refactor documentado', 'Sin regresiones en suite existente'],
    file: 'TDD.md'
  },
  {
    id: 'STDD', name: 'STDD — Security-Test-Driven Development', type: 'base',
    phase: 'Fase 4', artifact: 'tests/security/**/*.security.test.ts', skill: 'evol-stdd-security-test',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Aplica TDD al dominio de seguridad: los tests de seguridad se escriben antes de implementar controles. Cubre autenticación, autorización, validación de inputs, OWASP Top 10 y controles de STRIDE. Integra con el modelo de amenazas.',
    doD: ['Tests de seguridad para cada control del modelo de amenazas', 'OWASP Top 10 cubierto en suite', 'Cero CRITICAL en escaneo automatizado'],
    file: 'STDD.md'
  },
  {
    id: 'SecDD', name: 'SecDD — Security-Driven Development', type: 'base',
    phase: 'Fase 5', artifact: '.evol/qa/QA_REPORT.md', skill: 'evol-secdd-security',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Integra controles de seguridad en cada decisión de diseño e implementación, no como capa final. Trabaja sobre el modelo de amenazas STRIDE para asegurar que cada amenaza identificada tiene un control implementado y verificado.',
    doD: ['Todos los controles STRIDE implementados y probados', 'QA_REPORT.md con 0 CRITICAL', 'Revisión de seguridad aprobada por evol-sec'],
    file: 'SecDD.md'
  },
  {
    id: 'THREAT', name: 'Threat-Driven Development', type: 'base',
    phase: 'Fase 2', artifact: 'docs/specs/THREATS.md', skill: 'evol-threat-model',
    badge: 'Núcleo', badgeColor: 'var(--accent)',
    desc: 'Modela las amenazas del sistema usando STRIDE antes de diseñar la arquitectura. Identifica actores maliciosos, superficies de ataque, vectores y controles. THREATS.md es el artefacto que alimenta a SecDD y STDD en fases posteriores.',
    doD: ['THREATS.md con modelo STRIDE completo', 'Superficie de ataque mapeada', 'Controles propuestos por amenaza'],
    file: 'THREAT-DRIVEN.md'
  },
  {
    id: 'ODD_API', name: 'ODD_API — OpenAPI-Driven', type: 'extended',
    phase: 'Fase 2 (Spec)', artifact: 'openapi.yaml', skill: 'evol-odd-api',
    badge: 'Extendida', badgeColor: 'var(--text-tertiary)',
    desc: 'El contrato OpenAPI se diseña antes de implementar la API. openapi.yaml es la fuente de verdad: genera mocks, documentación y tests de contrato. Ningún endpoint se implementa sin estar especificado en el contrato aprobado.',
    doD: ['openapi.yaml válido y aprobado', 'Mocks generados desde el contrato', 'Tests de contrato ejecutables en CI'],
    file: 'ODD_API.md'
  },
  {
    id: 'UXDD', name: 'UXDD — UX-Driven Development', type: 'extended',
    phase: 'Fase 1 (Briefing)', artifact: 'DISCOVERY.md', skill: 'evol-uxdd-ux',
    badge: 'Extendida', badgeColor: 'var(--text-tertiary)',
    desc: 'Integra investigación de usuarios y diseño de experiencia al inicio del pipeline. Valida el problema antes de especificar la solución. DISCOVERY.md captura insights de usuarios, mapas de experiencia y criterios de usabilidad.',
    doD: ['DISCOVERY.md con validación de problema', 'User journeys documentados', 'Criterios de usabilidad en spec'],
    file: 'UXDD.md'
  },
  {
    id: 'ADD', name: 'ADD — Architecture Decision-Driven', type: 'extended',
    phase: 'Fase 2 (Spec)', artifact: 'docs/adr/', skill: 'evol-add-arch',
    badge: 'Extendida', badgeColor: 'var(--text-tertiary)',
    desc: 'Documenta cada decisión arquitectónica significativa como un ADR (Architecture Decision Record) en docs/adr/. Captura el contexto, las alternativas evaluadas, la decisión tomada y las consecuencias esperadas.',
    doD: ['ADR creado para cada decisión arquitectónica significativa', 'Alternativas evaluadas documentadas', 'Consecuencias y trade-offs explícitos'],
    file: 'ADD.md'
  }
];

const PHASE_COLOR: Record<string, string> = {
  'Todas (transversal)': 'var(--accent)',
  'Fase 1': 'var(--status-success-fg)',
  'Fase 2': '#7C3AED',
  'Fase 3': '#D97706',
  'Fase 4': '#0891B2',
  'Fase 5': '#BE185D',
  'Fase 1 + Fase 3': 'var(--status-success-fg)',
  'Fase 1 + Fase 5': 'var(--status-success-fg)',
  'Fase 2 (Spec)': '#7C3AED',
  'Fase 3 (Plan)': '#D97706',
  'Fase 4 (Build)': '#0891B2',
  'Fase 5 (QA)': '#BE185D',
  'Fase 1 (Briefing)': 'var(--status-success-fg)'
};

export const Disciplines: React.FC = () => {
  const { t } = useI18n();
  const [filter, setFilter] = useState<'all' | 'base' | 'extended'>('all');
  const [selectedDiscId, setSelectedDiscId] = useState<string | null>(null);

  const filteredDisc = DISCIPLINES.filter(d => filter === 'all' ? true : d.type === filter);
  const activeDisc = DISCIPLINES.find(d => d.id === selectedDiscId);

  return (
    <>
      <div className="section-header">
        <span className="section-title">{t('nav.disciplines', 'Disciplinas')}</span>
      </div>

      <div className="metrics-row reveal-group metrics-row--centered" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))', marginBottom: '24px' }}>
        <div className="metric">
          <div className="metric-label">{t('disciplines.metric.total', 'Total disciplinas')}</div>
          <div className="metric-value">31</div>
          <div className="metric-delta">9 base + 22 extendidas</div>
        </div>
        <div className="metric">
          <div className="metric-label">{t('disciplines.metric.base', 'Base (núcleo)')}</div>
          <div className="metric-value" style={{ color: 'var(--accent)' }}>9</div>
          <div className="metric-delta">{t('disciplines.metric.baseDesc', 'Todas las fases')}</div>
        </div>
        <div className="metric">
          <div className="metric-label">{t('disciplines.metric.extended', 'Extendidas')}</div>
          <div className="metric-value">22</div>
          <div className="metric-delta">{t('disciplines.metric.extendedDesc', 'Por perfil de proyecto')}</div>
        </div>
        <div className="metric metric-clickable">
          <div className="metric-label">{t('disciplines.metric.skills', 'Skills asociadas')}</div>
          <div className="metric-value" style={{ color: 'var(--accent)' }}>52</div>
          <div className="metric-delta">{t('disciplines.metric.skillsDesc', 'Discipline + Transfer')}</div>
        </div>
      </div>

      <div className="section-header reveal-group" style={{ marginBottom: '16px' }}>
        <span className="section-title">{t('disciplines.all', 'Todas las disciplinas')}</span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className={`btn btn-ghost disc-filter ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>{t('disciplines.filter.all', 'Todas')}</button>
          <button className={`btn btn-ghost disc-filter ${filter === 'base' ? 'active' : ''}`} onClick={() => setFilter('base')}>{t('disciplines.filter.base', 'Base')}</button>
          <button className={`btn btn-ghost disc-filter ${filter === 'extended' ? 'active' : ''}`} onClick={() => setFilter('extended')}>{t('disciplines.filter.extended', 'Extendidas')}</button>
        </div>
      </div>

      <div className="reveal-group" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: '12px', marginBottom: '32px' }}>
        {filteredDisc.map(d => (
          <div 
            key={d.id} 
            className="card disc-card" 
            tabIndex={0} 
            role="button" 
            style={{ cursor: 'pointer', transition: 'border-color var(--transition)' }}
            onClick={() => setSelectedDiscId(d.id)}
          >
            <div className="card-header" style={{ gap: '8px' }}>
              <div>
                <div style={{ fontSize: '11px', fontWeight: 500, color: d.badgeColor, textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: '3px' }}>{d.badge}</div>
                <div className="card-title" style={{ fontSize: '13px' }}>{d.name}</div>
              </div>
              <span style={{ fontSize: '10px', fontWeight: 500, padding: '2px 7px', borderRadius: '10px', background: 'var(--surface-el)', color: PHASE_COLOR[d.phase] || 'var(--text-tertiary)', whiteSpace: 'nowrap', flexShrink: 0 }}>{d.phase}</span>
            </div>
            <div className="card-body" style={{ padding: '12px 16px' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{d.desc}</div>
              <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)', background: 'var(--surface-el)', padding: '2px 6px', borderRadius: '3px' }}>{d.skill}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className={`task-drawer-overlay ${selectedDiscId ? 'open' : ''}`} onClick={() => setSelectedDiscId(null)}>
        <div className="task-drawer" onClick={e => e.stopPropagation()}>
          <div className="task-drawer-header">
            <div>
              <div className="task-drawer-id">{activeDisc?.badge} · {activeDisc?.phase}</div>
              <div className="task-drawer-title">{activeDisc?.name}</div>
            </div>
            <button className="icon-btn" aria-label="Cerrar" onClick={() => setSelectedDiscId(null)}>
              <X size={16} />
            </button>
          </div>

          <div className="task-drawer-body">
            <div className="td-section">
              <div className="td-section-title">{t('disciplines.drawer.description', 'Descripción')}</div>
              <div className="doc-drawer-text">{activeDisc?.desc}</div>
            </div>
            <div className="td-section">
              <div className="td-section-title">{t('disciplines.drawer.phase', 'Fase del pipeline')}</div>
              <div style={{ display: 'inline-block', fontSize: '12px', fontWeight: 500, padding: '3px 10px', borderRadius: '10px', background: 'var(--surface-el)', color: activeDisc ? PHASE_COLOR[activeDisc.phase] : 'inherit' }}>{activeDisc?.phase}</div>
            </div>
            <div className="td-section">
              <div className="td-section-title">{t('disciplines.drawer.artifact', 'Artefacto principal')}</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-primary)', background: 'var(--surface-el)', padding: '6px 10px', borderRadius: 'var(--radius-sm)' }}>{activeDisc?.artifact}</div>
            </div>
            <div className="td-section">
              <div className="td-section-title">{t('disciplines.drawer.dod', 'Definition of Done')}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '4px' }}>
                {activeDisc?.doD.map((item, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    <svg viewBox="0 0 12 12" fill="none" stroke="var(--status-success-fg)" strokeWidth="1.5" style={{ width: '12px', height: '12px', flexShrink: 0, marginTop: '1px' }}><path d="M2 6l3 3 5-5"/></svg>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="td-section">
              <div className="td-section-title">{t('disciplines.drawer.skill', 'Skill Evol-DD')}</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent)', background: 'var(--accent-muted)', padding: '6px 10px', borderRadius: 'var(--radius-sm)' }}>/{activeDisc?.skill}</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
