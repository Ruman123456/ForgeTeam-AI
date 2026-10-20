import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FolderGit2,
  Workflow,
  CheckCircle2,
  XCircle,
  PlusCircle,
  ArrowRight,
  Cpu,
  Layers,
  Sparkles,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { api } from '../api/client';
import { DashboardStats, Project, ConfigResponse } from '../types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, projectsData, configData] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getProjects(0, 5).catch(() => ({ projects: [], total: 0 })),
        api.getConfig().catch(() => null),
      ]);
      setStats(statsData);
      setProjects(projectsData.projects);
      setConfig(configData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickRun = async (projectId: string) => {
    try {
      const run = await api.createRun({
        project_id: projectId,
        demo_mode: true, // safe default for quick test
      });
      navigate(`/runs/${run.id}`);
    } catch (err: any) {
      alert(`Could not start run: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-slate-400 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
        <p className="text-sm">Loading workspace dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Welcome Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">
            Multi-Agent Software Forge
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Autonomous local engineering team orchestrating planning, architecture, coding, review, and verification.
          </p>
        </div>

        <Link
          to="/projects/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 transition-all"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Project</span>
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Total Projects</div>
            <div className="text-2xl font-bold text-slate-100 mt-1.5">
              {stats?.total_projects ?? 0}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 text-indigo-400">
            <FolderGit2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Total Runs</div>
            <div className="text-2xl font-bold text-slate-100 mt-1.5">
              {stats?.total_runs ?? 0}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/80 text-sky-400">
            <Workflow className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Completed Runs</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1.5">
              {stats?.completed_runs ?? 0}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Failed Runs</div>
            <div className="text-2xl font-bold text-rose-400 mt-1.5">
              {stats?.failed_runs ?? 0}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-rose-500/10 text-rose-400">
            <XCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Engine Status Banner */}
      <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-600/10 text-indigo-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Local AI Backend</div>
            <div className="text-xs text-slate-400 mt-0.5">
              Configured endpoint: <span className="font-mono text-slate-300">{config?.ollama_base_url || 'http://127.0.0.1:11434'}</span>
              {' • '}
              Model: <span className="font-mono text-slate-300">{config?.ollama_model || 'qwen2.5-coder:3b'}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {config?.ollama_connected ? (
            <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 text-xs font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Local Ollama Active
            </span>
          ) : config?.groq_configured ? (
            <span className="px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30 text-xs font-medium flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
              Groq Cloud LPU Ready
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 text-xs font-medium flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              Dual Engine System Ready
            </span>
          )}

          <Link
            to="/settings"
            className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-medium ml-2"
          >
            Configure
          </Link>
        </div>
      </div>

      {/* Recent Projects Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
            Recent Projects
          </h3>
          <Link
            to="/projects/new"
            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
          >
            <span>Create another</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {projects.length === 0 ? (
          <div className="p-12 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/20 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto">
              <Layers className="w-6 h-6" />
            </div>
            <h4 className="text-sm font-semibold text-slate-200">No projects yet</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
              Create your first project idea to assemble the multi-agent AI engineering team.
            </p>
            <Link
              to="/projects/new"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Create First Project</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((project) => (
              <div
                key={project.id}
                className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 hover:bg-slate-900 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <h4 className="font-semibold text-sm text-slate-100 truncate">
                      {project.name}
                    </h4>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                      {project.run_count} runs
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed mb-4">
                    {project.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                    <span>{new Date(project.created_at).toLocaleDateString()}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleQuickRun(project.id)}
                      className="px-2.5 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 text-xs font-medium border border-indigo-500/30 transition-colors"
                    >
                      Run Team
                    </button>
                    <Link
                      to={`/runs?project_id=${project.id}`}
                      className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                      title="View Project Runs"
                    >
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
