/**
 * POWER HOUSE Business Analysis Engine - Approval Rules Engine
 */

import { AUTHORITIES, CATEGORIES } from '../data/businessRules';
import { isTrue } from '../utils/analysisHelpers';

export const approvalRules = [
  // Rule 1: Factory License
  {
    id: 'rule-factory-license',
    name: 'Factory License Evaluation',
    evaluate: (profile) => {
      const isManufacturing =
        profile.industry === 'Manufacturing' ||
        isTrue(profile.manufacturingActivity) ||
        (profile.sector && profile.sector.toLowerCase().includes('equipment'));

      if (isManufacturing) {
        return {
          id: 'appr-factory-license',
          name: 'Factory License',
          authority: AUTHORITIES.DIRECTORATE_OF_INDUSTRIES,
          category: CATEGORIES.BUSINESS_REGISTRATION,
          priority: 'High',
          status: 'Completed',
          progress: 100,
          description: 'Mandatory license under Factories Act 1948 for industrial production premises and worker safety compliance.',
          triggerReason: 'Triggered because primary business operation involves Manufacturing activity.',
          dueDate: 'Active • Annual Renewal 31 Dec',
          documentsCount: 5,
          steps: [
            { name: 'Site Blueprint Approval', status: 'Completed' },
            { name: 'Safety Equipment Audit', status: 'Completed' },
            { name: 'License Grant & Endorsement', status: 'Completed' }
          ],
          requiredDocuments: ['Site Layout Blueprint', 'Machinery Schedule', 'Building Stability Certificate', 'PAN & GST Proof']
        };
      }
      return null;
    }
  },

  // Rule 2: Pollution Control NOC (CTO)
  {
    id: 'rule-pollution-noc',
    name: 'Pollution Control NOC Evaluation',
    evaluate: (profile) => {
      const isMfg = profile.industry === 'Manufacturing' || isTrue(profile.manufacturingActivity);
      const isModerateOrHighEnv =
        profile.environmentalImpact === 'Moderate' ||
        profile.environmentalImpact === 'High' ||
        profile.environmentalImpact === 'Critical (Red Category)';

      if (isMfg && isModerateOrHighEnv) {
        return {
          id: 'appr-pollution-noc',
          name: 'Pollution Control NOC (CTO)',
          authority: AUTHORITIES.POLLUTION_CONTROL_BOARD,
          category: CATEGORIES.ENVIRONMENTAL,
          priority: 'High',
          status: 'In Progress',
          progress: 65,
          description: 'Consent to Operate (CTO) under Air & Water (Prevention & Control of Pollution) Acts for industrial emissions.',
          triggerReason: `Triggered due to ${profile.environmentalImpact} environmental impact classification in Manufacturing sector.`,
          dueDate: 'Action Required (Renewal in 5 days)',
          documentsCount: 6,
          steps: [
            { name: 'Effluent Treatment Design Submission', status: 'Completed' },
            { name: 'Stack Emission Sampling', status: 'In Progress' },
            { name: 'Pollution Board Committee Review', status: 'Pending' }
          ],
          requiredDocuments: ['ETP Analysis Report', 'Ambient Air Quality Log', 'Hazardous Waste Management Plan', 'Manufacturing Process Flowchart']
        };
      }
      return null;
    }
  },

  // Rule 3: Fire Safety Certificate
  {
    id: 'rule-fire-safety',
    name: 'Fire Safety Certificate Evaluation',
    evaluate: (profile) => {
      if (isTrue(profile.manufacturingActivity) || profile.companySize !== 'Micro Enterprise (< ₹1 Cr)') {
        return {
          id: 'appr-fire-safety',
          name: 'Fire Safety Certificate',
          authority: AUTHORITIES.FIRE_DEPARTMENT,
          category: CATEGORIES.SAFETY,
          priority: 'High',
          status: 'In Progress',
          progress: 50,
          description: 'Fire hazard prevention inspection and hydrant readiness clearance for factory & industrial warehouses.',
          triggerReason: 'Triggered for active industrial manufacturing premises with heavy machinery.',
          dueDate: 'Audit Scheduled in 4 days',
          documentsCount: 4,
          steps: [
            { name: 'Sprinkler & Extinguisher Testing', status: 'Completed' },
            { name: 'Emergency Evacuation Route Audit', status: 'In Progress' },
            { name: 'Final Fire NOC Issue', status: 'Pending' }
          ],
          requiredDocuments: ['Fire Hydrant Layout Plan', 'Pressure Test Certificate', 'Emergency Evacuation Map']
        };
      }
      return null;
    }
  },

  // Rule 4: Electricity Connection Approval (HT/LT)
  {
    id: 'rule-electricity-approval',
    name: 'Electricity Sanction Evaluation',
    evaluate: (profile) => {
      if (isTrue(profile.manufacturingActivity)) {
        return {
          id: 'appr-electricity',
          name: 'Electricity Connection Approval (HT)',
          authority: AUTHORITIES.ELECTRICITY_BOARD,
          category: CATEGORIES.UTILITIES,
          priority: 'Medium',
          status: 'Pending',
          progress: 20,
          description: 'High-tension industrial power feeder sanction (500 kVA load) with dedicated transformer verification.',
          triggerReason: 'Triggered by industrial power sanction requirement for manufacturing machinery.',
          dueDate: 'Target: 15 Jun 2026',
          documentsCount: 4,
          steps: [
            { name: 'Load Feasibility Survey', status: 'Completed' },
            { name: 'Substation Transformer Approval', status: 'Pending' },
            { name: 'Meter Commissioning', status: 'Pending' }
          ],
          requiredDocuments: ['Premises Ownership Proof', 'Load Test Report', 'Licensed Electrical Contractor Certificate']
        };
      }
      return null;
    }
  },

  // Rule 5: Labour Establishment Registration
  {
    id: 'rule-labour-registration',
    name: 'Labour Establishment Registration',
    evaluate: (profile) => {
      const empCount = parseInt(profile.employees, 10) || 0;
      if (empCount >= 10) {
        return {
          id: 'appr-labour-reg',
          name: 'Labour Establishment Registration',
          authority: AUTHORITIES.LABOUR_DEPARTMENT,
          category: CATEGORIES.LABOUR,
          priority: 'High',
          status: 'Pending',
          progress: 15,
          description: 'Statutory registration under State Shops & Commercial Establishments / Contract Labour Acts.',
          triggerReason: `Triggered because employee headcount (${empCount} staff) meets statutory labour threshold (>= 10).`,
          dueDate: 'Due in 20 days',
          documentsCount: 4,
          steps: [
            { name: 'Muster Roll & Wage Register Submission', status: 'In Progress' },
            { name: 'Labour Inspector Verification', status: 'Pending' },
            { name: 'Registration Certificate Grant', status: 'Pending' }
          ],
          requiredDocuments: ['Employee Roster & Contracts', 'Form 1 Register', 'ESIC & EPFO Sub-Code Allotments']
        };
      }
      return null;
    }
  },

  // Rule 6: Employees ESI Registration
  {
    id: 'rule-esi-registration',
    name: 'Employees State Insurance Registration',
    evaluate: (profile) => {
      const empCount = parseInt(profile.employees, 10) || 0;
      if (empCount >= 10) {
        return {
          id: 'appr-esi',
          name: 'Employees ESI Registration',
          authority: AUTHORITIES.ESIC,
          category: CATEGORIES.LABOUR_COMPLIANCE,
          priority: 'High',
          status: 'Completed',
          progress: 100,
          description: 'Social security and medical benefit coverage under Employee State Insurance Act 1948.',
          triggerReason: `Triggered by statutory threshold for workforce of ${empCount} employees (>= 10).`,
          dueDate: 'Active / Compliant',
          documentsCount: 3,
          steps: [
            { name: 'Employer Registration', status: 'Completed' },
            { name: 'Employee Pehchan Cards Issue', status: 'Completed' }
          ],
          requiredDocuments: ['Employee Master Roster', 'Bank Mandate', 'Incorporation Certificate']
        };
      }
      return null;
    }
  },

  // Rule 7: PF (Provident Fund) Registration
  {
    id: 'rule-pf-registration',
    name: 'Employees Provident Fund Registration',
    evaluate: (profile) => {
      const empCount = parseInt(profile.employees, 10) || 0;
      if (empCount >= 20) {
        return {
          id: 'appr-pf',
          name: 'Employees PF Registration',
          authority: AUTHORITIES.EPFO,
          category: CATEGORIES.LABOUR_COMPLIANCE,
          priority: 'High',
          status: 'Completed',
          progress: 100,
          description: 'Retirement benefit and pension statutory fund management under EPF & MP Act 1952.',
          triggerReason: `Triggered because workforce count of ${empCount} exceeds the mandatory EPF threshold (>= 20).`,
          dueDate: 'Active / Monthly ECR Filing',
          documentsCount: 3,
          steps: [
            { name: 'EPFO Portal LIN Allotment', status: 'Completed' },
            { name: 'Monthly DSC Setup', status: 'Completed' }
          ],
          requiredDocuments: ['PAN Card', 'Cancelled Cheque', 'Form 5A Ownership Return']
        };
      }
      return null;
    }
  },

  // Rule 8: GST Compliance
  {
    id: 'rule-gst-compliance',
    name: 'GST Registration & Compliance',
    evaluate: (profile) => {
      if (profile.gstin || isTrue(profile.hasGST) || profile.annualTurnover) {
        return {
          id: 'appr-gst',
          name: 'GST Registration & Compliance',
          authority: AUTHORITIES.TAX_DEPARTMENT,
          category: CATEGORIES.TAXATION,
          priority: 'High',
          status: 'Completed',
          progress: 100,
          description: 'Goods and Services Tax interstate and domestic business tax registration & return gateway.',
          triggerReason: `Triggered by active GSTIN (${profile.gstin || 'Registered'}) and annual turnover.`,
          dueDate: 'Active / Monthly GSTR-3B Compliant',
          documentsCount: 3,
          steps: [
            { name: 'PAN & Jurisdiction Validation', status: 'Completed' },
            { name: 'Premises Verification', status: 'Completed' },
            { name: 'REG-06 Certificate Issue', status: 'Completed' }
          ],
          requiredDocuments: ['PAN Card', 'Bank Certificate', 'Electricity Bill / Lease Agreement']
        };
      }
      return null;
    }
  },

  // Rule 9: MSME / Udyam Compliance Review
  {
    id: 'rule-msme-compliance',
    name: 'MSME Udyam Registration & Compliance',
    evaluate: (profile) => {
      const isMSME =
        isTrue(profile.msmeRegistration) ||
        isTrue(profile.hasMSMERegistration) ||
        isTrue(profile.hasUdyamRegistration) ||
        Boolean(profile.udyamNumber);

      if (isMSME) {
        return {
          id: 'appr-msme',
          name: 'MSME Udyam Registration',
          authority: AUTHORITIES.MSME_MINISTRY,
          category: CATEGORIES.BUSINESS_COMPLIANCE,
          priority: 'Medium',
          status: 'Completed',
          progress: 100,
          description: 'Official Ministry of MSME registration certificate enabling priority sector lending and subsidies.',
          triggerReason: `Triggered by active Udyam registration (${profile.udyamNumber || 'Active'}).`,
          dueDate: 'Active / Perpetual',
          documentsCount: 2,
          steps: [
            { name: 'Aadhaar & PAN Verification', status: 'Completed' },
            { name: 'Udyam Certificate Grant', status: 'Completed' }
          ],
          requiredDocuments: ['Udyam Registration Certificate', 'Audited Balance Sheet']
        };
      }
      return null;
    }
  },

  // Rule 10: Import Export Code (IEC) Review
  {
    id: 'rule-iec-review',
    name: 'Import Export Code (IEC) Review',
    evaluate: (profile) => {
      if (isTrue(profile.importActivities) || isTrue(profile.exportActivities)) {
        return {
          id: 'appr-iec',
          name: 'Import Export Code (IEC)',
          authority: AUTHORITIES.DGFT,
          category: CATEGORIES.TRADE,
          priority: 'Medium',
          status: 'Completed',
          progress: 100,
          description: 'Directorate General of Foreign Trade authorization for international cross-border cargo clearance.',
          triggerReason: 'Triggered by active import/export industrial machinery procurement operations.',
          dueDate: 'Active / Perpetual',
          documentsCount: 2,
          steps: [
            { name: 'DGFT Portal Electronic Submission', status: 'Completed' },
            { name: 'IEC Allotment Letter Grant', status: 'Completed' }
          ],
          requiredDocuments: ['IEC Certificate', 'Bank Certificate (AD Code Letter)']
        };
      }
      return null;
    }
  }
];

export function runApprovalRules(profile) {
  const matchedApprovals = [];
  for (const rule of approvalRules) {
    const result = rule.evaluate(profile);
    if (result) {
      matchedApprovals.push(result);
    }
  }
  return matchedApprovals;
}
