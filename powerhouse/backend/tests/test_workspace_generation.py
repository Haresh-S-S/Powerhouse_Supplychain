import pytest
from app.engine.approval_rules import evaluate_approval_rules, resolve_business_category
from app.engine.compliance_rules import generate_compliance_tasks
from app.engine.document_rules import generate_document_requirements
from app.engine.scheme_rules import match_government_schemes
from app.engine.business_analyzer import analyze_business_profile, calculate_risk_level


# =========================================================================
# 1. MULTI-CATEGORY COMPLIANCE WORKSPACE GENERATION TEST
# =========================================================================
@pytest.mark.parametrize("category,expected_approval,expected_scheme", [
    ("restaurant", "FSSAI Registration / Licence", "PMFME Food Processing Subsidy"),
    ("clothing_textile", "Shops & Establishments Registration", "ATUFS Scheme"),
    ("jewellery", "BIS Hallmarking Registration", "Gold Monetisation Scheme"),
    ("retail", "Legal Metrology (Weights & Measures) Packaged Commodities Registration", "CGTMSE Retail Credit Guarantee"),
    ("manufacturing", "Factory License", "PLI Manufacturing Scheme"),
])
def test_multi_category_generation(category, expected_approval, expected_scheme):
    profile = {
        "business_name": f"Test {category.title()} Enterprise",
        "business_category": category,
        "industry": category,
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 15,
        "manufacturing_activity": (category == "manufacturing"),
        "environmental_impact": "Moderate" if category in ["manufacturing", "clothing_textile"] else "Low",
        "has_gst": True,
        "has_msme_registration": True
    }

    result = analyze_business_profile(profile)
    assert result["is_valid"] is True
    assert result["summary"]["total_approvals"] > 0
    assert result["summary"]["total_compliance_tasks"] > 0
    assert result["summary"]["total_required_documents"] > 0
    assert result["summary"]["total_recommended_schemes"] > 0

    approval_names = [a["name"] for a in result["approvals"]]
    scheme_names = [s["short_name"] for s in result["recommended_schemes"]]

    assert expected_approval in approval_names
    assert expected_scheme in scheme_names


# =========================================================================
# 2. CROSS-CATEGORY LEAKAGE PREVENTION TEST
# =========================================================================
def test_cross_category_zero_leakage():
    # 2.1 Textile Profile Isolation
    textile_profile = {
        "business_name": "Tiruppur Weaving Mills",
        "business_category": "clothing_textile",
        "industry": "Clothing & Textile",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 25,
        "environmental_impact": "Moderate"
    }
    textile_result = analyze_business_profile(textile_profile)
    textile_approvals = [a["name"] for a in textile_result["approvals"]]
    textile_schemes = [s["short_name"] for s in textile_result["recommended_schemes"]]

    # MUST NOT leak food or jewellery rules into textile
    assert "FSSAI Registration / Licence" not in textile_approvals
    assert "Eating House Licence" not in textile_approvals
    assert "Fire Safety NOC (Kitchen / Dining)" not in textile_approvals
    assert "BIS Hallmarking Registration" not in textile_approvals
    assert "PMFME Food Processing Subsidy" not in textile_schemes

    # 2.2 Restaurant Profile Isolation
    restaurant_profile = {
        "business_name": "The Spice Kitchen",
        "business_category": "restaurant",
        "industry": "Food Service",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "employee_count": 12,
        "environmental_impact": "Low"
    }
    restaurant_result = analyze_business_profile(restaurant_profile)
    restaurant_approvals = [a["name"] for a in restaurant_result["approvals"]]
    restaurant_schemes = [s["short_name"] for s in restaurant_result["recommended_schemes"]]

    # MUST NOT leak textile, factory or jewellery rules into restaurant
    assert "State Pollution Control Board Consent (Air & Water / ETP)" not in restaurant_approvals
    assert "Textile Committee / Ministry of Textiles Compliance" not in restaurant_approvals
    assert "Factory License" not in restaurant_approvals
    assert "BIS Hallmarking Registration" not in restaurant_approvals
    assert "ATUFS Scheme" not in restaurant_schemes
    assert "PLI for Textiles" not in restaurant_schemes

    # 2.3 Jewellery Profile Isolation
    jewellery_profile = {
        "business_name": "Sri Lakshmi Jewellers",
        "business_category": "jewellery",
        "industry": "Jewellery Retail",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "employee_count": 15,
        "environmental_impact": "Low"
    }
    jewellery_result = analyze_business_profile(jewellery_profile)
    jewellery_approvals = [a["name"] for a in jewellery_result["approvals"]]
    jewellery_schemes = [s["short_name"] for s in jewellery_result["recommended_schemes"]]

    assert "BIS Hallmarking Registration" in jewellery_approvals
    assert "PMLA FIU-IND Reporting Registration" in jewellery_approvals
    assert "FSSAI Registration / Licence" not in jewellery_approvals
    assert "Factory License" not in jewellery_approvals
    assert "ATUFS Scheme" not in jewellery_schemes

    # 2.4 Retail Profile Isolation
    retail_profile = {
        "business_name": "Daily Fresh Mart",
        "business_category": "retail",
        "industry": "Retail Trade",
        "city": "Madurai",
        "state": "Tamil Nadu",
        "employee_count": 8,
        "environmental_impact": "Low"
    }
    retail_result = analyze_business_profile(retail_profile)
    retail_approvals = [a["name"] for a in retail_result["approvals"]]

    assert "Legal Metrology (Weights & Measures) Packaged Commodities Registration" in retail_approvals
    assert "Factory License" not in retail_approvals
    assert "State Pollution Control Board Consent (Air & Water / ETP)" not in retail_approvals

    # 2.5 Manufacturing Profile Isolation
    mfg_profile = {
        "business_name": "Apex Precision Forge",
        "business_category": "manufacturing",
        "industry": "Manufacturing",
        "manufacturing_activity": True,
        "city": "Chennai",
        "state": "Tamil Nadu",
        "employee_count": 50,
        "environmental_impact": "High"
    }
    mfg_result = analyze_business_profile(mfg_profile)
    mfg_approvals = [a["name"] for a in mfg_result["approvals"]]

    assert "Factory License" in mfg_approvals
    assert "Pollution Control NOC (CTO)" in mfg_approvals
    assert "FSSAI Registration / Licence" not in mfg_approvals
    assert "Eating House Licence" not in mfg_approvals
    assert "BIS Hallmarking Registration" not in mfg_approvals


