import React, { useState, useEffect, useCallback } from 'react';
import {
  Truck,
  ShieldAlert,
  RotateCw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Database,
  Layers,
  FileCheck,
  PackageCheck,
  Clock,
  ExternalLink,
  Loader2,
  HelpCircle,
} from 'lucide-react';
import Button from '../components/ui/Button';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';
import { useAuth } from '../context/AuthContext';
import apiClient from '../services/apiClient';
import WhySupplyRiskModal from '../components/modals/WhySupplyRiskModal';
import ResilientSupplyChainTower from '../components/supply-chain/ResilientSupplyChainTower';

export default function SupplyChainPage({ showToast, _onNavigate, _setModalState }) {
  const { activeBusiness } = useAuth();
  const { backendProfileId } = useBusinessAnalysis();
  const profileId = activeBusiness?.id || backendProfileId;

  const [activeTab, setActiveTab] = useState('tower'); // tower, overview, suppliers, items, risks
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [summary, setSummary] = useState(null);
  const [suppliers, setSuppliers] = useState([]);
  const [items, setItems] = useState([]);
  const [risks, setRisks] = useState([]);
  const [selectedRisk, setSelectedRisk] = useState(null);
  const [whyRiskModalOpen, setWhyRiskModalOpen] = useState(false);

  const loadData = useCallback(async () => {
    if (!profileId) return;
    setLoading(true);
    try {
      const [sumRes, supRes, itemRes, riskRes] = await Promise.allSettled([
        apiClient.getSupplyChainSummary(profileId),
        apiClient.getSuppliers(profileId),
        apiClient.getSupplyItems(profileId),
        apiClient.getSupplyRisks(profileId),
      ]);

      if (sumRes.status === 'fulfilled') setSummary(sumRes.value);
      if (supRes.status === 'fulfilled') setSuppliers(supRes.value || []);
      if (itemRes.status === 'fulfilled') setItems(itemRes.value || []);
      if (riskRes.status === 'fulfilled') setRisks(riskRes.value || []);
    } catch {
      if (showToast) showToast('Could not load complete supply chain telemetry.');
    } finally {
      setLoading(false);
    }
  }, [profileId, showToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Run AI/Rule Engine Analysis
  const handleRunAnalysis = async () => {
    if (!profileId) return;
    setAnalyzing(true);
    try {
      await apiClient.runSupplyChainAnalysis(profileId);
      if (showToast) showToast('Supply Chain Resilience Agent evaluated active vendor network.');
      await loadData();
    } catch {
      if (showToast) showToast('Resilience analysis encountered an issue.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Create Action Proposal
  const handleCreateProposal = async (risk) => {
    if (!profileId) return;
    try {
      await apiClient.createSupplyChainProposal(risk.id, profileId);
      if (showToast) showToast(`Action Proposal created for "${risk.title}". Review in Overview or Proposals.`);
      await loadData();
    } catch {
      if (showToast) showToast('Failed to create action proposal.');
    }
  };

  // Seed Demo Data
  const handleSeedDemo = async () => {
    if (!profileId) return;
    try {
      await apiClient.seedDemoSupplyChain(profileId);
      if (showToast) showToast('Loaded verified [DEMO DATA] supplier & inventory network.');
      await loadData();
    } catch {
      if (showToast) showToast('Failed to seed demo supply chain data.');
    }
  };

  // Cleanup Demo Data
  const handleCleanupDemo = async () => {
    if (!profileId) return;
    try {
      await apiClient.cleanupDemoSupplyChain(profileId);
      if (showToast) showToast('Cleaned up synthetic demo supplier records.');
      await loadData();
    } catch {
      if (showToast) showToast('Failed to clean demo data.');
    }
  };

  const resilienceScore = summary?.overall_resilience_score ?? 68;
  const ratingBand = summary?.resilience_rating ?? 'Moderate';
  const hasDemo = suppliers.some((s) => s.is_demo) || items.some((i) => i.is_demo);

  return (
    <div className="space-y-6 font-sans antialiased text-slate-100">
      {/* Top Banner */}
      <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 sm:p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-amber-900/30 text-amber-400 border border-amber-800/50 flex items-center justify-center shrink-0">
            <Truck className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-xl font-bold text-slate-100">Supply Chain Resilience</h2>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-950/60 text-amber-400 border border-amber-800/50">
                Hackfest 2026 Theme 1
              </span>
              {hasDemo && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-amber-400 border border-slate-700 font-mono">
                  [DEMO DATA LOADED]
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Deterministic vendor dependency analysis, lead-time buffering, and compliance document verification
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={hasDemo ? handleCleanupDemo : handleSeedDemo}
            className="text-xs border-[#1E293B] text-slate-300 hover:text-white"
          >
            {hasDemo ? 'Reset Demo Data' : 'Seed [DEMO DATA] Network'}
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="flex items-center gap-1.5 bg-amber-600 hover:bg-amber-500 text-white"
          >
            {analyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4" />}
            <span>Analyze Resilience</span>
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto scrollbar-none">
        {[
          { id: 'tower', label: 'AI Control Tower (Flagship)' },
          { id: 'overview', label: 'Resilience Overview' },
          { id: 'suppliers', label: `Suppliers (${suppliers.length})` },
          { id: 'items', label: `Critical Materials (${items.length})` },
          { id: 'risks', label: `Identified Risks (${risks.length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors cursor-pointer ${
              activeTab === tab.id
                ? 'bg-amber-950/70 text-amber-300 border border-amber-800/80 shadow-sm shadow-amber-950/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#141C2B]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* FLAGSHIP TAB: RESILIENT SUPPLY CHAIN CONTROL TOWER */}
      {activeTab === 'tower' && (
        <ResilientSupplyChainTower businessId={profileId} showToast={showToast} />
      )}

      {activeTab !== 'tower' && loading ? (
        <div className="p-12 flex flex-col items-center justify-center space-y-3 bg-[#111827] rounded-2xl border border-[#1E293B]">
          <Loader2 className="w-6 h-6 animate-spin text-amber-400" />
          <span className="text-xs text-slate-400">Loading supply chain telemetry...</span>
        </div>
      ) : activeTab !== 'tower' ? (
        <>
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Score and KPI Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Resilience Score */}
                <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Resilience Index
                  </span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-white">{resilienceScore}</span>
                    <span className="text-xs font-bold text-amber-400">/ 100</span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Status: <strong className="text-amber-300">{ratingBand}</strong>
                  </div>
                </div>

                {/* Single Source Dependencies */}
                <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Single-Source Vulnerabilities
                  </span>
                  <div className="text-3xl font-black text-rose-400">
                    {summary?.single_source_count ?? 0}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Critical items with 0 backup vendors
                  </div>
                </div>

                {/* Missing / Expired Documents */}
                <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Vendor Compliance Gaps
                  </span>
                  <div className="text-3xl font-black text-amber-400">
                    {summary?.missing_docs_count ?? 0}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Unverified GST/ISO supplier certs
                  </div>
                </div>

                {/* Lead Time Average */}
                <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Average Lead Time
                  </span>
                  <div className="text-3xl font-black text-blue-400">
                    {summary?.lead_time_average_days ?? 0} <span className="text-sm font-normal text-slate-400">days</span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Replenishment transit window
                  </div>
                </div>
              </div>

              {/* Priority Risks Showcase */}
              <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                      Priority Supply Continuity Risks
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400">
                    {risks.length} active vulnerabilities flagged
                  </span>
                </div>

                {risks.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-400">
                    No active supply chain vulnerabilities detected. Click "Seed [DEMO DATA] Network" to test real scenarios.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {risks.slice(0, 3).map((r) => (
                      <div
                        key={r.id}
                        className="p-4 rounded-xl bg-[#141C2B] border border-[#1E293B] flex flex-col md:flex-row items-start md:items-center justify-between gap-3"
                      >
                        <div className="space-y-1 max-w-xl">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-bold text-slate-100 text-xs">{r.title}</span>
                            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                              r.priority === 'Critical'
                                ? 'bg-rose-950 text-rose-300 border border-rose-800'
                                : 'bg-amber-950 text-amber-300 border border-amber-800'
                            }`}>
                              {r.priority}
                            </span>
                            <span className="text-[9px] text-slate-400 font-mono">
                              {r.category}
                            </span>
                            {r.is_demo && (
                              <span className="text-[9px] text-amber-400 font-mono">
                                [DEMO DATA]
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed">{r.issue}</p>
                          <p className="text-[11px] text-slate-400">
                            Action: <strong className="text-amber-300">{r.recommended_action}</strong>
                          </p>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => {
                              setSelectedRisk(r);
                              setWhyRiskModalOpen(true);
                            }}
                            className="text-xs"
                          >
                            Why Risk?
                          </Button>
                          {r.status !== 'ACTION_CREATED' ? (
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleCreateProposal(r)}
                              className="text-xs bg-amber-600 hover:bg-amber-500 text-white flex items-center gap-1"
                            >
                              <span>Propose Action</span>
                              <ArrowRight className="w-3 h-3" />
                            </Button>
                          ) : (
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-1 rounded">
                              ✓ Task Created
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: SUPPLIERS */}
          {activeTab === 'suppliers' && (
            <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                  Active Supplier Registry
                </h3>
                <span className="text-xs text-slate-400">{suppliers.length} vendors registered</span>
              </div>

              {suppliers.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No suppliers registered yet. Seed demo network or add a supplier.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 text-[10px] uppercase">
                        <th className="py-2.5 px-3">Supplier Name</th>
                        <th className="py-2.5 px-3">Type</th>
                        <th className="py-2.5 px-3">Location</th>
                        <th className="py-2.5 px-3">Lead Time</th>
                        <th className="py-2.5 px-3">Dependency</th>
                        <th className="py-2.5 px-3">Risk Status</th>
                        <th className="py-2.5 px-3">Verified Documents</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {suppliers.map((s) => (
                        <tr key={s.id} className="hover:bg-[#141C2B] transition-colors">
                          <td className="py-3 px-3 font-semibold text-slate-100">
                            {s.name}
                            {s.is_demo && (
                              <span className="ml-1.5 text-[9px] text-amber-400 font-mono">[DEMO]</span>
                            )}
                          </td>
                          <td className="py-3 px-3 text-slate-300">{s.supplier_type}</td>
                          <td className="py-3 px-3 text-slate-400">{s.location}</td>
                          <td className="py-3 px-3 font-mono text-slate-300">{s.lead_time_days} days</td>
                          <td className="py-3 px-3">
                            <span className={`font-mono font-bold ${
                              s.dependency_percentage >= 70 ? 'text-rose-400' : 'text-slate-300'
                            }`}>
                              {s.dependency_percentage}%
                            </span>
                          </td>
                          <td className="py-3 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              s.risk_status === 'High' || s.risk_status === 'Critical'
                                ? 'bg-rose-950 text-rose-300 border border-rose-800'
                                : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            }`}>
                              {s.risk_status}
                            </span>
                          </td>
                          <td className="py-3 px-3">
                            <div className="space-y-0.5">
                              {s.documents && s.documents.length > 0 ? (
                                s.documents.map((d) => (
                                  <div key={d.id} className="text-[10px] flex items-center gap-1.5">
                                    <span className={`w-1.5 h-1.5 rounded-full ${
                                      d.verification_status === 'Verified' ? 'bg-emerald-400' : 'bg-amber-400'
                                    }`} />
                                    <span className="text-slate-300 truncate max-w-[150px]">{d.document_name}</span>
                                    <span className="text-[9px] text-slate-500 font-mono">({d.verification_status})</span>
                                  </div>
                                ))
                              ) : (
                                <span className="text-amber-400 text-[10px]">No documents attached</span>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CRITICAL MATERIALS */}
          {activeTab === 'items' && (
            <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                  Critical Materials &amp; Inventory Dependencies
                </h3>
                <span className="text-xs text-slate-400">{items.length} items tracked</span>
              </div>

              {items.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No materials recorded yet.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 text-[10px] uppercase">
                        <th className="py-2.5 px-3">Item Name</th>
                        <th className="py-2.5 px-3">Category</th>
                        <th className="py-2.5 px-3">Criticality</th>
                        <th className="py-2.5 px-3">Primary Supplier</th>
                        <th className="py-2.5 px-3">Dependency</th>
                        <th className="py-2.5 px-3">Alternate Suppliers</th>
                        <th className="py-2.5 px-3">Buffer Stock</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {items.map((it) => (
                        <tr key={it.id} className="hover:bg-[#141C2B] transition-colors">
                          <td className="py-3 px-3 font-semibold text-slate-100">
                            {it.name}
                            {it.is_demo && (
                              <span className="ml-1.5 text-[9px] text-amber-400 font-mono">[DEMO]</span>
                            )}
                          </td>
                          <td className="py-3 px-3 text-slate-300">{it.category}</td>
                          <td className="py-3 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              it.criticality === 'Critical'
                                ? 'bg-rose-950 text-rose-300 border border-rose-800'
                                : 'bg-blue-950 text-blue-300 border border-blue-800'
                            }`}>
                              {it.criticality}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-slate-300">{it.primary_supplier_name || 'Sole Vendor'}</td>
                          <td className="py-3 px-3 font-mono font-bold text-amber-400">
                            {it.dependency_percentage}%
                          </td>
                          <td className="py-3 px-3">
                            <span className={`font-bold ${
                              it.alternate_supplier_count === 0 ? 'text-rose-400' : 'text-emerald-400'
                            }`}>
                              {it.alternate_supplier_count} backups
                            </span>
                          </td>
                          <td className="py-3 px-3 font-mono text-slate-300">
                            {it.buffer_stock_days} days
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: RISKS */}
          {activeTab === 'risks' && (
            <div className="p-5 rounded-2xl bg-[#111827] border border-[#1E293B] space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                  Full Vulnerability Audit
                </h3>
                <span className="text-xs text-slate-400">{risks.length} risks tracked</span>
              </div>

              <div className="space-y-3">
                {risks.map((r) => (
                  <div key={r.id} className="p-4 rounded-xl bg-[#141C2B] border border-[#1E293B] space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-slate-100 text-sm">{r.title}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          r.priority === 'Critical'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}>
                          {r.priority}
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">{r.category}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            setSelectedRisk(r);
                            setWhyRiskModalOpen(true);
                          }}
                          className="text-xs"
                        >
                          Why Risk?
                        </Button>
                        {r.status !== 'ACTION_CREATED' ? (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleCreateProposal(r)}
                            className="text-xs bg-amber-600 hover:bg-amber-500 text-white"
                          >
                            Propose Action
                          </Button>
                        ) : (
                          <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-1 rounded">
                            ✓ Task Created
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-slate-300">{r.issue}</p>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
                      <span>Cause: {r.cause}</span>
                      <span className="text-emerald-400 font-semibold">
                        -{r.estimated_risk_reduction}% vulnerability
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : null}

      {/* Why Supply Risk Explainability Modal */}
      {whyRiskModalOpen && selectedRisk && (
        <WhySupplyRiskModal
          isOpen={true}
          onClose={() => setWhyRiskModalOpen(false)}
          risk={selectedRisk}
          onActionProposal={handleCreateProposal}
        />
      )}
    </div>
  );
}
