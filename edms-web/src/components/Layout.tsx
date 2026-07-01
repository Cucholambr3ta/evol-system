import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './layout/Sidebar';
import { Topbar } from './layout/Topbar';
import { CommandPalette } from './CommandPalette';

export const Layout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [cmdkOpen, setCmdkOpen] = useState(false);

  return (
    <div className="app">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        setCollapsed={setSidebarCollapsed} 
        mobileOpen={mobileSidebarOpen}
        setMobileOpen={setMobileSidebarOpen}
      />
      <div className="page">
        <Topbar 
          setMobileOpen={setMobileSidebarOpen} 
          openCmdk={() => setCmdkOpen(true)} 
        />
        <div className="page-body">
          <Outlet />
        </div>
      </div>
      <CommandPalette isOpen={cmdkOpen} onClose={() => setCmdkOpen(false)} />
    </div>
  );
};
