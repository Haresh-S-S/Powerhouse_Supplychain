/**
 * POWER HOUSE Business Analysis Engine - Document Requirement Rules
 */

export function runDocumentRequirementRules(profile, matchedApprovals) {
  const approvalNames = new Set(matchedApprovals.map((a) => a.name));
  const docs = [];

  // 1. Factory License Documents
  if (approvalNames.has('Factory License')) {
    docs.push({
      id: 'gen-doc-factory-cert',
      name: 'Factory Licence Certificate',
      category: 'Statutory License',
      relatedApproval: 'Factory License',
      required: true,
      status: 'Verified',
      fileType: 'PDF',
      fileSize: '2.4 MB',
      uploadDate: '14 Apr 2024',
      expiryDate: '31 Dec 2026',
      description: 'Endorsed Factory License issued by Directorate of Industrial Safety.',
    });
    docs.push({
      id: 'gen-doc-factory-layout',
      name: 'Approved Factory Machinery Layout Plan',
      category: 'Statutory License',
      relatedApproval: 'Factory License',
      required: true,
      status: 'Verified',
      fileType: 'PDF',
      fileSize: '5.1 MB',
      uploadDate: '10 Feb 2024',
      expiryDate: 'Perpetual',
      description: 'Architectural blueprint with machine foundations and clearance corridors.',
    });
  }

  // 2. GST Documents
  if (approvalNames.has('GST Registration & Compliance')) {
    docs.push({
      id: 'gen-doc-gst-cert',
      name: 'GST Registration Certificate (REG-06)',
      category: 'Taxation',
      relatedApproval: 'GST Registration & Compliance',
      required: true,
      status: 'Verified',
      fileType: 'PDF',
      fileSize: '1.1 MB',
      uploadDate: '10 Jan 2024',
      expiryDate: 'Perpetual',
      description: 'Principal place of business registration issued by Central Board of Indirect Taxes.',
    });
  }

  // 3. Pollution Documents
  if (approvalNames.has('Pollution Control NOC (CTO)')) {
    docs.push({
      id: 'gen-doc-pollution-app',
      name: 'Consent to Operate (CTO) Renewal Application',
      category: 'Environmental',
      relatedApproval: 'Pollution Control NOC (CTO)',
      required: true,
      status: 'Pending',
      fileType: 'PDF',
      fileSize: '4.8 MB',
      uploadDate: '02 May 2024',
      expiryDate: 'Under Review',
      description: 'Comprehensive effluent treatment plant (ETP) capacity and air emissions log.',
    });
    docs.push({
      id: 'gen-doc-eia',
      name: 'Environmental Impact Assessment & Hazard Plan',
      category: 'Environmental',
      relatedApproval: 'Pollution Control NOC (CTO)',
      required: true,
      status: 'Required',
      fileType: 'PDF',
      fileSize: '—',
      uploadDate: 'Not Uploaded',
      expiryDate: 'Required for Audit',
      description: 'Detailed analysis of solid and liquid waste generation protocols.',
    });
  }

  // 4. Fire Safety Documents
  if (approvalNames.has('Fire Safety Certificate')) {
    docs.push({
      id: 'gen-doc-fire-report',
      name: 'Fire Safety Hydrant & Sprinkler Audit Report',
      category: 'Safety',
      relatedApproval: 'Fire Safety Certificate',
      required: true,
      status: 'Pending',
      fileType: 'PDF',
      fileSize: '3.2 MB',
      uploadDate: '15 May 2024',
      expiryDate: '15 May 2025',
      description: 'Inspection log of hydraulic water pressure, fire hoses, and alarm sounders.',
    });
  }

  // 5. Labour Documents
  if (approvalNames.has('Employees ESI Registration') || approvalNames.has('Labour Establishment Registration')) {
    docs.push({
      id: 'gen-doc-esi-roster',
      name: 'Employee Master Roster & Form 1 Register',
      category: 'Labor & HR',
      relatedApproval: 'Labour Establishment Registration',
      required: true,
      status: 'Verified',
      fileType: 'XLSX',
      fileSize: '850 KB',
      uploadDate: '12 May 2024',
      expiryDate: '31 Mar 2025',
      description: 'Complete employee wage register, attendance muster, and insurance sub-codes.',
    });
  }

  // 6. MSME Documents
  if (approvalNames.has('MSME Udyam Registration')) {
    docs.push({
      id: 'gen-doc-udyam-cert',
      name: 'Udyam MSME Registration Certificate',
      category: 'Business Registration',
      relatedApproval: 'MSME Udyam Registration',
      required: true,
      status: 'Verified',
      fileType: 'PDF',
      fileSize: '720 KB',
      uploadDate: '15 Mar 2024',
      expiryDate: 'Perpetual',
      description: 'Official Udyam classification as Medium Manufacturing Enterprise.',
    });
  }

  return docs;
}
