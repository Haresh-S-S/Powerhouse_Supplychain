from datetime import datetime, timezone
from typing import Dict, Any
from app.engine.approval_rules import evaluate_approval_rules, resolve_business_category
from app.engine.compliance_rules import generate_compliance_tasks
from app.engine.document_rules import generate_document_requirements
from app.engine.scheme_rules import match_government_schemes


def calculate_risk_level(profile: Any) -> str:
    def get_val(key, default=None):
        if isinstance(profile, dict):
            return profile.get(key, default)
        return getattr(profile, key, default)

    category = resolve_business_category(profile)
    env_impact = get_val("environmental_impact", "Low")
    employees = get_val("employee_count", 0) or 0

    if category == "retail":
        return "Low"
    elif category == "clothing_textile":
        if env_impact in ["Moderate", "High", "Critical (Red Category)"]:
            return "Medium"
        return "Low"
    elif category == "restaurant":
        return "Medium"
    elif category == "jewellery":
        return "Medium"
    else:
        # Manufacturing / Factory
        points = 0
        if env_impact == "Critical (Red Category)":
            points += 4
        elif env_impact == "High":
            points += 3
        elif env_impact == "Moderate":
            points += 2
        else:
            points += 1

        if employees >= 100:
            points += 3
        elif employees >= 20:
            points += 2
        elif employees >= 10:
            points += 1

        if points >= 6:
            return "High"
        elif points >= 4:
            return "Medium"
        return "Low"


