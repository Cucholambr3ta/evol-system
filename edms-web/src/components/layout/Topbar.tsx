import React, { useState, useRef, useEffect } from 'react';
import { useI18n } from '../../contexts/I18nContext';
import { useTheme } from '../../contexts/ThemeContext';
import type { Theme } from '../../contexts/ThemeContext';
import { Search, Globe, ChevronDown, Palette, Menu } from 'lucide-react';

interface TopbarProps {
  setMobileOpen: (val: boolean) => void;
  openCmdk: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ setMobileOpen, openCmdk }) => {
  const { t, lang, setLang } = useI18n();
  const { theme, setTheme } = useTheme();
  
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const [themeMenuOpen, setThemeMenuOpen] = useState(false);
  
  const langRef = useRef<HTMLDivElement>(null);
  const themeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setLangMenuOpen(false);
      }
      if (themeRef.current && !themeRef.current.contains(event.target as Node)) {
        setThemeMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const THEMES = [
    { id: 'bruma', name: 'Bruma', hint: 'oscuro · azul hielo', colors: ['#2E3440', '#4C566A', '#88C0D0'] },
    { id: 'lavanda', name: 'Lavanda', hint: 'oscuro · malva pastel', colors: ['#1E1E2E', '#45475A', '#CBA6F7'] },
    { id: 'marfil', name: 'Marfil', hint: 'claro · neutro', colors: ['#FFFFFF', '#E5E7EB', '#4F46E5'] },
    { id: 'ambar', name: 'Ámbar', hint: 'oscuro · naranja retro', colors: ['#282828', '#504945', '#FE8019'] },
    { id: 'caramelo', name: 'Caramelo', hint: 'oscuro · durazno cálido', colors: ['#24273A', '#494D64', '#F5A97F'] },
    { id: 'nocturna', name: 'Nocturna', hint: 'oscuro · azul noche', colors: ['#1A1B26', '#3B4261', '#7AA2F7'] },
    { id: 'bosque', name: 'Bosque', hint: 'oscuro · verde bosque', colors: ['#2D353B', '#4F5B58', '#A7C080'] },
    { id: 'sumie', name: 'Sumie', hint: 'oscuro · tinta azulada', colors: ['#1F1F28', '#54546D', '#7E9CD8'] },
    { id: 'pizarra', name: 'Pizarra', hint: 'oscuro · gris equilibrado', colors: ['#282C34', '#4B5263', '#61AFEF'] },
    { id: 'terminal-verde', name: 'Terminal Verde', hint: 'oscuro · alto contraste', colors: ['#0A0E0A', '#1F3A1F', '#00FF66'] },
    { id: 'solana', name: 'Solana', hint: 'claro · arena cálida', colors: ['#FAFAFA', '#E0DFD5', '#FA8D3E'] },
    { id: 'estuario', name: 'Estuario', hint: 'oscuro · turquesa', colors: ['#002B36', '#285C66', '#2AA198'] },
    { id: 'pergamino', name: 'Pergamino', hint: 'claro · pergamino cálido', colors: ['#FDF6E3', '#D3CBB7', '#268BD2'] }
  ];

  return (
    <header className="topbar">
      <button className="icon-btn mobile-menu-btn" onClick={() => setMobileOpen(true)} style={{ display: 'none' /* handled by CSS media query in real implementation */ }}>
        <Menu size={16} />
      </button>
      
      <div className="topbar-breadcrumb">
        <span>{t('breadcrumb.dashboard', 'Tablero')}</span>
      </div>
      
      <div className="topbar-right">
        <button className="icon-btn" title={t('topbar.search', 'Buscar (⌘K)')} onClick={openCmdk}>
          <Search size={14} />
        </button>
        
        <div className={`lang-select ${langMenuOpen ? 'open' : ''}`} ref={langRef}>
          <button className="lang-trigger" title={t('topbar.lang', 'Idioma / Language')} onClick={() => setLangMenuOpen(!langMenuOpen)}>
            <Globe size={11} />
            <span className="lang-current">{lang.toUpperCase()}</span>
            <ChevronDown size={11} />
          </button>
          <div className="lang-menu">
            <button className={`lang-option ${lang === 'es' ? 'active' : ''}`} onClick={() => { setLang('es'); setLangMenuOpen(false); }}>Español <span className="lang-code">ES</span></button>
            <button className={`lang-option ${lang === 'en' ? 'active' : ''}`} onClick={() => { setLang('en'); setLangMenuOpen(false); }}>English <span className="lang-code">EN</span></button>
            <button className={`lang-option ${lang === 'pt' ? 'active' : ''}`} onClick={() => { setLang('pt'); setLangMenuOpen(false); }}>Português <span className="lang-code">PT</span></button>
          </div>
        </div>
        
        <div className="theme-picker" ref={themeRef}>
          <button 
            className="icon-btn" 
            title={t('topbar.theme', 'Elegir paleta de colores')} 
            aria-expanded={themeMenuOpen}
            onClick={() => setThemeMenuOpen(!themeMenuOpen)}
          >
            <Palette size={14} />
          </button>
          <div className={`theme-menu ${themeMenuOpen ? 'open' : ''}`} style={{ display: themeMenuOpen ? 'block' : 'none' }}>
            {THEMES.map(th => (
              <button 
                key={th.id}
                className={`theme-option ${theme === th.id ? 'selected' : ''}`} 
                onClick={() => { setTheme(th.id as Theme); setThemeMenuOpen(false); }}
              >
                <span className="theme-swatch" style={{ background: th.colors[0], border: `1px solid ${th.colors[1]}` }}>
                  <span style={{ background: th.colors[2] }}></span>
                </span>
                <span className="theme-name">{th.name}</span>
                <span className="theme-hint">{th.hint}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
};
