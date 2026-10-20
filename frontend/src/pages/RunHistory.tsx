import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  History,
  Workflow,
  Sparkles,
  ArrowRight,
  Filter,
  Loader2,
  Calendar,
  FileCode
} from 'lucide-react';
import { api } from '../api/client';
import { AgentRun } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const RunHistory: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const projectIdParam = searchParams.get('project_id') || '';
  const statusParam = searchParams.get('status') || '';

  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRuns();
  }, [projectIdParam, statusParam]);

  const loadRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRuns(
        projectIdParam || undefined,
        statusParam || undefined,
        0,
        50
      );
      setRuns(data.runs);
    } catch (err: any) {
      setError(err.message || 'Failed to load run history');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilter = (status: string) => {
    if (status) {
      searchParams.set('status', status);
    } else {
      searchParams.delete('status');
    }
    setSearchParams(searchParams);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            <History className="w-6 h-6 text-indigo-400" />
            <span>Agent Run History</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Chronological archive of all multi-agent software runs, revision iterations, and outputs.
          </p>
        </div>

        {/* Filter Badges */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={statusParam}
            onChange={(e) => handleStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="completed_with_issues">Completed with Issues</option>
            <option value="running">Running</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] text-slate-400 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          <p className="text-sm">Fetching historical runs from database...</p>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs">
          {error}
        </div>
      ) : runs.length === 0 ? (
        <div className="p-12 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/20 space-y-3">
          <Workflow className="w-8 h-8 text-slate-600 mx-auto" />
          <h4 className="text-sm font-semibold text-slate-200">No runs match criteria</h4>
          <p className="text-xs text-slate-400">
            {projectIdParam || statusParam
              ? 'Try resetting the filters above.'
              : 'Launch a project workflow to generate your first collaborative multi-agent run.'}
          </p>
          <Link
            to="/projects/new"
            className="inline-block px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-medium"
          >
            Create New Run
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {runs.map((run) => (
            <Link
              key={run.id}
              to={`/runs/${run.id}`}
              className="block p-5 rounded-2xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 hover:border-slate-700 transition-all group"
            >
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-sm text-slate-100 group-hover:text-indigo-300 transition-colors">
                      {run.project_name || 'Project Run'}
                    </span>
                    <StatusBadge status={run.status} size="sm" />
                    {run.demo_mode && (
                      <span className="px-2 py-0.5 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-400 text-[10px] font-mono flex items-center gap-1">
                        <Sparkles className="w-2.5 h-2.5" />
                        Demo
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-1 max-w-xl">
                    {run.original_request}
                  </p>
                </div>

                <div className="flex items-center gap-6 text-xs text-slate-400 font-mono">
                  <div className="hidden md:flex items-center gap-1.5">
                    <FileCode className="w-3.5 h-3.5 text-slate-500" />
                    <span>{run.artifact_count} artifacts</span>
                  </div>

                  <div className="hidden sm:flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span>{new Date(run.created_at).toLocaleDateString()}</span>
                  </div>

                  <div className="p-1 rounded-lg text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all">
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};
