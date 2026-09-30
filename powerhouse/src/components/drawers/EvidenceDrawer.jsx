import React from 'react';
import { X, Database, Clock, Tag, Activity, FileText, CheckCircle2 } from 'lucide-react';
import Button from '../ui/Button';

export default function EvidenceDrawer({
  isOpen,
  onClose,
  opportunity,
}) {
  if (!isOpen || !opportunity) return null;

  const evidenceList = opportunity.evidence || [];

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-xs animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-[#111827] border-l border-[#1E293B] w-full max-w-md h-full shadow-2xl p-6 relative flex flex-col overflow-y-auto animate-in slide-in-from-right duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-teal-950/80 border border-teal-800 text-teal-400 flex items-center justify-center shrink-0">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-100 text-base">
                Evidence Provenance
              </h3>
              <p className="text-xs text-slate-400 truncate max-w-[240px]">
                {opportunity.title}
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

        {/* Content */}
        <div className="py-5 space-y-4 flex-1">
          <div className="p-3 bg-[#141C2B] rounded-xl border border-slate-800 text-xs space-y-1">
            <div className="text-slate-400">Agent Origin:</div>
            <div className="font-bold text-white font-mono">{opportunity.agent_type}</div>
            <div className="text-[11px] text-slate-400 mt-1">
              Category: <span className="text-slate-300 font-semibold">{opportunity.category}</span>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-teal-400" />
              Collected Data Points ({evidenceList.length})
            </h4>

            {evidenceList.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-[#0B0F17] border border-slate-800/90 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200">
                    Observation #{idx + 1}
                  </span>
                  {item.is_demo ? (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/60 text-amber-400 border border-amber-800">
                      DEMO DATA
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-950/60 text-blue-400 border border-blue-800">
                      {item.source_type || 'TELEMETRY'}
                    </span>
                  )}
                </div>

                <p className="text-slate-300 text-xs leading-relaxed">
                  {item.evidence_summary}
                </p>

                <div className="pt-2 border-t border-slate-800/60 space-y-1 text-[11px] text-slate-400">
                  {item.metric && (
                    <div className="flex justify-between">
                      <span>Metric:</span>
                      <span className="font-mono text-slate-200">{item.metric}</span>
                    </div>
                  )}
                  {item.value && (
                    <div className="flex justify-between">
                      <span>Value:</span>
                      <span className="font-mono font-bold text-teal-400">{item.value}</span>
                    </div>
                  )}
                  {item.observation_time && (
                    <div className="flex justify-between">
                      <span>Timestamp:</span>
                      <span className="text-slate-300">{item.observation_time}</span>
                    </div>
                  )}
                  {item.source_id && (
                    <div className="flex justify-between">
                      <span>Source ID:</span>
                      <span className="font-mono text-[10px] text-slate-400 truncate max-w-[180px]">{item.source_id}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close Drawer
          </Button>
        </div>
      </div>
    </div>
  );
}
