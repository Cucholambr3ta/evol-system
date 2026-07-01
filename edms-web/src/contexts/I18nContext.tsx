import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

type Language = 'es' | 'en' | 'pt';

interface I18nContextProps {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: string, fallback?: string) => string;
}

const dictionaries: Record<Language, Record<string, string>> = {
  es: {
    'nav.main': 'Main', 'nav.workspace': 'Workspace',
    'nav.dashboard': 'Tablero', 'nav.projects': 'Proyectos', 'nav.knowledge': 'Conocimiento',
    'nav.search': 'Buscar', 'nav.agents': 'Agentes', 'nav.skills': 'Habilidades',
    'nav.disciplines': 'Disciplinas', 'nav.memory': 'Memoria', 'nav.analytics': 'Analítica',
    'sidebar.toggle': 'Mostrar/ocultar barra lateral',
    'breadcrumb.dashboard': 'Tablero',
    'topbar.search': 'Buscar (⌘K)', 'topbar.lang': 'Idioma / Language', 'topbar.theme': 'Elegir paleta de colores',
    // ... we will add more keys as we build the components
  },
  en: {
    'nav.main': 'Main', 'nav.workspace': 'Workspace',
    'nav.dashboard': 'Dashboard', 'nav.projects': 'Projects', 'nav.knowledge': 'Knowledge',
    'nav.search': 'Search', 'nav.agents': 'Agents', 'nav.skills': 'Skills',
    'nav.disciplines': 'Disciplines', 'nav.memory': 'Memory', 'nav.analytics': 'Analytics',
    'sidebar.toggle': 'Show/hide sidebar',
    'breadcrumb.dashboard': 'Dashboard',
    'topbar.search': 'Search (⌘K)', 'topbar.lang': 'Language', 'topbar.theme': 'Choose color palette',
  },
  pt: {
    'nav.main': 'Principal', 'nav.workspace': 'Workspace',
    'nav.dashboard': 'Painel', 'nav.projects': 'Projetos', 'nav.knowledge': 'Conhecimento',
    'nav.search': 'Buscar', 'nav.agents': 'Agentes', 'nav.skills': 'Habilidades',
    'nav.disciplines': 'Disciplinas', 'nav.memory': 'Memória', 'nav.analytics': 'Análise',
    'sidebar.toggle': 'Mostrar/ocultar barra lateral',
    'breadcrumb.dashboard': 'Painel',
    'topbar.search': 'Buscar (⌘K)', 'topbar.lang': 'Idioma', 'topbar.theme': 'Escolher paleta de cores',
  }
};

const I18nContext = createContext<I18nContextProps | undefined>(undefined);

export const I18nProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Language>(() => {
    return (localStorage.getItem('edms-lang') as Language) || 'es';
  });

  const setLang = (newLang: Language) => {
    setLangState(newLang);
    localStorage.setItem('edms-lang', newLang);
  };

  const t = (key: string, fallback?: string): string => {
    return dictionaries[lang][key] || fallback || key;
  };

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) throw new Error('useI18n must be used within I18nProvider');
  return context;
};
