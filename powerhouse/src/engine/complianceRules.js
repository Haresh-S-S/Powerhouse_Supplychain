/**
 * POWER HOUSE Business Analysis Engine - Compliance Task Generation Rules
 */

import { getRelativeDueDate } from '../utils/analysisHelpers';

export function runComplianceTaskRules(profile, matchedApprovals) {
  const approvalNames = new Set(matchedApprovals.map((a) => a.name));
  const tasks = [];

  // Factory License Tasks
  if (approvalNames.has('Factory License')) {
    tasks.push({
      id: 'gen-task-annual-compliance',
      title: 'Annual Factory Compliance Report',
      description: 'Consolidated submission of annual production hours, worker safety logs, and machine maintenance records.',
      relatedApproval: 'Factory License',
      priority: 'High',
      status: 'Upcoming',
      dueDate: getRelativeDueDate(7),
      estimatedDays: 7,
      assignee: 'Arjun Mehta (Compliance Officer)',
      category: 'Statutory Filing',
      completed: false,
    });
    tasks.push({
      id: 'gen-task-machinery-safety',
      title: 'Machinery Guarding & Safety Audit',
      description: 'Onsite inspection of mechanical interlocks, emergency stop switches, and worker PPE compliance.',
      relatedApproval: 'Factory License',
      priority: 'Medium',
      status: 'Upcoming',
      dueDate: getRelativeDueDate(18),
      estimatedDays: 18,
      assignee: 'Capt. R. Sharma (Safety Officer)',
      category: 'Safety',
      completed: false,
    });
  }

  // Pollution NOC Tasks
  if (approvalNames.has('Pollution Control NOC (CTO)')) {
    tasks.push({
      id: 'gen-task-waste-manifest',
      title: 'Hazardous Waste Management Compliance',
      description: 'Hazardous solid waste manifest verification and electronic transfer log to authorized recycler.',
      relatedApproval: 'Pollution Control NOC (CTO)',
      priority: 'High',
      status: 'Upcoming',
      dueDate: getRelativeDueDate(12),
      estimatedDays: 12,
      assignee: 'Dr. Sunita Rao (EHS Manager)',
      category: 'Environmental',
      completed: false,
    });
    tasks.push({
      id: 'gen-task-stack-emission',
      title: 'Quarterly Stack Emission & Flue Gas Analysis',
      description: 'Ambient air quality index sampling and chimney emissions laboratory testing report.',
      relatedApproval: 'Pollution Control NOC (CTO)',
      priority: 'High',
      status: 'Upcoming',
      dueDate: getRelativeDueDate(30),
      estimatedDays: 30,
      assignee: 'Dr. Sunita Rao (EHS Manager)',
      category: 'Environmental',
      completed: false,
    });
  }

  // Fire Safety Tasks
  if (approvalNames.has('Fire Safety Certificate')) {
    tasks.push({
      id: 'gen-task-fire-drill',
      title: 'Fire Safety Inspection & Hydrant Pressure Test',
      description: 'Pressure testing of automatic water sprinklers in Shop Floor 2 and extinguisher replenishment.',
      relatedApproval: 'Fire Safety Certificate',
      priority: 'High',
      status: 'In Progress',
      dueDate: getRelativeDueDate(4),
      estimatedDays: 4,
      assignee: 'Capt. R. Sharma (Safety Officer)',
      category: 'Safety',
      completed: false,
    });
  }

  // Electricity / Utilities
  if (approvalNames.has('Electricity Connection Approval (HT)')) {
    tasks.push({
      id: 'gen-task-transformer',
      title: 'Transformer Inspection Checklist',
      description: 'Earthing resistance measurement and dielectric oil strength testing for 500 kVA substation transformer.',
      relatedApproval: 'Electricity Connection Approval (HT)',
      priority: 'Medium',
      status: 'Upcoming',
      dueDate: getRelativeDueDate(22),
      estimatedDays: 22,
      assignee: 'K. S. Verma (Chief Engineer)',
      category: 'Utilities',
      completed: false,
    });
  }

  // Labour & Social Security Tasks
  if (approvalNames.has('Employees ESI Registration')) {
    tasks.push({
      id: 'gen-task-esi-cards',
      title: 'Employees ESI Pehchan Card Distribution',
      description: 'Generation and biometric distribution of insurance smart cards for newly onboarded staff.',
      relatedApproval: 'Employees ESI Registration',
      priority: 'Medium',
      status: 'Completed',
      dueDate: 'Completed on schedule',
      estimatedDays: 0,
      assignee: 'Rahul Varma (HR Lead)',
      category: 'HR & Benefits',
      completed: true,
    });
  }

  if (approvalNames.has('Employees PF Registration')) {
    tasks.push({
      id: 'gen-task-pf-ecr',
      title: 'Monthly PF Electronic Challan Return (ECR)',
      description: 'Monthly electronic challan upload and payment for employee provident fund contribution.',
      relatedApproval: 'Employees PF Registration',
      priority: 'Medium',
      status: 'Upcoming',
      dueDate: getRelativeDueDate(25),
      estimatedDays: 25,
      assignee: 'Kavita Nair (Finance Officer)',
      category: 'Statutory Filing',
      completed: false,
    });
  }

  // GST Tasks
  if (approvalNames.has('GST Registration & Compliance')) {
    tasks.push({
      id: 'gen-task-gstr-filing',
      title: 'Monthly GSTR-3B Return Filing',
      description: 'Summary return of outward supplies, input tax credit claimed, and tax liability settlement.',
      relatedApproval: 'GST Registration & Compliance',
      priority: 'High',
      status: 'Upcoming',
      dueDate: getRelativeDueDate(15),
      estimatedDays: 15,
      assignee: 'Kavita Nair (Finance Officer)',
      category: 'Taxation',
      completed: false,
    });
  }

  return tasks;
}
