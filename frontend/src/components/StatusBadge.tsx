import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, XCircle, Play, Ban } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '', size = 'md' }) => {
  const norm = status.toLowerCase();

  let colorClass = 'bg-slate-800 text-slate-300 border-slate-700';
  let Icon = Clock;
  let label = status;

  if (norm === 'completed') {
    colorClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    Icon = CheckCircle2;
    label = 'Completed';
  } else if (norm === 'completed_with_issues') {
    colorClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = AlertTriangle;
    label = 'Completed with Issues';
  } else if (norm === 'running') {
    colorClass = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30 animate-pulse';
    Icon = Play;
    label = 'Running';
  } else if (norm === 'queued') {
    colorClass = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    Icon = Clock;
    label = 'Queued';
  } else if (norm === 'failed') {
    colorClass = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    Icon = XCircle;
    label = 'Failed';
  } else if (norm === 'cancelled') {
    colorClass = 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    Icon = Ban;
    label = 'Cancelled';
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${colorClass} ${sizeClasses} ${className}`}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{label}</span>
    </span>
  );
};
