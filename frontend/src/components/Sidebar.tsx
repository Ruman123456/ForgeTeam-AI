import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  History,
  Settings,
  Bot,
  Cpu,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  ollamaConnected?: boolean;
  groqConfigured?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ ollamaConnected = false, groqConfigured = false }) => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/projects/new', label: 'Create Project', icon: PlusCircle },
    { to: '/runs', label: 'Run History', icon: History },
    { to: '/settings', label: 'Settings & Status', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white/90 dark:bg-slate-900/80 border-r border-slate-200 dark:border-slate-800 flex flex-col h-screen shrink-0 select-none">
      {/* Brand */}
      <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-base text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
            ForgeTeam <span className="text-xs px-1.5 py-0.5 rounded bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 font-mono font-semibold">AI</span>
          </h1>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Autonomous Agent Platform</p>
        </div>
      </div>

      {/* Nav links */}
      <nav className="p-3 space-y-1.5 flex-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-600/20 text-indigo-600 dark:text-indigo-300 font-semibold border border-indigo-200 dark:border-indigo-500/30 shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer status widget */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800/80 space-y-2">
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/60 text-xs space-y-2">
          <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
            <span className="flex items-center gap-1.5 font-medium">
              <Cpu className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
              Local Model
            </span>
            <span className="flex items-center gap-1">
              <span
                className={`w-2 h-2 rounded-full ${
                  ollamaConnected ? 'bg-emerald-500' : 'bg-slate-400'
                }`}
              />
              <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                {ollamaConnected ? 'Online' : 'Offline'}
              </span>
            </span>
          </div>

          <div className="flex items-center justify-between text-slate-600 dark:text-slate-400 pt-1 border-t border-slate-200 dark:border-slate-800/50">
            <span className="flex items-center gap-1.5 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              Cloud LPU
            </span>
            <span className="text-[11px] font-mono">
              {groqConfigured ? (
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Active</span>
              ) : (
                <span className="text-slate-400">Ready</span>
              )}
            </span>
          </div>
        </div>

        <div className="text-[10px] text-center text-slate-400 dark:text-slate-500">
          Enterprise Multi-Agent Runtime
        </div>
      </div>
    </aside>
  );
};