def analyze_business_profile(profile: Any) -> Dict[str, Any]:
    def get_val(key, default=None):
        if isinstance(profile, dict):
            return profile.get(key, default)
        return getattr(profile, key, default)

    category = resolve_business_category(profile)
    approvals = evaluate_approval_rules(profile)
    compliance_tasks = generate_compliance_tasks(profile, approvals)
    required_documents = generate_document_requirements(profile, approvals)
    recommended_schemes = match_government_schemes(profile)
    risk_level = calculate_risk_level(profile)

    high_priority_approvals = sum(1 for a in approvals if a.get("priority") == "High")
    completed_approvals = sum(1 for a in approvals if a.get("status") == "Completed")
    in_progress_approvals = sum(1 for a in approvals if a.get("status") == "In Progress")
    pending_approvals = sum(1 for a in approvals if a.get("status") == "Pending")

    upcoming_tasks = sum(1 for t in compliance_tasks if t.get("status") == "Upcoming")

    # Dynamic Category-Specific Insights
    insights = []
    category_label = category.replace("_", " ").title()
    insights.append({
        "id": "insight-approvals",
        "type": "approvals",
        "title": "Statutory Approval Requirements",
        "message": f"Identified {len(approvals)} applicable regulatory approvals, with {high_priority_approvals} classified as High Priority for {category_label} operations.",
        "severity": "info"
    })

    if category == "restaurant":
        insights.append({
            "id": "insight-food-safety",
            "type": "food-safety",
            "title": "FSSAI & Public Health Mandate",
            "message": "FSSAI registration and municipal Health Trade Licence are foundational statutory prerequisites for commercial dining operations.",
            "severity": "warning"
        })
    elif category == "jewellery":
        insights.append({
            "id": "insight-jewellery-pmla",
            "type": "certification",
            "title": "BIS Hallmarking & FIU-IND Reporting",
            "message": "Mandatory 6-digit HUID hallmarking and PMLA cash transaction reporting (> ₹2 Lakhs) are actively enforced for precious ornaments.",
            "severity": "warning"
        })
    elif category == "retail":
        insights.append({
            "id": "insight-retail-standards",
            "type": "standards",
            "title": "Legal Metrology & Shop Registration",
            "message": "Commercial weighing scales require annual stamping verification under the Legal Metrology Act.",
            "severity": "info"
        })
    else:
        env_impact = get_val("environmental_impact", "Moderate")
        if env_impact in ["Moderate", "High", "Critical (Red Category)"]:
            insights.append({
                "id": "insight-env",
                "type": "environmental",
                "title": "Environmental & Pollution Standing",
                "message": f"Your enterprise is subject to {env_impact} environmental oversight. Maintain stack emission logs and ETP renewal filings on schedule.",
                "severity": "warning"
            })

    employees = get_val("employee_count", 0) or 0
    if employees >= 10:
        insights.append({
            "id": "insight-labour",
            "type": "labour",
            "title": "Workforce & Labour Compliance",
            "message": f"With {employees} employees, statutory ESI medical coverage and mandatory monthly EPFO electronic returns are actively enforced.",
            "severity": "info"
        })

    if recommended_schemes:
        top_scheme = recommended_schemes[0]
        insights.append({
            "id": "insight-schemes",
            "type": "scheme",
            "title": "Government Scheme Opportunity",
            "message": f"{len(recommended_schemes)} schemes match your business profile. Top recommendation: \"{top_scheme.get('short_name')}\" ({top_scheme.get('match_score')}% match) offering {top_scheme.get('benefit')}.",
            "severity": "success"
        })

    insights.append({
        "id": "insight-action",
        "type": "action",
        "title": "Upcoming Critical Deadlines",
        "message": f"You have {upcoming_tasks} compliance tasks due in the upcoming cycle. Review statutory documentation to avoid regulatory penalties.",
        "severity": "warning"
    })

    # 1. Explainable Compliance Health Score Calculation
    total_app = len(approvals) or 1
    effective_app_ratio = (completed_approvals + 0.6 * in_progress_approvals) / total_app
    licence_pts = round(effective_app_ratio * 35)

    total_docs = len(required_documents) or 1
    verified_docs = sum(1 for d in required_documents if d.get("status") == "Verified")
    doc_pts = round((verified_docs / total_docs) * 30)

    total_tsk = len(compliance_tasks) or 1
    completed_tsk = sum(1 for t in compliance_tasks if t.get("status") == "Completed")
    task_pts = round((completed_tsk / total_tsk) * 25)

    overdue_tasks = sum(1 for t in compliance_tasks if t.get("status") == "Overdue")
    deadline_risk_penalty = min(10, overdue_tasks * 4)
    workflow_blocker_penalty = 2 if pending_approvals > 2 else 0

    base_score = 10
    computed_score = base_score + licence_pts + doc_pts + task_pts - deadline_risk_penalty - workflow_blocker_penalty
    computed_score = max(50, min(95, computed_score))

    compliance_health_breakdown = {
        "score": computed_score,
        "total_possible": 100,
        "health_tier": "Excellent" if computed_score >= 85 else ("Good" if computed_score >= 70 else "Action Required"),
        "licences": {
            "completed": completed_approvals,
            "in_progress": in_progress_approvals,
            "total": len(approvals),
            "contribution": licence_pts,
            "max_points": 35,
            "description": f"{completed_approvals} active and {in_progress_approvals} in-progress approvals"
        },
        "documents": {
            "verified": verified_docs,
            "total": len(required_documents),
            "contribution": doc_pts,
            "max_points": 30,
            "description": f"{verified_docs} verified statutory documents out of {len(required_documents)} required"
        },
        "tasks": {
            "completed": completed_tsk,
            "total": len(compliance_tasks),
            "contribution": task_pts,
            "max_points": 25,
            "description": f"{completed_tsk} tasks completed out of {len(compliance_tasks)} total compliance duties"
        },
        "deductions": {
            "deadline_risk": -deadline_risk_penalty,
            "workflow_blockers": -workflow_blocker_penalty,
            "critical_conflicts": 0,
            "description": f"-{deadline_risk_penalty} pts from {overdue_tasks} overdue task(s)" if overdue_tasks > 0 else "No active statutory penalties applied"
        },
        "base_weight": base_score,
        "formula": f"Base ({base_score}) + Licences ({licence_pts}/35) + Documents ({doc_pts}/30) + Tasks ({task_pts}/25) - Deductions ({deadline_risk_penalty + workflow_blocker_penalty}) = {computed_score}/100"
    }

    # 2. Control Tower Top Priorities with Explainable Factor Weights
    control_tower_priorities = []
    if category == "restaurant":
        control_tower_priorities = [
            {
                "id": "ct-res-1",
                "what": "FSSAI Annual FoSCoS Return Filing",
                "why": "Statutory food safety annual return deadline under FSS Regulations. Late filing incurs ₹100/day penalty.",
                "severity": "Critical",
                "deadline": "Overdue by 3 days",
                "priority_score": 92,
                "factors": {"overdue_penalty": 50, "statutory_deadline": 25, "licence_risk": 17},
                "explanation": "Overdue FSSAI annual return directly exposes food business operator to inspection notice under Section 31.",
                "recommended_action": "File pending FoSCoS annual return and upload acknowledgement.",
                "action_url": "compliance-tasks"
            },
            {
                "id": "ct-res-2",
                "what": "Commercial Kitchen Exhaust Degreasing & Hood Audit",
                "why": "Grease accumulation in exhaust duct creates severe commercial kitchen fire hazard under NBC 2016.",
                "severity": "High",
                "deadline": "Due in 2 days",
                "priority_score": 85,
                "factors": {"life_safety": 45, "inspection_mandate": 25, "operational_risk": 15},
                "explanation": "State Fire & Emergency Services requires certified wet-chemical hood suppression log.",
                "recommended_action": "Complete quarterly hood degreasing and upload service vendor certificate.",
                "action_url": "approvals"
            },
            {
                "id": "ct-res-3",
                "what": "Water Potability & Chemical Lab Test",
                "why": "Drinking water potability certificate mandatory for Municipal Health Trade Licence validity.",
                "severity": "Medium",
                "deadline": "Due in 15 days",
                "priority_score": 75,
                "factors": {"health_code": 40, "routine_renewal": 25, "water_safety": 10},
                "explanation": "Semi-annual bacteriological water testing required by local Municipal Health Officer.",
                "recommended_action": "Collect tap water sample and dispatch to certified NABL lab.",
                "action_url": "documents"
            }
        ]
    elif category == "jewellery":
        control_tower_priorities = [
            {
                "id": "ct-jwl-1",
                "what": "PMLA Monthly Cash Transaction Reporting (CTR)",
                "why": "Mandatory FIU-IND cash reporting for transactions exceeding ₹2 Lakhs under PMLA Section 12.",
                "severity": "Critical",
                "deadline": "Due in 5 days",
                "priority_score": 90,
                "factors": {"aml_compliance": 50, "statutory_reporting": 25, "fiu_enforcement": 15},
                "explanation": "Failure to file monthly CTR exposes reporting entities to penalty proceedings under Section 13.",
                "recommended_action": "Reconcile cash ledger and generate CTR electronic XML report on FINnet 2.0.",
                "action_url": "compliance-tasks"
            },
            {
                "id": "ct-jwl-2",
                "what": "BIS Hallmarking 6-Digit HUID Tag Reconciliation",
                "why": "All gold jewellery pieces must carry laser-etched HUID mapped to BIS portal registry.",
                "severity": "High",
                "deadline": "Due in 7 days",
                "priority_score": 84,
                "factors": {"consumer_protection": 44, "portal_sync": 25, "bis_audit": 15},
                "explanation": "Unreconciled showroom inventory is liable to seizure during random BIS market surveillance.",
                "recommended_action": "Scan and match physical RFID/HUID tags against BIS inventory records.",
                "action_url": "approvals"
            }
        ]
    else:
        # Clothing & Textile / Manufacturing / Retail default
        control_tower_priorities = [
            {
                "id": "ct-tex-1",
                "what": "GST Return Filing (GSTR-3B)",
                "why": "Statutory monthly indirect tax return overdue by 3 days. Late fees accrue daily under Section 47.",
                "severity": "Critical",
                "deadline": "Overdue 3 days",
                "priority_score": 92,
                "factors": {"overdue_status": 50, "statutory_deadline": 25, "tax_penalty": 17},
                "explanation": "Overdue return triggers portal blocking and automated interest levy under Section 50 of CGST Act.",
                "recommended_action": "Submit pending GSTR-3B tax return and remit net liability challan.",
                "action_url": "compliance-tasks"
            },
            {
                "id": "ct-tex-2",
                "what": "Fire Safety Certificate Renewal Audit",
                "why": f"Annual life safety audit required by {get_val('state', 'Tamil Nadu')} Fire & Rescue Services.",
                "severity": "High",
                "deadline": "Due in 2 days (15 May)",
                "priority_score": 85,
                "factors": {"upcoming_deadline": 45, "inspection_audit": 25, "life_safety": 15},
                "explanation": "Expiring fire safety clearance risks temporary suspension of commercial municipal trade endorsement.",
                "recommended_action": "Schedule on-site hydrant pressure inspection with District Fire Officer.",
                "action_url": "approvals"
            },
            {
                "id": "ct-tex-3",
                "what": "State PCB ETP Treated Water Quality Test",
                "why": "Mandatory quarterly trade effluent analysis report under Water Act Section 25.",
                "severity": "Medium",
                "deadline": "Due in 14 days",
                "priority_score": 76,
                "factors": {"environmental_oversight": 40, "renewal_prerequisite": 22, "water_norm": 14},
                "explanation": "ETP discharge parameters (COD, BOD, TDS) must be submitted to State PCB OCMMS portal.",
                "recommended_action": "Upload NABL lab test report for treated effluent discharge.",
                "action_url": "documents"
            },
            {
                "id": "ct-tex-4",
                "what": "Professional Tax Payment",
                "why": "Semi-annual employer deduction remittance to Municipal Corporation Revenue Section.",
                "severity": "Medium",
                "deadline": "Due in 5 days (18 May)",
                "priority_score": 70,
                "factors": {"local_tax": 40, "statutory_due": 20, "employer_duty": 10},
                "explanation": "Timely payment prevents municipal warrant notices and statutory interest penalties.",
                "recommended_action": "Remit professional tax payment on municipal revenue portal.",
                "action_url": "compliance-tasks"
            }
        ]

    # 3. Workspace Readiness & Next Best Action
    workspace_readiness = {
        "profile_status": "Completed",
        "requirements_count": len(approvals),
        "documents_status": f"{verified_docs}/{len(required_documents)} Verified",
        "applications_status": "2 In Progress • 1 Submitted",
        "open_tasks_count": upcoming_tasks,
        "critical_risks_count": 1 if overdue_tasks > 0 else 0
    }

    next_best_action = {
        "title": "Upload Fire Safety Certificate" if category == "clothing_textile" else ("Complete FSSAI FoSCoS Renewal" if category == "restaurant" else "Reconcile HUID Hallmarking Tags"),
        "reason": "Expiring within current statutory inspection cycle and blocks final approval stage.",
        "target_route": "documents" if category == "clothing_textile" else "approvals",
        "priority": "High"
    }

    summary = {
        "total_approvals": len(approvals),
        "completed_approvals": completed_approvals,
        "in_progress_approvals": in_progress_approvals,
        "pending_approvals": pending_approvals,
        "high_priority_approvals": high_priority_approvals,
        "total_compliance_tasks": len(compliance_tasks),
        "upcoming_tasks": upcoming_tasks,
        "total_required_documents": len(required_documents),
        "total_recommended_schemes": len(recommended_schemes),
        "compliance_score": computed_score,
        "compliance_health_breakdown": compliance_health_breakdown
    }

    business_summary = {
        "business_name": get_val("business_name"),
        "business_type": get_val("business_type"),
        "business_category": category,
        "industry": get_val("industry"),
        "sector": get_val("sector"),
        "city": get_val("city"),
        "state": get_val("state"),
        "company_size": get_val("company_size"),
        "employee_count": employees,
        "annual_turnover": get_val("annual_turnover"),
        "gstin": get_val("gstin"),
        "udyam_number": get_val("udyam_number"),
        "operating_status": get_val("operating_status")
    }

    return {
        "is_valid": True,
        "analysis_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "business_summary": business_summary,
        "risk_level": risk_level,
        "summary": summary,
        "approvals": approvals,
        "compliance_tasks": compliance_tasks,
        "required_documents": required_documents,
        "recommended_schemes": recommended_schemes,
        "insights": insights,
        "control_tower_priorities": control_tower_priorities,
        "compliance_health_breakdown": compliance_health_breakdown,
        "workspace_readiness": workspace_readiness,
        "next_best_action": next_best_action,
        "disclaimer": "Recommendations are generated for prototype and planning purposes and should be verified with relevant authorities."
    }


