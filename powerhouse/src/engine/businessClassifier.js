/**
 * POWER HOUSE Business Analysis Engine - Business Classifier
 *
 * 100% local, deterministic keyword classification.
 * No external AI API, no network calls, no ML model.
 *
 * This is intentionally simple: the value of this prototype is the
 * onboarding -> classification -> dashboard workflow, not sophisticated NLP.
 */

export const BUSINESS_CATEGORIES = {
  RESTAURANT: 'restaurant',
  JEWELLERY: 'jewellery',
  CLOTHING_TEXTILE: 'clothing_textile',
  FACTORY: 'factory',
  RETAIL: 'retail',
};

export const CATEGORY_LABELS = {
  [BUSINESS_CATEGORIES.RESTAURANT]: 'Restaurant / Food Business',
  [BUSINESS_CATEGORIES.JEWELLERY]: 'Jewellery Store',
  [BUSINESS_CATEGORIES.CLOTHING_TEXTILE]: 'Clothing & Textile Business',
  [BUSINESS_CATEGORIES.FACTORY]: 'Factory / Manufacturing',
  [BUSINESS_CATEGORIES.RETAIL]: 'Retail / Small Shop',
};

// Ordered from most specific to most generic. A more specific category
// (e.g. Jewellery) must always win over a generic one (e.g. Retail),
// even when a generic word like "shop" also appears in the text.
const CLASSIFICATION_RULES = [
  {
    category: BUSINESS_CATEGORIES.RESTAURANT,
    keywords: [
      'restaurant', 'cafe', 'café', 'bakery', 'food outlet', 'food shop',
      'catering', 'food business', 'eatery', 'dhaba', 'tiffin center',
      'tiffin centre', 'sweet shop', 'food truck', 'canteen',
    ],
  },
  {
    category: BUSINESS_CATEGORIES.JEWELLERY,
    keywords: [
      'jewellery', 'jewelry', 'gold shop', 'gold jewellery', 'gold jewelry',
      'silver shop', 'ornaments', 'ornament store', 'gold store', 'bullion',
    ],
  },
  {
    category: BUSINESS_CATEGORIES.CLOTHING_TEXTILE,
    keywords: [
      'clothing', 'garment', 'textile', 'fashion', 'apparel', 'clothes',
      'boutique', 'saree shop', 'tailoring',
    ],
  },
  {
    category: BUSINESS_CATEGORIES.FACTORY,
    keywords: [
      'factory', 'manufactur', 'production unit', 'industrial', 'plant',
      'fabrication', 'assembly unit', 'processing unit',
    ],
  },
  {
    category: BUSINESS_CATEGORIES.RETAIL,
    keywords: [
      'shop', 'store', 'retail', 'grocery', 'flower', 'general store',
      'stationery', 'supermarket', 'kirana', 'mart',
    ],
  },
];

/**
 * Classifies a free-text business description into one of the five
 * supported business templates. Returns null when nothing matches
 * confidently, so the caller can show the "couldn't identify" screen.
 */
export function classifyBusiness(description) {
  if (!description || !description.trim()) return null;
  const text = description.toLowerCase();

  for (const rule of CLASSIFICATION_RULES) {
    if (rule.keywords.some((keyword) => text.includes(keyword))) {
      return rule.category;
    }
  }

  return null;
}

// Minimal city -> state lookup. Intentionally small; this is only meant
// to give the prototype a sense of location awareness, not a full
// geographic database.
const CITY_STATE_MAP = [
  { match: 'chennai', city: 'Chennai', state: 'Tamil Nadu' },
  { match: 'coimbatore', city: 'Coimbatore', state: 'Tamil Nadu' },
  { match: 'tiruppur', city: 'Tiruppur', state: 'Tamil Nadu' },
  { match: 'madurai', city: 'Madurai', state: 'Tamil Nadu' },
  { match: 'salem', city: 'Salem', state: 'Tamil Nadu' },
  { match: 'tiruchirappalli', city: 'Tiruchirappalli', state: 'Tamil Nadu' },
  { match: 'trichy', city: 'Tiruchirappalli', state: 'Tamil Nadu' },
  { match: 'erode', city: 'Erode', state: 'Tamil Nadu' },
  { match: 'bengaluru', city: 'Bengaluru', state: 'Karnataka' },
  { match: 'bangalore', city: 'Bengaluru', state: 'Karnataka' },
  { match: 'mumbai', city: 'Mumbai', state: 'Maharashtra' },
  { match: 'delhi', city: 'Delhi', state: 'Delhi' },
  { match: 'hyderabad', city: 'Hyderabad', state: 'Telangana' },
];

/**
 * Tries to spot a known city name in the description. Returns
 * { city, state } or null when nothing is detected. Deliberately
 * simple - no NLP, no fuzzy matching.
 */
export function extractLocation(description) {
  if (!description) return null;
  const text = description.toLowerCase();

  for (const entry of CITY_STATE_MAP) {
    if (text.includes(entry.match)) {
      return { city: entry.city, state: entry.state };
    }
  }

  return null;
}
