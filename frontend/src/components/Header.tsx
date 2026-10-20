import React from 'react';
import { ThemeToggle } from './ThemeToggle';
import { ShieldCheck } from 'lucide-react';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({
  title = 'ForgeTeam AI',
  subtitle,
}) => {
  return (
    <header className="h-16 px-8 border-b border-slate-800 bg-slate-900/40 backdrop-blur-sm flex items-center justify-between shrink-0">
      <div>
        <h2 className="text-sm font-semibold text-slate-100">{title}</h2>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Local Sandbox Active</span>
        </div>

        <ThemeToggle />
      </div>
    </header>
  );
};
