/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { X } from 'lucide-react';

const AGENTS = [
  { id: 'evol-architect', name: 'evol-architect', spec: 'Arquitectura / ADRs', status: 'Activo', runs: 142, last: '2m', dot: 'on' },
  { id: 'evol-builder', name: 'evol-builder', spec: 'Implementación / TDD', status: 'Activo', runs: 318, last: '1m', dot: 'on' },
  { id: 'evol-qa', name: 'evol-qa', spec: 'Pruebas / BDD', status: 'Activo', runs: 201, last: '4m', dot: 'on' },
  { id: 'evol-sec', name: 'evol-sec', spec: 'Seguridad / STRIDE', status: 'Activo', runs: 88, last: '12m', dot: 'on' },
  { id: 'evol-orchestrator', name: 'evol-orchestrator', spec: 'Coordinación multi-agente', status: 'Activo', runs: 76, last: '30s', dot: 'on' },
  { id: 'evol-devops', name: 'evol-devops', spec: 'CI/CD / pipelines', status: 'Inactivo', runs: 64, last: '1h', dot: 'idle' },
  { id: 'evol-domain', name: 'evol-domain', spec: 'DDD / contextos acotados', status: 'Inactivo', runs: 52, last: '2h', dot: 'idle' },
  { id: 'evol-doc', name: 'evol-doc', spec: 'Documentación', status: 'Inactivo', runs: 97, last: '3h', dot: 'idle' },
  { id: 'evol-ux', name: 'evol-ux', spec: 'Descubrimiento / UX', status: 'Inactivo', runs: 41, last: '5h', dot: 'idle' },
  { id: 'evol-data', name: 'evol-data', spec: 'Ingeniería de datos', status: 'Inactivo', runs: 28, last: '1d', dot: 'idle' },
  { id: 'evol-reviewer', name: 'evol-reviewer', spec: 'Revisión de código', status: 'Inactivo', runs: 133, last: '6h', dot: 'idle' },
  { id: 'evol-pm', name: 'evol-pm', spec: 'Proyecto / sprints', status: 'Inactivo', runs: 59, last: '4h', dot: 'idle' },
  { id: 'evol-release', name: 'evol-release', spec: 'Releases / CHANGELOG', status: 'Inactivo', runs: 22, last: '1d', dot: 'idle' },
  { id: 'evol-analyst', name: 'evol-analyst', spec: 'Impacto / radio de alcance', status: 'Inactivo', runs: 37, last: '8h', dot: 'idle' },
  { id: 'evol-researcher', name: 'evol-researcher', spec: 'Investigación autónoma', status: 'Inactivo', runs: 45, last: '2d', dot: 'idle' },
  { id: 'evol-agent-factory', name: 'evol-agent-factory', spec: 'Agentes efímeros', status: 'Inactivo', runs: 14, last: '3d', dot: 'idle' },
  { id: 'evol-auditor', name: 'evol-auditor', spec: 'Auditoría de fase', status: 'Inactivo', runs: 31, last: '1d', dot: 'idle' },
  { id: 'evol-compliance-auditor', name: 'evol-compliance-auditor', spec: 'Auditoría de cumplimiento', status: 'Inactivo', runs: 19, last: '2d', dot: 'idle' },
];

