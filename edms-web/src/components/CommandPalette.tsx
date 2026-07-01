import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

const ITEMS = [
  { group: 'Páginas', icon: 'page', label: 'Tablero', meta: 'Resumen general', href: '/' },
  { group: 'Páginas', icon: 'page', label: 'Proyectos', meta: 'Tablero de proyectos', href: '/projects' },
  { group: 'Páginas', icon: 'page', label: 'Conocimiento', meta: 'Grafo de navegación', href: '/knowledge' },
  { group: 'Páginas', icon: 'page', label: 'Buscar', meta: 'Búsqueda global', href: '/search' },
  { group: 'Páginas', icon: 'page', label: 'Agentes', meta: 'Workspace', href: '/agents' },
  { group: 'Páginas', icon: 'page', label: 'Habilidades', meta: 'Skills registradas', href: '/skills' },
  { group: 'Páginas', icon: 'page', label: 'Disciplinas', meta: 'Disciplinas registradas', href: '/disciplines' },
  { group: 'Páginas', icon: 'page', label: 'Memoria', meta: 'EVOL-DD · consolidación', href: '/memory' },
  { group: 'Páginas', icon: 'page', label: 'Analítica', meta: 'Métricas del pipeline', href: '/analytics' },

  { group: 'Proyectos', icon: 'project', label: 'SaaS Platform', meta: 'Construcción · 84%', href: '/projects' },
  { group: 'Proyectos', icon: 'project', label: 'API Gateway v3', meta: 'QA · 61%', href: '/projects' },
  { group: 'Proyectos', icon: 'project', label: 'Auth Domain', meta: 'Plan · 32%', href: '/projects' },
  { group: 'Proyectos', icon: 'project', label: 'Analytics Pipeline', meta: 'Construcción · 47%', href: '/projects' },
];

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setQuery('');
      setActiveIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  const visible = React.useMemo(() => {
    const filtered = ITEMS.filter(it => 
      it.label.toLowerCase().includes(query.toLowerCase()) || 
      it.meta.toLowerCase().includes(query.toLowerCase()) || 
      it.group.toLowerCase().includes(query.toLowerCase())
    );
    const vis = [...filtered];
    if (query.trim()) {
      vis.push({
        group: 'Búsqueda global', icon: 'page', label: `Buscar "${query.trim()}" en todo el sistema`, meta: 'LadybugDB · ChromaDB · pipeline', href: `/search?q=${encodeURIComponent(query.trim())}`
      });
    }
    return vis;
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isK = e.key === 'k' || e.key === 'K';
      if ((e.metaKey || e.ctrlKey) && isK) {
        e.preventDefault();
        if (isOpen) onClose();
      } else if (isOpen) {
        if (e.key === 'Escape') {
          e.preventDefault();
          onClose();
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          setActiveIndex(prev => Math.min(prev + 1, visible.length - 1));
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setActiveIndex(prev => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter') {
          e.preventDefault();
          if (visible[activeIndex]) {
            navigate(visible[activeIndex].href);
            onClose();
          }
        }
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, visible, activeIndex, navigate, onClose]);

  if (!isOpen) return null;

  return (
    <div className="cmdk-overlay open" onClick={onClose}>
      <div className="cmdk-modal" role="dialog" onClick={e => e.stopPropagation()}>
        <div className="cmdk-input-row">
          <Search size={16} />
          <input 
            ref={inputRef}
            className="cmdk-input" 
            type="text" 
            placeholder="Buscar páginas, proyectos, agentes, skills, memoria…" 
            value={query}
            onChange={e => { setQuery(e.target.value); setActiveIndex(0); }}
            autoComplete="off" 
          />
          <span className="cmdk-esc">Esc</span>
        </div>
        <div className="cmdk-results">
          {visible.length === 0 ? (
            <div className="cmdk-empty">Sin resultados para "{query}"</div>
          ) : (
            visible.map((it, i) => {
              const isFirstInGroup = i === 0 || visible[i - 1].group !== it.group;
              return (
                <React.Fragment key={i}>
                  {isFirstInGroup && <div className="cmdk-group-label">{it.group}</div>}
                  <button 
                    className={`cmdk-item ${i === activeIndex ? 'active' : ''}`}
                    onClick={() => { navigate(it.href); onClose(); }}
                    onMouseEnter={() => setActiveIndex(i)}
                  >
                    <Search size={14} />
                    <span>{it.label}</span>
                    <span className="cmdk-item-meta">{it.meta}</span>
                  </button>
                </React.Fragment>
              );
            })
          )}
        </div>
        <div className="cmdk-footer" style={{ padding: '8px 16px', borderTop: '1px solid var(--border)', fontSize: '11px', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>Contexto en vivo:</span>
          <span style={{ fontFamily: 'var(--font-mono)' }}>LadybugDB</span><span>·</span>
          <span style={{ fontFamily: 'var(--font-mono)' }}>ChromaDB</span>
        </div>
      </div>
    </div>
  );
};
