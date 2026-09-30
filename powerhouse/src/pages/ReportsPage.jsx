import React from 'react';
import {
  FileSpreadsheet,
  Award,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  CheckSquare,
  FolderKanban,
  Printer
} from 'lucide-react';
import Button from '../components/ui/Button';
import { useBusinessAnalysis } from '../context/BusinessAnalysisContext';

export default function ReportsPage({ showToast, setModalState }) {
  const { analysisResult, businessTemplateBundle } = useBusinessAnalysis();
  const businessName = analysisResult?.businessSummary?.businessName || 'Tiruppur Textile Works';
  const complianceScore = analysisResult?.summary?.complianceScore ?? 92;

  const approvalsStats = businessTemplateBundle?.approvalsStats || { total: 8, completed: 6, inProgress: 1, pending: 1 };
  const documentsStats = businessTemplateBundle?.documentsStats || { total: 24, verified: 18, pending: 6, rejected: 0 };
  const tasksList = businessTemplateBundle?.tasksList || [];
  const completedTasksCount = tasksList.filter((t) => t.completed || t.status === 'Completed').length || 12;
  const inProgressTasksCount = tasksList.filter((t) => t.status === 'In Progress' && !t.completed).length || 5;
  const upcomingTasksCount = tasksList.filter((t) => (t.status === 'Upcoming' || t.status === 'Overdue' || !t.status) && !t.completed).length || 3;
  const totalTasks = tasksList.length || 20;

  const reportsSummary = {
    complianceScore,
    completedApprovals: { done: approvalsStats.completed || 6, total: approvalsStats.total || 8 },
    completedTasks: { done: completedTasksCount, total: totalTasks },
    documentsVerified: { done: documentsStats.verified || 18, total: documentsStats.total || 24 },
  };

  const pct = (count, total) => (total > 0 ? Math.round((count / total) * 100) : 0);

  const approvalDistribution = [
    { label: 'Completed', count: approvalsStats.completed || 6, color: '#10b981', percentage: pct(approvalsStats.completed || 6, approvalsStats.total || 8) },
    { label: 'In Progress', count: approvalsStats.inProgress || 1, color: '#3b82f6', percentage: pct(approvalsStats.inProgress || 1, approvalsStats.total || 8) },
    { label: 'Pending', count: approvalsStats.pending || 1, color: '#f59e0b', percentage: pct(approvalsStats.pending || 1, approvalsStats.total || 8) },
  ];

  const taskDistribution = [
    { label: 'Completed', count: completedTasksCount, color: 'bg-emerald-500', barHeight: `${pct(completedTasksCount, totalTasks)}%` },
    { label: 'In Progress', count: inProgressTasksCount, color: 'bg-amber-500', barHeight: `${pct(inProgressTasksCount, totalTasks)}%` },
    { label: 'Upcoming / Overdue', count: upcomingTasksCount, color: 'bg-rose-500', barHeight: `${pct(upcomingTasksCount, totalTasks)}%` },
  ];

  const scoreTrend = [
    { month: 'Jan', score: 72 },
    { month: 'Feb', score: 78 },
    { month: 'Mar', score: 81 },
    { month: 'Apr', score: 86 },
    { month: 'May', score: 92 },
    { month: 'Jun', score: 92 },
  ];
  const trendGrowth = 20;

  const insights = analysisResult?.insights || [];
  const strongAreas = insights.filter((i) => i.severity === 'success' || i.severity === 'info').slice(0, 2)
    .map((i) => ({ title: i.title, detail: i.message }));
  const needsAttention = insights.filter((i) => i.severity === 'warning').slice(0, 2)
    .map((i) => ({ title: i.title, detail: i.message }));

  const performanceSummary = {
    strongAreas: strongAreas.length ? strongAreas : [
      { title: 'Statutory Mappings Validated', detail: `Statutory roadmap certified for ${businessName}.` },
    ],
    needsAttention: needsAttention.length ? needsAttention : [
      { title: 'Fire Safety Renewal Due', detail: 'Schedule TN Fire & Rescue inspection audit.' },
    ],
  };

  const donutOffsets = {
    completed: 0,
    inProgress: -approvalDistribution[0].percentage,
    pending: -(approvalDistribution[0].percentage + approvalDistribution[1].percentage),
  };

  const handleGenerateReport = () => {
    showToast('Generating official compliance dossier report...');
    setTimeout(() => {
      setModalState({
        isOpen: true,
        title: 'Compliance Executive Dossier (H1 2026)',
        type: 'report-generate',
        data: {
          company: businessName,
          score: complianceScore ? `${complianceScore}%` : '92%',
          generatedOn: new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
        },
      });
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Reports &amp; Analytics
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            View compliance health analytics, statutory audit reports, and risk summaries.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => showToast('Printing summary report...')}
            className="text-xs font-semibold"
          >
            <Printer className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Print View</span>
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleGenerateReport}
            className="text-xs font-semibold"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Generate Full Dossier</span>
          </Button>
        </div>
      </div>

      {/* Top 4 Summary Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-5">
        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Overall Health Score</div>
            <div className="text-xl sm:text-2xl font-black text-emerald-400 mt-1">{reportsSummary.complianceScore}%</div>
            <div className="text-[11px] text-emerald-400 font-semibold mt-0.5">↑ +{trendGrowth}% this quarter</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-950/80 text-emerald-400 flex items-center justify-center border border-emerald-800/80 shrink-0">
            <Award className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Approvals Acquired</div>
            <div className="text-xl sm:text-2xl font-black text-white mt-1">{reportsSummary.completedApprovals.done}/{reportsSummary.completedApprovals.total}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{approvalsStats.inProgress || 1} in progress</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-800/80 shrink-0">
            <FileCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Tasks Completed</div>
            <div className="text-xl sm:text-2xl font-black text-white mt-1">{reportsSummary.completedTasks.done}/{reportsSummary.completedTasks.total}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{pct(completedTasksCount, totalTasks)}% workflow complete</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-950/80 text-indigo-400 flex items-center justify-center border border-indigo-800/80 shrink-0">
            <CheckSquare className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-400">Verified Documents</div>
            <div className="text-xl sm:text-2xl font-black text-white mt-1">{reportsSummary.documentsVerified.done}/{reportsSummary.documentsVerified.total}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{pct(documentsStats.verified, documentsStats.total)}% digital vault secure</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-purple-950/80 text-purple-400 flex items-center justify-center border border-purple-800/80 shrink-0">
            <FolderKanban className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Row 1 Charts: Health Trend (Line) + Approval Distribution (Donut) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Compliance Score Trend Chart (7 cols) */}
        <div className="lg:col-span-7 bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white leading-none">Compliance Score Trend</h2>
              <p className="text-xs text-slate-400 mt-1">Monthly statutory index progression (Jan - Jun 2026)</p>
            </div>
            <span className="px-2.5 py-1 rounded-lg bg-emerald-950 text-emerald-400 text-xs font-bold border border-emerald-800">
              +{trendGrowth} pts Growth
            </span>
          </div>

          {/* SVG Line Chart */}
          <div className="pt-4">
            <div className="relative h-44 w-full">
              <svg viewBox="0 0 500 150" className="w-full h-full overflow-visible">
                <defs>
                  <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2563eb" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#2563eb" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Grid Lines */}
                <line x1="0" y1="20" x2="500" y2="20" stroke="#1E293B" strokeWidth="1" strokeDasharray="4 4" />
                <line x1="0" y1="65" x2="500" y2="65" stroke="#1E293B" strokeWidth="1" strokeDasharray="4 4" />
                <line x1="0" y1="110" x2="500" y2="110" stroke="#1E293B" strokeWidth="1" strokeDasharray="4 4" />
                <line x1="0" y1="140" x2="500" y2="140" stroke="#1E293B" strokeWidth="1" />

                {/* Filled Area */}
                <path
                  d="M 20 120 L 110 105 L 200 85 L 290 70 L 380 45 L 470 20 L 470 140 L 20 140 Z"
                  fill="url(#lineGrad)"
                />

                {/* Smooth Polyline */}
                <path
                  d="M 20 120 L 110 105 L 200 85 L 290 70 L 380 45 L 470 20"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                {/* Data Points */}
                {[
                  { x: 20, y: 120, label: '72%' },
                  { x: 110, y: 105, label: '78%' },
                  { x: 200, y: 85, label: '81%' },
                  { x: 290, y: 70, label: '86%' },
                  { x: 380, y: 45, label: '92%' },
                  { x: 470, y: 20, label: '92%' },
                ].map((pt, idx) => (
                  <g key={idx}>
                    <circle cx={pt.x} cy={pt.y} r="5" fill="#111827" stroke="#3b82f6" strokeWidth="2.5" />
                    <text x={pt.x} y={pt.y - 10} textAnchor="middle" fontSize="10" fontWeight="bold" fill="#f8fafc">
                      {pt.label}
                    </text>
                  </g>
                ))}
              </svg>
            </div>

            {/* X-axis labels */}
            <div className="flex items-center justify-between text-xs text-slate-400 font-medium px-2 mt-2">
              {scoreTrend.map((item) => (
                <span key={item.month}>{item.month}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Approvals Status Donut (5 cols) */}
        <div className="lg:col-span-5 bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6 space-y-4">
          <div>
            <h2 className="text-base font-bold text-white leading-none">Licences Breakdown</h2>
            <p className="text-xs text-slate-400 mt-1">{approvalsStats.total || 8} total statutory approvals status</p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 py-2">
            {/* SVG Donut Chart */}
            <div className="relative w-32 h-32 shrink-0">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-800"
                  strokeWidth="3.8"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                {/* Completed */}
                <path
                  className="text-emerald-500"
                  strokeDasharray={`${approvalDistribution[0].percentage}, 100`}
                  strokeDashoffset={donutOffsets.completed}
                  strokeWidth="3.8"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                {/* In Progress */}
                <path
                  className="text-blue-500"
                  strokeDasharray={`${approvalDistribution[1].percentage}, 100`}
                  strokeDashoffset={donutOffsets.inProgress}
                  strokeWidth="3.8"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                {/* Pending */}
                <path
                  className="text-amber-500"
                  strokeDasharray={`${approvalDistribution[2].percentage}, 100`}
                  strokeDashoffset={donutOffsets.pending}
                  strokeWidth="3.8"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>

              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-xl font-black text-white leading-none">{approvalsStats.total || 8}</span>
                <span className="text-[10px] text-slate-400 font-semibold mt-0.5">Total</span>
              </div>
            </div>

            {/* Donut Legend */}
            <div className="space-y-2 text-xs w-full sm:w-auto">
              {approvalDistribution.map((item) => (
                <div key={item.label} className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-300 font-medium">{item.label}</span>
                  </div>
                  <span className="font-bold text-white">{item.count} ({item.percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Task Distribution Bars + Key Strengths */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Tasks Breakdown Bar Metrics (6 cols) */}
        <div className="lg:col-span-6 bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6 space-y-4">
          <div>
            <h2 className="text-base font-bold text-white leading-none">Compliance Tasks Overview</h2>
            <p className="text-xs text-slate-400 mt-1">{totalTasks} total statutory tasks distribution</p>
          </div>

          <div className="space-y-4 pt-2">
            {taskDistribution.map((item) => (
              <div key={item.label} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300">{item.label}</span>
                  <span className="font-bold text-white">{item.count} Tasks</span>
                </div>
                <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${item.color}`}
                    style={{
                      width: item.barHeight,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Compliance Strengths & Highlights (6 cols) */}
        <div className="lg:col-span-6 bg-[#111827] rounded-2xl border border-[#1E293B] shadow-2xs p-5 sm:p-6 space-y-4">
          <div>
            <h2 className="text-base font-bold text-white leading-none">Statutory Highlights</h2>
            <p className="text-xs text-slate-400 mt-1">Key operational audit standing points</p>
          </div>

          <div className="space-y-3 pt-1">
            {performanceSummary.strongAreas.map((item, idx) => (
              <div key={`strong-${idx}`} className="p-3 bg-[#141C2B] rounded-xl border border-slate-800 flex items-start gap-3">
                <div className="p-1 rounded-md bg-emerald-950 text-emerald-400 border border-emerald-800 shrink-0 mt-0.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-white">{item.title}</h3>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">{item.detail}</p>
                </div>
              </div>
            ))}
            {performanceSummary.needsAttention.map((item, idx) => (
              <div key={`attn-${idx}`} className="p-3 bg-[#141C2B] rounded-xl border border-slate-800 flex items-start gap-3">
                <div className="p-1 rounded-md bg-amber-950 text-amber-400 border border-amber-800 shrink-0 mt-0.5">
                  <AlertTriangle className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-white">{item.title}</h3>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">{item.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}