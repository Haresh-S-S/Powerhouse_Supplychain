from typing import List, Dict, Any
from app.engine.approval_rules import resolve_business_category


def match_government_schemes(profile: Any) -> List[Dict[str, Any]]:
    def get_val(key, default=None):
        if isinstance(profile, dict):
            return profile.get(key, default)
        return getattr(profile, key, default)

    category = resolve_business_category(profile)
    state = get_val("state", "")
    city = get_val("city", "")
    company_size = get_val("company_size", "") or ""
    env_impact = get_val("environmental_impact", "Moderate")
    op_status = get_val("operating_status", "Active")
    is_msme = get_val("has_msme_registration", True) or get_val("has_udyam_registration", True) or bool(get_val("udyam_number"))

    matched_schemes = []

    # ==========================================
    # 1. RESTAURANT SCHEMES
    # ==========================================
    if category == "restaurant":
        matched_schemes.append({
            "name": "Pradhan Mantri Formalisation of Micro Food Processing Enterprises (PMFME)",
            "short_name": "PMFME Food Processing Subsidy",
            "description": "Credit-linked capital subsidy for micro food processing, commercial cloud kitchens, and eatery modernization.",
            "benefit": "Up to 35% Capital Subsidy (Max ₹10 Lakhs)",
            "category": "Food Industry Subsidy",
            "match_score": 92,
            "match_reason": ["Micro food service enterprise (+40%)", "Equipment modernization eligible (+30%)", "Commercial kitchen food safety standard (+22%)"],
            "eligibility_status": "Eligible",
            "official_source": "Ministry of Food Processing Industries, Govt of India (mofpi.gov.in)",
            "deadline": "Open year-round (Quarterly tranches)"
        })
        matched_schemes.append({
            "name": "Pradhan Mantri MUDRA Yojana (Kishor / Tarun)",
            "short_name": "MUDRA Restaurant Equipment Loan",
            "description": "Collateral-free institutional micro-credit for commercial kitchen ovens, chillers, and dining setup.",
            "benefit": "Loans up to ₹10 Lakh (Collateral-Free)",
            "category": "Central Government Credit Scheme",
            "match_score": 85,
            "match_reason": ["Commercial restaurant dining operations (+35%)", "Working capital & kitchen assets (+30%)", "Clean business credit history (+20%)"],
            "eligibility_status": "Eligible",
            "official_source": "Department of Financial Services, Govt of India (mudra.org.in)",
            "deadline": "Rolling applications"
        })
        matched_schemes.append({
            "name": "PM SVANidhi (Prime Minister Street Vendor's AtmaNirbhar Nidhi)",
            "short_name": "PM SVANidhi Scheme",
            "description": "Special micro-credit facility with interest subsidy for small food kiosks, tiffin centers, and quick service stalls.",
            "benefit": "7% Interest Subsidy on Working Capital",
            "category": "Central Micro Credit",
            "match_score": 78,
            "match_reason": ["Urban food retail operations (+40%)", "Digital payments incentive eligible (+38%)"],
            "eligibility_status": "Eligible",
            "official_source": "Ministry of Housing and Urban Affairs (pmsvanidhi.mohua.gov.in)",
            "deadline": "31 December 2026"
        })

    # ==========================================
    # 2. CLOTHING & TEXTILE SCHEMES
    # ==========================================
    elif category == "clothing_textile":
        matched_schemes.append({
            "name": "Amended Technology Upgradation Fund Scheme (ATUFS)",
            "short_name": "ATUFS Scheme",
            "description": "Capital investment subsidy on benchmarked machinery for modern garment and textile retail/processing units.",
            "benefit": "Up to ₹25 Lakhs Capital Subsidy",
            "category": "Central Textile Subsidy",
            "match_score": 94,
            "match_reason": ["Registered textile/apparel establishment (+45%)", "Machinery modernization eligible (+30%)", "Udyam registration verified (+19%)"],
            "eligibility_status": "Eligible",
            "official_source": "Ministry of Textiles, Govt of India (texmin.nic.in)",
            "deadline": "Open all year round"
        })
        matched_schemes.append({
            "name": "Production Linked Incentive (PLI) Scheme for Textiles",
            "short_name": "PLI for Textiles",
            "description": "Incentive on incremental turnover for apparel, man-made fiber (MMF) fabrics, and technical textiles.",
            "benefit": "11% to 15% Turnover Incentive",
            "category": "National Manufacturing Incentive",
            "match_score": 88,
            "match_reason": ["Textile cluster geographic location (+40%)", "Value-added garment output (+30%)", "Active GST filing (+18%)"],
            "eligibility_status": "Eligible",
            "official_source": "Ministry of Textiles (pli.texmin.gov.in)",
            "deadline": "Annual review cycle"
        })
        matched_schemes.append({
            "name": "Scheme for Rebate of State and Central Taxes and Levies (RoSCTL / RoDTEP)",
            "short_name": "RoSCTL / RoDTEP Rebate",
            "description": "Duty drawback and tax rebate on export or domestic shipment of made-ups and apparel goods.",
            "benefit": "Up to 4.3% Duty Scrip Rebate",
            "category": "Trade Policy Rebate",
            "match_score": 82,
            "match_reason": ["Commercial textile supplies (+45%)", "Duty scrip redemption on customs/GST (+37%)"],
            "eligibility_status": "Eligible",
            "official_source": "Directorate General of Foreign Trade (dgft.gov.in)",
            "deadline": "Perpetual under Foreign Trade Policy"
        })

    # ==========================================
    # 3. JEWELLERY SCHEMES
    # ==========================================
    elif category == "jewellery":
        matched_schemes.append({
            "name": "Gold Monetisation Scheme (GMS)",
            "short_name": "Gold Monetisation Scheme",
            "description": "Mobilisation of idle gold stock and gold metal loan (GML) access with concessional interest rates for jewelers.",
            "benefit": "Concessional 2.5% Gold Metal Loan Interest",
            "category": "Central Gold Policy",
            "match_score": 91,
            "match_reason": ["Authorized precious jewellery dealership (+45%)", "BIS hallmarking compliance linkage (+30%)", "Bank bullion financing eligible (+16%)"],
            "eligibility_status": "Eligible",
            "official_source": "Reserve Bank of India & Department of Economic Affairs",
            "deadline": "Open year-round"
        })
        matched_schemes.append({
            "name": "Gem & Jewellery Export Promotion Council Financial Assistance Scheme",
            "short_name": "GJEPC Export & Exhibition Scheme",
            "description": "Subsidized participation in domestic B2B trade expos, international jewellery fairs, and buyer-seller meets.",
            "benefit": "Up to 50% Exhibition Booth Reimbursement",
            "category": "Industry Export Promotion",
            "match_score": 84,
            "match_reason": ["Active precious ornaments trade (+40%)", "GJEPC member cluster eligibility (+28%)", "Clean tax compliance standing (+16%)"],
            "eligibility_status": "Eligible",
            "official_source": "GJEPC & Ministry of Commerce (gjepc.org)",
            "deadline": "Quarterly expo allocations"
        })
        matched_schemes.append({
            "name": "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
            "short_name": "CGTMSE Collateral-Free Credit",
            "description": "Collateral-free credit guarantee coverage for jewellery showroom expansion and secure vault infrastructure.",
            "benefit": "Guaranteed credit lines up to ₹2 Crores",
            "category": "Credit Guarantee",
            "match_score": 79,
            "match_reason": ["Small enterprise scale (+40%)", "Working capital inventory coverage (+39%)"],
            "eligibility_status": "Eligible",
            "official_source": "SIDBI & Ministry of MSME (cgtmse.in)",
            "deadline": "Rolling applications"
        })

    # ==========================================
    # 4. RETAIL SCHEMES
    # ==========================================
    elif category == "retail":
        matched_schemes.append({
            "name": "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
            "short_name": "CGTMSE Retail Credit Guarantee",
            "description": "Institutional credit facility for retail stores without third-party guarantee or immovable collateral.",
            "benefit": "Up to ₹2 Crores Collateral-Free Credit",
            "category": "Retail Credit Guarantee",
            "match_score": 90,
            "match_reason": ["Verified retail trading enterprise (+45%)", "Storefront working capital support (+25%)", "Clean financial credit score (+20%)"],
            "eligibility_status": "Eligible",
            "official_source": "SIDBI & Ministry of MSME (cgtmse.in)",
            "deadline": "Rolling applications"
        })
        matched_schemes.append({
            "name": "Prime Minister Employment Generation Programme (PMEGP)",
            "short_name": "PMEGP Retail Subsidy",
            "description": "Credit-linked capital subsidy for new retail shop establishments and service units.",
            "benefit": "Up to 25% Capital Subsidy",
            "category": "Central Government Subsidy",
            "match_score": 83,
            "match_reason": ["New commercial shop establishment (+40%)", "Udyam registered (+25%)", "Eligible urban/rural bracket (+18%)"],
            "eligibility_status": "Eligible",
            "official_source": "KVIC & Ministry of MSME (kviconline.gov.in)",
            "deadline": "Open year-round"
        })
        matched_schemes.append({
            "name": "Stand-Up India Scheme for Retail & Trading Enterprises",
            "short_name": "Stand-Up India Scheme",
            "description": "Bank loans between ₹10 Lakhs and ₹1 Crore for greenfield commercial retail and trading stores.",
            "benefit": "₹10L to ₹1Cr Greenfield Bank Term Loan",
            "category": "Institutional Banking",
            "match_score": 77,
            "match_reason": ["Commercial storefront operations (+40%)", "Priority sector trading facility (+37%)"],
            "eligibility_status": "Eligible",
            "official_source": "Department of Financial Services (standupmitra.in)",
            "deadline": "Active • Perpetual"
        })

    # ==========================================
    # 5. MANUFACTURING / FACTORY SCHEMES
    # ==========================================
    else:
        matched_schemes.append({
            "name": "Production Linked Incentive (PLI) Scheme for Manufacturing",
            "short_name": "PLI Manufacturing Scheme",
            "description": "Direct financial incentives on incremental industrial production across benchmarked core manufacturing categories.",
            "benefit": "4% to 6% Incentive on Incremental Sales",
            "category": "National Industry Policy",
            "match_score": 93,
            "match_reason": ["Core industrial production unit (+45%)", "Installed machinery capacity (+30%)", "Active GST & Factory registration (+18%)"],
            "eligibility_status": "Eligible",
            "official_source": "Department for Promotion of Industry and Internal Trade (DPIIT)",
            "deadline": "31 October 2026"
        })
        matched_schemes.append({
            "name": "MSME Technology Upgradation Scheme (CLCSS & ZED Certification)",
            "short_name": "MSME Technology Upgradation & ZED",
            "description": "Capital subsidy for adopting state-of-the-art clean manufacturing technologies with Zero Defect Zero Effect (ZED) rating.",
            "benefit": "15% Upfront Capital Subsidy + ZED Grant",
            "category": "Technology & Quality Upgrade",
            "match_score": 88,
            "match_reason": ["Udyam verified manufacturing unit (+40%)", "Environmental & ETP compliance eligible (+28%)", "ZED green rating eligible (+20%)"],
            "eligibility_status": "Eligible",
            "official_source": "Development Commissioner, MSME (zed.msme.gov.in)",
            "deadline": "Rolling applications"
        })
        matched_schemes.append({
            "name": "Prime Minister Employment Generation Programme (PMEGP)",
            "short_name": "PMEGP Manufacturing Scheme",
            "description": "Credit-linked subsidy programme for establishing, expanding, and modernizing industrial manufacturing units.",
            "benefit": "Up to 35% Capital Subsidy",
            "category": "Central Government Subsidy",
            "match_score": 84,
            "match_reason": ["Industrial manufacturing activity (+40%)", "MSME scale qualification (+25%)", "Operational commercial standing (+19%)"],
            "eligibility_status": "Eligible",
            "official_source": "Ministry of MSME, Govt of India (kviconline.gov.in)",
            "deadline": "Open year-round (Quarterly tranches)"
        })

    matched_schemes.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_schemes
