"""
Suite 7: Document Intelligence & Evidence Mapping Test Suite
Verifies that document requirements are dynamically mapped to specific statutory approvals with evidence statuses and extracted intelligence.
"""
import pytest
from app.engine.business_analyzer import analyze_business_profile

def test_document_evidence_mapping():
    profile = {
        "business_name": "Apex Dyeing & Knitting",
        "business_category": "clothing_textile",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 28
    }
    res = analyze_business_profile(profile)
    docs = res["required_documents"]
    assert len(docs) > 0

    for doc in docs:
        assert "evidence_status" in doc
        assert doc["evidence_status"] in ["Supported", "Missing", "Needs Review"]
        assert "mapped_approval" in doc and len(doc["mapped_approval"]) > 0
        assert "extracted_intelligence" in doc
        intel = doc["extracted_intelligence"]
        assert "issuing_authority" in intel
        assert "confidence_score" in intel
        assert intel["confidence_score"] >= 0.80

def test_restaurant_evidence_mapping():
    profile = {
        "business_name": "Madurai Food Hub",
        "business_category": "restaurant",
        "company_size": "Small",
        "city": "Madurai",
        "state": "Tamil Nadu"
    }
    res = analyze_business_profile(profile)
    docs = res["required_documents"]
    fsms = next((d for d in docs if "FSMS" in d["name"] or "Food Safety" in d["name"]), None)
    assert fsms is not None
    assert any(w in fsms["mapped_approval"] for w in ["FSSAI", "Food", "Safety", "Licence"])
