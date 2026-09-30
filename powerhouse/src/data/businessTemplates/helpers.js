/**
 * POWER HOUSE Business Analysis Engine - Business Template Helpers
 *
 * Small utilities shared by every non-factory business template so that
 * stats (counts, percentages) are always derived from the actual list
 * data instead of being hand-maintained and risking drift.
 */

export function computeApprovalsStats(approvals) {
  return {
    total: approvals.length,
    completed: approvals.filter((a) => a.status === 'Completed').length,
    inProgress: approvals.filter((a) => a.status === 'In Progress').length,
    pending: approvals.filter((a) => a.status === 'Pending').length,
  };
}

export function computeDocumentsStats(documents) {
  return {
    total: documents.length,
    verified: documents.filter((d) => d.status === 'Verified').length,
    pending: documents.filter((d) => d.status === 'Pending').length,
    rejected: documents.filter((d) => d.status === 'Rejected').length,
  };
}

export function computeAlertsStats(alerts) {
  return {
    critical: alerts.filter((a) => a.severity === 'critical').length,
    upcoming: alerts.filter((a) => a.severity === 'upcoming').length,
    information: alerts.filter((a) => a.severity === 'information').length,
  };
}

export function computeApplicationsStats(applications) {
  return {
    total: applications.length,
    submitted: applications.filter((a) => a.status === 'Submitted').length,
    underReview: applications.filter((a) => a.status === 'Under Review').length,
    approved: applications.filter((a) => a.status === 'Approved').length,
    pending: applications.filter((a) => a.status === 'Pending' || a.status === 'In Progress').length,
  };
}

// Short, template-specific descriptions of what the business actually
// does day-to-day. Used to populate the Business Profile page's
// "Operations" section instead of leaking the factory's activity text.
const PRIMARY_ACTIVITY_BY_KEY = {
  retail: 'Retail Sale of General Merchandise',
  restaurant: 'Preparation & Sale of Food and Beverages',
  clothing_textile: 'Retail Sale of Clothing & Textile Products',
  jewellery: 'Retail Sale of Gold, Silver & Jewellery Products',
};

const SECONDARY_ACTIVITY_BY_KEY = {
  retail: 'Customer Service, Inventory Management',
  restaurant: 'Dine-in Service, Takeaway & Order Packaging',
  clothing_textile: 'Alterations & Customer Styling Assistance',
  jewellery: 'Custom Ornament Orders, Repair Services',
};

/**
 * Builds a Business-Profile-page-shaped record for a non-factory
 * template, so pages like BusinessProfile.jsx never fall back to
 * showing the PowerHouse Industries factory profile for a business
 * that was classified as retail/restaurant/clothing/jewellery.
 *
 * Field names intentionally mirror `initialBusinessProfile` in
 * `businessProfileData.js` so every existing profile component keeps
 * working unmodified.
 */
import { getCategoryDefaultName } from '../../utils/businessVisualResolver';

export function buildTemplateBusinessProfile(template, location) {
  const { meta } = template;
  const businessName = getCategoryDefaultName(meta.key, location) || meta.defaultBusinessName;

  return {
    businessName,
    businessType: meta.businessType,
    industry: meta.industry,
    sector: meta.sector,
    establishedDate: 'Not specified',
    companySize: meta.companySize,
    employees: meta.employees,
    annualTurnover: meta.annualTurnover,
    registeredAddress: 'Not yet added',
    city: location?.city || 'Not specified',
    state: location?.state || 'Not specified',
    country: 'India',
    pinCode: 'Not specified',
    operatingLocation: location ? `${location.city}, ${location.state}` : 'Not specified',
    primaryActivity: PRIMARY_ACTIVITY_BY_KEY[meta.key] || 'Not specified',
    secondaryActivities: SECONDARY_ACTIVITY_BY_KEY[meta.key] || 'Not specified',
    manufacturingActivity: 'No',
    importActivities: 'No',
    exportActivities: 'No',
    environmentalImpact: 'Low',
    operatingStatus: 'Active',
    cin: 'Not Applicable (Sole Proprietorship)',
    pan: 'Not Configured',
    gstin: 'Pending Registration',
    msmeRegistration: 'Recommended - not yet registered',
    udyamNumber: 'Pending Registration',
  };
}

/**
 * Builds the full data bundle consumed across the app (Dashboard,
 * Business Analysis page, Approvals/Documents/Compliance/Schemes/Alerts/
 * Applications hubs) for a single non-factory business template.
 *
 * `location` is the { city, state } detected from the user's free-text
 * description (or null if none was found).
 */
export function buildTemplateBundle(template, location) {
  const {
    meta,
    approvals,
    complianceTasks,
    requiredDocuments,
    recommendedSchemes,
    alerts,
    applications,
    insights,
    riskLevel,
  } = template;

  const businessName = getCategoryDefaultName(meta.key, location) || meta.defaultBusinessName;

  const businessSummary = {
    businessName,
    businessType: meta.businessType,
    industry: meta.industry,
    sector: meta.sector,
    city: location?.city || 'Not specified',
    state: location?.state || '',
    companySize: meta.companySize,
    employees: meta.employees,
    annualTurnover: meta.annualTurnover,
    gstin: 'Pending Registration',
    udyamNumber: 'Pending Registration',
    operatingStatus: 'Active',
  };

  const highPriorityApprovals = approvals.filter((a) => a.priority === 'High').length;
  const completedApprovals = approvals.filter((a) => a.status === 'Completed').length;
  const inProgressApprovals = approvals.filter((a) => a.status === 'In Progress').length;
  const pendingApprovals = approvals.filter((a) => a.status === 'Pending').length;
  const upcomingTasks = complianceTasks.filter((t) => t.status === 'Upcoming' && !t.completed).length;

  const summary = {
    totalApprovals: approvals.length,
    completedApprovals,
    inProgressApprovals,
    pendingApprovals,
    highPriorityApprovals,
    complianceTasks: complianceTasks.length,
    upcomingTasks,
    requiredDocuments: requiredDocuments.length,
    recommendedSchemes: recommendedSchemes.length,
    complianceScore: meta.complianceScore,
  };

  const analysis = {
    isValid: true,
    analysisDate: new Date().toISOString().split('T')[0],
    businessSummary,
    riskLevel,
    approvals,
    complianceTasks,
    requiredDocuments,
    recommendedSchemes,
    summary,
    insights,
  };

  const highMatch = recommendedSchemes.filter((s) => s.matchPercentage >= 85).length;

  const schemesHighlight = {
    title: 'Rule-Based Recommendations',
    description: `Based on your business description, we found ${recommendedSchemes.length} schemes relevant to your ${meta.categoryLabel.toLowerCase()}.`,
    totalSchemes: recommendedSchemes.length,
    highMatch,
    additionalOpportunities: Math.max(recommendedSchemes.length - highMatch, 0),
  };

  return {
    key: meta.key,
    meta,
    businessSummary,
    analysis,
    approvalsList: approvals,
    approvalsStats: computeApprovalsStats(approvals),
    tasksList: complianceTasks,
    documentsList: requiredDocuments,
    documentsStats: computeDocumentsStats(requiredDocuments),
    schemesList: recommendedSchemes,
    schemesHighlight,
    alertsList: alerts,
    alertsStats: computeAlertsStats(alerts),
    applicationsList: applications,
    applicationsStats: computeApplicationsStats(applications),
    complianceRoadmap: template.complianceRoadmap || [],
    upcomingDeadlines: template.upcomingDeadlines || [],
    analyticsData: template.analyticsData || null,
  };
}

