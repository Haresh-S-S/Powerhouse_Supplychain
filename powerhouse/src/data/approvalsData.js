export const approvalsStats = {
  total: 12,
  completed: 4,
  inProgress: 3,
  pending: 5,
};

export const approvalsList = [
  {
    id: 'appr-1',
    name: 'Factory License',
    authority: 'Directorate of Industries',
    category: 'Business Registration',
    status: 'Completed',
    priority: 'High',
    description: 'Mandatory license under Factories Act 1948 for industrial production operations and worker safety clearance.',
    documentsCount: 6,
    progress: 100,
    dueDate: 'Renew by 31 Dec 2026',
    applicationId: 'APP-2024-001',
    steps: [
      { name: 'Site Plan Approval', status: 'Completed' },
      { name: 'Safety Equipment Audit', status: 'Completed' },
      { name: 'Final Inspection & License Issue', status: 'Completed' }
    ],
    requiredDocuments: ['Site Blueprint', 'Machinery Layout', 'Pollution NOC', 'Building Stability Cert'],
    relatedTasks: ['Annual Compliance Report', 'Safety Mock Drill Filing']
  },
  {
    id: 'appr-2',
    name: 'Pollution Control NOC (CTO)',
    authority: 'Pollution Control Board',
    category: 'Environmental',
    status: 'In Progress',
    priority: 'High',
    description: 'Consent to Operate under Water & Air (Prevention & Control of Pollution) Acts for medium emission units.',
    documentsCount: 8,
    progress: 65,
    dueDate: 'Expires in 5 days',
    applicationId: 'APP-2024-002',
    steps: [
      { name: 'Effluent Treatment Design Submission', status: 'Completed' },
      { name: 'Stack Emission Sampling', status: 'In Progress' },
      { name: 'Board Review Committee', status: 'Pending' }
    ],
    requiredDocuments: ['ETP Analysis Report', 'Ambient Air Quality Log', 'Hazardous Waste Authorization'],
    relatedTasks: ['Pollution Monitoring Report', 'Waste Management Compliance']
  },
  {
    id: 'appr-3',
    name: 'Fire Safety Certificate',
    authority: 'State Fire Department',
    category: 'Safety',
    status: 'In Progress',
    priority: 'High',
    description: 'Periodic fire hazard inspection and hydrant readiness certification for industrial factory premises.',
    documentsCount: 4,
    progress: 50,
    dueDate: 'Audit in 4 days',
    applicationId: 'APP-2024-003',
    steps: [
      { name: 'Sprinkler & Extinguisher Testing', status: 'Completed' },
      { name: 'Emergency Exit Route Clearance', status: 'In Progress' },
      { name: 'Final NOC Grant', status: 'Pending' }
    ],
    requiredDocuments: ['Fire Layout Plan', 'Hydrant Pressure Cert', 'Emergency Evacuation Map'],
    relatedTasks: ['Fire Safety Inspection']
  },
  {
    id: 'appr-4',
    name: 'Electricity Connection Approval (HT)',
    authority: 'State Electricity Board',
    category: 'Utilities',
    status: 'Pending',
    priority: 'Medium',
    description: 'High-tension industrial power feeder sanction (500 kVA load) with dedicated transformer verification.',
    documentsCount: 5,
    progress: 20,
    dueDate: 'Target: 15 Jun 2026',
    applicationId: 'APP-2024-005',
    steps: [
      { name: 'Load Feasibility Survey', status: 'Completed' },
      { name: 'Substation Transformer Approval', status: 'Pending' },
      { name: 'Meter Commissioning', status: 'Pending' }
    ],
    requiredDocuments: ['Ownership Proof', 'Load Test Report', 'Electrical Contractor Cert'],
    relatedTasks: ['Transformer Inspection Checklist']
  },
  {
    id: 'appr-5',
    name: 'Labour Establishment Registration',
    authority: 'Labour Department',
    category: 'Labour',
    status: 'Pending',
    priority: 'High',
    description: 'Statutory registration for operating with over 50 contract and permanent industrial employees.',
    documentsCount: 4,
    progress: 15,
    dueDate: 'Due in 20 days',
    applicationId: 'APP-2024-004',
    steps: [
      { name: 'Wage Register & Muster Roll Submission', status: 'In Progress' },
      { name: 'Labour Officer Verification', status: 'Pending' },
      { name: 'License Issuance', status: 'Pending' }
    ],
    requiredDocuments: ['Contractor Agreements', 'Form 1 Register', 'ESI/PF Sub-Codes'],
    relatedTasks: ['Employees ESI Registration', 'PF Return Filing']
  },
  {
    id: 'appr-6',
    name: 'GST Registration',
    authority: 'Tax Department',
    category: 'Taxation',
    status: 'Completed',
    priority: 'High',
    description: 'Goods and Services Tax state and interstate supplier identification and electronic return gateway.',
    documentsCount: 3,
    progress: 100,
    dueDate: 'Active / Compliant',
    applicationId: 'GST-MH-2018',
    steps: [
      { name: 'PAN Validation', status: 'Completed' },
      { name: 'Premises Geotagging', status: 'Completed' },
      { name: 'GSTIN Generation', status: 'Completed' }
    ],
    requiredDocuments: ['PAN Card', 'Bank Certificate', 'Electricity Bill'],
    relatedTasks: ['GSTR-3B Monthly Filing']
  },
];