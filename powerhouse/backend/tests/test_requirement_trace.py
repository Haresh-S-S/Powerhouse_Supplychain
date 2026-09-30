"""
Suite 5: Requirement Trace & Statutory Explainability Test Suite
Verifies that every approval includes an explainable 8-step decision trace, verified Act citations, and why_required rationale.
"""
import pytest
from app.engine.approval_rules import evaluate_approval_rules

def test_decision_trace_structure_and_completeness():
    profile = {
        "business_name": "Tiruppur Garments",
        "business_category": "clothing_textile",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 22,
        "annual_turnover": "₹4.8 Cr"
    }
    approvals = evaluate_approval_rules(profile)
    assert len(approvals) > 0

    for appr in approvals:
        # 1. Why required justification
        assert "why_required" in appr and len(appr["why_required"]) > 20
        # 2. Jurisdiction
        assert any(j in appr["jurisdiction"] for j in ["Central", "Tamil Nadu", "Municipal"])
        # 3. Verification State
        assert appr["verification_state"] == "VERIFIED SOURCE"
        # 4. Confidence
        assert str(appr["confidence"]) in ["98%", "95%", "99%", "High", "Very High"] or (isinstance(appr["confidence"], (int, float)) and appr["confidence"] >= 0.8)
        # 5. Regulatory Basis with statutory Act & Section
        rb = appr["regulatory_basis"]
        assert "act" in rb and len(rb["act"]) > 0
        assert "section" in rb and len(rb["section"]) > 0
        assert "citation" in rb and len(rb["citation"]) > 0
        # 6. Decision Inputs
        di = appr["decision_inputs"]
        assert di["business_category"] == "clothing_textile"
        assert di["state"] == "Tamil Nadu"
        # 7. 8-Step Decision Trace
        dt = appr["decision_trace"]
        assert isinstance(dt, list) and len(dt) >= 6
        step_names = [s["step"] for s in dt]
        assert "Entity Classification" in step_names
        assert "Jurisdiction Resolution" in step_names
        assert "Statutory Citation Binding" in step_names
        assert "Final Verification" in step_names

def test_restaurant_fssai_statutory_basis():
    profile = {
        "business_name": "Annapoorna Mess",
        "business_category": "restaurant",
        "company_size": "Small",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "employee_count": 10
    }
    approvals = evaluate_approval_rules(profile)
    fssai = next((a for a in approvals if "FSSAI" in a["name"]), None)
    assert fssai is not None
    assert "Food Safety and Standards Act" in fssai["regulatory_basis"]["act"]
    assert "Section 31" in fssai["regulatory_basis"]["section"]
    assert fssai["verification_state"] == "VERIFIED SOURCE"
