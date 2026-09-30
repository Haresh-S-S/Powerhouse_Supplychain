import React, { useState } from 'react';
import {
  ArrowRight,
  Pencil,
  Building2,
  MapPin,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import Button from '../../components/ui/Button';
import { useBusinessAnalysis } from '../../context/BusinessAnalysisContext';
import { BUSINESS_CATEGORIES, CATEGORY_LABELS } from '../../engine/businessClassifier';
import { getCategoryDefaultName } from '../../utils/businessVisualResolver';

const EXAMPLE_INPUTS = [
  'I want to start a clothing store in Tiruppur',
  'I want to start a restaurant in Chennai',
  'I want to open a flower shop in Coimbatore',
  'I want to open a gold jewellery shop in Madurai',
  'I want to manufacture plastic components',
];

export default function BusinessOnboarding() {
  const { classifyDescription, confirmBusinessClassification } = useBusinessAnalysis();

  // 'describe' -> 'confirm' -> 'unknown'
  const [step, setStep] = useState('describe');
  const [description, setDescription] = useState('');
  const [result, setResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAnalyse = () => {
    if (!description.trim()) return;
    const classification = classifyDescription(description);

    if (!classification.category) {
      setResult(classification);
      setStep('unknown');
      return;
    }

    setResult(classification);
    setStep('confirm');
  };

  const handleUseExample = (example) => {
    setDescription(example);
  };

  const handleConfirm = async () => {
    if (!result?.category) return;
    setIsSubmitting(true);
    try {
      const defaultName = getCategoryDefaultName(result.category, result.location);
      await confirmBusinessClassification(result.category, result.location, defaultName);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = () => {
    setStep('describe');
  };

  const handleFallbackRetail = async () => {
    setIsSubmitting(true);
    try {
      const defaultName = getCategoryDefaultName(BUSINESS_CATEGORIES.RETAIL, result?.location || null);
      await confirmBusinessClassification(BUSINESS_CATEGORIES.RETAIL, result?.location || null, defaultName);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex items-center justify-center px-4 py-10 font-sans antialiased text-slate-100">
      <div className="w-full max-w-xl">
        {/* Brand mark */}
        <div className="flex items-center justify-center gap-2.5 mb-6">
          <div className="w-10 h-10 rounded-xl overflow-hidden bg-black border border-amber-500/30 flex items-center justify-center shadow-lg shadow-amber-500/10 shrink-0 p-0.5">
            <img src="/logo.png" alt="POWER HOUSE" className="w-full h-full object-contain" />
          </div>
          <span className="text-base font-bold text-white tracking-wide uppercase">POWER HOUSE</span>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xl p-6 sm:p-8">
          {step === 'describe' && (
            <div className="space-y-5">
              <div className="text-center space-y-1.5">
                <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                  Tell us about your business
                </h1>
                <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                  Describe your business in your own words and we&apos;ll prepare the relevant
                  compliance roadmap.
                </p>
              </div>

              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. I want to start a clothing store in Tiruppur"
                rows={4}
                className="w-full px-4 py-3 text-sm rounded-xl border border-slate-700 bg-[#141C2B] text-slate-100 focus:border-blue-500 focus:outline-none resize-none placeholder:text-slate-500"
              />

              <div className="space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Try an example
                </span>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_INPUTS.map((example) => (
                    <button
                      key={example}
                      type="button"
                      onClick={() => handleUseExample(example)}
                      className="text-[11px] font-medium px-2.5 py-1.5 rounded-lg bg-[#141C2B] hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-colors cursor-pointer"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                variant="primary"
                size="lg"
                className="w-full font-semibold"
                disabled={!description.trim()}
                onClick={handleAnalyse}
              >
                <span>Analyse My Business</span>
                <ArrowRight className="w-4 h-4" />
              </Button>

              <p className="text-[11px] text-center text-slate-400">
                Classification runs locally on your device — enterprise data isolation verified.
              </p>
            </div>
          )}

          {step === 'unknown' && (
            <div className="space-y-5 text-center">
              <div className="w-12 h-12 rounded-xl bg-amber-950/80 text-amber-400 flex items-center justify-center mx-auto border border-amber-800/80">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="space-y-1.5">
                <h2 className="text-lg font-bold text-white">
                  We couldn&apos;t confidently identify your business category
                </h2>
                <p className="text-xs text-slate-400 leading-relaxed max-w-sm mx-auto">
                  Please describe your business in a little more detail. For example:
                  &quot;I want to open a clothing store in Tiruppur&quot;
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-2.5 justify-center pt-1">
                <Button variant="secondary" size="sm" className="font-semibold" onClick={handleEdit}>
                  <Pencil className="w-3.5 h-3.5" />
                  <span>Try Again</span>
                </Button>
                <Button variant="primary" size="sm" className="font-semibold" onClick={handleFallbackRetail}>
                  <span>Continue as General Retail Business</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          )}

          {step === 'confirm' && result && (
            <div className="space-y-5">
              <div className="text-center space-y-1.5">
                <div className="w-12 h-12 rounded-xl bg-emerald-950/80 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-800/80">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h2 className="text-lg font-bold text-white">
                  Here&apos;s what we understood about your business
                </h2>
              </div>

              <div className="rounded-xl border border-slate-700 bg-[#141C2B] divide-y divide-slate-800">
                <div className="p-4 flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-blue-950 text-blue-400 flex items-center justify-center border border-blue-800 shrink-0">
                    <Building2 className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Business Category
                    </span>
                    <p className="text-sm font-bold text-white mt-0.5">
                      {result.categoryLabel || CATEGORY_LABELS[result.category]}
                    </p>
                  </div>
                </div>

                <div className="p-4 flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-amber-950/60 text-amber-400 flex items-center justify-center border border-amber-800/60 shrink-0">
                    <Building2 className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Proposed Workspace Name
                    </span>
                    <p className="text-sm font-bold text-white mt-0.5">
                      {getCategoryDefaultName(result.category, result.location)}
                    </p>
                  </div>
                </div>

                <div className="p-4 flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-indigo-950 text-indigo-400 flex items-center justify-center border border-indigo-800 shrink-0">
                    <MapPin className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Location
                    </span>
                    <p className="text-sm font-bold text-white mt-0.5">
                      {result.location ? `${result.location.city}, ${result.location.state}` : 'Not specified'}
                    </p>
                  </div>
                </div>

                <div className="p-4 flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-emerald-950/60 text-emerald-400 flex items-center justify-center border border-emerald-800/60 shrink-0">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Statutory Compliance Status
                    </span>
                    <p className="text-xs text-slate-300 mt-1">
                      PAN: <span className="text-amber-400 font-medium">Pending Setup</span> • GSTIN: <span className="text-amber-400 font-medium">Pending Registration</span> • Udyam: <span className="text-amber-400 font-medium">Pending Registration</span>
                    </p>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Zero fabricated legal credentials. You can update verified registration IDs anytime in Business Profile.
                    </p>
                  </div>
                </div>
              </div>

              <p className="text-[11px] text-slate-400 text-center leading-relaxed">
                We&apos;ll load a statutory compliance roadmap tailored to this category. You can always
                switch business type later from the sidebar.
              </p>

              <div className="flex flex-col sm:flex-row gap-2.5">
                <Button variant="secondary" size="lg" className="flex-1 font-semibold" onClick={handleEdit} disabled={isSubmitting}>
                  <Pencil className="w-4 h-4" />
                  <span>Edit</span>
                </Button>
                <Button variant="primary" size="lg" className="flex-1 font-semibold" onClick={handleConfirm} disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                      <span>Building Workspace...</span>
                    </>
                  ) : (
                    <>
                      <span>Confirm &amp; Build My Workspace</span>
                      <ArrowRight className="w-4 h-4 ml-1.5" />
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </div>

        <p className="text-[11px] text-center text-slate-500 mt-5">
          Recommendations are generated for prototype planning. Always verify final filing
          mandates with respective state and central authorities.
        </p>
      </div>
    </div>
  );
}
