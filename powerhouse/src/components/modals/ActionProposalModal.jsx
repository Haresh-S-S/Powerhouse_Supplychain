import React, { useState } from 'react';
import { X, ArrowRight, ShieldCheck, UserCheck } from 'lucide-react';

export default function ActionProposalModal({ isOpen, onClose, proposal, onConfirm }) {
  const [isProcessing, setIsProcessing] = useState(false);

  if (!isOpen || !proposal) return null;

  const handleConfirm = async () => {
    setIsProcessing(true);
    try {
      if (onConfirm) await onConfirm(proposal);
    } finally {
      setIsProcessing(false);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="proposal-modal-title"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-start justify-between gap-4 bg-[#141C2B]/60">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-purple-400 bg-purple-950/80 px-2 py-0.5 rounded border border-purple-800/80 uppercase tracking-wider">
                Human-in-the-Loop Proposal
              </span>
              <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/80">
                {proposal.risk_level || 'Low Risk'}
              </span>
            </div>
            <h2 id="proposal-modal-title" className="text-base font-bold text-white tracking-tight">
              {proposal.title || 'Review Proposed Operational Action'}
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

        {/* Content */}
        <div className="p-5 space-y-4 text-xs text-slate-300">
          {/* AI Security Policy Note */}
          <div className="p-3 rounded-xl bg-[#0B0F17] border border-blue-900/40 text-[11px] text-slate-300 leading-relaxed flex items-start gap-2.5">
            <ShieldCheck className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <span>
              <strong>Security Protocol:</strong> AI agents are restricted from mutating compliance states directly. All mutations require explicit human review and will emit an immutable audit entry for <strong>Mohith K</strong>.
            </span>
          </div>

          {/* Action Details */}
          <div className="space-y-2">
            <div className="p-3 rounded-xl bg-[#141C2B] border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Action Rationale</span>
              <p className="text-slate-200 text-xs leading-relaxed">
                {proposal.reason || 'Document intelligence analysis completed with high confidence. Verification satisfies statutory rule.'}
              </p>
            </div>

            {/* State Transition Delta */}
            <div className="p-3 rounded-xl bg-[#141C2B] border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1.5">State Transition Delta</span>
              <div className="flex items-center justify-around p-2 rounded-lg bg-[#0B0F17] border border-slate-800">
                <div className="text-center">
                  <span className="text-[10px] text-slate-500 block">Previous Status</span>
                  <span className="font-bold text-amber-400 text-xs">Pending</span>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-600" />
                <div className="text-center">
                  <span className="text-[10px] text-slate-500 block">New Status</span>
                  <span className="font-bold text-emerald-400 text-xs">Verified</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-[#141C2B]/60 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={isProcessing}
            className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors cursor-pointer flex items-center gap-1.5 shadow-sm shadow-emerald-500/20 disabled:opacity-50"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>{isProcessing ? 'Executing...' : 'Confirm Action (Mohith K)'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
