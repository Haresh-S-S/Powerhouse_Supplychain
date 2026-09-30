export const summaryStats = [
  {
    id: 'approvals',
    title: 'Approvals Required',
    value: '12',
    subtitle: 'View Details',
    icon: 'ClipboardCheck',
    accent: 'blue',
    trend: '+2 from last month',
  },
  {
    id: 'tasks',
    title: 'Pending Tasks',
    value: '18',
    subtitle: 'View Details',
    icon: 'ListTodo',
    accent: 'orange',
    trend: '4 due this week',
  },
  {
    id: 'deadlines',
    title: 'Upcoming Deadlines',
    value: '5',
    subtitle: 'View Details',
    icon: 'CalendarDays',
    accent: 'red',
    trend: 'Next: in 3 days',
  },
  {
    id: 'score',
    title: 'Compliance Score',
    value: '78%',
    subtitle: 'Good',
    icon: 'Gauge',
    accent: 'green',
    trend: '+4.5% improvement',
  },
];

export const roadmapSteps = [
  {
    step: 1,
    title: 'Factory License',
    authority: 'Directorate of Industries',
    status: 'Completed',
    estimatedDays: 'Completed on 14 Apr',
    category: 'Industrial',
  },
  {
    step: 2,
    title: 'Pollution Control NOC',
    authority: 'Pollution Control Board',
    status: 'In Progress',
    estimatedDays: 'Under inspection review',
    category: 'Environmental',
  },
  {
    step: 3,
    title: 'Fire Safety Certificate',
    authority: 'State Fire Department',
    status: 'In Progress',
    estimatedDays: 'Audit scheduled in 4 days',
    category: 'Safety',
  },
  {
    step: 4,
    title: 'Electricity Connection Approval',
    authority: 'State Electricity Board',
    status: 'Pending',
    estimatedDays: 'Awaiting NOC clearance',
    category: 'Infrastructure',
  },
  {
    step: 5,
    title: 'Labour Establishment Registration',
    authority: 'Labour Department',
    status: 'Pending',
    estimatedDays: 'Documentation required',
    category: 'Labor & Staff',
  },
];

export const complianceTasks = [
  {
    id: 'task-1',
    title: 'Annual Compliance Report',
    due: 'Due in 7 days',
    status: 'Upcoming',
    priority: 'High',
  },
  {
    id: 'task-2',
    title: 'Waste Management Compliance',
    due: 'Due in 12 days',
    status: 'Upcoming',
    priority: 'Medium',
  },
  {
    id: 'task-3',
    title: 'Employees ESI Registration',
    due: 'Due in 20 days',
    status: 'Completed',
    priority: 'Low',
  },
  {
    id: 'task-4',
    title: 'PF Return Filing',
    due: 'Due in 25 days',
    status: 'Upcoming',
    priority: 'High',
  },
];

export const documentStatusData = {
  total: 34,
  verified: 24,
  pending: 8,
  rejected: 2,
};

export const recommendedSchemes = [
  {
    id: 'scheme-1',
    title: 'PMEGP Scheme',
    description: 'Credit-linked subsidy for new MSME units',
    benefit: 'Up to 35% Subsidy',
    icon: 'Landmark',
    badge: 'Central Scheme',
  },
  {
    id: 'scheme-2',
    title: 'Industrial Development Incentive',
    description: 'Capital investment support for eligible businesses',
    benefit: 'Up to 20% Incentive',
    icon: 'TrendingUp',
    badge: 'State Subsidy',
  },
];

export const applicationTracking = [
  {
    id: 'APP-2024-001',
    department: 'Factories Department',
    application: 'Factory License',
    status: 'Under Review',
    updatedOn: '20 May 2024',
    referenceNo: 'FAC/IND/2024/9912',
  },
  {
    id: 'APP-2024-002',
    department: 'Pollution Control Board',
    application: 'Pollution NOC',
    status: 'Approved',
    updatedOn: '18 May 2024',
    referenceNo: 'PCB/NOC/CTE-8819',
  },
  {
    id: 'APP-2024-003',
    department: 'Fire Department',
    application: 'Fire Safety Certificate',
    status: 'Pending',
    updatedOn: '15 May 2024',
    referenceNo: 'FIRE/NOC/REV-3104',
  },
  {
    id: 'APP-2024-004',
    department: 'Labour Department',
    application: 'Labour Registration',
    status: 'In Progress',
    updatedOn: '12 May 2024',
    referenceNo: 'LAB/REG/CL-5421',
  },
];

export const notificationsList = [
  {
    id: 1,
    title: 'Pollution NOC status updated',
    time: '15 minutes ago',
    unread: true,
    type: 'success',
  },
  {
    id: 2,
    title: 'Annual Compliance filing due in 7 days',
    time: '2 hours ago',
    unread: true,
    type: 'warning',
  },
  {
    id: 3,
    title: 'New Government Subsidy recommendation available',
    time: '1 day ago',
    unread: true,
    type: 'info',
  },
];

export const navItems = [
  { id: 'overview', label: 'Overview', icon: 'LayoutDashboard' },
  { id: 'approvals', label: 'Licences & Approvals', icon: 'FileText' },
  { id: 'compliance-tasks', label: 'Compliance Tasks', icon: 'CalendarCheck' },
  { id: 'supply-chain', label: 'Supply Chain', icon: 'Truck' },
  { id: 'workforce', label: 'Workforce', icon: 'Users' },
  { id: 'documents', label: 'Documents Vault', icon: 'FolderLock' },
  { id: 'applications', label: 'Applications', icon: 'Send' },
  { id: 'government-schemes', label: 'Government Schemes', icon: 'Landmark' },
  { id: 'alerts', label: 'Alerts & Notifications', icon: 'Bell', badge: '3' },
  { id: 'reports', label: 'Reports & Analytics', icon: 'BarChart3' },
  { id: 'green-flow', label: 'Green Operations', icon: 'Leaf' },
  { id: 'ai', label: 'AI Compliance Advisor', icon: 'Brain' },
  { id: 'settings', label: 'Settings', icon: 'Settings' },
];

