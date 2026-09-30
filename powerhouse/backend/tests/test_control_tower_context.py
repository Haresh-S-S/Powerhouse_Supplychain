"""
Suite 9: Control Tower Priorities & Explainable Prioritization Test Suite
Verifies that top risks include weighted scoring factor breakdowns and statutory consequences.
"""
import pytest
from app.engine.business_analyzer import analyze_business_profile

def test_control_tower_weighted_priorities():
    profile = {
        "business_name": "Tiruppur Modern Weaving",
        "business_category": "clothing_textile",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 25
    }
    res = analyze_business_profile(profile)
    priorities = res["control_tower_priorities"]
    assert len(priorities) >= 3

    for p in priorities:
        assert "what" in p
        assert "priority_score" in p and 0 <= p["priority_score"] <= 100
        assert "factors" in p
        factors = p["factors"]
        assert len(factors) > 0
        total_factors = sum(factors.values())
        assert total_factors == p["priority_score"]

        # Explainable rationale and recommendations
        assert "why" in p and len(p["why"]) > 10
        assert "explanation" in p and len(p["explanation"]) > 10
        assert "recommended_action" in p and len(p["recommended_action"]) > 10

def test_compliance_health_score_breakdown():
    profile = {
        "business_name": "Tiruppur Modern Weaving",
        "business_category": "clothing_textile",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 25
    }
    res = analyze_business_profile(profile)
    breakdown = res["compliance_health_breakdown"]
    assert 50 <= breakdown["score"] <= 100
    assert breakdown["total_possible"] == 100
    assert "licences" in breakdown
    assert "documents" in breakdown
    assert "tasks" in breakdown
    assert "deductions" in breakdown
    assert breakdown["formula"] is not None
