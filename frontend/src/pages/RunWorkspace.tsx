import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Download,
  Ban,
  RefreshCw,
  Layers,
  CheckCircle2,
  FileCheck2,
  CheckSquare,
  FileText,
  Activity,
  Code2,
  Compass,
  Workflow,
  Sparkles,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { api } from '../api/client';
import {
  AgentRun,
  AgentEvent,
  Artifact,
  ArtifactContent,
  TesterOutput
} from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { AgentCard } from '../components/AgentCard';
import { CodeViewer } from '../components/CodeViewer';
import { FileTree } from '../components/FileTree';
import { ReviewFindingsList } from '../components/ReviewFindingsList';
import { TestSummaryView } from '../components/TestSummaryView';

type WorkspaceTab = 'overview' | 'plan' | 'activity' | 'code' | 'review' | 'tests' | 'report';

const STAGES = ['planner', 'architect', 'developer', 'reviewer', 'tester', 'coordinator'];

export const RunWorkspace: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();

  const [run, setRun] = useState<AgentRun | null>(null);
  const [logs, setLogs] = useState<AgentEvent[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('overview');

  // Code explorer state
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
  const [artifactContent, setArtifactContent] = useState<ArtifactContent | null>(null);
  const [loadingContent, setLoadingContent] = useState(false);

  // Parsed reports state
  const [planData, setPlanData] = useState<any>(null);
  const [archData, setArchData] = useState<any>(null);
  const [reviewData, setReviewData] = useState<any>(null);
  const [testData, setTestData] = useState<TesterOutput | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  const pollIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (!runId) return;

    fetchRunData();

    // Start polling for updates every 2.5 seconds
    pollIntervalRef.current = window.setInterval(() => {
      fetchRunData(false);
    }, 2500);

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [runId]);

  // Stop polling once the run hits a terminal state
  useEffect(() => {
    if (run && ['completed', 'completed_with_issues', 'failed', 'cancelled'].includes(run.status)) {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
  }, [run?.status]);

  const fetchRunData = async (showLoading = true) => {
    if (!runId) return;
    if (showLoading) setLoading(true);

    try {
      const [runData, logsData, artifactsData] = await Promise.all([
        api.getRun(runId),
        api.getRunLogs(runId).catch(() => []),
        api.getRunArtifacts(runId).catch(() => []),
      ]);

      setRun(runData);
      setLogs(logsData);
      setArtifacts(artifactsData);

      // Auto-select first source file if none selected
      if (!selectedArtifact && artifactsData.length > 0) {
        const firstPy = artifactsData.find((a) => a.relative_path.endsWith('.py')) || artifactsData[0];
        handleSelectArtifact(firstPy);
      }

      // Check for report artifacts to populate specialized tabs
      await loadParsedReports(artifactsData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch run data');
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const loadParsedReports = async (artifactsList: Artifact[]) => {
    if (!runId) return;

    for (const a of artifactsList) {
      try {
        if (a.relative_path === 'plan.json' && !planData) {
          const res = await api.getArtifactContent(runId, a.id);
          setPlanData(JSON.parse(res.content));
        } else if (a.relative_path === 'architecture.json' && !archData) {
          const res = await api.getArtifactContent(runId, a.id);
          setArchData(JSON.parse(res.content));
        } else if (a.relative_path === 'review_report.json' && !reviewData) {
          const res = await api.getArtifactContent(runId, a.id);
          setReviewData(JSON.parse(res.content));
        } else if (a.relative_path === 'test_report.json' && !testData) {
          const res = await api.getArtifactContent(runId, a.id);
          setTestData(JSON.parse(res.content));
        }
      } catch (e) {
        // Continue if parsing individual report fails
      }
    }
  };

  const handleSelectArtifact = async (artifact: Artifact) => {
    if (!runId) return;
    setSelectedArtifact(artifact);
    setLoadingContent(true);
    try {
      const content = await api.getArtifactContent(runId, artifact.id);
      setArtifactContent(content);
    } catch (err: any) {
      setArtifactContent({
        id: artifact.id,
        relative_path: artifact.relative_path,
        artifact_type: artifact.artifact_type,
        content: `Error loading artifact content: ${err.message}`,
      });
    } finally {
      setLoadingContent(false);
    }
  };

  const handleCancel = async () => {
    if (!runId || !window.confirm('Are you sure you want to cancel this agent run?')) return;
    setCancelling(true);
    try {
      await api.cancelRun(runId);
      await fetchRunData(false);
    } catch (err: any) {
      alert(`Cancel failed: ${err.message}`);
    } finally {
      setCancelling(false);
    }
  };

  if (loading && !run) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-slate-400 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
        <p className="text-sm">Connecting to agent workflow engine...</p>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="p-8 text-center space-y-4">
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs inline-flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error || 'Run not found'}</span>
        </div>
        <div>
          <Link to="/" className="text-xs text-indigo-400 underline">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  // Derive stage progression index
  const currentStageIdx = STAGES.indexOf((run.current_stage || '').toLowerCase());
  const progressPercent = Math.max(
    5,
    ['completed', 'completed_with_issues'].includes(run.status)
      ? 100
      : currentStageIdx >= 0
      ? Math.round(((currentStageIdx + 1) / STAGES.length) * 100)
      : 10
  );

  return (
    <div className="space-y-6">
      {/* Run Header Bar */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-slate-100">
              {run.project_name || 'Project Run'}
            </h2>
            <StatusBadge status={run.status} />
            {run.selected_model && (
              <span className="px-2.5 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 text-[11px] font-mono flex items-center gap-1 font-medium">
                <Sparkles className="w-3 h-3 text-indigo-500" />
                {run.selected_model.startsWith('groq') ? 'Groq LPU (Llama 3.3)' : run.selected_model.startsWith('ollama') ? 'Local Model (Qwen)' : 'Enterprise Engine'}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 font-mono flex items-center gap-2">
            <span>Run ID: {run.id}</span>
            <span>•</span>
            <span>Revisions: {run.retry_count}/2</span>
            <span>•</span>
            <span>Artifacts: {artifacts.length}</span>
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5">
          {artifacts.length > 0 && (
            <a
              href={api.getDownloadZipUrl(run.id)}
              download
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-indigo-400" />
              <span>Download ZIP</span>
            </a>
          )}

          {['queued', 'running'].includes(run.status) && (
            <button
              onClick={handleCancel}
              disabled={cancelling}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-rose-600/10 hover:bg-rose-600/20 text-rose-300 text-xs font-semibold border border-rose-500/30 transition-colors"
            >
              <Ban className="w-3.5 h-3.5" />
              <span>Cancel Run</span>
            </button>
          )}

          <button
            onClick={() => fetchRunData(false)}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-200 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 transition-colors"
            title="Refresh state"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Real Stage Progress Bar */}
      <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/40 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-600 dark:text-slate-400 font-medium">
            Active Agent Stage:{' '}
            <span className="text-indigo-600 dark:text-indigo-400 uppercase font-mono font-semibold">
              {run.current_stage || 'Initializing'}
            </span>
          </span>
          <span className="text-slate-500 dark:text-slate-400 font-mono font-semibold">{progressPercent}%</span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-950 overflow-hidden border border-slate-200 dark:border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 via-indigo-400 to-emerald-400 transition-all duration-500 rounded-full"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Multi-Agent Team Status Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
        {(['planner', 'architect', 'developer', 'reviewer', 'tester', 'coordinator'] as const).map(
          (role) => {
            const isCurrent = run.current_stage?.toLowerCase() === role;
            const stageIndex = STAGES.indexOf(role);
            let agentStatus: 'idle' | 'running' | 'completed' | 'failed' | 'waiting' = 'idle';

            if (run.status === 'failed' && isCurrent) {
              agentStatus = 'failed';
            } else if (isCurrent && ['running', 'queued'].includes(run.status)) {
              agentStatus = 'running';
            } else if (
              ['completed', 'completed_with_issues'].includes(run.status) ||
              currentStageIdx > stageIndex
            ) {
              agentStatus = 'completed';
            }

            return (
              <AgentCard
                key={role}
                role={role}
                status={agentStatus}
                isCurrent={isCurrent}
              />
            );
          }
        )}
      </div>

      {/* Workspace Tabs Navigation */}
      <div className="border-b border-slate-800 flex items-center gap-2 overflow-x-auto text-xs font-medium">
        {[
          { id: 'overview', label: 'Overview', icon: Workflow },
          { id: 'plan', label: 'Plan & Architecture', icon: Compass },
          { id: 'activity', label: 'Agent Activity', icon: Activity, count: logs.length },
          { id: 'code', label: 'Generated Code', icon: Code2, count: artifacts.length },
          { id: 'review', label: 'Code Review', icon: FileCheck2 },
          { id: 'tests', label: 'Test Report', icon: CheckSquare },
          { id: 'report', label: 'Final Report', icon: FileText },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as WorkspaceTab)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors whitespace-nowrap ${
                isActive
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-400 font-mono">
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      <div className="min-h-[450px]">
        {/* 1. OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Original User Request
              </h3>
              <p className="text-sm text-slate-200 leading-relaxed font-sans bg-slate-950 p-4 rounded-xl border border-slate-800/80">
                {run.original_request}
              </p>
            </div>

            {run.error_summary && (
              <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs space-y-1">
                <div className="font-semibold flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-rose-400" />
                  <span>Execution Issue</span>
                </div>
                <div className="font-mono text-[11px] leading-relaxed">{run.error_summary}</div>
              </div>
            )}

            {/* Quick Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40">
                <div className="text-xs text-slate-400">Generated Files</div>
                <div className="text-xl font-bold text-slate-100 mt-1 font-mono">
                  {artifacts.length}
                </div>
              </div>
              <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40">
                <div className="text-xs text-slate-400">Revision Loops</div>
                <div className="text-xl font-bold text-slate-100 mt-1 font-mono">
                  {run.retry_count} / 2
                </div>
              </div>
              <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40">
                <div className="text-xs text-slate-400">Agent Events Logged</div>
                <div className="text-xl font-bold text-slate-100 mt-1 font-mono">
                  {logs.length}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 2. PLAN & ARCHITECTURE TAB */}
        {activeTab === 'plan' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Planner Section */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-sky-400" />
                <h3 className="text-sm font-semibold text-slate-200">Planner Specifications</h3>
              </div>

              {planData ? (
                <div className="space-y-4 text-xs">
                  <div>
                    <h4 className="text-slate-400 uppercase font-semibold text-[10px] mb-1">
                      Summary
                    </h4>
                    <p className="text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
                      {planData.project_summary}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-slate-400 uppercase font-semibold text-[10px] mb-1.5">
                      Requirements Checklist
                    </h4>
                    <ul className="space-y-1.5 bg-slate-950 p-3 rounded-lg border border-slate-800">
                      {planData.requirements?.map((req: string, idx: number) => (
                        <li key={idx} className="flex items-center gap-2 text-slate-300">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                          <span>{req}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-slate-400 uppercase font-semibold text-[10px] mb-1.5">
                      Task Graph
                    </h4>
                    <div className="space-y-1.5">
                      {planData.task_list?.map((task: any, idx: number) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between"
                        >
                          <span className="font-mono text-slate-300">
                            [{task.id}] {task.title}
                          </span>
                          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                            {task.priority}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-500">
                  Plan in progress or awaiting planner output...
                </div>
              )}
            </div>

            {/* Architecture Section */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-semibold text-slate-200">System Architecture</h3>
              </div>

              {archData ? (
                <div className="space-y-4 text-xs">
                  <div>
                    <h4 className="text-slate-400 uppercase font-semibold text-[10px] mb-1">
                      Architectural Pattern
                    </h4>
                    <p className="text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
                      {archData.architecture_summary}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-slate-400 uppercase font-semibold text-[10px] mb-1.5">
                      API Interface Outline
                    </h4>
                    <div className="space-y-1.5 max-h-56 overflow-y-auto">
                      {archData.api_outline?.map((api: any, idx: number) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between gap-2"
                        >
                          <div className="flex items-center gap-2 font-mono">
                            <span className="text-indigo-400 font-bold">{api.method}</span>
                            <span className="text-slate-300">{api.path}</span>
                          </div>
                          <span className="text-[11px] text-slate-500 truncate max-w-xs">
                            {api.description}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-slate-400 uppercase font-semibold text-[10px] mb-1.5">
                      Planned File Tree
                    </h4>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300 max-h-40 overflow-y-auto space-y-1">
                      {archData.file_tree?.map((path: string, idx: number) => (
                        <div key={idx} className="truncate">
                          {path}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-500">
                  Architecture in progress or awaiting architect output...
                </div>
              )}
            </div>
          </div>
        )}

        {/* 3. AGENT ACTIVITY TAB */}
        {activeTab === 'activity' && (
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Chronological Multi-Agent Collaboration Log
            </h3>

            <div className="space-y-3">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="p-4 rounded-xl border border-slate-800 bg-slate-950 flex items-start gap-4"
                >
                  <div className="text-[11px] font-mono text-slate-500 shrink-0 pt-0.5">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </div>

                  <div className="space-y-1 flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 font-mono">
                        [{log.agent_name}]
                      </span>
                      <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                        {log.event_type}
                      </span>
                      <StatusBadge status={log.status} size="sm" />
                    </div>

                    {log.message && (
                      <p className="text-xs text-slate-300 leading-relaxed font-sans pt-1">
                        {log.message}
                      </p>
                    )}
                  </div>
                </div>
              ))}

              {logs.length === 0 && (
                <div className="p-8 text-center text-xs text-slate-500">
                  No activity logs recorded yet.
                </div>
              )}
            </div>
          </div>
        )}

        {/* 4. GENERATED CODE EXPLORER TAB */}
        {activeTab === 'code' && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 h-[600px]">
            {/* File Tree Panel */}
            <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/40 flex flex-col h-full">
              <div className="flex items-center justify-between pb-3 mb-2 border-b border-slate-800 text-xs font-semibold text-slate-300">
                <span>Project Files ({artifacts.length})</span>
              </div>
              <div className="flex-1 overflow-y-auto">
                <FileTree
                  artifacts={artifacts}
                  selectedFile={selectedArtifact?.id || null}
                  onSelectFile={handleSelectArtifact}
                />
              </div>
            </div>

            {/* Code Viewer Panel */}
            <div className="md:col-span-2 lg:col-span-3 h-full">
              {loadingContent ? (
                <div className="flex flex-col items-center justify-center h-full rounded-2xl border border-slate-800 bg-slate-950 text-slate-400 gap-2">
                  <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
                  <span className="text-xs">Reading artifact...</span>
                </div>
              ) : artifactContent ? (
                <CodeViewer
                  code={artifactContent.content}
                  filePath={artifactContent.relative_path}
                />
              ) : (
                <div className="flex items-center justify-center h-full rounded-2xl border border-slate-800 bg-slate-950 text-slate-500 text-xs">
                  Select a generated file from the tree to inspect source code.
                </div>
              )}
            </div>
          </div>
        )}

        {/* 5. CODE REVIEW TAB */}
        {activeTab === 'review' && (
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40">
            <ReviewFindingsList
              findings={reviewData?.findings || []}
              approval={reviewData?.approval}
              summary={reviewData?.summary}
            />
          </div>
        )}

        {/* 6. TESTS TAB */}
        {activeTab === 'tests' && (
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40">
            <TestSummaryView testData={testData} />
          </div>
        )}

        {/* 7. FINAL REPORT TAB */}
        {activeTab === 'report' && (
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-sm font-semibold text-slate-200">Final Verification Report</h3>
              {artifacts.length > 0 && (
                <a
                  href={api.getDownloadZipUrl(run.id)}
                  download
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Project ZIP</span>
                </a>
              )}
            </div>

            {run.final_summary ? (
              <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 font-mono text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
                {run.final_summary}
              </div>
            ) : (
              <div className="p-12 text-center text-xs text-slate-500">
                Final report will be compiled by the Coordinator once all agent loops conclude.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
