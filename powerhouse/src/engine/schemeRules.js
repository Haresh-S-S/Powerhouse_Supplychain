/**
 * POWER HOUSE Business Analysis Engine - Government Scheme Matching Rules
 */

import { isTrue } from '../utils/analysisHelpers';

export function runSchemeMatchingRules(profile) {
  const isMSME =
    isTrue(profile.msmeRegistration) ||
    isTrue(profile.hasMSMERegistration) ||
    Boolean(profile.udyamNumber);

  const isMfg =
    profile.industry === 'Manufacturing' ||
    isTrue(profile.manufacturingActivity);

  const isMediumOrSmall =
    profile.companySize?.includes('Medium') ||
    profile.companySize?.includes('Small') ||
    profile.companySize?.includes('Micro');

  const isMaharashtra = profile.state === 'Maharashtra' || profile.city === 'Mumbai';
  const hasTrade = isTrue(profile.importActivities) || isTrue(profile.exportActivities);

  const matchedSchemes = [];

  // Scheme 1: PMEGP Scheme
  if (isMSME && isMfg) {
    let score = 0;
    const matchReasons = [];

    if (isMSME) {
      score += 30;
      matchReasons.push('Verified active Udyam MSME Enterprise (+30%)');
    }
    if (isMfg) {
      score += 25;
      matchReasons.push('Industrial Manufacturing operations (+25%)');
    }
    if (isMediumOrSmall) {
      score += 20;
      matchReasons.push('Eligible enterprise scale (+20%)');
    }
    if (profile.operatingStatus === 'Active') {
      score += 17;
      matchReasons.push('Operational commercial standing (+17%)');
    }

    matchedSchemes.push({
      id: 'scheme-pmegp',
      name: 'Prime Minister Employment Generation Programme (PMEGP)',
      shortName: 'PMEGP Scheme',
      description: 'Credit-linked subsidy programme for establishing, expanding, and modernizing industrial manufacturing units.',
      benefit: 'Up to 35% Capital Subsidy',
      matchPercentage: Math.min(score, 98),
      matchReasons,
      category: 'Central Government Subsidy',
      eligibility: [
        'Manufacturing units registered under Udyam portal',
        'Project cost within MSME credit subsidy ceiling',
        'Clean statutory standing with no banking defaults'
      ],
      officialSource: 'Ministry of MSME, Govt of India (kviconline.gov.in)',
      deadline: 'Open year-round (Quarterly tranches)'
    });
  }

  // Scheme 2: Industrial Development Incentive (State Capital Subsidy)
  if (isMaharashtra && isMfg) {
    let score = 0;
    const matchReasons = [];

    if (isMaharashtra) {
      score += 35;
      matchReasons.push('Enterprise operating in Maharashtra Industrial Zone (+35%)');
    }
    if (isMfg) {
      score += 25;
      matchReasons.push('Capital manufacturing asset creation (+25%)');
    }
    if (isMediumOrSmall) {
      score += 20;
      matchReasons.push('Medium Enterprise bracket eligibility (+20%)');
    }
    score += 8;
    matchReasons.push('Clean GST tax filing history (+8%)');

    matchedSchemes.push({
      id: 'scheme-state-incentive',
      name: 'Industrial Development Incentive (Package Scheme of Incentives)',
      shortName: 'Industrial Development Incentive',
      description: 'Direct state capital investment support, electricity duty exemption, and stamp duty refund.',
      benefit: 'Up to 20% Capital Incentive',
      matchPercentage: Math.min(score, 98),
      matchReasons,
      category: 'State Industry Policy',
      eligibility: [
        'MSME manufacturing units in designated industrial estates (MIDC)',
        'Minimum active operation of 3 years',
        'Compliant statutory pollution and safety clearance'
      ],
      officialSource: 'Directorate of Industries, Maharashtra',
      deadline: '31 October 2026'
    });
  }

  // Scheme 3: MSME Technology Upgradation Scheme (CLCSS & ZED)
  if (isMSME) {
    let score = 0;
    const matchReasons = [];

    if (isMfg) {
      score += 30;
      matchReasons.push('Manufacturing precision machinery focus (+30%)');
    }
    if (isMSME) {
      score += 25;
      matchReasons.push('Udyam registration verified (+25%)');
    }
    if (profile.environmentalImpact === 'Moderate' || profile.environmentalImpact === 'High') {
      score += 20;
      matchReasons.push('Green technology & ETP modernization eligible (+20%)');
    }
    score += 7;
    matchReasons.push('Workforce scale (> 50 employees) qualified (+7%)');

    matchedSchemes.push({
      id: 'scheme-tech-upgradation',
      name: 'MSME Technology Upgradation Scheme (CLCSS & ZED Certification)',
      shortName: 'MSME Technology Upgradation',
      description: 'Financial assistance and upfront capital subsidy for inducting well-established clean technologies.',
      benefit: '15% Upfront Capital Subsidy',
      matchPercentage: Math.min(score, 98),
      matchReasons,
      category: 'Technology & Modernization',
      eligibility: [
        'Units upgrading to automated or energy-efficient machinery',
        'Registered under Udyam MSME portal',
        'Valid credit sanction from SIDBI or scheduled commercial banks'
      ],
      officialSource: 'Development Commissioner, MSME',
      deadline: 'Rolling applications'
    });
  }

  // Scheme 4: Export Promotion Capital Goods (EPCG) Scheme
  if (hasTrade || isMfg) {
    let score = 0;
    const matchReasons = [];

    if (hasTrade) {
      score += 40;
      matchReasons.push('Active import/export machinery procurement (+40%)');
    }
    if (isMfg) {
      score += 20;
      matchReasons.push('Capital goods domestic manufacturing (+20%)');
    }
    score += 16;
    matchReasons.push('Customs port clearance eligible (+16%)');

    matchedSchemes.push({
      id: 'scheme-epcg',
      name: 'Export Promotion Capital Goods (EPCG) Scheme',
      shortName: 'Export Promotion Scheme',
      description: 'Customs duty exemption on import of capital goods for producing quality goods and export capability.',
      benefit: 'Zero Duty on Machinery Import',
      matchPercentage: Math.min(score, 98),
      matchReasons,
      category: 'Foreign Trade Policy',
      eligibility: [
        'Industrial manufacturers with IEC code seeking high-precision overseas tooling',
        'Export obligation equivalent to 6x duty saved in 6 years'
      ],
      officialSource: 'Directorate General of Foreign Trade (DGFT)',
      deadline: 'Perpetual under Foreign Trade Policy'
    });
  }

  return matchedSchemes.sort((a, b) => b.matchPercentage - a.matchPercentage);
}
