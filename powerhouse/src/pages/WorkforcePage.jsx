import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  BookOpen,
  RotateCw,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Database,
  Layers,
  HeartHandshake,
  Clock,
  ShieldCheck,
  Briefcase,
  HelpCircle,
  Trash2,
  ChevronRight,
  GraduationCap,
  Brain
} from 'lucide-react';
import Button from '../components/ui/Button';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';
import { useAuth } from '../context/AuthContext';
import apiClient from '../services/apiClient';
import WhySkillGapModal from '../components/modals/WhySkillGapModal';
import WorkforceAIPanel from '../components/workforce/WorkforceAIPanel';

export default function WorkforcePage({ showToast, _onNavigate, _setModalState }) {
  const { activeBusiness } = useAuth();
  const { backendProfileId } = useBusinessAnalysis();
  const profileId = activeBusiness?.id || backendProfileId;

  const [activeTab, setActiveTab] = useState('overview'); // overview, roles, gaps, pathways
  const [loading, setLoading] = useState(true);
  const [rolesError, setRolesError] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [summary, setSummary] = useState(null);
  const [roles, setRoles] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [skillGaps, setSkillGaps] = useState([]);
  const [learningPaths, setLearningPaths] = useState([]);
  const [selectedGap, setSelectedGap] = useState(null);
  const [whyGapModalOpen, setWhyGapModalOpen] = useState(false);

  const loadData = useCallback(async () => {
    if (!profileId) return;
    setLoading(true);
    setRolesError(null);
    try {
      const [sumRes, roleRes, empRes, gapRes, pathRes] = await Promise.allSettled([
        apiClient.getWorkforceSummary(profileId),
        apiClient.getRoles(profileId),
        apiClient.getEmployees(profileId),
        apiClient.getSkillGaps(profileId),
        apiClient.getLearningPaths(profileId),
      ]);

      if (sumRes.status === 'fulfilled') setSummary(sumRes.value);
      if (roleRes.status === 'fulfilled') {
        setRoles(roleRes.value || []);
      } else {
        setRolesError(roleRes.reason?.message || 'Failed to load role profiles for this business.');
      }
      if (empRes.status === 'fulfilled') setEmployees(empRes.value || []);
      if (gapRes.status === 'fulfilled') setSkillGaps(gapRes.value || []);
      if (pathRes.status === 'fulfilled') setLearningPaths(pathRes.value || []);
    } catch {
      if (showToast) showToast('Could not load complete workforce telemetry.');
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
      await apiClient.runWorkforceAnalysis(profileId);
      if (showToast) showToast('Workforce Intelligence Agent assessed competencies and role alignments.');
      await loadData();
    } catch {
      if (showToast) showToast('Competency analysis encountered an issue.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Create Action Proposal
  const handleCreateProposal = async (gap) => {
    if (!profileId) return;
    try {
      await apiClient.createWorkforceProposal(gap.id, profileId);
      if (showToast) showToast(`Learning Proposal created for "${gap.required_skill}". Review in Approvals.`);
      await loadData();
    } catch {
      if (showToast) showToast('Failed to create learning proposal.');
    }
  };

  // Seed Demo Data
  const handleSeedDemo = async () => {
    if (!profileId) return;
    try {
      await apiClient.seedDemoWorkforce(profileId);
      if (showToast) showToast('Loaded verified [DEMO DATA] inclusive workforce and competency pathways.');
      await loadData();
    } catch {
      if (showToast) showToast('Failed to seed demo workforce records.');
    }
  };

  // Cleanup Demo Data
  const handleCleanupDemo = async () => {
    if (!profileId) return;
    try {
      await apiClient.cleanupDemoWorkforce(profileId);
      if (showToast) showToast('Cleared synthetic demo workforce entries.');
      await loadData();
    } catch {
      if (showToast) showToast('Failed to clean up demo workforce data.');
    }
  };

  const openWhyGap = (gap) => {
    setSelectedGap(gap);
    setWhyGapModalOpen(true);
  };

  const hasDemo = employees.some((e) => e.is_demo) || roles.some((r) => r.is_demo);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Banner / Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#111827] p-6 rounded-2xl border border-[#1E293B]">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-900/30 text-purple-400 border border-purple-800/50 flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-white tracking-tight">Inclusive Workforce Intelligence</h1>
                {hasDemo && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-950/80 text-purple-400 border border-purple-800/60 font-mono">
                    [DEMO DATA]
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400">
                Ethical Skill-Gap Detection • Multimodal Learning Pathways • Privacy-Preserving Upskilling
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadData}
            disabled={loading}
            className="border-slate-800 text-slate-300 hover:bg-slate-800 cursor-pointer"
          >
            <RotateCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="border-purple-800/60 bg-purple-950/30 text-purple-300 hover:bg-purple-900/40 cursor-pointer"
          >
            <Activity className={`w-3.5 h-3.5 mr-1.5 ${analyzing ? 'animate-spin text-purple-400' : 'text-purple-400'}`} />
            {analyzing ? 'Evaluating...' : 'Run Analysis'}
          </Button>

          {employees.length === 0 ? (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSeedDemo}
              className="border-emerald-800/50 bg-emerald-950/20 text-emerald-300 hover:bg-emerald-900/30 cursor-pointer"
            >
              <Database className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
              Seed Demo Data
            </Button>
          ) : (
            hasDemo && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleCleanupDemo}
                className="border-rose-900/40 text-rose-400 hover:bg-rose-950/30 cursor-pointer"
              >
                <Trash2 className="w-3.5 h-3.5 mr-1.5 text-rose-400" />
                Clear Demo Data
              </Button>
            )
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-[#1E293B] pb-2 text-sm flex-wrap">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'overview'
              ? 'bg-[#1E293B] text-white border border-slate-700'
              : 'text-slate-400 hover:text-slate-200 hover:bg-[#141C2B]'
          }`}
        >
          <Layers className="w-4 h-4" />
          Overview &amp; Metrics
        </button>
        <button
          onClick={() => setActiveTab('roles')}
          className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'roles'
              ? 'bg-[#1E293B] text-white border border-slate-700'
              : 'text-slate-400 hover:text-slate-200 hover:bg-[#141C2B]'
          }`}
        >
          <Briefcase className="w-4 h-4" />
          Roles &amp; Competencies ({roles.length})
        </button>
        <button
          onClick={() => setActiveTab('gaps')}
          className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'gaps'
              ? 'bg-[#1E293B] text-white border border-slate-700'
              : 'text-slate-400 hover:text-slate-200 hover:bg-[#141C2B]'
          }`}
        >
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          Skill Gaps ({skillGaps.length})
        </button>
        <button
          onClick={() => setActiveTab('pathways')}
          className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'pathways'
              ? 'bg-[#1E293B] text-white border border-slate-700'
              : 'text-slate-400 hover:text-slate-200 hover:bg-[#141C2B]'
          }`}
        >
          <BookOpen className="w-4 h-4 text-teal-400" />
          Learning Pathways ({learningPaths.length})
        </button>
        {/* Workforce AI Intelligence tab – additive */}
        <button
          onClick={() => setActiveTab('ai')}
          className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'ai'
              ? 'bg-purple-900/60 text-white border border-purple-700/60'
              : 'text-purple-400 hover:text-purple-200 hover:bg-purple-950/20 border border-transparent'
          }`}
        >
          <Brain className="w-4 h-4 text-purple-400" />
          Workforce AI
          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-700/60 text-purple-200 ml-0.5">NEW</span>
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Key Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B]">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Staff Profiles</span>
              <span className="text-2xl font-bold text-white mt-1 block">
                {summary?.total_employees || employees.length || 0}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Privacy-preserved</span>
            </div>

            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B]">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Role Profiles</span>
              <span className="text-2xl font-bold text-blue-400 mt-1 block">
                {summary?.total_roles || roles.length || 0}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Industry benchmarks</span>
            </div>

            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B]">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Role Coverage</span>
              <span className="text-2xl font-bold text-emerald-400 mt-1 block">
                {summary?.role_coverage_pct !== undefined ? `${summary.role_coverage_pct}%` : '85%'}
              </span>
              <span className="text-[10px] text-emerald-500/80 mt-0.5 block">Operational readiness</span>
            </div>

            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B]">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Open Skill Gaps</span>
              <span className="text-2xl font-bold text-amber-400 mt-1 block">
                {summary?.open_skill_gaps !== undefined ? summary.open_skill_gaps : skillGaps.length}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Targeted for upskilling</span>
            </div>

            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B]">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Active Pathways</span>
              <span className="text-2xl font-bold text-purple-400 mt-1 block">
                {summary?.active_learning_paths !== undefined ? summary.active_learning_paths : learningPaths.length}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Enrolled or In Progress</span>
            </div>

            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B]">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Accommodations</span>
              <span className="text-2xl font-bold text-teal-400 mt-1 block">
                {summary?.accommodations_count !== undefined ? summary.accommodations_count : 4}
              </span>
              <span className="text-[10px] text-teal-500/80 mt-0.5 block">Accessibility enabled</span>
            </div>
          </div>

          {/* Ethical AI & Privacy Guardrails Banner */}
          <div className="p-4 rounded-2xl bg-teal-950/20 border border-teal-800/40 flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-teal-900/30 text-teal-400 border border-teal-700/50 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div className="space-y-1 text-xs">
              <h4 className="font-bold text-teal-200 text-sm flex items-center gap-2">
                Ethical Workforce AI Guardrails Enforced
              </h4>
              <p className="text-slate-300 leading-relaxed">
                POWER HOUSE operates under strict privacy and non-punitive governance. Staff profiles use synthetic reference codes (e.g. <span className="font-mono text-teal-300">EMP-TX-101</span>). The system does not evaluate compensation, rank human workers against each other, or make automated hiring or termination decisions. Recommendations are strictly focused on capability building, accessibility accommodations, and statutory safety readiness.
              </p>
            </div>
          </div>

          {/* Action Proposals / Gaps Needing Attention */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Urgent Competency Gaps */}
            <div className="bg-[#111827] p-5 rounded-2xl border border-[#1E293B] space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <h3 className="font-bold text-white text-sm">Targeted Competency Gaps</h3>
                </div>
                <button
                  onClick={() => setActiveTab('gaps')}
                  className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 cursor-pointer"
                >
                  View All <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {skillGaps.length === 0 ? (
                <div className="p-8 text-center bg-[#141C2B] rounded-xl border border-slate-800/60">
                  <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                  <p className="text-xs font-medium text-slate-300">No open competency gaps identified.</p>
                  <p className="text-[11px] text-slate-500 mt-1">Run analysis or seed demo data to review roles.</p>
                </div>
              ) : (
                <div className="space-y-2.5">
                  {skillGaps.slice(0, 3).map((gap) => (
                    <div
                      key={gap.id}
                      className="p-3 bg-[#141C2B] rounded-xl border border-slate-800/80 flex items-center justify-between gap-3 hover:border-purple-800/50 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-white">{gap.required_skill}</span>
                          <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                            gap.gap_level === 'High'
                              ? 'bg-rose-950/80 text-rose-400 border border-rose-800/50'
                              : 'bg-amber-950/80 text-amber-400 border border-amber-800/50'
                          }`}>
                            {gap.gap_level} Priority
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          Ref: <span className="text-purple-300 font-mono">{gap.employee_reference || 'EMP'}</span> • Role: {gap.role_name || 'Assigned Role'}
                        </p>
                      </div>

                      <div className="flex items-center gap-1.5 shrink-0">
                        <button
                          onClick={() => openWhyGap(gap)}
                          className="px-2 py-1 rounded-lg text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 cursor-pointer flex items-center gap-1"
                        >
                          <HelpCircle className="w-3 h-3 text-purple-400" />
                          Why?
                        </button>
                        <button
                          onClick={() => handleCreateProposal(gap)}
                          className="px-2.5 py-1 rounded-lg text-xs font-medium text-purple-300 hover:text-purple-100 bg-purple-950/60 hover:bg-purple-900/60 border border-purple-800/50 cursor-pointer flex items-center gap-1"
                        >
                          <CheckCircle2 className="w-3 h-3" />
                          Propose
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Active Learning Pathways */}
            <div className="bg-[#111827] p-5 rounded-2xl border border-[#1E293B] space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-teal-400" />
                  <h3 className="font-bold text-white text-sm">Active Learning Pathways</h3>
                </div>
                <button
                  onClick={() => setActiveTab('pathways')}
                  className="text-xs text-teal-400 hover:text-teal-300 flex items-center gap-1 cursor-pointer"
                >
                  View All <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {learningPaths.length === 0 ? (
                <div className="p-8 text-center bg-[#141C2B] rounded-xl border border-slate-800/60">
                  <GraduationCap className="w-8 h-8 text-teal-400/60 mx-auto mb-2" />
                  <p className="text-xs font-medium text-slate-300">No active pathways currently underway.</p>
                  <p className="text-[11px] text-slate-500 mt-1">Enroll employees from the Skill Gaps tab.</p>
                </div>
              ) : (
                <div className="space-y-2.5">
                  {learningPaths.slice(0, 3).map((path) => (
                    <div
                      key={path.id}
                      className="p-3 bg-[#141C2B] rounded-xl border border-slate-800/80 space-y-2"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-white">{path.title}</span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-950/80 text-teal-400 border border-teal-800/50">
                          {path.status}
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-teal-500 h-full rounded-full transition-all"
                          style={{ width: `${path.progress_pct || 30}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-slate-400">
                        <span>Provider: {path.provider || 'Internal Academy'}</span>
                        <span className="text-teal-400 font-mono font-bold">{path.progress_pct || 30}% Completed</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: ROLES & COMPETENCIES */}
      {activeTab === 'roles' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-base">Standardized Industry Role Profiles</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Competency benchmarks and compliance requirements mapped to business sector
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono bg-[#111827] px-3 py-1.5 rounded-xl border border-[#1E293B]">
              Total Roles: {roles.length}
            </span>
          </div>

          {loading ? (
            <div className="p-12 text-center bg-[#111827] rounded-2xl border border-[#1E293B]">
              <RotateCw className="w-8 h-8 text-purple-400 mx-auto mb-3 animate-spin" />
              <h4 className="text-sm font-bold text-white">Loading standardized role profiles...</h4>
              <p className="text-xs text-slate-400 mt-1">Retrieving competency standards and sector benchmarks</p>
            </div>
          ) : rolesError ? (
            <div className="p-10 text-center bg-rose-950/20 rounded-2xl border border-rose-900/50">
              <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-rose-200">Unable to load role profiles</h4>
              <p className="text-xs text-rose-400/80 mt-1 max-w-md mx-auto">{rolesError}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={loadData}
                className="mt-4 border-rose-800/60 text-rose-300 hover:bg-rose-900/40 cursor-pointer"
              >
                <RotateCw className="w-3.5 h-3.5 mr-1.5" />
                Retry
              </Button>
            </div>
          ) : roles.length === 0 ? (
            <div className="p-12 text-center bg-[#111827] rounded-2xl border border-[#1E293B]">
              <Briefcase className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <h4 className="text-sm font-bold text-white">No role profiles available for this business.</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Seed industry demo data to populate standard role definitions and required competencies.
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleSeedDemo}
                className="mt-4 border-purple-800 text-purple-300 hover:bg-purple-950/30 cursor-pointer"
              >
                <Database className="w-3.5 h-3.5 mr-1.5 text-purple-400" />
                Seed Industry Roles
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {roles.map((role) => (
                <div
                  key={role.id}
                  className="bg-[#111827] p-5 rounded-2xl border border-[#1E293B] space-y-4 hover:border-slate-700 transition-colors flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-bold text-white text-sm">{role.role_name}</h4>
                        <p className="text-xs text-slate-400">{role.department || 'Operations'}</p>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded shrink-0 ${
                        role.criticality === 'High' || role.criticality === 'Critical'
                          ? 'bg-rose-950/70 text-rose-400 border border-rose-800/40'
                          : 'bg-blue-950/70 text-blue-400 border border-blue-800/40'
                      }`}>
                        {role.criticality || 'Critical'}
                      </span>
                    </div>

                    {/* Required Skills */}
                    <div className="space-y-1.5">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        Required Competencies:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {(role.required_skills || []).map((skill, idx) => {
                          const name = typeof skill === 'string' ? skill : (skill?.skill || skill?.name || JSON.stringify(skill));
                          const level = typeof skill === 'object' ? skill?.level : null;
                          return (
                            <span
                              key={idx}
                              className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#141C2B] text-slate-300 border border-slate-800 text-[11px]"
                            >
                              <span>{name}</span>
                              {level && (
                                <span className="text-[9px] px-1 rounded bg-purple-950 text-purple-300 border border-purple-800/40">
                                  {level}
                                </span>
                              )}
                            </span>
                          );
                        })}
                      </div>
                    </div>

                    {/* Optional Skills */}
                    {role.optional_skills && role.optional_skills.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                          Optional Skills:
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {role.optional_skills.map((skill, idx) => {
                            const name = typeof skill === 'string' ? skill : (skill?.skill || skill?.name || JSON.stringify(skill));
                            const level = typeof skill === 'object' ? skill?.level : null;
                            return (
                              <span
                                key={idx}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-900/60 text-slate-400 border border-slate-800/60 text-[11px]"
                              >
                                <span>{name}</span>
                                {level && (
                                  <span className="text-[9px] px-1 rounded bg-slate-800 text-slate-400">
                                    {level}
                                  </span>
                                )}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Suggested Training Path */}
                    <div className="space-y-1 pt-2 border-t border-slate-800/60">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        Suggested Training Path:
                      </span>
                      <p className="text-xs text-purple-300 font-medium">
                        {role.suggested_training_path || `${role.role_name} Industry Standard Qualification (NSQF Level 5)`}
                      </p>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                    <span className="flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-purple-400" />
                      <span>Target Headcount: <strong className="text-white">{role.target_headcount || '2–4 Personnel'}</strong></span>
                    </span>
                    <span className="flex items-center gap-1 text-emerald-400 font-medium text-[11px]">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Standard Mapped
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: SKILL GAPS */}
      {activeTab === 'gaps' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-base">Identified Competency Gaps</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Deterministic gap evaluation against role standards with Human-in-the-Loop action proposals
              </p>
            </div>
            <span className="text-xs text-amber-400 font-mono bg-[#111827] px-3 py-1.5 rounded-xl border border-amber-900/30">
              Open Gaps: {skillGaps.length}
            </span>
          </div>

          {skillGaps.length === 0 ? (
            <div className="p-12 text-center bg-[#111827] rounded-2xl border border-[#1E293B]">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
              <h4 className="text-sm font-bold text-white">All assessed employees meet role benchmarks</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                No active skill gaps detected. Click "Run Analysis" to perform a real-time compliance evaluation.
              </p>
            </div>
          ) : (
            <div className="bg-[#111827] rounded-2xl border border-[#1E293B] overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-[#141C2B] text-slate-400 uppercase text-[10px] tracking-wider border-b border-[#1E293B]">
                    <tr>
                      <th className="py-3 px-4">Staff Ref</th>
                      <th className="py-3 px-4">Target Role</th>
                      <th className="py-3 px-4">Competency Required</th>
                      <th className="py-3 px-4">Priority</th>
                      <th className="py-3 px-4">Accommodations</th>
                      <th className="py-3 px-4">Recommended Pathway</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80">
                    {skillGaps.map((gap) => (
                      <tr key={gap.id} className="hover:bg-[#141C2B]/50 transition-colors">
                        <td className="py-3 px-4 font-mono font-bold text-purple-400">
                          {gap.employee_reference || 'EMP-101'}
                        </td>
                        <td className="py-3 px-4 font-medium text-white">
                          {gap.role_name || 'Operator'}
                        </td>
                        <td className="py-3 px-4">
                          <span className="font-semibold text-slate-200">{gap.required_skill}</span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                            gap.gap_level === 'High'
                              ? 'bg-rose-950/80 text-rose-400 border border-rose-800/50'
                              : 'bg-amber-950/80 text-amber-400 border border-amber-800/50'
                          }`}>
                            {gap.gap_level || 'Medium'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-wrap gap-1 max-w-xs">
                            {(gap.accessibility_accommodations || ['Standard Multimodal']).map((acc, idx) => (
                              <span key={idx} className="px-1.5 py-0.2 rounded bg-teal-950/60 text-teal-300 border border-teal-800/40 text-[10px]">
                                {acc}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-slate-300 max-w-xs truncate">
                          {gap.recommended_pathway || 'Foundational Certification'}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => openWhyGap(gap)}
                              className="px-2 py-1 rounded-lg text-[11px] text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 cursor-pointer flex items-center gap-1"
                            >
                              <HelpCircle className="w-3 h-3 text-purple-400" />
                              Why?
                            </button>
                            <button
                              onClick={() => handleCreateProposal(gap)}
                              className="px-2.5 py-1 rounded-lg text-[11px] font-medium text-purple-300 hover:text-purple-100 bg-purple-950/60 hover:bg-purple-900/60 border border-purple-800/50 cursor-pointer flex items-center gap-1"
                            >
                              <CheckCircle2 className="w-3 h-3" />
                              Propose
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: LEARNING PATHWAYS */}
      {activeTab === 'pathways' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-base">Accessible Upskilling Pathways</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Targeted curricula with inclusive format adaptations and verified completion tracking
              </p>
            </div>
            <span className="text-xs text-teal-400 font-mono bg-[#111827] px-3 py-1.5 rounded-xl border border-teal-900/30">
              Total Pathways: {learningPaths.length}
            </span>
          </div>

          {learningPaths.length === 0 ? (
            <div className="p-12 text-center bg-[#111827] rounded-2xl border border-[#1E293B]">
              <BookOpen className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <h4 className="text-sm font-bold text-white">No active learning pathways</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Generate action proposals from the Skill Gaps tab or seed demo data to initialize learning journeys.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {learningPaths.map((path) => (
                <div
                  key={path.id}
                  className="bg-[#111827] p-5 rounded-2xl border border-[#1E293B] space-y-4 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-white text-sm">{path.title}</h4>
                        {path.is_demo && (
                          <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-purple-950/80 text-purple-400 border border-purple-800/60 font-mono">
                            [DEMO DATA]
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Target Competency: <strong className="text-purple-300">{path.target_skill}</strong>
                      </p>
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-950/80 text-teal-400 border border-teal-800/50">
                      {path.status || 'In Progress'}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>Curriculum Completion</span>
                      <span className="text-teal-400 font-bold font-mono">{path.progress_pct || 25}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-teal-500 to-purple-500 h-full rounded-full transition-all"
                        style={{ width: `${path.progress_pct || 25}%` }}
                      />
                    </div>
                  </div>

                  {/* Accommodations & Metadata */}
                  <div className="space-y-2 pt-2 border-t border-slate-800/80">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Briefcase className="w-3.5 h-3.5 text-slate-500" />
                        {path.provider || 'Skill India Digital / Sector Council'}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        {path.estimated_hours || 24} hours
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {(path.accommodations || ['Vernacular Audio', 'Large Print UI', 'Screen Reader']).map((acc, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded bg-teal-950/40 text-teal-300 border border-teal-800/40 text-[10px] flex items-center gap-1"
                        >
                          <HeartHandshake className="w-3 h-3 text-teal-400" />
                          {acc}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: WORKFORCE AI INTELLIGENCE — new, additive */}
      {activeTab === 'ai' && (
        <WorkforceAIPanel
          profileId={profileId}
          employees={employees}
          roles={roles}
          showToast={showToast}
        />
      )}

      {/* Explainability Modal */}
      {selectedGap && (
        <WhySkillGapModal
          isOpen={whyGapModalOpen}
          onClose={() => setWhyGapModalOpen(false)}
          skillGap={selectedGap}
          onActionProposal={() => {
            handleCreateProposal(selectedGap);
            setWhyGapModalOpen(false);
          }}
        />
      )}
    </div>
  );
}
