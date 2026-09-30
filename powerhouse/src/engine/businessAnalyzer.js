/**
 * POWER HOUSE Business Analysis Engine - Core Analyzer Orchestrator
 */

import { runApprovalRules } from './approvalRules';
import { runComplianceTaskRules } from './complianceRules';
import { runDocumentRequirementRules } from './documentRules';
import { runSchemeMatchingRules } from './schemeRules';
import { calculateRiskLevel, validateProfile } from '../utils/analysisHelpers';

export function analyzeBusiness(profile) {
  // 1. Validate Profile
  const validation = validateProfile(profile);
  if (!validation.isValid) {
    return {
      isValid: false,
      missingFields: validation.missingFields,
      message: `Complete the following fields in your business profile to generate an accurate analysis: ${validation.missingFields.join(', ')}`,
    };
  }

  // 2. Execute Approval Rules
  const approvals = runApprovalRules(profile);

  // 3. Generate Compliance Tasks
  const complianceTasks = runComplianceTaskRules(profile, approvals);

  // 4. Generate Document Requirements
  const requiredDocuments = runDocumentRequirementRules(profile, approvals);

  // 5. Match Government Schemes
  const recommendedSchemes = runSchemeMatchingRules(profile);

  // 6. Calculate Risk Level
  const riskLevel = calculateRiskLevel(profile);

  // 7. Compile Summary Counts
  const highPriorityApprovals = approvals.filter((a) => a.priority === 'High').length;
  const completedApprovals = approvals.filter((a) => a.status === 'Completed').length;
  const inProgressApprovals = approvals.filter((a) => a.status === 'In Progress').length;
  const pendingApprovals = approvals.filter((a) => a.status === 'Pending').length;

  const totalTasks = complianceTasks.length;
  const upcomingTasks = complianceTasks.filter((t) => t.status === 'Upcoming' && !t.completed).length;

  // 8. Generate Dynamic Rule-Based Insights
  const insights = [];

  insights.push({
    id: 'insight-approvals',
    type: 'approvals',
    title: 'Statutory Approval Requirements',
    message: `Identified ${approvals.length} applicable regulatory approvals, with ${highPriorityApprovals} classified as High Priority for factory operations.`,
    severity: 'info',
  });

  if (profile.environmentalImpact === 'Moderate' || profile.environmentalImpact === 'High') {
    insights.push({
      id: 'insight-env',
      type: 'environmental',
      title: 'Environmental & Pollution Standing',
      message: `Your enterprise is subject to ${profile.environmentalImpact} environmental oversight. Maintain stack emission logs and ETP renewal filings on schedule.`,
      severity: 'warning',
    });
  }

  const empCount = parseInt(profile.employees, 10) || 0;
  if (empCount >= 10) {
    insights.push({
      id: 'insight-labour',
      type: 'labour',
      title: 'Workforce & Labour Compliance',
      message: `With ${empCount} employees, statutory ESI medical coverage and mandatory monthly EPFO electronic returns are actively enforced.`,
      severity: 'info',
    });
  }

  if (recommendedSchemes.length > 0) {
    const topScheme = recommendedSchemes[0];
    insights.push({
      id: 'insight-schemes',
      type: 'scheme',
      title: 'Government Scheme Opportunity',
      message: `${recommendedSchemes.length} schemes match your business profile. Top recommendation: "${topScheme.shortName}" (${topScheme.matchPercentage}% match) offering ${topScheme.benefit}.`,
      severity: 'success',
    });
  }

  insights.push({
    id: 'insight-action',
    type: 'action',
    title: 'Upcoming Critical Deadlines',
    message: `You have ${upcomingTasks} compliance tasks due in the upcoming cycle. Review environmental documentation to avoid statutory penalties.`,
    severity: 'warning',
  });

  // 9. Assembled Final Analysis Result
  return {
    isValid: true,
    analysisDate: new Date().toISOString().split('T')[0],
    businessSummary: {
      businessName: profile.businessName,
      legalName: profile.legalName || profile.businessName,
      businessType: profile.businessType,
      industry: profile.industry,
      sector: profile.sector,
      city: profile.city,
      state: profile.state,
      companySize: profile.companySize,
      employees: empCount,
      annualTurnover: profile.annualTurnover,
      gstin: profile.gstin,
      udyamNumber: profile.udyamNumber,
      operatingStatus: profile.operatingStatus,
    },
    riskLevel,
    approvals,
    complianceTasks,
    requiredDocuments,
    recommendedSchemes,
    summary: {
      totalApprovals: approvals.length,
      completedApprovals,
      inProgressApprovals,
      pendingApprovals,
      highPriorityApprovals,
      complianceTasks: totalTasks,
      upcomingTasks,
      requiredDocuments: requiredDocuments.length,
      recommendedSchemes: recommendedSchemes.length,
      complianceScore: 78,
    },
    insights,
  };
}
