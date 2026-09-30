"""
Suite 3: Tenant Isolation Test Suite
Verifies that users cannot view, edit, or execute compliance actions belonging to other users.
"""
import pytest

def test_tenant_cannot_read_other_users_profile(client):
    # User A Signup
    uA = client.post("/api/v1/auth/signup", json={
        "full_name": "User Alpha", "email": "alpha.tenant5@powerhouse.io", "password": "Password123!"
    }).json()
    tokenA = uA["access_token"]

    # User B Signup
    uB = client.post("/api/v1/auth/signup", json={
        "full_name": "User Beta", "email": "beta.tenant5@powerhouse.io", "password": "Password123!"
    }).json()
    tokenB = uB["access_token"]

    # User A creates profile
    pA = client.post("/api/v1/business-profile", json={
        "business_name": "Alpha Textiles",
        "business_type": "Proprietorship",
        "industry": "Textiles",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "business_category": "clothing_textile"
    }, headers={"Authorization": f"Bearer {tokenA}"}).json()
    profile_id_A = pA["id"]

    # User B attempts to access User A's profile directly
    res = client.get(f"/api/v1/business-profile/{profile_id_A}", headers={"Authorization": f"Bearer {tokenB}"})
    assert res.status_code in [403, 404]

def test_tenant_cannot_access_other_users_approvals(client):
    uA = client.post("/api/v1/auth/signup", json={
        "full_name": "User A2", "email": "a2.tenant5@powerhouse.io", "password": "Password123!"
    }).json()["access_token"]
    uB = client.post("/api/v1/auth/signup", json={
        "full_name": "User B2", "email": "b2.tenant5@powerhouse.io", "password": "Password123!"
    }).json()["access_token"]

    pA = client.post("/api/v1/business-profile", json={
        "business_name": "A2 Mills",
        "business_type": "Private Limited",
        "industry": "Manufacturing",
        "company_size": "Small",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "business_category": "manufacturing"
    }, headers={"Authorization": f"Bearer {uA}"}).json()
    prof_id = pA["id"]

    # User B queries User A's approvals
    res = client.get(f"/api/v1/approvals?business_profile_id={prof_id}", headers={"Authorization": f"Bearer {uB}"})
    assert res.status_code == 403

def test_tenant_cannot_approve_other_users_proposals(client):
    uA = client.post("/api/v1/auth/signup", json={
        "full_name": "User A3", "email": "a3.tenant5@powerhouse.io", "password": "Password123!"
    }).json()["access_token"]
    uB = client.post("/api/v1/auth/signup", json={
        "full_name": "User B3", "email": "b3.tenant5@powerhouse.io", "password": "Password123!"
    }).json()["access_token"]

    pA = client.post("/api/v1/business-profile", json={
        "business_name": "A3 Services",
        "business_type": "LLP",
        "industry": "Retail",
        "company_size": "Small",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "business_category": "retail"
    }, headers={"Authorization": f"Bearer {uA}"}).json()
    prof_id = pA["id"]

    # User A creates a proposal
    prop = client.post(f"/api/v1/proposals/{prof_id}", json={
        "title": "File GSTR-1",
        "action_type": "TAX_FILING",
        "urgency": "HIGH",
        "rationale": "Avoid late fee",
        "jurisdiction": "Central GST",
        "regulatory_basis": "CGST Act Sec 37",
        "risk_of_inaction": "Notice trigger"
    }, headers={"Authorization": f"Bearer {uA}"}).json()

    prop_id = prop["id"]

    # User B attempts to confirm User A's proposal
    res = client.post(f"/api/v1/proposals/{prof_id}/{prop_id}/confirm", headers={"Authorization": f"Bearer {uB}"})
    assert res.status_code == 403
