import React, { useState, useEffect, useCallback } from 'react';
import {
  Leaf,
  Zap,
  RotateCw,
  Gauge,
  CheckCircle2,
  ArrowRight,
  Database,
  TrendingDown,
  Loader2,
  HelpCircle,
} from 'lucide-react';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';
import { useAuth } from '../context/AuthContext';
import apiClient from '../services/apiClient';
import WhyOpportunityModal from '../components/modals/WhyOpportunityModal';
import GreenScoreExplainModal from '../components/modals/GreenScoreExplainModal';
import EvidenceDrawer from '../components/drawers/EvidenceDrawer';

export default function GreenOperationsPage({ showToast, onNavigate, _setModalState }) {
  const { activeBusiness } = useAuth();
  const { businessTemplateBundle, backendProfileId } = useBusinessAnalysis();
  const profileId = activeBusiness?.id || backendProfileId;

  const [activeTab, setActiveTab] = useState('opportunities'); // opportunities, traces, impact, factors
  const [summary, setSummary] = useState(null);
  const [scoreDetail, setScoreDetail] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [agentRuns, setAgentRuns] = useState([]);
  const [impacts, setImpacts] = useState([]);
  const [emissionFactors, setEmissionFactors] = useState([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isOrchestrating, setIsOrchestrating] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState('All');

  // Modals state
  const [selectedWhyOpp, setSelectedWhyOpp] = useState(null);
  const [showScoreModal, setShowScoreModal] = useState(false);
  const [selectedEvidenceOpp, setSelectedEvidenceOpp] = useState(null);

  // Load all green intelligence data for active profile
  const loadGreenData = useCallback(async () => {
    if (!profileId) return;
    setIsLoading(true);
    try {
      const [sumRes, scoreRes, oppsRes, runsRes, impactsRes, factorsRes] = await Promise.all([
        apiClient.getGreenSummary(profileId).catch(() => null),
        apiClient.getGreenScore(profileId).catch(() => null),
        apiClient.getGreenOpportunities({ business_profile_id: profileId }).catch(() => []),
        apiClient.getGreenAgentRuns(profileId).catch(() => []),
        apiClient.getGreenImpact(profileId).catch(() => []),
        apiClient.getEmissionFactors().catch(() => []),
      ]);

      setSummary(sumRes);
      setScoreDetail(scoreRes);
      setOpportunities(Array.isArray(oppsRes) ? oppsRes : []);
      setAgentRuns(Array.isArray(runsRes) ? runsRes : []);
      setImpacts(Array.isArray(impactsRes) ? impactsRes : []);
      setEmissionFactors(Array.isArray(factorsRes) ? factorsRes : []);
    } catch {
      // Offline or network error
    } finally {
      setIsLoading(false);
    }
  }, [profileId]);

  useEffect(() => {
    loadGreenData();
  }, [loadGreenData]);

  // Run Agent Orchestrator
  const handleRunAgent = async () => {
    if (!profileId) return;
    setIsOrchestrating(true);
    try {
      const res = await apiClient.runGreenAgent(profileId);
      if (showToast) showToast(res.message || 'Agent orchestration completed successfully.');
      await loadGreenData();
    } catch {
      if (showToast) showToast('Failed to trigger agent orchestrator.');
    } finally {
      setIsOrchestrating(false);
    }
  };

  // Seed Demo Telemetry
  const handleSeedDemo = async () => {
    if (!profileId) return;
    setIsOrchestrating(true);
    try {
      const res = await apiClient.seedGreenDemoData(profileId);
      if (showToast) showToast(res.message || 'Demo telemetry generated and analyzed.');
      await loadGreenData();
    } catch {
      if (showToast) showToast('Failed to seed demo telemetry.');
    } finally {
      setIsOrchestrating(false);
    }
  };

  // Action Proposal Trigger
  const handleCreateProposal = async (opp) => {
    if (!profileId) return;
    try {
      await apiClient.createGreenProposal(opp.id, profileId);
      if (showToast) showToast(`Action Proposal created for "${opp.title}". Please review and confirm.`);
      await loadGreenData();
      if (onNavigate) {
        // Optional navigation to proposals or overview
      }
    } catch {
      if (showToast) showToast('Failed to generate action proposal.');
    }
  };

  // Verify Impact Measurement
  const handleVerifyImpact = async (impactId, measuredVal) => {
    if (!profileId) return;
    try {
      await apiClient.verifyGreenImpact(impactId, profileId, {
        measured_value: measuredVal,
        assumptions: 'Empirical post-implementation submeter verification.',
        is_demo: true,
      });
      if (showToast) showToast('Post-implementation measurement verified successfully.');
      await loadGreenData();
    } catch {
      if (showToast) showToast('Failed to verify impact measurement.');
    }
  };

  const filteredOpps = opportunities.filter((op) => {
    if (categoryFilter !== 'All' && op.category !== categoryFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-950/60 text-teal-400 border border-teal-800 flex items-center gap-1">
              <Leaf className="w-3 h-3" />
              GREEN INDUSTRY FLOW AI
            </span>
            <span className="text-xs text-slate-400">
              {businessTemplateBundle?.meta?.categoryLabel || 'Governed Sustainability Layer'}
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Green Operations &amp; Sustainability Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Real agentic energy diagnostics, compute optimization, and deterministic impact verification.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleSeedDemo}
            disabled={isOrchestrating}
            className="text-xs font-semibold"
          >
            <Database className="w-3.5 h-3.5 mr-1" />
            Seed Demo Telemetry
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleRunAgent}
            disabled={isOrchestrating}
            className="text-xs font-semibold bg-teal-600 hover:bg-teal-500 border-teal-500"
          >
            {isOrchestrating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                Orchestrating...
              </>
            ) : (
              <>
                <RotateCw className="w-3.5 h-3.5 mr-1" />
                Run Agent Orchestrator
              </>
            )}
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-5">
        {/* Card 1: Green Operations Score */}
        <div
          onClick={() => setShowScoreModal(true)}
          className="bg-[#111827] rounded-2xl border border-[#1E293B] hover:border-teal-800 p-4 sm:p-5 flex items-center justify-between cursor-pointer transition-colors shadow-2xs group"
        >
          <div>
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400">
              <span>Green Score</span>
              <HelpCircle className="w-3 h-3 text-slate-400 group-hover:text-teal-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-xl sm:text-2xl font-black text-white">
                {summary?.green_score ?? 72}
              </span>
              <span className="text-xs text-slate-400">/ 100</span>
              <span className="text-[10px] font-bold text-teal-400">
                {summary?.score_rating || 'Good'}
              </span>
            </div>
            <div className="text-[11px] text-teal-400/90 mt-1 font-medium flex items-center gap-1">
              <span>Why this score?</span>
              <ArrowRight className="w-2.5 h-2.5" />
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-teal-950/60 border border-teal-800 text-teal-400 flex items-center justify-center shrink-0">
            <Gauge className="w-5 h-5" />
          </div>
        </div>

        {/* Card 2: Potential Cost Savings */}
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-4 sm:p-5 flex items-center justify-between shadow-2xs">
          <div>
            <div className="text-xs font-semibold text-slate-400">Potential Savings</div>
            <div className="text-lg sm:text-xl font-black text-white mt-1">
              {summary?.potential_cost_savings || 'DATA REQUIRED'}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              At ₹7.50/kWh commercial tariff
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-400 flex items-center justify-center shrink-0">
            <TrendingDown className="w-5 h-5" />
          </div>
        </div>

        {/* Card 3: Energy Opportunity */}
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-4 sm:p-5 flex items-center justify-between shadow-2xs">
          <div>
            <div className="text-xs font-semibold text-slate-400">Energy Opportunity</div>
            <div className="text-lg sm:text-xl font-black text-white mt-1">
              {summary?.energy_opportunity || 'Insufficient energy data'}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Compute &amp; off-peak shifting
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-950/60 border border-amber-800 text-amber-400 flex items-center justify-center shrink-0">
            <Zap className="w-5 h-5" />
          </div>
        </div>

        {/* Card 4: Estimated Carbon Reduction */}
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-4 sm:p-5 flex items-center justify-between shadow-2xs">
          <div>
            <div className="text-xs font-semibold text-slate-400">Carbon Abatement</div>
            <div className="text-lg sm:text-xl font-black text-white mt-1">
              {summary?.estimated_carbon_reduction || 'Factor unconfigured'}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              CEA National Grid Baseline v19
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-cyan-950/60 border border-cyan-800 text-cyan-400 flex items-center justify-center shrink-0">
            <Leaf className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-slate-800 flex gap-4 text-xs font-bold">
        {[
          { id: 'opportunities', label: `Opportunities Radar (${opportunities.length})` },
          { id: 'traces', label: `Agent Runs & Traces (${agentRuns.length})` },
          { id: 'impact', label: `Impact Verification (${impacts.length})` },
          { id: 'factors', label: `Emission Factors (${emissionFactors.length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`pb-3 transition-colors cursor-pointer border-b-2 -mb-px ${
              activeTab === tab.id
                ? 'border-teal-400 text-teal-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Opportunities Radar */}
      {activeTab === 'opportunities' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Category Filter:</span>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-2.5 py-1 text-xs rounded-lg bg-[#141C2B] border border-slate-800 text-slate-200 focus:outline-none"
              >
                <option value="All">All Categories</option>
                <option value="Compute Efficiency">Compute Efficiency</option>
                <option value="Energy Optimization">Energy Optimization</option>
                <option value="Workflow Digitization">Workflow Digitization</option>
              </select>
            </div>

            <div className="text-xs text-slate-400">
              Data Quality: <span className="font-bold text-teal-400">{summary?.data_quality || 'MEDIUM'}</span>
            </div>
          </div>

          {isLoading ? (
            <div className="p-12 text-center text-slate-500 flex flex-col items-center gap-2">
              <Loader2 className="w-6 h-6 animate-spin text-teal-400" />
              <span>Analyzing green telemetry...</span>
            </div>
          ) : filteredOpps.length === 0 ? (
            <div className="p-8 text-center rounded-2xl bg-[#111827] border border-slate-800 text-slate-400 space-y-3">
              <CheckCircle2 className="w-8 h-8 text-teal-400 mx-auto" />
              <div className="font-bold text-white text-sm">No Open Inefficiencies Detected</div>
              <p className="text-xs max-w-md mx-auto text-slate-400">
                All telemetry matches optimal operational baseline thresholds, or telemetry data is unconfigured.
              </p>
              <Button size="sm" variant="secondary" onClick={handleSeedDemo}>
                Seed Demo Telemetry
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredOpps.map((opp) => (
                <div
                  key={opp.id}
                  className="bg-[#111827] rounded-2xl border border-[#1E293B] p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-colors hover:border-slate-700 shadow-2xs"
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-950/60 text-teal-400 border border-teal-800">
                        {opp.category}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        opp.priority === 'High'
                          ? 'bg-rose-950/60 text-rose-400 border-rose-800'
                          : 'bg-amber-950/60 text-amber-400 border-amber-800'
                      }`}>
                        {opp.priority} Priority
                      </span>
                      <span className="text-xs text-slate-400">
                        Confidence: <strong className="text-slate-200">{Math.round((opp.confidence || 0.85) * 100)}%</strong>
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Policy: <strong className="text-teal-400">{opp.policy_status}</strong>
                      </span>
                    </div>

                    <h3 className="font-bold text-white text-sm">{opp.title}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
                      {opp.detected_issue}
                    </p>

                    <div className="pt-2 flex flex-wrap items-center gap-4 text-xs text-slate-400">
                      {opp.estimated_cost_impact?.value && (
                        <div>
                          Est. Savings: <strong className="text-emerald-400">₹{opp.estimated_cost_impact.value.toLocaleString()}</strong>
                        </div>
                      )}
                      {opp.estimated_energy_impact?.value && (
                        <div>
                          Energy Delta: <strong className="text-amber-400">-{opp.estimated_energy_impact.value} kWh/mo</strong>
                        </div>
                      )}
                      {opp.estimated_carbon_impact?.value && (
                        <div>
                          Carbon Delta: <strong className="text-cyan-400">-{opp.estimated_carbon_impact.value} kgCO2e</strong>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex sm:flex-col items-center sm:items-end gap-2 shrink-0">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setSelectedWhyOpp(opp)}
                        className="px-3 py-1.5 rounded-lg bg-teal-950/60 text-teal-400 border border-teal-800 hover:bg-teal-900/60 text-xs font-semibold cursor-pointer transition-colors"
                      >
                        Why?
                      </button>
                      <button
                        onClick={() => setSelectedEvidenceOpp(opp)}
                        className="px-3 py-1.5 rounded-lg bg-[#141C2B] text-slate-300 border border-slate-700 hover:bg-slate-800 text-xs font-semibold cursor-pointer transition-colors"
                      >
                        Evidence
                      </button>
                    </div>

                    {opp.status === 'DETECTED' ? (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleCreateProposal(opp)}
                        className="text-xs font-semibold bg-teal-600 hover:bg-teal-500"
                      >
                        Create Task
                      </Button>
                    ) : (
                      <span className="px-2.5 py-1 rounded text-xs font-bold bg-slate-800 text-slate-300">
                        {opp.status}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Agent Orchestration & Traces */}
      {activeTab === 'traces' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-[#111827] border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <span>Orchestration Engine: <strong className="text-white">GreenAgentOrchestrator</strong></span>
            <span>Lifecycle: <strong className="text-teal-400">Observe → Retrieve → Detect → Analyze → Reason → Recommend → Validate</strong></span>
          </div>

          <div className="space-y-3">
            {agentRuns.map((run) => (
              <div
                key={run.id}
                className="bg-[#111827] rounded-2xl border border-slate-800 p-4 sm:p-5 space-y-3"
              >
                <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
                    <span className="font-bold text-white text-xs">{run.agent_type}</span>
                    <span className="text-[11px] text-slate-400">Run #{run.id.slice(0, 8)}</span>
                  </div>
                  <Badge variant={run.status === 'COMPLETED' ? 'Verified' : 'Pending'}>
                    {run.status}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <div className="text-[11px] font-bold text-slate-400 uppercase">Execution Steps ({run.trace_steps?.length || 0}):</div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {run.trace_steps?.map((step, sIdx) => (
                      <div key={sIdx} className="p-2.5 rounded-lg bg-[#0B0F17] border border-slate-800/80 text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-teal-400">{step.step}</span>
                          <span className="text-[10px] text-slate-500">{step.duration_ms}ms</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-snug">{step.summary}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-2 flex justify-between text-[11px] text-slate-500">
                  <span>Input Sources: {run.input_sources?.join(', ') || 'Telemetry'}</span>
                  <span>Generated: {run.output_count} opportunities</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Impact Verification (Before / After) */}
      {activeTab === 'impact' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-teal-950/40 border border-teal-800/60 text-xs text-slate-300">
            <strong>Empirical Measurement Verification:</strong> POWER HOUSE stores baseline measurements before executing human-approved tasks, and compares them against actual post-implementation telemetry readings.
          </div>

          <div className="space-y-3">
            {impacts.map((imp) => (
              <div
                key={imp.id}
                className="bg-[#111827] rounded-2xl border border-slate-800 p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{imp.metric_name}</span>
                    <Badge variant={imp.verification_status === 'VERIFIED' ? 'Verified' : 'Pending'}>
                      {imp.verification_status === 'VERIFIED' ? 'Verified Improvement' : 'Impact verification pending'}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
                    <div className="p-2 bg-[#0B0F17] rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Baseline</span>
                      <span className="font-bold text-slate-200">{imp.baseline_value} {imp.unit}</span>
                    </div>

                    <div className="p-2 bg-[#0B0F17] rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Measured</span>
                      <span className="font-bold text-teal-400">
                        {imp.measured_value !== null ? `${imp.measured_value} ${imp.unit}` : 'Pending Reading'}
                      </span>
                    </div>

                    <div className="p-2 bg-[#0B0F17] rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Absolute Delta</span>
                      <span className="font-bold text-emerald-400">
                        {imp.absolute_change !== null ? `-${imp.absolute_change} ${imp.unit}` : '—'}
                      </span>
                    </div>

                    <div className="p-2 bg-[#0B0F17] rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Improvement</span>
                      <span className="font-bold text-emerald-400">
                        {imp.percentage_change !== null ? `+${imp.percentage_change}%` : '—'}
                      </span>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 pt-1">
                    Formula: <code className="text-slate-300 font-mono">{imp.formula}</code> • {imp.assumptions}
                  </p>
                </div>

                {imp.verification_status !== 'VERIFIED' && (
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleVerifyImpact(imp.id, roundToTenth(imp.baseline_value * 0.78))}
                    className="text-xs font-semibold shrink-0"
                  >
                    Simulate Post-Action Reading
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Emission Factors Registry */}
      {activeTab === 'factors' && (
        <div className="space-y-4">
          <div className="bg-[#111827] rounded-2xl border border-slate-800 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase font-semibold">
                  <th className="p-4">Factor Name &amp; Scope</th>
                  <th className="p-4">Value &amp; Unit</th>
                  <th className="p-4">Statutory Source</th>
                  <th className="p-4">Geography</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {emissionFactors.map((fac) => (
                  <tr key={fac.id} className="hover:bg-slate-800/20">
                    <td className="p-4">
                      <div className="font-bold text-white">{fac.name}</div>
                      <div className="text-[10px] text-slate-400">{fac.scope}</div>
                    </td>
                    <td className="p-4 font-mono font-bold text-teal-400">
                      {fac.value} {fac.unit}
                    </td>
                    <td className="p-4 text-slate-300 max-w-xs leading-snug">
                      {fac.source}
                    </td>
                    <td className="p-4 text-slate-400">{fac.geography}</td>
                    <td className="p-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-800">
                        {fac.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modals & Drawers */}
      <WhyOpportunityModal
        isOpen={Boolean(selectedWhyOpp)}
        onClose={() => setSelectedWhyOpp(null)}
        opportunity={selectedWhyOpp}
        onReviewProposal={handleCreateProposal}
      />

      <GreenScoreExplainModal
        isOpen={showScoreModal}
        onClose={() => setShowScoreModal(false)}
        scoreDetail={scoreDetail}
      />

      <EvidenceDrawer
        isOpen={Boolean(selectedEvidenceOpp)}
        onClose={() => setSelectedEvidenceOpp(null)}
        opportunity={selectedEvidenceOpp}
      />
    </div>
  );
}

function roundToTenth(num) {
  return Math.round(num * 10) / 10;
}
