import React from 'react';
import { X, Users, BookOpen, CheckCircle2, ArrowRight, Layers, HeartHandshake } from 'lucide-react';
import Button from '../ui/Button';

export default function WhySkillGapModal({ isOpen, onClose, skillGap, onActionProposal }) {
  if (!isOpen || !skillGap) return null;

  const accommodations = skillGap.accessibility_accommodations || [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-150"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="bg-[#111827] rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-[#1E293B] text-slate-100 relative max-h-[90vh] overflow-y-auto space-y-6"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-900/30 text-purple-400 border border-purple-800/50 flex items-center justify-center shrink-0">
              <Users className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-100 text-base">
                  Competency Pathway: {skillGap.required_skill}
                </h3>
                {skillGap.is_demo && (
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-950/60 text-purple-400 border border-purple-800/50 font-mono">
                    [DEMO DATA]
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Workforce Intelligence Engine • Inclusive Learning &amp; Upskilling Trace
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Explainability Breakdown */}
        <div className="space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Role Competency &amp; Upskilling Reasoning</span>
          </div>

          <div className="space-y-2.5">
            {/* Scope */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-400">1. Staff Member &amp; Role Context</span>
              <div className="flex items-center justify-between text-xs text-slate-200">
                <span>Reference: <strong className="text-purple-400">{skillGap.employee_reference || 'Staff Member'}</strong></span>
                <span>Target Role: <strong className="text-white">{skillGap.role_name || 'Assigned Role'}</strong></span>
                <span>Department: <span className="text-slate-300">{skillGap.department || 'Operations'}</span></span>
              </div>
            </div>

            {/* Gap Analysis */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-amber-400">2. Identified Competency Need</span>
              <p className="text-xs text-slate-200">
                Target competency <strong className="text-white">{skillGap.required_skill}</strong> is required for optimal operational performance in this role. Gap Priority: <span className="font-bold text-rose-400">{skillGap.gap_level || 'Medium'}</span>.
              </p>
            </div>

            {/* Accessibility Accommodations */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1.5">
              <span className="text-[10px] uppercase font-bold text-teal-400 flex items-center gap-1">
                <HeartHandshake className="w-3.5 h-3.5 text-teal-400" />
                <span>3. Inclusive Learning Accommodations</span>
              </span>
              <div className="flex flex-wrap gap-2">
                {accommodations.length > 0 ? (
                  accommodations.map((acc, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded-md bg-teal-950/60 text-teal-300 border border-teal-800/50 text-[11px] font-medium">
                      ✓ {acc}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">Standard multimodal learning material (video, audio, text guides).</span>
                )}
              </div>
            </div>

            {/* Ethical Guardrail Check */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span>4. Privacy &amp; Dignity Guardrail</span>
              </span>
              <p className="text-xs text-slate-300">
                This assessment is strictly constructive for professional growth. It is never used for automated performance ranking, salary grading, or punitive disciplinary actions.
              </p>
            </div>

            {/* Recommended Action */}
            <div className="p-3 bg-purple-950/40 rounded-xl border border-purple-800/60 space-y-1">
              <span className="text-[10px] uppercase font-bold text-purple-300">5. Human-in-the-Loop Learning Proposal</span>
              <p className="text-xs text-slate-200 font-medium">{skillGap.recommended_action}</p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <Button variant="secondary" onClick={onClose} size="sm">
            Close
          </Button>
          {skillGap.status !== 'ENROLLED' && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                onClose();
                if (onActionProposal) onActionProposal(skillGap);
              }}
              className="flex items-center gap-1.5 bg-purple-600 hover:bg-purple-500 text-white"
            >
              <span>Create Learning Proposal</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