const AGENT_DESC: Record<string, any> = {
  'evol-architect': {
    desc: 'Diseña la arquitectura física y lógica, evaluando trade-offs antes de escribir código. Produce y mantiene ADRs (Architecture Decision Records).',
    phases: ['Spec', 'Plan'],
    contribution: 'Actúa como puente entre los requisitos de negocio y la topología del código, garantizando viabilidad estructural y escalabilidad.',
    functions: ['Generar y evaluar ADRs', 'Diseñar diagramas de arquitectura (C4)', 'Supervisar contratos entre componentes', 'Revisar la estructura física del repositorio'],
    tasks: [{ name: 'Redactar ADR-0042 — Migración OAuth2', type: 'Arquitectura' }, { name: 'Actualizar diagrama de componentes', type: 'Doc' }]
  },
  'evol-builder': {
    desc: 'Implementa la lógica central, infraestructura de código y componentes frontend/backend mediante TDD.',
    phases: ['Build'],
    contribution: 'Es el motor productivo — traduce los PLANs en código ejecutable con pruebas unitarias de respaldo.',
    functions: ['Redactar pruebas unitarias previas (TDD)', 'Escribir la lógica de implementación', 'Refactorizar código bajo demanda', 'Resolver conflictos de código técnicos'],
    tasks: [{ name: 'Implementar flujo OAuth2 principal', type: 'Backend' }, { name: 'Construir modal de Auth en UI', type: 'Frontend' }]
  },
  'evol-qa': {
    desc: 'Ejecuta pruebas automatizadas, diseña casos Gherkin (BDD) y actúa como gate keeper de calidad antes de cerrar una tarea.',
    phases: ['Plan', 'QA'],
    contribution: 'Asegura que el código cumpla los criterios de aceptación desde una perspectiva funcional y de borde.',
    functions: ['Escribir casos Gherkin a partir de PLAN', 'Traducir Gherkin a pruebas automatizadas', 'Auditar PRs antes del gate QA', 'Detectar regresiones funcionales'],
    tasks: [{ name: 'Casos Gherkin para Auth Domain', type: 'BDD' }, { name: 'Revisión final — TSK-208', type: 'Gate' }]
  },
  'evol-sec': {
    desc: 'Realiza modelado de amenazas STRIDE, revisa controles de seguridad y detecta vulnerabilidades en fase temprana.',
    phases: ['Spec', 'QA'],
    contribution: 'Impide que los fallos de seguridad lleguen a producción, aplicando SecDD (Security-Driven Development).',
    functions: ['Modelar amenazas (STRIDE)', 'Auditar dependencias vulnerables', 'Revisar vectores de inyección', 'Requerir controles compensatorios'],
    tasks: [{ name: 'Threat Model — Flujo de pago', type: 'STRIDE' }, { name: 'Auditoría SAST — API Gateway', type: 'Auditoría' }]
  },
  'evol-orchestrator': {
    desc: 'Gestiona la composición y el ciclo de vida del equipo multi-agente, invocando a los especialistas adecuados según el flujo.',
    phases: ['Continuous'],
    contribution: 'Actúa como "Lead Developer" automatizado — descompone historias, asigna a agentes especializados y recopila sus outputs.',
    functions: ['Ejecutar patrones de composición (Sequential/Parallel)', 'Invocar herramientas y habilidades de agentes', 'Agregar y consolidar outputs', 'Mantener el contexto global del pipeline'],
    tasks: [{ name: 'Orquestar fase Build — Auth Domain', type: 'Patrón' }, { name: 'Sync post-gate — SaaS Platform', type: 'Coordinación' }]
  },
  'evol-devops': {
    desc: 'Gestiona pipelines CI/CD e infraestructura de despliegue — automatiza desde el commit hasta producción.',
    phases: ['Build', 'QA'],
    contribution: 'Hace que el "funciona en mi máquina" sea irrelevante — automatiza la ruta a producción de forma repetible y auditable.',
    functions: ['Configurar pipelines CI/CD', 'Gestionar entornos (staging/prod)', 'Automatizar despliegues y rollbacks', 'Rotar credenciales e infraestructuras'],
    tasks: [{ name: 'Pipeline de release v0.6.3', type: 'CI/CD' }, { name: 'Rotar secretos — staging', type: 'Infra' }]
  },
  'evol-domain': {
    desc: 'Modela el dominio con DDD — identifica bounded contexts, agregados y lenguaje ubicuo.',
    phases: ['Spec', 'Plan'],
    contribution: 'Da nombre y forma al problema de negocio antes de escribir código — el modelo correcto evita meses de refactorización posterior.',
    functions: ['Redactar DOMAIN.md (bounded contexts)', 'Definir agregados y entidades raíz', 'Establecer el lenguaje ubicuo del dominio', 'Detectar context-mapping entre módulos'],
    tasks: [{ name: 'Mapear contextos — Payment Domain', type: 'DDD' }, { name: 'Revisar agregados Auth', type: 'Modelo' }]
  },
  'evol-doc': {
    desc: 'Genera documentación granular y mantiene los artefactos del proyecto sincronizados con el código.',
    phases: ['Spec', 'Build', 'Retro'],
    contribution: 'Evita que la documentación se pudra — cada artefacto refleja el estado real del sistema, no una foto antigua.',
    functions: ['Generar/actualizar artefactos (RUNBOOK, ONBOARDING…)', 'Sincronizar docs con cambios de código', 'Aplicar DOC_STANDARD a cada documento', 'Producir guías de uso por módulo'],
    tasks: [{ name: 'Actualizar RUNBOOK.md', type: 'Doc' }, { name: 'Generar ONBOARDING.md v2', type: 'Doc' }]
  },
  'evol-ux': {
    desc: 'Conduce el descubrimiento y validación UX — investiga el problema antes de dibujar la solución.',
    phases: ['Briefing'],
    contribution: 'Frena la tentación de construir rápido lo incorrecto — valida el problema con evidencia antes de comprometer recursos.',
    functions: ['Conducir discovery con usuarios reales', 'Redactar DISCOVERY.md', 'Prototipar y validar wireframes', 'Medir fricción en flujos críticos'],
    tasks: [{ name: 'DISCOVERY.md — flujo de búsqueda', type: 'Discovery' }, { name: 'Validar wireframes EVOL-DD', type: 'UX' }]
  },
  'evol-data': {
    desc: 'Diseña pipelines de datos y modelos de ingesta — desde la fuente bruta hasta la capa consolidada.',
    phases: ['Plan', 'Build'],
    contribution: 'Convierte datos crudos y dispersos en activos fiables y consultables — sin esto, "analytics" es solo una promesa.',
    functions: ['Diseñar esquemas de ingesta y retención', 'Construir pipelines ETL/ELT', 'Definir políticas de anonimización', 'Modelar capas de consolidación de memoria'],
    tasks: [{ name: 'Pipeline de ingesta — eventos de analytics', type: 'Data' }, { name: 'Esquema de retención — cajón de memoria', type: 'Schema' }]
  },
  'evol-reviewer': {
    desc: 'Revisa código en busca de corrección, simplificación y reuso — sin ceremonias, hallazgos accionables.',
    phases: ['Build', 'QA'],
    contribution: 'Atrapa bugs y complejidad innecesaria antes del merge — code review como red de seguridad, no como trámite.',
    functions: ['Revisar diffs línea por línea', 'Señalar duplicación y oportunidades de reuso', 'Verificar adherencia a convenciones', 'Priorizar hallazgos por severidad'],
    tasks: [{ name: 'Review PR #142 — zoom del grafo', type: 'Review' }, { name: 'Review PR #138 — selector de tema', type: 'Review' }]
  },
  'evol-pm': {
    desc: 'Acompaña sprints y métricas del proyecto — vela por el ritmo de entrega del pipeline.',
    phases: ['Plan', 'Retro'],
    contribution: 'Mantiene visible el ritmo real de entrega — detecta desviaciones de velocidad antes de que se vuelvan crisis.',
    functions: ['Planificar y cerrar sprints', 'Medir velocidad y carry-over', 'Reportar métricas del portafolio', 'Coordinar retrospectivas'],
    tasks: [{ name: 'Cierre Sprint 27 — retro', type: 'Sprint' }, { name: 'Planificar Sprint 29', type: 'Planning' }]
  },
  'evol-release': {
    desc: 'Gestiona releases y mantiene el CHANGELOG — versiona y documenta cada entrega.',
    phases: ['Build', 'Retro'],
    contribution: 'Hace rastreable cada versión publicada: qué cambió, por qué y para quién — sin sorpresas en producción.',
    functions: ['Versionar releases (semver)', 'Redactar CHANGELOG.md y notas de versión', 'Coordinar publicación (PyPI/registry)', 'Etiquetar y firmar tags de release'],
    tasks: [{ name: 'Tag v0.6.3 + notas', type: 'Release' }, { name: 'Borrador CHANGELOG v0.7.0', type: 'Changelog' }]
  },
  'evol-analyst': {
    desc: 'Evalúa impacto y radio de alcance de los cambios antes de aprobarlos — blast radius first.',
    phases: ['Plan', 'Build'],
    contribution: 'Responde "qué se rompe si cambio esto" con datos del grafo de código — transforma una suposición en análisis verificable.',
    functions: ['Ejecutar análisis de impacto sobre el grafo', 'Mapear llamadores y dependientes directos', 'Calcular el nivel de riesgo del cambio', 'Recomendar orden seguro de refactorización'],
    tasks: [{ name: 'Impacto: refactorización MemoryStore', type: 'Análisis' }, { name: 'Radio de alcance — renombrar API Gateway', type: 'Impacto' }]
  },
  'evol-researcher': {
    desc: 'Investiga mejoras del ecosistema de forma autónoma y propone adopciones con evidencia.',
    phases: ['Retro', 'Continuous'],
    contribution: 'Mantiene al sistema aprendiendo de sí mismo — convierte incidentes y hallazgos en lecciones reutilizables.',
    functions: ['Registrar lecciones (lecciones.md)', 'Investigar mejoras de herramientas/patrones', 'Verificar claims externos (fact-check)', 'Proponer adopciones con evidencia'],
    tasks: [{ name: 'Lección: CSRF en el state de OAuth2', type: 'Lección' }, { name: 'Investigar: LadybugDB vs alternativas', type: 'Research' }]
  },
  'evol-agent-factory': {
    desc: 'Crea agentes efímeros especializados bajo demanda cuando ningún agente core cubre el caso.',
    phases: ['Continuous'],
    contribution: 'Amplía las capacidades del sistema sin inflar el roster permanente — especialistas que aparecen, trabajan y se retiran.',
    functions: ['Diseñar prompts de agentes especializados', 'Registrar agentes efímeros temporalmente', 'Retirar agentes al concluir su propósito', 'Mantener el registro de agentes consistente'],
    tasks: [{ name: 'Crear agente: evol-i18n-reviewer', type: 'Factory' }, { name: 'Retirar agente efímero — evol-migrate-tmp', type: 'Lifecycle' }]
  },
  'evol-auditor': {
    desc: 'Audita conformidad de fase contra criterios del Gated Pipeline antes de firmar el gate.',
    phases: ['Plan', 'Build', 'QA'],
    contribution: 'Es el último filtro antes de dar una fase por cerrada — sin su aval, no hay transición.',
    functions: ['Verificar criterios de salida de cada fase', 'Validar presencia de los artefactos exigidos', 'Bloquear avance si faltan condiciones', 'Documentar hallazgos de auditoría'],
    tasks: [{ name: 'Auditoría fase Plan — Auth Domain', type: 'Auditoría' }, { name: 'Checklist de gate — Payment Domain', type: 'Gate' }]
  },
  'evol-compliance-auditor': {
    desc: 'Verifica el cumplimiento normativo y de convenciones internas en los artefactos y código.',
    phases: ['QA', 'Retro'],
    contribution: 'Asegura consistencia entre lo que el equipo dice que hace y lo que realmente queda registrado en el repo.',
    functions: ['Auditar adherencia a convenciones.md', 'Verificar formato de artefactos contra DOC_STANDARD', 'Detectar duplicados y desvíos', 'Reportar hallazgos por capa'],
    tasks: [{ name: 'Auditoría de convenciones — sprint 28', type: 'Compliance' }, { name: 'Revisar DOC_STANDARD — wireframes', type: 'Compliance' }]
  }
};

