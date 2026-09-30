import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle,
  XCircle,
  Eye,
  AlertTriangle,
  RotateCw,
  Clock,
  Sparkles,
  HelpCircle,
  ArrowRight,
} from 'lucide-react';
import Button from '../ui/Button';

export default function HumanApprovalCenter({ recommendations = [], onDecision }) {
  const [selectedRec, setSelectedRec] = useState(null);
  const [processingId, setProcessingId] = useState(null);

  const pendingList = recommendations.filter((r) => r.approval_status === 'PENDING');
  const pastList = recommendations.filter((r) => r.approval_status !== 'PENDING');

  const handleAction = async (recId, decision) => {
    setProcessingId(recId);
    try {
      if (onDecision) {
        await onDecision(recId, decision);
      }
    } finally {
      setProcessingId(null);
      if (selectedRec?.id === recId) {
        setSelectedRec(null);
      }
    }
  };

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Human Approval Center (AI Governance Gate)</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-950/70 text-amber-300 border border-amber-800 font-mono">
              Strict Gate Policy
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            The AI recommends optimal mitigation. The human executive retains sole approval authority.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-xl bg-amber-950/60 text-amber-300 border border-amber-800/60 font-bold">
            {pendingList.length} Action{pendingList.length === 1 ? '' : 's'} Pending Approval
          </span>
        </div>
      </div>

      {/* Pending Approval Cards */}
      <div className="space-y-4">
        {pendingList.map((rec) => {
          const isProcessing = processingId === rec.id;

          return (
            <div
              key={rec.id}
              className="p-4 rounded-xl bg-[#0B1120] border border-amber-900/40 hover:border-amber-700/60 transition-colors space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800 font-mono">
                      {rec.recommendation_type.toUpperCase().replace('_', ' ')}
                    </span>
                    <span className="text-xs font-mono text-slate-400">Created: {rec.created_at}</span>
                  </div>
                  <h4 className="text-sm font-bold text-white">{rec.title}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>
                </div>

                {/* 3 Metric Pills */}
                <div className="grid grid-cols-3 gap-2 shrink-0">
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[9px] uppercase font-bold text-slate-400 block">Exp. Cost</span>
                    <span className="text-xs font-mono font-bold text-amber-400">
                      ${rec.expected_cost_usd?.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[9px] uppercase font-bold text-slate-400 block">Delay Saved</span>
                    <span className="text-xs font-mono font-bold text-cyan-400">
                      -{rec.expected_delay_reduction_days} days
                    </span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center">
                    <span className="text-[9px] uppercase font-bold text-slate-400 block">Risk Reduction</span>
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      {rec.expected_risk_reduction_pct}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons: APPROVE, REJECT, REVIEW DETAILS */}
              <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
                <button
                  onClick={() => setSelectedRec(rec)}
                  className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold cursor-pointer"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Review AI Justification & "Why?" Details</span>
                </button>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={isProcessing}
                    onClick={() => handleAction(rec.id, 'REJECTED')}
                    className="text-xs border-rose-900 text-rose-300 hover:bg-rose-950/60"
                  >
                    <XCircle className="w-3.5 h-3.5 mr-1" />
                    <span>Reject</span>
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    disabled={isProcessing}
                    onClick={() => handleAction(rec.id, 'APPROVED')}
                    className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-1"
                  >
                    {isProcessing ? (
                      <RotateCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <CheckCircle className="w-3.5 h-3.5" />
                    )}
                    <span>Authorize Action</span>
                  </Button>
                </div>
              </div>
            </div>
          );
        })}

        {pendingList.length === 0 && (
          <div className="p-8 text-center rounded-xl bg-[#0B1120] border border-slate-800 text-xs text-slate-400 flex flex-col items-center justify-center space-y-2">
            <CheckCircle className="w-6 h-6 text-emerald-400" />
            <span className="font-bold text-slate-300">All High-Impact Actions Reviewed</span>
            <span>Zero pending actions requiring human governance sign-off.</span>
          </div>
        )}
      </div>

      {/* Review Details Modal */}
      {selectedRec && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-[#111827] border border-[#1E293B] rounded-2xl max-w-xl w-full p-6 space-y-5 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">
                  AI Recommendation Drilldown
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">{selectedRec.title}</h3>
              </div>
              <button
                onClick={() => setSelectedRec(null)}
                className="text-slate-400 hover:text-white text-sm cursor-pointer p-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-400 font-semibold block mb-1">Operational Description</span>
                <p className="text-slate-200 bg-slate-900/80 p-3 rounded-xl border border-slate-800 leading-relaxed">
                  {selectedRec.description}
                </p>
              </div>

              <div>
                <span className="text-slate-400 font-semibold block mb-1">Why? (Qwen3 Reasoning & Root Cause)</span>
                <div className="text-slate-200 bg-slate-900/80 p-3 rounded-xl border border-slate-800 whitespace-pre-line leading-relaxed font-sans text-xs">
                  {selectedRec.explanation_why}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center pt-1">
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Logistics Cost</span>
                  <span className="text-sm font-bold text-amber-400">${selectedRec.expected_cost_usd?.toLocaleString()}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Delay Compression</span>
                  <span className="text-sm font-bold text-cyan-400">-{selectedRec.expected_delay_reduction_days} days</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Risk Reduction</span>
                  <span className="text-sm font-bold text-emerald-400">{selectedRec.expected_risk_reduction_pct}%</span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAction(selectedRec.id, 'REJECTED')}
                className="text-xs border-rose-900 text-rose-300 hover:bg-rose-950/60"
              >
                Reject Action
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleAction(selectedRec.id, 'APPROVED')}
                className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                Approve & Execute
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
