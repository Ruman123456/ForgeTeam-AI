import React, { useEffect, useState } from 'react';
import {
  Settings,
  Cpu,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Terminal,
  ShieldCheck,
  Loader2,
  Zap,
  Key
} from 'lucide-react';
import { api } from '../api/client';
import { ConfigResponse, OllamaCheckResponse } from '../types';

export const SettingsPage: React.FC = () => {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [ollamaCheck, setOllamaCheck] = useState<OllamaCheckResponse | null>(null);
  const [groqCheck, setGroqCheck] = useState<{ configured: boolean; connected: boolean; model: string; message: string } | null>(null);
  const [checking, setChecking] = useState(false);
  const [checkingGroq, setCheckingGroq] = useState(false);
  const [inputKey, setInputKey] = useState('');
  const [savingKey, setSavingKey] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const handleSaveKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputKey.trim()) return;
    setSavingKey(true);
    setSaveMessage(null);
    try {
      const res = await api.saveGroqKey(inputKey);
      setSaveMessage(res.message);
      if (res.success) {
        setInputKey('');
        const updatedConfig = await api.getConfig();
        setConfig(updatedConfig);
        await handleCheckGroq();
      }
    } catch (err: any) {
      setSaveMessage(`Error saving key: ${err.message}`);
    } finally {
      setSavingKey(false);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await api.getConfig();
      setConfig(data);
    } catch (err) {
      console.error('Config fetch error:', err);
    }
  };

  const handleCheckConnection = async () => {
    setChecking(true);
    try {
      const result = await api.checkOllama();
      setOllamaCheck(result);
      const updatedConfig = await api.getConfig();
      setConfig(updatedConfig);
    } catch (err: any) {
      setOllamaCheck({
        connected: false,
        model_available: false,
        models: [],
        error: err.message || 'Connection test failed',
      });
    } finally {
      setChecking(false);
    }
  };

  const handleCheckGroq = async () => {
    setCheckingGroq(true);
    try {
      const result = await api.checkGroq();
      setGroqCheck(result);
      const updatedConfig = await api.getConfig();
      setConfig(updatedConfig);
    } catch (err: any) {
      setGroqCheck({
        configured: false,
        connected: false,
        model: 'llama-3.3-70b-versatile',
        message: err.message || 'Groq connection check failed',
      });
    } finally {
      setCheckingGroq(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
          <Settings className="w-6 h-6 text-indigo-400" />
          <span>Local Engine & AI Configuration</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Monitor your local Ollama runtime, model availability, and sandbox safety controls.
        </p>
      </div>

      {/* Ollama Status Card */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Ollama Local Inference Service</h3>
              <p className="text-xs text-slate-400">Connects to your locally hosted open-weights models</p>
            </div>
          </div>

          <button
            onClick={handleCheckConnection}
            disabled={checking}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            {checking ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5 text-indigo-400" />
            )}
            <span>Test Connection</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-slate-500 block uppercase text-[10px]">Configured Endpoint</span>
            <span className="text-slate-200 font-semibold">{config?.ollama_base_url || 'http://127.0.0.1:11434'}</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span className="text-slate-500 block uppercase text-[10px]">Target Model</span>
            <span className="text-slate-200 font-semibold">{config?.ollama_model || 'qwen2.5-coder:3b'}</span>
          </div>
        </div>

        {/* Live Diagnostics Feedback */}
        {ollamaCheck && (
          <div
            className={`p-4 rounded-xl border text-xs space-y-2 ${
              ollamaCheck.connected
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
            }`}
          >
            <div className="flex items-center gap-2 font-semibold">
              {ollamaCheck.connected ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Ollama service reached successfully.</span>
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 text-rose-400" />
                  <span>Cannot connect to local Ollama service.</span>
                </>
              )}
            </div>

            {ollamaCheck.connected && (
              <div className="text-[11px] text-slate-300">
                Model Status:{' '}
                {ollamaCheck.model_available ? (
                  <span className="text-emerald-400 font-bold">Installed & Ready</span>
                ) : (
                  <span className="text-amber-400 font-bold">Model not pulled yet</span>
                )}
                {ollamaCheck.models.length > 0 && (
                  <div className="mt-1 font-mono text-slate-400">
                    Installed models on host: {ollamaCheck.models.join(', ')}
                  </div>
                )}
              </div>
            )}

            {ollamaCheck.error && (
              <p className="text-[11px] text-rose-400 leading-relaxed font-mono">
                {ollamaCheck.error}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Groq Cloud Free Tier Card */}
      <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/40 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-500">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Groq Cloud (Free Tier)</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold">
                  Zero Cost
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Ultra-fast cloud inference on LPU hardware (Llama 3.3 70B, ~400 tokens/sec)
              </p>
            </div>
          </div>

          <button
            onClick={handleCheckGroq}
            disabled={checkingGroq}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition-colors"
          >
            {checkingGroq ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-500" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5 text-amber-500" />
            )}
            <span>Test Groq Connection</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-slate-500 block uppercase text-[10px]">Model</span>
            <span className="text-slate-900 dark:text-slate-200 font-semibold">{config?.groq_model || 'llama-3.3-70b-versatile'}</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-slate-500 block uppercase text-[10px]">API Key Status</span>
            <span className={config?.groq_configured ? "text-emerald-500 font-semibold" : "text-amber-500 font-semibold"}>
              {config?.groq_configured ? 'Key Configured (Ready)' : 'Not Set in .env'}
            </span>
          </div>
        </div>

        {/* In-app Key Configuration Form */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-3">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Key className="w-3.5 h-3.5 text-amber-500" />
              <span>Configure Groq API Key</span>
            </label>
            <a
              href="https://console.groq.com/keys"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-600/20 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30 text-xs font-medium hover:bg-indigo-100 transition-colors"
            >
              <span>1. Get Free Key at Groq.com</span>
              <span className="text-[10px]">↗</span>
            </a>
          </div>

          <form onSubmit={handleSaveKey} className="flex flex-col sm:flex-row gap-2">
            <input
              type="password"
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              placeholder="Paste your key here: gsk_..."
              className="flex-1 px-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 font-mono"
            />
            <button
              type="submit"
              disabled={savingKey || !inputKey.trim()}
              className="inline-flex items-center justify-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs transition-colors shadow-sm"
            >
              {savingKey ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <span>Save & Connect</span>
              )}
            </button>
          </form>

          {saveMessage && (
            <div className={`p-2.5 rounded-lg text-xs font-medium ${
              saveMessage.includes('successfully')
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
            }`}>
              {saveMessage}
            </div>
          )}
        </div>

        {groqCheck && (
          <div
            className={`p-4 rounded-xl border text-xs space-y-2 ${
              groqCheck.connected
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-300'
                : 'bg-amber-500/10 border-amber-500/30 text-amber-700 dark:text-amber-300'
            }`}
          >
            <div className="flex items-center gap-2 font-semibold">
              {groqCheck.connected ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>Groq Cloud API connected successfully! Ready to run full multi-agent flows.</span>
                </>
              ) : (
                <>
                  <Key className="w-4 h-4 text-amber-500" />
                  <span>{groqCheck.message}</span>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Execution Safety Policy */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Safe Execution & Sandbox Policy</h3>
            <p className="text-xs text-slate-400">Generated code is strictly treated as untrusted input</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 leading-relaxed space-y-2">
          <p>
            • <strong>No Unsafe Host Execution:</strong> AI-generated source files are never executed directly on the host operating system without container isolation.
          </p>
          <p>
            • <strong>Docker Sandboxing:</strong> When Docker is enabled and available, tests execute in a restricted container with no network access, dropped root capabilities, and memory limits.
          </p>
          <p>
            • <strong>Safe Static Fallback:</strong> When Docker is not detected, ForgeTeam performs Python AST parsing and syntax structure verification, explicitly reporting runtime execution as safely skipped.
          </p>
          <p>
            • <strong>Path Traversal Defense:</strong> All artifact reads, writes, and ZIP archive packaging enforce strict relative path validation to prevent workspace escapes.
          </p>
        </div>
      </div>

      {/* Setup Guide */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Ollama Setup Instructions</h3>
            <p className="text-xs text-slate-400">How to run local models without any paid APIs</p>
          </div>
        </div>

        <div className="space-y-3 text-xs">
          <div>
            <span className="text-slate-400 font-medium">1. Download and install Ollama from official site:</span>
            <div className="mt-1 p-2.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-indigo-300">
              https://ollama.com/download
            </div>
          </div>

          <div>
            <span className="text-slate-400 font-medium">2. Pull the recommended coding model (Qwen 2.5 Coder 3B or DeepSeek Coder):</span>
            <div className="mt-1 p-2.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-emerald-400">
              ollama pull qwen2.5-coder:3b
            </div>
          </div>

          <div>
            <span className="text-slate-400 font-medium">3. Start the Ollama background daemon:</span>
            <div className="mt-1 p-2.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-slate-300">
              ollama serve
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
