/**
 * POWER HOUSE Business Analysis Engine - Analysis Helpers
 */

/**
 * Normalizes boolean or string representations ('Yes', 'No', true, false)
 */
export function isTrue(val) {
  if (typeof val === 'boolean') return val;
  if (typeof val === 'string') {
    const s = val.trim().toLowerCase();
    return s === 'yes' || s === 'true' || s === 'registered' || s === '1';
  }
  return false;
}

/**
 * Returns formatted relative due date string given days in the future
 */
export function getRelativeDueDate(daysFromNow) {
  if (daysFromNow <= 0) return 'Immediate Action';
  if (daysFromNow === 1) return 'Due tomorrow';
  if (daysFromNow < 7) return `Due in ${daysFromNow} days`;
  if (daysFromNow === 7) return 'Due in 7 days';
  if (daysFromNow < 30) return `Due in ${daysFromNow} days`;
  const months = Math.round(daysFromNow / 30);
  return `Due in ~${months} month${months > 1 ? 's' : ''}`;
}

/**
 * Calculates a composite statutory risk level for the enterprise
 */
export function calculateRiskLevel(profile) {
  let riskPoints = 0;

  // Environmental impact
  if (profile.environmentalImpact === 'Critical (Red Category)') riskPoints += 4;
  else if (profile.environmentalImpact === 'High') riskPoints += 3;
  else if (profile.environmentalImpact === 'Moderate') riskPoints += 2;
  else riskPoints += 1;

  // Employee scale
  const employees = parseInt(profile.employees, 10) || 0;
  if (employees >= 100) riskPoints += 3;
  else if (employees >= 20) riskPoints += 2;
  else if (employees >= 10) riskPoints += 1;

  // Manufacturing & Trade
  if (isTrue(profile.manufacturingActivity)) riskPoints += 2;
  if (isTrue(profile.importActivities) || isTrue(profile.exportActivities)) riskPoints += 1;

  if (riskPoints >= 8) return 'High';
  if (riskPoints >= 5) return 'Medium';
  return 'Low';
}

/**
 * Validates whether essential business profile parameters are present
 */
export function validateProfile(profile) {
  const missingFields = [];

  if (!profile.businessName || !profile.businessName.trim()) missingFields.push('Business Name');
  if (!profile.industry || !profile.industry.trim()) missingFields.push('Industry');
  if (!profile.state || !profile.state.trim()) missingFields.push('State');
  if (profile.employees === undefined || profile.employees === null || profile.employees === '') {
    missingFields.push('Employee Count');
  }

  return {
    isValid: missingFields.length === 0,
    missingFields,
  };
}
