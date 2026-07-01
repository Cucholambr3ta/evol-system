import React from 'react';
import { NavLink } from 'react-router-dom';
import { useI18n } from '../../contexts/I18nContext';
import { 
  LayoutDashboard, Layers, Network, Search, 
  Bot, Zap, BookOpen, Database, LineChart, PanelLeftClose, PanelLeftOpen 
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (val: boolean) => void;
  mobileOpen: boolean;
  setMobileOpen: (val: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, setCollapsed, mobileOpen, setMobileOpen }) => {
  const { t } = useI18n();

  return (
    <>
      <nav className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-top">
          <span className="logo">EVOL-DD</span>
          <button 
            className="sidebar-toggle" 
            title={t('sidebar.toggle', 'Mostrar/ocultar barra lateral')}
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
          </button>
        </div>

        <div className="sidebar-nav">
          <div className="nav-section">
            <div className="nav-section-label">{t('nav.main', 'Main')}</div>
            <NavLink to="/" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <LayoutDashboard size={15} />
              <span className="nav-label">{t('nav.dashboard', 'Tablero')}</span>
            </NavLink>
            <NavLink to="/projects" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Layers size={15} />
              <span className="nav-label">{t('nav.projects', 'Proyectos')}</span>
              <span className="nav-count">24</span>
            </NavLink>
            <NavLink to="/knowledge" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Network size={15} />
              <span className="nav-label">{t('nav.knowledge', 'Conocimiento')}</span>
            </NavLink>
            <NavLink to="/search" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Search size={15} />
              <span className="nav-label">{t('nav.search', 'Buscar')}</span>
            </NavLink>
          </div>

          <div className="nav-section">
            <div className="nav-section-label">{t('nav.workspace', 'Workspace')}</div>
            <NavLink to="/agents" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Bot size={15} />
              <span className="nav-label">{t('nav.agents', 'Agentes')}</span>
              <span className="nav-count">18</span>
            </NavLink>
            <NavLink to="/skills" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Zap size={15} />
              <span className="nav-label">{t('nav.skills', 'Habilidades')}</span>
              <span className="nav-count">17</span>
            </NavLink>
            <NavLink to="/disciplines" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <BookOpen size={15} />
              <span className="nav-label">{t('nav.disciplines', 'Disciplinas')}</span>
              <span className="nav-count">31</span>
            </NavLink>
            <NavLink to="/memory" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <Database size={15} />
              <span className="nav-label">{t('nav.memory', 'Memoria')}</span>
            </NavLink>
            <NavLink to="/analytics" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
              <LineChart size={15} />
              <span className="nav-label">{t('nav.analytics', 'Analítica')}</span>
            </NavLink>
          </div>
        </div>
      </nav>
      {mobileOpen && (
        <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />
      )}
    </>
  );
};
