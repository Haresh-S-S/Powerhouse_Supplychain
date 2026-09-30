/**
 * POWER HOUSE Business Analysis Engine - Business Template Registry
 *
 * Factory / Manufacturing continues to use the existing deterministic
 * rule engine (src/engine/businessAnalyzer.js) and its existing static
 * data files - it is NOT part of this registry, by design, so the
 * existing PowerHouse Industries demo is left completely untouched.
 *
 * This registry only covers the four new generalized templates.
 */

import * as retail from './retail';
import * as restaurant from './restaurant';
import * as clothingTextile from './clothingTextile';
import * as jewellery from './jewellery';
import { buildTemplateBundle, buildTemplateBusinessProfile } from './helpers';
import { BUSINESS_CATEGORIES, CATEGORY_LABELS } from '../../engine/businessClassifier';

const TEMPLATES = {
  [BUSINESS_CATEGORIES.RETAIL]: retail,
  [BUSINESS_CATEGORIES.RESTAURANT]: restaurant,
  [BUSINESS_CATEGORIES.CLOTHING_TEXTILE]: clothingTextile,
  [BUSINESS_CATEGORIES.JEWELLERY]: jewellery,
};

export { BUSINESS_CATEGORIES, CATEGORY_LABELS };

/**
 * Returns true for any category this registry can build a bundle for
 * (i.e. every category except 'factory', which uses the original
 * rule engine + static data files instead).
 */
export function isGeneralizedTemplate(categoryKey) {
  return Boolean(TEMPLATES[categoryKey]);
}

/**
 * Builds the full data bundle for a given (non-factory) business
 * category, personalized with the detected location if any.
 */
export function getTemplateBundle(categoryKey, location) {
  const template = TEMPLATES[categoryKey];
  if (!template) return null;
  return buildTemplateBundle(template, location);
}

/**
 * Builds the Business-Profile-page record for a given (non-factory)
 * category, so the profile page shows this business instead of the
 * PowerHouse Industries factory profile. Returns null for 'factory'
 * (or any unrecognized category), letting the caller fall back to
 * `initialBusinessProfile`.
 */
export function getTemplateBusinessProfile(categoryKey, location) {
  const template = TEMPLATES[categoryKey];
  if (!template) return null;
  return buildTemplateBusinessProfile(template, location);
}
