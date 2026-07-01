import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { I18nProvider } from './contexts/I18nContext';
import { Layout } from './components/Layout';

import { Dashboard } from './pages/Dashboard';
import { Projects } from './pages/Projects';
import { Knowledge } from './pages/Knowledge';
import { GlobalSearch } from './pages/GlobalSearch';
import { Agents } from './pages/Agents';
import { Skills } from './pages/Skills';
import { Disciplines } from './pages/Disciplines';
import { Memory } from './pages/Memory';
import { Analytics } from './pages/Analytics';
function App() {
  return (
    <ThemeProvider>
      <I18nProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="projects" element={<Projects />} />
              <Route path="knowledge" element={<Knowledge />} />
              <Route path="search" element={<GlobalSearch />} />
              <Route path="agents" element={<Agents />} />
              <Route path="skills" element={<Skills />} />
              <Route path="disciplines" element={<Disciplines />} />
              <Route path="memory" element={<Memory />} />
              <Route path="analytics" element={<Analytics />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </I18nProvider>
    </ThemeProvider>
  );
}

export default App;
