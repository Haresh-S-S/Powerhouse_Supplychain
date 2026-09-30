"""
Workforce AI API Router
------------------------
Adds AI-powered endpoints to the existing Workforce module.
All routes are prefixed under /workforce/ai/ to avoid collisions
with existing /workforce/* endpoints.

Endpoints:
  POST /workforce/ai/resume/analyze         – NuExtract resume extraction
  POST /workforce/ai/skills/gap             – Skill-Sim gap analysis
  POST /workforce/ai/roles/match            – NBK ATS role matching
  POST /workforce/ai/career/recommend       – Full career recommendation
  POST /workforce/ai/development-plan       – Phased development plan
  GET  /workforce/ai/employee/{id}/analyze  – Full employee AI analysis
  POST /workforce/ai/agent/chat             – Workforce AI chat
  GET  /workforce/ai/status                 – AI model availability status
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.workforce import EmployeeProfile, RoleProfile

from app.workforce_ai.schemas import (
    ChatRequest,
    ChatResponse,
    CareerRecommendationRequest,
    CareerRecommendationResponse,
    DevelopmentPlanRequest,
    DevelopmentPlanResponse,
    EmployeeAIAnalysisResponse,
    ResumeAnalysisResponse,
    RoleMatchRequest,
    RoleMatchResponse,
    SkillGapAnalysisRequest,
    SkillGapAnalysisResponse,
)

logger = logging.getLogger("[WORKFORCE AI]")

router = APIRouter(prefix="/workforce/ai", tags=["Workforce AI Intelligence"])


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _verify_business(db: Session, user: User, business_profile_id: str) -> BusinessProfile:
    profile = db.query(BusinessProfile).filter(
        BusinessProfile.id == business_profile_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found.")
    if profile.user_id and profile.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access forbidden.")
    return profile


def _get_employee(db: Session, employee_id: str, business_id: str) -> EmployeeProfile:
    emp = db.query(EmployeeProfile).filter(
        EmployeeProfile.id == employee_id,
        EmployeeProfile.business_id == business_id,
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return emp


# ──────────────────────────────────────────────────────────────────────────────
# AI Status
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/status", summary="Workforce AI model availability status")
def get_ai_status() -> Dict[str, Any]:
    """
    Returns which AI models are currently loaded and available.
    Does NOT load models – just checks their state.
    """
    from app.workforce_ai.adapters.nuextract_adapter import NuExtractAdapter
    from app.workforce_ai.adapters.skillsim_adapter import SkillSimAdapter
    from app.workforce_ai.adapters.nbk_adapter import NBKAdapter
    from app.workforce_ai.adapters.qwen_adapter import QwenAdapter
    from app.workforce_ai.config import WORKFORCE_AI_ENABLED, QWEN_AVAILABLE

    return {
        "workforce_ai_enabled": WORKFORCE_AI_ENABLED,
        "models": {
            "nuextract": {
                "name": "NuExtract-tiny-Resume-Data-Extractor",
                "purpose": "Resume structured extraction",
                "loaded": NuExtractAdapter.get()._available,
            },
            "skill_sim": {
                "name": "skill-sim-model",
                "purpose": "Skill similarity & gap analysis",
                "loaded": SkillSimAdapter.get()._available,
            },
            "nbk_ats": {
                "name": "nbk-ats-semantic-v1-en",
                "purpose": "Resume-role semantic matching",
                "loaded": NBKAdapter.get()._available,
            },
            "qwen": {
                "name": "Qwen3-8B",
                "purpose": "AI reasoning & recommendations",
                "loaded": QwenAdapter.get()._available,
                "available": QWEN_AVAILABLE,
                "note": (
                    "Using structured analysis engine"
                    if not QWEN_AVAILABLE
                    else "Local model configured"
                ),
            },
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Resume Analysis
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/resume/analyze",
    response_model=ResumeAnalysisResponse,
    summary="Extract structured profile from resume PDF (NuExtract)",
)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume PDF file"),
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a resume PDF.
    Returns a structured employee profile extracted by NuExtract.
    """
    _verify_business(db, current_user, business_profile_id)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF files are accepted.",
        )

    # Size guard: 10 MB max
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum 10 MB.",
        )

    logger.info(
        f"[WORKFORCE AI] Resume upload: {file.filename} "
        f"({len(contents)} bytes)"
    )

    from app.workforce_ai.services.resume_service import analyze_resume as svc_analyze
    result = svc_analyze(contents)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Skill Gap Analysis
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/skills/gap",
    response_model=SkillGapAnalysisResponse,
    summary="Semantic skill-gap analysis (Skill-Sim + Qwen)",
)
def analyze_skill_gap(
    body: SkillGapAnalysisRequest,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compare employee skills vs required role skills using Skill-Sim.
    If employee_id provided, loads skills from DB.
    """
    _verify_business(db, current_user, business_profile_id)

    from app.workforce_ai.services.skill_service import (
        analyze_skill_gap as svc_gap,
        analyze_employee_skill_gap_db,
    )

    if body.employee_id:
        result = analyze_employee_skill_gap_db(
            db=db,
            business_id=business_profile_id,
            employee_id=body.employee_id,
        )
    else:
        result = svc_gap(
            employee_skills=body.employee_skills,
            required_skills=body.required_skills,
            role_name=body.role_name,
        )

    return SkillGapAnalysisResponse(
        employee_id=body.employee_id,
        role_name=result.get("role_name") or body.role_name,
        matching_skills=result.get("matching_skills", []),
        missing_skills=result.get("missing_skills", []),
        related_skills=result.get("related_skills", []),
        coverage_percent=result.get("coverage_percent", 0),
        skill_pairs=result.get("skill_pairs", []),
        explanation=result.get("explanation"),
        ai_available=result.get("ai_available", False),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Role Matching
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/roles/match",
    response_model=RoleMatchResponse,
    summary="Semantic employee-role match (NBK ATS + Skill-Sim)",
)
def match_role(
    body: RoleMatchRequest,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_business(db, current_user, business_profile_id)

    from app.workforce_ai.services.matching_service import match_employee_to_role

    result = match_employee_to_role(
        db=db,
        business_id=business_profile_id,
        employee_id=body.employee_id,
        role_id=body.role_id,
        role_name=body.role_name,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return RoleMatchResponse(
        employee_id=result["employee_id"],
        role_name=result["role_name"],
        ats_score=result.get("ats_score"),
        semantic_similarity=result.get("semantic_similarity"),
        fit_label=result.get("fit_label", ""),
        match_explanation=result.get("match_explanation", ""),
        matching_skills=result.get("matching_skills", []),
        missing_skills=result.get("missing_skills", []),
        related_skills=result.get("related_skills", []),
        skill_coverage_percent=result.get("skill_coverage_percent", 0),
        ai_available=result.get("ai_available", False),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Career Recommendation
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/career/recommend",
    summary="AI career path recommendation (Skill-Sim + NBK + Qwen)",
)
def recommend_career(
    body: CareerRecommendationRequest,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_business(db, current_user, business_profile_id)

    from app.workforce_ai.services.career_service import recommend_career_path

    result = recommend_career_path(
        db=db,
        business_id=business_profile_id,
        employee_id=body.employee_id,
        target_role_id=body.target_role_id,
        target_role_name=body.target_role_name,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Development Plan
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/development-plan",
    summary="Generate phased development plan (Skill-Sim + Qwen)",
)
def generate_development_plan(
    body: DevelopmentPlanRequest,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_business(db, current_user, business_profile_id)

    from app.workforce_ai.services.career_service import generate_development_plan as svc_plan

    result = svc_plan(
        db=db,
        business_id=business_profile_id,
        employee_id=body.employee_id,
        target_role_name=body.target_role_name,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Full Employee AI Analysis
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/employee/{employee_id}/analyze",
    summary="Full AI analysis for an employee (all models)",
)
def analyze_employee(
    employee_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_business(db, current_user, business_profile_id)

    from app.workforce_ai.services.recommendation_service import analyze_employee as svc_analyze

    result = svc_analyze(
        db=db,
        business_id=business_profile_id,
        employee_id=employee_id,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Workforce AI Chat
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/agent/chat",
    response_model=ChatResponse,
    summary="Workforce AI assistant chat (tool-based, Qwen)",
)
def workforce_chat(
    body: ChatRequest,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_business(db, current_user, business_profile_id)

    from app.workforce_ai.services.recommendation_service import workforce_chat as svc_chat

    result = svc_chat(
        db=db,
        business_id=business_profile_id,
        question=body.question,
        employee_id=body.employee_id,
        extra_context=body.context,
    )

    return ChatResponse(
        question=result["question"],
        answer=result["answer"],
        source=result.get("source", "structured-analysis"),
        ai_available=result.get("ai_available", False),
        suggested_actions=result.get("suggested_actions", []),
    )
