import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { initialBusinessProfile } from '../data/businessProfileData';
import businessAnalysisService from '../services/businessAnalysisService';
import apiClient from '../services/apiClient';
import { classifyBusiness, extractLocation, BUSINESS_CATEGORIES, CATEGORY_LABELS } from '../engine/businessClassifier';
import { getTemplateBundle, getTemplateBusinessProfile, isGeneralizedTemplate } from '../data/businessTemplates';

// Factory keeps using its original, untouched static data files.
import { approvalsStats as factoryApprovalsStats, approvalsList as factoryApprovalsList } from '../data/approvalsData';
import { initialTasksList as factoryTasksList } from '../data/tasksData';
import { documentsStats as factoryDocumentsStats, initialDocumentsList as factoryDocumentsList } from '../data/documentsData';
import { schemesHighlight as factorySchemesHighlight, schemesList as factorySchemesList } from '../data/schemesData';
import { alertsStats as factoryAlertsStats, initialAlertsList as factoryAlertsList } from '../data/alertsData';
import { applicationsStats as factoryApplicationsStats, initialApplicationsList as factoryApplicationsList } from '../data/applicationsData';

const BusinessAnalysisContext = createContext(null);

const ONBOARDING_STORAGE_KEY = 'phflow_onboarding_v1';

export const ANALYSIS_STEPS = [
  'Connecting to Enterprise Compliance Data Layer...',
  'Evaluating Statutory & Environmental Compliance Rules...',
  'Mapping Regulatory Approvals & Licences in PostgreSQL...',
  'Generating Compliance Tasks & Document Vault Checklists...',
  'Matching Eligible Central & State Government Schemes...',
  'Synthesizing Executive Business Intelligence Insights...',
];

