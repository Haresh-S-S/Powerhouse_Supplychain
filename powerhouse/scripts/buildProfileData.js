const fs = require('fs');

const initialBusinessProfile = {
  // Business Information
  businessName: 'Powerhouse Industries',
  businessType: 'Private Limited Company',
  industry: 'Manufacturing',
  sector: 'Industrial Equipment',
  establishedDate: '15 March 2018',
  companySize: 'Medium Enterprise',
  employees: 85,
  annualTurnover: '₹12.5 Crore',

  // Business Location
  registeredAddress: '42 Industrial Estate,\nAndheri East',
  city: 'Mumbai',
  state: 'Maharashtra',
  country: 'India',
  pinCode: '400093',
  operatingLocation: 'Mumbai, Maharashtra',

  // Business Operations
  primaryActivity: 'Manufacturing Industrial Equipment',
  secondaryActivities: 'Equipment Assembly, Distribution',
  manufacturingActivity: 'Yes',
  importActivities: 'Yes',
  exportActivities: 'No',
  environmentalImpact: 'Moderate',
  operatingStatus: 'Active',

  // Registration Details
  cin: 'U12345MH2018PTC123456',
  pan: 'ABCDE1234F',
  gstin: '27ABCDE1234F1Z5',
  msmeRegistration: 'Registered',
  udyamNumber: 'UDYAM-MH-12-0012345',
};

export const profileOptions = {
  businessTypes: [
    'Private Limited Company',
    'Public Limited Company',
    'Limited Liability Partnership (LLP)',
    'Partnership Firm',
    'Sole Proprietorship',
    'One Person Company (OPC)',
  ],
  industries: [
    'Manufacturing',
    'Information Technology & Services',
    'Healthcare & Pharmaceuticals',
    'Automotive & Aerospace',
    'Renewable Energy & Power',
    'Textiles & Apparel',
    'Chemicals & Petrochemicals',
    'Food Processing',
  ],
  sectors: [
    'Industrial Equipment',
    'Heavy Machinery',
    'Precision Engineering',
    'Electrical Appliances',
    'Automation Components',
  ],
  companySizes: [
    'Micro Enterprise (< ₹1 Cr)',
    'Small Enterprise (₹1 Cr - ₹10 Cr)',
    'Medium Enterprise',
    'Large Enterprise (> ₹50 Cr)',
  ],
  states: [
    'Maharashtra',
    'Gujarat',
    'Karnataka',
    'Tamil Nadu',
    'Delhi NCR',
    'Telangana',
    'Haryana',
    'Uttar Pradesh',
    'West Bengal',
  ],
  environmentalImpacts: [
    'Low',
    'Moderate',
    'High',
    'Critical (Red Category)',
  ],
  operatingStatuses: [
    'Active',
    'Temporarily Inactive',
    'Under Expansion',
    'Restructuring',
  ],
  yesNoOptions: ['Yes', 'No'],
};

export const profileStatusChecklist = [
  { id: 'business-info', label: 'Business Information', status: 'Completed' },
  { id: 'location-details', label: 'Location Details', status: 'Completed' },
  { id: 'operations', label: 'Operations', status: 'Completed' },
  { id: 'registration-details', label: 'Registration Details', status: 'Completed' },
  { id: 'financial-details', label: 'Financial Details', status: 'Pending' },
  { id: 'environmental-info', label: 'Environmental Information', status: 'Pending' },
];
;

fs.writeFileSync('src/data/businessProfileData.js', dataContent, 'utf8');
console.log('businessProfileData.js generated successfully');
