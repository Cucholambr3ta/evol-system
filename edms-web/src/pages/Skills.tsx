/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useMemo } from 'react';
import { useI18n } from '../contexts/I18nContext';
import { Search } from 'lucide-react';

const SKILL_META = [
  { name: "agent-eval", cat: "Quality Gate", trigger: "/eval", agents: [] },
  { name: "code-indexer", cat: "Code Analysis", trigger: "/code-index", agents: ["evol-analyst", "evol-builder", "evol-reviewer"] },
  { name: "crear-agente", cat: "Lifecycle", trigger: "", agents: ["evol-agent-factory", "evol-orchestrator"] },
  { name: "crear-skill", cat: "Growth", trigger: "", agents: [] },
  { name: "evol-a11ydd", cat: "Discipline", trigger: "/a11y", agents: [] },
  { name: "evol-add-arch", cat: "Discipline", trigger: "/add-arch", agents: [] },
  { name: "evol-ai-review", cat: "Quality Gate", trigger: "/ai-review", agents: [] },
  { name: "evol-apivdd", cat: "Discipline", trigger: "/apivdd", agents: [] },
  { name: "evol-atdd-acceptance", cat: "Discipline", trigger: "/atdd", agents: [] },
  { name: "evol-balance", cat: "Game-Inspired", trigger: "/balance", agents: [] },
  { name: "evol-bdd-behavior", cat: "Discipline", trigger: "/bdd", agents: [] },
  { name: "evol-ccdd-contract", cat: "Discipline", trigger: "/ccdd", agents: [] },
  { name: "evol-cdcdd", cat: "Discipline", trigger: "/cdc", agents: [] },
  { name: "evol-change-mgmt", cat: "Transfer", trigger: "/change-mgmt", agents: [] },
  { name: "evol-chaos-resilience", cat: "Discipline", trigger: "/chaos", agents: [] },
  { name: "evol-code-archaeology", cat: "Transfer", trigger: "/code-archaeology", agents: [] },
  { name: "evol-cognitive-ux", cat: "Transfer", trigger: "/cognitive-ux", agents: [] },
  { name: "evol-compact", cat: "Context Engineering", trigger: "/compact", agents: [] },
  { name: "evol-compliance-drivers", cat: "Discipline", trigger: "/compliance-drivers", agents: [] },
  { name: "evol-context7", cat: "Research", trigger: "", agents: [] },
  { name: "evol-cost-analysis", cat: "Transfer", trigger: "/cost-analysis", agents: [] },
  { name: "evol-ddd-domain", cat: "Discipline", trigger: "/ddd", agents: [] },
  { name: "evol-debt-budget", cat: "Discipline", trigger: "/debt-budget", agents: [] },
  { name: "evol-deprecation", cat: "Discipline", trigger: "/deprecation", agents: [] },
  { name: "evol-discovery", cat: "Transfer", trigger: "/discovery", agents: [] },
  { name: "evol-domain-finance", cat: "Domain Advisor", trigger: "/domain-finance", agents: [] },
  { name: "evol-domain-marketing", cat: "Domain Advisor", trigger: "/domain-marketing", agents: [] },
  { name: "evol-domain-sales", cat: "Domain Advisor", trigger: "/domain-sales", agents: [] },
  { name: "evol-dx-advocate", cat: "Transfer", trigger: "/dx", agents: [] },
  { name: "evol-eda", cat: "Discipline", trigger: "/eda", agents: [] },
  { name: "evol-esdd-events", cat: "Discipline", trigger: "/esdd", agents: [] },
  { name: "evol-ethnography", cat: "Transfer", trigger: "/ethnography", agents: [] },
  { name: "evol-fact-check", cat: "Verification", trigger: "", agents: [] },
  { name: "evol-fdd-feature", cat: "Discipline", trigger: "/fdd", agents: [] },
  { name: "evol-frontend-design", cat: "Growth / Design", trigger: "", agents: [] },
  { name: "evol-fs-context", cat: "Context Engineering", trigger: "/fs-context", agents: [] },
  { name: "evol-governance", cat: "Transfer", trigger: "/governance", agents: [] },
  { name: "evol-grill-me", cat: "Verification", trigger: "", agents: [] },
  { name: "evol-growth-experiment", cat: "Transfer", trigger: "/growth", agents: [] },
  { name: "evol-idea-refine", cat: "Verification", trigger: "", agents: [] },
  { name: "evol-iodd-iac", cat: "Discipline", trigger: "/iodd-iac", agents: [] },
  { name: "evol-mcp-builder", cat: "Transfer", trigger: "/mcp-builder", agents: [] },
  { name: "evol-mdd-migrate", cat: "Discipline", trigger: "/mdd", agents: [] },
  { name: "evol-narrative-docs", cat: "Game-Inspired", trigger: "/narrative-docs", agents: [] },
  { name: "evol-observability", cat: "Transfer", trigger: "/observability", agents: [] },
  { name: "evol-odd-api", cat: "Discipline", trigger: "/odd-api", agents: [] },
  { name: "evol-odd-obs", cat: "Discipline", trigger: "/odd-obs", agents: [] },
  { name: "evol-pacing", cat: "Game-Inspired", trigger: "/pacing", agents: [] },
  { name: "evol-pdd-perf", cat: "Discipline", trigger: "/pdd", agents: [] },
  { name: "evol-pipeline-ci", cat: "Discipline", trigger: "/pipeline-ci", agents: [] },
  { name: "evol-privacy-drivers", cat: "Discipline", trigger: "/privacy-drivers", agents: [] },
  { name: "evol-prompt-master", cat: "Growth", trigger: "", agents: [] },
  { name: "evol-rdd-refactor", cat: "Discipline", trigger: "/rdd", agents: [] },
  { name: "evol-remotion", cat: "Growth / Design", trigger: "", agents: [] },
  { name: "evol-sandbox", cat: "Security", trigger: "/sandbox", agents: [] },
  { name: "evol-sdd-spec", cat: "Discipline", trigger: "/sdd", agents: [] },
  { name: "evol-secdd-security", cat: "Discipline", trigger: "/secdd", agents: [] },
  { name: "evol-seo-technical", cat: "Transfer", trigger: "/seo", agents: [] },
  { name: "evol-skill-manager", cat: "Lifecycle", trigger: "/skill", agents: [] },
  { name: "evol-slo-sla", cat: "Discipline", trigger: "/slo-sla", agents: [] },
  { name: "evol-stdd-security-test", cat: "Discipline", trigger: "/stdd", agents: [] },
  { name: "evol-systems-design", cat: "Game-Inspired", trigger: "/systems-design", agents: [] },
  { name: "evol-talk-compact", cat: "Compression", trigger: "/compact-talk", agents: [] },
  { name: "evol-tdd-unit", cat: "Discipline", trigger: "/tdd", agents: [] },
  { name: "evol-team-dynamics", cat: "Transfer", trigger: "/team-dynamics", agents: [] },
  { name: "evol-threat-model", cat: "Discipline", trigger: "/threat-model", agents: [] },
  { name: "evol-udd-usecase", cat: "Discipline", trigger: "/udd-usecase", agents: [] },
  { name: "evol-uxdd-ux", cat: "Discipline", trigger: "/uxdd", agents: [] },
  { name: "evol-workflow-design", cat: "Transfer", trigger: "/workflow", agents: [] },
  { name: "readme-master", cat: "Documentación", trigger: "", agents: [] }
];

