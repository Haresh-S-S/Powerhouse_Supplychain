"""
Career Service
--------------
Generates career development recommendations and development plans
using all available AI signals (Skill-Sim gaps + NBK role match + Qwen).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.workforce import EmployeeProfile, RoleProfile

logger = logging.getLogger("[WORKFORCE AI]")


def recommend_career_path(
    db: Session,
    business_id: str,
    employee_id: str,
    target_role_id: Optional[str] = None,
    target_role_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full career recommendation pipeline:
      Skill-Sim gap analysis
        + NBK ATS role match
        → Qwen career recommendation
    """
    from app.workforce_ai.services.skill_service import _extract_skill_names, analyze_skill_gap
    from app.workforce_ai.services.matching_service import match_employee_to_role
    from app.workforce_ai.adapters.qwen_adapter import QwenAdapter

    emp = db.query(EmployeeProfile).filter(
        EmployeeProfile.id == employee_id,
        EmployeeProfile.business_id == business_id,
    ).first()

    if not emp:
        return {"error": "Employee not found", "ai_available": False}

    # Resolve target role
    target_role: Optional[RoleProfile] = None
    if target_role_id:
        target_role = db.query(RoleProfile).filter(
            RoleProfile.id == target_role_id,
            RoleProfile.business_id == business_id,
        ).first()
    if not target_role and target_role_name:
        target_role = db.query(RoleProfile).filter(
            RoleProfile.business_id == business_id,
            RoleProfile.role_name.ilike(f"%{target_role_name}%"),
        ).first()
    if not target_role:
        # Default: pick a role that isn't the employee's current role
        target_role = db.query(RoleProfile).filter(
            RoleProfile.business_id == business_id,
        ).first()

    emp_skills = _extract_skill_names(emp.current_skills or [])
    req_skills = _extract_skill_names(target_role.required_skills if target_role else [])
    role_name = target_role.role_name if target_role else ("Senior " + emp.role)

    employee_data = {
        "role": emp.role,
        "department": emp.department,
        "experience_years": emp.experience_years,
        "current_skills": emp_skills,
    }

    logger.info(
        f"[WORKFORCE AI] Career recommendation: "
        f"{emp.employee_reference} → {role_name}"
    )

    # Skill gap analysis
    skill_analysis = analyze_skill_gap(
        emp_skills, req_skills,
        employee_data=employee_data,
        role_name=role_name,
        include_explanation=True,
    )

    # Role match (NBK)
    role_match = None
    if target_role:
        role_match = match_employee_to_role(
            db, business_id, employee_id,
            role_id=target_role.id,
        )

    # Qwen / template career recommendation
    qwen = QwenAdapter.get()
    rec = qwen.generate_career_recommendation(employee_data, skill_analysis, role_match)

    return {
        "employee_id": emp.id,
        "employee_reference": emp.employee_reference,
        "current_role": emp.role,
        "target_role": role_name,
        "experience_years": emp.experience_years,
        "current_strengths": rec.get("current_strengths", skill_analysis.get("matching_skills", [])),
        "missing_skills": skill_analysis.get("missing_skills", []),
        "related_skills": skill_analysis.get("related_skills", []),
        "priority_skills": rec.get("priority_skills", skill_analysis.get("missing_skills", [])[:5]),
        "development_phases": rec.get("development_phases", []),
        "summary": rec.get("summary", ""),
        "recommendation_text": rec.get("recommendation_text"),
        "ats_match_note": rec.get("ats_match_note"),
        "ats_score": (role_match or {}).get("ats_score"),
        "fit_label": (role_match or {}).get("fit_label"),
        "source": rec.get("source", "structured-analysis"),
        "ai_available": rec.get("ai_available", False),
    }


def generate_development_plan(
    db: Session,
    business_id: str,
    employee_id: str,
    target_role_name: str,
) -> Dict[str, Any]:
    """
    Generate a phased development plan for an employee targeting a role.
    """
    from app.workforce_ai.services.skill_service import _extract_skill_names, analyze_skill_gap
    from app.workforce_ai.adapters.qwen_adapter import QwenAdapter

    emp = db.query(EmployeeProfile).filter(
        EmployeeProfile.id == employee_id,
        EmployeeProfile.business_id == business_id,
    ).first()

    if not emp:
        return {"error": "Employee not found", "ai_available": False}

    # Try to find role in DB, otherwise use role name
    role = db.query(RoleProfile).filter(
        RoleProfile.business_id == business_id,
        RoleProfile.role_name.ilike(f"%{target_role_name}%"),
    ).first()

    emp_skills = _extract_skill_names(emp.current_skills or [])
    req_skills = _extract_skill_names(role.required_skills if role else [])

    employee_data = {
        "role": emp.role,
        "department": emp.department,
        "experience_years": emp.experience_years,
        "current_skills": emp_skills,
    }

    skill_analysis = analyze_skill_gap(emp_skills, req_skills, include_explanation=False)
    missing_skills = skill_analysis.get("missing_skills", [])

    qwen = QwenAdapter.get()
    plan = qwen.generate_development_plan(employee_data, missing_skills, target_role_name)

    return {
        "employee_id": emp.id,
        "employee_reference": emp.employee_reference,
        "current_role": emp.role,
        "target_role": target_role_name,
        "estimated_weeks": plan.get("estimated_weeks", len(missing_skills) * 2 + 2),
        "phases": plan.get("phases", []),
        "summary": plan.get("summary", ""),
        "plan_text": plan.get("plan_text"),
        "source": plan.get("source", "structured-analysis"),
        "ai_available": plan.get("ai_available", False),
    }
