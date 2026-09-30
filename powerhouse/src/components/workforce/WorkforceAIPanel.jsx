/**
 * WorkforceAIPanel.jsx
 * 
 * AI-powered Workforce Intelligence panel integrated into the existing
 * PowerHouse Workforce section. Provides:
 *  - Resume Upload & AI extraction (NuExtract)
 *  - Skill Gap Analysis (Skill-Sim)
 *  - Role Matching (NBK ATS Semantic)
 *  - Career Recommendations & Development Plans (Qwen / structured engine)
 *  - Workforce AI Chat assistant
 *  - Full Employee AI Analysis
 * 
 * Design: Uses the existing PowerHouse dark theme system.
 * No external dependencies beyond what's already in the project.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Brain,
  Upload,
  Zap,
  Target,
  TrendingUp,
  MessageSquare,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ChevronRight,
  ChevronDown,
  Star,
  Award,
  BarChart3,
  Cpu,
  FileText,
  User,
  Search,
  Send,
  RotateCw,
  Sparkles,
  ArrowRight,
  Info,
} from 'lucide-react';
import apiClient from '../../services/apiClient';

// ─────────────────────────────────────────────────────────────────────────────
// Sub-tab constants
// ─────────────────────────────────────────────────────────────────────────────
const AI_TABS = [
  { id: 'resume',   icon: Upload,       label: 'Resume AI' },
  { id: 'skills',   icon: Zap,          label: 'Skill Analysis' },
  { id: 'match',    icon: Target,       label: 'Role Match' },
  { id: 'career',   icon: TrendingUp,   label: 'Career Plan' },
  { id: 'chat',     icon: MessageSquare, label: 'AI Chat' },
];

// ─────────────────────────────────────────────────────────────────────────────
// Small reusable UI atoms (all use existing PowerHouse class patterns)
// ─────────────────────────────────────────────────────────────────────────────

function AIBadge({ available }) {
  if (available === null || available === undefined) return null;
  return available ? (
    <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/50 font-medium">
      <Cpu className="w-2.5 h-2.5" /> AI Active
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700/60 font-medium">
      <Cpu className="w-2.5 h-2.5" /> Structured Analysis
    </span>
  );
}

function LoadingSpinner({ text = 'Analyzing…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="relative">
        <div className="w-10 h-10 rounded-full border-2 border-purple-900/40 border-t-purple-500 animate-spin" />
        <Brain className="w-4 h-4 text-purple-400 absolute inset-0 m-auto" />
      </div>
      <p className="text-xs text-slate-400 font-medium">{text}</p>
    </div>
  );
}

function ErrorBanner({ message }) {
  return (
    <div className="flex items-start gap-3 p-4 bg-rose-950/20 rounded-xl border border-rose-900/40">
      <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
      <p className="text-xs text-rose-300">{message}</p>
    </div>
  );
}

function SkillBadge({ skill, variant = 'match' }) {
  const styles = {
    match:   'bg-emerald-950/40 text-emerald-300 border-emerald-800/40',
    missing: 'bg-rose-950/40 text-rose-300 border-rose-800/40',
    related: 'bg-amber-950/40 text-amber-300 border-amber-800/40',
    neutral: 'bg-slate-800/60 text-slate-300 border-slate-700/40',
  };
  return (
    <span className={`inline-flex items-center text-[11px] px-2 py-0.5 rounded border font-medium ${styles[variant] || styles.neutral}`}>
      {skill}
    </span>
  );
}

function CoverageBar({ percent, label }) {
  const color =
    percent >= 70 ? 'from-emerald-500 to-teal-500' :
    percent >= 40 ? 'from-amber-500 to-orange-500' :
    'from-rose-500 to-pink-500';
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400">{label || 'Skill Coverage'}</span>
        <span className={`font-bold font-mono ${percent >= 70 ? 'text-emerald-400' : percent >= 40 ? 'text-amber-400' : 'text-rose-400'}`}>
          {percent}%
        </span>
      </div>
      <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-700`}
          style={{ width: `${Math.min(100, percent)}%` }}
        />
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Resume AI Tab
// ─────────────────────────────────────────────────────────────────────────────

function ResumeAITab({ profileId, showToast }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.type === 'application/pdf') {
      setFile(droppedFile);
      setResult(null);
      setError(null);
    } else {
      setError('Please upload a PDF file.');
    }
  };

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFile(f);
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file || !profileId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.analyzeResume(profileId, file);
      setResult(res);
      if (showToast) showToast('Resume analyzed successfully.');
    } catch (e) {
      setError(e.message || 'Resume analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-3 p-4 bg-purple-950/10 rounded-xl border border-purple-900/30">
        <Brain className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-purple-200">NuExtract Resume Intelligence</p>
          <p className="text-slate-400">
            Upload a resume PDF. Our AI extracts name, contact, skills, experience, education,
            and certifications into a structured profile — ready for skill analysis and role matching.
          </p>
        </div>
      </div>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all
          ${file
            ? 'border-purple-700/70 bg-purple-950/10'
            : 'border-slate-700/60 hover:border-purple-700/50 hover:bg-purple-950/5'
          }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleFileChange}
        />
        {file ? (
          <div className="space-y-2">
            <FileText className="w-8 h-8 text-purple-400 mx-auto" />
            <p className="text-sm font-semibold text-white">{file.name}</p>
            <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB • Click to change</p>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="w-8 h-8 text-slate-500 mx-auto" />
            <p className="text-sm font-medium text-slate-300">Drop resume PDF here or click to browse</p>
            <p className="text-xs text-slate-500">PDF files only • Max 10 MB</p>
          </div>
        )}
      </div>

      {file && (
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full py-2.5 rounded-xl text-sm font-semibold bg-purple-700 hover:bg-purple-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
        >
          {loading ? <RotateCw className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
          {loading ? 'Analyzing Resume…' : 'Analyze Resume'}
        </button>
      )}

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner text="NuExtract is reading your resume…" />}

      {result && !loading && (
        <div className="space-y-4 animate-in fade-in duration-500">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Extracted Profile
            </h4>
            <AIBadge available={result.ai_available !== false && !result.error} />
          </div>

          {result.error && <ErrorBanner message={`AI extraction error: ${result.error}. Skills may be incomplete.`} />}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Identity */}
            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B] space-y-2">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Contact</p>
              <div className="space-y-1 text-xs">
                {result.name && <p className="text-white font-semibold">{result.name}</p>}
                {result.email && <p className="text-slate-300">{result.email}</p>}
                {result.phone && <p className="text-slate-300">{result.phone}</p>}
                {result.website && <p className="text-purple-300">{result.website}</p>}
                {!result.name && !result.email && <p className="text-slate-500 italic">Contact information not detected</p>}
              </div>
            </div>

            {/* Skills */}
            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B] space-y-2">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Skills ({result.skills?.length || 0})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {(result.skills || []).map((s, i) => (
                  <SkillBadge key={i} skill={s} variant="neutral" />
                ))}
                {(!result.skills?.length) && <p className="text-slate-500 text-xs italic">No skills detected</p>}
              </div>
            </div>
          </div>

          {/* Experience */}
          {result.experience?.length > 0 && (
            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B] space-y-3">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Experience</p>
              {result.experience.map((e, i) => (
                <div key={i} className="flex items-start gap-3 text-xs">
                  <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0" />
                  <div>
                    <span className="font-semibold text-white">{e.title}</span>
                    {e.company && <span className="text-slate-400"> · {e.company}</span>}
                    {e.duration && <span className="text-slate-500"> · {e.duration}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Education */}
          {result.education?.length > 0 && (
            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B] space-y-3">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Education</p>
              {result.education.map((e, i) => (
                <div key={i} className="flex items-start gap-3 text-xs">
                  <div className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 shrink-0" />
                  <div>
                    <span className="font-semibold text-white">{e.degree}</span>
                    {e.institution && <span className="text-slate-400"> · {e.institution}</span>}
                    {e.year && <span className="text-slate-500"> · {e.year}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Other details */}
          {result.other_details?.length > 0 && (
            <div className="bg-[#111827] p-4 rounded-xl border border-[#1E293B] space-y-2">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Certifications & Other</p>
              <div className="flex flex-wrap gap-1.5">
                {result.other_details.map((d, i) => (
                  <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/40">{d}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Skill Analysis Tab
// ─────────────────────────────────────────────────────────────────────────────

function SkillAnalysisTab({ profileId, employees, roles, showToast }) {
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!selectedEmployee || !profileId) return;
    setLoading(true);
    setError(null);
    try {
      const payload = { employee_id: selectedEmployee };
      if (selectedRole) payload.role_id = selectedRole;
      const res = await apiClient.analyzeSkillGap(profileId, payload);
      setResult(res);
    } catch (e) {
      setError(e.message || 'Skill analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-3 p-4 bg-blue-950/10 rounded-xl border border-blue-900/30">
        <Zap className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-blue-200">Skill-Sim Semantic Intelligence</p>
          <p className="text-slate-400">
            Semantic skill matching using ESCO-trained embeddings. Detects related skills even when
            terminology differs (e.g. "ML" ≈ "Machine Learning", "JS" ≈ "JavaScript").
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Employee</label>
          <select
            value={selectedEmployee}
            onChange={(e) => { setSelectedEmployee(e.target.value); setResult(null); }}
            className="w-full bg-[#111827] border border-[#1E293B] text-white text-sm rounded-xl px-3 py-2.5 focus:outline-none focus:border-blue-700/60 cursor-pointer"
          >
            <option value="">Select employee…</option>
            {employees.map((e) => (
              <option key={e.id} value={e.id}>
                {e.employee_reference} — {e.role}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Target Role (optional)</label>
          <select
            value={selectedRole}
            onChange={(e) => { setSelectedRole(e.target.value); setResult(null); }}
            className="w-full bg-[#111827] border border-[#1E293B] text-white text-sm rounded-xl px-3 py-2.5 focus:outline-none focus:border-blue-700/60 cursor-pointer"
          >
            <option value="">Auto-detect from employee role</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>{r.role_name}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={handleAnalyze}
        disabled={!selectedEmployee || loading}
        className="w-full py-2.5 rounded-xl text-sm font-semibold bg-blue-700 hover:bg-blue-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
      >
        {loading ? <RotateCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
        {loading ? 'Analyzing Skills…' : 'Analyze Skill Gap'}
      </button>

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner text="Skill-Sim is computing semantic similarity…" />}

      {result && !loading && (
        <div className="space-y-4 animate-in fade-in duration-500">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-400" />
              Skill Gap Analysis
            </h4>
            <AIBadge available={result.ai_available} />
          </div>

          <CoverageBar percent={result.coverage_percent || 0} label="Role Skill Coverage" />

          {result.explanation && (
            <div className="p-4 bg-[#111827] rounded-xl border border-[#1E293B] text-xs text-slate-300 leading-relaxed">
              <p className="font-semibold text-white mb-1 flex items-center gap-1.5">
                <Brain className="w-3.5 h-3.5 text-blue-400" /> AI Insight
              </p>
              {result.explanation}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="bg-[#111827] p-4 rounded-xl border border-emerald-900/30 space-y-2">
              <p className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5" /> Matching ({result.matching_skills?.length || 0})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {(result.matching_skills || []).map((s, i) => <SkillBadge key={i} skill={s} variant="match" />)}
                {!result.matching_skills?.length && <p className="text-slate-500 text-xs italic">None detected</p>}
              </div>
            </div>
            <div className="bg-[#111827] p-4 rounded-xl border border-amber-900/30 space-y-2">
              <p className="text-[11px] font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" /> Related ({result.related_skills?.length || 0})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {(result.related_skills || []).map((s, i) => <SkillBadge key={i} skill={s} variant="related" />)}
                {!result.related_skills?.length && <p className="text-slate-500 text-xs italic">None</p>}
              </div>
            </div>
            <div className="bg-[#111827] p-4 rounded-xl border border-rose-900/30 space-y-2">
              <p className="text-[11px] font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                <XCircle className="w-3.5 h-3.5" /> Missing ({result.missing_skills?.length || 0})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {(result.missing_skills || []).map((s, i) => <SkillBadge key={i} skill={s} variant="missing" />)}
                {!result.missing_skills?.length && <p className="text-slate-500 text-xs italic">All covered ✓</p>}
              </div>
            </div>
          </div>

          {result.skill_pairs?.length > 0 && (
            <details className="group">
              <summary className="cursor-pointer text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 py-2">
                <ChevronRight className="w-3.5 h-3.5 group-open:rotate-90 transition-transform" />
                Detailed Skill Pairs ({result.skill_pairs.length})
              </summary>
              <div className="mt-2 space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {result.skill_pairs.map((pair, i) => (
                  <div key={i} className="flex items-center justify-between text-xs px-3 py-1.5 bg-[#111827] rounded-lg border border-[#1E293B]">
                    <span className="text-white font-medium">{pair.required}</span>
                    <div className="flex items-center gap-2">
                      {pair.best_match && <span className="text-slate-400">{pair.best_match}</span>}
                      <span className={`font-mono text-[10px] px-1.5 py-0.5 rounded ${
                        pair.status === 'match' ? 'bg-emerald-950/60 text-emerald-400' :
                        pair.status === 'related' ? 'bg-amber-950/60 text-amber-400' :
                        'bg-rose-950/60 text-rose-400'
                      }`}>
                        {(pair.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Role Match Tab
// ─────────────────────────────────────────────────────────────────────────────

function RoleMatchTab({ profileId, employees, roles, showToast }) {
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleMatch = async () => {
    if (!selectedEmployee || !profileId) return;
    setLoading(true);
    setError(null);
    try {
      const payload = { employee_id: selectedEmployee };
      if (selectedRole) payload.role_id = selectedRole;
      const res = await apiClient.matchEmployeeToRole(profileId, payload);
      setResult(res);
    } catch (e) {
      setError(e.message || 'Role matching failed.');
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (!score) return 'text-slate-400';
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-amber-400';
    return 'text-rose-400';
  };

  const scoreBg = (score) => {
    if (!score) return 'border-slate-700/50 bg-slate-800/40';
    if (score >= 80) return 'border-emerald-800/50 bg-emerald-950/20';
    if (score >= 60) return 'border-amber-800/50 bg-amber-950/20';
    return 'border-rose-800/50 bg-rose-950/20';
  };

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-3 p-4 bg-teal-950/10 rounded-xl border border-teal-900/30">
        <Target className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-teal-200">NBK ATS Semantic Role Matching</p>
          <p className="text-slate-400">
            Semantic similarity between employee profile and role requirements using 8,192-token context.
            Ensemble scoring (Ridge + Neural) for calibrated ATS match scores.
            Results are AI analysis signals — not hiring decisions.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Employee</label>
          <select
            value={selectedEmployee}
            onChange={(e) => { setSelectedEmployee(e.target.value); setResult(null); }}
            className="w-full bg-[#111827] border border-[#1E293B] text-white text-sm rounded-xl px-3 py-2.5 focus:outline-none focus:border-teal-700/60 cursor-pointer"
          >
            <option value="">Select employee…</option>
            {employees.map((e) => (
              <option key={e.id} value={e.id}>{e.employee_reference} — {e.role}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Target Role</label>
          <select
            value={selectedRole}
            onChange={(e) => { setSelectedRole(e.target.value); setResult(null); }}
            className="w-full bg-[#111827] border border-[#1E293B] text-white text-sm rounded-xl px-3 py-2.5 focus:outline-none focus:border-teal-700/60 cursor-pointer"
          >
            <option value="">Auto-detect primary role</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>{r.role_name}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={handleMatch}
        disabled={!selectedEmployee || loading}
        className="w-full py-2.5 rounded-xl text-sm font-semibold bg-teal-700 hover:bg-teal-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
      >
        {loading ? <RotateCw className="w-4 h-4 animate-spin" /> : <Target className="w-4 h-4" />}
        {loading ? 'Running AI Match…' : 'Analyze Role Match'}
      </button>

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner text="NBK ATS is computing semantic match…" />}

      {result && !loading && (
        <div className="space-y-4 animate-in fade-in duration-500">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white">AI Match Analysis</h4>
            <AIBadge available={result.ai_available} />
          </div>

          {/* Score card */}
          <div className={`p-5 rounded-2xl border ${scoreBg(result.ats_score)}`}>
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Role</p>
                <p className="text-lg font-bold text-white">{result.role_name}</p>
                <p className={`text-sm font-semibold mt-1 ${scoreColor(result.ats_score)}`}>
                  {result.fit_label}
                </p>
              </div>
              {result.ats_score != null && (
                <div className="text-right">
                  <p className="text-[11px] text-slate-400 uppercase tracking-wider">AI Match Score</p>
                  <p className={`text-4xl font-black font-mono ${scoreColor(result.ats_score)}`}>
                    {result.ats_score.toFixed(0)}<span className="text-xl">%</span>
                  </p>
                </div>
              )}
            </div>
            {result.match_explanation && (
              <p className="text-xs text-slate-300 mt-3 leading-relaxed border-t border-white/5 pt-3">
                {result.match_explanation}
              </p>
            )}
          </div>

          <div className="p-3 bg-amber-950/10 border border-amber-800/20 rounded-xl flex items-start gap-2">
            <Info className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
            <p className="text-[11px] text-amber-300/80 leading-relaxed">
              AI Match scores are development signals, not hiring or firing recommendations.
              All workforce decisions require human review.
            </p>
          </div>

          <CoverageBar percent={result.skill_coverage_percent || 0} label="Skill-Level Coverage" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="bg-[#111827] p-3 rounded-xl border border-emerald-900/30 space-y-2">
              <p className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">Matching</p>
              <div className="flex flex-wrap gap-1.5">
                {(result.matching_skills || []).map((s, i) => <SkillBadge key={i} skill={s} variant="match" />)}
                {!result.matching_skills?.length && <p className="text-slate-500 text-xs italic">None</p>}
              </div>
            </div>
            <div className="bg-[#111827] p-3 rounded-xl border border-amber-900/30 space-y-2">
              <p className="text-[11px] font-bold text-amber-400 uppercase tracking-wider">Related</p>
              <div className="flex flex-wrap gap-1.5">
                {(result.related_skills || []).map((s, i) => <SkillBadge key={i} skill={s} variant="related" />)}
                {!result.related_skills?.length && <p className="text-slate-500 text-xs italic">None</p>}
              </div>
            </div>
            <div className="bg-[#111827] p-3 rounded-xl border border-rose-900/30 space-y-2">
              <p className="text-[11px] font-bold text-rose-400 uppercase tracking-wider">Development Areas</p>
              <div className="flex flex-wrap gap-1.5">
                {(result.missing_skills || []).map((s, i) => <SkillBadge key={i} skill={s} variant="missing" />)}
                {!result.missing_skills?.length && <p className="text-slate-500 text-xs italic">All covered</p>}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Career Plan Tab
// ─────────────────────────────────────────────────────────────────────────────

function CareerPlanTab({ profileId, employees, roles, showToast }) {
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [mode, setMode] = useState('career'); // career | plan
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!selectedEmployee || !profileId) return;
    setLoading(true);
    setError(null);
    try {
      if (mode === 'career') {
        const payload = { employee_id: selectedEmployee };
        if (selectedRole) payload.target_role_id = selectedRole;
        const res = await apiClient.getCareerRecommendation(profileId, payload);
        setResult({ type: 'career', data: res });
      } else {
        const targetRole = roles.find(r => r.id === selectedRole)?.role_name || 'Senior ' + (employees.find(e => e.id === selectedEmployee)?.role || 'Role');
        const res = await apiClient.getDevelopmentPlan(profileId, {
          employee_id: selectedEmployee,
          target_role_name: targetRole,
        });
        setResult({ type: 'plan', data: res });
      }
    } catch (e) {
      setError(e.message || 'Generation failed.');
    } finally {
      setLoading(false);
    }
  };

  const phaseColors = ['purple', 'blue', 'teal'];
  const phaseStyles = [
    'border-purple-800/40 bg-purple-950/10',
    'border-blue-800/40 bg-blue-950/10',
    'border-teal-800/40 bg-teal-950/10',
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-3 p-4 bg-orange-950/10 rounded-xl border border-orange-900/30">
        <TrendingUp className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-orange-200">AI Career Development Engine</p>
          <p className="text-slate-400">
            Combines Skill-Sim gap analysis + NBK role matching + AI reasoning to generate
            personalised career recommendations and phased development plans.
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        {[{ id: 'career', label: 'Career Recommendation' }, { id: 'plan', label: 'Development Plan' }].map(m => (
          <button
            key={m.id}
            onClick={() => setMode(m.id)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              mode === m.id
                ? 'bg-orange-700/80 text-white border border-orange-600/50'
                : 'text-slate-400 hover:text-slate-200 bg-[#111827] border border-[#1E293B]'
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Employee</label>
          <select
            value={selectedEmployee}
            onChange={(e) => { setSelectedEmployee(e.target.value); setResult(null); }}
            className="w-full bg-[#111827] border border-[#1E293B] text-white text-sm rounded-xl px-3 py-2.5 focus:outline-none cursor-pointer"
          >
            <option value="">Select employee…</option>
            {employees.map((e) => (
              <option key={e.id} value={e.id}>{e.employee_reference} — {e.role}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Target Role</label>
          <select
            value={selectedRole}
            onChange={(e) => { setSelectedRole(e.target.value); setResult(null); }}
            className="w-full bg-[#111827] border border-[#1E293B] text-white text-sm rounded-xl px-3 py-2.5 focus:outline-none cursor-pointer"
          >
            <option value="">Auto-select best fit</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>{r.role_name}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={handleGenerate}
        disabled={!selectedEmployee || loading}
        className="w-full py-2.5 rounded-xl text-sm font-semibold bg-orange-700 hover:bg-orange-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
      >
        {loading ? <RotateCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
        {loading ? 'Generating…' : mode === 'career' ? 'Generate Career Recommendation' : 'Generate Development Plan'}
      </button>

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner text="AI is building your career plan…" />}

      {result && !loading && (
        <div className="space-y-4 animate-in fade-in duration-500">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-orange-400" />
              {result.type === 'career' ? 'Career Recommendation' : 'Development Plan'}
            </h4>
            <AIBadge available={result.data.ai_available} />
          </div>

          {/* Journey header */}
          <div className="flex items-center gap-2 text-sm">
            <span className="px-3 py-1.5 bg-[#111827] border border-[#1E293B] rounded-xl font-semibold text-white">
              {result.data.current_role}
            </span>
            <ArrowRight className="w-4 h-4 text-orange-400 shrink-0" />
            <span className="px-3 py-1.5 bg-orange-950/20 border border-orange-800/40 rounded-xl font-semibold text-orange-200">
              {result.data.target_role}
            </span>
            {result.data.estimated_weeks && (
              <span className="ml-auto text-xs text-slate-400 font-mono">~{result.data.estimated_weeks}w</span>
            )}
          </div>

          {/* Summary */}
          {result.data.summary && (
            <div className="p-4 bg-[#111827] rounded-xl border border-[#1E293B] text-xs text-slate-300 leading-relaxed">
              {result.data.summary}
            </div>
          )}

          {/* Qwen recommendation text */}
          {result.data.recommendation_text && (
            <div className="p-4 bg-[#111827] rounded-xl border border-purple-900/30 text-xs text-slate-300 leading-relaxed space-y-1">
              <p className="font-semibold text-purple-300 flex items-center gap-1.5">
                <Brain className="w-3.5 h-3.5" /> AI Recommendation
              </p>
              <p className="whitespace-pre-wrap">{result.data.recommendation_text}</p>
            </div>
          )}

          {/* Current strengths */}
          {result.data.current_strengths?.length > 0 && (
            <div className="bg-[#111827] p-4 rounded-xl border border-emerald-900/30 space-y-2">
              <p className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <Star className="w-3.5 h-3.5" /> Current Strengths
              </p>
              <div className="flex flex-wrap gap-1.5">
                {result.data.current_strengths.map((s, i) => <SkillBadge key={i} skill={s} variant="match" />)}
              </div>
            </div>
          )}

          {/* Priority skills */}
          {result.data.priority_skills?.length > 0 && (
            <div className="bg-[#111827] p-4 rounded-xl border border-orange-900/30 space-y-2">
              <p className="text-[11px] font-bold text-orange-400 uppercase tracking-wider flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5" /> Priority Skills to Develop
              </p>
              <div className="space-y-1.5">
                {result.data.priority_skills.map((s, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="w-5 h-5 rounded-full bg-orange-700/50 flex items-center justify-center text-[10px] font-bold text-orange-200 shrink-0">
                      {i + 1}
                    </span>
                    <span className="text-slate-200">{s}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Development phases */}
          {(result.data.development_phases || result.data.phases)?.map((phase, i) => (
            <div key={i} className={`p-4 rounded-xl border ${phaseStyles[i] || phaseStyles[2]} space-y-2`}>
              <div className="flex items-center justify-between text-xs">
                <p className="font-bold text-white flex items-center gap-2">
                  <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white bg-${phaseColors[i] || 'teal'}-700`}>
                    {phase.phase}
                  </span>
                  Phase {phase.phase}: {phase.name}
                </p>
                <span className="text-slate-400 font-mono">{phase.weeks}w</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(phase.skills || []).map((s, si) => <SkillBadge key={si} skill={s} variant="neutral" />)}
              </div>
            </div>
          ))}

          {/* Plan text (Qwen) */}
          {result.data.plan_text && (
            <div className="p-4 bg-[#111827] rounded-xl border border-purple-900/30 text-xs text-slate-300 leading-relaxed space-y-1">
              <p className="font-semibold text-purple-300 flex items-center gap-1.5">
                <Brain className="w-3.5 h-3.5" /> AI Development Plan
              </p>
              <p className="whitespace-pre-wrap">{result.data.plan_text}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// AI Chat Tab
// ─────────────────────────────────────────────────────────────────────────────

const STARTER_QUESTIONS = [
  "What are this employee's strongest skills?",
  "What skills are missing for the target role?",
  "Generate a development plan",
  "Which roles are most aligned?",
  "Summarize this employee's profile",
];

function AIChatTab({ profileId, employees, showToast }) {
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  const scrollToBottom = () => endRef.current?.scrollIntoView({ behavior: 'smooth' });

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (question) => {
    const q = question || input.trim();
    if (!q || !profileId) return;
    setInput('');

    const userMsg = { role: 'user', text: q, ts: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await apiClient.workforceAIChat(profileId, {
        question: q,
        employee_id: selectedEmployee || undefined,
      });
      const aiMsg = {
        role: 'ai',
        text: res.answer,
        source: res.source,
        ai_available: res.ai_available,
        suggested_actions: res.suggested_actions || [],
        ts: Date.now(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'ai',
        text: 'I encountered an error processing your request. Please try again.',
        source: 'error',
        ai_available: false,
        suggested_actions: [],
        ts: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 p-4 bg-[#111827] rounded-xl border border-[#1E293B]">
        <MessageSquare className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0 space-y-1.5">
          <p className="text-xs font-semibold text-purple-200">Workforce AI Assistant</p>
          <select
            value={selectedEmployee}
            onChange={(e) => { setSelectedEmployee(e.target.value); setMessages([]); }}
            className="w-full bg-[#0D1117] border border-[#1E293B] text-white text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-purple-700/60 cursor-pointer"
          >
            <option value="">General Workforce Query (no employee context)</option>
            {employees.map((e) => (
              <option key={e.id} value={e.id}>{e.employee_reference} — {e.role}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Messages */}
      <div className="min-h-[280px] max-h-96 overflow-y-auto space-y-3 pr-1">
        {messages.length === 0 && (
          <div className="space-y-3">
            <p className="text-xs text-slate-500 text-center pt-4">
              Ask anything about employees, skills, roles, or career development.
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {STARTER_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="text-[11px] px-3 py-1.5 rounded-xl bg-[#111827] border border-[#1E293B] text-slate-300 hover:text-white hover:border-purple-700/60 transition-colors cursor-pointer"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 rounded-xl shrink-0 flex items-center justify-center ${
              msg.role === 'user' ? 'bg-purple-700/60' : 'bg-[#1E293B]'
            }`}>
              {msg.role === 'user' ? <User className="w-3.5 h-3.5 text-white" /> : <Brain className="w-3.5 h-3.5 text-purple-400" />}
            </div>
            <div className={`max-w-[85%] space-y-1 ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
              <div className={`text-xs leading-relaxed p-3 rounded-xl ${
                msg.role === 'user'
                  ? 'bg-purple-700/40 text-white rounded-tr-sm'
                  : 'bg-[#111827] border border-[#1E293B] text-slate-200 rounded-tl-sm'
              }`}>
                {msg.text}
              </div>
              {msg.role === 'ai' && (
                <div className="flex items-center gap-2">
                  <AIBadge available={msg.ai_available} />
                </div>
              )}
              {msg.suggested_actions?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {msg.suggested_actions.map((action, ai) => (
                    <button
                      key={ai}
                      onClick={() => sendMessage(action)}
                      className="text-[10px] px-2 py-1 rounded-lg bg-[#1E293B] text-purple-300 hover:text-white border border-slate-700/40 hover:border-purple-700/60 transition-colors cursor-pointer flex items-center gap-1"
                    >
                      <ChevronRight className="w-2.5 h-2.5" />
                      {action}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5">
            <div className="w-7 h-7 rounded-xl shrink-0 flex items-center justify-center bg-[#1E293B]">
              <Brain className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
            </div>
            <div className="p-3 rounded-xl bg-[#111827] border border-[#1E293B]">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <div key={i} className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about skills, career paths, role matches…"
          rows={2}
          className="flex-1 bg-[#111827] border border-[#1E293B] text-white text-xs rounded-xl px-3 py-2.5 resize-none focus:outline-none focus:border-purple-700/60 placeholder:text-slate-600"
        />
        <button
          onClick={() => sendMessage()}
          disabled={!input.trim() || loading}
          className="px-4 rounded-xl bg-purple-700 hover:bg-purple-600 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer flex items-center justify-center"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main WorkforceAIPanel component
// ─────────────────────────────────────────────────────────────────────────────

export default function WorkforceAIPanel({ profileId, employees, roles, showToast }) {
  const [activeTab, setActiveTab] = useState('resume');
  const [aiStatus, setAiStatus] = useState(null);

  useEffect(() => {
    if (!profileId) return;
    apiClient.getWorkforceAIStatus().then(setAiStatus).catch(() => setAiStatus(null));
  }, [profileId]);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 bg-gradient-to-r from-purple-950/30 to-[#111827] p-5 rounded-2xl border border-purple-900/30">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-purple-900/40 border border-purple-700/40 flex items-center justify-center">
              <Brain className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Workforce AI Intelligence
                <Sparkles className="w-4 h-4 text-purple-400" />
              </h2>
              <p className="text-[11px] text-slate-400">
                NuExtract · Skill-Sim · NBK ATS Semantic · AI Reasoning Engine
              </p>
            </div>
          </div>
        </div>
        {aiStatus && (
          <div className="shrink-0 space-y-1 text-right">
            {Object.entries(aiStatus.models || {}).map(([key, m]) => (
              <div key={key} className="flex items-center gap-1.5 text-[10px]">
                <div className={`w-1.5 h-1.5 rounded-full ${m.loaded ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                <span className="text-slate-400">{m.name?.split('-').slice(0, 2).join('-')}</span>
                <span className={m.loaded ? 'text-emerald-400' : 'text-slate-500'}>
                  {m.loaded ? 'Active' : 'Ready'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tab navigation */}
      <div className="flex gap-1 bg-[#0D1117] p-1 rounded-xl border border-[#1E293B]">
        {AI_TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === tab.id
                  ? 'bg-purple-700/70 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#1E293B]'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      <div className="bg-[#0D1117] p-5 rounded-2xl border border-[#1E293B]">
        {activeTab === 'resume' && (
          <ResumeAITab profileId={profileId} showToast={showToast} />
        )}
        {activeTab === 'skills' && (
          <SkillAnalysisTab profileId={profileId} employees={employees} roles={roles} showToast={showToast} />
        )}
        {activeTab === 'match' && (
          <RoleMatchTab profileId={profileId} employees={employees} roles={roles} showToast={showToast} />
        )}
        {activeTab === 'career' && (
          <CareerPlanTab profileId={profileId} employees={employees} roles={roles} showToast={showToast} />
        )}
        {activeTab === 'chat' && (
          <AIChatTab profileId={profileId} employees={employees} showToast={showToast} />
        )}
      </div>
    </div>
  );
}
