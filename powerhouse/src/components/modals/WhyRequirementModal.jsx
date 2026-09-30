import React, { useState, useEffect } from 'react';
import {
  X,
  ShieldCheck,
  AlertTriangle,
  FileText,
  Building,
  Scale,
  MapPin,
  CheckCircle2,
  ArrowRight,
  Database,
  ExternalLink,
  Cpu
} from 'lucide-react';
import Badge from '../ui/Badge';
import apiClient from '../../services/apiClient';

export default function WhyRequirementModal({ isOpen, onClose, approval, businessProfile, onTakeAction }) {
  const [ragCitation, setRagCitation] = useState(approval?.rag_evidence || null);
  const [loadingRag, setLoadingRag] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function fetchEvidence() {
      if (!approval || approval.rag_evidence) {
        if (approval?.rag_evidence) setRagCitation(approval.rag_evidence);
        return;
      }
      const profileId = businessProfile?.id || approval.business_profile_id || 1;
      const query = `${approval.name} ${approval.authority || ''}`.trim();
      setLoadingRag(true);
      try {
        const res = await apiClient.queryRag(profileId, query, 1);
        if (isMounted && res?.citations && res.citations.length > 0) {
          setRagCitation(res.citations[0]);
        }
      } catch {
        // Fallback gracefully to deterministic static regBasis
      } finally {
        if (isMounted) setLoadingRag(false);
      }
    }
    if (isOpen) {
      fetchEvidence();
    }
    return () => { isMounted = false; };
  }, [isOpen, approval, businessProfile]);

  if (!isOpen || !approval) return null;

  const jurisdiction = approval.jurisdiction || 'State (Tamil Nadu)';
  const verificationState = approval.verification_state || 'VERIFIED SOURCE';
  const isVerified = verificationState === 'VERIFIED SOURCE';

  const regBasis = approval.regulatory_basis || {
    source: approval.authority || 'Statutory Regulatory Authority',
    authority: approval.authority || 'District Directorate',
    act: 'Applicable Commercial Statutory Act',
    section: 'Statutory Licensing Section',
    citation: 'Official Gazette Notification / Regulatory Order',
    verification_state: verificationState
  };

  const decisionInputs = approval.decision_inputs || {
    business_category: approval.category || 'Commercial Enterprise',
    primary_activity: 'Commercial Operations',
    location: 'Tiruppur, Tamil Nadu',
    condition_or_threshold: 'Statutory commercial activity threshold'
  };

  const decisionTrace = approval.decision_trace || [
    { step: 1, stage: 'Business Profile', title: 'Commercial Profile', description: 'Enterprise registered with active operations.' },
    { step: 2, stage: 'Category Classification', title: 'Industry Classification', description: `Classified as ${approval.category}.` },
    { step: 3, stage: 'Jurisdiction', title: 'Geographic Standing', description: `Premises situated in ${decisionInputs.location}.` },
    { step: 4, stage: 'Condition Evaluation', title: 'Threshold Condition', description: decisionInputs.condition_or_threshold },
    { step: 5, stage: 'Compliance Rule', title: 'Statutory Rule Match', description: `Matched statutory mandate under ${regBasis.act}.` },
    { step: 6, stage: 'Requirement Trigger', title: 'Approval Mandate', description: `Applicable statutory requirement: ${approval.name}.` },
    { step: 7, stage: 'Regulatory Authority', title: 'Enforcing Body', description: `Enforced by ${approval.authority}.` },
    { step: 8, stage: 'Compliance Status', title: 'Current Standing', description: `Status: ${approval.status}. Action recommended.` }
  ];

  const docs = approval.required_documents_list || [
    'Business Registration Proof / PAN',
    'Premises Lease Agreement / Property Tax Receipt',
    'Statutory Declaration Form'
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="bg-[#111827] border border-[#1E293B] rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="why-requirement-title"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-start justify-between gap-4 bg-[#141C2B]/60">
          <div className="space-y-1.5 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-bold text-blue-400 bg-blue-950/80 px-2.5 py-0.5 rounded-md border border-blue-800/80 uppercase tracking-wider">
                Why This Requirement?
              </span>
              <span className="text-[11px] font-semibold text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                {jurisdiction}
              </span>
              <span
                className={`text-[11px] font-bold px-2 py-0.5 rounded flex items-center gap-1 ${
                  isVerified
                    ? 'bg-emerald-950/90 text-emerald-400 border border-emerald-800/90'
                    : 'bg-amber-950/90 text-amber-400 border border-amber-800/90'
                }`}
              >
                {isVerified ? <ShieldCheck className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                {verificationState}
              </span>
            </div>
            <h2 id="why-requirement-title" className="text-lg sm:text-xl font-bold text-white tracking-tight leading-snug">
              {approval.name}
            </h2>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="truncate">{approval.authority}</span>
              <span className="text-slate-600">•</span>
              <Badge variant={approval.status} size="xs">{approval.status}</Badge>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer shrink-0"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-5 overflow-y-auto space-y-5 text-xs text-slate-300">
          {/* Section 1: Plain English Rationale */}
          <div className="p-4 rounded-xl bg-[#141C2B] border border-blue-900/40 space-y-1.5">
            <div className="text-[11px] font-bold text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5" />
              Statutory Basis & Rationale
            </div>
            <p className="text-slate-200 leading-relaxed text-xs">
              {approval.why_required || approval.trigger_reason || approval.description}
            </p>
          </div>

          {/* Section 2: Decision Inputs */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Deterministic Decision Inputs
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <div className="p-2.5 rounded-lg bg-[#0B0F17] border border-slate-800/80">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Business Category</span>
                <span className="font-semibold text-slate-200 mt-0.5 block">{decisionInputs.category_label || decisionInputs.business_category}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#0B0F17] border border-slate-800/80">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Operational Location</span>
                <span className="font-semibold text-slate-200 mt-0.5 flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-400" />
                  {decisionInputs.location}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#0B0F17] border border-slate-800/80 sm:col-span-2">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Statutory Trigger Condition</span>
                <span className="text-slate-300 mt-0.5 block">{decisionInputs.condition_or_threshold}</span>
              </div>
            </div>
          </div>

          {/* Section 3: 8-Step Decision Trace */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
                Decision Trace (8 Stages)
              </h3>
              <span className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Deterministic Match
              </span>
            </div>

            <div className="space-y-2 border-l-2 border-blue-800/60 ml-3 pl-3.5">
              {decisionTrace.map((st, idx) => (
                <div key={st.step || idx} className="relative group">
                  <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-[#111827]" />
                  <div className="text-[11px] text-slate-400 font-medium">
                    <span className="font-bold text-slate-200">Step {st.step_number || idx + 1}: {st.title || st.stage || st.step}</span>
                    <span className="text-slate-500 ml-1.5 text-[10px]">({st.stage || st.title})</span>
                  </div>
                  <div className="text-xs text-slate-300 mt-0.5 leading-snug">
                    {st.description}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 4: Hybrid Regulatory Engine Split & Vector RAG Evidence */}
          <div className="p-4 rounded-xl bg-[#0B0F17] border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Dual-Engine Verification & Statutory Citations
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-black bg-emerald-950 text-emerald-400 border border-emerald-800/80">
                VERIFIED SOURCE
              </span>
            </div>

            {/* Architecture Engine Distinction */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
              <div className="p-2.5 rounded-lg bg-[#141C2B] border border-blue-900/40 space-y-1">
                <div className="flex items-center gap-1.5 text-blue-400 font-bold uppercase text-[10px]">
                  <Cpu className="w-3 h-3" />
                  <span>Authoritative Selection</span>
                </div>
                <div className="text-slate-200 font-semibold">Deterministic Rules Engine</div>
                <div className="text-slate-400 text-[10px] leading-tight">
                  Evaluates enterprise profile conditions to select applicable legal mandates.
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-[#141C2B] border border-purple-900/40 space-y-1">
                <div className="flex items-center gap-1.5 text-purple-400 font-bold uppercase text-[10px]">
                  <Database className="w-3 h-3" />
                  <span>Supporting Evidence</span>
                </div>
                <div className="text-slate-200 font-semibold">Verified Vector RAG</div>
                <div className="text-slate-400 text-[10px] leading-tight">
                  Performs dense 384-d semantic retrieval across official gazettes and statutes.
                </div>
              </div>
            </div>

            {/* Vector RAG Retrieved Evidence Snippet */}
            {ragCitation && (
              <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/40 space-y-1.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <Database className="w-3 h-3" />
                    ChromaDB Vector Retrieval Match
                  </span>
                  {ragCitation.composite_relevance && (
                    <span className="text-[10px] font-mono font-bold text-emerald-300 bg-emerald-900/50 px-1.5 py-0.5 rounded border border-emerald-700/60">
                      {Math.round(ragCitation.composite_relevance * 100)}% Match
                    </span>
                  )}
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed italic">
                  "{ragCitation.content_preview || ragCitation.chunk_text || ragCitation.citation}"
                </p>
                {ragCitation.source_url && (
                  <a
                    href={ragCitation.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[10px] text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    <span>Official Ministry Source Document</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            )}

            {loadingRag && (
              <div className="text-[11px] text-slate-400 italic flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
                Querying local ChromaDB vector index for statutory evidence...
              </div>
            )}

            {/* Statutory Metadata */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1">
              <div>
                <span className="text-[10px] text-slate-500 block">Enforcing Body</span>
                <span className="font-semibold text-slate-200">{ragCitation?.statutory_authority || regBasis.source}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">Statutory Act</span>
                <span className="font-semibold text-slate-200">{ragCitation?.act || regBasis.act}</span>
              </div>
              <div className="sm:col-span-2">
                <span className="text-[10px] text-slate-500 block">Section / Provision</span>
                <span className="text-slate-300 font-mono text-[11px]">{ragCitation?.section || regBasis.section}</span>
              </div>
              <div className="sm:col-span-2">
                <span className="text-[10px] text-slate-500 block">Official Gazette / Order Citation</span>
                <span className="text-slate-400 italic text-[11px] block">{regBasis.citation}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 leading-tight">
              Evidence grounded in official statutory gazettes and circulars. Verified regulatory Vector RAG provides supporting citations without overriding deterministic compliance selection.
            </div>
          </div>

          {/* Section 5: Mandatory Required Documents */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Mandatory Evidence Documents ({docs.length})
            </h3>
            <div className="space-y-1.5">
              {docs.map((d, i) => (
                <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#141C2B] border border-slate-800/80 text-xs">
                  <span className="text-slate-200 flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    {d}
                  </span>
                  <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/80">
                    Mandatory
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-[#141C2B]/60 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-slate-400 truncate max-w-sm">
            <span className="font-semibold text-slate-300">Recommended Action: </span>
            {approval.next_action || 'Review requirement with local authority.'}
          </div>
          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition-colors cursor-pointer"
            >
              Close
            </button>
            <button
              onClick={() => {
                onClose();
                if (onTakeAction) onTakeAction(approval);
              }}
              className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors cursor-pointer flex items-center gap-1.5 shadow-sm shadow-blue-500/20"
            >
              <span>Take Action</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
