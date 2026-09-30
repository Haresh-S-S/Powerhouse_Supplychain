import React from 'react';
import { X, Gauge, CheckCircle2, ShieldAlert, Info, Layers } from 'lucide-react';
import Button from '../ui/Button';

export default function GreenScoreExplainModal({
  isOpen,
  onClose,
  scoreDetail,
}) {
  if (!isOpen || !scoreDetail) return null;

  const score = scoreDetail.score ?? 72;
  const rating = scoreDetail.rating || 'Good';
  const components = scoreDetail.components || [];

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-xl shadow-2xl p-6 relative flex flex-col max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-950/80 border border-teal-800 text-teal-400 flex items-center justify-center shrink-0">
              <Gauge className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-100 text-base">
                Green Operations Score Breakdown
              </h3>
              <p className="text-xs text-slate-400">
                Multi-Pillar Deterministic Calculation Engine
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Score Hero Banner */}
        <div className="my-4 p-4 rounded-xl bg-[#141C2B] border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Overall Score
            </span>
            <div className="flex items-baseline gap-2 mt-0.5">
              <span className="text-3xl font-black text-white">{score}</span>
              <span className="text-xs text-slate-400">/ 100</span>
              <span className="ml-2 px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-950/60 text-teal-400 border border-teal-800">
                {rating}
              </span>
            </div>
          </div>

          <div className="text-right text-[11px] text-slate-400">
            <div>Deterministic Model</div>
            <div className="text-slate-300 font-mono mt-0.5">{scoreDetail.last_updated || 'Live Telemetry'}</div>
          </div>
        </div>

        {/* 5 Pillars Contribution List */}
        <div className="space-y-2.5">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 mb-2">
            <Layers className="w-3.5 h-3.5 text-teal-400" />
            Component Contributions
          </h4>

          {components.map((comp) => (
            <div
              key={comp.name}
              className="p-3 rounded-xl bg-[#0B0F17] border border-slate-800/80 space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200">{comp.name}</span>
                <div className="flex items-center gap-2 font-mono text-xs">
                  <span className="text-slate-400 text-[11px]">Weight: {Math.round(comp.weight * 100)}%</span>
                  <span className="text-teal-400 font-bold">+{comp.contribution} pts</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-teal-500 rounded-full"
                  style={{ width: `${Math.min(100, comp.score)}%` }}
                />
              </div>

              <p className="text-[11px] text-slate-400 leading-relaxed">
                {comp.description}
              </p>
            </div>
          ))}
        </div>

        {/* Notice */}
        <div className="mt-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
          <Info className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
          <span>
            This score reflects operational sustainability and efficiency. It is calculated deterministically from telemetry, verified document vaults, and approved green actions. It is NOT an official government statutory compliance score.
          </span>
        </div>

        {/* Footer */}
        <div className="pt-4 mt-4 border-t border-slate-800 flex justify-end">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
