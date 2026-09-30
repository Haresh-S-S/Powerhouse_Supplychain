import React from 'react';
import { X, User } from 'lucide-react';

export default function AuditTrailModal({ isOpen, onClose, auditLogs }) {
  if (!isOpen) return null;

  const logs = auditLogs || [
    {
      id: 'aud-1',
      user_name: 'Mohith K',
      action: 'VERIFY_DOCUMENT',
      target_entity_name: 'Fire Safety Hydrant Test Report',
      previous_state: 'Pending',
      new_state: 'Verified',
      source: 'Action Proposal #AP-7492 (Human-Confirmed)',
      timestamp: '06 Sep 2026, 03:00 PM'
    },
    {
      id: 'aud-2',
      user_name: 'Mohith K',
      action: 'SUBMIT_APPLICATION',
      target_entity_name: 'Municipal Trade Licence Renewal',
      previous_state: 'Draft',
      new_state: 'Submitted',
      source: 'Action Proposal #AP-7421 (Human-Confirmed)',
      timestamp: '06 Sep 2026, 01:15 PM'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="audit-trail-title"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-start justify-between gap-4 bg-[#141C2B]/60">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 px-2.5 py-0.5 rounded border border-emerald-800/80 uppercase tracking-wider">
                Immutable Statutory Audit Trail
              </span>
            </div>
            <h2 id="audit-trail-title" className="text-base font-bold text-white tracking-tight">
              State-Changing Compliance Activity Log
            </h2>
            <p className="text-xs text-slate-400">
              Complete chronological record of all human-approved and system-executed mutations.
            </p>
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
        <div className="p-5 overflow-y-auto space-y-3 text-xs text-slate-300">
          {logs.length === 0 ? (
            <div className="p-6 text-center text-slate-400">
              No audit logs recorded yet. Human confirmations will appear here.
            </div>
          ) : (
            logs.map((log) => (
              <div key={log.id} className="p-3.5 rounded-xl bg-[#141C2B] border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-xs">{log.target_entity_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-950 text-blue-400 border border-blue-800">
                      {log.action}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">{log.timestamp}</span>
                </div>

                <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800/60">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">Status Delta:</span>
                    <span className="text-amber-400 font-medium">{log.previous_state}</span>
                    <span>→</span>
                    <span className="text-emerald-400 font-bold">{log.new_state}</span>
                  </div>
                  <div className="text-slate-400 flex items-center gap-1">
                    <User className="w-3 h-3 text-slate-500" />
                    <span>User: <strong className="text-slate-200">{log.user_name}</strong></span>
                  </div>
                </div>

                <div className="text-[10px] text-slate-500 italic">
                  Origin: {log.source}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-[#141C2B]/60 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
