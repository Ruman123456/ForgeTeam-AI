import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Header } from '../components/Header';
import { api } from '../api/client';
import { ConfigResponse } from '../types';

export const MainLayout: React.FC = () => {
  const [config, setConfig] = useState<ConfigResponse | null>(null);

  useEffect(() => {
    api.getConfig()
      .then(setConfig)
      .catch((err) => console.warn('Could not fetch config:', err));
  }, []);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      <Sidebar
        ollamaConnected={config?.ollama_connected || false}
        groqConfigured={config?.groq_configured || false}
      />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
