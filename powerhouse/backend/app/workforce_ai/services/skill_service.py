"""
Skill Service
-------------
Orchestrates skill intelligence using Skill-Sim + Qwen:
  • Skill normalization
  • Employee vs role skill comparison
  • Skill-gap analysis with AI explanation
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.workforce import EmployeeProfile, RoleProfile

logger = logging.getLogger("[WORKFORCE AI]")


def _extract_skill_names(skills_list: List) -> List[str]:
    """Normalize skill list which may contain strings or dicts."""
    result = []
    for s in (skills_list or []):
        if isinstance(s, str) and s.strip():
            result.append(s.strip())
        elif isinstance(s, dict):
            name = s.get("skill") or s.get("name") or ""
            if name.strip():
                result.append(name.strip())
    return result


def analyze_skill_gap(
    employee_skills: List[str],
    required_skills: List[str],
    employee_data: Optional[Dict] = None,
    role_name: Optional[str] = None,
    include_explanation: bool = True,
) -> Dict[str, Any]:
    """
    Run full skill-gap analysis:
      1. Skill-Sim semantic comparison
      2. Qwen explanation of gaps
    """
    from app.workforce_ai.adapters.skillsim_adapter import SkillSimAdapter
    from app.workforce_ai.adapters.qwen_adapter import QwenAdapter

    logger.info(
        f"[WORKFORCE AI] Analyzing skill gap: "
        f"{len(employee_skills)} employee skills vs {len(required_skills)} required"
    )

    # Step 1: Skill-Sim comparison
    sim_adapter = SkillSimAdapter.get()
    comparison = sim_adapter.compare_skill_lists(employee_skills, required_skills)
    comparison["role_name"] = role_name

    if not include_explanation:
        return comparison

    # Step 2: Qwen explanation
    qwen = QwenAdapter.get()
    emp_data = employee_data or {"role": role_name or "Current Role"}
    explanation_result = qwen.generate_skill_gap_explanation(emp_data, comparison)
    comparison["explanation"] = explanation_result.get("explanation", "")
    comparison["explanation_source"] = explanation_result.get("source", "structured-analysis")

    return comparison


def analyze_employee_skill_gap_db(
    db: Session,
    business_id: str,
    employee_id: str,
    role_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full skill-gap analysis for an employee from the database.
    Resolves employee and role from DB, then runs AI analysis.
    """
    emp = db.query(EmployeeProfile).filter(
        EmployeeProfile.id == employee_id,
        EmployeeProfile.business_id == business_id,
    ).first()

    if not emp:
        return {"error": "Employee not found", "ai_available": False}

    # Find the role – by role_id if given, else by name matching
    role: Optional[RoleProfile] = None
    if role_id:
        role = db.query(RoleProfile).filter(
            RoleProfile.id == role_id,
            RoleProfile.business_id == business_id,
        ).first()
    if not role:
        role = db.query(RoleProfile).filter(
            RoleProfile.business_id == business_id,
            RoleProfile.role_name.ilike(emp.role),
        ).first()
    if not role:
        # Pick first available role
        role = db.query(RoleProfile).filter(
            RoleProfile.business_id == business_id
        ).first()

    employee_skills = _extract_skill_names(emp.current_skills or [])
    required_skills = _extract_skill_names(role.required_skills if role else [])
    role_name = role.role_name if role else emp.role

    employee_data = {
        "role": emp.role,
        "department": emp.department,
        "experience_years": emp.experience_years,
        "current_skills": employee_skills,
    }

    result = analyze_skill_gap(
        employee_skills=employee_skills,
        required_skills=required_skills,
        employee_data=employee_data,
        role_name=role_name,
    )
    result["employee_id"] = emp.id
    result["employee_reference"] = emp.employee_reference
    result["role_name"] = role_name
    return result