# =========================================================================
# 3. AI ADVISOR CONTEXT GROUNDING & RISK LEVEL TEST
# =========================================================================
def test_ai_advisor_context_and_risk_grounding():
    # Restaurant Risk should be Medium, Insight should mention FSSAI
    res_prof = {"business_category": "restaurant", "city": "Chennai", "state": "Tamil Nadu"}
    assert calculate_risk_level(res_prof) == "Medium"
    res_res = analyze_business_profile(res_prof)
    res_insights = [i["message"] for i in res_res["insights"]]
    assert any("FSSAI" in msg for msg in res_insights)
    assert not any("effluent" in msg.lower() for msg in res_insights)

    # Jewellery Risk should be Medium, Insight should mention BIS/HUID
    jwl_prof = {"business_category": "jewellery", "city": "Coimbatore", "state": "Tamil Nadu"}
    assert calculate_risk_level(jwl_prof) == "Medium"
    jwl_res = analyze_business_profile(jwl_prof)
    jwl_insights = [i["message"] for i in jwl_res["insights"]]
    assert any("HUID" in msg or "PMLA" in msg for msg in jwl_insights)
    assert not any("food safety" in msg.lower() for msg in jwl_insights)

    # Retail Risk should be Low
    ret_prof = {"business_category": "retail", "city": "Madurai", "state": "Tamil Nadu"}
    assert calculate_risk_level(ret_prof) == "Low"


# =========================================================================
# 4. CANONICAL PROFILE PERSISTENCE TEST
# =========================================================================
def test_canonical_profile_persistence_in_analysis(client):
    # Register user
    user_payload = {
        "full_name": "Mohith K",
        "email": "mohith.test@powerhouse.io",
        "password": "SecurePassword123!",
        "phone_number": "+91 98765 43210"
    }
    signup_resp = client.post("/api/v1/auth/signup", json=user_payload)
    assert signup_resp.status_code == 201
    token = signup_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create profile with specific city Tiruppur
    prof_payload = {
        "business_name": "Tiruppur Quality Garments",
        "business_type": "Sole Proprietorship",
        "industry": "Clothing & Textile",
        "sector": "Apparel Retail",
        "company_size": "Small Enterprise",
        "employee_count": 12,
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "country": "India",
        "business_category": "clothing_textile",
        "has_gst": False,
        "has_msme_registration": False,
        "onboarding_completed": True
    }
    create_resp = client.post("/api/v1/business-profile", json=prof_payload, headers=headers)
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["id"]

    # Verify no fabricated legal IDs were generated
    assert create_resp.json()["gstin"] is None
    assert create_resp.json()["pan"] is None
    assert create_resp.json()["udyam_number"] is None

    # Run analysis
    analysis_resp = client.post(f"/api/v1/business-analysis/{profile_id}", headers=headers)
    assert analysis_resp.status_code == 201
    res_data = analysis_resp.json()["analysis_result"]

    # Assert city is preserved
    assert res_data["business_summary"]["city"] == "Tiruppur"
    assert res_data["business_summary"]["state"] == "Tamil Nadu"


