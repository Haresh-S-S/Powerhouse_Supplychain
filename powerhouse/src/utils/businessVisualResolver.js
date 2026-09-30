/**
 * POWER HOUSE Dynamic Business Visual Resolver
 *
 * Resolves category-specific commercial photography assets.
 * Guarantees zero fallback to textile for non-textile businesses.
 */

export const BUSINESS_IMAGE_MAP = {
  clothing_textile: '/business-images/textile.jpg',
  textile: '/business-images/textile.jpg',
  restaurant: '/business-images/restaurant.jpg',
  jewellery: '/business-images/jewellery.jpg',
  retail: '/business-images/retail.jpg',
  factory: '/business-images/manufacturing.jpg',
  manufacturing: '/business-images/manufacturing.jpg',
  default: '/business-images/default-business.jpg',
};

/**
 * Returns the exact matching commercial image for a given business category.
 * If the category is null, undefined, or unrecognized, it safely returns
 * default-business.jpg without ever leaking textile imagery.
 *
 * @param {string} category
 * @returns {string} Relative public image URL
 */
export function getBusinessImage(category) {
  if (!category || typeof category !== 'string') {
    return BUSINESS_IMAGE_MAP.default;
  }

  const key = category.toLowerCase().trim().replace(/[-\s]+/g, '_');

  if (BUSINESS_IMAGE_MAP[key]) {
    return BUSINESS_IMAGE_MAP[key];
  }

  if (key.includes('textile') || key.includes('cloth') || key.includes('garment') || key.includes('apparel')) {
    return BUSINESS_IMAGE_MAP.clothing_textile;
  }

  if (key.includes('restaurant') || key.includes('food') || key.includes('cafe') || key.includes('bakery')) {
    return BUSINESS_IMAGE_MAP.restaurant;
  }

  if (key.includes('jewel') || key.includes('gold')) {
    return BUSINESS_IMAGE_MAP.jewellery;
  }

  if (key.includes('retail') || key.includes('store') || key.includes('shop') || key.includes('market')) {
    return BUSINESS_IMAGE_MAP.retail;
  }

  if (key.includes('manufactur') || key.includes('factory') || key.includes('plant') || key.includes('industrial')) {
    return BUSINESS_IMAGE_MAP.factory;
  }

  return BUSINESS_IMAGE_MAP.default;
}

/**
 * Generates an appropriate initial display name for newly onboarded businesses
 * before the user sets an official registered legal name.
 * Avoids fabricating fictional legal company names.
 *
 * @param {string} category
 * @param {object} location
 * @returns {string} Clean temporary display name
 */
export function getCategoryDefaultName(category, location) {
  const city = location?.city ? `${location.city} ` : '';
  const key = (category || '').toLowerCase();

  if (key.includes('textile') || key.includes('cloth')) {
    return `${city}Textile Business`.trim();
  }
  if (key.includes('restaurant') || key.includes('food')) {
    return `${city}Restaurant Business`.trim();
  }
  if (key.includes('jewel')) {
    return `${city}Jewellery Store`.trim();
  }
  if (key.includes('retail') || key.includes('store') || key.includes('shop')) {
    return `${city}Retail Store`.trim();
  }
  if (key.includes('manufactur') || key.includes('factory')) {
    return `${city}Manufacturing Unit`.trim();
  }
  return `${city}Commercial Enterprise`.trim();
}

export default getBusinessImage;
