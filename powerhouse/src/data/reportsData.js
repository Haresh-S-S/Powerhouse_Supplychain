export const reportsSummary = {
  complianceScore: 78,
  completedApprovals: { done: 4, total: 12 },
  completedTasks: { done: 6, total: 18 },
  documentsVerified: { done: 24, total: 34 },
};

export const scoreTrend = [
  { month: 'Jan', score: 62 },
  { month: 'Feb', score: 65 },
  { month: 'Mar', score: 68 },
  { month: 'Apr', score: 70 },
  { month: 'May', score: 74 },
  { month: 'Jun', score: 78 },
];

export const approvalDistribution = [
  { label: 'Completed', count: 4, color: '#10b981', percentage: 33 },
  { label: 'In Progress', count: 3, color: '#3b82f6', percentage: 25 },
  { label: 'Pending', count: 5, color: '#f59e0b', percentage: 42 },
];

export const taskDistribution = [
  { label: 'Completed', count: 6, color: 'bg-emerald-500', barHeight: '60%' },
  { label: 'In Progress', count: 4, color: 'bg-blue-500', barHeight: '40%' },
  { label: 'Upcoming', count: 8, color: 'bg-amber-500', barHeight: '80%' },
];

export const performanceSummary = {
  strongAreas: [
    { title: 'Document Management', detail: '24 of 34 verified with zero compliance audit defaults' },
    { title: 'Tax & GST Compliance', detail: 'Consistent on-time GSTR-3B filings and valid GSTIN status' },
  ],
  needsAttention: [
    { title: 'Environmental Compliance', detail: 'Pollution Control CTO audit renewal due in 5 days' },
    { title: 'Safety Certification', detail: 'Annual Fire Safety onsite inspection scheduled in 4 days' },
  ],
};