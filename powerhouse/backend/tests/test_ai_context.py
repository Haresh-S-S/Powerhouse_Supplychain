"""
Suite 6: AI Copilot Context & Grounding Test Suite
Verifies that AI copilot prompts and responses are strictly grounded in active business context without cross-category pollution.
"""
import pytest
from app.engine.business_analyzer import analyze_business_profile

def test_ai_context_grounding():
    # Restaurant profile
    profile = {
        "business_name": "Royal Biryani",
        "business_category": "restaurant",
        "company_size": "Small",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "employee_count": 14
    }
    res = analyze_business_profile(profile)
    apprs = res["approvals"]

    # Must contain restaurant engines
    fssai_appr = next((a for a in apprs if "FSSAI" in a["name"]), None)
    assert fssai_appr is not None
    assert fssai_appr["verification_state"] == "VERIFIED SOURCE"

    # Must not contain textile / factory engines
    factory_appr = next((a for a in apprs if "Factory License" in a["name"]), None)
    assert factory_appr is None

def test_zero_hallucination_guarantees():
    profile = {
        "business_name": "Sri Krishna Jewellers",
        "business_category": "jewellery",
        "company_size": "Small",
        "city": "Salem",
        "state": "Tamil Nadu",
        "employee_count": 8
    }
    res = analyze_business_profile(profile)
    for appr in res["approvals"]:
        # Disallow prohibited deceptive claims
        assert "Government Approved" not in appr["name"]
        assert "Legally Guaranteed" not in appr["why_required"]
        # Mandatory verified source tag
        assert appr["verification_state"] in ["VERIFIED SOURCE", "REVIEW REQUIRED"]
