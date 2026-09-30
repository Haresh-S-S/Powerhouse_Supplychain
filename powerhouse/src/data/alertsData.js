export const alertsStats = {
  critical: 2,
  upcoming: 5,
  information: 8,
};

export const initialAlertsList = [
  {
    id: 'alert-1',
    title: 'Pollution Control NOC expires in 5 days',
    description: 'Consent to Operate validity ends on 02 Jun 2026. Submit ambient air sampling test report immediately to avoid fine.',
    date: '2 hours ago',
    severity: 'critical',
    category: 'Environmental',
    read: false,
    actionRoute: 'approvals'
  },
  {
    id: 'alert-2',
    title: 'Fire Safety Certificate requires renewal',
    description: 'Annual hydrant pressure and evacuation certification audit is scheduled with local fire department.',
    date: '5 hours ago',
    severity: 'critical',
    category: 'Safety',
    read: false,
    actionRoute: 'approvals'
  },
  {
    id: 'alert-3',
    title: 'Annual Compliance Report due in 7 days',
    description: 'Statutory factory health and employee work-hour log filing due for current financial quarter.',
    date: '1 day ago',
    severity: 'upcoming',
    category: 'Statutory',
    read: false,
    actionRoute: 'compliance-tasks'
  },
  {
    id: 'alert-4',
    title: 'Waste Management Compliance due in 12 days',
    description: 'Hazardous waste manifest transfer report due to State Pollution Control Board portal.',
    date: '2 days ago',
    severity: 'upcoming',
    category: 'Environmental',
    read: true,
    actionRoute: 'compliance-tasks'
  },
  {
    id: 'alert-5',
    title: 'PF Return Filing due in 25 days',
    description: 'Monthly ECR upload and challan payment window opens next week.',
    date: '3 days ago',
    severity: 'upcoming',
    category: 'Finance',
    read: true,
    actionRoute: 'compliance-tasks'
  },
  {
    id: 'alert-6',
    title: 'New government scheme available (PMEGP)',
    description: 'Your manufacturing business profile matches 92% of criteria for up to 35% capital subsidy.',
    date: '4 days ago',
    severity: 'information',
    category: 'Government Scheme',
    read: false,
    actionRoute: 'government-schemes'
  },
  {
    id: 'alert-7',
    title: 'Business profile updated successfully',
    description: 'Changes to Company Size (Medium Enterprise) and Employee Count (85) were saved and verified.',
    date: '5 days ago',
    severity: 'information',
    category: 'Profile',
    read: true,
    actionRoute: 'business-profile'
  },
  {
    id: 'alert-8',
    title: 'Document verification completed for Factory License',
    description: 'State Directorate of Industries verified your factory site blueprint and building stability cert.',
    date: '6 days ago',
    severity: 'information',
    category: 'Documents',
    read: true,
    actionRoute: 'documents'
  },
];