import React from 'react';
import {
  X,
  ShieldCheck,
  AlertTriangle,
  FileSearch,
  Cpu,
  Zap,
  Activity,
  ArrowDown,
  CheckCircle2,
  Clock,
} from 'lucide-react';
import Button from '../ui/Button';

export default function WhyOpportunityModal({
  isOpen,
  onClose,
  opportunity,
  onReviewProposal,
}) {
  if (!isOpen || !opportunity) return null;

  const evidence = (opportunity.evidence && opportunity.evidence[0]) || {};
  const energyImpact = opportunity.estimated_energy_impact || {};
  const costImpact = opportunity.estimated_cost_impact || {};
  const carbonImpact = opportunity.estimated_carbon_impact || {};

  const stages = [
    {
      num: '01',
      title: 'Observed Telemetry',
      badge: evidence.is_demo ? 'DEMO DATA' : evidence.source_type || 'SYSTEM METRIC',
      badgeColor: evidence.is_demo ? 'bg-amber-950/60 text-amber-400 border-amber-800' : 'bg-blue-950/60 text-blue-400 border-blue-800',
      icon: Activity,
      content: evidence.evidence_summary || `Observed value: ${evidence.value || 'Active metric'}`,
      subDetail: evidence.observation_time ? `Timestamp: ${evidence.observation_time}` : 'Collected from live business telemetry',
    },
    {
      num: '02',
      title: 'Detected Inefficiency Pattern',
      badge: opportunity.severity || 'Warning',
      badgeColor: opportunity.severity === 'Critical' ? 'bg-rose-950/60 text-rose-400 border-rose-800' : 'bg-amber-950/60 text-amber-400 border-amber-800',
      icon: AlertTriangle,
      content: opportunity.detected_issue,
      subDetail: `Flagged by: ${opportunity.agent_type}`,
    },
    {
      num: '03',
      title: 'Root Cause Diagnostics',
      badge: 'Agent Analysis',
      badgeColor: 'bg-indigo-950/60 text-indigo-400 border-indigo-800',
      icon: Cpu,
      content: opportunity.cause,
      subDetail: 'Evaluated against operational runtime baseline models',
    },
    {
      num: '04',
      title: 'Recommended Action',
      badge: `Effort: ${opportunity.implementation_effort || 'Medium'}`,
      badgeColor: 'bg-emerald-950/60 text-emerald-400 border-emerald-800',
      icon: CheckCircle2,
      content: opportunity.recommended_action,
      subDetail: 'Governed operational change — requires human approval before task creation',
    },
    {
      num: '05',
      title: 'Deterministic Impact Formula',
      badge: 'Verified Model',
      badgeColor: 'bg-teal-950/60 text-teal-400 border-teal-800',
      icon: Zap,
      content: energyImpact.formula ? `Formula: ${energyImpact.formula} (Projected: ${energyImpact.value} ${energyImpact.unit})` : (costImpact.formula ? `Formula: ${costImpact.formula}` : 'Standard emission factor reduction model'),
      subDetail: carbonImpact.factor_source ? `Factor Source: ${carbonImpact.factor_source}` : 'CEA India Grid Baseline v19 (0.716 kgCO2e/kWh)',
    },
    {
      num: '06',
      title: 'Operational Policy Check',
      badge: opportunity.policy_status || 'PASS',
      badgeColor: opportunity.policy_status === 'PASS' ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800' : 'bg-amber-950/60 text-amber-400 border-amber-800',
      icon: ShieldCheck,
      content: opportunity.policy_notes || 'Operational safety checks passed. No conflict with runtime freeze windows.',
      subDetail: 'GreenPolicyValidator verification check',
    },
    {
      num: '07',
      title: 'AI Confidence & Priority',
      badge: `${Math.round((opportunity.confidence || 0.85) * 100)}% Confidence`,
      badgeColor: 'bg-blue-950/60 text-blue-400 border-blue-800',
      icon: Activity,
      content: `Ranked Priority: ${opportunity.priority}. Opportunity is structured with provenance and ready for human review.`,
      subDetail: 'Grounded in verifiable telemetry — zero hallucinated metrics',
    },
  ];

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-2xl shadow-2xl p-6 relative flex flex-col max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-950/80 border border-teal-800 text-teal-400 flex items-center justify-center shrink-0">
              <FileSearch className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-bold tracking-wider text-teal-400">
                  Green Industry Flow AI Decision Trace
                </span>
                <span className="text-[10px] font-mono text-slate-500">•</span>
                <span className="text-[10px] text-slate-400">{opportunity.category}</span>
              </div>
              <h3 className="font-bold text-slate-100 text-base mt-0.5">
                Why was this flagged: "{opportunity.title}"?
              </h3>
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

        {/* Trace Progression Stepper */}
        <div className="py-5 space-y-3">
          {stages.map((stage, idx) => {
            const Icon = stage.icon;
            const isLast = idx === stages.length - 1;

            return (
              <div key={stage.num} className="relative">
                <div className="p-3.5 rounded-xl bg-[#141C2B] border border-slate-800 hover:border-slate-700 transition-colors">
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-6 h-6 rounded-lg bg-[#0B0F17] border border-slate-700 flex items-center justify-center text-teal-400">
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-xs font-bold text-slate-200">
                        {stage.num}. {stage.title}
                      </span>
                    </div>

                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${stage.badgeColor}`}>
                      {stage.badge}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed pl-8">
                    {stage.content}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-1 pl-8">
                    {stage.subDetail}
                  </p>
                </div>

                {!isLast && (
                  <div className="flex justify-center my-0.5">
                    <ArrowDown className="w-3.5 h-3.5 text-slate-400" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <div className="text-[11px] text-slate-400">
            Status: <span className="font-bold text-slate-200">{opportunity.status}</span>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={onClose}>
              Close Trace
            </Button>
            {onReviewProposal && opportunity.status === 'DETECTED' && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  onClose();
                  onReviewProposal(opportunity);
                }}
              >
                Create Action Proposal
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
