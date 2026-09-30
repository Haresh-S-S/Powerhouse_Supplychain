import React from 'react';
import { X, AlertCircle, Clock, ShieldAlert, ArrowRight } from 'lucide-react';

export default function WhyPriorityModal({ isOpen, onClose, priorityItem, onNavigate }) {
  if (!isOpen || !priorityItem) return null;

  const score = priorityItem.priority_score || 85;
  const factors = priorityItem.factors || {
    overdue_status: 50,
    statutory_deadline: 25,
    risk_weight: 17
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="why-priority-title"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-start justify-between gap-4 bg-[#141C2B]/60">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-black text-rose-400 bg-rose-950/80 px-2 py-0.5 rounded border border-rose-800/80 uppercase tracking-wider">
                Top Priority Inspector
              </span>
              <span className="text-[11px] text-amber-400 font-semibold">{priorityItem.deadline}</span>
            </div>
            <h2 id="why-priority-title" className="text-base font-bold text-white tracking-tight leading-snug">
              {priorityItem.what}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 text-xs text-slate-300">
          {/* Priority Score Header Card */}
          <div className="p-4 rounded-xl bg-[#0B0F17] border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Urgency Priority Score</span>
              <span className="text-2xl font-black text-rose-400">{score} <span className="text-xs text-slate-500 font-medium">/ 100</span></span>
            </div>
            <div className="w-10 h-10 rounded-xl bg-rose-950/60 border border-rose-800/60 flex items-center justify-center text-rose-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>

          {/* Factor Breakdown */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Weighted Urgency Factors
            </h3>
            <div className="space-y-1.5">
              {Object.entries(factors).map(([factor, pts]) => (
                <div key={factor} className="p-2.5 rounded-lg bg-[#141C2B] border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-300 capitalize font-medium">
                    {factor.replace(/_/g, ' ')}
                  </span>
                  <span className="font-extrabold text-amber-400">+{pts} pts</span>
                </div>
              ))}
            </div>
          </div>

          {/* Impact Explanation */}
          <div className="p-3.5 rounded-xl bg-[#141C2B] border border-blue-900/40 space-y-1">
            <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider block">
              Business & Regulatory Impact
            </span>
            <p className="text-slate-200 leading-relaxed text-xs">
              {priorityItem.explanation || priorityItem.why}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-[#141C2B]/60 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold cursor-pointer"
          >
            Dismiss
          </button>
          <button
            onClick={() => {
              onClose();
              if (onNavigate && priorityItem.action_url) onNavigate(priorityItem.action_url);
            }}
            className="px-4 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition-colors cursor-pointer flex items-center gap-1.5 shadow-sm shadow-rose-500/20"
          >
            <span>Resolve Priority</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
