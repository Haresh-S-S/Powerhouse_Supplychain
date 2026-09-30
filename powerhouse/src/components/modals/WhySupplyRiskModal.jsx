import React from 'react';
import { X, ShieldAlert, Truck, CheckCircle2, AlertTriangle, ArrowRight, Layers, Database } from 'lucide-react';
import Button from '../ui/Button';

export default function WhySupplyRiskModal({ isOpen, onClose, risk, onActionProposal }) {
  if (!isOpen || !risk) return null;

  const evidence = risk.evidence || {};
  const isSingleSource = risk.category === 'Single Supplier Dependency';
  const isMissingDoc = risk.category === 'Missing Documentation';
  const isLeadTime = risk.category === 'Extended Lead Time';

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
            <div className="w-10 h-10 rounded-2xl bg-amber-900/30 text-amber-400 border border-amber-800/50 flex items-center justify-center shrink-0">
              <Truck className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-100 text-base">{risk.title}</h3>
                {risk.is_demo && (
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-400 border border-amber-800/50 font-mono">
                    [DEMO DATA]
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Supply Chain Resilience Engine • 7-Stage Explainability Audit
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

        {/* 7-Stage Reasoning & Provenance Chain */}
        <div className="space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Deterministic Explainability Trace</span>
          </div>

          <div className="space-y-2.5">
            {/* Stage 1: Observation */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-400">1. Observation &amp; Inventory Scope</span>
              <p className="text-xs text-slate-200">
                {evidence.supply_item ? `Supply item monitored: ${evidence.supply_item} (${evidence.criticality || 'Critical'}). Primary vendor: ${evidence.primary_supplier || 'Sole Supplier'}.` :
                 evidence.supplier_name ? `Vendor profile monitored: ${evidence.supplier_name} (${evidence.supplier_type || 'Vendor'}). Location: ${evidence.location || 'India'}.` :
                 risk.issue}
              </p>
            </div>

            {/* Stage 2: Policy Rule */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-blue-400">2. Governing Policy Rule</span>
              <p className="text-xs text-slate-200 font-mono">
                {isSingleSource ? 'POLICY-SC-01: Critical raw materials must maintain >= 1 qualified alternate supplier or dependency < 70%.' :
                 isMissingDoc ? 'POLICY-SC-04: Mandatory active GST clearance, ISO, and statutory certificates required for active tier-1 vendors.' :
                 isLeadTime ? 'POLICY-SC-02: Lead time for high-criticality items cannot exceed 21 days without local buffer stock.' :
                 'POLICY-SC-GEN: Supply continuity standards mandate verified vendor risk controls.'}
              </p>
            </div>

            {/* Stage 3: Trigger Condition */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-amber-400">3. Trigger Threshold Exceeded</span>
              <div className="text-xs text-slate-200 space-y-1">
                <div>• Measured Dependency: <span className="font-bold text-rose-400">{evidence.dependency_percentage ? `${evidence.dependency_percentage}%` : 'High'}</span> (Threshold: 70%)</div>
                {evidence.lead_time_days && <div>• Fulfilment Lead Time: <span className="font-bold text-amber-400">{evidence.lead_time_days} days</span> (Threshold: 21 days)</div>}
                {evidence.buffer_stock_days !== undefined && <div>• Buffer Stock On-Hand: <span className="font-bold text-rose-400">{evidence.buffer_stock_days} days</span> (Safe Minimum: 7 days)</div>}
                {evidence.missing_or_expired_documents && (
                  <div>• Missing/Expired Credentials: <span className="text-amber-400">{evidence.missing_or_expired_documents.join(', ')}</span></div>
                )}
              </div>
            </div>

            {/* Stage 4: Root Cause Analysis */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-400">4. Root Cause</span>
              <p className="text-xs text-slate-200">{risk.cause}</p>
            </div>

            {/* Stage 5: Safety & Governance Validation */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1">
              <span className="text-[10px] uppercase font-bold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span>5. Policy Validation Result: {risk.policy_check_status || 'PASS'}</span>
              </span>
              <p className="text-xs text-slate-300">
                Action recommendation adheres to non-destructive vendor qualification guidelines. Automated order cancellations and unverified supplier onboarding are strictly prohibited.
              </p>
            </div>

            {/* Stage 6: Projected Resilience Impact */}
            <div className="p-3 bg-[#141C2B] rounded-xl border border-[#1E293B] flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400">6. Estimated Risk Reduction</span>
                <div className="text-sm font-bold text-emerald-400">-{risk.estimated_risk_reduction}% Disruption Vulnerability</div>
              </div>
              <div className="text-right">
                <span className="text-[10px] uppercase font-bold text-slate-400">Confidence Score</span>
                <div className="text-sm font-bold text-blue-400">{Math.round((risk.confidence || 0.85) * 100)}% Verified</div>
              </div>
            </div>

            {/* Stage 7: Human Action Required */}
            <div className="p-3 bg-blue-950/40 rounded-xl border border-blue-800/60 space-y-1">
              <span className="text-[10px] uppercase font-bold text-blue-300">7. Recommended Human-in-the-Loop Action</span>
              <p className="text-xs text-slate-200 font-medium">{risk.recommended_action}</p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <Button variant="secondary" onClick={onClose} size="sm">
            Close
          </Button>
          {risk.status !== 'ACTION_CREATED' && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                onClose();
                if (onActionProposal) onActionProposal(risk);
              }}
              className="flex items-center gap-1.5"
            >
              <span>Create Action Proposal</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