export const Agents: React.FC = () => {
  const { t } = useI18n();
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const activeAgent = AGENTS.find(a => a.id === selectedAgentId);
  const activeDesc = selectedAgentId ? AGENT_DESC[selectedAgentId] : null;

  return (
    <>
      <div className="section-header">
        <span className="section-title">{t('agents.coreTitle', 'Agentes núcleo')}</span>
        <span className="section-action">{t('agents.permanentCount', '18 permanentes')}</span>
      </div>

      <div className="card reveal-group">
        <div className="agent-list">
          <div className="agent-row header" style={{ display: 'grid', gridTemplateColumns: '1fr 180px 100px 100px 80px', alignItems: 'center', padding: '11px 16px', borderBottom: '1px solid var(--border-subtle)', fontSize: '11px', fontWeight: 500, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            <span>{t('agents.col.agent', 'Agente')}</span>
            <span>{t('agents.col.spec', 'Especialidad')}</span>
            <span>{t('agents.col.status', 'Estado')}</span>
            <span style={{ textAlign: 'center' }}>{t('agents.col.runs', 'Ejecuciones')}</span>
            <span style={{ textAlign: 'center' }}>{t('agents.col.last', 'Última')}</span>
          </div>

          {AGENTS.map(agent => (
            <div 
              key={agent.id} 
              className="agent-row" 
              style={{ display: 'grid', gridTemplateColumns: '1fr 180px 100px 100px 80px', alignItems: 'center', padding: '11px 16px', borderBottom: '1px solid var(--border-subtle)', fontSize: '13px', cursor: 'pointer', transition: 'background var(--transition)' }}
              onClick={() => setSelectedAgentId(agent.id)}
            >
              <span className="agent-name" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className={`dot ${agent.dot}`} style={{ width: '6px', height: '6px', borderRadius: '50%', flexShrink: 0, background: agent.dot === 'on' ? 'var(--status-success-fg)' : 'var(--text-tertiary)' }}></span>
                <span className="agent-id" style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-primary)' }}>{agent.id}</span>
              </span>
              <span className="agent-spec" style={{ color: 'var(--text-secondary)' }}>{t(`agent.spec.${agent.id}`, agent.spec)}</span>
              <span>
                <span className={`badge ${agent.status === 'Activo' ? 'success' : 'neutral'}`}>{agent.status === 'Activo' ? t('status.active', 'Activo') : t('status.inactive', 'Inactivo')}</span>
              </span>
              <span className="agent-runs" style={{ color: 'var(--text-tertiary)', fontVariantNumeric: 'tabular-nums', textAlign: 'center' }}>{agent.runs}</span>
              <span className="agent-runs" style={{ color: 'var(--text-tertiary)', fontVariantNumeric: 'tabular-nums', textAlign: 'center' }}>{agent.last}</span>
            </div>
          ))}
        </div>
      </div>

      <div className={`task-drawer-overlay ${selectedAgentId ? 'open' : ''}`} onClick={() => setSelectedAgentId(null)}>
        <div className="task-drawer" onClick={e => e.stopPropagation()}>
          <div className="task-drawer-header">
            <div>
              <div className="task-drawer-id">{activeAgent?.id || '—'}</div>
              <div className="task-drawer-title">{activeAgent ? t(`agent.spec.${activeAgent.id}`, activeAgent.spec) : '—'}</div>
            </div>
            <button className="icon-btn" aria-label="Cerrar" onClick={() => setSelectedAgentId(null)}>
              <X size={16} />
            </button>
          </div>

          <div className="task-drawer-body">
            <div className="td-section">
              <div className="td-section-title">{t('agent.drawer.status', 'Estado')}</div>
              <div className="detail-row">
                <span className="detail-row-label">{t('agent.drawer.currentStatus', 'Estado actual')}</span>
                <span className="detail-row-value">{activeAgent?.status}</span>
              </div>
              <div className="detail-row">
                <span className="detail-row-label">{t('agent.drawer.totalRuns', 'Ejecuciones totales')}</span>
                <span className="detail-row-value">{activeAgent?.runs}</span>
              </div>
              <div className="detail-row">
                <span className="detail-row-label">{t('agent.drawer.lastActivity', 'Última actividad')}</span>
                <span className="detail-row-value">{activeAgent?.last}</span>
              </div>
            </div>

            <div className="td-section">
              <div className="td-section-title">{t('agent.drawer.description', 'Descripción')}</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{activeDesc?.desc}</p>
            </div>

            <div className="td-section">
              <div className="td-section-title">{t('agent.drawer.pipelineIntegration', 'Integración en el pipeline')}</div>
              <div className="td-disciplines">
                {activeDesc?.phases.map((phase: string, i: number) => (
                  <span key={i} className="td-discipline">{phase}</span>
                ))}
              </div>
            </div>

            <div className="td-section">
              <div className="td-section-title">{t('agent.drawer.contribution', 'Aporte al proceso')}</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{activeDesc?.contribution}</p>
            </div>

            <div className="td-section">
              <div className="td-section-title">{t('agent.drawer.functions', 'Funciones')}</div>
              <ul className="td-criteria" style={{ paddingLeft: '20px', margin: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {activeDesc?.functions.map((fn: string, i: number) => (
                  <li key={i}>{fn}</li>
                ))}
              </ul>
            </div>

            <div className="td-section">
              <div className="td-section-title">{t('agent.drawer.recentTasks', 'Tareas recientes')}</div>
              <div className="relations-list">
                {activeDesc?.tasks.map((task: any, i: number) => (
                  <div key={i} className="relation-item">
                    <span className="relation-arrow">→</span>
                    <span className="relation-name">{task.name}</span>
                    <span className="relation-type">{task.type}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="td-section">
              <a className="btn btn-ghost" href="#" style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
                Mostrar documento
              </a>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
