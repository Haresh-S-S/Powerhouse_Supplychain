import React from 'react';
import { X } from 'lucide-react';

export default function CategoryComparisonModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="comparison-modal-title"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-start justify-between gap-4 bg-[#141C2B]/60">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-blue-400 bg-blue-950/80 px-2.5 py-0.5 rounded border border-blue-800/80 uppercase tracking-wider">
                SIH Product Hardening Proof
              </span>
              <span className="text-[11px] text-slate-400">Jurisdiction: Tiruppur, Tamil Nadu</span>
            </div>
            <h2 id="comparison-modal-title" className="text-base sm:text-lg font-bold text-white tracking-tight">
              Contextual Compliance Comparison: Textile vs Restaurant
            </h2>
            <p className="text-xs text-slate-400">
              Proving deterministic regulatory differentiation based strictly on canonical business activity.
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
        <div className="p-5 overflow-y-auto space-y-4 text-xs text-slate-300">
          {/* Divergence Stat Banner */}
          <div className="p-3.5 rounded-xl bg-[#0B0F17] border border-blue-900/40 flex items-center justify-between gap-4">
            <div>
              <span className="text-xs font-bold text-blue-400 uppercase tracking-wider block">73% Statutory Requirement Divergence</span>
              <p className="text-[11px] text-slate-300 mt-0.5">
                Operating in the exact same municipality, statutory compliance is completely distinct between manufacturing trade and food service.
              </p>
            </div>
            <div className="text-2xl font-black text-white px-3 py-1 rounded-lg bg-blue-950 border border-blue-800 shrink-0">
              73%
            </div>
          </div>

          {/* Side by Side Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Textile Column */}
            <div className="p-4 rounded-xl bg-[#141C2B] border border-slate-800 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div>
                  <h3 className="font-bold text-white text-sm">Clothing & Textile</h3>
                  <span className="text-[10px] text-slate-400">Tiruppur Textile Works</span>
                </div>
                <span className="text-xs font-extrabold text-blue-400 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800">
                  8 Licences
                </span>
              </div>

              <div className="space-y-1.5">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold block">Mandatory Licences</span>
                <ul className="space-y-1 text-slate-200">
                  <li className="flex items-center gap-1.5">✓ Shops &amp; Establishments Registration</li>
                  <li className="flex items-center gap-1.5">✓ Municipal Trade Licence (Textile Retail)</li>
                  <li className="flex items-center gap-1.5 text-blue-300 font-medium">★ State PCB Consent (Air &amp; Water / ETP)</li>
                  <li className="flex items-center gap-1.5 text-blue-300 font-medium">★ Textile Committee Registration</li>
                  <li className="flex items-center gap-1.5">✓ Fire Safety Certificate</li>
                </ul>
              </div>

              <div className="p-2.5 rounded-lg bg-[#0B0F17] border border-slate-800 text-[11px] space-y-1">
                <span className="text-slate-400 font-bold block">Primary Enforcing Authorities:</span>
                <span className="text-slate-300 block">• Tamil Nadu Pollution Control Board (TNPCB)</span>
                <span className="text-slate-300 block">• Ministry of Textiles (Textiles Committee)</span>
              </div>
            </div>

            {/* Restaurant Column */}
            <div className="p-4 rounded-xl bg-[#141C2B] border border-slate-800 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div>
                  <h3 className="font-bold text-white text-sm">Restaurant / Food Service</h3>
                  <span className="text-[10px] text-slate-400">Tiruppur Eatery Outlet</span>
                </div>
                <span className="text-xs font-extrabold text-amber-400 bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800">
                  7 Licences
                </span>
              </div>

              <div className="space-y-1.5">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold block">Mandatory Licences</span>
                <ul className="space-y-1 text-slate-200">
                  <li className="flex items-center gap-1.5 text-amber-300 font-medium">★ FSSAI Registration / Licence (FoSCoS)</li>
                  <li className="flex items-center gap-1.5 text-amber-300 font-medium">★ Municipal Health Trade Licence</li>
                  <li className="flex items-center gap-1.5 text-amber-300 font-medium">★ Eating House Licence (Police Dept)</li>
                  <li className="flex items-center gap-1.5">✓ Fire Safety NOC (Kitchen Hood &amp; LPG)</li>
                  <li className="flex items-center gap-1.5">✓ Shops &amp; Establishments Registration</li>
                </ul>
              </div>

              <div className="p-2.5 rounded-lg bg-[#0B0F17] border border-slate-800 text-[11px] space-y-1">
                <span className="text-slate-400 font-bold block">Primary Enforcing Authorities:</span>
                <span className="text-slate-300 block">• Food Safety and Standards Authority (FSSAI)</span>
                <span className="text-slate-300 block">• Tiruppur Municipal Public Health Directorate</span>
              </div>
            </div>
          </div>

          {/* Common Baseline */}
          <div className="p-3 rounded-xl bg-[#0B0F17] border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold block">
              Universal Statutory Foundation (Shared Across Both)
            </span>
            <div className="flex flex-wrap gap-2 pt-1 text-[11px]">
              <span className="px-2 py-1 rounded bg-[#141C2B] text-slate-300 border border-slate-700">GST Registration (CGST Act)</span>
              <span className="px-2 py-1 rounded bg-[#141C2B] text-slate-300 border border-slate-700">Shops &amp; Establishments (Form C)</span>
              <span className="px-2 py-1 rounded bg-[#141C2B] text-slate-300 border border-slate-700">Commercial Fire Safety Clearance</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-[#141C2B]/60 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors cursor-pointer"
          >
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
}
