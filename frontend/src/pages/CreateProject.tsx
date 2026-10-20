import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  ArrowRight,
  Cpu,
  AlertCircle,
  Loader2,
  Wand2,
  Zap
} from 'lucide-react';
import { api } from '../api/client';

const PRESETS = [
  {
    title: 'Task Management System',
    description: 'Build a task management application with user registration, task creation, priorities, deadlines, and a dashboard.',
    lang: 'python',
    framework: 'fastapi',
  },
  {
    title: 'Authentication & Profile Microservice',
    description: 'Create a secure user authentication service with JWT tokens, password hashing, profile updates, and role-based permissions.',
    lang: 'python',
    framework: 'fastapi',
  },
  {
    title: 'Real-time Metrics Dashboard API',
    description: 'Develop an analytics aggregation backend with data ingestion endpoints, statistics calculation, and SQLite persistence.',
    lang: 'python',
    framework: 'fastapi',
  },
];

export const CreateProject: React.FC = () => {
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('python');
  const [framework, setFramework] = useState('fastapi');
  const [engine, setEngine] = useState<'groq' | 'local'>('groq');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const applyPreset = (preset: typeof PRESETS[0]) => {
    setName(preset.title);
    setDescription(preset.description);
    setLanguage(preset.lang);
    setFramework(preset.framework);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Project name is required');
      return;
    }
    if (description.trim().length < 10) {
      setError('Requirements description must be at least 10 characters');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // 1. Create project
      const project = await api.createProject({
        name: name.trim(),
        description: description.trim(),
        language_preference: language.trim() || undefined,
        framework_preference: framework.trim() || undefined,
      });

      // 2. Start multi-agent run with selected engine
      const run = await api.createRun({
        project_id: project.id,
        demo_mode: false,
        engine: engine,
      });

      // 3. Navigate directly to active run workspace
      navigate(`/runs/${run.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to initialize project and start agents');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100">
          Create Software Project
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Specify your application requirements. ForgeTeam's specialized agents will collaborate to plan, design, code, review, and test the system.
        </p>
      </div>

      {/* Preset Suggestions */}
      <div className="space-y-2.5">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <Wand2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Quick Inspiration Presets</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPreset(p)}
              className="p-3.5 text-left rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/40 hover:border-indigo-400 dark:hover:border-indigo-500/60 hover:bg-indigo-50/50 dark:hover:bg-slate-800/60 hover:shadow-sm transition-all group"
            >
              <div className="text-xs font-semibold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                {p.title}
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                {p.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Project Form */}
      <form onSubmit={handleSubmit} className="space-y-6 bg-white/70 dark:bg-slate-900/40 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            Project Name <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Distributed Task Manager"
            className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            required
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Software Requirements & Features <span className="text-rose-500">*</span>
            </label>
            <span className="text-[11px] text-slate-400 dark:text-slate-500 font-mono">
              {description.length} chars (min 10)
            </span>
          </div>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={5}
            placeholder="Describe the software you want built: modules, API endpoints, data models, priorities, validations, or constraints..."
            className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors leading-relaxed font-sans"
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Language Preference
            </label>
            <input
              type="text"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              placeholder="e.g. python, typescript"
              className="w-full px-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              Framework Preference
            </label>
            <input
              type="text"
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              placeholder="e.g. fastapi, react"
              className="w-full px-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Execution Engine Selector */}
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
              AI Inference Engine
            </span>
            <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
              100% Free • Zero-Cost
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div
              onClick={() => setEngine('groq')}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                engine === 'groq'
                  ? 'border-indigo-500 bg-indigo-50/80 dark:bg-indigo-500/10 text-slate-900 dark:text-slate-100 ring-2 ring-indigo-500/30'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/30 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-500" />
                  <span className="text-xs font-semibold">Groq Cloud (Free Tier)</span>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 font-semibold">
                  Fastest
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                Powered by Llama-3.3-70B on Groq LPUs. Generates complete multi-file code in ~5 seconds with zero hardware load.
              </p>
            </div>

            <div
              onClick={() => setEngine('local')}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                engine === 'local'
                  ? 'border-indigo-500 bg-indigo-50/80 dark:bg-indigo-500/10 text-slate-900 dark:text-slate-100 ring-2 ring-indigo-500/30'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/30 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                  <span className="text-xs font-semibold">Local Ollama Model</span>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-semibold">
                  Offline
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                Runs locally on your machine with qwen2.5-coder:3b. Fully private and works with no internet connection.
              </p>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs shadow-lg shadow-indigo-600/20 transition-all"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Launching Multi-Agent Team...</span>
              </>
            ) : (
              <>
                <Bot className="w-4 h-4" />
                <span>Start Agent Workflow</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