const SKILL_TEXT: Record<string, any> = {
  "agent-eval": { fn: "Eval-harness para skills/agents/workflows Evol-DD.", pipe: [] },
  "code-indexer": { fn: "Indexación del grafo de código vía Tree-sitter.", pipe: [["Fase 4 (Build)", "Calcula el radio de impacto antes de refactorizar"], ["Transversal", "Mantiene el grafo de código sincronizado"]] },
  "crear-agente": { fn: "Crea nuevos agentes Evol-DD desde cero.", pipe: [] },
  "crear-skill": { fn: "Crea nuevas skills para Evol-DD desde cero con loop iterativo de eval.", pipe: [] },
  "evol-fdd-feature": { fn: "Feature-Driven Development. Descompone features en FEATURES.md.", pipe: [] },
  "evol-tdd-unit": { fn: "Test-Driven Development. Aplica ciclo Rojo-Verde-Refactor.", pipe: [] },
  "evol-bdd-behavior": { fn: "Behavior-Driven Development. Convierte criterios de aceptación en Gherkin.", pipe: [] }
};

export const Skills: React.FC = () => {
  const { t } = useI18n();
  const [filter, setFilter] = useState('');
  const [selectedSkillName, setSelectedSkillName] = useState<string | null>(null);

  const filteredSkills = useMemo(() => {
    return SKILL_META.filter(s => s.name.toLowerCase().includes(filter.toLowerCase()) || (s.trigger && s.trigger.toLowerCase().includes(filter.toLowerCase())));
  }, [filter]);

  const grouped = useMemo(() => {
    const groups: Record<string, typeof SKILL_META> = {};
    filteredSkills.forEach(s => {
      if (!groups[s.cat]) groups[s.cat] = [];
      groups[s.cat].push(s);
    });
    return groups;
  }, [filteredSkills]);

  const activeSkill = SKILL_META.find(s => s.name === selectedSkillName);
  const activeDesc = selectedSkillName ? SKILL_TEXT[selectedSkillName] : null;

  return (
    <>
      <div className="section-header">
        <span className="section-title">{t('nav.skills', 'Habilidades')}</span>
        <div className="search-box">
          <Search size={14} style={{ color: 'var(--text-tertiary)' }} />
          <input 
            type="text" 
            placeholder={t('skills.filterPlaceholder', 'Filtrar habilidades...')} 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
      </div>

      <div className="metrics-row reveal-group metrics-row--centered" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', marginBottom: '24px' }}>
        <div className="metric">
          <div className="metric-label">{t('skills.metric.total', 'Habilidades totales')}</div>
          <div className="metric-value">{SKILL_META.length}</div>
          <div className="metric-delta up">{t('skills.metric.totalDelta', '+3 absorbidas')}</div>
        </div>
        <div className="metric">
          <div className="metric-label">{t('skills.metric.categories', 'Categorías')}</div>
          <div className="metric-value">{Object.keys(grouped).length}</div>
          <div className="metric-delta">{t('skills.metric.categoriesDelta', 'Agrupadas')}</div>
        </div>
        <div className="metric metric-clickable">
          <div className="metric-label">{t('skills.metric.mcpServers', 'Servidores MCP')}</div>
          <div className="metric-value">1</div>
        </div>
      </div>

      <div className="skills-layout reveal-group">
        <div>
          {Object.entries(grouped).map(([cat, skills]) => (
            <div key={cat} className="skill-group" style={{ marginBottom: '18px' }}>
              <div className="skill-group-label" style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', padding: '0 4px 8px' }}>{cat}</div>
              <div className="skill-list" style={{ display: 'flex', flexDirection: 'column' }}>
                {skills.map(skill => (
                  <div 
                    key={skill.name} 
                    className={`skill-row ${selectedSkillName === skill.name ? 'selected' : ''}`}
                    style={{ 
                      display: 'flex', alignItems: 'center', gap: '12px', padding: '11px 14px', 
                      background: selectedSkillName === skill.name ? 'var(--surface-el)' : 'var(--surface)', 
                      border: `1px solid ${selectedSkillName === skill.name ? 'var(--accent)' : 'var(--border)'}`, 
                      borderRadius: 'var(--radius-md)', marginBottom: '6px', cursor: 'pointer' 
                    }}
                    onClick={() => setSelectedSkillName(skill.name)}
                  >
                    <div className="skill-icon" style={{ width: '28px', height: '28px', borderRadius: 'var(--radius-sm)', background: 'var(--surface-el)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '13px', height: '13px', color: selectedSkillName === skill.name ? 'var(--accent)' : 'var(--text-tertiary)' }}><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                    </div>
                    <div className="skill-main" style={{ flex: 1, minWidth: 0 }}>
                      <div className="skill-name" style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)' }}>{skill.name}</div>
                      {skill.trigger && <div className="skill-trigger" style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '1px' }}>{skill.trigger}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="detail-panel" style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', position: 'sticky', top: '24px', overflow: 'hidden' }}>
          {!selectedSkillName ? (
            <div className="detail-empty" style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-tertiary)', fontSize: '13px' }}>
              Selecciona una habilidad para ver sus detalles.
            </div>
          ) : (
            <>
              <div className="detail-head" style={{ padding: '16px', borderBottom: '1px solid var(--border)' }}>
                <div className="detail-skill-name" style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>{activeSkill?.name}</div>
                {activeSkill?.trigger && <div className="detail-skill-trigger" style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent)' }}>{activeSkill.trigger}</div>}
              </div>
              <div className="detail-sec" style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
                <div className="detail-sec-label" style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{t('skills.detail.category', 'Categoría')}</div>
                <div className="detail-sec-body" style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{activeSkill?.cat}</div>
              </div>
              <div className="detail-sec" style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
                <div className="detail-sec-label" style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{t('skills.detail.prompt', 'Prompt')}</div>
                <div className="detail-sec-body" style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                  {activeDesc?.fn || 'Sin descripción detallada.'}
                </div>
              </div>
              {activeSkill && activeSkill.agents.length > 0 && (
                <div className="detail-sec" style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
                  <div className="detail-sec-label" style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{t('skills.detail.agentsUsing', 'Agentes que la usan')}</div>
                  <div className="detail-sec-body">
                    {activeSkill.agents.map(a => (
                      <span key={a} style={{ display: 'inline-flex', alignItems: 'center', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', background: 'var(--surface-el)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '2px 7px', margin: '0 4px 4px 0' }}>{a}</span>
                    ))}
                  </div>
                </div>
              )}
              {activeDesc && activeDesc.pipe && activeDesc.pipe.length > 0 && (
                <div className="detail-sec" style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
                  <div className="detail-sec-label" style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{t('skills.detail.pipelineIntegration', 'Integración en el pipeline')}</div>
                  <div className="detail-sec-body">
                    {activeDesc.pipe.map((p: any, i: number) => (
                      <div key={i} style={{ display: 'flex', gap: '8px', padding: '3px 0', fontSize: '13px', color: 'var(--text-secondary)' }}>
                        <span style={{ fontSize: '11px', fontWeight: 500, color: 'var(--accent)', background: 'var(--accent-muted)', borderRadius: 'var(--radius-sm)', padding: '0 6px', flexShrink: 0, height: '18px', display: 'flex', alignItems: 'center' }}>{p[0]}</span>
                        <span>{p[1]}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
};
