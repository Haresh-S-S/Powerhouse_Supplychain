export const schemesHighlight = {
  title: 'AI-Powered Recommendations',
  description: 'Based on your business profile, we found 8 schemes relevant to Powerhouse Industries.',
  totalSchemes: 8,
  highMatch: 3,
  additionalOpportunities: 5,
};

export const schemesList = [
  {
    id: 'scheme-1',
    name: 'PMEGP Scheme (Prime Minister Employment Generation Programme)',
    shortName: 'PMEGP Scheme',
    description: 'Credit-linked subsidy programme for establishing and modernizing micro & medium manufacturing units.',
    benefit: 'Up to 35% Subsidy',
    matchPercentage: 92,
    category: 'Central Government Subsidy',
    tags: ['MSME', 'Capital Subsidy', 'Manufacturing'],
    eligibility: [
      'Manufacturing units with project cost up to 50 Lakhs',
      'No income ceiling for setting up projects',
      'Existing units upgrading to green machinery'
    ],
    requiredDocuments: ['Project Report', 'Udyam Registration', 'Pollution NOC', 'Bank Sanction Letter'],
    applicationProcess: 'Online application via KVIC Portal with bank branch linkage.',
    deadline: 'Open all year round (Quarterly tranches)',
    officialSource: 'Ministry of MSME, Govt of India (kviconline.gov.in)'
  },
  {
    id: 'scheme-2',
    name: 'Industrial Development Incentive (State Capital Subsidy)',
    shortName: 'Industrial Development Incentive',
    description: 'Direct state capital investment support and stamp duty exemption for eligible industrial units.',
    benefit: 'Up to 20% Incentive',
    matchPercentage: 88,
    category: 'State Industry Policy',
    tags: ['State Scheme', 'Plant & Machinery', 'Stamp Duty'],
    eligibility: [
      'MSME registered manufacturing facilities in designated industrial zones (MIDC)',
      'Minimum continuous operation of 3 years',
      'At least 70% local workforce employment'
    ],
    requiredDocuments: ['Audited Financials', 'Factory License', 'Electricity Bills', 'Workforce Roster'],
    applicationProcess: 'State Single Window Investor Portal submission with District Industry Center audit.',
    deadline: '31 October 2026',
    officialSource: 'Directorate of Industries, Maharashtra'
  },
  {
    id: 'scheme-3',
    name: 'MSME Technology Upgradation Scheme (CLCSS & ZED)',
    shortName: 'MSME Technology Upgradation',
    description: 'Financial assistance and upfront capital subsidy for inducting well-established clean technologies.',
    benefit: 'Technology Support (15% Upfront)',
    matchPercentage: 82,
    category: 'Technology & Modernization',
    tags: ['Automation', 'ZED Gold/Silver', 'Green Tech'],
    eligibility: [
      'Units upgrading CNC, automation, or zero-defect zero-effect manufacturing lines',
      'Registered under Udyam MSME portal'
    ],
    requiredDocuments: ['Machinery Quotations', 'Chartered Engineer Certificate', 'ZED Assessment ID'],
    applicationProcess: 'Commercial Bank nodal agency upload with Small Industries Development Bank of India (SIDBI).',
    deadline: 'Rolling applications',
    officialSource: 'Development Commissioner, MSME'
  },
  {
    id: 'scheme-4',
    name: 'Export Promotion Capital Goods (EPCG) Scheme',
    shortName: 'Export Promotion Scheme',
    description: 'Customs duty exemption on import of capital goods for producing quality goods and export capability.',
    benefit: 'Zero Duty on Machinery Import',
    matchPercentage: 76,
    category: 'Foreign Trade Policy',
    tags: ['Import/Export', 'Customs Exemption', 'DGFT'],
    eligibility: [
      'Industrial manufacturers with IEC code seeking high-precision overseas tooling',
      'Export obligation equivalent to 6x duty saved in 6 years'
    ],
    requiredDocuments: ['IEC Code', 'Installation Certificate', 'Bank Guarantee'],
    applicationProcess: 'Directorate General of Foreign Trade (DGFT) online portal.',
    deadline: 'Perpetual under FTP 2023-28',
    officialSource: 'DGFT (dgft.gov.in)'
  },
];