def compare_business_categories(
    category_a: str = "clothing_textile",
    category_b: str = "restaurant",
    city: str = "Tiruppur",
    state: str = "Tamil Nadu"
) -> Dict[str, Any]:
    """
    Lightweight controlled comparison engine contrasting compliance requirements,
    evidence burdens, and regulatory authorities between two business categories
    in the same geographic location (e.g. Textile vs Restaurant in Tiruppur).
    Proves deterministic compliance differentiation based purely on business profile.
    """
    profile_a = {
        "business_name": f"{city} Textile Works",
        "business_category": category_a,
        "industry": "Clothing & Textile",
        "city": city,
        "state": state,
        "employee_count": 25,
        "environmental_impact": "Moderate",
        "has_gst": True,
        "has_msme_registration": True
    }
    profile_b = {
        "business_name": f"{city} Flavours Restaurant",
        "business_category": category_b,
        "industry": "Restaurant & Food Service",
        "city": city,
        "state": state,
        "employee_count": 15,
        "environmental_impact": "Low",
        "has_gst": True,
        "has_msme_registration": True
    }

    analysis_a = analyze_business_profile(profile_a)
    analysis_b = analyze_business_profile(profile_b)

    names_a = [a["name"] for a in analysis_a["approvals"]]
    names_b = [a["name"] for a in analysis_b["approvals"]]

    docs_a = [d["name"] for d in analysis_a["required_documents"]]
    docs_b = [d["name"] for d in analysis_b["required_documents"]]

    common_licences = sorted(list(set(names_a).intersection(set(names_b))))
    exclusive_a = sorted(list(set(names_a) - set(names_b)))
    exclusive_b = sorted(list(set(names_b) - set(names_a)))

    return {
        "location": f"{city}, {state}",
        "category_a": {
            "category_key": category_a,
            "title": "Clothing & Textile Manufacturing",
            "business_name": profile_a["business_name"],
            "total_licences": len(names_a),
            "total_documents": len(docs_a),
            "risk_level": analysis_a["risk_level"],
            "primary_regulators": [
                f"{state} Pollution Control Board (TNPCB)",
                "Textiles Committee, Ministry of Textiles",
                f"{city} Municipal Corporation",
                f"Labour Department, {state}"
            ],
            "licences_list": names_a,
            "top_scheme": analysis_a["recommended_schemes"][0]["short_name"] if analysis_a["recommended_schemes"] else "ATUFS"
        },
        "category_b": {
            "category_key": category_b,
            "title": "Restaurant & Food Service",
            "business_name": profile_b["business_name"],
            "total_licences": len(names_b),
            "total_documents": len(docs_b),
            "risk_level": analysis_b["risk_level"],
            "primary_regulators": [
                "Food Safety & Standards Authority of India (FSSAI)",
                f"{city} Municipal Corporation Public Health Section",
                f"{state} Police Department (Eating House)",
                f"{state} Fire & Rescue Services"
            ],
            "licences_list": names_b,
            "top_scheme": analysis_b["recommended_schemes"][0]["short_name"] if analysis_b["recommended_schemes"] else "PMFME"
        },
        "comparison_summary": {
            "common_licences": common_licences,
            "exclusive_to_category_a": exclusive_a,
            "exclusive_to_category_b": exclusive_b,
            "divergence_percentage": round((len(exclusive_a) + len(exclusive_b)) / (len(names_a) + len(names_b)) * 100),
            "conclusion": f"Operating in the exact same jurisdiction ({city}, {state}), statutory compliance diverges significantly based on business operations. Textile mandates effluent discharge (TNPCB) and yarn quality oversight, whereas Restaurant mandates food safety hygiene (FSSAI) and municipal health trade licensing."
        }
    }