function readStoredOnboarding() {
  try {
    const raw = window.localStorage.getItem(ONBOARDING_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

function writeStoredOnboarding(state) {
  try {
    window.localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    // Local storage unavailable - prototype continues without persistence.
  }
}

function normalizeAnalysisResult(res) {
  if (!res) return null;

  const approvals = res.approvals || [];
  const complianceTasks = res.complianceTasks || res.compliance_tasks || [];
  const requiredDocuments = res.requiredDocuments || res.required_documents || [];
  const recommendedSchemes = res.recommendedSchemes || res.recommended_schemes || [];
  const insights = res.insights || [];
  const rawSummary = res.summary || {};

  const totalApprovals = rawSummary.totalApprovals ?? rawSummary.total_approvals ?? approvals.length;
  const highPriorityApprovals = rawSummary.highPriorityApprovals ?? rawSummary.high_priority_approvals ?? 0;
  const totalComplianceTasks = rawSummary.complianceTasks ?? rawSummary.total_compliance_tasks ?? complianceTasks.length;
  const upcomingTasks = rawSummary.upcomingTasks ?? rawSummary.upcoming_tasks ?? 0;
  const totalRequiredDocuments = rawSummary.requiredDocuments ?? rawSummary.total_required_documents ?? requiredDocuments.length;
  const totalRecommendedSchemes = rawSummary.recommendedSchemes ?? rawSummary.total_recommended_schemes ?? recommendedSchemes.length;
  const complianceScore = rawSummary.complianceScore ?? rawSummary.compliance_score ?? 78;

  const normalizedSummary = {
    totalApprovals,
    total_approvals: totalApprovals,
    highPriorityApprovals,
    high_priority_approvals: highPriorityApprovals,
    complianceTasks: totalComplianceTasks,
    total_compliance_tasks: totalComplianceTasks,
    upcomingTasks,
    upcoming_tasks: upcomingTasks,
    requiredDocuments: totalRequiredDocuments,
    total_required_documents: totalRequiredDocuments,
    recommendedSchemes: totalRecommendedSchemes,
    total_recommended_schemes: totalRecommendedSchemes,
    complianceScore,
    compliance_score: complianceScore,
  };

  const businessSummary = res.businessSummary || res.business_summary || {};

  return {
    ...res,
    isValid: res.isValid ?? res.is_valid ?? true,
    is_valid: res.isValid ?? res.is_valid ?? true,
    analysisDate: res.analysisDate || res.analysis_date || new Date().toISOString().split('T')[0],
    analysis_date: res.analysisDate || res.analysis_date || new Date().toISOString().split('T')[0],
    riskLevel: res.riskLevel || res.risk_level || 'Medium',
    risk_level: res.riskLevel || res.risk_level || 'Medium',
    businessSummary: {
      ...businessSummary,
      businessName: businessSummary.businessName || businessSummary.business_name || 'Powerhouse Industries',
      businessType: businessSummary.businessType || businessSummary.business_type || 'Private Limited Company',
      industry: businessSummary.industry || 'Manufacturing',
      sector: businessSummary.sector || 'Industrial Equipment & Machinery',
      city: businessSummary.city || 'Mumbai',
      state: businessSummary.state || 'Maharashtra',
      companySize: businessSummary.companySize || businessSummary.company_size || 'Medium Enterprise',
      employees: businessSummary.employees ?? businessSummary.employee_count ?? 85,
      annualTurnover: businessSummary.annualTurnover || businessSummary.annual_turnover || '₹28.5 Crores',
      operatingStatus: businessSummary.operatingStatus || businessSummary.operating_status || 'Active',
      gstin: businessSummary.gstin || '27AAACP4821K1ZV',
      udyamNumber: businessSummary.udyamNumber || businessSummary.udyam_number || 'UDYAM-MH-19-0024891',
    },
    approvals,
    complianceTasks,
    compliance_tasks: complianceTasks,
    requiredDocuments,
    required_documents: requiredDocuments,
    recommendedSchemes,
    recommended_schemes: recommendedSchemes,
    summary: normalizedSummary,
    insights,
  };
}

import { useAuth } from './AuthContext';
import { getCategoryDefaultName } from '../utils/businessVisualResolver';

const FACTORY_BUNDLE = {
  key: BUSINESS_CATEGORIES.FACTORY,
  meta: {
    key: 'factory',
    categoryLabel: 'Factory / Manufacturing',
    defaultBusinessName: 'Powerhouse Industries',
    businessType: 'Private Limited Company',
    industry: 'Industrial Equipment & Machinery',
    sector: 'Manufacturing',
    companySize: 'Medium Enterprise',
    employees: 85,
    annualTurnover: '₹28.5 Crores',
    gstinPlaceholder: '27AAACP4821K1ZV',
    udyamPlaceholder: 'UDYAM-MH-19-0024891',
    complianceScore: 78,
    image: '/business-images/manufacturing.jpg',
    constitution: 'Private Limited Company',
  },
  approvalsList: factoryApprovalsList,
  approvalsStats: factoryApprovalsStats,
  tasksList: factoryTasksList,
  documentsList: factoryDocumentsList,
  documentsStats: factoryDocumentsStats,
  schemesList: factorySchemesList,
  schemesHighlight: factorySchemesHighlight,
  alertsList: factoryAlertsList,
  alertsStats: factoryAlertsStats,
  applicationsList: factoryApplicationsList,
  applicationsStats: factoryApplicationsStats,
};

function isFactoryCategory(category) {
  return !category || category === BUSINESS_CATEGORIES.FACTORY || !isGeneralizedTemplate(category);
}

export function BusinessAnalysisProvider({ children }) {
  const auth = useAuth();
  const storedOnboarding = useMemo(() => readStoredOnboarding(), []);

  const defaultCategory = auth?.activeBusiness?.business_category || storedOnboarding?.category || BUSINESS_CATEGORIES.CLOTHING_TEXTILE;
  const defaultLocation = auth?.activeBusiness
    ? { city: auth.activeBusiness.city, state: auth.activeBusiness.state }
    : (storedOnboarding?.location || { city: 'Tiruppur', state: 'Tamil Nadu' });
  const defaultOnboardingComplete = auth?.onboardingCompleted ?? (storedOnboarding ? Boolean(storedOnboarding.onboardingComplete) : false);

  const [businessProfile, setBusinessProfile] = useState(() => {
    if (isFactoryCategory(defaultCategory)) return initialBusinessProfile;
    return getTemplateBusinessProfile(defaultCategory, defaultLocation) || initialBusinessProfile;
  });
  const [backendProfileId, setBackendProfileId] = useState(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);

  const [onboardingComplete, setOnboardingComplete] = useState(defaultOnboardingComplete);
  const [businessCategory, setBusinessCategory] = useState(defaultCategory);
  const [businessLocation, setBusinessLocation] = useState(defaultLocation);

  const [analysisResult, setAnalysisResult] = useState(() => {
    if (!isFactoryCategory(defaultCategory)) {
      const bundle = getTemplateBundle(defaultCategory, defaultLocation);
      if (bundle) return normalizeAnalysisResult(bundle.analysis);
    }
    return normalizeAnalysisResult(businessAnalysisService.getQuickSummary(initialBusinessProfile));
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [hasAnalysisRun, setHasAnalysisRun] = useState(true);

  // Sync with auth.activeBusiness when it changes
  useEffect(() => {
    if (auth?.activeBusiness) {
      const cat = auth.activeBusiness.business_category || BUSINESS_CATEGORIES.FACTORY;
      const loc = { city: auth.activeBusiness.city, state: auth.activeBusiness.state };
      setBusinessCategory(cat);
      setBusinessLocation(loc);
      setOnboardingComplete(true);
      setBackendProfileId(auth.activeBusiness.id);

      if (isFactoryCategory(cat)) {
        setBusinessProfile({
          ...initialBusinessProfile,
          businessName: auth.activeBusiness.business_name || initialBusinessProfile.businessName,
          city: auth.activeBusiness.city || initialBusinessProfile.city,
          state: auth.activeBusiness.state || initialBusinessProfile.state,
        });
        setAnalysisResult(
          normalizeAnalysisResult(businessAnalysisService.getQuickSummary(initialBusinessProfile))
        );
      } else {
        const bundle = getTemplateBundle(cat, loc);
        if (bundle) {
          setAnalysisResult(normalizeAnalysisResult(bundle.analysis));
        }
        const templateProfile = getTemplateBusinessProfile(cat, loc) || initialBusinessProfile;
        setBusinessProfile({
          ...templateProfile,
          businessName: auth.activeBusiness.business_name || templateProfile.businessName,
        });
      }
    } else if (auth && !auth.isAuthenticated && !auth.isLoading) {
      setOnboardingComplete(false);
    }
  }, [auth?.activeBusiness, auth?.isAuthenticated, auth?.isLoading]);

  // Only the factory demo talks to the (optional) backend - the
  // generalized templates are purely local, per the prototype's
  // "no external API" requirement.
  useEffect(() => {
    if (!isFactoryCategory(businessCategory)) return;

    async function initBackend() {
      try {
        const profiles = await apiClient.getBusinessProfiles();
        if (profiles && profiles.length > 0) {
          const primary = profiles[0];
          setBackendProfileId(primary.id);
          setIsBackendConnected(true);

          try {
            const backendAnalysis = await apiClient.getLatestAnalysis(primary.id);
            if (backendAnalysis && backendAnalysis.analysis_result) {
              setAnalysisResult(normalizeAnalysisResult(backendAnalysis.analysis_result));
            }
          } catch (e) {
            // Keep current normalized state
          }
        }
      } catch (err) {
        setIsBackendConnected(false);
      }
    }
    initBackend();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const persistOnboarding = (next) => {
    writeStoredOnboarding(next);
  };

  const updateBusinessProfile = async (updatedData) => {
    setBusinessProfile(updatedData);

    if (isBackendConnected && backendProfileId && isFactoryCategory(businessCategory)) {
      try {
        await apiClient.updateBusinessProfile(backendProfileId, {
          business_name: updatedData.businessName,
          business_type: updatedData.businessType,
          industry: updatedData.industry,
          sector: updatedData.sector,
          company_size: updatedData.companySize,
          employee_count: parseInt(updatedData.employees, 10) || 1,
          annual_turnover: updatedData.annualTurnover,
          city: updatedData.city,
          state: updatedData.state,
          manufacturing_activity: updatedData.manufacturingActivity === 'Yes' || updatedData.manufacturingActivity === true,
          import_activities: updatedData.importActivities === 'Yes' || updatedData.importActivities === true,
          export_activities: updatedData.exportActivities === 'Yes' || updatedData.exportActivities === true,
          environmental_impact: updatedData.environmentalImpact || 'Moderate',
          operating_status: updatedData.operatingStatus || 'Active',
          gstin: updatedData.gstin,
          udyam_number: updatedData.udyamNumber,
        });
      } catch (e) {
        console.warn('Backend sync failed, state retained locally.');
      }
    }
  };

  const runAnalysis = async (profileOverride = null, onComplete = null) => {
    setIsAnalyzing(true);
    setCurrentStepIndex(0);

    for (let i = 0; i < ANALYSIS_STEPS.length; i++) {
      setCurrentStepIndex(i);
      await new Promise((r) => setTimeout(r, 200));
    }

    let finalResult = null;

    if (isFactoryCategory(businessCategory)) {
      const targetProfile = profileOverride || businessProfile;

      if (isBackendConnected && backendProfileId) {
        try {
          const backendResp = await apiClient.runAnalysis(backendProfileId);
          if (backendResp && backendResp.analysis_result) {
            finalResult = backendResp.analysis_result;
          }
        } catch (err) {
          console.warn('Backend analysis failed, falling back to local engine:', err);
        }
      }

      if (!finalResult) {
        finalResult = await businessAnalysisService.analyzeBusinessProfile(targetProfile);
      }
    } else {
      // Deterministic local templates - re-running simply rebuilds the
      // same bundle (no external calls, no randomness).
      const bundle = getTemplateBundle(businessCategory, businessLocation);
      finalResult = bundle?.analysis;
    }

    const normalized = normalizeAnalysisResult(finalResult);
    setAnalysisResult(normalized);
    setHasAnalysisRun(true);
    setIsAnalyzing(false);

    if (onComplete) {
      onComplete(normalized);
    }
    return normalized;
  };

  /**
   * Runs the local keyword classifier + location extractor on a free-text
   * business description. Does NOT commit anything - used to populate the
   * onboarding confirmation screen before the user confirms.
   */
  const classifyDescription = (description) => {
    const category = classifyBusiness(description);
    const location = extractLocation(description);
    return {
      category,
      location,
      categoryLabel: category ? CATEGORY_LABELS[category] : null,
    };
  };

  /**
   * Commits a classification result: switches the active business
   * category/location, updates the analysis result accordingly, and
   * marks onboarding as complete. Persists to backend if authenticated.
   */
  const confirmBusinessClassification = async (category, location, customName = null) => {
    setBusinessCategory(category);
    setBusinessLocation(location || null);
    setOnboardingComplete(true);

    const displayName = customName || getCategoryDefaultName(category, location);

    persistOnboarding({
      onboardingComplete: true,
      category,
      location: location || null,
      businessName: displayName,
    });

    let activeProfile = null;

    if (isFactoryCategory(category)) {
      activeProfile = {
        ...initialBusinessProfile,
        businessName: displayName || initialBusinessProfile.businessName,
        city: location?.city || initialBusinessProfile.city,
        state: location?.state || initialBusinessProfile.state,
      };
      setBusinessProfile(activeProfile);
      setAnalysisResult(
        normalizeAnalysisResult(businessAnalysisService.getQuickSummary(activeProfile))
      );
    } else {
      const bundle = getTemplateBundle(category, location);
      if (bundle) {
        setAnalysisResult(normalizeAnalysisResult(bundle.analysis));
      }
      const templateProfile = getTemplateBusinessProfile(category, location) || initialBusinessProfile;
      activeProfile = {
        ...templateProfile,
        businessName: displayName || templateProfile.businessName,
      };
      setBusinessProfile(activeProfile);
    }

    // Persist to backend if user is authenticated
    if (auth?.isAuthenticated) {
      try {
        const payload = {
          business_name: displayName,
          business_type: activeProfile.businessType || 'Sole Proprietorship',
          industry: activeProfile.industry || 'Trade & Commerce',
          sector: activeProfile.sector || 'Commercial Enterprise',
          company_size: activeProfile.companySize || 'Micro / Small Enterprise',
          employee_count: parseInt(activeProfile.employees, 10) || 5,
          annual_turnover: activeProfile.annualTurnover || '₹25 - 50 Lakhs',
          city: location?.city || activeProfile.city || 'Chennai',
          state: location?.state || activeProfile.state || 'Tamil Nadu',
          country: 'India',
          manufacturing_activity: category === BUSINESS_CATEGORIES.FACTORY,
          operating_status: 'Active',
          has_gst: false,
          has_msme_registration: false,
          has_udyam_registration: false,
          onboarding_completed: true,
          business_category: category,
          image_category: category,
        };

        const created = await apiClient.createBusinessProfile(payload);
        if (created?.id) {
          setBackendProfileId(created.id);
          setIsBackendConnected(true);
          auth.updateOnboardingState(true, created);
          return created;
        }
      } catch (err) {
        console.warn('Backend business creation failed, continuing in local state:', err);
      }
    }

    if (auth?.updateOnboardingState) {
      auth.updateOnboardingState(true, {
        id: `local-${Date.now()}`,
        business_name: displayName,
        business_category: category,
        city: location?.city || 'Chennai',
        state: location?.state || 'Tamil Nadu',
        onboarding_completed: true,
      });
    }
  };

  /**
   * Switches the active business category with zero data bleed.
   */
  const switchBusinessCategory = (targetCategory, targetLocation = null) => {
    const existing = auth?.userBusinesses?.find((b) => b.business_category === targetCategory);
    if (existing && auth?.switchActiveBusiness) {
      auth.switchActiveBusiness(existing);
      return;
    }

    setBusinessCategory(targetCategory);
    setBusinessLocation(targetLocation || null);
    setOnboardingComplete(true);
    persistOnboarding({
      onboardingComplete: true,
      category: targetCategory,
      location: targetLocation || null,
    });

    if (isFactoryCategory(targetCategory)) {
      setBusinessProfile(initialBusinessProfile);
      setAnalysisResult(
        normalizeAnalysisResult(businessAnalysisService.getQuickSummary(initialBusinessProfile))
      );
    } else {
      const bundle = getTemplateBundle(targetCategory, targetLocation);
      if (bundle) {
        setAnalysisResult(normalizeAnalysisResult(bundle.analysis));
      }
      setBusinessProfile(getTemplateBusinessProfile(targetCategory, targetLocation) || initialBusinessProfile);
    }
  };

  /**
   * Sends the user back to the onboarding screen (e.g. "Sign Out" or
   * "Switch Business Type").
   */
  const resetOnboarding = () => {
    setOnboardingComplete(false);
    persistOnboarding({
      onboardingComplete: false,
      category: businessCategory,
      location: businessLocation,
    });
    if (auth?.updateOnboardingState) {
      auth.updateOnboardingState(false);
    }
  };

  const businessTemplateBundle = useMemo(() => {
    if (isFactoryCategory(businessCategory)) {
      return FACTORY_BUNDLE;
    }
    return getTemplateBundle(businessCategory, businessLocation) || FACTORY_BUNDLE;
  }, [businessCategory, businessLocation]);

  return (
    <BusinessAnalysisContext.Provider
      value={{
        businessProfile,
        backendProfileId,
        isBackendConnected,
        updateBusinessProfile,
        analysisResult,
        isAnalyzing,
        currentStepIndex,
        currentStepText: ANALYSIS_STEPS[currentStepIndex],
        analysisSteps: ANALYSIS_STEPS,
        hasAnalysisRun,
        runAnalysis,

        // Business classification / onboarding
        onboardingComplete,
        businessCategory,
        businessCategoryLabel: CATEGORY_LABELS[businessCategory] || CATEGORY_LABELS[BUSINESS_CATEGORIES.FACTORY],
        businessLocation,
        classifyDescription,
        confirmBusinessClassification,
        switchBusinessCategory,
        resetOnboarding,

        // Unified per-category data bundle for hub pages
        businessTemplateBundle,
      }}
    >
      {children}
    </BusinessAnalysisContext.Provider>
  );
}

export function useBusinessAnalysis() {
  const context = useContext(BusinessAnalysisContext);
  if (!context) {
    throw new Error('useBusinessAnalysis must be used within a BusinessAnalysisProvider');
  }
  return context;
}

export default BusinessAnalysisContext;
