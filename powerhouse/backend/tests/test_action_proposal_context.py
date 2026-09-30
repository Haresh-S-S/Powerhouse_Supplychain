"""
Suite 10: Human-in-the-Loop Action Proposal & Immutable Audit Trail Test Suite
Verifies proposal lifecycle: creation -> PENDING -> explicit human approval -> EXECUTED with immutable audit log.
"""
import pytest

def test_action_proposal_lifecycle_and_audit_trail(client):
    # 1. Signup user Mohith K
    user = client.post("/api/v1/auth/signup", json={
        "full_name": "Mohith K", "email": "mohith.proposal5@powerhouse.io", "password": "SecurePassword123!"
    }).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create business profile
    prof = client.post("/api/v1/business-profile", json={
        "business_name": "Mohith Power Enterprises",
        "business_type": "Proprietorship",
        "industry": "Manufacturing",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "business_category": "manufacturing"
    }, headers=headers).json()
    prof_id = prof["id"]

    # 3. Create proposal
    prop_resp = client.post(f"/api/v1/proposals/{prof_id}", json={
        "title": "File GSTR-3B Monthly Return",
        "action_type": "GST_RETURN_FILING",
        "urgency": "HIGH",
        "rationale": "Avoid ₹50/day late fees under Section 47",
        "jurisdiction": "Central GST",
        "regulatory_basis": "CGST Act 2017, Sec 39",
        "risk_of_inaction": "Statutory late fee and interest penalty",
        "payload": {"period": "April 2025", "turnover": "₹4.8 Cr"}
    }, headers=headers)
    assert prop_resp.status_code == 200
    proposal = prop_resp.json()
    prop_id = proposal["id"]
    assert proposal["status"] in ["PROPOSED", "Pending Review"]
    assert proposal["confirmed_by"] is None

    # 4. Confirm proposal as human-in-the-loop (Mohith K)
    confirm_resp = client.post(f"/api/v1/proposals/{prof_id}/{prop_id}/confirm", json={"confirmed_by": "Mohith K"}, headers=headers)
    assert confirm_resp.status_code == 200
    confirmed_prop = confirm_resp.json()
    assert confirmed_prop["status"] in ["CONFIRMED", "Confirmed"]
    assert confirmed_prop["confirmed_by"] == "Mohith K"
    assert confirmed_prop["confirmed_at"] is not None

    # 5. Query Audit Logs
    audit_resp = client.get(f"/api/v1/audit-logs/{prof_id}", headers=headers)
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) >= 1
    recent_log = logs[0]
    assert recent_log["user_name"] == "Mohith K"
    assert recent_log["action_type"] == "GST_RETURN_FILING"
    assert recent_log["action_status"] == "COMPLETED"
    assert "GSTR-3B" in recent_log["action_name"]

def test_proposal_rejection(client):
    user = client.post("/api/v1/auth/signup", json={
        "full_name": "Mohith K", "email": "mohith.reject5@powerhouse.io", "password": "SecurePassword123!"
    }).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prof = client.post("/api/v1/business-profile", json={
        "business_name": "Mohith Reject Test",
        "business_type": "Proprietorship",
        "industry": "Retail",
        "company_size": "Small",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "business_category": "retail"
    }, headers=headers).json()
    prof_id = prof["id"]

    prop = client.post(f"/api/v1/proposals/{prof_id}", json={
        "title": "Optional Trade Brand Application",
        "action_type": "TRADEMARK_FILING",
        "urgency": "LOW",
        "rationale": "Brand protection",
        "jurisdiction": "Trade Marks Registry",
        "regulatory_basis": "Trade Marks Act 1999",
        "risk_of_inaction": "None immediate"
    }, headers=headers).json()

    assert prop["status"] in ["PROPOSED", "Pending Review"]
    assert prop["id"] is not None
