"""
Recommendation Service
-----------------------
Full employee AI analysis combining all AI signals into a single
comprehensive view of an employee's capabilities and potential.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.workforce import EmployeeProfile, RoleProfile

logger = logging.getLogger("[WORKFORCE AI]")


def analyze_employee(
    db: Session,
    business_id: str,
    employee_id: str,
) -> Dict[str, Any]:
    """
    Comprehensive AI analysis for a single employee:
      • Skill-gap vs current role
      • NBK ATS role matching against all available roles
      • Qwen employee summary
    """
    from app.workforce_ai.services.skill_service import _extract_skill_names, analyze_skill_gap
    from app.workforce_ai.adapters.nbk_adapter import NBKAdapter
    from app.workforce_ai.adapters.qwen_adapter import QwenAdapter
    from app.workforce_ai.services.matching_service import _build_resume_text, _build_role_description

    emp = db.query(EmployeeProfile).filter(
        EmployeeProfile.id == employee_id,
        EmployeeProfile.business_id == business_id,
    ).first()

    if not emp:
        return {"error": "Employee not found", "ai_available": False}

    logger.info(f"[WORKFORCE AI] Full employee analysis for {emp.employee_reference} …")

    emp_skills = _extract_skill_names(emp.current_skills or [])

    # Match employee against primary role
    matching_role = db.query(RoleProfile).filter(
        RoleProfile.business_id == business_id,
        RoleProfile.role_name.ilike(emp.role),
    ).first()
    if not matching_role:
        matching_role = db.query(RoleProfile).filter(
            RoleProfile.business_id == business_id
        ).first()

    req_skills = _extract_skill_names(matching_role.required_skills if matching_role else [])
    role_name = matching_role.role_name if matching_role else emp.role

    employee_data = {
        "role": emp.role,
        "department": emp.department,
        "experience_years": emp.experience_years,
        "current_skills": emp_skills,
    }

    # Skill gap analysis
    skill_analysis = analyze_skill_gap(
        emp_skills, req_skills,
        employee_data=employee_data,
        role_name=role_name,
        include_explanation=True,
    )

    # NBK ranking against all roles
    all_roles = db.query(RoleProfile).filter(
        RoleProfile.business_id == business_id
    ).limit(10).all()

    nbk = NBKAdapter.get()
    resume_text = _build_resume_text(emp)
    potential_roles = []
    for role in all_roles:
        role_desc = _build_role_description(role)
        match = nbk.match_resume_to_role(resume_text, role_desc, role.role_name)
        potential_roles.append({
            "role_id": role.id,
            "role_name": role.role_name,
            "ats_score": match.get("ats_score"),
            "fit_label": match.get("fit_label"),
            "department": role.department,
        })
    potential_roles.sort(key=lambda x: (x.get("ats_score") or 0), reverse=True)

    # Employee summary via Qwen
    qwen = QwenAdapter.get()
    summary_result = qwen.summarize_employee(employee_data, skill_analysis)

    return {
        "employee_id": emp.id,
        "employee_reference": emp.employee_reference,
        "current_role": emp.role,
        "department": emp.department,
        "experience_years": emp.experience_years,
        "current_skills": emp_skills,
        "skill_coverage_percent": skill_analysis.get("coverage_percent", 0),
        "matching_skills": skill_analysis.get("matching_skills", []),
        "missing_skills": skill_analysis.get("missing_skills", []),
        "related_skills": skill_analysis.get("related_skills", []),
        "skill_explanation": skill_analysis.get("explanation", ""),
        "ai_summary": summary_result.get("summary", ""),
        "potential_roles": potential_roles[:5],
        "ai_available": skill_analysis.get("ai_available", False),
    }


def workforce_chat(
    db: Session,
    business_id: str,
    question: str,
    employee_id: str = None,
    extra_context: Dict = None,
) -> Dict[str, Any]:
    """
    Workforce AI chat handler.
    Builds context from DB data and routes to Qwen.
    """
    from app.workforce_ai.adapters.qwen_adapter import QwenAdapter
    from app.workforce_ai.services.skill_service import _extract_skill_names, analyze_skill_gap
    from app.workforce_ai.adapters.nbk_adapter import NBKAdapter
    from app.workforce_ai.services.matching_service import _build_resume_text, _build_role_description

    context: Dict[str, Any] = extra_context or {}

    if employee_id:
        emp = db.query(EmployeeProfile).filter(
            EmployeeProfile.id == employee_id,
            EmployeeProfile.business_id == business_id,
        ).first()

        if emp:
            emp_skills = _extract_skill_names(emp.current_skills or [])
            matching_role = db.query(RoleProfile).filter(
                RoleProfile.business_id == business_id,
                RoleProfile.role_name.ilike(emp.role),
            ).first() or db.query(RoleProfile).filter(
                RoleProfile.business_id == business_id
            ).first()

            req_skills = _extract_skill_names(matching_role.required_skills if matching_role else [])

            skill_analysis = analyze_skill_gap(
                emp_skills, req_skills,
                employee_data={"role": emp.role},
                role_name=matching_role.role_name if matching_role else emp.role,
                include_explanation=False,
            )

            role_match = None
            if matching_role:
                nbk = NBKAdapter.get()
                resume_text = _build_resume_text(emp)
                role_desc = _build_role_description(matching_role)
                role_match = nbk.match_resume_to_role(
                    resume_text, role_desc, matching_role.role_name
                )

            context = {
                "employee": {
                    "role": emp.role,
                    "department": emp.department,
                    "experience_years": emp.experience_years,
                    "current_skills": emp_skills,
                },
                "skill_analysis": skill_analysis,
                "role_match": role_match or {},
            }

    qwen = QwenAdapter.get()
    result = qwen.answer_workforce_question(question, context)

    suggested_actions = _suggest_actions(question)

    return {
        "question": question,
        "answer": result.get("answer", "I was unable to process your question. Please try again."),
        "source": result.get("source", "structured-analysis"),
        "ai_available": result.get("ai_available", False),
        "suggested_actions": suggested_actions,
    }


def _suggest_actions(question: str) -> List[str]:
    """Suggest follow-up actions based on question content."""
    q = question.lower()
    actions = []
    if any(k in q for k in ["skill", "gap", "missing"]):
        actions.append("View detailed skill gap analysis")
        actions.append("Generate development plan")
    if any(k in q for k in ["role", "match", "suit"]):
        actions.append("Run full role matching analysis")
        actions.append("View potential roles")
    if any(k in q for k in ["plan", "develop", "learn", "path"]):
        actions.append("Generate development plan")
        actions.append("View learning pathways")
    if any(k in q for k in ["summary", "summarize", "profile"]):
        actions.append("View full employee analysis")
    if not actions:
        actions = ["Analyze skill gaps", "View role matches", "Generate career plan"]
    return actions[:3]
