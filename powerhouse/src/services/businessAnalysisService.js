/**
 * POWER HOUSE Business Analysis Engine - Business Analysis Service
 * 
 * Service Layer abstraction decoupling UI from specific analysis rule engines.
 * Ready for future backend / AI API replacements without modifying UI callers.
 */

import { analyzeBusiness } from '../engine/businessAnalyzer';
import { validateProfile } from '../utils/analysisHelpers';

class BusinessAnalysisService {
  /**
   * Evaluates the business profile through the deterministic rule engine.
   * Supports async resolution to mimic seamless service execution.
   */
  async analyzeBusinessProfile(profile) {
    return new Promise((resolve) => {
      // Simulate micro-computation step
      const result = analyzeBusiness(profile);
      resolve(result);
    });
  }

  /**
   * Synchronous quick evaluator for dashboard badges and overview cards
   */
  getQuickSummary(profile) {
    return analyzeBusiness(profile);
  }

  /**
   * Validates mandatory profile attributes
   */
  validate(profile) {
    return validateProfile(profile);
  }
}

export const businessAnalysisService = new BusinessAnalysisService();
export default businessAnalysisService;
