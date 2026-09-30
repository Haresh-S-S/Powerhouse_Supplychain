"""
Matching Service
----------------
Orchestrates employee ↔ role semantic matching using NBK ATS.
Combines with Skill-Sim data for a richer result.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.workforce import EmployeeProfile, RoleProfile

logger = logging.getLogger("[WORKFORCE AI]")


def _build_resume_text(emp: EmployeeProfile) -> str:
    """Build a text representation of an employee profile for embedding."""
    skills = emp.current_skills or []
    skill_str = ", ".join(
        (s if isinstance(s, str) else s.get("skill", "")) for s in skills
    )
    exp_years = emp.experience_years or 1
    return (
        f"Role: {emp.role}\n"
        f"Department: {emp.department}\n"
        f"Experience: {exp_years} years\n"
        f"Skills: {skill_str}\n"
    )


def _build_role_description(role: RoleProfile) -> str:
    """Build a text description of a role for embedding."""
    req_skills = role.required_skills or []
    skill_names = []
    for s in req_skills:
        if isinstance(s, str):
            skill_names.append(s)
        elif isinstance(s, dict):
            skill_names.append(s.get("skill", ""))
    skill_str = ", ".join(s for s in skill_names if s)
    return (
        f"Role: {role.role_name}\n"
        f"Department: {role.department}\n"
        f"Required Skills: {skill_str}\n"
    )


def match_employee_to_role(
    db: Session,
    business_id: str,
    employee_id: str,
    role_id: Optional[str] = None,
    role_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full employee-role matching pipeline:
      1. Build resume text + role description
      2. NBK ATS semantic similarity + score
      3. Skill-Sim skill-level comparison
    """
    from app.workforce_ai.adapters.nbk_adapter import NBKAdapter
    from app.workforce_ai.services.skill_service import analyze_skill_gap, _extract_skill_names

    emp = db.query(EmployeeProfile).filter(
        EmployeeProfile.id == employee_id,
        EmployeeProfile.business_id == business_id,
    ).first()

    if not emp:
        return {"error": "Employee not found", "ai_available": False}

    # Resolve role
    role: Optional[RoleProfile] = None
    if role_id:
        role = db.query(RoleProfile).filter(
            RoleProfile.id == role_id, RoleProfile.business_id == business_id
        ).first()
    if not role and role_name:
        role = db.query(RoleProfile).filter(
            RoleProfile.business_id == business_id,
            RoleProfile.role_name.ilike(role_name),
        ).first()
    if not role:
        role = db.query(RoleProfile).filter(
            RoleProfile.business_id == business_id
        ).first()

    if not role:
        return {
            "error": "No role found to match against",
            "employee_id": emp.id,
            "ai_available": False,
        }

    logger.info(
        f"[WORKFORCE AI] Matching employee {emp.employee_reference} "
        f"to role {role.role_name} …"
    )

    resume_text = _build_resume_text(emp)
    role_desc = _build_role_description(role)

    # NBK semantic match
    nbk = NBKAdapter.get()
    match_result = nbk.match_resume_to_role(resume_text, role_desc, role.role_name)

    # Skill-level comparison (Skill-Sim)
    emp_skills = _extract_skill_names(emp.current_skills or [])
    req_skills = _extract_skill_names(role.required_skills or [])
    skill_comparison = analyze_skill_gap(
        emp_skills, req_skills,
        employee_data={"role": emp.role},
        role_name=role.role_name,
        include_explanation=False,
    )

    return {
        "employee_id": emp.id,
        "employee_reference": emp.employee_reference,
        "role_id": role.id,
        "role_name": role.role_name,
        "ats_score": match_result.get("ats_score"),
        "semantic_similarity": match_result.get("semantic_similarity"),
        "fit_label": match_result.get("fit_label", ""),
        "match_explanation": match_result.get("match_explanation", ""),
        "matching_skills": skill_comparison.get("matching_skills", []),
        "missing_skills": skill_comparison.get("missing_skills", []),
        "related_skills": skill_comparison.get("related_skills", []),
        "skill_coverage_percent": skill_comparison.get("coverage_percent", 0),
        "ai_available": match_result.get("ai_available", False),
    }


def rank_employees_for_role(
    db: Session,
    business_id: str,
    role_id: str,
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """
    Rank all employees in the business against a specific role.
    Returns sorted list with ATS scores.
    """
    from app.workforce_ai.adapters.nbk_adapter import NBKAdapter

    role = db.query(RoleProfile).filter(
        RoleProfile.id == role_id, RoleProfile.business_id == business_id
    ).first()
    if not role:
        return []

    employees = db.query(EmployeeProfile).filter(
        EmployeeProfile.business_id == business_id
    ).all()

    if not employees:
        return []

    nbk = NBKAdapter.get()
    role_desc = _build_role_description(role)
    results = []

    for emp in employees:
        resume_text = _build_resume_text(emp)
        match = nbk.match_resume_to_role(resume_text, role_desc, role.role_name)
        results.append({
            "employee_id": emp.id,
            "employee_reference": emp.employee_reference,
            "current_role": emp.role,
            "department": emp.department,
            "ats_score": match.get("ats_score"),
            "fit_label": match.get("fit_label"),
            "ai_available": match.get("ai_available", False),
        })

    results.sort(
        key=lambda x: (x.get("ats_score") or 0),
        reverse=True,
    )
    return results[:top_n]
