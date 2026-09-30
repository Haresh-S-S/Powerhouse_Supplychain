export const documentsStats = {
  total: 34,
  verified: 24,
  pending: 8,
  rejected: 2,
};

export const initialDocumentsList = [
  {
    id: 'doc-1',
    name: 'Factory Licence Certificate',
    category: 'Statutory License',
    relatedApproval: 'Factory License',
    uploadDate: '14 Apr 2024',
    expiryDate: '31 Dec 2026',
    status: 'Verified',
    fileType: 'PDF',
    fileSize: '2.4 MB',
    uploadedBy: 'Compliance Dept',
    verifiedBy: 'State Directorate Portal'
  },
  {
    id: 'doc-2',
    name: 'GST Registration Certificate (REG-06)',
    category: 'Taxation',
    relatedApproval: 'GST Registration',
    uploadDate: '10 Jan 2024',
    expiryDate: 'Perpetual',
    status: 'Verified',
    fileType: 'PDF',
    fileSize: '1.1 MB',
    uploadedBy: 'Accounts Team',
    verifiedBy: 'GSTN Gateway'
  },
  {
    id: 'doc-3',
    name: 'Pollution Control Application Form',
    category: 'Environmental',
    relatedApproval: 'Pollution Control NOC (CTO)',
    uploadDate: '02 May 2024',
    expiryDate: 'Under Review',
    status: 'Pending',
    fileType: 'PDF',
    fileSize: '4.8 MB',
    uploadedBy: 'EHS Lead',
    verifiedBy: 'Pending Officer Review'
  },
  {
    id: 'doc-4',
    name: 'Fire Safety Hydrant Audit Report',
    category: 'Safety',
    relatedApproval: 'Fire Safety Certificate',
    uploadDate: '15 May 2024',
    expiryDate: '15 May 2025',
    status: 'Pending',
    fileType: 'PDF',
    fileSize: '3.2 MB',
    uploadedBy: 'Safety Officer',
    verifiedBy: 'Pending Field Audit'
  },
  {
    id: 'doc-5',
    name: 'Employee ESI Master Roster',
    category: 'Labor & HR',
    relatedApproval: 'Labour Establishment Registration',
    uploadDate: '12 May 2024',
    expiryDate: '31 Mar 2025',
    status: 'Verified',
    fileType: 'XLSX',
    fileSize: '850 KB',
    uploadedBy: 'HR Lead',
    verifiedBy: 'ESIC Portal Sync'
  },
  {
    id: 'doc-6',
    name: 'Environmental Impact Assessment 2023',
    category: 'Environmental',
    relatedApproval: 'Pollution Control NOC (CTO)',
    uploadDate: '20 Mar 2024',
    expiryDate: 'Expired / Superseded',
    status: 'Rejected',
    fileType: 'PDF',
    fileSize: '6.7 MB',
    uploadedBy: 'Third Party Agency',
    verifiedBy: 'Pollution Board (Old Schema)'
  },
];