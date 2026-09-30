"""
Suite 4: Business Switching Test Suite
Verifies that switching active business categories completely recalculates compliance mandates with zero residual state.
"""
import pytest
from app.engine.business_analyzer import analyze_business_profile

def test_business_category_switch_resets_workspace():
    # Phase 1: Textile Profile
    textile_profile = {
        "business_name": "Vanguard Tex",
        "business_category": "clothing_textile",
        "industry": "Clothing & Textile",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 25,
        "environmental_impact": "Moderate"
    }
    tex_analysis = analyze_business_profile(textile_profile)
    tex_approvals = {a["name"] for a in tex_analysis["approvals"]}
    assert "Shops & Establishments Registration" in tex_approvals
    assert "FSSAI Registration / Licence" not in tex_approvals

    # Phase 2: Switch to Restaurant Profile
    restaurant_profile = {
        "business_name": "Vanguard Dining",
        "business_category": "restaurant",
        "industry": "Food Service",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 12,
        "environmental_impact": "Low"
    }
    rest_analysis = analyze_business_profile(restaurant_profile)
    rest_approvals = {a["name"] for a in rest_analysis["approvals"]}

    # Zero residue: Food license must exist, textile committee must be absent
    assert "FSSAI Registration / Licence" in rest_approvals
    assert "Textile Committee / Ministry of Textiles Compliance" not in rest_approvals
    assert "State Pollution Control Board Consent (Air & Water / ETP)" not in rest_approvals

def test_clean_workspace_initialization_on_new_profile(client):
    user = client.post("/api/v1/auth/signup", json={
        "full_name": "Mohith K", "email": "switch.tester5@powerhouse.io", "password": "Password123!"
    }).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Profile 1: Jewellery
    p1 = client.post("/api/v1/business-profile", json={
        "business_name": "Mohith Gems",
        "business_type": "Proprietorship",
        "industry": "Jewellery",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "business_category": "jewellery"
    }, headers=headers).json()

    # Profile 2: Restaurant
    p2 = client.post("/api/v1/business-profile", json={
        "business_name": "Mohith Cafe",
        "business_type": "Proprietorship",
        "industry": "Food Service",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "business_category": "restaurant"
    }, headers=headers).json()

    # Run analysis on p1
    client.post(f"/api/v1/business-analysis/{p1['id']}", headers=headers)
    apprs_1 = client.get(f"/api/v1/approvals?business_profile_id={p1['id']}", headers=headers).json()
    assert any("BIS Hallmarking" in a["name"] for a in apprs_1)
    assert not any("FSSAI" in a["name"] for a in apprs_1)

    # Run analysis on p2
    client.post(f"/api/v1/business-analysis/{p2['id']}", headers=headers)
    apprs_2 = client.get(f"/api/v1/approvals?business_profile_id={p2['id']}", headers=headers).json()
    assert any("FSSAI" in a["name"] for a in apprs_2)
    assert not any("BIS Hallmarking" in a["name"] for a in apprs_2)
