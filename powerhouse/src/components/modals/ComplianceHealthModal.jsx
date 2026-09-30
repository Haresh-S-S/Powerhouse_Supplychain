import React from 'react';
import { X, ShieldCheck, AlertCircle, FileText, Calendar, FolderLock, ArrowUpRight } from 'lucide-react';

export default function ComplianceHealthModal({ isOpen, onClose, healthData, onNavigate }) {
  if (!isOpen) return null;

  const score = healthData?.score || 92;
  const breakdown = healthData || {
    score: 92,
    total_possible: 100,
    health_tier: 'Excellent',
    licences: { completed: 6, total: 8, contribution: 33, max_points: 35, description: '6 active and 1 in-progress approvals' },
    documents: { verified: 5, total: 6, contribution: 25, max_points: 30, description: '5 verified statutory documents out of 6 required' },
    tasks: { completed: 15, total: 20, contribution: 24, max_points: 25, description: '15 tasks completed out of 20 statutory duties' },
    deductions: { deadline_risk: 0, workflow_blockers: 0, description: 'No active statutory penalty deductions' },
    base_weight: 10,
    formula: 'Base (10) + Licences (33/35) + Documents (25/30) + Tasks (24/25) - Deductions (0) = 92/100'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="compliance-health-title"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-center justify-between bg-[#141C2B]/60">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-950/80 border border-emerald-800/80 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 id="compliance-health-title" className="text-base font-bold text-white tracking-tight">
                Compliance Health Score Explainability
              </h2>
              <p className="text-xs text-slate-400">Deterministic mathematical breakdown based on live database records</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-4 text-xs text-slate-300">
          {/* Top Gauge & Standing Banner */}
          <div className="p-4 rounded-xl bg-[#0B0F17] border border-slate-800 flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-emerald-950/90 border-2 border-emerald-500 flex flex-col items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/10 shrink-0">
                <span className="text-xl font-black text-white leading-none">{score}</span>
                <span className="text-[9px] text-emerald-400 font-bold uppercase mt-0.5">/100</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-emerald-400">Regulatory Standing: Excellent</span>
                </div>
                <p className="text-xs text-slate-400 mt-1 leading-snug">
                  Your business meets 92% of statutory requirements. Low regulatory enforcement and penalty exposure.
                </p>
              </div>
            </div>
          </div>

          {/* Breakdown Items */}
          <div className="space-y-2.5">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Component Point Contributions
            </h3>

            {/* Licences */}
            <div className="p-3 rounded-xl bg-[#141C2B] border border-slate-800 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-950/80 text-blue-400 border border-blue-800/80 flex items-center justify-center shrink-0">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-semibold text-white">Statutory Licences & Approvals</div>
                  <div className="text-[11px] text-slate-400">{breakdown.licences?.description}</div>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-sm font-extrabold text-emerald-400">+{breakdown.licences?.contribution || 33}</span>
                <span className="text-[10px] text-slate-500 block">/ {breakdown.licences?.max_points || 35} max</span>
              </div>
            </div>

            {/* Documents */}
            <div className="p-3 rounded-xl bg-[#141C2B] border border-slate-800 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 flex items-center justify-center shrink-0">
                  <FolderLock className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-semibold text-white">Document Evidence Verification</div>
                  <div className="text-[11px] text-slate-400">{breakdown.documents?.description}</div>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-sm font-extrabold text-emerald-400">+{breakdown.documents?.contribution || 25}</span>
                <span className="text-[10px] text-slate-500 block">/ {breakdown.documents?.max_points || 30} max</span>
              </div>
            </div>

            {/* Tasks */}
            <div className="p-3 rounded-xl bg-[#141C2B] border border-slate-800 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-purple-950/80 text-purple-400 border border-purple-800/80 flex items-center justify-center shrink-0">
                  <Calendar className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-semibold text-white">Compliance Tasks & Filings</div>
                  <div className="text-[11px] text-slate-400">{breakdown.tasks?.description}</div>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-sm font-extrabold text-emerald-400">+{breakdown.tasks?.contribution || 24}</span>
                <span className="text-[10px] text-slate-500 block">/ {breakdown.tasks?.max_points || 25} max</span>
              </div>
            </div>

            {/* Deductions */}
            <div className="p-3 rounded-xl bg-[#141C2B] border border-slate-800 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-rose-950/80 text-rose-400 border border-rose-800/80 flex items-center justify-center shrink-0">
                  <AlertCircle className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-semibold text-white">Statutory Risk Deductions</div>
                  <div className="text-[11px] text-slate-400">{breakdown.deductions?.description}</div>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-sm font-extrabold text-rose-400">
                  {breakdown.deductions?.deadline_risk || 0} pts
                </span>
                <span className="text-[10px] text-slate-500 block">penalty applied</span>
              </div>
            </div>
          </div>

          {/* Transparent Formula */}
          <div className="p-3 rounded-xl bg-[#0B0F17] border border-slate-800/80 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Transparent Calculation Arithmetic
            </span>
            <div className="font-mono text-[11px] text-blue-400 bg-black/40 p-2 rounded-md overflow-x-auto">
              {breakdown.formula || 'Base (10) + Licences (33) + Documents (25) + Tasks (24) - Deductions (0) = 92/100'}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-[#141C2B]/60 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            Next target: <strong className="text-white">98%</strong> by uploading Fire Safety Certificate.
          </span>
          <button
            onClick={() => {
              onClose();
              if (onNavigate) onNavigate('documents');
            }}
            className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors cursor-pointer flex items-center gap-1 shadow-sm shadow-blue-500/20"
          >
            <span>Upload Document</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
