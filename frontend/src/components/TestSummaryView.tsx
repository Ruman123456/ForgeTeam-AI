import React from 'react';
import { CheckCircle2, XCircle, AlertCircle, ShieldCheck } from 'lucide-react';
import { TesterOutput } from '../types';

interface TestSummaryViewProps {
  testData?: TesterOutput | null;
}

export const TestSummaryView: React.FC<TestSummaryViewProps> = ({ testData }) => {
  if (!testData) {
    return (
      <div className="p-8 text-center text-xs text-slate-500 border border-slate-800/60 rounded-xl">
        No test results recorded yet.
      </div>
    );
  }

  const { passed, failed, skipped, summary, execution_method, test_results } = testData;

  return (
    <div className="space-y-4">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/20 text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-400">{passed}</div>
            <div className="text-xs text-slate-400 font-medium">Passed</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-rose-500/20 text-rose-400">
            <XCircle className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-rose-400">{failed}</div>
            <div className="text-xs text-slate-400 font-medium">Failed</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-amber-500/20 text-amber-400">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-amber-400">{skipped}</div>
            <div className="text-xs text-slate-400 font-medium">Skipped</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-slate-800 text-slate-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Execution
            </div>
            <div className="text-xs font-mono text-slate-200 mt-0.5 capitalize">
              {execution_method || 'Static Analysis'}
            </div>
          </div>
        </div>
      </div>

      {/* Summary note */}
      {summary && (
        <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/50 text-xs text-slate-300 leading-relaxed">
          {summary}
        </div>
      )}

      {/* Test details list */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Individual Test Results
        </h4>

        {test_results.map((tr, idx) => {
          let statusColor = 'text-slate-400 border-slate-800 bg-slate-900/40';
          let StatusIcon = AlertCircle;

          if (tr.status === 'passed') {
            statusColor = 'text-emerald-400 border-emerald-500/30 bg-emerald-500/5';
            StatusIcon = CheckCircle2;
          } else if (tr.status === 'failed') {
            statusColor = 'text-rose-400 border-rose-500/30 bg-rose-500/5';
            StatusIcon = XCircle;
          }

          return (
            <div
              key={idx}
              className={`p-3 rounded-lg border flex items-start justify-between gap-3 ${statusColor}`}
            >
              <div className="flex items-start gap-2.5">
                <StatusIcon className="w-4 h-4 mt-0.5 shrink-0" />
                <div>
                  <div className="font-mono font-medium text-xs text-slate-200">
                    {tr.test_name}
                  </div>
                  {tr.message && (
                    <div className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                      {tr.message}
                    </div>
                  )}
                </div>
              </div>

              {tr.file_path && (
                <span className="text-[11px] font-mono text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  {tr.file_path}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