# =========================================================================
# 5. TENANT ISOLATION TEST (HTTP 403 FORBIDDEN)
# =========================================================================
def test_tenant_isolation_returns_403(client):
    # Create User A
    user_a = {
        "full_name": "User Alpha",
        "email": "alpha.tenant@powerhouse.io",
        "password": "PasswordAlpha123!",
        "phone_number": "+91 91111 11111"
    }
    resp_a = client.post("/api/v1/auth/signup", json=user_a)
    assert resp_a.status_code == 201
    token_a = resp_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Create User B
    user_b = {
        "full_name": "User Beta",
        "email": "beta.tenant@powerhouse.io",
        "password": "PasswordBeta123!",
        "phone_number": "+91 92222 22222"
    }
    resp_b = client.post("/api/v1/auth/signup", json=user_b)
    assert resp_b.status_code == 201
    token_b = resp_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a business profile
    prof_a_payload = {
        "business_name": "Alpha Restricted Showroom",
        "business_type": "Proprietorship",
        "industry": "Jewellery",
        "company_size": "Small",
        "employee_count": 10,
        "city": "Chennai",
        "state": "Tamil Nadu",
        "business_category": "jewellery"
    }
    create_prof_a = client.post("/api/v1/business-profile", json=prof_a_payload, headers=headers_a)
    assert create_prof_a.status_code == 201
    profile_a_id = create_prof_a.json()["id"]

    # Run analysis as User A
    analysis_a = client.post(f"/api/v1/business-analysis/{profile_a_id}", headers=headers_a)
    assert analysis_a.status_code == 201

    # User B attempts to access User A's profile -> MUST RETURN 403 FORBIDDEN
    leak_profile = client.get(f"/api/v1/business-profile/{profile_a_id}", headers=headers_b)
    assert leak_profile.status_code == 403
    assert "Access forbidden" in leak_profile.json()["detail"]

    # User B attempts to access User A's latest analysis -> MUST RETURN 403 FORBIDDEN
    leak_analysis = client.get(f"/api/v1/business-analysis/{profile_a_id}/latest", headers=headers_b)
    assert leak_analysis.status_code == 403
    assert "Access forbidden" in leak_analysis.json()["detail"]

    # User B attempts to trigger analysis on User A's profile -> MUST RETURN 403 FORBIDDEN
    leak_trigger = client.post(f"/api/v1/business-analysis/{profile_a_id}", headers=headers_b)
    assert leak_trigger.status_code == 403

    # User B attempts to list approvals for User A's profile -> MUST RETURN 403 FORBIDDEN
    leak_approvals = client.get(f"/api/v1/approvals?business_profile_id={profile_a_id}", headers=headers_b)
    assert leak_approvals.status_code == 403


# =========================================================================
# 6. DUPLICATE PREVENTION TEST
# =========================================================================
def test_duplicate_prevention_on_reanalysis(client):
    # Create User and Profile
    user_payload = {
        "full_name": "Mohith K",
        "email": "dup.prevention@powerhouse.io",
        "password": "SecurePassword123!",
        "phone_number": "+91 93333 33333"
    }
    signup_resp = client.post("/api/v1/auth/signup", json=user_payload)
    assert signup_resp.status_code == 201
    token = signup_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prof_payload = {
        "business_name": "Chennai Bistro",
        "business_type": "Partnership",
        "industry": "Food Service",
        "company_size": "Micro",
        "employee_count": 8,
        "city": "Chennai",
        "state": "Tamil Nadu",
        "business_category": "restaurant"
    }
    create_resp = client.post("/api/v1/business-profile", json=prof_payload, headers=headers)
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["id"]

    # Run 1st analysis
    client.post(f"/api/v1/business-analysis/{profile_id}", headers=headers)
    approvals_1 = client.get(f"/api/v1/approvals?business_profile_id={profile_id}", headers=headers).json()
    tasks_1 = client.get(f"/api/v1/tasks?business_profile_id={profile_id}", headers=headers).json()
    docs_1 = client.get(f"/api/v1/documents?business_profile_id={profile_id}", headers=headers).json()

    count_appr_1 = len(approvals_1)
    count_tasks_1 = len(tasks_1)
    count_docs_1 = len(docs_1)

    assert count_appr_1 > 0
    assert count_tasks_1 > 0

    # Run 2nd analysis on same profile
    client.post(f"/api/v1/business-analysis/{profile_id}", headers=headers)
    approvals_2 = client.get(f"/api/v1/approvals?business_profile_id={profile_id}", headers=headers).json()
    tasks_2 = client.get(f"/api/v1/tasks?business_profile_id={profile_id}", headers=headers).json()
    docs_2 = client.get(f"/api/v1/documents?business_profile_id={profile_id}", headers=headers).json()

    # Verify counts are identical: zero duplicates created
    assert len(approvals_2) == count_appr_1
    assert len(tasks_2) == count_tasks_1
    assert len(docs_2) == count_docs_1


# =========================================================================
# 7. UNKNOWN BUSINESS CLASSIFICATION TEST
# =========================================================================
def test_unknown_business_classification_confidence():
    """Verify vague input does not arbitrarily categorize into a random business."""
    vague_input = "I want to start a new business"
    category = resolve_business_category({"business_category": "", "industry": vague_input, "sector": ""})
    # Must fallback safely or resolve without generating factory licenses
    assert category != "manufacturing"
