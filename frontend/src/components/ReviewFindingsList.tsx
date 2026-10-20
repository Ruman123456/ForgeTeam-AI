import React from 'react';
import { AlertCircle, AlertTriangle, Info, CheckCircle2, ShieldAlert } from 'lucide-react';
import { ReviewFinding } from '../types';

interface ReviewFindingsListProps {
  findings: ReviewFinding[];
  approval?: boolean;
  summary?: string;
}

export const ReviewFindingsList: React.FC<ReviewFindingsListProps> = ({
  findings,
  approval,
  summary,
}) => {
  const errors = findings.filter((f) => f.severity === 'error');
  const warnings = findings.filter((f) => f.severity === 'warning');
  const infos = findings.filter((f) => f.severity === 'info');

  return (
    <div className="space-y-4">
      {/* Review verdict banner */}
      {summary && (
        <div
          className={`p-4 rounded-xl border flex items-start gap-3 ${
            approval
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
          }`}
        >
          {approval ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          )}
          <div>
            <div className="font-semibold text-sm">
              {approval ? 'Implementation Approved' : 'Revision Recommended'}
            </div>
            <div className="text-xs mt-1 text-slate-300 leading-relaxed">{summary}</div>
            <div className="flex gap-4 mt-2 text-xs">
              <span className="text-rose-400 font-medium">{errors.length} Errors</span>
              <span className="text-amber-400 font-medium">{warnings.length} Warnings</span>
              <span className="text-sky-400 font-medium">{infos.length} Info</span>
            </div>
          </div>
        </div>
      )}

      {/* Findings items */}
      <div className="space-y-2.5">
        {findings.map((finding, idx) => {
          let Icon = Info;
          let badgeClass = 'bg-sky-500/10 text-sky-400 border-sky-500/30';

          if (finding.severity === 'error') {
            Icon = AlertCircle;
            badgeClass = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
          } else if (finding.severity === 'warning') {
            Icon = AlertTriangle;
            badgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
          }

          return (
            <div
              key={idx}
              className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-900 transition-colors"
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border uppercase tracking-wider ${badgeClass}`}
                  >
                    <Icon className="w-3 h-3" />
                    <span>{finding.severity}</span>
                  </span>
                  <span className="text-xs text-slate-400 uppercase font-mono px-2 py-0.5 rounded bg-slate-800">
                    {finding.category || 'general'}
                  </span>
                </div>

                {finding.file_path && (
                  <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    {finding.file_path}
                    {finding.line_number ? `:${finding.line_number}` : ''}
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-200 leading-relaxed font-medium mb-1.5">
                {finding.description}
              </p>

              {finding.suggestion && (
                <div className="mt-2 text-xs bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80 text-emerald-300 font-mono">
                  <span className="text-slate-500 mr-2">Suggestion:</span>
                  {finding.suggestion}
                </div>
              )}
            </div>
          );
        })}

        {findings.length === 0 && (
          <div className="p-8 text-center text-xs text-slate-500 border border-slate-800/60 rounded-xl">
            No code review findings recorded yet.
          </div>
        )}
      </div>
    </div>
  );
};
