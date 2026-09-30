import React, { useState } from 'react';
import {
  BrainCircuit,
  RefreshCw,
  ArrowLeft,
  FileCheck,
  CheckSquare,
  FolderKanban,
  Gift,
  AlertTriangle,
  Info,
  CheckCircle2,
  Building,
  Calendar,
  Activity,
  TrendingUp,
  Clock,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function BusinessAnalysisPage({ onNavigate, showToast, setModalState }) {
  const { analysisResult, isAnalyzing, runAnalysis, businessProfile } = useBusinessAnalysis();
  const [activeTab, setActiveTab] = useState('approvals');

  const handleReRun = async () => {
    showToast('Executing deterministic business analysis engine...');
    await runAnalysis(businessProfile);
    showToast('Business analysis successfully updated.');
  };

  if (!analysisResult || !analysisResult.isValid) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200/90 p-8 text-center max-w-2xl mx-auto my-8 space-y-4">
        <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-100">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-slate-900">Incomplete Business Profile</h2>
        <p className="text-xs text-slate-500 leading-relaxed max-w-md mx-auto">
          {analysisResult?.message || 'Complete your business profile to generate accurate compliance and scheme recommendations.'}
        </p>
        <Button
          variant="primary"
          size="sm"
          onClick={() => onNavigate('business-profile')}
          className="text-xs font-semibold"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Edit Business Profile</span>
        </Button>
      </div>
    );
  }

  const { businessSummary, summary, riskLevel, approvals, complianceTasks, requiredDocuments, recommendedSchemes, insights } = analysisResult;

  const tabs = [
    { id: 'approvals', label: 'Required Approvals', count: approvals.length, icon: FileCheck },
    { id: 'tasks', label: 'Compliance Tasks', count: complianceTasks.length, icon: CheckSquare },
    { id: 'documents', label: 'Document Checklist', count: requiredDocuments.length, icon: FolderKanban },
    { id: 'schemes', label: 'Matched Schemes', count: recommendedSchemes.length, icon: Gift },
  ];

  return (
    <div className="space-y-6">
      {/* Top Navigation & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('business-profile')}
            className="p-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 hover:text-slate-900 transition-colors cursor-pointer shadow-2xs"
            title="Back to Business Profile"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
                Intelligence Engine v1.0
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                Deterministic Rule-Based
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight mt-0.5">
              Business Analysis
            </h1>
            <p className="text-xs sm:text-sm text-slate-500">
              Personalized business intelligence generated from your business profile.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleReRun}
            disabled={isAnalyzing}
            className="text-xs font-semibold"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin text-blue-600' : ''}`} />
            <span>{isAnalyzing ? 'Analyzing...' : 'Re-run Analysis'}</span>
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => onNavigate('dashboard')}
            className="text-xs font-semibold"
          >
            <span>View on Dashboard</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Section 1: Business Overview Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 sm:p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-base shadow-sm">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900">
                  {businessSummary.businessName}
                </h2>
                <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-semibold">
                  {businessSummary.businessType}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {businessSummary.industry} • {businessSummary.sector} • {businessSummary.city}, {businessSummary.state}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-[11px] text-slate-400 font-semibold uppercase">Statutory Risk Rating</div>
              <div className="flex items-center gap-1.5 justify-end mt-0.5">
                <span className={`w-2 h-2 rounded-full ${
                  riskLevel === 'High' ? 'bg-rose-500' : riskLevel === 'Medium' ? 'bg-amber-500' : 'bg-emerald-500'
                }`} />
                <span className="text-xs font-bold text-slate-900">{riskLevel} Risk Profile</span>
              </div>
            </div>
            <div className="w-px h-8 bg-slate-200 hidden sm:block" />
            <div className="text-right hidden sm:block">
              <div className="text-[11px] text-slate-400 font-semibold uppercase">Analysis Date</div>
              <div className="text-xs font-bold text-slate-700 mt-0.5">{analysisResult.analysisDate}</div>
            </div>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 block text-[11px]">Workforce Size</span>
            <span className="font-bold text-slate-900 text-sm mt-0.5 block">{businessSummary.employees} Employees</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 block text-[11px]">Turnover Tier</span>
            <span className="font-bold text-slate-900 text-sm mt-0.5 block">{businessSummary.annualTurnover}</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 block text-[11px]">GST Status</span>
            <span className="font-mono font-bold text-slate-900 text-xs mt-0.5 block truncate">{businessSummary.gstin || 'Active'}</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 block text-[11px]">Udyam MSME</span>
            <span className="font-mono font-bold text-slate-900 text-xs mt-0.5 block truncate">{businessSummary.udyamNumber || 'Active'}</span>
          </div>
        </div>
      </div>

      {/* Section 2: Summary Stats (4 Metrics) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-5">
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500">Approvals Required</div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 mt-1">{summary.totalApprovals}</div>
            <div className="text-[11px] text-rose-600 font-semibold mt-0.5">{summary.highPriorityApprovals} High Priority</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100 shrink-0">
            <FileCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500">Compliance Tasks</div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 mt-1">{summary.complianceTasks}</div>
            <div className="text-[11px] text-amber-600 font-semibold mt-0.5">{summary.upcomingTasks} upcoming deadlines</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100 shrink-0">
            <CheckSquare className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500">Document Requirements</div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 mt-1">{summary.requiredDocuments}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Vault items categorized</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center border border-sky-100 shrink-0">
            <FolderKanban className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500">Matched Schemes</div>
            <div className="text-xl sm:text-2xl font-black text-emerald-600 mt-1">{summary.recommendedSchemes}</div>
            <div className="text-[11px] text-emerald-600 font-semibold mt-0.5">Up to 35% subsidies</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100 shrink-0">
            <Gift className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Section 3: Key Insights Generated by Rules */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 sm:p-6 space-y-3">
        <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
          <Activity className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Rule-Generated Business Insights
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {insights.map((insight) => (
            <div
              key={insight.id}
              className={`p-3.5 rounded-xl border flex items-start gap-3 ${
                insight.severity === 'warning'
                  ? 'bg-amber-50/50 border-amber-200/80 text-amber-900'
                  : insight.severity === 'success'
                  ? 'bg-emerald-50/50 border-emerald-200/80 text-emerald-900'
                  : 'bg-blue-50/50 border-blue-200/80 text-blue-900'
              }`}
            >
              <div
                className={`p-1.5 rounded-lg shrink-0 mt-0.5 ${
                  insight.severity === 'warning'
                    ? 'bg-amber-100 text-amber-700'
                    : insight.severity === 'success'
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-blue-100 text-blue-700'
                }`}
              >
                {insight.severity === 'warning' ? (
                  <AlertTriangle className="w-4 h-4" />
                ) : insight.severity === 'success' ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <Info className="w-4 h-4" />
                )}
              </div>
              <div>
                <h3 className="text-xs font-bold">{insight.title}</h3>
                <p className="text-xs mt-0.5 opacity-90 leading-relaxed">{insight.message}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 4: Detailed Breakdown Tabs */}
      <div className="space-y-4">
        {/* Tab Switcher */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20'
                    : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200/80'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                <span
                  className={`px-1.5 py-0.2 text-[10px] rounded-full font-bold ${
                    isActive ? 'bg-white text-blue-700' : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Tab 1: Approvals Deep Dive */}
        {activeTab === 'approvals' && (
          <div className="space-y-3">
            {approvals.map((appr) => (
              <div
                key={appr.id}
                className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 hover:border-blue-200 transition-all space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                        {appr.category}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          appr.priority === 'High'
                            ? 'bg-rose-50 text-rose-700 border border-rose-200'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {appr.priority} Priority
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-900 mt-1.5">{appr.name}</h3>
                    <div className="text-xs text-slate-500 mt-0.5">{appr.authority}</div>
                  </div>

                  <Badge variant={appr.status} withDot size="xs">
                    {appr.status}
                  </Badge>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">{appr.description}</p>

                {/* Trigger Reason Box */}
                <div className="p-3 bg-blue-50/60 rounded-xl border border-blue-100 text-xs text-blue-950 flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold block text-[11px] uppercase tracking-wider text-blue-700">Rule Logic Trigger</span>
                    <p className="mt-0.5">{appr.triggerReason}</p>
                  </div>
                </div>

                {/* Milestone Steps */}
                <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <span className="font-semibold text-slate-600">{appr.dueDate}</span>
                  <button
                    onClick={() => onNavigate('approvals')}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
                  >
                    <span>View in Approvals Hub</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 2: Compliance Tasks Deep Dive */}
        {activeTab === 'tasks' && (
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs divide-y divide-slate-100 overflow-hidden">
            {complianceTasks.map((task) => (
              <div key={task.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/70 transition-colors">
                <div className="space-y-1 min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-xs sm:text-sm font-bold text-slate-900">{task.title}</h3>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
                        task.priority === 'High'
                          ? 'bg-rose-50 text-rose-700 border-rose-200'
                          : 'bg-amber-50 text-amber-700 border-amber-200'
                      }`}
                    >
                      {task.priority}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed">{task.description}</p>
                  <div className="text-[11px] text-slate-400 pt-0.5 flex items-center gap-2">
                    <span className="font-medium text-blue-600">Related: {task.relatedApproval}</span>
                    <span>•</span>
                    <span>{task.assignee}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100">
                  <div className="text-right">
                    <span className="text-xs font-semibold text-slate-700 block">{task.dueDate}</span>
                    <Badge variant={task.status} withDot size="xs" className="mt-0.5">
                      {task.status}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 3: Document Checklist Deep Dive */}
        {activeTab === 'documents' && (
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden">
            <div className="divide-y divide-slate-100">
              {requiredDocuments.map((doc) => (
                <div key={doc.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/70 transition-colors">
                  <div className="flex items-center gap-3.5 min-w-0 flex-1">
                    <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-[10px] border border-blue-100 shrink-0">
                      {doc.fileType}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-xs sm:text-sm font-bold text-slate-900">{doc.name}</h3>
                        <Badge variant={doc.status} withDot size="xs">
                          {doc.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{doc.description}</p>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Approval: {doc.relatedApproval} • Expiry: {doc.expiryDate}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Matched Schemes Deep Dive */}
        {activeTab === 'schemes' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendedSchemes.map((scheme) => (
              <div
                key={scheme.id}
                className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-5 hover:border-blue-200 transition-all flex flex-col justify-between space-y-3"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                      {scheme.category}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {scheme.matchPercentage}% Match
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900">{scheme.name}</h3>
                  <p className="text-xs text-slate-500 leading-relaxed">{scheme.description}</p>

                  <div className="p-2.5 bg-emerald-50/70 border border-emerald-100 rounded-xl">
                    <span className="text-[10px] font-bold uppercase text-emerald-800">Benefit</span>
                    <div className="text-xs font-bold text-emerald-950 mt-0.5">{scheme.benefit}</div>
                  </div>

                  {/* Match Reasons */}
                  <div className="space-y-1 pt-1">
                    <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Score Breakdown</span>
                    <ul className="text-[11px] text-slate-600 space-y-0.5">
                      {scheme.matchReasons?.map((r, i) => (
                        <li key={i} className="flex items-center gap-1.5">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-[11px] text-slate-400">{scheme.deadline}</span>
                  <button
                    onClick={() => onNavigate('government-schemes')}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
                  >
                    <span>Scheme Catalog</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Subtle Prototype Disclaimer */}
      <div className="p-3.5 rounded-xl bg-slate-100/70 border border-slate-200 text-center text-slate-400 text-[11px]">
        Recommendations and statutory roadmaps are generated for prototype planning and business intelligence simulation. Always verify final filing mandates with respective state and central authorities.
      </div>
    </div>
  );
}
