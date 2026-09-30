from app.engine.approval_rules import evaluate_approval_rules
from app.engine.compliance_rules import generate_compliance_tasks
from app.engine.scheme_rules import match_government_schemes
from app.engine.business_analyzer import analyze_business_profile, calculate_risk_level


def test_manufacturing_triggers_factory_license():
    profile = {
        "industry": "Manufacturing",
        "manufacturing_activity": True,
        "employee_count": 15,
        "state": "Maharashtra",
        "environmental_impact": "Moderate"
    }
    approvals = evaluate_approval_rules(profile)
    approval_names = [a["name"] for a in approvals]
    assert "Factory License" in approval_names
    assert "Pollution Control NOC (CTO)" in approval_names


def test_employee_threshold_pf_rules():
    # Less than 20 employees -> No PF
    profile_small = {
        "industry": "Services",
        "manufacturing_activity": False,
        "employee_count": 8,
        "environmental_impact": "Low"
    }
    approvals_small = evaluate_approval_rules(profile_small)
    names_small = [a["name"] for a in approvals_small]
    assert "Employees PF Registration" not in names_small
    assert "Employees ESI Registration" not in names_small

    # >= 20 employees -> PF and ESI triggered
    profile_large = {
        "industry": "Services",
        "manufacturing_activity": False,
        "employee_count": 25,
        "environmental_impact": "Low"
    }
    approvals_large = evaluate_approval_rules(profile_large)
    names_large = [a["name"] for a in approvals_large]
    assert "Employees PF Registration" in names_large
    assert "Employees ESI Registration" in names_large


def test_import_activities_triggers_iec():
    profile = {
        "industry": "Manufacturing",
        "import_activities": True,
        "export_activities": False,
        "employee_count": 10
    }
    approvals = evaluate_approval_rules(profile)
    names = [a["name"] for a in approvals]
    assert "Import Export Code (IEC)" in names


def test_scheme_matching_deterministic_scoring():
    profile = {
        "industry": "Manufacturing",
        "manufacturing_activity": True,
        "has_msme_registration": True,
        "company_size": "Medium Enterprise",
        "state": "Maharashtra",
        "city": "Mumbai",
        "operating_status": "Active",
        "import_activities": True
    }
    schemes = match_government_schemes(profile)
    assert len(schemes) >= 3
    # First scheme has highest score
    assert schemes[0]["match_score"] >= 80
    assert "benefit" in schemes[0]


def test_complete_business_analyzer_output():
    profile = {
        "business_name": "Powerhouse Tech",
        "business_type": "Private Limited Company",
        "industry": "Manufacturing",
        "sector": "Industrial Valves",
        "employee_count": 85,
        "company_size": "Medium Enterprise",
        "state": "Maharashtra",
        "city": "Mumbai",
        "manufacturing_activity": True,
        "import_activities": True,
        "environmental_impact": "Moderate",
        "has_gst": True,
        "has_msme_registration": True,
        "operating_status": "Active"
    }
    result = analyze_business_profile(profile)
    assert result["is_valid"] is True
    assert result["risk_level"] in ["Low", "Medium", "High"]
    assert len(result["approvals"]) >= 8
    assert len(result["compliance_tasks"]) >= 5
    assert len(result["insights"]) >= 3
    assert "disclaimer" in result
