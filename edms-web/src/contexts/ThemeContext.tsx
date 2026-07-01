import React, { createContext, useContext, useState, useEffect } from 'react';

export type Theme = 
  | 'bruma' | 'lavanda' | 'marfil' | 'ambar' 
  | 'caramelo' | 'nocturna' | 'bosque' | 'sumie' 
  | 'pizarra' | 'terminal-verde' | 'solana' 
  | 'estuario' | 'pergamino';

interface ThemeContextProps {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextProps | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const saved = localStorage.getItem('edms-theme') as Theme;
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'bruma' : 'marfil';
  });

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('edms-theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};
