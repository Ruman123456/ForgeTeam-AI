import React from 'react';
import {
  Compass,
  Layers,
  Code2,
  FileCheck2,
  CheckSquare,
  Workflow,
  Clock,
  CheckCircle2,
  Loader2,
  AlertCircle
} from 'lucide-react';

interface AgentCardProps {
  role: 'planner' | 'architect' | 'developer' | 'reviewer' | 'tester' | 'coordinator';
  status: 'idle' | 'running' | 'completed' | 'failed' | 'waiting';
  message?: string;
  isCurrent?: boolean;
}

const AGENT_CONFIG = {
  planner: {
    title: 'Project Planner',
    description: 'Requirements extraction & task graph breakdown',
    icon: Compass,
    color: 'text-sky-400',
    borderColor: 'border-sky-500/40',
  },
  architect: {
    title: 'System Architect',
    description: 'System modularity, data models & API contracts',
    icon: Layers,
    color: 'text-purple-400',
    borderColor: 'border-purple-500/40',
  },
  developer: {
    title: 'Developer Agent',
    description: 'Source code generation & automated revisions',
    icon: Code2,
    color: 'text-emerald-400',
    borderColor: 'border-emerald-500/40',
  },
  reviewer: {
    title: 'Code Reviewer',
    description: 'Security, logic verification & feedback loops',
    icon: FileCheck2,
    color: 'text-amber-400',
    borderColor: 'border-amber-500/40',
  },
  tester: {
    title: 'Testing Agent',
    description: 'Static analysis, AST checks & test suites',
    icon: CheckSquare,
    color: 'text-teal-400',
    borderColor: 'border-teal-500/40',
  },
  coordinator: {
    title: 'Workflow Coordinator',
    description: 'State management, graph routing & final summary',
    icon: Workflow,
    color: 'text-indigo-400',
    borderColor: 'border-indigo-500/40',
  },
};

export const AgentCard: React.FC<AgentCardProps> = ({
  role,
  status,
  message,
  isCurrent = false,
}) => {
  const config = AGENT_CONFIG[role] || AGENT_CONFIG.coordinator;
  const Icon = config.icon;

  let statusBadge = (
    <span className="flex items-center gap-1 text-xs text-slate-500">
      <Clock className="w-3.5 h-3.5" />
      <span>Idle</span>
    </span>
  );

  if (status === 'running') {
    statusBadge = (
      <span className="flex items-center gap-1 text-xs text-indigo-400 font-medium animate-pulse">
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
        <span>Active</span>
      </span>
    );
  } else if (status === 'completed') {
    statusBadge = (
      <span className="flex items-center gap-1 text-xs text-emerald-400 font-medium">
        <CheckCircle2 className="w-3.5 h-3.5" />
        <span>Done</span>
      </span>
    );
  } else if (status === 'failed') {
    statusBadge = (
      <span className="flex items-center gap-1 text-xs text-rose-400 font-medium">
        <AlertCircle className="w-3.5 h-3.5" />
        <span>Failed</span>
      </span>
    );
  }

  return (
    <div
      className={`rounded-xl border p-3 flex flex-col justify-between transition-all duration-200 min-h-[108px] ${
        isCurrent
          ? `bg-indigo-50/80 dark:bg-slate-900/90 border-indigo-500 shadow-md shadow-indigo-500/10 ring-2 ring-indigo-500/30`
          : 'bg-white/80 dark:bg-slate-900/40 border-slate-200 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700/80'
      }`}
    >
      <div>
        <div className="flex items-center justify-between gap-1.5 mb-2">
          <div className={`p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800/80 ${config.color} shrink-0`}>
            <Icon className="w-4 h-4" />
          </div>
          <div className="shrink-0">{statusBadge}</div>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100 leading-tight">
            {config.title}
          </h4>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-snug">
            {config.description}
          </p>
        </div>
      </div>

      {message && (
        <div className="mt-2 p-1.5 rounded bg-slate-100 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/60 text-[10px] text-slate-700 dark:text-slate-300 font-mono leading-tight truncate">
          {message}
        </div>
      )}
    </div>
  );
};
